#!/usr/bin/env python3
"""Trace the remaining Tower actor model 80C88434 visible-material selector frontier.

The green actor-material signature census leaves exactly one visible external group
for model 80C88434 (parent EntityResource 80C883FD) without an S152 placement
configuration in the 918-placement corpus. The three source-owned EntitySK variants
are serialized at the same physical Tower location in generation/scenario-specific
D912 tables:

  80C7A5AD -> 80C7A581 (harvest)
  80C7ACC5 -> 80C7ACB4 (legacy/default-family scenarios)
  80C883CA -> 80C88477 (ambient/current family)

This probe opens only those exact D912s and EntitySKs. It emits the source-typed
SMapDataEntry DataResource class/null state, exact local bytes, every EntitySK
resource reference, and the exact four-member visible permutation group from
80C883FD. It does not guess a winner.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from d1_entity_resource_probe import ENTITY_RESOURCE_CLASS, parse_resource
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_remote_s_entity_resource_package_find import S_ENTITY_REF, parse_entity_resources
from d1_remote_tower_descriptor_selection_calibration import parse_graph
from d1_remote_tower_placement_permutation_calibration_v2 import discover_smap_placements
from d1_split_tar_extract import SplitHttpTar

MODEL = '80C88434'
PARENT = '80C883FD'
TARGETS = {
    '80C7A5AD': '80C7A581',
    '80C7ACC5': '80C7ACB4',
    '80C883CA': '80C88477',
}


def norm(x):
    return str(x).upper().removeprefix('0X').zfill(8)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    cats = load_catalogs(a.member_catalog)
    arc = SplitHttpTar([f'{a.base_url.rstrip("/")}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    c = RemoteCorpus(arc, cats, a.runtime)
    violations = []
    placements = []
    entities = []

    for entity, owner in TARGETS.items():
        try:
            rows = [x for x in discover_smap_placements(c, owner) if norm(x.get('entity_hash')) == entity]
        except Exception as ex:
            violations.append(f'{owner}:placement_parse:{ex!r}')
            continue
        if len(rows) != 1:
            violations.append(f'{owner}:{entity}:expected_one_smap_got_{len(rows)}')
            continue
        r = rows[0]
        ob, osrc = c.payload(owner)
        so = int(r['smap_offset'])
        placements.append({
            'entity_hash': entity,
            'd912': owner,
            'd912_source': str(osrc),
            'smap_offset': so,
            'data_resource': r.get('data_resource'),
            'has_s152': bool(r.get('s152')),
            's152': r.get('s152'),
            'smap_context_start': max(0, so - 0x20),
            'smap_context_end': min(len(ob), so + 0xC0),
            'smap_context_hex': ob[max(0, so - 0x20):min(len(ob), so + 0xC0)].hex(),
        })

        em = c.entry_meta(entity)
        eb, esrc = c.payload(entity)
        if em is None or eb is None or norm(em.get('reference', '')) != S_ENTITY_REF:
            violations.append(f'{entity}:SEntity_unavailable_or_class_mismatch')
            continue
        try:
            resource_rows = parse_entity_resources(eb)
        except Exception as ex:
            violations.append(f'{entity}:parse_entity_resources:{ex!r}')
            continue
        erows = []
        for rr in resource_rows:
            rh = norm(rr['resource_hash'])
            rm = c.entry_meta(rh)
            ref = norm(rm.get('reference', 'FFFFFFFF')) if rm else None
            x = {
                'resource_index': int(rr.get('resource_index', -1)),
                'resource_hash': rh,
                'reference': ref,
                'available': rm is not None,
            }
            if rm is not None and ref == ENTITY_RESOURCE_CLASS:
                rb, rsrc = c.payload(rh)
                if rb is None:
                    x['entity_resource_error'] = 'payload_unavailable'
                else:
                    try:
                        p = parse_resource(rb, 'PS4')
                        x['entity_resource'] = {
                            'source': str(rsrc),
                            'semantic_role': p.get('semantic_role'),
                            'embedded_model_tag_hash': norm(p.get('embedded_model_tag_hash', 'FFFFFFFF')),
                            'unk08': p.get('unk08'),
                            'unk10': p.get('unk10'),
                            'unk18': p.get('unk18'),
                        }
                    except Exception as ex:
                        x['entity_resource_error'] = repr(ex)
            erows.append(x)
        entities.append({
            'entity_hash': entity,
            'source': str(esrc),
            'resource_count': len(resource_rows),
            'resources': erows,
        })

    try:
        graph = parse_graph(c, PARENT)
        groups = [g for g in graph.get('groups', []) if int(g.get('variant_shader_index', -1)) == 0]
        if len(groups) != 1:
            violations.append(f'{PARENT}:expected_one_variant0_group_got_{len(groups)}')
            group0 = None
        else:
            group0 = groups[0]
    except Exception as ex:
        graph = None
        group0 = None
        violations.append(f'{PARENT}:parse_graph:{ex!r}')

    out = {
        'schema_version': 1,
        'status': 'D1_TOWER_80C88434_CONFIG_FRONTIER_EXACT' if not violations else 'D1_TOWER_80C88434_CONFIG_FRONTIER_VIOLATIONS',
        'model': MODEL,
        'model_parent_resource': PARENT,
        'targets': TARGETS,
        'placements': placements,
        'entities': entities,
        'visible_variant0_group': group0,
        'graph_summary': None if graph is None else {
            'switch_record_count': graph.get('switch_record_count'),
            'descriptor_count': graph.get('descriptor_count'),
            'group_count': graph.get('group_count'),
            'material_count': graph.get('material_count'),
        },
        'violations': violations,
        'gates': {
            'visible_variant0_material_selected': False,
            'D1_retail_descriptor_evaluator_source_closed': False,
        },
        'policy': (
            'The probe is restricted to three exact source-owned EntitySK/D912 pairs and the exact model parent 80C883FD. '
            'SMap DataResource structure, EntitySK resource graph, and descriptor requirements are evidence only. No '
            'material member is selected unless a source-typed configuration or an independently closed equivalent selector is found.'
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({
        'status': out['status'],
        'placements': [
            {'entity': x['entity_hash'], 'd912': x['d912'], 'data_resource': x['data_resource'], 'has_s152': x['has_s152']}
            for x in placements
        ],
        'variant0_members': None if group0 is None else [
            {
                'member_index': m['member_index'], 'material': m['material_tag_hash'],
                'descriptor_index': m['descriptor_index'], 'list_a_pairs': m['list_a_pairs'], 'list_b_pairs': m['list_b_pairs']
            } for m in group0.get('members', [])
        ],
        'violations': violations,
        'gates': out['gates'],
    }, indent=2))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
