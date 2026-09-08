#!/usr/bin/env python3
"""Strict-JSON adapter for the Tower actor production assembly manifest.

The upstream location/visual join intentionally preserves D1 Vector4 location
records whose fourth lane is an unused non-finite sentinel. Production placement
consumes XYZ only. This adapter replaces only those known location[3] sentinels
with JSON null, validates that every placement XYZ remains finite, then delegates
all production logic to the pinned v1 assembler unchanged.
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path


def normalize_location_rows(loc: dict) -> dict[str, int]:
    specs = (
        ('exact_location_visual_alternatives', 547),
        ('ambiguous_location_groups_with_spawned_actor_overlap', 61),
    )
    counts: dict[str, int] = {}
    for key, expected in specs:
        rows = loc.get(key) or []
        replaced = 0
        for i, row in enumerate(rows):
            location = row.get('location')
            if not isinstance(location, list) or len(location) < 4:
                raise SystemExit(f'{key} row {i}: malformed Vector4 location')
            xyz = [float(v) for v in location[:3]]
            if not all(math.isfinite(v) for v in xyz):
                raise SystemExit(f'{key} row {i}: non-finite placement XYZ')
            try:
                w = float(location[3])
            except (TypeError, ValueError):
                if location[3] is not None:
                    raise SystemExit(f'{key} row {i}: invalid diagnostic W lane')
            else:
                if not math.isfinite(w):
                    location[3] = None
                    replaced += 1
        if replaced != expected:
            raise SystemExit(f'{key}: expected {expected} D1 diagnostic W sentinels, replaced {replaced}')
        counts[key] = replaced
    return counts


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--location-visual-join', type=Path, required=True)
    ap.add_argument('--action-compatibility', type=Path, required=True)
    ap.add_argument('--visual-checkpoint', type=Path, required=True)
    ap.add_argument('-o', '--out', type=Path, required=True)
    a = ap.parse_args()

    loc = json.loads(a.location_visual_join.read_text())
    counts = normalize_location_rows(loc)
    replaced = sum(counts.values())
    if replaced != 608:
        raise SystemExit(f'expected 608 total D1 diagnostic W sentinels, replaced {replaced}')

    with tempfile.TemporaryDirectory(prefix='d1_tower_assembly_v2_') as td:
        strict_loc = Path(td) / 'location_visual_join_strict.json'
        strict_loc.write_text(json.dumps(loc, indent=2, allow_nan=False) + '\n')
        cmd = [
            sys.executable,
            str(Path(__file__).with_name('d1_tower_actor_production_assembly_manifest.py')),
            '--location-visual-join', str(strict_loc),
            '--action-compatibility', str(a.action_compatibility),
            '--visual-checkpoint', str(a.visual_checkpoint),
            '-o', str(a.out),
        ]
        cp = subprocess.run(cmd)
        if cp.returncode != 0:
            return cp.returncode

    out = json.loads(a.out.read_text())
    if out.get('status') != 'D1_TOWER_ACTOR_PRODUCTION_ASSEMBLY_MANIFEST_COMPLETE' or out.get('violations'):
        raise SystemExit('delegated assembly manifest is not green')
    if (out.get('used_visual_variant_count'), out.get('shared_action_library_count'), out.get('placement_alternative_count')) != (29, 6, 547):
        raise SystemExit('delegated assembly counts changed')

    a.out.write_text(json.dumps(out, indent=2, allow_nan=False) + '\n')
    print(json.dumps({
        'status': 'D1_TOWER_ACTOR_PRODUCTION_ASSEMBLY_MANIFEST_V2_STRICT_COMPLETE',
        'diagnostic_location_w_sentinels_replaced_with_null': replaced,
        'breakdown': counts,
        'placement_alternative_count': out['placement_alternative_count'],
        'used_visual_variant_count': out['used_visual_variant_count'],
        'shared_action_library_count': out['shared_action_library_count'],
    }, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
