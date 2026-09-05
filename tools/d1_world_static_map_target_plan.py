#!/usr/bin/env python3
"""Build a source-driven D1 static-map execution plan from a closed map-resource chain.

This is the bridge between ownership discovery and downstream world export/validation.
It deliberately does not infer carriers from package names or hand-written hash lists.

For each SMapDataTable it preserves two distinct D1 source behaviors:

1. Table-scoped decal/common load target
   Charm D1 MapView.ExtractDataTables loads decals from DataEntries[0] once per table.
   The first row's SStaticMapData is therefore emitted exactly once as the table-scoped
   decal target, regardless of whether that resource also has a direct D1 baked child.

2. Baked-static row targets
   Every row whose SStaticMapData was classified as direct_d1_baked_static remains a
   baked-static target. Unique SStaticMapData resources are emitted once per table while
   the exact source row indices are retained.

The tool consumes only the loss-preserving output of
`d1_world_static_map_resource_chain_census.py`. It does not touch package bytes and it
never guesses a missing ownership edge.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

BAKED = 'direct_d1_baked_static'
NO_DIRECT_D1 = 'no_direct_d1_static_child'
VALID_KINDS = {BAKED, NO_DIRECT_D1}


def norm(x: object) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--chain-json', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--tsv', type=Path)
    a = ap.parse_args()

    chain = json.loads(a.chain_json.read_text())
    violations: list[str] = []

    if chain.get('closed_chain_count') != chain.get('entry_count'):
        violations.append(
            'input_resource_chain_not_fully_closed:'
            f"{chain.get('closed_chain_count')}/{chain.get('entry_count')}"
        )

    table_reports = []
    target_rows = []
    all_baked_rows = []
    all_nonbaked_rows = []

    for table_pos, table in enumerate(chain.get('tables', [])):
        th = norm(table.get('map_data_table', ''))
        entries = table.get('entries', [])
        closed = [e for e in entries if e.get('chain_closed') and e.get('static_map')]
        tr = {
            'table_position': table_pos,
            'map_data_table': th,
            'serialized_entry_count': len(entries),
            'closed_entry_count': len(closed),
            'table_scoped_decal_target': None,
            'baked_static_targets': [],
            'static_map_reference_counts': {},
            'kind_counts': {},
            'violations': [],
        }

        if len(closed) != len(entries):
            tr['violations'].append(
                f'not_all_rows_closed:{len(closed)}/{len(entries)}'
            )
        if not closed:
            tr['violations'].append('no_closed_rows')
            violations.extend(f'{th}:{v}' for v in tr['violations'])
            table_reports.append(tr)
            continue

        sm_counts = Counter(norm(e['static_map']['hash']) for e in closed)
        kind_counts = Counter(e.get('static_map_kind') or 'UNCLASSIFIED' for e in closed)
        tr['static_map_reference_counts'] = dict(sm_counts)
        tr['kind_counts'] = dict(kind_counts)

        for e in closed:
            kind = e.get('static_map_kind')
            if kind not in VALID_KINDS:
                tr['violations'].append(
                    f"row_{e.get('index')}_unknown_kind:{kind}"
                )
            elif kind == BAKED:
                all_baked_rows.append(e)
            else:
                all_nonbaked_rows.append(e)

        # D1 source behavior: LoadDecalsIntoExporterScene(DataEntries[0]) once/table.
        first = closed[0]
        first_sm = norm(first['static_map']['hash'])
        first_kind = first.get('static_map_kind')
        decal_target = {
            'role': 'table_scoped_decal_target',
            'map_data_table': th,
            'source_index': first.get('index'),
            'static_map_data': first_sm,
            'static_map_kind': first_kind,
            'static_map_parent': norm(first['static_map_parent']['hash']) if first.get('static_map_parent') else None,
            'table_reference_count': sm_counts[first_sm],
            'd1_static_map_data': (
                norm(first['d1_static_map_data']['hash'])
                if first.get('d1_static_map_data') else None
            ),
        }
        tr['table_scoped_decal_target'] = decal_target
        target_rows.append(decal_target)

        # Preserve every direct baked row, but emit each baked SStaticMapData once/table.
        baked_groups: dict[str, list[dict]] = defaultdict(list)
        for e in closed:
            if e.get('static_map_kind') == BAKED:
                baked_groups[norm(e['static_map']['hash'])].append(e)

        for sm in sorted(baked_groups, key=lambda h: min(int(x.get('index', 0)) for x in baked_groups[h])):
            rows = baked_groups[sm]
            d1s = sorted({
                norm(x['d1_static_map_data']['hash'])
                for x in rows if x.get('d1_static_map_data')
            })
            if len(d1s) != 1:
                tr['violations'].append(f'baked_{sm}_d1_child_count:{len(d1s)}')
            target = {
                'role': 'baked_static_target',
                'map_data_table': th,
                'source_index': min(int(x.get('index', 0)) for x in rows),
                'source_indices': sorted(int(x.get('index', 0)) for x in rows),
                'static_map_data': sm,
                'static_map_kind': BAKED,
                'table_reference_count': len(rows),
                'd1_static_map_data': d1s[0] if len(d1s) == 1 else None,
            }
            tr['baked_static_targets'].append(target)
            target_rows.append(target)

        if tr['violations']:
            violations.extend(f'{th}:{v}' for v in tr['violations'])
        table_reports.append(tr)

    table_scoped = [x for x in target_rows if x['role'] == 'table_scoped_decal_target']
    baked_targets = [x for x in target_rows if x['role'] == 'baked_static_target']
    first_kind_counts = Counter(x.get('static_map_kind') or 'UNCLASSIFIED' for x in table_scoped)

    out = {
        'schema_version': 1,
        'status': 'D1_WORLD_STATIC_MAP_TARGET_PLAN_COMPLETE' if not violations else 'D1_WORLD_STATIC_MAP_TARGET_PLAN_PARTIAL',
        'source_chain_status': chain.get('status'),
        'map_data_table_count': len(table_reports),
        'source_entry_count': chain.get('entry_count'),
        'table_scoped_decal_target_count': len(table_scoped),
        'table_scoped_target_kind_counts': dict(first_kind_counts),
        'table_scoped_target_row_reference_count': sum(int(x['table_reference_count']) for x in table_scoped),
        'baked_static_target_count': len(baked_targets),
        'direct_d1_baked_row_count': len(all_baked_rows),
        'no_direct_d1_static_child_row_count': len(all_nonbaked_rows),
        'unique_table_scoped_static_maps': len({x['static_map_data'] for x in table_scoped}),
        'unique_baked_static_maps': len({x['static_map_data'] for x in baked_targets}),
        'tables': table_reports,
        'targets': target_rows,
        'violations': violations,
        'policy': (
            'Table-scoped decal/common loading follows D1 MapView source behavior and '
            'uses the first SMapDataEntry static-map target exactly once per table. '
            'Baked-static targets are derived independently from direct 80801B75 child '
            'classification. No target hash is supplied manually.'
        ),
    }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + '\n')

    if a.tsv:
        a.tsv.parent.mkdir(parents=True, exist_ok=True)
        with a.tsv.open('w', newline='') as f:
            w = csv.writer(f, delimiter='\t', lineterminator='\n')
            w.writerow([
                'role', 'map_data_table', 'source_index', 'static_map_data',
                'static_map_kind', 'table_reference_count', 'd1_static_map_data'
            ])
            for x in target_rows:
                w.writerow([
                    x['role'], x['map_data_table'], x['source_index'],
                    x['static_map_data'], x.get('static_map_kind') or '',
                    x['table_reference_count'], x.get('d1_static_map_data') or '',
                ])

    print(json.dumps({k: out[k] for k in (
        'status', 'map_data_table_count', 'source_entry_count',
        'table_scoped_decal_target_count', 'table_scoped_target_kind_counts',
        'table_scoped_target_row_reference_count', 'baked_static_target_count',
        'direct_d1_baked_row_count', 'no_direct_d1_static_child_row_count',
        'unique_table_scoped_static_maps', 'unique_baked_static_maps', 'violations'
    )}, indent=2))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
