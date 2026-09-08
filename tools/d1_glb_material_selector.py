#!/usr/bin/env python3
"""Extract exact D1 material TagHashes referenced by a GLB.

This is intentionally a thin adapter: material identity is recovered from the
existing D1/Tiger material names and emitted as a destination-neutral selector
for source package/render-state closure.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from d1_gltf_layer_merge import read_glb

MAT_RE = re.compile(r'(?:TigerMaterial_|D1_)([0-9A-Fa-f]{8})')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--input-glb', type=Path, required=True)
    ap.add_argument('-o', '--out', type=Path, required=True)
    a = ap.parse_args()

    doc, _ = read_glb(a.input_glb)
    mats = {}
    unresolved = []
    for i, m in enumerate(doc.get('materials') or []):
        name = str(m.get('name') or '')
        mm = MAT_RE.search(name)
        if mm:
            h = mm.group(1).upper()
            mats.setdefault(h, {'visual': True, 'material_indices': []})['material_indices'].append(i)
        else:
            unresolved.append({'material_index': i, 'name': name})

    if not mats:
        raise SystemExit('no D1 material hashes found in GLB')

    out = {
        'schema_version': 1,
        'status': 'D1_GLB_MATERIAL_SELECTOR_COMPLETE',
        'input_glb': str(a.input_glb),
        'gltf_material_count': len(doc.get('materials') or []),
        'd1_material_count': len(mats),
        'materials': dict(sorted(mats.items())),
        'unresolved_non_d1_materials': unresolved,
        'policy': 'D1 material identity only; no appearance or shader semantics inferred from glTF.',
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in ('status','gltf_material_count','d1_material_count')}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
