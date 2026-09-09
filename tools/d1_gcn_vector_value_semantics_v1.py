#!/usr/bin/env python3
"""Conservative architectural value classes for the exact D1 GFX7 VGPR-def surface.

This registry is intentionally a promotion frontier, not a shader decompiler.  It assigns
all 74 observed VGPR-defining opcodes to an ISA-domain/value-boundary class while leaving
per-op ALU formulas, floating-point MODE behavior, interpolation parameters, LDS contents,
and image/buffer resource/address/format semantics for later source-closure gates.
"""
from __future__ import annotations
import json

import d1_gcn_vgpr_machine_semantics_v1 as vgpr_machine
import d1_condition_machine_semantics_v1 as condition_machine

SCHEMA = "d1_gcn_vector_value_semantics/v1"
STATUS = "D1_GCN_VECTOR_VALUE_SEMANTICS_FRONTIER_SOURCE_CLOSED"
AMD = {
    "vendor": "Advanced Micro Devices, Inc.",
    "title": "AMD Sea Islands Series Instruction Set Architecture",
    "document_id": "70653",
    "revision": "1.3",
    "release_date": "2013-12-01",
    "architecture": "GCN 2 / GFX7 / Sea Islands",
    "official_url": "https://docs.amd.com/v/u/en-US/sea-islands-instruction-set-architecture_0",
}

IMAGE_VALUE_OPAQUE = {
    "image_gather4_lz", "image_gather4_lz_o", "image_get_lod", "image_get_resinfo",
    "image_load_mip", "image_sample", "image_sample_d", "image_sample_l",
    "image_sample_lz", "image_sample_lz_o",
}
BUFFER_VALUE_OPAQUE = {
    "buffer_load_dword", "tbuffer_load_format_xyz", "tbuffer_load_format_xyzw",
}
DS_VALUE_OPAQUE = {"ds_read2_b32", "ds_read_b32", "ds_swizzle_b32"}
INTERPOLATION_VALUE_OPAQUE = {"v_interp_mov_f32", "v_interp_p1_f32", "v_interp_p2_f32"}
DYNAMIC_VGPR_SOURCE = {"v_movrels_b32"}
SINGLE_LANE_MUTATION = {"v_writelane_b32"}
PREDICATE_SELECT = {"v_cndmask_b32"}
CARRY_COUPLED = set(condition_machine.CARRY)

SPECIAL = (
    IMAGE_VALUE_OPAQUE | BUFFER_VALUE_OPAQUE | DS_VALUE_OPAQUE | INTERPOLATION_VALUE_OPAQUE |
    DYNAMIC_VGPR_SOURCE | SINGLE_LANE_MUTATION | PREDICATE_SELECT | CARRY_COUPLED
)
VALU_FORMULA_PENDING = set(vgpr_machine.VGPR_DEF_OPCODES) - SPECIAL
OBSERVED = set(vgpr_machine.VGPR_DEF_OPCODES)


def source(locator: str) -> dict:
    return {**AMD, "locator": locator}


def category(op: str) -> str:
    if op in IMAGE_VALUE_OPAQUE: return "IMAGE_RESOURCE_VALUE_OPAQUE"
    if op in BUFFER_VALUE_OPAQUE: return "BUFFER_RESOURCE_VALUE_OPAQUE"
    if op in DS_VALUE_OPAQUE: return "DS_LDS_VALUE_OPAQUE"
    if op in INTERPOLATION_VALUE_OPAQUE: return "INTERPOLATION_VALUE_OPAQUE"
    if op in DYNAMIC_VGPR_SOURCE: return "DYNAMIC_VGPR_SOURCE_IDENTITY"
    if op in SINGLE_LANE_MUTATION: return "SINGLE_LANE_MUTATION_VALUE"
    if op in PREDICATE_SELECT: return "PREDICATE_SELECT_VALUE"
    if op in CARRY_COUPLED: return "VALU_CARRY_COUPLED_VALUE"
    if op in VALU_FORMULA_PENDING: return "VALU_FORMULA_PENDING"
    raise KeyError(op)


def behavior(op: str) -> dict:
    cat = category(op)
    base = {
        "category": cat,
        "vgpr_write_behavior": vgpr_machine.behavior(op)["write_behavior"],
        "shader_expression_semantics": "WITHHELD",
        "material_semantics": "WITHHELD",
    }
    if cat == "IMAGE_RESOURCE_VALUE_OPAQUE":
        return {**base,
            "architectural_value_status": "RESOURCE_RESULT_OPAQUE",
            "value_formula_status": "WITHHELD_RESOURCE_DESCRIPTOR_ADDRESS_FORMAT",
            "source": source("Ch. 8 Image Instructions; exact image resource/address/format semantics deferred"),
        }
    if cat == "BUFFER_RESOURCE_VALUE_OPAQUE":
        return {**base,
            "architectural_value_status": "RESOURCE_RESULT_OPAQUE",
            "value_formula_status": "WITHHELD_RESOURCE_DESCRIPTOR_ADDRESS_FORMAT",
            "source": source("Ch. 7/8 Buffer and typed-buffer instructions; exact resource/address/format semantics deferred"),
        }
    if cat == "DS_LDS_VALUE_OPAQUE":
        return {**base,
            "architectural_value_status": "LDS_DS_RESULT_OPAQUE",
            "value_formula_status": "WITHHELD_LDS_ADDRESS_DATA_SEMANTICS",
            "source": source("Ch. 9 Data Share instructions; exact LDS address/data semantics deferred"),
        }
    if cat == "INTERPOLATION_VALUE_OPAQUE":
        return {**base,
            "architectural_value_status": "INTERPOLATION_RESULT_OPAQUE",
            "value_formula_status": "WITHHELD_INTERPOLATION_PARAMETER_STATE",
            "source": source("Ch. 12 VINTRP instructions; parameter/interpolation state semantics deferred"),
        }
    if cat == "DYNAMIC_VGPR_SOURCE_IDENTITY":
        return {**base,
            "architectural_value_status": "SOURCE_DOCUMENTED_DYNAMIC_IDENTITY",
            "value_formula_status": "IDENTITY_ONLY",
            "implicit_inputs": ["M0"],
            "identity": "VGPR[encoded_source + M0]",
            "source": vgpr_machine.behavior(op)["source"],
        }
    if cat == "SINGLE_LANE_MUTATION_VALUE":
        return {**base,
            "architectural_value_status": "SOURCE_DOCUMENTED_LANE_MUTATION",
            "value_formula_status": "WRITE_VALUE_OPERAND_PENDING_BINDING",
            "exec_dependency": "IGNORES_EXEC",
            "old_destination_dependency": "PRESERVE_ALL_OTHER_LANES",
            "source": vgpr_machine.behavior(op)["source"],
        }
    if cat == "PREDICATE_SELECT_VALUE":
        return {**base,
            "architectural_value_status": "SOURCE_DOCUMENTED_PREDICATE_SELECT_SURFACE",
            "value_formula_status": "OPERAND_BINDING_PENDING",
            "implicit_or_typed_inputs": ["CONDITION_MASK"],
            "source": source("Ch. 12 V_CNDMASK_B32; exact condition-mask dataflow layer is authoritative"),
        }
    if cat == "VALU_CARRY_COUPLED_VALUE":
        return {**base,
            "architectural_value_status": "SOURCE_DOCUMENTED_VALUE_PLUS_MASK_SIDE_EFFECT",
            "value_formula_status": "OPERAND_BINDING_PENDING",
            "implicit_outputs": ["CONDITION_CARRY_MASK"],
            "source": source("Ch. 6 integer arithmetic and Ch. 12 V_ADD_I32/V_SUB_I32; exact carry-mask layer is authoritative"),
        }
    # Remaining VALU opcodes are admitted only as exact observed ALU surface.  Their actual
    # operation formulas are intentionally not claimed by this registry.
    return {**base,
        "architectural_value_status": "OBSERVED_VALU_RESULT_FORMULA_WITHHELD",
        "value_formula_status": "NEXT_SOURCE_CLOSURE_GATE",
        "fp_mode_sensitive_candidate": any(t in op for t in ("f32", "f16")),
        "source": source("Ch. 6 and Ch. 12 VALU instruction families; per-op formula/rounding/MODE proof deferred"),
    }


def document() -> dict:
    cats = {}
    for op in sorted(OBSERVED):
        cats.setdefault(category(op), []).append(op)
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "source": AMD,
        "observed_vgpr_def_opcode_count": len(OBSERVED),
        "categories": cats,
        "category_opcode_counts": {k: len(v) for k, v in sorted(cats.items())},
        "opcode_behaviors": {op: behavior(op) for op in sorted(OBSERVED)},
        "shader_expression_semantic_promotions": 0,
        "policy": (
            "All observed VGPR-defining opcodes receive one conservative ISA-domain value class. "
            "Resource, LDS and interpolation values stay opaque; dynamic/lane/predicate/carry roles preserve "
            "already source-closed machine identities. Remaining VALU formulas and floating-point MODE behavior "
            "are explicitly deferred. No shader expression or material meaning is inferred."
        ),
    }


def validate() -> list[str]:
    bad = []
    groups = [
        IMAGE_VALUE_OPAQUE, BUFFER_VALUE_OPAQUE, DS_VALUE_OPAQUE, INTERPOLATION_VALUE_OPAQUE,
        DYNAMIC_VGPR_SOURCE, SINGLE_LANE_MUTATION, PREDICATE_SELECT, CARRY_COUPLED, VALU_FORMULA_PENDING,
    ]
    union = set().union(*groups)
    if union != OBSERVED:
        bad.append(f"coverage:{sorted(OBSERVED-union)}:{sorted(union-OBSERVED)}")
    for i, a in enumerate(groups):
        for b in groups[i+1:]:
            if a & b: bad.append(f"category_overlap:{sorted(a & b)}")
    expected = {
        "IMAGE_RESOURCE_VALUE_OPAQUE": 10,
        "BUFFER_RESOURCE_VALUE_OPAQUE": 3,
        "DS_LDS_VALUE_OPAQUE": 3,
        "INTERPOLATION_VALUE_OPAQUE": 3,
        "DYNAMIC_VGPR_SOURCE_IDENTITY": 1,
        "SINGLE_LANE_MUTATION_VALUE": 1,
        "PREDICATE_SELECT_VALUE": 1,
        "VALU_CARRY_COUPLED_VALUE": 2,
        "VALU_FORMULA_PENDING": 50,
    }
    got = {}
    for op in OBSERVED: got[category(op)] = got.get(category(op), 0) + 1
    if got != expected: bad.append(f"category_counts:{got}!={expected}")
    if len(OBSERVED) != 74: bad.append(f"opcode_count:{len(OBSERVED)}!=74")
    if CARRY_COUPLED != {"v_add_i32", "v_sub_i32"}: bad.append("carry_surface_changed")
    return bad


if __name__ == "__main__":
    bad = validate()
    print(json.dumps(document() if not bad else {"status": "INVALID", "violations": bad}, indent=2, sort_keys=True))
    raise SystemExit(0 if not bad else 2)
