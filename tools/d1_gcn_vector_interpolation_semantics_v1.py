#!/usr/bin/env python3
"""Source-backed Sea Islands VINTRP semantics for the exact Destiny 1 shader corpus.

This registry closes architectural operation identity only.  P0/P10/P20 remain values read from
pixel-shader parameter storage in LDS, selected by ATTR/CHAN and the automatic M0 parameter-state
input.  Floating numeric replay and shader varying/material meaning are deliberately withheld.
"""
from __future__ import annotations
import json

SCHEMA = "d1_gcn_vector_interpolation_semantics/v1"
STATUS = "D1_GCN_VECTOR_INTERPOLATION_SEMANTICS_SOURCE_CLOSED"
AMD = {
    "vendor": "Advanced Micro Devices, Inc.",
    "title": "Sea Islands Series Instruction Set Architecture",
    "document_id": "70653",
    "revision": "1.3",
    "release_date": "2013-12-01",
    "architecture": "GCN 2 / GFX7 / Sea Islands",
    "official_url": "https://docs.amd.com/v/u/en-US/sea-islands-instruction-set-architecture_0",
}


def src(locator: str, pdf_pages: str) -> dict:
    return {**AMD, "locator": locator, "pdf_pages": pdf_pages}


OPS = {
    "v_interp_p1_f32": {
        "formula": "D = P10(ATTR,CHAN,M0) * S + P0(ATTR,CHAN,M0)",
        "explicit_vgpr_source_count": 1,
        "old_destination_is_arithmetic_input": False,
        "parameter_coefficients": ["P10", "P0"],
        "selector_operand": None,
        "source": src("10.3.2 LDS Parameter Reads; 12.12 VINTRP V_INTERP_P1_F32", "10-4..10-5, 12-140"),
    },
    "v_interp_p2_f32": {
        "formula": "D = P20(ATTR,CHAN,M0) * S + OLD_D",
        "explicit_vgpr_source_count": 1,
        "old_destination_is_arithmetic_input": True,
        "parameter_coefficients": ["P20"],
        "selector_operand": None,
        "source": src("10.3.2 LDS Parameter Reads; 12.12 VINTRP V_INTERP_P2_F32", "10-4..10-5, 12-140"),
    },
    "v_interp_mov_f32": {
        "formula": "D = selected_parameter(ATTR,CHAN,M0,SELECTOR)",
        "explicit_vgpr_source_count": 0,
        "old_destination_is_arithmetic_input": False,
        "parameter_coefficients": [],
        "selector_operand": "P0_P10_P20_SELECTOR",
        "source": src("10.3.2 LDS Parameter Reads; 12.12 VINTRP V_INTERP_MOV_F32", "10-4..10-5, 12-140"),
    },
}

PARAMETER_STATE = {
    "status": "SOURCE_CLOSED_IDENTITY_VALUE_OPAQUE",
    "rule": "P0, P10, and P20 are parameter values read from LDS for ATTR/CHAN; use of M0 is automatic.",
    "m0_layout": "{0, new_prim_mask[15:1], lds_param_offset[15:0]}",
    "attribute_range": [0, 32],
    "channels": {"x": 0, "y": 1, "z": 2, "w": 3},
    "source": src("10.3.2 Table 10.1 Parameter Instruction Fields", "10-5"),
}


def validate() -> list[str]:
    bad=[]
    expected={"v_interp_p1_f32","v_interp_p2_f32","v_interp_mov_f32"}
    if set(OPS)!=expected: bad.append(f"opcode_surface:{sorted(OPS)}")
    if OPS["v_interp_p1_f32"]["parameter_coefficients"] != ["P10","P0"]: bad.append("p1_parameters")
    if OPS["v_interp_p2_f32"]["parameter_coefficients"] != ["P20"]: bad.append("p2_parameters")
    if not OPS["v_interp_p2_f32"]["old_destination_is_arithmetic_input"]: bad.append("p2_old_dest")
    if PARAMETER_STATE["channels"] != {"x":0,"y":1,"z":2,"w":3}: bad.append("channels")
    return bad


def document() -> dict:
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "source": AMD,
        "opcode_count": len(OPS),
        "opcodes": OPS,
        "parameter_state": PARAMETER_STATE,
        "numeric_replay": "WITHHELD_PARAMETER_VALUES_AND_HARDWARE_FP_BEHAVIOR",
        "shader_varying_semantics": "WITHHELD",
        "material_semantics": "WITHHELD",
        "shader_expression_semantic_promotions": 0,
        "policy": (
            "VINTRP formulas, ATTR/CHAN identity, P0/P10/P20 parameter roles and automatic M0 dependency are "
            "source-closed. Parameter contents and floating numeric evaluation remain architectural boundaries; "
            "no semantic varying name or material role is inferred."
        ),
    }

if __name__ == "__main__":
    bad=validate()
    print(json.dumps(document() if not bad else {"status":"INVALID","violations":bad},indent=2,sort_keys=True))
    raise SystemExit(0 if not bad else 2)
