#!/usr/bin/env python3
"""Validate Family-E retarget/local animation ordering and numeric ranges.

The current GLB builder binds local[bone_index] directly to skeleton bone_index.
This probe proves or rejects that assumption from the pinned production parser and
reports transform ranges for both exact owner-selected clips.
"""
from __future__ import annotations
import argparse, io, json, sys, tempfile
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_entry_extract import EntryReader
from d1_tower_family_e_animated_layer import norm, entry_map, exact_payload

SKELETON='809D8613'; RIG='809D856E'; ENTITY_RESOURCE_REF='80800861'; CLIP_REF='808005A1'

def read_anim_filebacked(read_animation,payload,ver):
    with tempfile.NamedTemporaryFile() as f:
        f.write(payload);f.flush();f.seek(0);return read_animation(f,ver)

def stats(arr,kind):
    if arr is None or len(arr)==0:return {'count':0}
    a=np.asarray(arr,dtype=np.float64)
    out={'count':int(len(a)),'finite':bool(np.isfinite(a).all()),'min':float(np.min(a)),'max':float(np.max(a)),'abs_max':float(np.max(np.abs(a)))}
    if a.ndim==2: out['component_min']=[float(x) for x in np.min(a,axis=0)];out['component_max']=[float(x) for x in np.max(a,axis=0)]
    if kind=='rotation' and a.ndim==2 and a.shape[1]==4:
        q=np.linalg.norm(a,axis=1);out['quat_norm_min']=float(q.min());out['quat_norm_max']=float(q.max());out['quat_norm_abs_error_max']=float(np.max(np.abs(q-1.0)))
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-pkg',type=Path,required=True);ap.add_argument('--tower-pkg',type=Path,required=True);ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--parser-root',type=Path,required=True);ap.add_argument('--ownership',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args()
    src=EntryReader(a.source_pkg,a.runtime);tower=EntryReader(a.tower_pkg,a.runtime);sm=entry_map(src);tm=entry_map(tower)
    sys.path.insert(0,str(a.parser_root.resolve()))
    from tag.game_version import Game_Version
    from tag_readers.read_skeleton import read_skeleton
    from tag_readers.read_rig import read_runtime_rig
    from tag_readers.read_animation import read_animation
    from animation_decoding.decode_animation import decode_animation
    from runtime_rig.rig_retarget import rig_retarget
    from animation_export.convert_animation_object_to_local import convert_obj_to_local
    ver=Game_Version.D1_ROI
    _,sb=exact_payload(src,sm,SKELETON,ENTITY_RESOURCE_REF);sk=read_skeleton(io.BytesIO(sb),ver)
    _,rb=exact_payload(src,sm,RIG,ENTITY_RESOURCE_REF);rig=read_runtime_rig(io.BytesIO(rb),ver)
    own=json.loads(a.ownership.read_text());clips=sorted({norm(x.get('expected_animation_clip')) for x in own.get('entities',{}).values()})
    if clips!=['809D8572','80C7AE98']:raise ValueError(f'unexpected Family-E clip set {clips}')
    skeleton_hashes=[f'{int(x.bone_hash)&0xffffffff:08X}' for x in sk.node_defs]
    rows={}; violations=[]
    for clip in clips:
        reader,em=(src,sm) if clip in sm else (tower,tm)
        _,cb=exact_payload(reader,em,clip,CLIP_REF);anim=read_anim_filebacked(read_animation,cb,ver)
        decoded=decode_animation(anim);ret=rig_retarget(anim,decoded,sk,rig);local=convert_obj_to_local(anim,ret,sk)
        if len(local)!=67:violations.append(f'{clip}: local track count {len(local)} != 67')
        track_rows=[]; mismatches=[]
        global_stats={'translation_abs_max':0.0,'scale_abs_max':0.0,'rotation_quat_error_max':0.0,'nonfinite_tracks':0}
        for i,t in enumerate(local):
            th=f'{int(t.bone_name_hash)&0xffffffff:08X}'; expected=skeleton_hashes[i] if i<len(skeleton_hashes) else None
            if th!=expected:mismatches.append({'index':i,'track_hash':th,'skeleton_hash':expected})
            ts=stats(t.translations,'translation');rs=stats(t.rotations,'rotation');ss=stats(t.scales,'scale')
            global_stats['translation_abs_max']=max(global_stats['translation_abs_max'],ts.get('abs_max',0.0));global_stats['scale_abs_max']=max(global_stats['scale_abs_max'],ss.get('abs_max',0.0));global_stats['rotation_quat_error_max']=max(global_stats['rotation_quat_error_max'],rs.get('quat_norm_abs_error_max',0.0))
            if not ts.get('finite',True) or not rs.get('finite',True) or not ss.get('finite',True):global_stats['nonfinite_tracks']+=1
            track_rows.append({'bone_index':i,'track_hash':th,'skeleton_hash':expected,'translation':ts,'rotation':rs,'scale':ss})
        if mismatches:violations.append(f'{clip}: {len(mismatches)} local track hash/order mismatches')
        if global_stats['nonfinite_tracks']:violations.append(f'{clip}: non-finite tracks present')
        rows[clip]={'package_id':f'{int(reader.h["pkg_id"]):04X}','frame_count':int(anim.animation_header.frame_count),'decoded_count':len(decoded),'retargeted_count':len(ret),'local_count':len(local),'track_hash_order_exact':not mismatches,'mismatches':mismatches,'global_stats':global_stats,'tracks':track_rows}
    out={'schema_version':1,'status':'D1_TOWER_FAMILY_E_ANIMATION_SPACE_DIAGNOSTIC_COMPLETE' if not violations else 'D1_TOWER_FAMILY_E_ANIMATION_SPACE_DIAGNOSTIC_PARTIAL','skeleton':SKELETON,'runtime_rig':RIG,'skeleton_hashes':skeleton_hashes,'clips':rows,'violations':violations,'policy':'Directly validates the list-index-to-bone-index assumption used by the GLB builder after production decode -> rig_retarget -> local conversion. No semantic animation labels are inferred.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'violations':violations,'clips':{k:{'frame_count':v['frame_count'],'track_hash_order_exact':v['track_hash_order_exact'],'global_stats':v['global_stats']} for k,v in rows.items()}},indent=2));return 0 if not violations else 2
if __name__=='__main__':raise SystemExit(main())
