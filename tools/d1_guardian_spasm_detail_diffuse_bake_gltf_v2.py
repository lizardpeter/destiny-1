#!/usr/bin/env python3
"""Bake the exact archived D1 Spasm detail-diffuse path into glTF plate space.

This is the corrected v2 implementation.  The first portable bake rasterized glTF
TEXCOORD_0 with an extra vertical flip.  That was wrong because glTF 2.0 defines
(0,0) at the upper-left of the texture image, while ``d1_entity_model_export`` has
*already* converted Tiger/D1 V to glTF V with::

    gltf_v = 1 - d1_v

Therefore:

* geometry masks are rasterized directly with ``y = gltf_v * height``;
* the archived Spasm detail equation is evaluated in D1 texture-coordinate space,
  so the plate pixel is converted back with ``d1_v = 1 - gltf_v``;
* the resulting D1 detail V is converted to the extracted/glTF image convention
  with ``detail_gltf_v = 1 - detail_d1_v``.

No visual alignment or hand-authored offset is used.  The transform is fixed by the
existing source-backed Tiger->glTF UV conversion plus the normative glTF texture
coordinate convention.  The current Spektar data gives an independent byte/image
check: corrected active masks fall on the non-empty source plate regions, while the
old vertically-flipped masks mostly fall in transparent atlas space.

The output still deliberately uses KHR_materials_unlit.  This tool source-closes the
published Bungie Spasm diffuse/change-color path only; it does not invent native PS4
roughness, metallic, or lighting semantics.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from d1_guardian_spasm_detail_diffuse_bake import (
    accessor,
    append_bytes,
    blend_overlay,
    image_bytes,
    load_detail_images,
    load_dyes,
    load_selectors,
    range_key,
    read_glb,
    selector_dye,
    write_glb,
)


def make_mask_gltf(triangles_uv: list[np.ndarray], width: int, height: int) -> np.ndarray:
    """Rasterize glTF UVs into image rows without another V flip."""
    mask = np.zeros((height, width), dtype=np.uint8)
    polygons = []
    for tri in triangles_uv:
        pts = np.rint(np.column_stack((
            tri[:, 0] * (width - 1),
            tri[:, 1] * (height - 1),
        ))).astype(np.int32)
        polygons.append(pts)
    if polygons:
        cv2.fillPoly(mask, polygons, 255)
    return mask


def make_mask_legacy_vflip(triangles_uv: list[np.ndarray], width: int, height: int) -> np.ndarray:
    """Old v1 mapping, retained only to quantify the regression in the report."""
    mask = np.zeros((height, width), dtype=np.uint8)
    polygons = []
    for tri in triangles_uv:
        pts = np.rint(np.column_stack((
            tri[:, 0] * (width - 1),
            (1.0 - tri[:, 1]) * (height - 1),
        ))).astype(np.int32)
        polygons.append(pts)
    if polygons:
        cv2.fillPoly(mask, polygons, 255)
    return mask


def sample_d1_detail_from_gltf_plate(
    detail_rgba: np.ndarray,
    width: int,
    height: int,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    multiplier: np.ndarray,
    transform: np.ndarray,
) -> np.ndarray:
    """Evaluate Bungie's D1 detail UV equation for glTF plate pixels.

    ``TEXCOORD_0`` is already glTF-oriented.  Convert its V back to D1 before
    evaluating ``((texcoord * a_texcoord2) * detailTransform.xy) + zw``, then
    convert the resulting D1 V back to the extracted/glTF image row convention.
    Sampling is source-backed level-0 LINEAR + REPEAT.  Runtime mip choice remains
    screen dependent and is intentionally not guessed by a static bake.
    """
    detail_h, detail_w, _ = detail_rgba.shape
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)

    gltf_u = (xx + 0.5) / float(width)
    gltf_v = (yy + 0.5) / float(height)
    d1_u = gltf_u
    d1_v = 1.0 - gltf_v

    detail_d1_u = (d1_u * multiplier[0]) * transform[0] + transform[2]
    detail_d1_v = (d1_v * multiplier[1]) * transform[1] + transform[3]

    detail_gltf_u = np.mod(detail_d1_u, 1.0)
    detail_gltf_v = 1.0 - np.mod(detail_d1_v, 1.0)
    map_x = (detail_gltf_u * detail_w - 0.5).astype(np.float32)
    map_y = (detail_gltf_v * detail_h - 0.5).astype(np.float32)
    return cv2.remap(
        detail_rgba,
        map_x,
        map_y,
        interpolation=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_WRAP,
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('input_glb', type=Path)
    ap.add_argument('--stage-dyes', type=Path, required=True)
    ap.add_argument('--exact-dyes', type=Path, required=True)
    ap.add_argument('--detail-manifest', type=Path, required=True)
    ap.add_argument('--detail-dir', type=Path, required=True)
    ap.add_argument('-o', '--out', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    args = ap.parse_args()

    graph, blob = read_glb(args.input_glb)
    selectors = load_selectors(args.stage_dyes)
    dyes = load_dyes(args.exact_dyes)
    detail_paths = load_detail_images(args.detail_manifest, args.detail_dir)

    groups: dict[tuple[int, int], dict[tuple[float, float], list[np.ndarray]]] = {}
    active = []
    for node_index, node in enumerate(graph.get('nodes', [])):
        if node.get('mesh') is None:
            continue
        mesh_index = int(node['mesh'])
        mesh = graph['meshes'][mesh_index]
        if len(mesh.get('primitives', [])) != 1:
            raise ValueError(f'active mesh {mesh.get("name")} must have one primitive')
        primitive = mesh['primitives'][0]
        attrs = primitive.get('attributes') or {}
        required = {
            'POSITION', 'NORMAL', 'TANGENT', 'TEXCOORD_0', 'TEXCOORD_1',
            'JOINTS_0', 'WEIGHTS_0',
        }
        if not required <= set(attrs):
            raise ValueError(
                f'{mesh.get("name")}: missing exact source attributes '
                f'{sorted(required - set(attrs))}'
            )
        if int(primitive.get('mode', 4)) != 4 or 'indices' not in primitive:
            raise ValueError(f'{mesh.get("name")}: indexed TRIANGLES required')

        name = mesh.get('name') or node.get('name') or ''
        key = range_key(name)
        if key not in selectors:
            raise ValueError(f'{name}: no exact stage-part dye selector')
        selector = int(selectors[key])
        uv = accessor(graph, blob, int(attrs['TEXCOORD_0'])).astype(np.float32)
        multiplier = accessor(graph, blob, int(attrs['TEXCOORD_1'])).astype(np.float32)
        indices = accessor(graph, blob, int(primitive['indices'])).reshape(-1).astype(np.int64)
        if len(indices) % 3:
            raise ValueError(f'{name}: triangle index count is not divisible by three')
        triangles = indices.reshape((-1, 3))
        old_material = int(primitive['material'])
        bucket = groups.setdefault((old_material, selector), {})
        for tri in triangles:
            local = multiplier[tri]
            if float(np.max(np.ptp(local, axis=0))) > 1e-6:
                raise ValueError(f'{name}: a_texcoord2 varies within a triangle')
            value = (float(local[0, 0]), float(local[0, 1]))
            bucket.setdefault(value, []).append(uv[tri])
        active.append((node_index, mesh_index, name, old_material, selector, primitive))

    baked_materials: dict[tuple[int, int], int] = {}
    material_rows = []
    total_overlap = 0
    total_alpha_mismatch = 0
    total_legacy_alpha_hit = 0
    total_legacy_covered = 0

    for (old_material_index, selector), multiplier_groups in sorted(groups.items()):
        old_material = graph['materials'][old_material_index]
        extras = old_material.get('extras') or {}
        if 'd1TexturePlateHeader' not in extras or 'd1GStackTextureIndex' not in extras:
            raise ValueError(f'material {old_material_index} lacks exact D1 plate/GStack provenance')
        plate = str(extras['d1TexturePlateHeader']).upper()
        albedo_texture = int(old_material['pbrMetallicRoughness']['baseColorTexture']['index'])
        gstack_texture = int(extras['d1GStackTextureIndex'])
        albedo_image = int(graph['textures'][albedo_texture]['source'])
        gstack_image = int(graph['textures'][gstack_texture]['source'])
        albedo = np.asarray(
            Image.open(io.BytesIO(image_bytes(graph, blob, albedo_image))).convert('RGBA'),
            dtype=np.float32,
        ) / 255.0
        gstack = np.asarray(
            Image.open(io.BytesIO(image_bytes(graph, blob, gstack_image))).convert('RGBA'),
            dtype=np.float32,
        ) / 255.0
        if albedo.shape != gstack.shape:
            raise ValueError(f'{plate}: albedo/GStack dimensions differ')
        height, width, _ = albedo.shape

        dye_index, dye, color_role, change_color = selector_dye(selector, dyes)
        detail_hash = str(dye['detail_diffuse_texture_hash']).upper()
        if detail_hash not in detail_paths:
            raise ValueError(f'dye {dye_index}: missing exact detail diffuse {detail_hash}')
        detail_rgba = np.asarray(
            Image.open(detail_paths[detail_hash]).convert('RGBA'), dtype=np.float32
        ) / 255.0
        detail_transform = np.asarray(dye['detail_transform'], dtype=np.float32)

        color_linear = np.power(albedo[..., :3], 2.2)
        alpha_nonzero = albedo[..., 3] > 0.0
        covered = np.zeros((height, width), dtype=np.uint8)
        legacy_union = np.zeros((height, width), dtype=np.uint8)
        overlap_pixels = 0

        for multiplier_value, triangles_uv in sorted(multiplier_groups.items()):
            mask = make_mask_gltf(triangles_uv, width, height)
            legacy_union = np.maximum(
                legacy_union,
                make_mask_legacy_vflip(triangles_uv, width, height),
            )
            overlap = (mask > 0) & (covered > 0)
            overlap_count = int(np.count_nonzero(overlap))
            if overlap_count:
                raise ValueError(
                    f'{plate} selector {selector}: {overlap_count} texels overlap '
                    'across different exact a_texcoord2 multiplier regions'
                )
            overlap_pixels += overlap_count
            covered = np.maximum(covered, mask)
            ys, xs = np.nonzero(mask)
            if not len(xs):
                continue
            x0, x1 = int(xs.min()), int(xs.max()) + 1
            y0, y1 = int(ys.min()), int(ys.max()) + 1
            submask = mask[y0:y1, x0:x1] > 0
            sampled = sample_d1_detail_from_gltf_plate(
                detail_rgba,
                width,
                height,
                x0,
                y0,
                x1,
                y1,
                np.asarray(multiplier_value, dtype=np.float32),
                detail_transform,
            )
            alpha = sampled[..., 3:4]
            normalize = (1.0 - alpha) * 0.5
            detail_linear = np.power(
                np.clip(sampled[..., :3] * alpha + normalize, 0.0, 1.0), 2.2
            )
            target = color_linear[y0:y1, x0:x1]
            merged = blend_overlay(detail_linear, target)
            target[submask] = merged[submask]

        current = covered > 0
        alpha_mismatch = int(np.count_nonzero(current & ~alpha_nonzero))
        legacy = legacy_union > 0
        legacy_hit = int(np.count_nonzero(legacy & alpha_nonzero))
        legacy_covered = int(np.count_nonzero(legacy))
        total_alpha_mismatch += alpha_mismatch
        total_legacy_alpha_hit += legacy_hit
        total_legacy_covered += legacy_covered

        mask_r = gstack[..., 0:1]
        dyed = blend_overlay(color_linear, change_color.reshape((1, 1, 3)))
        color_linear = color_linear * (1.0 - mask_r) + dyed * mask_r
        srgb = np.power(np.clip(color_linear, 0.0, 1.0), 1.0 / 2.2)
        rgba = np.concatenate((
            srgb,
            np.ones((height, width, 1), dtype=np.float32),
        ), axis=2)
        image = Image.fromarray(np.rint(rgba * 255.0).astype(np.uint8), 'RGBA')
        bio = io.BytesIO()
        image.save(bio, format='PNG', compress_level=6)
        png = bio.getvalue()
        view_index = append_bytes(
            graph, blob, png, f'{plate}_selector{selector}_spasm_detail_diffuse_gltf_v2_png'
        )
        image_index = len(graph.setdefault('images', []))
        graph['images'].append({
            'bufferView': view_index,
            'mimeType': 'image/png',
            'name': f'{plate}_selector{selector}_spasm_detail_diffuse_gltf_v2',
        })
        texture_index = len(graph.setdefault('textures', []))
        graph['textures'].append({
            'source': image_index,
            'sampler': graph['textures'][albedo_texture].get('sampler', 0),
            'name': f'{plate}_selector{selector}_spasm_detail_diffuse_gltf_v2',
        })
        material_name = (
            f'D1_{plate}_selector{selector}_dye{dye_index}_'
            'SPASM_DETAIL_DIFFUSE_GLTF_V2_UNLIT'
        )
        material = {
            'name': material_name,
            'pbrMetallicRoughness': {
                'baseColorFactor': [1.0, 1.0, 1.0, 1.0],
                'baseColorTexture': {'index': texture_index, 'texCoord': 0},
                'metallicFactor': 0.0,
                'roughnessFactor': 1.0,
            },
            'extensions': {'KHR_materials_unlit': {}},
            'alphaMode': 'OPAQUE',
            'doubleSided': bool(old_material.get('doubleSided', False)),
            'extras': {
                'd1MaterialDiagnostic': 'archived Bungie Spasm detail-diffuse + change-color path; glTF upper-left UV convention corrected',
                'd1OriginalMaterialIndex': old_material_index,
                'd1TexturePlateHeader': plate,
                'd1GearDyeChangeColorIndex': selector,
                'd1DyeIndex': dye_index,
                'd1DyeColorRole': color_role,
                'd1ChangeColor': [float(x) for x in change_color],
                'd1DetailDiffuseTextureHash': detail_hash,
                'd1DetailTransform': [float(x) for x in detail_transform],
                'd1DistinctATexcoord2Values': len(multiplier_groups),
                'd1CoveredPixels': int(np.count_nonzero(current)),
                'd1CoveredTransparentSourceAlbedoPixels': alpha_mismatch,
                'd1LegacyVFlipCoveredPixels': legacy_covered,
                'd1LegacyVFlipNontransparentSourceAlbedoPixels': legacy_hit,
                'd1OverlapPixelsAcrossMultiplierMasks': overlap_pixels,
                'd1UVPolicy': 'TEXCOORD_0 is already D1->glTF V-flipped; glTF image origin is upper-left; convert back to D1 only while evaluating archived Spasm detail UV equation',
                'd1ShaderOrder': 'diffuse^2.2 -> exact detail diffuse overlay -> exact GStack.R change-color -> gamma',
                'd1Sampling': 'level-0 LINEAR/REPEAT; runtime mip LOD is view dependent and intentionally not baked',
            },
        }
        new_material_index = len(graph.setdefault('materials', []))
        graph['materials'].append(material)
        baked_materials[(old_material_index, selector)] = new_material_index
        total_overlap += overlap_pixels
        material_rows.append({
            'old_material_index': old_material_index,
            'new_material_index': new_material_index,
            'name': material_name,
            **material['extras'],
        })
        print(
            'BAKED_GLTF_V2', plate, 'selector', selector,
            'covered', int(np.count_nonzero(current)),
            'alpha_mismatch', alpha_mismatch,
            'legacy_hit', legacy_hit, '/', legacy_covered,
        )

    for _node, _mesh, _name, old_material, selector, primitive in active:
        primitive['material'] = baked_materials[(old_material, selector)]

    used = graph.setdefault('extensionsUsed', [])
    if 'KHR_materials_unlit' not in used:
        used.append('KHR_materials_unlit')
    policy = {
        'activePrimitiveCount': len(active),
        'bakedMaterialCount': len(baked_materials),
        'uvConvention': 'glTF 2.0 upper-left texture origin; exact exporter already maps D1/Tiger V to glTF V',
        'detailEquationSpace': 'convert glTF V back to D1 V, evaluate archived Spasm equation, convert resulting detail V back to glTF image V',
        'overlapConflictPixels': total_overlap,
        'coveredTransparentSourceAlbedoPixels': total_alpha_mismatch,
        'legacyVFlipNontransparentPixels': total_legacy_alpha_hit,
        'legacyVFlipCoveredPixels': total_legacy_covered,
        'nativePS4MaterialClaim': False,
    }
    graph.setdefault('extras', {})['d1SpasmDetailDiffuseGltfV2'] = policy

    write_glb(args.out, graph, blob)
    report = {
        'schema': 'd1_guardian_spasm_detail_diffuse_bake_gltf/v2',
        'input': str(args.input_glb),
        'output': str(args.out),
        'output_bytes': args.out.stat().st_size,
        'output_sha256': hashlib.sha256(args.out.read_bytes()).hexdigest(),
        'active_primitive_count': len(active),
        'baked_material_count': len(baked_materials),
        'overlap_conflict_pixels': total_overlap,
        'covered_transparent_source_albedo_pixels': total_alpha_mismatch,
        'legacy_vflip_nontransparent_pixels': total_legacy_alpha_hit,
        'legacy_vflip_covered_pixels': total_legacy_covered,
        'materials': material_rows,
        'policy': policy,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({
        'active': len(active),
        'materials': len(baked_materials),
        'overlap': total_overlap,
        'alpha_mismatch': total_alpha_mismatch,
        'legacy_hit': total_legacy_alpha_hit,
        'legacy_covered': total_legacy_covered,
        'bytes': args.out.stat().st_size,
        'sha256': report['output_sha256'],
    }, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
