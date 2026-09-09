#!/usr/bin/env python3
"""Validate the source-backed architectural-effect tranche against exact D1 corpus evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import d1_gcn_arch_effects_v1 as arch

INPUT_SCHEMA = "d1_gcn_opcode_structural_evidence_frontier/v1"
INPUT_STATUS = "D1_GCN_OPCODE_STRUCTURAL_EVIDENCE_FRONTIER_EXACT"
OUTPUT_SCHEMA = "d1_gcn_arch_effects_frontier/v1"
OUTPUT_STATUS = "D1_GCN_ARCH_EFFECTS_FRONTIER_SOURCE_CLOSED_EXACT"
EXPECTED_NOVEL_OPCODE_COUNT = 67
EXPECTED_NOVEL_OCCURRENCES = 261733
EXPECTED_SOURCE_CLOSED_COUNT = 27
EXPECTED_SOURCE_CLOSED_OCCURRENCES = 255449
EXPECTED_SOURCE_CLOSED_PROGRAMS = 20137
EXPECTED_SOURCE_CLOSED_STAGE_PROGRAMS = {"PS": 12050, "VS": 8068, "DS": 19}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def build(path: Path, expected_sha256: str | None = None) -> dict:
    violations: list[str] = []
    got_sha = sha256_file(path)
    if expected_sha256 and got_sha != expected_sha256.lower():
        violations.append(f"input_sha256:{got_sha}!={expected_sha256.lower()}")
    d = json.loads(path.read_text())
    if d.get("schema") != INPUT_SCHEMA:
        violations.append(f"input_schema:{d.get('schema')!r}")
    if d.get("status") != INPUT_STATUS:
        violations.append(f"input_status:{d.get('status')!r}")
    if d.get("violations"):
        violations.append(f"input_violations:{len(d['violations'])}")
    coverage = d.get("coverage") or {}
    if int(coverage.get("novel_opcode_count", -1)) != EXPECTED_NOVEL_OPCODE_COUNT:
        violations.append("input_novel_opcode_count")
    if int(coverage.get("novel_opcode_instruction_occurrences", -1)) != EXPECTED_NOVEL_OCCURRENCES:
        violations.append("input_novel_occurrences")
    if int(coverage.get("semantic_promotions", -1)) != 0:
        violations.append("input_semantic_promotions_nonzero")

    violations.extend(f"registry:{x}" for x in arch.validate_registry())
    novel = {str(x["opcode"]): x for x in (d.get("novel_opcodes") or [])}
    reg_ops = set(arch.REGISTRY)
    missing = sorted(reg_ops - set(novel))
    if missing:
        violations.append(f"registry_opcodes_not_in_exact_frontier:{missing}")
    if len(reg_ops) != EXPECTED_SOURCE_CLOSED_COUNT:
        violations.append(f"registry_count:{len(reg_ops)}!={EXPECTED_SOURCE_CLOSED_COUNT}")

    programs: set[str] = set()
    stage_programs = {"PS": set(), "VS": set(), "DS": set()}
    occurrences = 0
    rows = []
    correction_totals: dict[str, int] = {}
    for op in sorted(reg_ops, key=lambda x: (-int(novel.get(x, {}).get("instruction_count", 0)), x)):
        src = novel.get(op)
        if src is None:
            continue
        occurrences += int(src["instruction_count"])
        programs.update(src.get("program_sha256") or [])
        for sha in src.get("program_sha256") or []:
            prow = (d.get("program_provenance") or {}).get(sha)
            if not prow:
                violations.append(f"missing_program_provenance:{op}:{sha}")
                continue
            stage = prow.get("stage")
            if stage not in stage_programs:
                violations.append(f"invalid_stage:{op}:{sha}:{stage!r}")
                continue
            stage_programs[stage].add(sha)

        corrected_examples = []
        correction_classes: set[str] = set()
        for inst in src.get("examples") or []:
            ann = arch.annotate_instruction(inst)
            struct_defs = list(inst.get("defs") or [])
            struct_uses = list(inst.get("uses") or [])
            if ann["architectural_defs"] != struct_defs:
                correction_classes.add("ARCHITECTURAL_DEFS_DIFFER")
            if ann["architectural_uses"] != struct_uses:
                correction_classes.add("ARCHITECTURAL_USES_DIFFER")
            e = arch.REGISTRY[op]
            if e["control_flow"] != "NONE":
                correction_classes.add("ARCHITECTURAL_CONTROL_FLOW_EFFECT")
            if e["destination_write_scope"] != "FULL_DESTINATION":
                correction_classes.add("NONTRIVIAL_DESTINATION_WRITE_SCOPE")
            corrected_examples.append({
                "gcn_sha256": inst.get("gcn_sha256"),
                "stage": inst.get("stage"),
                "address": inst.get("address"),
                "source_line": inst.get("source_line"),
                "encoding_hex": inst.get("encoding_hex"),
                "operands": inst.get("operands") or [],
                "structural_defs": struct_defs,
                "structural_uses": struct_uses,
                "architectural_defs": ann["architectural_defs"],
                "architectural_uses": ann["architectural_uses"],
            })
        for c in correction_classes:
            correction_totals[c] = correction_totals.get(c, 0) + 1

        e = arch.REGISTRY[op]
        rows.append({
            "opcode": op,
            "architectural_status": e["architectural_status"],
            "shader_expression_status": e["shader_expression_status"],
            "instruction_count": int(src["instruction_count"]),
            "program_count": int(src["program_count"]),
            "stages": src.get("stages") or [],
            "family": e["family"],
            "execution_scope": e["execution_scope"],
            "exec_behavior": e["exec_behavior"],
            "memory_effect": e["memory_effect"],
            "control_flow": e["control_flow"],
            "destination_write_scope": e["destination_write_scope"],
            "implicit_reads": e["implicit_reads"],
            "implicit_writes": e["implicit_writes"],
            "reads_old_destination": e["reads_old_destination"],
            "operation": e["operation"],
            "source": e["source"],
            "structural_correction_classes": sorted(correction_classes),
            "examples": corrected_examples,
        })

    stage_counts = {k: len(v) for k, v in stage_programs.items()}
    if occurrences != EXPECTED_SOURCE_CLOSED_OCCURRENCES:
        violations.append(f"source_closed_occurrences:{occurrences}!={EXPECTED_SOURCE_CLOSED_OCCURRENCES}")
    if len(programs) != EXPECTED_SOURCE_CLOSED_PROGRAMS:
        violations.append(f"source_closed_programs:{len(programs)}!={EXPECTED_SOURCE_CLOSED_PROGRAMS}")
    if stage_counts != EXPECTED_SOURCE_CLOSED_STAGE_PROGRAMS:
        violations.append(f"source_closed_stage_programs:{stage_counts!r}!={EXPECTED_SOURCE_CLOSED_STAGE_PROGRAMS!r}")
    if any(x["shader_expression_status"] != "UNPROVEN" for x in rows):
        violations.append("semantic_promotion_detected")

    expected_hazards = {
        "v_writelane_b32": ("ARCHITECTURAL_USES_DIFFER", "NONTRIVIAL_DESTINATION_WRITE_SCOPE"),
        "v_readfirstlane_b32": ("ARCHITECTURAL_USES_DIFFER",),
        "s_or_b64": ("ARCHITECTURAL_DEFS_DIFFER",),
        "s_swappc_b64": ("ARCHITECTURAL_DEFS_DIFFER", "ARCHITECTURAL_USES_DIFFER", "ARCHITECTURAL_CONTROL_FLOW_EFFECT"),
        "v_cmpx_eq_i32": ("ARCHITECTURAL_DEFS_DIFFER", "ARCHITECTURAL_USES_DIFFER", "NONTRIVIAL_DESTINATION_WRITE_SCOPE"),
        "v_cmpx_lt_u32": ("ARCHITECTURAL_DEFS_DIFFER", "ARCHITECTURAL_USES_DIFFER", "NONTRIVIAL_DESTINATION_WRITE_SCOPE"),
    }
    byop = {x["opcode"]: set(x["structural_correction_classes"]) for x in rows}
    for op, classes in expected_hazards.items():
        absent = set(classes) - byop.get(op, set())
        if absent:
            violations.append(f"expected_structural_hazard_missing:{op}:{sorted(absent)}")

    return {
        "schema": OUTPUT_SCHEMA,
        "status": OUTPUT_STATUS if not violations else "D1_GCN_ARCH_EFFECTS_FRONTIER_WITH_VIOLATIONS",
        "input": {"path": str(path), "sha256": got_sha, "schema": d.get("schema"), "status": d.get("status")},
        "architectural_source": arch.AMD_SEA_ISLANDS,
        "coverage": {
            "exact_novel_opcode_count": len(novel),
            "exact_novel_opcode_instruction_occurrences": int(coverage.get("novel_opcode_instruction_occurrences", -1)),
            "source_closed_opcode_count": len(rows),
            "source_closed_opcode_instruction_occurrences": occurrences,
            "source_closed_novel_occurrence_ratio": occurrences / EXPECTED_NOVEL_OCCURRENCES,
            "source_closed_unique_programs": len(programs),
            "source_closed_stage_programs": stage_counts,
            "remaining_architecturally_unclosed_opcode_count": len(novel) - len(rows),
            "remaining_architecturally_unclosed_occurrences": EXPECTED_NOVEL_OCCURRENCES - occurrences,
            "shader_expression_semantic_promotions": 0,
        },
        "structural_correction_summary": dict(sorted(correction_totals.items())),
        "source_closed_opcodes": rows,
        "remaining_unclosed_opcodes": [
            {"opcode": x["opcode"], "instruction_count": int(x["instruction_count"]), "program_count": int(x["program_count"]), "stages": x.get("stages") or []}
            for x in d.get("novel_opcodes") or [] if x["opcode"] not in reg_ops
        ],
        "violations": violations,
        "policy": (
            "Architectural SOURCE_CLOSED is not shader semantic promotion. This gate only proves effects "
            "specified by AMD GFX7 ISA and their exact occurrence in the D1 corpus. The structural v2 parser "
            "remains the immutable accounting boundary until a separately replayed v3 effect-aware IR proves "
            "that its extra special-register and control-flow annotations preserve all exact native accounting."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence", required=True, type=Path)
    ap.add_argument("--expected-sha256")
    ap.add_argument("-o", "--output", required=True, type=Path)
    a = ap.parse_args()
    out = build(a.evidence, a.expected_sha256)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": out["status"], "coverage": out["coverage"], "structural_correction_summary": out["structural_correction_summary"], "violation_count": len(out["violations"])}, indent=2))
    if out["violations"]:
        for x in out["violations"][:100]:
            print("VIOLATION", x)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
