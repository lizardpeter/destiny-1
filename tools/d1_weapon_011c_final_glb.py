#!/usr/bin/env python3
"""Build the corrected final-snapshot D1 ROI PS4 011C weapon GLB.

This is deliberately a thin specialization of d1_weapon_011c_test_glb.py so
all proven geometry, rigid Pedestal attachment and 12-clip animation logic stay
identical.  The historical test fixture hard-coded tombstoned material
80A3CD9A; this wrapper switches the native main-shell binding to the material
actually serialized by final model 80A39E12: 80A382A6.

Core glTF PBR remains explicitly portable/approximate.  Exact entity texture
plates drive the main shell.  Direct shader resources (current cubemap,
secondary 2D texture, GStack and the small-component decal atlas) are embedded
as provenance images until their complete native shader semantics are proven.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import d1_weapon_011c_test_glb as base

FINAL_MAIN_MATERIAL = "80A382A6"
FINAL_MAIN_CUBE = "80AB0B74"
FINAL_MAIN_DIRECT_2D = "80A3D4D6"
SMALL_MATERIAL = "80A3D294"
SMALL_ATLAS = "80AA9D4D"

_SMALL_REPORT: dict | None = None


def add_final_materials(gltf, texture_root: Path, material_report: dict, plate_report: dict) -> dict[str, int]:
    if _SMALL_REPORT is None:
        raise RuntimeError("small material report was not loaded")

    gltf.samplers.append(base.Sampler(
        magFilter=base.LINEAR,
        minFilter=base.LINEAR_MIPMAP_LINEAR,
        wrapS=base.CLAMP_TO_EDGE,
        wrapT=base.CLAMP_TO_EDGE,
    ))

    def add_image(name: str, path: Path, extras: dict | None = None) -> int:
        if not path.exists():
            raise FileNotFoundError(path)
        idx = len(gltf.images)
        gltf.images.append(base.Image(name=name, uri=base.data_uri(path), extras=extras or {}))
        return idx

    def add_texture(image_index: int, name: str) -> int:
        idx = len(gltf.textures)
        gltf.textures.append(base.Texture(name=name, source=image_index, sampler=0))
        return idx

    plate_dir = texture_root / "plates"
    src_dir = texture_root / "source"

    albedo_i = add_image(
        "80A39E19_albedo_plate",
        plate_dir / "80A39E17_albedo_plate.png",
        {"d1PlateHeader": base.TEXTURE_PLATE_HEADER, "d1Plate": "80A39E19", "d1Source": "80A3D844"},
    )
    normal_i = add_image(
        "80A39E1A_normal_plate",
        plate_dir / "80A39E17_normal_plate.png",
        {"d1PlateHeader": base.TEXTURE_PLATE_HEADER, "d1Plate": "80A39E1A", "d1Source": "80A3D845", "nativeFormat": "BC5"},
    )
    gstack_i = add_image(
        "80A39E1B_gstack_plate_NATIVE_ONLY",
        plate_dir / "80A39E17_gstack_plate.png",
        {"d1PlateHeader": base.TEXTURE_PLATE_HEADER, "d1Plate": "80A39E1B", "d1Source": "80A3D846", "nativeOnly": True},
    )
    direct2d_i = add_image(
        f"{FINAL_MAIN_DIRECT_2D}_direct_shader_texture_NATIVE_ONLY",
        src_dir / f"{FINAL_MAIN_DIRECT_2D}_128x128_BC1.png",
        {"d1TagHash": FINAL_MAIN_DIRECT_2D, "textureIndex": 1, "nativeOnly": True},
    )

    cube_images = []
    for face in range(6):
        cube_images.append(add_image(
            f"{FINAL_MAIN_CUBE}_cube_face{face}_NATIVE_ONLY",
            src_dir / f"{FINAL_MAIN_CUBE}_128x128_BC1_face{face}.png",
            {"d1TagHash": FINAL_MAIN_CUBE, "textureIndex": 0, "cubeFace": face, "nativeOnly": True},
        ))

    small_atlas_i = add_image(
        f"{SMALL_ATLAS}_small_component_atlas_NATIVE_ONLY",
        src_dir / f"{SMALL_ATLAS}_1024x1024_BC3.png",
        {
            "d1TagHash": SMALL_ATLAS,
            "d1Material": SMALL_MATERIAL,
            "textureIndex": 0,
            "nativeFormat": "BC3",
            "nativeOnly": True,
            "semanticStatus": "exact texture bytes resolved; shader-role dataflow must authorize any core glTF mapping",
        },
    )

    albedo_t = add_texture(albedo_i, "D1_weapon_albedo_plate")
    normal_t = add_texture(normal_i, "D1_weapon_normal_plate")

    main_idx = len(gltf.materials)
    gltf.materials.append(base.Material(
        name=f"D1_{FINAL_MAIN_MATERIAL}_MainWeapon_PORTABLE",
        alphaMode="OPAQUE",
        pbrMetallicRoughness=base.PbrMetallicRoughness(
            baseColorTexture=base.TextureInfo(index=albedo_t, texCoord=0),
            metallicFactor=0.0,
            roughnessFactor=0.65,
        ),
        normalTexture=base.NormalMaterialTexture(index=normal_t, texCoord=0, scale=1.0),
        extras={
            "d1Material": FINAL_MAIN_MATERIAL,
            "d1VertexShader": material_report.get("vertex_shader"),
            "d1PixelShader": material_report.get("pixel_shader"),
            "d1TexturePlateHeader": base.TEXTURE_PLATE_HEADER,
            "d1TexturePlateReport": plate_report,
            "d1MaterialReport": material_report,
            "nativeGStackImageIndex": gstack_i,
            "nativeDirect2DImageIndex": direct2d_i,
            "nativeCubeImageIndices": cube_images,
            "nativeTextureIndexBindings": {
                "0": FINAL_MAIN_CUBE,
                "1": FINAL_MAIN_DIRECT_2D,
            },
            "portableApproximation": "Exact entity plate albedo + BC5 normal are connected to core glTF. GStack/direct shader textures and native shader math remain provenance-only; roughness/metallic factors are not claims about D1 channel semantics.",
        },
    ))

    small_idx = len(gltf.materials)
    gltf.materials.append(base.Material(
        name=f"D1_{SMALL_MATERIAL}_SmallComponent_NATIVE_TEXTURE_UNMAPPED",
        alphaMode="OPAQUE",
        pbrMetallicRoughness=base.PbrMetallicRoughness(
            baseColorFactor=[0.18, 0.18, 0.18, 1.0],
            metallicFactor=0.0,
            roughnessFactor=0.7,
        ),
        extras={
            "d1Material": SMALL_MATERIAL,
            "d1VertexShader": _SMALL_REPORT.get("vertex_shader"),
            "d1PixelShader": _SMALL_REPORT.get("pixel_shader"),
            "d1MaterialReport": _SMALL_REPORT,
            "nativeAtlasImageIndex": small_atlas_i,
            "nativeTextureIndexBindings": {"0": SMALL_ATLAS},
            "portableApproximation": True,
            "warning": "The exact 0154 BC3 atlas is embedded, but it is not connected to core PBR until the retail PS 80AA9D63 dataflow authorizes that mapping.",
        },
    ))
    return {FINAL_MAIN_MATERIAL: main_idx, SMALL_MATERIAL: small_idx}


def main() -> None:
    global _SMALL_REPORT
    ap = argparse.ArgumentParser()
    ap.add_argument("pkg", type=Path, help="final 011c logical package view with sibling patch files beside it")
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--parser-root", type=Path, required=True)
    ap.add_argument("--texture-root", type=Path, required=True)
    ap.add_argument("--material-report", type=Path, required=True, help="decoded final material 80A382A6")
    ap.add_argument("--small-material-report", type=Path, required=True, help="decoded final material 80A3D294")
    ap.add_argument("--plate-report", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()

    _SMALL_REPORT = json.loads(args.small_material_report.read_text())
    base.MAIN_MATERIAL = FINAL_MAIN_MATERIAL
    base.SMALL_MATERIAL = SMALL_MATERIAL
    base.add_materials = add_final_materials
    report = base.build(args)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
