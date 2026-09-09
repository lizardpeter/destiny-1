#!/usr/bin/env python3
"""Source-backed GFX7 architectural effects for D1 GCN instructions.

This module is intentionally *not* a shader semantic decompiler. It records only
architectural effects that are stated by AMD's Sea Islands (GFX7) ISA reference and
that matter to a later exact D1 shader IR: EXEC/VCC/SCC/PC effects, cross-lane
behavior, partial destination writes, memory class and control-flow class.

The first tranche is restricted to opcodes that are actually in the exact
808EE505-baseline-novel frontier. High-level shader/material meaning remains
UNPROVEN even when an instruction's architectural behavior is source-closed.
"""
from __future__ import annotations

from copy import deepcopy

SCHEMA = "d1_gcn_arch_effect_registry/v1"
STATUS = "D1_GCN_ARCH_EFFECT_REGISTRY_SOURCE_CLOSED_TRANCHE_V1"
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


def _e(
    *, family: str, execution_scope: str, exec_behavior: str,
    destination_write_scope: str = "FULL_DESTINATION",
    implicit_reads=(), implicit_writes=(), memory_effect: str = "NONE",
    control_flow: str = "NONE", reads_old_destination: bool = False,
    operation: str, source_locator: str, notes=(),
):
    return {
        "architectural_status": "SOURCE_CLOSED",
        "shader_expression_status": SEMANTIC_STATUS,
        "family": family,
        "execution_scope": execution_scope,
        "exec_behavior": exec_behavior,
        "destination_write_scope": destination_write_scope,
        "implicit_reads": list(implicit_reads),
        "implicit_writes": list(implicit_writes),
        "memory_effect": memory_effect,
        "control_flow": control_flow,
        "reads_old_destination": bool(reads_old_destination),
        "operation": operation,
        "source": {**AMD_SEA_ISLANDS, "locator": source_locator},
        "notes": list(notes),
    }


# IMPORTANT: every key below must be admitted by the exact global structural
# evidence frontier before a consumer may treat this registry as applicable.
REGISTRY = {
    "v_cmp_eq_i32": _e(
        family="VOPC_OR_VOP3_COMPARE", execution_scope="VECTOR_PER_LANE",
        exec_behavior="EXEC_GATED", destination_write_scope="COMPARE_MASK",
        implicit_reads=("exec",), operation="signed integer equality compare",
        source_locator="Ch. 6 vector compare behavior; Ch. 12 V_CMP_EQ_I32",
        notes=("VOPC writes VCC; VOP3 writes its encoded SGPR-pair destination.",),
    ),
    "v_fract_f32": _e(
        family="VOP1", execution_scope="VECTOR_PER_LANE", exec_behavior="EXEC_GATED",
        implicit_reads=("exec",), operation="D = S0 - floor(S0)",
        source_locator="Ch. 12 V_FRACT_F32",
    ),
    "v_readlane_b32": _e(
        family="VOP2_CROSS_LANE", execution_scope="CROSS_LANE",
        exec_behavior="IGNORES_EXEC_PREDICATION", operation="copy selected VGPR lane to SGPR",
        source_locator="Ch. 12 V_READLANE_B32",
        notes=("The ISA explicitly states that this instruction ignores the EXEC mask.",),
    ),
    "v_lshlrev_b32": _e(
        family="VOP2", execution_scope="VECTOR_PER_LANE", exec_behavior="EXEC_GATED",
        implicit_reads=("exec",), operation="D = S1 << S0[4:0]",
        source_locator="Ch. 12 V_LSHLREV_B32",
    ),
    "tbuffer_load_format_xyzw": _e(
        family="MTBUF", execution_scope="VECTOR_MEMORY_PER_LANE", exec_behavior="EXEC_GATED",
        implicit_reads=("exec",), memory_effect="TYPED_BUFFER_READ",
        destination_write_scope="FOUR_DWORDS_FORMAT_CONVERTED",
        operation="typed buffer load of XYZW components with format conversion",
        source_locator="Ch. 8 vector memory operations; Ch. 12 TBUFFER_LOAD_FORMAT_XYZW",
    ),
    "v_writelane_b32": _e(
        family="VOP2_CROSS_LANE", execution_scope="CROSS_LANE",
        exec_behavior="IGNORES_EXEC_PREDICATION", destination_write_scope="ONE_SELECTED_VGPR_LANE",
        reads_old_destination=True, operation="write one selected VGPR lane from scalar source",
        source_locator="Ch. 12 V_WRITELANE_B32",
        notes=("Untouched destination lanes are preserved; old destination value is therefore an architectural input.",),
    ),
    "v_cmp_le_f32": _e(
        family="VOPC_OR_VOP3_COMPARE", execution_scope="VECTOR_PER_LANE",
        exec_behavior="EXEC_GATED", destination_write_scope="COMPARE_MASK",
        implicit_reads=("exec",), operation="floating-point less-than-or-equal compare",
        source_locator="Ch. 6 vector compare behavior; Ch. 12 V_CMP_LE_F32",
        notes=("VOPC writes VCC; VOP3 writes its encoded SGPR-pair destination.",),
    ),
    "v_floor_f32": _e(
        family="VOP1", execution_scope="VECTOR_PER_LANE", exec_behavior="EXEC_GATED",
        implicit_reads=("exec",), operation="round toward negative infinity",
        source_locator="Ch. 12 V_FLOOR_F32",
    ),
    "v_rndne_f32": _e(
        family="VOP1", execution_scope="VECTOR_PER_LANE", exec_behavior="EXEC_GATED",
        implicit_reads=("exec",), operation="round to nearest integer, ties to even",
        source_locator="Ch. 12 V_RNDNE_F32",
    ),
    "s_swappc_b64": _e(
        family="SOP1", execution_scope="SCALAR_WAVE", exec_behavior="SCALAR_UNMASKED",
        implicit_reads=("pc",), implicit_writes=("pc",), control_flow="INDIRECT_PC_SWAP",
        operation="save next PC in destination and load PC from source SGPR pair",
        source_locator="Ch. 12 S_SWAPPC_B64",
    ),
    "v_and_b32": _e(
        family="VOP2", execution_scope="VECTOR_PER_LANE", exec_behavior="EXEC_GATED",
        implicit_reads=("exec",), operation="bitwise AND",
        source_locator="Ch. 12 V_AND_B32",
    ),
    "v_or_b32": _e(
        family="VOP2", execution_scope="VECTOR_PER_LANE", exec_behavior="EXEC_GATED",
        implicit_reads=("exec",), operation="bitwise OR",
        source_locator="Ch. 12 V_OR_B32",
    ),
    "v_cos_f32": _e(
        family="VOP1", execution_scope="VECTOR_PER_LANE", exec_behavior="EXEC_GATED",
        implicit_reads=("exec",), operation="cosine special function",
        source_locator="Ch. 12 V_COS_F32",
    ),
    "image_load_mip": _e(
        family="MIMG", execution_scope="VECTOR_MEMORY_PER_LANE", exec_behavior="EXEC_GATED",
        implicit_reads=("exec",), memory_effect="IMAGE_READ",
        operation="image load using user-supplied mip level; no sampler",
        source_locator="Ch. 8 image memory operations; Ch. 12 IMAGE_LOAD_MIP",
    ),
    "v_sin_f32": _e(
        family="VOP1", execution_scope="VECTOR_PER_LANE", exec_behavior="EXEC_GATED",
        implicit_reads=("exec",), operation="sine special function",
        source_locator="Ch. 12 V_SIN_F32",
    ),
    "v_min_f32": _e(
        family="VOP2", execution_scope="VECTOR_PER_LANE", exec_behavior="EXEC_GATED",
        implicit_reads=("exec",), operation="floating-point minimum with ISA-defined NaN handling",
        source_locator="Ch. 12 V_MIN_F32",
    ),
    "s_or_b64": _e(
        family="SOP2", execution_scope="SCALAR_WAVE", exec_behavior="SCALAR_UNMASKED",
        implicit_writes=("scc",), operation="64-bit bitwise OR; SCC = 1 iff result is nonzero",
        source_locator="Ch. 12 S_OR_B64",
    ),
    "v_sub_i32": _e(
        family="VOP2_OR_VOP3", execution_scope="VECTOR_PER_LANE", exec_behavior="EXEC_GATED",
        implicit_reads=("exec",), destination_write_scope="VALUE_AND_ENCODED_CARRY_DESTINATION",
        operation="32-bit integer subtract with carry/borrow result to encoded carry destination",
        source_locator="Ch. 6 integer arithmetic behavior; Ch. 12 V_SUB_I32",
        notes=("The carry destination is VCC in VOP2 and an encoded SGPR pair in VOP3.",),
    ),
    "image_sample_lz": _e(
        family="MIMG", execution_scope="VECTOR_MEMORY_PER_LANE", exec_behavior="EXEC_GATED",
        implicit_reads=("exec",), memory_effect="IMAGE_SAMPLE",
        operation="sample image at level zero",
        source_locator="Ch. 8 image memory operations; Ch. 12 IMAGE_SAMPLE_LZ",
    ),
    "v_mul_lo_u32": _e(
        family="VOP3", execution_scope="VECTOR_PER_LANE", exec_behavior="EXEC_GATED",
        implicit_reads=("exec",), operation="low 32 bits of unsigned 32x32 product",
        source_locator="Ch. 12 V_MUL_LO_U32",
    ),
    "s_nop": _e(
        family="SOPP", execution_scope="SCALAR_WAVE", exec_behavior="SCALAR_UNMASKED",
        operation="no architectural data result; immediate encodes repeat count",
        source_locator="Ch. 12 S_NOP",
    ),
    "v_readfirstlane_b32": _e(
        family="VOP1_CROSS_LANE", execution_scope="CROSS_LANE",
        exec_behavior="READS_EXEC_FOR_LANE_SELECTION_BUT_IGNORES_PREDICATION",
        implicit_reads=("exec",), operation="copy source VGPR from first active EXEC lane to SGPR",
        source_locator="Ch. 12 V_READFIRSTLANE_B32",
        notes=("If EXEC is zero, the ISA specifies lane zero; EXEC selects the source lane but does not predicate the instruction.",),
    ),
    "s_cbranch_vccz": _e(
        family="SOPP", execution_scope="SCALAR_WAVE", exec_behavior="SCALAR_UNMASKED",
        implicit_reads=("vcc", "pc"), implicit_writes=("pc",), control_flow="DIRECT_CONDITIONAL",
        operation="branch when VCC == 0",
        source_locator="Ch. 4 program flow; Ch. 12 S_CBRANCH_VCCZ",
    ),
    "s_cbranch_vccnz": _e(
        family="SOPP", execution_scope="SCALAR_WAVE", exec_behavior="SCALAR_UNMASKED",
        implicit_reads=("vcc", "pc"), implicit_writes=("pc",), control_flow="DIRECT_CONDITIONAL",
        operation="branch when VCC != 0",
        source_locator="Ch. 4 program flow; Ch. 12 S_CBRANCH_VCCNZ",
    ),
    "s_cbranch_execnz": _e(
        family="SOPP", execution_scope="SCALAR_WAVE", exec_behavior="SCALAR_UNMASKED",
        implicit_reads=("exec", "pc"), implicit_writes=("pc",), control_flow="DIRECT_CONDITIONAL",
        operation="branch when EXEC != 0",
        source_locator="Ch. 4 program flow; Ch. 12 S_CBRANCH_EXECNZ",
    ),
    "v_cmpx_eq_i32": _e(
        family="VOPC_OR_VOP3_COMPARE_X", execution_scope="VECTOR_PER_LANE",
        exec_behavior="EXEC_GATED_AND_UPDATES_EXEC", destination_write_scope="COMPARE_MASK",
        implicit_reads=("exec",), implicit_writes=("exec",),
        operation="signed integer equality compare; compare result also updates EXEC",
        source_locator="Ch. 6 vector compare behavior; Ch. 12 V_CMPX_EQ_I32",
        notes=("CMPX writes the compare mask destination and additionally writes EXEC.",),
    ),
    "v_cmpx_lt_u32": _e(
        family="VOPC_OR_VOP3_COMPARE_X", execution_scope="VECTOR_PER_LANE",
        exec_behavior="EXEC_GATED_AND_UPDATES_EXEC", destination_write_scope="COMPARE_MASK",
        implicit_reads=("exec",), implicit_writes=("exec",),
        operation="unsigned integer less-than compare; compare result also updates EXEC",
        source_locator="Ch. 6 vector compare behavior; Ch. 12 V_CMPX_LT_U32",
        notes=("CMPX writes the compare mask destination and additionally writes EXEC.",),
    ),
}


def validate_registry() -> list[str]:
    problems = []
    required = {
        "architectural_status", "shader_expression_status", "family", "execution_scope",
        "exec_behavior", "destination_write_scope", "implicit_reads", "implicit_writes",
        "memory_effect", "control_flow", "reads_old_destination", "operation", "source", "notes",
    }
    for op, e in sorted(REGISTRY.items()):
        missing = required - set(e)
        if missing:
            problems.append(f"{op}:missing:{sorted(missing)}")
        if e.get("architectural_status") != "SOURCE_CLOSED":
            problems.append(f"{op}:architectural_status")
        if e.get("shader_expression_status") != SEMANTIC_STATUS:
            problems.append(f"{op}:shader_expression_status")
        s = e.get("source") or {}
        for k in ("document_id", "revision", "release_date", "official_url", "locator"):
            if not s.get(k):
                problems.append(f"{op}:source:{k}")
    return problems


def annotate_instruction(inst: dict) -> dict:
    """Return architectural defs/uses for a source-closed opcode, else unchanged status."""
    op = str(inst.get("opcode", ""))
    e = REGISTRY.get(op)
    if e is None:
        return {
            "opcode": op,
            "architectural_status": "UNPROVEN",
            "shader_expression_status": SEMANTIC_STATUS,
            "architectural_defs": list(inst.get("defs") or []),
            "architectural_uses": list(inst.get("uses") or []),
        }
    defs = list(inst.get("defs") or [])
    uses = list(inst.get("uses") or [])
    if e["reads_old_destination"]:
        uses.extend(defs)
    defs.extend(e["implicit_writes"])
    uses.extend(e["implicit_reads"])
    return {
        "opcode": op,
        "architectural_status": "SOURCE_CLOSED",
        "shader_expression_status": SEMANTIC_STATUS,
        "architectural_defs": list(dict.fromkeys(defs)),
        "architectural_uses": list(dict.fromkeys(uses)),
        "effects": deepcopy(e),
    }


def registry_document() -> dict:
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "source": AMD_SEA_ISLANDS,
        "source_closed_opcode_count": len(REGISTRY),
        "semantic_promotions": 0,
        "opcodes": {k: deepcopy(REGISTRY[k]) for k in sorted(REGISTRY)},
        "policy": (
            "SOURCE_CLOSED means only that the GFX7 architectural instruction effect recorded here is "
            "backed by AMD document 70653 revision 1.3. It does not promote shader expression, material, "
            "resource-role, or game-level semantics."
        ),
    }


if __name__ == "__main__":
    import json
    bad = validate_registry()
    if bad:
        print(json.dumps({"status": "INVALID", "problems": bad}, indent=2))
        raise SystemExit(2)
    print(json.dumps(registry_document(), indent=2, sort_keys=True))
