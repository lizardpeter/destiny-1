#!/usr/bin/env python3
"""Restore source-backed D1 Guardian stage-0 attributes to an existing GLB.

The earlier combined Guardian skin/animation path preserved POSITION/TEXCOORD_0 and
skin data but dropped secondary-stream normals and the D1 dye-detail multiplier.
For an active range this tool reopens the exact retail s_entity_model vertex streams,
uses the range's preserved ``source_vertex_indices`` mapping, and appends:

* NORMAL       — exact decoded D1 secondary-stream normal, Tiger->glTF basis mapped;
* TEXCOORD_1   — exact final half2 D1 ``a_texcoord2`` multiplier for detail UVs.

Promotion of TEXCOORD_1 is gated by a previously produced native PS4 stage-0 vertex
shader join: the exact range must be present, marked detail-enabled, and the native
input signature must end in vec2. No visual or neighboring-resource inference is
used. TANGENT is intentionally not emitted here because the current D1 decoder has
only source-closed the tangent xyz lane, while glTF TANGENT requires an exact fourth
handedness component.
"""
from __future__ import annotations

import argparse
import json
import math
import struct
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_entity_model_export import (
    byhash,
    decode_vb0_uv,
    decode_vb1,
    hdr_stride,
    read_linked,
)
from d1_entity_model_probe import D1_ENTITY_MODEL_CLASS, parse_model
from d1_guardian_texcoord2_lane_probe import candidate_offset
from d1_investment_arrangement_probe import filehash_pkg_index
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_remote_model_export import MultiPackageReader
from d1_split_tar_extract import SplitHttpTar

JSON_CHUNK = 0x4E4F534A
BIN_CHUNK = 0x004E4942


def read_glb(path: Path):
    raw = path.read_bytes()
    magic, version, total = struct.unpack_from('<4sII', raw, 0)
    if magic != b'glTF' or version != 2 or total != len(raw):
        raise ValueError('input is not a valid GLB v2')
    pos = 12
    graph = None
    blob = None
    while pos < len(raw):
        length, typ = struct.unpack_from('<II', raw, pos)
        pos += 8
        data = raw[pos:pos + length]
        pos += length
        if typ == JSON_CHUNK:
            graph = json.loads(data.decode('utf-8').rstrip('\x00 '))
        elif typ == BIN_CHUNK:
            blob = bytearray(data)
    if graph is None or blob is None:
        raise ValueError('GLB must contain JSON and BIN chunks')
    if len(graph.get('buffers', [])) != 1:
        raise ValueError('only one-buffer GLBs are supported')
    return graph, blob


def write_glb(path: Path, graph: dict, blob: bytearray):
    graph['buffers'][0]['byteLength'] = len(blob)
    js = json.dumps(graph, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    js += b' ' * ((4 - len(js) % 4) % 4)
    bb = bytes(blob)
    bb += b'\x00' * ((4 - len(bb) % 4) % 4)
    total = 12 + 8 + len(js) + 8 + len(bb)
    out = bytearray(struct.pack('<4sII', b'glTF', 2, total))
    out += struct.pack('<II', len(js), JSON_CHUNK) + js
    out += struct.pack('<II', len(bb), BIN_CHUNK) + bb
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(out)


def accessor_count(graph: dict, accessor_index: int) -> int:
    return int(graph['accessors'][accessor_index]['count'])


def append_accessor(graph: dict, blob: bytearray, values: np.ndarray, typ: str, name: str) -> int:
    values = np.asarray(values, dtype='<f4')
    expected = {'VEC2': 2, 'VEC3': 3}[typ]
    if values.ndim != 2 or values.shape[1] != expected:
        raise ValueError((name, values.shape, typ))
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
    item = {
        'bufferView': bv,
        'byteOffset': 0,
        'componentType': 5126,
        'count': int(values.shape[0]),
        'type': typ,
        'name': name,
    }
    if typ == 'VEC3':
        item['min'] = [float(x) for x in np.min(values, axis=0)]
        item['max'] = [float(x) for x in np.max(values, axis=0)]
    graph['accessors'].append(item)
    return acc


def load_vs_join(path: Path) -> dict:
    d = json.loads(path.read_text())
    if d.get('schema') != 'd1_guardian_stage0_vs_join/v1':
        raise ValueError('unexpected stage0 VS join schema')
    rows = {}
    for r in d.get('ranges', []):
        key = (
            str(r['model_tag']).upper(), int(r['mesh_index']),
            int(r['index_offset']), int(r['index_count']), int(r['primitive_type'])
        )
        if key in rows:
            raise ValueError(f'duplicate VS evidence row {key}')
        if r.get('detail_half2_candidate') is not True:
            raise ValueError(f'active stage0 range is not detail-enabled: {key}')
        widths = r.get('input_component_widths') or []
        if not widths or int(widths[-1]) != 2:
            raise ValueError(f'native vertex signature does not end in vec2: {key} {widths}')
        nc = r.get('native_checks') or {}
        if not nc.get('stage_is_vertex_shader'):
            raise ValueError(f'native shader is not vertex stage: {key}')
        if not nc.get('gnmx_shader_size_matches_orbshdr_end') or not nc.get('usage_count_matches_orbshdr'):
            raise ValueError(f'native shader framing validation failed: {key}')
        rows[key] = r
    return rows


def decode_detail_half2(data: bytes, stride: int, offset: int) -> np.ndarray:
    if len(data) % stride:
        raise ValueError(f'secondary vertex bytes {len(data)} not divisible by stride {stride:#x}')
    n = len(data) // stride
    out = np.empty((n, 2), dtype=np.float32)
    for i in range(n):
        x, y = struct.unpack_from('<ee', data, i * stride + offset)
        x, y = float(x), float(y)
        if not (math.isfinite(x) and math.isfinite(y) and x > 0.0 and y > 0.0 and x <= 64.0 and y <= 64.0):
            raise ValueError(f'invalid D1 detail half2 at vertex {i}: {(x, y)}')
        out[i] = (x, y)
    return out


def basis_map_normal(native: np.ndarray) -> np.ndarray:
    native = np.asarray(native, dtype=np.float32)
    out = native[:, [1, 2, 0]].copy()  # Tiger [x,y,z] -> glTF-side [y,z,x]
    lengths = np.linalg.norm(out, axis=1)
    if np.any(~np.isfinite(lengths)) or np.any(lengths < 1e-8):
        raise ValueError('invalid zero/non-finite source normal')
    # glTF requires NORMAL to be unit length. This is representation normalization,
    # not a guessed semantic transform.
    out /= lengths[:, None]
    return out.astype(np.float32)


def range_key_from_mesh(mesh: dict):
    ex = mesh.get('extras') or {}
    required = ('model_tag_hash', 'mesh_index', 'index_offset', 'index_count', 'primitive_type', 'source_vertex_indices')
    missing = [x for x in required if x not in ex]
    if missing:
        raise ValueError(f'active mesh lacks preserved D1 source metadata: {mesh.get("name")} {missing}')
    return (
        str(ex['model_tag_hash']).upper(), int(ex['mesh_index']),
        int(ex['index_offset']), int(ex['index_count']), int(ex['primitive_type'])
    ), [int(x) for x in ex['source_vertex_indices']]


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
    needed_models = set()
    for ni, node in enumerate(graph.get('nodes', [])):
        if node.get('mesh') is None:
            continue
        mesh_index = int(node['mesh'])
        mesh = graph['meshes'][mesh_index]
        if len(mesh.get('primitives', [])) != 1:
            raise ValueError(f'active mesh {mesh.get("name")} must have one primitive')
        key, source_indices = range_key_from_mesh(mesh)
        if key not in evidence:
            raise ValueError(f'active GLB range lacks exact native VS evidence: {key}')
        pos_count = accessor_count(graph, int(mesh['primitives'][0]['attributes']['POSITION']))
        if len(source_indices) != pos_count:
            raise ValueError(f'{key}: source index count {len(source_indices)} != POSITION count {pos_count}')
        active.append((ni, mesh_index, mesh, key, source_indices))
        needed_models.add(key[0])

    if len(active) != len(evidence):
        missing = sorted(set(evidence) - {x[3] for x in active})
        extra = sorted({x[3] for x in active} - set(evidence))
        raise ValueError(f'active/evidence range mismatch active={len(active)} evidence={len(evidence)} missing={missing} extra={extra}')

    catalogs = load_catalogs(a.member_catalog)
    required_pkgs = {filehash_pkg_index(int(tag, 16))[0] for tag in needed_models}
    missing_pkgs = sorted(required_pkgs - set(catalogs))
    if missing_pkgs:
        raise ValueError('missing package catalogs: ' + ', '.join(f'{x:04X}' for x in missing_pkgs))

    base = a.base_url.rstrip('/')
    archive = SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    views = {pkg: RemoteLogicalPackage(archive, fam, a.runtime) for pkg, fam in sorted(catalogs.items())}
    multi = MultiPackageReader(views)
    hmap = byhash(multi)

    decoded = {}
    for tag in sorted(needed_models):
        ent = hmap.get(tag)
        if ent is None or ent['reference'].upper() != D1_ENTITY_MODEL_CLASS:
            raise ValueError(f'{tag}: exact s_entity_model not available in supplied package views')
        model = parse_model(multi.entry(ent['index']), 'PS4')
        for mi, mesh in enumerate(model['meshes']):
            _, h0, _, d0 = read_linked(multi, hmap, mesh['vertices1'])
            _, h1, _, d1 = read_linked(multi, hmap, mesh['vertices2'])
            s0, s1 = hdr_stride(h0), hdr_stride(h1)
            primary_uv = decode_vb0_uv(d0, s0, mesh['texcoord_scale'], mesh['texcoord_translation'])
            secondary_uv, normal, tangent_xyz, color = decode_vb1(
                d1, s1, mesh['texcoord_scale'], mesh['texcoord_translation'],
                primary_uv_exists=primary_uv is not None, other_stride=s0,
            )
            uv_source = 'primary' if primary_uv is not None else ('secondary' if secondary_uv is not None else None)
            if normal is None:
                raise ValueError(f'{tag} mesh {mi}: source decoder produced no normal')
            detail_off = candidate_offset(s1, uv_source)
            if detail_off is None:
                raise ValueError(f'{tag} mesh {mi}: no conservative D1 detail half2 location for {s0:#x}/{s1:#x} {uv_source}')
            detail = decode_detail_half2(d1, s1, detail_off)
            if len(normal) != len(detail):
                raise ValueError(f'{tag} mesh {mi}: normal/detail vertex counts differ')
            decoded[(tag, mi)] = {
                'normal': basis_map_normal(normal),
                'detail': detail,
                'stride0': s0,
                'stride1': s1,
                'uv_source': uv_source,
                'detail_offset': detail_off,
                'tangent_xyz_source_closed': tangent_xyz is not None,
            }

    rows = []
    for ni, gltf_mesh_index, mesh, key, source_indices in active:
        tag, source_mesh_index, off, count, prim_type = key
        src = decoded[(tag, source_mesh_index)]
        ids = np.asarray(source_indices, dtype=np.int64)
        if len(ids) and (ids.min() < 0 or ids.max() >= len(src['normal'])):
            raise ValueError(f'{key}: source vertex index out of range')
        normal = src['normal'][ids]
        detail = src['detail'][ids]
        normal_acc = append_accessor(graph, blob, normal, 'VEC3', f'{tag}_mesh{source_mesh_index}_range{off}_{count}_NORMAL')
        detail_acc = append_accessor(graph, blob, detail, 'VEC2', f'{tag}_mesh{source_mesh_index}_range{off}_{count}_D1_a_texcoord2')
        prim = mesh['primitives'][0]
        prim.setdefault('attributes', {})['NORMAL'] = normal_acc
        prim['attributes']['TEXCOORD_1'] = detail_acc
        mesh['extras'] = {
            **(mesh.get('extras') or {}),
            'd1SourceAttributeRestore': {
                'normal': 'exact D1 secondary stream; Tiger [x,y,z] -> glTF [y,z,x]; normalized only for glTF NORMAL requirement',
                'TEXCOORD_1': 'exact D1 a_texcoord2 multiplier encoded as final little-endian half2 and promoted by native PS4 stage0 VS signature + archived Bungie Spasm contract',
                'source_stride0': src['stride0'],
                'source_stride1': src['stride1'],
                'uv0_source': src['uv_source'],
                'detail_half2_byte_offset': src['detail_offset'],
                'tangent': 'not emitted: tangent xyz is decoded, but exact glTF tangent handedness w is not yet source-closed',
            },
        }
        rows.append({
            'node_index': ni,
            'gltf_mesh_index': gltf_mesh_index,
            'model_tag': tag,
            'source_mesh_index': source_mesh_index,
            'index_offset': off,
            'index_count': count,
            'primitive_type': prim_type,
            'vertex_count': len(ids),
            'normal_accessor': normal_acc,
            'texcoord1_accessor': detail_acc,
            'normal_length_minmax': [float(np.linalg.norm(normal, axis=1).min()), float(np.linalg.norm(normal, axis=1).max())],
            'detail_min': [float(x) for x in np.min(detail, axis=0)],
            'detail_max': [float(x) for x in np.max(detail, axis=0)],
            'source_stride0': src['stride0'],
            'source_stride1': src['stride1'],
            'uv0_source': src['uv_source'],
            'detail_half2_byte_offset': src['detail_offset'],
        })

    graph['extras'] = {
        **(graph.get('extras') or {}),
        'd1Stage0SourceAttributes': {
            'active_range_count': len(rows),
            'normal_restored': True,
            'detail_texcoord_multiplier_restored_as_TEXCOORD_1': True,
            'tangent_emitted': False,
            'policy': 'All active ranges matched exact retail source metadata and exact native PS4 stage0 VS detail evidence. No inferred range or semantic was accepted.',
        },
    }
    write_glb(a.out, graph, blob)
    report = {
        'schema': 'd1_guardian_stage0_source_attributes_patch/v1',
        'input': str(a.input_glb),
        'output': str(a.out),
        'output_bytes': a.out.stat().st_size,
        'active_range_count': len(rows),
        'rows': rows,
        'policy': graph['extras']['d1Stage0SourceAttributes'],
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'rows'}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
