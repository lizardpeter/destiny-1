#!/usr/bin/env python3
"""Replay effect-aware IR v3 across every exact D1 PS/VS/DS structural IR."""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path

import d1_gcn_arch_effects_v1 as arch
import d1_gcn_effect_ir_v3 as effect_ir

EVIDENCE_SCHEMA = "d1_gcn_opcode_structural_evidence_frontier/v1"
EVIDENCE_STATUS = "D1_GCN_OPCODE_STRUCTURAL_EVIDENCE_FRONTIER_EXACT"
OUTPUT_SCHEMA = "d1_gcn_effect_ir_corpus_replay/v1"
OUTPUT_STATUS = "D1_GCN_EFFECT_IR_V3_GLOBAL_REPLAY_EXACT"
EXPECTED_PROGRAMS = 26464
EXPECTED_INSTRUCTIONS = 4896165
EXPECTED_SOURCE_CLOSED = 255449
EXPECTED_SOURCE_CLOSED_PROGRAMS = 20137
EXPECTED_SWAPP = 8053


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def replay(ir_dir: Path, evidence_path: Path, expected_evidence_sha256: str | None = None) -> dict:
    violations = []
    esha = sha256_file(evidence_path)
    if expected_evidence_sha256 and esha != expected_evidence_sha256.lower():
        violations.append(f"evidence_sha256:{esha}!={expected_evidence_sha256.lower()}")
    ev = json.loads(evidence_path.read_text())
    if ev.get("schema") != EVIDENCE_SCHEMA:
        violations.append(f"evidence_schema:{ev.get('schema')!r}")
    if ev.get("status") != EVIDENCE_STATUS:
        violations.append(f"evidence_status:{ev.get('status')!r}")
    if ev.get("violations"):
        violations.append(f"evidence_violations:{len(ev['violations'])}")
    prov = ev.get("program_provenance") or {}
    novel = {x["opcode"]: x for x in ev.get("novel_opcodes") or []}
    expected_registry_counts = {op: int(novel[op]["instruction_count"]) for op in arch.REGISTRY if op in novel}
    if set(expected_registry_counts) != set(arch.REGISTRY):
        violations.append("registry_not_subset_of_exact_frontier")

    paths = sorted(ir_dir.glob("*.json"))
    if len(paths) != EXPECTED_PROGRAMS:
        violations.append(f"ir_file_count:{len(paths)}!={EXPECTED_PROGRAMS}")
    total_instructions = 0
    source_closed = 0
    closed_programs = 0
    stage_closed_programs = collections.Counter()
    opcode_counts = collections.Counter()
    defs_differ = 0
    uses_differ = 0
    partial = 0
    indirect = 0
    v2_blocks = 0
    v3_blocks = 0
    v2_edges = 0
    v3_edges = 0
    indirect_programs = 0
    program_rows = []

    for p in paths:
        sha = p.stem.lower()
        if len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha):
            violations.append(f"ir_filename_not_sha256:{p.name}")
            continue
        prow = prov.get(sha)
        if prow is None:
            violations.append(f"program_provenance_missing:{sha}")
            continue
        v2 = json.loads(p.read_text())
        try:
            v3 = effect_ir.upgrade(v2)
        except Exception as exc:
            violations.append(f"upgrade_failed:{sha}:{type(exc).__name__}:{exc}")
            continue
        total_instructions += v3["instruction_count"]
        sc = v3["source_closed_instruction_count"]
        source_closed += sc
        opcode_counts.update(v3["source_closed_opcode_counts"])
        defs_differ += v3["architectural_defs_differ_instruction_count"]
        uses_differ += v3["architectural_uses_differ_instruction_count"]
        partial += v3["partial_destination_write_instruction_count"]
        indirect += v3["indirect_pc_swap_instruction_count"]
        delta = v3["cfg_delta_vs_structural_v2"]
        v2_blocks += delta["basic_block_count_v2"]
        v3_blocks += delta["basic_block_count_v3"]
        v2_edges += delta["concrete_cfg_edge_count_v2"]
        v3_edges += delta["concrete_cfg_edge_count_v3"]
        stage = prow.get("stage")
        if sc:
            closed_programs += 1
            stage_closed_programs[stage] += 1
        if v3["indirect_pc_swap_instruction_count"]:
            indirect_programs += 1
        program_rows.append({
            "gcn_sha256": sha,
            "stage": stage,
            "shader": v3.get("shader"),
            "instruction_count": v3["instruction_count"],
            "source_closed_instruction_count": sc,
            "architectural_defs_differ_instruction_count": v3["architectural_defs_differ_instruction_count"],
            "architectural_uses_differ_instruction_count": v3["architectural_uses_differ_instruction_count"],
            "partial_destination_write_instruction_count": v3["partial_destination_write_instruction_count"],
            "indirect_pc_swap_instruction_count": v3["indirect_pc_swap_instruction_count"],
            "basic_block_delta": delta["basic_block_delta"],
            "concrete_cfg_edge_delta": delta["concrete_cfg_edge_delta"],
        })

    if total_instructions != EXPECTED_INSTRUCTIONS:
        violations.append(f"instruction_count:{total_instructions}!={EXPECTED_INSTRUCTIONS}")
    if source_closed != EXPECTED_SOURCE_CLOSED:
        violations.append(f"source_closed_instructions:{source_closed}!={EXPECTED_SOURCE_CLOSED}")
    if closed_programs != EXPECTED_SOURCE_CLOSED_PROGRAMS:
        violations.append(f"source_closed_programs:{closed_programs}!={EXPECTED_SOURCE_CLOSED_PROGRAMS}")
    if dict(opcode_counts) != expected_registry_counts:
        violations.append("source_closed_opcode_histogram_disagrees_with_exact_evidence")
    if indirect != EXPECTED_SWAPP:
        violations.append(f"indirect_pc_swap_count:{indirect}!={EXPECTED_SWAPP}")
    if indirect_programs != EXPECTED_SWAPP:
        violations.append(f"indirect_pc_swap_programs:{indirect_programs}!={EXPECTED_SWAPP}")
    if len(program_rows) != EXPECTED_PROGRAMS:
        violations.append(f"successful_program_replays:{len(program_rows)}!={EXPECTED_PROGRAMS}")

    return {
        "schema": OUTPUT_SCHEMA,
        "status": OUTPUT_STATUS if not violations else "D1_GCN_EFFECT_IR_V3_GLOBAL_REPLAY_WITH_VIOLATIONS",
        "sources": {"ir_dir": str(ir_dir), "evidence": str(evidence_path), "evidence_sha256": esha},
        "coverage": {
            "exact_programs_replayed": len(program_rows),
            "exact_instructions_replayed": total_instructions,
            "source_closed_instruction_count": source_closed,
            "source_closed_program_count": closed_programs,
            "source_closed_stage_program_counts": dict(sorted(stage_closed_programs.items())),
            "source_closed_opcode_counts": dict(sorted(opcode_counts.items())),
            "architectural_defs_differ_instruction_count": defs_differ,
            "architectural_uses_differ_instruction_count": uses_differ,
            "partial_destination_write_instruction_count": partial,
            "indirect_pc_swap_instruction_count": indirect,
            "indirect_pc_swap_program_count": indirect_programs,
            "structural_v2_basic_block_count": v2_blocks,
            "effect_v3_basic_block_count": v3_blocks,
            "basic_block_delta": v3_blocks - v2_blocks,
            "structural_v2_concrete_cfg_edge_count": v2_edges,
            "effect_v3_concrete_cfg_edge_count": v3_edges,
            "concrete_cfg_edge_delta": v3_edges - v2_edges,
            "shader_expression_semantic_promotions": 0,
        },
        "programs": program_rows,
        "violations": violations,
        "policy": (
            "Every exact structural v2 IR is replayed through the additive v3 adapter. V2 native instruction and parse-accounting "
            "facts must remain byte/order/address identical. Source-closed architectural effects may add defs/uses or split local CFG "
            "at indirect PC swaps, but no indirect target and no high-level shader expression is promoted."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ir-dir", type=Path, required=True)
    ap.add_argument("--evidence", type=Path, required=True)
    ap.add_argument("--expected-evidence-sha256")
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()
    out = replay(a.ir_dir, a.evidence, a.expected_evidence_sha256)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": out["status"], "coverage": out["coverage"], "violation_count": len(out["violations"])}, indent=2))
    for x in out["violations"][:100]:
        print("VIOLATION", x)
    return 0 if not out["violations"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
