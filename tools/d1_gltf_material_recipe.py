#!/usr/bin/env python3
"""Build portable glTF-oriented images + provenance for a solved D1 material.

This is deliberately an approximation layer, not a redefinition of native D1
semantics.  It preserves source hashes/equations and only bakes transformations
that are unambiguous in image space:

* BC3 RGB -> opaque base-color source (BC3 alpha is NOT transparency)
* BC3 alpha S -> native control map + roughness approximation
      roughness_approx = saturate(2.3*S - 1.3)
* primary BC5 RG -> ordinary RGB tangent normal using z reconstruction
* circuitry RGB -> exact luminance/palette bake
      L = saturate(dot(rgb,[.30,.59,.11]))
      palette = base + delta*L

The second/detail normal has a nontrivial shader UV transform and is therefore
not silently baked into the primary normal map by this tool.  Its exact equation
is serialized in the recipe for a later mesh-aware bake/runtime shader.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

DEFAULTS = {
    "main_color": "80AACCDD",
    "normal_primary": "80AACCDF",
    "normal_detail": "80AACC26",
    "environment_cube": "80AACC28",
    "circuitry": "816CE1C5",
}
DEFAULT_PALETTE_BASE = np.array([0.01516041997820139, 0.020845577120780945, 0.037901051342487335], dtype=np.float32)
DEFAULT_PALETTE_DELTA = np.array([0.38483959436416626, 0.5291544198989868, 0.9620989561080933], dtype=np.float32)
LUMA = np.array([0.30, 0.59, 0.11], dtype=np.float32)


def norm_hash(x: str) -> str:
    return x.upper().removeprefix("0X")


def parse_vec3(text: str) -> np.ndarray:
    vals = [float(x.strip()) for x in text.split(",")]
    if len(vals) != 3:
        raise argparse.ArgumentTypeError("expected comma-separated r,g,b")
    return np.asarray(vals, dtype=np.float32)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def find_hash_png(root: Path, tag_hash: str, *, allow_faces: bool = False) -> Path:
    tag_hash = norm_hash(tag_hash)
    hits = sorted(root.glob(f"{tag_hash}_*.png"))
    if not allow_faces:
        hits = [p for p in hits if "_face" not in p.stem]
    if len(hits) != 1:
        raise FileNotFoundError(f"expected exactly one PNG for {tag_hash} in {root}, found {[p.name for p in hits]}")
    return hits[0]


def rgba_float(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGBA"), dtype=np.float32) / 255.0


def save_rgba01(a: np.ndarray, path: Path) -> None:
    a = np.clip(a, 0.0, 1.0)
    Image.fromarray(np.rint(a * 255.0).astype(np.uint8), mode="RGBA").save(path)


def bake_opaque_base(src: np.ndarray) -> np.ndarray:
    out = src.copy()
    out[..., 3] = 1.0
    return out


def bake_control(src: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    s = src[..., 3]
    native = np.stack([s, s, s, np.ones_like(s)], axis=-1)
    rough = np.clip(2.3 * s - 1.3, 0.0, 1.0)
    rough_rgba = np.stack([rough, rough, rough, np.ones_like(rough)], axis=-1)
    # glTF metallicRoughnessTexture reads roughness from G and metalness from B.
    # We intentionally set B=0 because native metalness has NOT been recovered.
    mr = np.stack([np.ones_like(rough), rough, np.zeros_like(rough), np.ones_like(rough)], axis=-1)
    return native, rough_rgba, mr


def bake_primary_normal(src: np.ndarray) -> np.ndarray:
    xy = 2.0 * src[..., :2] - 1.0
    z = np.sqrt(np.maximum(0.0, 1.0 - np.sum(xy * xy, axis=-1)))
    n = np.concatenate([xy, z[..., None]], axis=-1)
    lengths = np.linalg.norm(n, axis=-1, keepdims=True)
    n = np.divide(n, np.maximum(lengths, 1e-8))
    rgb = 0.5 * n + 0.5
    return np.concatenate([rgb, np.ones((*rgb.shape[:2], 1), dtype=np.float32)], axis=-1)


def bake_circuitry(src: np.ndarray, palette_base: np.ndarray, palette_delta: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    l = np.clip(np.sum(src[..., :3] * LUMA[None, None, :], axis=-1), 0.0, 1.0)
    rgb = palette_base[None, None, :] + palette_delta[None, None, :] * l[..., None]
    rgba = np.concatenate([np.clip(rgb, 0.0, 1.0), np.ones((*l.shape, 1), dtype=np.float32)], axis=-1)
    mask = np.stack([l, l, l, np.ones_like(l)], axis=-1)
    return rgba, mask


def image_record(source: Path, output: Path | None = None) -> dict:
    row = {"source_file": source.name, "source_sha256": sha256_file(source)}
    if output is not None:
        row.update(output_file=output.name, output_sha256=sha256_file(output))
    return row


def build_recipe(args) -> dict:
    root = args.texture_dir
    out = args.out
    out.mkdir(parents=True, exist_ok=True)

    hashes = {
        "main_color": norm_hash(args.main_color),
        "normal_primary": norm_hash(args.normal_primary),
        "normal_detail": norm_hash(args.normal_detail),
        "environment_cube": norm_hash(args.environment_cube),
        "circuitry": norm_hash(args.circuitry),
    }

    p_color = find_hash_png(root, hashes["main_color"])
    p_n1 = find_hash_png(root, hashes["normal_primary"])
    p_n2 = find_hash_png(root, hashes["normal_detail"])
    p_circuit = find_hash_png(root, hashes["circuitry"])
    cube_faces = sorted(root.glob(f"{hashes['environment_cube']}_*_face*.png"))
    if len(cube_faces) != 6:
        raise FileNotFoundError(f"expected six cubemap face PNGs for {hashes['environment_cube']}, found {len(cube_faces)}")

    color = rgba_float(p_color)
    n1 = rgba_float(p_n1)
    circuit = rgba_float(p_circuit)

    f_base = out / "main_basecolor_opaque.png"
    f_control = out / "main_surface_control_S.png"
    f_rough = out / "main_roughness_approx.png"
    f_mr = out / "main_metallicRoughness_approx.png"
    f_normal = out / "main_primary_normal_approx.png"
    f_circuit = out / "circuitry_palette_rgb.png"
    f_mask = out / "circuitry_luminance_mask.png"

    save_rgba01(bake_opaque_base(color), f_base)
    control, rough, mr = bake_control(color)
    save_rgba01(control, f_control)
    save_rgba01(rough, f_rough)
    save_rgba01(mr, f_mr)
    save_rgba01(bake_primary_normal(n1), f_normal)
    circuitry, mask = bake_circuitry(circuit, args.palette_base, args.palette_delta)
    save_rgba01(circuitry, f_circuit)
    save_rgba01(mask, f_mask)

    recipe = {
        "format": "d1-gltf-material-recipe-v1",
        "native_truth": {
            "owner": "816CE12B",
            "model": "816CE09A",
            "main_material": "809C475F",
            "main_pixel_shader": "80AAE14B",
            "main_b0": "80AAE14C",
            "circuitry_material": "816CE240",
            "circuitry_pixel_shader": "816CE0A8",
            "circuitry_b0": "816CE185",
            "texture_hashes": hashes,
            "main_texture_indices": {
                "0": hashes["main_color"],
                "1": hashes["normal_primary"],
                "2": hashes["normal_detail"],
                "3": hashes["environment_cube"],
                "4": hashes["main_color"],
            },
            "main_sampler_2d": {
                "tag_hash": "80AAE177",
                "gnm_words": ["00000000", "00F00000", "0A503F80", "00000000"],
                "wrap": "Wrap",
                "min_mag": "Bilinear",
                "mip": "Linear",
            },
            "main_sampler_cube": {
                "tag_hash": "80AAE176",
                "gnm_words": ["00000092", "00F00000", "0A503F80", "00000000"],
                "wrap": "ClampLastTexel",
                "min_mag": "Bilinear",
                "mip": "Linear",
            },
            "circuitry_sampler": {
                "tag_hash": "816CE0AA",
                "gnm_words": ["000001B6", "00F00000", "0A503F80", "80000000"],
                "wrap": "ClampBorder",
                "border": "OpaqueWhite",
                "min_mag": "Bilinear",
                "mip": "Linear",
            },
            "main_equations": {
                "detail_uv": ["20*(1-v)", "0.4*u"],
                "normal_xy": "1.25*(2*t1.xy-1) + (2*t2.xy-1)",
                "normal_z": "sqrt(max(0,1-dot(normal_xy,normal_xy)))",
                "surface_rgb": "t0.rgb",
                "surface_control_S": "t4.a (same BC3 image as t0; NOT transparency)",
                "reflection_q": "saturate(2.3*S-1.3)",
                "material_cube_lod": "3+3*reflection_q",
                "cube_lod": "max(hardware_cube_lod, material_cube_lod)",
                "reflection_strength": "2.5*S*cube.a",
                "reflection_rgb": "cube.rgb*[2,0.84,0]*reflection_strength",
                "mrt0_rgb": "B+(0.75*B+0.75)*reflection_rgb",
                "mrt0_a": "attr0.w",
                "mrt1_xyz": "saturate(0.5+(0.375+0.125*S)*N)",
            },
            "circuitry_equations": {
                "height_centered": "T0-0.5",
                "parallax": "view-dependent UV displacement; global scale producer unresolved",
                "luminance": "saturate(dot(T1.rgb,[0.30,0.59,0.11]))",
                "palette": "vec4.rgb+vec5.rgb*L",
                "local_intensity": float(args.local_intensity),
                "global_intensity_multipliers": "unresolved",
                "native_output_alpha": 0,
            },
        },
        "portable_outputs": {
            "base_color": image_record(p_color, f_base),
            "native_surface_control": image_record(p_color, f_control),
            "roughness_approx": image_record(p_color, f_rough),
            "metallic_roughness_approx": image_record(p_color, f_mr),
            "primary_normal_approx": image_record(p_n1, f_normal),
            "normal_detail_source": image_record(p_n2),
            "environment_cube_faces": [image_record(p) for p in cube_faces],
            "circuitry_palette": image_record(p_circuit, f_circuit),
            "circuitry_luminance": image_record(p_circuit, f_mask),
        },
        "portable_policy": {
            "surface_alpha_mode": "OPAQUE",
            "base_color_uses_source_alpha": False,
            "roughness_approx_formula": "saturate(2.3*S-1.3)",
            "metallic_factor_approx": 0.0,
            "metallic_factor_reason": "native metalness not recovered; do not invent it",
            "normal_approximation": "primary t1 only; exact t2 detail UV transform preserved but not silently baked",
            "environment_cube": "preserve in extras; core glTF has no per-material native cube+LOD equivalent",
            "circuitry_emissive_strength_suggestion": float(args.local_intensity),
            "circuitry_emissive_strength_scope": "material-local factor only; native global multipliers unresolved",
            "circuitry_blend_mode": "unresolved; do not claim native additive until render state is proven",
            "recommended_extensions": ["KHR_materials_emissive_strength"],
        },
        "palette": {
            "base": [float(x) for x in args.palette_base],
            "delta": [float(x) for x in args.palette_delta],
            "bright_endpoint": [float(x) for x in (args.palette_base + args.palette_delta)],
        },
    }
    recipe_path = out / "material_recipe.json"
    recipe_path.write_text(json.dumps(recipe, indent=2) + "\n")
    return recipe


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--texture-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--main-color", default=DEFAULTS["main_color"])
    ap.add_argument("--normal-primary", default=DEFAULTS["normal_primary"])
    ap.add_argument("--normal-detail", default=DEFAULTS["normal_detail"])
    ap.add_argument("--environment-cube", default=DEFAULTS["environment_cube"])
    ap.add_argument("--circuitry", default=DEFAULTS["circuitry"])
    ap.add_argument("--palette-base", type=parse_vec3, default=DEFAULT_PALETTE_BASE.copy())
    ap.add_argument("--palette-delta", type=parse_vec3, default=DEFAULT_PALETTE_DELTA.copy())
    ap.add_argument("--local-intensity", type=float, default=5.0)
    args = ap.parse_args()
    recipe = build_recipe(args)
    print(json.dumps({"out": str(args.out), "format": recipe["format"], "bright_endpoint": recipe["palette"]["bright_endpoint"]}, indent=2))


if __name__ == "__main__":
    main()
