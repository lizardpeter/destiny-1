#!/usr/bin/env python3
"""Strict-JSON adapter for the Tower actor production assembly manifest.

The upstream location/visual join intentionally preserves a D1 Vector4 location
record whose fourth lane is an unused non-finite sentinel. The production
assembly only consumes XYZ for placement, but the v1 manifest also carries the
ambiguous-group rows as diagnostic metadata. This adapter replaces only that
unused diagnostic location[3] sentinel with JSON null, validates that every
placement XYZ remains finite, then delegates all production logic to the pinned
v1 assembler unchanged.
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--location-visual-join', type=Path, required=True)
    ap.add_argument('--action-compatibility', type=Path, required=True)
    ap.add_argument('--visual-checkpoint', type=Path, required=True)
    ap.add_argument('-o', '--out', type=Path, required=True)
    a = ap.parse_args()

    loc = json.loads(a.location_visual_join.read_text())
    rows = loc.get('ambiguous_location_groups_with_spawned_actor_overlap') or []
    replaced = 0
    for i, row in enumerate(rows):
        location = row.get('location')
        if not isinstance(location, list) or len(location) < 3:
            raise SystemExit(f'ambiguous row {i}: malformed location')
        xyz = [float(v) for v in location[:3]]
        if not all(math.isfinite(v) for v in xyz):
            raise SystemExit(f'ambiguous row {i}: non-finite placement XYZ')
        if len(location) >= 4:
            try:
                w = float(location[3])
            except (TypeError, ValueError):
                if location[3] is not None:
                    raise SystemExit(f'ambiguous row {i}: invalid diagnostic W lane')
            else:
                if not math.isfinite(w):
                    location[3] = None
                    replaced += 1

    if replaced != 61:
        raise SystemExit(f'expected 61 D1 diagnostic W sentinels, replaced {replaced}')

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

    # Re-serialize strictly once more as a final no-NaN canary.
    a.out.write_text(json.dumps(out, indent=2, allow_nan=False) + '\n')
    print(json.dumps({
        'status': 'D1_TOWER_ACTOR_PRODUCTION_ASSEMBLY_MANIFEST_V2_STRICT_COMPLETE',
        'diagnostic_location_w_sentinels_replaced_with_null': replaced,
        'placement_alternative_count': out['placement_alternative_count'],
        'used_visual_variant_count': out['used_visual_variant_count'],
        'shared_action_library_count': out['shared_action_library_count'],
    }, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
