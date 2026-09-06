#!/usr/bin/env python3
"""Build a current D1 Activity + package-family index from the remote split TAR.

This is the archive-wide entry point for a reusable world/map exporter. It does
not download package bodies. Instead it:

* walks the public split TAR once to locate every current ``packages.txt`` member;
* reads only the 0x140-byte Tiger package header from each physical member;
* groups members by Tiger package id and selects the current physical generation
  using the same ``(header.patch_id, filename_generation)`` ordering already used
  by the local Activity census;
* reads only the selected member's named-tag table (0x44-byte rows);
* SHA-1 validates the serialized named-tag table against the package header;
* canonicalizes the D1 ROI Activity named TagClassHash without guessing from names;
* losslessly merges same-TagHash aliases while rejecting class/package conflicts;
* preserves the exact split-TAR location of every current physical package member,
  not only Activity-owning families, so any later FileHash package dependency can
  be range-recovered without rescanning TAR headers.

Semantic selection never uses package or Activity display-name text. The named
TagClassHash is the authority for Activity identity. Package filenames are used
only to group physical patch siblings and validate package-id consistency.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from d1_pkg_probe import parse_header, parse_named
from d1_split_tar_extract import SplitHttpTar

ACTIVITY_ROI = '8080052E'      # Charm schema display: 2E058080
UNK_ACTIVITY_ROI = '80800616'  # Charm schema display: 16068080
NAMED_STRIDE = 0x44
PKG_RX = re.compile(r'_([0-9A-Fa-f]{4})_([0-9]+)\.pkg$', re.IGNORECASE)


def norm(x: object) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def charm_display(raw_uint_hex: str) -> str:
    h = norm(raw_uint_hex)
    return ''.join(reversed([h[i:i + 2] for i in range(0, 8, 2)]))


def canonical_named_class(raw_uint_hex: str) -> str:
    h = norm(raw_uint_hex)
    aliases = {
        ACTIVITY_ROI: ACTIVITY_ROI,
        charm_display(ACTIVITY_ROI): ACTIVITY_ROI,
        UNK_ACTIVITY_ROI: UNK_ACTIVITY_ROI,
        charm_display(UNK_ACTIVITY_ROI): UNK_ACTIVITY_ROI,
    }
    return aliases.get(h, h)


def filename_identity(name: str) -> tuple[str, int] | None:
    m = PKG_RX.search(Path(name).name)
    if not m:
        return None
    return m.group(1).upper(), int(m.group(2))


def merge_alias_rows(rows: list[dict]) -> tuple[list[dict], list[str]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row['tag_hash']].append(row)

    merged = []
    violations = []
    for h in sorted(grouped):
        xs = grouped[h]
        classes = sorted({x['class_hash_canonical'] for x in xs})
        packages = sorted({x['source_package_id'] for x in xs})
        if len(classes) != 1:
            violations.append(f'current_named_tag_class_conflict:{h}:{classes}')
        if len(packages) != 1:
            violations.append(f'current_named_tag_package_conflict:{h}:{packages}')
        aliases = []
        named_indices = []
        for x in xs:
            if x.get('name') not in aliases:
                aliases.append(x.get('name'))
            named_indices.append(int(x['index']))
        display_name = max((x for x in aliases if x is not None), key=len, default=None)
        base = dict(xs[0])
        base['name'] = display_name
        base['aliases'] = aliases
        base['named_table_indices'] = named_indices
        base['alias_count'] = len(xs)
        merged.append(base)
    return merged, violations


def compact_family(rows: list[dict]) -> list[dict]:
    keys = (
        'name', 'package_id', 'filename_generation', 'header_patch_id',
        'tar_header_offset', 'data_offset', 'size', 'platform_code', 'language_code',
        'named_tag_table_count', 'named_tag_table_offset', 'named_tag_table_hash',
    )
    return [{k: x[k] for k in keys} for x in rows]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--package-list', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--tsv', type=Path)
    ap.add_argument('--base-url', default='https://crypt.cohae.dev/destiny/ps4/packages/latest')
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--retries', type=int, default=6)
    ap.add_argument('--timeout', type=int, default=120)
    a = ap.parse_args()

    package_list_bytes = a.package_list.read_bytes()
    package_list_sha256 = hashlib.sha256(package_list_bytes).hexdigest()
    listed = []
    seen = set()
    for raw in package_list_bytes.decode('utf-8', errors='replace').splitlines():
        name = Path(raw.strip()).name
        if not name or name in seen or not filename_identity(name):
            continue
        seen.add(name)
        listed.append(name)
    listed.sort()
    if not listed:
        raise SystemExit('packages.txt yielded no D1 package members')

    archive = SplitHttpTar(
        [f'{a.base_url.rstrip("/")}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)],
        retries=a.retries,
        timeout=a.timeout,
    )
    locations, tar_headers = archive.find(set(listed))
    missing = sorted(set(listed) - set(locations))
    if missing:
        raise SystemExit(f'{len(missing)} current packages.txt members absent from split TAR: {missing[:20]}')

    physical = []
    families: dict[str, list[dict]] = defaultdict(list)
    violations = []
    for n, name in enumerate(listed, 1):
        ident = filename_identity(name)
        assert ident is not None
        filename_pkg, filename_generation = ident
        loc = locations[name]
        size = int(loc['size'])
        if size < 0x140:
            violations.append(f'{name}:physical_member_shorter_than_package_header:{size}')
            continue
        header_bytes = archive.read_at(int(loc['data_offset']), 0x140)
        h = parse_header(io.BytesIO(header_bytes))
        header_pkg = f"{int(h['pkg_id']):04X}"
        if header_pkg != filename_pkg:
            violations.append(f'{name}:filename_package_id_{filename_pkg}_header_{header_pkg}')
        row = {
            'name': name,
            'package_id': header_pkg,
            'filename_package_id': filename_pkg,
            'filename_generation': filename_generation,
            'header_patch_id': int(h['patch_id']),
            'platform': h['platform'],
            'platform_code': int(h['platform_code']),
            'language': h['language'],
            'language_code': int(h['language_code']),
            'named_tag_table_count': int(h['named_tag_table_count']),
            'named_tag_table_offset': int(h['named_tag_table_offset']),
            'named_tag_table_hash': str(h['named_tag_table_hash']).lower(),
            'tar_header_offset': int(loc['header_offset']),
            'data_offset': int(loc['data_offset']),
            'size': size,
        }
        if row['platform'] != 'PS4':
            violations.append(f'{name}:unexpected_platform:{row["platform"]}')
        physical.append(row)
        families[header_pkg].append(row)
        if n % 100 == 0 or n == len(listed):
            print(f'HEADERS {n}/{len(listed)}', flush=True)

    current_packages = []
    current_named_rows = []
    family_members = {}
    for pkg_id in sorted(families):
        rows = sorted(families[pkg_id], key=lambda r: (r['header_patch_id'], r['filename_generation'], r['name']))
        chosen = rows[-1]
        family_members[pkg_id] = rows
        current = dict(chosen)
        current['family_member_count'] = len(rows)
        current['selection_policy'] = 'max(header_patch_id, filename_generation)'
        current_packages.append(current)

        count = int(chosen['named_tag_table_count'])
        off = int(chosen['named_tag_table_offset'])
        if count == 0:
            continue
        byte_count = count * NAMED_STRIDE
        if off < 0 or byte_count < 0 or off + byte_count > int(chosen['size']):
            violations.append(f'{chosen["name"]}:named_tag_table_bounds:{off}+{byte_count}>{chosen["size"]}')
            continue
        raw = archive.read_at(int(chosen['data_offset']) + off, byte_count)
        actual_sha = hashlib.sha1(raw).hexdigest()
        expected_sha = str(chosen['named_tag_table_hash']).lower()
        if actual_sha != expected_sha:
            violations.append(f'{chosen["name"]}:named_tag_table_sha1_mismatch:{actual_sha}!={expected_sha}')
            continue
        for e in parse_named(raw):
            raw_cls = norm(e['class_hash'])
            current_named_rows.append({
                **e,
                'tag_hash': norm(e['tag_hash']),
                'class_hash_raw_uint': raw_cls,
                'class_hash_charm_display': charm_display(raw_cls),
                'class_hash_canonical': canonical_named_class(raw_cls),
                'source_package_id': pkg_id,
                'source_snapshot': chosen['name'],
                'source_patch_id': chosen['header_patch_id'],
                'source_generation': chosen['filename_generation'],
                'named_table_sha1': actual_sha,
            })

    merged, alias_violations = merge_alias_rows(current_named_rows)
    violations.extend(alias_violations)
    activities = []
    unk_activities = []
    by_class = Counter(x['class_hash_canonical'] for x in merged)
    for row in merged:
        cls = row['class_hash_canonical']
        if cls not in {ACTIVITY_ROI, UNK_ACTIVITY_ROI}:
            continue
        pkg_id = row['source_package_id']
        outrow = dict(row)
        outrow['physical_family_members'] = compact_family(family_members[pkg_id])
        if cls == ACTIVITY_ROI:
            activities.append(outrow)
        else:
            unk_activities.append(outrow)

    family_catalog = {pkg_id: compact_family(rows) for pkg_id, rows in sorted(family_members.items())}
    out = {
        'schema_version': 2,
        'status': 'D1_REMOTE_ACTIVITY_INDEX_COMPLETE' if not violations else 'D1_REMOTE_ACTIVITY_INDEX_PARTIAL',
        'source': {
            'package_list': str(a.package_list),
            'package_list_sha256': package_list_sha256,
            'base_url': a.base_url,
            'part_count': a.part_count,
            'part_sizes': archive.sizes,
            'logical_split_tar_bytes': archive.logical_size,
            'tar_headers_scanned': tar_headers,
        },
        'physical_member_count': len(physical),
        'package_family_count': len(families),
        'current_package_count': len(current_packages),
        'package_families': family_catalog,
        'current_packages_with_named_tags': sum(int(x['named_tag_table_count']) > 0 for x in current_packages),
        'current_named_row_count': len(current_named_rows),
        'current_unique_named_tag_count': len(merged),
        'current_named_alias_row_count': len(current_named_rows) - len(merged),
        'current_named_class_counts': dict(by_class),
        'activity_class_raw_uint': ACTIVITY_ROI,
        'current_d1_activity_count': len(activities),
        'current_d1_activities': activities,
        'current_unknown_activity_count': len(unk_activities),
        'current_unknown_activities': unk_activities,
        'current_packages': current_packages,
        'violations': violations,
        'policy': (
            'Activity identity comes only from the current package named-tag TagClassHash. '
            'Package display names and Activity names are not semantic selection inputs. '
            'The remote index reads package headers and named-tag tables only; no asset payload bodies are downloaded. '
            'The package_families table is a physical byte-location index only and may be reused only when the exact packages.txt SHA-256 matches.'
        ),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + '\n')

    tsv = a.tsv or a.out.with_suffix('.tsv')
    tsv.parent.mkdir(parents=True, exist_ok=True)
    with tsv.open('w', encoding='utf-8', newline='') as f:
        f.write('activity\tname\taliases\tpackage_id\tcurrent_snapshot\tpatch_id\tfamily_members\n')
        for x in activities:
            aliases = '|'.join('' if v is None else str(v) for v in x.get('aliases', []))
            f.write('\t'.join([
                x['tag_hash'],
                '' if x.get('name') is None else str(x['name']).replace('\t',' '),
                aliases.replace('\t',' '),
                x['source_package_id'],
                x['source_snapshot'],
                str(x['source_patch_id']),
                str(len(x['physical_family_members'])),
            ]) + '\n')

    print(json.dumps({
        'status': out['status'],
        'physical_member_count': out['physical_member_count'],
        'package_family_count': out['package_family_count'],
        'current_packages_with_named_tags': out['current_packages_with_named_tags'],
        'current_named_row_count': out['current_named_row_count'],
        'current_d1_activity_count': out['current_d1_activity_count'],
        'current_unknown_activity_count': out['current_unknown_activity_count'],
        'package_list_sha256': package_list_sha256,
        'violations': out['violations'][:20],
    }, indent=2))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
