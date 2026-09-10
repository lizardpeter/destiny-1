#!/usr/bin/env python3
"""Replay any exact D1 GCN candidate through universal formula source-state binding.

This wrapper does not decode shader stages or invent resource/material semantics. It calls the
existing `d1_gcn_vector_formula_source_binding_v1.analyze` unchanged for every exact structural
IR and reconciles the resulting VGPR/SGPR/literal source identities against frozen candidate
formula-lane and scalar-SSA prerequisites.
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

import d1_gcn_vector_formula_semantics_v1 as sem
import d1_gcn_vector_formula_source_binding_v1 as binding

STRUCT_STATUS = "D1_GCN_SOURCE_CLOSED_STRUCTURAL_PROMOTION_EXACT"
FORMULA_LANE_STATUS = "D1_GCN_CANDIDATE_VECTOR_FORMULA_LANE_BINDING_REPLAY_EXACT"
SCALAR_REPORT_STATUS = "D1_GCN_CANDIDATE_SGPR_M0_SSA_REPLAY_EXACT"
BIND_STATUS = "D1_GCN_VECTOR_FORMULA_SOURCE_BINDING_EXACT"
SCHEMA = "d1_gcn_candidate_vector_formula_source_binding_replay/v1"
STATUS = "D1_GCN_CANDIDATE_VECTOR_FORMULA_SOURCE_BINDING_REPLAY_EXACT"


def analyze_one(path: Path, output_dir: Path | None) -> dict:
    sha = path.stem.lower()
    try:
        out = binding.analyze(json.loads(path.read_text()))
        if output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / f"{sha}.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
        c = out.get("source_binding_coverage") or {}
        kind_by_opcode = collections.Counter()
        for b in out.get("formula_source_bindings") or []:
            kind_by_opcode[(str(b.get("opcode")), str(b.get("kind")))] += 1
        return {
            "gcn_sha256": sha,
            "ok": out.get("status") == BIND_STATUS and not out.get("violations"),
            "status": out.get("status"),
            "violations": (out.get("violations") or [])[:8],
            "instruction_count": out.get("instruction_count", 0),
            "formula_instruction_count": c.get("formula_instruction_count", 0),
            "expected_source_slot_count": c.get("expected_source_slot_count", 0),
            "exact_source_slot_count": c.get("exact_source_slot_count", 0),
            "vgpr_source_slot_count": c.get("vgpr_source_slot_count", 0),
            "sgpr_source_slot_count": c.get("sgpr_source_slot_count", 0),
            "literal_source_slot_count": c.get("literal_source_slot_count", 0),
            "sgpr_placeholder_replacement_count": c.get("sgpr_placeholder_replacement_count", 0),
            "formula_source_placeholder_leak_count": c.get("formula_source_placeholder_leak_count", 0),
            "integrated_vector_node_count": c.get("integrated_vector_node_count", 0),
            "scalar_ssa_node_count": c.get("scalar_ssa_node_count", 0),
            "scalar_state_kind_counts": c.get("scalar_state_kind_counts") or {},
            "opcode_source_slot_counts": c.get("opcode_source_slot_counts") or {},
            "kind_by_opcode": {f"{op}|{kind}": n for (op, kind), n in sorted(kind_by_opcode.items())},
            "shader_expression_semantic_promotions": c.get("shader_expression_semantic_promotions", 0),
        }
    except Exception as e:
        return {"gcn_sha256": sha, "ok": False, "exception": f"{type(e).__name__}:{e}"}


def replay(struct_path: Path, formula_lane_path: Path, scalar_path: Path,
           ir_dir: Path, output_dir: Path | None) -> dict:
    violations: list[str] = []
    struct = json.loads(struct_path.read_text())
    fl = json.loads(formula_lane_path.read_text())
    scalar = json.loads(scalar_path.read_text())
    for name, doc, status in (
        ("structural", struct, STRUCT_STATUS),
        ("formula_lane", fl, FORMULA_LANE_STATUS),
        ("scalar", scalar, SCALAR_REPORT_STATUS),
    ):
        if doc.get("status") != status or doc.get("violations"):
            violations.append(f"prerequisite:{name}:{doc.get('status')!r}:{len(doc.get('violations') or [])}")

    roster = sorted(str(x.get("gcn_sha256", "")).lower() for x in (struct.get("programs") or []))
    if not roster or len(roster) != len(set(roster)):
        violations.append(f"structural_roster_invalid:{len(roster)}:{len(set(roster))}")
    paths = {p.stem.lower(): p for p in ir_dir.glob("*.json")}
    if set(paths) != set(roster):
        violations.append(f"ir_roster_mismatch:expected={len(roster)}:actual={len(paths)}")

    fc = fl.get("coverage") or {}
    sc = scalar.get("coverage") or {}
    opi = fc.get("formula_opcode_instruction_counts") or {}
    expected_formula_instructions = int(fc.get("formula_instruction_count", -1))
    expected_sources = sum(int(n) * int(sem.FORMULAS[op]["explicit_source_count"]) for op, n in opi.items())
    expected_opcode_sources = {
        op: int(n) * int(sem.FORMULAS[op]["explicit_source_count"])
        for op, n in sorted(opi.items())
    }

    totals = collections.Counter()
    scalar_kinds = collections.Counter()
    opcode_sources = collections.Counter()
    kind_by_opcode = collections.Counter()
    rows = []
    for sha in roster:
        p = paths.get(sha)
        if p is None:
            continue
        r = analyze_one(p, output_dir)
        if not r.get("ok"):
            violations.append(f"analyze:{sha}:{r.get('exception') or (r.get('status'), r.get('violations'))}")
            continue
        rows.append(r)
        for k in (
            "instruction_count", "formula_instruction_count", "expected_source_slot_count",
            "exact_source_slot_count", "vgpr_source_slot_count", "sgpr_source_slot_count",
            "literal_source_slot_count", "sgpr_placeholder_replacement_count",
            "formula_source_placeholder_leak_count", "integrated_vector_node_count",
            "scalar_ssa_node_count", "shader_expression_semantic_promotions",
        ):
            totals[k] += int(r.get(k, 0))
        scalar_kinds.update(r.get("scalar_state_kind_counts") or {})
        opcode_sources.update(r.get("opcode_source_slot_counts") or {})
        kind_by_opcode.update(r.get("kind_by_opcode") or {})

    checks = {
        "programs": (len(rows), len(roster)),
        "instructions": (totals["instruction_count"], int(fc.get("exact_instructions_replayed", -1))),
        "formula_instructions": (totals["formula_instruction_count"], expected_formula_instructions),
        "expected_sources": (totals["expected_source_slot_count"], expected_sources),
        "exact_sources": (totals["exact_source_slot_count"], expected_sources),
        "source_partition": (
            totals["vgpr_source_slot_count"] + totals["sgpr_source_slot_count"] + totals["literal_source_slot_count"],
            expected_sources,
        ),
        "sgpr_replacements": (totals["sgpr_placeholder_replacement_count"], totals["sgpr_source_slot_count"]),
        "placeholder_leaks": (totals["formula_source_placeholder_leak_count"], 0),
        "scalar_nodes": (totals["scalar_ssa_node_count"], int(sc.get("scalar_ssa_node_count", -1))),
        "semantic_promotions": (totals["shader_expression_semantic_promotions"], 0),
    }
    for key, (got, want) in checks.items():
        if got != want:
            violations.append(f"accounting:{key}:{got}!={want}")
    if dict(sorted(opcode_sources.items())) != expected_opcode_sources:
        violations.append("opcode_source_slot_histogram_mismatch")

    # This is the exact architectural frontier that made LocalShader new: every one of its
    # 65 V_MUL_LO_I32 instances has one SGPR source. The source binder must therefore replace
    # exactly 65 instruction-local scalar placeholders for this opcode with SGPR-SSA references.
    mul_sgpr = int(kind_by_opcode.get("v_mul_lo_i32|SGPR_STATE", 0))
    if mul_sgpr != 65:
        violations.append(f"v_mul_lo_i32_sgpr_source_binding:{mul_sgpr}!=65")

    coverage = {
        "planned_unique_gcn_programs": len(roster),
        "exact_source_bound_unique_gcn_programs": len(rows),
        "exact_instructions_replayed": totals["instruction_count"],
        "formula_instruction_count": totals["formula_instruction_count"],
        "formula_source_slot_count": totals["expected_source_slot_count"],
        "exact_formula_source_binding_count": totals["exact_source_slot_count"],
        "vgpr_source_slot_count": totals["vgpr_source_slot_count"],
        "sgpr_source_slot_count": totals["sgpr_source_slot_count"],
        "literal_source_slot_count": totals["literal_source_slot_count"],
        "sgpr_placeholder_replacement_count": totals["sgpr_placeholder_replacement_count"],
        "formula_source_placeholder_leak_count": totals["formula_source_placeholder_leak_count"],
        "v_mul_lo_i32_sgpr_source_binding_count": mul_sgpr,
        "integrated_vector_node_count": totals["integrated_vector_node_count"],
        "scalar_ssa_node_count": totals["scalar_ssa_node_count"],
        "scalar_state_kind_counts": dict(sorted(scalar_kinds.items())),
        "opcode_source_slot_counts": dict(sorted(opcode_sources.items())),
        "source_kind_by_opcode_counts": dict(sorted(kind_by_opcode.items())),
        "shader_expression_semantic_promotions": totals["shader_expression_semantic_promotions"],
    }
    compact = [{
        "gcn_sha256": r["gcn_sha256"],
        "formula_instruction_count": r["formula_instruction_count"],
        "source_slot_count": r["exact_source_slot_count"],
        "sgpr_source_slot_count": r["sgpr_source_slot_count"],
    } for r in rows]
    return {
        "schema": SCHEMA,
        "status": STATUS if not violations else "D1_GCN_CANDIDATE_VECTOR_FORMULA_SOURCE_BINDING_REPLAY_WITH_VIOLATIONS",
        "sources": {
            "structural_source_closure": str(struct_path),
            "formula_lane_binding": str(formula_lane_path),
            "sgpr_m0_ssa": str(scalar_path),
            "ir_dir": str(ir_dir),
        },
        "coverage": coverage,
        "programs": compact,
        "violations": violations,
        "semantic_boundary": {
            "candidate_stage_affects_formula_source_analyzer": False,
            "formula_result_lane_binding": "EXACT_PREREQUISITE",
            "vgpr_formula_source_state_identity": "EXACT" if not violations else "NOT_PROMOTED",
            "sgpr_formula_source_state_identity": "EXACT_CROSS_GRAPH_REFERENCE" if not violations else "NOT_PROMOTED",
            "literal_formula_source_identity": "EXACT" if not violations else "NOT_PROMOTED",
            "instruction_local_sgpr_formula_source_placeholders": "ZERO_REMAINING" if not violations else "UNRESOLVED",
            "scalar_memory_values": "OPAQUE_RESOURCE_ADDRESS_WITHHELD",
            "resource_lds_interpolation_values": "NEXT_ARCHITECTURAL_VALUE_FRONTIER" if not violations else "WITHHELD",
            "shader_expression_semantics": "WITHHELD",
            "material_semantics": "WITHHELD",
            "shader_expression_semantic_promotions": 0,
        },
        "policy": "Every explicit formula source is attached to an existing architectural VGPR/SGPR state or exact encoded literal by the unchanged universal source binder. SGPR placeholders are replaced only by cross-graph references to the exact scalar SSA. Resource values and material intent remain withheld."
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--structural-source-closure", type=Path, required=True)
    ap.add_argument("--formula-lane-binding", type=Path, required=True)
    ap.add_argument("--sgpr-m0-ssa", type=Path, required=True)
    ap.add_argument("--ir-dir", type=Path, required=True)
    ap.add_argument("--binding-dir", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()
    out = replay(a.structural_source_closure, a.formula_lane_binding, a.sgpr_m0_ssa,
                 a.ir_dir, a.binding_dir)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    c = out["coverage"]
    print("STATUS", out["status"], "PROGRAMS", f"{c['exact_source_bound_unique_gcn_programs']}/{c['planned_unique_gcn_programs']}",
          "FORMULAS", c["formula_instruction_count"], "SOURCES", c["exact_formula_source_binding_count"],
          "VGPR", c["vgpr_source_slot_count"], "SGPR", c["sgpr_source_slot_count"],
          "LITERAL", c["literal_source_slot_count"], "LEAKS", c["formula_source_placeholder_leak_count"],
          "VIOLATIONS", len(out["violations"]))
    for v in out["violations"][:100]:
        print("VIOLATION", v)
    return 0 if not out["violations"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
