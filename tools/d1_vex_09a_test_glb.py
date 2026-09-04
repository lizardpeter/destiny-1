#!/usr/bin/env python3
"""Build a proof-grade portable GLB for the solved D1 PS4 Vex model 816CE09A.

This is intentionally a *portable approximation layer* over byte-proven native
Destiny data. It does not redefine D1 rendering semantics. Native owner,
materials, shaders, texture/sampler hashes and equations are preserved in
``extras`` so a future game-engine renderer can implement the original two-pass
behavior directly.

The animation decoder is currently validated through the public
SolUnshadowed/tiger-animation-parser implementation, imported from a caller-
supplied checkout. Geometry, skin indices, parent/material selection and image
recipes are decoded by this repository's tools and retail bytes.
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import math
import struct
import sys
from pathlib import Path

import numpy as np
from pygltflib import (
    GLTF2, Asset, Scene, Node, Mesh, Primitive, Attributes,
    Buffer, BufferView, Accessor, Material, PbrMetallicRoughness,
    TextureInfo, NormalMaterialTexture, Image, Texture, Sampler,
)

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from d1_entry_extract import EntryReader
from d1_entity_model_probe import parse_model

MODEL = "816CE09A"
SKELETON = "816CE092"
RIG = "816CE095"
CLIPS = ("816CE09D", "816CE09E")
OWNER = "816CE12B"
MAIN_MATERIAL = "809C475F"
CIRCUIT_MATERIAL = "816CE240"

# glTF numeric constants, kept local to avoid pygltflib-version constant drift.
FLOAT = 5126
UNSIGNED_SHORT = 5123
ARRAY_BUFFER = 34962
ELEMENT_ARRAY_BUFFER = 34963
LINEAR = 9729
LINEAR_MIPMAP_LINEAR = 9987
REPEAT = 10497
CLAMP_TO_EDGE = 33071


def snorm16(a: np.ndarray) -> np.ndarray:
    x = np.asarray(a, dtype=np.float32) / 32767.0
    return np.maximum(x, -1.0)


def data_uri(path: Path, mime: str = "image/png") -> str:
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def entry_bytes(reader: EntryReader, tag_hash: str) -> bytes:
    wanted = tag_hash.upper()
    for e in reader.entries:
        if e["tag_hash"].upper() == wanted:
            if not reader.available(e["index"]):
                raise RuntimeError(f"{wanted} is not resident in {reader.pkg}")
            return reader.entry(e["index"])
    raise KeyError(f"missing tag {wanted} in {reader.pkg}")


def linked_payload(reader: EntryReader, by_hash: dict[str, dict], tag_hash: str) -> tuple[bytes, bytes]:
    e = by_hash[tag_hash.upper()]
    header = reader.entry(e["index"])
    payload_entry = by_hash.get(e["reference"].upper())
    if payload_entry is None:
        raise KeyError(f"{tag_hash} -> missing local payload {e['reference']}")
    return header, reader.entry(payload_entry["index"])


def strip_to_triangles(values: np.ndarray) -> np.ndarray:
    out: list[tuple[int, int, int]] = []
    strip: list[int] = []
    for raw in values.tolist():
        if raw == 0xFFFF:
            strip.clear()
            continue
        strip.append(int(raw))
        if len(strip) < 3:
            continue
        tri_no = len(strip) - 3
        a, b, c = strip[-3], strip[-2], strip[-1]
        if tri_no & 1:
            a, b = b, a
        if a != b and b != c and a != c:
            out.append((a, b, c))
    return np.asarray(out, dtype=np.uint16).reshape((-1, 3))


def append_buffer(gltf: GLTF2, payload: bytes) -> int:
    idx = len(gltf.buffers)
    gltf.buffers.append(Buffer(
        byteLength=len(payload),
        uri="data:application/octet-stream;base64," + base64.b64encode(payload).decode("ascii"),
    ))
    return idx


def append_accessor(
    gltf: GLTF2,
    array: np.ndarray,
    component_type: int,
    accessor_type: str,
    *,
    target: int | None = None,
    normalized: bool = False,
    with_minmax: bool = False,
) -> int:
    a = np.ascontiguousarray(array)
    payload = a.tobytes()
    bi = append_buffer(gltf, payload)
    bvi = len(gltf.bufferViews)
    gltf.bufferViews.append(BufferView(buffer=bi, byteOffset=0, byteLength=len(payload), target=target))
    ai = len(gltf.accessors)
    acc = Accessor(
        bufferView=bvi,
        byteOffset=0,
        componentType=component_type,
        count=int(a.shape[0]),
        type=accessor_type,
        normalized=normalized,
    )
    if with_minmax:
        flat = a.reshape((a.shape[0], -1))
        acc.min = [float(x) for x in np.min(flat, axis=0)]
        acc.max = [float(x) for x in np.max(flat, axis=0)]
    gltf.accessors.append(acc)
    return ai


def decode_geometry(reader: EntryReader) -> tuple[dict, dict]:
    by_hash = {e["tag_hash"].upper(): e for e in reader.entries}
    me = by_hash[MODEL]
    model = parse_model(reader.entry(me["index"]), reader.h["platform"])
    if model["mesh_count"] != 1:
        raise RuntimeError(f"fixture expected one mesh, got {model['mesh_count']}")
    mesh = model["meshes"][0]

    h0, p0 = linked_payload(reader, by_hash, mesh["vertices1"])
    h1, p1 = linked_payload(reader, by_hash, mesh["vertices2"])
    hi, pi = linked_payload(reader, by_hash, mesh["indices"])
    stride0 = struct.unpack_from("<h", h0, 4)[0]
    stride1 = struct.unpack_from("<h", h1, 4)[0]
    if stride0 != 0x0C or stride1 != 0x10:
        raise RuntimeError(f"unexpected 09A strides {stride0:#x}/{stride1:#x}")

    r0 = np.frombuffer(p0, dtype="<i2").reshape((-1, stride0 // 2))
    r1 = np.frombuffer(p1, dtype="<i2").reshape((-1, stride1 // 2))
    if len(r0) != 4172 or len(r1) != 4172:
        raise RuntimeError(f"unexpected vertex counts {len(r0)}/{len(r1)}")

    scale = np.asarray(mesh["model_scale"][:3], dtype=np.float32)
    trans = np.asarray(mesh["model_translation"][:3], dtype=np.float32)
    positions = snorm16(r0[:, :3]) * scale + trans

    rigid = r0[:, 3].astype(np.int32)
    if rigid.min() < 0 or rigid.max() >= 12:
        raise RuntimeError(f"invalid rigid joint range {rigid.min()}..{rigid.max()}")
    joints = np.zeros((len(r0), 4), dtype=np.uint16)
    joints[:, 0] = rigid.astype(np.uint16)
    weights = np.zeros((len(r0), 4), dtype=np.float32)
    weights[:, 0] = 1.0

    uv0 = snorm16(r0[:, 4:6])
    uvscale = np.asarray(mesh["texcoord_scale"], dtype=np.float32)
    uvtrans = np.asarray(mesh["texcoord_translation"], dtype=np.float32)
    uv = np.column_stack((
        uv0[:, 0] * uvscale[0] + uvtrans[0],
        uv0[:, 1] * (-uvscale[1]) + 1.0 - uvtrans[1],
    )).astype(np.float32)

    normals = snorm16(r1[:, :3])
    lengths = np.linalg.norm(normals, axis=1, keepdims=True)
    normals = np.divide(normals, np.maximum(lengths, 1e-8)).astype(np.float32)

    source_indices = np.frombuffer(pi, dtype="<u2")
    groups: dict[tuple[int, int], list[dict]] = {}
    for part in mesh["parts"]:
        if part["primitive_type"] != 5:
            raise RuntimeError(f"fixture expected strip primitive 5, got {part['primitive_type']}")
        key = (part["index_offset"], part["index_count"])
        groups.setdefault(key, []).append(part)

    primitives = []
    for (off, count), parts in sorted(groups.items()):
        variants = sorted({int(p["variant_shader_index"]) for p in parts})
        if len(variants) != 1:
            raise RuntimeError(f"range {off}+{count} has mixed variant shader indices {variants}")
        tri = strip_to_triangles(source_indices[off:off + count])
        primitives.append({
            "index_offset": off,
            "index_count": count,
            "triangle_count": int(len(tri)),
            "variant_shader_index": variants[0],
            "material_tags": sorted({p["material"] for p in parts}),
            "lod_values": sorted({int(p["lod"]) for p in parts}),
            "triangles": tri,
        })

    total_tri = sum(p["triangle_count"] for p in primitives)
    if total_tri != 5336:
        raise RuntimeError(f"expected 5336 triangles, got {total_tri}")

    report = {
        "vertex_count": int(len(positions)),
        "triangle_count": int(total_tri),
        "joint_range": [int(rigid.min()), int(rigid.max())],
        "joint_histogram": {str(i): int(np.sum(rigid == i)) for i in sorted(set(rigid.tolist()))},
        "uv_min": [float(x) for x in uv.min(axis=0)],
        "uv_max": [float(x) for x in uv.max(axis=0)],
        "source_resources": {
            "vertices0": mesh["vertices1"], "vertices1": mesh["vertices2"], "indices": mesh["indices"]
        },
        "primitive_groups": [
            {k: v for k, v in p.items() if k != "triangles"} for p in primitives
        ],
    }
    return {
        "positions": positions.astype(np.float32),
        "normals": normals,
        "uv": uv,
        "joints": joints,
        "weights": weights,
        "primitives": primitives,
    }, report


def load_animation_oracle(parser_root: Path, reader: EntryReader):
    sys.path.insert(0, str(parser_root.resolve()))
    from tag.game_version import Game_Version
    from tag_readers.read_skeleton import read_skeleton
    from tag_readers.read_rig import read_runtime_rig
    from tag_readers.read_animation import read_animation
    from animation_decoding.decode_animation import decode_animation
    from runtime_rig.rig_retarget import rig_retarget
    from animation_export.convert_animation_object_to_local import convert_obj_to_local
    from animation_export.gltf_export import create_armature_hierarchy, add_animation
    from animation_export.enums import Name_Convention

    version = Game_Version.D1_ROI
    skeleton = read_skeleton(io.BytesIO(entry_bytes(reader, SKELETON)), version)
    rig = read_runtime_rig(io.BytesIO(entry_bytes(reader, RIG)), version)
    tracks = []
    clip_reports = []
    for tag in CLIPS:
        anim = read_animation(io.BytesIO(entry_bytes(reader, tag)), version)
        raw = decode_animation(anim)
        retargeted = rig_retarget(anim, raw, skeleton, rig)
        local = convert_obj_to_local(anim, retargeted, skeleton)
        tracks.append((tag, local))
        clip_reports.append({
            "tag_hash": tag,
            "frame_count": int(anim.animation_header.frame_count),
            "node_count": int(anim.animation_header.node_count),
            "rig_control_count": int(anim.animation_header.rig_control_count),
            "static_codec": int(anim.static_bones_header.codec_type) if anim.static_bones_header else None,
            "animated_codec": int(anim.animated_bones_header.codec_type) if anim.animated_bones_header else None,
        })
    return skeleton, tracks, clip_reports, create_armature_hierarchy, add_animation, Name_Convention


def add_images_and_materials(gltf: GLTF2, recipe_dir: Path, recipe: dict) -> dict[str, int]:
    gltf.samplers.extend([
        Sampler(name="D1_80AAE177_Wrap", magFilter=LINEAR, minFilter=LINEAR_MIPMAP_LINEAR, wrapS=REPEAT, wrapT=REPEAT),
        Sampler(name="D1_816CE0AA_ClampBorderPortable", magFilter=LINEAR, minFilter=LINEAR_MIPMAP_LINEAR, wrapS=CLAMP_TO_EDGE, wrapT=CLAMP_TO_EDGE),
    ])

    def add_image(name: str, filename: str, extras: dict | None = None) -> int:
        idx = len(gltf.images)
        gltf.images.append(Image(name=name, uri=data_uri(recipe_dir / filename), extras=extras or {}))
        return idx

    base_i = add_image("80AACCDD_rgb_opaque", "main_basecolor_opaque.png", {"d1TagHash": "80AACCDD", "nativeChannels": "rgb"})
    mr_i = add_image("80AACCDD_alpha_roughness_approx", "main_metallicRoughness_approx.png", {"d1TagHash": "80AACCDD", "nativeChannels": "alpha", "approximation": True})
    n_i = add_image("80AACCDF_primary_normal_approx", "main_primary_normal_approx.png", {"d1TagHash": "80AACCDF", "nativeChannels": "rg", "zReconstructed": True})
    circuit_i = add_image("816CE1C5_palette_bake", "circuitry_palette_rgb.png", {"d1TagHash": "816CE1C5", "paletteMaterial": CIRCUIT_MATERIAL})

    # Preserve native-only image sources inside the GLB even when core glTF cannot bind them faithfully.
    detail_src = recipe["portable_outputs"]["normal_detail_source"]["source_file"]
    detail_i = add_image("80AACC26_detail_normal_native_source", detail_src, {"d1TagHash": "80AACC26", "nativeOnly": True})
    cube_indices = []
    for face in recipe["portable_outputs"]["environment_cube_faces"]:
        cube_indices.append(add_image("80AACC28_cube_" + face["source_file"], face["source_file"], {"d1TagHash": "80AACC28", "nativeCubeFace": True}))

    def add_tex(image_index: int, sampler_index: int, name: str) -> int:
        idx = len(gltf.textures)
        gltf.textures.append(Texture(name=name, source=image_index, sampler=sampler_index))
        return idx

    base_t = add_tex(base_i, 0, "t0_surface_rgb")
    mr_t = add_tex(mr_i, 0, "t4_surface_control_as_roughness")
    n_t = add_tex(n_i, 0, "t1_primary_normal")
    circuit_t = add_tex(circuit_i, 1, "t1_circuitry_palette_portable")

    main_extras = {
        "d1": recipe["native_truth"],
        "portableApproximation": recipe["portable_policy"],
        "nativeDetailImageIndex": detail_i,
        "nativeCubeImageIndices": cube_indices,
    }
    main = Material(
        name="D1_809C475F_MainSurface_PORTABLE",
        alphaMode="OPAQUE",
        pbrMetallicRoughness=PbrMetallicRoughness(
            baseColorTexture=TextureInfo(index=base_t, texCoord=0),
            metallicRoughnessTexture=TextureInfo(index=mr_t, texCoord=0),
            metallicFactor=0.0,
            roughnessFactor=1.0,
        ),
        normalTexture=NormalMaterialTexture(index=n_t, texCoord=0, scale=1.0),
        extras=main_extras,
    )
    main_idx = len(gltf.materials)
    gltf.materials.append(main)

    circuit = Material(
        name="D1_816CE240_Circuitry_PORTABLE",
        alphaMode="OPAQUE",
        pbrMetallicRoughness=PbrMetallicRoughness(
            baseColorTexture=TextureInfo(index=circuit_t, texCoord=0),
            baseColorFactor=[0.18, 0.18, 0.18, 1.0],
            metallicFactor=0.0,
            roughnessFactor=0.5,
        ),
        emissiveTexture=TextureInfo(index=circuit_t, texCoord=0),
        emissiveFactor=[1.0, 1.0, 1.0],
        extensions={"KHR_materials_emissive_strength": {"emissiveStrength": 5.0}},
        extras={
            "d1": recipe["native_truth"]["circuitry_equations"],
            "material": CIRCUIT_MATERIAL,
            "shader": "816CE0A8",
            "texture": "816CE1C5",
            "sampler": "816CE0AA",
            "nativeBlendMode": "UNRESOLVED",
            "portableWarning": "BaseColor fallback is deliberately dim; native pass is HDR/emissive-like and exact blend/global multipliers remain under reversal.",
        },
    )
    circuit_idx = len(gltf.materials)
    gltf.materials.append(circuit)
    return {"0": main_idx, "1": circuit_idx}


def build(args) -> dict:
    reader = EntryReader(args.pkg, args.runtime)
    geom, geom_report = decode_geometry(reader)
    recipe = json.loads((args.recipe_dir / "material_recipe.json").read_text())

    skeleton, tracks, clip_reports, create_armature_hierarchy, add_animation, Name_Convention = load_animation_oracle(args.parser_root, reader)

    gltf = GLTF2(
        asset=Asset(version="2.0", generator="destiny-1 d1_vex_09a_test_glb.py + tiger-animation-parser validation oracle"),
        scene=0,
        scenes=[Scene(nodes=[])],
        nodes=[], meshes=[], skins=[], animations=[], materials=[], textures=[], images=[], samplers=[],
        buffers=[], bufferViews=[], accessors=[],
    )
    root_idx, bone_indices = create_armature_hierarchy(gltf, skeleton, Name_Convention.FNV1BE)
    for tag, local_tracks in tracks:
        before = len(gltf.animations)
        add_animation(gltf, bone_indices, local_tracks, Name_Convention.FNV1BE, fps=30)
        if len(gltf.animations) != before + 1:
            raise RuntimeError(f"animation {tag} did not append exactly one glTF animation")
        gltf.animations[-1].name = tag
        gltf.animations[-1].extras = {"d1TagHash": tag}

    material_map = add_images_and_materials(gltf, args.recipe_dir, recipe)

    pos_a = append_accessor(gltf, geom["positions"].astype("<f4"), FLOAT, "VEC3", target=ARRAY_BUFFER, with_minmax=True)
    norm_a = append_accessor(gltf, geom["normals"].astype("<f4"), FLOAT, "VEC3", target=ARRAY_BUFFER)
    uv_a = append_accessor(gltf, geom["uv"].astype("<f4"), FLOAT, "VEC2", target=ARRAY_BUFFER)
    joint_a = append_accessor(gltf, geom["joints"].astype("<u2"), UNSIGNED_SHORT, "VEC4", target=ARRAY_BUFFER)
    weight_a = append_accessor(gltf, geom["weights"].astype("<f4"), FLOAT, "VEC4", target=ARRAY_BUFFER)

    primitives = []
    for p in geom["primitives"]:
        variant = str(p["variant_shader_index"])
        if variant not in material_map:
            raise RuntimeError(f"unsupported VariantShaderIndex {variant}")
        flat_indices = p["triangles"].reshape(-1).astype("<u2")
        idx_a = append_accessor(gltf, flat_indices, UNSIGNED_SHORT, "SCALAR", target=ELEMENT_ARRAY_BUFFER)
        prim = Primitive(
            attributes=Attributes(POSITION=pos_a, NORMAL=norm_a, TEXCOORD_0=uv_a, JOINTS_0=joint_a, WEIGHTS_0=weight_a),
            indices=idx_a,
            material=material_map[variant],
            mode=4,
            extras={
                "d1VariantShaderIndex": int(p["variant_shader_index"]),
                "d1SourceIndexOffset": int(p["index_offset"]),
                "d1SourceIndexCount": int(p["index_count"]),
                "d1SourceMaterialTags": p["material_tags"],
                "d1LodValues": p["lod_values"],
            },
        )
        primitives.append(prim)

    mesh_idx = len(gltf.meshes)
    gltf.meshes.append(Mesh(name=MODEL, primitives=primitives, extras={"d1Owner": OWNER, "d1Model": MODEL}))
    mesh_node_idx = len(gltf.nodes)
    gltf.nodes.append(Node(name=MODEL, mesh=mesh_idx, skin=0, extras={"d1Owner": OWNER}))
    gltf.scenes[0].nodes = [root_idx, mesh_node_idx]
    gltf.extensionsUsed = ["KHR_materials_emissive_strength"]
    gltf.extras = {
        "d1Provenance": {
            "owner": OWNER, "model": MODEL, "skeleton": SKELETON, "runtimeRig": RIG,
            "animations": list(CLIPS), "mainMaterial": MAIN_MATERIAL, "circuitryMaterial": CIRCUIT_MATERIAL,
            "portableMaterialRecipe": recipe,
        },
        "reverseEngineeringPolicy": "Native D1 data preserved; core glTF material is explicitly an approximation. Do not use portable PBR fields to redefine native Destiny semantics.",
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    gltf.save_binary(str(args.out))
    if not args.out.exists() or args.out.stat().st_size < 1024:
        raise RuntimeError("GLB was not written correctly")

    # Re-open with pygltflib as a structural sanity check.
    check = GLTF2().load_binary(str(args.out))
    report = {
        "output": str(args.out),
        "output_bytes": args.out.stat().st_size,
        "mesh_count": len(check.meshes),
        "node_count": len(check.nodes),
        "skin_count": len(check.skins),
        "animation_count": len(check.animations),
        "animation_names": [a.name for a in check.animations],
        "material_count": len(check.materials),
        "image_count": len(check.images),
        "geometry": geom_report,
        "clips": clip_reports,
        "native_owner": OWNER,
        "native_materials": [MAIN_MATERIAL, CIRCUIT_MATERIAL],
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    return report


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pkg", type=Path, help="ps4_arch_vex_com01_0767 package view containing 09A/skeleton/rig/clips")
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--parser-root", type=Path, required=True, help="checkout of SolUnshadowed/tiger-animation-parser")
    ap.add_argument("--recipe-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()
    rep = build(args)
    print(json.dumps(rep, indent=2))


if __name__ == "__main__":
    main()
