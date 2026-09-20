#!/usr/bin/env python3
"""Group exact Crota retargeted clips by structural motion signatures.

A signature contains only source-closed decoded facts:
* frame_count;
* target track indices with dynamic scale;
* target track indices with dynamic rotation;
* target track indices with dynamic translation.

Equal structural signatures mean equal channel-occupancy structure at equal frame count.
The upstream motion summary also carries a canonical SHA256 of the complete decoded
local transform arrays, so this census can separately identify byte-identical decoded
curves under the pinned parser/retarget/localize pipeline. Neither relation assigns a
behavioral identity.
"""
from __future__ import annotations
import argparse,collections,hashlib,json
from pathlib import Path

def stable(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--motion-census',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    d=json.loads(a.motion_census.read_text());v=[];rows=[]
    if d.get('status')!='D1_ANIMATION_MOTION_CENSUS_EXACT' or d.get('missing_motion_summary_count'):
        v.append('motion census not exact')

    bysig=collections.defaultdict(list);byoccupancy=collections.defaultdict(list);bycurve=collections.defaultdict(list)
    for r in d.get('rows',[]):
        m=r.get('local_motion_summary') or {}
        if m.get('semantic_boundary')!='LOCAL_SPACE_VARIATION_ONLY_BONE0_NOT_NAMED_ROOT_MOTION':
            v.append(f"{r.get('clip')}: motion semantic boundary drift");continue
        sig={
            'frame_count':int(r['frame_count']),
            'dynamic_scale_track_indices':[int(x) for x in m.get('dynamic_scale_track_indices',[])],
            'dynamic_rotation_track_indices':[int(x) for x in m.get('dynamic_rotation_track_indices',[])],
            'dynamic_translation_track_indices':[int(x) for x in m.get('dynamic_translation_track_indices',[])],
        }
        occupancy={k:sig[k] for k in (
            'dynamic_scale_track_indices','dynamic_rotation_track_indices','dynamic_translation_track_indices'
        )}
        sh=stable(sig);oh=stable(occupancy)
        curve=str(m.get('decoded_local_curve_sha256') or '')
        if len(curve)!=64 or curve.lower()!=curve or any(ch not in '0123456789abcdef' for ch in curve):
            v.append(f"{r.get('clip')}: invalid decoded local curve sha256 {curve!r}")
            continue
        if m.get('decoded_local_curve_hash_basis')!='D1_DECODED_LOCAL_CURVE_V1_CANONICAL_LE_FLOAT64_ARRAY_BYTES':
            v.append(f"{r.get('clip')}: decoded curve hash basis drift")
            continue
        payload=str(r.get('source_clip_payload_sha256') or '')
        if len(payload)!=64 or payload.lower()!=payload or any(ch not in '0123456789abcdef' for ch in payload):
            v.append(f"{r.get('clip')}: invalid source clip payload sha256 {payload!r}")
            continue
        row={
            'target_id':r.get('target_id'),'control':r.get('control'),'clip':r.get('clip'),
            'frame_count':sig['frame_count'],'source_dimensions_exact':bool(r.get('source_dimensions_exact')),
            'source_clip_payload_sha256':payload,
            'motion_signature_sha256':sh,'occupancy_signature_sha256':oh,
            'decoded_local_curve_sha256':curve,
            'signature':sig,
        }
        rows.append(row);bysig[sh].append(row);byoccupancy[oh].append(row);bycurve[curve].append(row)

    def groups(src,include_sig):
        out=[]
        for h,rr in src.items():
            clips=sorted({str(x['clip']) for x in rr})
            targets=sorted({str(x['target_id']) for x in rr})
            controls=sorted({str(x['control']) for x in rr})
            q={
                'signature_sha256':h,'clip_instance_count':len(rr),
                'unique_clip_count':len(clips),'clips':clips,
                'target_ids':targets,'controls':controls,
            }
            if include_sig:q['signature']=rr[0]['signature']
            else:
                q['occupancy']={k:rr[0]['signature'][k] for k in (
                    'dynamic_scale_track_indices','dynamic_rotation_track_indices','dynamic_translation_track_indices'
                )}
                q['frame_counts']=sorted({int(x['frame_count']) for x in rr})
            out.append(q)
        return sorted(out,key=lambda x:(-x['unique_clip_count'],-x['clip_instance_count'],x['signature_sha256']))

    exact_groups=groups(bysig,True);occ_groups=groups(byoccupancy,False)
    curve_groups=[]
    for h,rr in bycurve.items():
        clips=sorted({str(x['clip']) for x in rr})
        curve_groups.append({
            'decoded_local_curve_sha256':h,
            'clip_instance_count':len(rr),
            'unique_clip_count':len(clips),
            'clips':clips,
            'target_ids':sorted({str(x['target_id']) for x in rr}),
            'controls':sorted({str(x['control']) for x in rr}),
            'frame_counts':sorted({int(x['frame_count']) for x in rr}),
        })
    curve_groups.sort(key=lambda x:(-x['unique_clip_count'],-x['clip_instance_count'],x['decoded_local_curve_sha256']))
    out={
        'schema':'d1_animation_motion_signature_census/v1',
        'status':'D1_ANIMATION_MOTION_SIGNATURE_CENSUS_EXACT' if rows and not v else 'D1_ANIMATION_MOTION_SIGNATURE_CENSUS_PARTIAL',
        'clip_instance_count':len(rows),
        'unique_clip_count':len({x['clip'] for x in rows}),
        'exact_signature_group_count':len(exact_groups),
        'occupancy_signature_group_count':len(occ_groups),
        'decoded_curve_group_count':len(curve_groups),
        'multi_clip_exact_signature_groups':[x for x in exact_groups if x['unique_clip_count']>1],
        'multi_clip_occupancy_signature_groups':[x for x in occ_groups if x['unique_clip_count']>1],
        'multi_clip_decoded_curve_groups':[x for x in curve_groups if x['unique_clip_count']>1],
        'exact_signature_groups':exact_groups,
        'occupancy_signature_groups':occ_groups,
        'decoded_curve_groups':curve_groups,
        'rows':rows,'violations':v,
        'semantic_boundary':{
            'frame_count_and_dynamic_track_sets':'EXACT_DECODED_RETARGETED_STRUCTURE',
            'equal_signature':'EQUAL_CHANNEL_OCCUPANCY_STRUCTURE_ONLY',
            'decoded_curve_hash':'SHA256_OF_CANONICAL_COMPLETE_LOCAL_SCALE_ROTATION_TRANSLATION_ARRAYS',
            'equal_decoded_curve_hash':'BYTE_EQUAL_CANONICAL_DECODED_LOCAL_ARRAYS_UNDER_PINNED_PIPELINE',
            'source_clip_payload_sha256':'EXACT_RETAIL_PAYLOAD_BYTES',
            'source_compressed_clip_byte_equality':'PROVEN_ONLY_WHEN_SOURCE_PAYLOAD_SHA256_MATCHES',
            'behavioral_clip_label':'WITHHELD',
        },
        'policy':'Structural signatures are intentionally weaker than decoded-curve equality. A shared decoded curve hash means the canonical decoded local arrays are byte-identical under the pinned pipeline. Exact source-payload equality is tracked separately by SHA256, so different compressed resources that converge to the same decoded motion remain distinguishable. No grouping establishes behavioral meaning.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({
        'status':out['status'],'instances':len(rows),'unique_clips':out['unique_clip_count'],
        'exact_signature_groups':len(exact_groups),'occupancy_groups':len(occ_groups),'decoded_curve_groups':len(curve_groups),
        'multi_clip_exact_groups':[{
            'clips':x['clips'],'instances':x['clip_instance_count'],'frame_count':x['signature']['frame_count']
        } for x in out['multi_clip_exact_signature_groups']],
        'multi_clip_occupancy_groups':[{
            'clips':x['clips'],'frame_counts':x['frame_counts']
        } for x in out['multi_clip_occupancy_signature_groups']],
        'multi_clip_decoded_curve_groups':[{
            'clips':x['clips'],'instances':x['clip_instance_count'],'frame_counts':x['frame_counts'],
            'sha256':x['decoded_local_curve_sha256']
        } for x in out['multi_clip_decoded_curve_groups']],
        'violations':v,
    },indent=2))
    return 0 if out['status']=='D1_ANIMATION_MOTION_SIGNATURE_CENSUS_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
