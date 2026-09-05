#!/usr/bin/env python3
"""Recover the exact pinned 24-member D1 Tower map/activity root corpus.

This combines the previously pinned 023D/0244 Activity roots with the already pinned
024C/0250 destination generations. It exists so world-root discovery can operate on a
small semantic-neutral physical corpus, while geometry/material dependencies remain in
a separate larger corpus.

Package filenames are used only to reproduce the established physical fixture and to
fail closed if archive family membership changes. Actual world ownership is resolved
from serialized D1 Activity/Bubble/MapContainer/MapDataTable classes after recovery.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from d1_split_tar_extract import SplitHttpTar
from d1_tower_recover_activity_root_corpus import MEMBERS as ACTIVITY_MEMBERS
from d1_tower_recover_current_corpus import CORE as CURRENT_CORE, pkg_id

DESTINATION_MEMBERS = [x for x in CURRENT_CORE if pkg_id(x[0]) in {'024c', '0250'}]
MEMBERS = ACTIVITY_MEMBERS + DESTINATION_MEMBERS
FAMILY_IDS = {'023d', '0244', '024c', '0250'}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--package-list', type=Path, required=True)
    ap.add_argument('--out-dir', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    ap.add_argument('--base-url', default='https://crypt.cohae.dev/destiny/ps4/packages/latest')
    a = ap.parse_args()

    listed = {
        Path(x.strip()).name
        for x in a.package_list.read_text(errors='replace').splitlines()
        if x.strip()
    }
    expected_names = {x[0] for x in MEMBERS}
    if len(expected_names) != 24:
        raise SystemExit(f'internal Tower map/activity root member count is {len(expected_names)}, expected 24')

    current = {
        i: sorted(n for n in listed if pkg_id(n) == i)
        for i in FAMILY_IDS
    }
    expected = {
        i: sorted(n for n in expected_names if pkg_id(n) == i)
        for i in FAMILY_IDS
    }
    mismatch = {
        i: {'expected': expected[i], 'current': current[i]}
        for i in sorted(FAMILY_IDS) if expected[i] != current[i]
    }
    if mismatch:
        raise SystemExit('current Tower map/activity root family membership changed: ' + json.dumps(mismatch, indent=2))

    a.out_dir.mkdir(parents=True, exist_ok=True)
    arc = SplitHttpTar(
        [f'{a.base_url}/packages.tar.{i:03d}' for i in range(1, 11)],
        retries=6,
        timeout=120,
    )
    rows = []
    for name, offset, size, expected_sha in MEMBERS:
        dst = a.out_dir / name
        got = arc.copy_to(offset, size, dst)
        if got.lower() != expected_sha.lower():
            raise SystemExit(f'{name}: SHA mismatch {got} != {expected_sha}')
        rows.append({
            'name': name,
            'package_id': pkg_id(name),
            'data_offset': offset,
            'size': size,
            'sha256': got,
            'sha_pinned': True,
        })
        print('RECOVERED_MAP_ACTIVITY_ROOT', name, size, got, flush=True)

    report = {
        'schema_version': 1,
        'status': 'D1_TOWER_MAP_ACTIVITY_ROOT_CORPUS_SHA256_VERIFIED',
        'package_ids': sorted(FAMILY_IDS),
        'member_count': len(rows),
        'family_membership': current,
        'members': rows,
        'policy': (
            'Physical world-root corpus only. No semantic ownership is inferred from '
            'the filenames or package IDs. Activity/Bubble/MapContainer/Table parsers '
            'must select the world from serialized current-class references.'
        ),
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + '\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
