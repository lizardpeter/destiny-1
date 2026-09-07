#!/usr/bin/env python3
"""Export Crota's complete highest-detail Blender visual union.

The old Crota Blender checkpoint incorrectly took only StagePartOffsets[0:1]. For
8108E5B7 that interval covers only three ranges and omits disjoint highest-detail
ranges whose retail materials reference Crota's real 2048x2048 colour atlas 8108E951.

This adapter keeps every unique highest-detail (mesh,index range,primitive) serialized
by the retail model and chooses the first source-ordered material candidate when a
later render variant repeats the exact same geometry range. Every later variant is
retained in the report rather than silently discarded.

Crota also exposed a second defect in the old generic exporter: D1 ROI dynamic vertex
layout is a *stride-pair* decision.  In particular a 0x0C primary stream uses bytes
8..11 as inline two-bone skin data when position-W is +/-32767, but uses those same
bytes as UV0 when W is ordinary (and W itself is then the rigid bone index).  Charm's
pinned ReadD1VertexData does this row-wise and carries the resulting _uvExists state
into the secondary-stream decoder.  The previous Crota path called independent
primary_attrs/secondary_attrs heuristics, which could not distinguish these forms.

For exact model 8108E5B7 the source-closed pairs are:
  mesh 0: primary 0x10 + secondary 0x14 -> position/4-weight + UV/normal/tangent
  mesh 1: primary 0x0C + secondary 0x14 -> position/2-weight + UV/normal/tangent
  mesh 2: primary 0x0C + secondary 0x10 -> position+UV/rigid-W + normal/tangent
Any other pair is fatal in this Crota-specific exporter.

Unlike the generic forensic model exporter, this Blender-facing adapter explicitly
preserves exact decoded UV0 as custom glTF attribute ``_D1_UV0``. Trimesh normally
creates TEXCOORD_0 when TextureVisuals carries UVs even when no image is assigned;
that creates a duplicate accessor alongside our protected source accessor.  Therefore
the forensic geometry layer deliberately gives TextureVisuals no UV and carries the
single authoritative source UV through ``_D1_UV0`` only. A later loss-preserving
adapter aliases that same accessor to TEXCOORD_0 for Blender without changing bytes.

No texture is assigned a PBR role here and no native shader is approximated here.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_entity_model_probe import parse_model
from d1_entity_model_export import (
    decode_vb0,
    decode_vb0_uv,
    decode_vb1,
    hdr_stride,
    index_is32,
    primitive_faces,
)
from d1_entity_model_corpus_export import HIGHEST_LODS, NULLS, linked, material_info, norm
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_split_tar_extract import SplitHttpTar
from d1_remote_activity_placements import RemoteCorpus

ENTITY_MODEL_CLASS = '80801AB5'
CROTA_MODEL = '8108E5B7'
CROTA_STRIDE_PAIRS = {
    0: (0x10, 0x14),
    1: (0x0C, 0x14),
    2: (0x0C, 0x10),
}


def visual_union_ranges(model: dict, binding: dict):
    selected = []
    mesh_summaries = []
    bmeshes = {int(x['mesh_index']): x for x in binding.get('meshes', [])}
    for mi, mesh in enumerate(model['meshes']):
        bm = bmeshes.get(mi)
        if bm is None:
            raise ValueError(f'mesh {mi}: no material binding')
        bparts = {int(x['part_index']): x for x in bm.get('parts', [])}
        grouped = defaultdict(list)
        for pi, p in enumerate(mesh['parts']):
            if int(p['lod']) not in HIGHEST_LODS:
                continue
            bp = bparts.get(pi)
            if bp is None:
                raise ValueError(f'mesh {mi} part {pi}: missing exact material binding')
            sm = bp.get('selected_material') or {}
            mh = norm(sm.get('hash', 'FFFFFFFF'))
            if not sm.get('class_matches') or mh in NULLS:
                raise ValueError(f'mesh {mi} part {pi}: selected material unresolved {mh}')
            key = (int(p['index_offset']), int(p['index_count']), int(p['primitive_type']))
            grouped[key].append({
                'part_index': pi,
                'lod': int(p['lod']),
                'material': mh,
                'gear_dye_change_color_index': int(p['gear_dye_change_color_index']),
                'variant_shader_index': int(p['variant_shader_index']),
                'flags_d1': int(p['flags_d1']),
            })
        for (off, count, prim), rows in sorted(grouped.items(), key=lambda kv: min(x['part_index'] for x in kv[1])):
            rows = sorted(rows, key=lambda x: x['part_index'])
            chosen = rows[0]
            selected.append({
                'mesh_index': mi,
                'index_offset': off,
                'index_count': count,
                'primitive_type': prim,
                'material': chosen['material'],
                'part_indices': [chosen['part_index']],
                'lod_values': [chosen['lod']],
                'dye_indices': [chosen['gear_dye_change_color_index']],
                'parts': [chosen],
                'visual_union_source_first_part': chosen['part_index'],
                'duplicate_render_variants': rows[1:],
                'all_candidate_part_indices': [x['part_index'] for x in rows],
                'all_candidate_materials': [x['material'] for x in rows],
            })
        mesh_summaries.append({
            'mesh_index': mi,
            'part_count': len(mesh['parts']),
            'highest_detail_part_count': sum(int(p['lod']) in HIGHEST_LODS for p in mesh['parts']),
            'unique_highest_detail_range_count': len(grouped),
        })
    return selected, mesh_summaries


def decode_crota_mesh_pair(mesh_index: int, mesh: dict, d0: bytes, s0: int,
                           d1: bytes | None, s1: int | None):
    """Decode one exact 8108E5B7 D1 ROI dynamic stream pair like Charm."""
    expected = CROTA_STRIDE_PAIRS.get(mesh_index)
    pair = (s0, s1)
    if expected is None or pair != expected:
        raise ValueError(f'Crota mesh {mesh_index}: retail stride pair {pair} != pinned expected {expected}')
    if d1 is None or s1 is None:
        raise ValueError(f'Crota mesh {mesh_index}: exact secondary stream is required')
    if len(d0) % s0 or len(d1) % s1:
        raise ValueError(f'Crota mesh {mesh_index}: stream byte count not divisible by stride')
    n0, n1 = len(d0) // s0, len(d1) // s1
    if n0 != n1:
        raise ValueError(f'Crota mesh {mesh_index}: stream vertex count mismatch {n0} != {n1}')

    uvscale = np.asarray(mesh['texcoord_scale'], dtype=np.float32)
    uvtrans = np.asarray(mesh['texcoord_translation'], dtype=np.float32)
    pos = decode_vb0(d0, s0)
    uv0 = decode_vb0_uv(d0, s0, uvscale, uvtrans)
    uv1, normal, tangent, color = decode_vb1(
        d1, s1, uvscale, uvtrans,
        primary_uv_exists=uv0 is not None,
        other_stride=s0,
    )
    uv = uv0 if uv0 is not None else uv1
    if uv is None:
        raise ValueError(f'Crota mesh {mesh_index}: pinned D1 stride-pair decode produced no UV0')

    row_mode = None
    if s0 == 0x0C:
        raw16 = np.frombuffer(d0, dtype='<i2').reshape((-1, 6))
        w = raw16[:, 3]
        sentinel = (w == 32767) | (w == -32767)
        if mesh_index == 1:
            if not np.all(sentinel):
                raise ValueError('Crota mesh 1: expected every 0x0C position-W to be +/-32767 inline2 sentinel')
            if uv0 is not None:
                raise ValueError('Crota mesh 1: inline2 sentinel primary unexpectedly produced UV0')
            row_mode = '0x0C_all_inline2_sentinel_secondary_uv'
        elif mesh_index == 2:
            if np.any(sentinel):
                raise ValueError('Crota mesh 2: expected every 0x0C position-W to be rigid non-sentinel')
            if uv0 is None:
                raise ValueError('Crota mesh 2: rigid 0x0C primary failed to produce UV0')
            row_mode = '0x0C_all_rigid_w_primary_uv'
    elif mesh_index == 0:
        row_mode = '0x10_inline4_secondary_uv'

    layout = {
        'decoder': 'Charm ReadD1VertexData D1 ROI stride-pair equivalent',
        'primary_stride': s0,
        'secondary_stride': s1,
        'primary_uv': uv0 is not None,
        'secondary_uv': uv1 is not None,
        'row_mode': row_mode,
    }
    return pos, uv, normal, tangent, color, layout


def export_visual_union(c: RemoteCorpus, model_hash: str, binding: dict, out_dir: Path) -> dict:
    model_hash = norm(model_hash)
    if model_hash != CROTA_MODEL:
        raise ValueError(f'this exact visual-union decoder is scoped to Crota model {CROTA_MODEL}, got {model_hash}')
    meta = c.entry_meta(model_hash)
    payload, source = c.payload(model_hash)
    if meta is None or payload is None or norm(meta.get('reference', '')) != ENTITY_MODEL_CLASS:
        raise ValueError(f'{model_hash}: s_entity_model unavailable')
    model = parse_model(payload, 'PS4')
    if len(model['meshes']) != 3:
        raise ValueError(f'{model_hash}: expected exact three source meshes, got {len(model["meshes"])}')
    ranges, mesh_summaries = visual_union_ranges(model, binding)
    by_mesh = defaultdict(list)
    for row in ranges:
        by_mesh[int(row['mesh_index'])].append(row)

    scene = trimesh.Scene()
    reports = []
    active_materials = set()
    for mi, mesh in enumerate(model['meshes']):
        lr0, h0, _, d0 = linked(c, mesh['vertices1'])
        s0 = hdr_stride(h0)
        lr1 = None
        s1 = None
        d1 = None
        if norm(mesh['vertices2']) not in NULLS:
            lr1, h1, _, d1 = linked(c, mesh['vertices2'])
            s1 = hdr_stride(h1)
        pos, uv, normal, tangent, color, pair_layout = decode_crota_mesh_pair(mi, mesh, d0, s0, d1, s1)

        lri, ih, _, idata = linked(c, mesh['indices'])
        is32 = index_is32(ih)
        inds = np.frombuffer(idata, dtype='<u4' if is32 else '<u2').astype(np.int64)
        scale = np.asarray(mesh['model_scale'][:3], dtype=np.float32)
        trans = np.asarray(mesh['model_translation'][:3], dtype=np.float32)
        pos = (pos * scale + trans).astype(np.float32)

        for row in by_mesh.get(mi, []):
            off, count, prim = int(row['index_offset']), int(row['index_count']), int(row['primitive_type'])
            sl = inds[off:off + count]
            if len(sl) != count:
                raise ValueError(f'{model_hash} mesh {mi} range {off}/{count}: short index slice')
            faces_global = primitive_faces(sl, prim, is32)
            if len(faces_global) == 0:
                continue
            if faces_global.max() >= len(pos):
                raise ValueError(f'{model_hash} mesh {mi} range {off}/{count}: vertex index OOB')
            used, inv = np.unique(faces_global.reshape(-1), return_inverse=True)
            faces = inv.reshape((-1, 3))
            vv = pos[used]
            nn = normal[used] if normal is not None else None
            uu = uv[used]
            ttan = tangent[used] if tangent is not None else None
            cc = color[used] if color is not None else None
            mh = row['material']
            minfo = material_info(c, mh)
            if not minfo.get('exists') or not minfo.get('class_matches'):
                raise ValueError(f'{model_hash} mesh {mi}: active material {mh} unavailable')
            mat = trimesh.visual.material.PBRMaterial(name=f'D1_{mh}')
            # Do not pass UV to TextureVisuals yet: that would make Trimesh create a
            # second TEXCOORD_0 accessor. _D1_UV0 below is the sole exact transport.
            visual = trimesh.visual.TextureVisuals(material=mat)
            tm = trimesh.Trimesh(vertices=vv, faces=faces, vertex_normals=nn, visual=visual,
                                 process=False, validate=False)
            tm.vertex_attributes['_D1_UV0'] = np.asarray(uu, dtype=np.float32)
            if cc is not None:
                tm.vertex_attributes['_D1_COLOR0'] = np.asarray(cc, dtype=np.float32)
            if ttan is not None:
                tm.vertex_attributes['D1_TANGENT'] = np.asarray(ttan, dtype=np.float32)
            name = f'{model_hash}_mesh{mi}_range{off}_{count}'
            tm.metadata = {
                'model': model_hash,
                'mesh_index': mi,
                'index_offset': off,
                'index_count': count,
                'primitive_type': prim,
                'material': mh,
                'part_indices': row['part_indices'],
                'lod_values': row['lod_values'],
                'dye_indices': row['dye_indices'],
                'source_vertex_indices': used.tolist(),
                'd1_roi_stride_pair_layout': pair_layout,
            }
            scene.add_geometry(tm, geom_name=name, node_name=name)
            active_materials.add(mh)
            reports.append({
                **row,
                'name': name,
                'source_vertex_count': len(used),
                'triangle_count': len(faces_global),
                'has_uv': True,
                'has_normals': nn is not None,
                'has_tangents': ttan is not None,
                'has_colors': cc is not None,
                'material_info': minfo,
                'd1_roi_stride_pair_layout': pair_layout,
                'vertices1': lr0,
                'vertices2': lr1,
                'indices': lri,
                'primary_stride': s0,
                'secondary_stride': s1,
            })

    if not scene.geometry:
        raise ValueError(f'{model_hash}: visual union emitted no geometry')
    if any(not x['has_uv'] for x in reports):
        raise ValueError(f'{model_hash}: Blender visual union contains a range without exact UV0')
    out_dir.mkdir(parents=True, exist_ok=True)
    glb = out_dir / f'{model_hash}.glb'
    scene.export(glb)
    rep = {
        'schema_version': 3,
        'status': 'D1_WORLD_ARTICULATED_MODEL_EXPORT_COMPLETE',
        'model': model_hash,
        'source': source,
        'mesh_count': len(model['meshes']),
        'stage0_selected_range_count': len(reports),
        'visual_union_selected_range_count': len(reports),
        'geometry_count': len(scene.geometry),
        'triangle_count': sum(x['triangle_count'] for x in reports),
        'active_materials': sorted(active_materials),
        'active_material_count': len(active_materials),
        'bounds': scene.bounds.tolist() if scene.bounds is not None else None,
        'glb': str(glb),
        'glb_bytes': glb.stat().st_size,
        'meshes': mesh_summaries,
        'ranges': reports,
        'selection_mode': 'all_unique_highest_detail_ranges_source_first_duplicate_variant',
        'selection_policy': (
            'All unique Charm IsHighestLevel D1 index ranges are retained. Repeated identical geometry ranges use the '
            'first source-ordered material candidate while every later render variant remains explicit in the report. '
            'Vertex attributes are decoded by the exact D1 ROI primary/secondary stride-pair and position-W sentinel rules; '
            'UV0 is preserved as the sole protected _D1_UV0 accessor for the later Blender adapter.'
        ),
    }
    (out_dir / f'{model_hash}.json').write_text(json.dumps(rep, indent=2) + '\n')
    return rep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--material-bindings', type=Path, required=True)
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--out-dir', type=Path, required=True)
    ap.add_argument('--model', default='8108E5B7')
    ap.add_argument('--parent', default='8108E4BA')
    a = ap.parse_args()
    model = norm(a.model); parent = norm(a.parent)
    bd = json.loads(a.material_bindings.read_text())
    if bd.get('status') not in ('D1_REMOTE_ACTIVITY_MODEL_MATERIAL_BINDINGS_COMPLETE', 'D1_WORLD_ENTITY_MODEL_MATERIAL_BINDINGS_COMPLETE'):
        raise SystemExit(f'bindings not complete: {bd.get("status")}')
    rows = [x for x in bd.get('bindings', []) if norm(x.get('model')) == model and norm(x.get('parent_resource')) == parent]
    if len(rows) != 1:
        raise SystemExit(f'expected one {model}/{parent} binding, got {len(rows)}')
    if not rows[0].get('validation_ok') or rows[0].get('violations'):
        raise SystemExit('binding validation failed')
    cats = load_catalogs(a.member_catalog)
    arc = SplitHttpTar([f'{a.base_url.rstrip("/")}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    c = RemoteCorpus(arc, cats, a.runtime)
    rep = export_visual_union(c, model, rows[0], a.out_dir)
    assert rep['geometry_count'] == 9, rep['geometry_count']
    assert rep['active_material_count'] == 7, rep['active_materials']
    assert all(x['has_uv'] for x in rep['ranges'])
    print('CROTA_VISUAL_UNION', 'RANGES', rep['geometry_count'], 'TRIANGLES', rep['triangle_count'], 'MATERIALS', rep['active_materials'])
    for rr in rep['ranges']:
        print('RANGE', rr['mesh_index'], rr['index_offset'], rr['index_count'], 'PART', rr['visual_union_source_first_part'], 'MAT', rr['material'], 'PAIR', rr['d1_roi_stride_pair_layout']['row_mode'], 'DUPLICATES', [(x['part_index'], x['material']) for x in rr['duplicate_render_variants']])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
