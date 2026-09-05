#!/usr/bin/env python3
"""Derive the EntityModel dependency set for a D1 table-scoped common/decal layer.

The only input is a completed `d1_world_table_scoped_decal_census.py` JSON. Model hashes
are therefore consequences of closed SMapDataTable ownership and parsed BA048080 records,
not hand-authored world fixtures. Counts supplied by a world-specific regression remain
assertions outside this tool.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def norm(x: object) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--census', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--model-list', type=Path)
    a = ap.parse_args()

    census = json.loads(a.census.read_text())
    violations: list[str] = []
    if census.get('status') != 'D1_WORLD_TABLE_SCOPED_DECAL_CENSUS_COMPLETE':
        violations.append(f"census_status:{census.get('status')}")

    records = census.get('table_scoped_records', [])
    declared = census.get('table_scoped_materialized_record_count')
    if declared is not None and len(records) != int(declared):
        violations.append(f'materialized_record_count:{len(records)}!={declared}')

    hist = Counter()
    table_hist: dict[str, Counter] = defaultdict(Counter)
    carrier_hist: dict[str, Counter] = defaultdict(Counter)
    unresolved = []

    for i, r in enumerate(records):
        table = norm(r.get('map_data_table'))
        carrier = norm(r.get('static_map_data'))
        models = r.get('models', [])
        valid = [
            norm(m.get('hash')) for m in models
            if m.get('hash') and m.get('reference_matches')
        ]
        if not r.get('export_ready_singleton') or len(valid) != 1:
            unresolved.append({
                'record': i,
                'map_data_table': table,
                'static_map_data': carrier,
                'decal_index': r.get('decal_index'),
                'export_ready_singleton': r.get('export_ready_singleton'),
                'valid_model_hashes': valid,
            })
            continue
        h = valid[0]
        hist[h] += 1
        table_hist[table][h] += 1
        carrier_hist[carrier][h] += 1

    if unresolved:
        violations.append(f'unresolved_or_non_singleton_records:{len(unresolved)}')

    models = sorted(hist)
    out = {
        'schema_version': 1,
        'status': 'D1_WORLD_COMMON_MODEL_PLAN_COMPLETE' if not violations else 'D1_WORLD_COMMON_MODEL_PLAN_PARTIAL',
        'source_census': str(a.census),
        'source_census_status': census.get('status'),
        'source_record_count': len(records),
        'resolved_model_reference_records': sum(hist.values()),
        'unique_model_count': len(models),
        'models': models,
        'model_reference_histogram': dict(hist),
        'models_by_map_data_table': {k: dict(v) for k, v in sorted(table_hist.items())},
        'models_by_static_map_data': {k: dict(v) for k, v in sorted(carrier_hist.items())},
        'unresolved_records': unresolved,
        'violations': violations,
        'policy': (
            'EntityModel dependencies are derived only from source-driven table-scoped '
            'BA048080 records. This tool accepts no model hashes and contains no '
            'world-specific model list.'
        ),
    }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + '\n')
    if a.model_list:
        a.model_list.parent.mkdir(parents=True, exist_ok=True)
        a.model_list.write_text('\n'.join(models) + ('\n' if models else ''))

    print(json.dumps({k: out[k] for k in (
        'status', 'source_record_count', 'resolved_model_reference_records',
        'unique_model_count', 'models', 'violations'
    )}, indent=2))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
