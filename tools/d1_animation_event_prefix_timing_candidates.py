#!/usr/bin/env python3
"""Correlate exact animation event-prefix lanes with the proven 30:1 timing relation.

For every aligned 32-bit lane in the first 32 bytes of each non-null frame-event
target, interpret the exact bytes as both little-endian u32 and IEEE754 float32.

The tool computes structural diagnostics:
* u32 bounded by frame_count / frame_intervals;
* u32 monotonicity by pointer ordinal within multi-pointer clips;
* finite nonnegative float32 values;
* whether float32*30 lies on an integer frame grid;
* whether float32*30 lies within that clip's frame interval range;
* float32 monotonicity by pointer ordinal.

Candidate labels are heuristics only. They do not promote a field name, record size,
event type, or event behavior.
"""
from __future__ import annotations
import argparse,collections,json,math,struct
from pathlib import Path

OFFSETS=tuple(range(0,32,4))
GRID_TOL=1e-5

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--events',type=Path,required=True)
    ap.add_argument('--timing',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()

    ev=json.loads(a.events.read_text());tm=json.loads(a.timing.read_text());violations=[]
    if ev.get('status')!='D1_ANIMATION_FRAME_EVENT_POINTER_CENSUS_EXACT' or ev.get('violations'):
        violations.append('event pointer census not exact')
    if tm.get('status')!='D1_ANIMATION_STATE_SCALAR_TIMING_RATIO_EXACT' or tm.get('violations'):
        violations.append('timing proof not exact')
    ratio=float(tm.get('ratio_frame_intervals_per_scalar_unit',0.0))
    if ratio!=30.0:violations.append(f'timing ratio drift {ratio}')

    samples=[];byclip=collections.defaultdict(list)
    for row in ev.get('rows',[]):
        clip=str(row['clip']).upper();fc=int(row['frame_count']);fi=max(0,fc-1)
        for p in row.get('pointers',[]):
            if p.get('target_offset') is None:continue
            hx=str(p.get('target_prefix_hex') or '')
            try:raw=bytes.fromhex(hx)
            except Exception as ex:
                violations.append(f'{clip}:{p.get("index")}: bad prefix hex {ex}');continue
            if len(raw)<32:
                violations.append(f'{clip}:{p.get("index")}: prefix <32 bytes');continue
            s={'clip':clip,'frame_count':fc,'frame_intervals':fi,
               'pointer_index':int(p['index']),'raw':raw[:32]}
            samples.append(s);byclip[clip].append(s)

    lanes={}
    for off in OFFSETS:
        uvals=[];fvals=[];u_lt_fc=u_le_fi=0
        f_finite_nonneg=f_grid=f_in_range=0
        for s in samples:
            u=struct.unpack_from('<I',s['raw'],off)[0]
            f=struct.unpack_from('<f',s['raw'],off)[0]
            uvals.append((s,u));fvals.append((s,f))
            u_lt_fc += u < s['frame_count']
            u_le_fi += u <= s['frame_intervals']
            if math.isfinite(f) and f>=0:
                f_finite_nonneg+=1
                frames=f*ratio
                nearest=round(frames)
                if abs(frames-nearest)<=GRID_TOL:f_grid+=1
                if -GRID_TOL <= frames <= s['frame_intervals']+GRID_TOL:f_in_range+=1

        multi=0;u_nondec=u_strict=f_nondec=f_strict=0
        for clip,rows in byclip.items():
            rr=sorted(rows,key=lambda x:x['pointer_index'])
            if len(rr)<2:continue
            multi+=1
            us=[struct.unpack_from('<I',x['raw'],off)[0] for x in rr]
            fs=[struct.unpack_from('<f',x['raw'],off)[0] for x in rr]
            u_nondec+=all(b>=a for a,b in zip(us,us[1:]))
            u_strict+=all(b>a for a,b in zip(us,us[1:]))
            if all(math.isfinite(x) for x in fs):
                f_nondec+=all(b>=a for a,b in zip(fs,fs[1:]))
                f_strict+=all(b>a for a,b in zip(fs,fs[1:]))

        n=len(samples)
        u_counter=collections.Counter(v for _,v in uvals)
        finite_f=[f for _,f in fvals if math.isfinite(f)]
        row={
            'offset':off,'sample_count':n,
            'u32':{
                'distinct_value_count':len(u_counter),
                'min':min((v for _,v in uvals),default=None),
                'max':max((v for _,v in uvals),default=None),
                'value_lt_frame_count_fraction':u_lt_fc/n if n else None,
                'value_le_frame_intervals_fraction':u_le_fi/n if n else None,
                'multi_pointer_clip_count':multi,
                'monotonic_nondecreasing_clip_count':u_nondec,
                'strictly_increasing_clip_count':u_strict,
                'top_values':[{'value':v,'count':c} for v,c in u_counter.most_common(12)],
            },
            'f32':{
                'finite_nonnegative_fraction':f_finite_nonneg/n if n else None,
                'times30_integer_grid_fraction':f_grid/n if n else None,
                'times30_within_frame_intervals_fraction':f_in_range/n if n else None,
                'finite_min':min(finite_f,default=None),
                'finite_max':max(finite_f,default=None),
                'multi_pointer_clip_count':multi,
                'monotonic_nondecreasing_clip_count':f_nondec,
                'strictly_increasing_clip_count':f_strict,
            },
        }
        lanes[f'0x{off:02X}']=row

    u_candidates=[];f_candidates=[]
    for k,r in lanes.items():
        u=r['u32'];f=r['f32']
        if (u['distinct_value_count']>1 and
            u['value_le_frame_intervals_fraction']==1.0 and
            (u['multi_pointer_clip_count']==0 or u['monotonic_nondecreasing_clip_count']==u['multi_pointer_clip_count'])):
            u_candidates.append(k)
        if (f['finite_nonnegative_fraction']==1.0 and
            f['times30_integer_grid_fraction']==1.0 and
            f['times30_within_frame_intervals_fraction']==1.0 and
            (f['multi_pointer_clip_count']==0 or f['monotonic_nondecreasing_clip_count']==f['multi_pointer_clip_count'])):
            f_candidates.append(k)

    out={
        'schema':'d1_animation_event_prefix_timing_candidates/v1',
        'status':'D1_ANIMATION_EVENT_PREFIX_TIMING_CANDIDATES_EXACT' if samples and not violations else 'D1_ANIMATION_EVENT_PREFIX_TIMING_CANDIDATES_PARTIAL',
        'sample_count':len(samples),'event_bearing_clip_count':len(byclip),
        'ratio_frame_intervals_per_scalar_unit':ratio,
        'lanes':lanes,
        'u32_frame_bounded_monotonic_candidate_offsets':u_candidates,
        'f32_30hz_grid_bounded_monotonic_candidate_offsets':f_candidates,
        'violations':violations,
        'semantic_boundary':{
            'lane_bytes':'EXACT',
            'u32_and_f32_interpretations':'EXACT_REINTERPRETATION',
            '30hz_ratio':'EXACT_RETAIL_CORRELATION_FROM_SEPARATE_PROOF',
            'candidate_offsets':'STRUCTURAL_HEURISTIC_ONLY',
            'frame_or_time_field_identity':'WITHHELD',
            'record_size':'WITHHELD',
            'event_type_and_behavior':'WITHHELD',
        },
        'policy':'A candidate offset must satisfy exact byte reinterpretation plus clip-bound/grid/ordinal diagnostics. Passing those diagnostics is not sufficient to name a field; it only narrows the record-layout frontier.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'samples':len(samples),
                      'u32_candidates':u_candidates,'f32_candidates':f_candidates,
                      'candidate_rows':{k:lanes[k] for k in sorted(set(u_candidates+f_candidates))},
                      'violations':violations},indent=2))
    return 0 if out['status']=='D1_ANIMATION_EVENT_PREFIX_TIMING_CANDIDATES_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
