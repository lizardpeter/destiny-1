#!/usr/bin/env python3
"""Apply the six proven Gjallarhorn arrangement-1229 texture plates to a proof GLB.

This is deliberately an interchange/presentation layer.  It preserves the exact
retail six-model geometry and each primitive's native material-hash provenance,
while duplicating portable glTF materials per owning model so that each model can
sample its own byte-proven EntityResource texture plate.

Albedo and normal plates are connected to core glTF PBR.  GStack is embedded as
an image and referenced in material extras, but is not interpreted as metallic /
roughness because the complete D1 deferred GStack semantics are not yet closed.
Likewise, gear dye indices remain source provenance; this tool does not invent
Gjallarhorn's final dye colors.
"""
from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path

from pygltflib import (
    GLTF2, Image, Texture, Sampler, Material, PbrMetallicRoughness,
    TextureInfo, NormalMaterialTexture,
)

MODEL_PLATES = {
    '80A743A6': '80A39C90',
    '80A73BAB': '80A398B5',
    '80A72202': '80A38D5D',
    '80A7317B': '80A39407',
    '80A73256': '80A3947C',
    '80A73D13': '80A7E1B4',
}

LINEAR = 9729
LINEAR_MIPMAP_LINEAR = 9987
CLAMP_TO_EDGE = 33071


def data_uri(path: Path) -> str:
    return 'data:image/png;base64,' + base64.b64encode(path.read_bytes()).decode('ascii')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('input_glb', type=Path)
    ap.add_argument('--plate-dir', type=Path, required=True)
    ap.add_argument('--plate-report', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    a = ap.parse_args()

    gltf = GLTF2().load_binary(str(a.input_glb))
    plate_report = json.loads(a.plate_report.read_text())
    rows = {r['model_tag']: r for r in plate_report['models']}
    if set(rows) != set(MODEL_PLATES):
        raise RuntimeError(f'plate report models differ: {sorted(rows)}')

    # Identify each glTF mesh's owning model from the byte-proven geometry export.
    mesh_owner: dict[int, str] = {}
    for node in gltf.nodes:
        if node.mesh is None:
            continue
        extras = node.extras or {}
        model = extras.get('d1Model')
        if model not in MODEL_PLATES:
            raise RuntimeError(f'mesh node {node.name!r} lacks recognized d1Model')
        mesh_owner[int(node.mesh)] = model
    if set(mesh_owner.values()) != set(MODEL_PLATES):
        raise RuntimeError(f'not all six model owners represented: {mesh_owner}')

    gltf.samplers.append(Sampler(
        magFilter=LINEAR,
        minFilter=LINEAR_MIPMAP_LINEAR,
        wrapS=CLAMP_TO_EDGE,
        wrapT=CLAMP_TO_EDGE,
    ))
    sampler_index = len(gltf.samplers) - 1

    plate_assets = {}
    for model, header in MODEL_PLATES.items():
        role_assets = {}
        for role in ('albedo', 'normal', 'gstack'):
            path = a.plate_dir / f'{header}_{role}_plate.png'
            if not path.is_file():
                raise FileNotFoundError(path)
            ii = len(gltf.images)
            gltf.images.append(Image(
                name=f'{model}_{header}_{role}',
                uri=data_uri(path),
                extras={
                    'd1Model': model,
                    'd1TexturePlateHeader': header,
                    'd1TexturePlateRole': role,
                    'nativeInterpretation': role if role in ('albedo','normal') else 'GStack preserved; portable semantics unresolved',
                },
            ))
            if role in ('albedo', 'normal'):
                ti = len(gltf.textures)
                gltf.textures.append(Texture(name=f'{model}_{role}', source=ii, sampler=sampler_index))
            else:
                ti = None
            role_assets[role] = {'image': ii, 'texture': ti, 'path': str(path)}
        plate_assets[model] = role_assets

    old_materials = list(gltf.materials)
    material_map = {}
    material_rows = []
    new_materials = []

    # Keep no orphaned neutral placeholder materials in the final portable view.
    for mesh_index, mesh in enumerate(gltf.meshes):
        model = mesh_owner[mesh_index]
        prow = rows[model]
        plate_header = MODEL_PLATES[model]
        for prim in mesh.primitives:
            old_index = int(prim.material)
            key = (model, old_index)
            new_index = material_map.get(key)
            if new_index is None:
                old = old_materials[old_index]
                native_extras = dict(old.extras or {})
                native_hash = native_extras.get('d1DisplayMaterial')
                native_candidates = native_extras.get('nativeMaterialCandidates', [])
                extras = {
                    **native_extras,
                    'd1Model': model,
                    'd1TexturePlateHeader': plate_header,
                    'd1AlbedoPlate': prow['plate_tags']['albedo'],
                    'd1NormalPlate': prow['plate_tags']['normal'],
                    'd1GStackPlate': prow['plate_tags']['gstack'],
                    'd1GStackImageIndex': plate_assets[model]['gstack']['image'],
                    'portablePolicy': 'exact model plate albedo+normal; GStack preserved but not mapped to glTF metallic/roughness; gear dyes not synthesized',
                }
                mat = Material(
                    name=f'D1_{model}_{native_hash or old_index}_PLATE_PBR',
                    pbrMetallicRoughness=PbrMetallicRoughness(
                        baseColorTexture=TextureInfo(index=plate_assets[model]['albedo']['texture']),
                        metallicFactor=0.0,
                        roughnessFactor=0.65,
                    ),
                    normalTexture=NormalMaterialTexture(index=plate_assets[model]['normal']['texture']),
                    doubleSided=old.doubleSided,
                    extras=extras,
                )
                new_index = len(new_materials)
                new_materials.append(mat)
                material_map[key] = new_index
                material_rows.append({
                    'model_tag': model,
                    'old_material_index': old_index,
                    'new_material_index': new_index,
                    'native_material_hash': native_hash,
                    'native_material_candidates': native_candidates,
                    'plate_header': plate_header,
                    'albedo_plate': prow['plate_tags']['albedo'],
                    'normal_plate': prow['plate_tags']['normal'],
                    'gstack_plate': prow['plate_tags']['gstack'],
                })
            prim.material = new_index

    gltf.materials = new_materials
    extras = gltf.extras or {}
    extras['d1GjallarhornPortableTextureLayer'] = {
        'arrangement': 1229,
        'modelPlateHeaders': MODEL_PLATES,
        'geometryChanged': False,
        'albedoAndNormalConnected': True,
        'gstackEmbeddedButNotInterpreted': True,
        'gearDyesApplied': False,
    }
    gltf.extras = extras
    gltf.asset.generator = 'destiny-1 Gjallarhorn 1229 exact geometry + proven plate portable layer'

    a.out.parent.mkdir(parents=True, exist_ok=True)
    gltf.save_binary(str(a.out))

    check = GLTF2().load_binary(str(a.out))
    if len(check.meshes) != len(gltf.meshes):
        raise RuntimeError('mesh count changed during texture application')
    report = {
        'input_glb': str(a.input_glb),
        'output_glb': str(a.out),
        'output_bytes': a.out.stat().st_size,
        'model_count': 6,
        'mesh_count': len(check.meshes),
        'material_count': len(check.materials),
        'image_count': len(check.images),
        'texture_count': len(check.textures),
        'plate_assets': plate_assets,
        'materials': material_rows,
        'policy': {
            'geometry': 'unchanged exact arrangement-1229 LOD1 geometry',
            'albedo_normal': 'byte-proven per-model texture plates connected to core glTF',
            'gstack': 'embedded/proven but not interpreted as glTF PBR channels',
            'dyes': 'not applied; final native dye semantics/colors remain separate work',
        },
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('plate_assets','materials')}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
