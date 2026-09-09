#!/usr/bin/env python3
"""Replay exact vector-formula source-state binding across the full Destiny 1 shader corpus."""
from __future__ import annotations

import argparse
import collections
import json
import multiprocessing as mp
import os
from pathlib import Path

import d1_gcn_vector_formula_source_binding_v1 as binding

CENSUS_STATUS = "D1_GCN_SHADER_CORPUS_STRUCTURAL_CENSUS_COMPLETE"
BINDING_STATUS = "D1_GCN_VECTOR_FORMULA_SOURCE_BINDING_EXACT"
SCHEMA = "d1_gcn_vector_formula_source_binding_corpus_replay/v1"
STATUS = "D1_GCN_VECTOR_FORMULA_SOURCE_BINDING_CORPUS_EXACT"
EXPECTED_PROGRAMS = 26464
EXPECTED_INSTRUCTIONS = 4896165
EXPECTED_FORMULA_INSTRUCTIONS = 2994322
EXPECTED_STAGE = {"DS": 20, "PS": 18375, "VS": 8069}


def worker(path: str) -> dict:
    p = Path(path)
    sha = p.stem.lower()
    try:
        d = binding.analyze(json.loads(p.read_text()))
        c = d.get("source_binding_coverage") or {}
        return {
            "sha": sha,
            "ok": d.get("status") == BINDING_STATUS and not d.get("violations"),
            "status": d.get("status"),
            "violations": (d.get("violations") or [])[:8],
            "instructions": d.get("instruction_count", 0),
            "formula_instructions": c.get("formula_instruction_count", 0),
            "expected_sources": c.get("expected_source_slot_count", 0),
            "exact_sources": c.get("exact_source_slot_count", 0),
            "vgpr_sources": c.get("vgpr_source_slot_count", 0),
            "sgpr_sources": c.get("sgpr_source_slot_count", 0),
            "literal_sources": c.get("literal_source_slot_count", 0),
            "sgpr_replacements": c.get("sgpr_placeholder_replacement_count", 0),
            "placeholder_leaks": c.get("formula_source_placeholder_leak_count", 0),
            "vector_nodes": c.get("integrated_vector_node_count", 0),
            "scalar_nodes": c.get("scalar_ssa_node_count", 0),
            "scalar_kinds": c.get("scalar_state_kind_counts") or {},
            "opcode_sources": c.get("opcode_source_slot_counts") or {},
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
    scalar_kinds = collections.Counter()
    opcode_sources = collections.Counter()
    rows = []

    pool = None
    iterator = map(worker, map(str, paths))
    if workers > 1:
        pool = mp.Pool(workers)
        iterator = pool.imap_unordered(worker, map(str, paths), chunksize=4)
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
                "instructions", "formula_instructions", "expected_sources", "exact_sources",
                "vgpr_sources", "sgpr_sources", "literal_sources", "sgpr_replacements",
                "placeholder_leaks", "vector_nodes", "scalar_nodes", "promotions",
            ):
                totals[k] += r[k]
            scalar_kinds.update(r["scalar_kinds"])
            opcode_sources.update(r["opcode_sources"])
            rows.append({
                "gcn_sha256": sha,
                "stage": stage,
                "formula_instruction_count": r["formula_instructions"],
                "source_slot_count": r["exact_sources"],
                "sgpr_source_slot_count": r["sgpr_sources"],
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
    if totals["formula_instructions"] != EXPECTED_FORMULA_INSTRUCTIONS:
        violations.append(f"formula_instructions:{totals['formula_instructions']}!={EXPECTED_FORMULA_INSTRUCTIONS}")
    if totals["exact_sources"] != totals["expected_sources"]:
        violations.append(f"source_accounting:{totals['exact_sources']}!={totals['expected_sources']}")
    if totals["vgpr_sources"] + totals["sgpr_sources"] + totals["literal_sources"] != totals["expected_sources"]:
        violations.append(
            f"source_partition:{totals['vgpr_sources']}+{totals['sgpr_sources']}+{totals['literal_sources']}"
            f"!={totals['expected_sources']}"
        )
    if totals["sgpr_replacements"] != totals["sgpr_sources"]:
        violations.append(f"sgpr_replacements:{totals['sgpr_replacements']}!={totals['sgpr_sources']}")
    if totals["placeholder_leaks"] != 0:
        violations.append(f"placeholder_leaks:{totals['placeholder_leaks']}")
    if totals["promotions"] != 0:
        violations.append(f"shader_expression_semantic_promotions:{totals['promotions']}")

    coverage = {
        "exact_programs_replayed": len(rows),
        "stage_program_counts": dict(sorted(stage_counts.items())),
        "exact_instructions_replayed": totals["instructions"],
        "formula_instruction_count": totals["formula_instructions"],
        "formula_source_slot_count": totals["expected_sources"],
        "exact_formula_source_binding_count": totals["exact_sources"],
        "vgpr_source_slot_count": totals["vgpr_sources"],
        "sgpr_source_slot_count": totals["sgpr_sources"],
        "literal_source_slot_count": totals["literal_sources"],
        "sgpr_placeholder_replacement_count": totals["sgpr_replacements"],
        "formula_source_placeholder_leak_count": totals["placeholder_leaks"],
        "integrated_vector_node_count": totals["vector_nodes"],
        "scalar_ssa_node_count": totals["scalar_nodes"],
        "scalar_state_kind_counts": dict(sorted(scalar_kinds.items())),
        "opcode_source_slot_counts": dict(sorted(opcode_sources.items())),
        "shader_expression_semantic_promotions": totals["promotions"],
    }
    return {
        "schema": SCHEMA,
        "status": STATUS if not violations else "D1_GCN_VECTOR_FORMULA_SOURCE_BINDING_CORPUS_WITH_VIOLATIONS",
        "coverage": coverage,
        "programs": rows,
        "violations": violations,
        "semantic_boundary": {
            "formula_result_lane_binding": "GLOBAL_EXACT_PREREQUISITE",
            "vgpr_formula_source_state_identity": "GLOBAL_EXACT" if not violations else "NOT_PROMOTED",
            "sgpr_formula_source_state_identity": "GLOBAL_EXACT_CROSS_GRAPH" if not violations else "NOT_PROMOTED",
            "literal_formula_source_identity": "GLOBAL_EXACT" if not violations else "NOT_PROMOTED",
            "scalar_memory_values": "OPAQUE_RESOURCE_ADDRESS_WITHHELD",
            "resource_lds_interpolation_values": "UNCHANGED_OPAQUE_BOUNDARIES",
            "next_gate": "RESOURCE_MEMORY_INTERPOLATION_PROVENANCE_AND_RUNTIME_BINDING" if not violations else "WITHHELD",
            "shader_expression_semantics": "WITHHELD",
            "material_semantics": "WITHHELD",
            "shader_expression_semantic_promotions": 0,
        },
        "policy": (
            "All source-closed formula inputs are reconciled to exact existing architectural state identities or encoded "
            "literals. The temporary SGPR-use leaves are removed from formula-source edges only; the scalar and vector "
            "register graphs remain separately owned and cross-referenced. Resource and material meaning remains withheld."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ir-dir", type=Path, required=True)
    ap.add_argument("--census", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=max(1, min(2, os.cpu_count() or 1)))
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()
    out = replay(a.ir_dir, a.census, max(1, a.workers))
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": out["status"], "coverage": out["coverage"], "violations": out["violations"][:50]}, indent=2, sort_keys=True))
    return 0 if not out["violations"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
