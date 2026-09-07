#!/usr/bin/env python3
"""Trace exact D1 PS4 ownership for multiple s_entity_model FileHashes in one pass.

Ownership gates are identical to d1_remote_model_owner_trace.py:
1. EntityResource 80800861 must source-parse as entity_model.
2. Its validated PS4 model-parent +0x15C FileHash must equal a requested model.
3. An s_entity 80800734 owner is accepted only when its serialized Resource[]
   contains that exact model-owning EntityResource FileHash.

The multi-target form avoids repeatedly downloading/scanning the same packages.
No names, package locality, visual similarity, or untyped scalar matches are used.
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
    return v.upper().removeprefix('0X').zfill(8)


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

    resource_hits = []
    resource_errors = []
    resource_candidates = 0
    resource_to_models: dict[str, set[str]] = defaultdict(set)
    for pkg, view in views.items():
        for e in view.entries:
            if e['type'] != 16 or e['subtype'] != 0 or e['reference'].upper() != ENTITY_RESOURCE_CLASS:
                continue
            resource_candidates += 1
            try:
                d = parse_resource(view.entry(e['index']), 'PS4')
            except Exception as ex:
                resource_errors.append({'package_id': f'{pkg:04X}', 'tag_hash': e['tag_hash'].upper(), 'entry_index': e['index'], 'error': repr(ex)})
                continue
            if d.get('semantic_role') != 'entity_model':
                continue
            embedded = (d.get('embedded_model_tag_hash') or '').upper()
            if embedded not in target_set:
                continue
            rh = e['tag_hash'].upper()
            resource_to_models[rh].add(embedded)
            row = {
                'package_id': f'{pkg:04X}',
                'resource_hash': rh,
                'resource_entry_index': int(e['index']),
                'resource_file_size': int(e['file_size']),
                'embedded_model_tag_hash': embedded,
                'model_field_offset_in_parent': d.get('model_field_offset_in_parent'),
                'discriminator_class': (d.get('unk10') or {}).get('class_hash'),
                'parent_class': (d.get('unk18') or {}).get('class_hash'),
                'parent_target_offset': (d.get('unk18') or {}).get('target_offset'),
            }
            resource_hits.append(row)
            print('MODEL_RESOURCE_OWNER', json.dumps(row, separators=(',', ':')), flush=True)

    owner_hashes = set(resource_to_models)
    entity_hits = []
    entity_errors = []
    entity_candidates = 0
    if owner_hashes:
        for pkg, view in views.items():
            for e in view.entries:
                if e['reference'].upper() != S_ENTITY_REF:
                    continue
                entity_candidates += 1
                try:
                    resources = parse_entity_resources(view.entry(e['index']))
                except Exception as ex:
                    entity_errors.append({'package_id': f'{pkg:04X}', 'entity_hash': e['tag_hash'].upper(), 'entry_index': e['index'], 'error': repr(ex)})
                    continue
                matches = [x for x in resources if x['resource_hash'].upper() in owner_hashes]
                if not matches:
                    continue
                models = sorted({m for x in matches for m in resource_to_models[x['resource_hash'].upper()]})
                row = {
                    'package_id': f'{pkg:04X}',
                    'entity_hash': e['tag_hash'].upper(),
                    'entity_entry_index': int(e['index']),
                    'entity_file_size': int(e['file_size']),
                    'resource_count': len(resources),
                    'models': models,
                    'matching_resources': matches,
                    'all_resources': resources,
                }
                entity_hits.append(row)
                print('S_ENTITY_MODEL_OWNER', json.dumps(row, separators=(',', ':')), flush=True)

    by_model = {}
    for model in targets:
        rr = [x for x in resource_hits if x['embedded_model_tag_hash'] == model]
        rset = {x['resource_hash'] for x in rr}
        ee = [x for x in entity_hits if any(m['resource_hash'].upper() in rset for m in x['matching_resources'])]
        by_model[model] = {
            'model_owner_resources': rr,
            's_entity_owners': ee,
            'model_owner_resource_count': len(rr),
            's_entity_owner_count': len(ee),
        }

    rep = {
        'schema': 'd1_remote_multi_model_owner_trace/v1',
        'model_tag_hashes': targets,
        'scan_package_ids': [f'{x:04X}' for x in scan_ids],
        'entity_resource_candidate_count': resource_candidates,
        'model_owner_resource_count': len(resource_hits),
        'model_owner_resources': resource_hits,
        's_entity_candidate_count': entity_candidates,
        's_entity_owner_count': len(entity_hits),
        's_entity_owners': entity_hits,
        'by_model': by_model,
        'resource_error_count': len(resource_errors),
        'resource_errors': resource_errors,
        'entity_error_count': len(entity_errors),
        'entity_errors': entity_errors,
        'policy': (
            'Model ownership is accepted only from the validated PS4 EntityResource model-parent +0x15C FileHash. '
            'Entity ownership is accepted only from exact s_entity Resource[] equality to those EntityResources.'
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(rep, indent=2) + '\n')
    print('MODELS', targets, 'RESOURCES', len(resource_hits), 'S_ENTITIES', len(entity_hits),
          'RESOURCE_ERRORS', len(resource_errors), 'ENTITY_ERRORS', len(entity_errors))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
