#!/usr/bin/env python3
"""Restore exact glTF TANGENT for active D1 Guardian stage-0 geometry.

The archived Bungie D1 GearShader consumes ``a_tangent`` as vec4 and constructs:

    object_space_binormal = cross(object_space_normal, object_space_tangent)
                            * a_tangent.w

The already-proven native PS4 stage-0 input signatures contain a vec4 tangent lane
immediately before the final detail vec2. The active Spektar layouts place that vec4
in the exact retail secondary stream as:

- stride 0x14 with primary UV0: int16 lanes 4..7
- stride 0x18 with secondary UV0: int16 lanes 6..9

This tool reopens only source meshes referenced by the exact active stage-0 ranges,
recovers tangent xyz + handedness W from those lanes, validates that source W is
exactly +/-32767 for every used source vertex, applies the proven Tiger->glTF cyclic
basis mapping [x,y,z]->[y,z,x], and emits glTF TANGENT with W +/-1 unchanged. The
basis permutation has determinant +1, so handedness does not flip.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_entity_model_export import byhash, decode_vb0_uv, hdr_stride, read_linked
from d1_entity_model_probe import D1_ENTITY_MODEL_CLASS, parse_model
from d1_guardian_stage0_source_attributes_patch import append_accessor, range_key_from_mesh, read_glb, write_glb
from d1_guardian_stage0_source_attributes_patch_active_only import load_vs_join
from d1_investment_arrangement_probe import filehash_pkg_index
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_remote_model_export import MultiPackageReader
from d1_split_tar_extract import SplitHttpTar


def snorm16(values: np.ndarray) -> np.ndarray:
    x = np.asarray(values, dtype=np.float32) / 32767.0
    return np.maximum(x, -1.0)


def decode_active_tangent4(data: bytes, stride: int, uv_source: str):
    if len(data) % stride:
        raise ValueError(f'secondary stream bytes {len(data)} not divisible by stride {stride:#x}')
    raw = np.frombuffer(data, dtype='<i2').reshape((-1, stride // 2))
    if stride == 0x14 and uv_source == 'primary':
        lane = raw[:, 4:8]
    elif stride == 0x18 and uv_source == 'secondary':
        lane = raw[:, 6:10]
    else:
        raise ValueError(f'active tangent layout not source-closed for stride={stride:#x} uv={uv_source}')
    if lane.shape[1] != 4:
        raise ValueError('tangent lane is not four int16 components')
    return lane.copy()


def basis_map_tangent(raw_lane: np.ndarray) -> np.ndarray:
    raw_lane = np.asarray(raw_lane, dtype=np.int16)
    wraw = raw_lane[:, 3].astype(np.int32)
    bad = np.logical_and(wraw != 32767, wraw != -32767)
    if np.any(bad):
        values, counts = np.unique(wraw[bad], return_counts=True)
        raise ValueError(f'tangent handedness contains non +/-32767 source values: {list(zip(values.tolist(), counts.tolist()))[:20]}')
    xyz = snorm16(raw_lane[:, :3])
    xyz = xyz[:, [1, 2, 0]].copy()  # cyclic permutation, determinant +1
    lengths = np.linalg.norm(xyz, axis=1)
    if np.any(~np.isfinite(lengths)) or np.any(lengths < 1e-8):
        raise ValueError('zero/non-finite tangent xyz')
    xyz /= lengths[:, None]  # representation normalization required by glTF
    w = np.where(wraw > 0, 1.0, -1.0).astype(np.float32)
    return np.column_stack((xyz, w)).astype(np.float32), wraw


def append_tangent_accessor(graph: dict, blob: bytearray, tangent: np.ndarray, name: str) -> int:
    values = np.asarray(tangent, dtype='<f4')
    if values.ndim != 2 or values.shape[1] != 4:
        raise ValueError((name, values.shape))
    pad = (-len(blob)) % 4
    if pad:
        blob.extend(b'\x00' * pad)
    offset = len(blob)
    raw = values.tobytes(order='C')
    blob.extend(raw)
    bv = len(graph.setdefault('bufferViews', []))
    graph['bufferViews'].append({
        'buffer': 0,
        'byteOffset': offset,
        'byteLength': len(raw),
        'target': 34962,
        'name': name + '_bufferView',
    })
    acc = len(graph.setdefault('accessors', []))
    graph['accessors'].append({
        'bufferView': bv,
        'byteOffset': 0,
        'componentType': 5126,
        'count': int(values.shape[0]),
        'type': 'VEC4',
        'name': name,
    })
    return acc


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('input_glb', type=Path)
    ap.add_argument('--vs-join', type=Path, required=True)
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('-o', '--out', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    a = ap.parse_args()

    graph, blob = read_glb(a.input_glb)
    evidence = load_vs_join(a.vs_join)

    active = []
    needed: dict[str, set[int]] = {}
    for node_index, node in enumerate(graph.get('nodes', [])):
        if node.get('mesh') is None:
            continue
        gltf_mesh_index = int(node['mesh'])
        mesh = graph['meshes'][gltf_mesh_index]
        if len(mesh.get('primitives', [])) != 1:
            raise ValueError(f'active mesh {mesh.get("name")} must have one primitive')
        key, source_indices = range_key_from_mesh(mesh)
        if key not in evidence:
            raise ValueError(f'active range lacks native VS evidence: {key}')
        widths = [int(x) for x in evidence[key].get('input_component_widths', [])]
        if len(widths) < 2 or widths[-2:] != [4, 2]:
            raise ValueError(f'{key}: native VS signature does not end tangent vec4 + detail vec2: {widths}')
        attrs = mesh['primitives'][0].get('attributes') or {}
        if 'NORMAL' not in attrs or 'TEXCOORD_1' not in attrs:
            raise ValueError(f'{key}: source normal/detail UV must already be present before tangent restore')
        active.append((node_index, gltf_mesh_index, mesh, key, source_indices))
        needed.setdefault(key[0], set()).add(int(key[1]))

    if {x[3] for x in active} != set(evidence):
        raise ValueError('active/evidence range set mismatch')

    catalogs = load_catalogs(a.member_catalog)
    required_pkgs = {filehash_pkg_index(int(tag, 16))[0] for tag in needed}
    missing = sorted(required_pkgs - set(catalogs))
    if missing:
        raise ValueError('missing package catalogs: ' + ', '.join(f'{x:04X}' for x in missing))
    base = a.base_url.rstrip('/')
    archive = SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    views = {pkg: RemoteLogicalPackage(archive, fam, a.runtime) for pkg, fam in sorted(catalogs.items())}
    multi = MultiPackageReader(views)
    hmap = byhash(multi)

    decoded = {}
    source_rows = []
    for tag in sorted(needed):
        ent = hmap.get(tag)
        if ent is None or ent['reference'].upper() != D1_ENTITY_MODEL_CLASS:
            raise ValueError(f'{tag}: exact s_entity_model unavailable')
        model = parse_model(multi.entry(ent['index']), 'PS4')
        for mi in sorted(needed[tag]):
            mesh = model['meshes'][mi]
            _, h0, _, d0 = read_linked(multi, hmap, mesh['vertices1'])
            _, h1, _, d1 = read_linked(multi, hmap, mesh['vertices2'])
            s0, s1 = hdr_stride(h0), hdr_stride(h1)
            primary_uv = decode_vb0_uv(d0, s0, mesh['texcoord_scale'], mesh['texcoord_translation'])
            uv_source = 'primary' if primary_uv is not None else 'secondary'
            raw_lane = decode_active_tangent4(d1, s1, uv_source)
            tangent, wraw = basis_map_tangent(raw_lane)
            decoded[(tag, mi)] = tangent
            vals, counts = np.unique(wraw, return_counts=True)
            source_rows.append({
                'model_tag': tag,
                'source_mesh_index': mi,
                'stride0': s0,
                'stride1': s1,
                'uv0_source': uv_source,
                'source_vertex_count': len(tangent),
                'handedness_raw_counts': {str(int(v)): int(c) for v, c in zip(vals, counts)},
                'tangent_length_minmax': [
                    float(np.linalg.norm(tangent[:, :3], axis=1).min()),
                    float(np.linalg.norm(tangent[:, :3], axis=1).max()),
                ],
            })

    range_rows = []
    for node_index, gltf_mesh_index, mesh, key, source_indices in active:
        tag, source_mesh_index, off, count, primitive_type = key
        all_tangent = decoded[(tag, source_mesh_index)]
        ids = np.asarray(source_indices, dtype=np.int64)
        if len(ids) and (ids.min() < 0 or ids.max() >= len(all_tangent)):
            raise ValueError(f'{key}: source vertex index out of tangent range')
        tangent = all_tangent[ids]
        acc = append_tangent_accessor(
            graph, blob, tangent,
            f'{tag}_mesh{source_mesh_index}_range{off}_{count}_TANGENT',
        )
        primitive = mesh['primitives'][0]
        primitive.setdefault('attributes', {})['TANGENT'] = acc
        mesh['extras'] = {
            **(mesh.get('extras') or {}),
            'd1SourceTangentRestore': {
                'source': 'exact D1 secondary stream tangent vec4 lane selected by active layout + native PS4 VS signature',
                'basis': 'Tiger xyz -> glTF [y,z,x], determinant +1, source handedness preserved',
                'w': 'source int16 must be exactly +/-32767, exported as +/-1',
                'xyzNormalization': 'representation normalization for glTF TANGENT requirement only',
            },
        }
        vals, counts = np.unique(tangent[:, 3], return_counts=True)
        range_rows.append({
            'node_index': node_index,
            'gltf_mesh_index': gltf_mesh_index,
            'model_tag': tag,
            'source_mesh_index': source_mesh_index,
            'index_offset': off,
            'index_count': count,
            'primitive_type': primitive_type,
            'vertex_count': len(ids),
            'tangent_accessor': acc,
            'handedness_counts': {str(float(v)): int(c) for v, c in zip(vals, counts)},
        })

    graph.setdefault('extras', {})['d1GuardianStage0TangentRestore'] = {
        'activeRangeCount': len(range_rows),
        'decodedSourceMeshCount': len(decoded),
        'policy': 'exact active source tangent vec4 only; no tangent generation from geometry or UV derivatives',
    }
    write_glb(a.out, graph, blob)
    report = {
        'schema': 'd1_guardian_stage0_tangent_restore/v1',
        'input': str(a.input_glb),
        'output': str(a.out),
        'active_range_count': len(range_rows),
        'decoded_source_mesh_count': len(decoded),
        'source_meshes': source_rows,
        'ranges': range_rows,
        'policy': graph['extras']['d1GuardianStage0TangentRestore'],
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + '\n')
    print('TANGENT_RESTORE ranges', len(range_rows), 'source_meshes', len(decoded), 'bytes', a.out.stat().st_size)
    for row in source_rows:
        print('SOURCE', row)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
