#!/usr/bin/env python3
"""Build a source-constrained portable preview for Tower card model 80CA0B97.

Exact native facts already closed elsewhere:

* material 80B9E8C2 -> PS 80B9E8CF;
* material 80B9E8C3 -> PS 80B9E8D0;
* both bind t0=80B9F76D and t1=80B9E867, both BC4 scalar textures;
* exact GCN proves t0.x*t1.x is a multiplicative ancestor of final MRT0 alpha;
* 80B9E8CF exports RGB premultiplied by that final alpha scalar;
* 80B9E8D0 exports RGB=0 and the same class of final alpha scalar;
* material +0x20 byte0 == 0x88 selects blend state 8:
  Source + Destination*(1-SourceAlpha).

Core glTF cannot reproduce the native TFX-driven, two-sample alpha expression.
This adapter therefore creates a deliberately bounded *proxy* alpha texture from
exact retail t0.x*t1.x in one common normalized UV domain.  It is not promoted as
native alpha.  Its purpose is to stop Blender from rendering these proven
transparent/compositional cards as opaque white sheets while retaining every
source resource and the exact native contract in extras.

The source GLB BIN chunk is preserved as an exact prefix.  Geometry, transforms,
indices, accessors and existing exact source textures are unchanged.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
from pathlib import Path

import numpy as np
from PIL import Image

from d1_gltf_layer_merge import read_glb, write_glb

MODEL = "80CA0B97"
MAT_COLOR = "80B9E8C2"
MAT_ATTEN = "80B9E8C3"
T0 = "80B9F76D"
T1 = "80B9E867"
PS_COLOR = "80B9E8CF"
PS_ATTEN = "80B9E8D0"


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for q in iter(lambda: f.read(1 << 20), b""):
            h.update(q)
    return h.hexdigest()


def material_hash(m: dict) -> str:
    ex = m.get("extras") or {}
    return str(ex.get("d1_material_taghash") or "").upper()


def source_texture_index(doc: dict, tag: str) -> int:
    image_index = None
    for i, image in enumerate(doc.get("images", [])):
        ex = image.get("extras") or {}
        if str(ex.get("d1_taghash") or "").upper() == tag:
            image_index = i
            break
    if image_index is None:
        raise ValueError(f"exact source image {tag} is not embedded")
    hits = [i for i, t in enumerate(doc.get("textures", [])) if int(t.get("source", -1)) == image_index]
    if len(hits) != 1:
        raise ValueError(f"expected one glTF texture for {tag}, got {hits}")
    return hits[0]


def manifest_png(manifest: dict, texture_dir: Path, tag: str) -> tuple[Path, dict]:
    row = (manifest.get("textures") or {}).get(tag)
    if not row:
        raise ValueError(f"manifest missing texture {tag}")
    rel = row.get("png")
    if not rel:
        raise ValueError(f"manifest texture {tag} has no PNG")
    p = texture_dir / rel
    if not p.exists():
        raise ValueError(f"missing decoded exact PNG {p}")
    return p, row


def append_png(doc: dict, bin_data: bytes, png: bytes, name: str, extras: dict, sampler: int | None) -> tuple[bytes, int]:
    pad = (-len(bin_data)) & 3
    if pad:
        bin_data += b"\x00" * pad
    off = len(bin_data)
    bin_data += png
    bvi = len(doc.setdefault("bufferViews", []))
    doc["bufferViews"].append({"buffer": 0, "byteOffset": off, "byteLength": len(png)})
    ii = len(doc.setdefault("images", []))
    doc["images"].append({"name": name, "mimeType": "image/png", "bufferView": bvi, "extras": extras})
    ti = len(doc.setdefault("textures", []))
    tex = {"source": ii, "name": name}
    if sampler is not None:
        tex["sampler"] = int(sampler)
    doc["textures"].append(tex)
    return bin_data, ti


def build_proxy_rgba(t0_path: Path, t1_path: Path, rgb: tuple[int, int, int]) -> tuple[bytes, dict]:
    with Image.open(t0_path) as im0, Image.open(t1_path) as im1:
        a0 = np.asarray(im0.convert("RGB"), dtype=np.uint8)[..., 0]
        a1 = np.asarray(im1.convert("RGB"), dtype=np.uint8)[..., 0]
    source0_shape = [int(a0.shape[1]), int(a0.shape[0])]
    source1_shape = [int(a1.shape[1]), int(a1.shape[0])]
    # The two exact retail resources have the same 4:1 aspect ratio and t1 is
    # exactly 2x t0 in each dimension.  A single common normalized-UV product is
    # a portable proxy only; native GCN computes its own sample coordinates.
    if source1_shape != [source0_shape[0] * 2, source0_shape[1] * 2]:
        raise ValueError(f"unexpected t0/t1 dimensional relation {source0_shape} -> {source1_shape}")
    a0_up = np.asarray(Image.fromarray(a0, mode="L").resize(tuple(source1_shape), Image.Resampling.BILINEAR), dtype=np.uint16)
    a1_u16 = a1.astype(np.uint16)
    alpha = ((a0_up * a1_u16 + 127) // 255).astype(np.uint8)
    rgba = np.empty((alpha.shape[0], alpha.shape[1], 4), dtype=np.uint8)
    rgba[..., 0] = rgb[0]
    rgba[..., 1] = rgb[1]
    rgba[..., 2] = rgb[2]
    rgba[..., 3] = alpha
    out = io.BytesIO()
    Image.fromarray(rgba, mode="RGBA").save(out, format="PNG", optimize=False)
    payload = out.getvalue()
    stats = {
        "source_t0_shape": source0_shape,
        "source_t1_shape": source1_shape,
        "proxy_shape": source1_shape,
        "alpha_min_u8": int(alpha.min()),
        "alpha_max_u8": int(alpha.max()),
        "alpha_zero_fraction": float(np.count_nonzero(alpha == 0) / alpha.size),
        "alpha_nonopaque_fraction": float(np.count_nonzero(alpha < 255) / alpha.size),
        "alpha_mean": float(alpha.mean() / 255.0),
        "png_sha256": sha256_bytes(payload),
        "png_bytes": len(payload),
    }
    return payload, stats


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-glb", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--texture-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    a = ap.parse_args()

    manifest = json.loads(a.manifest.read_text())
    doc, bin_data = read_glb(a.input_glb)
    original_bin = bytes(bin_data)
    original_counts = {k: len(doc.get(k, [])) for k in ("bufferViews", "images", "textures", "materials", "meshes", "nodes", "accessors")}

    mats = {material_hash(m): (i, m) for i, m in enumerate(doc.get("materials", [])) if material_hash(m)}
    if MAT_COLOR not in mats or MAT_ATTEN not in mats:
        raise ValueError(f"target materials absent: have color={MAT_COLOR in mats} attenuation={MAT_ATTEN in mats}")

    # Fail closed on exact material/shader/resource identity from the manifest.
    for mh, ps in ((MAT_COLOR, PS_COLOR), (MAT_ATTEN, PS_ATTEN)):
        mr = (manifest.get("materials") or {}).get(mh)
        if not mr or str(mr.get("pixel_shader") or "").upper() != ps:
            raise ValueError(f"{mh} shader identity drift")
        bindings = [(int(x["texture_index"]), str(x["texture"]).upper()) for x in mr.get("ps_texture_tags", [])]
        if bindings != [(0, T0), (1, T1)]:
            raise ValueError(f"{mh} texture bindings drift: {bindings}")

    t0_path, t0_row = manifest_png(manifest, a.texture_dir, T0)
    t1_path, t1_row = manifest_png(manifest, a.texture_dir, T1)
    for tag, row, expected in ((T0, t0_row, [512, 128]), (T1, t1_row, [1024, 256])):
        if str(row.get("format_name") or "").upper() != "BC4":
            raise ValueError(f"{tag} format drift: {row.get('format_name')}")
        hi = row.get("header_info") or {}
        if [int(hi.get("width", -1)), int(hi.get("height", -1))] != expected:
            raise ValueError(f"{tag} dimensions drift: {hi}")

    source_t0_tex = source_texture_index(doc, T0)
    source_sampler = doc["textures"][source_t0_tex].get("sampler")

    rows = []
    for mh, ps, rgb, native_rgb in (
        (MAT_COLOR, PS_COLOR, (255, 255, 255), "SOURCE_RGB_COEFFICIENT * FINAL_ALPHA_SCALAR"),
        (MAT_ATTEN, PS_ATTEN, (0, 0, 0), "EXPLICIT_ZERO"),
    ):
        png, stats = build_proxy_rgba(t0_path, t1_path, rgb)
        extras = {
            "d1_derived_preview": True,
            "d1_model": MODEL,
            "d1_material": mh,
            "d1_pixel_shader": ps,
            "d1_exact_sources": [T0, T1],
            "d1_exact_alpha_ancestor": "t0.x * t1.x multiplies FINAL_ALPHA_SCALAR",
            "d1_proxy_alpha": "resampled_t0.x * t1.x in one common normalized UV domain",
            "d1_proxy_status": "SOURCE_CONSTRAINED_PORTABLE_APPROXIMATION",
            "d1_native_rgb_structure": native_rgb,
            "d1_native_blend_selector_raw": "0x88",
            "d1_native_blend_state_index": 8,
            "d1_native_blend_equation": "Source + Destination*(1-SourceAlpha)",
        }
        bin_data, tex_idx = append_png(doc, bin_data, png, f"D1_80CA0B97_{mh}_CARD_PROXY", extras, source_sampler)
        mi, mat = mats[mh]
        pbr = mat.setdefault("pbrMetallicRoughness", {})
        pbr["baseColorTexture"] = {"index": tex_idx}
        pbr["baseColorFactor"] = [1.0, 1.0, 1.0, 1.0]
        pbr["metallicFactor"] = 0.0
        pbr["roughnessFactor"] = 1.0
        mat["alphaMode"] = "BLEND"
        ex = mat.setdefault("extras", {})
        ex["d1_exact_blend_equation"] = "Source + Destination*(1-SourceAlpha)"
        ex["d1_exact_blend_selector"] = {"raw": "0x88", "index": 8}
        ex["d1_card_proxy_texture_index"] = tex_idx
        ex["d1_card_proxy_alpha_status"] = "SOURCE_CONSTRAINED_PORTABLE_APPROXIMATION"
        ex["d1_card_proxy_missing_native_terms"] = [
            "native independent t0/t1 sample-coordinate dataflow",
            "TFX/runtime-written PS CBuffer terms",
            "higher-level/global shader inputs",
        ]
        rows.append({"material": mh, "material_index": mi, "pixel_shader": ps, "derived_texture_index": tex_idx, "proxy": stats})

    doc.setdefault("asset", {"version": "2.0"}).setdefault("extras", {})["d1_80ca0b97_card_preview"] = {
        "status": "SOURCE_CONSTRAINED_PORTABLE_APPROXIMATION",
        "model": MODEL,
        "materials": [MAT_COLOR, MAT_ATTEN],
        "exact_blend_selector": "0x88 -> state 8",
        "exact_blend_equation": "Source + Destination*(1-SourceAlpha)",
        "exact_alpha_dependency": "t0.x*t1.x is a multiplicative ancestor of final alpha",
        "proxy_alpha": "common-normalized-UV t0.x*t1.x only",
        "warning": "Not native-equivalent: dynamic TFX/CBuffer/global terms and native sample-coordinate transforms are intentionally not fabricated.",
    }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    write_glb(a.out, doc, bin_data)
    check, check_bin = read_glb(a.out)
    if check_bin[:len(original_bin)] != original_bin:
        raise ValueError("source BIN is not an exact output prefix")
    final_counts = {k: len(check.get(k, [])) for k in original_counts}
    for k in ("materials", "meshes", "nodes", "accessors"):
        if final_counts[k] != original_counts[k]:
            raise ValueError(f"unexpected {k} count change {original_counts[k]}->{final_counts[k]}")
    if final_counts["images"] != original_counts["images"] + 2 or final_counts["textures"] != original_counts["textures"] + 2:
        raise ValueError("expected exactly two derived portable textures")

    report = {
        "schema_version": 1,
        "status": "D1_80CA0B97_CARD_SOURCE_CONSTRAINED_PREVIEW_BUILT",
        "input_glb": str(a.input_glb),
        "input_sha256": sha256_file(a.input_glb),
        "output_glb": str(a.out),
        "output_sha256": sha256_file(a.out),
        "output_bytes": a.out.stat().st_size,
        "source_bin_exact_prefix": True,
        "original_counts": original_counts,
        "final_counts": final_counts,
        "model": MODEL,
        "materials": rows,
        "exact_native_contract": {
            "blend_selector_raw": "0x88",
            "blend_state_index": 8,
            "blend_equation": "Source + Destination*(1-SourceAlpha)",
            "color_shader_rgb": "source RGB coefficient * final alpha scalar",
            "attenuation_shader_rgb": "0",
            "alpha": "final alpha scalar with exact multiplicative ancestor t0.x*t1.x",
        },
        "portable_proxy_contract": {
            "alpha": "same-normalized-UV product of exact t0.x and exact t1.x",
            "color_material_rgb": "white straight-alpha color, matching native premultiplied composition when proxy alpha substitutes for final alpha",
            "attenuation_material_rgb": "black straight-alpha color, yielding Destination*(1-proxyAlpha)",
            "status": "SOURCE_CONSTRAINED_PORTABLE_APPROXIMATION",
        },
        "withheld": [
            "native t0/t1 coordinate equivalence",
            "TFX/runtime CBuffer values at any chosen retail instant",
            "higher-level/global inputs",
        ],
        "policy": "No source geometry is removed or hidden. The only derived content is an explicitly marked portable alpha proxy from two exact scalar source textures; native blend/output equations remain authoritative.",
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ("status", "output_bytes", "output_sha256", "source_bin_exact_prefix", "original_counts", "final_counts")}, indent=2))
    for r in rows:
        print("CARD_PROXY", r["material"], r["proxy"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
