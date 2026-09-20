#!/usr/bin/env python3
"""Census the unnamed D1 ROI animation-header vector adjacent to frame events.

The pinned parser reads a Vec_Pointer at header 0x130/0x138 and discards it.
d1_remote_spawned_actor_animation_options_v2 now preserves that exact vector,
the following frame-event vector, and rig-components vector.

This tool correlates only exact lengths/addresses and bounded target bytes. It
does not assign an element type, stride, event role, or semantic name.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,struct
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--options',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    d=json.loads(a.options.read_text());v=[];rows=[]
    if d.get('schema')!='d1_remote_spawned_actor_animation_options/v3':
        v.append('options schema not v3')
    if d.get('status')!='D1_ACTIVITY_ACTOR_ANIMATION_OPTIONS_COMPLETE' or d.get('violations'):
        v.append('animation options not exact complete')

    selected=[str(x).upper() for x in d.get('unique_selector_selected_clip_hashes',[])]
    clips={str(k).upper():x for k,x in (d.get('clips') or {}).items()}
    len_hist=collections.Counter();pair_hist=collections.Counter();region_hist=collections.Counter()
    prefix_hist=collections.Counter();stride_candidates=collections.Counter()
    equal_event_count=0;nonzero_unknown=0

    for h in selected:
        cp=clips.get(h)
        if not cp:
            v.append(f'{h}: clip metadata missing');continue
        adj=cp.get('adjacent_header_vectors')
        ev=cp.get('frame_event_pointers')
        if not adj or not ev:
            v.append(f'{h}: adjacent header vectors/frame events missing');continue
        if adj.get('semantic_boundary')!='RAW_D1_ROI_HEADER_VEC_POINTERS_UNNAMED_0X130_ELEMENT_SCHEMA_WITHHELD':
            v.append(f'{h}: adjacent vector semantic boundary drift')
        checks=adj.get('parser_crosschecks') or {}
        if not checks or not all(checks.values()):
            v.append(f'{h}: parser cross-check not fully green')
        u=adj['unnamed_vector'];fe=adj['frame_events_vector'];rg=adj['rig_components_vector']
        ul=int(u['length_u64']);ec=int(ev['count']);fl=int(fe['length_u64'])
        if fl!=ec:v.append(f'{h}: frame-event vector length mismatch {fl}/{ec}')
        rcl=len(cp.get('runtime_components') or [])
        if int(rg['length_u64'])!=rcl:v.append(f'{h}: rig-component vector length mismatch {rg["length_u64"]}/{rcl}')
        len_hist[ul]+=1;pair_hist[(ul,ec)]+=1
        if ul==ec:equal_event_count+=1
        if ul>0:nonzero_unknown+=1
        ut=u.get('target_offset');ft=fe.get('target_offset')
        event_targets=sorted({int(x['target_offset']) for x in ev.get('pointers',[]) if x.get('target_offset') is not None})
        if ut is None:region='NULL'
        elif ft is not None and ut<ft:region='BEFORE_FRAME_POINTER_ARRAY'
        elif ft is not None and ut==ft:region='SAME_AS_FRAME_POINTER_ARRAY'
        elif ft is not None and ut>ft:region='AFTER_FRAME_POINTER_ARRAY'
        else:region='FRAME_POINTER_ARRAY_NULL'
        region_hist[region]+=1

        hx=str(u.get('target_prefix_hex') or '')
        if hx:
            prefix_hist[(hashlib.sha256(bytes.fromhex(hx)).hexdigest(),hx)]+=1

        dist=None;candidate=None
        if ut is not None and ft is not None:
            dist=ft-ut
            if ul>0 and dist>0 and dist%ul==0:
                candidate=dist//ul
                stride_candidates[candidate]+=1

        target_overlap=None
        if ut is not None and event_targets:
            target_overlap={
                'unknown_target_equals_event_target':ut in event_targets,
                'unknown_target_before_min_event_target':ut<min(event_targets),
                'unknown_target_after_max_event_target':ut>max(event_targets),
                'distance_to_nearest_event_target':min(abs(ut-x) for x in event_targets),
            }

        # Pure reinterpretation of the bounded 64-byte prefix for inspection.
        raw=bytes.fromhex(hx) if hx else b''
        u32=[struct.unpack_from('<I',raw,o)[0] for o in range(0,len(raw)-3,4)]
        u64=[struct.unpack_from('<Q',raw,o)[0] for o in range(0,len(raw)-7,8)]
        rows.append({
            'clip':h,'frame_count':int(cp['frame_count']),
            'unnamed_length':ul,'frame_event_pointer_count':ec,
            'rig_component_count':rcl,
            'unnamed_target_offset':ut,
            'frame_pointer_array_target_offset':ft,
            'unnamed_to_frame_pointer_array_distance':dist,
            'distance_divided_by_unnamed_length_if_integral':candidate,
            'event_target_offsets':event_targets,
            'unknown_target_event_target_relation':target_overlap,
            'unnamed_target_prefix_sha256':None if not raw else hashlib.sha256(raw).hexdigest(),
            'unnamed_target_prefix_byte_count':len(raw),
            'unnamed_prefix_u32':u32,
            'unnamed_prefix_u64':u64,
        })

    out={
        'schema':'d1_animation_header_unnamed_vector_census/v1',
        'status':'D1_ANIMATION_HEADER_UNNAMED_VECTOR_CENSUS_EXACT' if len(rows)==len(selected) and not v else 'D1_ANIMATION_HEADER_UNNAMED_VECTOR_CENSUS_PARTIAL',
        'clip_count':len(rows),
        'nonzero_unnamed_vector_clip_count':nonzero_unknown,
        'unnamed_length_histogram':{str(k):n for k,n in sorted(len_hist.items())},
        'unnamed_length_frame_event_count_pair_histogram':[
            {'unnamed_length':a0,'frame_event_pointer_count':b,'clip_count':n}
            for (a0,b),n in sorted(pair_hist.items())
        ],
        'unnamed_length_equals_frame_event_count_clip_count':equal_event_count,
        'target_region_histogram':dict(sorted(region_hist.items())),
        'integral_distance_per_element_candidate_histogram':{str(k):n for k,n in sorted(stride_candidates.items())},
        'unique_nonnull_prefix_count':len(prefix_hist),
        'prefix_groups':[
            {'sha256':sha,'prefix_hex':hx,'clip_count':n}
            for (sha,hx),n in sorted(prefix_hist.items(),key=lambda x:(-x[1],x[0][0]))
        ],
        'rows':rows,'violations':v,
        'semantic_boundary':{
            'header_offsets_and_vec_pointer_words':'EXACT_D1_ROI_LAYOUT',
            'bounded_target_prefix':'EXACT_BYTES',
            'count_and_address_correlations':'EXACT_ARITHMETIC',
            'integral_distance_per_element_candidate':'STRUCTURAL_DIAGNOSTIC_ONLY',
            'unnamed_vector_element_stride':'WITHHELD',
            'unnamed_vector_element_type':'WITHHELD',
            'relationship_to_frame_events':'WITHHELD_UNLESS_CORRELATION_BECOMES_CONCLUSIVE',
        },
        'policy':'The vector at header 0x130 is preserved because the pinned parser reads it but discards it. Count/address equality or integral spacing is reported mechanically and is not sufficient to name the vector or its element schema.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({
        'status':out['status'],'clip_count':len(rows),
        'nonzero':nonzero_unknown,'length_hist':out['unnamed_length_histogram'],
        'pairs':out['unnamed_length_frame_event_count_pair_histogram'],
        'equal_event_count':equal_event_count,'regions':out['target_region_histogram'],
        'distance_candidates':out['integral_distance_per_element_candidate_histogram'],
        'violations':v,
    },indent=2))
    return 0 if out['status']=='D1_ANIMATION_HEADER_UNNAMED_VECTOR_CENSUS_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
