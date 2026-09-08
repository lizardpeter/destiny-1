#!/usr/bin/env python3
"""Join source-owned Tower D912 actor locations to closed visual material signatures.

Inputs are three independently green checkpoints:
  * eight-scenario D912 spawned-actor location alternatives;
  * 13-model / 30-signature visible material closure;
  * 57-actor runtime closure, used only for exact EntitySK -> visual model identity.

For placement-specific models a D912 table is allowed to select a visual signature only
when the material-calibration rows for that same D912 owner collapse to exactly one
signature.  Configuration-independent/single-signature models require no placement
selector.  Runtime scenario/group/location activation is never inferred.
"""
from __future__ import annotations

import argparse, collections, json
from pathlib import Path


def norm(x: object) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def cfg_key(cfg) -> tuple[tuple[str,str], ...]:
    return tuple(sorted((norm(x[0]), norm(x[1])) for x in (cfg or [])))


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--locations',type=Path,required=True)
    ap.add_argument('--signatures',type=Path,required=True)
    ap.add_argument('--runtime-closure',type=Path,required=True)
    ap.add_argument('-o','--out',type=Path,required=True)
    a=ap.parse_args()

    loc=json.loads(a.locations.read_text())
    sig=json.loads(a.signatures.read_text())
    rt=json.loads(a.runtime_closure.read_text())
    violations=[]
    if loc.get('status')!='D1_TOWER_EIGHT_SCENARIO_SPAWNED_LOCATION_MANIFEST_COMPLETE':
        violations.append('location_manifest_not_green')
    if sig.get('status')!='D1_TOWER_ACTOR_VISIBLE_MATERIAL_SIGNATURES_COMPLETE' or sig.get('violations'):
        violations.append('signature_manifest_not_green')
    if rt.get('status')!='D1_TOWER_SPAWNED_ACTOR_RUNTIME_CLOSURE_COMPLETE' or rt.get('violations'):
        violations.append('runtime_closure_not_green')

    sig_by={norm(x['model']):x for x in sig.get('models',[])}
    entity_model={norm(e):norm(r.get('model')) for e,r in (rt.get('actors') or {}).items() if r.get('model')}
    if len(sig_by)!=13: violations.append(f'signature_model_count_{len(sig_by)}_not_13')
    if len(entity_model)!=57: violations.append(f'runtime_entity_model_count_{len(entity_model)}_not_57')

    # Derive configuration -> signature from the signature report itself, then
    # D912 owner -> signature from exact source placement rows.
    d912_values={norm(x['d912']) for x in loc.get('exact_actor_location_alternatives',[]) if x.get('d912')}
    d912_sig_sets=collections.defaultdict(set)
    d912_entity_sets=collections.defaultdict(set)
    calibrated_rows=0
    calibrated_d912_rows=0
    for model,m in sig_by.items():
        cmap={}
        for s in m.get('signatures',[]):
            si=int(s['signature_index'])
            for cfg in s.get('configurations',[]) or []:
                k=cfg_key(cfg)
                if k in cmap and cmap[k]!=si:
                    violations.append(f'{model}:configuration_maps_to_multiple_signatures:{k}')
                cmap[k]=si
        for r in m.get('placement_rows',[]) or []:
            calibrated_rows+=1
            k=cfg_key(r.get('configuration_pairs'))
            si=cmap.get(k)
            if si is None:
                violations.append(f'{model}:{r.get("scripted_owner")}:configuration_has_no_signature:{k}')
                continue
            owner=norm(r['scripted_owner'])
            if owner in d912_values:
                calibrated_d912_rows+=1
                d912_sig_sets[(model,owner)].add(si)
                d912_entity_sets[(model,owner)].add(norm(r['entity_hash']))

    ambiguous_d912_signature_keys=[]
    d912_signature_map={}
    for (model,d912),vals in sorted(d912_sig_sets.items()):
        if len(vals)!=1:
            ambiguous_d912_signature_keys.append({'model':model,'d912':d912,'signature_indices':sorted(vals)})
            continue
        d912_signature_map[(model,d912)]=next(iter(vals))
    if ambiguous_d912_signature_keys:
        violations.append(f'{len(ambiguous_d912_signature_keys)} D912/model keys map to multiple signatures')

    rows=[]
    methods=collections.Counter(); scenario_counts=collections.Counter(); model_counts=collections.Counter(); sig_counts=collections.Counter()
    for i,x in enumerate(loc.get('exact_actor_location_alternatives',[])):
        entity=norm(x['entity_hash']); d912=norm(x['d912']); model=entity_model.get(entity)
        if not model or model not in sig_by:
            violations.append(f'location[{i}] {entity}: exact visual model unavailable')
            continue
        m=sig_by[model]; n=int(m.get('unique_visible_external_signature_count') or 0)
        if n==1:
            si=0; method='single_signature_model'
        else:
            vals=d912_sig_sets.get((model,d912),set())
            if len(vals)!=1:
                violations.append(f'location[{i}] {entity}/{model}/{d912}: D912 signature count {len(vals)}')
                continue
            si=next(iter(vals)); method='exact_d912_owner_configuration_signature'
        valid={int(s['signature_index']) for s in m.get('signatures',[])}
        if si not in valid:
            violations.append(f'location[{i}] {entity}/{model}: signature {si} absent from model')
            continue
        scenario=norm(x['scenario'])
        methods[method]+=1; scenario_counts[scenario]+=1; model_counts[model]+=1; sig_counts[f'{model}:SIG{si:02d}']+=1
        rows.append({
            **x,
            'entity_hash':entity,
            'model':model,
            'visual_signature_index':si,
            'visual_signature_resolution':method,
            'visual_variant_key':f'{model}:SIG{si:02d}',
            'native_skinned_glb_basename':f'{model}_SIG{si:02d}_SKINNED_NATIVE_D1.glb',
            'textured_glb_basename':f'{model}_SIG{si:02d}_SKINNED_NATIVE_D1_TEXTURED.glb',
        })

    expected=int(loc.get('scenario_expanded_exact_actor_location_alternative_count',-1))
    if expected!=547: violations.append(f'location_checkpoint_expected_count_{expected}_not_547')
    if len(rows)!=expected: violations.append(f'resolved_location_visual_rows_{len(rows)}_not_{expected}')
    if sum(methods.values())!=len(rows): violations.append('resolution_method_count_mismatch')

    out={
        'schema_version':1,
        'status':'D1_TOWER_ACTOR_LOCATION_VISUAL_SIGNATURE_JOIN_COMPLETE' if not violations else 'D1_TOWER_ACTOR_LOCATION_VISUAL_SIGNATURE_JOIN_PARTIAL',
        'scenario_count':int(loc.get('scenario_count',0)),
        'spawned_actor_seed_count':int(loc.get('spawned_actor_seed_count',0)),
        'exact_location_alternative_count':expected,
        'resolved_visual_location_alternative_count':len(rows),
        'resolved_visual_model_count':len({x['model'] for x in rows}),
        'resolved_visual_variant_count':len({x['visual_variant_key'] for x in rows}),
        'resolution_method_counts':dict(methods),
        'scenario_row_counts':dict(sorted(scenario_counts.items())),
        'model_row_counts':dict(sorted(model_counts.items())),
        'visual_variant_row_counts':dict(sorted(sig_counts.items())),
        'material_calibration_row_count':calibrated_rows,
        'material_calibration_rows_on_exact_location_d912_tables':calibrated_d912_rows,
        'calibrated_model_d912_signature_key_count':len(d912_sig_sets),
        'ambiguous_calibrated_model_d912_signature_keys':ambiguous_d912_signature_keys,
        'exact_location_visual_alternatives':rows,
        'source_entities_without_exact_group_location':loc.get('spawned_actor_entities_without_exact_group_location',[]),
        'ambiguous_location_groups_with_spawned_actor_overlap':loc.get('ambiguous_location_groups_with_spawned_actor_overlap',[]),
        'violations':violations,
        'gates':{
            'runtime_active_scenario_selected':False,
            'runtime_active_D912_group_selected':False,
            'runtime_active_actor_location_selected':False,
            'runtime_actor_animation_state_selected':False,
            'D1_retail_descriptor_evaluator_source_closed':False,
        },
        'policy':(
            'Every row is a source-owned location alternative, not a simultaneous spawn claim. '
            'Single-signature models are configuration-independent for the visible export. Multi-signature '
            'models use a signature only when exact material-calibration rows owned by the same D912 table '
            'collapse to one signature. Scenario/group/location activation and animation state remain fail-closed.'
        )
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2,allow_nan=True)+'\n')
    print(json.dumps({k:out[k] for k in ('status','scenario_count','exact_location_alternative_count','resolved_visual_location_alternative_count','resolved_visual_model_count','resolved_visual_variant_count','resolution_method_counts','material_calibration_rows_on_exact_location_d912_tables','calibrated_model_d912_signature_key_count','violations')},indent=2))
    return 0 if not violations else 2

if __name__=='__main__': raise SystemExit(main())
