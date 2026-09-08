#!/usr/bin/env python3
"""Decode one or more exact D1 material stage records from a recovered corpus.

Unlike ``d1_material_decode.py`` this tool is package-file agnostic: the caller
provides every recovered snapshot and the material TagHash is resolved through the
corpus.  This makes the output suitable as a stable decoder contract for Blender
and the Rust renderer.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import d1_tower_map_schema_validate_v5 as v5
from d1_material_decode import PS4_MATERIAL_CLASS, parse_material


def norm(x) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', type=Path, action='append', required=True)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--material', action='append', required=True)
    ap.add_argument('-o', '--out', type=Path, required=True)
    a = ap.parse_args()

    c = v5.v3.base.Corpus([p.resolve() for p in a.snapshot], a.runtime.resolve())
    rows = []
    violations = []
    for h in sorted({norm(x) for x in a.material}):
        row = {'material': h, 'violations': []}
        meta = c.entry_meta(h)
        row['meta'] = meta
        payload, source = c.payload(h)
        row['source'] = source
        if meta is None:
            row['violations'].append('entry_meta_unavailable')
        elif norm(meta.get('reference', '')) != PS4_MATERIAL_CLASS:
            row['violations'].append(f"resource_class:{norm(meta.get('reference',''))}!={PS4_MATERIAL_CLASS}")
        if payload is None:
            row['violations'].append('payload_unavailable')
        else:
            row['payload_bytes'] = len(payload)
            row['payload_sha256'] = hashlib.sha256(payload).hexdigest()
            try:
                row['stage'] = parse_material(payload, 'PS4')
            except Exception as ex:
                row['violations'].append('parse_material:' + repr(ex))
        if row['violations']:
            violations.extend(f"{h}:{x}" for x in row['violations'])
        rows.append(row)

    out = {
        'schema_version': 1,
        'status': 'D1_CORPUS_MATERIAL_STAGE_EXACT' if not violations else 'D1_CORPUS_MATERIAL_STAGE_PARTIAL',
        'material_count': len(rows),
        'materials': rows,
        'violations': violations,
        'policy': 'Exact retail material payload and source-closed D1 ROI stage layout only. Texture role, shader dataflow, blend equation, and sampler semantics remain separate proof layers.',
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({
        'status': out['status'],
        'material_count': len(rows),
        'materials': [{
            'material': r['material'],
            'vertex_shader': (r.get('stage') or {}).get('vertex_shader'),
            'pixel_shader': (r.get('stage') or {}).get('pixel_shader'),
            'vs_texture_count': ((r.get('stage') or {}).get('vs_textures') or {}).get('count'),
            'ps_texture_count': ((r.get('stage') or {}).get('ps_textures') or {}).get('count'),
            'unk20_hex': (r.get('stage') or {}).get('unk20_hex'),
            'violations': r['violations'],
        } for r in rows],
    }, indent=2))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
