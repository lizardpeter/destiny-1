#!/usr/bin/env python3
"""Export source-selected D1 terrain geometry to a portable glTF scene.

This consumes two already-closed inputs:
  * ``d1_world_terrain_census.py``: exact STerrain payloads, MainGeom0 parts,
    materials, mesh groups and dyemap references.
  * ``d1_world_terrain_buffer_layout_probe.py``: exact Vertices1/Vertices2/Indices1
    reference/backing identity, 0x08/0x0C stream layout and selected strip ranges.

The vertex decode and transforms reproduce Charm's D1 terrain consumer:
  Vertices1 0x08: four raw int16 position components (cast to float)
  Vertices2 0x0C: four int16 normal components, XYZ / 32767, then half2 UV
  TransformPositions: STerrain.Unk30 + packed position, 16-bit Z/W height combine,
                      1/64 XY, 1/8192 Z scale, normal-length correction
  TransformTexcoords: mesh-group Unk20 scale/offset
  TransformVertexColors: GroupIndex % 4 -> R/G/B/white dyemap selector

The generated dyemap selector is NOT written to glTF COLOR_0 because portable PBR
would multiply base color by it. It is losslessly retained in the report and node
metadata along with the exact group/effective-dyemap identity.

Terrain is already pre-transformed by the source consumer, so the outer
SMapDataEntry transform is deliberately ignored. A pure D1 Z-up -> glTF Y-up node
basis is applied to every emitted part.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import trimesh

import d1_tower_map_schema_validate_v5 as v5
import d1_tower_static_chunk_export as static
from d1_entity_model_export import decode_indices, index_is32, primitive_faces
from d1_world_articulated_scene_v2 import A

NULLS = {"00000000", "FFFFFFFF"}


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def snorm16_xyz(raw: np.ndarray) -> np.ndarray:
    x = raw[:, :3].astype(np.float32) / np.float32(32767.0)
    return np.maximum(x, np.float32(-1.0))


def decode_streams(v0: bytes, v1: bytes) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if len(v0) % 8 or len(v1) % 12:
        raise ValueError(f"terrain stream byte divisibility {len(v0)}/8 {len(v1)}/12")
    n0 = len(v0) // 8
    n1 = len(v1) // 12
    if n0 != n1:
        raise ValueError(f"terrain paired vertex count mismatch {n0}!={n1}")
    p = np.frombuffer(v0, dtype="<i2").reshape((-1, 4)).astype(np.float32)
    nraw = np.frombuffer(v1, dtype="<i2").reshape((-1, 6))[:, :4]
    n = snorm16_xyz(nraw)
    # Terrain signature reader consumes the final four bytes as two IEEE-754 halfs.
    uv = np.frombuffer(v1, dtype="<f2").reshape((-1, 6))[:, 4:6].astype(np.float32)
    return p, n, uv


def transform_positions(raw_pos: np.ndarray, normals: np.ndarray, unk30: list[float]) -> np.ndarray:
    """Vectorized source-equivalent form of Terrain.TransformPositions."""
    u = np.asarray(unk30, dtype=np.float32)
    if u.shape != (4,) or not np.isfinite(u).all():
        raise ValueError(f"bad STerrain Unk30 {unk30!r}")
    r = raw_pos.astype(np.float32, copy=True)
    r += u[None, :]
    packed_height = (r[:, 3] * np.float32(65536.0) + r[:, 2]).astype(np.float32)
    x = (r[:, 0] * np.float32(0.015625)).astype(np.float32)
    y = (r[:, 1] * np.float32(0.015625)).astype(np.float32)
    height = (packed_height * np.float32(0.000122070313)).astype(np.float32)

    # Charm's shader transcription builds two cross-product helpers and ends with
    # rsqrt(dot(r2,r2)); algebraically this is reciprocal length of normal XYZ.
    # Keep float32 arithmetic and fail closed on zero/non-finite normals.
    len2 = np.sum(normals.astype(np.float32) * normals.astype(np.float32), axis=1, dtype=np.float32)
    if np.any(~np.isfinite(len2)) or np.any(len2 <= 0):
        bad = np.where((~np.isfinite(len2)) | (len2 <= 0))[0][:8].tolist()
        raise ValueError(f"terrain zero/nonfinite normal length at {bad}")
    inv_len = (np.float32(1.0) / np.sqrt(len2, dtype=np.float32)).astype(np.float32)
    z = (inv_len * height).astype(np.float32)
    out = np.column_stack((x, y, z)).astype(np.float32)
    if not np.isfinite(out).all():
        raise ValueError("terrain transformed positions contain non-finite values")
    return out


def transform_uv(uv: np.ndarray, group_vec20: list[float]) -> np.ndarray:
    g = np.asarray(group_vec20, dtype=np.float32)
    if g.shape != (4,) or not np.isfinite(g).all():
        raise ValueError(f"bad mesh-group Unk20 {group_vec20!r}")
    out = np.empty_like(uv, dtype=np.float32)
    out[:, 0] = uv[:, 0] * g[0] + g[2]
    out[:, 1] = uv[:, 1] * (-g[1]) + np.float32(1.0) - g[3]
    if not np.isfinite(out).all():
        raise ValueError("terrain transformed UV contains non-finite values")
    return out


def dye_control(group_index: int) -> list[float]:
    return (
        [1.0, 0.0, 0.0, 1.0],
        [0.0, 1.0, 0.0, 1.0],
        [0.0, 0.0, 1.0, 1.0],
        [1.0, 1.0, 1.0, 1.0],
    )[group_index % 4]


def effective_dyemaps(groups: list[dict]) -> list[str | None]:
    """Replay Charm's ordered last-valid / first-valid dyemap fallback exactly."""
    raw = []
    for g in groups:
        h = norm((g.get("dyemap") or {}).get("hash") or "FFFFFFFF")
        raw.append(None if h in NULLS else h)
    first = next((x for x in raw if x is not None), None)
    out = []
    last = None
    for h in raw:
        if h is not None:
            last = h
            out.append(h)
        elif last is not None:
            out.append(last)
        else:
            out.append(first)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", type=Path, action="append", required=True)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--terrain-census", type=Path, required=True)
    ap.add_argument("--buffer-layout", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    a = ap.parse_args()

    census = json.loads(a.terrain_census.read_text(encoding="utf-8"))
    layout = json.loads(a.buffer_layout.read_text(encoding="utf-8"))
    if census.get("status") != "D1_WORLD_TERRAIN_CENSUS_COMPLETE" or census.get("violations") or census.get("missing_dependency_package_ids"):
        raise SystemExit("terrain census is not authoritative")
    if layout.get("status") != "D1_WORLD_TERRAIN_BUFFER_LAYOUT_COMPLETE" or layout.get("violations"):
        raise SystemExit("terrain buffer layout is not authoritative")
    if int(census.get("unique_terrain_count", -1)) != 49 or int(layout.get("terrain_count", -1)) != 49:
        raise SystemExit("terrain count mismatch")
    if int(census.get("selected_main_geom0_part_count", -1)) != int(layout.get("selected_main_geom0_part_count", -2)):
        raise SystemExit("selected terrain part count mismatch")
    if layout.get("stride_pair_histogram") != {"0x8/0xc": 49} or layout.get("index_format_histogram") != {"u16": 49}:
        raise SystemExit("unexpected terrain stream/index family")

    c = v5.v3.base.Corpus([p.resolve() for p in a.snapshot], a.runtime.resolve())
    census_by = {norm(t["hash"]): t for t in census.get("terrains", [])}
    layout_by = {norm(t["terrain"]): t for t in layout.get("terrains", [])}
    if set(census_by) != set(layout_by):
        raise SystemExit("terrain census/layout hash sets differ")

    scene = trimesh.Scene()
    material_cache: dict[str, trimesh.visual.material.PBRMaterial] = {}
    rows = []
    triangle_total = 0
    unique_vertex_total = 0
    selected_total = 0
    used_dyemaps = set()
    source_dyemaps = set()
    null_source_dyemap_groups = 0

    for th in sorted(census_by):
        t = census_by[th]
        l = layout_by[th]
        deps = t.get("top_level_dependencies") or {}
        v0h = norm((deps.get("vertices1") or {}).get("hash"))
        v1h = norm((deps.get("vertices2") or {}).get("hash"))
        ibh = norm((deps.get("indices1") or {}).get("hash"))
        v0r = static.read_reference_file(c, v0h)
        v1r = static.read_reference_file(c, v1h)
        ibr = static.read_reference_file(c, ibh)
        p_raw, normals, uv_raw = decode_streams(v0r["backing"], v1r["backing"])
        if len(p_raw) != int(l["vertex_count"]):
            raise SystemExit(f"{th}: vertex count differs from buffer-layout proof")
        if bool(index_is32(ibr["header"])):
            raise SystemExit(f"{th}: unexpected u32 terrain index buffer")
        inds = decode_indices(ibr["backing"], False)
        pos = transform_positions(p_raw, normals, t["vector30"])
        groups = t.get("mesh_groups", [])
        eff_dyes = effective_dyemaps(groups)
        if len(eff_dyes) != len(groups):
            raise SystemExit(f"{th}: dyemap replay count mismatch")
        for gi, g in enumerate(groups):
            raw_dye = norm((g.get("dyemap") or {}).get("hash") or "FFFFFFFF")
            if raw_dye in NULLS:
                null_source_dyemap_groups += 1
            else:
                source_dyemaps.add(raw_dye)

        proved_parts = {int(p["part_index"]): p for p in l.get("selected_parts", [])}
        selected = [p for p in t.get("static_parts", []) if p.get("selected_main_geom0")]
        if len(selected) != int(l["selected_part_count"]) or set(int(p["index"]) for p in selected) != set(proved_parts):
            raise SystemExit(f"{th}: selected part set differs from buffer-layout proof")

        for p in selected:
            pi = int(p["index"])
            proof = proved_parts[pi]
            gi = int(p["group_index"])
            if gi < 0 or gi >= len(groups):
                raise SystemExit(f"{th}: part {pi} group {gi} out of range")
            off = int(p["index_offset"])
            cnt = int(p["index_count"])
            faces_global = primitive_faces(inds[off:off + cnt], 5, False)
            if len(faces_global) != int(proof["triangle_count"]):
                raise SystemExit(f"{th}: part {pi} triangle count differs from proof")
            used, inv = np.unique(faces_global.reshape(-1), return_inverse=True)
            faces = inv.reshape((-1, 3))
            vv = pos[used]
            nn = normals[used]
            uu = transform_uv(uv_raw[used], groups[gi]["vector20"])
            mh = norm((p.get("material") or {}).get("hash"))
            if mh in NULLS:
                raise SystemExit(f"{th}: selected part {pi} has null material")
            mat = material_cache.get(mh)
            if mat is None:
                mat = trimesh.visual.material.PBRMaterial(
                    name=f"D1_{mh}", metallicFactor=0.0, roughnessFactor=1.0
                )
                material_cache[mh] = mat
            visual = trimesh.visual.TextureVisuals(uv=uu, material=mat)
            mesh = trimesh.Trimesh(
                vertices=vv,
                faces=faces,
                vertex_normals=nn,
                visual=visual,
                process=False,
                validate=False,
            )
            dy = eff_dyes[gi]
            if dy is not None:
                used_dyemaps.add(dy)
            ctrl = dye_control(gi)
            gname = f"D1_TERRAIN_{th}_p{pi:04d}_g{gi:03d}_m{mh}"
            nname = gname
            mesh.metadata = {
                "d1Terrain": th,
                "d1StaticPartIndex": pi,
                "d1GroupIndex": gi,
                "d1Material": mh,
                "d1SourceDyemap": norm((groups[gi].get("dyemap") or {}).get("hash") or "FFFFFFFF"),
                "d1EffectiveDyemap": dy,
                "d1DyemapControlRGBA": ctrl,
                "d1DetailLevel": int(p["detail_level"]),
                "d1IndexOffset": off,
                "d1IndexCount": cnt,
            }
            scene.geometry[gname] = mesh
            scene.graph.update(
                frame_to=nname,
                matrix=A,
                geometry=gname,
                metadata=mesh.metadata,
            )
            triangle_total += len(faces)
            unique_vertex_total += len(used)
            selected_total += 1
            rows.append({
                "terrain": th,
                "part_index": pi,
                "group_index": gi,
                "detail_level": int(p["detail_level"]),
                "material": mh,
                "source_dyemap": norm((groups[gi].get("dyemap") or {}).get("hash") or "FFFFFFFF"),
                "effective_dyemap": dy,
                "dyemap_control_rgba": ctrl,
                "index_offset": off,
                "index_count": cnt,
                "triangle_count": int(len(faces)),
                "unique_vertex_count": int(len(used)),
                "min_source_vertex": int(used.min()),
                "max_source_vertex": int(used.max()),
                "node": nname,
                "geometry": gname,
            })

    expected_parts = int(census["selected_main_geom0_part_count"])
    expected_triangles = int(layout["triangle_count"])
    if selected_total != expected_parts:
        raise SystemExit(f"selected part coverage {selected_total}!={expected_parts}")
    if triangle_total != expected_triangles:
        raise SystemExit(f"triangle coverage {triangle_total}!={expected_triangles}")
    if set(material_cache) != {norm(x) for x in census.get("selected_materials", [])}:
        raise SystemExit("selected material coverage differs from terrain census")

    a.out.parent.mkdir(parents=True, exist_ok=True)
    scene.export(a.out)
    report = {
        "schema_version": 1,
        "status": "D1_WORLD_TERRAIN_SCENE_COMPLETE",
        "terrain_count": len(census_by),
        "selected_main_geom0_part_count": selected_total,
        "triangle_count": int(triangle_total),
        "summed_part_unique_vertex_count": int(unique_vertex_total),
        "material_count": len(material_cache),
        "materials": sorted(material_cache),
        "source_nonnull_dyemap_count": len(source_dyemaps),
        "source_nonnull_dyemaps": sorted(source_dyemaps),
        "null_source_dyemap_group_count": null_source_dyemap_groups,
        "effective_selected_dyemap_count": len(used_dyemaps),
        "effective_selected_dyemaps": sorted(used_dyemaps),
        "geometry_count": len(scene.geometry),
        "scene_node_count": selected_total,
        "bounds": scene.bounds.tolist() if scene.bounds is not None else None,
        "glb": str(a.out),
        "glb_bytes": a.out.stat().st_size,
        "glb_sha256": sha256(a.out),
        "coordinate_adapter": "Each pre-transformed D1 terrain part receives only D1_ZUP_TO_GLTF_YUP; outer SMapDataEntry transform is intentionally not applied.",
        "vertex_decode": "Vertices1 0x08 = raw int16x4 position; Vertices2 0x0C = SNORM16 XYZ normal with padded int16 W + half2 UV, per pinned Charm terrain reader.",
        "dyemap_policy": "Exact ordered Charm fallback replay: non-null group dyemap updates last-valid; null uses last-valid, or the first later valid dyemap when no previous valid exists. GroupIndex%4 selector is retained as D1 metadata, not glTF COLOR_0.",
        "parts": rows,
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in (
        "status", "terrain_count", "selected_main_geom0_part_count", "triangle_count",
        "summed_part_unique_vertex_count", "material_count", "source_nonnull_dyemap_count",
        "null_source_dyemap_group_count", "effective_selected_dyemap_count", "geometry_count",
        "scene_node_count", "bounds", "glb_bytes", "glb_sha256"
    )}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
