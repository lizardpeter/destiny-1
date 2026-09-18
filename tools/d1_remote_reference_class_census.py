#!/usr/bin/env python3
"""Enumerate every current D1 PS4 FileEntry whose Reference equals an exact class hash.

This is a package-metadata census, not a graph walk.  It is intended for global
engine classes (for example ROI s_scope=80801C47) that are poor targets for broad
aligned-u32 traversal.  Every physical package family is opened through the pinned
universal member catalog, the current logical entry table is inspected, and each
matching payload is recovered and SHA-256 pinned.

No payload integer receives semantics here.  The report additionally records
printable in-payload strings and aligned values that independently resolve as
current FileHashes only as discovery evidence for subsequent class-specific parsers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import package_of
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_split_tar_extract import SplitHttpTar

NULLS = {'00000000', 'FFFFFFFF'}
PRINTABLE = re.compile(rb'[\x20-\x7e]{4,}')


def norm(x: object) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def logical_view(arc: SplitHttpTar, members: list[dict], runtime: Path) -> RemoteLogicalPackage:
    return RemoteLogicalPackage(arc, members, runtime)


def resolved_edges(payload: bytes, entry_maps: dict[int, dict[str, dict]], catalogs: dict) -> list[dict]:
    out = []
    for off in range(0, len(payload) - 3, 4):
        h = f'{struct.unpack_from("<I", payload, off)[0]:08X}'
        if h in NULLS or not h.startswith('80'):
            continue
        try:
            pkg = package_of(h)
        except Exception:
            continue
        if pkg not in catalogs:
            continue
        m = entry_maps.get(pkg)
        if m is None:
            continue
        e = m.get(h)
        if e is None:
            continue
        out.append({
            'offset': off,
            'target': h,
            'target_package_id': f'{pkg:04X}',
            'target_reference': norm(e.get('reference', 'FFFFFFFF')),
            'target_type': e.get('type'),
            'target_subtype': e.get('subtype'),
            'target_size': e.get('file_size'),
        })
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--reference', action='append', required=True)
    ap.add_argument('--dump-dir', type=Path)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    refs = sorted({norm(x) for x in a.reference})
    catalogs = load_catalogs(a.member_catalog)
    arc = SplitHttpTar(
        [f'{a.base_url.rstrip("/")}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)],
        retries=6, timeout=90,
    )

    views: dict[int, RemoteLogicalPackage] = {}
    entry_maps: dict[int, dict[str, dict]] = {}
    violations: list[str] = []

    # Open every current logical package once.  This is the authoritative global
    # class census; package-family count is part of the output boundary.
    for n, (pkg_text, members) in enumerate(sorted(catalogs.items()), 1):
        pkg = int(pkg_text, 16) if isinstance(pkg_text, str) else int(pkg_text)
        try:
            v = logical_view(arc, members, a.runtime)
            views[pkg] = v
            entry_maps[pkg] = {norm(e['tag_hash']): e for e in v.entries}
        except Exception as ex:
            violations.append(f'{pkg:04X}: logical package open failed: {ex!r}')
        if n % 50 == 0 or n == len(catalogs):
            print(f'PACKAGE_TABLES {n}/{len(catalogs)} matches_pending')

    rows = []
    reference_counts = Counter()
    package_counts = Counter()
    size_counts = Counter()
    payload_sha_to_hashes: dict[str, list[str]] = {}

    for pkg, v in sorted(views.items()):
        for e in v.entries:
            ref = norm(e.get('reference', 'FFFFFFFF'))
            if ref not in refs:
                continue
            h = norm(e['tag_hash'])
            reference_counts[ref] += 1
            package_counts[f'{pkg:04X}'] += 1
            size_counts[str(e.get('file_size'))] += 1
            row = {
                'tag_hash': h,
                'package_id': f'{pkg:04X}',
                'entry_index': int(e['index']),
                'reference': ref,
                'type': e.get('type'),
                'subtype': e.get('subtype'),
                'declared_size': e.get('file_size'),
            }
            try:
                payload = v.entry(e['index'])
                sha = hashlib.sha256(payload).hexdigest()
                row.update({
                    'payload_bytes': len(payload),
                    'payload_sha256': sha,
                    'declared_size_matches_payload': int(e.get('file_size', -1)) == len(payload),
                    'prefix_256_hex': payload[:256].hex(),
                    'suffix_128_hex': payload[-128:].hex(),
                    'printable_strings': [
                        {'offset': m.start(), 'text': m.group().decode('ascii')}
                        for m in PRINTABLE.finditer(payload)
                    ],
                })
                payload_sha_to_hashes.setdefault(sha, []).append(h)
                if a.dump_dir:
                    a.dump_dir.mkdir(parents=True, exist_ok=True)
                    (a.dump_dir / f'{h}.bin').write_bytes(payload)
            except Exception as ex:
                row['error'] = repr(ex)
                violations.append(f'{h}: payload recovery failed: {ex!r}')
            rows.append(row)

    # Resolve aligned FileHash edges after all current entry maps are available.
    for row in rows:
        if row.get('error'):
            row['resolved_aligned_filehash_edges'] = []
            continue
        p = None
        if a.dump_dir:
            fp = a.dump_dir / f"{row['tag_hash']}.bin"
            if fp.exists():
                p = fp.read_bytes()
        if p is None:
            v = views[int(row['package_id'], 16)]
            p = v.entry(row['entry_index'])
        row['resolved_aligned_filehash_edges'] = resolved_edges(p, entry_maps, catalogs)
        row['resolved_aligned_filehash_edge_count'] = len(row['resolved_aligned_filehash_edges'])

    if not rows:
        violations.append(f'no entries found for references {refs!r}')

    duplicate_payload_groups = [
        {'payload_sha256': sha, 'tag_hashes': sorted(hs), 'count': len(hs)}
        for sha, hs in sorted(payload_sha_to_hashes.items()) if len(hs) > 1
    ]
    out = {
        'schema_version': 1,
        'status': 'D1_REMOTE_REFERENCE_CLASS_CENSUS_EXACT' if not violations else 'D1_REMOTE_REFERENCE_CLASS_CENSUS_VIOLATIONS',
        'requested_references': refs,
        'package_family_count': len(catalogs),
        'opened_package_family_count': len(views),
        'matching_entry_count': len(rows),
        'reference_counts': dict(reference_counts),
        'package_counts': dict(package_counts),
        'declared_size_histogram': dict(size_counts),
        'unique_payload_sha256_count': len(payload_sha_to_hashes),
        'duplicate_payload_groups': duplicate_payload_groups,
        'rows': rows,
        'violations': violations,
        'gates': {
            'all_catalog_package_families_opened': len(views) == len(catalogs),
            'requested_class_present': bool(rows),
            'all_matching_payloads_recovered': bool(rows) and all(not r.get('error') for r in rows),
        },
        'policy': 'Global current logical FileEntry.Reference census. Reference equality establishes class membership. Printable strings and aligned values are discovery evidence only; an aligned value is emitted only when it independently resolves as a current FileHash.',
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({
        'status': out['status'],
        'requested_references': refs,
        'package_family_count': len(catalogs),
        'matching_entry_count': len(rows),
        'reference_counts': dict(reference_counts),
        'package_counts': dict(package_counts),
        'declared_size_histogram': dict(size_counts),
        'unique_payload_sha256_count': len(payload_sha_to_hashes),
        'violations': violations,
    }, indent=2))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
