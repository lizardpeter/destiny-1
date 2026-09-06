#!/usr/bin/env python3
"""Remap mesh geometry from native Destiny/Tiger basis into the glTF skeleton basis.

D1 mesh positions decoded by this repository are still in Tiger coordinates:
    Z-up, X-forward, Y-right.

The animation parser used by the Guardian rig path explicitly converts Tiger to
its Three.js/glTF basis as:
    [x, y, z] -> [y, z, x]

Attaching that converted skeleton/animation to unconverted Tiger mesh positions
is structurally valid glTF but visually wrong as soon as the armature evaluates:
vertices rotate about bone pivots expressed in a different coordinate basis.
This post-process remaps POSITION, NORMAL, and TANGENT data into the exact same
basis as the decoded D1 skeleton and animation, without changing joints, weights,
inverse-bind matrices, animation tracks, materials, UVs, or node indices.

The pass fails closed on sparse/non-float accessors or non-identity mesh-node
transforms so it cannot silently double-apply or partially apply a basis change.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from pygltflib import GLTF2, Accessor, BufferView

FLOAT = 5126
ARRAY_BUFFER = 34962


def align4(blob: bytearray) -> None:
    while len(blob) & 3:
        blob.append(0)


def append_accessor(g: GLTF2, blob: bytearray, data: np.ndarray, accessor_type: str, *, with_minmax: bool = False) -> int:
    data = np.asarray(data, dtype='<f4')
    align4(blob)
    off = len(blob)
    raw = data.tobytes(order='C')
    blob.extend(raw)
    vi = len(g.bufferViews)
    g.bufferViews.append(BufferView(buffer=0, byteOffset=off, byteLength=len(raw), target=ARRAY_BUFFER))
    a = Accessor(bufferView=vi, byteOffset=0, componentType=FLOAT, count=int(data.shape[0]), type=accessor_type)
    if with_minmax:
        a.min = [float(x) for x in np.min(data, axis=0)]
        a.max = [float(x) for x in np.max(data, axis=0)]
    ai = len(g.accessors)
    g.accessors.append(a)
    return ai


def read_float_accessor(g: GLTF2, blob: bytes | bytearray, accessor_index: int, width: int) -> np.ndarray:
    a = g.accessors[accessor_index]
    if a.sparse is not None:
        raise ValueError(f'accessor {accessor_index}: sparse accessor unsupported for basis remap')
    if a.componentType != FLOAT:
        raise ValueError(f'accessor {accessor_index}: componentType {a.componentType} is not FLOAT')
    if a.normalized:
        raise ValueError(f'accessor {accessor_index}: normalized float accessor is unexpected')
    expected_type = f'VEC{width}'
    if a.type != expected_type:
        raise ValueError(f'accessor {accessor_index}: type {a.type} != {expected_type}')
    v = g.bufferViews[a.bufferView]
    if v.buffer != 0:
        raise ValueError(f'accessor {accessor_index}: expected buffer 0, got {v.buffer}')
    start = int(v.byteOffset or 0) + int(a.byteOffset or 0)
    item_bytes = width * 4
    stride = int(v.byteStride or item_bytes)
    if stride < item_bytes:
        raise ValueError(f'accessor {accessor_index}: byteStride {stride} < item size {item_bytes}')
    out = np.empty((int(a.count), width), dtype='<f4')
    if stride == item_bytes:
        raw = np.frombuffer(blob, dtype='<f4', count=int(a.count) * width, offset=start)
        out[:] = raw.reshape((-1, width))
    else:
        for i in range(int(a.count)):
            out[i] = np.frombuffer(blob, dtype='<f4', count=width, offset=start + i * stride)
    return out


def node_is_identity(n) -> bool:
    if n.matrix is not None:
        m = np.asarray(n.matrix, dtype=np.float64).reshape((4, 4), order='F')
        if not np.allclose(m, np.eye(4), atol=1e-7):
            return False
    if n.translation is not None and not np.allclose(n.translation, [0, 0, 0], atol=1e-7):
        return False
    if n.rotation is not None and not np.allclose(n.rotation, [0, 0, 0, 1], atol=1e-7):
        return False
    if n.scale is not None and not np.allclose(n.scale, [1, 1, 1], atol=1e-7):
        return False
    return True


def bounds(rows: list[np.ndarray]) -> dict | None:
    if not rows:
        return None
    lo = np.min(np.vstack([np.min(x, axis=0) for x in rows]), axis=0)
    hi = np.max(np.vstack([np.max(x, axis=0) for x in rows]), axis=0)
    return {'min': [float(x) for x in lo], 'max': [float(x) for x in hi]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('input_glb', type=Path)
    ap.add_argument('-o', '--output', type=Path, required=True)
    ap.add_argument('--json', type=Path)
    a = ap.parse_args()

    g = GLTF2().load_binary(str(a.input_glb))
    if len(g.buffers or []) != 1:
        raise ValueError(f'expected exactly one GLB buffer, got {len(g.buffers or [])}')
    blob = bytearray(g.binary_blob() or b'')

    bad_nodes = []
    for ni, n in enumerate(g.nodes or []):
        if n.mesh is not None and not node_is_identity(n):
            bad_nodes.append({'node_index': ni, 'name': n.name, 'mesh': n.mesh})
    if bad_nodes:
        raise ValueError(f'non-identity mesh nodes make basis remap ambiguous: {bad_nodes[:8]}')

    pos_cache: dict[int, int] = {}
    norm_cache: dict[int, int] = {}
    tan_cache: dict[int, int] = {}
    before_positions: list[np.ndarray] = []
    after_positions: list[np.ndarray] = []
    primitive_count = 0

    for mi, mesh in enumerate(g.meshes or []):
        for pi, prim in enumerate(mesh.primitives or []):
            primitive_count += 1
            if prim.targets:
                raise ValueError(f'mesh {mi} primitive {pi}: morph targets are not supported by this basis pass')

            pa = prim.attributes.POSITION
            if pa is None:
                raise ValueError(f'mesh {mi} primitive {pi}: missing POSITION')
            if pa not in pos_cache:
                p = read_float_accessor(g, blob, pa, 3)
                q = np.ascontiguousarray(p[:, [1, 2, 0]], dtype='<f4')
                before_positions.append(p)
                after_positions.append(q)
                pos_cache[pa] = append_accessor(g, blob, q, 'VEC3', with_minmax=True)
            prim.attributes.POSITION = pos_cache[pa]

            na = prim.attributes.NORMAL
            if na is not None:
                if na not in norm_cache:
                    n = read_float_accessor(g, blob, na, 3)
                    qn = np.ascontiguousarray(n[:, [1, 2, 0]], dtype='<f4')
                    norm_cache[na] = append_accessor(g, blob, qn, 'VEC3')
                prim.attributes.NORMAL = norm_cache[na]

            ta = prim.attributes.TANGENT
            if ta is not None:
                if ta not in tan_cache:
                    t = read_float_accessor(g, blob, ta, 4)
                    qt = np.ascontiguousarray(t[:, [1, 2, 0, 3]], dtype='<f4')
                    tan_cache[ta] = append_accessor(g, blob, qt, 'VEC4')
                prim.attributes.TANGENT = tan_cache[ta]

    if primitive_count == 0:
        raise ValueError('GLB contains no mesh primitives')

    pre = bounds(before_positions)
    post = bounds(after_positions)
    if pre is None or post is None:
        raise ValueError('could not compute geometry bounds')

    # Exact permutation invariant: post[x,y,z] = pre[y,z,x].
    expected_min = [pre['min'][1], pre['min'][2], pre['min'][0]]
    expected_max = [pre['max'][1], pre['max'][2], pre['max'][0]]
    if not np.allclose(post['min'], expected_min, atol=1e-6) or not np.allclose(post['max'], expected_max, atol=1e-6):
        raise ValueError(f'basis bounds invariant failed: pre={pre} post={post}')

    g.extras = {
        **(g.extras or {}),
        'd1TigerMeshBasis': {
            'source': 'Tiger Z-up X-forward Y-right',
            'target': 'D1 animation-parser / glTF Y-up basis',
            'permutation': '[x,y,z] -> [y,z,x]',
            'positionsRemapped': len(pos_cache),
            'normalsRemapped': len(norm_cache),
            'tangentsRemapped': len(tan_cache),
            'policy': 'Geometry basis only; joints, weights, inverse bind matrices, animation, materials and UVs untouched.'
        }
    }
    g.buffers[0].byteLength = len(blob)
    g.set_binary_blob(bytes(blob))
    a.output.parent.mkdir(parents=True, exist_ok=True)
    g.save_binary(str(a.output))

    rep = {
        'schema': 'd1_gltf_tiger_mesh_basis_fix/v1',
        'input': str(a.input_glb),
        'output': str(a.output),
        'output_bytes': a.output.stat().st_size,
        'mesh_count': len(g.meshes or []),
        'primitive_count': primitive_count,
        'position_accessors_remapped': len(pos_cache),
        'normal_accessors_remapped': len(norm_cache),
        'tangent_accessors_remapped': len(tan_cache),
        'skin_count': len(g.skins or []),
        'animation_count': len(g.animations or []),
        'bounds_before_tiger': pre,
        'bounds_after_gltf': post,
        'basis_permutation': '[x,y,z] -> [y,z,x]',
        'policy': 'Fail-closed coordinate-basis correction only; no retail skin/material/animation data synthesized.'
    }
    jp = a.json or a.output.with_suffix('.basis.json')
    jp.write_text(json.dumps(rep, indent=2) + '\n')
    print(json.dumps(rep, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
