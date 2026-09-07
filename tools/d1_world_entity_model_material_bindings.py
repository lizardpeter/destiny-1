#!/usr/bin/env python3
"""Resolve D1 world EntityModel part materials through their owning EntityResource.

Pinned Charm source:
  MontagueM/Charm@50d36ee1f9ecadad7522504c20b1f3f9c97e30af
  Tiger/Schema/Entity/EntityModel.cs
  Tiger/Schema/Entity/EntityStructs.cs

For D1 model-parent EntityResource (80800861):
  +0x10 ResourcePointer -> 80801A80 model discriminator
  +0x18 ResourcePointer -> 80801A9C model-parent payload

D1 model-parent payload (raw 9C1A8080, size 0x290):
  +0x15C EntityModel FileHash
  +0x230 DynamicArray<SExternalMaterialMapEntry>, stride 0x0C
  +0x270 DynamicArray<D2Class_14008080>, stride 0x04

SExternalMaterialMapEntry:
  +0x00 int MaterialCount
  +0x04 int MaterialStartIndex
  +0x08 int unknown

Charm DynamicMeshPart material selection:
  VariantShaderIndex == -1 -> part.Material
  otherwise map[VariantShaderIndex], then
    mats[MaterialStartIndex + (0 % MaterialCount)].Material

Charm's ROI EntityModel.GenerateParts then explicitly skips a DynamicMeshPart when
its resolved Material is null (and also skips missing VS/PS). Therefore serialized
00000000/FFFFFFFF Material FileHash sentinels are valid source-proven non-renderable
parts, not broken material bindings. Non-null missing/wrong-class materials remain
hard failures.

This tool proves the mapping independently from geometry export. It fails closed on
invalid variant indices, empty mapped material ranges, out-of-bounds external material
indices, unavailable non-null material tags, or a parent/model ownership mismatch.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import d1_tower_map_schema_validate_v5 as v5
from d1_entity_model_probe import parse_model
from d1_entity_resource_probe import parse_resource, ENTITY_RESOURCE_CLASS, D1_MODEL_PARENT

ENTITY_MODEL_CLASS = "80801AB5"
MATERIAL_CLASS = "80801AD7"
NULLS = {"00000000", "FFFFFFFF"}
MODEL_PARENT_SIZE = 0x290
MAP_OFF = 0x230
MAP_STRIDE = 0x0C
MATS_OFF = 0x270
MATS_STRIDE = 0x04
PINNED_SOURCE = (
    "MontagueM/Charm@50d36ee1f9ecadad7522504c20b1f3f9c97e30af "
    "Tiger/Schema/Entity/EntityModel.cs + Tiger/Schema/Entity/EntityStructs.cs + Tiger/SchemaTypes.cs"
)
NULL_MATERIAL_SOURCE_RULE = (
    "ROI EntityModel.GenerateParts skips DynamicMeshPart when resolved Material is null; "
    "00000000/FFFFFFFF serialized Material sentinels are therefore explicit non-renderable parts."
)


def norm(x):
    return str(x).upper().removeprefix("0X").zfill(8)


def hx(v):
    return f"{v:08X}"


def i32(b, o):
    return struct.unpack_from("<i", b, o)[0]


def u32(b, o):
    return struct.unpack_from("<I", b, o)[0]


def i64(b, o):
    return struct.unpack_from("<q", b, o)[0]


def dyn(b, off, stride):
    if off + 0x10 > len(b):
        return {"ok": False, "field_offset": off, "error": "descriptor_oob"}
    count = i32(b, off)
    unk = u32(b, off + 4)
    rel = i64(b, off + 8)
    absolute = off + 8 + rel + 0x10
    end = absolute + max(count, 0) * stride
    pointer_ok = absolute >= 0 and end <= len(b)
    ok = count >= 0 and (count == 0 or pointer_ok)
    return {
        "ok": ok,
        "field_offset": off,
        "count": count,
        "unknown04": unk,
        "relative": rel,
        "absolute": absolute,
        "end": end,
        "stride": stride,
        "serialized_pointer_bounds_ok": pointer_ok,
        "zero_count_no_dereference": count == 0,
        "payload_size": len(b),
    }


def meta(c, h, expected=None):
    h = norm(h)
    m = c.entry_meta(h)
    return {
        "hash": h,
        "meta": m,
        "exists": m is not None,
        "expected_class": expected,
        "class_matches": bool(m and (expected is None or norm(m.get("reference", "")) == expected)),
        "is_null_sentinel": h in NULLS,
    }


def parse_parent(c, parent_hash, expected_model):
    parent_hash = norm(parent_hash)
    expected_model = norm(expected_model)
    m = meta(c, parent_hash, ENTITY_RESOURCE_CLASS)
    b, src = c.payload(parent_hash)
    out = {
        "parent_resource": parent_hash,
        "target": m,
        "payload_source": src,
        "expected_model": expected_model,
        "violations": [],
    }
    if not m["class_matches"] or b is None:
        out["violations"].append("model_parent_resource_missing_class_or_payload")
        return out
    try:
        pr = parse_resource(b, "PS4")
    except Exception as ex:
        out["violations"].append("model_parent_resource_parse:" + repr(ex))
        return out
    out["entity_resource"] = pr
    if pr.get("semantic_role") != "entity_model":
        out["violations"].append("resource_not_entity_model_role")
        return out
    actual = norm(pr.get("embedded_model_tag_hash", "FFFFFFFF"))
    out["embedded_model"] = meta(c, actual, ENTITY_MODEL_CLASS)
    if actual != expected_model:
        out["violations"].append(f"parent_model_mismatch:{actual}!={expected_model}")
        return out
    p = pr.get("unk18", {})
    base = p.get("target_offset")
    if p.get("class_hash") != f"{D1_MODEL_PARENT:08X}" or not isinstance(base, int):
        out["violations"].append("unk18_not_D1_model_parent")
        return out
    if base < 0 or base + MODEL_PARENT_SIZE > len(b):
        out["violations"].append("model_parent_payload_oob")
        return out
    maps = dyn(b, base + MAP_OFF, MAP_STRIDE)
    mats = dyn(b, base + MATS_OFF, MATS_STRIDE)
    out["external_material_map_array"] = maps
    out["external_materials_array"] = mats
    if not maps["ok"]:
        out["violations"].append("external_material_map_bounds")
    if not mats["ok"]:
        out["violations"].append("external_materials_bounds")
    if out["violations"]:
        return out
    map_rows = []
    for i in range(maps["count"]):
        o = maps["absolute"] + i * MAP_STRIDE
        map_rows.append(
            {
                "variant_shader_index": i,
                "record_offset": o,
                "material_count": i32(b, o),
                "material_start_index": i32(b, o + 4),
                "unknown08": i32(b, o + 8),
            }
        )
    material_rows = []
    for i in range(mats["count"]):
        o = mats["absolute"] + i * MATS_STRIDE
        h = hx(u32(b, o))
        material_rows.append({"index": i, "record_offset": o, **meta(c, h, MATERIAL_CLASS)})
    out["external_material_map"] = map_rows
    out["external_materials"] = material_rows
    out["validation_ok"] = not out["violations"]
    return out


def _classify_selected_material(row, selected, violation_name):
    """Apply the pinned ROI null-material renderability rule to one selected slot."""
    row["selected_material"] = selected
    if selected.get("is_null_sentinel"):
        row["selection_status"] = "EXPLICIT_NULL_MATERIAL"
        row["renderable"] = False
        row["null_material_source_rule"] = NULL_MATERIAL_SOURCE_RULE
    elif selected.get("class_matches"):
        row["selection_status"] = "BOUND_MATERIAL"
        row["renderable"] = True
    else:
        row["selection_status"] = "INVALID_NON_NULL_MATERIAL"
        row["renderable"] = False
        row["violations"].append(violation_name)


def bind_model(c, model_hash, parent_hash):
    model_hash = norm(model_hash)
    parent = parse_parent(c, parent_hash, model_hash)
    out = {
        "model": model_hash,
        "parent_resource": norm(parent_hash),
        "parent": parent,
        "meshes": [],
        "violations": list(parent.get("violations", [])),
    }
    mm = meta(c, model_hash, ENTITY_MODEL_CLASS)
    mb, msrc = c.payload(model_hash)
    out["model_target"] = mm
    out["model_payload_source"] = msrc
    if not mm["class_matches"] or mb is None:
        out["violations"].append("model_missing_class_or_payload")
        return out
    if out["violations"]:
        return out
    try:
        model = parse_model(mb, "PS4")
    except Exception as ex:
        out["violations"].append("model_parse:" + repr(ex))
        return out
    maps = parent["external_material_map"]
    mats = parent["external_materials"]
    for mi, mesh in enumerate(model["meshes"]):
        mr = {"mesh_index": mi, "parts": []}
        for pi, part in enumerate(mesh["parts"]):
            variant = int(part["variant_shader_index"])
            direct = norm(part["material"])
            row = {
                "part_index": pi,
                "variant_shader_index": variant,
                "inline_material": direct,
                "lod": part.get("lod"),
                "index_offset": part.get("index_offset"),
                "index_count": part.get("index_count"),
                "primitive_type": part.get("primitive_type"),
                "violations": [],
            }
            if variant == -1:
                row["selection"] = "inline_material"
                _classify_selected_material(
                    row,
                    meta(c, direct, MATERIAL_CLASS),
                    "inline_material_missing_or_class_mismatch",
                )
            else:
                row["selection"] = "external_material_first_in_mapped_range"
                if variant < 0 or variant >= len(maps):
                    row["violations"].append("variant_shader_index_oob")
                else:
                    me = maps[variant]
                    row["external_map_entry"] = me
                    count = me["material_count"]
                    start = me["material_start_index"]
                    if count <= 0:
                        row["violations"].append("external_material_count_not_positive")
                    else:
                        idx = start + (0 % count)
                        row["selected_external_material_index"] = idx
                        if idx < 0 or idx >= len(mats):
                            row["violations"].append("selected_external_material_index_oob")
                        else:
                            _classify_selected_material(
                                row,
                                mats[idx],
                                "external_material_missing_or_class_mismatch",
                            )
            if row["violations"]:
                out["violations"].extend(f"mesh[{mi}].part[{pi}]:{x}" for x in row["violations"])
            mr["parts"].append(row)
        out["meshes"].append(mr)
    parts = [p for m in out["meshes"] for p in m["parts"]]
    out["part_count"] = len(parts)
    out["external_variant_part_count"] = sum(p["variant_shader_index"] != -1 for p in parts)
    out["explicit_null_material_part_count"] = sum(
        p.get("selection_status") == "EXPLICIT_NULL_MATERIAL" for p in parts
    )
    out["renderable_material_part_count"] = sum(p.get("renderable") is True for p in parts)
    out["validation_ok"] = not out["violations"]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", type=Path, action="append", required=True)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--articulated-plan", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    plan = json.loads(a.articulated_plan.read_text())
    c = v5.v3.base.Corpus([x.resolve() for x in a.snapshot], a.runtime.resolve())
    pairs = []
    for ent in plan.get("candidates", []):
        models = [norm(x) for x in ent.get("models", [])]
        parents = [norm(x) for x in ent.get("model_parent_resources", [])]
        if len(models) == 1 and len(parents) == 1:
            pairs.append((models[0], parents[0], ent["entity"]))
        else:
            # Preserve ambiguity rather than cross-product guessing. A model-parent ownership pair must be exact.
            for m in models:
                matches = []
                for p in parents:
                    pb, _ = c.payload(p)
                    if pb is None:
                        continue
                    try:
                        pr = parse_resource(pb, "PS4")
                    except Exception:
                        continue
                    if norm(pr.get("embedded_model_tag_hash", "FFFFFFFF")) == m:
                        matches.append(p)
                if len(matches) == 1:
                    pairs.append((m, matches[0], ent["entity"]))
                else:
                    pairs.append((m, None, ent["entity"]))
    grouped = {}
    pair_owners = Counter()
    viol = []
    for m, p, e in pairs:
        key = (m, p)
        pair_owners[key] += 1
        if key in grouped:
            continue
        if p is None:
            r = {
                "model": m,
                "parent_resource": None,
                "violations": ["model_parent_ownership_not_unique"],
                "validation_ok": False,
            }
        else:
            r = bind_model(c, m, p)
        grouped[key] = r
        viol.extend(f"{m}/{p}:{x}" for x in r.get("violations", []))
    rows = []
    for key, r in grouped.items():
        r["owning_entity_count"] = pair_owners[key]
        rows.append(r)
    selected = Counter()
    for r in rows:
        for m in r.get("meshes", []):
            for p in m["parts"]:
                sm = p.get("selected_material") or {}
                h = norm(sm.get("hash")) if sm.get("hash") else None
                if h and h not in NULLS:
                    selected[h] += 1
    out = {
        "schema_version": 2,
        "status": "D1_WORLD_ENTITY_MODEL_MATERIAL_BINDINGS_COMPLETE" if not viol else "D1_WORLD_ENTITY_MODEL_MATERIAL_BINDINGS_PARTIAL",
        "pinned_source": PINNED_SOURCE,
        "null_material_source_rule": NULL_MATERIAL_SOURCE_RULE,
        "model_parent_pair_count": len(rows),
        "validated_pair_count": sum(r.get("validation_ok", False) for r in rows),
        "part_count": sum(r.get("part_count", 0) for r in rows),
        "external_variant_part_count": sum(r.get("external_variant_part_count", 0) for r in rows),
        "explicit_null_material_part_count": sum(r.get("explicit_null_material_part_count", 0) for r in rows),
        "renderable_material_part_count": sum(r.get("renderable_material_part_count", 0) for r in rows),
        "unique_selected_material_count": len(selected),
        "selected_material_reference_counts": dict(selected),
        "bindings": rows,
        "violations": viol,
        "policy": (
            "External variant materials are selected only through the exact SEntity-owned model-parent EntityResource "
            "using Charm D1 map/range semantics. Source-proven null Material sentinels are retained as non-renderable "
            "parts and are not material dependencies. Any non-null missing/wrong-class material remains a hard failure. "
            "No package adjacency or material similarity is used."
        ),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + "\n")
    print(
        json.dumps(
            {
                k: out[k]
                for k in (
                    "status",
                    "model_parent_pair_count",
                    "validated_pair_count",
                    "part_count",
                    "external_variant_part_count",
                    "explicit_null_material_part_count",
                    "renderable_material_part_count",
                    "unique_selected_material_count",
                    "violations",
                )
            },
            indent=2,
        )
    )
    return 0 if not viol else 2


if __name__ == "__main__":
    raise SystemExit(main())
