#!/usr/bin/env python3
"""Replay an exact candidate D1 GCN corpus through special non-formula value binding.

Expected opcode/category denominators are derived from the candidate's frozen vector-value
frontier.  The per-program analyzer is corpus-neutral and contains no LocalShader stage rule.
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

import d1_gcn_vector_special_value_binding_v1 as binding
import d1_gcn_vector_special_value_semantics_v1 as sem

MANIFEST_STATUS = "D1_GCN_STRUCTURAL_CANDIDATE_MANIFEST_EXACT"
VALUE_STATUS = "D1_GCN_CANDIDATE_VECTOR_VALUE_FRONTIER_EXACT"
BIND_STATUS = "D1_GCN_VECTOR_SPECIAL_VALUE_BINDING_EXACT"
SCHEMA = "d1_gcn_candidate_vector_special_value_binding_replay/v1"
STATUS = "D1_GCN_CANDIDATE_VECTOR_SPECIAL_VALUE_BINDING_REPLAY_EXACT"


def analyze_one(path: Path, output_dir: Path | None) -> dict:
    sha = path.stem.lower()
    try:
        out = binding.analyze(json.loads(path.read_text()))
        if output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / f"{sha}.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
        c = out.get("special_value_coverage") or {}
        return {
            "gcn_sha256": sha,
            "ok": out.get("status") == BIND_STATUS and not out.get("violations"),
            "status": out.get("status"),
            "violations": (out.get("violations") or [])[:8],
            "instruction_count": out.get("instruction_count", 0),
            "special_instruction_count": c.get("special_instruction_count", 0),
            "special_result_component_count": c.get("special_result_component_count", 0),
            "computational_instruction_count": c.get("computational_instruction_count", 0),
            "computational_result_component_count": c.get("computational_result_component_count", 0),
            "resource_opaque_instruction_count": c.get("resource_opaque_instruction_count", 0),
            "resource_opaque_result_component_count": c.get("resource_opaque_result_component_count", 0),
            "carry_mask_alias_count": c.get("carry_mask_alias_count", 0),
            "predicate_mask_alias_count": c.get("predicate_mask_alias_count", 0),
            "opcode_instruction_counts": c.get("opcode_instruction_counts") or {},
            "opcode_result_component_counts": c.get("opcode_result_component_counts") or {},
            "integrated_vector_node_count": c.get("integrated_vector_node_count", 0),
            "shader_expression_semantic_promotions": c.get("shader_expression_semantic_promotions", 0),
        }
    except Exception as e:
        return {"gcn_sha256": sha, "ok": False, "exception": f"{type(e).__name__}:{e}"}


def replay(manifest_path: Path, value_path: Path, ir_dir: Path, output_dir: Path | None) -> dict:
    violations: list[str] = []
    manifest = json.loads(manifest_path.read_text())
    value = json.loads(value_path.read_text())
    if manifest.get("status") != MANIFEST_STATUS or manifest.get("violations"):
        violations.append(f"manifest_not_exact:{manifest.get('status')}:{len(manifest.get('violations') or [])}")
    if value.get("status") != VALUE_STATUS or value.get("violations"):
        violations.append(f"value_frontier_not_exact:{value.get('status')}:{len(value.get('violations') or [])}")
    if sem.validate():
        violations.append(f"special_semantics_invalid:{sem.validate()}")

    roster = sorted(str(x.get("gcn_sha256", "")).lower() for x in (manifest.get("programs") or []))
    if not roster or len(roster) != len(set(roster)):
        violations.append(f"manifest_roster_invalid:{len(roster)}:{len(set(roster))}")
    paths = {p.stem.lower(): p for p in ir_dir.glob("*.json")}
    if set(paths) != set(roster):
        violations.append(f"ir_roster_mismatch:expected={len(roster)}:actual={len(paths)}")

    vc = value.get("coverage") or {}
    expected_programs = int(vc.get("exact_program_count", -1))
    expected_instructions = int(vc.get("exact_instruction_count", -1))
    expected_vgpr_instructions = int(vc.get("vgpr_def_instruction_count", -1))
    expected_vgpr_components = int(vc.get("vgpr_def_entry_count", -1))
    formula_i = int((vc.get("category_instruction_counts") or {}).get("VALU_FORMULA_PENDING", 0))
    formula_c = int((vc.get("category_def_entry_counts") or {}).get("VALU_FORMULA_PENDING", 0))
    expected_special_opi = {op: int((vc.get("opcode_instruction_counts") or {}).get(op, 0)) for op in sorted(sem.SEMANTICS)}
    expected_special_opc = {op: int((vc.get("opcode_def_entry_counts") or {}).get(op, 0)) for op in sorted(sem.SEMANTICS)}
    expected_special_i = sum(expected_special_opi.values())
    expected_special_c = sum(expected_special_opc.values())
    expected_nonformula_i = expected_vgpr_instructions - formula_i
    expected_nonformula_c = expected_vgpr_components - formula_c
    if expected_special_i != expected_nonformula_i:
        violations.append(f"candidate_special_instruction_surface:{expected_special_i}!={expected_nonformula_i}")
    if expected_special_c != expected_nonformula_c:
        violations.append(f"candidate_special_component_surface:{expected_special_c}!={expected_nonformula_c}")
    if any(v <= 0 for v in expected_special_opi.values()):
        violations.append(f"candidate_missing_special_opcode:{expected_special_opi}")

    rows = []
    totals = collections.Counter()
    opi = collections.Counter()
    opc = collections.Counter()
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
            "instruction_count", "special_instruction_count", "special_result_component_count",
            "computational_instruction_count", "computational_result_component_count",
            "resource_opaque_instruction_count", "resource_opaque_result_component_count",
            "carry_mask_alias_count", "predicate_mask_alias_count", "integrated_vector_node_count",
            "shader_expression_semantic_promotions",
        ):
            totals[k] += int(r.get(k, 0))
        opi.update(r.get("opcode_instruction_counts") or {})
        opc.update(r.get("opcode_result_component_counts") or {})

    checks = {
        "programs": (len(rows), expected_programs),
        "instructions": (totals["instruction_count"], expected_instructions),
        "special_instructions": (totals["special_instruction_count"], expected_special_i),
        "special_components": (totals["special_result_component_count"], expected_special_c),
        "computational_instructions": (totals["computational_instruction_count"],
                                       expected_special_opi.get("v_add_i32", 0) + expected_special_opi.get("v_cndmask_b32", 0)),
        "computational_components": (totals["computational_result_component_count"],
                                     expected_special_opc.get("v_add_i32", 0) + expected_special_opc.get("v_cndmask_b32", 0)),
        "resource_instructions": (totals["resource_opaque_instruction_count"], expected_special_opi.get("tbuffer_load_format_xyzw", 0)),
        "resource_components": (totals["resource_opaque_result_component_count"], expected_special_opc.get("tbuffer_load_format_xyzw", 0)),
        "carry_aliases": (totals["carry_mask_alias_count"], expected_special_opi.get("v_add_i32", 0)),
        "predicate_aliases": (totals["predicate_mask_alias_count"], expected_special_opi.get("v_cndmask_b32", 0)),
        "semantic_promotions": (totals["shader_expression_semantic_promotions"], 0),
    }
    for key, (got, want) in checks.items():
        if got != want:
            violations.append(f"accounting:{key}:{got}!={want}")
    if dict(sorted(opi.items())) != expected_special_opi:
        violations.append(f"opcode_instruction_histogram:{dict(sorted(opi.items()))}!={expected_special_opi}")
    if dict(sorted(opc.items())) != expected_special_opc:
        violations.append(f"opcode_component_histogram:{dict(sorted(opc.items()))}!={expected_special_opc}")

    source_backed_computational_components = formula_c + totals["computational_result_component_count"]
    if source_backed_computational_components + totals["resource_opaque_result_component_count"] != expected_vgpr_components:
        violations.append(
            f"vgpr_component_partition:{source_backed_computational_components}+"
            f"{totals['resource_opaque_result_component_count']}!={expected_vgpr_components}"
        )

    compact = [{
        "gcn_sha256": r["gcn_sha256"],
        "instruction_count": r["instruction_count"],
        "special_instruction_count": r["special_instruction_count"],
        "special_result_component_count": r["special_result_component_count"],
    } for r in rows]
    coverage = {
        "planned_unique_gcn_programs": expected_programs,
        "exact_special_value_bound_unique_gcn_programs": len(rows),
        "exact_instructions_replayed": totals["instruction_count"],
        "vgpr_def_instruction_count": expected_vgpr_instructions,
        "vgpr_result_component_count": expected_vgpr_components,
        "formula_instruction_count": formula_i,
        "formula_result_component_count": formula_c,
        "special_instruction_count": totals["special_instruction_count"],
        "special_result_component_count": totals["special_result_component_count"],
        "computational_special_instruction_count": totals["computational_instruction_count"],
        "computational_special_result_component_count": totals["computational_result_component_count"],
        "typed_buffer_opaque_instruction_count": totals["resource_opaque_instruction_count"],
        "typed_buffer_opaque_result_component_count": totals["resource_opaque_result_component_count"],
        "carry_mask_alias_count": totals["carry_mask_alias_count"],
        "predicate_mask_alias_count": totals["predicate_mask_alias_count"],
        "source_backed_computational_result_component_count": source_backed_computational_components,
        "architecturally_classified_vgpr_result_component_count": (
            source_backed_computational_components + totals["resource_opaque_result_component_count"]
        ),
        "generic_opaque_nonformula_result_component_count": 0,
        "opcode_instruction_counts": dict(sorted(opi.items())),
        "opcode_result_component_counts": dict(sorted(opc.items())),
        "integrated_vector_node_count": totals["integrated_vector_node_count"],
        "shader_expression_semantic_promotions": 0,
    }
    return {
        "schema": SCHEMA,
        "status": STATUS if not violations else "D1_GCN_CANDIDATE_VECTOR_SPECIAL_VALUE_BINDING_REPLAY_WITH_VIOLATIONS",
        "coverage": coverage,
        "programs": compact,
        "violations": violations,
        "semantic_boundary": {
            "candidate_stage_affects_special_value_analyzer": False,
            "formula_value_and_source_binding": "EXACT_PREREQUISITE",
            "carry_coupled_vector_values": "SOURCE_CLOSED_WITH_CONDITION_GRAPH_ALIAS" if not violations else "WITHHELD",
            "predicate_select_vector_values": "SOURCE_CLOSED_WITH_CONDITION_GRAPH_ALIAS" if not violations else "WITHHELD",
            "typed_buffer_address_resource_format_inputs": "EXACT" if not violations else "WITHHELD",
            "typed_buffer_fetched_contents": "OPAQUE_RESOURCE_DESCRIPTOR_BACKING_MEMORY_WITHHELD",
            "shader_expression_semantics": "WITHHELD",
            "material_semantics": "WITHHELD",
            "shader_expression_semantic_promotions": 0,
        },
        "policy": (
            "The exact candidate corpus is replayed through one corpus-neutral special-value analyzer. "
            "Expected opcodes and counts come from the frozen vector-value frontier. Every non-formula VGPR "
            "result in this candidate must be either source-backed carry/predicate computation or an explicitly "
            "typed resource-value boundary; no stage-specific arithmetic or material meaning is introduced."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate-manifest", type=Path, required=True)
    ap.add_argument("--vector-frontier", type=Path, required=True)
    ap.add_argument("--ir-dir", type=Path, required=True)
    ap.add_argument("--binding-dir", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()
    out = replay(a.candidate_manifest, a.vector_frontier, a.ir_dir, a.binding_dir)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": out["status"], "coverage": out["coverage"],
                      "violations": out["violations"][:50]}, indent=2, sort_keys=True))
    return 0 if not out["violations"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
