#!/usr/bin/env python3
"""Corpus-wide proof that all source-closed D1 vector formulas bind into existing lane SSA."""
from __future__ import annotations

import argparse
import collections
import json
import multiprocessing as mp
import os
from pathlib import Path

import d1_gcn_vector_formula_lane_binding_v1 as binding
import d1_gcn_vector_formula_semantics_v1 as sem

CENSUS_STATUS = "D1_GCN_SHADER_CORPUS_STRUCTURAL_CENSUS_COMPLETE"
VECTOR_STATUS = "D1_GCN_VECTOR_VALUE_OPERAND_FRONTIER_EXACT"
FORMULA_STATUS = "D1_GCN_VECTOR_BASE_FORMULA_FRONTIER_EXACT"
BIND_STATUS = "D1_GCN_VECTOR_FORMULA_LANE_BINDING_EXACT"
SCHEMA = "d1_gcn_vector_formula_lane_binding_corpus_replay/v1"
STATUS = "D1_GCN_VECTOR_FORMULA_LANE_BINDING_CORPUS_EXACT"
EXPECTED_PROGRAMS = 26_464
EXPECTED_INSTRUCTIONS = 4_896_165
EXPECTED_FORMULA_INSTRUCTIONS = 2_994_322
EXPECTED_FORMULA_COMPONENTS = 2_994_369
EXPECTED_BIT_INSTRUCTIONS = 389_102
EXPECTED_BIT_COMPONENTS = 389_149
EXPECTED_SYMBOLIC_INSTRUCTIONS = 2_605_220
EXPECTED_SYMBOLIC_COMPONENTS = 2_605_220
EXPECTED_TOTAL_VGPR_COMPONENTS = 3_864_039
EXPECTED_NONFORMULA_COMPONENTS = EXPECTED_TOTAL_VGPR_COMPONENTS - EXPECTED_FORMULA_COMPONENTS
EXPECTED_STAGE = {"DS": 20, "PS": 18_375, "VS": 8_069}
EXPECTED_MODIFIERS = {"abs": 47_624, "neg": 158_330, "omod": 28_931, "clamp": 129_395, "touched": 313_444}


def worker(path: str) -> dict:
    p = Path(path)
    sha = p.stem.lower()
    try:
        d = binding.analyze(json.loads(p.read_text()))
        c = d.get("coverage") or {}
        return {
            "sha": sha,
            "ok": d.get("status") == BIND_STATUS and not d.get("violations"),
            "status": d.get("status"),
            "violations": (d.get("violations") or [])[:5],
            "instructions": d.get("instruction_count", 0),
            "nodes": d.get("node_count", 0),
            "formula_instructions": c.get("formula_instruction_count", 0),
            "formula_components": c.get("formula_result_component_binding_count", 0),
            "write_bindings": c.get("physical_write_binding_count", 0),
            "raw_input_accounting": c.get("formula_raw_input_accounting_instruction_count", 0),
            "bit_instructions": c.get("bit_exact_instruction_count", 0),
            "bit_components": c.get("bit_exact_result_component_count", 0),
            "symbolic_instructions": c.get("symbolic_instruction_count", 0),
            "symbolic_components": c.get("symbolic_result_component_count", 0),
            "nonformula_components": c.get("opaque_nonformula_result_component_count", 0),
            "mode_snapshots": c.get("mode_snapshot_instruction_count", 0),
            "old_dest_instructions": c.get("old_destination_arithmetic_input_instruction_count", 0),
            "old_dest_components": c.get("old_destination_arithmetic_input_component_count", 0),
            "abs": c.get("abs_modifier_instruction_count", 0),
            "neg": c.get("neg_modifier_instruction_count", 0),
            "omod": c.get("omod_modifier_instruction_count", 0),
            "clamp": c.get("clamp_modifier_instruction_count", 0),
            "touched": c.get("modifier_touched_instruction_count", 0),
            "promotions": c.get("shader_expression_semantic_promotions", 0),
            "op_instructions": c.get("formula_opcode_instruction_counts") or {},
            "op_components": c.get("formula_opcode_component_counts") or {},
        }
    except Exception as e:
        return {"sha": sha, "ok": False, "exception": f"{type(e).__name__}:{e}"}


def replay(ir_dir: Path, census_path: Path, vector_path: Path, formula_path: Path, workers: int) -> dict:
    violations: list[str] = []
    census = json.loads(census_path.read_text())
    vector = json.loads(vector_path.read_text())
    formula = json.loads(formula_path.read_text())
    if census.get("status") != CENSUS_STATUS:
        violations.append(f"census_status:{census.get('status')!r}")
    if vector.get("status") != VECTOR_STATUS or vector.get("violations"):
        violations.append(f"vector_frontier:{vector.get('status')!r}")
    if formula.get("status") != FORMULA_STATUS or formula.get("violations"):
        violations.append(f"formula_frontier:{formula.get('status')!r}")

    stages = {p["gcn_sha256"]: (p.get("stages") or []) for p in census.get("programs") or []}
    if len(stages) != EXPECTED_PROGRAMS:
        violations.append(f"stage_map:{len(stages)}!={EXPECTED_PROGRAMS}")
    paths = sorted(ir_dir.glob("*.json"))
    if len(paths) != EXPECTED_PROGRAMS:
        violations.append(f"ir_file_count:{len(paths)}!={EXPECTED_PROGRAMS}")

    totals = collections.Counter()
    stage_counts = collections.Counter()
    opi = collections.Counter()
    opc = collections.Counter()
    rows = []
    pool = None
    iterator = map(worker, map(str, paths))
    if workers > 1:
        pool = mp.Pool(workers)
        iterator = pool.imap_unordered(worker, map(str, paths), chunksize=8)
    try:
        for r in iterator:
            sha = r["sha"]
            st = stages.get(sha)
            if not st or len(st) != 1:
                violations.append(f"stage:{sha}:{st}")
                continue
            stage_counts[st[0]] += 1
            if not r.get("ok"):
                violations.append(f"analyze:{sha}:{r.get('exception') or (r.get('status'), r.get('violations'))}")
                continue
            for k in (
                "instructions", "nodes", "formula_instructions", "formula_components", "write_bindings",
                "raw_input_accounting", "bit_instructions", "bit_components", "symbolic_instructions",
                "symbolic_components", "nonformula_components", "mode_snapshots", "old_dest_instructions",
                "old_dest_components", "abs", "neg", "omod", "clamp", "touched", "promotions",
            ):
                totals[k] += r[k]
            opi.update(r["op_instructions"])
            opc.update(r["op_components"])
            rows.append({
                "gcn_sha256": sha,
                "stage": st[0],
                "formula_instruction_count": r["formula_instructions"],
                "formula_result_component_count": r["formula_components"],
                "bit_exact_result_component_count": r["bit_components"],
            })
    finally:
        if pool:
            pool.close()
            pool.join()
    rows.sort(key=lambda x: x["gcn_sha256"])

    exact_checks = {
        "programs": (len(rows), EXPECTED_PROGRAMS),
        "instructions": (totals["instructions"], EXPECTED_INSTRUCTIONS),
        "formula_instructions": (totals["formula_instructions"], EXPECTED_FORMULA_INSTRUCTIONS),
        "formula_components": (totals["formula_components"], EXPECTED_FORMULA_COMPONENTS),
        "write_bindings": (totals["write_bindings"], EXPECTED_FORMULA_COMPONENTS),
        "raw_input_accounting": (totals["raw_input_accounting"], EXPECTED_FORMULA_INSTRUCTIONS),
        "bit_instructions": (totals["bit_instructions"], EXPECTED_BIT_INSTRUCTIONS),
        "bit_components": (totals["bit_components"], EXPECTED_BIT_COMPONENTS),
        "symbolic_instructions": (totals["symbolic_instructions"], EXPECTED_SYMBOLIC_INSTRUCTIONS),
        "symbolic_components": (totals["symbolic_components"], EXPECTED_SYMBOLIC_COMPONENTS),
        "nonformula_components": (totals["nonformula_components"], EXPECTED_NONFORMULA_COMPONENTS),
    }
    for k, (got, want) in exact_checks.items():
        if got != want:
            violations.append(f"{k}:{got}!={want}")
    if dict(sorted(stage_counts.items())) != EXPECTED_STAGE:
        violations.append(f"stage_counts:{dict(stage_counts)}!={EXPECTED_STAGE}")
    for k, want in EXPECTED_MODIFIERS.items():
        if totals[k] != want:
            violations.append(f"modifier_{k}:{totals[k]}!={want}")
    if totals["promotions"] != 0:
        violations.append(f"shader_expression_semantic_promotions:{totals['promotions']}")

    vc = vector.get("coverage") or {}
    expected_opi = {op: (vc.get("opcode_instruction_counts") or {}).get(op, 0) for op in sorted(sem.PENDING)}
    expected_opc = {op: (vc.get("opcode_def_entry_counts") or {}).get(op, 0) for op in sorted(sem.PENDING)}
    if dict(sorted(opi.items())) != expected_opi:
        violations.append("formula_opcode_instruction_histogram_mismatch")
    if dict(sorted(opc.items())) != expected_opc:
        violations.append("formula_opcode_component_histogram_mismatch")
    if set(opi) != sem.PENDING:
        violations.append(f"formula_opcode_surface:{sorted(opi)}!={sorted(sem.PENDING)}")

    expected_mode = sum(expected_opi[op] for op in sem.PENDING if sem.FORMULAS[op]["fp_state_policy"] != "NOT_APPLICABLE")
    if totals["mode_snapshots"] != expected_mode:
        violations.append(f"mode_snapshot_instruction_count:{totals['mode_snapshots']}!={expected_mode}")
    expected_old_dest = sum(expected_opi[op] for op in sem.PENDING if sem.FORMULAS[op]["old_destination_is_input"])
    expected_old_dest_components = sum(expected_opc[op] for op in sem.PENDING if sem.FORMULAS[op]["old_destination_is_input"])
    if totals["old_dest_instructions"] != expected_old_dest:
        violations.append(f"old_destination_instruction_count:{totals['old_dest_instructions']}!={expected_old_dest}")
    if totals["old_dest_components"] != expected_old_dest_components:
        violations.append(f"old_destination_component_count:{totals['old_dest_components']}!={expected_old_dest_components}")

    fc = formula.get("coverage") or {}
    reconciliations = {
        "formula_instruction_count": totals["formula_instructions"],
        "formula_result_component_count": totals["formula_components"],
        "bit_exact_replay_ready_instruction_count": totals["bit_instructions"],
        "bit_exact_replay_ready_result_component_count": totals["bit_components"],
        "floating_or_special_symbolic_instruction_count": totals["symbolic_instructions"],
        "modifier_touched_instruction_count": totals["touched"],
        "neg_modifier_instruction_count": totals["neg"],
        "abs_modifier_instruction_count": totals["abs"],
        "omod_modifier_instruction_count": totals["omod"],
        "clamp_modifier_instruction_count": totals["clamp"],
    }
    for remote, got in reconciliations.items():
        if fc.get(remote) != got:
            violations.append(f"formula_frontier_reconcile:{remote}:{got}!={fc.get(remote)}")

    coverage = {
        "exact_programs_replayed": len(rows),
        "stage_program_counts": dict(sorted(stage_counts.items())),
        "exact_instructions_replayed": totals["instructions"],
        "formula_instruction_count": totals["formula_instructions"],
        "formula_result_component_binding_count": totals["formula_components"],
        "physical_write_binding_count": totals["write_bindings"],
        "formula_raw_input_accounting_instruction_count": totals["raw_input_accounting"],
        "bit_exact_instruction_count": totals["bit_instructions"],
        "bit_exact_result_component_count": totals["bit_components"],
        "symbolic_formula_instruction_count": totals["symbolic_instructions"],
        "symbolic_formula_result_component_count": totals["symbolic_components"],
        "opaque_nonformula_result_component_count": totals["nonformula_components"],
        "mode_snapshot_instruction_count": totals["mode_snapshots"],
        "old_destination_arithmetic_input_instruction_count": totals["old_dest_instructions"],
        "old_destination_arithmetic_input_component_count": totals["old_dest_components"],
        "modifier_touched_instruction_count": totals["touched"],
        "abs_modifier_instruction_count": totals["abs"],
        "neg_modifier_instruction_count": totals["neg"],
        "omod_modifier_instruction_count": totals["omod"],
        "clamp_modifier_instruction_count": totals["clamp"],
        "formula_opcode_instruction_counts": dict(sorted(opi.items())),
        "formula_opcode_component_counts": dict(sorted(opc.items())),
        "integrated_graph_node_count": totals["nodes"],
        "shader_expression_semantic_promotions": totals["promotions"],
    }
    return {
        "schema": SCHEMA,
        "status": STATUS if not violations else "D1_GCN_VECTOR_FORMULA_LANE_BINDING_CORPUS_WITH_VIOLATIONS",
        "sources": {
            "ir_dir": str(ir_dir),
            "structural_census": str(census_path),
            "vector_frontier": str(vector_path),
            "formula_frontier": str(formula_path),
        },
        "coverage": coverage,
        "programs": rows,
        "violations": violations,
        "semantic_boundary": {
            "formula_result_to_lane_candidate_binding": "GLOBAL_EXACT" if not violations else "NOT_PROMOTED",
            "formula_result_to_physical_write_binding": "GLOBAL_EXACT" if not violations else "NOT_PROMOTED",
            "bit_exact_integer_value_nodes": "GLOBAL_EXECUTABLE_ARCHITECTURAL_NODES" if not violations else "NOT_PROMOTED",
            "floating_special_value_nodes": "GLOBAL_SOURCE_CLOSED_SYMBOLIC_MODE_RETAINED",
            "mac_old_destination_role_separation": "GLOBAL_EXACT" if not violations else "NOT_PROMOTED",
            "vop3_abs_neg_omod_order": "GLOBAL_SOURCE_CLOSED_EXPLICIT",
            "vop3_clamp_numeric_range": "WITHHELD_AMD_REV1_3_INTERNAL_SOURCE_CONFLICT",
            "resource_lds_interpolation_values": "UNCHANGED_OPAQUE_BOUNDARIES",
            "shader_expression_semantics": "WITHHELD",
            "material_semantics": "WITHHELD",
            "shader_expression_semantic_promotions": 0,
        },
        "policy": (
            "Every source-documented formula result component must bind exactly once to the pre-existing lane-SSA "
            "result candidate and exactly once to its pre-existing physical write. Integer/bit formulas are executable "
            "bit-pattern nodes; floating/special formulas remain source-closed symbolic nodes with MODE state retained. "
            "No resource/interpolation value or shader/material intent is inferred."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ir-dir", type=Path, required=True)
    ap.add_argument("--structural-census", type=Path, required=True)
    ap.add_argument("--vector-frontier", type=Path, required=True)
    ap.add_argument("--formula-frontier", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=max(1, min(4, os.cpu_count() or 1)))
    a = ap.parse_args()
    out = replay(a.ir_dir, a.structural_census, a.vector_frontier, a.formula_frontier, a.workers)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": out["status"], "coverage": out["coverage"], "violations": out["violations"][:30]}, indent=2, sort_keys=True))
    return 0 if not out["violations"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
