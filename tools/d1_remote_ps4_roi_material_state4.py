#!/usr/bin/env python3
"""Read the exact four bytes at D1 PS4 ROI Material +0x20.

Charm currently names only the first 16 bits of this window ``Unk20``.  This
probe deliberately preserves the complete four bytes without assigning render
semantics.  It is intended for cross-source correlation with independently
reversed Tiger pipeline-state layouts.

The material must resolve through the exact PS4 ROI Material class 0x80801AD7;
class drift, unavailable payloads, short records, or duplicate/conflicting
payloads fail closed through RemoteCorpus.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_split_tar_extract import SplitHttpTar
from d1_filehash import package_hex

MAT_CLASS = '80801AD7'


def norm(v: object) -> str:
    return str(v).upper().removeprefix('0X').zfill(8)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--material', action='append', required=True)
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    catalogs = load_catalogs(a.member_catalog)
    base = a.base_url.rstrip('/')
    arc = SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    corpus = RemoteCorpus(arc, catalogs, a.runtime)

    rows = []
    violations = []
    for h in sorted({norm(x) for x in a.material}):
        row = {'material': h, 'package_id': package_hex(h), 'violations': []}
        meta = corpus.entry_meta(h)
        row['meta'] = meta
        if meta is None:
            row['violations'].append('material_meta_unavailable')
        elif norm(meta.get('reference', '')) != MAT_CLASS:
            row['violations'].append(f'class_mismatch:{norm(meta.get("reference", ""))}!={MAT_CLASS}')
        else:
            try:
                b, src = corpus.payload(h)
            except Exception as ex:
                b = None
                row['violations'].append('payload:' + repr(ex))
                src = None
            row['payload_source'] = src
            if b is None:
                row['violations'].append('payload_unavailable')
            elif len(b) < 0x24:
                row['violations'].append(f'payload_short:{len(b)}<36')
            else:
                raw = b[0x20:0x24]
                row['payload_bytes'] = len(b)
                row['state4_offset'] = '0x20'
                row['state4_hex'] = raw.hex().upper()
                row['state4_u32_le'] = int.from_bytes(raw, 'little')
                row['lanes_u8'] = list(raw)
                row['lanes_hex'] = [f'{x:02X}' for x in raw]
                row['lane_select7_syntax'] = [
                    {'raw': x, 'selected_low7_if_highbit_set': (x & 0x7F) if (x & 0x80) else None}
                    for x in raw
                ]
        if row['violations']:
            violations.extend(f'{h}:{x}' for x in row['violations'])
        rows.append(row)

    out = {
        'schema': 'd1_remote_ps4_roi_material_state4/v1',
        'status': 'D1_REMOTE_PS4_ROI_MATERIAL_STATE4_COMPLETE' if not violations else 'D1_REMOTE_PS4_ROI_MATERIAL_STATE4_WITH_VIOLATIONS',
        'material_class': MAT_CLASS,
        'material_count': len(rows),
        'rows': rows,
        'violations': violations,
        'policy': (
            'The four bytes at Material +0x20 are preserved exactly. lane_select7_syntax is only a mechanical high-bit/low-seven-bit decomposition and does not assign blend/depth/raster/depth-bias semantics.'
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + '\n')
    print('STATUS', out['status'], 'MATERIALS', len(rows), 'VIOLATIONS', len(violations))
    for r in rows:
        print(r['material'], r.get('state4_hex'), r.get('lanes_hex'))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
