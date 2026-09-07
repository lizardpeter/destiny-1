#!/usr/bin/env python3
"""Build Blender-friendly Crota R6 views from the source-closed R5 GLBs.

This adapter changes only portable preview packaging. It does not alter geometry,
JOINTS/WEIGHTS, skin inverse binds, joint transforms, or animation channel payloads.

Two corrections are made:

1. D1 texture 8108E7B6 is a single-channel BC4 control resource. The exact retail PNG
   is preserved untouched, but glTF Base Color must not consume that red-only PNG as
   RGB. A derived PREVIEW_ONLY RGB image is appended with R replicated into RGB.
2. For Blender animation inspection, an exact one-clip low-motion view can be emitted
   using source-selected clip 809D9D3E. The full 82-clip view can also be reordered so
   that same exact clip is first. No clip payload is modified or fabricated.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
from pathlib import Path

from PIL import Image

from d1_gltf_bind_exact_shader_textures_v2 import append_blob, read_glb, write_glb

SCALAR_SOURCE = '8108E7B6'
LOW_MOTION_CLIP = '809D9D3E'
LOW_MOTION_NAME = f'D1_CROTA_{LOW_MOTION_CLIP}'
CONTROL_MATERIALS = {'8108E667', '8108E66B'}
PROCEDURAL_MATERIALS = {'8108E7A9', '8108E7B2'}
ATLAS_MATERIALS = {'8108E7AA', '8108E7B3'}
AUX_MATERIALS = {'8108E7B1'}
EXPECTED_MATERIALS = CONTROL_MATERIALS | PROCEDURAL_MATERIALS | ATLAS_MATERIALS | AUX_MATERIALS
EXACT_TEXTURES = {'8108E7B6','80AACF2A','80AAD0E1','8108E951','8108E952'}


def hfile(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def norm(x) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def image_bytes(doc: dict, blob: bytes, image: dict) -> bytes:
    bv = doc['bufferViews'][int(image['bufferView'])]
    off = int(bv.get('byteOffset', 0))
    n = int(bv['byteLength'])
    return blob[off:off+n]


def scalar_rgb_png(raw: bytes) -> bytes:
    im = Image.open(io.BytesIO(raw)).convert('RGBA')
    r, _, _, a = im.split()
    rgb = Image.merge('RGBA', (r, r, r, a))
    out = io.BytesIO()
    rgb.save(out, format='PNG', compress_level=9, optimize=False)
    return out.getvalue()


def animation_clip(anim: dict) -> str | None:
    ex = anim.get('extras') or {}
    h = ex.get('d1OwnerSelectedClip')
    if h:
        return norm(h)
    name = str(anim.get('name') or '')
    if name.upper().startswith('D1_CROTA_'):
        return norm(name.split('_')[-1])
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('input_glb', type=Path)
    ap.add_argument('--animation-mode', choices=('none','one-low-motion','all-low-motion-first'), required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    a = ap.parse_args()

    src, srcbin = read_glb(a.input_glb)
    doc = copy.deepcopy(src)
    mats = doc.get('materials') or []
    if len(mats) != 7:
        raise SystemExit(f'expected 7 Crota materials, got {len(mats)}')
    by_mat = {}
    for i, m in enumerate(mats):
        h = norm((m.get('extras') or {}).get('d1_material_taghash', ''))
        if h in by_mat:
            raise SystemExit(f'duplicate material {h}')
        by_mat[h] = i
    if set(by_mat) != EXPECTED_MATERIALS:
        raise SystemExit(f'material set drift: {sorted(set(by_mat)^EXPECTED_MATERIALS)}')

    exact_images = {}
    for i, img in enumerate(doc.get('images') or []):
        h = norm((img.get('extras') or {}).get('d1_taghash', ''))
        if h in EXACT_TEXTURES:
            exact_images[h] = (i, img)
    if set(exact_images) != EXACT_TEXTURES:
        raise SystemExit(f'exact image set drift: {sorted(set(exact_images)^EXACT_TEXTURES)}')

    scalar_i, scalar_img = exact_images[SCALAR_SOURCE]
    scalar_raw = image_bytes(doc, srcbin, scalar_img)
    scalar_sha = hashlib.sha256(scalar_raw).hexdigest()
    preview_raw = scalar_rgb_png(scalar_raw)
    preview_sha = hashlib.sha256(preview_raw).hexdigest()

    bindata = srcbin
    bvi, bindata = append_blob(doc, bindata, preview_raw, 'D1_CROTA_PREVIEW_SCALAR_RGB_8108E7B6_PNG')
    preview_image_index = len(doc.setdefault('images', []))
    doc['images'].append({
        'name': 'D1_PREVIEW_SCALAR_RGB_8108E7B6',
        'mimeType': 'image/png',
        'bufferView': bvi,
        'extras': {
            'd1_preview_only': True,
            'd1_derived_from_exact_texture': SCALAR_SOURCE,
            'd1_derivation': 'replicate exact decoded R scalar into RGB; preserve alpha',
            'd1_source_png_sha256': scalar_sha,
            'd1_preview_png_sha256': preview_sha,
        },
    })
    preview_texture_index = len(doc.setdefault('textures', []))
    doc['textures'].append({
        'name': 'D1_PREVIEW_SCALAR_RGB_8108E7B6',
        'source': preview_image_index,
        'extras': {
            'd1_preview_only': True,
            'd1_derived_from_exact_texture': SCALAR_SOURCE,
        },
    })

    material_rows = []
    for mh, mi in sorted(by_mat.items()):
        m = doc['materials'][mi]
        pbr = m.setdefault('pbrMetallicRoughness', {})
        pbr['metallicFactor'] = 0.0
        pbr['roughnessFactor'] = 0.82
        ex = m.setdefault('extras', {})
        if mh in PROCEDURAL_MATERIALS:
            # Exact source cbuffer [0.373239398, 2, 1.740176, 1] normalized by its
            # dominant 2.0 component; only the portable scalar visualization is derived.
            factor = [0.18661969900131226, 1.0, 0.8700880408287048, 1.0]
            pbr['baseColorTexture'] = {'index': preview_texture_index, 'texCoord': 0}
            pbr['baseColorFactor'] = factor
            policy = 'PREVIEW_SCALAR_RGB_WITH_SOURCE_CBUFFER_TINT'
        elif mh in CONTROL_MATERIALS:
            # Native PS 8108E7B7 writes control/deferred data rather than portable
            # final colour. Keep the exact resources in extras, but visualize its
            # scalar mask as dark Hive-green instead of the invalid red-channel RGB.
            factor = [0.10, 0.18, 0.14, 1.0]
            pbr['baseColorTexture'] = {'index': preview_texture_index, 'texCoord': 0}
            pbr['baseColorFactor'] = factor
            policy = 'PREVIEW_DEFERRED_CONTROL_SCALAR_DARK_HIVE_GREEN'
        else:
            # Atlas/direct-colour materials already have correct portable bindings from R5.
            factor = pbr.get('baseColorFactor')
            policy = 'KEEP_R5_DIRECT_NATIVE_COLOR_PREVIEW'
        ex['d1_r6_blender_preview_policy'] = policy
        ex['d1_r6_preview_scalar_texture_index'] = preview_texture_index if mh in (CONTROL_MATERIALS|PROCEDURAL_MATERIALS) else None
        material_rows.append({'material': mh, 'index': mi, 'policy': policy, 'baseColorFactor': factor, 'baseColorTexture': pbr.get('baseColorTexture')})

    original_anims = list(src.get('animations') or [])
    clips = [animation_clip(x) for x in original_anims]
    if original_anims:
        if len(original_anims) != 82 or len(set(clips)) != 82 or LOW_MOTION_CLIP not in clips:
            raise SystemExit(f'animation library drift: count={len(original_anims)} low_motion_present={LOW_MOTION_CLIP in clips}')
    if a.animation_mode == 'none':
        doc['animations'] = []
    elif a.animation_mode == 'one-low-motion':
        if not original_anims:
            raise SystemExit('one-low-motion requires animated R5 input')
        row = [x for x in original_anims if animation_clip(x) == LOW_MOTION_CLIP]
        if len(row) != 1:
            raise SystemExit('low-motion clip not unique')
        doc['animations'] = [row[0]]
    else:
        if not original_anims:
            raise SystemExit('all-low-motion-first requires animated R5 input')
        first = [x for x in original_anims if animation_clip(x) == LOW_MOTION_CLIP]
        rest = [x for x in original_anims if animation_clip(x) != LOW_MOTION_CLIP]
        doc['animations'] = first + rest

    doc.setdefault('asset', {}).setdefault('extras', {})['d1CrotaR6BlenderPreview'] = {
        'schema': 'd1_gltf_crota_r6_preview_fix/v1',
        'sourceExactTextureCount': 5,
        'derivedPreviewImageCount': 1,
        'scalarSourceTexture': SCALAR_SOURCE,
        'lowMotionExactClip': LOW_MOTION_CLIP,
        'animationMode': a.animation_mode,
        'geometrySkinAnimationPayloadPolicy': 'unchanged; only material preview JSON, one appended preview PNG, and animation-array packaging change',
    }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    write_glb(a.out, doc, bindata)
    chk, chkbin = read_glb(a.out)
    if chkbin[:len(srcbin)] != srcbin:
        raise SystemExit('R5 binary chunk is not exact R6 prefix')
    for key in ('meshes','nodes','skins','scenes'):
        if chk.get(key, []) != src.get(key, []):
            raise SystemExit(f'{key} changed in R6 preview adapter')
    if len(chk.get('images') or []) != len(src.get('images') or []) + 1:
        raise SystemExit('derived preview image count drift')
    if len(chk.get('textures') or []) != len(src.get('textures') or []) + 1:
        raise SystemExit('derived preview texture count drift')
    # All exact retail images must survive structurally unchanged.
    for h, (i, _) in exact_images.items():
        if chk['images'][i] != src['images'][i]:
            raise SystemExit(f'exact image metadata changed for {h}')
    actual_clips = [animation_clip(x) for x in chk.get('animations') or []]
    if a.animation_mode == 'none' and actual_clips:
        raise SystemExit('none mode retained animations')
    if a.animation_mode == 'one-low-motion' and actual_clips != [LOW_MOTION_CLIP]:
        raise SystemExit(f'one-low-motion drift {actual_clips}')
    if a.animation_mode == 'all-low-motion-first':
        if len(actual_clips) != 82 or actual_clips[0] != LOW_MOTION_CLIP or set(actual_clips) != set(clips):
            raise SystemExit('full animation library/order drift')

    report = {
        'schema': 'd1_gltf_crota_r6_preview_fix/v1',
        'status': 'D1_CROTA_R6_BLENDER_PREVIEW_COMPLETE',
        'input_glb': str(a.input_glb),
        'input_sha256': hfile(a.input_glb),
        'output_glb': str(a.out),
        'output_sha256': hfile(a.out),
        'output_bytes': a.out.stat().st_size,
        'animation_mode': a.animation_mode,
        'animation_count': len(chk.get('animations') or []),
        'first_animation_clip': actual_clips[0] if actual_clips else None,
        'mesh_count': len(chk.get('meshes') or []),
        'skin_count': len(chk.get('skins') or []),
        'joint_count': len((chk.get('skins') or [{}])[0].get('joints') or []) if chk.get('skins') else 0,
        'material_count': len(chk.get('materials') or []),
        'exact_retail_image_count': 5,
        'derived_preview_image_count': 1,
        'derived_scalar_source': SCALAR_SOURCE,
        'source_scalar_png_sha256': scalar_sha,
        'preview_scalar_rgb_png_sha256': preview_sha,
        'preview_image_index': preview_image_index,
        'preview_texture_index': preview_texture_index,
        'material_rows': material_rows,
        'binary_prefix_preserved': True,
        'low_motion_exact_clip': LOW_MOTION_CLIP,
        'policy': 'Exact retail textures remain embedded unchanged. The additional RGB scalar image and all non-native PBR roles are explicitly preview-only Blender adapters.',
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('status','animation_mode','animation_count','first_animation_clip','mesh_count','joint_count','material_count','output_bytes','output_sha256')}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
