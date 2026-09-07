#!/usr/bin/env python3
"""Join Crota/Hive semantic hashes to exact Investment art-arrangement final entities.

Consumes the exhaustive d1-bulk-weapon-resolution-census art-arrangement output.
That corpus already proves, for every resolved row:

  EntityArrangementMap assignment -> EntityParent -> EntityParent +0x10 EntityDataROI

This tool does not scan arbitrary Investment entries.  It opens only the exact
EntityDataROI FileHashes selected by those serialized art-arrangement edges, scans
their resident structured payloads for caller-supplied aligned u32 semantic hashes,
and emits every original arrangement/assignment/parent context for a hit.

An aligned literal hit proves serialization of the semantic hash inside that exact
final record.  Field meaning is deliberately not inferred; source class and offsets
are preserved for a schema-specific follow-up parser.
"""
from __future__ import annotations

import argparse
import collections
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from d1_investment_arrangement_probe import filehash_pkg_index
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_split_tar_extract import SplitHttpTar


def norm(v: object) -> str:
    return str(v).upper().removeprefix('0X').zfill(8)


def parse_target(text: str) -> tuple[str, str]:
    if '=' in text:
        label, raw = text.split('=', 1)
    else:
        label, raw = text, text
    h = norm(raw)
    int(h, 16)
    return label, h


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('resolved_arrangements', type=Path)
    ap.add_argument('--target', action='append', required=True,
                    help='semantic target as LABEL=HASH or HASH')
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--max-entry-size', type=int, default=4_000_000)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    src = json.loads(a.resolved_arrangements.read_text())
    remote = src.get('remote_parent_resolution') or {}
    if int(remote.get('unique_parent_count', 0)) < 8000:
        raise SystemExit('input is not the exhaustive art-arrangement parent-resolution corpus')
    if int(remote.get('resolved_parent_count', 0)) < 8000:
        raise SystemExit('input has insufficient resolved parent coverage')

    targets = [parse_target(x) for x in a.target]
    by_value = {int(h, 16): (label, h) for label, h in targets}
    if len(by_value) != len(targets):
        raise SystemExit('duplicate target hash values')

    # Preserve the exact parallel assignment/parent positions from each retail
    # arrangement row and attach them to each already-resolved final EntityDataROI.
    entity_context: dict[str, list[dict]] = collections.defaultdict(list)
    context_errors = []
    for arr in src.get('arrangements', []):
        assignments = [norm(x) for x in arr.get('assignment_hashes', [])]
        parents = [norm(x) if x is not None else None for x in arr.get('entity_parent_hashes', [])]
        entities = arr.get('entities', [])
        if len(entities) != len(parents):
            context_errors.append({
                'arrangement_index': arr.get('arrangement_index'),
                'reason': 'entities/parent list length mismatch',
                'entities': len(entities), 'parents': len(parents),
            })
            continue
        if len(assignments) != len(parents):
            context_errors.append({
                'arrangement_index': arr.get('arrangement_index'),
                'reason': 'assignment/parent list length mismatch',
                'assignments': len(assignments), 'parents': len(parents),
            })
            continue
        for i, rec in enumerate(entities):
            if not rec or not rec.get('resolved'):
                continue
            ph = norm(rec.get('parent_hash'))
            if parents[i] is not None and ph != parents[i]:
                context_errors.append({
                    'arrangement_index': arr.get('arrangement_index'), 'slot': i,
                    'reason': 'resolved parent does not match serialized parallel parent slot',
                    'row_parent': parents[i], 'resolved_parent': ph,
                })
                continue
            eh = norm(rec.get('entity_data_hash'))
            entity_context[eh].append({
                'arrangement_index': int(arr.get('arrangement_index')),
                'arrangement_source': arr.get('source'),
                'slot': i,
                'assignment_hash': assignments[i],
                'parent_hash': ph,
                'parent_reference': norm(rec.get('reference', 'FFFFFFFF')),
            })

    if context_errors:
        raise SystemExit('parallel assignment/parent context integrity failure: ' + json.dumps(context_errors[:10]))

    catalogs = load_catalogs(a.member_catalog)
    needed_pkgs = {filehash_pkg_index(int(h, 16))[0] for h in entity_context}
    missing = sorted(needed_pkgs - set(catalogs))
    if missing:
        raise SystemExit('missing verified member catalogs for final entity packages: ' + ','.join(f'{x:04X}' for x in missing))

    base = a.base_url.rstrip('/')
    arc = SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    views: dict[int, RemoteLogicalPackage] = {}

    def view(pkg: int) -> RemoteLogicalPackage:
        if pkg not in views:
            views[pkg] = RemoteLogicalPackage(arc, catalogs[pkg], a.runtime)
        return views[pkg]

    hits = []
    errors = []
    class_counts = collections.Counter()
    scanned_pkg_counts = collections.Counter()
    hit_target_occurrences = collections.Counter()
    hit_target_sources = collections.Counter()
    skipped_size = 0
    skipped_nonstructured = 0

    tags = sorted(entity_context)
    for n, tag in enumerate(tags, 1):
        pkg, idx = filehash_pkg_index(int(tag, 16))
        r = view(pkg)
        try:
            if idx >= len(r.entries):
                raise ValueError('final entity file index outside logical entry table')
            e = r.entries[idx]
            if e['tag_hash'].upper() != tag:
                raise ValueError(f"logical tag mismatch {e['tag_hash']}")
            ref = e['reference'].upper()
            class_counts[ref] += 1
            scanned_pkg_counts[f'{pkg:04X}'] += 1
            if e['type'] != 16 or e['subtype'] != 0:
                skipped_nonstructured += 1
                continue
            if int(e['file_size']) > a.max_entry_size:
                skipped_size += 1
                continue
            b = r.entry(idx)
            found: dict[str, list[int]] = collections.defaultdict(list)
            end = len(b) - (len(b) % 4)
            for off in range(0, end, 4):
                v = struct.unpack_from('<I', b, off)[0]
                target = by_value.get(v)
                if target is not None:
                    found[target[1]].append(off)
            if found:
                labels = {h: next(label for label, hh in targets if hh == h) for h in found}
                row = {
                    'entity_data_hash': tag,
                    'package_id': f'{pkg:04X}',
                    'file_index': idx,
                    'reference': ref,
                    'type': int(e['type']),
                    'subtype': int(e['subtype']),
                    'size': int(e['file_size']),
                    'semantic_hits': {
                        h: {'label': labels[h], 'offsets': offs}
                        for h, offs in sorted(found.items())
                    },
                    'art_arrangement_contexts': entity_context[tag],
                }
                hits.append(row)
                for h, offs in found.items():
                    hit_target_occurrences[h] += len(offs)
                    hit_target_sources[h] += 1
                print('SEMANTIC_FINAL_ENTITY_HIT', json.dumps(row, separators=(',', ':')), flush=True)
        except Exception as ex:
            errors.append({'entity_data_hash': tag, 'package_id': f'{pkg:04X}', 'file_index': idx, 'error': repr(ex)})
        if n % 500 == 0:
            print('PROGRESS', n, '/', len(tags), 'HITS', len(hits), 'ERRORS', len(errors), flush=True)

    report = {
        'schema': 'd1_crota_investment_final_entity_semantic_join/v1',
        'status': 'D1_CROTA_INVESTMENT_FINAL_ENTITY_SEMANTIC_JOIN_COMPLETE' if not errors else 'D1_CROTA_INVESTMENT_FINAL_ENTITY_SEMANTIC_JOIN_WITH_ERRORS',
        'source_parent_resolution': {
            'unique_parent_count': int(remote.get('unique_parent_count', 0)),
            'resolved_parent_count': int(remote.get('resolved_parent_count', 0)),
            'evidence_policy': remote.get('evidence_policy'),
        },
        'targets': [{'label': label, 'hash': h} for label, h in targets],
        'unique_final_entity_count': len(tags),
        'final_entity_package_ids': [f'{x:04X}' for x in sorted(needed_pkgs)],
        'scanned_entity_count_by_package': dict(sorted(scanned_pkg_counts.items())),
        'final_entity_reference_counts': dict(class_counts.most_common()),
        'skipped_nonstructured_count': skipped_nonstructured,
        'skipped_oversize_count': skipped_size,
        'hit_source_count': len(hits),
        'hit_occurrences_by_target': dict(sorted(hit_target_occurrences.items())),
        'hit_sources_by_target': dict(sorted(hit_target_sources.items())),
        'hits': hits,
        'error_count': len(errors),
        'errors': errors,
        'remote_blocks_read': {f'{pkg:04X}': len(r.block_cache) for pkg, r in sorted(views.items())},
        'policy': (
            'Only exact EntityDataROI FileHashes already selected by serialized art-arrangement assignment->EntityParent->+0x10 edges are scanned. '
            'Every semantic hit is an exact aligned u32 literal inside that final record and is joined back to its exact assignment/parent contexts. '
            'Literal presence alone does not assign field semantics; source reference and offsets are retained for schema-specific closure.'
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + '\n')
    print('STATUS', report['status'], 'FINAL_ENTITIES', len(tags), 'HIT_SOURCES', len(hits), 'ERRORS', len(errors))
    print('BY_TARGET', json.dumps(report['hit_occurrences_by_target'], sort_keys=True))
    return 0 if not errors else 2


if __name__ == '__main__':
    raise SystemExit(main())
