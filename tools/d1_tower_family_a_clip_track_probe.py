#!/usr/bin/env python3
"""Compare Family-A selected clip track identity with exact 01E3 skeletons/rigs.

This is diagnostic evidence only. Hash/name matches are reported but never promoted to
ownership without a literal source edge.
"""
from __future__ import annotations
import argparse, io, json, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_entry_extract import EntryReader
from d1_tower_family_f_animation_ownership import norm, entry_map, exact_payload, filebacked, dyn_resources
from d1_animation_retarget_probe import component_rows

ENTITY_RESOURCE_REF='80800861'; CLIP_REF='808005A1'
SENTITY='80C7A05E'; CLIP='80BC648A'; MODEL_SKELETON='80BC60B2'; MODEL_RIG='80BC60B4'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--activity-pkg',type=Path,required=True);ap.add_argument('--cinematic-pkg',type=Path,required=True);ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--parser-root',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args()
    ra=EntryReader(a.activity_pkg,a.runtime);rc=EntryReader(a.cinematic_pkg,a.runtime);ma=entry_map(ra);mc=entry_map(rc)
    sys.path.insert(0,str(a.parser_root.resolve()))
    from tag.game_version import Game_Version
    from tag_readers.read_animation import read_animation
    from tag_readers.read_skeleton import read_skeleton
    from tag_readers.read_rig import read_runtime_rig
    from animation_decoding.decode_animation import decode_animation
    from fnv_hashes.bones_names import convert_hash_to_bungie_name
    ver=Game_Version.D1_ROI

    _,cb=exact_payload(rc,mc,CLIP,CLIP_REF);anim=filebacked(read_animation,cb,ver);tracks=decode_animation(anim)
    decoded=[]
    for i,t in enumerate(tracks):
        h=int(t.bone_name_hash)&0xffffffff
        decoded.append({'track_index':i,'bone_name_hash':f'{h:08X}','bone_name':convert_hash_to_bungie_name(h),
                        'scale_keys':0 if t.scales is None else len(t.scales),'rotation_keys':0 if t.rotations is None else len(t.rotations),'translation_keys':0 if t.translations is None else len(t.translations)})

    _,sb=exact_payload(rc,mc,MODEL_SKELETON,ENTITY_RESOURCE_REF);sk=read_skeleton(io.BytesIO(sb),ver)
    model_bones=[]
    for i,n in enumerate(sk.node_defs):
        h=int(n.bone_hash)&0xffffffff
        model_bones.append({'index':i,'parent':int(n.parent_node_index),'bone_hash':f'{h:08X}','bone_name':convert_hash_to_bungie_name(h)})
    _,rb=exact_payload(rc,mc,MODEL_RIG,ENTITY_RESOURCE_REF);rig=read_runtime_rig(io.BytesIO(rb),ver)
    model_rig={'components':component_rows(rig.rig_components),'control_count':len(rig.controls_relations),
               'bone_to_control':[int(x) for x in rig.bone_to_control], 'control_to_bone':[int(x) for x in rig.control_to_bone],
               'control_name_to_bone_index':[{'hash':f'{int(x.hash)&0xffffffff:08X}','count':int(x.count)} for x in rig.control_name_to_bone_index]}

    one_node=[]; all_rigs=[]
    for e in rc.entries:
        if norm(e['reference'])!=ENTITY_RESOURCE_REF or not rc.available(e['index']): continue
        payload=rc.entry(e['index'])
        try:
            s=read_skeleton(io.BytesIO(payload),ver)
            if len(s.node_defs)==1:
                n=s.node_defs[0];h=int(n.bone_hash)&0xffffffff
                one_node.append({'tag_hash':norm(e['tag_hash']),'entry_index':int(e['index']),'bone_hash':f'{h:08X}','bone_name':convert_hash_to_bungie_name(h),
                                 'matches_decoded_track':any(x['bone_name_hash']==f'{h:08X}' for x in decoded)})
        except Exception: pass
        try:
            rr=read_runtime_rig(io.BytesIO(payload),ver)
            all_rigs.append({'tag_hash':norm(e['tag_hash']),'entry_index':int(e['index']),'control_count':len(rr.controls_relations),
                             'components':component_rows(rr.rig_components),
                             'bone_to_control':[int(x) for x in rr.bone_to_control], 'control_to_bone':[int(x) for x in rr.control_to_bone],
                             'control_name_to_bone_index':[{'hash':f'{int(x.hash)&0xffffffff:08X}','count':int(x.count)} for x in rr.control_name_to_bone_index]})
        except Exception: pass

    _,eb=exact_payload(ra,ma,SENTITY,'80800734');resources=dyn_resources(eb)
    out={'schema_version':1,'status':'D1_TOWER_FAMILY_A_CLIP_TRACK_DIAGNOSTIC_COMPLETE','clip':CLIP,
         'clip_header':{'frame_count':int(anim.animation_header.frame_count),'node_count':int(anim.animation_header.node_count),'rig_control_count':int(anim.animation_header.rig_control_count),'components':component_rows(anim.runtime_rig_components)},
         'decoded_tracks':decoded,'model_skeleton':{'tag_hash':MODEL_SKELETON,'bones':model_bones},'model_runtime_rig':{'tag_hash':MODEL_RIG,**model_rig},
         'one_node_skeletons_01e3':one_node,'runtime_rigs_01e3':all_rigs,'family_a_serialized_resources':resources,
         'track_hash_matches_model_bones':[{'track':x,'bone':b} for x in decoded for b in model_bones if x['bone_name_hash']==b['bone_hash']],
         'track_hash_matches_one_node_skeletons':[{'track':x,'skeleton':s} for x in decoded for s in one_node if x['bone_name_hash']==s['bone_hash']],
         'policy':'Track/bone hash equality is identity evidence only. It does not override runtime-rig component incompatibility or establish a source ownership edge.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'decoded_tracks':decoded,'model_bones':model_bones,'model_rig':model_rig,'one_node_skeletons':one_node,'runtime_rigs':all_rigs,'model_matches':out['track_hash_matches_model_bones'],'one_node_matches':out['track_hash_matches_one_node_skeletons']},indent=2))
if __name__=='__main__':main()
