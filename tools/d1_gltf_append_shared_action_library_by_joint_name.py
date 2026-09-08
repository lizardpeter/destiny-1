#!/usr/bin/env python3
"""Append a compatible D1 action library to a corrected textured actor GLB.

Only animation-owned payload is imported from the source action-library GLB:
- bufferViews referenced by animation accessors;
- the referenced accessors themselves; and
- animations, with channel target nodes remapped by exact joint name.

The target actor is authoritative for geometry, skin, materials and textures.  Its
existing BIN payload must remain an exact prefix and every pre-existing glTF array
must remain an exact prefix.  No source meshes/materials/images/textures/nodes/skins
are copied.  This makes the adapter suitable for applying one decoded family action
library to multiple exact visual/material variants that share the same source rig.
"""
from __future__ import annotations

import argparse, copy, hashlib, json
from pathlib import Path

from d1_gltf_layer_merge import read_glb, write_glb


def hbytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def hfile(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8<<20),b''): h.update(b)
    return h.hexdigest()


def joint_domain(doc: dict) -> list[tuple[int,str]]:
    skins=doc.get('skins') or []
    if len(skins)!=1: raise ValueError(f'expected one skin, got {len(skins)}')
    out=[]; seen=set()
    for ni0 in skins[0].get('joints') or []:
        ni=int(ni0); name=str((doc.get('nodes') or [])[ni].get('name') or '')
        if not name or name in seen: raise ValueError(f'invalid/duplicate joint name {name!r}')
        seen.add(name); out.append((ni,name))
    return out


def animation_accessor_ids(doc: dict) -> set[int]:
    out=set()
    for a in doc.get('animations') or []:
        for s in a.get('samplers') or []:
            out.add(int(s['input'])); out.add(int(s['output']))
    return out


def accessor_buffer_views(acc: dict) -> set[int]:
    out=set()
    if acc.get('bufferView') is not None: out.add(int(acc['bufferView']))
    sp=acc.get('sparse')
    if isinstance(sp,dict):
        for k in ('indices','values'):
            q=sp.get(k)
            if isinstance(q,dict) and q.get('bufferView') is not None: out.add(int(q['bufferView']))
    return out


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--target',type=Path,required=True)
    ap.add_argument('--action-library',type=Path,required=True)
    ap.add_argument('--expected-action-count',type=int)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--report',type=Path,required=True)
    a=ap.parse_args()

    tgt,tbin=read_glb(a.target); src,sbin=read_glb(a.action_library)
    # These files can be hundreds of megabytes. Hash each input exactly once and
    # reuse the digest for per-animation provenance instead of rereading the same
    # action-library file once for every animation.
    target_sha=hfile(a.target); action_library_sha=hfile(a.action_library)
    violations=[]
    tdom=joint_domain(tgt); sdom=joint_domain(src)
    tnames=[n for _,n in tdom]; snames=[n for _,n in sdom]
    if tnames!=snames: violations.append('ordered_skin_joint_names_differ')
    target_by_name={n:i for i,n in tdom}; source_joint_nodes={i:n for i,n in sdom}
    anims=src.get('animations') or []
    if not anims: violations.append('source_action_library_has_no_animations')
    if a.expected_action_count is not None and len(anims)!=a.expected_action_count:
        violations.append(f'action_count_{len(anims)}_not_expected_{a.expected_action_count}')

    # Validate channel domain before copying anything.
    target_paths=set(); target_names=set()
    for ai,anim in enumerate(anims):
        for ci,ch in enumerate(anim.get('channels') or []):
            t=ch.get('target') or {}; ni=int(t.get('node',-1)); path=str(t.get('path') or '')
            name=source_joint_nodes.get(ni)
            if name is None: violations.append(f'animation_{ai}_channel_{ci}_targets_non_skin_node_{ni}'); continue
            if name not in target_by_name: violations.append(f'animation_{ai}_channel_{ci}_joint_missing_in_target_{name}')
            if path not in {'translation','rotation','scale'}: violations.append(f'animation_{ai}_channel_{ci}_unsupported_path_{path}')
            target_names.add(name); target_paths.add(path)

    used_acc=sorted(animation_accessor_ids(src))
    src_acc=src.get('accessors') or []; src_bv=src.get('bufferViews') or []
    if any(i<0 or i>=len(src_acc) for i in used_acc): violations.append('animation_accessor_index_oob')
    used_bv=set()
    for i in used_acc:
        if 0<=i<len(src_acc): used_bv.update(accessor_buffer_views(src_acc[i]))
    used_bv=sorted(used_bv)
    if any(i<0 or i>=len(src_bv) for i in used_bv): violations.append('animation_buffer_view_index_oob')
    for i in used_bv:
        bv=src_bv[i]
        if int(bv.get('buffer',0))!=0: violations.append(f'animation_buffer_view_{i}_not_buffer0')
        off=int(bv.get('byteOffset',0)); ln=int(bv.get('byteLength',0))
        if off<0 or ln<0 or off+ln>len(sbin): violations.append(f'animation_buffer_view_{i}_slice_oob')
    if violations:
        raise SystemExit('; '.join(violations))

    # Preserve exact target state for round-trip validation.
    preserved_keys=('scenes','nodes','skins','meshes','materials','images','textures','samplers','cameras')
    before_exact={k:copy.deepcopy(tgt.get(k,[])) for k in preserved_keys}
    before_acc=copy.deepcopy(tgt.get('accessors',[])); before_bv=copy.deepcopy(tgt.get('bufferViews',[])); before_anim=copy.deepcopy(tgt.get('animations',[]))
    before_bin_sha=hbytes(tbin); before_len=len(tbin)

    doc=copy.deepcopy(tgt); bin_data=tbin
    bv_map={}; copied_bv_bytes=0
    for old in used_bv:
        bv=copy.deepcopy(src_bv[old]); off=int(bv.get('byteOffset',0)); ln=int(bv['byteLength'])
        aligned=(len(bin_data)+3)&~3
        if aligned!=len(bin_data): bin_data+=b'\x00'*(aligned-len(bin_data))
        new_off=len(bin_data); payload=sbin[off:off+ln]; bin_data+=payload; copied_bv_bytes+=len(payload)
        bv['buffer']=0; bv['byteOffset']=new_off
        new_i=len(doc.setdefault('bufferViews',[])); doc['bufferViews'].append(bv); bv_map[old]=new_i

    acc_map={}
    for old in used_acc:
        ac=copy.deepcopy(src_acc[old])
        if ac.get('bufferView') is not None: ac['bufferView']=bv_map[int(ac['bufferView'])]
        sp=ac.get('sparse')
        if isinstance(sp,dict):
            for k in ('indices','values'):
                q=sp.get(k)
                if isinstance(q,dict) and q.get('bufferView') is not None: q['bufferView']=bv_map[int(q['bufferView'])]
        new_i=len(doc.setdefault('accessors',[])); doc['accessors'].append(ac); acc_map[old]=new_i

    appended=[]
    for ai,anim0 in enumerate(anims):
        anim=copy.deepcopy(anim0)
        for s in anim.get('samplers') or []:
            s['input']=acc_map[int(s['input'])]; s['output']=acc_map[int(s['output'])]
        for ch in anim.get('channels') or []:
            t=ch['target']; old_node=int(t['node']); name=source_joint_nodes[old_node]; t['node']=target_by_name[name]
        ex=anim.setdefault('extras',{})
        ex['d1_shared_action_library_source_sha256']=action_library_sha
        ex['d1_shared_action_library_source_animation_index']=ai
        doc.setdefault('animations',[]).append(anim)
        appended.append(str(anim.get('name') or f'animation_{ai}'))

    write_glb(a.out,doc,bin_data)
    chk,cbin=read_glb(a.out)
    post_viol=[]
    if cbin[:before_len]!=tbin: post_viol.append('target_bin_not_exact_prefix')
    for k in preserved_keys:
        if chk.get(k,[])!=before_exact[k]: post_viol.append(f'target_{k}_changed')
    if chk.get('accessors',[])[:len(before_acc)]!=before_acc: post_viol.append('target_accessor_prefix_changed')
    if chk.get('bufferViews',[])[:len(before_bv)]!=before_bv: post_viol.append('target_bufferView_prefix_changed')
    if chk.get('animations',[])[:len(before_anim)]!=before_anim: post_viol.append('target_animation_prefix_changed')
    if len(chk.get('animations',[]))!=len(before_anim)+len(anims): post_viol.append('final_animation_count_mismatch')
    if post_viol: raise SystemExit('; '.join(post_viol))

    rep={
        'schema_version':1,
        'status':'D1_GLTF_SHARED_ACTION_LIBRARY_APPENDED_BY_JOINT_NAME',
        'target':str(a.target),'target_sha256':target_sha,
        'action_library':str(a.action_library),'action_library_sha256':action_library_sha,
        'output':str(a.out),'output_sha256':hfile(a.out),'output_bytes':a.out.stat().st_size,
        'joint_count':len(tdom),'ordered_skin_joint_names_identical':tnames==snames,
        'animation_target_joint_count':len(target_names),'animation_target_paths':sorted(target_paths),
        'existing_animation_count':len(before_anim),'appended_animation_count':len(anims),'final_animation_count':len(chk.get('animations',[])),
        'copied_animation_accessor_count':len(used_acc),'copied_animation_buffer_view_count':len(used_bv),'copied_animation_buffer_view_payload_bytes':copied_bv_bytes,
        'target_bin_payload_bytes_before':before_len,'target_bin_payload_sha256_before':before_bin_sha,
        'target_bin_exact_prefix':True,
        'preserved_target_arrays_exact':list(preserved_keys),
        'violations':[],
        'gates':{'runtime_actor_animation_state_selected':False},
        'policy':'Only animation-owned bufferViews/accessors and animation JSON are appended. Channels are remapped by exact skin-joint name. Target geometry, skin, nodes, materials, images, textures and existing BIN bytes remain authoritative and unchanged.'
    }
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps({k:rep[k] for k in ('status','joint_count','appended_animation_count','copied_animation_accessor_count','copied_animation_buffer_view_count','target_bin_exact_prefix','output_bytes','output_sha256')},indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
