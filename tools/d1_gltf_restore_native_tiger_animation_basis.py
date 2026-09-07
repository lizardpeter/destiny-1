#!/usr/bin/env python3
"""Restore parser-retargeted glTF animation tracks to native D1/Tiger model basis.

The pinned tiger-animation-parser performs [x,y,z] -> [y,z,x] internally. Its
rig_retarget + convert_obj_to_local pipeline therefore returns parser-space local TRS.
Repository D1 actor meshes and corrected skins are native D1/Tiger model-space assets.
Before those retargeted tracks can drive such a skin, every joint-targeted animation
output must be converted back by the exact inverse basis.

This adapter changes only animation output accessor values. It does not alter times,
channel targets, interpolation, joint hierarchy, inverse binds, mesh data, weights,
materials, textures, action hashes, or selector-state evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.spatial.transform import Rotation

from d1_gltf_layer_merge import read_glb, write_glb
from d1_gltf_skin_bind_identity_probe import accessor

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


def basis_matrix(m: np.ndarray) -> np.ndarray:
    return PI @ np.asarray(m, dtype=np.float64) @ P


def set_float_accessor(doc: dict, blob: bytearray, ai: int, data: np.ndarray) -> None:
    a = doc['accessors'][ai]
    if int(a['componentType']) != FLOAT:
        raise ValueError(f'accessor {ai}: animation output is not FLOAT')
    n = {'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']]
    x = np.asarray(data, dtype='<f4').reshape((int(a['count']), n))
    bv = doc['bufferViews'][a['bufferView']]
    base = int(bv.get('byteOffset', 0)) + int(a.get('byteOffset', 0))
    rowbytes = 4 * n
    stride = int(bv.get('byteStride', rowbytes))
    if stride < rowbytes:
        raise ValueError(f'accessor {ai}: invalid byteStride {stride}')
    if stride == rowbytes:
        raw = x.tobytes(order='C')
        blob[base:base + len(raw)] = raw
    else:
        for i, row in enumerate(x):
            blob[base + i * stride:base + i * stride + rowbytes] = row.astype('<f4').tobytes()


def convert_values(path: str, values: np.ndarray) -> np.ndarray:
    v = np.asarray(values, dtype=np.float64)
    if path in ('translation', 'scale'):
        if v.ndim != 2 or v.shape[1] != 3:
            raise ValueError(f'{path}: expected Nx3, got {v.shape}')
        return v[:, [2, 0, 1]]
    if path == 'rotation':
        if v.ndim != 2 or v.shape[1] != 4:
            raise ValueError(f'rotation: expected Nx4, got {v.shape}')
        out = []
        for q in v:
            m = np.eye(4, dtype=np.float64)
            m[:3, :3] = Rotation.from_quat(q).as_matrix()
            out.append(Rotation.from_matrix(basis_matrix(m)[:3, :3]).as_quat())
        return np.asarray(out, dtype=np.float64)
    raise ValueError(f'unsupported animation target path {path}')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('input_glb', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    a = ap.parse_args()

    doc, binary = read_glb(a.input_glb)
    skins = doc.get('skins', [])
    animations = doc.get('animations', [])
    if not skins:
        raise SystemExit('input has no skin')
    if not animations:
        raise SystemExit('input has no animations')

    joint_nodes = {int(j) for skin in skins for j in skin.get('joints', [])}
    if not joint_nodes:
        raise SystemExit('skins contain no joints')

    blob = bytearray(binary)
    converted: dict[int, str] = {}
    channel_rows = []
    animation_rows = []
    nonjoint_channels = []

    for ani, anim in enumerate(animations):
        converted_here = 0
        for ch_i, ch in enumerate(anim.get('channels', [])):
            target = ch.get('target') or {}
            node = int(target['node'])
            path = str(target['path'])
            sampler_index = int(ch['sampler'])
            sampler = anim['samplers'][sampler_index]
            output_ai = int(sampler['output'])
            if node not in joint_nodes:
                nonjoint_channels.append({'animation_index': ani, 'channel_index': ch_i,
                                          'target_node': node, 'path': path,
                                          'output_accessor': output_ai})
                continue
            previous = converted.get(output_ai)
            if previous is not None and previous != path:
                raise ValueError(f'output accessor {output_ai} shared across incompatible paths {previous}/{path}')
            if previous is None:
                vals = accessor(doc, bytes(blob), output_ai).astype(np.float64)
                new = convert_values(path, vals)
                set_float_accessor(doc, blob, output_ai, new)
                converted[output_ai] = path
            converted_here += 1
            channel_rows.append({'animation_index': ani, 'animation_name': anim.get('name'),
                                 'channel_index': ch_i, 'target_node': node, 'path': path,
                                 'output_accessor': output_ai})
        animation_rows.append({'animation_index': ani, 'name': anim.get('name'),
                               'channel_count': len(anim.get('channels', [])),
                               'joint_targeted_channel_count': converted_here})

    if nonjoint_channels:
        raise ValueError(f'found {len(nonjoint_channels)} non-joint animation channels; refusing partial basis conversion')
    if not converted:
        raise ValueError('no joint-targeted animation output accessors found')

    asset = doc.setdefault('asset', {'version': '2.0'})
    ex = asset.setdefault('extras', {})
    ex['d1NativeTigerAnimationBasis'] = {
        'sourceParserBasis': '[x,y,z] -> [y,z,x]',
        'restoredBasis': 'native D1/Tiger [x,y,z]',
        'animationCount': len(animations),
        'jointTargetedChannelCount': len(channel_rows),
        'convertedOutputAccessorCount': len(converted),
        'animationTimesChanged': False,
        'channelTargetsChanged': False,
        'skinChanged': False,
        'meshChanged': False,
    }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    write_glb(a.out, doc, bytes(blob))
    out_doc, out_binary = read_glb(a.out)
    if len(out_binary) != len(binary):
        raise ValueError(f'BIN byte length changed {len(binary)} -> {len(out_binary)}')
    if len(out_doc.get('animations', [])) != len(animations):
        raise ValueError('animation count changed')
    if len(out_doc.get('skins', [])) != len(skins):
        raise ValueError('skin count changed')

    report = {
        'schema_version': 1,
        'status': 'D1_GLTF_NATIVE_TIGER_ANIMATION_BASIS_RESTORED',
        'input': str(a.input_glb),
        'input_sha256': sha256_file(a.input_glb),
        'output': str(a.out),
        'output_sha256': sha256_file(a.out),
        'output_bytes': a.out.stat().st_size,
        'skin_count': len(skins),
        'animation_count': len(animations),
        'joint_node_count': len(joint_nodes),
        'joint_targeted_channel_count': len(channel_rows),
        'converted_output_accessor_count': len(converted),
        'binary_byte_length_unchanged': len(out_binary) == len(binary),
        'converted_accessors': [{'accessor': ai, 'path': path} for ai, path in sorted(converted.items())],
        'animations': animation_rows,
        'parser_basis_unapplied': True,
        'restored_basis': 'native D1/Tiger [x,y,z]',
        'policy': (
            'Only joint-targeted animation output values are basis-converted. Exact animation '
            'time accessors, interpolation, channel targets, selector/action provenance, skin, '
            'mesh, weights and materials are preserved.'
        ),
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in (
        'status','animation_count','joint_node_count','joint_targeted_channel_count',
        'converted_output_accessor_count','binary_byte_length_unchanged','restored_basis'
    )}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
