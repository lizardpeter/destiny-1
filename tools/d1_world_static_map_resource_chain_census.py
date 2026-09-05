#!/usr/bin/env python3
"""Close D1 SMapDataEntry -> SStaticMapData ownership chains for a world.

This sits immediately above the map-root/map-data parsers. Preferred input is a
--map-root-json produced by the activity/bubble ownership census. Direct repeated
--map-data-table values remain supported for targeted validation and historical runs.

For each table it uses the binary-validated D1 DynamicArray framing and 0x90
SMapDataEntry layout, then follows the source-backed resource chain:

  SMapDataTable/808009A2
    -> SMapDataEntry[0x90].DataResource +0x88
    -> class 80801AEA / SMapDataResource
    -> +0x0C SStaticMapParent/80801AC6
    -> parent +0x08 SStaticMapData/808008B4

An SStaticMapData is then *classified*, not forced into one subtype. In shipped
Tower data there are two proven families:

- baked-static carriers whose +0x30 target is 80801B75 D1 static-map data;
- large/common carriers with no direct 80801B75 child, handled separately by the
  table-scoped embedded-model/decal pipeline.

The tool also records the post-array resource sidecar exactly. Tower's shipped
files have one 0x18-spaced resource sidecar slot per 0x90 entry. Thus whole-file
size can be factorized as 0x30 + count*0xA8, but 0xA8 is NOT the entry stride.
"""
from __future__ import annotations

import argparse, json, math, struct, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import d1_tower_map_schema_validate_v5 as v5
import d1_world_map_data_layer_census as layer

TABLE_CLASS = '808009A2'
MAP_DATA_RESOURCE = '80801AEA'
STATIC_MAP_PARENT = '80801AC6'
STATIC_MAP_DATA = '808008B4'
D1_STATIC_MAP_DATA = '80801B75'
ENTRY_STRIDE = 0x90
RESOURCE_FIELD = 0x88
PINNED_SOURCE = (
    'MontagueM/Charm@50d36ee1f9ecadad7522504c20b1f3f9c97e30af '
    'Tiger/Schema/Static/StaticMapData.cs + Tiger/SchemaTypes.cs'
)


def norm(x):
    return str(x).upper().removeprefix('0X').zfill(8)


def hx(x):
    return f'{x:08X}'


def u32(b, o):
    return struct.unpack_from('<I', b, o)[0]


def i64(b, o):
    return struct.unpack_from('<q', b, o)[0]


def f4(b, o):
    return [float(x) for x in struct.unpack_from('<4f', b, o)]


def target(c, h, expected=None):
    h = norm(h)
    m = c.entry_meta(h)
    return {
        'hash': h,
        'exists': m is not None,
        'meta': m,
        'expected_reference': expected,
        'reference_matches': bool(m and (expected is None or norm(m.get('reference', '')) == expected)),
    }


def load_table_roots(a):
    if a.map_root_json:
        d = json.loads(a.map_root_json.read_text())
        vals = d.get('map_data_tables')
        if not isinstance(vals, list) or not vals:
            raise SystemExit(f'{a.map_root_json}: missing non-empty map_data_tables list')
        return list(dict.fromkeys(norm(x) for x in vals)), {
            'mode': 'ownership_root_manifest',
            'path': str(a.map_root_json),
            'status': d.get('status'),
            'schema_version': d.get('schema_version'),
            'selection_mode': d.get('selection_mode'),
            'selected_activities': d.get('selected_activities'),
            'bubble_definitions': d.get('bubble_definitions'),
            'map_containers': d.get('map_containers'),
        }
    vals = list(dict.fromkeys(norm(x) for x in (a.map_data_table or [])))
    return vals, {'mode': 'explicit_map_data_tables'}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', type=Path, action='append', required=True)
    ap.add_argument('--runtime', type=Path, required=True)
    roots = ap.add_mutually_exclusive_group(required=True)
    roots.add_argument('--map-data-table', action='append')
    roots.add_argument('--map-root-json', type=Path)
    ap.add_argument('--expected-static-map', action='append', default=[])
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    table_roots, root_source = load_table_roots(a)
    c = v5.v3.base.Corpus([p.resolve() for p in a.snapshot], a.runtime.resolve())
    tables = []
    rows = []
    violations = []

    for raw_table in table_roots:
        th = norm(raw_table)
        meta = c.entry_meta(th)
        b, src = c.payload(th)
        tr = {'map_data_table': th, 'meta': meta, 'source': src, 'entries': []}
        if not meta or norm(meta.get('reference', '')) != TABLE_CLASS:
            tr['error'] = 'map_data_table_class_mismatch'
            violations.append(f'{th}: not {TABLE_CLASS}')
            tables.append(tr)
            continue
        if b is None:
            tr['error'] = 'payload_unavailable'
            violations.append(f'{th}: payload unavailable')
            tables.append(tr)
            continue

        arr = layer.dyn(b, 0x08, ENTRY_STRIDE)
        tr['payload_bytes'] = len(b)
        tr['entries_array'] = arr
        if not arr['ok']:
            tr['error'] = 'entry_array_bounds'
            violations.append(f'{th}: entry array bounds')
            tables.append(tr)
            continue

        class_offsets = []
        target_offsets = []
        for i in range(arr['count']):
            o = arr['absolute'] + i * ENTRY_STRIDE
            pf = o + RESOURCE_FIELD
            rel = i64(b, pf)
            r = {
                'map_data_table': th,
                'index': i,
                'record_offset': o,
                'entity_hash': hx(u32(b, o)),
                'rotation': f4(b, o + 0x20),
                'translation': f4(b, o + 0x30),
                'resource_pointer_field': pf,
                'resource_relative': rel,
                'resource_absolute': None,
                'resource_class': None,
                'static_map_parent': None,
                'static_map': None,
                'static_map_kind': None,
                'd1_static_map_data': None,
                'chain_closed': False,
            }
            if not all(math.isfinite(x) for x in r['rotation'] + r['translation']):
                r['error'] = 'nonfinite_transform'
                tr['entries'].append(r); rows.append(r); continue
            if rel == 0:
                r['error'] = 'null_resource_pointer'
                tr['entries'].append(r); rows.append(r); continue

            absolute = pf + rel
            r['resource_absolute'] = absolute
            if absolute < 4 or absolute + 0x10 > len(b):
                r['error'] = 'resource_pointer_oob'
                tr['entries'].append(r); rows.append(r); continue
            class_off = absolute - 4
            cls = hx(u32(b, class_off))
            r['resource_class_offset'] = class_off
            r['resource_class'] = cls
            class_offsets.append(class_off)
            target_offsets.append(absolute)
            if cls != MAP_DATA_RESOURCE:
                r['error'] = f'non_static_map_resource:{cls}'
                tr['entries'].append(r); rows.append(r); continue

            parent_hash = hx(u32(b, absolute + 0x0C))
            parent = target(c, parent_hash, STATIC_MAP_PARENT)
            r['static_map_parent'] = parent
            if not parent['reference_matches']:
                r['error'] = 'static_map_parent_missing_or_class_mismatch'
                tr['entries'].append(r); rows.append(r); continue

            pb, psrc = c.payload(parent_hash)
            r['static_map_parent_payload_source'] = psrc
            if pb is None or len(pb) < 0x0C:
                r['error'] = 'static_map_parent_payload_unavailable_or_short'
                tr['entries'].append(r); rows.append(r); continue

            sm_hash = hx(u32(pb, 0x08))
            sm = target(c, sm_hash, STATIC_MAP_DATA)
            r['static_map'] = sm
            if not sm['reference_matches']:
                r['error'] = 'static_map_missing_or_class_mismatch'
                tr['entries'].append(r); rows.append(r); continue

            # Ownership is now fully closed. Subtype classification is separate.
            r['chain_closed'] = True
            sb, ssrc = c.payload(sm_hash)
            r['static_map_payload_source'] = ssrc
            if sb is None:
                r['static_map_kind'] = 'payload_unavailable'
                r['classification_error'] = 'static_map_payload_unavailable'
            elif len(sb) < 0x34:
                r['static_map_kind'] = 'no_direct_d1_static_child'
                r['direct_d1_field_available'] = False
            else:
                d1_hash = hx(u32(sb, 0x30))
                d1 = target(c, d1_hash, D1_STATIC_MAP_DATA)
                r['d1_static_map_data_candidate'] = d1
                if d1['reference_matches']:
                    r['static_map_kind'] = 'direct_d1_baked_static'
                    r['d1_static_map_data'] = d1
                else:
                    r['static_map_kind'] = 'no_direct_d1_static_child'

            tr['entries'].append(r)
            rows.append(r)

        tail = len(b) - arr['end']
        sorted_class = sorted(class_offsets)
        class_stride = sorted({b - a for a, b in zip(sorted_class, sorted_class[1:])})
        tr['post_array_resource_sidecar'] = {
            'array_end': arr['end'],
            'payload_end': len(b),
            'tail_bytes': tail,
            'entry_count': arr['count'],
            'tail_bytes_per_entry_exact': (tail // arr['count']) if arr['count'] and tail % arr['count'] == 0 else None,
            'resource_class_offset_min': min(sorted_class) if sorted_class else None,
            'resource_class_offset_max': max(sorted_class) if sorted_class else None,
            'resource_class_offset_deltas': class_stride,
            'first_class_offset_minus_array_end': (min(sorted_class) - arr['end']) if sorted_class else None,
            'last_resource_frontier': (max(target_offsets) + 0x10) if target_offsets else None,
            'last_resource_frontier_equals_payload_end': bool(target_offsets and max(target_offsets) + 0x10 == len(b)),
        }
        tr['summary'] = {
            'entry_count': len(tr['entries']),
            'closed_chains': sum(bool(x.get('chain_closed')) for x in tr['entries']),
            'resource_classes': dict(Counter(x.get('resource_class') or 'NULL' for x in tr['entries'])),
            'static_map_kinds': dict(Counter(x.get('static_map_kind') or 'UNCLASSIFIED' for x in tr['entries'] if x.get('chain_closed'))),
            'unique_static_map_parents': len({x['static_map_parent']['hash'] for x in tr['entries'] if x.get('static_map_parent')}),
            'unique_static_maps': len({x['static_map']['hash'] for x in tr['entries'] if x.get('static_map')}),
            'unique_direct_d1_static_map_data': len({x['d1_static_map_data']['hash'] for x in tr['entries'] if x.get('d1_static_map_data')}),
        }
        tables.append(tr)

    closed = [x for x in rows if x.get('chain_closed')]
    static_maps = Counter(x['static_map']['hash'] for x in closed)
    parents = Counter(x['static_map_parent']['hash'] for x in closed)
    baked = [x for x in closed if x.get('static_map_kind') == 'direct_d1_baked_static']
    nonbaked = [x for x in closed if x.get('static_map_kind') == 'no_direct_d1_static_child']
    unclassified = [x for x in closed if x.get('static_map_kind') not in {'direct_d1_baked_static', 'no_direct_d1_static_child'}]
    d1_maps = Counter(x['d1_static_map_data']['hash'] for x in baked)
    expected = [norm(x) for x in a.expected_static_map]
    expected_counts = {h: static_maps.get(h, 0) for h in expected}

    if expected and any(v != 1 for v in expected_counts.values()):
        violations.append('one_or_more_expected_static_maps_not_unique:' + json.dumps(expected_counts, sort_keys=True))
    if unclassified:
        violations.append(f'unclassified_static_map_rows:{len(unclassified)}')

    out = {
        'schema_version': 3,
        'status': 'D1_WORLD_STATIC_MAP_RESOURCE_CHAIN_CLOSED' if len(closed) == len(rows) and not violations else 'D1_WORLD_STATIC_MAP_RESOURCE_CHAIN_PARTIAL',
        'pinned_source': PINNED_SOURCE,
        'root_source': root_source,
        'map_data_tables': table_roots,
        'map_data_table_count': len(tables),
        'entry_count': len(rows),
        'closed_chain_count': len(closed),
        'resource_class_counts': dict(Counter(x.get('resource_class') or 'NULL' for x in rows)),
        'static_map_kind_counts': dict(Counter(x.get('static_map_kind') or 'UNCLASSIFIED' for x in closed)),
        'unique_static_map_parent_count': len(parents),
        'unique_static_map_count': len(static_maps),
        'direct_d1_baked_entry_count': len(baked),
        'no_direct_d1_static_child_entry_count': len(nonbaked),
        'unique_direct_d1_static_map_data_count': len(d1_maps),
        'duplicate_parent_targets': {k: v for k, v in parents.items() if v != 1},
        'static_map_reference_counts': dict(static_maps),
        'expected_static_map_counts': expected_counts,
        'static_maps': sorted(static_maps),
        'direct_d1_static_map_data': sorted(d1_maps),
        'tables': tables,
        'violations': violations,
        'policy': 'Map roots may be consumed directly from an ownership manifest. Ownership closes at SStaticMapData. +0x30 is used only to classify a direct 80801B75 baked-static child; common carriers without that child are valid. 0x90 remains the SMapDataEntry stride; the post-array 0x18-per-entry resource sidecar is separate.',
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in (
        'status', 'root_source', 'map_data_table_count', 'entry_count', 'closed_chain_count',
        'resource_class_counts', 'static_map_kind_counts',
        'unique_static_map_parent_count', 'unique_static_map_count',
        'direct_d1_baked_entry_count', 'no_direct_d1_static_child_entry_count',
        'unique_direct_d1_static_map_data_count', 'expected_static_map_counts',
        'violations')}, indent=2))
    return 0 if out['status'] == 'D1_WORLD_STATIC_MAP_RESOURCE_CHAIN_CLOSED' else 2


if __name__ == '__main__':
    raise SystemExit(main())
