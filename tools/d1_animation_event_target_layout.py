#!/usr/bin/env python3
"""Exact layout census for D1 animation frame-event pointer targets.

Consumes the source-closed pointer census and studies only offsets:
* target alignment modulo 4/8/16;
* sorted unique target offsets per clip;
* positive deltas between adjacent unique targets;
* whether bounded 32-byte target-prefix windows overlap;
* whether targets fall before, inside, or after the pointer-array byte range.

A GCD/minimum delta is emitted only as a structural candidate. It is not promoted
as a record size because pointers may address subrecords, shared objects, or fields.
"""
from __future__ import annotations
import argparse,collections,json,math
from pathlib import Path

def gcd_all(vals):
    g=0
    for x in vals:g=math.gcd(g,int(x))
    return g

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--events',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    d=json.loads(a.events.read_text());violations=[];rows=[]
    if d.get('status')!='D1_ANIMATION_FRAME_EVENT_POINTER_CENSUS_EXACT' or d.get('violations'):
        violations.append('event pointer census not exact')

    delta_hist=collections.Counter();align={4:collections.Counter(),8:collections.Counter(),16:collections.Counter()}
    all_deltas=[];overlaps=[];region_hist=collections.Counter()
    for r in d.get('rows',[]):
        clip=str(r['clip']).upper();size=int(r['clip_size']);array=int(r['pointer_array_offset']);count=int(r['frame_event_pointer_count'])
        array_end=array+count*8
        pts=[int(p['target_offset']) for p in r.get('pointers',[]) if p.get('target_offset') is not None]
        if any(x<0 or x>=size for x in pts):
            violations.append(f'{clip}: target outside clip bounds')
        uniq=sorted(set(pts))
        deltas=[b-a0 for a0,b in zip(uniq,uniq[1:]) if b>a0]
        for x in deltas:
            delta_hist[x]+=1;all_deltas.append(x)
        local_overlaps=[]
        for a0,b in zip(uniq,uniq[1:]):
            delta=b-a0
            if 0<delta<32:
                rec={'clip':clip,'first_target':a0,'second_target':b,'delta':delta}
                overlaps.append(rec);local_overlaps.append(rec)
        for x in pts:
            for n in align:align[n][x%n]+=1
            if x<array:region='BEFORE_POINTER_ARRAY'
            elif x<array_end:region='INSIDE_POINTER_ARRAY'
            else:region='AFTER_POINTER_ARRAY'
            region_hist[region]+=1
        rows.append({
            'clip':clip,'clip_size':size,
            'pointer_array_offset':array,'pointer_array_end':array_end,
            'pointer_count':count,'nonnull_pointer_count':len(pts),
            'unique_target_count':len(uniq),'unique_target_offsets':uniq,
            'duplicate_target_reference_count':len(pts)-len(uniq),
            'adjacent_positive_target_deltas':deltas,
            'minimum_positive_target_delta':min(deltas) if deltas else None,
            'target_delta_gcd':gcd_all(deltas) if deltas else None,
            'overlapping_32byte_prefix_window_pairs':local_overlaps,
            'target_regions':{
                'before':sum(x<array for x in pts),
                'inside':sum(array<=x<array_end for x in pts),
                'after':sum(x>=array_end for x in pts),
            },
        })

    out={
        'schema':'d1_animation_event_target_layout/v1',
        'status':'D1_ANIMATION_EVENT_TARGET_LAYOUT_EXACT' if rows and not violations else 'D1_ANIMATION_EVENT_TARGET_LAYOUT_PARTIAL',
        'clip_count':len(rows),
        'clips_with_nonnull_targets':sum(x['nonnull_pointer_count']>0 for x in rows),
        'clips_with_duplicate_target_references':sum(x['duplicate_target_reference_count']>0 for x in rows),
        'global_positive_target_delta_histogram':{str(k):v for k,v in sorted(delta_hist.items())},
        'global_minimum_positive_target_delta':min(all_deltas) if all_deltas else None,
        'global_positive_target_delta_gcd':gcd_all(all_deltas) if all_deltas else None,
        'target_alignment_remainders':{
            str(n):{str(k):v for k,v in sorted(h.items())} for n,h in align.items()
        },
        'target_region_histogram':dict(sorted(region_hist.items())),
        'overlapping_32byte_prefix_window_pair_count':len(overlaps),
        'overlapping_32byte_prefix_window_pairs':overlaps,
        'rows':rows,'violations':violations,
        'semantic_boundary':{
            'pointer_and_target_offsets':'EXACT',
            'delta_and_alignment_statistics':'EXACT_ARITHMETIC',
            'candidate_stride_from_gcd':'STRUCTURAL_DIAGNOSTIC_ONLY',
            '32byte_overlap':'BOUNDED_PREFIX_WINDOW_OVERLAP_ONLY',
            'record_size':'WITHHELD',
            'event_record_identity':'WITHHELD',
        },
        'policy':'Offset arithmetic constrains possible layouts but does not turn a target-delta GCD into a record stride. A 32-byte prefix overlap only says the captured windows overlap in clip address space.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({
        'status':out['status'],
        'clips_with_nonnull_targets':out['clips_with_nonnull_targets'],
        'delta_gcd':out['global_positive_target_delta_gcd'],
        'min_delta':out['global_minimum_positive_target_delta'],
        'region_histogram':out['target_region_histogram'],
        'alignments':out['target_alignment_remainders'],
        'prefix_overlap_count':len(overlaps),
        'overlap_preview':overlaps[:20],
        'violations':violations,
    },indent=2))
    return 0 if out['status']=='D1_ANIMATION_EVENT_TARGET_LAYOUT_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
