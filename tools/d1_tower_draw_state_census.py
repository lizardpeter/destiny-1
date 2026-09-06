#!/usr/bin/env python3
"""Correlate D1 PS4 Tower static draw records with exact material state.

This is a structural census only. It joins the already-proven D1 static-table
MaterialIndex/StaticIndex relation to the raw mesh record and material header,
then groups the resulting rows by pixel shader. Unknown fields remain unknown.

Material FileHashes are resolved class-stably: only occurrences whose reference is
exactly the D1 PS4 ROI material class can supply material bytes. Newer occurrences
with another class are never accepted as fallback material payloads.

This census deliberately does NOT require every referenced vertex/index/transform
payload to be present. Those payloads are required for geometry export, but not to
read a static table's serialized material index, static index, mesh state, detail
level, primitive type, or index range. Missing unrelated backing payloads are
reported separately as source gaps and cannot invalidate the draw-state join.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import d1_tower_map_schema_validate as schema
from d1_material_decode import parse_material
from d1_ps4_material_state_census import class_stable_payload

CELLS = [
    "80C98254", "80C984D8", "80C98A6B", "80C993CD", "80C993CF",
    "80C997F5", "80C99981", "80CA0B70", "80CA0B72", "80CA0C60",
]
TARGET_PS = "809DCD66"
PEER_PS = "80CA0BE9"
VISIBLE_DETAIL_LEVELS = {0, 1, 2, 3, 10}


def norm(x: object) -> str:
    return str(x).upper().removeprefix("0X").zfill(8)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", type=Path, action="append", required=True)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    c = schema.Corpus([p.resolve() for p in a.snapshot], a.runtime.resolve())
    material_cache: dict[str, dict | None] = {}
    rows = []
    violations = []
    source_gaps = []

    def material(h: str) -> dict | None:
        h = norm(h)
        if h in material_cache:
            return material_cache[h]
        b, src, meta = class_stable_payload(c, h)
        if b is None:
            source_gaps.append({"material": h, "gap": "class_stable_material_payload_unavailable"})
            material_cache[h] = None
            return None
        try:
            p = parse_material(b, "PS4")
        except Exception as ex:
            violations.append({"material": h, "error": "material_parse_failed", "detail": repr(ex), "source": src})
            material_cache[h] = None
            return None
        r = {
            "material": h,
            "source": src,
            "meta": meta,
            "unk08": norm(p["unk08"]),
            "unk0c": norm(p["unk0c"]),
            "unk10": norm(p["unk10"]),
            "unk20_hex": str(p["unk20_hex"]).upper().zfill(4),
            "vertex_shader": norm(p["vertex_shader"]),
            "pixel_shader": norm(p["pixel_shader"]),
            "ps_vector4_container": norm(p["ps_vector4_container"]),
        }
        material_cache[h] = r
        return r

    for cell in CELLS:
        vr = schema.validate_static_map_data(c, cell)
        d1 = vr.get("d1_validation")
        if d1 is None:
            violations.append({"cell": cell, "error": "d1_static_data_unavailable", "validation": vr.get("violations")})
            continue
        if not vr.get("ok"):
            source_gaps.append({
                "cell": cell,
                "gap": "full_geometry_validation_not_green",
                "validation": vr.get("violations"),
                "d1_validation": d1.get("violations"),
                "note": "nonfatal for draw-state census; backing geometry/transform availability is outside this join",
            })

        tables = d1.get("static_tables", [])
        if not tables:
            violations.append({"cell": cell, "error": "no_static_tables"})
            continue

        for table in tables:
            arrays = table.get("arrays", {})
            required = [arrays.get("materials"), arrays.get("meshes"), arrays.get("infos")]
            if any(not x or not x.get("ok") for x in required):
                violations.append({"cell": cell, "static_table": table.get("hash"), "error": "required_static_table_array_bounds"})
                continue
            mats = table.get("material_hashes", [])
            meshes = table.get("mesh_entries", [])
            infos = table.get("info_entries", [])
            if len(mats) != arrays["materials"]["count"] or len(meshes) != arrays["meshes"]["count"] or len(infos) != arrays["infos"]["count"]:
                violations.append({"cell": cell, "static_table": table.get("hash"), "error": "decoded_array_count_mismatch"})
                continue

            missing_mesh_targets = sum(not bool(m.get("all_targets_exist")) for m in meshes)
            if missing_mesh_targets:
                source_gaps.append({
                    "cell": cell,
                    "static_table": table.get("hash"),
                    "gap": "mesh_backing_targets_absent_from_bounded_corpus",
                    "mesh_count": len(meshes),
                    "missing_mesh_target_rows": missing_mesh_targets,
                })

            for info in infos:
                # The draw-state join needs only the two serialized table indices.
                # Transform bounds/backing are intentionally not a prerequisite.
                if not info.get("material_in_bounds") or not info.get("static_in_bounds"):
                    violations.append({
                        "cell": cell,
                        "static_table": table.get("hash"),
                        "info_index": info.get("index"),
                        "error": "material_or_static_index_out_of_bounds",
                    })
                    continue
                mi = info["material_index"]
                si = info["static_index"]
                mh = norm(mats[mi])
                mr = material(mh)
                if mr is None:
                    continue
                mesh = meshes[si]
                visible = (
                    mesh.get("detail_level") in VISIBLE_DETAIL_LEVELS
                    and mr["unk08"] == "00000001"
                    and mr["pixel_shader"] not in ("00000000", "FFFFFFFF")
                    and mr["vertex_shader"] not in ("00000000", "FFFFFFFF")
                )
                rows.append({
                    "cell": cell,
                    "d1_static_map_data": d1.get("hash"),
                    "static_table": table.get("hash"),
                    "info_index": info["index"],
                    "instance_count": info["instance_count"],
                    "transform_index": info["transform_index"],
                    "transform_in_bounds_in_bounded_corpus": info.get("transform_in_bounds"),
                    "material_index": mi,
                    "static_index": si,
                    "material": mh,
                    "pixel_shader": mr["pixel_shader"],
                    "vertex_shader": mr["vertex_shader"],
                    "material_unk08": mr["unk08"],
                    "material_unk0c": mr["unk0c"],
                    "material_unk10": mr["unk10"],
                    "material_unk20": mr["unk20_hex"],
                    "material_payload_source": mr["source"],
                    "ps_external_vector_present": mr["ps_vector4_container"] not in ("00000000", "FFFFFFFF"),
                    "mesh_backing_targets_present": bool(mesh.get("all_targets_exist")),
                    "mesh_unk0c_u16": mesh.get("unk0C"),
                    "mesh_unk0c_hex": f"{int(mesh.get('unk0C', 0)):04X}",
                    "detail_level": mesh.get("detail_level"),
                    "primitive_type": mesh.get("primitive_type"),
                    "index_offset": mesh.get("index_offset"),
                    "index_count": mesh.get("index_count"),
                    "retail_visible_candidate": visible,
                })

    by_ps = defaultdict(list)
    for r in rows:
        by_ps[r["pixel_shader"]].append(r)

    groups = {}
    for ps, grp in sorted(by_ps.items()):
        groups[ps] = {
            "row_count": len(grp),
            "visible_row_count": sum(bool(x["retail_visible_candidate"]) for x in grp),
            "material_count": len({x["material"] for x in grp}),
            "mesh_unk0c_histogram": dict(Counter(x["mesh_unk0c_hex"] for x in grp)),
            "material_unk0c_histogram": dict(Counter(x["material_unk0c"] for x in grp)),
            "material_unk20_histogram": dict(Counter(x["material_unk20"] for x in grp)),
            "detail_level_histogram": dict(Counter(str(x["detail_level"]) for x in grp)),
            "primitive_type_histogram": dict(Counter(str(x["primitive_type"]) for x in grp)),
        }

    target = [r for r in rows if r["pixel_shader"] == TARGET_PS]
    target_visible = [r for r in target if r["retail_visible_candidate"]]
    peer = [r for r in rows if r["pixel_shader"] == PEER_PS]

    out = {
        "schema_version": 3,
        "status": "D1_TOWER_DRAW_STATE_CENSUS_COMPLETE" if not violations else "D1_TOWER_DRAW_STATE_CENSUS_PARTIAL",
        "cells": CELLS,
        "material_selection_policy": "CLASS_STABLE_NEWEST_REFERENCE_ONLY",
        "structural_scope": "static-table arrays + MaterialIndex + StaticIndex + serialized mesh record; geometry/transform backing not required",
        "row_count": len(rows),
        "material_count": len({r["material"] for r in rows}),
        "pixel_shader_count": len(by_ps),
        "source_gap_count": len(source_gaps),
        "source_gaps": source_gaps,
        "violations": violations,
        "pixel_shader_groups": groups,
        "target_809DCD66": {
            "row_count": len(target),
            "visible_row_count": len(target_visible),
            "material_count": len({r["material"] for r in target}),
            "mesh_unk0c_histogram": dict(Counter(r["mesh_unk0c_hex"] for r in target)),
            "visible_mesh_unk0c_histogram": dict(Counter(r["mesh_unk0c_hex"] for r in target_visible)),
            "material_unk0c_histogram": dict(Counter(r["material_unk0c"] for r in target)),
            "material_unk20_histogram": dict(Counter(r["material_unk20"] for r in target)),
            "primitive_type_histogram": dict(Counter(str(r["primitive_type"]) for r in target_visible)),
            "rows": target,
        },
        "peer_80CA0BE9": {
            "row_count": len(peer),
            "material_count": len({r["material"] for r in peer}),
            "mesh_unk0c_histogram": dict(Counter(r["mesh_unk0c_hex"] for r in peer)),
            "rows": peer,
        },
        "rows": rows,
        "policy": (
            "Static Info MaterialIndex/StaticIndex joins and mesh-record bytes are structural retail facts. Material and mesh unknown fields "
            "are emitted raw and grouped mechanically; no blend/cull/depth semantic is assigned. Material FileHash reuse is resolved only "
            "inside the exact PS4 ROI material class. Missing geometry/transform payloads are source gaps, not evidence against serialized draw state."
        ),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({
        "status": out["status"],
        "row_count": out["row_count"],
        "material_count": out["material_count"],
        "pixel_shader_count": out["pixel_shader_count"],
        "source_gap_count": out["source_gap_count"],
        "target_809DCD66": {k: out["target_809DCD66"][k] for k in (
            "row_count", "visible_row_count", "material_count", "mesh_unk0c_histogram",
            "visible_mesh_unk0c_histogram", "material_unk0c_histogram", "material_unk20_histogram",
            "primitive_type_histogram")},
        "peer_80CA0BE9": {k: out["peer_80CA0BE9"][k] for k in ("row_count", "material_count", "mesh_unk0c_histogram")},
        "violations": violations,
    }, indent=2))
    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
