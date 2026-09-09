#!/usr/bin/env python3
"""Replay effect-aware IR v3 across every exact D1 PS/VS/DS structural IR.

The complete structural census is the authoritative program/stage ledger for all
26,464 exact binaries. The structural-evidence frontier intentionally carries
full provenance only for binaries that touch baseline-novel structural forms, so
it must not be used as a total program roster.
"""
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
CENSUS_SCHEMA = "d1_gcn_shader_corpus_structural_census/v1"
CENSUS_STATUS = "D1_GCN_SHADER_CORPUS_STRUCTURAL_CENSUS_COMPLETE"
OUTPUT_SCHEMA = "d1_gcn_effect_ir_corpus_replay/v1"
OUTPUT_STATUS = "D1_GCN_EFFECT_IR_V3_GLOBAL_REPLAY_EXACT"
EXPECTED_PROGRAMS = 26464
EXPECTED_INSTRUCTIONS = 4896165
EXPECTED_STAGE_PROGRAMS = {"PS": 18375, "VS": 8069, "DS": 20}
EXPECTED_FRONTIER_PROVENANCE_PROGRAMS = 26379
EXPECTED_BASELINE_ONLY_PROGRAMS = 85
EXPECTED_SOURCE_CLOSED = 255449
EXPECTED_SOURCE_CLOSED_PROGRAMS = 20137
EXPECTED_SWAPP = 8053


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _load_program_stage_ledger(census_path: Path, expected_sha256: str | None, violations: list[str]) -> tuple[dict[str, str], str]:
    csha = sha256_file(census_path)
    if expected_sha256 and csha != expected_sha256.lower():
        violations.append(f"census_sha256:{csha}!={expected_sha256.lower()}")
    census = json.loads(census_path.read_text())
    if census.get("schema") != CENSUS_SCHEMA:
        violations.append(f"census_schema:{census.get('schema')!r}")
    if census.get("status") != CENSUS_STATUS:
        violations.append(f"census_status:{census.get('status')!r}")
    if census.get("violations"):
        violations.append(f"census_violations:{len(census['violations'])}")
    rows = census.get("programs") or []
    if len(rows) != EXPECTED_PROGRAMS:
        violations.append(f"census_program_count:{len(rows)}!={EXPECTED_PROGRAMS}")
    out: dict[str, str] = {}
    stage_counts = collections.Counter()
    for row in rows:
        sha = str(row.get("gcn_sha256", "")).lower()
        stages = [str(x).upper() for x in (row.get("stages") or [])]
        if len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha):
            violations.append(f"census_program_sha_invalid:{sha!r}")
            continue
        if sha in out:
            violations.append(f"census_program_sha_duplicate:{sha}")
            continue
        if len(stages) != 1 or stages[0] not in EXPECTED_STAGE_PROGRAMS:
            violations.append(f"census_program_stage_invalid:{sha}:{stages!r}")
            continue
        if row.get("violations"):
            violations.append(f"census_program_violations:{sha}:{len(row['violations'])}")
        out[sha] = stages[0]
        stage_counts[stages[0]] += 1
    if dict(stage_counts) != EXPECTED_STAGE_PROGRAMS:
        violations.append(f"census_stage_program_counts:{dict(stage_counts)!r}!={EXPECTED_STAGE_PROGRAMS!r}")
    if len(out) != EXPECTED_PROGRAMS:
        violations.append(f"census_program_stage_ledger:{len(out)}!={EXPECTED_PROGRAMS}")
    return out, csha


def replay(
    ir_dir: Path,
    evidence_path: Path,
    census_path: Path,
    expected_evidence_sha256: str | None = None,
    expected_census_sha256: str | None = None,
) -> dict:
    violations: list[str] = []
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
    frontier_prov = ev.get("program_provenance") or {}
    if len(frontier_prov) != EXPECTED_FRONTIER_PROVENANCE_PROGRAMS:
        violations.append(
            f"frontier_provenance_program_count:{len(frontier_prov)}!={EXPECTED_FRONTIER_PROVENANCE_PROGRAMS}"
        )
    novel = {x["opcode"]: x for x in ev.get("novel_opcodes") or []}
    expected_registry_counts = {op: int(novel[op]["instruction_count"]) for op in arch.REGISTRY if op in novel}
    if set(expected_registry_counts) != set(arch.REGISTRY):
        violations.append("registry_not_subset_of_exact_frontier")

    stage_by_sha, csha = _load_program_stage_ledger(census_path, expected_census_sha256, violations)
    # For every frontier-touching program, the richer provenance artifact must agree
    # with the total structural census. The remaining 85 binaries are intentionally
    # absent from frontier_prov because they are wholly inside the 808EE505 form set.
    for sha, prow in frontier_prov.items():
        census_stage = stage_by_sha.get(sha)
        if census_stage is None:
            violations.append(f"frontier_program_not_in_census:{sha}")
            continue
        if prow.get("stage") != census_stage:
            violations.append(f"frontier_census_stage_disagreement:{sha}:{prow.get('stage')!r}!={census_stage!r}")
    baseline_only_shas = sorted(set(stage_by_sha) - set(frontier_prov))
    if len(baseline_only_shas) != EXPECTED_BASELINE_ONLY_PROGRAMS:
        violations.append(
            f"baseline_only_program_count:{len(baseline_only_shas)}!={EXPECTED_BASELINE_ONLY_PROGRAMS}"
        )
    baseline_only_stage_counts = collections.Counter(stage_by_sha[x] for x in baseline_only_shas)
    if dict(baseline_only_stage_counts) != {"PS": EXPECTED_BASELINE_ONLY_PROGRAMS}:
        violations.append(f"baseline_only_stage_counts:{dict(baseline_only_stage_counts)!r}")

    paths = sorted(ir_dir.glob("*.json"))
    if len(paths) != EXPECTED_PROGRAMS:
        violations.append(f"ir_file_count:{len(paths)}!={EXPECTED_PROGRAMS}")
    total_instructions = 0
    source_closed = 0
    closed_programs = 0
    stage_closed_programs = collections.Counter()
    replay_stage_programs = collections.Counter()
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
        stage = stage_by_sha.get(sha)
        if stage is None:
            violations.append(f"program_stage_missing_from_census:{sha}")
            continue
        v2 = json.loads(p.read_text())
        try:
            v3 = effect_ir.upgrade(v2)
        except Exception as exc:
            violations.append(f"upgrade_failed:{sha}:{type(exc).__name__}:{exc}")
            continue
        replay_stage_programs[stage] += 1
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
        if sc:
            closed_programs += 1
            stage_closed_programs[stage] += 1
        if v3["indirect_pc_swap_instruction_count"]:
            indirect_programs += 1
        program_rows.append({
            "gcn_sha256": sha,
            "stage": stage,
            "frontier_provenance_present": sha in frontier_prov,
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

    if dict(replay_stage_programs) != EXPECTED_STAGE_PROGRAMS:
        violations.append(f"replay_stage_program_counts:{dict(replay_stage_programs)!r}!={EXPECTED_STAGE_PROGRAMS!r}")
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
        "sources": {
            "ir_dir": str(ir_dir),
            "evidence": str(evidence_path),
            "evidence_sha256": esha,
            "structural_census": str(census_path),
            "structural_census_sha256": csha,
        },
        "coverage": {
            "exact_programs_replayed": len(program_rows),
            "exact_stage_program_counts": dict(sorted(replay_stage_programs.items())),
            "frontier_provenance_program_count": len(frontier_prov),
            "baseline_only_program_count": len(baseline_only_shas),
            "baseline_only_stage_program_counts": dict(sorted(baseline_only_stage_counts.items())),
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
            "Every exact structural v2 IR is replayed through the additive v3 adapter. The complete structural census is the "
            "authoritative all-program stage ledger; the novel-form evidence provenance map is intentionally partial and is "
            "cross-checked wherever present. V2 native instruction and parse-accounting facts must remain byte/order/address "
            "identical. Source-closed architectural effects may add defs/uses or split local CFG at indirect PC swaps, but no "
            "indirect target and no high-level shader expression is promoted."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ir-dir", type=Path, required=True)
    ap.add_argument("--evidence", type=Path, required=True)
    ap.add_argument("--structural-census", type=Path, required=True)
    ap.add_argument("--expected-evidence-sha256")
    ap.add_argument("--expected-census-sha256")
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()
    out = replay(
        a.ir_dir,
        a.evidence,
        a.structural_census,
        a.expected_evidence_sha256,
        a.expected_census_sha256,
    )
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": out["status"], "coverage": out["coverage"], "violation_count": len(out["violations"])}, indent=2))
    for x in out["violations"][:100]:
        print("VIOLATION", x)
    return 0 if not out["violations"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
