#!/usr/bin/env python3
"""Replay lane-aware physical-VGPR SSA across every exact Destiny 1 shader program."""
from __future__ import annotations

import argparse
import collections
import json
import multiprocessing as mp
import os
from pathlib import Path

import d1_gcn_vgpr_lane_ssa_v1 as lane

CENSUS_STATUS = "D1_GCN_SHADER_CORPUS_STRUCTURAL_CENSUS_COMPLETE"
FRONTIER_STATUS = "D1_GCN_VGPR_MACHINE_FRONTIER_EXACT"
SSA_STATUS = "D1_GCN_VGPR_LANE_SSA_EXACT"
SCHEMA = "d1_gcn_vgpr_lane_ssa_corpus_replay/v1"
STATUS = "D1_GCN_VGPR_LANE_SSA_CORPUS_REPLAY_EXACT"
EXPECTED_PROGRAMS = 26464
EXPECTED_INSTRUCTIONS = 4896165
EXPECTED_BLOCKS = 68622
EXPECTED_EDGES = 51073
EXPECTED_STAGE = {"DS": 20, "PS": 18375, "VS": 8069}


def worker(path: str) -> dict:
    p = Path(path)
    sha = p.stem.lower()
    try:
        d = lane.analyze(json.loads(p.read_text()))
        c = d.get("coverage") or {}
        return {
            "sha": sha,
            "ok": d.get("status") == SSA_STATUS and not d.get("violations"),
            "status": d.get("status"),
            "violations": (d.get("violations") or [])[:5],
            "instructions": d.get("instruction_count", 0),
            "blocks": d.get("basic_block_count", 0),
            "edges": d.get("concrete_cfg_edge_count", 0),
            "nodes": d.get("node_count", 0),
            "tracked": c.get("tracked_vgpr_count", 0),
            "max_index": c.get("max_tracked_vgpr_index", -1),
            "entries": c.get("entry_node_count", 0),
            "phis": c.get("cfg_phi_node_count", 0),
            "orphan_blocks": c.get("unresolved_control_entry_block_count", 0),
            "orphan_nodes": c.get("unresolved_control_entry_vgpr_node_count", 0),
            "scalar_leaves": c.get("non_vgpr_source_leaf_count", 0),
            "def_instructions": c.get("vgpr_def_instruction_count", 0),
            "def_entries": c.get("vgpr_def_entry_count", 0),
            "use_instructions": c.get("vgpr_use_instruction_count", 0),
            "use_entries": c.get("vgpr_use_entry_count", 0),
            "exec_writes": c.get("exec_gated_write_node_count", 0),
            "single_writes": c.get("single_lane_write_node_count", 0),
            "results": c.get("vgpr_result_component_node_count", 0),
            "dynamic_reads": c.get("dynamic_vgpr_read_boundary_count", 0),
            "write_ops": c.get("opcode_write_instruction_counts") or {},
            "write_entries": c.get("opcode_write_entry_counts") or {},
            "promotions": c.get("shader_expression_semantic_promotions", 0),
        }
    except Exception as e:
        return {"sha": sha, "ok": False, "exception": f"{type(e).__name__}:{e}"}


def replay(ir_dir: Path, census_path: Path, frontier_path: Path, workers: int) -> dict:
    violations: list[str] = []
    census = json.loads(census_path.read_text())
    frontier = json.loads(frontier_path.read_text())
    if census.get("status") != CENSUS_STATUS:
        violations.append(f"census_status:{census.get('status')!r}")
    if frontier.get("status") != FRONTIER_STATUS or frontier.get("violations"):
        violations.append(f"frontier_status:{frontier.get('status')!r}:{(frontier.get('violations') or [])[:5]}")

    stages = {p["gcn_sha256"]: (p.get("stages") or []) for p in census.get("programs") or []}
    if len(stages) != EXPECTED_PROGRAMS:
        violations.append(f"stage_map:{len(stages)}!={EXPECTED_PROGRAMS}")
    paths = sorted(ir_dir.glob("*.json"))
    if len(paths) != EXPECTED_PROGRAMS:
        violations.append(f"ir_file_count:{len(paths)}!={EXPECTED_PROGRAMS}")

    totals = collections.Counter()
    stage_counts = collections.Counter()
    write_ops = collections.Counter()
    write_entries = collections.Counter()
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
                "orphan_blocks", "orphan_nodes", "scalar_leaves", "def_instructions", "def_entries",
                "use_instructions", "use_entries", "exec_writes", "single_writes", "results",
                "dynamic_reads", "promotions",
            ):
                totals[k] += r[k]
            max_index = max(max_index, r["max_index"])
            write_ops.update(r["write_ops"])
            write_entries.update(r["write_entries"])
            rows.append({
                "gcn_sha256": sha,
                "stage": stage,
                "tracked_vgpr_count": r["tracked"],
                "max_tracked_vgpr_index": r["max_index"],
                "node_count": r["nodes"],
                "cfg_phi_node_count": r["phis"],
                "vgpr_def_entry_count": r["def_entries"],
                "vgpr_use_entry_count": r["use_entries"],
            })
    finally:
        if pool:
            pool.close()
            pool.join()

    rows.sort(key=lambda x: x["gcn_sha256"])
    exact = {
        "programs": len(rows),
        "instructions": totals["instructions"],
        "blocks": totals["blocks"],
        "edges": totals["edges"],
    }
    for k, expected in {
        "programs": EXPECTED_PROGRAMS,
        "instructions": EXPECTED_INSTRUCTIONS,
        "blocks": EXPECTED_BLOCKS,
        "edges": EXPECTED_EDGES,
    }.items():
        if exact[k] != expected:
            violations.append(f"{k}:{exact[k]}!={expected}")
    if dict(sorted(stage_counts.items())) != EXPECTED_STAGE:
        violations.append(f"stage_counts:{dict(stage_counts)}!={EXPECTED_STAGE}")

    fc = frontier.get("coverage") or {}
    reconciliations = {
        "def_instructions": "vgpr_def_instruction_count",
        "def_entries": "vgpr_def_entry_count",
        "use_instructions": "vgpr_use_instruction_count",
        "use_entries": "vgpr_use_entry_count",
        "exec_writes": "exec_masked_def_entry_count",
        "single_writes": "single_lane_unmasked_def_entry_count",
        "dynamic_reads": "dynamic_vgpr_source_instruction_count",
    }
    for local, remote in reconciliations.items():
        if totals[local] != fc.get(remote):
            violations.append(f"frontier_{local}:{totals[local]}!={fc.get(remote)}")
    if totals["results"] != totals["def_entries"]:
        violations.append(f"result_components:{totals['results']}!={totals['def_entries']}")
    if totals["exec_writes"] + totals["single_writes"] != totals["def_entries"]:
        violations.append(
            f"write_partition:{totals['exec_writes']}+{totals['single_writes']}!={totals['def_entries']}"
        )
    if dict(sorted(write_ops.items())) != (fc.get("vgpr_def_opcode_counts") or {}):
        violations.append("frontier_write_instruction_opcode_histogram_mismatch")
    if dict(sorted(write_entries.items())) != (fc.get("vgpr_def_entry_opcode_counts") or {}):
        violations.append("frontier_write_entry_opcode_histogram_mismatch")
    if max_index != fc.get("max_vgpr_index"):
        violations.append(f"max_vgpr_index:{max_index}!={fc.get('max_vgpr_index')}")
    if totals["promotions"] != 0:
        violations.append(f"shader_expression_semantic_promotions:{totals['promotions']}")

    coverage = {
        "exact_programs_replayed": len(rows),
        "stage_program_counts": dict(sorted(stage_counts.items())),
        "exact_instructions_replayed": totals["instructions"],
        "effect_aware_basic_block_count": totals["blocks"],
        "concrete_cfg_edge_count": totals["edges"],
        "vgpr_ssa_node_count": totals["nodes"],
        "tracked_vgpr_instances": totals["tracked"],
        "max_vgpr_index": max_index,
        "program_entry_vgpr_node_count": totals["entries"],
        "vgpr_cfg_phi_node_count": totals["phis"],
        "unresolved_control_entry_block_count": totals["orphan_blocks"],
        "unresolved_control_entry_vgpr_node_count": totals["orphan_nodes"],
        "non_vgpr_source_leaf_count": totals["scalar_leaves"],
        "vgpr_def_instruction_count": totals["def_instructions"],
        "vgpr_def_entry_count": totals["def_entries"],
        "vgpr_use_instruction_count": totals["use_instructions"],
        "vgpr_use_entry_count": totals["use_entries"],
        "exec_gated_write_node_count": totals["exec_writes"],
        "single_lane_write_node_count": totals["single_writes"],
        "vgpr_result_component_node_count": totals["results"],
        "dynamic_vgpr_read_boundary_count": totals["dynamic_reads"],
        "opcode_write_instruction_counts": dict(sorted(write_ops.items())),
        "opcode_write_entry_counts": dict(sorted(write_entries.items())),
        "shader_expression_semantic_promotions": totals["promotions"],
    }
    return {
        "schema": SCHEMA,
        "status": STATUS if not violations else "D1_GCN_VGPR_LANE_SSA_CORPUS_REPLAY_WITH_VIOLATIONS",
        "sources": {
            "ir_dir": str(ir_dir),
            "structural_census": str(census_path),
            "vgpr_machine_frontier": str(frontier_path),
        },
        "coverage": coverage,
        "programs": rows,
        "violations": violations,
        "semantic_boundary": {
            "exec_symbolic_dataflow": "GLOBAL_EXACT_PREREQUISITE",
            "vgpr_machine_frontier": "GLOBAL_EXACT_PREREQUISITE",
            "physical_vgpr_lane_ssa": "GLOBAL_EXACT" if not violations else "NOT_PROMOTED",
            "inactive_lane_preservation": "GLOBAL_EXACT" if not violations else "NOT_PROMOTED",
            "dynamic_vgpr_source_identity": "GLOBAL_EXACT_OPAQUE_VALUE_BOUNDARY" if not violations else "NOT_PROMOTED",
            "ordinary_sgpr_value_ssa": "NEXT_GATE" if not violations else "WITHHELD",
            "opcode_result_value_semantics": "WITHHELD",
            "shader_expression_semantics": "WITHHELD",
            "shader_expression_semantic_promotions": 0,
        },
        "policy": (
            "Every exact D1 shader is replayed through the same physical-VGPR lane SSA. Machine-frontier definition/use "
            "counts and opcode histograms must reconcile exactly. Ordinary vector writes remain EXEC-gated lane merges, "
            "V_WRITELANE is a single-lane unmasked mutation, and V_MOVRELS preserves an explicit dynamic source identity. "
            "Instruction result values and shader/material semantics remain withheld."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ir-dir", type=Path, required=True)
    ap.add_argument("--structural-census", type=Path, required=True)
    ap.add_argument("--vgpr-machine-frontier", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=max(1, min(4, os.cpu_count() or 1)))
    a = ap.parse_args()
    out = replay(a.ir_dir, a.structural_census, a.vgpr_machine_frontier, a.workers)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": out["status"], "coverage": out["coverage"], "violations": out["violations"][:20]}, indent=2, sort_keys=True))
    return 0 if not out["violations"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
