#!/usr/bin/env python3
"""Source-backed architectural value semantics for non-formula GFX7 vector results.

This registry closes only three machine-value families that remain outside the 50-opcode
formula registry and are present in the exact Destiny LocalShader corpus:
  * V_ADD_I32: low 32-bit unsigned sum plus a separate carry-mask side effect;
  * V_CNDMASK_B32: source selection by a VCC/SGPR-pair lane mask;
  * TBUFFER_LOAD_FORMAT_XYZW: four-component typed-buffer result with exact encoded
    address/resource/format inputs, while fetched memory contents remain opaque.

It is architecture-level provenance, not shader/material interpretation.
"""
from __future__ import annotations
import json

SCHEMA = "d1_gcn_vector_special_value_semantics/v1"
STATUS = "D1_GCN_VECTOR_SPECIAL_VALUE_SEMANTICS_SOURCE_CLOSED"
AMD = {
    "vendor": "Advanced Micro Devices, Inc.",
    "title": "AMD Sea Islands Series Instruction Set Architecture",
    "document_id": "70653",
    "revision": "1.3",
    "release_date": "2013-12-01",
    "architecture": "GCN 2 / GFX7 / Sea Islands",
    "official_url": "https://docs.amd.com/v/u/en-US/sea-islands-instruction-set-architecture_0",
}

SEMANTICS = {
    "v_add_i32": {
        "category": "VALU_CARRY_COUPLED_VALUE",
        "result_components": 1,
        "value_operation": "LOW32_UNSIGNED_ADD",
        "value_formula": "D.u = (S0.u + S1.u) mod 2^32",
        "side_effect": "UNSIGNED_CARRY_OUT_TO_MASK_DESTINATION",
        "value_numeric_status": "BIT_EXACT",
        "source": {**AMD, "locator": "V_ADD_I32 instruction table; Ch. 12 VOP2/VOP3b"},
    },
    "v_cndmask_b32": {
        "category": "PREDICATE_SELECT_VALUE",
        "result_components": 1,
        "value_operation": "LANE_MASK_SELECT_B32",
        "value_formula": "D = predicate_bit ? S1 : S0",
        "predicate": "VCC for VOP2; scalar GPR pair/VCC for VOP3",
        "source_modifier_status": "PRESERVE_ENCODED_VOP3_SOURCE_MODIFIERS",
        "value_numeric_status": "SYMBOLIC_WHEN_SOURCE_MODIFIER_PRESENT",
        "source": {**AMD, "locator": "V_CNDMASK_B32 instruction table; Ch. 12 VOP2/VOP3"},
    },
    "tbuffer_load_format_xyzw": {
        "category": "BUFFER_RESOURCE_VALUE_OPAQUE",
        "result_components": 4,
        "value_operation": "TYPED_BUFFER_LOAD_4_DWORDS_WITH_FORMAT_CONVERSION",
        "architectural_inputs": ["VADDR", "SRSRC_128", "SOFFSET", "IDXEN", "OFFEN", "OFFSET12", "DFMT", "NFMT"],
        "result_value_status": "OPAQUE_UNTIL_RESOURCE_DESCRIPTOR_AND_BACKING_MEMORY_PROVEN",
        "source": {**AMD, "locator": "MTBUF / TBUFFER_LOAD_FORMAT_XYZW; typed-buffer format and addressing fields"},
    },
}


def behavior(op: str) -> dict:
    return SEMANTICS[op]


def validate() -> list[str]:
    bad = []
    if set(SEMANTICS) != {"v_add_i32", "v_cndmask_b32", "tbuffer_load_format_xyzw"}:
        bad.append(f"surface:{sorted(SEMANTICS)}")
    if SEMANTICS["v_add_i32"]["result_components"] != 1:
        bad.append("v_add_i32_width")
    if SEMANTICS["v_cndmask_b32"]["result_components"] != 1:
        bad.append("v_cndmask_b32_width")
    if SEMANTICS["tbuffer_load_format_xyzw"]["result_components"] != 4:
        bad.append("tbuffer_xyzw_width")
    return bad


def document() -> dict:
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "source": AMD,
        "opcode_count": len(SEMANTICS),
        "opcodes": {k: SEMANTICS[k] for k in sorted(SEMANTICS)},
        "shader_expression_semantic_promotions": 0,
        "policy": (
            "Only source-documented architectural value identities are admitted. Carry and predicate "
            "state reuse the existing condition-mask graph. Typed-buffer result contents remain opaque "
            "until descriptor, address and backing-memory provenance are closed."
        ),
    }


if __name__ == "__main__":
    bad = validate()
    print(json.dumps(document() if not bad else {"status": "INVALID", "violations": bad}, indent=2, sort_keys=True))
    raise SystemExit(0 if not bad else 2)
