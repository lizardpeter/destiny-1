#!/usr/bin/env python3
"""Join Tower articulated runtime placements to source-typed permutation configs.

Inputs are independently closed layers:
- D1_WORLD_ARTICULATED_ENTITY_PLAN_COMPLETE: exact EntitySK/model/WorldID/transforms.
- D1_TOWER_PLACEMENT_WORLDID_ATTACH_COMPLETE: SD912/SMapDataEntry/S152 rows with
  exact model-switch-bank correspondence plus source WorldID/transforms.

The join is strict. Real WorldIDs join by EntitySK+WorldID; retail sentinel WorldIDs
join by EntitySK+serialized transform. Repeated SD912 serializations are accepted only
when they resolve to the same model resource and exact own-bank configuration set.

This tool does not evaluate material descriptors. It establishes whether the 37 exact
articulated runtime placements can safely carry placement-specific configuration into
a later visual selector.
"""
from __future__ import annotations

import argparse, json, math
from collections import defaultdict
from pathlib import Path

SENTINEL = 'FFFFFFFFFFFFFFFF'


def norm(x):
    return str(x).upper().removeprefix('0X').zfill(8)


def close_vec(a, b, eps=1e-6):
    return len(a) == len(b) and all(math.isfinite(float(x)) and math.isfinite(float(y)) and abs(float(x)-float(y)) <= eps for x,y in zip(a,b))


def config_pairs(row):
    return tuple(sorted({
        (norm(x['pair'][0]), norm(x['pair'][1]))
        for x in row.get('record_matches', [])
        if x.get('exact_pair_in_own_model_switch_bank')
    }))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--articulated-plan', type=Path, required=True)
    ap.add_argument('--placement-calibration', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    plan = json.loads(a.articulated_plan.read_text())
    cal = json.loads(a.placement_calibration.read_text())
    violations = []
    if plan.get('status') != 'D1_WORLD_ARTICULATED_ENTITY_PLAN_COMPLETE':
        violations.append('articulated_plan_not_green')
    if cal.get('status') != 'D1_TOWER_PLACEMENT_WORLDID_ATTACH_COMPLETE':
        violations.append('placement_calibration_not_green')
    if cal.get('violations'):
        violations.append('placement_calibration_has_violations')

    by_entity = defaultdict(list)
    for r in cal.get('calibration_rows', []):
        if r.get('exact_switch_bank_model_count') == 1 and r.get('model_resource_hash') and r.get('world_id_hex'):
            by_entity[norm(r['entity_hash'])].append(r)

    joined = []
    unmatched = []
    conflicts = []
    model_signatures = defaultdict(set)
    runtime_count = 0

    for c in plan.get('candidates', []):
        entity = norm(c['entity'])
        models = [norm(x) for x in c.get('models', [])]
        if len(models) != 1:
            violations.append(f'{entity}:model_not_singleton')
            continue
        model = models[0]
        for pi, p in enumerate(c.get('placements', [])):
            runtime_count += 1
            wid = str(p.get('world_id_hex') or '').upper().zfill(16)
            rows = []
            for r in by_entity.get(entity, []):
                if norm(r.get('model_tag_hash', 'FFFFFFFF')) != model:
                    continue
                rwid = str(r.get('world_id_hex') or '').upper().zfill(16)
                if wid != SENTINEL:
                    if rwid == wid:
                        rows.append(r)
                else:
                    if rwid == SENTINEL and close_vec(p.get('rotation', []), r.get('rotation_xyzw', [])) and close_vec(p.get('translation', []), r.get('translation', [])):
                        rows.append(r)
            if not rows:
                unmatched.append({'entity': entity, 'model': model, 'placement_index': pi, 'world_id_hex': wid})
                continue
            sigs = {}
            for r in rows:
                sig = (norm(r['model_resource_hash']), config_pairs(r))
                sigs.setdefault(sig, []).append(r)
            if len(sigs) != 1:
                conflicts.append({
                    'entity': entity, 'model': model, 'placement_index': pi, 'world_id_hex': wid,
                    'signatures': [
                        {'model_resource_hash': s[0], 'config_pairs': [list(x) for x in s[1]], 'serialization_count': len(rs)}
                        for s,rs in sigs.items()
                    ],
                })
                continue
            sig, evidence = next(iter(sigs.items()))
            resource, pairs = sig
            model_signatures[model].add(sig)
            joined.append({
                'entity': entity,
                'model_tag_hash': model,
                'placement_index': pi,
                'world_id': p.get('world_id'),
                'world_id_hex': wid,
                'world_id_identity_kind': p.get('world_id_identity_kind'),
                'rotation_xyzw': p.get('rotation'),
                'translation': p.get('translation'),
                'model_resource_hash': resource,
                'config_pairs': [list(x) for x in pairs],
                'calibration_serialization_count': len(evidence),
                'calibration_sources': [
                    {'owner': r['owner'], 'smap_offset': r['smap_offset'], 'world_id_hex': r['world_id_hex']}
                    for r in evidence
                ],
            })

    if runtime_count != int(plan.get('runtime_placement_count', -1)):
        violations.append(f'plan_runtime_count_mismatch:{runtime_count}!={plan.get("runtime_placement_count")}')
    if unmatched:
        violations.append(f'unmatched_runtime_placements:{len(unmatched)}')
    if conflicts:
        violations.append(f'conflicting_runtime_placement_configs:{len(conflicts)}')

    variant_rows = []
    variant_lookup = {}
    for model in sorted(model_signatures):
        sigs = sorted(model_signatures[model], key=lambda s: (s[0], s[1]))
        for i, sig in enumerate(sigs):
            vid = f'{model}_cfg{i:02d}'
            variant_lookup[(model, sig)] = vid
            variant_rows.append({
                'variant_id': vid,
                'model_tag_hash': model,
                'model_resource_hash': sig[0],
                'config_pairs': [list(x) for x in sig[1]],
            })
    for row in joined:
        sig = (row['model_resource_hash'], tuple(tuple(x) for x in row['config_pairs']))
        row['variant_id'] = variant_lookup[(row['model_tag_hash'], sig)]

    out = {
        'schema': 'd1_tower_articulated_permutation_coverage/v1',
        'status': 'D1_TOWER_ARTICULATED_PERMUTATION_COVERAGE_COMPLETE' if not violations and len(joined) == runtime_count else 'D1_TOWER_ARTICULATED_PERMUTATION_COVERAGE_PARTIAL',
        'candidate_count': len(plan.get('candidates', [])),
        'runtime_placement_count': runtime_count,
        'joined_runtime_placement_count': len(joined),
        'unmatched_runtime_placement_count': len(unmatched),
        'conflicting_runtime_placement_count': len(conflicts),
        'unique_model_count': len(model_signatures),
        'unique_model_config_variant_count': len(variant_rows),
        'model_variant_counts': {m: len(s) for m,s in sorted(model_signatures.items())},
        'variants': variant_rows,
        'placements': joined,
        'unmatched': unmatched,
        'conflicts': conflicts,
        'proof': {
            'runtime_placement_to_source_configuration_join_closed': not unmatched and not conflicts and len(joined) == runtime_count,
            'repeated_serializations_require_identical_configuration': True,
            'material_descriptor_evaluation_performed': False,
            'D1_retail_consumer_execution_path_proven': False,
        },
        'violations': violations,
        'policy': (
            'Real runtime placements join by exact EntitySK+WorldID. Sentinel WorldID rows join only by exact EntitySK and serialized transform. '
            'Repeated source serializations must agree on model resource and own-bank configuration. This is configuration transport only; material descriptors are not evaluated here.'
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in (
        'status','candidate_count','runtime_placement_count','joined_runtime_placement_count',
        'unmatched_runtime_placement_count','conflicting_runtime_placement_count',
        'unique_model_count','unique_model_config_variant_count','model_variant_counts','violations'
    )}, indent=2))
    return 0 if out['status'] == 'D1_TOWER_ARTICULATED_PERMUTATION_COVERAGE_COMPLETE' else 2


if __name__ == '__main__':
    raise SystemExit(main())
