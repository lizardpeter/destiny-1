#!/usr/bin/env python3
"""Test whether archived D1 Spasm normal math is exactly representable by glTF normalTexture.

This is an evidence probe, not a renderer.  It uses only:

* an already source-backed Guardian GLB with exact TEXCOORD_0/TEXCOORD_1 and the
  corrected glTF/D1 UV convention;
* the exact base plate normal texture preserved in the original D1 material;
* the exact SDye_D1 detail normal texture and detail_transform;
* Bungie's archived Spasm fragment equation:

    base_xy   = texture2D(u_texture_normal, v_texcoord).xy * 2 - 1
    detail_xy = texture2D(u_texture_dye_normal, v_texcoord2).xy * 2 - 1
    xy        = base_xy + detail_xy
    z         = sqrt(saturate(1 - dot(xy, xy)))

Spasm then transforms that vector through the tangent frame and uses it directly in
its dot/reflection lighting calculations.  It does not normalize the reconstructed
``normal_tangent_space`` after z reconstruction.  Therefore any active texel with
``dot(xy,xy) > 1`` has vector length > 1 and cannot be represented exactly by a
standard glTF normalTexture path that normalizes the normal vector.

The probe deliberately does not clamp, renormalize, scale, or visually tune the
result.  Its purpose is to prevent a portable approximation from being promoted as
an exact D1 material reconstruction.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from d1_guardian_spasm_detail_diffuse_bake import (
    accessor,
    image_bytes,
    load_detail_images,
    load_dyes,
    read_glb,
)
from d1_guardian_spasm_detail_diffuse_bake_gltf_v2 import (
    make_mask_gltf,
    sample_d1_detail_from_gltf_plate,
)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('input_glb', type=Path)
    ap.add_argument('--exact-dyes', type=Path, required=True)
    ap.add_argument('--detail-manifest', type=Path, required=True)
    ap.add_argument('--detail-dir', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    args = ap.parse_args()

    graph, blob = read_glb(args.input_glb)
    dyes = load_dyes(args.exact_dyes)
    detail_paths = load_detail_images(args.detail_manifest, args.detail_dir)

    # Group active triangles by exact source plate material, exact stage selector,
    # and exact per-triangle a_texcoord2 value.  The v5 material stores provenance
    # for all three, so no name or visual matching is needed here.
    groups: dict[tuple[int, int], dict[tuple[float, float], list[np.ndarray]]] = {}
    active_ranges = 0
    for node in graph.get('nodes', []):
        if node.get('mesh') is None:
            continue
        mesh = graph['meshes'][int(node['mesh'])]
        if len(mesh.get('primitives', [])) != 1:
            raise ValueError(f'{mesh.get("name")}: one primitive required')
        prim = mesh['primitives'][0]
        attrs = prim.get('attributes') or {}
        required = {'POSITION','NORMAL','TANGENT','TEXCOORD_0','TEXCOORD_1','JOINTS_0','WEIGHTS_0'}
        if not required <= set(attrs):
            raise ValueError(f'{mesh.get("name")}: missing exact source attributes {sorted(required-set(attrs))}')
        material = graph['materials'][int(prim['material'])]
        extras = material.get('extras') or {}
        uv_policy = str(extras.get('d1UVPolicy',''))
        if not uv_policy.startswith('TEXCOORD_0 is already D1->glTF V-flipped'):
            raise ValueError(f'{mesh.get("name")}: input is not corrected glTF-UV material checkpoint')
        old_material = int(extras['d1OriginalMaterialIndex'])
        selector = int(extras['d1GearDyeChangeColorIndex'])
        uv = accessor(graph, blob, int(attrs['TEXCOORD_0'])).astype(np.float32)
        mult = accessor(graph, blob, int(attrs['TEXCOORD_1'])).astype(np.float32)
        inds = accessor(graph, blob, int(prim['indices'])).reshape(-1).astype(np.int64)
        if len(inds) % 3:
            raise ValueError(f'{mesh.get("name")}: non-triangle index count')
        bucket = groups.setdefault((old_material, selector), {})
        for tri in inds.reshape((-1,3)):
            mm = mult[tri]
            if float(np.max(np.ptp(mm, axis=0))) > 1e-6:
                raise ValueError(f'{mesh.get("name")}: a_texcoord2 varies within a triangle')
            key = (float(mm[0,0]), float(mm[0,1]))
            bucket.setdefault(key, []).append(uv[tri])
        active_ranges += 1

    rows = []
    total_pixels = 0
    total_over_unit = 0
    global_max_len = 0.0
    global_max_r2 = 0.0

    for (old_material_index, selector), multiplier_groups in sorted(groups.items()):
        old = graph['materials'][old_material_index]
        old_extras = old.get('extras') or {}
        plate = str(old_extras.get('d1TexturePlateHeader','')).upper()
        if not plate:
            raise ValueError(f'original material {old_material_index}: no D1 plate header')
        if 'normalTexture' not in old:
            raise ValueError(f'{plate}: no exact base plate normal texture')
        normal_tex = int(old['normalTexture']['index'])
        normal_image = int(graph['textures'][normal_tex]['source'])
        base = np.asarray(Image.open(__import__('io').BytesIO(image_bytes(graph,blob,normal_image))).convert('RGBA'), dtype=np.float32) / 255.0
        h,w,_ = base.shape

        # The v5 material records the exact dye selected for this selector.  Resolve
        # the authoritative SDye_D1 row again and require that selector slot agrees.
        # selector 0/1 -> slot 0; 2/3 -> slot 1; 4/5 -> slot 2.
        slot = selector // 2
        candidates = [(idx,d) for idx,d in dyes.items() if int(d['slot_type_index']) == slot]
        if len(candidates) != 1:
            raise ValueError(f'{plate} selector {selector}: expected one exact dye for slot {slot}, got {len(candidates)}')
        dye_index,dye = candidates[0]
        detail_hash = str(dye['detail_normal_texture_hash']).upper()
        if detail_hash not in detail_paths:
            raise ValueError(f'{plate}: missing exact detail normal {detail_hash}')
        detail = np.asarray(Image.open(detail_paths[detail_hash]).convert('RGBA'), dtype=np.float32) / 255.0
        transform = np.asarray(dye['detail_transform'], dtype=np.float32)

        union = np.zeros((h,w), dtype=np.uint8)
        values = []
        overlaps = 0
        for mult_value, triangles_uv in sorted(multiplier_groups.items()):
            mask = make_mask_gltf(triangles_uv,w,h)
            overlap = (mask > 0) & (union > 0)
            overlaps += int(np.count_nonzero(overlap))
            if overlaps:
                raise ValueError(f'{plate} selector {selector}: multiplier mask overlap {overlaps}')
            union = np.maximum(union,mask)
            ys,xs = np.nonzero(mask)
            if not len(xs):
                continue
            x0,x1=int(xs.min()),int(xs.max())+1
            y0,y1=int(ys.min()),int(ys.max())+1
            sub = mask[y0:y1,x0:x1] > 0
            sampled = sample_d1_detail_from_gltf_plate(
                detail,w,h,x0,y0,x1,y1,np.asarray(mult_value,dtype=np.float32),transform
            )
            base_xy = base[y0:y1,x0:x1,:2] * 2.0 - 1.0
            detail_xy = sampled[...,:2] * 2.0 - 1.0
            xy = base_xy + detail_xy
            r2 = np.sum(xy*xy, axis=2)
            values.append(r2[sub])

        if not values:
            raise ValueError(f'{plate} selector {selector}: no covered pixels')
        r2 = np.concatenate(values).astype(np.float64)
        z = np.sqrt(np.maximum(0.0,1.0-r2))
        length = np.sqrt(r2 + z*z)
        over = r2 > 1.0
        count = int(r2.size)
        over_count = int(np.count_nonzero(over))
        max_len = float(np.max(length))
        max_r2 = float(np.max(r2))
        total_pixels += count
        total_over_unit += over_count
        global_max_len = max(global_max_len,max_len)
        global_max_r2 = max(global_max_r2,max_r2)
        rows.append({
            'plate': plate,
            'original_material_index': old_material_index,
            'selector': selector,
            'dye_index': int(dye_index),
            'detail_normal_texture_hash': detail_hash,
            'detail_transform': [float(x) for x in transform],
            'covered_pixels': count,
            'xy_length_squared_gt_1_pixels': over_count,
            'xy_length_squared_gt_1_fraction': over_count / count,
            'xy_length_squared_min': float(np.min(r2)),
            'xy_length_squared_p50': float(np.quantile(r2,0.50)),
            'xy_length_squared_p95': float(np.quantile(r2,0.95)),
            'xy_length_squared_max': max_r2,
            'spasm_reconstructed_vector_length_max': max_len,
            'exact_standard_gltf_normal_texture_equivalent': over_count == 0,
        })
        print('SPASM_NORMAL',plate,'selector',selector,'pixels',count,'over_unit',over_count,'max_len',max_len)

    report = {
        'schema':'d1_guardian_spasm_normal_equivalence/v1',
        'input':str(args.input_glb),
        'active_range_count':active_ranges,
        'material_selector_group_count':len(rows),
        'covered_pixels_total':total_pixels,
        'xy_length_squared_gt_1_pixels_total':total_over_unit,
        'xy_length_squared_gt_1_fraction_total':total_over_unit/total_pixels,
        'spasm_reconstructed_vector_length_max':global_max_len,
        'xy_length_squared_max':global_max_r2,
        'standard_gltf_normal_texture_is_exact':total_over_unit == 0,
        'rows':rows,
        'source_formula':{
            'base':'base_xy = baseNormal.rg*2-1',
            'detail':'detail_xy = dyeDetailNormal.rg*2-1',
            'combine':'xy = base_xy + detail_xy',
            'z':'sqrt(max(0,1-dot(xy,xy)))',
            'post_reconstruction_normalize':'none in archived Bungie Spasm shader',
        },
        'policy':'No normalization, scaling, strength adjustment, or other approximation is applied. If any active sample has dot(xy,xy)>1, standard glTF normalTexture is classified non-exact for the archived Spasm path.',
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('active_range_count','material_selector_group_count','covered_pixels_total','xy_length_squared_gt_1_pixels_total','xy_length_squared_gt_1_fraction_total','spasm_reconstructed_vector_length_max','standard_gltf_normal_texture_is_exact')},indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
