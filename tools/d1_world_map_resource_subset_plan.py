#!/usr/bin/env python3
"""Derive typed map-table subsets from a full D1 SMapDataEntry resource-class census.

The Activity ownership graph is intentionally broader than any one renderer/gameplay
subsystem. This tool consumes d1_world_map_data_layer_census.py output and derives a
smaller table-root manifest only when serialized ResourcePointer classes justify it.

For the static/render layer the required class is SMapDataResource (80801AEA). A table
is selected only when every row in that table has that resource class. Tables mixing
static and non-static rows are reported explicitly instead of silently dropping rows.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def norm(x: object) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--census',type=Path,required=True)
    ap.add_argument('--resource-class',default='80801AEA')
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()

    d=json.loads(a.census.read_text())
    wanted=norm(a.resource_class)
    violations=[]
    selected=[]
    mixed=[]
    matching_rows=0
    other_rows=0
    per_table=[]

    for t in d.get('tables',[]):
        th=norm(t.get('map_data_table'))
        rows=t.get('entries') or []
        hist=Counter((norm(r.get('resource_class')) if r.get('resource_class') else 'NULL') for r in rows)
        n=hist.get(wanted,0)
        matching_rows += n
        other_rows += len(rows)-n
        mode='all_matching' if rows and n==len(rows) else ('mixed' if n else 'none_matching')
        row={'map_data_table':th,'entry_count':len(rows),'resource_class_counts':dict(hist),'selection_mode':mode}
        per_table.append(row)
        if mode=='all_matching': selected.append(th)
        elif mode=='mixed': mixed.append(row)

    if mixed:
        violations.append('one_or_more_tables_mix_requested_resource_class_with_other_classes')

    root=d.get('root_source') or {}
    out={
        'schema_version':1,
        'status':'D1_WORLD_MAP_RESOURCE_SUBSET_PLAN_COMPLETE' if not violations else 'D1_WORLD_MAP_RESOURCE_SUBSET_PLAN_PARTIAL',
        'resource_class':wanted,
        'source_census':str(a.census),
        'source_root':root,
        'source_map_data_table_count':d.get('map_data_table_count'),
        'source_entry_count':d.get('entry_count'),
        'map_data_tables':selected,
        'map_data_table_count':len(selected),
        'entry_count':matching_rows,
        'nonmatching_entry_count':other_rows,
        'mixed_table_count':len(mixed),
        'mixed_tables':mixed,
        'table_classification':per_table,
        'violations':violations,
        'selection_mode':'all_rows_in_table_have_requested_resource_class',
        'selected_activities':root.get('selected_activities'),
        'bubble_definitions':root.get('bubble_definitions'),
        'map_containers':root.get('map_containers'),
        'policy':'Subset is derived solely from serialized SMapDataEntry ResourcePointer classes. Mixed tables fail closed so row-level ownership is never approximated by table membership.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','resource_class','source_map_data_table_count','source_entry_count','map_data_table_count','entry_count','nonmatching_entry_count','mixed_table_count','map_data_tables','violations')},indent=2))
    return 0 if not violations else 2

if __name__=='__main__':
    raise SystemExit(main())
