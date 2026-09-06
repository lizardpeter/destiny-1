#!/usr/bin/env python3
"""Recover the exact current package corpus for the integrated Tower articulated visual.

The articulated validation artifact already preserves exact split-TAR data offsets,
sizes, and SHA-256s for every package family reached by the source-owned entity
dependency closure.  Rewalking the entire public package TAR to rediscover those
same physical members is unnecessary and slow.

This tool therefore:
  * accepts the current packages.txt as the authority for physical family membership;
  * reuses a prior member location only when the prior family membership matches the
    current family exactly;
  * SHA-verifies every prior member that supplied a digest;
  * consumes checked-in physical member catalogs for extra proven texture families;
  * scans the TAR only for explicitly requested package IDs still lacking a complete
    validated member-location family (currently the newly discovered 0050 material family).

No package filename is used to infer semantic ownership.  All dependency package IDs
must already be supplied by serialized FileHashes or a caller's independently proven
texture dependency plan.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from d1_split_tar_extract import SplitHttpTar

RX = re.compile(r'_([0-9a-fA-F]{4})_[0-9]+\.pkg$')


def pid(name: str) -> str | None:
    m = RX.search(Path(name).name)
    return m.group(1).lower() if m else None


def parse_int(v):
    if isinstance(v, int):
        return v
    if isinstance(v, str):
        return int(v, 0)
    raise TypeError(v)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def current_families(package_list: Path) -> dict[str, list[str]]:
    out = defaultdict(list)
    for raw in package_list.read_text(errors='replace').splitlines():
        name = Path(raw.strip()).name
        if not name:
            continue
        p = pid(name)
        if p:
            out[p].append(name)
    return {k: sorted(set(v)) for k, v in out.items()}


def ingest_prior_report(path: Path, locations: dict[str, dict], provenance: list[dict]):
    d = json.loads(path.read_text())
    rows = list(d.get('members', [])) + list(d.get('recovered_members', []))
    accepted = 0
    for r in rows:
        name = Path(r['name']).name
        p = pid(name)
        if p is None or r.get('data_offset') is None or r.get('size') is None:
            continue
        row = {
            'name': name,
            'package_id': p,
            'data_offset': parse_int(r['data_offset']),
            'size': parse_int(r['size']),
            'sha256': r.get('sha256'),
            'source': str(path),
            'mode': 'validated_prior_articulated_provenance',
        }
        old = locations.get(name)
        if old is not None and (old['data_offset'], old['size']) != (row['data_offset'], row['size']):
            raise ValueError(f'conflicting prior locations for {name}: {old} vs {row}')
        locations[name] = row
        accepted += 1
    provenance.append({'path': str(path), 'kind': 'prior_report', 'accepted_member_rows': accepted})


def ingest_catalog(path: Path, locations: dict[str, dict], provenance: list[dict]):
    d = json.loads(path.read_text())
    accepted = 0
    for p, rows in (d.get('families') or {}).items():
        p = p.lower()
        for r in rows:
            name = Path(r['name']).name
            actual = pid(name)
            if actual != p:
                raise ValueError(f'{path}: catalog key {p} does not match {name} package id {actual}')
            row = {
                'name': name,
                'package_id': p,
                'data_offset': parse_int(r['data_offset']),
                'size': parse_int(r['size']),
                'sha256': r.get('sha256'),
                'source': str(path),
                'mode': 'validated_checked_in_member_catalog',
            }
            old = locations.get(name)
            if old is not None and (old['data_offset'], old['size']) != (row['data_offset'], row['size']):
                raise ValueError(f'conflicting catalog locations for {name}: {old} vs {row}')
            locations[name] = row
            accepted += 1
    provenance.append({'path': str(path), 'kind': 'member_catalog', 'accepted_member_rows': accepted})


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--package-list', type=Path, required=True)
    ap.add_argument('--required-package-id', action='append', default=[])
    ap.add_argument('--prior-report', type=Path, action='append', default=[])
    ap.add_argument('--member-catalog', type=Path, action='append', default=[])
    ap.add_argument('--out-dir', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    ap.add_argument('--base-url', default='https://crypt.cohae.dev/destiny/ps4/packages/latest')
    ap.add_argument('--part-count', type=int, default=10)
    a = ap.parse_args()

    required = sorted({x.lower().removeprefix('0x').zfill(4) for x in a.required_package_id})
    if not required:
        raise SystemExit('no required package IDs')
    current = current_families(a.package_list)
    missing_ids = [p for p in required if p not in current]
    if missing_ids:
        raise SystemExit('required package IDs absent from current packages.txt: ' + ','.join(missing_ids))

    locations: dict[str, dict] = {}
    provenance = []
    for p in a.prior_report:
        ingest_prior_report(p, locations, provenance)
    for p in a.member_catalog:
        ingest_catalog(p, locations, provenance)

    family_modes = {}
    scan_names = set()
    for p in required:
        names = current[p]
        located = sorted(n for n in names if n in locations)
        extra = sorted(n for n, r in locations.items() if r['package_id'] == p and n not in names)
        if located == names and not extra:
            family_modes[p] = 'validated_prior_exact_current_family_membership'
        else:
            # A stale/partial prior catalog is not mixed with a scan. Rediscover the
            # entire current family so all physical members share one provenance mode.
            family_modes[p] = 'current_family_split_tar_scan'
            scan_names.update(names)

    archive = SplitHttpTar(
        [f'{a.base_url.rstrip("/")}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)],
        retries=6,
        timeout=120,
    )
    scanned = {}
    headers = 0
    if scan_names:
        scanned, headers = archive.find(scan_names)
        absent = sorted(scan_names - set(scanned))
        if absent:
            raise SystemExit('current family members not found in split TAR: ' + repr(absent))

    a.out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for p in required:
        for name in current[p]:
            if family_modes[p] == 'current_family_split_tar_scan':
                info = scanned[name]
                source = 'current_split_tar_scan'
                expected_sha = None
                data_offset = int(info['data_offset'])
                size = int(info['size'])
            else:
                info = locations[name]
                source = info['source']
                expected_sha = info.get('sha256')
                data_offset = int(info['data_offset'])
                size = int(info['size'])
            dst = a.out_dir / name
            got_sha = archive.copy_to(data_offset, size, dst)
            if expected_sha and got_sha.lower() != expected_sha.lower():
                raise SystemExit(f'{name}: SHA mismatch {got_sha} != {expected_sha}')
            if dst.stat().st_size != size:
                raise SystemExit(f'{name}: size mismatch after recovery')
            rows.append({
                'package_id': p,
                'name': name,
                'data_offset': data_offset,
                'size': size,
                'sha256': got_sha,
                'expected_sha256': expected_sha,
                'sha_verified': bool(expected_sha),
                'family_mode': family_modes[p],
                'location_source': source,
                'output': str(dst),
            })
            print('RECOVERED', p, name, size, got_sha, family_modes[p], flush=True)

    report = {
        'schema_version': 1,
        'status': 'D1_TOWER_ARTICULATED_VISUAL_CORPUS_RECOVERED',
        'required_package_ids': required,
        'required_family_count': len(required),
        'member_count': len(rows),
        'family_modes': family_modes,
        'split_tar_scanned_package_ids': sorted(p for p, mode in family_modes.items() if mode == 'current_family_split_tar_scan'),
        'split_tar_headers_scanned': headers,
        'provenance_sources': provenance,
        'members': rows,
        'policy': (
            'Current packages.txt is the authority for physical family membership. Prior offsets are reused only '
            'when their family membership is an exact current match; prior SHA-256s are reverified. Any incomplete '
            'or stale family is rediscovered in full. Semantic dependency package IDs are caller-supplied and are '
            'never inferred from filenames.'
        ),
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('status','required_family_count','member_count','family_modes','split_tar_scanned_package_ids','split_tar_headers_scanned')}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
