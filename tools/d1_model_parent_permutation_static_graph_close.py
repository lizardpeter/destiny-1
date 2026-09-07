#!/usr/bin/env python3
"""Close the static D1 ROI model-parent external-material permutation graph.

Input is the exact retail layout report emitted by
`d1_remote_model_parent_permutation_layout_probe.py`.

This promotes only relationships directly forced by the D1 bytes:

* ExternalMaterialsMap member ranges -> material bank;
* ExternalMaterialsMap.Unk08 -> a same-length range in the +0x260 descriptor bank;
* +0x250 -> an indirect switch-record-index list used when a descriptor list
  contains more than one switch record;
* +0x260 FE1A8080 descriptor -> two encoded lists of switch-record indices;
* parent +0x50 -> 0x18-byte switch-record containers whose +0x08 nested arrays
  are exact 8-byte (key,value) pairs.

The two descriptor lists remain deliberately named list_a/list_b.  Their logical
operator/meaning is not inferred here.  Live NPC configuration and retail member
selection remain separate gates.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def fail(msg: str) -> None:
    raise ValueError(msg)


def resolve_descriptor_list(count: int, start: int, indirect: list[int], switch_count: int) -> dict:
    """Decode the exact D1 compact switch-record list reference shape.

    Exact Xur retail invariants establish three encodings:
      count == 0 -> start == 0xFFFF, empty list
      count == 1 -> start is the switch-record index directly
      count > 1  -> start is an offset into the +0x250 uint16 index list
    """
    if count == 0:
        if start != 0xFFFF:
            fail(f'null descriptor list has start {start}, expected 65535')
        return {'mode': 'null', 'count': 0, 'start': start, 'switch_record_indices': []}
    if count == 1:
        if not (0 <= start < switch_count):
            fail(f'direct single switch index {start} outside 0..{switch_count-1}')
        return {'mode': 'direct_single', 'count': 1, 'start': start, 'switch_record_indices': [start]}
    if start < 0 or start + count > len(indirect):
        fail(f'indirect range start={start} count={count} outside +0x250 list size {len(indirect)}')
    vals = indirect[start:start + count]
    if any(v < 0 or v >= switch_count for v in vals):
        fail(f'indirect range resolves outside switch bank: {vals!r} / {switch_count}')
    return {'mode': 'indirect_list', 'count': count, 'start': start, 'switch_record_indices': vals}


def close_row(row: dict) -> dict:
    if row.get('error'):
        fail(f"{row.get('entity')}: upstream row error {row['error']}")
    if row.get('parent_class_hash') != '80801A9C':
        fail(f"{row.get('entity')}: parent class {row.get('parent_class_hash')} != 80801A9C")
    if row.get('parsed_model_tag') != '80C88CEF':
        fail(f"{row.get('entity')}: model {row.get('parsed_model_tag')} != 80C88CEF")

    f = row['parent_fields']
    maps = f['external_materials_map']
    indirect = f['candidate_index_0x250_as_i16']
    desc = f['descriptor_0x260_FE1A8080']
    mats = f['external_materials']

    for name, obj in [('map', maps), ('+0x250', indirect), ('+0x260', desc), ('materials', mats)]:
        if not obj.get('bounds_valid'):
            fail(f"{row['entity']}: {name} bounds invalid")

    if maps['count'] != 81:
        fail(f"{row['entity']}: expected 81 external map entries, got {maps['count']}")
    if indirect['count'] != 46:
        fail(f"{row['entity']}: expected 46 +0x250 uint16 indices, got {indirect['count']}")
    if desc['count'] != 108:
        fail(f"{row['entity']}: expected 108 +0x260 descriptors, got {desc['count']}")
    if mats['count'] != 820:
        fail(f"{row['entity']}: expected 820 external materials, got {mats['count']}")

    # The only aligned early dynamic array that validates exactly as the later-
    # strategy 0x18 container + nested 8-byte pair shape is parent +0x50.
    switch_candidates = [x for x in row.get('switch_container_shape_tests', [])
                         if x.get('all_outer_elements_have_valid_nested_pair_array') and x.get('inner_pair_total', 0) > 0]
    if len(switch_candidates) != 1:
        fail(f"{row['entity']}: expected one switch-container shape candidate, got {len(switch_candidates)}")
    sw = switch_candidates[0]
    if sw.get('parent_relative_offset') != 0x50:
        fail(f"{row['entity']}: switch-container candidate at {sw.get('parent_relative_offset')}, expected 0x50")
    if sw.get('outer_count') != 55:
        fail(f"{row['entity']}: expected 55 switch records, got {sw.get('outer_count')}")
    if sw.get('inner_pair_total') != 164 or sw.get('inner_pair_nonzero_key_count') != 164:
        fail(f"{row['entity']}: expected 164 nonzero key/value pairs, got {sw.get('inner_pair_total')}/{sw.get('inner_pair_nonzero_key_count')}")

    switch_rows = {int(x['outer_index']): x['pairs'] for x in sw.get('inner_pair_rows', [])}
    if set(switch_rows) != set(range(55)):
        fail(f"{row['entity']}: switch record index coverage is not exact 0..54")

    indirect_vals = [int(x) for x in indirect['u16_values']]
    if len(indirect_vals) != 46 or any(x < 0 or x >= 55 for x in indirect_vals):
        fail(f"{row['entity']}: +0x250 index list does not resolve wholly inside 55-record bank")

    descriptor_rows = []
    used_indirect_positions: set[int] = set()
    for d in desc['rows']:
        vals = [int(x) for x in d['u16']]
        if len(vals) != 4:
            fail(f"{row['entity']}: descriptor {d['index']} does not have four uint16 fields")
        a = resolve_descriptor_list(vals[0], vals[1], indirect_vals, 55)
        b = resolve_descriptor_list(vals[2], vals[3], indirect_vals, 55)
        for z in (a, b):
            if z['mode'] == 'indirect_list':
                used_indirect_positions.update(range(z['start'], z['start'] + z['count']))
        descriptor_rows.append({
            'descriptor_index': int(d['index']),
            'raw_u16': vals,
            'list_a': a,
            'list_b': b,
        })

    # Every serialized +0x250 entry is consumed by at least one multi-record
    # descriptor list.  There is no unexplained tail or padding element.
    if used_indirect_positions != set(range(46)):
        fail(f"{row['entity']}: +0x250 indirect positions not exactly consumed: missing {sorted(set(range(46))-used_indirect_positions)}")

    material_tags = list(mats['tag_hashes'])
    if len(material_tags) != 820:
        fail(f"{row['entity']}: material tag list length mismatch")

    descriptor_coverage: set[int] = set()
    members = []
    groups = set()
    for m in maps['rows']:
        vi = int(m['index'])
        count = int(m['material_count'])
        mat_start = int(m['material_start_index'])
        desc_start = int(m['unk08'])
        if count <= 0:
            fail(f"{row['entity']}: map {vi} has nonpositive material_count {count}")
        if mat_start < 0 or mat_start + count > 820:
            fail(f"{row['entity']}: map {vi} material range OOB")
        if desc_start < 0 or desc_start + count > 108:
            fail(f"{row['entity']}: map {vi} descriptor range OOB: start={desc_start}, count={count}")
        groups.add((desc_start, count))
        for local in range(count):
            di = desc_start + local
            bi = mat_start + local
            descriptor_coverage.add(di)
            dr = descriptor_rows[di]
            members.append({
                'variant_shader_index': vi,
                'member_index': local,
                'material_bank_index': bi,
                'material_tag_hash': material_tags[bi],
                'descriptor_index': di,
                'descriptor_list_a': dr['list_a'],
                'descriptor_list_b': dr['list_b'],
            })

    if descriptor_coverage != set(range(108)):
        fail(f"{row['entity']}: map descriptor groups do not cover exact descriptor bank")
    expected_groups = {(0,12),(12,14),(26,13),(39,24),(63,24),(87,4),(91,6),(97,2),(99,4),(103,3),(106,2)}
    if groups != expected_groups:
        fail(f"{row['entity']}: descriptor group set mismatch: {sorted(groups)}")
    if len(members) != 820:
        fail(f"{row['entity']}: expected one descriptor association per 820 material-bank positions, got {len(members)}")

    # Expand exact key/value records for each descriptor list while retaining the
    # unresolved list-A/list-B logical semantics.
    for m in members:
        for label in ('a', 'b'):
            z = m[f'descriptor_list_{label}']
            z['switch_records'] = [
                {'switch_record_index': i, 'pairs': switch_rows[i]}
                for i in z['switch_record_indices']
            ]

    return {
        'entity': row['entity'],
        'model_entity_resource': row['model_entity_resource'],
        'model_entity_resource_sha256': row['model_entity_resource_sha256'],
        'parent_offset': row['parent_offset'],
        'counts': {
            'external_material_map': 81,
            'indirect_switch_index_u16': 46,
            'descriptors_FE1A8080': 108,
            'switch_records': 55,
            'switch_key_value_pairs': 164,
            'external_materials': 820,
        },
        'descriptor_groups': [{'start': a, 'count': b} for a,b in sorted(groups)],
        'indirect_switch_record_indices': indirect_vals,
        'switch_records': [{'index': i, 'pairs': switch_rows[i]} for i in range(55)],
        'descriptors': descriptor_rows,
        'variant_members': members,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--layout-report', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()
    src = json.loads(a.layout_report.read_text())
    if src.get('target_model') != '80C88CEF':
        fail('layout report target_model is not 80C88CEF')
    if src.get('violations'):
        fail(f"upstream layout report has violations: {src['violations']}")
    rows = [close_row(r) for r in src.get('rows', [])]
    if len(rows) != 2:
        fail(f'expected two Xur entity rows, got {len(rows)}')

    # Both serialized Xur SEntities independently point to the exact same
    # 80C88CE2 model-owner payload; require the complete static graph to match.
    def canon(r: dict) -> str:
        q = dict(r)
        q.pop('entity', None)
        return json.dumps(q, sort_keys=True, separators=(',', ':'))
    if canon(rows[0]) != canon(rows[1]):
        fail('the two Xur entities did not produce byte-identical static model-parent graphs')

    graph = rows[0]
    out = {
        'schema_version': 1,
        'status': 'D1_XUR_MODEL_PARENT_PERMUTATION_STATIC_REFERENCE_GRAPH_EXACT',
        'target_model': '80C88CEF',
        'source_entities': [r['entity'] for r in rows],
        'model_entity_resource': graph['model_entity_resource'],
        'model_entity_resource_sha256': graph['model_entity_resource_sha256'],
        'parent_class': '80801A9C',
        'parent_offsets': {
            'switch_record_container_array': '0x50',
            'external_materials_map': '0x230',
            'indirect_switch_record_index_list': '0x250',
            'descriptor_FE1A8080': '0x260',
            'external_materials': '0x270',
        },
        'counts': graph['counts'],
        'descriptor_groups': graph['descriptor_groups'],
        'indirect_switch_record_indices': graph['indirect_switch_record_indices'],
        'switch_records': graph['switch_records'],
        'descriptors': graph['descriptors'],
        'variant_members': graph['variant_members'],
        'promoted_semantics': {
            'external_map_unk08': 'descriptor_start_index; descriptor range length equals MaterialCount',
            'descriptor_list_encoding': 'count=0 null/FFFF; count=1 direct switch-record index; count>1 start/count slice of +0x250 uint16 indirect-index list',
            'switch_record_payload': 'nested exact 8-byte uint32 key/value pairs',
        },
        'withheld_semantics': {
            'descriptor_list_a_vs_list_b_logic': 'unknown',
            'switch_key_human_names': 'not required for static graph closure and not guessed',
            'live_xur_configuration': 'unknown',
            'selected_external_material_member': 'unknown until live configuration and descriptor logic are closed',
        },
        'live_configuration_state_complete': False,
        'retail_material_member_selection_complete': False,
        'violations': [],
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({
        'status': out['status'],
        'model_entity_resource': out['model_entity_resource'],
        'counts': out['counts'],
        'descriptor_groups': out['descriptor_groups'],
        'variant_member_count': len(out['variant_members']),
        'live_configuration_state_complete': False,
    }, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
