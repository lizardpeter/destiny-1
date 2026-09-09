#!/usr/bin/env python3
"""Replay the scalar architectural value overlay across all exact D1 PS4 GCN programs."""
from __future__ import annotations

import argparse
import collections
import json
import multiprocessing as mp
import os
from pathlib import Path

import d1_gcn_scalar_value_overlay_v1 as overlay

CENSUS_STATUS = "D1_GCN_SHADER_CORPUS_STRUCTURAL_CENSUS_COMPLETE"
OVERLAY_STATUS = "D1_GCN_SCALAR_VALUE_OVERLAY_EXACT"
SCHEMA = "d1_gcn_scalar_value_overlay_corpus_replay/v1"
STATUS = "D1_GCN_SCALAR_VALUE_OVERLAY_CORPUS_REPLAY_EXACT"
EXPECTED_PROGRAMS = 26464
EXPECTED_INSTRUCTIONS = 4896165
EXPECTED_STAGE = {"DS": 20, "PS": 18375, "VS": 8069}
EXPECTED_CATEGORY_INSTRUCTIONS = {
    "PURE_SCALAR_TRANSFORM": 70540,
    "CROSS_STATE_IDENTITY": 32167,
    "CONDITION_MASK_VALUE": 13422,
    "SCALAR_MEMORY_RESULT": 493923,
}
EXPECTED_CATEGORY_COMPONENTS = {
    "PURE_SCALAR_TRANSFORM": 95219,
    "CROSS_STATE_IDENTITY": 49525,
    "CONDITION_MASK_VALUE": 26844,
    "SCALAR_MEMORY_RESULT": 1884697,
}
EXPECTED_CROSS_OPS = {
    "s_and_saveexec_b64": 9305,
    "s_swappc_b64": 8053,
    "v_readlane_b32": 14592,
    "v_readfirstlane_b32": 217,
}


def worker(path: str) -> dict:
    p = Path(path)
    sha = p.stem.lower()
    try:
        d = overlay.analyze(json.loads(p.read_text()))
        c = d.get("coverage") or {}
        return {
            "sha": sha,
            "ok": d.get("status") == OVERLAY_STATUS and not d.get("violations"),
            "status": d.get("status"),
            "violations": (d.get("violations") or [])[:8],
            "instructions": d.get("instruction_count", 0),
            "scalar_defs": c.get("scalar_def_instruction_count", 0),
            "components": c.get("scalar_result_component_count", 0),
            "bound_instructions": c.get("bound_instruction_count", 0),
            "bound_components": c.get("bound_component_count", 0),
            "nonmemory_instructions": c.get("architectural_nonmemory_instruction_count", 0),
            "nonmemory_components": c.get("architectural_nonmemory_component_count", 0),
            "memory_instructions": c.get("opaque_memory_instruction_count", 0),
            "memory_components": c.get("opaque_memory_component_count", 0),
            "pure_instructions": c.get("pure_scalar_instruction_count", 0),
            "pure_components": c.get("pure_scalar_component_count", 0),
            "cross_instructions": c.get("cross_state_instruction_count", 0),
            "cross_components": c.get("cross_state_component_count", 0),
            "condition_instructions": c.get("condition_alias_instruction_count", 0),
            "condition_components": c.get("condition_alias_component_count", 0),
            "pure_condition_aliases": c.get("pure_condition_alias_instruction_count", 0),
            "scalar_alu": c.get("scalar_alu_instruction_count", 0),
            "old_exec": c.get("old_exec_alias_instruction_count", 0),
            "pc_plus_4": c.get("pc_plus_4_instruction_count", 0),
            "readlane": c.get("vgpr_readlane_instruction_count", 0),
            "readfirstlane": c.get("vgpr_readfirstlane_instruction_count", 0),
            "value_kind_counts": c.get("value_kind_counts") or {},
            "opcode_binding_counts": c.get("opcode_binding_counts") or {},
            "promotions": c.get("shader_expression_semantic_promotions", 0),
        }
    except Exception as e:
        return {"sha": sha, "ok": False, "exception": f"{type(e).__name__}:{e}"}


def replay(ir_dir: Path, census_path: Path, workers: int) -> dict:
    violations: list[str] = []
    census = json.loads(census_path.read_text())
    if census.get("status") != CENSUS_STATUS:
        violations.append(f"census_status:{census.get('status')!r}")
    stages = {p["gcn_sha256"]: (p.get("stages") or []) for p in census.get("programs") or []}
    if len(stages) != EXPECTED_PROGRAMS:
        violations.append(f"stage_map:{len(stages)}!={EXPECTED_PROGRAMS}")
    paths = sorted(ir_dir.glob("*.json"))
    if len(paths) != EXPECTED_PROGRAMS:
        violations.append(f"ir_file_count:{len(paths)}!={EXPECTED_PROGRAMS}")

    totals = collections.Counter()
    stage_counts = collections.Counter()
    value_kinds = collections.Counter()
    opcounts = collections.Counter()
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
            stage = st[0]
            stage_counts[stage] += 1
            if not r.get("ok"):
                violations.append(f"analyze:{sha}:{r.get('exception') or (r.get('status'), r.get('violations'))}")
                continue
            for k in (
                "instructions", "scalar_defs", "components", "bound_instructions", "bound_components",
                "nonmemory_instructions", "nonmemory_components", "memory_instructions", "memory_components",
                "pure_instructions", "pure_components", "cross_instructions", "cross_components",
                "condition_instructions", "condition_components", "pure_condition_aliases", "scalar_alu",
                "old_exec", "pc_plus_4", "readlane", "readfirstlane", "promotions",
            ):
                totals[k] += r[k]
            value_kinds.update(r["value_kind_counts"])
            opcounts.update(r["opcode_binding_counts"])
            rows.append({
                "gcn_sha256": sha,
                "stage": stage,
                "scalar_def_instruction_count": r["scalar_defs"],
                "scalar_result_component_count": r["components"],
                "architectural_nonmemory_instruction_count": r["nonmemory_instructions"],
                "opaque_memory_instruction_count": r["memory_instructions"],
            })
    finally:
        if pool:
            pool.close(); pool.join()

    rows.sort(key=lambda x: x["gcn_sha256"])
    if len(rows) != EXPECTED_PROGRAMS:
        violations.append(f"programs:{len(rows)}!={EXPECTED_PROGRAMS}")
    if dict(sorted(stage_counts.items())) != EXPECTED_STAGE:
        violations.append(f"stage_counts:{dict(stage_counts)}!={EXPECTED_STAGE}")
    if totals["instructions"] != EXPECTED_INSTRUCTIONS:
        violations.append(f"instructions:{totals['instructions']}!={EXPECTED_INSTRUCTIONS}")

    category_i = {
        "PURE_SCALAR_TRANSFORM": totals["pure_instructions"],
        "CROSS_STATE_IDENTITY": totals["cross_instructions"],
        "CONDITION_MASK_VALUE": totals["condition_instructions"],
        "SCALAR_MEMORY_RESULT": totals["memory_instructions"],
    }
    category_c = {
        "PURE_SCALAR_TRANSFORM": totals["pure_components"],
        "CROSS_STATE_IDENTITY": totals["cross_components"],
        "CONDITION_MASK_VALUE": totals["condition_components"],
        "SCALAR_MEMORY_RESULT": totals["memory_components"],
    }
    if category_i != EXPECTED_CATEGORY_INSTRUCTIONS:
        violations.append(f"category_instruction_counts:{category_i}!={EXPECTED_CATEGORY_INSTRUCTIONS}")
    if category_c != EXPECTED_CATEGORY_COMPONENTS:
        violations.append(f"category_component_counts:{category_c}!={EXPECTED_CATEGORY_COMPONENTS}")

    expected_scalar_defs = sum(EXPECTED_CATEGORY_INSTRUCTIONS.values())
    expected_components = sum(EXPECTED_CATEGORY_COMPONENTS.values())
    expected_nonmemory_i = expected_scalar_defs - EXPECTED_CATEGORY_INSTRUCTIONS["SCALAR_MEMORY_RESULT"]
    expected_nonmemory_c = expected_components - EXPECTED_CATEGORY_COMPONENTS["SCALAR_MEMORY_RESULT"]
    for name, got, expected in (
        ("scalar_defs", totals["scalar_defs"], expected_scalar_defs),
        ("components", totals["components"], expected_components),
        ("bound_instructions", totals["bound_instructions"], expected_scalar_defs),
        ("bound_components", totals["bound_components"], expected_components),
        ("nonmemory_instructions", totals["nonmemory_instructions"], expected_nonmemory_i),
        ("nonmemory_components", totals["nonmemory_components"], expected_nonmemory_c),
    ):
        if got != expected:
            violations.append(f"{name}:{got}!={expected}")

    cross = {
        "s_and_saveexec_b64": totals["old_exec"],
        "s_swappc_b64": totals["pc_plus_4"],
        "v_readlane_b32": totals["readlane"],
        "v_readfirstlane_b32": totals["readfirstlane"],
    }
    if cross != EXPECTED_CROSS_OPS:
        violations.append(f"cross_state_counts:{cross}!={EXPECTED_CROSS_OPS}")
    if totals["pure_condition_aliases"] + totals["scalar_alu"] != totals["pure_instructions"]:
        violations.append(
            f"pure_partition:{totals['pure_condition_aliases']}+{totals['scalar_alu']}!={totals['pure_instructions']}"
        )
    if totals["promotions"] != 0:
        violations.append(f"shader_expression_semantic_promotions:{totals['promotions']}")
    if dict(sorted(opcounts.items())) and sum(opcounts.values()) != expected_scalar_defs:
        violations.append(f"opcode_binding_total:{sum(opcounts.values())}!={expected_scalar_defs}")

    coverage = {
        "exact_programs_replayed": len(rows),
        "stage_program_counts": dict(sorted(stage_counts.items())),
        "exact_instructions_replayed": totals["instructions"],
        "scalar_def_instruction_count": totals["scalar_defs"],
        "scalar_result_component_count": totals["components"],
        "bound_instruction_count": totals["bound_instructions"],
        "bound_component_count": totals["bound_components"],
        "architectural_nonmemory_instruction_count": totals["nonmemory_instructions"],
        "architectural_nonmemory_component_count": totals["nonmemory_components"],
        "opaque_memory_instruction_count": totals["memory_instructions"],
        "opaque_memory_component_count": totals["memory_components"],
        "category_instruction_counts": category_i,
        "category_component_counts": category_c,
        "pure_condition_alias_instruction_count": totals["pure_condition_aliases"],
        "scalar_alu_instruction_count": totals["scalar_alu"],
        "cross_state_instruction_counts": cross,
        "value_kind_counts": dict(sorted(value_kinds.items())),
        "opcode_binding_counts": dict(sorted(opcounts.items())),
        "shader_expression_semantic_promotions": totals["promotions"],
    }
    return {
        "schema": SCHEMA,
        "status": STATUS if not violations else "D1_GCN_SCALAR_VALUE_OVERLAY_CORPUS_REPLAY_WITH_VIOLATIONS",
        "coverage": coverage,
        "programs": rows,
        "violations": violations,
        "semantic_boundary": {
            "scalar_result_expression_dag_binding": "GLOBAL_EXACT" if not violations else "NOT_PROMOTED",
            "scalar_memory_result_values": "OPAQUE_RESOURCE_ADDRESS_WITHHELD",
            "vector_result_expression_dag_binding": "NEXT_GATE" if not violations else "WITHHELD",
            "shader_expression_semantics": "WITHHELD",
            "shader_expression_semantic_promotions": 0,
        },
        "policy": (
            "All exact scalar result components are replayed through the source-backed architectural value overlay. "
            "Non-memory values bind to exact machine identities; SMEM values remain opaque. No shader or material "
            "meaning is promoted."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ir-dir", type=Path, required=True)
    ap.add_argument("--census", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=max(1, min(4, os.cpu_count() or 1)))
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()
    out = replay(a.ir_dir, a.census, max(1, a.workers))
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": out["status"], "coverage": out["coverage"], "violations": out["violations"][:50]}, indent=2, sort_keys=True))
    return 0 if not out["violations"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
