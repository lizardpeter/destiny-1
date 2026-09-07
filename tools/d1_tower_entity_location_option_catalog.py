#!/usr/bin/env python3
"""Build a loss-preserving Tower EntitySK location-option catalog from D912 evidence.

The D912 location-tail proof establishes an exact structural group index and therefore
exact EntitySK<->location ownership whenever the indexed group contains one unique
EntitySK. Multi-entity groups remain candidate associations.

This adapter deliberately does *not* select a single "current" location. Tower
scenario data can preserve alternate/historical/conditional placements for the same
actor. Every source option is retained, scenario membership is preserved, duplicate
transforms across scenario tables are clustered, and no default is invented.

The resulting catalog is intended as the stable interface for Blender/export tooling:
all alternatives are available to the user, while later scenario/state evidence may
optionally choose one without destroying the others.
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

CLOSED = 'D1_D912_LOCATION_TAIL_GROUPING_STRUCTURALLY_CLOSED'
NULLS = {None, '00000000', 'FFFFFFFF'}


def norm(x):
    return None if x is None else str(x).upper().removeprefix('0X').zfill(8)


def transform_key(row: dict) -> tuple:
    # Decoded retail float values are preserved exactly as represented in the proof.
    return tuple(row.get('location') or []) + tuple(row.get('rotation') or [])


def option_row(row: dict, entity: str, association: str, d912_membership: dict) -> dict:
    d912 = norm(row['d912'])
    li = int(row['location_index'])
    return {
        'option_id': f'{d912}:{li}',
        'entity_hash': norm(entity),
        'association_status': association,
        'd912': d912,
        'location_index': li,
        'location': row.get('location'),
        'rotation': row.get('rotation'),
        'source_scenarios': list(d912_membership.get(d912, [row.get('scenario')])),
        'representative_scenario': row.get('scenario'),
        'activity_hash': norm(row.get('activity_hash')),
        'candidate_group_index': int(row.get('candidate_group_index', -1)),
        'group_type_string_hash': norm(row.get('group_type_string_hash')),
        'group_record_count': int(row.get('group_record_count', 0)),
        'group_unique_entity_count': int(row.get('group_unique_entity_count', 0)),
        'group_entity_hashes': [norm(x) for x in row.get('group_entity_hashes', [])],
        'tail_words_hex': row.get('tail_words_hex'),
        'tail_unk20': row.get('tail_unk20'),
        'tail_unk24': row.get('tail_unk24'),
        'tail_unk2c': row.get('tail_unk2c'),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('d912_group_probe', type=Path)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    src = json.loads(a.d912_group_probe.read_text())
    if src.get('status') != CLOSED or src.get('violations'):
        raise SystemExit(f'D912 group proof is not closed: {src.get("status")} {src.get("violations")}')

    membership = {norm(k): list(v) for k, v in (src.get('d912_scenario_membership') or {}).items()}
    by_entity = collections.defaultdict(list)
    exact_count = candidate_count = 0

    for r in src.get('unique_exact_entity_locations', []):
        e = norm(r.get('entity_hash'))
        if e in NULLS:
            raise ValueError(f'exact row has null entity: {r}')
        by_entity[e].append(option_row(r, e, 'exact_unique_entity_in_indexed_group', membership))
        exact_count += 1

    # Preserve ambiguous locations as explicit candidate options for every entity in
    # the indexed group. This does not promote them to exact ownership.
    for r in src.get('unique_ambiguous_entity_locations', []):
        entities = sorted({norm(x) for x in r.get('group_entity_hashes', []) if norm(x) not in NULLS})
        for e in entities:
            by_entity[e].append(option_row(r, e, 'candidate_multi_entity_indexed_group', membership))
            candidate_count += 1

    entities_out = {}
    total_distinct_transforms = 0
    multi_location_entities = 0
    scenario_index = collections.defaultdict(lambda: collections.defaultdict(list))

    for entity, options in sorted(by_entity.items()):
        # De-duplicate only exact source option IDs for one entity. Different D912 rows
        # that happen to share a transform are intentionally retained as provenance.
        uniq = {}
        for o in options:
            key = (o['option_id'], o['association_status'])
            old = uniq.get(key)
            if old is not None and transform_key(old) != transform_key(o):
                raise ValueError(f'{entity} option {key} transform disagreement')
            uniq.setdefault(key, o)
        options = sorted(uniq.values(), key=lambda x: (x['association_status'], x['d912'], x['location_index']))

        clusters = collections.defaultdict(list)
        for o in options:
            clusters[transform_key(o)].append(o['option_id'])
            for sc in o['source_scenarios']:
                scenario_index[sc][entity].append(o['option_id'])

        transform_clusters = []
        for i, (tk, ids) in enumerate(sorted(clusters.items(), key=lambda kv: (kv[0], kv[1]))):
            loc = list(tk[:4])
            rot = list(tk[4:8])
            transform_clusters.append({
                'transform_cluster_id': f'{entity}:T{i:03d}',
                'location': loc,
                'rotation': rot,
                'source_option_ids': sorted(set(ids)),
            })
        for o in options:
            tk = transform_key(o)
            ci = next(i for i, c in enumerate(transform_clusters)
                      if tuple(c['location']) + tuple(c['rotation']) == tk)
            o['transform_cluster_id'] = transform_clusters[ci]['transform_cluster_id']

        exact = sum(o['association_status'].startswith('exact_') for o in options)
        candidate = len(options) - exact
        distinct = len(transform_clusters)
        total_distinct_transforms += distinct
        if distinct > 1:
            multi_location_entities += 1
        entities_out[entity] = {
            'entity_hash': entity,
            'source_option_count': len(options),
            'exact_option_count': exact,
            'candidate_option_count': candidate,
            'distinct_transform_count': distinct,
            'has_multiple_location_alternatives': distinct > 1,
            'default_option_id': None,
            'options': options,
            'transform_clusters': transform_clusters,
        }

    scenario_out = {
        sc: {
            e: sorted(set(ids))
            for e, ids in sorted(rows.items())
        }
        for sc, rows in sorted(scenario_index.items())
    }

    out = {
        'schema': 'd1_tower_entity_location_option_catalog/v1',
        'status': 'D1_TOWER_ENTITY_LOCATION_OPTIONS_COMPLETE',
        'source_status': src.get('status'),
        'entity_count_with_any_location_option': len(entities_out),
        'exact_source_entity_option_count': exact_count,
        'ambiguous_candidate_entity_option_count': candidate_count,
        'total_entity_option_count': exact_count + candidate_count,
        'total_distinct_entity_transforms': total_distinct_transforms,
        'multi_location_entity_count': multi_location_entities,
        'entities': entities_out,
        'scenario_entity_option_ids': scenario_out,
        'selection_policy': {
            'default_selection': 'unset',
            'preserve_all_alternatives': True,
            'allow_manual_editor_selection': True,
            'allow_future_scenario_or_state_selection': True,
            'instantiate_all_simultaneously_by_default': False,
            'reason': (
                'Multiple source locations can represent alternate, historical, seasonal, or conditional placements. '
                'The binary grouping proof establishes source options but does not establish simultaneous-spawn semantics.'
            ),
        },
        'evidence_policy': (
            'Exact options come only from D912 locations whose structurally indexed group contains one unique EntitySK. '
            'Multi-entity group locations are retained as candidates for every member but never promoted to exact. '
            'All D912/scenario provenance and duplicate transforms are preserved; no current/default location is guessed.'
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + '\n')
    print('STATUS', out['status'])
    print('ENTITIES', out['entity_count_with_any_location_option'])
    print('OPTIONS', out['total_entity_option_count'], 'EXACT', exact_count, 'CANDIDATE', candidate_count)
    print('DISTINCT_TRANSFORMS', total_distinct_transforms, 'MULTI_LOCATION_ENTITIES', multi_location_entities)
    for e, r in sorted(entities_out.items(), key=lambda kv: (-kv[1]['distinct_transform_count'], kv[0]))[:30]:
        print('ENTITY', e, 'options', r['source_option_count'], 'distinct', r['distinct_transform_count'],
              'exact', r['exact_option_count'], 'candidate', r['candidate_option_count'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
