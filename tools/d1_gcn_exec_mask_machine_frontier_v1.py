#!/usr/bin/env python3
"""Join the exact structural EXEC census with source-closed implicit CMPX effects.

This closes the complete machine-level EXEC-touching opcode surface for the pinned
PS/VS/DS D1 corpus. It does not attempt symbolic propagation yet.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import d1_gcn_exec_mask_semantics_v1 as sem

EXEC_SCHEMA = "d1_gcn_exec_mask_opcode_frontier/v1"
EXEC_STATUS = "D1_GCN_EXEC_MASK_OPCODE_FRONTIER_EXACT"
CENSUS_STATUS = "D1_GCN_SHADER_CORPUS_STRUCTURAL_CENSUS_COMPLETE"
OUTPUT_SCHEMA = "d1_gcn_exec_mask_machine_frontier/v1"
OUTPUT_STATUS = "D1_GCN_EXEC_MASK_MACHINE_FRONTIER_EXACT"
EXPECTED_EXPLICIT_INSTRUCTIONS = 109678
EXPECTED_IMPLICIT_CMPX_INSTRUCTIONS = 12
EXPECTED_MACHINE_INSTRUCTIONS = 109690
EXPECTED_PROGRAMS = 18521
EXPECTED_OPCODES = {
    "s_and_b64": 1922,
    "s_and_saveexec_b64": 9305,
    "s_andn2_b64": 12581,
    "s_cbranch_execnz": 6,
    "s_cbranch_execz": 14822,
    "s_mov_b64": 51134,
    "s_wqm_b64": 19908,
    "v_cmpx_eq_i32": 6,
    "v_cmpx_lt_u32": 6,
}


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def build(exec_path: Path, census_path: Path) -> dict:
    violations = []
    ex = json.loads(exec_path.read_text())
    ce = json.loads(census_path.read_text())
    if ex.get("schema") != EXEC_SCHEMA:
        violations.append(f"exec_schema:{ex.get('schema')!r}")
    if ex.get("status") != EXEC_STATUS:
        violations.append(f"exec_status:{ex.get('status')!r}")
    if ex.get("violations"):
        violations.append(f"exec_violations:{len(ex['violations'])}")
    if ce.get("status") != CENSUS_STATUS:
        violations.append(f"census_status:{ce.get('status')!r}")
    if ce.get("violations"):
        violations.append(f"census_violations:{len(ce['violations'])}")
    bad = sem.validate_registry()
    if bad:
        violations.extend(f"registry:{x}" for x in bad)

    explicit = {x["opcode"]: int(x["instruction_count"]) for x in ex.get("opcodes") or []}
    explicit_total = sum(explicit.values())
    if explicit_total != EXPECTED_EXPLICIT_INSTRUCTIONS:
        violations.append(f"explicit_instruction_count:{explicit_total}!={EXPECTED_EXPLICIT_INSTRUCTIONS}")

    census_ops = {x["opcode"]: int(x["count"]) for x in (ce.get("census") or {}).get("opcodes") or []}
    cmpx_all = {op: n for op, n in census_ops.items() if op.startswith("v_cmpx_")}
    cmpx_expected = {op: EXPECTED_OPCODES[op] for op in EXPECTED_OPCODES if op.startswith("v_cmpx_")}
    if cmpx_all != cmpx_expected:
        violations.append(f"cmpx_opcode_surface:{cmpx_all!r}!={cmpx_expected!r}")

    joined = dict(explicit)
    joined.update(cmpx_all)
    if joined != EXPECTED_OPCODES:
        violations.append("machine_opcode_histogram_mismatch")
    if set(joined) != set(sem.REGISTRY):
        violations.append(f"registry_surface_mismatch:joined={sorted(joined)} registry={sorted(sem.REGISTRY)}")

    program_count = int((ex.get("coverage") or {}).get("exec_touching_unique_programs", -1))
    stage_counts = (ex.get("coverage") or {}).get("stage_exec_touching_unique_program_counts") or {}
    if program_count != EXPECTED_PROGRAMS:
        violations.append(f"program_count:{program_count}!={EXPECTED_PROGRAMS}")

    total = sum(joined.values())
    if total != EXPECTED_MACHINE_INSTRUCTIONS:
        violations.append(f"machine_instruction_count:{total}!={EXPECTED_MACHINE_INSTRUCTIONS}")

    rows = []
    for op in sorted(joined):
        rows.append({
            "opcode": op,
            "instruction_count": joined[op],
            "discovery": "STRUCTURAL_EXEC_FRONTIER" if op in explicit else "ARCHITECTURAL_IMPLICIT_EXEC_WRITE",
            "semantics": sem.REGISTRY[op],
        })

    return {
        "schema": OUTPUT_SCHEMA,
        "status": OUTPUT_STATUS if not violations else "D1_GCN_EXEC_MASK_MACHINE_FRONTIER_WITH_VIOLATIONS",
        "sources": {
            "exec_frontier": str(exec_path),
            "exec_frontier_sha256": sha256_file(exec_path),
            "structural_census": str(census_path),
            "structural_census_sha256": sha256_file(census_path),
            "amd_isa": sem.AMD_SEA_ISLANDS,
        },
        "coverage": {
            "explicit_structural_exec_instruction_count": explicit_total,
            "implicit_cmpx_exec_instruction_count": sum(cmpx_all.values()),
            "machine_exec_instruction_count": total,
            "machine_exec_opcode_count": len(joined),
            "machine_exec_unique_program_count": program_count,
            "stage_machine_exec_unique_program_counts": stage_counts,
            "shader_expression_semantic_promotions": 0,
        },
        "opcodes": rows,
        "violations": violations,
        "semantic_boundary": {
            "machine_exec_semantics": "SOURCE_CLOSED",
            "symbolic_exec_dataflow": "NEXT_GATE",
            "lane_aware_vgpr_values": "WITHHELD",
            "shader_expression_semantics": "WITHHELD",
        },
        "policy": (
            "The complete exact D1 EXEC-touching machine surface is the union of the structural EXEC frontier and "
            "architecturally implicit CMPX EXEC writes. This artifact proves instruction semantics coverage only; it "
            "does not claim path-sensitive symbolic propagation or shader-expression meaning."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exec-frontier", required=True, type=Path)
    ap.add_argument("--census", required=True, type=Path)
    ap.add_argument("-o", "--output", required=True, type=Path)
    a = ap.parse_args()
    out = build(a.exec_frontier, a.census)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": out["status"], "coverage": out["coverage"], "violation_count": len(out["violations"])}, indent=2))
    for x in out["violations"][:100]: print("VIOLATION", x)
    return 0 if not out["violations"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
