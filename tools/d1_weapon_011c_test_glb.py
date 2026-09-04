#!/usr/bin/env python3
"""Build the first proof-oriented D1 ROI PS4 weapon GLB fixture.

Fixture:
  EntityResource/model parent 80A39E0F
  model                       80A39E12
  skeleton                    80A39DF2
  runtime rig                 80A39DF1
  clips                       80A39DF6..80A39E01
  main visible material       80A3CD9A (shared from package 011E)
  texture plate header        80A39E17

The weapon shell has no native skin weights.  The portable GLB therefore keeps
it as a rigid node parented to the byte/source-proven weapon Pedestal bone
C410084A, itself a child of player Grip.R.  Do not replace this with invented
JOINTS/WEIGHTS.

The core glTF material is intentionally approximate: exact albedo and normal
texture plates are used, while GStack and direct shader textures are preserved
as native-only provenance because their complete renderer semantics are not yet
proven.
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import struct
import sys
import tempfile
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

MODEL = "80A39E12"
OWNER = "80A39E0F"
SKELETON = "80A39DF2"
RIG = "80A39DF1"
CLIPS = tuple(f"80A39{n:03X}" for n in range(0xDF6, 0xE02))
MAIN_MATERIAL = "80A3CD9A"
SMALL_MATERIAL = "80A3D294"
TEXTURE_PLATE_HEADER = "80A39E17"
WEAPON_PEDESTAL_HASH = 0xC410084A
WEAPON_PEDESTAL_HEX = "C410084A"

FLOAT = 5126
UNSIGNED_SHORT = 5123
ARRAY_BUFFER = 34962
ELEMENT_ARRAY_BUFFER = 34963
LINEAR = 9729
LINEAR_MIPMAP_LINEAR = 9987
CLAMP_TO_EDGE = 33071


def snorm16(a: np.ndarray) -> np.ndarray:
    x = np.asarray(a, dtype=np.float32) / 32767.0
    return np.maximum(x, -1.0)


def tiger_to_gltf_xyz(a: np.ndarray) -> np.ndarray:
    # Match tiger-animation-parser's validated D1 conversion.
    return np.ascontiguousarray(a[:, [1, 2, 0]])


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
    )
    if with_minmax:
        flat = a.reshape((a.shape[0], -1))
        acc.min = [float(x) for x in np.min(flat, axis=0)]
        acc.max = [float(x) for x in np.max(flat, axis=0)]
    gltf.accessors.append(acc)
    return ai


def decode_mesh(reader: EntryReader, by_hash: dict[str, dict], mesh: dict, mesh_index: int) -> tuple[dict, dict]:
    h0, p0 = linked_payload(reader, by_hash, mesh["vertices1"])
    h1, p1 = linked_payload(reader, by_hash, mesh["vertices2"])
    _, pi = linked_payload(reader, by_hash, mesh["indices"])
    stride0 = struct.unpack_from("<h", h0, 4)[0]
    stride1 = struct.unpack_from("<h", h1, 4)[0]
    if stride0 != 8 or stride1 not in (20, 24):
        raise RuntimeError(f"mesh {mesh_index}: unexpected weapon strides {stride0}/{stride1}")

    r0 = np.frombuffer(p0, dtype="<i2").reshape((-1, stride0 // 2))
    r1 = np.frombuffer(p1, dtype="<i2").reshape((-1, stride1 // 2))
    if len(r0) != len(r1):
        raise RuntimeError(f"mesh {mesh_index}: stream vertex count mismatch {len(r0)}/{len(r1)}")

    # Position stream is rigid geometry, not a native skin stream.  The fourth
    # int16 is zero for this fixture and is recorded but not assigned a semantic.
    fourth = r0[:, 3].copy()
    scale = np.asarray(mesh["model_scale"][:3], dtype=np.float32)
    trans = np.asarray(mesh["model_translation"][:3], dtype=np.float32)
    positions_tiger = snorm16(r0[:, :3]) * scale + trans
    positions = tiger_to_gltf_xyz(positions_tiger).astype(np.float32)

    raw_uv = snorm16(r1[:, :2])
    uvscale = np.asarray(mesh["texcoord_scale"], dtype=np.float32)
    uvtrans = np.asarray(mesh["texcoord_translation"], dtype=np.float32)
    # Byte/plate-proven native D1 transform.  No V flip belongs to the Tiger
    # equation; any interchange-image conversion must be labeled separately.
    uv_native = (raw_uv * uvscale + uvtrans).astype(np.float32)

    normals_tiger = snorm16(r1[:, 2:5])
    lengths = np.linalg.norm(normals_tiger, axis=1, keepdims=True)
    normals_tiger = np.divide(normals_tiger, np.maximum(lengths, 1e-8)).astype(np.float32)
    normals = tiger_to_gltf_xyz(normals_tiger).astype(np.float32)

    unresolved_tail = None
    if stride1 == 24:
        unresolved_tail = r1[:, 10:12].copy()

    source_indices = np.frombuffer(pi, dtype="<u2")
    groups: dict[tuple[int, int, int], list[dict]] = {}
    for part in mesh["parts"]:
        key = (int(part["index_offset"]), int(part["index_count"]), int(part["primitive_type"]))
        groups.setdefault(key, []).append(part)

    primitives = []
    for (off, count, prim_type), parts in sorted(groups.items()):
        if prim_type != 5:
            raise RuntimeError(f"mesh {mesh_index}: expected strip primitive 5, got {prim_type}")
        lod_values = sorted({int(p["lod"]) for p in parts})
        # Export the retail LOD1 ranges only.  LOD8 ranges are separate low-detail
        # geometry, not additional visible pieces to overlay on LOD1.
        if 1 not in lod_values:
            continue
        materials = sorted({p["material"] for p in parts})
        if MAIN_MATERIAL in materials:
            visible_material = MAIN_MATERIAL
            auxiliary = sorted(x for x in materials if x != MAIN_MATERIAL)
        elif SMALL_MATERIAL in materials:
            visible_material = SMALL_MATERIAL
            auxiliary = sorted(x for x in materials if x != SMALL_MATERIAL)
        else:
            raise RuntimeError(f"mesh {mesh_index} range {off}+{count}: unresolved visible material candidates {materials}")
        tri = strip_to_triangles(source_indices[off:off + count])
        primitives.append({
            "index_offset": off,
            "index_count": count,
            "triangle_count": int(len(tri)),
            "material": visible_material,
            "auxiliary_materials": auxiliary,
            "lod_values": lod_values,
            "triangles": tri,
        })

    report = {
        "mesh_index": mesh_index,
        "vertex_count": int(len(r0)),
        "vertex_stride0": stride0,
        "vertex_stride1": stride1,
        "buffer0_fourth_i16_minmax": [int(fourth.min()), int(fourth.max())],
        "native_uv_min": [float(x) for x in uv_native.min(axis=0)],
        "native_uv_max": [float(x) for x in uv_native.max(axis=0)],
        "source_resources": {
            "vertices0": mesh["vertices1"],
            "vertices1": mesh["vertices2"],
            "indices": mesh["indices"],
        },
        "primitive_groups_lod1": [{k: v for k, v in p.items() if k != "triangles"} for p in primitives],
        "triangle_count_lod1": int(sum(p["triangle_count"] for p in primitives)),
    }
    if unresolved_tail is not None:
        uniq = np.unique(unresolved_tail, axis=0)
        report["unresolved_stride24_tail_unique_i16"] = uniq.astype(int).tolist()
        report["unresolved_stride24_tail_unique_hex"] = [
            [f"{int(v) & 0xffff:04X}" for v in row] for row in uniq
        ]

    return {
        "positions": positions,
        "normals": normals,
        "uv": uv_native,
        "primitives": primitives,
    }, report


def decode_geometry(reader: EntryReader) -> tuple[list[dict], dict]:
    by_hash = {e["tag_hash"].upper(): e for e in reader.entries}
    me = by_hash[MODEL]
    model = parse_model(reader.entry(me["index"]), reader.h["platform"])
    if model["mesh_count"] != 2:
        raise RuntimeError(f"fixture expected two meshes, got {model['mesh_count']}")
    decoded = []
    reports = []
    for i, mesh in enumerate(model["meshes"]):
        d, r = decode_mesh(reader, by_hash, mesh, i)
        decoded.append(d)
        reports.append(r)
    total = sum(r["triangle_count_lod1"] for r in reports)
    if total != 2620:
        raise RuntimeError(f"expected 2620 LOD1 weapon triangles, got {total}")
    return decoded, {
        "model": MODEL,
        "mesh_count": 2,
        "triangle_count_lod1": int(total),
        "coordinate_conversion": "Tiger [x,y,z] -> glTF/animation-oracle [y,z,x]",
        "native_uv_policy": "uv = snorm16(raw) * texcoord_scale + texcoord_translation; no native V flip",
        "meshes": reports,
    }


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
        clip_bytes = entry_bytes(reader, tag)
        with tempfile.NamedTemporaryFile() as clip_file:
            clip_file.write(clip_bytes)
            clip_file.flush()
            clip_file.seek(0)
            anim = read_animation(clip_file, version)
        raw = decode_animation(anim)
        retargeted = rig_retarget(anim, raw, skeleton, rig)
        local = convert_obj_to_local(anim, retargeted, skeleton)
        tracks.append((tag, local))
        clip_reports.append({
            "tag_hash": tag,
            "frame_count": int(anim.animation_header.frame_count),
            "node_count": int(anim.animation_header.node_count),
            "rig_control_count": int(anim.animation_header.rig_control_count),
        })
    return skeleton, rig, tracks, clip_reports, create_armature_hierarchy, add_animation, Name_Convention


def add_materials(gltf: GLTF2, texture_root: Path, material_report: dict, plate_report: dict) -> dict[str, int]:
    gltf.samplers.append(Sampler(
        magFilter=LINEAR,
        minFilter=LINEAR_MIPMAP_LINEAR,
        wrapS=CLAMP_TO_EDGE,
        wrapT=CLAMP_TO_EDGE,
    ))

    def add_image(name: str, path: Path, extras: dict | None = None) -> int:
        if not path.exists():
            raise FileNotFoundError(path)
        idx = len(gltf.images)
        gltf.images.append(Image(name=name, uri=data_uri(path), extras=extras or {}))
        return idx

    def add_texture(image_index: int, name: str) -> int:
        idx = len(gltf.textures)
        gltf.textures.append(Texture(name=name, source=image_index, sampler=0))
        return idx

    plate_dir = texture_root / "plates"
    src_dir = texture_root / "source"
    albedo_i = add_image(
        "80A39E19_albedo_plate",
        plate_dir / "80A39E17_albedo_plate.png",
        {"d1PlateHeader": TEXTURE_PLATE_HEADER, "d1Plate": "80A39E19", "d1Source": "80A3D844"},
    )
    normal_i = add_image(
        "80A39E1A_normal_plate",
        plate_dir / "80A39E17_normal_plate.png",
        {"d1PlateHeader": TEXTURE_PLATE_HEADER, "d1Plate": "80A39E1A", "d1Source": "80A3D845", "nativeFormat": "BC5"},
    )
    gstack_i = add_image(
        "80A39E1B_gstack_plate_NATIVE_ONLY",
        plate_dir / "80A39E17_gstack_plate.png",
        {"d1PlateHeader": TEXTURE_PLATE_HEADER, "d1Plate": "80A39E1B", "d1Source": "80A3D846", "nativeOnly": True},
    )
    direct2d_i = add_image(
        "80A3D4D6_direct_shader_texture_NATIVE_ONLY",
        src_dir / "80A3D4D6_128x128_BC1.png",
        {"d1TagHash": "80A3D4D6", "textureIndex": 1, "nativeOnly": True},
    )
    cube_images = []
    for face in range(6):
        cube_images.append(add_image(
            f"80A3D4CF_cube_face{face}_NATIVE_ONLY",
            src_dir / f"80A3D4CF_128x128_BC1_face{face}.png",
            {"d1TagHash": "80A3D4CF", "textureIndex": 0, "cubeFace": face, "nativeOnly": True},
        ))

    albedo_t = add_texture(albedo_i, "D1_weapon_albedo_plate")
    normal_t = add_texture(normal_i, "D1_weapon_normal_plate")

    main_idx = len(gltf.materials)
    gltf.materials.append(Material(
        name="D1_80A3CD9A_MainWeapon_PORTABLE",
        alphaMode="OPAQUE",
        pbrMetallicRoughness=PbrMetallicRoughness(
            baseColorTexture=TextureInfo(index=albedo_t, texCoord=0),
            metallicFactor=0.0,
            roughnessFactor=0.65,
        ),
        normalTexture=NormalMaterialTexture(index=normal_t, texCoord=0, scale=1.0),
        extras={
            "d1Material": MAIN_MATERIAL,
            "d1VertexShader": "80A3D28E",
            "d1PixelShader": "80A3D145",
            "d1TexturePlateHeader": TEXTURE_PLATE_HEADER,
            "d1TexturePlateReport": plate_report,
            "d1MaterialReport": material_report,
            "nativeGStackImageIndex": gstack_i,
            "nativeDirect2DImageIndex": direct2d_i,
            "nativeCubeImageIndices": cube_images,
            "portableApproximation": "Exact plate albedo + BC5 normal are connected to core glTF. GStack/direct shader textures and native shader math remain provenance-only; roughness/metallic factors are not claims about D1 channel semantics.",
        },
    ))

    small_idx = len(gltf.materials)
    gltf.materials.append(Material(
        name="D1_80A3D294_SmallComponent_UNRESOLVED",
        alphaMode="OPAQUE",
        pbrMetallicRoughness=PbrMetallicRoughness(
            baseColorFactor=[0.18, 0.18, 0.18, 1.0],
            metallicFactor=0.0,
            roughnessFactor=0.7,
        ),
        extras={
            "d1Material": SMALL_MATERIAL,
            "d1Texture": "80AA9D4D",
            "d1TexturePackageId": "0154",
            "portableApproximation": True,
            "warning": "Small-component 0154 texture dependency not yet recovered; neutral fallback is visual-only.",
        },
    ))
    return {MAIN_MATERIAL: main_idx, SMALL_MATERIAL: small_idx}


def build(args) -> dict:
    reader = EntryReader(args.pkg, args.runtime)
    meshes, geom_report = decode_geometry(reader)
    material_report = json.loads(args.material_report.read_text())
    plate_report = json.loads(args.plate_report.read_text())

    skeleton, rig, tracks, clip_reports, create_armature_hierarchy, add_animation, Name_Convention = load_animation_oracle(args.parser_root, reader)
    if len(skeleton.node_defs) != 73:
        raise RuntimeError(f"expected 73-node player+weapon skeleton, got {len(skeleton.node_defs)}")
    if int(skeleton.node_defs[72].bone_hash) != WEAPON_PEDESTAL_HASH:
        raise RuntimeError(f"bone 72 expected {WEAPON_PEDESTAL_HEX}, got {int(skeleton.node_defs[72].bone_hash):08X}")

    gltf = GLTF2(
        asset=Asset(version="2.0", generator="destiny-1 d1_weapon_011c_test_glb.py + pinned tiger-animation-parser validation oracle"),
        scene=0,
        scenes=[Scene(nodes=[])],
        nodes=[], meshes=[], skins=[], animations=[], materials=[], textures=[], images=[], samplers=[],
        buffers=[], bufferViews=[], accessors=[],
    )
    root_idx, bone_indices = create_armature_hierarchy(gltf, skeleton, Name_Convention.FNV1BE)

    # Bone nodes are appended in skeleton order before the fake Skeleton root by
    # the pinned validation oracle.  Verify the dictionary agrees before using
    # node 72 as the rigid weapon attachment parent.
    pedestal_node_idx = None
    for name, idx in bone_indices.items():
        if name.upper().replace("0X", "") == WEAPON_PEDESTAL_HEX:
            pedestal_node_idx = idx
            break
    if pedestal_node_idx is None:
        # Defensive fallback to skeleton order, with the bone-hash assertion above.
        pedestal_node_idx = 72
    if pedestal_node_idx != 72:
        raise RuntimeError(f"weapon Pedestal unexpectedly mapped to glTF node {pedestal_node_idx}, expected 72")

    for tag, local_tracks in tracks:
        before = len(gltf.animations)
        add_animation(gltf, bone_indices, local_tracks, Name_Convention.FNV1BE, fps=30)
        if len(gltf.animations) != before + 1:
            raise RuntimeError(f"animation {tag} did not append exactly one glTF animation")
        gltf.animations[-1].name = tag
        gltf.animations[-1].extras = {"d1TagHash": tag}

    material_map = add_materials(gltf, args.texture_root, material_report, plate_report)

    weapon_node_indices = []
    for mi, geom in enumerate(meshes):
        pos_a = append_accessor(gltf, geom["positions"].astype("<f4"), FLOAT, "VEC3", target=ARRAY_BUFFER, with_minmax=True)
        norm_a = append_accessor(gltf, geom["normals"].astype("<f4"), FLOAT, "VEC3", target=ARRAY_BUFFER)
        uv_a = append_accessor(gltf, geom["uv"].astype("<f4"), FLOAT, "VEC2", target=ARRAY_BUFFER)
        primitives = []
        for p in geom["primitives"]:
            flat_indices = p["triangles"].reshape(-1).astype("<u2")
            idx_a = append_accessor(gltf, flat_indices, UNSIGNED_SHORT, "SCALAR", target=ELEMENT_ARRAY_BUFFER)
            primitives.append(Primitive(
                attributes=Attributes(POSITION=pos_a, NORMAL=norm_a, TEXCOORD_0=uv_a),
                indices=idx_a,
                material=material_map[p["material"]],
                mode=4,
                extras={
                    "d1Material": p["material"],
                    "d1AuxiliaryMaterials": p["auxiliary_materials"],
                    "d1SourceIndexOffset": p["index_offset"],
                    "d1SourceIndexCount": p["index_count"],
                    "d1LodValues": p["lod_values"],
                    "rigidAttachment": WEAPON_PEDESTAL_HEX,
                },
            ))
        mesh_idx = len(gltf.meshes)
        gltf.meshes.append(Mesh(
            name=f"{MODEL}_mesh{mi}_LOD1",
            primitives=primitives,
            extras={"d1Owner": OWNER, "d1Model": MODEL, "d1MeshIndex": mi},
        ))
        node_idx = len(gltf.nodes)
        gltf.nodes.append(Node(
            name=f"{MODEL}_mesh{mi}_RigidWeapon",
            mesh=mesh_idx,
            extras={
                "d1Owner": OWNER,
                "d1Model": MODEL,
                "nativeAttachment": "rigid child of weapon Pedestal; no native skin weights",
                "weaponPedestalBoneHash": WEAPON_PEDESTAL_HEX,
            },
        ))
        weapon_node_indices.append(node_idx)

    if gltf.nodes[pedestal_node_idx].children is None:
        gltf.nodes[pedestal_node_idx].children = []
    gltf.nodes[pedestal_node_idx].children.extend(weapon_node_indices)
    gltf.scenes[0].nodes = [root_idx]

    gltf.extras = {
        "d1Provenance": {
            "owner": OWNER,
            "model": MODEL,
            "skeleton": SKELETON,
            "runtimeRig": RIG,
            "animations": list(CLIPS),
            "mainMaterial": MAIN_MATERIAL,
            "smallMaterial": SMALL_MATERIAL,
            "texturePlateHeader": TEXTURE_PLATE_HEADER,
            "weaponPedestalBoneHash": WEAPON_PEDESTAL_HEX,
            "weaponPedestalBoneIndex": 72,
            "gripRBoneIndex": 24,
            "attachmentHierarchy": "Hand.R -> Grip.R -> Weapon Pedestal -> rigid weapon mesh nodes",
        },
        "reverseEngineeringPolicy": "Native rigid attachment and hashes are preserved. Core glTF PBR fields are portable approximations and must not redefine Destiny renderer semantics.",
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    gltf.save_binary(str(args.out))
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
        "weapon_pedestal_node_index": pedestal_node_idx,
        "weapon_mesh_node_indices": weapon_node_indices,
        "geometry": geom_report,
        "clips": clip_reports,
        "native_attachment": "rigid child of C410084A weapon Pedestal",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    return report


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pkg", type=Path, help="011c_0 package view with sibling patch files beside it")
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--parser-root", type=Path, required=True)
    ap.add_argument("--texture-root", type=Path, required=True, help="directory containing source/ and plates/")
    ap.add_argument("--material-report", type=Path, required=True)
    ap.add_argument("--plate-report", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()
    print(json.dumps(build(args), indent=2))


if __name__ == "__main__":
    main()
