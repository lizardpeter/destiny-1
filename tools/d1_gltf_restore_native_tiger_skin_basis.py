#!/usr/bin/env python3
"""Restore glTF skin bind data from parser space to native D1/Tiger model space.

The pinned tiger-animation-parser intentionally maps raw Tiger coordinates

    [x, y, z] -> [y, z, x]

when reading skeleton transforms. That conversion is useful for the parser's own
standalone export path, but D1 model geometry emitted by this repository remains in
native D1 local/model coordinates until the world-placement adapter is applied.
Using parser-space joint TRS/IBMs directly on native-D1 geometry therefore mixes two
coordinate bases while still being capable of satisfying formal bind identity.

This adapter performs the exact inverse basis conjugation on every skin in a GLB:
  * every joint local transform;
  * every inverseBindMatrix accessor.

It deliberately does not touch mesh positions, indices, JOINTS_0, WEIGHTS_0,
materials, textures, node-to-mesh assignment, or world placement. Animation data is
also left untouched; animated files must convert parser-retargeted output tracks by
the same basis before use.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.spatial.transform import Rotation

from d1_gltf_layer_merge import read_glb, write_glb
from d1_gltf_skin_bind_identity_probe import accessor, node_local

# parser p = P @ native, where p = [native_y, native_z, native_x]
P = np.array([
    [0.0, 1.0, 0.0, 0.0],
    [0.0, 0.0, 1.0, 0.0],
    [1.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 1.0],
], dtype=np.float64)
PI = P.T
FLOAT = 5126


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def parser_to_native_matrix(m: np.ndarray) -> np.ndarray:
    return PI @ np.asarray(m, dtype=np.float64) @ P


def decompose(m: np.ndarray):
    t = m[:3, 3].copy()
    a = m[:3, :3].copy()
    scale = np.linalg.norm(a, axis=0)
    if np.any(scale < 1e-12):
        raise ValueError('zero scale during native-Tiger basis restoration')
    r = a / scale
    if np.linalg.det(r) < 0:
        k = int(np.argmax(scale))
        scale[k] *= -1.0
        r[:, k] *= -1.0
    q = Rotation.from_matrix(r).as_quat()
    return t, q, scale


def set_float_accessor(doc: dict, blob: bytearray, accessor_index: int, data: np.ndarray) -> None:
    a = doc['accessors'][accessor_index]
    if int(a['componentType']) != FLOAT:
        raise ValueError(f'accessor {accessor_index}: inverse bind accessor is not FLOAT')
    if a['type'] != 'MAT4':
        raise ValueError(f'accessor {accessor_index}: expected MAT4, got {a["type"]}')
    bv = doc['bufferViews'][a['bufferView']]
    count = int(a['count'])
    x = np.asarray(data, dtype='<f4')
    if x.shape != (count, 4, 4):
        raise ValueError(f'accessor {accessor_index}: matrix shape {x.shape} != {(count,4,4)}')
    flat = np.stack([m.reshape(16, order='F') for m in x], axis=0)
    base = int(bv.get('byteOffset', 0)) + int(a.get('byteOffset', 0))
    stride = int(bv.get('byteStride', 64))
    if stride < 64:
        raise ValueError(f'accessor {accessor_index}: invalid MAT4 byteStride {stride}')
    if stride == 64:
        raw = flat.astype('<f4', copy=False).tobytes(order='C')
        blob[base:base + len(raw)] = raw
    else:
        for i, row in enumerate(flat):
            blob[base + i * stride:base + i * stride + 64] = row.astype('<f4').tobytes()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('input_glb', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    args = ap.parse_args()

    doc, binary = read_glb(args.input_glb)
    skins = doc.get('skins', [])
    nodes = doc.get('nodes', [])
    if not skins:
        raise SystemExit('input GLB has no skins')
    if doc.get('animations'):
        raise SystemExit('skin-only basis adapter refuses animated GLBs; convert animation tracks by the same basis explicitly')

    blob = bytearray(binary)
    joint_nodes = set()
    ibm_accessors = set()
    skin_rows = []
    for si, skin in enumerate(skins):
        joints = [int(x) for x in skin.get('joints', [])]
        ibm = skin.get('inverseBindMatrices')
        if not joints or ibm is None:
            raise ValueError(f'skin {si}: missing joints or inverseBindMatrices')
        for j in joints:
            if not 0 <= j < len(nodes):
                raise ValueError(f'skin {si}: joint node {j} out of range')
        joint_nodes.update(joints)
        ibm_accessors.add(int(ibm))
        root = skin.get('skeleton')
        root_extras = nodes[int(root)].get('extras', {}) if root is not None else {}
        skin_rows.append({
            'skin_index': si,
            'name': skin.get('name'),
            'joint_count': len(joints),
            'inverse_bind_accessor': int(ibm),
            'skeleton_root': root,
            'model': str(root_extras.get('d1Model', '')).upper() or None,
            'skeleton': str(root_extras.get('d1Skeleton', '')).upper() or None,
            'runtime_rig': str(root_extras.get('d1RuntimeRig', '')).upper() or None,
        })

    # Convert joint local transforms by basis conjugation. Shared joints are converted once.
    for ji in sorted(joint_nodes):
        native = parser_to_native_matrix(node_local(nodes[ji]))
        t, q, s = decompose(native)
        node = nodes[ji]
        node.pop('matrix', None)
        node['translation'] = [float(x) for x in t]
        node['rotation'] = [float(x) for x in q]
        node['scale'] = [float(x) for x in s]

    # The inverse-bind mathematical matrices require the same conjugation.
    for ai in sorted(ibm_accessors):
        mats = accessor(doc, binary, ai).astype(np.float64)
        if mats.ndim != 3 or mats.shape[1:] != (4, 4):
            raise ValueError(f'inverse bind accessor {ai}: unexpected shape {mats.shape}')
        converted = np.stack([parser_to_native_matrix(m) for m in mats], axis=0)
        set_float_accessor(doc, blob, ai, converted)

    asset = doc.setdefault('asset', {'version': '2.0'})
    extras = asset.setdefault('extras', {})
    extras['d1NativeTigerSkinBasis'] = {
        'sourceParserBasis': '[x,y,z] -> [y,z,x]',
        'restoredBasis': 'native D1/Tiger [x,y,z]',
        'skinCount': len(skins),
        'jointNodeCount': len(joint_nodes),
        'inverseBindAccessorCount': len(ibm_accessors),
        'meshVertexDataChanged': False,
        'jointIndicesChanged': False,
        'weightsChanged': False,
        'materialsChanged': False,
        'animationsPresent': False,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    write_glb(args.out, doc, bytes(blob))
    out_doc, out_binary = read_glb(args.out)
    if len(out_binary) != len(binary):
        raise ValueError(f'BIN byte length changed {len(binary)} -> {len(out_binary)}')
    if len(out_doc.get('meshes', [])) != len(doc.get('meshes', [])):
        raise ValueError('mesh count changed')
    if len(out_doc.get('skins', [])) != len(skins):
        raise ValueError('skin count changed')

    report = {
        'schema_version': 1,
        'status': 'D1_GLTF_NATIVE_TIGER_SKIN_BASIS_RESTORED',
        'input': str(args.input_glb),
        'input_sha256': sha256_file(args.input_glb),
        'output': str(args.out),
        'output_sha256': sha256_file(args.out),
        'output_bytes': args.out.stat().st_size,
        'skin_count': len(skins),
        'joint_node_count': len(joint_nodes),
        'inverse_bind_accessor_count': len(ibm_accessors),
        'binary_byte_length_unchanged': len(out_binary) == len(binary),
        'skins': skin_rows,
        'parser_basis_unapplied': True,
        'restored_basis': 'native D1/Tiger [x,y,z]',
        'policy': (
            'The pinned animation parser maps raw Tiger [x,y,z] to [y,z,x]. '
            'Repository model geometry remains native D1 local space. This adapter '
            'converts only joint bind TRS and inverse-bind matrices back to native D1. '
            'Mesh positions, indices, JOINTS_0, WEIGHTS_0, materials and placements are unchanged.'
        ),
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({
        k: report[k] for k in (
            'status','output_bytes','output_sha256','skin_count','joint_node_count',
            'inverse_bind_accessor_count','binary_byte_length_unchanged','restored_basis'
        )
    }, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
