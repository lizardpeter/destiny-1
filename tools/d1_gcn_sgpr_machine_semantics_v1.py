#!/usr/bin/env python3
"""Source-backed physical SGPR/M0 mutation behavior for the exact D1 GFX7 corpus.

This registry closes only state-identity behavior needed by scalar SSA. Whole scalar
writes replace the destination register. Vector compares targeting an SGPR pair update
condition-mask bits only for EXEC-active lanes, preserving inactive bits. S_ADDK_I32 is
a true destination read-modify-write. Opcode result values remain withheld.
"""
from __future__ import annotations

import json

SCHEMA = "d1_gcn_sgpr_machine_semantics/v1"
STATUS = "D1_GCN_SGPR_MACHINE_SEMANTICS_SOURCE_CLOSED"
AMD = {
    "vendor": "Advanced Micro Devices, Inc.",
    "title": "AMD Sea Islands Series Instruction Set Architecture",
    "document_id": "70653",
    "revision": "1.3",
    "release_date": "2013-12-01",
    "architecture": "GCN 2 / GFX7 / Sea Islands",
    "official_url": "https://docs.amd.com/v/u/en-US/sea-islands-instruction-set-architecture_0",
}

COMPARE_MASK_DEST_OPCODES = {
    "v_cmp_class_f32", "v_cmp_eq_f32", "v_cmp_ge_f32", "v_cmp_gt_f32",
    "v_cmp_le_f32", "v_cmp_lg_i32", "v_cmp_lt_f32", "v_cmp_lt_i32",
    "v_cmp_neq_f32", "v_cmp_ngt_f32", "v_cmpx_eq_i32", "v_cmpx_lt_u32",
}

WHOLE_SCALAR_DEF_OPCODES = {
    "s_addk_i32", "s_and_b32", "s_and_b64", "s_and_saveexec_b64", "s_andn2_b64",
    "s_buffer_load_dword", "s_buffer_load_dwordx2", "s_buffer_load_dwordx4",
    "s_load_dwordx4", "s_load_dwordx8", "s_lshl_b32", "s_mov_b32", "s_mov_b64",
    "s_movk_i32", "s_or_b64", "s_swappc_b64", "s_xor_b64",
    "v_readfirstlane_b32", "v_readlane_b32",
}

OBSERVED_SGPR_DEF_OPCODES = COMPARE_MASK_DEST_OPCODES | WHOLE_SCALAR_DEF_OPCODES
RMW_DEST_OPCODES = {"s_addk_i32"}


def source(locator: str) -> dict:
    return {**AMD, "locator": locator}


def behavior(op: str) -> dict:
    if op not in OBSERVED_SGPR_DEF_OPCODES:
        raise KeyError(op)
    if op in COMPARE_MASK_DEST_OPCODES:
        return {
            "write_behavior": "EXEC_GATED_MASK_HALF_WRITE",
            "old_destination_dependency": "YES_INACTIVE_LANE_BITS_PRESERVED",
            "exec_dependency": "EXEC_IN",
            "result_value_semantics": "VECTOR_COMPARE_MASK_VALUE_WITHHELD",
            "source": source("Ch. 3 EXEC mask plus VOPC/VOP3 compare destination mask behavior"),
        }
    if op == "s_addk_i32":
        return {
            "write_behavior": "WHOLE_SCALAR_RMW_WRITE",
            "old_destination_dependency": "YES_DEST_IS_SOURCE",
            "exec_dependency": "NONE_SCALAR_INSTRUCTION",
            "result_value_semantics": "D = D + signext(SIMM16), arithmetic expression promotion withheld",
            "source": source("Ch. 5 / SOPK S_ADDK_I32: D.i = D.i + signext(SIMM16)"),
        }
    return {
        "write_behavior": "WHOLE_SCALAR_WRITE",
        "old_destination_dependency": "NO_FOR_REGISTER_IDENTITY",
        "exec_dependency": "NONE_SCALAR_STATE_WRITE_OR_SOURCE_CLOSED_VECTOR_TO_SCALAR_WRITE",
        "result_value_semantics": "WITHHELD",
        "source": source("Opcode destination behavior; exact value expression intentionally deferred"),
    }


def document() -> dict:
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "source": AMD,
        "observed_sgpr_def_opcodes": sorted(OBSERVED_SGPR_DEF_OPCODES),
        "whole_scalar_def_opcodes": sorted(WHOLE_SCALAR_DEF_OPCODES),
        "compare_mask_destination_opcodes": sorted(COMPARE_MASK_DEST_OPCODES),
        "rmw_destination_opcodes": sorted(RMW_DEST_OPCODES),
        "opcode_behaviors": {op: behavior(op) for op in sorted(OBSERVED_SGPR_DEF_OPCODES)},
        "shader_expression_semantic_promotions": 0,
        "policy": "This registry proves physical scalar destination mutation only. Compare-mask SGPR halves preserve inactive EXEC lanes; S_ADDK reads its old destination; all other observed scalar destinations become new whole-register definitions. Result expressions remain withheld.",
    }


def validate() -> list[str]:
    bad = []
    if len(OBSERVED_SGPR_DEF_OPCODES) != 31:
        bad.append(f"observed_def_opcode_count:{len(OBSERVED_SGPR_DEF_OPCODES)}!=31")
    if len(COMPARE_MASK_DEST_OPCODES) != 12:
        bad.append(f"compare_def_opcode_count:{len(COMPARE_MASK_DEST_OPCODES)}!=12")
    if RMW_DEST_OPCODES != {"s_addk_i32"}:
        bad.append("rmw_surface_changed")
    for op in OBSERVED_SGPR_DEF_OPCODES:
        if behavior(op)["write_behavior"] not in {
            "WHOLE_SCALAR_WRITE", "WHOLE_SCALAR_RMW_WRITE", "EXEC_GATED_MASK_HALF_WRITE"
        }:
            bad.append(f"bad_behavior:{op}")
    return bad


if __name__ == "__main__":
    bad = validate()
    print(json.dumps(document() if not bad else {"status": "INVALID", "violations": bad}, indent=2, sort_keys=True))
    raise SystemExit(0 if not bad else 2)
