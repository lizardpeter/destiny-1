#!/usr/bin/env python3
"""Bind exact D1 Guardian model-parent texture plates into an existing GLB.

This stage intentionally does less than a native D1 shader conversion. It uses
only already-proven retail relations:

  exported primitive name -> exact s_entity_model FileHash
  s_entity_model -> exact model-parent TexturePlatesROI header
  plate header -> exact composed albedo / normal / GStack images

Albedo and normal are attached through standard glTF texture slots so the result
is immediately viewable. GStack is embedded in the GLB and referenced through
material extras, but it is NOT mapped to metallic/roughness/occlusion until D1's
channel semantics are source-closed. The neutral glTF metallic/roughness factors
are preview compatibility values, not claims about the retail D1 shader.

No texture is resized, recolored, repacked, or synthesized here.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from pygltflib import (
    GLTF2,
    BufferView,
    Image,
    Material,
    NormalMaterialTexture,
    PbrMetallicRoughness,
    Sampler,
    Texture,
    TextureInfo,
)

NAME_RE = re.compile(r'(?P<tag>[0-9A-F]{8})_mesh(?P<mesh>\d+)_range(?P<off>\d+)_(?P<count>\d+)', re.I)


def align4(blob: bytearray) -> None:
    while len(blob) & 3:
        blob.append(0)


def embed_png(g: GLTF2, blob: bytearray, path: Path, name: str) -> int:
    data = path.read_bytes()
    if not data.startswith(b'\x89PNG\r\n\x1a\n'):
        raise ValueError(f'{path}: expected PNG')
    align4(blob)
    off = len(blob)
    blob.extend(data)
    bv = len(g.bufferViews)
    g.bufferViews.append(BufferView(buffer=0, byteOffset=off, byteLength=len(data)))
    ii = len(g.images)
    g.images.append(Image(name=name, mimeType='image/png', bufferView=bv))
    return ii


def exact_model_plate_map(visual: dict) -> dict[str, str]:
    out: dict[str, str] = {}
    for m in visual.get('models', []):
        tag = str(m.get('tag_hash') or '').upper()
        rp = m.get('render_parent') or {}
        rows = rp.get('texture_plates_roi_entries') or []
        headers = [str(x.get('texture_plate_header_tag_hash') or '').upper() for x in rows]
        headers = [x for x in headers if x]
        if len(headers) != 1:
            raise ValueError(f'{tag}: expected exactly one proven TexturePlatesROI header, got {headers}')
        if tag in out and out[tag] != headers[0]:
            raise ValueError(f'{tag}: conflicting plate headers {out[tag]} / {headers[0]}')
        out[tag] = headers[0]
    return out


def exact_plate_images(report: dict, plate_dir: Path) -> dict[str, dict[str, Path]]:
    out: dict[str, dict[str, Path]] = {}
    for p in report.get('plates', []):
        header = str(p.get('header_tag') or '').upper()
        role = str(p.get('role') or '').lower()
        rel = p.get('output_png')
        if not header or role not in {'albedo', 'normal', 'gstack'} or not rel:
            raise ValueError(f'malformed composed plate row: {p}')
        path = plate_dir / str(rel)
        if not path.is_file():
            path = plate_dir / Path(str(rel)).name
        if not path.is_file():
            raise FileNotFoundError(f'{header} {role}: plate image not found for {rel}')
        out.setdefault(header, {})[role] = path
    for h, roles in out.items():
        if set(roles) != {'albedo', 'normal', 'gstack'}:
            raise ValueError(f'{h}: incomplete exact plate roles {sorted(roles)}')
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('input_glb', type=Path)
    ap.add_argument('--visual-context', type=Path, required=True)
    ap.add_argument('--composed-plate-report', type=Path, required=True)
    ap.add_argument('--plate-dir', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    a = ap.parse_args()

    visual = json.loads(a.visual_context.read_text())
    plates = json.loads(a.composed_plate_report.read_text())
    if visual.get('body_role') != 'masculine':
        raise ValueError(f"expected masculine visual context, got {visual.get('body_role')!r}")
    if visual.get('model_count') != 5 or visual.get('texture_plate_header_count') != 5 or visual.get('errors'):
        raise ValueError('visual-context report is not the proven five-model/five-header clean census')
    if plates.get('header_count') != 5 or plates.get('plate_image_count') != 15 or plates.get('allow_resize'):
        raise ValueError('composed plate report is not the exact five-header/15-image non-resampled set')
    if any(x.get('resized') for p in plates.get('plates', []) for x in p.get('placements', [])):
        raise ValueError('refusing plate report containing resized source placements')

    model_to_header = exact_model_plate_map(visual)
    header_to_images = exact_plate_images(plates, a.plate_dir)
    if set(model_to_header.values()) != set(header_to_images):
        raise ValueError(
            f'visual-context/composed-header mismatch: {sorted(set(model_to_header.values()))} != {sorted(header_to_images)}'
        )

    g = GLTF2().load_binary(str(a.input_glb))
    if len(g.buffers) != 1:
        raise ValueError(f'expected one-buffer GLB, got {len(g.buffers)}')
    blob = bytearray(g.binary_blob() or b'')
    g.bufferViews = g.bufferViews or []
    g.images = g.images or []
    g.textures = g.textures or []
    g.samplers = g.samplers or []
    g.materials = g.materials or []

    sampler_index = len(g.samplers)
    g.samplers.append(Sampler(magFilter=9729, minFilter=9987, wrapS=10497, wrapT=10497))

    material_for_model: dict[str, int] = {}
    texture_rows = []
    for model_tag in sorted(model_to_header):
        header = model_to_header[model_tag]
        role_texture: dict[str, int] = {}
        for role in ('albedo', 'normal', 'gstack'):
            path = header_to_images[header][role]
            image_index = embed_png(g, blob, path, f'{header}_{role}')
            texture_index = len(g.textures)
            g.textures.append(Texture(name=f'{header}_{role}', sampler=sampler_index, source=image_index))
            role_texture[role] = texture_index
            texture_rows.append({
                'model_tag': model_tag,
                'plate_header': header,
                'role': role,
                'source_png': str(path),
                'image_index': image_index,
                'texture_index': texture_index,
                'bytes': path.stat().st_size,
            })

        material_index = len(g.materials)
        g.materials.append(Material(
            name=f'D1_{model_tag}_{header}_plate_preview',
            pbrMetallicRoughness=PbrMetallicRoughness(
                baseColorTexture=TextureInfo(index=role_texture['albedo'], texCoord=0),
                baseColorFactor=[1.0, 1.0, 1.0, 1.0],
                metallicFactor=0.0,
                roughnessFactor=1.0,
            ),
            normalTexture=NormalMaterialTexture(index=role_texture['normal'], texCoord=0, scale=1.0),
            extras={
                'd1TexturePlateHeader': header,
                'd1GStackTextureIndex': role_texture['gstack'],
                'd1GStackPolicy': 'embedded_exact_retail_plate_not_mapped_to_PBR_until_channel_semantics_are_proven',
                'd1PreviewPbrPolicy': 'metallic=0 roughness=1 are neutral viewer defaults, not decoded D1 material parameters',
            },
        ))
        material_for_model[model_tag] = material_index

    primitive_rows = []
    model_primitive_counts = {x: 0 for x in model_to_header}
    for mesh_index, mesh in enumerate(g.meshes):
        m = NAME_RE.search(mesh.name or '')
        if m is None:
            raise ValueError(f'cannot recover source model from GLB mesh name {mesh.name!r}')
        model_tag = m.group('tag').upper()
        if model_tag not in material_for_model:
            raise ValueError(f'{mesh.name}: model {model_tag} absent from visual-context map')
        if len(mesh.primitives) != 1:
            raise ValueError(f'{mesh.name}: expected exactly one primitive')
        prim = mesh.primitives[0]
        if prim.attributes.TEXCOORD_0 is None:
            raise ValueError(f'{mesh.name}: exact plate binding requires corrected TEXCOORD_0')
        prim.material = material_for_model[model_tag]
        model_primitive_counts[model_tag] += 1
        primitive_rows.append({
            'mesh_index': mesh_index,
            'mesh_name': mesh.name,
            'model_tag': model_tag,
            'plate_header': model_to_header[model_tag],
            'material_index': prim.material,
            'texcoord_accessor': prim.attributes.TEXCOORD_0,
        })

    if len(primitive_rows) != 69:
        raise ValueError(f'expected 69 Spektar primitives, got {len(primitive_rows)}')
    if any(v <= 0 for v in model_primitive_counts.values()):
        raise ValueError(f'not every exact model received a material: {model_primitive_counts}')

    g.extras = {
        **(g.extras or {}),
        'd1ExactTexturePlateBinding': {
            'modelToPlateHeader': model_to_header,
            'plateRoles': ['albedo', 'normal', 'gstack'],
            'sourceTexturePolicy': 'exact composed retail plates; no resizing/repacking/recoloring in binder',
            'gstackPolicy': 'embedded but intentionally not interpreted as standard PBR channels',
            'dyePolicy': 'not applied; D1 gear dye resolution remains a separate source-closure stage',
        },
    }
    align4(blob)
    g.buffers[0].byteLength = len(blob)
    g.set_binary_blob(bytes(blob))
    a.out.parent.mkdir(parents=True, exist_ok=True)
    g.save_binary(str(a.out))

    report = {
        'schema': 'd1_guardian_texture_plate_bind/v1',
        'input': str(a.input_glb),
        'output': str(a.out),
        'output_bytes': a.out.stat().st_size,
        'model_count': len(model_to_header),
        'primitive_count': len(primitive_rows),
        'material_count_added': len(material_for_model),
        'image_count_added': len(texture_rows),
        'texture_count_added': len(texture_rows),
        'model_to_plate_header': model_to_header,
        'model_primitive_counts': model_primitive_counts,
        'textures': texture_rows,
        'primitives': primitive_rows,
        'policy': (
            'Albedo and normal use exact composed retail model-parent plates. Exact GStack is embedded and provenance-linked '
            'but receives no metallic/roughness/occlusion interpretation. D1 dye parameters are not fabricated.'
        ),
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + '\n')
    print('SUCCESS', report['model_count'], 'models', report['primitive_count'], 'primitives',
          report['image_count_added'], 'exact plate images embedded')
    for model, header in sorted(model_to_header.items()):
        print(model, '->', header, 'primitives', model_primitive_counts[model])
    print('wrote', a.out, a.out.stat().st_size, 'bytes')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
