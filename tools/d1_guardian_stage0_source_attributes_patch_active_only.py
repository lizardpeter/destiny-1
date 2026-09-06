#!/usr/bin/env python3
"""Restore exact D1 source normals/detail UVs for only active stage-0 Guardian meshes.

This is the fail-closed successor to d1_guardian_stage0_source_attributes_patch.py.
The earlier tool correctly validated every visible stage-0 range, but then decoded
*every* serialized mesh in each owner model. Inactive meshes can legitimately use
other vertex layouts, so that broader decode could fail on data that is not part of
the selected render set.

This tool decodes only source (model, mesh) pairs referenced by the exact active
stage-0 ranges already joined to native PS4 vertex-shader evidence. No inactive
layout is interpreted and no visual override is introduced.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_entity_model_export import byhash, decode_vb0_uv, decode_vb1, hdr_stride, read_linked
from d1_entity_model_probe import D1_ENTITY_MODEL_CLASS, parse_model
from d1_guardian_stage0_source_attributes_patch import (
    accessor_count,
    append_accessor,
    basis_map_normal,
    decode_detail_half2,
    load_vs_join,
    range_key_from_mesh,
    read_glb,
    write_glb,
)
from d1_guardian_texcoord2_lane_probe import candidate_offset
from d1_investment_arrangement_probe import filehash_pkg_index
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_remote_model_export import MultiPackageReader
from d1_split_tar_extract import SplitHttpTar


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
    needed_meshes: dict[str, set[int]] = {}
    for ni, node in enumerate(graph.get('nodes', [])):
        if node.get('mesh') is None:
            continue
        gltf_mesh_index = int(node['mesh'])
        mesh = graph['meshes'][gltf_mesh_index]
        if len(mesh.get('primitives', [])) != 1:
            raise ValueError(f'active mesh {mesh.get("name")} must have one primitive')
        key, source_indices = range_key_from_mesh(mesh)
        if key not in evidence:
            raise ValueError(f'active GLB range lacks exact native VS evidence: {key}')
        pos_count = accessor_count(graph, int(mesh['primitives'][0]['attributes']['POSITION']))
        if len(source_indices) != pos_count:
            raise ValueError(f'{key}: source index count {len(source_indices)} != POSITION count {pos_count}')
        active.append((ni, gltf_mesh_index, mesh, key, source_indices))
        needed_meshes.setdefault(key[0], set()).add(int(key[1]))

    active_keys = {x[3] for x in active}
    if active_keys != set(evidence):
        missing = sorted(set(evidence) - active_keys)
        extra = sorted(active_keys - set(evidence))
        raise ValueError(f'active/evidence mismatch active={len(active_keys)} evidence={len(evidence)} missing={missing} extra={extra}')

    catalogs = load_catalogs(a.member_catalog)
    required_pkgs = {filehash_pkg_index(int(tag, 16))[0] for tag in needed_meshes}
    missing_pkgs = sorted(required_pkgs - set(catalogs))
    if missing_pkgs:
        raise ValueError('missing package catalogs: ' + ', '.join(f'{x:04X}' for x in missing_pkgs))

    base = a.base_url.rstrip('/')
    archive = SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    views = {pkg: RemoteLogicalPackage(archive, fam, a.runtime) for pkg, fam in sorted(catalogs.items())}
    multi = MultiPackageReader(views)
    hmap = byhash(multi)

    decoded = {}
    decode_rows = []
    for tag in sorted(needed_meshes):
        ent = hmap.get(tag)
        if ent is None or ent['reference'].upper() != D1_ENTITY_MODEL_CLASS:
            raise ValueError(f'{tag}: exact s_entity_model not available in supplied package views')
        model = parse_model(multi.entry(ent['index']), 'PS4')
        for mi in sorted(needed_meshes[tag]):
            if mi < 0 or mi >= len(model['meshes']):
                raise ValueError(f'{tag}: active source mesh index {mi} outside serialized mesh count {len(model["meshes"])}')
            mesh = model['meshes'][mi]
            _, h0, _, d0 = read_linked(multi, hmap, mesh['vertices1'])
            _, h1, _, d1 = read_linked(multi, hmap, mesh['vertices2'])
            s0, s1 = hdr_stride(h0), hdr_stride(h1)
            primary_uv = decode_vb0_uv(d0, s0, mesh['texcoord_scale'], mesh['texcoord_translation'])
            secondary_uv, normal, tangent_xyz, _color = decode_vb1(
                d1, s1, mesh['texcoord_scale'], mesh['texcoord_translation'],
                primary_uv_exists=primary_uv is not None, other_stride=s0,
            )
            uv_source = 'primary' if primary_uv is not None else ('secondary' if secondary_uv is not None else None)
            if normal is None:
                raise ValueError(f'{tag} mesh {mi}: source decoder produced no normal')

            mesh_evidence = [r for k, r in evidence.items() if k[0] == tag and int(k[1]) == mi]
            if not mesh_evidence:
                raise ValueError(f'{tag} mesh {mi}: no active native VS evidence')
            offsets = {int(r['detail_half2_offset']) for r in mesh_evidence if r.get('detail_half2_offset') is not None}
            if len(offsets) != 1:
                raise ValueError(f'{tag} mesh {mi}: active ranges disagree on detail half2 offset: {sorted(offsets)}')
            detail_off = next(iter(offsets))
            conservative = candidate_offset(s1, uv_source)
            if conservative is not None and int(conservative) != detail_off:
                raise ValueError(f'{tag} mesh {mi}: VS evidence detail offset {detail_off} != layout evidence {conservative}')
            if detail_off < 0 or detail_off + 4 > s1:
                raise ValueError(f'{tag} mesh {mi}: detail offset {detail_off} outside stride {s1}')

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
            decode_rows.append({
                'model_tag': tag,
                'source_mesh_index': mi,
                'stride0': s0,
                'stride1': s1,
                'uv0_source': uv_source,
                'detail_half2_byte_offset': detail_off,
                'active_range_count': len(mesh_evidence),
                'source_vertex_count': int(len(normal)),
            })

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
                'selection': 'only exact active stage0 source meshes were decoded',
                'normal': 'exact D1 secondary stream; Tiger [x,y,z] -> glTF [y,z,x]; normalized only for glTF NORMAL requirement',
                'TEXCOORD_1': 'exact D1 a_texcoord2 multiplier; byte offset taken from this active range native PS4 VS join and checked against the conservative layout decoder when available',
                'source_stride0': src['stride0'],
                'source_stride1': src['stride1'],
                'uv0_source': src['uv_source'],
                'detail_half2_byte_offset': src['detail_offset'],
                'tangent': 'not emitted: tangent xyz is source-decoded but glTF tangent handedness w is not yet source-closed',
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
            'vertex_count': int(len(ids)),
            'normal_accessor': normal_acc,
            'texcoord1_accessor': detail_acc,
            'normal_length_minmax': [float(np.linalg.norm(normal, axis=1).min()), float(np.linalg.norm(normal, axis=1).max())],
            'detail_min': [float(x) for x in np.min(detail, axis=0)],
            'detail_max': [float(x) for x in np.max(detail, axis=0)],
        })

    graph.setdefault('extras', {})['d1GuardianStage0SourceAttributes'] = {
        'policy': 'active-stage0-only source decode; inactive serialized mesh layouts are intentionally untouched',
        'active_range_count': len(rows),
        'decoded_source_mesh_count': len(decoded),
    }
    write_glb(a.out, graph, blob)

    report = {
        'schema': 'd1_guardian_stage0_source_attributes_patch_active_only/v1',
        'input_glb': str(a.input_glb),
        'output_glb': str(a.out),
        'active_range_count': len(rows),
        'decoded_source_mesh_count': len(decoded),
        'decoded_source_meshes': decode_rows,
        'ranges': rows,
        'policy': 'Only source meshes referenced by exact active stage0 ranges are decoded. No inactive mesh layout is interpreted and no visual range override is performed.',
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + '\n')
    print('ACTIVE_STAGE0_SOURCE_ATTRIBUTES', 'ranges', len(rows), 'source_meshes', len(decoded), 'bytes', a.out.stat().st_size)
    for d in decode_rows:
        print('SOURCE_MESH', d)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
