#!/usr/bin/env python3
"""Retail audit for Tower VS 80CA0DDA tangent handedness and glTF UV adapter.

This closes the remaining vertex-to-Blender boundary for pixel shader 809DCD66
without promoting any portable tangent semantics by assumption.

For the exact target family the native VS consumes an 8+20 static layout and
constructs its bitangent as::

    B = cross(N, T) * source_tangent_w

The current world GLB adapter also converts the native texture coordinate to its
PNG/glTF convention as::

    portable_u = native_u
    portable_v = 1 - native_v

This script measures those facts on the retail Tower cell population, checks
triangle handedness consistency, checks every placement transform for the
conditions needed by a Blender world-space replay, and proves the portable
parallax-coordinate conversion algebraically against exact shader outputs.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import d1_tower_map_schema_validate_v5 as v5
import d1_tower_static_chunk_export as base
from d1_world_static_common import apply_d1_instance_uv
from d1_tower_80ca0dda_vs_replay import (
    decode_static_inputs,
    record_from_sidecar,
    replay_pixel_varyings,
)
from d1_tower_809dcd66_ps_replay import parallax_uv

TARGET_VS = "80CA0DDA"
TARGET_PS = "809DCD66"


def _fstats(a: np.ndarray) -> dict:
    x = np.asarray(a, dtype=np.float64).reshape(-1)
    return {
        "min": float(x.min()) if len(x) else None,
        "max": float(x.max()) if len(x) else None,
        "mean": float(x.mean()) if len(x) else None,
    }


def _orthogonality_metrics(m3: np.ndarray) -> tuple[np.ndarray, float, float]:
    # Column lengths are the local basis scales. For a uniform-scale rotation
    # they are equal and normalized columns are mutually orthogonal.
    cols = np.asarray(m3, dtype=np.float64)
    lens = np.linalg.norm(cols, axis=0)
    if np.any(lens == 0):
        return lens, float("inf"), float("inf")
    q = cols / lens[None, :]
    gram = q.T @ q
    off = gram - np.eye(3)
    max_orth = float(np.max(np.abs(off)))
    scale_spread = float(lens.max() - lens.min())
    return lens, max_orth, scale_spread


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", type=Path, action="append", required=True)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--world", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    c = v5.v3.base.Corpus([p.resolve() for p in a.snapshot], a.runtime.resolve())
    world = json.loads(a.world.read_text())
    manifest = json.loads(a.manifest.read_text())
    target_materials = {
        str(h).upper()
        for h, r in manifest["materials"].items()
        if str(r.get("vertex_shader") or "").upper() == TARGET_VS
        and str(r.get("pixel_shader") or "").upper() == TARGET_PS
    }
    if len(target_materials) != 24:
        raise SystemExit(f"target material fixture changed: {len(target_materials)} != 24")

    geoms = [
        g for g in world["geometry"]
        if str(g.get("source_key", {}).get("material_hash") or "").upper() in target_materials
    ]
    nodes = [n for n in world["nodes"] if str(n.get("material_hash") or "").upper() in target_materials]
    if len(geoms) != 12 or len(nodes) != 64:
        raise SystemExit(f"retail cell fixture changed: geoms={len(geoms)} nodes={len(nodes)}")

    by_geom: dict[str, list[dict]] = defaultdict(list)
    for n in nodes:
        by_geom[n["geometry"]].append(n)

    ref_cache = {}
    def ref(h: str):
        h = str(h).upper()
        if h not in ref_cache:
            ref_cache[h] = base.read_reference_file(c, h)
        return ref_cache[h]

    raw_w_counter: Counter[int] = Counter()
    used_w_counter: Counter[float] = Counter()
    tri_mixed = []
    geometry_rows = []
    placement_rows = []
    all_tangent_lengths = []
    all_normal_lengths = []
    portable_uv_max_error = 0.0
    portable_parallax_max_error = 0.0

    # Fixed camera/displacement is only an algebraic coordinate-conversion
    # canary. It is not a claim about the retail runtime camera.
    synthetic_camera = np.array([17.0, -9.0, 31.0], dtype=np.float32)
    synthetic_disp = np.float32(0.025)

    for g in geoms:
        k = g["source_key"]
        v0 = ref(k["vertices0"])
        v1 = ref(k["vertices1"])
        ib = ref(k["indices"])
        s0 = base.hdr_stride(v0["header"])
        s1 = base.hdr_stride(v1["header"])
        if (s0, s1) != (8, 20):
            raise AssertionError((g["geometry"], s0, s1))

        inputs = decode_static_inputs(v0["backing"], v1["backing"])
        inds = base.decode_indices(ib["backing"], base.index_is32(ib["header"]))
        off = int(k["index_offset"])
        cnt = int(k["index_count"])
        prim = int(k["primitive_type"])
        faces = base.primitive_faces(inds[off:off + cnt], prim, base.index_is32(ib["header"]))
        if len(faces) == 0:
            raise AssertionError(f"{g['geometry']}: no faces")
        used = np.unique(faces.reshape(-1))
        if sorted(g["source_vertex_indices"]) != used.tolist():
            raise AssertionError(f"{g['geometry']}: source vertex identity changed")

        rw = inputs.raw_tangent[used, 3]
        nw = inputs.v16_v19_tangent[used, 3]
        raw_w_counter.update(int(x) for x in rw.tolist())
        used_w_counter.update(float(x) for x in nw.tolist())

        # glTF defines tangent space only if all three triangle vertices agree on
        # tangent.w. Audit the actual source triangles, not merely unique verts.
        g_mixed = 0
        for fi, face in enumerate(faces):
            vals = inputs.raw_tangent[np.asarray(face, dtype=np.int64), 3]
            if not np.all(vals == vals[0]):
                g_mixed += 1
                if len(tri_mixed) < 32:
                    tri_mixed.append({
                        "geometry": g["geometry"], "face_index": fi,
                        "source_indices": [int(x) for x in face],
                        "raw_tangent_w": [int(x) for x in vals],
                    })

        placements = by_geom[g["geometry"]]
        if len(placements) != int(g["placement_count"]):
            raise AssertionError(f"{g['geometry']}: placement count mismatch")

        for n in placements:
            rec = record_from_sidecar(n["source_affine"], n["uv_transform"], n["tail_0x3c"])
            out = replay_pixel_varyings(inputs, rec)
            sel_n = out.normal[used]
            sel_t = out.tangent[used]
            sel_b = out.bitangent[used]
            sel_w = inputs.v16_v19_tangent[used, 3]

            # This is the native shader identity we need Blender to retain.
            expect_b = np.cross(sel_n, sel_t).astype(np.float32) * sel_w[:, None]
            np.testing.assert_allclose(sel_b, expect_b, rtol=0, atol=2e-6)

            nl = np.linalg.norm(sel_n, axis=1)
            tl = np.linalg.norm(sel_t, axis=1)
            all_normal_lengths.extend(float(x) for x in nl)
            all_tangent_lengths.extend(float(x) for x in tl)

            # Exact relation between native VS UV and current portable world GLB
            # TEXCOORD_0 convention.
            ruv = np.asarray(n["uv_transform"], dtype=np.float32)
            src_uv = inputs.v8_v9_uv[used]
            portable = apply_d1_instance_uv(src_uv, float(ruv[0]), float(ruv[1]), float(ruv[2]))
            native = out.uv[used]
            expected_portable = np.column_stack((native[:, 0], np.float32(1.0) - native[:, 1])).astype(np.float32)
            uv_err = float(np.max(np.abs(portable - expected_portable)))
            portable_uv_max_error = max(portable_uv_max_error, uv_err)
            np.testing.assert_allclose(portable, expected_portable, rtol=0, atol=2e-6)

            # Native displaced UV -> portable PNG/glTF coordinate transform:
            #   p2.x = n2.x
            #   p2.y = 1 - n2.y
            # Thus when starting from portable base UV, native X displacement is
            # retained while native Y displacement changes sign.
            p = parallax_uv(
                native, out.world_position[used], sel_n, sel_t, sel_b,
                synthetic_camera, float(synthetic_disp),
            )
            native2 = p.displaced_uv
            portable2_from_native = np.column_stack(
                (native2[:, 0], np.float32(1.0) - native2[:, 1])
            ).astype(np.float32)
            delta_native = native2 - native
            portable2_direct = portable.copy()
            portable2_direct[:, 0] += delta_native[:, 0]
            portable2_direct[:, 1] -= delta_native[:, 1]
            # Ignore the synthetic grazing-angle rows where the native shader's
            # unguarded reciprocal intentionally yields non-finite coordinates.
            finite = np.isfinite(portable2_from_native).all(axis=1)
            if np.any(finite):
                pe = float(np.max(np.abs(portable2_from_native[finite] - portable2_direct[finite])))
                portable_parallax_max_error = max(portable_parallax_max_error, pe)
                np.testing.assert_allclose(
                    portable2_from_native[finite], portable2_direct[finite], rtol=0, atol=3e-6
                )

            m3 = rec[:3, :3].astype(np.float64)
            det = float(np.linalg.det(m3))
            scales, orth_err, spread = _orthogonality_metrics(m3)
            placement_rows.append({
                "node": n["node"], "geometry": g["geometry"],
                "determinant": det, "determinant_sign": 1 if det > 0 else (-1 if det < 0 else 0),
                "column_scales": [float(x) for x in scales],
                "max_normalized_basis_orthogonality_error": orth_err,
                "uniform_scale_spread": spread,
                "normal_length_min": float(nl.min()), "normal_length_max": float(nl.max()),
                "tangent_length_min": float(tl.min()), "tangent_length_max": float(tl.max()),
            })

        geometry_rows.append({
            "geometry": g["geometry"],
            "material": str(k["material_hash"]).upper(),
            "used_vertex_count": int(len(used)),
            "triangle_count": int(len(faces)),
            "placement_count": int(len(placements)),
            "raw_tangent_w_counts": dict(Counter(int(x) for x in rw.tolist())),
            "mixed_handedness_triangle_count": int(g_mixed),
        })

    raw_keys = sorted(raw_w_counter)
    all_sign_only = set(raw_keys).issubset({-32767, 32767}) and bool(raw_keys)
    dets = np.array([x["determinant"] for x in placement_rows], dtype=np.float64)
    orth = np.array([x["max_normalized_basis_orthogonality_error"] for x in placement_rows], dtype=np.float64)
    spread = np.array([x["uniform_scale_spread"] for x in placement_rows], dtype=np.float64)
    tlen = np.asarray(all_tangent_lengths, dtype=np.float64)
    nlen = np.asarray(all_normal_lengths, dtype=np.float64)

    report = {
        "schema_version": 1,
        "status": "D1_TOWER_809DCD66_TANGENT_AND_PORTABLE_UV_AUDIT",
        "cell": world.get("static_map_data", "80C98254"),
        "target_vs": TARGET_VS,
        "target_ps": TARGET_PS,
        "target_material_count_global": len(target_materials),
        "geometry_count": len(geoms),
        "placement_count": len(nodes),
        "raw_tangent_w_counts": {str(k): int(v) for k, v in sorted(raw_w_counter.items())},
        "normalized_tangent_w_counts": {str(k): int(v) for k, v in sorted(used_w_counter.items())},
        "all_referenced_tangent_w_are_exact_signs": all_sign_only,
        "mixed_handedness_triangle_count": len(tri_mixed),
        "mixed_handedness_triangle_examples": tri_mixed,
        "normal_length_stats_after_native_vs": _fstats(nlen),
        "tangent_length_stats_after_native_vs": _fstats(tlen),
        "placement_determinant_stats": _fstats(dets),
        "positive_determinant_placements": int(np.sum(dets > 0)),
        "negative_determinant_placements": int(np.sum(dets < 0)),
        "zero_determinant_placements": int(np.sum(dets == 0)),
        "max_normalized_basis_orthogonality_error": float(orth.max()),
        "max_uniform_scale_spread": float(spread.max()),
        "portable_uv_relation": "portable=(native_u,1-native_v)",
        "portable_uv_max_abs_error": portable_uv_max_error,
        "portable_parallax_relation": "portable_displaced=(portable_u+native_du, portable_v-native_dv)",
        "portable_parallax_max_abs_error": portable_parallax_max_error,
        "geometry": geometry_rows,
        "placements": placement_rows,
        "promotion_gates": {
            "tangent_w_is_glTF_sign_compatible": bool(all_sign_only),
            "every_triangle_has_uniform_tangent_w": len(tri_mixed) == 0,
            "all_instance_transforms_orientation_preserving": bool(np.all(dets > 0)),
            "instance_bases_are_orthogonal_within_1e_5": bool(np.all(orth <= 1e-5)),
            "instance_scales_are_uniform_within_1e_5": bool(np.all(spread <= 1e-5)),
            "native_normal_is_unit_within_1e_5": bool(np.all(np.abs(nlen - 1.0) <= 1e-5)),
            "native_tangent_is_unit_within_1e_5": bool(np.all(np.abs(tlen - 1.0) <= 1e-5)),
            "portable_uv_v_flip_exact_within_2e_6": portable_uv_max_error <= 2e-6,
            "portable_parallax_y_sign_flip_exact_within_3e_6": portable_parallax_max_error <= 3e-6,
        },
        "policy": (
            "No standard glTF TANGENT promotion is performed by this audit. It proves the retail source sign, "
            "triangle consistency, native cross(N,T)*W identity, placement transform conditions, and exact "
            "native-to-portable UV/parallax relation needed by a later Blender adapter."
        ),
    }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "status": report["status"],
        "geometry_count": report["geometry_count"],
        "placement_count": report["placement_count"],
        "raw_tangent_w_counts": report["raw_tangent_w_counts"],
        "mixed_handedness_triangle_count": report["mixed_handedness_triangle_count"],
        "placement_determinant_stats": report["placement_determinant_stats"],
        "max_normalized_basis_orthogonality_error": report["max_normalized_basis_orthogonality_error"],
        "max_uniform_scale_spread": report["max_uniform_scale_spread"],
        "portable_uv_max_abs_error": report["portable_uv_max_abs_error"],
        "portable_parallax_max_abs_error": report["portable_parallax_max_abs_error"],
        "promotion_gates": report["promotion_gates"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
