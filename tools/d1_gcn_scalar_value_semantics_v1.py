#!/usr/bin/env python3
"""Source-backed architectural value classification for the exact D1 GFX7 SGPR-def surface.

This registry distinguishes machine-level result value identity from shader-expression meaning.
All observed non-memory SGPR-defining opcode families are source-documented here. Scalar-memory
loads remain explicit opaque memory-result boundaries until descriptor/address semantics close.
"""
from __future__ import annotations
import json

SCHEMA = "d1_gcn_scalar_value_semantics/v1"
STATUS = "D1_GCN_SCALAR_VALUE_SEMANTICS_SOURCE_CLOSED"
AMD = {
    "vendor": "Advanced Micro Devices, Inc.",
    "title": "AMD Sea Islands Series Instruction Set Architecture",
    "document_id": "70653",
    "revision": "1.3",
    "release_date": "2013-12-01",
    "architecture": "GCN 2 / GFX7 / Sea Islands",
    "official_url": "https://docs.amd.com/v/u/en-US/sea-islands-instruction-set-architecture_0",
}

PURE_SCALAR = {
    "s_addk_i32": ("I32_ADD_SIGNEXT_IMM16", 32, "12.2 SOPK, p.12-13 / PDF p.110: D.i = D.i + signext(SIMM16)"),
    "s_and_b32": ("BIT_AND", 32, "12.1 SOP2, PDF p.99: D.u = S0.u & S1.u"),
    "s_and_b64": ("BIT_AND", 64, "12.1 SOP2, PDF p.100: D.u = S0.u & S1.u"),
    "s_andn2_b64": ("BIT_AND_NOT_SECOND", 64, "12.1 SOP2, PDF p.100: D.u = S0.u & ~S1.u"),
    "s_lshl_b32": ("LOGICAL_SHIFT_LEFT_MASK5", 32, "12.1 SOP2, PDF p.104: D.u = S0.u << S1.u[4:0]"),
    "s_mov_b32": ("COPY_BITS", 32, "12.3 SOP1, PDF p.122: D.u = S0.u"),
    "s_mov_b64": ("COPY_BITS", 64, "12.3 SOP1, PDF p.122: D.u = S0.u"),
    "s_movk_i32": ("SIGNEXT_IMM16", 32, "12.2 SOPK, PDF p.114: D.i = signext(SIMM16)"),
    "s_or_b64": ("BIT_OR", 64, "12.1 SOP2, PDF p.107: D.u = S0.u | S1.u"),
    "s_xor_b64": ("BIT_XOR", 64, "12.1 SOP2, PDF p.109: D.u = S0.u ^ S1.u"),
}

CROSS_STATE = {
    "s_and_saveexec_b64": (
        "OLD_EXEC_SNAPSHOT", 64,
        "12.3 SOP1, PDF p.116: D.u = EXEC; EXEC = S0.u & EXEC; SCC follows new EXEC",
    ),
    "s_swappc_b64": (
        "NEXT_PC_BYTE_ADDRESS", 64,
        "12.3 SOP1, PDF p.126: D.u = PC + 4; PC = S0.u",
    ),
    "v_readlane_b32": (
        "SELECTED_VGPR_LANE", 32,
        "12.7 VOP2, PDF p.166: VGPR lane -> SGPR; lane selector SGPR/M0; ignores EXEC mask",
    ),
    "v_readfirstlane_b32": (
        "FIRST_ACTIVE_EXEC_VGPR_LANE", 32,
        "12.8 VOP1, PDF p.199: lane = first set EXEC bit, lane 0 if EXEC=0; ignores EXEC mask",
    ),
}

COMPARE_MASK_DEST = {
    "v_cmp_class_f32", "v_cmp_eq_f32", "v_cmp_ge_f32", "v_cmp_gt_f32",
    "v_cmp_le_f32", "v_cmp_lg_i32", "v_cmp_lt_f32", "v_cmp_lt_i32",
    "v_cmp_neq_f32", "v_cmp_ngt_f32", "v_cmpx_eq_i32", "v_cmpx_lt_u32",
}

MEMORY_OPAQUE = {
    "s_buffer_load_dword", "s_buffer_load_dwordx2", "s_buffer_load_dwordx4",
    "s_load_dwordx4", "s_load_dwordx8",
}

OBSERVED = set(PURE_SCALAR) | set(CROSS_STATE) | COMPARE_MASK_DEST | MEMORY_OPAQUE


def source(locator: str) -> dict:
    return {**AMD, "locator": locator}


def behavior(op: str) -> dict:
    if op in PURE_SCALAR:
        kind, width, locator = PURE_SCALAR[op]
        return {
            "category": "PURE_SCALAR_TRANSFORM",
            "architectural_value_status": "SOURCE_DOCUMENTED",
            "value_kind": kind,
            "width_bits": width,
            "cross_state_inputs": [],
            "memory_value_status": "NOT_MEMORY",
            "source": source(locator),
        }
    if op in CROSS_STATE:
        kind, width, locator = CROSS_STATE[op]
        cross = {
            "s_and_saveexec_b64": ["EXEC_IN"],
            "s_swappc_b64": ["PC_IN"],
            "v_readlane_b32": ["VGPR_STATE", "LANE_SELECTOR"],
            "v_readfirstlane_b32": ["VGPR_STATE", "EXEC_IN_AS_LANE_SELECTOR"],
        }[op]
        return {
            "category": "CROSS_STATE_IDENTITY",
            "architectural_value_status": "SOURCE_DOCUMENTED",
            "value_kind": kind,
            "width_bits": width,
            "cross_state_inputs": cross,
            "memory_value_status": "NOT_MEMORY",
            "source": source(locator),
        }
    if op in COMPARE_MASK_DEST:
        return {
            "category": "CONDITION_MASK_VALUE",
            "architectural_value_status": "SOURCE_DOCUMENTED_REUSE_CONDITION_LAYER",
            "value_kind": "EXEC_GATED_VECTOR_COMPARE_MASK",
            "width_bits": 64,
            "cross_state_inputs": ["EXEC_IN", "VECTOR_COMPARE_CONDITION"],
            "memory_value_status": "NOT_MEMORY",
            "source": source("Ch.3/6/12 VOPC/VOP3 compare destination mask behavior; existing exact condition-mask layer is authoritative"),
        }
    if op in MEMORY_OPAQUE:
        return {
            "category": "SCALAR_MEMORY_RESULT",
            "architectural_value_status": "SOURCE_DOCUMENTED_MEMORY_OPERATION_VALUE_OPAQUE",
            "value_kind": "OPAQUE_MEMORY_LOAD_RESULT",
            "width_bits": None,
            "cross_state_inputs": ["SCALAR_MEMORY_ADDRESS_RESOURCE_STATE"],
            "memory_value_status": "WITHHELD_UNTIL_DESCRIPTOR_ADDRESS_SEMANTICS",
            "source": source("Ch.7 Scalar Memory Operations; load result is memory data, descriptor/address meaning intentionally deferred"),
        }
    raise KeyError(op)


def document() -> dict:
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "source": AMD,
        "observed_sgpr_def_opcodes": sorted(OBSERVED),
        "pure_scalar_transform_opcodes": sorted(PURE_SCALAR),
        "cross_state_identity_opcodes": sorted(CROSS_STATE),
        "condition_mask_value_opcodes": sorted(COMPARE_MASK_DEST),
        "scalar_memory_result_opcodes": sorted(MEMORY_OPAQUE),
        "opcode_behaviors": {op: behavior(op) for op in sorted(OBSERVED)},
        "architectural_value_semantic_opcode_count": len(OBSERVED - MEMORY_OPAQUE),
        "opaque_memory_value_opcode_count": len(MEMORY_OPAQUE),
        "shader_expression_semantic_promotions": 0,
        "policy": (
            "Source-documented GFX7 machine result identities are separated from shader meaning. "
            "The 26 observed non-memory scalar-def opcode families have architectural value rules; "
            "the five scalar-memory load families remain opaque memory values until resource/address "
            "semantics are proven. No material role or shader expression is inferred."
        ),
    }


def validate() -> list[str]:
    bad = []
    if len(OBSERVED) != 31:
        bad.append(f"observed:{len(OBSERVED)}!=31")
    if len(PURE_SCALAR) != 10:
        bad.append(f"pure:{len(PURE_SCALAR)}!=10")
    if len(CROSS_STATE) != 4:
        bad.append(f"cross:{len(CROSS_STATE)}!=4")
    if len(COMPARE_MASK_DEST) != 12:
        bad.append(f"compare:{len(COMPARE_MASK_DEST)}!=12")
    if len(MEMORY_OPAQUE) != 5:
        bad.append(f"memory:{len(MEMORY_OPAQUE)}!=5")
    if len(OBSERVED - MEMORY_OPAQUE) != 26:
        bad.append("architectural_nonmemory_surface_changed")
    return bad

if __name__ == "__main__":
    bad = validate()
    print(json.dumps(document() if not bad else {"status":"INVALID","violations":bad}, indent=2, sort_keys=True))
    raise SystemExit(0 if not bad else 2)
