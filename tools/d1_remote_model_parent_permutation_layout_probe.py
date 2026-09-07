#!/usr/bin/env python3
"""Fail-closed structural probe for D1 ROI external-material permutation data.

This tool is intentionally split into two proof layers:

1. D1 authority: exact Rise-of-Iron retail bytes from the entity-owned model
   EntityResource and the D1 parent layout already pinned by Charm.
2. Comparative hypothesis testing: later-strategy MIDA places an int16 index
   array immediately before an 8-byte descriptor array and represents switch
   records as 0x18-byte containers with a nested array of 8-byte key/value
   pairs.  We test those shapes against D1 bytes, but do not promote them unless
   all D1 bounds/invariants close.

No live NPC configuration value is inferred here.  This probe only targets the
static model-parent permutation graph.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from d1_entity_resource_probe import parse_resource
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_split_tar_extract import SplitHttpTar
from d1_world_entity_dependency_census import parse_entity

ENTITY_RESOURCE = '80800861'
MODEL_PARENT = '80801A9C'
NULLS = {'00000000', 'FFFFFFFF'}

# Source-closed D1 ROI parent fields from pinned Charm.
MODEL_OFF = 0x15C
EXTERNAL_MAP_OFF = 0x230
UNKNOWN_240_OFF = 0x240
CANDIDATE_INDEX_OFF = 0x250
DESCRIPTOR_OFF = 0x260
EXTERNAL_MATERIALS_OFF = 0x270


def norm(x) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def u16(b: bytes, o: int) -> int:
    if o < 0 or o + 2 > len(b):
        raise ValueError(f'u16 OOB 0x{o:X}/0x{len(b):X}')
    return struct.unpack_from('<H', b, o)[0]


def i16(b: bytes, o: int) -> int:
    if o < 0 or o + 2 > len(b):
        raise ValueError(f'i16 OOB 0x{o:X}/0x{len(b):X}')
    return struct.unpack_from('<h', b, o)[0]


def u32(b: bytes, o: int) -> int:
    if o < 0 or o + 4 > len(b):
        raise ValueError(f'u32 OOB 0x{o:X}/0x{len(b):X}')
    return struct.unpack_from('<I', b, o)[0]


def i32(b: bytes, o: int) -> int:
    if o < 0 or o + 4 > len(b):
        raise ValueError(f'i32 OOB 0x{o:X}/0x{len(b):X}')
    return struct.unpack_from('<i', b, o)[0]


def q64(b: bytes, o: int) -> int:
    if o < 0 or o + 8 > len(b):
        raise ValueError(f'q64 OOB 0x{o:X}/0x{len(b):X}')
    return struct.unpack_from('<q', b, o)[0]


def dyn_header(b: bytes, field: int) -> dict:
    """Decode the D1 Charm-style DynamicArray header without assuming T."""
    if field < 0 or field + 0x10 > len(b):
        return {'field_offset': field, 'valid_header': False, 'error': 'header_oob'}
    count = u32(b, field)
    reserved = u32(b, field + 4)
    rel = q64(b, field + 8)
    data = field + 8 + rel + 0x10
    return {
        'field_offset': field,
        'count': count,
        'reserved_u32': reserved,
        'relative_qword': rel,
        'data_offset': data,
        'valid_header': True,
    }


def dyn_with_elem(b: bytes, field: int, elem_size: int) -> dict:
    d = dyn_header(b, field)
    d['element_size'] = elem_size
    if not d.get('valid_header'):
        d['bounds_valid'] = False
        return d
    count = int(d['count'])
    data = int(d['data_offset'])
    end = data + count * elem_size
    d['data_end'] = end
    d['bounds_valid'] = (0 <= data <= len(b) and 0 <= end <= len(b))
    return d


def exact_payload(c: RemoteCorpus, tag: str, expected_ref: str | None = None) -> tuple[dict, bytes, str | None]:
    tag = norm(tag)
    m = c.entry_meta(tag)
    b, src = c.payload(tag)
    if m is None or b is None:
        raise ValueError(f'{tag}: exact payload unavailable')
    ref = norm(m.get('reference', 'FFFFFFFF'))
    if expected_ref is not None and ref != norm(expected_ref):
        raise ValueError(f'{tag}: reference {ref} != {norm(expected_ref)}')
    return m, b, src


def parse_map(b: bytes, base: int) -> dict:
    d = dyn_with_elem(b, base + EXTERNAL_MAP_OFF, 0x0C)
    rows = []
    if d['bounds_valid']:
        for i in range(d['count']):
            o = d['data_offset'] + i * 0x0C
            rows.append({
                'index': i,
                'material_count': i32(b, o),
                'material_start_index': i32(b, o + 4),
                'unk08': i32(b, o + 8),
            })
    d['rows'] = rows
    return d


def parse_materials(b: bytes, base: int) -> dict:
    d = dyn_with_elem(b, base + EXTERNAL_MATERIALS_OFF, 4)
    vals = []
    if d['bounds_valid']:
        vals = [f'{u32(b, d["data_offset"] + i * 4):08X}' for i in range(d['count'])]
    d['tag_hashes'] = vals
    return d


def parse_candidate_indices(b: bytes, base: int) -> dict:
    d = dyn_with_elem(b, base + CANDIDATE_INDEX_OFF, 2)
    vals_u = []
    vals_s = []
    if d['bounds_valid']:
        for i in range(d['count']):
            o = d['data_offset'] + i * 2
            vals_u.append(u16(b, o))
            vals_s.append(i16(b, o))
    d['u16_values'] = vals_u
    d['i16_values'] = vals_s
    d['u16_min'] = min(vals_u) if vals_u else None
    d['u16_max'] = max(vals_u) if vals_u else None
    d['negative_i16_count'] = sum(v < 0 for v in vals_s)
    return d


def parse_descriptors(b: bytes, base: int, index_count: int | None) -> dict:
    # Charm source closes this field as D1 FE1A8080: four ushort fields.
    d = dyn_with_elem(b, base + DESCRIPTOR_OFF, 8)
    rows = []
    bound_ok = 0
    bound_bad = 0
    if d['bounds_valid']:
        for i in range(d['count']):
            o = d['data_offset'] + i * 8
            vals = [u16(b, o + k) for k in (0, 2, 4, 6)]
            # Comparative MIDA interpretation only: first=count, second=start.
            count, start = vals[0], vals[1]
            in_bounds = None if index_count is None else (start <= index_count and count <= index_count - start)
            if in_bounds is True:
                bound_ok += 1
            elif in_bounds is False:
                bound_bad += 1
            rows.append({
                'index': i,
                'u16': vals,
                'candidate_count': count,
                'candidate_start': start,
                'candidate_index_bounds_valid': in_bounds,
            })
    d['rows'] = rows
    d['candidate_count_start_bounds_valid_count'] = bound_ok
    d['candidate_count_start_bounds_invalid_count'] = bound_bad
    return d


def early_dynamic_headers(b: bytes, base: int) -> list[dict]:
    out = []
    # Deliberately scan aligned parent fields only, not arbitrary payload windows.
    for rel in range(0x00, MODEL_OFF, 0x08):
        field = base + rel
        d = dyn_header(b, field)
        if not d.get('valid_header'):
            continue
        count = int(d['count'])
        data = int(d['data_offset'])
        # A useful candidate must have a sane non-zero count, zero reserved lane,
        # and a data pointer inside this exact EntityResource payload.
        plausible = (0 < count <= 4096 and d['reserved_u32'] == 0 and 0 <= data < len(b))
        if plausible:
            out.append({
                'parent_relative_offset': rel,
                **d,
            })
    return out


def test_switch_container_candidate(b: bytes, row: dict) -> dict:
    """Test the MIDA 0x18-container + nested 8-byte pair shape against D1.

    This is a structural test only.  A passing shape is not by itself a semantic
    promotion of the array to D1 switch records.
    """
    count = int(row['count'])
    data = int(row['data_offset'])
    outer_size = 0x18
    outer_end = data + count * outer_size
    result = {
        'parent_relative_offset': row['parent_relative_offset'],
        'outer_count': count,
        'outer_element_size_tested': outer_size,
        'outer_bounds_valid': 0 <= data <= len(b) and 0 <= outer_end <= len(b),
        'inner_headers_valid': 0,
        'inner_headers_nonzero': 0,
        'inner_pair_total': 0,
        'inner_pair_nonzero_key_count': 0,
        'inner_pair_rows': [],
    }
    if not result['outer_bounds_valid']:
        return result
    all_valid = True
    for i in range(count):
        elem = data + i * outer_size
        # Comparative MIDA S8080BACC places nested DynamicArray at +0x08.
        inner = dyn_with_elem(b, elem + 0x08, 8)
        valid = bool(inner['bounds_valid'] and inner['count'] <= 256)
        if not valid:
            all_valid = False
            continue
        result['inner_headers_valid'] += 1
        if inner['count']:
            result['inner_headers_nonzero'] += 1
        pairs = []
        for j in range(inner['count']):
            p = inner['data_offset'] + j * 8
            key, val = u32(b, p), u32(b, p + 4)
            pairs.append([f'{key:08X}', f'{val:08X}'])
            result['inner_pair_total'] += 1
            if key not in (0, 0xFFFFFFFF):
                result['inner_pair_nonzero_key_count'] += 1
        if pairs:
            result['inner_pair_rows'].append({'outer_index': i, 'pairs': pairs})
    result['all_outer_elements_have_valid_nested_pair_array'] = all_valid and result['inner_headers_valid'] == count
    return result


def model_rows(entity_row: dict, model_tag: str) -> list[dict]:
    target = norm(model_tag)
    rows = []
    for r in entity_row.get('resources', []):
        er = r.get('entity_resource') or {}
        if er.get('semantic_role') == 'entity_model' and norm(er.get('embedded_model_tag_hash', 'FFFFFFFF')) == target:
            rows.append(r)
    return rows


def probe_one(c: RemoteCorpus, entity: str, model_tag: str) -> dict:
    entity = norm(entity)
    erow = parse_entity(c, entity)
    matches = model_rows(erow, model_tag)
    out = {
        'entity': entity,
        'entity_parse_violations': erow.get('violations', []),
        'matching_model_resource_count': len(matches),
    }
    if len(matches) != 1:
        out['error'] = f'expected exactly one entity_model resource for {norm(model_tag)}, got {len(matches)}'
        return out
    rr = matches[0]
    resource = norm(rr['resource_hash'])
    meta, payload, src = exact_payload(c, resource, ENTITY_RESOURCE)
    parsed = parse_resource(payload, meta.get('platform'))
    parent = parsed.get('unk18') or {}
    base = parent.get('target_offset')
    out.update({
        'model_entity_resource': resource,
        'model_entity_resource_reference': norm(meta.get('reference', 'FFFFFFFF')),
        'model_entity_resource_source': src,
        'model_entity_resource_bytes': len(payload),
        'model_entity_resource_sha256': hashlib.sha256(payload).hexdigest(),
        'parsed_model_tag': parsed.get('embedded_model_tag_hash'),
        'parent_class_hash': parent.get('class_hash'),
        'parent_offset': base,
    })
    if parent.get('class_hash') != MODEL_PARENT or not isinstance(base, int):
        out['error'] = 'model parent class/offset mismatch'
        return out
    if norm(parsed.get('embedded_model_tag_hash', 'FFFFFFFF')) != norm(model_tag):
        out['error'] = 'embedded model mismatch'
        return out

    known_map = parse_map(payload, base)
    materials = parse_materials(payload, base)
    index_candidate = parse_candidate_indices(payload, base)
    descriptors = parse_descriptors(payload, base, index_candidate['count'] if index_candidate['bounds_valid'] else None)
    slot240 = dyn_header(payload, base + UNKNOWN_240_OFF)

    headers = early_dynamic_headers(payload, base)
    switch_tests = [test_switch_container_candidate(payload, h) for h in headers]
    switch_tests.sort(key=lambda x: (
        bool(x.get('all_outer_elements_have_valid_nested_pair_array')),
        int(x.get('inner_pair_nonzero_key_count', 0)),
        int(x.get('inner_pair_total', 0)),
    ), reverse=True)

    map_ranges_valid = bool(known_map['bounds_valid'] and materials['bounds_valid'])
    if map_ranges_valid:
        for r in known_map['rows']:
            c0, s0 = r['material_count'], r['material_start_index']
            if c0 < 0 or s0 < 0 or s0 + c0 > materials['count']:
                map_ranges_valid = False
                break

    descriptor_index_bounds_all = bool(
        descriptors['bounds_valid'] and index_candidate['bounds_valid'] and
        descriptors['candidate_count_start_bounds_invalid_count'] == 0
    )

    exact_switch_candidates = [x for x in switch_tests if x.get('all_outer_elements_have_valid_nested_pair_array') and x.get('inner_pair_total', 0) > 0]

    out['parent_fields'] = {
        'external_materials_map': known_map,
        'unknown_0x240_header': slot240,
        'candidate_index_0x250_as_i16': index_candidate,
        'descriptor_0x260_FE1A8080': descriptors,
        'external_materials': materials,
    }
    out['early_dynamic_array_headers'] = headers
    out['switch_container_shape_tests'] = switch_tests
    out['invariants'] = {
        'external_map_ranges_inside_material_bank': map_ranges_valid,
        'candidate_0x250_bounds_valid_as_i16': bool(index_candidate['bounds_valid']),
        'descriptor_0x260_bounds_valid': bool(descriptors['bounds_valid']),
        'all_descriptor_candidate_count_start_ranges_inside_0x250': descriptor_index_bounds_all,
        'switch_container_shape_candidate_count': len(exact_switch_candidates),
        'switch_container_shape_candidate_offsets': [f'0x{x["parent_relative_offset"]:X}' for x in exact_switch_candidates],
    }

    static_graph_shape_exact = bool(
        map_ranges_valid and index_candidate['bounds_valid'] and descriptors['bounds_valid'] and
        descriptor_index_bounds_all and len(exact_switch_candidates) == 1
    )
    out['static_graph_shape_exact'] = static_graph_shape_exact
    if static_graph_shape_exact:
        out['unique_switch_container_candidate'] = exact_switch_candidates[0]
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--entity', action='append', required=True)
    ap.add_argument('--model-tag', default='80C88CEF')
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    cats = load_catalogs(a.member_catalog)
    arc = SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    c = RemoteCorpus(arc, cats, a.runtime)

    rows = []
    violations = []
    for e in a.entity:
        try:
            row = probe_one(c, e, a.model_tag)
        except Exception as ex:
            row = {'entity': norm(e), 'error': repr(ex)}
        rows.append(row)
        if row.get('error'):
            violations.append(f"{row['entity']}:{row['error']}")

    # Cross-entity identity: both serialized Xur entities should resolve to the
    # same exact model-owner payload for a shared model-family proof.
    owner_hashes = {r.get('model_entity_resource_sha256') for r in rows if r.get('model_entity_resource_sha256')}
    parent_classes = {r.get('parent_class_hash') for r in rows if r.get('parent_class_hash')}
    model_tags = {norm(r.get('parsed_model_tag', 'FFFFFFFF')) for r in rows if r.get('parsed_model_tag')}
    exact_rows = [r for r in rows if r.get('static_graph_shape_exact')]

    status = 'D1_XUR_MODEL_PARENT_PERMUTATION_LAYOUT_EXACT' if (
        not violations and len(exact_rows) == len(rows) and len(owner_hashes) == 1 and
        parent_classes == {MODEL_PARENT} and model_tags == {norm(a.model_tag)}
    ) else 'D1_XUR_MODEL_PARENT_PERMUTATION_LAYOUT_FRONTIER'

    rep = {
        'schema_version': 1,
        'status': status,
        'target_model': norm(a.model_tag),
        'entities': [norm(x) for x in a.entity],
        'comparative_hypothesis': {
            'source': 'MIDA Marathon ModelPermutation architecture',
            'd1_authority_rule': 'comparative offsets/types are promoted only when exact D1 retail bytes close all bounds/invariants',
            'candidate_index_parent_offset': '0x250',
            'source_closed_d1_descriptor_parent_offset': '0x260',
        },
        'rows': rows,
        'cross_entity': {
            'unique_model_owner_payload_sha256_count': len(owner_hashes),
            'unique_model_owner_payload_sha256': sorted(x for x in owner_hashes if x),
            'parent_classes': sorted(parent_classes),
            'embedded_model_tags': sorted(model_tags),
        },
        'violations': violations,
        'live_configuration_state_complete': False,
        'retail_material_member_selection_complete': False,
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(rep, indent=2) + '\n')
    print(json.dumps({
        'status': status,
        'row_count': len(rows),
        'owner_sha_count': len(owner_hashes),
        'static_exact_rows': len(exact_rows),
        'violations': violations,
        'row_summaries': [
            {
                'entity': r.get('entity'),
                'resource': r.get('model_entity_resource'),
                'parent_offset': r.get('parent_offset'),
                'map_count': ((r.get('parent_fields') or {}).get('external_materials_map') or {}).get('count'),
                'index_0x250_count': ((r.get('parent_fields') or {}).get('candidate_index_0x250_as_i16') or {}).get('count'),
                'descriptor_0x260_count': ((r.get('parent_fields') or {}).get('descriptor_0x260_FE1A8080') or {}).get('count'),
                'material_count': ((r.get('parent_fields') or {}).get('external_materials') or {}).get('count'),
                'switch_candidates': (r.get('invariants') or {}).get('switch_container_shape_candidate_offsets'),
                'static_graph_shape_exact': r.get('static_graph_shape_exact'),
            } for r in rows
        ],
    }, indent=2))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
