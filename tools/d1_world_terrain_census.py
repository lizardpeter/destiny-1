#!/usr/bin/env python3
"""Loss-preserving D1 map terrain census and dependency frontier.

Consumes a map-layer census extended with the source-proven D1
``SMapTerrainResource`` mapping and decodes only the exact D1 layouts from:

  MontagueM/Charm@e5c4c7b0affcc00a988441e8f913dad7d0aa9bb9
  Tiger/Schema/Static/Terrain.cs

Canonical D1 schema:
  80801C37 SMapTerrainResource (0x20)
    +0x18 STerrain TagHash (80801B2E)
    +0x1C SOcclusionBounds TagHash

  80801B2E STerrain (0xB0)
    +0x10/+0x20/+0x30 Vector4
    +0x58 DynamicArray<SMeshGroup> stride 0x60
    +0x68 Vertices1
    +0x6C Vertices2
    +0x70 Indices1
    +0x74 Material
    +0x78 Material
    +0x80 DynamicArray<SStaticPart> stride 0x0C
    +0x90 Vertices3
    +0x94 Vertices4
    +0x98 Indices2
    +0xA4 Material
    +0xA8 Texture

  SMeshGroup (80801A7F, 0x60)
    +0x00/+0x10/+0x20 Vector4
    +0x30..+0x4C eight u32 values
    +0x58 Dyemap Texture TagHash

  SStaticPart (80801A48, 0x0C)
    +0x00 Material TagHash
    +0x04 u32 IndexOffset
    +0x08 u16 IndexCount
    +0x0A u8 GroupIndex
    +0x0B u8 DetailLevel

Charm exports terrain parts only when ``ELodCategory.MainGeom0 == 0``. This census
preserves every serialized part and marks that source selection without attempting
geometry decode. All dependency FileHashes come only from typed schema fields; raw
byte scanning is not used.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import d1_tower_map_schema_validate_v5 as v5
import d1_world_map_data_layer_census as layer
from d1_filehash import package_hex

TERRAIN_RESOURCE = "80801C37"
TERRAIN = "80801B2E"
NULLS = {"00000000", "FFFFFFFF"}
PINNED_SOURCE = (
    "MontagueM/Charm@e5c4c7b0affcc00a988441e8f913dad7d0aa9bb9 "
    "Tiger/Schema/Static/Terrain.cs"
)


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def hx(v: int) -> str:
    return f"{v:08X}"


def u8(b: bytes, o: int) -> int:
    return b[o]


def u16(b: bytes, o: int) -> int:
    return struct.unpack_from("<H", b, o)[0]


def i16(b: bytes, o: int) -> int:
    return struct.unpack_from("<h", b, o)[0]


def u32(b: bytes, o: int) -> int:
    return struct.unpack_from("<I", b, o)[0]


def u64(b: bytes, o: int) -> int:
    return struct.unpack_from("<Q", b, o)[0]


def vec4(b: bytes, o: int) -> list[float]:
    return [float(x) for x in struct.unpack_from("<4f", b, o)]


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def pkgid(h: str) -> str | None:
    h = norm(h)
    if h in NULLS:
        return None
    try:
        return package_hex(h).lower()
    except Exception:
        return None


def meta(c, h: str, expected: str | None = None) -> dict:
    h = norm(h)
    m = c.entry_meta(h)
    return {
        "hash": h,
        "package_id": pkgid(h),
        "exists": m is not None,
        "expected_class": expected,
        "class_matches": bool(m and (expected is None or norm(m.get("reference", "")) == expected)),
        "meta": m,
    }


def add_dep(c, h: str, role: str, deps: list[dict], missing: Counter) -> dict:
    h = norm(h)
    row = meta(c, h)
    row["role"] = role
    deps.append(row)
    if h not in NULLS and not row["exists"]:
        p = pkgid(h)
        if p:
            missing[p] += 1
    return row


def parse_terrain(c, h: str, violations: list[str], deps: list[dict], missing: Counter) -> dict:
    h = norm(h)
    out = {"hash": h, "target": meta(c, h, TERRAIN)}
    b, src = c.payload(h)
    out["source"] = src
    if b is None:
        out["status"] = "UNAVAILABLE"
        p = pkgid(h)
        if p:
            missing[p] += 1
        return out
    out["payload_bytes"] = len(b)
    out["payload_sha256"] = sha(b)
    if not out["target"]["class_matches"]:
        out["status"] = "CLASS_MISMATCH"
        violations.append(f"terrain:{h}:class_mismatch")
        return out
    if len(b) < 0xB0:
        out["status"] = "SHORT"
        violations.append(f"terrain:{h}:short:{len(b)}")
        return out

    groups = layer.dyn(b, 0x58, 0x60)
    parts = layer.dyn(b, 0x80, 0x0C)
    out["file_size_u64"] = u64(b, 0x00)
    out["vector10"] = vec4(b, 0x10)
    out["vector20"] = vec4(b, 0x20)
    out["vector30"] = vec4(b, 0x30)
    out["mesh_groups_array"] = groups
    out["static_parts_array"] = parts
    if not groups["ok"]:
        violations.append(f"terrain:{h}:mesh_groups_bounds")
    if not parts["ok"]:
        violations.append(f"terrain:{h}:static_parts_bounds")
    if not (groups["ok"] and parts["ok"]):
        out["status"] = "ARRAY_BOUNDS"
        return out

    top_fields = [
        (0x68, "vertices1"), (0x6C, "vertices2"), (0x70, "indices1"),
        (0x74, "material74"), (0x78, "material78"),
        (0x90, "vertices3"), (0x94, "vertices4"), (0x98, "indices2"),
        (0xA4, "materialA4"), (0xA8, "textureA8"),
    ]
    out["top_level_dependencies"] = {}
    for off, role in top_fields:
        th = hx(u32(b, off))
        out["top_level_dependencies"][role] = add_dep(c, th, f"terrain_{role}", deps, missing)

    mesh_groups = []
    for i in range(groups["count"]):
        o = groups["absolute"] + i * 0x60
        raw = b[o:o + 0x60]
        vals = [vec4(b, o + x) for x in (0x00, 0x10, 0x20)]
        if not all(math.isfinite(x) for v in vals for x in v):
            violations.append(f"terrain:{h}:mesh_group_{i}:nonfinite")
        dyemap = hx(u32(b, o + 0x58))
        mesh_groups.append({
            "index": i,
            "record_offset": o,
            "record_sha256": sha(raw),
            "record_hex": raw.hex().upper(),
            "vector00": vals[0],
            "vector10": vals[1],
            "vector20": vals[2],
            "u32_30_4c": [u32(b, o + x) for x in range(0x30, 0x50, 4)],
            "dyemap": add_dep(c, dyemap, "terrain_mesh_group_dyemap", deps, missing),
        })
    out["mesh_groups"] = mesh_groups
    out["mesh_group_count"] = len(mesh_groups)

    static_parts = []
    for i in range(parts["count"]):
        o = parts["absolute"] + i * 0x0C
        raw = b[o:o + 0x0C]
        material = hx(u32(b, o + 0x00))
        detail = u8(b, o + 0x0B)
        static_parts.append({
            "index": i,
            "record_offset": o,
            "record_sha256": sha(raw),
            "record_hex": raw.hex().upper(),
            "material": add_dep(c, material, "terrain_static_part_material", deps, missing),
            "index_offset": u32(b, o + 0x04),
            "index_count": u16(b, o + 0x08),
            "group_index": u8(b, o + 0x0A),
            "detail_level": detail,
            "selected_main_geom0": detail == 0,
        })
    out["static_parts"] = static_parts
    out["static_part_count"] = len(static_parts)
    out["selected_main_geom0_part_count"] = sum(x["selected_main_geom0"] for x in static_parts)
    bad_groups = [x for x in static_parts if x["group_index"] >= len(mesh_groups)]
    out["static_parts_with_group_index_oob"] = len(bad_groups)
    if bad_groups:
        violations.append(f"terrain:{h}:static_part_group_index_oob:{len(bad_groups)}")
    out["status"] = "D1_TERRAIN_PAYLOAD_PRESERVED"
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", type=Path, action="append", required=True)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--layer-census", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    layer_doc = json.loads(a.layer_census.read_text(encoding="utf-8"))
    if layer_doc.get("status") not in {"D1_WORLD_MAP_DATA_LAYER_CENSUS", "D1_WORLD_MAP_DATA_LAYER_CENSUS_PARTIAL"}:
        raise SystemExit(f"unexpected layer census status {layer_doc.get('status')!r}")
    c = v5.v3.base.Corpus([p.resolve() for p in a.snapshot], a.runtime.resolve())
    violations: list[str] = []
    missing: Counter = Counter()
    deps: list[dict] = []
    occurrences = []
    terrains: dict[str, dict] = {}

    for table in layer_doc.get("tables", []):
        for row in table.get("entries", []):
            if norm(row.get("resource_class") or "00000000") != TERRAIN_RESOURCE:
                continue
            rt = row.get("resource_target") or {}
            th = norm(rt.get("hash") or "FFFFFFFF")
            occ = {
                "map_data_table": row.get("map_data_table"),
                "entry_index": row.get("index"),
                "world_id": row.get("world_id"),
                "outer_rotation": row.get("rotation"),
                "outer_translation": row.get("translation"),
                "terrain": meta(c, th, TERRAIN),
            }
            occurrences.append(occ)
            if th in NULLS:
                violations.append(f"terrain_occurrence:{row.get('map_data_table')}:{row.get('index')}:null_target")
                continue
            if not occ["terrain"]["exists"]:
                p = pkgid(th)
                if p:
                    missing[p] += 1
                continue
            if not occ["terrain"]["class_matches"]:
                violations.append(f"terrain_occurrence:{th}:target_class_mismatch")
                continue
            if th not in terrains:
                terrains[th] = parse_terrain(c, th, violations, deps, missing)

    unique_deps = {}
    for d in deps:
        h = d["hash"]
        if h in NULLS:
            continue
        u = unique_deps.setdefault(h, {"hash": h, "package_id": d.get("package_id"), "exists": d.get("exists"), "meta": d.get("meta"), "roles": []})
        if d.get("role") not in u["roles"]:
            u["roles"].append(d.get("role"))
        u["exists"] = u["exists"] or d.get("exists")
        if u.get("meta") is None and d.get("meta") is not None:
            u["meta"] = d.get("meta")

    selected_parts = sum(x.get("selected_main_geom0_part_count", 0) for x in terrains.values())
    serialized_parts = sum(x.get("static_part_count", 0) for x in terrains.values())
    mesh_groups = sum(x.get("mesh_group_count", 0) for x in terrains.values())
    material_hashes = sorted({
        p["material"]["hash"]
        for t in terrains.values() for p in t.get("static_parts", [])
        if p["material"]["hash"] not in NULLS
    })
    selected_material_hashes = sorted({
        p["material"]["hash"]
        for t in terrains.values() for p in t.get("static_parts", [])
        if p.get("selected_main_geom0") and p["material"]["hash"] not in NULLS
    })
    dyemaps = sorted({
        g["dyemap"]["hash"]
        for t in terrains.values() for g in t.get("mesh_groups", [])
        if g["dyemap"]["hash"] not in NULLS
    })
    missing_ids = dict(sorted(missing.items()))
    out = {
        "schema_version": 1,
        "status": "D1_WORLD_TERRAIN_CENSUS_COMPLETE" if not violations and not missing_ids else "D1_WORLD_TERRAIN_CENSUS_PARTIAL",
        "pinned_source": PINNED_SOURCE,
        "source_map_data_table_count": layer_doc.get("map_data_table_count"),
        "source_entry_count": layer_doc.get("entry_count"),
        "terrain_resource_occurrence_count": len(occurrences),
        "unique_terrain_count": len(terrains),
        "mesh_group_count": mesh_groups,
        "serialized_static_part_count": serialized_parts,
        "selected_main_geom0_part_count": selected_parts,
        "unique_static_part_material_count": len(material_hashes),
        "unique_selected_material_count": len(selected_material_hashes),
        "unique_dyemap_count": len(dyemaps),
        "static_part_materials": material_hashes,
        "selected_materials": selected_material_hashes,
        "dyemaps": dyemaps,
        "unique_typed_dependency_count": len(unique_deps),
        "typed_dependencies": [unique_deps[k] for k in sorted(unique_deps)],
        "missing_dependency_package_ids": missing_ids,
        "occurrences": occurrences,
        "terrains": [terrains[k] for k in sorted(terrains)],
        "violations": violations,
        "policy": "Only source-typed D1 terrain fields are decoded. Every serialized terrain part is preserved; selected_main_geom0 marks only Charm's exact ELodCategory.MainGeom0 == 0 render selection. No vertex, UV, dye, shader, or material behavior is inferred by this census.",
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in (
        "status", "terrain_resource_occurrence_count", "unique_terrain_count", "mesh_group_count",
        "serialized_static_part_count", "selected_main_geom0_part_count", "unique_static_part_material_count",
        "unique_selected_material_count", "unique_dyemap_count", "unique_typed_dependency_count",
        "missing_dependency_package_ids", "violations"
    )}, indent=2))
    return 0 if out["status"] == "D1_WORLD_TERRAIN_CENSUS_COMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
