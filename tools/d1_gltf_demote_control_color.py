#!/usr/bin/env python3
"""Demote source D1 COLOR_0 to a custom glTF control attribute for selected materials.

D1 static vertex streams frequently serialize a field that source readers call
COLOR/RGBA8, but native shaders are free to consume those components as arbitrary
blend/material controls.  glTF COLOR_0 has a stronger semantic contract: the
metallic-roughness material path multiplies base color and alpha by COLOR_0.

For shader families where portable colour modulation has not been proven, this
adapter losslessly renames the primitive attribute from COLOR_0 to _D1_COLOR.
The accessor, bufferView and binary bytes are untouched.  This preserves the exact
normalized RGBA8 source control vector while preventing generic PBR viewers from
silently changing appearance.

No material is selected by appearance.  Callers must provide exact material hashes
whose native dataflow established non-portable control use.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

MAGIC = 0x46546C67
JSON_CHUNK = 0x4E4F534A
BIN_CHUNK = 0x004E4942
MAT_RE = re.compile(r'(?:TigerMaterial_|D1_)([0-9A-Fa-f]{8})')


def norm(x: str) -> str:
    return x.upper().removeprefix('0X').zfill(8)


def read_glb(path: Path) -> tuple[dict, bytes, bytes]:
    b = path.read_bytes()
    if len(b) < 20:
        raise ValueError('GLB too short')
    magic, version, total = struct.unpack_from('<III', b, 0)
    if magic != MAGIC or version != 2 or total != len(b):
        raise ValueError('invalid GLB v2 header')
    o = 12
    chunks = []
    while o < len(b):
        if o + 8 > len(b):
            raise ValueError('truncated GLB chunk header')
        n, typ = struct.unpack_from('<II', b, o)
        o += 8
        if o + n > len(b):
            raise ValueError('truncated GLB chunk')
        chunks.append((typ, b[o:o+n]))
        o += n
    if not chunks or chunks[0][0] != JSON_CHUNK:
        raise ValueError('first GLB chunk is not JSON')
    if len(chunks) != 2 or chunks[1][0] != BIN_CHUNK:
        raise ValueError('adapter currently requires exactly JSON + BIN chunks')
    doc = json.loads(chunks[0][1].rstrip(b' \t\r\n\0').decode('utf-8'))
    return doc, chunks[1][1], b


def write_glb(path: Path, doc: dict, bin_chunk: bytes) -> None:
    jb = json.dumps(doc, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    jb += b' ' * ((-len(jb)) & 3)
    bb = bin_chunk + b'\0' * ((-len(bin_chunk)) & 3)
    total = 12 + 8 + len(jb) + 8 + len(bb)
    out = bytearray(struct.pack('<III', MAGIC, 2, total))
    out += struct.pack('<II', len(jb), JSON_CHUNK) + jb
    out += struct.pack('<II', len(bb), BIN_CHUNK) + bb
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(out)


def material_hash(doc: dict, idx: int | None) -> str | None:
    if idx is None:
        return None
    mats = doc.get('materials') or []
    if idx < 0 or idx >= len(mats):
        return None
    name = str(mats[idx].get('name') or '')
    m = MAT_RE.search(name)
    return m.group(1).upper() if m else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--input-glb', type=Path, required=True)
    ap.add_argument('--material', action='append', required=True,
                    help='exact D1 material hash whose COLOR_0 is shader-control data')
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    a = ap.parse_args()
    selected = {norm(x) for x in a.material}

    doc, bin_chunk, source_bytes = read_glb(a.input_glb)
    source_bin_sha = hashlib.sha256(bin_chunk).hexdigest()
    changed = []
    matched_materials = set()
    for mi, mesh in enumerate(doc.get('meshes') or []):
        for pi, prim in enumerate(mesh.get('primitives') or []):
            mh = material_hash(doc, prim.get('material'))
            if mh not in selected:
                continue
            matched_materials.add(mh)
            attrs = prim.setdefault('attributes', {})
            if 'COLOR_0' not in attrs:
                changed.append({'mesh': mi, 'primitive': pi, 'material': mh,
                                'status': 'selected_but_COLOR_0_absent'})
                continue
            if '_D1_COLOR' in attrs:
                raise ValueError(f'mesh {mi} primitive {pi} already has _D1_COLOR')
            accessor = attrs.pop('COLOR_0')
            attrs['_D1_COLOR'] = accessor
            changed.append({'mesh': mi, 'primitive': pi, 'material': mh,
                            'status': 'COLOR_0_RENAMED_TO_D1_COLOR', 'accessor': accessor})

    missing = sorted(selected - matched_materials)
    if missing:
        raise SystemExit(f'selected material(s) absent from GLB: {missing}')
    renamed = [x for x in changed if x['status'] == 'COLOR_0_RENAMED_TO_D1_COLOR']
    if not renamed:
        raise SystemExit('no selected COLOR_0 attributes were renamed')

    doc.setdefault('asset', {}).setdefault('extras', {})['d1ControlColorAdapter'] = {
        'status': 'D1_CONTROL_COLOR_CUSTOM_ATTRIBUTE',
        'attribute': '_D1_COLOR',
        'materials': sorted(selected),
        'renamedPrimitiveCount': len(renamed),
        'policy': 'Exact source accessor preserved; portable PBR COLOR_0 semantics intentionally withheld because native D1 shader control use is proven.'
    }
    write_glb(a.out, doc, bin_chunk)
    check_doc, check_bin, _ = read_glb(a.out)
    if hashlib.sha256(check_bin).hexdigest() != source_bin_sha:
        raise SystemExit('BIN chunk changed')

    report = {
        'schema_version': 1,
        'status': 'D1_GLTF_CONTROL_COLOR_DEMOTION_COMPLETE',
        'input_glb': str(a.input_glb),
        'input_sha256': hashlib.sha256(source_bytes).hexdigest(),
        'output_glb': str(a.out),
        'output_sha256': hashlib.sha256(a.out.read_bytes()).hexdigest(),
        'input_bin_sha256': source_bin_sha,
        'output_bin_sha256': hashlib.sha256(check_bin).hexdigest(),
        'bin_byte_identical': check_bin == bin_chunk,
        'selected_materials': sorted(selected),
        'renamed_primitive_count': len(renamed),
        'changes': changed,
        'policy': 'Only exact caller-selected D1 materials are modified. COLOR_0 accessor identity and binary data are preserved byte-for-byte as _D1_COLOR; no visual semantic is guessed.'
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
