#!/usr/bin/env python3
"""Validate/retarget source-selected D1 animations across package families.

This closes a limitation of earlier animation tools which assumed skeleton, runtime
rig, action control and clips lived in one logical Tiger package. The resolver is
fed verified package-member catalogs and routes each exact FileHash independently.

For every requested clip this tool requires:
  * the exact control serializes/selects the clip;
  * the runtime rig is the validated 808008B2 -> 8080099B EntityResource form;
  * the clip's ordered runtime-component fingerprint exactly equals the rig's;
  * clip header node/control counts equal the supplied skeleton/rig dimensions;
  * the pinned D1 parser decodes exactly the runtime-rig control domain, then
    retargets/expands it to exactly the supplied skeleton-node domain and converts
    all resulting node tracks to local space.

This distinction is intentional: a D1 animation may advertise 72 skeleton nodes but
only 66 runtime-rig controls. ``decode_animation`` therefore yields 66 control
tracks, while ``rig_retarget`` maps/expands those controls to 72 skeleton-node
tracks. Treating decoded-track count as skeleton-node count would erase the very
runtime-rig mapping this tool is meant to prove.

Success proves this concrete skeleton/rig/control/clip path is mechanically
exportable. State/action semantics remain only those explicitly decoded from the
control StringHash table; no package-name or motion-appearance inference is used.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
import tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from d1_animation_control_state_map import decode_control
from d1_animation_retarget_probe import component_rows
from d1_character_family_census import RUNTIME_RIG_DISCRIMINATOR,RUNTIME_RIG_INFO
from d1_entity_resource_probe import parse_resource
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_model_tgxm_signature_match import LazyExactHashResolver
from d1_split_tar_extract import SplitHttpTar


def norm(s:str)->str:
    return s.upper().removeprefix('0X').zfill(8)


def read_animation_filebacked(read_animation,payload:bytes,version):
    with tempfile.NamedTemporaryFile() as f:
        f.write(payload);f.flush();f.seek(0)
        return read_animation(f,version)


def selected_by_control(control:dict)->dict[str,list[dict]]:
    out={}
    for state in control['state_table']['records']:
        for a in state['selected_animations']:
            out.setdefault(a['tag_hash'].upper(),[]).append({
                'record_index':state['record_index'],
                'state_hash':state['state_hash'],
                'state_name':state.get('state_name'),
                'scalar_f32':state['scalar_f32'],
                'packed_selection':state['packed_selection'],
            })
    return out


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--parser-root',type=Path,required=True)
    ap.add_argument('--skeleton',required=True);ap.add_argument('--rig',required=True);ap.add_argument('--control',required=True)
    ap.add_argument('--clip',action='append',required=True)
    ap.add_argument('--name',action='append',default=[])
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()

    sh,rh,ch=map(norm,(a.skeleton,a.rig,a.control));clips=list(dict.fromkeys(norm(x) for x in a.clip))
    cats=load_catalogs(a.member_catalog)
    arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90)
    resolver=LazyExactHashResolver(arc,cats,a.runtime)

    sv,se,sb=resolver.bytes(sh);rv,re,rb=resolver.bytes(rh);cv,ce,cb=resolver.bytes(ch)
    rig_outer=parse_resource(rb,'PS4')
    u10=(rig_outer.get('unk10') or {}).get('class_hash');u18=(rig_outer.get('unk18') or {}).get('class_hash')
    if (u10,u18)!=(RUNTIME_RIG_DISCRIMINATOR,RUNTIME_RIG_INFO):
        raise ValueError(f'{rh}: runtime-rig class pair {u10}->{u18} != {RUNTIME_RIG_DISCRIMINATOR}->{RUNTIME_RIG_INFO}')

    control=decode_control(cb,None,a.name)
    selected=selected_by_control(control)
    missing=[h for h in clips if h not in selected]
    if missing:raise ValueError(f'clips not selected by control {ch}: {missing}')

    sys.path.insert(0,str(a.parser_root.resolve()))
    from tag.game_version import Game_Version
    from tag_readers.read_skeleton import read_skeleton
    from tag_readers.read_rig import read_runtime_rig
    from tag_readers.read_animation import read_animation
    from animation_decoding.decode_animation import decode_animation
    from runtime_rig.rig_retarget import rig_retarget,calc_control_limit
    from animation_export.convert_animation_object_to_local import convert_obj_to_local

    ver=Game_Version.D1_ROI
    skeleton=read_skeleton(io.BytesIO(sb),ver);rig=read_runtime_rig(io.BytesIO(rb),ver)
    target_components=component_rows(rig.rig_components)
    node_count=len(skeleton.node_defs);control_count=len(rig.controls_relations)
    if node_count<=0 or control_count<=0:raise ValueError('empty skeleton or rig')

    rows=[]
    for h in clips:
        vv,e,b=resolver.bytes(h)
        anim=read_animation_filebacked(read_animation,b,ver);hdr=anim.animation_header
        comps=component_rows(anim.runtime_rig_components)
        native_limit=int(calc_control_limit(rig,anim.runtime_rig_components))
        if comps!=target_components:raise ValueError(f'{h}: runtime component fingerprint mismatch')
        if int(hdr.node_count)!=node_count:raise ValueError(f'{h}: node count {hdr.node_count} != skeleton {node_count}')
        if int(hdr.rig_control_count)!=control_count:raise ValueError(f'{h}: control count {hdr.rig_control_count} != rig {control_count}')
        if native_limit!=control_count:raise ValueError(f'{h}: native control limit {native_limit} != {control_count}')
        decoded=decode_animation(anim);ret=rig_retarget(anim,decoded,skeleton,rig);local=convert_obj_to_local(anim,ret,skeleton)
        if len(decoded)!=control_count or len(ret)!=node_count or len(local)!=node_count:
            raise ValueError(
                f'{h}: track-domain mismatch decoded_controls={len(decoded)}/{control_count} '
                f'retargeted_nodes={len(ret)}/{node_count} local_nodes={len(local)}/{node_count}')
        channel_counts={'translation':0,'rotation':0,'scale':0}
        frame_counts={'translation':set(),'rotation':set(),'scale':set()}
        for tr in local:
            for key,attr in (('translation','translations'),('rotation','rotations'),('scale','scales')):
                vals=getattr(tr,attr,[])
                if len(vals):
                    channel_counts[key]+=1;frame_counts[key].add(len(vals))
        rows.append({
            'clip_tag_hash':h,'entry_index':int(e['index']),'entry_size':int(e['file_size']),
            'frame_count':int(hdr.frame_count),'node_count':int(hdr.node_count),'rig_control_count':int(hdr.rig_control_count),
            'native_control_limit':native_limit,'runtime_rig_components':comps,
            'selected_by_control_states':selected[h],
            'decoded_domain':'runtime_controls','decoded_track_count':len(decoded),
            'retargeted_domain':'skeleton_nodes','retargeted_track_count':len(ret),'local_track_count':len(local),
            'local_channel_node_counts':channel_counts,
            'local_channel_frame_count_sets':{k:sorted(v) for k,v in frame_counts.items()},
            'retarget_success':True,
        })

    rep={
      'schema':'d1_remote_cross_package_animation_retarget/v2',
      'skeleton':{'tag_hash':sh,'entry_index':int(se['index']),'entry_size':int(se['file_size']),'node_count':node_count},
      'runtime_rig':{'tag_hash':rh,'entry_index':int(re['index']),'entry_size':int(re['file_size']),'control_count':control_count,
                     'components':target_components,'discriminator_class':u10,'info_class':u18},
      'control':{'tag_hash':ch,'entry_index':int(ce['index']),'entry_size':int(ce['file_size']),
                 'animation_count':control['animation_list']['count'],'state_count':control['state_table']['count'],
                 'unique_selected_clip_count':len(selected)},
      'clip_count':len(rows),'clips':rows,
      'catalog_package_ids':[f'{x:04X}' for x in sorted(cats)],
      'policy':'Every clip is explicitly selected by the exact control, exactly runtime-component compatible with the supplied rig, decoded over the exact runtime-control domain, then successfully expanded/retargeted to the exact skeleton-node domain by the pinned D1 parser. State semantics are not inferred from motion.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps({'skeleton':rep['skeleton'],'runtime_rig':rep['runtime_rig'],'control':rep['control'],
                      'clips':[{k:x[k] for k in ('clip_tag_hash','frame_count','native_control_limit','decoded_track_count','retargeted_track_count','local_track_count')} for x in rows]},indent=2))
    return 0

if __name__=='__main__':raise SystemExit(main())
