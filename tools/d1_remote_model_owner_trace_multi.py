#!/usr/bin/env python3
"""Trace exact D1 PS4 ownership for multiple s_entity_model FileHashes in one corpus pass.

This is the batched counterpart to d1_remote_model_owner_trace.py. It preserves the
same proof boundary while avoiding repeated package downloads/decompression when several
models from one encounter must be compared.

Accepted ownership edges only:
  EntityResource 80800861
    -> validated entity-model discriminator 80801A80
    -> validated model-parent 80801A9C
    -> PS4 parent +0x15C exact model FileHash
  s_entity 80800734 Resource[]
    -> exact FileHash equality to the model-owning EntityResource

No adjacency, package locality, naming, transform, visual, or morphology inference is used.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_entity_resource_probe import ENTITY_RESOURCE_CLASS, parse_resource
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_remote_s_entity_resource_package_find import S_ENTITY_REF, parse_entity_resources
from d1_split_tar_extract import SplitHttpTar


def norm(v: str) -> str:
    return str(v).upper().removeprefix('0X').zfill(8)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', action='append', required=True)
    ap.add_argument('--scan-package-id', action='append', type=lambda x: int(x, 0), required=True)
    ap.add_argument('--member-catalog', action='append', type=Path, required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    targets = list(dict.fromkeys(norm(x) for x in a.model))
    target_set = set(targets)
    catalogs = load_catalogs(a.member_catalog)
    scan_ids = list(dict.fromkeys(a.scan_package_id))
    missing = [x for x in scan_ids if x not in catalogs]
    if missing:
        raise SystemExit('missing verified member catalogs: ' + ', '.join(f'{x:04X}' for x in missing))

    base = a.base_url.rstrip('/')
    arc = SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    views = {pkg: RemoteLogicalPackage(arc, catalogs[pkg], a.runtime) for pkg in scan_ids}

    resource_hits_by_model: dict[str, list[dict]] = defaultdict(list)
    resource_errors = []
    resource_candidates = 0

    for pkg, view in views.items():
        for e in view.entries:
            if e['type'] != 16 or e['subtype'] != 0 or e['reference'].upper() != ENTITY_RESOURCE_CLASS:
                continue
            resource_candidates += 1
            try:
                d = parse_resource(view.entry(e['index']), 'PS4')
            except Exception as ex:
                resource_errors.append({
                    'package_id': f'{pkg:04X}', 'tag_hash': e['tag_hash'].upper(),
                    'entry_index': int(e['index']), 'error': repr(ex)
                })
                continue
            if d.get('semantic_role') != 'entity_model':
                continue
            embedded = d.get('embedded_model_tag_hash')
            if not embedded:
                continue
            mh = norm(embedded)
            if mh not in target_set:
                continue
            row = {
                'package_id': f'{pkg:04X}',
                'resource_hash': e['tag_hash'].upper(),
                'resource_entry_index': int(e['index']),
                'resource_file_size': int(e['file_size']),
                'embedded_model_tag_hash': mh,
                'model_field_offset_in_parent': d.get('model_field_offset_in_parent'),
                'discriminator_class': (d.get('unk10') or {}).get('class_hash'),
                'parent_class': (d.get('unk18') or {}).get('class_hash'),
                'parent_target_offset': (d.get('unk18') or {}).get('target_offset'),
            }
            resource_hits_by_model[mh].append(row)
            print('MODEL_RESOURCE_OWNER', json.dumps(row, separators=(',', ':')), flush=True)

    owner_resource_to_models: dict[str, set[str]] = defaultdict(set)
    for mh, rows in resource_hits_by_model.items():
        for row in rows:
            owner_resource_to_models[row['resource_hash']].add(mh)

    entity_hits_by_model: dict[str, list[dict]] = defaultdict(list)
    entity_errors = []
    entity_candidates = 0
    if owner_resource_to_models:
        for pkg, view in views.items():
            for e in view.entries:
                if e['reference'].upper() != S_ENTITY_REF:
                    continue
                entity_candidates += 1
                try:
                    resources = parse_entity_resources(view.entry(e['index']))
                except Exception as ex:
                    entity_errors.append({
                        'package_id': f'{pkg:04X}', 'entity_hash': e['tag_hash'].upper(),
                        'entry_index': int(e['index']), 'error': repr(ex)
                    })
                    continue
                matched_by_model: dict[str, list[dict]] = defaultdict(list)
                for rr in resources:
                    rh = norm(rr['resource_hash'])
                    for mh in owner_resource_to_models.get(rh, ()):
                        matched_by_model[mh].append(rr)
                for mh, matches in matched_by_model.items():
                    row = {
                        'package_id': f'{pkg:04X}',
                        'entity_hash': e['tag_hash'].upper(),
                        'entity_entry_index': int(e['index']),
                        'entity_file_size': int(e['file_size']),
                        'resource_count': len(resources),
                        'matching_resources': matches,
                        'all_resources': resources,
                    }
                    entity_hits_by_model[mh].append(row)
                    print('S_ENTITY_MODEL_OWNER', mh, json.dumps(row, separators=(',', ':')), flush=True)

    model_rows = []
    all_entity_owners = set()
    for mh in targets:
        resources = resource_hits_by_model.get(mh, [])
        entities = entity_hits_by_model.get(mh, [])
        all_entity_owners.update(x['entity_hash'] for x in entities)
        model_rows.append({
            'model_tag_hash': mh,
            'model_owner_resource_count': len(resources),
            'model_owner_resources': resources,
            's_entity_owner_count': len(entities),
            's_entity_owners': entities,
        })

    report = {
        'schema': 'd1_remote_model_owner_trace_multi/v1',
        'models_requested': targets,
        'scan_package_ids': [f'{x:04X}' for x in scan_ids],
        'entity_resource_candidate_count': resource_candidates,
        's_entity_candidate_count': entity_candidates,
        'models': model_rows,
        'unique_s_entity_owner_hashes': sorted(all_entity_owners),
        'resource_error_count': len(resource_errors),
        'resource_errors': resource_errors,
        'entity_error_count': len(entity_errors),
        'entity_errors': entity_errors,
        'violations': [],
        'policy': (
            'Model ownership is accepted only from the validated PS4 EntityResource model-parent +0x15C FileHash. '
            'Entity backlinks are accepted only from exact s_entity Resource[] FileHash equality. '
            'No locality, adjacency, package-name, appearance, transform, or semantic guessing is used.'
        ),
    }
    if resource_errors:
        report['violations'].append('entity_resource_parse_errors')
    if entity_errors:
        report['violations'].append('s_entity_parse_errors')

    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + '\n')
    for row in model_rows:
        print('MODEL', row['model_tag_hash'], 'RESOURCES', row['model_owner_resource_count'],
              'S_ENTITIES', row['s_entity_owner_count'])
    print('UNIQUE_S_ENTITY_OWNERS', sorted(all_entity_owners))
    print('RESOURCE_ERRORS', len(resource_errors), 'ENTITY_ERRORS', len(entity_errors),
          'VIOLATIONS', report['violations'])
    return 0 if not report['violations'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
