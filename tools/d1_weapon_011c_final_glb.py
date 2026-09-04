#!/usr/bin/env python3
"""Build the corrected final-snapshot D1 ROI PS4 011C weapon GLB.

This is deliberately a thin specialization of d1_weapon_011c_test_glb.py so
all proven geometry, rigid Pedestal attachment and 12-clip animation logic stay
identical. The historical test fixture hard-coded tombstoned material
80A3CD9A; this wrapper switches the native main-shell binding to the material
actually serialized by final model 80A39E12: 80A382A6.

Core glTF PBR remains explicitly portable/approximate. Exact entity texture
plates drive the main shell. Direct shader resources whose renderer semantics
remain unresolved are embedded as provenance images. The small-component
80AA9D4D atlas is different: retail PS 80AA9D63 is now instruction-proven to
sample attr0.xy, pass sampled RGB, and discard when sampled alpha is below 0.5,
so that texture is legitimately mapped as a glTF MASK base-color texture.
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
SMALL_PIXEL_SHADER = "80AA9D63"
SMALL_PIXEL_VECTOR4 = "80AAE1E1"
SMALL_PIXEL_SAMPLER = "80AAE1D5"
SMALL_SHADER_CODE_SHA256 = "c846c4182497fb5f7e98226964f91045e2c8fab244141c380845800968fdbf51"
SMALL_ALPHA_CUTOFF = 0.5
REPEAT = 10497

_SMALL_REPORT: dict | None = None


def material_record(report: dict, expected_tag: str) -> dict:
    """Accept either d1_material_decode's report wrapper or a bare record."""
    if not isinstance(report, dict):
        raise TypeError(f"material report for {expected_tag} is not an object")
    if "materials" in report:
        rows = report.get("materials")
        if not isinstance(rows, list):
            raise ValueError("material report 'materials' field is not a list")
        matches = [r for r in rows if isinstance(r, dict) and r.get("tag_hash", "").upper() == expected_tag]
        if len(matches) != 1:
            raise ValueError(f"expected exactly one {expected_tag} material record, got {len(matches)}")
        return matches[0]
    if report.get("tag_hash", "").upper() != expected_tag:
        raise ValueError(f"expected material {expected_tag}, got {report.get('tag_hash')}")
    return report


def add_final_materials(gltf, texture_root: Path, material_report: dict, plate_report: dict) -> dict[str, int]:
    if _SMALL_REPORT is None:
        raise RuntimeError("small material report was not loaded")
    material_report = material_record(material_report, FINAL_MAIN_MATERIAL)

    # Main plate sampler is a conservative portable choice. The small atlas gets
    # a separate wrap sampler because retail sampler 80AAE1D5 is byte-decoded as
    # Wrap/Wrap with anisotropic bilinear min+mag and linear mip filtering.
    gltf.samplers.append(base.Sampler(
        magFilter=base.LINEAR,
        minFilter=base.LINEAR_MIPMAP_LINEAR,
        wrapS=base.CLAMP_TO_EDGE,
        wrapT=base.CLAMP_TO_EDGE,
    ))
    gltf.samplers.append(base.Sampler(
        magFilter=base.LINEAR,
        minFilter=base.LINEAR_MIPMAP_LINEAR,
        wrapS=REPEAT,
        wrapT=REPEAT,
    ))

    def add_image(name: str, path: Path, extras: dict | None = None) -> int:
        if not path.exists():
            raise FileNotFoundError(path)
        idx = len(gltf.images)
        gltf.images.append(base.Image(name=name, uri=base.data_uri(path), extras=extras or {}))
        return idx

    def add_texture(image_index: int, name: str, sampler_index: int = 0) -> int:
        idx = len(gltf.textures)
        gltf.textures.append(base.Texture(name=name, source=image_index, sampler=sampler_index))
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
        f"{SMALL_ATLAS}_small_component_masked_base_color",
        src_dir / f"{SMALL_ATLAS}_1024x1024_BC3.png",
        {
            "d1TagHash": SMALL_ATLAS,
            "d1Material": SMALL_MATERIAL,
            "textureIndex": 0,
            "nativeFormat": "BC3",
            "semanticStatus": "retail pixel-shader dataflow proven",
            "pixelShader": SMALL_PIXEL_SHADER,
            "pixelShaderCodeSha256": SMALL_SHADER_CODE_SHA256,
            "mapping": "sampled RGB -> portable base color; sampled A -> alpha-test mask",
        },
    )

    albedo_t = add_texture(albedo_i, "D1_weapon_albedo_plate")
    normal_t = add_texture(normal_i, "D1_weapon_normal_plate")
    small_atlas_t = add_texture(small_atlas_i, "D1_small_component_masked_atlas", sampler_index=1)

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
        name=f"D1_{SMALL_MATERIAL}_SmallComponent_MASKED",
        alphaMode="MASK",
        alphaCutoff=SMALL_ALPHA_CUTOFF,
        pbrMetallicRoughness=base.PbrMetallicRoughness(
            baseColorTexture=base.TextureInfo(index=small_atlas_t, texCoord=0),
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
            "provenPixelShaderSemantics": {
                "shader": SMALL_PIXEL_SHADER,
                "codeSha256": SMALL_SHADER_CODE_SHA256,
                "uv": "attr0.xy / TEXCOORD_0",
                "rgb": "sampled texture RGB passes to MRT0 RGB",
                "alphaUse": "coverage test only; sampled alpha is not exported as native MRT0 alpha",
                "discardEquation": "discard when clamp(CB0[dword5],0,1) * sampled_alpha - 0.5 < 0",
                "constantBuffer": SMALL_PIXEL_VECTOR4,
                "constantDword5": 1.0,
                "effectiveAlphaCutoff": SMALL_ALPHA_CUTOFF,
            },
            "nativeSampler": {
                "tag": SMALL_PIXEL_SAMPLER,
                "wrapX": "Wrap",
                "wrapY": "Wrap",
                "magFilter": "AnisoBilinear",
                "minFilter": "AnisoBilinear",
                "mipFilter": "Linear",
            },
            "portableApproximation": "Core glTF MASK exactly preserves the proven 0.5 coverage decision and uses the same atlas RGB. Core glTF cannot express the native anisotropic sampler descriptor; linear mipmapped repeat filtering is the portable fallback.",
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

    _SMALL_REPORT = material_record(json.loads(args.small_material_report.read_text()), SMALL_MATERIAL)
    if _SMALL_REPORT.get("pixel_shader") != SMALL_PIXEL_SHADER:
        raise RuntimeError(f"{SMALL_MATERIAL} expected PS {SMALL_PIXEL_SHADER}, got {_SMALL_REPORT.get('pixel_shader')}")
    if _SMALL_REPORT.get("ps_vector4_container") != SMALL_PIXEL_VECTOR4:
        raise RuntimeError(f"{SMALL_MATERIAL} expected PS vec4 {SMALL_PIXEL_VECTOR4}, got {_SMALL_REPORT.get('ps_vector4_container')}")
    base.MAIN_MATERIAL = FINAL_MAIN_MATERIAL
    base.SMALL_MATERIAL = SMALL_MATERIAL
    base.add_materials = add_final_materials
    report = base.build(args)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
