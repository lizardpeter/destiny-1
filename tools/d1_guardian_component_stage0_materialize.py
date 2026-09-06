#!/usr/bin/env python3
"""Materialize source-proven D1 component stage-0 surfaces into a portable GLB.

The stage report remains authoritative for visibility and material identity. This
adapter renders only highest-detail ranges and only their stage-group-0 surface
material. A separate explicit binding map tells the portability layer which exact
retail texture is the base diffuse and normal map for each material; every native
source texture hash is retained in material extras.

This does not claim glTF PBR reproduces the native D1 shader. It is a visual
checkpoint that replaces diagnostic flat/white materials with exact retail image
inputs while preserving the proof boundary for detail/scratch/gear-stack logic.
"""
from __future__ import annotations

import argparse, json, re
from pathlib import Path

from d1_gltf_layer_merge import read_glb, write_glb

NAME_RE = re.compile(r'(?P<tag>[0-9A-F]{8})_mesh(?P<mesh>\d+)_range(?P<off>\d+)_(?P<count>\d+)', re.I)


def align4(b: bytearray) -> None:
    while len(b) & 3:
        b.append(0)


def append_bytes(doc: dict, buf: bytearray, data: bytes) -> int:
    align4(buf)
    off = len(buf)
    buf.extend(data)
    doc.setdefault('bufferViews', []).append({'buffer': 0, 'byteOffset': off, 'byteLength': len(data)})
    return len(doc['bufferViews']) - 1


def texture_png(doc: dict, buf: bytearray, path: Path, tag: str, cache: dict[str, int]) -> int:
    if tag in cache:
        return cache[tag]
    bv = append_bytes(doc, buf, path.read_bytes())
    doc.setdefault('images', []).append({'name': tag, 'mimeType': 'image/png', 'bufferView': bv})
    ii = len(doc['images']) - 1
    doc.setdefault('textures', []).append({'name': tag, 'source': ii})
    ti = len(doc['textures']) - 1
    cache[tag] = ti
    return ti


def find_png(root: Path, tag: str) -> Path:
    hits = sorted(root.glob(f'{tag}_*.png'))
    if len(hits) != 1:
        raise ValueError(f'{tag}: expected exactly one PNG in {root}, got {hits}')
    return hits[0]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('input_glb', type=Path)
    ap.add_argument('--stage-report', type=Path, required=True)
    ap.add_argument('--bindings', type=Path, required=True)
    ap.add_argument('--texture-dir', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    doc, bin0 = read_glb(a.input_glb)
    buf = bytearray(bin0)
    stage = json.loads(a.stage_report.read_text())
    bindings = json.loads(a.bindings.read_text())
    if stage.get('schema') != 'd1_guardian_stage_part_material_resolve/v1':
        raise ValueError('unexpected stage report schema')
    if stage.get('errors'):
        raise ValueError('stage report has errors')
    bmap = bindings.get('materials') or {}

    surfaces = {}
    for r in stage.get('ranges', []):
        group0 = [p for p in (r.get('parts') or []) if p.get('stage_group_index') == 0]
        if len(group0) != 1:
            raise ValueError(f"range {r['model_tag']} {r['mesh_index']} {r['index_offset']}/{r['index_count']}: group0 count {len(group0)}")
        p = group0[0]
        mh = p.get('active_material_hash')
        if not mh:
            raise ValueError('group0 lacks active material')
        key = (r['model_tag'].upper(), int(r['mesh_index']), int(r['index_offset']), int(r['index_count']))
        surfaces[key] = {'material': mh.upper(), 'part_index': p['part_index'], 'variant_shader_index': p['variant_shader_index']}

    tex_cache = {}
    mat_cache = {}
    rows = []
    scene = doc['scenes'][int(doc.get('scene', 0))]
    active_nodes = []
    for ni, n in enumerate(doc.get('nodes', [])):
        if n.get('mesh') is None:
            continue
        mesh = doc['meshes'][n['mesh']]
        name = mesh.get('name') or n.get('name') or ''
        m = NAME_RE.search(name)
        if not m:
            continue
        key = (m.group('tag').upper(), int(m.group('mesh')), int(m.group('off')), int(m.group('count')))
        surf = surfaces.get(key)
        if surf is None:
            continue
        mh = surf['material']
        bind = bmap.get(mh)
        if not bind:
            raise ValueError(f'{mh}: missing explicit portable binding')
        if mh not in mat_cache:
            base = bind['base_color'].upper()
            normal = bind.get('normal')
            bt = texture_png(doc, buf, find_png(a.texture_dir, base), base, tex_cache)
            rec = {
                'name': f'D1_{mh}_exact_source_bound',
                'pbrMetallicRoughness': {'baseColorTexture': {'index': bt}, 'metallicFactor': 0.0, 'roughnessFactor': 0.7},
                'doubleSided': False,
                'extras': {
                    'd1MaterialHash': mh,
                    'd1SourceTextures': [str(x).upper() for x in bind.get('source_textures', [])],
                    'd1BaseColorTexture': base,
                    'd1NormalTexture': str(normal).upper() if normal else None,
                    'd1PortabilityPolicy': 'Exact retail images and exact stage-group-0 material identity; glTF PBR is a preview adapter, not a claim of native D1 shader equivalence.'
                }
            }
            if normal:
                nh = str(normal).upper()
                nt = texture_png(doc, buf, find_png(a.texture_dir, nh), nh, tex_cache)
                rec['normalTexture'] = {'index': nt}
            doc.setdefault('materials', []).append(rec)
            mat_cache[mh] = len(doc['materials']) - 1
        if len(mesh.get('primitives', [])) != 1:
            raise ValueError(f'{name}: expected one primitive')
        mesh['primitives'][0]['material'] = mat_cache[mh]
        mesh.setdefault('extras', {})['d1Stage0Surface'] = dict(surf)
        active_nodes.append(ni)
        rows.append({'node': ni, 'mesh': name, 'model': key[0], 'source_mesh': key[1], 'index_offset': key[2], 'index_count': key[3], 'material': mh})

    expected = set(surfaces)
    actual = {(r['model'], r['source_mesh'], r['index_offset'], r['index_count']) for r in rows}
    if actual != expected:
        raise ValueError(f'visible range coverage mismatch missing={sorted(expected-actual)} extra={sorted(actual-expected)}')
    scene['nodes'] = active_nodes
    doc.setdefault('extras', {})['d1Stage0Materialization'] = {
        'activeRangeCount': len(rows),
        'materialHashes': sorted(mat_cache),
        'policy': 'Only source-proven highest-detail stage-group-0 ranges are attached to the scene. Other serialized LOD/pass geometry remains unreachable.'
    }
    write_glb(a.output, doc, bytes(buf))
    rep = {
        'schema': 'd1_guardian_component_stage0_materialize/v1',
        'input': str(a.input_glb), 'output': str(a.output), 'output_bytes': a.output.stat().st_size,
        'active_range_count': len(rows), 'active_materials': sorted(mat_cache),
        'embedded_texture_hashes': sorted(tex_cache), 'ranges': rows,
        'policy': 'Stage visibility/material identity are source-proven. PBR base diffuse/normal are exact retail images; remaining native shader operations are preserved as evidence, not approximated.'
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(rep, indent=2) + '\n')
    print(json.dumps(rep, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
