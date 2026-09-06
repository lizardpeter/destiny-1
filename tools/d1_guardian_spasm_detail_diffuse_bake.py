#!/usr/bin/env python3
"""Bake the source-backed D1 Spasm dye-detail diffuse path into a portable GLB.

Input requirements:
- exact active stage-0 Guardian geometry;
- exact D1 NORMAL already restored;
- exact D1 ``a_texcoord2`` multiplier exported as glTF ``TEXCOORD_1``;
- exact stage-part change-color selector report;
- exact SDye_D1 records;
- exact exported retail dye-detail diffuse PNGs.

The archived Bungie D1 Spasm shader computes:

    v_texcoord2 = ((texcoord * a_texcoord2) * u_detail_transform.xy)
                  + u_detail_transform.zw

and, in the fragment path:

    color_diffuse = pow(texture2D(u_texture_diffuse, v_texcoord), 2.2)
    detail = texture2D(u_texture_dye_diffuse, v_texcoord2)
    dye_alpha = detail.a
    dye_normalize = (1 - dye_alpha) * 0.5
    detail_linear = pow(detail.rgb * dye_alpha + dye_normalize, 2.2)
    color_diffuse = blend_overlay(detail_linear, color_diffuse)
    color_diffuse = mix(color_diffuse,
                        blend_overlay(color_diffuse, u_change_color),
                        gearstack.r)
    output = pow(color_diffuse, 1/2.2)

This tool bakes that diffuse/color path into KHR_materials_unlit textures so Blender
or another glTF viewer cannot make the color diagnostic artificially dark. It does
NOT claim final native PS4 material equivalence: dye-detail normal, native tangent
handedness, screen-dependent mip selection, and the complete specular path remain
separate source-closure tasks.

A crucial safety gate is enforced: if two different ``a_texcoord2`` multiplier
regions overlap the same base-plate texel, the bake fails instead of choosing one.
For the current exact Spektar stage-0 set the independently validated result has zero
such conflicts.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import struct
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

JSON_CHUNK = 0x4E4F534A
BIN_CHUNK = 0x004E4942
NAME_RE = re.compile(r'(?P<tag>[0-9A-F]{8})_mesh(?P<mesh>\d+)_range(?P<off>\d+)_(?P<count>\d+)', re.I)
DYE_FOR_SLOT = {0: 8752, 1: 8753, 2: 8754}

COMPONENTS = {
    5126: ('<f4', 4),
    5123: ('<u2', 2),
    5125: ('<u4', 4),
    5121: ('u1', 1),
}
TYPE_COMPONENTS = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}


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


def image_bytes(graph: dict, blob: bytearray, image_index: int) -> bytes:
    image = graph['images'][image_index]
    if 'bufferView' not in image:
        raise ValueError(f'image {image_index} is not bufferView-backed')
    view = graph['bufferViews'][image['bufferView']]
    if int(view.get('buffer', 0)) != 0:
        raise ValueError('image is not in buffer 0')
    off = int(view.get('byteOffset', 0))
    return bytes(blob[off:off + int(view['byteLength'])])


def append_bytes(graph: dict, blob: bytearray, data: bytes, name: str) -> int:
    pad = (-len(blob)) % 4
    if pad:
        blob.extend(b'\x00' * pad)
    off = len(blob)
    blob.extend(data)
    index = len(graph.setdefault('bufferViews', []))
    graph['bufferViews'].append({
        'buffer': 0,
        'byteOffset': off,
        'byteLength': len(data),
        'name': name,
    })
    return index


def accessor(graph: dict, blob: bytearray, index: int) -> np.ndarray:
    a = graph['accessors'][index]
    if a.get('sparse'):
        raise ValueError(f'sparse accessor {index} is not supported')
    if a['componentType'] not in COMPONENTS or a['type'] not in TYPE_COMPONENTS:
        raise ValueError(f'unsupported accessor {index}: {a}')
    dtype, item_bytes = COMPONENTS[a['componentType']]
    component_count = TYPE_COMPONENTS[a['type']]
    view = graph['bufferViews'][a['bufferView']]
    if int(view.get('buffer', 0)) != 0:
        raise ValueError(f'accessor {index} is not in buffer 0')
    off = int(view.get('byteOffset', 0)) + int(a.get('byteOffset', 0))
    stride = int(view.get('byteStride', item_bytes * component_count))
    if stride == item_bytes * component_count:
        return np.frombuffer(
            blob, dtype=dtype, count=int(a['count']) * component_count, offset=off
        ).reshape((-1, component_count)).copy()
    return np.vstack([
        np.frombuffer(blob, dtype=dtype, count=component_count, offset=off + i * stride)
        for i in range(int(a['count']))
    ])


def range_key(name: str) -> str:
    m = NAME_RE.search(name)
    if not m:
        raise ValueError(f'cannot recover D1 range identity from {name!r}')
    return (
        f"{m.group('tag').upper()}_mesh{int(m.group('mesh'))}_"
        f"range{int(m.group('off'))}_{int(m.group('count'))}"
    ).upper()


def load_selectors(path: Path) -> dict[str, int]:
    d = json.loads(path.read_text())
    if int(d.get('conflict_count', 0)) != 0:
        raise ValueError('stage selector report contains conflicts')
    out: dict[str, int] = {}
    for model in d.get('models', []):
        for mesh in model.get('meshes', []):
            for group in mesh.get('groups', []):
                if not group.get('resolved'):
                    raise ValueError(f"unresolved stage selector: {group.get('name')}")
                key = str(group['name']).upper()
                value = int(group['gear_dye_change_color_index'])
                if key in out and out[key] != value:
                    raise ValueError(f'conflicting selector for {key}')
                out[key] = value
    return out


def load_dyes(path: Path) -> dict[int, dict]:
    d = json.loads(path.read_text())
    out = {int(x['dye_index']): x['dye'] for x in d.get('dyes', []) if x.get('resolved')}
    missing = set(DYE_FOR_SLOT.values()) - set(out)
    if missing:
        raise ValueError(f'missing exact Spektar dyes: {sorted(missing)}')
    for slot, dye_index in DYE_FOR_SLOT.items():
        if int(out[dye_index]['slot_type_index']) != slot:
            raise ValueError(f'dye {dye_index} slot mismatch')
    return out


def load_detail_images(manifest_path: Path, root: Path) -> dict[str, Path]:
    d = json.loads(manifest_path.read_text())
    out = {}
    for row in d.get('textures', []):
        tag = str(row['header']).upper()
        path = root / row['png']
        if not path.is_file():
            raise ValueError(f'missing exact detail texture {tag}: {path}')
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != row['sha256']:
            raise ValueError(f'detail texture SHA mismatch {tag}: {digest} != {row["sha256"]}')
        out[tag] = path
    return out


def blend_overlay(back: np.ndarray, front: np.ndarray) -> np.ndarray:
    return front * np.clip(back * 4.0, 0.0, 1.0) + np.clip(back - 0.25, 0.0, 1.0)


def selector_dye(selector: int, dyes: dict[int, dict]):
    if not 0 <= selector <= 5:
        raise ValueError(f'unsupported armor change-color selector {selector}')
    slot = selector // 2
    secondary = bool(selector & 1)
    dye_index = DYE_FOR_SLOT[slot]
    dye = dyes[dye_index]
    role = 'secondary_color' if secondary else 'primary_color'
    return dye_index, dye, role, np.asarray(dye[role][:3], dtype=np.float32)


def make_mask(triangles_uv: list[np.ndarray], width: int, height: int) -> np.ndarray:
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


def sample_level0_linear_repeat(
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
    """Sample base-level detail with WebGL-style repeat + linear filtering.

    Archived Spasm explicitly sets LINEAR magnification and generated mipmaps with
    LINEAR_MIPMAP_NEAREST minification for square images. A static plate-space bake
    cannot preserve the viewer's screen-dependent implicit mip LOD, so this function
    intentionally reproduces only the source-backed level-0/LINEAR/REPEAT behavior.
    """
    detail_h, detail_w, _ = detail_rgba.shape
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    u = (xx + 0.5) / float(width)
    v = 1.0 - ((yy + 0.5) / float(height))
    du = (u * multiplier[0]) * transform[0] + transform[2]
    dv = (v * multiplier[1]) * transform[1] + transform[3]
    map_x = (np.mod(du, 1.0) * detail_w - 0.5).astype(np.float32)
    map_y = ((1.0 - np.mod(dv, 1.0)) * detail_h - 0.5).astype(np.float32)
    return cv2.remap(
        detail_rgba, map_x, map_y,
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
    a = ap.parse_args()

    graph, blob = read_glb(a.input_glb)
    selectors = load_selectors(a.stage_dyes)
    dyes = load_dyes(a.exact_dyes)
    detail_paths = load_detail_images(a.detail_manifest, a.detail_dir)

    # Aggregate exact triangles by original material, selector, and constant source
    # a_texcoord2 multiplier. The current Spektar source proves each triangle is
    # constant in that multiplier; fail if a future asset is not.
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
        required = {'POSITION', 'TEXCOORD_0', 'TEXCOORD_1', 'NORMAL', 'JOINTS_0', 'WEIGHTS_0'}
        if not required <= set(attrs):
            raise ValueError(f'{mesh.get("name")}: missing source-backed attributes {sorted(required-set(attrs))}')
        if int(primitive.get('mode', 4)) != 4:
            raise ValueError(f'{mesh.get("name")}: expected glTF TRIANGLES mode')
        if 'indices' not in primitive:
            raise ValueError(f'{mesh.get("name")}: indexed primitive required')

        name = mesh.get('name') or node.get('name') or ''
        key = range_key(name)
        if key not in selectors:
            raise ValueError(f'{name}: missing exact stage-part dye selector')
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
                raise ValueError(f'{name}: a_texcoord2 multiplier varies within one triangle')
            value = (float(local[0, 0]), float(local[0, 1]))
            bucket.setdefault(value, []).append(uv[tri])
        active.append((node_index, mesh_index, name, key, old_material, selector, primitive))

    baked_materials = {}
    material_rows = []
    total_overlap = 0

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
            raise ValueError(f'dye {dye_index}: exact detail diffuse {detail_hash} is not in texture manifest')
        detail_rgba = np.asarray(Image.open(detail_paths[detail_hash]).convert('RGBA'), dtype=np.float32) / 255.0
        detail_transform = np.asarray(dye['detail_transform'], dtype=np.float32)

        # Archived source order: base diffuse -> dye-detail overlay -> GStack.R
        # change-color overlay -> gamma correction.
        color_linear = np.power(albedo[..., :3], 2.2)
        covered = np.zeros((height, width), dtype=np.uint8)
        overlap_pixels = 0

        for multiplier_value, triangles_uv in sorted(multiplier_groups.items()):
            mask = make_mask(triangles_uv, width, height)
            overlap = (mask > 0) & (covered > 0)
            overlap_count = int(np.count_nonzero(overlap))
            if overlap_count:
                # Different multiplier buckets mapping to the same base texel would
                # make one baked texture incapable of representing both mappings.
                raise ValueError(
                    f'{plate} selector {selector}: {overlap_count} base texels overlap '
                    f'across different a_texcoord2 multiplier regions'
                )
            overlap_pixels += overlap_count
            covered = np.maximum(covered, mask)
            ys, xs = np.nonzero(mask)
            if not len(xs):
                continue
            x0, x1 = int(xs.min()), int(xs.max()) + 1
            y0, y1 = int(ys.min()), int(ys.max()) + 1
            submask = mask[y0:y1, x0:x1] > 0
            sampled = sample_level0_linear_repeat(
                detail_rgba, width, height, x0, y0, x1, y1,
                np.asarray(multiplier_value, dtype=np.float32), detail_transform,
            )
            alpha = sampled[..., 3:4]
            normalize = (1.0 - alpha) * 0.5
            detail_linear = np.power(
                np.clip(sampled[..., :3] * alpha + normalize, 0.0, 1.0), 2.2
            )
            target = color_linear[y0:y1, x0:x1]
            merged = blend_overlay(detail_linear, target)
            target[submask] = merged[submask]

        mask_r = gstack[..., 0:1]
        dyed = blend_overlay(color_linear, change_color.reshape((1, 1, 3)))
        color_linear = color_linear * (1.0 - mask_r) + dyed * mask_r
        srgb = np.power(np.clip(color_linear, 0.0, 1.0), 1.0 / 2.2)
        rgba = np.concatenate((srgb, np.ones((height, width, 1), dtype=np.float32)), axis=2)
        image = Image.fromarray(np.rint(rgba * 255.0).astype(np.uint8), 'RGBA')
        bio = io.BytesIO()
        image.save(bio, format='PNG', compress_level=6)
        png = bio.getvalue()
        view_index = append_bytes(graph, blob, png, f'{plate}_selector{selector}_spasm_detail_diffuse_png')
        image_index = len(graph.setdefault('images', []))
        graph['images'].append({
            'bufferView': view_index,
            'mimeType': 'image/png',
            'name': f'{plate}_selector{selector}_spasm_detail_diffuse',
        })
        texture_index = len(graph.setdefault('textures', []))
        graph['textures'].append({
            'source': image_index,
            'sampler': graph['textures'][albedo_texture].get('sampler', 0),
            'name': f'{plate}_selector{selector}_spasm_detail_diffuse',
        })
        material_name = f'D1_{plate}_selector{selector}_dye{dye_index}_SPASM_DETAIL_DIFFUSE_UNLIT'
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
                'd1MaterialDiagnostic': 'archived Bungie Spasm detail-diffuse + change-color path baked into a portable unlit texture',
                'd1OriginalMaterialIndex': old_material_index,
                'd1TexturePlateHeader': plate,
                'd1GearDyeChangeColorIndex': selector,
                'd1DyeIndex': dye_index,
                'd1DyeColorRole': color_role,
                'd1ChangeColor': [float(x) for x in change_color],
                'd1DetailDiffuseTextureHash': detail_hash,
                'd1DetailTransform': [float(x) for x in detail_transform],
                'd1DistinctATexcoord2Values': len(multiplier_groups),
                'd1CoveredPixels': int(np.count_nonzero(covered)),
                'd1OverlapPixelsAcrossMultiplierMasks': overlap_pixels,
                'd1ShaderOrder': 'diffuse^2.2 -> detail normalization/pow -> blend_overlay(detail,diffuse) -> mix(diffuse,blend_overlay(diffuse,changeColor),GStack.R) -> gamma',
                'd1Sampling': 'level-0 LINEAR with REPEAT; archived Spasm runtime uses LINEAR and generated mipmaps, whose screen-dependent implicit mip LOD cannot be frozen into one static texture',
                'd1DetailNormalStatus': 'not_applied_native_tangent_handedness_and_full_normal_path_not_yet_source_closed',
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
            'BAKED', plate, 'selector', selector, 'dye', dye_index,
            'detail', detail_hash, 'multipliers', len(multiplier_groups),
            'covered', int(np.count_nonzero(covered)), 'overlap', overlap_pixels,
        )

    for _node, _mesh, _name, _key, old_material, selector, primitive in active:
        primitive['material'] = baked_materials[(old_material, selector)]

    used = graph.setdefault('extensionsUsed', [])
    if 'KHR_materials_unlit' not in used:
        used.append('KHR_materials_unlit')
    graph.setdefault('extras', {})['d1SpasmDetailDiffuseDiagnostic'] = {
        'activePrimitiveCount': len(active),
        'bakedMaterialCount': len(baked_materials),
        'detailDiffuse': 'exact retail texture selected directly by exact SDye_D1 record',
        'detailUV': 'exact source a_texcoord2 multiplier exported as TEXCOORD_1 plus exact SDye_D1 detail_transform',
        'fragmentOrder': 'archived Bungie D1 Spasm GearShader source',
        'textureSampling': 'level-0 LINEAR/REPEAT portable bake; runtime mip LOD remains view dependent',
        'detailNormal': 'not applied yet',
        'overlapConflictPixels': total_overlap,
    }

    write_glb(a.out, graph, blob)
    report = {
        'schema': 'd1_guardian_spasm_detail_diffuse_bake/v1',
        'input': str(a.input_glb),
        'output': str(a.out),
        'output_bytes': a.out.stat().st_size,
        'output_sha256': hashlib.sha256(a.out.read_bytes()).hexdigest(),
        'active_primitive_count': len(active),
        'baked_material_count': len(baked_materials),
        'overlap_conflict_pixels': total_overlap,
        'materials': material_rows,
        'policy': graph['extras']['d1SpasmDetailDiffuseDiagnostic'],
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({
        'active': len(active),
        'baked_materials': len(baked_materials),
        'overlap_conflict_pixels': total_overlap,
        'bytes': a.out.stat().st_size,
        'sha256': report['output_sha256'],
    }, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
