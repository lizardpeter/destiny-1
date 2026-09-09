#!/usr/bin/env python3
"""Source-backed GFX7 EXEC-mask machine semantics for the exact D1 corpus frontier.

This registry closes only wave-mask mechanics needed for symbolic EXEC dataflow.
It does not interpret shader expressions, material intent, resource roles, or game
semantics. The exact structural frontier contains seven explicit EXEC-touching
opcodes; the global architectural frontier adds two CMPX opcodes whose EXEC write
is implicit in the instruction semantics.
"""
from __future__ import annotations

from copy import deepcopy

SCHEMA = "d1_gcn_exec_mask_machine_semantics/v1"
STATUS = "D1_GCN_EXEC_MASK_MACHINE_SEMANTICS_SOURCE_CLOSED"
SEMANTIC_STATUS = "UNPROVEN"
AMD_SEA_ISLANDS = {
    "vendor": "Advanced Micro Devices, Inc.",
    "title": "AMD Sea Islands Series Instruction Set Architecture",
    "document_id": "70653",
    "revision": "1.3",
    "release_date": "2013-12-01",
    "architecture": "GCN 2 / GFX7 / Sea Islands",
    "official_url": "https://docs.amd.com/v/u/en-US/sea-islands-instruction-set-architecture_0",
}


def _e(*, kind: str, reads=(), writes=(), result=None, saved_result=None,
       branch_condition=None, scc=None, source_locator: str, notes=()):
    return {
        "architectural_status": "SOURCE_CLOSED",
        "shader_expression_status": SEMANTIC_STATUS,
        "exec_dataflow_kind": kind,
        "reads": list(reads),
        "writes": list(writes),
        "result": result,
        "saved_result": saved_result,
        "branch_condition": branch_condition,
        "scc_result": scc,
        "source": {**AMD_SEA_ISLANDS, "locator": source_locator},
        "notes": list(notes),
    }


REGISTRY = {
    "s_mov_b64": _e(
        kind="SCALAR_MASK_MOVE", reads=("src0",), writes=("dst",),
        result="SRC0",
        source_locator="Ch. 12 S_MOV_B64; Ch. 13 SOP1 opcode 4",
        notes=("When SDST is EXEC, this is an explicit EXEC overwrite; when SSRC0 is EXEC it saves the current mask.",),
    ),
    "s_wqm_b64": _e(
        kind="WHOLE_QUAD_MODE", reads=("src0",), writes=("dst", "scc"),
        result="WQM(SRC0)", scc="NONZERO(RESULT)",
        source_locator="Ch. 12 S_WQM_B64; Ch. 13 SOP1 opcode 10",
        notes=("Each group of four mask bits becomes all ones iff any source bit in that group is one.",),
    ),
    "s_and_b64": _e(
        kind="SCALAR_MASK_AND", reads=("src0", "src1"), writes=("dst", "scc"),
        result="AND(SRC0,SRC1)", scc="NONZERO(RESULT)",
        source_locator="Ch. 12 S_AND_B64; Ch. 13 SOP2 opcode 15",
    ),
    "s_andn2_b64": _e(
        kind="SCALAR_MASK_AND_NOT_SECOND", reads=("src0", "src1"), writes=("dst", "scc"),
        result="AND(SRC0,NOT(SRC1))", scc="NONZERO(RESULT)",
        source_locator="Ch. 12 S_ANDN2_B64; Ch. 13 SOP2 opcode 21",
    ),
    "s_and_saveexec_b64": _e(
        kind="SAVEEXEC_AND", reads=("src0", "exec_in"), writes=("dst", "exec", "scc"),
        result="AND(SRC0,EXEC_IN)", saved_result="EXEC_IN", scc="NONZERO(EXEC_OUT)",
        source_locator="Ch. 12 S_AND_SAVEEXEC_B64; Ch. 13 SOP1 opcode 36",
        notes=("Destination receives old EXEC before EXEC is replaced by SRC0 & old EXEC.",),
    ),
    "s_cbranch_execz": _e(
        kind="EXEC_BRANCH", reads=("exec",), writes=("pc",), branch_condition="EXEC_EQ_ZERO",
        source_locator="Ch. 12 S_CBRANCH_EXECZ; Ch. 13 SOPP opcode 8",
    ),
    "s_cbranch_execnz": _e(
        kind="EXEC_BRANCH", reads=("exec",), writes=("pc",), branch_condition="EXEC_NE_ZERO",
        source_locator="Ch. 12 S_CBRANCH_EXECNZ; Ch. 13 SOPP opcode 9",
    ),
    "v_cmpx_eq_i32": _e(
        kind="CMPX_MASK", reads=("exec_in", "src0", "src1"), writes=("encoded_compare_dst", "exec"),
        result="CMPX_EQ_I32_ACTIVE_LANES(SRC0,SRC1,EXEC_IN)",
        source_locator="Ch. 6 vector compare behavior; Ch. 12 V_CMPX_EQ_I32",
        notes=("CMPX compare result is written to the encoded mask destination and also updates EXEC; inactive lanes do not become active.",),
    ),
    "v_cmpx_lt_u32": _e(
        kind="CMPX_MASK", reads=("exec_in", "src0", "src1"), writes=("encoded_compare_dst", "exec"),
        result="CMPX_LT_U32_ACTIVE_LANES(SRC0,SRC1,EXEC_IN)",
        source_locator="Ch. 6 vector compare behavior; Ch. 12 V_CMPX_LT_U32",
        notes=("CMPX compare result is written to the encoded mask destination and also updates EXEC; inactive lanes do not become active.",),
    ),
}

EXPECTED_OPCODES = tuple(sorted(REGISTRY))


def validate_registry() -> list[str]:
    problems = []
    if len(REGISTRY) != 9:
        problems.append(f"registry_count:{len(REGISTRY)}!=9")
    required = {
        "architectural_status", "shader_expression_status", "exec_dataflow_kind",
        "reads", "writes", "result", "saved_result", "branch_condition", "scc_result",
        "source", "notes",
    }
    for op, e in sorted(REGISTRY.items()):
        missing = required - set(e)
        if missing:
            problems.append(f"{op}:missing:{sorted(missing)}")
        if e.get("architectural_status") != "SOURCE_CLOSED":
            problems.append(f"{op}:architectural_status")
        if e.get("shader_expression_status") != SEMANTIC_STATUS:
            problems.append(f"{op}:shader_expression_status")
        src = e.get("source") or {}
        for k in ("document_id", "revision", "release_date", "official_url", "locator"):
            if not src.get(k):
                problems.append(f"{op}:source:{k}")
    return problems


def registry_document() -> dict:
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "source": AMD_SEA_ISLANDS,
        "source_closed_opcode_count": len(REGISTRY),
        "shader_expression_semantic_promotions": 0,
        "opcodes": {k: deepcopy(REGISTRY[k]) for k in sorted(REGISTRY)},
        "policy": (
            "SOURCE_CLOSED here means only exact wave-mask machine behavior. The registry may be used to build "
            "EXEC provenance and branch predicates, but not to infer high-level shader expressions or game semantics."
        ),
    }


if __name__ == "__main__":
    import json
    bad = validate_registry()
    if bad:
        print(json.dumps({"status": "INVALID", "problems": bad}, indent=2))
        raise SystemExit(2)
    print(json.dumps(registry_document(), indent=2, sort_keys=True))
