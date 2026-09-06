#!/usr/bin/env python3
"""Discover source-owned animation controls for Tower articulated families without assuming a runtime rig.

This closes a gap left by the runtime-rig animation owner probes.  Families B/C/D
have source-owned EntityModels and skeletons but no runtime rig was proven in the
first articulated closure.  For each supplied SEntity this tool:

* reopens the exact SEntity and its serialized EntityResource list;
* resolves every EntityResource through the cross-package corpus;
* parses its exact class pair;
* scans every aligned 32-bit payload slot and promotes a slot only when its value
  resolves to an entry whose exact reference class is 80802C0E (animation control);
* decodes every such control and all selector-selected animation FileHashes;
* parses selected clips with the pinned D1 animation parser;
* compares clip node counts to the source-owned skeleton, but does not invent a
  runtime rig or claim retargetability from dimensions alone.

A control edge found this way is literal source ownership evidence.  Clip/skeleton
node-count equality is only structural evidence until a compatible runtime rig or
other exact binding architecture is recovered.
"""
from __future__ import annotations

import argparse, io, json, struct, sys, tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import d1_tower_map_schema_validate_v5 as v5
from d1_entity_resource_probe import parse_resource
from d1_animation_control_state_map import decode_control

SENTITY='80800734'; ENTITY_RESOURCE='80800861'; CONTROL='80802C0E'; CLIP='808005A1'


def norm(x): return str(x).upper().removeprefix('0X').zfill(8)
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def i64(b,o): return struct.unpack_from('<q',b,o)[0]

def dyn_resources(b:bytes)->list[str]:
    if len(b)<0x30: raise ValueError('SEntity too short')
    n=u32(b,0x20); rel=i64(b,0x28); hdr=0x28+rel
    if hdr<0 or hdr+0x10>len(b): raise ValueError(f'resource array header OOB 0x{hdr:X}')
    repeated=u32(b,hdr)
    if repeated!=n: raise ValueError(f'resource count mismatch {n}!={repeated}')
    data=hdr+0x10; end=data+n*0x0c
    if end>len(b): raise ValueError(f'resource array OOB 0x{end:X}>0x{len(b):X}')
    return [f'{u32(b,data+i*0x0c):08X}' for i in range(n)]

def filebacked(read_animation,b,ver):
    with tempfile.NamedTemporaryFile() as f:
        f.write(b);f.flush();f.seek(0);return read_animation(f,ver)

def selected(decoded):
    out=[]
    for st in decoded.get('state_table',{}).get('records',[]):
        for a in st.get('selected_animations',[]):
            out.append({'state_hash':norm(st.get('state_hash','0')),'state_name':st.get('state_name'),
                        'record_index':st.get('record_index'),'animation':norm(a['tag_hash'])})
    return out

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--snapshot',type=Path,action='append',required=True)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--parser-root',type=Path,required=True)
    ap.add_argument('--family',action='append',required=True,
                    help='ID:SENTITY:SKELETON, e.g. B:80C7A532:809D8573')
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    c=v5.v3.base.Corpus([p.resolve() for p in a.snapshot],a.runtime.resolve())

    sys.path.insert(0,str(a.parser_root.resolve()))
    from tag.game_version import Game_Version
    from tag_readers.read_skeleton import read_skeleton
    from tag_readers.read_animation import read_animation
    ver=Game_Version.D1_ROI

    families=[]; violations=[]
    for spec in a.family:
        fid,se,sk=spec.split(':',2);fid=fid.upper();se=norm(se);sk=norm(sk)
        sem=c.entry_meta(se);seb,sesrc=c.payload(se)
        row={'family':fid,'sentity':se,'skeleton':sk,'sentity_meta':sem,'sentity_source':sesrc}
        if not sem or norm(sem.get('reference',''))!=SENTITY or seb is None:
            row['error']='SEntity unavailable/wrong class';families.append(row);violations.append(row['error']);continue
        try: resources=dyn_resources(seb)
        except Exception as ex:
            row['error']=f'SEntity resources failed: {ex!r}';families.append(row);violations.append(row['error']);continue
        row['resource_hashes']=resources
        skm=c.entry_meta(sk);skb,sksrc=c.payload(sk)
        if not skm or skb is None:
            row['skeleton_error']='skeleton unavailable';nodes=None
        else:
            try:nodes=len(read_skeleton(io.BytesIO(skb),ver).node_defs)
            except Exception as ex: row['skeleton_error']=repr(ex);nodes=None
        row['skeleton_node_count']=nodes;row['skeleton_source']=sksrc

        rrows=[]; control_edges=[]
        for rh in resources:
            rm=c.entry_meta(rh);rb,rsrc=c.payload(rh)
            rr={'resource':rh,'meta':rm,'source':rsrc}
            if not rm or norm(rm.get('reference',''))!=ENTITY_RESOURCE or rb is None:
                rr['error']='unavailable/non-EntityResource';rrows.append(rr);continue
            try:
                pr=parse_resource(rb,'PS4')
                rr['class_pair']=[norm((pr.get('unk10') or {}).get('class_hash','0')),norm((pr.get('unk18') or {}).get('class_hash','0'))]
            except Exception as ex: rr['parse_error']=repr(ex)
            hits=[]
            for off in range(0,len(rb)-3,4):
                h=f'{u32(rb,off):08X}';m=c.entry_meta(h)
                if m and norm(m.get('reference',''))==CONTROL:
                    hits.append({'offset':off,'offset_hex':f'0x{off:X}','control':h,'control_meta':m})
                    control_edges.append({'owner_resource':rh,'owner_class_pair':rr.get('class_pair'),'offset':off,'control':h})
            rr['animation_control_filehash_hits']=hits
            rrows.append(rr)
        row['resources']=rrows;row['animation_control_edges']=control_edges

        controls={}
        for edge in control_edges:
            ch=edge['control']
            if ch in controls:continue
            cm=c.entry_meta(ch);cb,csrc=c.payload(ch);cr={'control':ch,'meta':cm,'source':csrc}
            if cb is None:
                cr['error']='control payload unavailable';controls[ch]=cr;continue
            try:
                dec=decode_control(cb,None,[]);sel=selected(dec)
                cr.update({'animation_list':dec.get('animation_list'),'state_table':dec.get('state_table'),'selected':sel,
                           'unique_selected_clips':sorted({x['animation'] for x in sel})})
            except Exception as ex:
                cr['error']=f'control decode failed: {ex!r}';controls[ch]=cr;continue
            clips=[]
            for h in cr['unique_selected_clips']:
                m=c.entry_meta(h);b,src=c.payload(h);x={'clip':h,'meta':m,'source':src}
                if not m or norm(m.get('reference',''))!=CLIP or b is None:
                    x['error']='selected clip unavailable/wrong class';clips.append(x);continue
                try:
                    an=filebacked(read_animation,b,ver);hdr=an.animation_header
                    x.update({'frame_count':int(hdr.frame_count),'node_count':int(hdr.node_count),'rig_control_count':int(hdr.rig_control_count),
                              'node_count_matches_skeleton':None if nodes is None else int(hdr.node_count)==nodes})
                except Exception as ex:x['error']=repr(ex)
                clips.append(x)
            cr['selected_clips']=clips;controls[ch]=cr
        row['controls']=controls
        row['literal_control_edge_count']=len(control_edges)
        row['unique_control_count']=len(controls)
        families.append(row)

    out={'schema_version':1,'status':'D1_TOWER_UNRIGGED_ANIMATION_OWNER_DISCOVERY_COMPLETE',
         'family_count':len(families),'families':families,'violations':violations,
         'policy':'Animation owner edges are promoted only when a literal aligned FileHash in a source-owned SEntity EntityResource resolves to exact class 80802C0E. Selected clips are source-decoded. Node-count equality is not treated as retarget proof and no default action or semantic name is inferred.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
    summary=[]
    for r in families:
        summary.append({'family':r['family'],'sentity':r['sentity'],'skeleton_nodes':r.get('skeleton_node_count'),
                        'resources':len(r.get('resource_hashes',[])),'control_edges':r.get('literal_control_edge_count',0),
                        'controls':sorted((r.get('controls') or {}).keys())})
    print(json.dumps({'status':out['status'],'summary':summary,'violations':violations},indent=2))
    return 0 if not violations else 2
if __name__=='__main__':raise SystemExit(main())
