#!/usr/bin/env python3
"""Trace D1 Rise-of-Iron Activity -> Bubble -> MapContainer -> MapDataTable ownership.

Pinned source: MontagueM/Charm commit
50d36ee1f9ecadad7522504c20b1f3f9c97e30af.

D1 ownership chain:

  SActivity_ROI / 8080052E (raw Charm 2E058080, size 0x28)
    +0x10 DynamicArray<S0A418080>, elem 0x04
      -> ChildMapReference: SBubbleDefinition / 808091E0
        +0x08 DynamicArray<SMapContainerEntry>, elem 0x04
          -> SMapContainer / 80808A54
            +0x18 DynamicArray<SMapDataTableEntry>, elem 0x04
              -> SMapDataTable / 808009A2

This tool deliberately takes package snapshots, not hand-written bubble/container/table
hashes. When --activity is omitted it enumerates every *current-class* D1 Activity in
the supplied corpus and unions the map roots reachable from those activities. When one
or more --activity hashes are supplied, they are treated as explicit user/world roots,
not as inferred implementation constants.

The lower Bubble/MapContainer/Table parsing is shared with d1_world_map_root_census.py.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import d1_tower_map_schema_validate_v5 as v5
import d1_world_map_data_layer_census as layer
import d1_world_map_root_census as roots

ACTIVITY_ROI = '8080052E'
BUBBLE_DEFINITION = roots.BUBBLE_DEFINITION
PINNED_SOURCE = (
    'MontagueM/Charm@50d36ee1f9ecadad7522504c20b1f3f9c97e30af '
    'Tiger/Schema/Activity/Activity.cs + ActivityStructsROI.cs + '
    'Tiger/Schema/Static/StaticMapData.cs'
)


def norm(x: object) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def u32(b: bytes, o: int) -> int:
    return struct.unpack_from('<I', b, o)[0]


def hx(v: int) -> str:
    return f'{v:08X}'


def current_hashes_by_ref(c, reference: str) -> list[str]:
    out = []
    for h in c.occ:
        m = c.entry_meta(h)
        if m and norm(m.get('reference')) == reference:
            out.append(norm(h))
    return sorted(set(out))


def parse_activity(c, h: str) -> dict:
    h = norm(h)
    meta = c.entry_meta(h)
    rep = {
        'activity': h,
        'meta': meta,
        'bubble_references': [],
        'validation_ok': False,
        'violations': [],
    }
    if not meta or norm(meta.get('reference')) != ACTIVITY_ROI:
        rep['violations'].append(f'class_mismatch_or_missing:{ACTIVITY_ROI}')
        return rep

    b, src = c.payload(h)
    rep['payload_source'] = src
    if b is None:
        rep['violations'].append('payload_unavailable')
        return rep
    rep['payload_bytes'] = len(b)
    if len(b) < 0x20:
        rep['violations'].append('payload_shorter_than_activity_frontier')
        return rep

    # LocationNames is a Tag at +0x08. It is retained as evidence but is not
    # required for map ownership closure.
    rep['location_names_raw'] = hx(u32(b, 0x08))

    arr = layer.dyn(b, 0x10, 0x04)
    rep['bubbles_array'] = arr
    if not arr['ok']:
        rep['violations'].append('bubbles_array_bounds')
        return rep

    for i in range(arr['count']):
        o = arr['absolute'] + i * 4
        bh = hx(u32(b, o))
        t = roots.target(c, bh, BUBBLE_DEFINITION)
        row = {
            'bubble_index': i,
            'offset': o,
            'bubble_definition': bh,
            'is_null_sentinel': bh in {'00000000', 'FFFFFFFF'},
            'target': t,
        }
        if row['is_null_sentinel']:
            row['skipped'] = 'null_child_map_reference'
        elif not t['reference_matches']:
            row['violation'] = 'bubble_definition_missing_or_class_mismatch'
            rep['violations'].append(f'bubble[{i}]={bh}:target_mismatch')
        else:
            row['bubble_validation'] = roots.parse_bubble(c, bh)
            if not row['bubble_validation']['validation_ok']:
                rep['violations'].append(f'bubble[{i}]={bh}:payload_validation_failed')
        rep['bubble_references'].append(row)

    rep['non_null_bubble_count'] = sum(not x['is_null_sentinel'] for x in rep['bubble_references'])
    rep['resolved_bubble_count'] = sum(
        bool(x.get('target', {}).get('reference_matches'))
        for x in rep['bubble_references'] if not x['is_null_sentinel']
    )
    rep['validation_ok'] = not rep['violations']
    return rep


def component_summary(activity: dict) -> dict:
    bubbles = []
    containers = []
    tables = []
    table_entry_counts = {}

    for br in activity.get('bubble_references', []):
        if br.get('is_null_sentinel') or not br.get('target', {}).get('reference_matches'):
            continue
        bh = norm(br['bubble_definition'])
        bubbles.append(bh)
        bv = br.get('bubble_validation') or {}
        for cr in bv.get('map_containers', []):
            if not cr.get('target', {}).get('reference_matches'):
                continue
            ch = norm(cr['map_container'])
            containers.append(ch)
            cv = cr.get('container_validation') or {}
            for tr in cv.get('map_data_tables', []):
                if not tr.get('target', {}).get('reference_matches'):
                    continue
                th = norm(tr['map_data_table'])
                tables.append(th)
                tv = tr.get('table_validation') or {}
                if tv.get('validation_ok'):
                    table_entry_counts.setdefault(th, int(tv.get('entry_count', 0)))

    # Preserve source order while deduplicating shared roots.
    bubbles = list(dict.fromkeys(bubbles))
    containers = list(dict.fromkeys(containers))
    tables = list(dict.fromkeys(tables))
    return {
        'activity': activity['activity'],
        'validation_ok': activity.get('validation_ok'),
        'bubble_count': len(bubbles),
        'bubbles': bubbles,
        'map_container_count': len(containers),
        'map_containers': containers,
        'map_data_table_count': len(tables),
        'map_data_tables': tables,
        'map_data_table_entry_counts': table_entry_counts,
        'total_map_entries': sum(table_entry_counts.values()),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', type=Path, action='append', required=True)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--activity', action='append', default=[])
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    c = v5.v3.base.Corpus([p.resolve() for p in a.snapshot], a.runtime.resolve())
    current_activities = current_hashes_by_ref(c, ACTIVITY_ROI)
    selected = [norm(x) for x in a.activity] if a.activity else current_activities
    selected = list(dict.fromkeys(selected))

    violations = []
    if not selected:
        violations.append('no_selected_or_current_d1_activities')

    activities = [parse_activity(c, h) for h in selected]
    components = [component_summary(x) for x in activities]

    for x in activities:
        if not x.get('validation_ok'):
            violations.append(f"activity:{x['activity']}:validation_failed")

    all_bubbles = list(dict.fromkeys(
        h for cpt in components for h in cpt.get('bubbles', [])
    ))
    all_containers = list(dict.fromkeys(
        h for cpt in components for h in cpt.get('map_containers', [])
    ))
    all_tables = list(dict.fromkeys(
        h for cpt in components for h in cpt.get('map_data_tables', [])
    ))
    table_entry_counts = {}
    table_activity_owners: dict[str, list[str]] = defaultdict(list)
    bubble_activity_owners: dict[str, list[str]] = defaultdict(list)
    container_activity_owners: dict[str, list[str]] = defaultdict(list)

    for cpt in components:
        ah = cpt['activity']
        for h in cpt.get('bubbles', []):
            if ah not in bubble_activity_owners[h]:
                bubble_activity_owners[h].append(ah)
        for h in cpt.get('map_containers', []):
            if ah not in container_activity_owners[h]:
                container_activity_owners[h].append(ah)
        for h in cpt.get('map_data_tables', []):
            if ah not in table_activity_owners[h]:
                table_activity_owners[h].append(ah)
        for h, n in cpt.get('map_data_table_entry_counts', {}).items():
            if h in table_entry_counts and table_entry_counts[h] != n:
                violations.append(
                    f'table_entry_count_conflict:{h}:{table_entry_counts[h]}!={n}'
                )
            table_entry_counts[h] = n

    current_bubbles = current_hashes_by_ref(c, roots.BUBBLE_DEFINITION)
    current_containers = current_hashes_by_ref(c, roots.MAP_CONTAINER)
    current_tables = current_hashes_by_ref(c, roots.MAP_DATA_TABLE)

    if selected and not all_bubbles:
        violations.append('selected_activities_reach_no_bubbles')
    if all_bubbles and not all_containers:
        violations.append('activity_bubbles_reach_no_map_containers')
    if all_containers and not all_tables:
        violations.append('activity_containers_reach_no_map_data_tables')

    out = {
        'schema_version': 1,
        'status': 'D1_WORLD_ACTIVITY_MAP_ROOT_CENSUS_COMPLETE' if not violations else 'D1_WORLD_ACTIVITY_MAP_ROOT_CENSUS_PARTIAL',
        'pinned_source': PINNED_SOURCE,
        'selection_mode': 'explicit_activity_roots' if a.activity else 'all_current_class_activities_in_corpus',
        'current_d1_activity_count': len(current_activities),
        'current_d1_activities': current_activities,
        'selected_activity_count': len(selected),
        'selected_activities': selected,
        'reachable_bubble_count': len(all_bubbles),
        'bubble_definitions': all_bubbles,
        'reachable_map_container_count': len(all_containers),
        'map_containers': all_containers,
        'reachable_map_data_table_count': len(all_tables),
        'map_data_tables': all_tables,
        'map_data_table_entry_counts': table_entry_counts,
        'total_reachable_map_entries': sum(table_entry_counts.values()),
        'bubble_activity_owners': dict(bubble_activity_owners),
        'container_activity_owners': dict(container_activity_owners),
        'table_activity_owners': dict(table_activity_owners),
        'unowned_current_bubble_definitions': sorted(set(current_bubbles) - set(all_bubbles)),
        'unowned_current_map_containers': sorted(set(current_containers) - set(all_containers)),
        'unowned_current_map_data_tables': sorted(set(current_tables) - set(all_tables)),
        'activity_components': components,
        'activities': activities,
        'violations': violations,
        'policy': (
            'World map roots are followed only through the pinned D1 Activity.Bubbles '
            'ChildMapReference chain. With no --activity argument every current-class '
            'D1 activity in the supplied corpus is enumerated; explicit --activity '
            'values are legitimate exporter roots rather than hidden world fixtures. '
            'Current-class map resources not owned by selected activities are reported '
            'separately and are never silently merged.'
        ),
    }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in (
        'status', 'selection_mode', 'current_d1_activity_count',
        'selected_activity_count', 'selected_activities',
        'reachable_bubble_count', 'bubble_definitions',
        'reachable_map_container_count', 'reachable_map_data_table_count',
        'map_data_tables', 'map_data_table_entry_counts',
        'total_reachable_map_entries', 'unowned_current_bubble_definitions',
        'unowned_current_map_containers', 'unowned_current_map_data_tables',
        'violations'
    )}, indent=2))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
