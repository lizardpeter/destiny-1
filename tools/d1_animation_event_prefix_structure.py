#!/usr/bin/env python3
"""Structural census of bounded D1 animation frame-event target prefixes.

Consumes the exact pointer-prefix census and examines the first 32 bytes only.
For every aligned u8/u16/u32/u64 lane it records:
- zero/nonzero frequency;
- distinct-value count;
- min/max;
- most common values;
- whether the value is less than frame_count or frame_intervals;
- per-clip monotonicity across pointer ordinal.

These are structural diagnostics only.  No lane is called frame/time/opcode/type
without independent source evidence.
"""
from __future__ import annotations
import argparse,collections,json,struct
from pathlib import Path

WIDTHS=(1,2,4,8)

def unpack(raw:bytes,off:int,w:int)->int:
    if w==1:return raw[off]
    if w==2:return struct.unpack_from('<H',raw,off)[0]
    if w==4:return struct.unpack_from('<I',raw,off)[0]
    if w==8:return struct.unpack_from('<Q',raw,off)[0]
    raise ValueError(w)

def lane_key(w,off):return f'u{w*8}@0x{off:02X}'

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--events',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    d=json.loads(a.events.read_text())
    violations=[]
    if d.get('status')!='D1_ANIMATION_FRAME_EVENT_POINTER_CENSUS_EXACT' or d.get('violations'):
        violations.append('event pointer census not exact')

    samples=[]
    per_clip=collections.defaultdict(list)
    for row in d.get('rows',[]):
        clip=str(row['clip']).upper()
        fc=int(row['frame_count']); fi=max(0,fc-1)
        for p in row.get('pointers',[]):
            if p.get('target_offset') is None:
                continue
            hx=str(p.get('target_prefix_hex') or '')
            try:raw=bytes.fromhex(hx)
            except Exception as ex:
                violations.append(f'{clip}:{p.get("index")}: bad hex {ex}')
                continue
            if len(raw)<32:
                violations.append(f'{clip}:{p.get("index")}: prefix shorter than 32 bytes ({len(raw)})')
                continue
            s={'clip':clip,'frame_count':fc,'frame_intervals':fi,'pointer_index':int(p['index']),'raw':raw[:32]}
            samples.append(s);per_clip[clip].append(s)

    lanes={}
    for w in WIDTHS:
        for off in range(0,32,w):
            vals=[];lt_fc=0;le_fi=0;zero=0
            for s in samples:
                v=unpack(s['raw'],off,w);vals.append(v)
                zero+=v==0
                lt_fc+=v < s['frame_count']
                le_fi+=v <= s['frame_intervals']
            c=collections.Counter(vals)
            monotonic_nondec=0;monotonic_strict=0;eligible=0
            for clip,rows in per_clip.items():
                rr=sorted(rows,key=lambda x:x['pointer_index'])
                if len(rr)<2:continue
                eligible+=1
                seq=[unpack(x['raw'],off,w) for x in rr]
                monotonic_nondec+=all(b>=a for a,b in zip(seq,seq[1:]))
                monotonic_strict+=all(b>a for a,b in zip(seq,seq[1:]))
            lanes[lane_key(w,off)]={
                'width_bytes':w,'offset':off,'sample_count':len(vals),
                'zero_count':zero,'zero_fraction':(zero/len(vals) if vals else None),
                'distinct_value_count':len(c),
                'min':min(vals) if vals else None,'max':max(vals) if vals else None,
                'top_values':[{'value':v,'count':n} for v,n in c.most_common(12)],
                'value_lt_frame_count_count':lt_fc,
                'value_lt_frame_count_fraction':(lt_fc/len(vals) if vals else None),
                'value_le_frame_intervals_count':le_fi,
                'value_le_frame_intervals_fraction':(le_fi/len(vals) if vals else None),
                'multi_pointer_clip_count':eligible,
                'monotonic_nondecreasing_clip_count':monotonic_nondec,
                'strictly_increasing_clip_count':monotonic_strict,
            }

    candidate=[]
    for k,r in lanes.items():
        n=r['sample_count'] or 0
        if not n:continue
        # Purely structural candidate flag.  This is not a semantic promotion.
        if r['distinct_value_count']>1 and r['value_lt_frame_count_fraction']>=0.95:
            candidate.append(k)

    byte_signatures=collections.Counter(x['raw'].hex() for x in samples)
    out={
        'schema':'d1_animation_event_prefix_structure/v1',
        'status':'D1_ANIMATION_EVENT_PREFIX_STRUCTURE_EXACT' if samples and not violations else 'D1_ANIMATION_EVENT_PREFIX_STRUCTURE_PARTIAL',
        'sample_count':len(samples),
        'clip_count_with_nonnull_event_targets':len(per_clip),
        'unique_32byte_prefix_count':len(byte_signatures),
        'duplicate_32byte_prefix_sample_count':sum(n for n in byte_signatures.values() if n>1),
        'lanes':lanes,
        'frame_bounded_candidate_lanes':candidate,
        'prefix_groups':[{'prefix_hex':hx,'occurrence_count':n} for hx,n in byte_signatures.most_common()],
        'violations':violations,
        'semantic_boundary':{
            'aligned_word_values':'EXACT_BYTES',
            'frame_bounded_candidate_lanes':'STRUCTURAL_HEURISTIC_ONLY',
            'record_size':'WITHHELD',
            'field_names':'WITHHELD',
            'frame_field':'WITHHELD',
            'event_type':'WITHHELD',
        },
        'policy':'All word values are direct little-endian views of the exact first 32 target bytes. Candidate lanes are statistical diagnostics only and are not promoted to event fields.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2)+'\n')
    shortlist={k:lanes[k] for k in candidate}
    print(json.dumps({'status':out['status'],'sample_count':len(samples),
                      'unique_prefixes':out['unique_32byte_prefix_count'],
                      'frame_bounded_candidate_lanes':candidate,
                      'candidate_stats':shortlist,'violations':violations},indent=2))
    return 0 if out['status']=='D1_ANIMATION_EVENT_PREFIX_STRUCTURE_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
