#!/usr/bin/env python3
"""Recover arbitrary current D1 package families from a global Activity index.

The archive-wide ``d1_remote_activity_index.py`` artifact records exact split-TAR
locations for every current physical package member.  This tool turns that catalog
into a generic zero-header-scan recovery primitive for all later dependency walks.

Safety rules:

* the supplied current ``packages.txt`` must SHA-256 match the index exactly;
* requested package IDs must exist in ``index.package_families``;
* current family membership derived from packages.txt must exactly equal the index;
* current split-volume sizes must equal those recorded in the index;
* every recovered member is SHA-256 hashed and reported for downstream pinning.

The requested package IDs are semantic-neutral physical dependencies.  Higher-level
parsers must derive why a package is needed from serialized FileHashes/typed Tags.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from d1_split_tar_extract import SplitHttpTar

RX = re.compile(r'_([0-9A-Fa-f]{4})_[0-9]+\.pkg$', re.IGNORECASE)


def norm_pid(x: str) -> str:
    return x.lower().removeprefix('0x').zfill(4)


def pid(name: str) -> str | None:
    m = RX.search(Path(name).name)
    return m.group(1).lower() if m else None


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def current_families(package_list_bytes: bytes) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for raw in package_list_bytes.decode('utf-8', errors='replace').splitlines():
        name = Path(raw.strip()).name
        p = pid(name) if name else None
        if p is None:
            continue
        out.setdefault(p, []).append(name)
    return {k: sorted(set(v)) for k, v in out.items()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--index', type=Path, required=True)
    ap.add_argument('--package-list', type=Path, required=True)
    ap.add_argument('--package-id', action='append', required=True)
    ap.add_argument('--out-dir', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    ap.add_argument('--base-url')
    ap.add_argument('--retries', type=int, default=6)
    ap.add_argument('--timeout', type=int, default=120)
    a = ap.parse_args()

    index = json.loads(a.index.read_text())
    if index.get('status') != 'D1_REMOTE_ACTIVITY_INDEX_COMPLETE':
        raise SystemExit('global index is not complete: ' + str(index.get('status')))
    source = index.get('source') or {}
    catalog = index.get('package_families') or {}
    if not catalog:
        raise SystemExit('global index has no package_families catalog')

    package_list_bytes = a.package_list.read_bytes()
    actual_list_sha = sha256_bytes(package_list_bytes)
    expected_list_sha = str(source.get('package_list_sha256') or '').lower()
    if not expected_list_sha or actual_list_sha.lower() != expected_list_sha:
        raise SystemExit(f'packages.txt SHA-256 mismatch: {actual_list_sha} != {expected_list_sha}')
    current = current_families(package_list_bytes)

    requested = sorted({norm_pid(x) for x in a.package_id})
    missing_ids = [x for x in requested if x.upper() not in catalog and x.lower() not in catalog]
    if missing_ids:
        raise SystemExit('requested package IDs absent from index: ' + ','.join(missing_ids))

    base = (a.base_url or source.get('base_url') or '').rstrip('/')
    part_count = int(source.get('part_count') or 0)
    if not base or part_count <= 0:
        raise SystemExit('global index does not provide a usable split-TAR source')
    archive = SplitHttpTar(
        [f'{base}/packages.tar.{i:03d}' for i in range(1, part_count + 1)],
        retries=a.retries,
        timeout=a.timeout,
    )
    expected_sizes = [int(x) for x in (source.get('part_sizes') or [])]
    if expected_sizes and archive.sizes != expected_sizes:
        raise SystemExit('split-TAR part sizes changed from global index')
    expected_logical = int(source.get('logical_split_tar_bytes') or 0)
    if expected_logical and archive.logical_size != expected_logical:
        raise SystemExit(f'split-TAR logical size changed: {archive.logical_size} != {expected_logical}')

    a.out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    family_reports = {}
    for p in requested:
        key = p.upper() if p.upper() in catalog else p.lower()
        members = list(catalog[key])
        index_names = sorted(Path(x['name']).name for x in members)
        current_names = current.get(p, [])
        if current_names != index_names:
            raise SystemExit(f'{p}: current family membership differs from index: current={current_names} index={index_names}')
        family_rows = []
        for member in sorted(members, key=lambda x: Path(x['name']).name):
            name = Path(member['name']).name
            off = int(member['data_offset'])
            size = int(member['size'])
            dst = a.out_dir / name
            got = archive.copy_to(off, size, dst)
            row = {
                'package_id': p,
                'name': name,
                'data_offset': off,
                'size': size,
                'sha256': got,
                'header_patch_id': int(member.get('header_patch_id', -1)),
                'filename_generation': int(member.get('filename_generation', -1)),
                'source': 'D1_REMOTE_ACTIVITY_INDEX/package_families',
                'output': str(dst),
            }
            rows.append(row)
            family_rows.append(row)
            print('RECOVERED_INDEXED_FAMILY', p, name, size, got, flush=True)
        family_reports[p] = {
            'member_count': len(family_rows),
            'members': family_rows,
        }

    report = {
        'schema_version': 1,
        'status': 'D1_INDEXED_PACKAGE_FAMILY_RECOVERY_COMPLETE',
        'index': str(a.index),
        'index_schema_version': index.get('schema_version'),
        'package_list_sha256': actual_list_sha,
        'requested_package_ids': requested,
        'family_count': len(requested),
        'member_count': len(rows),
        'split_tar_headers_scanned': 0,
        'families': family_reports,
        'members': rows,
        'policy': (
            'Physical recovery is permitted only against the exact packages.txt and split-volume sizes captured by the global index. '
            'Package IDs must be supplied by higher-level serialized dependency logic; this tool performs no semantic inference.'
        ),
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in (
        'status','requested_package_ids','family_count','member_count','split_tar_headers_scanned','package_list_sha256'
    )}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
