#!/usr/bin/env python3
"""Join authoritative D1 Investment final EntityDataROI records to exact model resources.

Input is the already source-closed art_arrangements_resolved.json.  For every exact
final EntityDataROI destination selected by arrangement -> assignment -> EntityParent
+0x10, this tool reads only that serialized final record.  If and only if the record
is an s_entity (80800734), its source-parsed Resource[] is compared by exact FileHash
equality against requested model-owning EntityResources.

This is deliberately narrower than package-wide scanning: a hit proves the full
Investment selection path reaches an s_entity that directly owns the requested
EntityResource.  A miss is reported without inventing an indirect edge.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_remote_s_entity_resource_package_find import S_ENTITY_REF, parse_entity_resources
from d1_split_tar_extract import SplitHttpTar


def norm(v: str) -> str:
    return v.upper().removeprefix('0X').zfill(8)


def parse_pair(v: str) -> tuple[str, str]:
    if '=' not in v:
        raise argparse.ArgumentTypeError('expected RESOURCE=MODEL')
    a, b = v.split('=', 1)
    return norm(a), norm(b)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('resolved_arrangements', type=Path)
    ap.add_argument('--target-resource', action='append', type=parse_pair, required=True)
    ap.add_argument('--member-catalog', action='append', type=Path, required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    src = json.loads(a.resolved_arrangements.read_text())
    assert src.get('arrangement_count') == len(src.get('arrangements', []))
    targets = dict(a.target_resource)
    target_set = set(targets)

    # Preserve every exact arrangement context while deduplicating physical reads.
    finals: dict[tuple[int, int, str], dict] = {}
    for arr in src.get('arrangements', []):
        for ent in arr.get('entities', []):
            if not ent.get('resolved'):
                continue
            pkg = ent.get('entity_data_package_id')
            idx = ent.get('entity_data_file_index')
            h = norm(ent.get('entity_data_hash', ''))
            if not isinstance(pkg, int) or not isinstance(idx, int):
                continue
            key = (pkg, idx, h)
            row = finals.setdefault(key, {
                'package_id': pkg,
                'entry_index': idx,
                'entity_data_hash': h,
                'contexts': [],
            })
            row['contexts'].append({
                'arrangement_index': arr.get('arrangement_index'),
                'source': arr.get('source'),
                'assignment_hashes': list(arr.get('assignment_hashes', [])),
                'parent_hash': ent.get('parent_hash'),
            })

    catalogs = load_catalogs(a.member_catalog)
    needed = sorted({k[0] for k in finals})
    missing = [p for p in needed if p not in catalogs]
    if missing:
        raise SystemExit('missing catalogs for exact final packages: ' + ','.join(f'{p:04X}' for p in missing))

    arc = SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    views = {p: RemoteLogicalPackage(arc, catalogs[p], a.runtime) for p in needed}

    refs = collections.Counter()
    exact_final_count = 0
    s_entity_count = 0
    parsed_s_entity_count = 0
    hits = []
    errors = []
    target_occ = collections.Counter()

    for (pkg, idx, expected_hash), info in sorted(finals.items()):
        view = views[pkg]
        if idx < 0 or idx >= len(view.entries):
            errors.append({'package_id': f'{pkg:04X}', 'entry_index': idx, 'entity_data_hash': expected_hash, 'error': 'entry_index_oob'})
            continue
        e = view.entries[idx]
        actual = norm(e.get('tag_hash', ''))
        if actual != expected_hash:
            errors.append({'package_id': f'{pkg:04X}', 'entry_index': idx, 'entity_data_hash': expected_hash, 'actual_tag_hash': actual, 'error': 'catalog_tag_hash_mismatch'})
            continue
        exact_final_count += 1
        ref = norm(e.get('reference', ''))
        refs[ref] += 1
        if ref != S_ENTITY_REF:
            continue
        s_entity_count += 1
        try:
            resources = parse_entity_resources(view.entry(idx))
        except Exception as ex:
            errors.append({'package_id': f'{pkg:04X}', 'entry_index': idx, 'entity_data_hash': expected_hash, 'reference': ref, 'error': repr(ex)})
            continue
        parsed_s_entity_count += 1
        matched = [r for r in resources if norm(r.get('resource_hash', '')) in target_set]
        if not matched:
            continue
        for r in matched:
            target_occ[norm(r['resource_hash'])] += 1
        row = {
            'package_id': f'{pkg:04X}',
            'entry_index': idx,
            'entity_data_hash': expected_hash,
            'reference': ref,
            'resource_count': len(resources),
            'matching_resources': [
                {**r, 'embedded_model_tag_hash': targets[norm(r['resource_hash'])]}
                for r in matched
            ],
            'all_resources': resources,
            'art_arrangement_contexts': info['contexts'],
        }
        hits.append(row)
        print('INVESTMENT_MODEL_RESOURCE_HIT', json.dumps(row, separators=(',', ':')), flush=True)

    rep = {
        'schema': 'd1_crota_investment_model_resource_join/v1',
        'status': 'D1_CROTA_INVESTMENT_MODEL_RESOURCE_JOIN_COMPLETE' if not errors else 'D1_CROTA_INVESTMENT_MODEL_RESOURCE_JOIN_ERRORS',
        'arrangement_count': src.get('arrangement_count'),
        'resolved_parent_count': (src.get('remote_parent_resolution') or {}).get('resolved_parent_count'),
        'unique_final_destination_count': len(finals),
        'exact_final_records_verified': exact_final_count,
        'final_reference_distribution': dict(sorted(refs.items())),
        's_entity_final_count': s_entity_count,
        'parsed_s_entity_final_count': parsed_s_entity_count,
        'target_resources': targets,
        'hit_source_count': len(hits),
        'hit_occurrences_by_resource': dict(target_occ),
        'hits': hits,
        'error_count': len(errors),
        'errors': errors,
        'policy': (
            'Only final EntityDataROI records selected by the authoritative serialized Investment arrangement graph are read. '
            'A model-resource hit requires final class 80800734 and exact source-parsed s_entity Resource[] FileHash equality. '
            'No semantic literal scan, package locality, adjacency, or appearance participates.'
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(rep, indent=2) + '\n')
    print('FINALS', len(finals), 'VERIFIED', exact_final_count, 'S_ENTITIES', s_entity_count,
          'PARSED', parsed_s_entity_count, 'HITS', len(hits), 'BY_RESOURCE', dict(target_occ),
          'REFS', dict(refs), 'ERRORS', len(errors))
    return 0 if not errors else 2


if __name__ == '__main__':
    raise SystemExit(main())
