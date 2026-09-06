#!/usr/bin/env python3
"""Export source-owned D1 articulated world models with exact stage/material selection.

This is the visual counterpart to d1_world_articulated_entity_plan.py.  It does
not infer NPC identity.  For every exact model/parent pair in the articulated
plan it applies the archived D1 stage-0 draw interval, Charm highest-detail LOD
set, and the already validated owning-parent material binding.  External shader
variants are therefore never guessed from the inline part material.

Geometry decoding reuses the cross-package D1 entity-model corpus decoder.  The
output GLBs remain in D1 local coordinates; d1_world_articulated_scene.py applies
the source world transforms and the proven D1 Z-up -> glTF Y-up basis.
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

import d1_tower_map_schema_validate_v5 as v5
from d1_entity_model_probe import parse_model
from d1_entity_model_export import hdr_stride, index_is32, primitive_faces
from d1_entity_model_corpus_export import (
    HIGHEST_LODS,
    NULLS,
    linked,
    material_info,
    norm,
    primary_attrs,
    secondary_attrs,
)

ENTITY_MODEL_CLASS = '80801AB5'


def binding_map(doc: dict) -> dict[str, dict]:
    if doc.get('status') != 'D1_WORLD_ENTITY_MODEL_MATERIAL_BINDINGS_COMPLETE':
        raise ValueError('material bindings are not complete')
    out = {}
    for row in doc.get('bindings', []):
        model = norm(row['model'])
        if not row.get('validation_ok'):
            raise ValueError(f'{model}: material binding not valid')
        if model in out:
            raise ValueError(f'duplicate model material binding {model}')
        out[model] = row
    return out


def models_from_plan(plan: dict) -> list[str]:
    if plan.get('status') != 'D1_WORLD_ARTICULATED_ENTITY_PLAN_COMPLETE':
        raise ValueError('articulated plan is not complete')
    out = []
    for c in plan.get('candidates', []):
        models = [norm(x) for x in c.get('models', []) if norm(x) not in NULLS]
        parents = [norm(x) for x in c.get('model_parent_resources', []) if norm(x) not in NULLS]
        if len(models) != 1 or len(parents) != 1:
            raise ValueError(f"{c.get('entity')}: articulated candidate lacks exact model/parent singleton")
        if models[0] not in out:
            out.append(models[0])
    return out


def selected_ranges(model: dict, binding: dict) -> tuple[list[dict], list[dict]]:
    selected = []
    mesh_summaries = []
    bmeshes = {int(x['mesh_index']): x for x in binding.get('meshes', [])}
    for mi, mesh in enumerate(model['meshes']):
        bm = bmeshes.get(mi)
        if bm is None:
            raise ValueError(f'mesh {mi}: no material binding')
        bparts = {int(x['part_index']): x for x in bm.get('parts', [])}
        offsets = [int(x) for x in (mesh.get('stage_part_offsets_source_derived') or [])]
        if len(offsets) < 2:
            raise ValueError(f'mesh {mi}: missing D1 stage boundaries')
        start, end = offsets[0], offsets[1]
        if start < 0 or end < start or end > len(mesh['parts']):
            raise ValueError(f'mesh {mi}: invalid stage-0 interval [{start},{end})/{len(mesh["parts"])}')
        grouped: dict[tuple[int, int, int], list[dict]] = defaultdict(list)
        for pi in range(start, end):
            p = mesh['parts'][pi]
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
        for (off, count, prim), rows in grouped.items():
            mats = sorted({x['material'] for x in rows})
            if len(mats) != 1:
                raise ValueError(
                    f'mesh {mi} stage-0 range {off}/{count}/{prim}: conflicting active materials {mats}'
                )
            selected.append({
                'mesh_index': mi,
                'index_offset': off,
                'index_count': count,
                'primitive_type': prim,
                'material': mats[0],
                'part_indices': [x['part_index'] for x in rows],
                'lod_values': sorted({x['lod'] for x in rows}),
                'dye_indices': sorted({x['gear_dye_change_color_index'] for x in rows}),
                'parts': rows,
            })
        mesh_summaries.append({
            'mesh_index': mi,
            'part_count': len(mesh['parts']),
            'stage_part_offsets': offsets,
            'stage0_start': start,
            'stage0_end_exclusive': end,
            'stage0_part_count': end - start,
            'selected_range_count': len(grouped),
        })
    return selected, mesh_summaries


def export_one(c, model_hash: str, binding: dict, out_dir: Path) -> dict:
    meta = c.entry_meta(model_hash)
    payload, source = c.payload(model_hash)
    if meta is None or payload is None or norm(meta.get('reference', '')) != ENTITY_MODEL_CLASS:
        raise ValueError(f'{model_hash}: s_entity_model unavailable')
    model = parse_model(payload, 'PS4')
    ranges, mesh_summaries = selected_ranges(model, binding)
    by_mesh: dict[int, list[dict]] = defaultdict(list)
    for r in ranges:
        by_mesh[r['mesh_index']].append(r)

    scene = trimesh.Scene()
    range_reports = []
    active_materials = set()
    for mi, mesh in enumerate(model['meshes']):
        lr0, h0, _, d0 = linked(c, mesh['vertices1'])
        s0 = hdr_stride(h0)
        pos, uv0, n0, t0, col0 = primary_attrs(d0, s0)
        lr1 = None
        s1 = None
        uv1 = n1 = t1 = col1 = None
        secondary_layout = None
        if norm(mesh['vertices2']) not in NULLS:
            lr1, h1, _, d1 = linked(c, mesh['vertices2'])
            s1 = hdr_stride(h1)
            uv1, n1, t1, col1, secondary_layout = secondary_attrs(d1, s1, uv0 is not None, s0)
            if len(pos) != len(d1) // s1:
                raise ValueError(f'{model_hash} mesh {mi}: stream vertex count mismatch')
        lri, ih, _, idata = linked(c, mesh['indices'])
        is32 = index_is32(ih)
        inds = np.frombuffer(idata, dtype='<u4' if is32 else '<u2').astype(np.int64)

        scale = np.asarray(mesh['model_scale'][:3], dtype=np.float32)
        trans = np.asarray(mesh['model_translation'][:3], dtype=np.float32)
        pos = (pos * scale + trans).astype(np.float32)
        uv = uv0 if uv0 is not None else uv1
        normal = n0 if n0 is not None else n1
        tangent = t0 if t0 is not None else t1
        color = col0 if col0 is not None else col1
        if uv is not None:
            ts = np.asarray(mesh['texcoord_scale'], dtype=np.float32)
            tt = np.asarray(mesh['texcoord_translation'], dtype=np.float32)
            uv = np.column_stack((uv[:, 0] * ts[0] + tt[0], uv[:, 1] * (-ts[1]) + 1.0 - tt[1])).astype(np.float32)

        for row in by_mesh.get(mi, []):
            off = row['index_offset']; count = row['index_count']; prim = row['primitive_type']
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
            uu = uv[used] if uv is not None else None
            ttan = tangent[used] if tangent is not None else None
            cc = color[used] if color is not None else None
            mh = row['material']
            minfo = material_info(c, mh)
            if not minfo.get('exists') or not minfo.get('class_matches'):
                raise ValueError(f'{model_hash} mesh {mi}: active material {mh} unavailable')
            mat = trimesh.visual.material.PBRMaterial(name=f'D1_{mh}')
            visual = trimesh.visual.TextureVisuals(uv=uu, material=mat)
            if cc is not None:
                visual.vertex_attributes['color'] = np.clip(cc * 255.0 + 0.5, 0, 255).astype(np.uint8)
            tm = trimesh.Trimesh(vertices=vv, faces=faces, vertex_normals=nn, visual=visual,
                                 process=False, validate=False)
            if ttan is not None:
                tm.vertex_attributes['D1_TANGENT'] = ttan.astype(np.float32)
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
            }
            scene.add_geometry(tm, geom_name=name, node_name=name)
            active_materials.add(mh)
            range_reports.append({
                **row,
                'name': name,
                'source_vertex_count': len(used),
                'triangle_count': len(faces_global),
                'has_uv': uu is not None,
                'has_normals': nn is not None,
                'has_tangents': ttan is not None,
                'has_colors': cc is not None,
                'material_info': minfo,
                'secondary_layout': secondary_layout,
                'vertices1': lr0,
                'vertices2': lr1,
                'indices': lri,
                'primary_stride': s0,
                'secondary_stride': s1,
            })

    if not scene.geometry:
        raise ValueError(f'{model_hash}: stage-0 highest-detail selection emitted no geometry')
    out_dir.mkdir(parents=True, exist_ok=True)
    glb = out_dir / f'{model_hash}.glb'
    rep_path = out_dir / f'{model_hash}.json'
    scene.export(glb)
    rep = {
        'schema_version': 1,
        'status': 'D1_WORLD_ARTICULATED_MODEL_EXPORT_COMPLETE',
        'model': model_hash,
        'source': source,
        'mesh_count': len(model['meshes']),
        'stage0_selected_range_count': len(range_reports),
        'geometry_count': len(scene.geometry),
        'triangle_count': sum(x['triangle_count'] for x in range_reports),
        'active_materials': sorted(active_materials),
        'active_material_count': len(active_materials),
        'bounds': scene.bounds.tolist() if scene.bounds is not None else None,
        'glb': str(glb),
        'glb_bytes': glb.stat().st_size,
        'meshes': mesh_summaries,
        'ranges': range_reports,
        'selection_policy': (
            'Archived D1 stage 0 half-open stage_part_offsets[0:1], Charm highest-detail LODs, '
            'and exact owning-parent material binding. Conflicting active materials on one selected '
            'index range are fatal; no pass, LOD, or external material is guessed.'
        ),
    }
    rep_path.write_text(json.dumps(rep, indent=2) + '\n')
    return rep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', type=Path, action='append', required=True)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--articulated-plan', type=Path, required=True)
    ap.add_argument('--material-bindings', type=Path, required=True)
    ap.add_argument('--out-dir', type=Path, required=True)
    ap.add_argument('--summary', type=Path, required=True)
    a = ap.parse_args()

    plan = json.loads(a.articulated_plan.read_text())
    bindings = binding_map(json.loads(a.material_bindings.read_text()))
    models = models_from_plan(plan)
    missing = sorted(set(models) - set(bindings))
    if missing:
        raise SystemExit('missing exact parent-aware bindings for: ' + ','.join(missing))
    c = v5.v3.base.Corpus([p.resolve() for p in a.snapshot], a.runtime.resolve())
    rows = []
    errors = []
    for h in models:
        try:
            rows.append(export_one(c, h, bindings[h], a.out_dir))
        except Exception as ex:
            errors.append({'model': h, 'error': repr(ex)})
    active = sorted({m for r in rows for m in r['active_materials']})
    out = {
        'schema_version': 1,
        'status': 'D1_WORLD_ARTICULATED_MODEL_SET_COMPLETE' if not errors and len(rows) == len(models)
                  else 'D1_WORLD_ARTICULATED_MODEL_SET_PARTIAL',
        'requested_model_count': len(models),
        'exported_model_count': len(rows),
        'geometry_count': sum(r['geometry_count'] for r in rows),
        'triangle_count': sum(r['triangle_count'] for r in rows),
        'active_material_count': len(active),
        'active_materials': active,
        'models': rows,
        'errors': errors,
    }
    a.summary.parent.mkdir(parents=True, exist_ok=True)
    a.summary.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in ('status','requested_model_count','exported_model_count','geometry_count','triangle_count','active_material_count','errors')}, indent=2))
    return 0 if out['status'] == 'D1_WORLD_ARTICULATED_MODEL_SET_COMPLETE' else 2


if __name__ == '__main__':
    raise SystemExit(main())
