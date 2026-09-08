#!/usr/bin/env python3
"""Close D1 terrain selected-material -> PS4 vertex-shader input signatures.

The input terrain census already source-closes every rendered MainGeom0 part and
its exact material.  This adapter follows only those selected material FileHashes,
reads the retail ROI material VertexShader link at +0x28, validates the D1 PS4
32:9 shader header, and decodes the native Gnmx input semantic table with the
project's source-validated parser.

Missing shader/native payloads are reported only by exact FileHash package ID so
an indexed package closer can recover them.  Native semantic bytes remain numeric;
this tool does not invent POSITION/NORMAL/TEXCOORD names.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import struct
from pathlib import Path

import d1_tower_map_schema_validate_v5 as v5
from d1_filehash import package_hex
from d1_ps4_vertex_shader_header import parse_header, VERTEX_SHADER_TYPE, VERTEX_SHADER_SUBTYPE

PS4_MATERIAL_CLASS = "80801AD7"
NULLS = {"00000000", "FFFFFFFF"}


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def u32(b: bytes, o: int) -> int:
    if o < 0 or o + 4 > len(b):
        raise ValueError(f"u32 out of bounds 0x{o:X}/0x{len(b):X}")
    return struct.unpack_from("<I", b, o)[0]


def hx(v: int) -> str:
    return f"{v & 0xFFFFFFFF:08X}"


def pkgid(h: str) -> str | None:
    h = norm(h)
    if h in NULLS:
        return None
    try:
        return package_hex(h).lower()
    except Exception:
        return None


def meta_brief(m: dict | None) -> dict | None:
    if m is None:
        return None
    return {k: m.get(k) for k in ("tag_hash", "reference", "type", "subtype", "file_size", "index") if k in m}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", type=Path, action="append", required=True)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--terrain-census", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    census = json.loads(a.terrain_census.read_text(encoding="utf-8"))
    if census.get("status") != "D1_WORLD_TERRAIN_CENSUS_COMPLETE":
        raise SystemExit(f"terrain census not complete: {census.get('status')!r}")
    if census.get("violations") or census.get("missing_dependency_package_ids"):
        raise SystemExit("terrain census contains unresolved evidence")

    selected = sorted({norm(x) for x in census.get("selected_materials", []) if norm(x) not in NULLS})
    if len(selected) != int(census.get("unique_selected_material_count", -1)):
        raise SystemExit(f"selected material count mismatch {len(selected)} != {census.get('unique_selected_material_count')}")

    c = v5.v3.base.Corpus([p.resolve() for p in a.snapshot], a.runtime.resolve())
    missing = collections.Counter()
    violations: list[dict] = []
    materials = []
    vs_users: dict[str, list[str]] = collections.defaultdict(list)

    for mh in selected:
        m = c.entry_meta(mh)
        row = {"material": mh, "required_package_id": pkgid(mh), "entry": meta_brief(m)}
        if m is None:
            if pkgid(mh): missing[pkgid(mh)] += 1
            row["status"] = "MISSING"
            materials.append(row)
            continue
        if norm(m.get("reference") or "") != PS4_MATERIAL_CLASS:
            row["status"] = "CLASS_MISMATCH"
            violations.append({"material": mh, "error": f"reference {m.get('reference')} != {PS4_MATERIAL_CLASS}"})
            materials.append(row)
            continue
        b, src = c.payload(mh)
        row["source"] = src
        if b is None:
            if pkgid(mh): missing[pkgid(mh)] += 1
            row["status"] = "PAYLOAD_UNAVAILABLE"
            materials.append(row)
            continue
        row["payload_bytes"] = len(b)
        row["payload_sha256"] = hashlib.sha256(b).hexdigest()
        try:
            vs = hx(u32(b, 0x28))
        except Exception as ex:
            row["status"] = "DECODE_ERROR"
            violations.append({"material": mh, "error": repr(ex)})
            materials.append(row)
            continue
        row["vertex_shader"] = vs
        row["vertex_shader_required_package_id"] = pkgid(vs)
        if vs in NULLS:
            row["status"] = "NULL_VERTEX_SHADER"
            violations.append({"material": mh, "error": "null serialized vertex shader"})
        else:
            row["status"] = "D1_TERRAIN_SELECTED_MATERIAL_VS_LINK_PRESERVED"
            vs_users[vs].append(mh)
        materials.append(row)

    shaders = []
    sig_hist = collections.Counter()
    semantic_hist = collections.Counter()
    width_total_hist = collections.Counter()
    for vs in sorted(vs_users):
        m = c.entry_meta(vs)
        row = {
            "vertex_shader": vs,
            "material_count": len(set(vs_users[vs])),
            "materials": sorted(set(vs_users[vs])),
            "required_package_id": pkgid(vs),
            "entry": meta_brief(m),
        }
        if m is None:
            if pkgid(vs): missing[pkgid(vs)] += 1
            row["status"] = "HEADER_MISSING"
            shaders.append(row)
            continue
        if (int(m.get("type", -1)), int(m.get("subtype", -1))) != (VERTEX_SHADER_TYPE, VERTEX_SHADER_SUBTYPE):
            row["status"] = "HEADER_CLASS_MISMATCH"
            violations.append({"vertex_shader": vs, "error": f"resource {m.get('type')}:{m.get('subtype')} != 32:9"})
            shaders.append(row)
            continue
        hb, hsrc = c.payload(vs)
        row["header_source"] = hsrc
        if hb is None:
            if pkgid(vs): missing[pkgid(vs)] += 1
            row["status"] = "HEADER_PAYLOAD_UNAVAILABLE"
            shaders.append(row)
            continue
        native = norm(m.get("reference") or "FFFFFFFF")
        row["native_shader"] = native
        row["native_required_package_id"] = pkgid(native)
        nm = None if native in NULLS else c.entry_meta(native)
        row["native_entry"] = meta_brief(nm)
        nb = None
        nsrc = None
        if native not in NULLS:
            nb, nsrc = c.payload(native)
        row["native_source"] = nsrc
        if native in NULLS:
            row["status"] = "NULL_NATIVE_SHADER"
            violations.append({"vertex_shader": vs, "error": "null native shader reference"})
            shaders.append(row)
            continue
        if nm is None or nb is None:
            if pkgid(native): missing[pkgid(native)] += 1
            row["status"] = "NATIVE_PAYLOAD_MISSING"
            shaders.append(row)
            continue
        try:
            dec = parse_header(hb, nb)
            sem = dec["gnmx"]["input_semantics"]
            widths = [int(x["size_in_elements"]) for x in sem]
            ids = [int(x["semantic"]) for x in sem]
            vgprs = [int(x["vgpr"]) for x in sem]
            row.update({
                "status": "D1_TERRAIN_NATIVE_VS_SIGNATURE_PRESERVED",
                "header_bytes": len(hb),
                "header_sha256": hashlib.sha256(hb).hexdigest(),
                "native_bytes": len(nb),
                "native_sha256": hashlib.sha256(nb).hexdigest(),
                "input_semantic_count": len(sem),
                "input_component_widths": widths,
                "input_semantic_ids": ids,
                "input_vgprs": vgprs,
                "output_semantic_count": int(dec["gnmx"]["num_export_semantics"]),
                "checks": dec.get("checks"),
                "native_checks": dec.get("native_checks"),
            })
            sig_hist["/".join(map(str, widths))] += 1
            width_total_hist[str(sum(widths))] += 1
            semantic_hist["/".join(map(str, ids))] += 1
            checks = dec.get("checks") or {}
            native_checks = dec.get("native_checks") or {}
            if not all(bool(v) for v in checks.values()):
                violations.append({"vertex_shader": vs, "error": "header checks failed", "checks": checks})
            for k in ("resolved", "stage_is_vertex_shader", "gnmx_shader_size_matches_orbshdr_end", "usage_count_matches_orbshdr"):
                if k in native_checks and not bool(native_checks[k]):
                    violations.append({"vertex_shader": vs, "error": f"native check {k} failed", "native_checks": native_checks})
        except Exception as ex:
            row["status"] = "SIGNATURE_DECODE_ERROR"
            row["error"] = repr(ex)
            violations.append({"vertex_shader": vs, "error": repr(ex)})
        shaders.append(row)

    missing_ids = dict(sorted(missing.items()))
    resolved_materials = sum(x.get("status") == "D1_TERRAIN_SELECTED_MATERIAL_VS_LINK_PRESERVED" for x in materials)
    resolved_shaders = sum(x.get("status") == "D1_TERRAIN_NATIVE_VS_SIGNATURE_PRESERVED" for x in shaders)
    complete = not missing_ids and not violations and resolved_materials == len(selected) and resolved_shaders == len(vs_users)
    out = {
        "schema_version": 1,
        "status": "D1_WORLD_TERRAIN_VS_SIGNATURE_CENSUS_COMPLETE" if complete else "D1_WORLD_TERRAIN_VS_SIGNATURE_CENSUS_PARTIAL",
        "terrain_count": census.get("unique_terrain_count"),
        "selected_main_geom0_part_count": census.get("selected_main_geom0_part_count"),
        "selected_material_count": len(selected),
        "resolved_selected_material_count": resolved_materials,
        "unique_vertex_shader_count": len(vs_users),
        "resolved_vertex_shader_count": resolved_shaders,
        "signature_component_width_histogram": dict(sorted(sig_hist.items())),
        "signature_total_component_histogram": dict(sorted(width_total_hist.items())),
        "native_semantic_id_sequence_histogram": dict(sorted(semantic_hist.items())),
        "missing_dependency_package_ids": missing_ids,
        "materials": materials,
        "vertex_shaders": shaders,
        "violations": violations,
        "policy": "Only the 108 source-selected terrain materials participate. VertexShader comes from retail ROI material +0x28. Gnmx input semantic IDs remain numeric native link IDs. Missing dependencies are reported only by exact FileHash package ID; no vertex semantic names or byte offsets are inferred here.",
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in (
        "status", "terrain_count", "selected_main_geom0_part_count", "selected_material_count",
        "resolved_selected_material_count", "unique_vertex_shader_count", "resolved_vertex_shader_count",
        "signature_component_width_histogram", "signature_total_component_histogram",
        "native_semantic_id_sequence_histogram", "missing_dependency_package_ids", "violations"
    )}, indent=2))
    return 0 if complete else 2


if __name__ == "__main__":
    raise SystemExit(main())
