#!/usr/bin/env python3
"""Exact operand/source-domain frontier for the full D1 GFX7 VGPR-result surface."""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import d1_gcn_vector_value_semantics_v1 as sem
import d1_gcn_vgpr_machine_semantics_v1 as machine
import d1_condition_machine_semantics_v1 as condition
import d1_gcn_shader_corpus_structural_census as census
from d1_gcn_shader_corpus_structural_census_v3 import fixed_reg_kind

SCHEMA = "d1_gcn_vector_value_operand_frontier/v1"
STATUS = "D1_GCN_VECTOR_VALUE_OPERAND_FRONTIER_EXACT"
EXPECTED_PROGRAMS = 26464
EXPECTED_INSTRUCTIONS = 4896165
EXPECTED_VGPR_DEF_INSTRUCTIONS = 3690362
EXPECTED_VGPR_DEF_ENTRIES = 3864039
EXPECTED_SINGLE_LANE_WRITES = 9436
EXPECTED_DYNAMIC_MOVRELS = 6
VREG = re.compile(r"^v(\d+)$")


def is_vgpr(r: str) -> bool:
    return bool(VREG.fullmatch(r or ""))


def build(ir_dir: Path) -> dict:
    violations: list[str] = []
    unresolved: list[dict] = []
    paths = sorted(ir_dir.glob("*.json"))
    if len(paths) != EXPECTED_PROGRAMS:
        violations.append(f"ir_file_count:{len(paths)}!={EXPECTED_PROGRAMS}")

    total_ins = 0
    op_counts = collections.Counter()
    entry_counts = collections.Counter()
    category_counts = collections.Counter()
    category_entries = collections.Counter()
    program_category = collections.defaultdict(set)
    operand_forms = collections.defaultdict(collections.Counter)
    use_kind_forms = collections.defaultdict(collections.Counter)
    def_width_forms = collections.defaultdict(collections.Counter)
    special_use_counts = collections.Counter()
    special_use_opcodes = collections.Counter()
    write_behavior_counts = collections.Counter()
    write_behavior_opcodes = collections.Counter()
    machine_role_counts = collections.Counter()
    machine_role_opcodes = collections.Counter()
    examples = {}

    for p in paths:
        sha = p.stem.lower()
        d = json.loads(p.read_text())
        if d.get("status") != "D1_GCN_STRUCTURAL_IR_COMPLETE":
            violations.append(f"ir_status:{sha}:{d.get('status')!r}")
        if (d.get("parse_accounting") or {}).get("status") != "D1_GCN_STRUCTURAL_PARSE_ACCOUNTING_EXACT":
            violations.append(f"parse_status:{sha}")
        ins = d.get("instructions") or []
        total_ins += len(ins)
        for x in ins:
            vd = [r for r in (x.get("defs") or []) if is_vgpr(r)]
            if not vd:
                continue
            op = x["opcode"]
            op_counts[op] += 1
            entry_counts[op] += len(vd)
            def_width_forms[op][len(vd)] += 1

            if op not in sem.OBSERVED or op not in machine.VGPR_DEF_OPCODES:
                unresolved.append({
                    "gcn_sha256": sha, "instruction": x["index"], "opcode": op,
                    "problem": "UNREGISTERED_VGPR_DEF_OPCODE",
                })
                continue

            beh = sem.behavior(op)
            cat = beh["category"]
            category_counts[cat] += 1
            category_entries[cat] += len(vd)
            program_category[cat].add(sha)

            mb = machine.behavior(op)
            wb = mb["write_behavior"]
            write_behavior_counts[wb] += 1
            write_behavior_opcodes[(op, wb)] += 1

            operands = tuple(census.normalized_operand(z) for z in (x.get("operands") or []))
            kinds = tuple(fixed_reg_kind(z) for z in (x.get("uses") or []))
            operand_forms[op][operands] += 1
            use_kind_forms[op][kinds] += 1
            special = tuple(k for k in kinds if k in {"EXEC", "VCC", "SCC", "SGPR", "M0"})
            if special:
                special_use_counts[special] += 1
                special_use_opcodes[op] += 1

            roles = []
            if op in condition.CARRY:
                roles.append("CONDITION_CARRY_MASK_OUTPUT")
            if op == "v_cndmask_b32":
                roles.append("CONDITION_MASK_INPUT")
            if op == "v_movrels_b32":
                roles.append("M0_INDEXED_DYNAMIC_VGPR_SOURCE")
            if op == "v_writelane_b32":
                roles.extend(["EXEC_BYPASS", "SINGLE_LANE_DESTINATION_MUTATION"])
            if cat in {"IMAGE_RESOURCE_VALUE_OPAQUE", "BUFFER_RESOURCE_VALUE_OPAQUE"}:
                roles.append("RESOURCE_VALUE_BOUNDARY")
            if cat == "DS_LDS_VALUE_OPAQUE":
                roles.append("LDS_DS_VALUE_BOUNDARY")
            if cat == "INTERPOLATION_VALUE_OPAQUE":
                roles.append("INTERPOLATION_VALUE_BOUNDARY")
            if not roles:
                roles.append("NO_ADDITIONAL_MACHINE_ROLE_PROMOTED")
            for role in roles:
                machine_role_counts[role] += 1
                machine_role_opcodes[(op, role)] += 1

            key = (op, operands, kinds, len(vd), tuple(roles))
            examples.setdefault(key, {
                "gcn_sha256": sha,
                "instruction": x["index"],
                "address": x["address_hex"],
                "opcode": op,
                "operands": x.get("operands") or [],
                "defs": vd,
                "uses": x.get("uses") or [],
                "normalized_operands": list(operands),
                "use_kinds": list(kinds),
                "vgpr_result_component_count": len(vd),
                "category": cat,
                "write_behavior": wb,
                "machine_roles": roles,
            })

    if total_ins != EXPECTED_INSTRUCTIONS:
        violations.append(f"instruction_count:{total_ins}!={EXPECTED_INSTRUCTIONS}")
    if sum(op_counts.values()) != EXPECTED_VGPR_DEF_INSTRUCTIONS:
        violations.append(f"vgpr_def_instructions:{sum(op_counts.values())}!={EXPECTED_VGPR_DEF_INSTRUCTIONS}")
    if sum(entry_counts.values()) != EXPECTED_VGPR_DEF_ENTRIES:
        violations.append(f"vgpr_def_entries:{sum(entry_counts.values())}!={EXPECTED_VGPR_DEF_ENTRIES}")
    if set(op_counts) != sem.OBSERVED:
        violations.append(f"opcode_surface:{sorted(op_counts)}!={sorted(sem.OBSERVED)}")
    if len(op_counts) != 74:
        violations.append(f"opcode_count:{len(op_counts)}!=74")
    if op_counts.get("v_writelane_b32", 0) != EXPECTED_SINGLE_LANE_WRITES:
        violations.append(f"writelane:{op_counts.get('v_writelane_b32',0)}!={EXPECTED_SINGLE_LANE_WRITES}")
    if op_counts.get("v_movrels_b32", 0) != EXPECTED_DYNAMIC_MOVRELS:
        violations.append(f"movrels:{op_counts.get('v_movrels_b32',0)}!={EXPECTED_DYNAMIC_MOVRELS}")
    if sum(op_counts.get(op, 0) for op in condition.CARRY) != 11521:
        violations.append(f"carry_surface_count:{sum(op_counts.get(op,0) for op in condition.CARRY)}!=11521")
    if op_counts.get("v_cndmask_b32", 0) != 114066:
        violations.append(f"cndmask:{op_counts.get('v_cndmask_b32',0)}!=114066")
    if unresolved:
        violations.extend(
            f"unresolved:{r['gcn_sha256']}:{r['instruction']}:{r['opcode']}:{r['problem']}"
            for r in unresolved[:50]
        )

    def encode_forms(src):
        return {
            op: [{"signature": list(sig) if isinstance(sig, tuple) else sig, "count": n}
                 for sig, n in sorted(c.items(), key=lambda kv: str(kv[0]))]
            for op, c in sorted(src.items())
        }

    coverage = {
        "exact_program_count": len(paths),
        "exact_instruction_count": total_ins,
        "vgpr_def_instruction_count": sum(op_counts.values()),
        "vgpr_def_entry_count": sum(entry_counts.values()),
        "vgpr_def_opcode_count": len(op_counts),
        "opcode_instruction_counts": dict(sorted(op_counts.items())),
        "opcode_def_entry_counts": dict(sorted(entry_counts.items())),
        "category_instruction_counts": dict(sorted(category_counts.items())),
        "category_def_entry_counts": dict(sorted(category_entries.items())),
        "category_program_counts": {k: len(v) for k, v in sorted(program_category.items())},
        "operand_form_count": sum(len(v) for v in operand_forms.values()),
        "use_kind_form_count": sum(len(v) for v in use_kind_forms.values()),
        "def_width_form_count": sum(len(v) for v in def_width_forms.values()),
        "write_behavior_instruction_counts": dict(sorted(write_behavior_counts.items())),
        "machine_role_instruction_counts": dict(sorted(machine_role_counts.items())),
        "instructions_with_special_structural_use_kinds": sum(special_use_counts.values()),
        "special_structural_use_signature_counts": {
            "|".join(k): v for k, v in sorted(special_use_counts.items(), key=lambda kv: str(kv[0]))
        },
        "special_structural_use_opcode_counts": dict(sorted(special_use_opcodes.items())),
        "single_lane_write_instruction_count": op_counts.get("v_writelane_b32", 0),
        "dynamic_vgpr_source_instruction_count": op_counts.get("v_movrels_b32", 0),
        "condition_carry_coupled_instruction_count": sum(op_counts.get(op, 0) for op in condition.CARRY),
        "predicate_select_instruction_count": op_counts.get("v_cndmask_b32", 0),
        "shader_expression_semantic_promotions": 0,
    }

    return {
        "schema": SCHEMA,
        "status": STATUS if not violations else "D1_GCN_VECTOR_VALUE_OPERAND_FRONTIER_WITH_VIOLATIONS",
        "source_registry": sem.document(),
        "coverage": coverage,
        "operand_forms_by_opcode": encode_forms(operand_forms),
        "structural_use_kinds_by_opcode": encode_forms(use_kind_forms),
        "vgpr_result_widths_by_opcode": {
            op: [{"component_count": width, "instruction_count": n} for width, n in sorted(c.items())]
            for op, c in sorted(def_width_forms.items())
        },
        "write_behavior_opcode_counts": {
            op: {wb: n for (o, wb), n in sorted(write_behavior_opcodes.items()) if o == op}
            for op in sorted(op_counts)
        },
        "machine_role_opcode_counts": {
            op: {role: n for (o, role), n in sorted(machine_role_opcodes.items()) if o == op}
            for op in sorted(op_counts)
        },
        "examples": [v for _, v in sorted(examples.items(), key=lambda kv: str(kv[0]))],
        "unresolved": unresolved,
        "violations": violations,
        "semantic_boundary": {
            "lane_aware_vgpr_ssa": "GLOBAL_EXACT_PREREQUISITE",
            "actual_vector_operand_source_domains": "GLOBAL_EXACT" if not violations else "WITHHELD",
            "vgpr_result_component_shapes": "GLOBAL_EXACT" if not violations else "WITHHELD",
            "resource_lds_interpolation_values": "EXPLICIT_OPAQUE_BOUNDARIES",
            "dynamic_and_single_lane_machine_roles": "SOURCE_CLOSED",
            "predicate_and_carry_machine_roles": "SOURCE_CLOSED_REUSE_CONDITION_LAYER",
            "per_opcode_valu_formula_semantics": "NEXT_GATE" if not violations else "WITHHELD",
            "floating_point_mode_semantics": "WITHHELD",
            "shader_expression_semantics": "WITHHELD",
            "shader_expression_semantic_promotions": 0,
        },
        "policy": (
            "Every exact VGPR-def instruction is assigned to one conservative ISA-domain value class and its "
            "normalized operand/source-domain/result-width/write-behavior forms are censused. Resource, LDS and "
            "interpolation values remain opaque. ALU formulas and floating-point MODE behavior are not inferred."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ir-dir", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()
    out = build(a.ir_dir)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": out["status"], "coverage": out["coverage"], "violations": out["violations"][:30]}, indent=2, sort_keys=True))
    return 0 if not out["violations"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
