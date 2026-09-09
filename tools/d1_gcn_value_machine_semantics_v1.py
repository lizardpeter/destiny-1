#!/usr/bin/env python3
"""Source-backed GFX7 result-value operation surface for the exact Destiny 1 shader corpus.

This layer closes *machine value provenance*, not high-level shader meaning.  Every
observed physical VGPR/SGPR/M0 or architectural mask result is assigned an ISA
operation family and retains the exact opcode/operand identity required by a later
expression DAG.  Mathematical normalization, resource roles, material intent and
backend expressions remain withheld.
"""
from __future__ import annotations

import json

import d1_condition_machine_semantics_v1 as cond
import d1_gcn_exec_mask_semantics_v1 as exec_sem
import d1_gcn_sgpr_machine_semantics_v1 as sgpr
import d1_gcn_vgpr_machine_semantics_v1 as vgpr

SCHEMA = "d1_gcn_value_machine_semantics/v1"
STATUS = "D1_GCN_VALUE_MACHINE_SEMANTICS_SOURCE_CLOSED"
AMD = {
    "vendor": "Advanced Micro Devices, Inc.",
    "title": "AMD Sea Islands Series Instruction Set Architecture",
    "document_id": "70653",
    "revision": "1.3",
    "release_date": "2013-12-01",
    "architecture": "GCN 2 / GFX7 / Sea Islands",
    "official_url": "https://docs.amd.com/v/u/en-US/sea-islands-instruction-set-architecture_0",
}

IMAGE = {
    "image_gather4_lz", "image_gather4_lz_o", "image_get_lod", "image_get_resinfo",
    "image_load_mip", "image_sample", "image_sample_d", "image_sample_l",
    "image_sample_lz", "image_sample_lz_o",
}
VECTOR_MEMORY = {
    "buffer_load_dword", "tbuffer_load_format_xyz", "tbuffer_load_format_xyzw",
}
LDS_VALUE = {"ds_read2_b32", "ds_read_b32", "ds_swizzle_b32"}
INTERPOLATION = {"v_interp_mov_f32", "v_interp_p1_f32", "v_interp_p2_f32"}
CONVERSION = {op for op in vgpr.VGPR_DEF_OPCODES if op.startswith("v_cvt_")}
LANE_TRANSFER = {"v_readfirstlane_b32", "v_readlane_b32", "v_writelane_b32", "v_movrels_b32"}
SCALAR_MEMORY = {
    "s_buffer_load_dword", "s_buffer_load_dwordx2", "s_buffer_load_dwordx4",
    "s_load_dwordx4", "s_load_dwordx8",
}
SCALAR_CONTROL_VALUE = {"s_swappc_b64"}
MASK_ALU = set(cond.SCALAR_MASK)
COMPARE_MASK = set(cond.COMPARES)
CARRY_VALUE = set(cond.CARRY)

# The exact value-producing surface is inherited from already-frozen destination
# frontiers, plus architectural mask producers whose destination can be a special
# register rather than a physical SGPR.
VALUE_PRODUCER_OPCODES = (
    set(vgpr.VGPR_DEF_OPCODES)
    | set(sgpr.OBSERVED_SGPR_DEF_OPCODES)
    | COMPARE_MASK
    | MASK_ALU
)


def source(locator: str) -> dict:
    return {**AMD, "locator": locator}


def family(op: str) -> str:
    if op not in VALUE_PRODUCER_OPCODES:
        raise KeyError(op)
    if op in COMPARE_MASK:
        return "VECTOR_COMPARE_MASK"
    if op in MASK_ALU:
        return "SCALAR_MASK_ALU"
    if op in IMAGE:
        return "IMAGE_VALUE"
    if op in INTERPOLATION:
        return "INTERPOLATED_VALUE"
    if op in LDS_VALUE:
        return "LDS_OR_PERMUTE_VALUE"
    if op in VECTOR_MEMORY:
        return "VECTOR_MEMORY_LOAD"
    if op in SCALAR_MEMORY:
        return "SCALAR_MEMORY_LOAD"
    if op in CONVERSION:
        return "VECTOR_CONVERSION"
    if op in LANE_TRANSFER:
        return "LANE_TRANSFER_OR_INDEXED_VALUE"
    if op in SCALAR_CONTROL_VALUE:
        return "SCALAR_CONTROL_RETURN_VALUE"
    if op in CARRY_VALUE:
        return "VECTOR_INTEGER_ARITHMETIC_WITH_CARRY"
    if op in sgpr.OBSERVED_SGPR_DEF_OPCODES:
        return "SCALAR_ISA_RESULT"
    if op in vgpr.VGPR_DEF_OPCODES:
        return "VECTOR_ISA_RESULT"
    raise AssertionError(op)


def result_form(op: str) -> str:
    f = family(op)
    if f == "VECTOR_COMPARE_MASK":
        return "LANE_MASK_PREDICATE"
    if f == "SCALAR_MASK_ALU":
        return "64_BIT_MASK_VALUE"
    if f == "IMAGE_VALUE":
        return "IMAGE_INSTRUCTION_RESULT"
    if f in {"VECTOR_MEMORY_LOAD", "SCALAR_MEMORY_LOAD"}:
        return "MEMORY_LOAD_RESULT"
    if f == "INTERPOLATED_VALUE":
        return "INTERPOLATOR_MACHINE_RESULT"
    if f == "LDS_OR_PERMUTE_VALUE":
        return "LDS_OR_LANE_PERMUTE_MACHINE_RESULT"
    if f == "VECTOR_CONVERSION":
        return "CONVERTED_NUMERIC_RESULT"
    if f == "LANE_TRANSFER_OR_INDEXED_VALUE":
        return "LANE_OR_INDEXED_REGISTER_RESULT"
    if f == "SCALAR_CONTROL_RETURN_VALUE":
        return "CONTROL_RETURN_PC_VALUE"
    return "ISA_OPCODE_RESULT"


def behavior(op: str) -> dict:
    f = family(op)
    locator = "Ch. 12 instruction descriptions and Ch. 13 encoding tables: " + op.upper()
    if op in IMAGE:
        locator = "Ch. 10 image instructions; Ch. 12 " + op.upper()
    elif op in INTERPOLATION:
        locator = "Ch. 8 parameter interpolation; Ch. 12 " + op.upper()
    elif op in LDS_VALUE:
        locator = "Ch. 9 data-share instructions; Ch. 12 " + op.upper()
    elif op in VECTOR_MEMORY or op in SCALAR_MEMORY:
        locator = "Memory instruction descriptions; Ch. 12 " + op.upper()
    elif op in COMPARE_MASK:
        locator = "Ch. 6 vector compare behavior; Ch. 12 " + op.upper()
    elif op in MASK_ALU:
        locator = "Ch. 12 " + op.upper()
    return {
        "architectural_status": "SOURCE_CLOSED_OPERATION_IDENTITY",
        "operation_family": f,
        "result_form": result_form(op),
        "operand_provenance": "EXACT_ORDERED_NATIVE_OPERANDS",
        "ssa_binding": "DEFER_TO_FROZEN_VGPR_SGPR_CONDITION_EXEC_LAYERS",
        "expression_lowering": "WITHHELD",
        "resource_role_semantics": "WITHHELD",
        "material_semantics": "WITHHELD",
        "source": source(locator),
    }


def document() -> dict:
    fam = {}
    for op in sorted(VALUE_PRODUCER_OPCODES):
        fam.setdefault(family(op), []).append(op)
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "source": AMD,
        "value_producer_opcode_count": len(VALUE_PRODUCER_OPCODES),
        "frozen_prerequisites": {
            "vgpr_def_opcode_count": len(vgpr.VGPR_DEF_OPCODES),
            "sgpr_def_opcode_count": len(sgpr.OBSERVED_SGPR_DEF_OPCODES),
            "condition_compare_opcode_count": len(cond.COMPARES),
            "scalar_mask_opcode_count": len(cond.SCALAR_MASK),
        },
        "operation_families": {k: v for k, v in sorted(fam.items())},
        "opcode_behaviors": {op: behavior(op) for op in sorted(VALUE_PRODUCER_OPCODES)},
        "shader_expression_semantic_promotions": 0,
        "policy": (
            "SOURCE_CLOSED_OPERATION_IDENTITY means the native GFX7 operation producing each machine value is known, "
            "its exact ordered operands are preserved, and its result category is architectural. It does not yet permit "
            "algebraic expression lowering, resource-role inference, material-role inference, or game-semantic promotion."
        ),
    }


def validate() -> list[str]:
    bad = []
    expected = set(vgpr.VGPR_DEF_OPCODES) | set(sgpr.OBSERVED_SGPR_DEF_OPCODES) | set(cond.COMPARES) | set(cond.SCALAR_MASK)
    if VALUE_PRODUCER_OPCODES != expected:
        bad.append("producer_surface_mismatch")
    for op in sorted(VALUE_PRODUCER_OPCODES):
        try:
            b = behavior(op)
        except Exception as e:
            bad.append(f"unclassified:{op}:{type(e).__name__}:{e}")
            continue
        if b["architectural_status"] != "SOURCE_CLOSED_OPERATION_IDENTITY":
            bad.append(f"status:{op}")
        if not b["source"].get("locator"):
            bad.append(f"source:{op}")
    # Keep all high-level promotion gates hard-zero at this layer.
    if document()["shader_expression_semantic_promotions"] != 0:
        bad.append("unexpected_expression_promotion")
    return bad


if __name__ == "__main__":
    problems = validate()
    print(json.dumps(document() if not problems else {"status": "INVALID", "violations": problems}, indent=2, sort_keys=True))
    raise SystemExit(0 if not problems else 2)
