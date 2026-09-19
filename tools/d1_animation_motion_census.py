#!/usr/bin/env python3
"""Census exact retargeted D1 animation motion variation from v3 outputs.

Input motion summaries are generated from the pinned native decode -> retarget ->
local-space conversion.  This tool aggregates only numerical variation.  It does
not label clips as idle/walk/attack, does not assume a sample rate, and does not
rename bone 0 translation as root motion.
"""
from __future__ import annotations
import argparse, collections, json, math
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('input',type=Path)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    d=json.loads(a.input.read_text())
    if d.get('schema')!='d1_remote_spawned_actor_animation_options/v3':
        raise SystemExit('expected animation options v3')
    rows=[]; missing=[]; frames=collections.Counter(); dyn_any=collections.Counter()
    dyn_t=collections.Counter(); dyn_r=collections.Counter(); dyn_s=collections.Counter()
    animated_codecs=collections.Counter(); static_codecs=collections.Counter()
    control_map_shapes=collections.Counter()
    exact_dims=retargeted=0
    for target in d.get('targets',[]):
        tid=target.get('target_id')
        for clip in target.get('clips',[]) or []:
            if not clip.get('retarget_success'):
                continue
            m=clip.get('local_motion_summary')
            if not m:
                missing.append({'target_id':tid,'clip':clip.get('clip')})
                continue
            if m.get('semantic_boundary')!='LOCAL_SPACE_VARIATION_ONLY_BONE0_NOT_NAMED_ROOT_MOTION':
                missing.append({'target_id':tid,'clip':clip.get('clip'),'reason':'motion semantic boundary drift'})
                continue
            fc=int(clip['frame_count']); frames[fc]+=1
            ac=clip.get('source_animated_codec')
            sc=clip.get('source_static_codec')
            animated_codecs[str(None if ac is None else ac.get('codec_type'))]+=1
            static_codecs[str(None if sc is None else sc.get('codec_type'))]+=1
            maps=clip.get('source_control_map_counts') or {}
            mapshape=tuple(int(maps.get(k,0)) for k in ('static_scale','static_rotation','static_translation','animated_scale','animated_rotation','animated_translation'))
            control_map_shapes[str(mapshape)]+=1
            dyn_any[int(m['dynamic_any_track_count'])]+=1
            dyn_t[int(m['dynamic_translation_track_count'])]+=1
            dyn_r[int(m['dynamic_rotation_track_count'])]+=1
            dyn_s[int(m['dynamic_scale_track_count'])]+=1
            if clip.get('source_dimensions_exact'): exact_dims+=1
            else: retargeted+=1
            rows.append({
                'target_id':tid,'control':target.get('control'),'clip':clip.get('clip'),
                'frame_count':fc,
                'source_node_count':int(clip['source_node_count']),
                'source_rig_control_count':int(clip['source_rig_control_count']),
                'target_node_count':int(clip['target_node_count']),
                'target_rig_control_count':int(clip['target_rig_control_count']),
                'source_dimensions_exact':bool(clip.get('source_dimensions_exact')),
                'source_animation_hash':clip.get('source_animation_hash'),
                'source_static_codec':sc,
                'source_animated_codec':ac,
                'source_control_map_counts':maps,
                'local_motion_summary':m,
            })
    b0=[float(x['local_motion_summary'].get('bone0_translation_syntax',{}).get('translation_end_displacement',0.0)) for x in rows]
    bp=[float(x['local_motion_summary'].get('bone0_translation_syntax',{}).get('translation_peak_displacement_from_start',0.0)) for x in rows]
    out={
        'schema':'d1_animation_motion_census/v1',
        'status':'D1_ANIMATION_MOTION_CENSUS_EXACT' if rows and not missing else 'D1_ANIMATION_MOTION_CENSUS_PARTIAL',
        'source_status':d.get('status'),
        'successful_clip_instance_count':len(rows),
        'missing_motion_summary_count':len(missing),
        'missing_motion_summaries':missing,
        'frame_count_histogram':{str(k):v for k,v in sorted(frames.items())},
        'dynamic_any_track_count_histogram':{str(k):v for k,v in sorted(dyn_any.items())},
        'dynamic_translation_track_count_histogram':{str(k):v for k,v in sorted(dyn_t.items())},
        'dynamic_rotation_track_count_histogram':{str(k):v for k,v in sorted(dyn_r.items())},
        'dynamic_scale_track_count_histogram':{str(k):v for k,v in sorted(dyn_s.items())},
        'animated_codec_type_histogram':dict(sorted(animated_codecs.items())),
        'static_codec_type_histogram':dict(sorted(static_codecs.items())),
        'control_map_shape_histogram':dict(sorted(control_map_shapes.items())),
        'source_dimension_exact_clip_instance_count':exact_dims,
        'native_retarget_required_clip_instance_count':retargeted,
        'bone0_translation_end_displacement_range':[min(b0),max(b0)] if b0 else None,
        'bone0_translation_peak_displacement_range':[min(bp),max(bp)] if bp else None,
        'sample_rate_hz':'WITHHELD',
        'behavioral_clip_names':'WITHHELD',
        'bone0_semantic':'WITHHELD',
        'rows':rows,
        'policy':'Frame counts and local-space numerical track variation are exact consequences of the pinned decode/retarget/localize path. Timing in seconds, behavioral clip labels, and bone-0/root-motion semantics remain withheld without independent evidence.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','successful_clip_instance_count','missing_motion_summary_count','frame_count_histogram','dynamic_any_track_count_histogram','animated_codec_type_histogram','static_codec_type_histogram','control_map_shape_histogram','source_dimension_exact_clip_instance_count','native_retarget_required_clip_instance_count','bone0_translation_end_displacement_range')},indent=2))
    return 0 if out['status']=='D1_ANIMATION_MOTION_CENSUS_EXACT' else 2

if __name__=='__main__': raise SystemExit(main())
