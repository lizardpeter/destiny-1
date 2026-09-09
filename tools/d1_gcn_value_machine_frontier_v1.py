#!/usr/bin/env python3
"""Fail-closed global value-producing opcode frontier over exact D1 GFX7 structural IR."""
from __future__ import annotations

import argparse
import collections
import json
import re
from pathlib import Path

import d1_condition_machine_semantics_v1 as cond
import d1_gcn_exec_mask_semantics_v1 as exec_sem
import d1_gcn_sgpr_machine_semantics_v1 as sgpr
import d1_gcn_value_machine_semantics_v1 as sem
import d1_gcn_vgpr_machine_semantics_v1 as vgpr

SCHEMA = "d1_gcn_value_machine_frontier/v1"
STATUS = "D1_GCN_VALUE_MACHINE_FRONTIER_EXACT"
IR_STATUS = "D1_GCN_STRUCTURAL_IR_COMPLETE"
PARSE_STATUS = "D1_GCN_STRUCTURAL_PARSE_ACCOUNTING_EXACT"
CENSUS_STATUS = "D1_GCN_SHADER_CORPUS_STRUCTURAL_CENSUS_COMPLETE"
EXPECTED_PROGRAMS = 26464
EXPECTED_INSTRUCTIONS = 4896165
EXPECTED_STAGE = {"DS": 20, "PS": 18375, "VS": 8069}
VREG = re.compile(r"^v\d+$")
SREG = re.compile(r"^s\d+$")


def dest_class(d: str) -> str:
    if VREG.fullmatch(d):
        return "VGPR"
    if SREG.fullmatch(d):
        return "SGPR"
    if d == "m0":
        return "M0"
    if d in {"vcc", "vcc_lo", "vcc_hi"}:
        return "VCC"
    if d in {"exec", "exec_lo", "exec_hi"}:
        return "EXEC"
    if d == "scc":
        return "SCC"
    return "UNKNOWN"


def allowed_for_dest(op: str, cls: str) -> bool:
    if cls == "VGPR":
        return op in vgpr.VGPR_DEF_OPCODES
    if cls in {"SGPR", "M0"}:
        return op in sgpr.OBSERVED_SGPR_DEF_OPCODES
    if cls == "VCC":
        return op in (set(cond.COMPARES) | set(cond.CARRY) | set(cond.SCALAR_MASK) | {"s_mov_b32"})
    if cls == "EXEC":
        return op in exec_sem.REGISTRY
    if cls == "SCC":
        return op in cond.SCC_PRODUCERS
    return False


def run(ir_dir: Path, census_path: Path) -> dict:
    violations: list[str] = []
    census = json.loads(census_path.read_text())
    if census.get("status") != CENSUS_STATUS:
        violations.append(f"census_status:{census.get('status')}")
    stage_by_sha = {p["gcn_sha256"].lower(): (p.get("stages") or []) for p in census.get("programs") or []}
    if len(stage_by_sha) != EXPECTED_PROGRAMS:
        violations.append(f"stage_map_count:{len(stage_by_sha)}!={EXPECTED_PROGRAMS}")

    paths = sorted(ir_dir.glob("*.json"))
    if len(paths) != EXPECTED_PROGRAMS:
        violations.append(f"ir_file_count:{len(paths)}!={EXPECTED_PROGRAMS}")

    counts = collections.Counter()
    stage_counts = collections.Counter()
    opcode_counts = collections.Counter()
    producer_opcode_counts = collections.Counter()
    family_instruction_counts = collections.Counter()
    family_opcode_sets: dict[str, set[str]] = collections.defaultdict(set)
    dest_class_counts = collections.Counter()
    observed_vgpr_ops: set[str] = set()
    observed_scalar_ops: set[str] = set()
    observed_special_ops: set[str] = set()
    bad_rows = []

    for path in paths:
        sha = path.stem.lower()
        stages = stage_by_sha.get(sha)
        if not stages or len(stages) != 1:
            violations.append(f"stage:{sha}:{stages}")
            continue
        stage_counts[stages[0]] += 1
        d = json.loads(path.read_text())
        if d.get("status") != IR_STATUS:
            violations.append(f"ir_status:{sha}:{d.get('status')}")
            continue
        if (d.get("parse_accounting") or {}).get("status") != PARSE_STATUS:
            violations.append(f"parse_status:{sha}")
            continue
        ins = d.get("instructions") or []
        counts["program_count"] += 1
        counts["instruction_count"] += len(ins)
        for x in ins:
            op = x["opcode"]
            defs = x.get("defs") or []
            opcode_counts[op] += 1
            if not defs:
                continue
            counts["producer_instruction_count"] += 1
            counts["definition_entry_count"] += len(defs)
            producer_opcode_counts[op] += 1
            try:
                fam = sem.family(op)
            except Exception:
                fam = "UNCLASSIFIED_VALUE_OPCODE"
                bad_rows.append({"sha": sha, "instruction": x.get("index"), "address": x.get("address_hex"), "opcode": op, "defs": defs, "reason": "opcode_not_in_value_registry"})
            family_instruction_counts[fam] += 1
            family_opcode_sets[fam].add(op)
            for dst in defs:
                cls = dest_class(dst)
                dest_class_counts[cls] += 1
                if cls == "VGPR":
                    observed_vgpr_ops.add(op)
                elif cls in {"SGPR", "M0"}:
                    observed_scalar_ops.add(op)
                else:
                    observed_special_ops.add(op)
                if not allowed_for_dest(op, cls):
                    bad_rows.append({"sha": sha, "instruction": x.get("index"), "address": x.get("address_hex"), "opcode": op, "destination": dst, "destination_class": cls, "reason": "destination_effect_not_source_closed"})

    if counts["program_count"] != EXPECTED_PROGRAMS:
        violations.append(f"program_count:{counts['program_count']}!={EXPECTED_PROGRAMS}")
    if counts["instruction_count"] != EXPECTED_INSTRUCTIONS:
        violations.append(f"instruction_count:{counts['instruction_count']}!={EXPECTED_INSTRUCTIONS}")
    if dict(sorted(stage_counts.items())) != EXPECTED_STAGE:
        violations.append(f"stage_counts:{dict(sorted(stage_counts.items()))}!={EXPECTED_STAGE}")
    if observed_vgpr_ops != set(vgpr.VGPR_DEF_OPCODES):
        violations.append(f"vgpr_opcode_surface_missing_or_extra:{sorted(observed_vgpr_ops ^ set(vgpr.VGPR_DEF_OPCODES))}")
    if observed_scalar_ops != set(sgpr.OBSERVED_SGPR_DEF_OPCODES):
        violations.append(f"scalar_opcode_surface_missing_or_extra:{sorted(observed_scalar_ops ^ set(sgpr.OBSERVED_SGPR_DEF_OPCODES))}")
    if bad_rows:
        violations.append(f"unclosed_value_definition_rows:{len(bad_rows)}")

    observed_producer_ops = set(producer_opcode_counts)
    missing_registry_ops = observed_producer_ops - sem.VALUE_PRODUCER_OPCODES
    if missing_registry_ops:
        violations.append(f"unclassified_value_opcodes:{sorted(missing_registry_ops)}")

    return {
        "schema": SCHEMA,
        "status": STATUS if not violations else "D1_GCN_VALUE_MACHINE_FRONTIER_WITH_VIOLATIONS",
        "sources": {"ir_dir": str(ir_dir), "structural_census": str(census_path)},
        "coverage": {
            "exact_program_count": counts["program_count"],
            "stage_program_counts": dict(sorted(stage_counts.items())),
            "exact_instruction_count": counts["instruction_count"],
            "value_producer_instruction_count": counts["producer_instruction_count"],
            "definition_entry_count": counts["definition_entry_count"],
            "observed_value_producer_opcode_count": len(observed_producer_ops),
            "source_closed_registry_opcode_count": len(sem.VALUE_PRODUCER_OPCODES),
            "observed_vgpr_result_opcode_count": len(observed_vgpr_ops),
            "observed_scalar_result_opcode_count": len(observed_scalar_ops),
            "observed_special_result_opcode_count": len(observed_special_ops),
            "destination_class_counts": dict(sorted(dest_class_counts.items())),
            "operation_family_instruction_counts": dict(sorted(family_instruction_counts.items())),
            "operation_family_opcode_counts": {k: len(v) for k, v in sorted(family_opcode_sets.items())},
            "value_producer_opcode_counts": dict(sorted(producer_opcode_counts.items())),
            "unclosed_value_definition_row_count": len(bad_rows),
            "shader_expression_semantic_promotions": 0,
        },
        "unclosed_examples": bad_rows[:100],
        "violations": violations,
        "semantic_boundary": {
            "exec_condition_vgpr_sgpr_ssa": "GLOBAL_EXACT_PREREQUISITE",
            "value_producer_operation_identity": "GLOBAL_EXACT" if not violations else "NOT_PROMOTED",
            "ordered_native_operand_provenance": "GLOBAL_EXACT" if not violations else "NOT_PROMOTED",
            "expression_dag_binding": "NEXT_GATE" if not violations else "WITHHELD",
            "algebraic_expression_lowering": "WITHHELD",
            "resource_role_semantics": "WITHHELD",
            "material_semantics": "WITHHELD",
            "shader_expression_semantic_promotions": 0,
        },
        "policy": "Every structural definition is checked against a frozen source-backed destination machine registry and a source-backed value-operation family. Any new result opcode, destination class or unsupported special-register effect fails closed. No high-level shader or material meaning is inferred.",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ir-dir", type=Path, required=True)
    ap.add_argument("--structural-census", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()
    out = run(a.ir_dir, a.structural_census)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": out["status"], "coverage": out["coverage"], "violations": out["violations"][:20]}, indent=2, sort_keys=True))
    return 0 if not out["violations"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
