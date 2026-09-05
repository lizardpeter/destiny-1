#!/usr/bin/env python3
"""Validate source-driven table-scoped decal/common targets for a D1 world.

Input is the execution plan from `d1_world_static_map_target_plan.py`. The plan is the
only source of target hashes: this tool never accepts a hand-written common-carrier list.
It validates every table-scoped DataEntries[0] SStaticMapData and every independently
classified baked-static target using the generic D1 SStaticMapData decal parser.

The table-scoped subset models the exact D1 MapView behavior: decals are loaded once from
the first SMapDataEntry for each table. Baked targets are retained as controls because an
SStaticMapData can legally carry both decal data and a direct D1 baked-static child.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from d1_tower_map_schema_validate import Corpus
from d1_world_static_map_decal_validate import validate_static_map


def norm(x: object) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', type=Path, action='append', required=True)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--target-plan', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--validation-dir', type=Path)
    a = ap.parse_args()

    plan = json.loads(a.target_plan.read_text())
    violations: list[str] = []
    if plan.get('status') != 'D1_WORLD_STATIC_MAP_TARGET_PLAN_COMPLETE':
        violations.append(f"target_plan_status:{plan.get('status')}")

    c = Corpus([p.resolve() for p in a.snapshot], a.runtime.resolve())
    rows = []
    model_union = set()

    for i, target in enumerate(plan.get('targets', [])):
        role = target.get('role')
        if role not in {'table_scoped_decal_target', 'baked_static_target'}:
            violations.append(f'target_{i}_unknown_role:{role}')
            continue
        sm = norm(target.get('static_map_data', ''))
        rep = validate_static_map(c, sm)
        summary = rep.get('summary', {})
        model_union.update(summary.get('entity_model_histogram', {}).keys())
        row = {
            'target_index': i,
            'role': role,
            'map_data_table': target.get('map_data_table'),
            'source_index': target.get('source_index'),
            'static_map_data': sm,
            'static_map_kind': target.get('static_map_kind'),
            'table_reference_count': target.get('table_reference_count'),
            'd1_static_map_data_from_plan': target.get('d1_static_map_data'),
            'validation_ok': rep.get('ok'),
            'evidence_status': rep.get('evidence_status'),
            'payload_size': rep.get('payload_size'),
            'decal_count': summary.get('decal_count'),
            'decal_records_parsed': summary.get('decal_records_parsed'),
            'decal_records_structurally_valid': summary.get('decal_records_structurally_valid'),
            'singleton_transform_model_records': summary.get('singleton_transform_model_records'),
            'all_decal_records_singleton_transform_model': summary.get('all_decal_records_singleton_transform_model'),
            'model_reference_occurrences': summary.get('model_reference_occurrences'),
            'unique_entity_models': summary.get('unique_entity_models'),
            'entity_model_hashes': sorted(summary.get('entity_model_histogram', {})),
            'has_direct_d1_static_child': summary.get('has_direct_d1_static_child'),
            'd1_static_child': summary.get('d1_static_child'),
            'occlusion_bounds': summary.get('occlusion_bounds'),
            'violations': rep.get('violations', []),
        }
        rows.append(row)
        if not rep.get('ok'):
            violations.append(f'{role}:{sm}:validation_failed')

        # The ownership classifier and local SStaticMapData bytes must agree.
        kind = target.get('static_map_kind')
        if kind == 'direct_d1_baked_static':
            expected = norm(target.get('d1_static_map_data')) if target.get('d1_static_map_data') else None
            actual = norm(summary.get('d1_static_child')) if summary.get('d1_static_child') else None
            if not summary.get('has_direct_d1_static_child') or expected != actual:
                violations.append(
                    f'{role}:{sm}:baked_child_mismatch:plan={expected}:local={actual}'
                )
        elif kind == 'no_direct_d1_static_child' and summary.get('has_direct_d1_static_child'):
            violations.append(f'{role}:{sm}:unexpected_direct_d1_static_child')

        if a.validation_dir:
            a.validation_dir.mkdir(parents=True, exist_ok=True)
            p = a.validation_dir / f'{i:03d}_{role}_{sm}.json'
            p.write_text(json.dumps(rep, indent=2) + '\n')

    table_rows = [x for x in rows if x['role'] == 'table_scoped_decal_target']
    baked_rows = [x for x in rows if x['role'] == 'baked_static_target']

    table_decal_records = sum(int(x.get('decal_count') or 0) for x in table_rows)
    table_valid_records = sum(int(x.get('decal_records_structurally_valid') or 0) for x in table_rows)
    table_singletons = sum(int(x.get('singleton_transform_model_records') or 0) for x in table_rows)
    table_model_occurrences = sum(int(x.get('model_reference_occurrences') or 0) for x in table_rows)
    table_model_union = {
        h for x in table_rows for h in x.get('entity_model_hashes', [])
    }

    baked_decal_records = sum(int(x.get('decal_count') or 0) for x in baked_rows)
    baked_model_union = {
        h for x in baked_rows for h in x.get('entity_model_hashes', [])
    }

    role_counts = Counter(x['role'] for x in rows)
    kind_counts = Counter(x.get('static_map_kind') or 'UNCLASSIFIED' for x in rows)

    out = {
        'schema_version': 1,
        'status': 'D1_WORLD_TABLE_SCOPED_DECAL_CENSUS_COMPLETE' if not violations else 'D1_WORLD_TABLE_SCOPED_DECAL_CENSUS_PARTIAL',
        'source_target_plan_status': plan.get('status'),
        'target_count': len(rows),
        'target_role_counts': dict(role_counts),
        'target_kind_counts': dict(kind_counts),
        'validated_target_count': sum(bool(x.get('validation_ok')) for x in rows),
        'table_scoped_target_count': len(table_rows),
        'table_scoped_decal_records': table_decal_records,
        'table_scoped_structurally_valid_decal_records': table_valid_records,
        'table_scoped_singleton_transform_model_records': table_singletons,
        'table_scoped_all_records_singleton': bool(
            table_decal_records > 0 and table_singletons == table_decal_records
        ),
        'table_scoped_model_reference_occurrences': table_model_occurrences,
        'table_scoped_unique_entity_models': len(table_model_union),
        'baked_target_count': len(baked_rows),
        'baked_target_decal_records': baked_decal_records,
        'baked_target_unique_entity_models': len(baked_model_union),
        'all_target_unique_entity_models': len(model_union),
        'rows': rows,
        'violations': violations,
        'policy': (
            'Target hashes come only from the closed SMapDataTable ownership plan. '
            'DataEntries[0] is validated once per table for table-scoped decal/common '
            'content; baked-static targets are validated independently as controls.'
        ),
    }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in (
        'status', 'target_count', 'target_role_counts', 'target_kind_counts',
        'validated_target_count', 'table_scoped_target_count',
        'table_scoped_decal_records', 'table_scoped_structurally_valid_decal_records',
        'table_scoped_singleton_transform_model_records',
        'table_scoped_all_records_singleton', 'table_scoped_model_reference_occurrences',
        'table_scoped_unique_entity_models', 'baked_target_count',
        'baked_target_decal_records', 'baked_target_unique_entity_models',
        'all_target_unique_entity_models', 'violations'
    )}, indent=2))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
