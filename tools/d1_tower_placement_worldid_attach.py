#!/usr/bin/env python3
"""Attach source-typed SMapDataEntry identity/transform fields to Tower permutation rows.

The existing placement-permutation corpus deliberately stopped at S152 configuration
and model-switch-bank correspondence.  For placement-aware visual export we also need
a lossless join key back to the runtime Activity placement set.  D1 SMapDataEntry is
source-pinned at 0x90 bytes with:

  +0x00 EntitySK FileHash
  +0x20 Rotation XYZW Vector4
  +0x30 Translation Vector4
  +0x80 WorldID u64

This adapter re-reads the exact SD912 owner payload and validates the SMapDataEntry
class marker/entity before attaching WorldID and transform.  It does not change or
promote any material-selection semantics.
"""
from __future__ import annotations

import argparse, json, math, struct, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_split_tar_extract import SplitHttpTar

SD912 = '808012D9'
SMAP = 0x80800406
SMAP_SIZE = 0x90


def norm(x):
    return str(x).upper().removeprefix('0X').zfill(8)


def u32(b, o):
    return struct.unpack_from('<I', b, o)[0]


def u64(b, o):
    return struct.unpack_from('<Q', b, o)[0]


def f4(b, o):
    return list(struct.unpack_from('<4f', b, o))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--calibration', type=Path, required=True)
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    src = json.loads(a.calibration.read_text())
    violations = []
    if src.get('status') != 'D1_TOWER_PLACEMENT_PERMUTATION_CROSS_ENTITY_CALIBRATION':
        violations.append('upstream_calibration_not_green')
    if src.get('violations'):
        violations.append('upstream_calibration_has_violations')

    cats = load_catalogs(a.member_catalog)
    arc = SplitHttpTar(
        [f'{a.base_url.rstrip("/")}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)],
        retries=6, timeout=90,
    )
    c = RemoteCorpus(arc, cats, a.runtime)

    owner_cache = {}
    rows = []
    for i, raw in enumerate(src.get('calibration_rows', [])):
        row = dict(raw)
        owner = norm(row.get('owner'))
        off = int(row.get('smap_offset', -1))
        try:
            if owner not in owner_cache:
                meta = c.entry_meta(owner)
                payload, source = c.payload(owner)
                if meta is None or payload is None:
                    raise ValueError('owner payload unavailable')
                if norm(meta.get('reference', '0')) != SD912:
                    raise ValueError(f'owner class {meta.get("reference")} != {SD912}')
                owner_cache[owner] = (payload, source)
            b, source = owner_cache[owner]
            if off < 4 or off + SMAP_SIZE > len(b):
                raise ValueError(f'SMapDataEntry OOB 0x{off:X}')
            if u32(b, off - 4) != SMAP:
                raise ValueError(f'SMapDataEntry class marker mismatch at 0x{off-4:X}')
            entity = f'{u32(b, off):08X}'
            if entity != norm(row.get('entity_hash')):
                raise ValueError(f'entity mismatch {entity}!={norm(row.get("entity_hash"))}')
            rot = f4(b, off + 0x20)
            tr = f4(b, off + 0x30)
            if not all(math.isfinite(x) for x in rot + tr):
                raise ValueError('non-finite transform')
            wid = u64(b, off + 0x80)
            row.update({
                'owner_source': source,
                'world_id': wid,
                'world_id_hex': f'{wid:016X}',
                'rotation_xyzw': rot,
                'translation': tr,
            })
        except Exception as ex:
            violations.append(f'row[{i}]/{owner}/0x{off:X}:{ex!r}')
        rows.append(row)

    with_world = sum('world_id_hex' in r for r in rows)
    out = dict(src)
    out['schema'] = 'd1_tower_placement_worldid_attach/v1'
    out['status'] = 'D1_TOWER_PLACEMENT_WORLDID_ATTACH_COMPLETE' if not violations and with_world == len(rows) else 'D1_TOWER_PLACEMENT_WORLDID_ATTACH_PARTIAL'
    out['upstream_schema'] = src.get('schema')
    out['upstream_status'] = src.get('status')
    out['calibration_rows'] = rows
    out['worldid_attached_row_count'] = with_world
    out['unique_world_id_count'] = len({r['world_id_hex'] for r in rows if 'world_id_hex' in r})
    out['proof'] = dict(src.get('proof') or {})
    out['proof']['smap_worldid_and_transform_source_typed'] = True
    out['proof']['material_permutation_consumer_semantics_proven'] = False
    out['proof']['descriptor_A_B_evaluation_semantics_proven'] = False
    out['violations'] = violations
    out['policy'] = (
        'WorldID/rotation/translation are attached only after exact SD912/SMapDataEntry class and entity validation. '
        'This creates a lossless runtime-placement join key only; no material selector/evaluator semantics are promoted.'
    )
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({
        'status': out['status'],
        'row_count': len(rows),
        'worldid_attached_row_count': with_world,
        'unique_world_id_count': out['unique_world_id_count'],
        'violations': violations,
    }, indent=2))
    return 0 if out['status'] == 'D1_TOWER_PLACEMENT_WORLDID_ATTACH_COMPLETE' else 2


if __name__ == '__main__':
    raise SystemExit(main())
