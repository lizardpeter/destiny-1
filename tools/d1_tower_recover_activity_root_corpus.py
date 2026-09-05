#!/usr/bin/env python3
"""Recover the exact D1 Tower Activity/Bubble root package generations.

These 12 physical members were recovered and SHA-256 verified by successful workflow
run 33945026693 (`D1 Tower map-entry resource chain resolution`, commit
4b8a9c4c225f49d7c59d42bee13af3b40561cf6a). The artifact digest was:

  sha256:daf9aadd23c5c2c5bf59f07025d7074401fd2a069643e476175abe754bd5a7a4

They are the missing 023D activity and 0244 ambient-activity generations needed above
the already pinned 024C/0250 Tower destination corpus. This script performs physical
recovery only. It does NOT infer map ownership from the filenames; semantic ownership is
resolved later from current D1 Activity/Bubble/MapContainer classes.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from d1_split_tar_extract import SplitHttpTar

SOURCE_WORKFLOW_RUN = 33945026693
SOURCE_COMMIT = '4b8a9c4c225f49d7c59d42bee13af3b40561cf6a'
SOURCE_ARTIFACT_DIGEST = 'sha256:daf9aadd23c5c2c5bf59f07025d7074401fd2a069643e476175abe754bd5a7a4'

MEMBERS = [
    ('ps4_city_tower_activities_act_023d_0.pkg', 5321093120, 1544192, 'a69fc58b6692ac55e08da03c2364058351fbb85db8e06387a28de3cf4748a076'),
    ('ps4_city_tower_activities_act_023d_1.pkg', 5322637824, 835584, '7386776a514488b2ee89fb3259aaa79f1bdaab3991181ea2bd423ab893bfc0f5'),
    ('ps4_city_tower_activities_act_023d_2.pkg', 5323473920, 49981440, '6c51c45edcefcfc4954d0adcbe4c84b17d67c02a5d39512639987063880118f0'),
    ('ps4_city_tower_activities_act_023d_3.pkg', 5373455872, 4132864, '71fe16c95cdaa4dc4119f75c34a3af2ace7798819460f97fa1656624782170b3'),
    ('ps4_city_tower_activities_act_023d_4.pkg', 5377589248, 42117120, 'ec698392d37149c03d678dbd8605d66a36084bea4b41d77c7daef7894b1526a9'),
    ('ps4_city_tower_activities_act_023d_5.pkg', 5419706880, 131072, 'de0a2e4052602d26184d9f739678a0805b8cb8272f3758204700e1687cb55695'),
    ('ps4_city_tower_ambient_activi_0244_0.pkg', 5643446272, 46385152, 'cf483101913c7f640b85679216075dad5d1292c001430bc6b9e066d3e6fa29dd'),
    ('ps4_city_tower_ambient_activi_0244_1.pkg', 5689831936, 19652608, '9acf40811494a8d33afd2f1094d0b658b59dc22f8bb0dc84863e481f5f095af3'),
    ('ps4_city_tower_ambient_activi_0244_2.pkg', 5709485056, 892928, '61eb14b4d3e1cc3bce10917a1a750117c34b758fcc456aeebc90ad2949f0ec2e'),
    ('ps4_city_tower_ambient_activi_0244_3.pkg', 5710378496, 92160, 'bd34e7681b87d79e7f88335741f6189ab0c09100132e84c0af8df9c7c6cf6c19'),
    ('ps4_city_tower_ambient_activi_0244_4.pkg', 5710471168, 108544, '06e431d8c54cba3d03dd55b18661aa484e5cb9beb8c364a8088460929d431a14'),
    ('ps4_city_tower_ambient_activi_0244_5.pkg', 5710580224, 110592, '1537bc62b74f19065c7e1416e3a7eb2b49429f6458024f716ecb255e871f93bf'),
]


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
    expected = {x[0] for x in MEMBERS}
    missing_from_current = sorted(expected - listed)
    if missing_from_current:
        raise SystemExit('pinned Tower activity-root members missing from current package list: ' + json.dumps(missing_from_current))

    # Fail if the current 023D/0244 generation membership differs from the pinned set.
    current_family = sorted(
        n for n in listed
        if n.startswith('ps4_city_tower_activities_act_023d_')
        or n.startswith('ps4_city_tower_ambient_activi_0244_')
    )
    if current_family != sorted(expected):
        raise SystemExit('current Tower Activity root family membership changed: ' + json.dumps({
            'expected': sorted(expected), 'current': current_family
        }, indent=2))

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
            'data_offset': offset,
            'size': size,
            'sha256': got,
            'sha_pinned': True,
        })
        print('RECOVERED_ACTIVITY_ROOT', name, size, got, flush=True)

    report = {
        'schema_version': 1,
        'status': 'D1_TOWER_ACTIVITY_ROOT_CORPUS_SHA256_VERIFIED',
        'source_workflow_run': SOURCE_WORKFLOW_RUN,
        'source_commit': SOURCE_COMMIT,
        'source_artifact_digest': SOURCE_ARTIFACT_DIGEST,
        'member_count': len(rows),
        'members': rows,
        'policy': (
            'This is only a reproducible physical package fixture. Semantic world '
            'ownership is discovered later from SActivity_ROI -> SBubbleDefinition -> '
            'SMapContainer -> SMapDataTable serialized references.'
        ),
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + '\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
