#!/usr/bin/env python3
"""Trace exact D1 PS4 ownership of an s_entity_model FileHash.

The first ownership edge is source-closed by the ROI EntityResource schema:
EntityResource class 0x80800861, entity-model discriminator 0x80801A80,
model-parent class 0x80801A9C, embedded model FileHash at parent +0x15C on PS4.

After finding every EntityResource that embeds --model, this tool performs a
second exact pass over D1 s_entity Resource[] arrays (class 0x80800734) and
reports every entity whose serialized resource FileHash equals one of those
model-owning EntityResources.

No neighboring hashes, naming, package locality, visual similarity or guessed
composition semantics participate.  A missing backlink is reported as a
negative result, not replaced by a heuristic search.
"""
from __future__ import annotations

import argparse
import json
import sys
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
    ap.add_argument('--model', required=True)
    ap.add_argument('--scan-package-id', action='append', type=lambda x: int(x, 0), required=True)
    ap.add_argument('--member-catalog', action='append', type=Path, required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    target = norm(a.model)
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
            embedded = d.get('embedded_model_tag_hash')
            if embedded and embedded.upper() == target:
                row = {
                    'package_id': f'{pkg:04X}',
                    'resource_hash': e['tag_hash'].upper(),
                    'resource_entry_index': int(e['index']),
                    'resource_file_size': int(e['file_size']),
                    'embedded_model_tag_hash': embedded.upper(),
                    'model_field_offset_in_parent': d.get('model_field_offset_in_parent'),
                    'discriminator_class': (d.get('unk10') or {}).get('class_hash'),
                    'parent_class': (d.get('unk18') or {}).get('class_hash'),
                    'parent_target_offset': (d.get('unk18') or {}).get('target_offset'),
                }
                resource_hits.append(row)
                print('MODEL_RESOURCE_OWNER', json.dumps(row, separators=(',', ':')), flush=True)

    owner_hashes = {x['resource_hash'] for x in resource_hits}
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
                row = {
                    'package_id': f'{pkg:04X}',
                    'entity_hash': e['tag_hash'].upper(),
                    'entity_entry_index': int(e['index']),
                    'entity_file_size': int(e['file_size']),
                    'resource_count': len(resources),
                    'matching_resources': matches,
                    'all_resources': resources,
                }
                entity_hits.append(row)
                print('S_ENTITY_MODEL_OWNER', json.dumps(row, separators=(',', ':')), flush=True)

    rep = {
        'schema': 'd1_remote_model_owner_trace/v1',
        'model_tag_hash': target,
        'scan_package_ids': [f'{x:04X}' for x in scan_ids],
        'entity_resource_candidate_count': resource_candidates,
        'model_owner_resource_count': len(resource_hits),
        'model_owner_resources': resource_hits,
        's_entity_candidate_count': entity_candidates,
        's_entity_owner_count': len(entity_hits),
        's_entity_owners': entity_hits,
        'resource_error_count': len(resource_errors),
        'resource_errors': resource_errors,
        'entity_error_count': len(entity_errors),
        'entity_errors': entity_errors,
        'policy': (
            'Model ownership is accepted only from the validated PS4 EntityResource model-parent +0x15C FileHash. '
            'Entity backlinks are accepted only from exact s_entity Resource[] FileHash equality. No locality or '
            'semantic guesses are used.'
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(rep, indent=2) + '\n')
    print('MODEL', target, 'RESOURCES', len(resource_hits), 'S_ENTITIES', len(entity_hits),
          'RESOURCE_ERRORS', len(resource_errors), 'ENTITY_ERRORS', len(entity_errors))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
