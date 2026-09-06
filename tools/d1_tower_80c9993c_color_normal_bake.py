#!/usr/bin/env python3
"""Bake Tower material 80C9993C colour + native normal direction into glTF.

This is the second scoped visual adapter for the two proven retail grass draws in
static table 80C99827.  It preserves the successful per-triangle colour atlas,
but also replays the complete source-closed normal-direction path:

  * 0x40 instance record = first 3 rows spatial affine + final 4 shader words;
  * VS 80CA0CB7 transforms source normal/tangent and exports attr0/1/2;
  * PS 80C9994A samples t1/t3 BC5, blends XY with the same mask/control weight,
    reconstructs +Z, forms z*attr0 + x*attr1 + y*attr2, and normalizes;
  * D1 Z-up world vectors are rotated into glTF Y-up;
  * each private atlas triangle gets a constant explicit glTF TBN frame, and the
    native final normal is re-expressed in that frame as a standard normal map.

The exported geometry is already baked into glTF world coordinates.  There is no
projective node matrix: +0x30..+0x3C of the D1 record never enter the spatial
transform.  Trimesh exports custom attributes with a leading underscore, so the
final GLB JSON chunk is deterministically patched from _TANGENT to the standard
TANGENT semantic after export.

Boundary: source images are the established full-resolution ROI exports, so this
adapter samples mip 0 with the proven 80AAE177 repeat + bilinear state. Native
screen derivatives/mip selection are not replayed. The PS deferred MRT1 packing
magnitude is also not exported because glTF consumes the decoded normal direction
rather than Destiny's deferred-buffer encoding.
"""
from __future__ import annotations

import argparse
import json
import math
import struct
import sys
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import d1_tower_map_schema_validate as schema
import d1_tower_static_chunk_export as static_base
import d1_tower_80c9993c_triangle_bake as rgb_bake
from d1_tower_80ca0cb7_static_inputs import decode_static_inputs
import d1_tower_80ca0cb7_vs_replay as vs_replay
import d1_tower_grass_shader_80c9994a as grass
from d1_world_static_common import parse_static_instance_records, D1_TO_GLTF_Y_UP

MATERIAL = "80C9993C"
TABLE = "80C99827"
D1_STATIC = "80C994B2"
TRANSFORMS = "80C99845"
INFO_INDICES = (976, 978)
COLOR_TEX = "80C9988C"
NORMAL_TEX = "80C9988D"
MASK_TEX = "80C9988E"


def unit(v: np.ndarray, *, axis: int = -1, eps: float = 1e-20) -> np.ndarray:
    a = np.asarray(v, dtype=np.float32)
    n2 = np.sum(a * a, axis=axis, keepdims=True, dtype=np.float32)
    if np.any(~np.isfinite(n2)) or np.any(n2 <= np.float32(eps)):
        raise ValueError("cannot normalize zero/non-finite vector")
    return (a / np.sqrt(n2, dtype=np.float32)).astype(np.float32)


def interp_triangle(bary: np.ndarray, values: np.ndarray) -> np.ndarray:
    v = np.asarray(values, dtype=np.float32)
    if v.ndim != 2 or v.shape[0] != 3:
        raise ValueError("triangle varying must be 3xC")
    return np.einsum("hwk,kc->hwc", bary, v, optimize=True).astype(np.float32)


def native_normal_cell(
    attr3_vertices: np.ndarray,
    attr0_vertices: np.ndarray,
    attr1_vertices: np.ndarray,
    attr2_vertices: np.ndarray,
    normal_linear: np.ndarray,
    mask_linear: np.ndarray,
    bary: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Replay PS 80C9994A through its normalized final normal direction.

    Returns ``(native_tangent_vector, final_world_normal)``. The first is the
    exact pre-basis (x,y,z) vector after BC5 blend/Z reconstruction; it is not
    forcibly normalized because the native shader normalizes only after basis
    application. The second is unit length, matching the PS v_rsq_clamp path at
    the semantic level (not bit-for-bit GCN rsq approximation).
    """
    if np.asarray(attr3_vertices).shape != (3, 4):
        raise ValueError("attr3_vertices must be 3x4")
    a3 = interp_triangle(bary, attr3_vertices)
    a0 = interp_triangle(bary, attr0_vertices)
    a1 = interp_triangle(bary, attr1_vertices)
    a2 = interp_triangle(bary, attr2_vertices)

    uv0, uv2, uvm = grass.ps_uvs(a3[..., :2])
    t1 = rgb_bake.sample_repeat_bilinear(normal_linear, uv0)[..., :2]
    t3 = rgb_bake.sample_repeat_bilinear(normal_linear, uv2)[..., :2]
    mask = rgb_bake.sample_repeat_bilinear(mask_linear, uvm)[..., 0]
    xy = grass.normal_xy(t1, t3, mask, a3[..., 3])
    z = grass.reconstruct_normal_z(xy)
    nts = np.concatenate([xy, z[..., None]], axis=-1).astype(np.float32)

    # Exact PS ordering by semantic role:
    #   world = y*attr2 + x*attr1 + z*attr0
    world = (
        nts[..., 1, None] * a2
        + nts[..., 0, None] * a1
        + nts[..., 2, None] * a0
    ).astype(np.float32)
    return nts, unit(world)


def triangle_reference_frame(
    attr0_vertices: np.ndarray,
    attr1_vertices: np.ndarray,
    attr2_vertices: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    """Build one orthonormal explicit glTF frame for a private atlas triangle."""
    a0 = np.asarray(attr0_vertices, dtype=np.float32)
    a1 = np.asarray(attr1_vertices, dtype=np.float32)
    a2 = np.asarray(attr2_vertices, dtype=np.float32)
    if a0.shape != (3, 3) or a1.shape != (3, 3) or a2.shape != (3, 3):
        raise ValueError("basis varyings must each be 3x3")

    n = unit(np.mean(a0, axis=0, dtype=np.float32))
    th = np.mean(a1, axis=0, dtype=np.float32)
    t = th - n * np.dot(n, th)
    if float(np.dot(t, t)) <= 1e-12:
        # Deterministic fallback: use the Cartesian axis least parallel to N.
        axes = np.eye(3, dtype=np.float32)
        axis = axes[int(np.argmin(np.abs(axes @ n)))]
        t = axis - n * np.dot(n, axis)
    t = unit(t)
    c = unit(np.cross(n, t).astype(np.float32))
    bh = np.mean(a2, axis=0, dtype=np.float32)
    w = np.float32(-1.0 if float(np.dot(c, bh)) < 0.0 else 1.0)
    b = c * w
    return n.astype(np.float32), t.astype(np.float32), b.astype(np.float32), float(w)


def encode_normal_in_frame(
    world_normal: np.ndarray,
    n: np.ndarray,
    t: np.ndarray,
    b: np.ndarray,
) -> np.ndarray:
    """Encode unit world normal as an 8-bit linear glTF tangent-space map."""
    w = np.asarray(world_normal, dtype=np.float32)
    c = np.stack([
        np.sum(w * t, axis=-1, dtype=np.float32),
        np.sum(w * b, axis=-1, dtype=np.float32),
        np.sum(w * n, axis=-1, dtype=np.float32),
    ], axis=-1).astype(np.float32)
    c = unit(c)
    out = np.empty(c.shape[:-1] + (4,), dtype=np.uint8)
    out[..., :3] = np.rint(np.clip(np.float32(0.5) * c + np.float32(0.5), 0, 1) * 255.0).astype(np.uint8)
    out[..., 3] = 255
    return out


def encode_native_tangent_debug(nts: np.ndarray) -> np.ndarray:
    """Encode the native pre-basis (x,y,z) vector for forensic visualization."""
    v = np.asarray(nts, dtype=np.float32)
    out = np.empty(v.shape[:-1] + (4,), dtype=np.uint8)
    out[..., :3] = np.rint(np.clip(np.float32(0.5) * v + np.float32(0.5), 0, 1) * 255.0).astype(np.uint8)
    out[..., 3] = 255
    return out


def patch_glb_standard_tangent(path: Path) -> int:
    """Rename trimesh custom ``_TANGENT`` attributes to standard glTF TANGENT."""
    data = path.read_bytes()
    if len(data) < 20:
        raise ValueError("truncated GLB")
    magic, version, declared = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF" or version != 2 or declared != len(data):
        raise ValueError("invalid GLB header")
    off = 12
    chunks: list[tuple[int, bytes]] = []
    while off < len(data):
        if off + 8 > len(data):
            raise ValueError("truncated GLB chunk header")
        size, kind = struct.unpack_from("<II", data, off)
        off += 8
        if off + size > len(data):
            raise ValueError("truncated GLB chunk")
        chunks.append((kind, data[off:off+size]))
        off += size
    if not chunks or chunks[0][0] != 0x4E4F534A:
        raise ValueError("GLB JSON chunk missing")
    tree = json.loads(chunks[0][1].rstrip(b" \x00").decode("utf-8"))
    changed = 0
    for mesh in tree.get("meshes", []):
        for prim in mesh.get("primitives", []):
            attrs = prim.get("attributes", {})
            if "_TANGENT" in attrs:
                if "TANGENT" in attrs:
                    raise ValueError("both _TANGENT and TANGENT present")
                attrs["TANGENT"] = attrs.pop("_TANGENT")
                changed += 1
    if changed == 0:
        raise ValueError("no trimesh _TANGENT attributes found")

    jb = json.dumps(tree, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    jb += b" " * ((4 - (len(jb) % 4)) % 4)
    out = bytearray(struct.pack("<4sII", b"glTF", 2, 0))
    out += struct.pack("<II", len(jb), 0x4E4F534A) + jb
    for kind, chunk in chunks[1:]:
        out += struct.pack("<II", len(chunk), kind) + chunk
    struct.pack_into("<I", out, 8, len(out))
    path.write_bytes(out)
    return changed


def glb_json(path: Path) -> dict:
    data = path.read_bytes()
    magic, version, declared = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF" or version != 2 or declared != len(data):
        raise ValueError("invalid GLB")
    size, kind = struct.unpack_from("<II", data, 12)
    if kind != 0x4E4F534A:
        raise ValueError("first GLB chunk is not JSON")
    return json.loads(data[20:20+size].rstrip(b" \x00").decode("utf-8"))


def rotate_rows_y_up(v: np.ndarray) -> np.ndarray:
    r = D1_TO_GLTF_Y_UP[:3, :3].astype(np.float32)
    return np.einsum("ij,nj->ni", r, np.asarray(v, dtype=np.float32), optimize=True).astype(np.float32)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", type=Path, action="append", required=True)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--color-png", type=Path, required=True)
    ap.add_argument("--normal-png", type=Path, required=True)
    ap.add_argument("--mask-png", type=Path, required=True)
    ap.add_argument("--out-glb", type=Path, required=True)
    ap.add_argument("--out-color-atlas", type=Path, required=True)
    ap.add_argument("--out-normal-atlas", type=Path, required=True)
    ap.add_argument("--out-native-normal-atlas", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--cell-size", type=int, default=64)
    ap.add_argument("--gutter", type=int, default=3)
    args = ap.parse_args()

    c = schema.Corpus([p.resolve() for p in args.snapshot], args.runtime.resolve())
    d1 = schema.validate_static_data_d1(c, D1_STATIC)
    if d1.get("instance_transforms") != TRANSFORMS:
        raise ValueError(f"unexpected transform owner {d1.get('instance_transforms')}")
    tb, tsource = c.payload(TRANSFORMS)
    count = int(d1["instance_count"])
    if tb is None or len(tb) != count * 0x40:
        raise ValueError("exact instance-record backing unavailable/size mismatch")
    records = parse_static_instance_records(tb, count)
    table = schema.parse_static_table(c, TABLE, count)

    color = rgb_bake.load_color_srgb_as_linear(args.color_png)
    normal = rgb_bake.load_linear_rgba(args.normal_png)
    mask = rgb_bake.load_linear_rgba(args.mask_png)
    if color.shape[:2] != (1024, 1024) or normal.shape[:2] != (1024, 1024) or mask.shape[:2] != (1024, 1024):
        raise ValueError(f"unexpected target texture dimensions {color.shape} {normal.shape} {mask.shape}")

    draws = []
    triangle_total = 0
    for ii in INFO_INDICES:
        info = table["info_entries"][ii]
        mesh = table["mesh_entries"][int(info["static_index"])]
        mh = table["material_hashes"][int(info["material_index"])]
        if mh != MATERIAL or int(mesh["detail_level"]) != 1 or int(mesh["primitive_type"]) != 3:
            raise ValueError(f"retail target drift at info {ii}: {mh} {mesh}")
        v0 = static_base.read_reference_file(c, mesh["vertices0"])
        v1 = static_base.read_reference_file(c, mesh["vertices1"])
        ib = static_base.read_reference_file(c, mesh["indices"])
        if (static_base.hdr_stride(v0["header"]), static_base.hdr_stride(v1["header"])) != (8, 24):
            raise ValueError("retail target left scoped 8+24 family")
        is32 = static_base.index_is32(ib["header"])
        indices = static_base.decode_indices(ib["backing"], is32)
        off = int(mesh["index_offset"]); cnt = int(mesh["index_count"])
        faces = static_base.primitive_faces(indices[off:off+cnt], 3, is32)
        if len(faces) == 0:
            raise ValueError("target draw produced zero triangles")
        faces = np.asarray(faces, dtype=np.int64)
        used = np.unique(faces.reshape(-1))
        inputs = decode_static_inputs(v0["backing"], v1["backing"], used_indices=used)
        ti = int(info["transform_index"])
        rec = records[ti]
        shader_tail = np.array([rec.uv_scale, rec.uv_translate_x, rec.uv_translate_y, rec.tail_3c], dtype=np.float32)
        attr3 = inputs.attr3(shader_tail)
        basis = vs_replay.instance_basis(inputs, rec.affine)
        pos_d1 = vs_replay.instance_positions(inputs.v4_v6_position, rec.affine)
        pos_gltf = rotate_rows_y_up(pos_d1)
        a0 = rotate_rows_y_up(basis.attr0_normal)
        a1 = rotate_rows_y_up(basis.attr1_tangent)
        a2 = rotate_rows_y_up(basis.attr2_bitangent)

        if not np.all(inputs.raw_v20_scalar[used] == 32767):
            raise ValueError("target alpha source is no longer exact 1.0")
        if not np.all(np.isin(inputs.raw_v16_v19_tangent[used, 3], (-32767, 32767))):
            raise ValueError("target tangent handedness left exact branch-A +/-32767 domain")
        nlen = np.linalg.norm(a0[used], axis=1)
        if not np.allclose(nlen, 1.0, rtol=0, atol=2e-6):
            raise ValueError("replayed attr0 normal is not unit length")
        rel = np.cross(a0[used], a1[used]).astype(np.float32) * basis.tangent_w[used, None]
        if not np.allclose(rel, a2[used], rtol=2e-6, atol=2e-6):
            raise ValueError("replayed attr2 handed cross relation drifted")

        draws.append({
            "info_index": ii,
            "static_index": int(info["static_index"]),
            "transform_index": ti,
            "faces": faces,
            "positions": pos_gltf,
            "attr3": attr3,
            "attr0": a0,
            "attr1": a1,
            "attr2": a2,
            "shader_tail": shader_tail.tolist(),
            "affine": rec.affine.tolist(),
            "normal_length_range": [float(basis.normal_length[used].min()), float(basis.normal_length[used].max())],
            "buffers": {"v0": mesh["vertices0"], "v1": mesh["vertices1"], "indices": mesh["indices"]},
        })
        triangle_total += int(len(faces))

    grid = int(math.ceil(math.sqrt(triangle_total)))
    atlas_w = atlas_h = grid * args.cell_size
    color_atlas = np.zeros((atlas_h, atlas_w, 4), dtype=np.uint8)
    normal_atlas = np.zeros((atlas_h, atlas_w, 4), dtype=np.uint8)
    native_atlas = np.zeros((atlas_h, atlas_w, 4), dtype=np.uint8)
    bary, local_uv_pixels = rgb_bake.atlas_cell_barycentrics(args.cell_size, args.gutter)

    scene = trimesh.Scene()
    tri_cursor = 0
    report_draws = []
    world_min = np.full(3, np.inf, dtype=np.float64)
    world_max = np.full(3, -np.inf, dtype=np.float64)
    nts_min = np.full(3, np.inf, dtype=np.float64)
    nts_max = np.full(3, -np.inf, dtype=np.float64)
    frame_w_counts = {"+1": 0, "-1": 0}

    for draw in draws:
        out_pos = []
        out_uv = []
        out_norm = []
        out_tangent = []
        out_faces = []
        start = tri_cursor
        for face in draw["faces"]:
            cell = tri_cursor
            cx = (cell % grid) * args.cell_size
            cy = (cell // grid) * args.cell_size
            a3 = draw["attr3"][face]
            a0 = draw["attr0"][face]
            a1 = draw["attr1"][face]
            a2 = draw["attr2"][face]

            color_cell = rgb_bake.bake_cell(a3, color, mask, bary)
            nts, world_n = native_normal_cell(a3, a0, a1, a2, normal, mask, bary)
            nref, tref, bref, tw = triangle_reference_frame(a0, a1, a2)
            gltf_normal_cell = encode_normal_in_frame(world_n, nref, tref, bref)
            native_cell = encode_native_tangent_debug(nts)

            color_atlas[cy:cy+args.cell_size, cx:cx+args.cell_size] = color_cell
            normal_atlas[cy:cy+args.cell_size, cx:cx+args.cell_size] = gltf_normal_cell
            native_atlas[cy:cy+args.cell_size, cx:cx+args.cell_size] = native_cell
            world_min = np.minimum(world_min, world_n.reshape(-1, 3).min(axis=0))
            world_max = np.maximum(world_max, world_n.reshape(-1, 3).max(axis=0))
            nts_min = np.minimum(nts_min, nts.reshape(-1, 3).min(axis=0))
            nts_max = np.maximum(nts_max, nts.reshape(-1, 3).max(axis=0))
            frame_w_counts["+1" if tw > 0 else "-1"] += 1

            base = len(out_pos)
            out_pos.extend(draw["positions"][face].tolist())
            out_norm.extend([nref.tolist()] * 3)
            tan4 = [float(tref[0]), float(tref[1]), float(tref[2]), float(tw)]
            out_tangent.extend([tan4] * 3)
            pix = local_uv_pixels + np.array([cx, cy], dtype=np.float32)
            uv = np.empty((3, 2), dtype=np.float32)
            uv[:, 0] = pix[:, 0] / np.float32(atlas_w)
            uv[:, 1] = pix[:, 1] / np.float32(atlas_h)
            out_uv.extend(uv.tolist())
            out_faces.append([base, base + 1, base + 2])
            tri_cursor += 1

        tm = trimesh.Trimesh(
            vertices=np.asarray(out_pos, dtype=np.float32),
            faces=np.asarray(out_faces, dtype=np.int64),
            vertex_normals=np.asarray(out_norm, dtype=np.float32),
            vertex_attributes={"TANGENT": np.asarray(out_tangent, dtype=np.float32)},
            process=False,
            validate=False,
        )
        tm.metadata = {
            "material_hash": MATERIAL,
            "vertex_shader": grass.VERTEX_SHADER,
            "pixel_shader": grass.PIXEL_SHADER,
            "info_index": draw["info_index"],
            "static_index": draw["static_index"],
            "transform_index": draw["transform_index"],
            "atlas_triangle_range": [start, tri_cursor],
            "spatial_policy": "D1 first 3x4 instance rows baked into vertices; shader tail excluded from transform",
            "basis_policy": "D1 Z-up native normal replay converted to glTF Y-up and re-expressed in explicit per-triangle TBN",
        }
        draw["trimesh"] = tm
        draw["uv"] = np.asarray(out_uv, dtype=np.float32)
        report_draws.append({
            "info_index": draw["info_index"],
            "static_index": draw["static_index"],
            "transform_index": draw["transform_index"],
            "triangles": int(len(draw["faces"])),
            "duplicated_vertices": int(len(out_pos)),
            "atlas_triangle_range": [start, tri_cursor],
            "instance_shader_tail_30_3c": draw["shader_tail"],
            "spatial_affine_3x4": [row[:4] for row in draw["affine"][:3]],
            "normal_length_range_before_vs_normalize": draw["normal_length_range"],
            "buffers": draw["buffers"],
        })

    if tri_cursor != triangle_total:
        raise ValueError(f"atlas cursor {tri_cursor} != triangle total {triangle_total}")

    args.out_color_atlas.parent.mkdir(parents=True, exist_ok=True)
    color_image = Image.fromarray(color_atlas, mode="RGBA")
    normal_image = Image.fromarray(normal_atlas, mode="RGBA")
    native_image = Image.fromarray(native_atlas, mode="RGBA")
    color_image.save(args.out_color_atlas)
    normal_image.save(args.out_normal_atlas)
    native_image.save(args.out_native_normal_atlas)

    material = trimesh.visual.material.PBRMaterial(
        name="D1_80C9993C_PS80C9994A_BakedColorNativeNormal",
        baseColorTexture=color_image,
        normalTexture=normal_image,
        baseColorFactor=[1.0, 1.0, 1.0, 1.0],
        metallicFactor=0.0,
        roughnessFactor=1.0,
        doubleSided=True,
        alphaMode="OPAQUE",
    )
    for draw in draws:
        draw["trimesh"].visual = trimesh.visual.TextureVisuals(uv=draw["uv"], material=material)
        geom_name = f"grass_native_normal_{draw['static_index']}_info{draw['info_index']}"
        node_name = f"{TABLE}_info{draw['info_index']}_xform{draw['transform_index']}_BAKED_AFFINE"
        scene.add_geometry(draw["trimesh"], geom_name=geom_name, node_name=node_name)

    args.out_glb.parent.mkdir(parents=True, exist_ok=True)
    scene.export(args.out_glb)
    tangent_patch_count = patch_glb_standard_tangent(args.out_glb)
    tree = glb_json(args.out_glb)
    if tangent_patch_count != len(draws):
        raise ValueError(f"patched {tangent_patch_count} TANGENT attributes for {len(draws)} meshes")
    for mesh in tree.get("meshes", []):
        for prim in mesh.get("primitives", []):
            attrs = prim.get("attributes", {})
            if "TANGENT" not in attrs or "_TANGENT" in attrs or "NORMAL" not in attrs:
                raise ValueError(f"standard normal/tangent semantics absent after patch: {attrs}")
    mats = tree.get("materials", [])
    if not mats or not all("normalTexture" in m for m in mats):
        raise ValueError("normalTexture missing from exported glTF material")

    report = {
        "schema_version": 2,
        "status": "D1_80C9993C_COLOR_NATIVE_NORMAL_GLTF_ADAPTER",
        "material": MATERIAL,
        "vertex_shader": grass.VERTEX_SHADER,
        "pixel_shader": grass.PIXEL_SHADER,
        "table": TABLE,
        "d1_static": D1_STATIC,
        "instance_records": TRANSFORMS,
        "instance_record_source": tsource,
        "source_textures": {
            "t0_t2_color": {"hash": COLOR_TEX, "path": str(args.color_png), "colorspace": "sRGB sampled to linear"},
            "t1_t3_normal": {"hash": NORMAL_TEX, "path": str(args.normal_png), "colorspace": "linear BC5 RG"},
            "t4_mask": {"hash": MASK_TEX, "path": str(args.mask_png), "colorspace": "linear BC4"},
        },
        "sampler": {
            "hash": "80AAE177",
            "gnm_words": ["00000000", "00F00000", "0A503F80", "00000000"],
            "wrap_xyz": "Wrap", "mag_filter": "Bilinear", "min_filter": "Bilinear", "mip_filter": "Linear",
        },
        "atlas": {
            "width": atlas_w, "height": atlas_h, "cell_size": args.cell_size,
            "gutter": args.gutter, "grid": grid, "triangle_count": triangle_total,
            "color": str(args.out_color_atlas),
            "gltf_normal": str(args.out_normal_atlas),
            "native_tangent_debug": str(args.out_native_normal_atlas),
        },
        "draws": report_draws,
        "normal_stats": {
            "final_gltf_world_component_min": world_min.tolist(),
            "final_gltf_world_component_max": world_max.tolist(),
            "native_prebasis_component_min": nts_min.tolist(),
            "native_prebasis_component_max": nts_max.tolist(),
            "explicit_tangent_w_triangle_counts": frame_w_counts,
        },
        "gltf": {
            "geometry_count": len(draws),
            "standard_tangent_attributes_patched": tangent_patch_count,
            "node_transform_policy": "identity; spatial 3x4 D1 affine is baked into vertex positions",
            "world_basis": "D1 Z-up -> glTF Y-up rigid adapter",
            "normal_texture_policy": "native final normal direction re-expressed in explicit per-triangle orthonormal glTF TBN",
        },
        "exact_components": [
            "retail geometry/index draw ranges",
            "D1 0x40 instance record split: first 3x4 spatial, final 4 shader words non-spatial",
            "80CA0CB7 source normal/tangent transform and handed cross basis",
            "per-instance attr3 UV/control affine from +0x30/+0x34/+0x38",
            "80C9994A BC5 t1/t3 normal branch blend and +Z reconstruction",
            "80C9994A z*attr0 + x*attr1 + y*attr2 final normal direction and normalization",
            "80AAE177 repeat+bilinear mip0 sampling",
            "BC3 sRGB colour arithmetic and linear BC5/BC4 sampling",
            "D1 Z-up to glTF Y-up rigid basis conversion",
        ],
        "adapter_components": [
            "triangle-private atlas UVs",
            "per-triangle explicit orthonormal glTF TBN used to encode the already-solved native final normal direction",
            "trimesh _TANGENT JSON semantic renamed to standard glTF TANGENT without changing accessor data",
        ],
        "approximation_boundary": [
            "native screen-space derivatives and runtime mip selection are not replayed",
            "GCN reciprocal-square-root approximation is represented by float32 semantic normalization, not bit-for-bit v_rsq emulation",
            "Destiny deferred MRT1 normal packing magnitude/auxiliary alpha is not represented because glTF consumes decoded normal direction",
        ],
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "status": report["status"],
        "triangles": triangle_total,
        "atlas": report["atlas"],
        "normal_stats": report["normal_stats"],
        "tangent_patch_count": tangent_patch_count,
        "out_glb": str(args.out_glb),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
