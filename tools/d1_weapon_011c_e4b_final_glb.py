#!/usr/bin/env python3
"""Build the fuller entity-backed D1 ROI PS4 011C weapon variant 80A39E4B.

80A39E4B is not created by mirroring or combining guessed parts.  Retail model
80A39E4B is embedded by EntityResource 80A39E48 and has its own texture plate
header 80A39E4C.  Its first 2,604 LOD1 triangles reproduce the two base-shell
ranges of 80A39E12, while a third native range contributes another 1,694 LOD1
triangles under material 80A3CED5.

The geometry still has no native skin weights.  The proof GLB therefore keeps
it rigidly attached to the recovered C410084A Pedestal chain.  A separate
post-process tool can bake the evaluated Pedestal world motion directly onto a
visible weapon root for interchange/viewer compatibility without inventing
internal weapon articulation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import d1_weapon_011c_test_glb as base
from d1_entity_model_probe import parse_model

MODEL = "80A39E4B"
OWNER_RESOURCE = "80A39E48"
OWNER_ENTITY = "80A39E47"
TEXTURE_PLATE_HEADER = "80A39E4C"
MAIN_MATERIAL = "80A382A6"
EXTRA_MATERIAL = "80A3CED5"
MAIN_CUBE = "80AB0B74"
MAIN_DIRECT_2D = "80A3D4D6"
EXPECTED_TRIANGLES = 4298
EXPECTED_VERTICES = 4044

_EXTRA_REPORT: dict | None = None


def material_record(report: dict, expected_tag: str) -> dict:
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


def decode_e4b_geometry(reader):
    by_hash = {e["tag_hash"].upper(): e for e in reader.entries}
    me = by_hash[MODEL]
    model = parse_model(reader.entry(me["index"]), reader.h["platform"])
    if model["mesh_count"] != 1:
        raise RuntimeError(f"{MODEL}: expected one mesh, got {model['mesh_count']}")
    d, r = base.decode_mesh(reader, by_hash, model["meshes"][0], 0)
    total = int(r["triangle_count_lod1"])
    if total != EXPECTED_TRIANGLES:
        raise RuntimeError(f"{MODEL}: expected {EXPECTED_TRIANGLES} LOD1 triangles, got {total}")
    if int(r["vertex_count"]) != EXPECTED_VERTICES:
        raise RuntimeError(f"{MODEL}: expected {EXPECTED_VERTICES} vertices, got {r['vertex_count']}")
    groups = r["primitive_groups_lod1"]
    exact = [(int(x["index_offset"]), int(x["index_count"]), int(x["triangle_count"]), x["material"]) for x in groups]
    wanted = [
        (114, 2015, 1294, MAIN_MATERIAL),
        (2240, 2188, 1310, MAIN_MATERIAL),
        (4429, 2706, 1694, EXTRA_MATERIAL),
    ]
    if exact != wanted:
        raise RuntimeError(f"{MODEL}: native LOD1 range census changed: {exact!r}")
    return [d], {
        "model": MODEL,
        "entity": OWNER_ENTITY,
        "entity_resource": OWNER_RESOURCE,
        "texture_plate_header": TEXTURE_PLATE_HEADER,
        "mesh_count": 1,
        "vertex_count": EXPECTED_VERTICES,
        "triangle_count_lod1": total,
        "native_range_census": exact,
        "coordinate_conversion": "Tiger [x,y,z] -> glTF/animation-oracle [y,z,x]",
        "native_uv_policy": "uv = snorm16(raw) * texcoord_scale + texcoord_translation; no native V flip",
        "assembly_status": "CONFIRMED_NATIVE_ENTITY_MODEL; no mirrored or guessed geometry added",
        "meshes": [r],
    }


def add_e4b_materials(gltf, texture_root: Path, material_report: dict, plate_report: dict) -> dict[str, int]:
    if _EXTRA_REPORT is None:
        raise RuntimeError("extra material report was not loaded")
    main = material_record(material_report, MAIN_MATERIAL)
    extra = material_record(_EXTRA_REPORT, EXTRA_MATERIAL)

    for rec, tag in ((main, MAIN_MATERIAL), (extra, EXTRA_MATERIAL)):
        if rec.get("vertex_shader") != "80A3D28E" or rec.get("pixel_shader") != "80A3D145":
            raise RuntimeError(f"{tag}: unexpected final shader pair {rec.get('vertex_shader')}/{rec.get('pixel_shader')}")
        tex = {x.get("texture") for x in rec.get("ps_textures", {}).get("items", [])}
        if not {MAIN_CUBE, MAIN_DIRECT_2D}.issubset(tex):
            raise RuntimeError(f"{tag}: expected direct resources {MAIN_CUBE}/{MAIN_DIRECT_2D}, got {sorted(tex)}")

    gltf.samplers.append(base.Sampler(
        magFilter=base.LINEAR,
        minFilter=base.LINEAR_MIPMAP_LINEAR,
        wrapS=base.CLAMP_TO_EDGE,
        wrapT=base.CLAMP_TO_EDGE,
    ))

    def add_image(name: str, path: Path, extras: dict | None = None) -> int:
        if not path.exists():
            raise FileNotFoundError(path)
        i = len(gltf.images)
        gltf.images.append(base.Image(name=name, uri=base.data_uri(path), extras=extras or {}))
        return i

    def add_texture(image_index: int, name: str) -> int:
        i = len(gltf.textures)
        gltf.textures.append(base.Texture(name=name, source=image_index, sampler=0))
        return i

    plate_dir = texture_root / "plates"
    src_dir = texture_root / "source"
    albedo_i = add_image(
        "80A39E50_albedo_plate",
        plate_dir / "80A39E4C_albedo_plate.png",
        {"d1PlateHeader": TEXTURE_PLATE_HEADER, "d1Plate": "80A39E50", "nativeTransformCount": 5},
    )
    normal_i = add_image(
        "80A39E51_normal_plate",
        plate_dir / "80A39E4C_normal_plate.png",
        {"d1PlateHeader": TEXTURE_PLATE_HEADER, "d1Plate": "80A39E51", "nativeTransformCount": 5},
    )
    gstack_i = add_image(
        "80A39E52_gstack_plate_NATIVE_ONLY",
        plate_dir / "80A39E4C_gstack_plate.png",
        {"d1PlateHeader": TEXTURE_PLATE_HEADER, "d1Plate": "80A39E52", "nativeTransformCount": 5, "nativeOnly": True},
    )
    direct_i = add_image(
        f"{MAIN_DIRECT_2D}_direct_shader_texture_NATIVE_ONLY",
        src_dir / f"{MAIN_DIRECT_2D}_128x128_BC1.png",
        {"d1TagHash": MAIN_DIRECT_2D, "textureIndex": 1, "nativeOnly": True,
         "instructionProvenRole": "scalar modulation of cubemap/reflection contribution"},
    )
    cube_images = []
    for face in range(6):
        cube_images.append(add_image(
            f"{MAIN_CUBE}_cube_face{face}_NATIVE_ONLY",
            src_dir / f"{MAIN_CUBE}_128x128_BC1_face{face}.png",
            {"d1TagHash": MAIN_CUBE, "textureIndex": 0, "cubeFace": face, "nativeOnly": True,
             "instructionProvenRole": "environment/reflection cubemap path"},
        ))

    albedo_t = add_texture(albedo_i, "D1_E4B_albedo_plate")
    normal_t = add_texture(normal_i, "D1_E4B_normal_plate")

    result = {}
    for tag, rec, role in (
        (MAIN_MATERIAL, main, "base_shell_ranges"),
        (EXTRA_MATERIAL, extra, "extra_native_range_1694_triangles"),
    ):
        idx = len(gltf.materials)
        gltf.materials.append(base.Material(
            name=f"D1_{tag}_E4B_PORTABLE",
            alphaMode="OPAQUE",
            pbrMetallicRoughness=base.PbrMetallicRoughness(
                baseColorTexture=base.TextureInfo(index=albedo_t, texCoord=0),
                metallicFactor=0.0,
                roughnessFactor=0.65,
            ),
            normalTexture=base.NormalMaterialTexture(index=normal_t, texCoord=0, scale=1.0),
            extras={
                "d1Material": tag,
                "d1Entity": OWNER_ENTITY,
                "d1EntityResource": OWNER_RESOURCE,
                "d1Model": MODEL,
                "d1TexturePlateHeader": TEXTURE_PLATE_HEADER,
                "d1TexturePlateReport": plate_report,
                "d1MaterialReport": rec,
                "nativeRangeRole": role,
                "nativeGStackImageIndex": gstack_i,
                "nativeDirect2DImageIndex": direct_i,
                "nativeCubeImageIndices": cube_images,
                "nativeTextureIndexBindings": {"0": MAIN_CUBE, "1": MAIN_DIRECT_2D},
                "sharedShaderProgramEvidence": {
                    "vertexShader": "80A3D28E",
                    "pixelShader": "80A3D145",
                    "note": "80A382A6 and 80A3CED5 are distinct native material records using the same recovered VS/PS/direct-resource program; this does not assert the materials are identical.",
                },
                "portableApproximation": "Exact E4B entity plate albedo + normal are connected to core glTF. Native GStack/deferred/reflection math remains provenance-only; metallic/roughness constants are portable presentation choices, not D1 semantic claims.",
            },
        ))
        result[tag] = idx
    return result


def main() -> None:
    global _EXTRA_REPORT
    ap = argparse.ArgumentParser()
    ap.add_argument("pkg", type=Path)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--parser-root", type=Path, required=True)
    ap.add_argument("--texture-root", type=Path, required=True)
    ap.add_argument("--material-report", type=Path, required=True, help=f"decoded {MAIN_MATERIAL}")
    ap.add_argument("--extra-material-report", type=Path, required=True, help=f"decoded {EXTRA_MATERIAL}")
    ap.add_argument("--plate-report", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()

    _EXTRA_REPORT = json.loads(args.extra_material_report.read_text())
    base.MODEL = MODEL
    base.OWNER = OWNER_RESOURCE
    base.TEXTURE_PLATE_HEADER = TEXTURE_PLATE_HEADER
    base.MAIN_MATERIAL = MAIN_MATERIAL
    # Reuse the base decoder's second visible-material branch for E4B's third
    # native primitive range.  This is only a decoder slot, not a semantic claim
    # that 80A3CED5 is the old small-component material.
    base.SMALL_MATERIAL = EXTRA_MATERIAL
    base.decode_geometry = decode_e4b_geometry
    base.add_materials = add_e4b_materials

    report = base.build(args)
    report["variant"] = {
        "entity": OWNER_ENTITY,
        "entity_resource": OWNER_RESOURCE,
        "model": MODEL,
        "texture_plate_header": TEXTURE_PLATE_HEADER,
        "native_materials": [MAIN_MATERIAL, EXTRA_MATERIAL],
        "expected_vertices": EXPECTED_VERTICES,
        "expected_lod1_triangles": EXPECTED_TRIANGLES,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
