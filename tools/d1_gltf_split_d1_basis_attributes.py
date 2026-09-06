#!/usr/bin/env python3
"""Loss-preserving GLB postprocessor for explicit D1 shader-basis replay.

Existing D1 world GLBs already retain:

* standard ``NORMAL`` containing the decoded source normal xyz;
* custom ``_D1_TANGENT`` containing decoded source tangent xyzw.

For Blender shader-node access we add, without removing either source attribute:

* ``_D1_NORMAL``      -> aliases the exact existing NORMAL accessor;
* ``_D1_TANGENT_XYZ`` -> new float VEC3 copied from _D1_TANGENT.xyz;
* ``_D1_TANGENT_W``   -> new float SCALAR copied from _D1_TANGENT.w.

Positions, indices, UVs, colors, materials, images, textures, nodes, animations and
the original BIN payload remain untouched. New split tangent payloads are appended
after the exact input BIN prefix. No standard glTF TANGENT semantic is created.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import struct

import numpy as np

from d1_gltf_layer_merge import read_glb, write_glb

FLOAT = 5126


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def type_components(t: str) -> int:
    return {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[t]


def decode_float_accessor(doc: dict, bin_data: bytes, ai: int) -> np.ndarray:
    a = doc['accessors'][ai]
    if int(a.get('componentType', -1)) != FLOAT:
        raise ValueError(f'accessor {ai}: expected FLOAT componentType')
    if a.get('sparse'):
        raise ValueError(f'accessor {ai}: sparse accessors are outside this postprocessor scope')
    typ = str(a['type'])
    ncomp = type_components(typ)
    count = int(a['count'])
    bvi = int(a['bufferView'])
    bv = doc['bufferViews'][bvi]
    if int(bv.get('buffer', 0)) != 0:
        raise ValueError(f'accessor {ai}: expected embedded buffer 0')
    base = int(bv.get('byteOffset', 0)) + int(a.get('byteOffset', 0))
    stride = int(bv.get('byteStride', ncomp * 4))
    if stride < ncomp * 4 or stride % 4:
        raise ValueError(f'accessor {ai}: invalid float stride {stride}')
    end = base + (count - 1) * stride + ncomp * 4 if count else base
    if base < 0 or end > len(bin_data):
        raise ValueError(f'accessor {ai}: payload outside BIN')
    if stride == ncomp * 4:
        return np.frombuffer(bin_data, dtype='<f4', count=count * ncomp, offset=base).reshape(count, ncomp).copy()
    out = np.empty((count, ncomp), dtype=np.float32)
    for i in range(count):
        out[i] = np.frombuffer(bin_data, dtype='<f4', count=ncomp, offset=base + i * stride)
    return out


def append_float_accessor(doc: dict, bin_data: bytes, data: np.ndarray, typ: str, name: str) -> tuple[int, bytes]:
    x = np.ascontiguousarray(data, dtype='<f4')
    ncomp = type_components(typ)
    if x.ndim != 2 or x.shape[1] != ncomp:
        raise ValueError(f'{name}: expected Nx{ncomp}, got {x.shape}')
    aligned = (len(bin_data) + 3) & ~3
    if aligned != len(bin_data):
        bin_data += b'\0' * (aligned - len(bin_data))
    raw = x.tobytes(order='C')
    off = len(bin_data)
    bvi = len(doc.setdefault('bufferViews', []))
    doc['bufferViews'].append({
        'buffer': 0,
        'byteOffset': off,
        'byteLength': len(raw),
        'name': name + '_BUFFER',
    })
    ai = len(doc.setdefault('accessors', []))
    mn = x.min(axis=0).tolist() if len(x) else [0.0] * ncomp
    mx = x.max(axis=0).tolist() if len(x) else [0.0] * ncomp
    doc['accessors'].append({
        'bufferView': bvi,
        'byteOffset': 0,
        'componentType': FLOAT,
        'count': int(len(x)),
        'type': typ,
        'min': mn,
        'max': mx,
        'name': name,
    })
    return ai, bin_data + raw


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--input-glb', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    a = ap.parse_args()

    src, src_bin = read_glb(a.input_glb)
    doc = copy.deepcopy(src)
    bin_data = src_bin
    original_counts = {k: len(src.get(k, [])) for k in ('accessors', 'bufferViews', 'meshes', 'nodes', 'materials')}

    split_cache: dict[int, tuple[int, int]] = {}
    primitive_rows = []
    skipped_no_tangent = 0
    w_counts: dict[str, int] = {}

    for mi, mesh in enumerate(doc.get('meshes', [])):
        for pi, prim in enumerate(mesh.get('primitives', [])):
            attrs = prim.get('attributes') or {}
            if '_D1_TANGENT' not in attrs:
                skipped_no_tangent += 1
                continue
            if 'NORMAL' not in attrs:
                raise ValueError(f'mesh {mi} primitive {pi}: _D1_TANGENT exists without NORMAL')
            tai = int(attrs['_D1_TANGENT'])
            nai = int(attrs['NORMAL'])
            tacc = doc['accessors'][tai]
            nacc = doc['accessors'][nai]
            if tacc.get('type') != 'VEC4' or int(tacc.get('componentType', -1)) != FLOAT:
                raise ValueError(f'mesh {mi} primitive {pi}: _D1_TANGENT is not FLOAT VEC4')
            if nacc.get('type') != 'VEC3' or int(nacc.get('componentType', -1)) != FLOAT:
                raise ValueError(f'mesh {mi} primitive {pi}: NORMAL is not FLOAT VEC3')
            if int(tacc['count']) != int(nacc['count']):
                raise ValueError(f'mesh {mi} primitive {pi}: normal/tangent count mismatch')

            if tai not in split_cache:
                full = decode_float_accessor(doc, bin_data, tai)
                xyz = full[:, :3].astype(np.float32, copy=True)
                w = full[:, 3:4].astype(np.float32, copy=True)
                xyz_ai, bin_data = append_float_accessor(doc, bin_data, xyz, 'VEC3', f'D1_TANGENT_XYZ_FROM_{tai}')
                w_ai, bin_data = append_float_accessor(doc, bin_data, w, 'SCALAR', f'D1_TANGENT_W_FROM_{tai}')
                split_cache[tai] = (xyz_ai, w_ai)
                vals, counts = np.unique(w[:, 0], return_counts=True)
                for v, c in zip(vals.tolist(), counts.tolist()):
                    key = f'{float(v):.9g}'
                    w_counts[key] = w_counts.get(key, 0) + int(c)
            xyz_ai, w_ai = split_cache[tai]

            # NORMAL can be referenced by both standard and application-specific
            # semantics with no data duplication.
            attrs['_D1_NORMAL'] = nai
            attrs['_D1_TANGENT_XYZ'] = xyz_ai
            attrs['_D1_TANGENT_W'] = w_ai
            primitive_rows.append({
                'mesh': mi,
                'primitive': pi,
                'normal_accessor': nai,
                'full_tangent_accessor': tai,
                'split_tangent_xyz_accessor': xyz_ai,
                'split_tangent_w_accessor': w_ai,
                'vertex_count': int(tacc['count']),
            })

    if not primitive_rows:
        raise SystemExit('input GLB contained no _D1_TANGENT primitives')

    doc.setdefault('asset', {'version': '2.0'}).setdefault('extras', {})['d1_explicit_shader_basis_attributes'] = {
        'schema_version': 1,
        'normal': '_D1_NORMAL',
        'tangent_xyz': '_D1_TANGENT_XYZ',
        'tangent_w': '_D1_TANGENT_W',
        'full_forensic_tangent': '_D1_TANGENT',
        'standard_gltf_tangent_promoted': False,
        'native_basis_rule': 'Nraw=M*_D1_NORMAL; Traw=M*_D1_TANGENT_XYZ; invN=1/length(Nraw); N=Nraw*invN; T=Traw*invN; B=cross(N,T)*_D1_TANGENT_W',
    }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    write_glb(a.out, doc, bin_data)
    chk, chk_bin = read_glb(a.out)
    if chk_bin[:len(src_bin)] != src_bin:
        raise SystemExit('input BIN is not an exact output prefix')
    # The postprocessor is allowed to alter only mesh primitive attribute maps,
    # append accessors/bufferViews/BIN, and add one asset extra. Core scene identity
    # arrays remain unchanged.
    for k in ('nodes', 'materials', 'images', 'textures', 'samplers', 'animations', 'skins'):
        if chk.get(k, []) != src.get(k, []):
            raise SystemExit(f'input {k} changed')
    if len(chk.get('meshes', [])) != len(src.get('meshes', [])):
        raise SystemExit('mesh count changed')

    report = {
        'schema_version': 1,
        'status': 'D1_GLTF_EXPLICIT_SHADER_BASIS_ATTRIBUTES_ADDED',
        'input_glb': str(a.input_glb),
        'input_sha256': sha256_file(a.input_glb),
        'input_bytes': a.input_glb.stat().st_size,
        'output_glb': str(a.out),
        'output_sha256': sha256_file(a.out),
        'output_bytes': a.out.stat().st_size,
        'input_bin_bytes': len(src_bin),
        'output_bin_bytes': len(chk_bin),
        'input_bin_exact_prefix': True,
        'original_counts': original_counts,
        'final_counts': {k: len(chk.get(k, [])) for k in ('accessors', 'bufferViews', 'meshes', 'nodes', 'materials')},
        'primitives_augmented': len(primitive_rows),
        'unique_full_tangent_accessors_split': len(split_cache),
        'primitives_without_d1_tangent': skipped_no_tangent,
        'tangent_w_counts_over_unique_source_accessors': w_counts,
        'primitives': primitive_rows,
        'policy': 'No standard TANGENT semantic is created. Existing NORMAL and _D1_TANGENT remain authoritative; split application attributes only expose the same source values to Blender nodes.',
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in (
        'status', 'input_bytes', 'output_bytes', 'input_bin_exact_prefix',
        'primitives_augmented', 'unique_full_tangent_accessors_split',
        'tangent_w_counts_over_unique_source_accessors', 'final_counts'
    )}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
