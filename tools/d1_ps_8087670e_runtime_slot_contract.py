#!/usr/bin/env python3
"""Fail-closed runtime-slot contract for D1 PS4 pixel shader 8087670E.

Joins five independently retained proof products:
  * full retail peer-material census for exact PS 8087670E;
  * exact spilled API15 descriptor/index proof;
  * exact API15 surviving-component/dataflow proof;
  * exact Bungie WebGL semantic-position correlation;
  * exact current t5 retail texture decode.

The output deliberately DOES NOT invent either unresolved runtime input.
It closes the stronger family-wide statement that t4 is never serialized by any
of the 10/10 observed retail materials using this exact PS, despite native GCN
sampling t4. Therefore an exact renderer requires a non-material resource-table
producer/default binding for t4. API15 similarly remains runtime-provided; the
current material state selects c0 and only c0.w survives into the proven factor.

This tool is an evidence join, not a runtime capture.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

PS = "8087670E"
GCN = "c3751c74f6cc13660cf4acf6c5372f6a178f64bfe29c5b55ef5b5f694a3d98bc"
TARGET_MATS = {"808766B2", "808766B6"}


def load(p: Path) -> dict:
    return json.loads(p.read_text())


def norm(x: object) -> str:
    return str(x).upper().removeprefix("0X").zfill(8)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--peer-census", type=Path, required=True)
    ap.add_argument("--api15-binding", type=Path, required=True)
    ap.add_argument("--blend-factor", type=Path, required=True)
    ap.add_argument("--bungie-correlation", type=Path, required=True)
    ap.add_argument("--t5-proof", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    peer = load(a.peer_census)
    api15 = load(a.api15_binding)
    blend = load(a.blend_factor)
    bungie = load(a.bungie_correlation)
    t5 = load(a.t5_proof)
    v: list[str] = []

    if peer.get("status") != "D1_PS_8087670E_PEER_MATERIAL_CENSUS_EXACT":
        v.append("peer_census_not_exact")
    if int(peer.get("unique_material_count", -1)) != 10:
        v.append(f"peer_unique_material_count:{peer.get('unique_material_count')}")
    if int(peer.get("physical_occurrence_count", -1)) != 70:
        v.append(f"peer_physical_occurrence_count:{peer.get('physical_occurrence_count')}")
    if int(peer.get("t4_serialized_occurrence_count", -1)) != 0:
        v.append(f"t4_serialized_occurrence_count:{peer.get('t4_serialized_occurrence_count')}")
    if int(peer.get("t4_absent_occurrence_count", -1)) != 70:
        v.append(f"t4_absent_occurrence_count:{peer.get('t4_absent_occurrence_count')}")

    unique = {norm(x) for x in peer.get("unique_materials", [])}
    if len(unique) != 10:
        v.append(f"peer_material_identity_count:{len(unique)}")
    tex_maps = peer.get("per_material_texture_maps") or {}
    if set(tex_maps) != unique:
        v.append("peer_texture_map_material_set_mismatch")
    observed_t5 = set()
    for mh in sorted(unique):
        variants = tex_maps.get(mh) or []
        if not variants:
            v.append(f"{mh}:no_texture_map")
            continue
        for variant in variants:
            slots = {int(x[0]): norm(x[1]) for x in variant}
            if set(slots) != {0, 1, 2, 3, 5}:
                v.append(f"{mh}:serialized_slot_set:{sorted(slots)}")
            if 4 in slots:
                v.append(f"{mh}:unexpected_serialized_t4")
            if 5 in slots:
                observed_t5.add(slots[5])

    if api15.get("status") != "D1_TOWER_PS_8087670E_API15_BINDING_EXACT" or api15.get("violations"):
        v.append("api15_binding_not_exact")
    if api15.get("shader") != PS or set(api15.get("scope_materials", [])) != TARGET_MATS:
        v.append("api15_binding_scope_drift")
    al = api15.get("api15_load") or {}
    if int(al.get("current_api15_vec4_index", -1)) != 0 or int(al.get("current_api15_byte_offset", -1)) != 0:
        v.append("api15_current_selector_drift")

    if blend.get("status") != "D1_TOWER_PS_8087670E_BLEND_FACTOR_EXACT" or blend.get("violations"):
        v.append("blend_factor_not_exact")
    if blend.get("shader") != PS or blend.get("gcn_sha256") != GCN:
        v.append("blend_factor_identity_drift")
    red = blend.get("api15_reduction") or {}
    if red.get("selected_vector") != "c0" or red.get("surviving_component") != "w":
        v.append("api15_surviving_component_drift")
    if red.get("blend_factor") != "f = -API15.c0.w":
        v.append("api15_factor_equation_drift")

    if bungie.get("status") != "D1_PS_8087670E_BUNGIE_WEBGL_CORRELATION_EXACT" or bungie.get("violations"):
        v.append("bungie_correlation_not_exact")
    if bungie.get("native_shader") != PS or bungie.get("native_gcn_sha256") != GCN:
        v.append("bungie_correlation_identity_drift")
    bg = bungie.get("gates") or {}
    if bg.get("t0_base_diffuse_semantic_correlated") is not True:
        v.append("t0_semantic_correlation_not_closed")
    if bg.get("t3_r_change_color_mask_semantic_correlated") is not True:
        v.append("t3_semantic_correlation_not_closed")
    if bg.get("runtime_t4_binding_closed") is not False or bg.get("api15_c0_w_runtime_value_closed") is not False:
        v.append("bungie_correlation_unexpected_runtime_promotion")

    if t5.get("status") != "D1_PS_8087670E_T5_80AB04C7_TEXTURE_CHAIN_EXACT":
        v.append("t5_proof_not_exact")
    if norm(t5.get("root")) != "80AB04C7":
        v.append("t5_root_identity_drift")
    if t5.get("uniform_rgba") != [127, 127, 0, 255]:
        v.append(f"t5_uniform_rgba_drift:{t5.get('uniform_rgba')}")
    if int(t5.get("unique_rgba_count", -1)) != 1:
        v.append("t5_not_uniform")
    if "80AB04C7" not in observed_t5:
        v.append("current_t5_not_present_in_peer_census")

    exact = not v
    out = {
        "schema": "d1_ps_8087670e_runtime_slot_contract/v1",
        "status": "D1_PS_8087670E_RUNTIME_SLOT_FRONTIER_EXACT" if exact else "D1_PS_8087670E_RUNTIME_SLOT_FRONTIER_VIOLATIONS",
        "shader": PS,
        "gcn_sha256": GCN,
        "retail_peer_denominator": {
            "unique_material_count": len(unique),
            "physical_occurrence_count": int(peer.get("physical_occurrence_count", -1)),
            "serialized_texture_slot_set": [0, 1, 2, 3, 5] if exact else None,
            "t4_serialized_occurrence_count": int(peer.get("t4_serialized_occurrence_count", -1)),
            "t4_absent_occurrence_count": int(peer.get("t4_absent_occurrence_count", -1)),
            "observed_t5_resource_versions": sorted(observed_t5),
        },
        "t4_frontier": {
            "native_shader_samples_t4": True,
            "material_serialization_absent_across_all_observed_peers": exact,
            "classification": "NON_MATERIAL_RESOURCE_TABLE_BINDING_REQUIRED" if exact else "UNRESOLVED",
            "resource_identity": None,
            "descriptor_dwords": None,
            "backing_bytes": None,
            "runtime_or_default_producer": None,
        },
        "api15_frontier": {
            "descriptor_binding_closed": exact,
            "selected_vec4_index": 0 if exact else None,
            "selected_byte_offset": 0 if exact else None,
            "surviving_component": "c0.w" if exact else None,
            "factor_equation": "f = -API15.c0.w" if exact else None,
            "c0_runtime_value": None,
            "runtime_producer": None,
            "backing_bytes": None,
        },
        "closed_semantic_positions": {
            "t0": "base_diffuse_algebra_position",
            "t3_r": "change_color_mask_lerp_position",
            "t5_current_80AB04C7": {
                "exact_resource": True,
                "dimensions": [4, 4],
                "format": "RGBA8",
                "uniform_rgba": [127, 127, 0, 255],
                "high_level_role": "WITHHELD_BEYOND_NATIVE_T5_ARITHMETIC",
            },
        } if exact else None,
        "final_five_tower_primitives": {
            "materials": sorted(TARGET_MATS),
            "remaining_runtime_inputs": [
                "t4 exact resource-table descriptor/resource/backing identity",
                "API15 c0.w exact runtime value and producer/backing identity",
            ],
            "native_color_dataflow_complete": False,
            "portable_retail_correct_recreation_complete": False,
        },
        "gates": {
            "t4_material_absence_family_wide_closed": exact,
            "t4_runtime_binding_closed": False,
            "api15_descriptor_and_selector_closed": exact,
            "api15_c0_w_dataflow_closed": exact,
            "api15_c0_w_runtime_value_closed": False,
            "final_shader_color_closed": False,
        },
        "violations": v,
        "policy": (
            "Absence is promoted only at the material-serialization layer: 0/70 exact retail occurrences serialize t4. "
            "Because native GCN samples t4, exact rendering requires another resource-table producer. No default texture, "
            "descriptor, API15 value, engine name, or WebGL-to-PS4 binding identity is invented."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0 if exact else 2


if __name__ == "__main__":
    raise SystemExit(main())
