#!/usr/bin/env python3
"""Parse D1 Bubble -> MapContainer -> MapDataTable ownership.

Pinned D1 Rise-of-Iron schema chain (MontagueM/Charm commit
50d36ee1f9ecadad7522504c20b1f3f9c97e30af):

  SBubbleDefinition / SchemaStruct 808091E0
    +0x08 DynamicArray<SMapContainerEntry>, elem 0x04
      -> typed Tag<SMapContainer> / SchemaStruct 80808A54
        +0x18 DynamicArray<SMapDataTableEntry>, elem 0x04
          -> typed Tag<SMapDataTable> / SchemaStruct 808009A2
            +0x08 DynamicArray<SMapDataEntry>, elem 0x90

D1 global Tag manifest TagClassHash values are not assumed to equal SchemaStruct class
identifiers. For source-typed Tag<T> edges this parser uses `resolve_typed_tag`: a direct
schema Reference is accepted directly; otherwise a valid S48018080 manifest parent and
exact +0x10 backlink proves target identity while the pinned field type supplies the
payload schema. The manifest TagClassHash is preserved separately as evidence.

The standalone class-scan mode remains a conservative diagnostic only. It can enumerate
class-direct/exact-manifest-class resources, but Activity ownership is the authoritative
world-root discovery path for D1 global Bubble tags.
"""
from __future__ import annotations

import argparse
import json
import sys
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import d1_tower_map_schema_validate_v5 as v5
import d1_world_map_data_layer_census as layer
from d1_tag_manifest_resolver import resolve_typed_tag, current_hashes_by_class

BUBBLE_DEFINITION = '808091E0'
MAP_CONTAINER = '80808A54'
MAP_DATA_TABLE = '808009A2'
MAP_ENTRY_STRIDE = 0x90
PINNED_SOURCE = (
    'MontagueM/Charm@50d36ee1f9ecadad7522504c20b1f3f9c97e30af '
    'Tiger/Schema/Static/StaticMapData.cs + Tiger/TigerHash.cs::GetReferenceFromManifest'
)


def norm(x: object) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def u32(b: bytes, o: int) -> int:
    return struct.unpack_from('<I', b, o)[0]


def hx(v: int) -> str:
    return f'{v:08X}'


def current_hashes_by_ref(c, reference: str) -> list[str]:
    """Conservative exact TagClassHash/class-direct diagnostic enumeration."""
    return current_hashes_by_class(c, reference)


def target(c, h: str, expected: str) -> dict:
    """Resolve a target reached through a pinned source-typed Tag<T> field."""
    return resolve_typed_tag(c, norm(h), norm(expected))


def parse_table(c, h: str) -> dict:
    h = norm(h)
    resolved = target(c, h, MAP_DATA_TABLE)
    rep = {
        'map_data_table': h,
        'meta': resolved.get('meta'),
        'class_resolution': resolved,
        'validation_ok': False,
        'violations': [],
    }
    if not resolved.get('typed_target_valid'):
        rep['violations'].append(f'typed_target_unresolved:{MAP_DATA_TABLE}')
        return rep
    b, src = c.payload(h)
    rep['payload_source'] = src
    if b is None:
        rep['violations'].append('payload_unavailable')
        return rep
    rep['payload_bytes'] = len(b)
    if len(b) < 0x18:
        rep['violations'].append('payload_shorter_than_SMapDataTable_0x18')
        return rep
    arr = layer.dyn(b, 0x08, MAP_ENTRY_STRIDE)
    rep['data_entries_array'] = arr
    if not arr['ok']:
        rep['violations'].append('data_entries_array_bounds')
        return rep
    rep['entry_count'] = arr['count']
    rep['validation_ok'] = True
    return rep


def parse_container(c, h: str) -> dict:
    h = norm(h)
    resolved = target(c, h, MAP_CONTAINER)
    rep = {
        'map_container': h,
        'meta': resolved.get('meta'),
        'class_resolution': resolved,
        'map_data_tables': [],
        'validation_ok': False,
        'violations': [],
    }
    if not resolved.get('typed_target_valid'):
        rep['violations'].append(f'typed_target_unresolved:{MAP_CONTAINER}')
        return rep
    b, src = c.payload(h)
    rep['payload_source'] = src
    if b is None:
        rep['violations'].append('payload_unavailable')
        return rep
    rep['payload_bytes'] = len(b)
    if len(b) < 0x28:
        rep['violations'].append('payload_shorter_than_SMapContainer_0x28')
        return rep
    arr = layer.dyn(b, 0x18, 0x04)
    rep['map_data_tables_array'] = arr
    if not arr['ok']:
        rep['violations'].append('map_data_tables_array_bounds')
        return rep

    for i in range(arr['count']):
        o = arr['absolute'] + i * 4
        th = hx(u32(b, o))
        t = target(c, th, MAP_DATA_TABLE)
        row = {'index': i, 'offset': o, 'map_data_table': th, 'target': t}
        if not t.get('typed_target_valid'):
            row['violation'] = 'map_data_table_typed_target_unresolved'
            rep['violations'].append(f'table[{i}]={th}:target_unresolved')
        else:
            row['table_validation'] = parse_table(c, th)
            if not row['table_validation']['validation_ok']:
                rep['violations'].append(f'table[{i}]={th}:payload_validation_failed')
        rep['map_data_tables'].append(row)

    rep['validation_ok'] = not rep['violations']
    return rep


def parse_bubble(c, h: str) -> dict:
    h = norm(h)
    resolved = target(c, h, BUBBLE_DEFINITION)
    rep = {
        'bubble_definition': h,
        'meta': resolved.get('meta'),
        'class_resolution': resolved,
        'map_containers': [],
        'validation_ok': False,
        'violations': [],
    }
    if not resolved.get('typed_target_valid'):
        rep['violations'].append(f'typed_target_unresolved:{BUBBLE_DEFINITION}')
        return rep
    b, src = c.payload(h)
    rep['payload_source'] = src
    if b is None:
        rep['violations'].append('payload_unavailable')
        return rep
    rep['payload_bytes'] = len(b)
    if len(b) < 0x18:
        rep['violations'].append('payload_shorter_than_SBubbleDefinition_0x18')
        return rep
    arr = layer.dyn(b, 0x08, 0x04)
    rep['map_resources_array'] = arr
    if not arr['ok']:
        rep['violations'].append('map_resources_array_bounds')
        return rep

    for i in range(arr['count']):
        o = arr['absolute'] + i * 4
        ch = hx(u32(b, o))
        t = target(c, ch, MAP_CONTAINER)
        row = {'index': i, 'offset': o, 'map_container': ch, 'target': t}
        if not t.get('typed_target_valid'):
            row['violation'] = 'map_container_typed_target_unresolved'
            rep['violations'].append(f'container[{i}]={ch}:target_unresolved')
        else:
            row['container_validation'] = parse_container(c, ch)
            if not row['container_validation']['validation_ok']:
                rep['violations'].append(f'container[{i}]={ch}:payload_validation_failed')
        rep['map_containers'].append(row)

    rep['validation_ok'] = not rep['violations']
    return rep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', type=Path, action='append', required=True)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    c = v5.v3.base.Corpus([p.resolve() for p in a.snapshot], a.runtime.resolve())
    # This standalone scan is intentionally conservative. It cannot infer source-typed
    # global Bubble tags from TagClassHash alone when TagClassHash != SchemaStruct hash.
    current_bubbles = current_hashes_by_class(c, BUBBLE_DEFINITION)
    current_containers = current_hashes_by_class(c, MAP_CONTAINER)
    current_tables = current_hashes_by_class(c, MAP_DATA_TABLE)

    bubbles = [parse_bubble(c, h) for h in current_bubbles]
    reachable_containers = []
    reachable_tables = []
    table_entries = {}
    violations = []

    for b in bubbles:
        if not b['validation_ok']:
            violations.append(f"bubble:{b['bubble_definition']}:validation_failed")
        for cr in b.get('map_containers', []):
            if not cr.get('target', {}).get('typed_target_valid'):
                continue
            ch = norm(cr['map_container'])
            reachable_containers.append(ch)
            cv = cr.get('container_validation') or {}
            for tr in cv.get('map_data_tables', []):
                if not tr.get('target', {}).get('typed_target_valid'):
                    continue
                th = norm(tr['map_data_table'])
                reachable_tables.append(th)
                tv = tr.get('table_validation') or {}
                if tv.get('validation_ok'):
                    table_entries.setdefault(th, int(tv.get('entry_count', 0)))

    reachable_containers = list(dict.fromkeys(reachable_containers))
    reachable_tables = list(dict.fromkeys(reachable_tables))
    orphan_containers = sorted(set(current_containers) - set(reachable_containers))
    orphan_tables = sorted(set(current_tables) - set(reachable_tables))

    # No failure is attached merely because exact TagClassHash scanning finds no
    # Bubble globals; Activity traversal is the authoritative discovery path.
    if current_bubbles and not reachable_containers:
        violations.append('exact_class_bubbles_reach_no_map_containers')
    if reachable_containers and not reachable_tables:
        violations.append('exact_class_containers_reach_no_map_data_tables')

    out = {
        'schema_version': 3,
        'status': 'D1_WORLD_MAP_ROOT_DIAGNOSTIC_COMPLETE' if not violations else 'D1_WORLD_MAP_ROOT_DIAGNOSTIC_PARTIAL',
        'pinned_source': PINNED_SOURCE,
        'scan_scope': 'CONSERVATIVE_EXACT_TAGCLASS_DIAGNOSTIC_NOT_WORLD_SELECTION',
        'current_exact_tagclass_counts': {
            BUBBLE_DEFINITION: len(current_bubbles),
            MAP_CONTAINER: len(current_containers),
            MAP_DATA_TABLE: len(current_tables),
        },
        'bubble_definition_count': len(current_bubbles),
        'bubble_definitions': current_bubbles,
        'reachable_map_container_count': len(reachable_containers),
        'map_containers': reachable_containers,
        'reachable_map_data_table_count': len(reachable_tables),
        'map_data_tables': reachable_tables,
        'map_data_table_entry_counts': table_entries,
        'total_reachable_map_entries': sum(table_entries.values()),
        'orphan_current_map_containers': orphan_containers,
        'orphan_current_map_data_tables': orphan_tables,
        'bubbles': bubbles,
        'violations': violations,
        'policy': (
            'Source-typed Tag<T> traversal uses S48018080 identity/backlinks plus the '
            'pinned field schema; manifest TagClassHash is preserved separately and is '
            'not conflated with SchemaStruct identifiers. Standalone class scanning is '
            'diagnostic only. Activity ownership is authoritative world-root discovery.'
        ),
    }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in (
        'status', 'scan_scope', 'current_exact_tagclass_counts',
        'bubble_definition_count', 'reachable_map_container_count',
        'reachable_map_data_table_count', 'map_data_tables',
        'map_data_table_entry_counts', 'total_reachable_map_entries',
        'orphan_current_map_containers', 'orphan_current_map_data_tables', 'violations'
    )}, indent=2))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
