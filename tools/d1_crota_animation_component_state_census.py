#!/usr/bin/env python3
"""Exact structural census of Crota selector states by clip runtime-component family.

This tool scopes one source-closed control and groups its selector-selected clips by
their exact serialized runtime-rig component signature. It then maps every selector
state to the family sequence of the clips it selects.

No component family is named anatomically or behaviorally. Multi-selection ordering
is preserved exactly as serialized by the decoded control state table.
"""
from __future__ import annotations
import argparse,collections,json
from pathlib import Path

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def sig(clip):
    return tuple((norm(x['hash']),int(x['count'])) for x in clip.get('runtime_components',[]))

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--options',type=Path,required=True)
    ap.add_argument('--control',required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()

    d=json.loads(a.options.read_text())
    ctlh=norm(a.control);violations=[]
    if d.get('schema')!='d1_remote_spawned_actor_animation_options/v3':
        violations.append(f"unexpected options schema {d.get('schema')}")
    if d.get('violation_count',0) or d.get('violations'):
        violations.append('animation options contain violations')
    controls=d.get('controls') or {}
    clips=d.get('clips') or {}
    ctl=controls.get(ctlh)
    if ctl is None:
        violations.append(f'{ctlh}: control missing')
        ctl={'selector_selected_clip_hashes':[],'state_table':{'records':[]}}

    selected=[norm(x) for x in ctl.get('selector_selected_clip_hashes',[])]
    missing=[h for h in selected if h not in clips]
    if missing: violations.append(f'missing clip rows: {missing}')

    clip_sig={}
    for h in selected:
        if h in clips: clip_sig[h]=sig(clips[h])
    counts=collections.Counter(clip_sig.values())
    # Stable neutral IDs: descending selected clip population, then exact signature.
    ordered=sorted(counts,key=lambda s:(-counts[s],s))
    family_id={s:i for i,s in enumerate(ordered)}
    families=[]
    for s in ordered:
        members=sorted(h for h,z in clip_sig.items() if z==s)
        families.append({
            'family_index':family_id[s],
            'runtime_components':[{'hash':h,'count':n} for h,n in s],
            'component_total_count':sum(n for _,n in s),
            'selected_clip_count':len(members),
            'selected_clips':members,
        })

    patterns=collections.Counter();rows=[];multi=[]
    for r in (ctl.get('state_table') or {}).get('records',[]):
        sel=[norm(x['tag_hash']) for x in r.get('selected_animations',[])]
        unknown=[h for h in sel if h not in clip_sig]
        if unknown:
            violations.append(f"{ctlh}:record{r.get('record_index')}: selected clips outside scoped exact set {unknown}")
            continue
        fs=[family_id[clip_sig[h]] for h in sel]
        pattern=tuple(fs);patterns[(len(sel),pattern)]+=1
        selected_rows=[]
        for ordinal,h in enumerate(sel):
            cp=clips[h]
            fc=int(cp['frame_count'])
            selected_rows.append({
                'selection_ordinal':ordinal,'clip':h,'family_index':family_id[clip_sig[h]],
                'frame_count':fc,'frame_intervals':max(0,fc-1),
                'frame_intervals_div_30':max(0,fc-1)/30.0,
            })
        row={
            'record_index':int(r['record_index']),'state_hash':norm(r['state_hash']),
            'scalar_f32':float(r['scalar_f32']),'selection_count':len(sel),
            'family_sequence':fs,'selected':selected_rows,
        }
        if selected_rows:
            row['scalar_minus_lead_clip_frame_intervals_div_30']=(
                row['scalar_f32']-selected_rows[0]['frame_intervals_div_30']
            )
        rows.append(row)
        if len(sel)>1:multi.append(row)

    pattern_rows=[]
    for (n,pat),ct in sorted(patterns.items(),key=lambda kv:(kv[0][0],kv[0][1])):
        pattern_rows.append({
            'selection_count':n,'family_sequence':list(pat),'state_record_count':ct,
        })

    out={
        'schema':'d1_crota_animation_component_state_census/v1',
        'status':'D1_CROTA_ANIMATION_COMPONENT_STATE_CENSUS_EXACT' if families and rows and not violations else 'D1_CROTA_ANIMATION_COMPONENT_STATE_CENSUS_PARTIAL',
        'control':ctlh,
        'selected_clip_count':len(selected),
        'state_record_count':len(rows),
        'component_family_count':len(families),
        'families':families,
        'state_family_patterns':pattern_rows,
        'multi_selection_record_count':len(multi),
        'multi_selection_records':multi,
        'rows':rows,
        'violations':violations,
        'semantic_boundary':{
            'runtime_component_signatures':'EXACT_SERIALIZED_CLIP_STRUCTURE',
            'selector_state_to_family_sequence':'EXACT',
            'selection_order':'EXACT_DECODED_CONTROL_ORDER',
            'component_family_semantics':'WITHHELD',
            'state_hash_semantics':'WITHHELD',
            'behavioral_clip_names':'WITHHELD',
            'multi_choice_alternate_timing_semantics':'WITHHELD',
        },
        'policy':'Family IDs are neutral deterministic labels for exact runtime-component signatures. State mapping preserves decoded selection order and numerical frame/scalar facts only; no behavior or component meaning is inferred.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({
        'status':out['status'],
        'families':[(x['family_index'],x['selected_clip_count'],x['runtime_components']) for x in families],
        'patterns':pattern_rows,
        'multi':[{
            'record_index':x['record_index'],'state_hash':x['state_hash'],
            'scalar_f32':x['scalar_f32'],'family_sequence':x['family_sequence'],
            'selected':x['selected'],
        } for x in multi],
        'violations':violations,
    },indent=2))
    return 0 if out['status']=='D1_CROTA_ANIMATION_COMPONENT_STATE_CENSUS_EXACT' else 2

if __name__=='__main__':
    raise SystemExit(main())
