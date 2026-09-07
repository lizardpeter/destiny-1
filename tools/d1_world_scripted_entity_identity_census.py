#!/usr/bin/env python3
"""Trace D1 ROI scripted-entity identity records to source-owned world placements.

Pinned Charm source:
  MontagueM/Charm@50d36ee1f9ecadad7522504c20b1f3f9c97e30af
  Tiger/Schema/Activity/ActivityStructsROI.cs
  Tiger/Schema/Static/StaticMapData.cs

Source chain:

  SA7058080 / 808005A7
    +0x68 Tag<SD9128080>
  SD9128080 / 808012D9
    +0x08 StringHash (script/dev family; source comment example sq_machine)
    +0x0C TigerHash
    +0x10 FileHash
    +0x20 DynamicArray<SD6148080>, stride 0x38
  SD6148080
    +0x00 StringHash Type (source comment example boss)
    +0x08 DynamicArray<S48138080>, stride 0x10
  S48138080
    +0x00 ResourcePointer -> SMapDataEntry / 80800406
  SMapDataEntry / 80800406, size 0x90
    +0x00 EntitySK FileHash
    +0x20 Rotation Vector4
    +0x30 Translation Vector4
    +0x80 WorldID u64
    +0x88 DataResource ResourcePointer -> S33138080 / 80801333
  S33138080 / 80801333
    +0x00 ResourcePointer -> S152B8080 / 80802B15
    +0x20 StringHash EntityName

D912 SMapDataEntry records are scripted overlays, not redundant copies of the
runtime placement table. Retail King's Fall, Wrath, strike and Plaguelands data
proves that a scripted record may have the same WorldID and exact transform as a
runtime placement while serializing a different EntitySK. Both hashes are preserved
and are never aliased.

A scripted EntityName StringHash is eligible to attach to runtime placement identity
only when BOTH WorldID and EntitySK agree with the independently materialized
Activity placement census. Transform agreement is reported independently. A script
record is never used to rename an SEntity family globally: identity is instance-owned
evidence.
"""
from __future__ import annotations

import argparse
import json
import math
import struct
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import d1_tower_map_schema_validate_v5 as v5

A705 = '808005A7'
D912 = '808012D9'
MAP_ENTRY_CLASS = '80800406'
SCRIPT_NAME_DATA = '80801333'
S152 = '80802B15'
MAP_ENTRY_STRIDE = 0x90
NULLS = {'00000000', 'FFFFFFFF'}
PINNED_SOURCE = (
    'MontagueM/Charm@50d36ee1f9ecadad7522504c20b1f3f9c97e30af '
    'Tiger/Schema/Activity/ActivityStructsROI.cs + Tiger/Schema/Static/StaticMapData.cs + Tiger/SchemaTypes.cs'
)


def norm(x):
    return str(x).upper().removeprefix('0X').zfill(8)


def hx(v):
    return f'{v:08X}'


def u32(b, o):
    return struct.unpack_from('<I', b, o)[0]


def u64(b, o):
    return struct.unpack_from('<Q', b, o)[0]


def i32(b, o):
    return struct.unpack_from('<i', b, o)[0]


def i64(b, o):
    return struct.unpack_from('<q', b, o)[0]


def f4(b, o):
    return list(struct.unpack_from('<4f', b, o))


def dyn(b, off, stride):
    if off + 0x10 > len(b):
        return {'ok': False, 'field_offset': off, 'error': 'descriptor_oob'}
    count = i32(b, off)
    unk = u32(b, off + 4)
    rel = i64(b, off + 8)
    absolute = off + 8 + rel + 0x10
    end = absolute + max(count, 0) * stride
    pointer_ok = absolute >= 0 and end <= len(b)
    ok = count >= 0 and (count == 0 or pointer_ok)
    return {
        'ok': ok, 'field_offset': off, 'count': count, 'unknown04': unk,
        'relative': rel, 'absolute': absolute, 'end': end, 'stride': stride,
        'serialized_pointer_bounds_ok': pointer_ok,
        'zero_count_no_dereference': count == 0,
        'payload_size': len(b),
    }


def resource_ptr(b, off):
    if off + 8 > len(b):
        return {'ok': False, 'field_offset': off, 'error': 'pointer_oob'}
    rel = i64(b, off)
    out = {'ok': True, 'field_offset': off, 'relative': rel, 'absolute': None, 'resource_class': None, 'is_null': rel == 0}
    if rel == 0:
        return out
    absolute = off + rel
    out['absolute'] = absolute
    if absolute < 4 or absolute > len(b):
        out['ok'] = False
        out['error'] = 'target_oob'
        return out
    out['resource_class_offset'] = absolute - 4
    out['resource_class'] = hx(u32(b, absolute - 4))
    return out


def current_hashes_by_ref(c, ref):
    hashes = set()
    for _, _, _, e in c.occurrences_by_ref(ref):
        h = norm(e['tag_hash'])
        m = c.entry_meta(h)
        if m and norm(m.get('reference', '')) == ref:
            hashes.add(h)
    return sorted(hashes)


def placement_index(p):
    rows = p.get('unique_world_placements')
    if rows is None:
        rows = []
        seen = {}
        for key in ('direct_tables', 'tables'):
            for t in p.get(key, []):
                for x in t.get('entries', []):
                    if norm(x.get('entity_hash', 'FFFFFFFF')) in NULLS:
                        continue
                    wid = x.get('world_id_hex')
                    sig = (norm(x.get('entity_hash')), tuple(x.get('rotation') or []), tuple(x.get('translation') or []))
                    if wid in seen and seen[wid][0] != sig:
                        raise ValueError(f'placement census has conflicting WorldID {wid}')
                    seen[wid] = (sig, x)
        rows = [v[1] for _, v in sorted(seen.items())]
    return {str(x.get('world_id_hex')).upper(): x for x in rows if x.get('world_id_hex')}


def close_vec(a, b, eps=1e-5):
    if a is None or b is None or len(a) != len(b):
        return False
    return all(math.isfinite(float(x)) and math.isfinite(float(y)) and abs(float(x) - float(y)) <= eps for x, y in zip(a, b))


def classify_runtime_relation(world_exists, entity_match, transform_match):
    if not world_exists:
        return 'WORLDID_NOT_IN_RUNTIME_PLACEMENTS'
    if entity_match and transform_match:
        return 'WORLDID_ENTITY_TRANSFORM_MATCH'
    if entity_match:
        return 'WORLDID_ENTITY_MATCH_TRANSFORM_DIFFERS'
    if transform_match:
        return 'WORLDID_TRANSFORM_MATCH_ENTITY_DIFFERS'
    return 'WORLDID_MATCH_ENTITY_AND_TRANSFORM_DIFFER'


def parse_scripted_map_entry(host, base, source):
    out = {
        'map_entry_absolute': base,
        'source': source,
        'violations': [],
    }
    if base < 0 or base + MAP_ENTRY_STRIDE > len(host):
        out['violations'].append('map_entry_oob')
        return out
    out['entity_hash'] = hx(u32(host, base))
    out['rotation'] = f4(host, base + 0x20)
    out['translation'] = f4(host, base + 0x30)
    out['world_id'] = u64(host, base + 0x80)
    out['world_id_hex'] = f'{out["world_id"]:016X}'
    dr = resource_ptr(host, base + 0x88)
    out['data_resource'] = dr
    if not dr['ok']:
        out['violations'].append('map_entry_data_resource_invalid')
        return out
    if dr.get('resource_class') != SCRIPT_NAME_DATA:
        out['script_name_data_present'] = False
        out['script_name_data_class'] = dr.get('resource_class')
        return out
    nbase = dr.get('absolute')
    out['script_name_data_present'] = True
    out['script_name_data_class'] = SCRIPT_NAME_DATA
    out['script_name_data_absolute'] = nbase
    if not isinstance(nbase, int) or nbase < 0 or nbase + 0x34 > len(host):
        out['violations'].append('S331_script_name_data_oob')
        return out
    nested = resource_ptr(host, nbase)
    out['script_name_nested_resource'] = nested
    if nested['ok'] and not nested.get('is_null') and nested.get('resource_class') not in (S152, None):
        out['violations'].append(f'S331_nested_resource_class_{nested.get("resource_class")}_not_{S152}')
    out['entity_name_string_hash'] = hx(u32(host, nbase + 0x20))
    return out


def parse_d912(c, h, placements):
    h = norm(h)
    b, src = c.payload(h)
    m = c.entry_meta(h)
    out = {
        'scripted_entity_table': h,
        'meta': m,
        'payload_source': src,
        'violations': [],
        'groups': [],
        'records': [],
    }
    if m is None or norm(m.get('reference', '')) != D912 or b is None:
        out['violations'].append('D912_missing_class_or_payload')
        return out
    if len(b) < 0x40:
        out['violations'].append('D912_payload_shorter_than_0x40')
        return out
    out['script_family_string_hash'] = hx(u32(b, 0x08))
    out['unk0C_tiger_hash'] = hx(u32(b, 0x0C))
    out['unk10_file_hash'] = hx(u32(b, 0x10))
    groups = dyn(b, 0x20, 0x38)
    locations = dyn(b, 0x30, 0x30)
    out['groups_array'] = groups
    out['locations_array'] = locations
    if not groups['ok']:
        out['violations'].append('D912_groups_bounds')
        return out
    if not locations['ok']:
        out['violations'].append('D912_locations_bounds')
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
                    row['violations'].append(f'S481_resource_class_{rp.get("resource_class")}_not_{MAP_ENTRY_CLASS}')
                elif isinstance(rp.get('absolute'), int):
                    parsed = parse_scripted_map_entry(b, rp['absolute'], {'D912': h, 'group': gi, 'record': ri})
                    row.update(parsed)
                    row['violations'].extend(parsed.get('violations', []))
                    wid = row.get('world_id_hex')
                    live = placements.get(wid)
                    if live is None:
                        world_exists = False
                        entity_match = False
                        transform_match = False
                        placement_entity_hash = None
                    else:
                        world_exists = True
                        entity_match = norm(live.get('entity_hash', 'FFFFFFFF')) == norm(row.get('entity_hash', 'FFFFFFFF'))
                        transform_match = close_vec(live.get('rotation'), row.get('rotation')) and close_vec(live.get('translation'), row.get('translation'))
                        placement_entity_hash = norm(live.get('entity_hash', 'FFFFFFFF'))
                    relation = classify_runtime_relation(world_exists, entity_match, transform_match)
                    row['placement_match'] = {
                        'world_id_exists': world_exists,
                        'entity_matches': entity_match,
                        'transform_matches': transform_match,
                        'placement_entity_hash': placement_entity_hash,
                        'relation': relation,
                    }
                    row['scripted_runtime_relation'] = relation
                    row['placement_identity_attachment_eligible'] = bool(world_exists and entity_match)
                    row['placement_identity_transform_exact'] = bool(world_exists and entity_match and transform_match)
                if row['violations']:
                    group['violations'].extend(f'record[{ri}]:{x}' for x in row['violations'])
                group['records'].append(row)
                out['records'].append(row)
        if group['violations']:
            out['violations'].extend(f'group[{gi}]:{x}' for x in group['violations'])
        out['groups'].append(group)
    out['group_count'] = len(out['groups'])
    out['record_count'] = len(out['records'])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', type=Path, action='append', required=True)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--placements', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    p = json.loads(a.placements.read_text())
    placements = placement_index(p)
    c = v5.v3.base.Corpus([x.resolve() for x in a.snapshot], a.runtime.resolve())
    a705_hashes = current_hashes_by_ref(c, A705)
    d912_from_a705 = []
    a705_rows = []
    violations = []
    for h in a705_hashes:
        b, src = c.payload(h)
        row = {'a705': h, 'meta': c.entry_meta(h), 'payload_source': src, 'd912': None, 'violations': []}
        if b is None or len(b) < 0x6C:
            row['violations'].append('A705_missing_or_short_payload')
        else:
            dh = hx(u32(b, 0x68))
            row['d912'] = dh
            dm = c.entry_meta(dh)
            row['d912_meta'] = dm
            if dh not in NULLS:
                d912_from_a705.append(dh)
                if dm is None or norm(dm.get('reference', '')) != D912:
                    row['violations'].append('A705_d912_target_missing_or_class_mismatch')
        violations.extend(f'{h}:{x}' for x in row['violations'])
        a705_rows.append(row)
    current_d912 = current_hashes_by_ref(c, D912)
    d912_hashes = sorted(set(current_d912) | set(d912_from_a705))
    tables = [parse_d912(c, h, placements) for h in d912_hashes]
    for t in tables:
        violations.extend(f'{t["scripted_entity_table"]}:{x}' for x in t['violations'])

    records = [r for t in tables for r in t.get('records', [])]
    named = [r for r in records if r.get('entity_name_string_hash') not in (None, '00000000', 'FFFFFFFF')]
    matched_named = [r for r in named if r.get('placement_identity_attachment_eligible')]
    fully_matched_named = [r for r in named if r.get('placement_identity_transform_exact')]
    named_unattached = [r for r in named if not r.get('placement_identity_attachment_eligible')]
    relations = Counter(r.get('scripted_runtime_relation', 'NO_RUNTIME_PLACEMENT_EVIDENCE') for r in records)
    name_hashes = Counter(r['entity_name_string_hash'] for r in named)
    type_hashes = Counter(r['type_string_hash'] for r in records if r.get('type_string_hash') not in NULLS)
    family_hashes = Counter(t['script_family_string_hash'] for t in tables if t.get('script_family_string_hash') not in NULLS)
    named_worldids = Counter(r['world_id_hex'] for r in named if r.get('world_id_hex'))
    named_entities = Counter(r['entity_hash'] for r in named if r.get('entity_hash') not in NULLS)
    out = {
        'schema_version': 2,
        'status': 'D1_WORLD_SCRIPTED_ENTITY_IDENTITY_CENSUS_COMPLETE' if not violations else 'D1_WORLD_SCRIPTED_ENTITY_IDENTITY_CENSUS_PARTIAL',
        'pinned_source': PINNED_SOURCE,
        'runtime_placement_world_id_count': len(placements),
        'current_a705_count': len(a705_rows),
        'current_d912_count': len(current_d912),
        'reachable_d912_from_a705_count': len(set(d912_from_a705)),
        'scripted_table_count': len(tables),
        'scripted_record_count': len(records),
        'named_scripted_record_count': len(named),
        'named_record_world_id_entity_match_count': len(matched_named),
        'named_record_full_transform_match_count': len(fully_matched_named),
        'named_record_unattached_count': len(named_unattached),
        'scripted_runtime_relation_counts': dict(relations),
        'unique_entity_name_string_hash_count': len(name_hashes),
        'entity_name_string_hash_reference_counts': dict(name_hashes),
        'unique_type_string_hash_count': len(type_hashes),
        'type_string_hash_reference_counts': dict(type_hashes),
        'script_family_string_hash_reference_counts': dict(family_hashes),
        'named_world_id_reference_counts': dict(named_worldids),
        'named_entity_reference_counts': dict(named_entities),
        'a705_roots': a705_rows,
        'scripted_tables': tables,
        'violations': violations,
        'policy': (
            'D912 records are scripted overlays, not redundant placement copies. Scripted identity is attached only at the instance level. EntityName StringHash becomes placement evidence only when WorldID exists in the independently materialized Activity placement census and EntitySK matches. A matching WorldID/transform with a different EntitySK is preserved as WORLDID_TRANSFORM_MATCH_ENTITY_DIFFERS and is not a violation or alias. No SEntity family is globally renamed by this layer.'
        ),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in (
        'status', 'runtime_placement_world_id_count', 'current_a705_count', 'current_d912_count',
        'reachable_d912_from_a705_count', 'scripted_table_count', 'scripted_record_count',
        'named_scripted_record_count', 'named_record_world_id_entity_match_count',
        'named_record_full_transform_match_count', 'named_record_unattached_count',
        'scripted_runtime_relation_counts', 'unique_entity_name_string_hash_count',
        'entity_name_string_hash_reference_counts', 'unique_type_string_hash_count', 'violations')}, indent=2))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
