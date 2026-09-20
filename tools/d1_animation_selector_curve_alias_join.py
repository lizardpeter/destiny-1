#!/usr/bin/env python3
"""Join exact selector-state aliases to complete decoded local animation curves.

This separates three distinct forms of reuse:
1. state records selecting the exact same FileHash sequence;
2. different selected FileHash sequences that map to byte-identical canonical
   decoded local curves under the pinned retarget/localize pipeline;
3. merely similar structural motion signatures (reported upstream, not collapsed here).

The join is control-aware: a selected clip is resolved against motion rows for the
same decoded control.  No state/clip behavioral names are inferred.
"""
from __future__ import annotations
import argparse,collections,json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--aliases',type=Path,required=True)
    ap.add_argument('--motion-signatures',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    al=json.loads(a.aliases.read_text())
    mo=json.loads(a.motion_signatures.read_text())
    v=[]

    if al.get('status')!='D1_ANIMATION_SELECTOR_ALIAS_CENSUS_EXACT' or al.get('violations'):
        v.append('selector alias census not exact')
    if mo.get('status')!='D1_ANIMATION_MOTION_SIGNATURE_CENSUS_EXACT' or mo.get('violations'):
        v.append('motion signature census not exact')

    by_control_clip=collections.defaultdict(set)
    by_control_clip_payload=collections.defaultdict(set)
    clip_to_curves=collections.defaultdict(set)
    clip_to_payloads=collections.defaultdict(set)
    for r in mo.get('rows',[]):
        key=(str(r.get('control')),str(r.get('clip')))
        h=str(r.get('decoded_local_curve_sha256') or '')
        p=str(r.get('source_clip_payload_sha256') or '')
        by_control_clip[key].add(h)
        by_control_clip_payload[key].add(p)
        clip_to_curves[str(r.get('clip'))].add(h)
        clip_to_payloads[str(r.get('clip'))].add(p)

    # Same control+clip must decode to one canonical local curve. Multiple target
    # instances are allowed only when they are curve-identical.
    ambiguous_control_clip=[]
    ambiguous_control_clip_payload=[]
    for (ctl,clip),hs in sorted(by_control_clip.items()):
        if len(hs)!=1:
            ambiguous_control_clip.append({'control':ctl,'clip':clip,'curve_hashes':sorted(hs)})
        ps=by_control_clip_payload.get((ctl,clip),set())
        if len(ps)!=1:
            ambiguous_control_clip_payload.append({'control':ctl,'clip':clip,'payload_hashes':sorted(ps)})
    if ambiguous_control_clip:
        v.append(f'{len(ambiguous_control_clip)} control+clip keys have multiple decoded curves')
    if ambiguous_control_clip_payload:
        v.append(f'{len(ambiguous_control_clip_payload)} control+clip keys have multiple source payload hashes')

    records=[]
    by_curve_sequence=collections.defaultdict(list)
    unresolved=[]
    for g in al.get('selected_sequence_groups',[]):
        seq=[str(x) for x in g.get('selected_clip_sequence',[])]
        for rec in g.get('records',[]):
            ctl=str(rec.get('control'))
            curve_seq=[];payload_seq=[]
            ok=True
            for clip in seq:
                hs=by_control_clip.get((ctl,clip),set())
                ps=by_control_clip_payload.get((ctl,clip),set())
                if len(hs)!=1 or len(ps)!=1:
                    unresolved.append({
                        'control':ctl,'state_hash':rec.get('state_hash'),'clip':clip,
                        'curve_hashes':sorted(hs),'payload_hashes':sorted(ps),
                    })
                    ok=False
                    break
                curve_seq.append(next(iter(hs)));payload_seq.append(next(iter(ps)))
            if not ok:
                continue
            row={
                'entity':rec.get('entity'),'control':ctl,
                'record_index':int(rec.get('record_index',-1)),
                'state_hash':rec.get('state_hash'),
                'scalar_f32':float(rec.get('scalar_f32',0.0)),
                'selection_kind':rec.get('selection_kind'),
                'selected_clip_sequence':seq,
                'source_payload_sha256_sequence':payload_seq,
                'decoded_curve_sequence':curve_seq,
            }
            records.append(row)
            by_curve_sequence[tuple(curve_seq)].append(row)
    if unresolved:
        v.append(f'{len(unresolved)} selector clip references lack a unique control-local decoded curve')

    curve_sequence_groups=[]
    for seq,rr in by_curve_sequence.items():
        clip_sequences=sorted({tuple(x['selected_clip_sequence']) for x in rr})
        states=sorted({str(x['state_hash']) for x in rr})
        controls=sorted({str(x['control']) for x in rr})
        curve_sequence_groups.append({
            'decoded_curve_sequence':list(seq),
            'state_record_count':len(rr),
            'state_hashes':states,
            'controls':controls,
            'unique_selected_clip_sequence_count':len(clip_sequences),
            'selected_clip_sequences':[list(x) for x in clip_sequences],
            'cross_filehash_curve_alias':len(clip_sequences)>1,
        })
    curve_sequence_groups.sort(key=lambda x:(
        -x['unique_selected_clip_sequence_count'],-x['state_record_count'],x['decoded_curve_sequence']
    ))

    # Global clip FileHash aliases by exact decoded curve. This is weaker than
    # source payload equality but stronger than structural occupancy equality.
    curve_to_clips=collections.defaultdict(set)
    curve_to_controls=collections.defaultdict(set)
    for (ctl,clip),hs in by_control_clip.items():
        if len(hs)==1:
            h=next(iter(hs));curve_to_clips[h].add(clip);curve_to_controls[h].add(ctl)
    decoded_curve_clip_aliases=[]
    for h,clips in curve_to_clips.items():
        if len(clips)<=1:continue
        payloads=sorted({p for clip in clips for p in clip_to_payloads.get(clip,set())})
        decoded_curve_clip_aliases.append({
            'decoded_local_curve_sha256':h,
            'unique_clip_count':len(clips),
            'clips':sorted(clips),
            'controls':sorted(curve_to_controls[h]),
            'source_payload_sha256s':payloads,
            'source_payload_hash_count':len(payloads),
            'source_payloads_byte_identical':len(payloads)==1,
            'different_source_payloads_same_decoded_curve':len(payloads)>1,
        })
    decoded_curve_clip_aliases.sort(key=lambda x:(-x['unique_clip_count'],x['decoded_local_curve_sha256']))

    cross_seq=[x for x in curve_sequence_groups if x['cross_filehash_curve_alias']]
    out={
        'schema':'d1_animation_selector_curve_alias_join/v1',
        'status':'D1_ANIMATION_SELECTOR_CURVE_ALIAS_JOIN_EXACT' if records and not v else 'D1_ANIMATION_SELECTOR_CURVE_ALIAS_JOIN_PARTIAL',
        'selector_state_record_count':len(records),
        'decoded_curve_sequence_group_count':len(curve_sequence_groups),
        'cross_filehash_curve_sequence_alias_group_count':len(cross_seq),
        'different_clip_hash_same_decoded_curve_group_count':len(decoded_curve_clip_aliases),
        'different_clip_hash_same_decoded_curve_groups':decoded_curve_clip_aliases,
        'cross_filehash_curve_sequence_alias_groups':cross_seq,
        'decoded_curve_sequence_groups':curve_sequence_groups,
        'records':records,
        'ambiguous_control_clip_keys':ambiguous_control_clip,
        'ambiguous_control_clip_payload_keys':ambiguous_control_clip_payload,
        'unresolved_selector_curve_refs':unresolved,
        'violations':v,
        'semantic_boundary':{
            'selector_state_to_clip_filehash':'EXACT_BINARY_DECODE',
            'clip_to_decoded_curve_hash':'EXACT_CANONICAL_DECODED_LOCAL_ARRAY_JOIN',
            'different_filehash_same_curve':'BYTE_EQUAL_DECODED_LOCAL_ARRAYS',
            'source_payload_identity':'EXACT_RETAIL_PAYLOAD_SHA256_SEPARATE_FROM_DECODED_CURVE_HASH',
            'state_or_clip_behavior':'WITHHELD',
        },
        'policy':'A shared decoded curve hash collapses only the canonical local transform result under the pinned pipeline. Exact retail payload SHA256 is carried independently, so byte-identical source resources and different source resources converging to one decoded motion are distinguished. Neither relation proves equal event metadata or gameplay meaning.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({
        'status':out['status'],
        'state_records':len(records),
        'curve_sequence_groups':len(curve_sequence_groups),
        'cross_filehash_curve_sequence_alias_groups':cross_seq,
        'different_clip_hash_same_decoded_curve_groups':decoded_curve_clip_aliases,
        'ambiguous_control_clip_keys':ambiguous_control_clip,
        'ambiguous_control_clip_payload_keys':ambiguous_control_clip_payload,
        'unresolved_selector_curve_refs':unresolved,
        'violations':v,
    },indent=2))
    return 0 if out['status']=='D1_ANIMATION_SELECTOR_CURVE_ALIAS_JOIN_EXACT' else 2

if __name__=='__main__':
    raise SystemExit(main())
