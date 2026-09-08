#!/usr/bin/env python3
"""Build an exact current D1 PS4 named-tag catalog from a pinned universal package catalog.

The universal package catalog already preserves exact split-TAR byte locations for
all current ordinary package-family members. This probe chooses the current member
of each family, reads only the serialized Tiger header and named-tag table, SHA-1
validates every table, and emits every named tag without semantic filtering.

This is intended for renderer-global discovery (for example ``render_globals``),
not name-based asset inference. A named tag is authoritative only because its name,
TagHash and TagClassHash are serialized together in the package named-tag table.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from collections import Counter
from pathlib import Path

from d1_pkg_probe import parse_header, parse_named
from d1_split_tar_extract import SplitHttpTar

NAMED_STRIDE = 0x44


def norm(x: object) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def choose_current(rows: list[dict]) -> dict:
    if not rows:
        raise ValueError('empty package family')
    return max(rows, key=lambda r: (int(r.get('header_patch_id', -1)), int(r.get('filename_generation', -1)), str(r.get('name', ''))))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--catalog', type=Path, required=True)
    ap.add_argument('--base-url', default='https://crypt.cohae.dev/destiny/ps4/packages/latest')
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--query', action='append', default=[])
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()

    source_bytes = args.catalog.read_bytes()
    source_sha = hashlib.sha256(source_bytes).hexdigest()
    catalog = json.loads(source_bytes)
    families = catalog.get('families') or {}
    if catalog.get('schema') != 'd1_remote_package_member_catalog/v1':
        raise SystemExit(f"unexpected catalog schema {catalog.get('schema')!r}")
    if not families:
        raise SystemExit('catalog has no package families')

    archive = SplitHttpTar(
        [f"{args.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1, args.part_count + 1)],
        retries=6,
        timeout=90,
    )

    rows = []
    package_rows = []
    violations = []
    for n, (pkg_text, members) in enumerate(sorted(families.items()), 1):
        pkg = norm(pkg_text)[-4:]
        current = choose_current(members)
        data_offset = int(current['data_offset'])
        size = int(current['size'])
        if size < 0x140:
            violations.append(f'{pkg}:{current.get("name")}:short package {size}')
            continue
        hb = archive.read_at(data_offset, 0x140)
        h = parse_header(io.BytesIO(hb))
        actual_pkg = f"{int(h['pkg_id']):04X}"
        if actual_pkg != pkg:
            violations.append(f'{pkg}:{current.get("name")}:header pkg {actual_pkg}')
        count = int(h['named_tag_table_count'])
        off = int(h['named_tag_table_offset'])
        byte_count = count * NAMED_STRIDE
        package_row = {
            'package_id': actual_pkg,
            'snapshot': current['name'],
            'header_patch_id': int(h['patch_id']),
            'filename_generation': int(current.get('filename_generation', -1)),
            'named_tag_count': count,
            'named_tag_offset': off,
            'named_tag_sha1_expected': str(h['named_tag_table_hash']).lower(),
        }
        if count:
            if off < 0 or off + byte_count > size:
                violations.append(f'{pkg}:{current.get("name")}:named table bounds {off}+{byte_count}>{size}')
                package_rows.append(package_row)
                continue
            raw = archive.read_at(data_offset + off, byte_count)
            actual_sha = hashlib.sha1(raw).hexdigest()
            package_row['named_tag_sha1_actual'] = actual_sha
            package_row['named_tag_sha1_matches'] = actual_sha == package_row['named_tag_sha1_expected']
            if actual_sha != package_row['named_tag_sha1_expected']:
                violations.append(f'{pkg}:{current.get("name")}:named SHA1 mismatch')
                package_rows.append(package_row)
                continue
            for r in parse_named(raw):
                rows.append({
                    'tag_hash': norm(r['tag_hash']),
                    'class_hash': norm(r['class_hash']),
                    'name': r.get('name'),
                    'named_table_index': int(r['index']),
                    'package_id': actual_pkg,
                    'snapshot': current['name'],
                    'header_patch_id': int(h['patch_id']),
                    'filename_generation': int(current.get('filename_generation', -1)),
                    'named_table_sha1': actual_sha,
                })
        package_rows.append(package_row)
        if n % 50 == 0 or n == len(families):
            print(f'NAMED_HEADERS {n}/{len(families)} rows={len(rows)}', flush=True)

    duplicate_identity = []
    identities = {}
    for r in rows:
        k = (r['tag_hash'], r['name'])
        old = identities.get(k)
        if old and old['class_hash'] != r['class_hash']:
            duplicate_identity.append({'tag_hash': r['tag_hash'], 'name': r['name'], 'classes': sorted({old['class_hash'], r['class_hash']})})
        else:
            identities[k] = r
    if duplicate_identity:
        violations.append(f'named tag/name class conflicts: {len(duplicate_identity)}')

    query_rows = {}
    for q in args.query:
        needle = q.casefold()
        query_rows[q] = [r for r in rows if needle in str(r.get('name') or '').casefold()]

    out = {
        'schema_version': 1,
        'status': 'D1_CURRENT_NAMED_TAG_CATALOG_EXACT' if not violations else 'D1_CURRENT_NAMED_TAG_CATALOG_VIOLATIONS',
        'source_catalog': str(args.catalog),
        'source_catalog_sha256': source_sha,
        'source_catalog_packages_txt_sha256': catalog.get('packages_txt_sha256'),
        'package_family_count': len(families),
        'scanned_package_count': len(package_rows),
        'packages_with_named_tags': sum(int(x['named_tag_count']) > 0 for x in package_rows),
        'named_row_count': len(rows),
        'unique_tag_hash_count': len({r['tag_hash'] for r in rows}),
        'unique_name_count': len({r['name'] for r in rows}),
        'class_histogram': dict(Counter(r['class_hash'] for r in rows)),
        'queries': query_rows,
        'duplicate_identity_conflicts': duplicate_identity,
        'violations': violations,
        'package_rows': package_rows,
        'named_tags': rows,
        'policy': 'Exact current package named-tag bytes only. Names are serialized evidence for locating named engine roots; no asset semantics are inferred from substring matches.',
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({
        'status': out['status'],
        'package_family_count': out['package_family_count'],
        'packages_with_named_tags': out['packages_with_named_tags'],
        'named_row_count': out['named_row_count'],
        'query_counts': {k: len(v) for k, v in query_rows.items()},
        'query_rows': query_rows,
        'violations': violations,
    }, indent=2))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
