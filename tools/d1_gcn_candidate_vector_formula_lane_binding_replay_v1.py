#!/usr/bin/env python3
"""Replay any exact D1 GCN candidate corpus through universal formula-to-lane binding.

The candidate denominator is derived from frozen prerequisite reports. Stage labels do not
change decoding or value semantics. The per-program analyzer is the existing universal
`d1_gcn_vector_formula_lane_binding_v1.analyze`; this wrapper only reconciles exact corpus
accounting against the candidate value, formula and VGPR-lane checkpoints.
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

import d1_gcn_vector_formula_lane_binding_v1 as binding
import d1_gcn_vector_formula_semantics_v1 as sem

STRUCT_STATUS = "D1_GCN_SOURCE_CLOSED_STRUCTURAL_PROMOTION_EXACT"
LANE_REPORT_STATUS = "D1_GCN_CANDIDATE_VGPR_LANE_SSA_REPLAY_EXACT"
VALUE_STATUS = "D1_GCN_CANDIDATE_VECTOR_VALUE_FRONTIER_EXACT"
FORMULA_STATUS = "D1_GCN_CANDIDATE_VECTOR_BASE_FORMULA_FRONTIER_EXACT"
BIND_STATUS = "D1_GCN_VECTOR_FORMULA_LANE_BINDING_EXACT"
SCHEMA = "d1_gcn_candidate_vector_formula_lane_binding_replay/v1"
STATUS = "D1_GCN_CANDIDATE_VECTOR_FORMULA_LANE_BINDING_REPLAY_EXACT"


def analyze_one(path: Path, output_dir: Path | None) -> dict:
    sha = path.stem.lower()
    try:
        out = binding.analyze(json.loads(path.read_text()))
        if output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / f"{sha}.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
        c = out.get("coverage") or {}
        return {
            "gcn_sha256": sha,
            "ok": out.get("status") == BIND_STATUS and not out.get("violations"),
            "status": out.get("status"),
            "violations": (out.get("violations") or [])[:8],
            "instruction_count": out.get("instruction_count", 0),
            "node_count": out.get("node_count", 0),
            "formula_instruction_count": c.get("formula_instruction_count", 0),
            "formula_result_component_count": c.get("formula_result_component_binding_count", 0),
            "physical_write_binding_count": c.get("physical_write_binding_count", 0),
            "formula_raw_input_accounting_instruction_count": c.get("formula_raw_input_accounting_instruction_count", 0),
            "bit_exact_instruction_count": c.get("bit_exact_instruction_count", 0),
            "bit_exact_result_component_count": c.get("bit_exact_result_component_count", 0),
            "symbolic_instruction_count": c.get("symbolic_instruction_count", 0),
            "symbolic_result_component_count": c.get("symbolic_result_component_count", 0),
            "opaque_nonformula_result_component_count": c.get("opaque_nonformula_result_component_count", 0),
            "mode_snapshot_instruction_count": c.get("mode_snapshot_instruction_count", 0),
            "old_destination_arithmetic_input_instruction_count": c.get("old_destination_arithmetic_input_instruction_count", 0),
            "old_destination_arithmetic_input_component_count": c.get("old_destination_arithmetic_input_component_count", 0),
            "modifier_touched_instruction_count": c.get("modifier_touched_instruction_count", 0),
            "abs_modifier_instruction_count": c.get("abs_modifier_instruction_count", 0),
            "neg_modifier_instruction_count": c.get("neg_modifier_instruction_count", 0),
            "omod_modifier_instruction_count": c.get("omod_modifier_instruction_count", 0),
            "clamp_modifier_instruction_count": c.get("clamp_modifier_instruction_count", 0),
            "formula_opcode_instruction_counts": c.get("formula_opcode_instruction_counts") or {},
            "formula_opcode_component_counts": c.get("formula_opcode_component_counts") or {},
            "shader_expression_semantic_promotions": c.get("shader_expression_semantic_promotions", 0),
        }
    except Exception as e:
        return {"gcn_sha256": sha, "ok": False, "exception": f"{type(e).__name__}:{e}"}


def replay(struct_path: Path, lane_path: Path, value_path: Path, formula_path: Path,
           ir_dir: Path, binding_dir: Path | None) -> dict:
    violations: list[str] = []
    struct = json.loads(struct_path.read_text())
    lane = json.loads(lane_path.read_text())
    value = json.loads(value_path.read_text())
    formula = json.loads(formula_path.read_text())

    for name, doc, status in (
        ("structural", struct, STRUCT_STATUS),
        ("lane", lane, LANE_REPORT_STATUS),
        ("value", value, VALUE_STATUS),
        ("formula", formula, FORMULA_STATUS),
    ):
        if doc.get("status") != status or doc.get("violations"):
            violations.append(f"prerequisite:{name}:{doc.get('status')!r}:{len(doc.get('violations') or [])}")

    roster = sorted(str(x.get("gcn_sha256", "")).lower() for x in (struct.get("programs") or []))
    if not roster or len(roster) != len(set(roster)):
        violations.append(f"structural_roster_invalid:{len(roster)}:{len(set(roster))}")
    paths = {p.stem.lower(): p for p in ir_dir.glob("*.json")}
    if set(paths) != set(roster):
        violations.append(f"ir_roster_mismatch:expected={len(roster)}:actual={len(paths)}")

    lc = lane.get("coverage") or {}
    vc = value.get("coverage") or {}
    fc = formula.get("coverage") or {}
    expected_programs = len(roster)
    expected_instructions = int(lc.get("exact_instructions_replayed", -1))
    expected_formula_instructions = int(fc.get("formula_instruction_count", -1))
    expected_formula_components = int(fc.get("formula_result_component_count", -1))
    expected_bit_instructions = int(fc.get("bit_exact_replay_ready_instruction_count", -1))
    expected_bit_components = int(fc.get("bit_exact_replay_ready_result_component_count", -1))
    expected_symbolic_instructions = int(fc.get("floating_or_special_symbolic_instruction_count", -1))
    expected_symbolic_components = expected_formula_components - expected_bit_components
    expected_nonformula_components = int(lc.get("vgpr_def_entry_count", -1)) - expected_formula_components
    expected_formula_ops = set(formula.get("candidate_formula_opcodes") or [])

    rows = []
    totals = collections.Counter()
    opi = collections.Counter()
    opc = collections.Counter()
    for sha in roster:
        p = paths.get(sha)
        if p is None:
            continue
        r = analyze_one(p, binding_dir)
        if not r.get("ok"):
            violations.append(f"analyze:{sha}:{r.get('exception') or (r.get('status'), r.get('violations'))}")
            continue
        rows.append(r)
        for k in (
            "instruction_count", "node_count", "formula_instruction_count",
            "formula_result_component_count", "physical_write_binding_count",
            "formula_raw_input_accounting_instruction_count", "bit_exact_instruction_count",
            "bit_exact_result_component_count", "symbolic_instruction_count",
            "symbolic_result_component_count", "opaque_nonformula_result_component_count",
            "mode_snapshot_instruction_count", "old_destination_arithmetic_input_instruction_count",
            "old_destination_arithmetic_input_component_count", "modifier_touched_instruction_count",
            "abs_modifier_instruction_count", "neg_modifier_instruction_count",
            "omod_modifier_instruction_count", "clamp_modifier_instruction_count",
            "shader_expression_semantic_promotions",
        ):
            totals[k] += int(r.get(k, 0))
        opi.update(r.get("formula_opcode_instruction_counts") or {})
        opc.update(r.get("formula_opcode_component_counts") or {})

    checks = {
        "programs": (len(rows), expected_programs),
        "instructions": (totals["instruction_count"], expected_instructions),
        "formula_instructions": (totals["formula_instruction_count"], expected_formula_instructions),
        "formula_components": (totals["formula_result_component_count"], expected_formula_components),
        "physical_write_bindings": (totals["physical_write_binding_count"], expected_formula_components),
        "raw_input_accounting": (totals["formula_raw_input_accounting_instruction_count"], expected_formula_instructions),
        "bit_exact_instructions": (totals["bit_exact_instruction_count"], expected_bit_instructions),
        "bit_exact_components": (totals["bit_exact_result_component_count"], expected_bit_components),
        "symbolic_instructions": (totals["symbolic_instruction_count"], expected_symbolic_instructions),
        "symbolic_components": (totals["symbolic_result_component_count"], expected_symbolic_components),
        "opaque_nonformula_components": (totals["opaque_nonformula_result_component_count"], expected_nonformula_components),
        "modifier_touched": (totals["modifier_touched_instruction_count"], int(fc.get("modifier_touched_instruction_count", -1))),
        "modifier_abs": (totals["abs_modifier_instruction_count"], int(fc.get("abs_modifier_instruction_count", -1))),
        "modifier_neg": (totals["neg_modifier_instruction_count"], int(fc.get("neg_modifier_instruction_count", -1))),
        "modifier_omod": (totals["omod_modifier_instruction_count"], int(fc.get("omod_modifier_instruction_count", -1))),
        "modifier_clamp": (totals["clamp_modifier_instruction_count"], int(fc.get("clamp_modifier_instruction_count", -1))),
        "semantic_promotions": (totals["shader_expression_semantic_promotions"], 0),
    }
    for key, (got, want) in checks.items():
        if got != want:
            violations.append(f"accounting:{key}:{got}!={want}")

    expected_opi = {op: int((vc.get("opcode_instruction_counts") or {}).get(op, 0)) for op in sorted(expected_formula_ops)}
    expected_opc = {op: int((vc.get("opcode_def_entry_counts") or {}).get(op, 0)) for op in sorted(expected_formula_ops)}
    if dict(sorted(opi.items())) != expected_opi:
        violations.append("formula_opcode_instruction_histogram_mismatch")
    if dict(sorted(opc.items())) != expected_opc:
        violations.append("formula_opcode_component_histogram_mismatch")
    if set(opi) != expected_formula_ops:
        violations.append(f"formula_opcode_surface:{sorted(opi)}!={sorted(expected_formula_ops)}")

    expected_mode = sum(expected_opi[op] for op in expected_formula_ops if sem.FORMULAS[op]["fp_state_policy"] != "NOT_APPLICABLE")
    expected_old_i = sum(expected_opi[op] for op in expected_formula_ops if sem.FORMULAS[op]["old_destination_is_input"])
    expected_old_c = sum(expected_opc[op] for op in expected_formula_ops if sem.FORMULAS[op]["old_destination_is_input"])
    if totals["mode_snapshot_instruction_count"] != expected_mode:
        violations.append(f"mode_snapshot_instruction_count:{totals['mode_snapshot_instruction_count']}!={expected_mode}")
    if totals["old_destination_arithmetic_input_instruction_count"] != expected_old_i:
        violations.append(f"old_destination_instruction_count:{totals['old_destination_arithmetic_input_instruction_count']}!={expected_old_i}")
    if totals["old_destination_arithmetic_input_component_count"] != expected_old_c:
        violations.append(f"old_destination_component_count:{totals['old_destination_arithmetic_input_component_count']}!={expected_old_c}")

    compact_rows = [{
        "gcn_sha256": r["gcn_sha256"],
        "instruction_count": r["instruction_count"],
        "formula_instruction_count": r["formula_instruction_count"],
        "formula_result_component_count": r["formula_result_component_count"],
        "bit_exact_instruction_count": r["bit_exact_instruction_count"],
    } for r in rows]
    coverage = {
        "planned_unique_gcn_programs": expected_programs,
        "exact_formula_lane_bound_unique_gcn_programs": len(rows),
        "exact_instructions_replayed": totals["instruction_count"],
        "formula_instruction_count": totals["formula_instruction_count"],
        "formula_result_component_binding_count": totals["formula_result_component_count"],
        "physical_write_binding_count": totals["physical_write_binding_count"],
        "formula_raw_input_accounting_instruction_count": totals["formula_raw_input_accounting_instruction_count"],
        "bit_exact_instruction_count": totals["bit_exact_instruction_count"],
        "bit_exact_result_component_count": totals["bit_exact_result_component_count"],
        "symbolic_formula_instruction_count": totals["symbolic_instruction_count"],
        "symbolic_formula_result_component_count": totals["symbolic_result_component_count"],
        "opaque_nonformula_result_component_count": totals["opaque_nonformula_result_component_count"],
        "mode_snapshot_instruction_count": totals["mode_snapshot_instruction_count"],
        "old_destination_arithmetic_input_instruction_count": totals["old_destination_arithmetic_input_instruction_count"],
        "old_destination_arithmetic_input_component_count": totals["old_destination_arithmetic_input_component_count"],
        "modifier_touched_instruction_count": totals["modifier_touched_instruction_count"],
        "abs_modifier_instruction_count": totals["abs_modifier_instruction_count"],
        "neg_modifier_instruction_count": totals["neg_modifier_instruction_count"],
        "omod_modifier_instruction_count": totals["omod_modifier_instruction_count"],
        "clamp_modifier_instruction_count": totals["clamp_modifier_instruction_count"],
        "formula_opcode_instruction_counts": dict(sorted(opi.items())),
        "formula_opcode_component_counts": dict(sorted(opc.items())),
        "integrated_graph_node_count": totals["node_count"],
        "shader_expression_semantic_promotions": totals["shader_expression_semantic_promotions"],
    }
    return {
        "schema": SCHEMA,
        "status": STATUS if not violations else "D1_GCN_CANDIDATE_VECTOR_FORMULA_LANE_BINDING_REPLAY_WITH_VIOLATIONS",
        "sources": {
            "structural_source_closure": str(struct_path),
            "lane_ssa_report": str(lane_path),
            "vector_value_frontier": str(value_path),
            "vector_formula_frontier": str(formula_path),
            "ir_dir": str(ir_dir),
        },
        "coverage": coverage,
        "programs": compact_rows,
        "violations": violations,
        "semantic_boundary": {
            "candidate_stage_affects_formula_lane_analyzer": False,
            "physical_vgpr_lane_ssa": "REUSED_WITH_IDENTITIES_UNCHANGED",
            "formula_result_to_lane_candidate_binding": "EXACT" if not violations else "NOT_PROMOTED",
            "formula_result_to_physical_write_binding": "EXACT" if not violations else "NOT_PROMOTED",
            "integer_bit_exact_operations": "EXECUTABLE_ARCHITECTURAL_NODES" if not violations else "NOT_PROMOTED",
            "floating_special_operations": "SOURCE_CLOSED_SYMBOLIC_MODE_RETAINED",
            "vop3_clamp_numeric_range": "WITHHELD_AMD_REV1_3_INTERNAL_SOURCE_CONFLICT",
            "resource_lds_interpolation_values": "UNCHANGED_OPAQUE_BOUNDARIES",
            "shader_expression_semantic_promotions": 0
        },
        "policy": "The exact candidate corpus is replayed through the unchanged universal formula-to-lane analyzer. Expected totals are derived from frozen candidate prerequisites rather than a hardcoded stage denominator. Every formula result must reuse the existing lane result and physical-write identities; no shader or material meaning is promoted."
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--structural-source-closure", type=Path, required=True)
    ap.add_argument("--lane-ssa-report", type=Path, required=True)
    ap.add_argument("--vector-frontier", type=Path, required=True)
    ap.add_argument("--formula-frontier", type=Path, required=True)
    ap.add_argument("--ir-dir", type=Path, required=True)
    ap.add_argument("--binding-dir", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()
    out = replay(a.structural_source_closure, a.lane_ssa_report, a.vector_frontier,
                 a.formula_frontier, a.ir_dir, a.binding_dir)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    c = out["coverage"]
    print("STATUS", out["status"], "PROGRAMS", f"{c['exact_formula_lane_bound_unique_gcn_programs']}/{c['planned_unique_gcn_programs']}",
          "FORMULAS", c["formula_instruction_count"], "COMPONENTS", c["formula_result_component_binding_count"],
          "BIT_EXACT", c["bit_exact_instruction_count"], "SYMBOLIC", c["symbolic_formula_instruction_count"],
          "VIOLATIONS", len(out["violations"]))
    for v in out["violations"][:100]:
        print("VIOLATION", v)
    return 0 if not out["violations"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
