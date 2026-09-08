#!/usr/bin/env python3
"""Close selected D1 terrain materials to exact PS4 pixel-shader resource usage.

Inputs are source-selected MainGeom0 materials from ``d1_world_terrain_census.py``.
For each material this adapter:
  * reads SMaterial_ROI.PixelShader at the pinned +0x2A8 offset;
  * preserves the exact +0x2B8 PS texture-index -> Texture TagHash array;
  * validates the observed PS4 pixel-shader FileEntry class 32:8;
  * follows the shader header's serialized Reference to the native Orbis payload;
  * parses OrbShdr ShaderBinaryInfo and InputUsageSlot records using the project's
    source-correlated PS4 parser.

The result is a fail-closed census of exact material -> PS -> native resource API
slots. It does not assign diffuse/normal/dyemap meanings and it does not infer any
terrain shader equation. Missing dependencies are reported only by FileHash package
ID for indexed archive recovery.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path

import d1_tower_map_schema_validate_v5 as v5
from d1_filehash import package_hex
from d1_material_decode import parse_material
from d1_ps4_shader_binary_probe import find_footer, parse_binary_info, parse_usage

PS4_MATERIAL_CLASS = "80801AD7"
PIXEL_SHADER_TYPE = 32
PIXEL_SHADER_SUBTYPE = 8
NULLS = {"00000000", "FFFFFFFF"}


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def pkgid(h: object) -> str | None:
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

    terrain = json.loads(a.terrain_census.read_text(encoding="utf-8"))
    if terrain.get("status") != "D1_WORLD_TERRAIN_CENSUS_COMPLETE":
        raise SystemExit(f"terrain census not complete: {terrain.get('status')!r}")
    if terrain.get("violations") or terrain.get("missing_dependency_package_ids"):
        raise SystemExit("terrain census contains unresolved evidence")

    selected = sorted({norm(x) for x in terrain.get("selected_materials", []) if norm(x) not in NULLS})
    if len(selected) != int(terrain.get("unique_selected_material_count", -1)):
        raise SystemExit("terrain selected-material count mismatch")

    c = v5.v3.base.Corpus([p.resolve() for p in a.snapshot], a.runtime.resolve())
    missing = collections.Counter()
    violations: list[dict] = []
    material_rows = []
    ps_users: dict[str, list[str]] = collections.defaultdict(list)
    ps_texture_layouts: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)

    for mh in selected:
        mm = c.entry_meta(mh)
        row = {"material": mh, "required_package_id": pkgid(mh), "entry": meta_brief(mm)}
        if mm is None:
            if pkgid(mh):
                missing[pkgid(mh)] += 1
            row["status"] = "MISSING"
            material_rows.append(row)
            continue
        if norm(mm.get("reference") or "") != PS4_MATERIAL_CLASS:
            row["status"] = "CLASS_MISMATCH"
            violations.append({"material": mh, "error": f"reference {mm.get('reference')} != {PS4_MATERIAL_CLASS}"})
            material_rows.append(row)
            continue
        b, src = c.payload(mh)
        row["source"] = src
        if b is None:
            if pkgid(mh):
                missing[pkgid(mh)] += 1
            row["status"] = "PAYLOAD_UNAVAILABLE"
            material_rows.append(row)
            continue
        try:
            dec = parse_material(b, "PS4")
        except Exception as ex:
            row["status"] = "MATERIAL_DECODE_ERROR"
            row["error"] = repr(ex)
            violations.append({"material": mh, "error": repr(ex)})
            material_rows.append(row)
            continue
        ps = norm(dec.get("pixel_shader"))
        textures = [
            {"texture_index": int(x["texture_index"]), "texture": norm(x["texture"])}
            for x in dec["ps_textures"]["items"]
            if norm(x.get("texture")) not in NULLS
        ]
        indices = [x["texture_index"] for x in textures]
        if len(indices) != len(set(indices)):
            violations.append({"material": mh, "error": "duplicate PS texture index", "indices": indices})
        row.update({
            "payload_bytes": len(b),
            "payload_sha256": hashlib.sha256(b).hexdigest(),
            "pixel_shader": ps,
            "pixel_shader_required_package_id": pkgid(ps),
            "ps_textures": textures,
            "ps_texture_indices": indices,
            "ps_texture_count": len(textures),
        })
        if ps in NULLS:
            row["status"] = "NULL_PIXEL_SHADER"
            violations.append({"material": mh, "error": "null serialized pixel shader"})
        else:
            row["status"] = "D1_TERRAIN_SELECTED_MATERIAL_PS_LINK_PRESERVED"
            ps_users[ps].append(mh)
            ps_texture_layouts[ps]["/".join(str(x) for x in indices)] += 1
        material_rows.append(row)

    shader_rows = []
    native_slot_layout_hist = collections.Counter()
    native_texture_api_slot_hist = collections.Counter()
    stage_hist = collections.Counter()
    for ps in sorted(ps_users):
        pm = c.entry_meta(ps)
        row = {
            "pixel_shader": ps,
            "required_package_id": pkgid(ps),
            "entry": meta_brief(pm),
            "material_count": len(set(ps_users[ps])),
            "materials": sorted(set(ps_users[ps])),
            "material_ps_texture_layout_histogram": dict(sorted(ps_texture_layouts[ps].items())),
        }
        if pm is None:
            if pkgid(ps):
                missing[pkgid(ps)] += 1
            row["status"] = "HEADER_MISSING"
            shader_rows.append(row)
            continue
        if (int(pm.get("type", -1)), int(pm.get("subtype", -1))) != (PIXEL_SHADER_TYPE, PIXEL_SHADER_SUBTYPE):
            row["status"] = "HEADER_CLASS_MISMATCH"
            violations.append({"pixel_shader": ps, "error": f"resource {pm.get('type')}:{pm.get('subtype')} != 32:8"})
            shader_rows.append(row)
            continue
        hb, hsrc = c.payload(ps)
        row["header_source"] = hsrc
        if hb is None:
            if pkgid(ps):
                missing[pkgid(ps)] += 1
            row["status"] = "HEADER_PAYLOAD_UNAVAILABLE"
            shader_rows.append(row)
            continue
        native = norm(pm.get("reference") or "FFFFFFFF")
        row["native_shader"] = native
        row["native_required_package_id"] = pkgid(native)
        nm = None if native in NULLS else c.entry_meta(native)
        row["native_entry"] = meta_brief(nm)
        if native in NULLS:
            row["status"] = "NULL_NATIVE_SHADER"
            violations.append({"pixel_shader": ps, "error": "null native shader reference"})
            shader_rows.append(row)
            continue
        nb, nsrc = c.payload(native) if nm is not None else (None, None)
        row["native_source"] = nsrc
        if nm is None or nb is None:
            if pkgid(native):
                missing[pkgid(native)] += 1
            row["status"] = "NATIVE_PAYLOAD_MISSING"
            shader_rows.append(row)
            continue
        try:
            footer, locator = find_footer(nb)
            row["orbshdr_locator"] = locator
            if footer is None:
                raise ValueError("OrbShdr footer unresolved")
            info = parse_binary_info(nb, footer)
            usage = parse_usage(nb, footer, info)
            slots = usage["slots"]
            tex_slots = sorted({
                int(x["api_slot"])
                for x in slots
                if x.get("resource_descriptor_kind") == "T# texture/image"
            })
            slot_key = ";".join(
                f"{x['usage_name']}:{x['api_slot']}:{x['start_register']}:{x.get('resource_descriptor_kind') or '-'}"
                for x in slots
            )
            native_slot_layout_hist[slot_key] += 1
            native_texture_api_slot_hist["/".join(map(str, tex_slots))] += 1
            stage_hist[str(info.get("stage"))] += 1
            row.update({
                "status": "D1_TERRAIN_NATIVE_PS_RESOURCE_USAGE_PRESERVED",
                "header_bytes": len(hb),
                "header_sha256": hashlib.sha256(hb).hexdigest(),
                "native_bytes": len(nb),
                "native_sha256": hashlib.sha256(nb).hexdigest(),
                "binary_info": info,
                "usage": usage,
                "native_texture_api_slots": tex_slots,
            })
            if info.get("stage") != "PixelShader":
                violations.append({"pixel_shader": ps, "error": f"native stage {info.get('stage')!r} != PixelShader"})
            if not locator.get("first_token_standard") or not locator.get("formula_magic_matches"):
                violations.append({"pixel_shader": ps, "error": "native OrbShdr framing checks failed", "locator": locator})
        except Exception as ex:
            row["status"] = "NATIVE_RESOURCE_DECODE_ERROR"
            row["error"] = repr(ex)
            violations.append({"pixel_shader": ps, "error": repr(ex)})
        shader_rows.append(row)

    missing_ids = dict(sorted(missing.items()))
    resolved_materials = sum(x.get("status") == "D1_TERRAIN_SELECTED_MATERIAL_PS_LINK_PRESERVED" for x in material_rows)
    resolved_shaders = sum(x.get("status") == "D1_TERRAIN_NATIVE_PS_RESOURCE_USAGE_PRESERVED" for x in shader_rows)
    complete = (
        not missing_ids and not violations and
        resolved_materials == len(selected) and
        resolved_shaders == len(ps_users)
    )
    freq = {h: len(set(users)) for h, users in sorted(ps_users.items())}
    out = {
        "schema_version": 1,
        "status": "D1_WORLD_TERRAIN_PS_RESOURCE_CENSUS_COMPLETE" if complete else "D1_WORLD_TERRAIN_PS_RESOURCE_CENSUS_PARTIAL",
        "terrain_count": terrain.get("unique_terrain_count"),
        "selected_main_geom0_part_count": terrain.get("selected_main_geom0_part_count"),
        "selected_material_count": len(selected),
        "resolved_selected_material_count": resolved_materials,
        "unique_pixel_shader_count": len(ps_users),
        "resolved_pixel_shader_count": resolved_shaders,
        "pixel_shader_frequency": freq,
        "native_stage_histogram": dict(sorted(stage_hist.items())),
        "native_texture_api_slot_histogram": dict(sorted(native_texture_api_slot_hist.items())),
        "native_resource_slot_layout_histogram": dict(sorted(native_slot_layout_hist.items())),
        "missing_dependency_package_ids": missing_ids,
        "materials": material_rows,
        "pixel_shaders": shader_rows,
        "violations": violations,
        "policy": (
            "Only source-selected terrain materials participate. PixelShader and PSTextures come from pinned "
            "SMaterial_ROI +0x2A8/+0x2B8 fields. Native InputUsageSlot records are preserved exactly. "
            "No texture role, dyemap slot, or shading equation is inferred from slot numbers."
        ),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in (
        "status", "terrain_count", "selected_main_geom0_part_count", "selected_material_count",
        "resolved_selected_material_count", "unique_pixel_shader_count", "resolved_pixel_shader_count",
        "pixel_shader_frequency", "native_stage_histogram", "native_texture_api_slot_histogram",
        "missing_dependency_package_ids", "violations"
    )}, indent=2))
    return 0 if complete else 2


if __name__ == "__main__":
    raise SystemExit(main())
