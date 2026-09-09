#!/usr/bin/env python3
"""Replay physical SGPR/M0 SSA across every exact Destiny 1 shader program."""
from __future__ import annotations

import argparse
import collections
import json
import multiprocessing as mp
import os
from pathlib import Path

import d1_gcn_sgpr_machine_semantics_v1 as machine
import d1_gcn_sgpr_ssa_v1 as scalar

CENSUS_STATUS = "D1_GCN_SHADER_CORPUS_STRUCTURAL_CENSUS_COMPLETE"
SGPR_FRONTIER_STATUS = "D1_GCN_SGPR_MACHINE_FRONTIER_EXACT"
M0_FRONTIER_STATUS = "D1_GCN_M0_IMPLICIT_FRONTIER_EXACT"
SSA_STATUS = "D1_GCN_SGPR_SSA_EXACT"
SCHEMA = "d1_gcn_sgpr_ssa_corpus_replay/v1"
STATUS = "D1_GCN_SGPR_SSA_CORPUS_REPLAY_EXACT"
EXPECTED_PROGRAMS = 26464
EXPECTED_INSTRUCTIONS = 4896165
EXPECTED_BLOCKS = 68622
EXPECTED_EDGES = 51073
EXPECTED_STAGE = {"DS": 20, "PS": 18375, "VS": 8069}


def worker(path: str) -> dict:
    p = Path(path)
    sha = p.stem.lower()
    try:
        d = scalar.analyze(json.loads(p.read_text()))
        c = d.get("coverage") or {}
        m0_defs = sum(
            1 for r in (d.get("instructions") or [])
            for w in (r.get("scalar_writes") or [])
            if w.get("register") == "m0"
        )
        return {
            "sha": sha,
            "ok": d.get("status") == SSA_STATUS and not d.get("violations"),
            "status": d.get("status"),
            "violations": (d.get("violations") or [])[:5],
            "instructions": d.get("instruction_count", 0),
            "blocks": d.get("basic_block_count", 0),
            "edges": d.get("concrete_cfg_edge_count", 0),
            "nodes": len(d.get("nodes") or {}),
            "tracked": c.get("tracked_scalar_register_count", 0),
            "max_index": c.get("max_tracked_sgpr_index", -1),
            "entries": c.get("entry_node_count", 0),
            "phis": c.get("cfg_phi_node_count", 0),
            "orphan_blocks": c.get("unresolved_control_entry_block_count", 0),
            "orphan_nodes": c.get("unresolved_control_entry_scalar_node_count", 0),
            "leaves": c.get("non_scalar_source_leaf_count", 0),
            "defs": c.get("sgpr_def_instruction_count", 0),
            "def_entries": c.get("sgpr_def_entry_count", 0),
            "uses": c.get("sgpr_use_instruction_count", 0),
            "use_entries": c.get("sgpr_use_entry_count", 0),
            "whole_writes": c.get("whole_scalar_write_entry_count", 0),
            "rmw_writes": c.get("whole_scalar_rmw_write_entry_count", 0),
            "mask_writes": c.get("exec_gated_mask_half_write_entry_count", 0),
            "results": c.get("scalar_result_component_node_count", 0),
            "rmw_uses": c.get("implicit_rmw_use_entry_count", 0),
            "m0_defs": m0_defs,
            "m0_uses": c.get("implicit_m0_use_instruction_count", 0),
            "def_ops": c.get("sgpr_def_opcode_counts") or {},
            "def_entry_ops": c.get("sgpr_def_entry_opcode_counts") or {},
            "use_ops": c.get("sgpr_use_opcode_counts") or {},
            "use_entry_ops": c.get("sgpr_use_entry_opcode_counts") or {},
            "m0_use_ops": c.get("implicit_m0_use_opcode_counts") or {},
            "promotions": c.get("shader_expression_semantic_promotions", 0),
        }
    except Exception as e:
        return {"sha": sha, "ok": False, "exception": f"{type(e).__name__}:{e}"}


def replay(ir_dir: Path, census_path: Path, sgpr_frontier_path: Path,
           m0_frontier_path: Path, workers: int) -> dict:
    violations: list[str] = []
    census = json.loads(census_path.read_text())
    sf = json.loads(sgpr_frontier_path.read_text())
    mf = json.loads(m0_frontier_path.read_text())
    if census.get("status") != CENSUS_STATUS:
        violations.append(f"census_status:{census.get('status')!r}")
    if sf.get("status") != SGPR_FRONTIER_STATUS or sf.get("violations"):
        violations.append(f"sgpr_frontier_status:{sf.get('status')!r}:{(sf.get('violations') or [])[:5]}")
    if mf.get("status") != M0_FRONTIER_STATUS or mf.get("violations") or mf.get("unresolved"):
        violations.append(f"m0_frontier_status:{mf.get('status')!r}:{(mf.get('violations') or [])[:5]}")

    stages = {p["gcn_sha256"]: (p.get("stages") or []) for p in census.get("programs") or []}
    if len(stages) != EXPECTED_PROGRAMS:
        violations.append(f"stage_map:{len(stages)}!={EXPECTED_PROGRAMS}")
    paths = sorted(ir_dir.glob("*.json"))
    if len(paths) != EXPECTED_PROGRAMS:
        violations.append(f"ir_file_count:{len(paths)}!={EXPECTED_PROGRAMS}")

    totals = collections.Counter()
    stage_counts = collections.Counter()
    def_ops = collections.Counter()
    def_entry_ops = collections.Counter()
    use_ops = collections.Counter()
    use_entry_ops = collections.Counter()
    m0_use_ops = collections.Counter()
    rows: list[dict] = []
    max_index = -1

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
            stage = st[0]
            stage_counts[stage] += 1
            if not r.get("ok"):
                violations.append(f"analyze:{sha}:{r.get('exception') or (r.get('status'), r.get('violations'))}")
                continue
            for k in (
                "instructions", "blocks", "edges", "nodes", "tracked", "entries", "phis",
                "orphan_blocks", "orphan_nodes", "leaves", "defs", "def_entries", "uses",
                "use_entries", "whole_writes", "rmw_writes", "mask_writes", "results",
                "rmw_uses", "m0_defs", "m0_uses", "promotions",
            ):
                totals[k] += r[k]
            max_index = max(max_index, r["max_index"])
            def_ops.update(r["def_ops"])
            def_entry_ops.update(r["def_entry_ops"])
            use_ops.update(r["use_ops"])
            use_entry_ops.update(r["use_entry_ops"])
            m0_use_ops.update(r["m0_use_ops"])
            rows.append({
                "gcn_sha256": sha,
                "stage": stage,
                "tracked_scalar_register_count": r["tracked"],
                "max_tracked_sgpr_index": r["max_index"],
                "node_count": r["nodes"],
                "cfg_phi_node_count": r["phis"],
                "sgpr_def_entry_count": r["def_entries"],
                "sgpr_use_entry_count": r["use_entries"],
                "implicit_m0_use_instruction_count": r["m0_uses"],
            })
    finally:
        if pool:
            pool.close()
            pool.join()

    rows.sort(key=lambda x: x["gcn_sha256"])
    for key, got, expected in (
        ("programs", len(rows), EXPECTED_PROGRAMS),
        ("instructions", totals["instructions"], EXPECTED_INSTRUCTIONS),
        ("blocks", totals["blocks"], EXPECTED_BLOCKS),
        ("edges", totals["edges"], EXPECTED_EDGES),
    ):
        if got != expected:
            violations.append(f"{key}:{got}!={expected}")
    if dict(sorted(stage_counts.items())) != EXPECTED_STAGE:
        violations.append(f"stage_counts:{dict(stage_counts)}!={EXPECTED_STAGE}")

    sfc = sf.get("coverage") or {}
    for local, remote in {
        "defs": "sgpr_def_instruction_count",
        "def_entries": "sgpr_def_entry_count",
        "uses": "sgpr_use_instruction_count",
        "use_entries": "sgpr_use_entry_count",
    }.items():
        if totals[local] != sfc.get(remote):
            violations.append(f"sgpr_frontier_{local}:{totals[local]}!={sfc.get(remote)}")
    if dict(sorted(def_ops.items())) != (sfc.get("sgpr_def_opcode_counts") or {}):
        violations.append("sgpr_def_opcode_histogram_mismatch")
    if dict(sorted(def_entry_ops.items())) != (sfc.get("sgpr_def_entry_opcode_counts") or {}):
        violations.append("sgpr_def_entry_opcode_histogram_mismatch")
    if dict(sorted(use_ops.items())) != (sfc.get("sgpr_use_opcode_counts") or {}):
        violations.append("sgpr_use_opcode_histogram_mismatch")
    if dict(sorted(use_entry_ops.items())) != (sfc.get("sgpr_use_entry_opcode_counts") or {}):
        violations.append("sgpr_use_entry_opcode_histogram_mismatch")
    if max_index != sfc.get("max_sgpr_index"):
        violations.append(f"max_sgpr_index:{max_index}!={sfc.get('max_sgpr_index')}")

    mfc = mf.get("coverage") or {}
    if totals["m0_defs"] != mfc.get("explicit_m0_def_instruction_count"):
        violations.append(f"m0_defs:{totals['m0_defs']}!={mfc.get('explicit_m0_def_instruction_count')}")
    if totals["m0_uses"] != mfc.get("implicit_m0_value_use_instruction_count"):
        violations.append(f"m0_uses:{totals['m0_uses']}!={mfc.get('implicit_m0_value_use_instruction_count')}")
    expected_m0_ops = collections.Counter()
    for cat, ops in (mfc.get("implicit_m0_opcode_counts") or {}).items():
        if cat == "DS_NON_MEMORY_NO_M0_VALUE_DEPENDENCY":
            continue
        expected_m0_ops.update(ops)
    if dict(sorted(m0_use_ops.items())) != dict(sorted(expected_m0_ops.items())):
        violations.append("implicit_m0_use_opcode_histogram_mismatch")

    expected_mask_entries = sum(
        (sfc.get("sgpr_def_entry_opcode_counts") or {}).get(op, 0)
        for op in machine.COMPARE_MASK_DEST_OPCODES
    )
    if totals["mask_writes"] != expected_mask_entries:
        violations.append(f"compare_mask_write_entries:{totals['mask_writes']}!={expected_mask_entries}")
    expected_rmw = (sfc.get("sgpr_def_entry_opcode_counts") or {}).get("s_addk_i32", 0)
    if totals["rmw_writes"] != expected_rmw or totals["rmw_uses"] != expected_rmw:
        violations.append(
            f"rmw_accounting:writes={totals['rmw_writes']}:uses={totals['rmw_uses']}:expected={expected_rmw}"
        )
    if totals["whole_writes"] + totals["mask_writes"] != totals["def_entries"]:
        violations.append(
            f"write_partition:{totals['whole_writes']}+{totals['mask_writes']}!={totals['def_entries']}"
        )
    if totals["results"] != totals["def_entries"]:
        violations.append(f"result_components:{totals['results']}!={totals['def_entries']}")
    if totals["promotions"] != 0:
        violations.append(f"shader_expression_semantic_promotions:{totals['promotions']}")

    coverage = {
        "exact_programs_replayed": len(rows),
        "stage_program_counts": dict(sorted(stage_counts.items())),
        "exact_instructions_replayed": totals["instructions"],
        "effect_aware_basic_block_count": totals["blocks"],
        "concrete_cfg_edge_count": totals["edges"],
        "scalar_ssa_node_count": totals["nodes"],
        "tracked_scalar_register_instances": totals["tracked"],
        "max_sgpr_index": max_index,
        "program_entry_scalar_node_count": totals["entries"],
        "scalar_cfg_phi_node_count": totals["phis"],
        "unresolved_control_entry_block_count": totals["orphan_blocks"],
        "unresolved_control_entry_scalar_node_count": totals["orphan_nodes"],
        "non_scalar_source_leaf_count": totals["leaves"],
        "sgpr_def_instruction_count": totals["defs"],
        "sgpr_def_entry_count": totals["def_entries"],
        "sgpr_use_instruction_count": totals["uses"],
        "sgpr_use_entry_count": totals["use_entries"],
        "whole_scalar_write_entry_count": totals["whole_writes"],
        "whole_scalar_rmw_write_entry_count": totals["rmw_writes"],
        "exec_gated_mask_half_write_entry_count": totals["mask_writes"],
        "scalar_result_component_node_count": totals["results"],
        "implicit_rmw_use_entry_count": totals["rmw_uses"],
        "m0_def_instruction_count": totals["m0_defs"],
        "implicit_m0_use_instruction_count": totals["m0_uses"],
        "sgpr_def_opcode_counts": dict(sorted(def_ops.items())),
        "sgpr_def_entry_opcode_counts": dict(sorted(def_entry_ops.items())),
        "sgpr_use_opcode_counts": dict(sorted(use_ops.items())),
        "sgpr_use_entry_opcode_counts": dict(sorted(use_entry_ops.items())),
        "implicit_m0_use_opcode_counts": dict(sorted(m0_use_ops.items())),
        "shader_expression_semantic_promotions": totals["promotions"],
    }
    return {
        "schema": SCHEMA,
        "status": STATUS if not violations else "D1_GCN_SGPR_SSA_CORPUS_REPLAY_WITH_VIOLATIONS",
        "sources": {
            "ir_dir": str(ir_dir),
            "structural_census": str(census_path),
            "sgpr_machine_frontier": str(sgpr_frontier_path),
            "m0_implicit_frontier": str(m0_frontier_path),
        },
        "coverage": coverage,
        "programs": rows,
        "violations": violations,
        "semantic_boundary": {
            "exec_symbolic_dataflow": "GLOBAL_EXACT_PREREQUISITE",
            "physical_vgpr_lane_ssa": "GLOBAL_EXACT_SEPARATE_LAYER",
            "physical_sgpr_m0_ssa": "GLOBAL_EXACT" if not violations else "NOT_PROMOTED",
            "implicit_m0_provenance": "GLOBAL_EXACT" if not violations else "NOT_PROMOTED",
            "scalar_rmw_identity": "GLOBAL_EXACT" if not violations else "NOT_PROMOTED",
            "opcode_result_value_semantics": "NEXT_GATE" if not violations else "WITHHELD",
            "shader_expression_semantics": "WITHHELD",
            "shader_expression_semantic_promotions": 0,
        },
        "policy": "Every exact D1 shader is replayed through physical SGPR/M0 SSA and reconciled against the frozen SGPR and implicit-M0 frontiers. This closes scalar register identity and hidden M0 dependencies only; instruction values and shader expressions remain withheld.",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ir-dir", type=Path, required=True)
    ap.add_argument("--structural-census", type=Path, required=True)
    ap.add_argument("--sgpr-machine-frontier", type=Path, required=True)
    ap.add_argument("--m0-implicit-frontier", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=max(1, min(4, os.cpu_count() or 1)))
    a = ap.parse_args()
    out = replay(a.ir_dir, a.structural_census, a.sgpr_machine_frontier, a.m0_implicit_frontier, a.workers)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": out["status"], "coverage": out["coverage"], "violations": out["violations"][:20]}, indent=2, sort_keys=True))
    return 0 if not out["violations"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
