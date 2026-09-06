#!/usr/bin/env python3
"""Bake the scoped Tower grass shader 80C9994A into a glTF-compatible atlas.

This is a visualization adapter, not a replacement claim for the native shader.
Exact inputs reused here:
  * material 80C9993C -> VS 80CA0CB7 -> PS 80C9994A;
  * retail-canary-locked 8+24 source-to-VGPR mapping;
  * exact per-instance attr3 affine from transform dwords 12..15;
  * exact PS colour arithmetic and material constants;
  * texture t0/t2 = 80C9988C, t4 = 80C9988E;
  * 80AAE177 wrap/repeat addressing and bilinear filtering;
  * 80C9988C is sampled as sRGB, 80C9988E as linear.

The native shader depends on interpolated attr3.w, so a single ordinary texture
using the original mesh UVs cannot encode the result.  This adapter duplicates
vertices per triangle and assigns each triangle a private atlas cell.  Pixels in
that cell replay the native branch colour math using barycentrically interpolated
80CA0CB7 outputs.

Boundary: the exported PNGs contain only the full-resolution texture surface in
the established D1 exporter.  This adapter therefore samples mip 0 with the exact
wrap + bilinear policy.  Native derivative/LOD/mip selection is NOT claimed exact.
The output is suitable for visual proof in Blender, not for declaring the full
runtime sampler pipeline solved.
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
from d1_tower_80ca0cb7_static_inputs import decode_static_inputs
import d1_tower_grass_shader_80c9994a as grass

MATERIAL = "80C9993C"
TABLE = "80C99827"
D1_STATIC = "80C994B2"
TRANSFORMS = "80C99845"
INFO_INDICES = (976, 978)
COLOR_TEX = "80C9988C"
MASK_TEX = "80C9988E"
# Exact PS constant vector 1 from 80C9994B.
TINT_RGB = np.array(
    [0.5335593819618225, 0.431231826543808, 0.4029434025287628],
    dtype=np.float32,
)


def srgb_to_linear(x):
    a = np.asarray(x, dtype=np.float32)
    return np.where(a <= np.float32(0.04045), a / np.float32(12.92),
                    ((a + np.float32(0.055)) / np.float32(1.055)) ** np.float32(2.4))


def linear_to_srgb(x):
    a = np.clip(np.asarray(x, dtype=np.float32), 0.0, 1.0)
    return np.where(a <= np.float32(0.0031308), np.float32(12.92) * a,
                    np.float32(1.055) * (a ** (np.float32(1.0) / np.float32(2.4))) - np.float32(0.055))


def load_color_srgb_as_linear(path: Path) -> np.ndarray:
    im = np.asarray(Image.open(path).convert("RGBA"), dtype=np.float32) / np.float32(255.0)
    out = im.copy()
    out[..., :3] = srgb_to_linear(out[..., :3])
    return out


def load_linear_rgba(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGBA"), dtype=np.float32) / np.float32(255.0)


def sample_repeat_bilinear(image: np.ndarray, uv: np.ndarray) -> np.ndarray:
    """Normalized repeat + bilinear sample with texel-center convention.

    For normalized coordinates, x=u*width-0.5 and y=v*height-0.5.  Integer
    neighbours wrap modulo the texture size.  This is the ordinary normalized
    bilinear interpretation of the proven 80AAE177 sampler state at mip 0.
    """
    tex = np.asarray(image, dtype=np.float32)
    q = np.asarray(uv, dtype=np.float32)
    if tex.ndim != 3 or q.shape[-1] != 2:
        raise ValueError("expected HxWxC image and (...,2) UVs")
    h, w, _ = tex.shape
    shape = q.shape[:-1]
    f = q.reshape(-1, 2)
    x = np.mod(f[:, 0], np.float32(1.0)) * np.float32(w) - np.float32(0.5)
    y = np.mod(f[:, 1], np.float32(1.0)) * np.float32(h) - np.float32(0.5)
    x0f = np.floor(x); y0f = np.floor(y)
    tx = (x - x0f).astype(np.float32); ty = (y - y0f).astype(np.float32)
    x0 = x0f.astype(np.int64) % w; y0 = y0f.astype(np.int64) % h
    x1 = (x0 + 1) % w; y1 = (y0 + 1) % h
    c00 = tex[y0, x0]; c10 = tex[y0, x1]; c01 = tex[y1, x0]; c11 = tex[y1, x1]
    top = c00 + tx[:, None] * (c10 - c00)
    bot = c01 + tx[:, None] * (c11 - c01)
    out = top + ty[:, None] * (bot - top)
    return out.reshape(shape + (tex.shape[2],))


def atlas_cell_barycentrics(cell_size: int, gutter: int):
    """Return cell pixels, edge-extruded barycentrics, and three vertex pixels."""
    if cell_size < 8 or gutter < 1 or gutter * 2 + 3 >= cell_size:
        raise ValueError("invalid atlas cell/gutter")
    # Vertex locations are pixel-center coordinates in glTF's top-left texture convention.
    a = np.array([gutter + 0.5, gutter + 0.5], dtype=np.float32)
    b = np.array([cell_size - gutter - 0.5, gutter + 0.5], dtype=np.float32)
    c = np.array([gutter + 0.5, cell_size - gutter - 0.5], dtype=np.float32)
    yy, xx = np.mgrid[0:cell_size, 0:cell_size]
    p = np.stack([xx.astype(np.float32) + 0.5, yy.astype(np.float32) + 0.5], axis=-1)
    wb = (p[..., 0] - a[0]) / (b[0] - a[0])
    wc = (p[..., 1] - a[1]) / (c[1] - a[1])
    wa = np.float32(1.0) - wb - wc
    bary = np.stack([wa, wb, wc], axis=-1)
    # Fill the entire private cell with a clamped continuation of the triangle.
    # This creates a deterministic edge extrusion so glTF bilinear filtering cannot
    # pull black pixels into the triangle along atlas seams.
    bary = np.maximum(bary, np.float32(0.0))
    denom = np.sum(bary, axis=-1, keepdims=True)
    bary = bary / np.maximum(denom, np.float32(1e-20))
    return bary.astype(np.float32), np.stack([a, b, c], axis=0)


def bake_cell(attr3_vertices: np.ndarray, color_linear: np.ndarray,
              mask_linear: np.ndarray, bary: np.ndarray) -> np.ndarray:
    if attr3_vertices.shape != (3, 4):
        raise ValueError("attr3_vertices must be 3x4")
    interp = np.einsum("hwk,kc->hwc", bary, attr3_vertices, optimize=True).astype(np.float32)
    uv0, uv2, uvm = grass.ps_uvs(interp[..., :2])
    t0 = sample_repeat_bilinear(color_linear, uv0)
    t2 = sample_repeat_bilinear(color_linear, uv2)
    mask = sample_repeat_bilinear(mask_linear, uvm)[..., 0]
    rgb_linear = grass.base_rgb(t0[..., :3], t2[..., :3], mask, interp[..., 3], TINT_RGB)
    rgb_srgb = linear_to_srgb(rgb_linear)
    out = np.empty(rgb_srgb.shape[:2] + (4,), dtype=np.uint8)
    out[..., :3] = np.rint(np.clip(rgb_srgb, 0.0, 1.0) * 255.0).astype(np.uint8)
    out[..., 3] = 255
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", type=Path, action="append", required=True)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--color-png", type=Path, required=True)
    ap.add_argument("--mask-png", type=Path, required=True)
    ap.add_argument("--out-glb", type=Path, required=True)
    ap.add_argument("--out-atlas", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--cell-size", type=int, default=64)
    ap.add_argument("--gutter", type=int, default=3)
    args = ap.parse_args()

    c = schema.Corpus([p.resolve() for p in args.snapshot], args.runtime.resolve())
    d1 = schema.validate_static_data_d1(c, D1_STATIC)
    if d1.get("instance_transforms") != TRANSFORMS:
        raise ValueError(f"unexpected transform owner {d1.get('instance_transforms')}")
    tb, tsource = c.payload(TRANSFORMS)
    if tb is None or len(tb) != int(d1["instance_count"]) * 0x40:
        raise ValueError("exact transform backing unavailable/size mismatch")
    table = schema.parse_static_table(c, TABLE, int(d1["instance_count"]))

    color = load_color_srgb_as_linear(args.color_png)
    mask = load_linear_rgba(args.mask_png)
    if color.shape[:2] != (1024, 1024) or mask.shape[:2] != (1024, 1024):
        raise ValueError(f"unexpected target texture dimensions {color.shape} {mask.shape}")

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
        indices = static_base.decode_indices(ib["backing"], static_base.index_is32(ib["header"]))
        off = int(mesh["index_offset"]); cnt = int(mesh["index_count"])
        faces = static_base.primitive_faces(indices[off:off+cnt], 3, static_base.index_is32(ib["header"]))
        if len(faces) == 0:
            raise ValueError("target draw produced zero triangles")
        used = np.unique(faces.reshape(-1))
        inputs = decode_static_inputs(v0["backing"], v1["backing"], used_indices=used)
        ti = int(info["transform_index"])
        constants = struct.unpack_from("<4f", tb, ti * 0x40 + 0x30)
        attr3 = inputs.attr3(constants)
        if not np.all(inputs.raw_v20_scalar[used] == 32767):
            raise ValueError("target alpha source is no longer exact 1.0")
        matrix = np.frombuffer(tb, dtype="<f4", count=16, offset=ti*0x40).reshape(4,4).astype(np.float64)
        draws.append({
            "info_index": ii,
            "static_index": int(info["static_index"]),
            "transform_index": ti,
            "mesh": mesh,
            "faces": np.asarray(faces, dtype=np.int64),
            "positions": inputs.v4_v6_position,
            "attr3": attr3,
            "instance_constants": list(constants),
            "matrix": matrix,
            "buffers": {"v0": mesh["vertices0"], "v1": mesh["vertices1"], "indices": mesh["indices"]},
        })
        triangle_total += int(len(faces))

    grid = int(math.ceil(math.sqrt(triangle_total)))
    atlas_w = atlas_h = grid * args.cell_size
    atlas = np.zeros((atlas_h, atlas_w, 4), dtype=np.uint8)
    bary, local_uv_pixels = atlas_cell_barycentrics(args.cell_size, args.gutter)

    scene = trimesh.Scene()
    tri_cursor = 0
    report_draws = []
    for draw in draws:
        out_pos = []
        out_uv = []
        out_faces = []
        start = tri_cursor
        for face in draw["faces"]:
            cell = tri_cursor
            cx = (cell % grid) * args.cell_size
            cy = (cell // grid) * args.cell_size
            a3 = draw["attr3"][face]
            cell_rgba = bake_cell(a3, color, mask, bary)
            atlas[cy:cy+args.cell_size, cx:cx+args.cell_size] = cell_rgba
            base = len(out_pos)
            out_pos.extend(draw["positions"][face].tolist())
            pix = local_uv_pixels + np.array([cx, cy], dtype=np.float32)
            # glTF normalized texture coordinates use a top-left (0,0) origin.
            uv = np.empty((3, 2), dtype=np.float32)
            uv[:, 0] = pix[:, 0] / np.float32(atlas_w)
            uv[:, 1] = pix[:, 1] / np.float32(atlas_h)
            out_uv.extend(uv.tolist())
            out_faces.append([base, base+1, base+2])
            tri_cursor += 1

        tm = trimesh.Trimesh(vertices=np.asarray(out_pos, dtype=np.float32),
                             faces=np.asarray(out_faces, dtype=np.int64),
                             process=False, validate=False)
        # Material is assigned after the atlas image is finalized; all meshes share it.
        tm.metadata = {
            "material_hash": MATERIAL,
            "vertex_shader": grass.VERTEX_SHADER,
            "pixel_shader": grass.PIXEL_SHADER,
            "info_index": draw["info_index"],
            "static_index": draw["static_index"],
            "transform_index": draw["transform_index"],
            "atlas_triangle_range": [start, tri_cursor],
            "native_alpha": "attr0.w=v20=1.0 on all selected retail vertices",
            "adapter_boundary": "mip0 wrap+bilinear bake; native derivative/mip selection not replayed",
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
            "instance_dwords12_15": draw["instance_constants"],
            "buffers": draw["buffers"],
        })

    args.out_atlas.parent.mkdir(parents=True, exist_ok=True)
    atlas_image = Image.fromarray(atlas, mode="RGBA")
    atlas_image.save(args.out_atlas)

    material = trimesh.visual.material.PBRMaterial(
        name="D1_80C9993C_PS80C9994A_BakedRGB",
        baseColorTexture=atlas_image,
        baseColorFactor=[1.0, 1.0, 1.0, 1.0],
        metallicFactor=0.0,
        roughnessFactor=1.0,
        doubleSided=True,
        alphaMode="OPAQUE",
    )
    for draw in draws:
        draw["trimesh"].visual = trimesh.visual.TextureVisuals(uv=draw["uv"], material=material)
        geom_name = f"grass_{draw['static_index']}_info{draw['info_index']}"
        node_name = f"{TABLE}_info{draw['info_index']}_xform{draw['transform_index']}"
        scene.add_geometry(draw["trimesh"], geom_name=geom_name, node_name=node_name,
                           transform=draw["matrix"])

    args.out_glb.parent.mkdir(parents=True, exist_ok=True)
    scene.export(args.out_glb)

    report = {
        "schema_version": 1,
        "status": "D1_80C9993C_TRIANGLE_ATLAS_VISUAL_ADAPTER",
        "material": MATERIAL,
        "vertex_shader": grass.VERTEX_SHADER,
        "pixel_shader": grass.PIXEL_SHADER,
        "table": TABLE,
        "d1_static": D1_STATIC,
        "instance_transforms": TRANSFORMS,
        "transform_source": tsource,
        "source_textures": {
            "t0_t2_color": {"hash": COLOR_TEX, "path": str(args.color_png), "sampling_colorspace": "sRGB->linear"},
            "t4_mask": {"hash": MASK_TEX, "path": str(args.mask_png), "sampling_colorspace": "linear"},
        },
        "sampler": {
            "hash": "80AAE177",
            "gnm_words": ["00000000", "00F00000", "0A503F80", "00000000"],
            "wrap_xyz": "Wrap",
            "mag_filter": "Bilinear",
            "min_filter": "Bilinear",
            "mip_filter": "Linear",
        },
        "atlas": {"width": atlas_w, "height": atlas_h, "cell_size": args.cell_size,
                  "gutter": args.gutter, "grid": grid, "triangle_count": triangle_total},
        "tint_rgb_exact_ps_vec1": TINT_RGB.tolist(),
        "draws": report_draws,
        "exact_components": [
            "retail geometry/index ranges and transforms",
            "scoped 80CA0CB7 source input reconstruction",
            "per-instance attr3 affine",
            "80C9994A RGB arithmetic/constants",
            "80AAE177 repeat+bilinear mip0 address/filter behavior",
            "BC3 sRGB decode and glTF baseColor sRGB re-encode",
            "opaque alpha from v20=1.0",
        ],
        "approximation_boundary": [
            "native screen-space derivatives and runtime mip selection are not replayed",
            "normal/deferred auxiliary outputs are not baked into this RGB proof GLB",
        ],
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "status": report["status"], "triangles": triangle_total,
        "atlas": report["atlas"], "draws": report_draws,
        "out_glb": str(args.out_glb), "out_atlas": str(args.out_atlas),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
