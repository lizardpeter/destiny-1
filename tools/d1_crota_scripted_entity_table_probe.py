#!/usr/bin/env python3
"""Decode selected D1 Crota's End SD912/808012D9 scripted-entity tables.

Pinned source schema:
  MontagueM/Charm@50d36ee1f9ecadad7522504c20b1f3f9c97e30af
  Tiger/Schema/Activity/ActivityStructsROI.cs
  Tiger/Schema/Static/StaticMapData.cs

This is the schema-specific closure stage after a literal FileHash backlink scan.
It proves field meaning for 808012D9 records instead of treating aligned u32 hits as
semantic ownership. Each selected table emits script-family/type StringHashes and
its embedded SMapDataEntry records (EntitySK, transform, WorldID, optional instance
EntityName StringHash).

No EntitySK is identified as Crota by this tool. Semantic promotion still requires
an exact name/archetype/encounter ownership edge.
"""
from __future__ import annotations

import argparse
import collections
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_crota_raid_candidate_probe import LazyExactHashResolver
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_split_tar_extract import SplitHttpTar
from d1_world_scripted_entity_identity_census import (
    D912,
    MAP_ENTRY_CLASS,
    NULLS,
    dyn,
    hx,
    parse_scripted_map_entry,
    resource_ptr,
)


def norm(x: str) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def u32(b: bytes, o: int) -> int:
    if o < 0 or o + 4 > len(b):
        raise ValueError(f'u32 out of bounds at 0x{o:X}/0x{len(b):X}')
    return struct.unpack_from('<I', b, o)[0]


def parse_table(resolver: LazyExactHashResolver, tag_hash: str) -> dict:
    h = norm(tag_hash)
    view, entry = resolver.locate(h)
    out = {
        'scripted_entity_table': h,
        'package_id': f"{int(view.h['pkg_id']):04X}",
        'logical_view': view.view.name,
        'entry_index': int(entry['index']),
        'reference': entry['reference'].upper(),
        'file_size': int(entry['file_size']),
        'violations': [],
        'groups': [],
        'records': [],
    }
    if out['reference'] != D912:
        out['violations'].append(f'reference_{out["reference"]}_not_{D912}')
        return out
    b = view.entry(entry['index'])
    if len(b) < 0x40:
        out['violations'].append('payload_shorter_than_0x40')
        return out
    out['payload_size'] = len(b)
    out['script_family_string_hash'] = hx(u32(b, 0x08))
    out['unk0C_tiger_hash'] = hx(u32(b, 0x0C))
    out['unk10_file_hash'] = hx(u32(b, 0x10))
    groups = dyn(b, 0x20, 0x38)
    locations = dyn(b, 0x30, 0x30)
    out['groups_array'] = groups
    out['locations_array'] = locations
    if not groups['ok']:
        out['violations'].append('groups_bounds')
        return out
    if not locations['ok']:
        out['violations'].append('locations_bounds')

    for gi in range(groups['count']):
        go = groups['absolute'] + gi * 0x38
        group = {
            'group_index': gi,
            'record_offset': go,
            'type_string_hash': hx(u32(b, go)),
            'violations': [],
            'records': [],
        }
        arr = dyn(b, go + 0x08, 0x10)
        group['records_array'] = arr
        if not arr['ok']:
            group['violations'].append('scripted_record_array_bounds')
        else:
            for ri in range(arr['count']):
                ro = arr['absolute'] + ri * 0x10
                rp = resource_ptr(b, ro)
                row = {
                    'group_index': gi,
                    'record_index': ri,
                    'record_offset': ro,
                    'type_string_hash': group['type_string_hash'],
                    'map_entry_pointer': rp,
                    'violations': [],
                }
                if not rp['ok']:
                    row['violations'].append('S481_resource_pointer_invalid')
                elif rp.get('resource_class') != MAP_ENTRY_CLASS:
                    row['violations'].append(
                        f'S481_resource_class_{rp.get("resource_class")}_not_{MAP_ENTRY_CLASS}'
                    )
                elif isinstance(rp.get('absolute'), int):
                    parsed = parse_scripted_map_entry(
                        b,
                        rp['absolute'],
                        {'D912': h, 'group': gi, 'record': ri},
                    )
                    row.update(parsed)
                    row['violations'].extend(parsed.get('violations', []))
                if row['violations']:
                    group['violations'].extend(f'record[{ri}]:{x}' for x in row['violations'])
                group['records'].append(row)
                out['records'].append(row)
        if group['violations']:
            out['violations'].extend(f'group[{gi}]:{x}' for x in group['violations'])
        out['groups'].append(group)

    out['group_count'] = len(out['groups'])
    out['record_count'] = len(out['records'])
    out['entity_hash_counts'] = dict(collections.Counter(
        r['entity_hash'] for r in out['records'] if r.get('entity_hash') not in NULLS
    ))
    out['entity_name_string_hash_counts'] = dict(collections.Counter(
        r['entity_name_string_hash'] for r in out['records']
        if r.get('entity_name_string_hash') not in (None, *NULLS)
    ))
    out['type_string_hash_counts'] = dict(collections.Counter(
        r['type_string_hash'] for r in out['records'] if r.get('type_string_hash') not in NULLS
    ))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--table', action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    catalogs = load_catalogs(a.member_catalog)
    base = a.base_url.rstrip('/')
    arc = SplitHttpTar(
        [f'{base}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)],
        retries=6,
        timeout=90,
    )
    resolver = LazyExactHashResolver(arc, catalogs, a.runtime)
    tables = [parse_table(resolver, h) for h in dict.fromkeys(a.table)]
    violations = [
        f"{t['scripted_entity_table']}:{v}"
        for t in tables for v in t.get('violations', [])
    ]
    entity_counts = collections.Counter()
    name_counts = collections.Counter()
    family_counts = collections.Counter()
    type_counts = collections.Counter()
    for t in tables:
        family = t.get('script_family_string_hash')
        if family not in (None, *NULLS):
            family_counts[family] += 1
        entity_counts.update(t.get('entity_hash_counts', {}))
        name_counts.update(t.get('entity_name_string_hash_counts', {}))
        type_counts.update(t.get('type_string_hash_counts', {}))

    report = {
        'schema': 'd1_crota_scripted_entity_table_probe/v1',
        'status': 'D1_CROTA_SCRIPTED_ENTITY_TABLES_EXACT' if not violations else 'D1_CROTA_SCRIPTED_ENTITY_TABLES_PARTIAL',
        'table_count': len(tables),
        'script_family_string_hash_counts': dict(family_counts),
        'type_string_hash_counts': dict(type_counts),
        'entity_hash_counts': dict(entity_counts),
        'entity_name_string_hash_counts': dict(name_counts),
        'tables': tables,
        'violations': violations,
        'pinned_schema_source': 'MontagueM/Charm@50d36ee1f9ecadad7522504c20b1f3f9c97e30af ActivityStructsROI.cs + StaticMapData.cs',
        'policy': (
            '808012D9 field semantics are decoded from the source-pinned D1 schema. '
            'EntitySK occurrence in one scripted map entry is exact instance/spawn evidence, '
            'but it does not by itself prove that an entity is Crota.'
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + '\n')
    print('STATUS', report['status'], 'TABLES', len(tables), 'VIOLATIONS', len(violations))
    print('FAMILIES', dict(family_counts))
    print('TYPES', dict(type_counts))
    print('ENTITIES', dict(entity_counts))
    print('INSTANCE_NAMES', dict(name_counts))
    for t in tables:
        print('\nTABLE', t['scripted_entity_table'], 'FAMILY', t.get('script_family_string_hash'),
              'GROUPS', t.get('group_count'), 'RECORDS', t.get('record_count'))
        for g in t.get('groups', []):
            print(' GROUP', g['group_index'], 'TYPE', g['type_string_hash'])
            for r in g.get('records', []):
                print('  RECORD', r['record_index'], 'ENTITY', r.get('entity_hash'),
                      'WORLD', r.get('world_id_hex'), 'INSTANCE_NAME', r.get('entity_name_string_hash'),
                      'POS', r.get('translation'))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
