#!/usr/bin/env python3
"""Fail-closed corpus census for the lane-aware VGPR SSA boundary.

This is deliberately a structural frontier, not shader-expression lifting. It
proves what the existing exact structural IR says about VGPR definitions/uses
before per-lane SSA is introduced. Vector writes are *candidate* EXEC-gated
SSA writes here; no opcode is assigned shader-level meaning.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
from pathlib import Path

SCHEMA = "d1_gcn_vgpr_ssa_frontier/v1"
STATUS = "D1_GCN_VGPR_SSA_FRONTIER_CENSUS"
EXPECTED_PROGRAMS = 26464
EXPECTED_INSTRUCTIONS = 4896165

VGPR_RE = re.compile(r"^v([0-9]+)$")
SGPR_RE = re.compile(r"^s([0-9]+)$")
SPECIAL_REGS = {
    "vcc", "vcc_lo", "vcc_hi",
    "exec", "exec_lo", "exec_hi",
    "m0", "scc",
}
VECTOR_FAMILY_PREFIXES = (
    "v_", "ds_", "buffer_", "tbuffer_", "flat_", "global_", "image_",
)


def is_vgpr(x: str) -> bool:
    return bool(VGPR_RE.fullmatch(x or ""))


def valid_structural_reg(x: str) -> bool:
    return is_vgpr(x) or bool(SGPR_RE.fullmatch(x or "")) or x in SPECIAL_REGS


def family(op: str) -> str:
    for prefix in VECTOR_FAMILY_PREFIXES:
        if op.startswith(prefix):
            return prefix.rstrip("_")
    return "other"


def build(ir_dir: Path) -> dict:
    paths = sorted(ir_dir.glob("*.json"))
    violations: list[str] = []
    if len(paths) != EXPECTED_PROGRAMS:
        violations.append(f"ir_file_count:{len(paths)}!={EXPECTED_PROGRAMS}")

    c = collections.Counter()
    def_ops = collections.Counter()
    use_ops = collections.Counter()
    def_arity = collections.Counter()
    use_arity = collections.Counter()
    def_families = collections.Counter()
    rmw_ops = collections.Counter()
    examples: dict[tuple[str, str], dict] = {}
    programs = []
    total_ins = 0

    def remember(role: str, key: str, sha: str, x: dict) -> None:
        k = (role, key)
        if k not in examples:
            examples[k] = {
                "role": role,
                "key": key,
                "gcn_sha256": sha,
                "instruction": x["index"],
                "address": x["address_hex"],
                "opcode": x["opcode"],
                "operands": x.get("operands") or [],
                "defs": x.get("defs") or [],
                "uses": x.get("uses") or [],
            }

    for p in paths:
        sha = p.stem.lower()
        d = json.loads(p.read_text())
        ins = d.get("instructions") or []
        total_ins += len(ins)
        pc = collections.Counter()

        if d.get("status") != "D1_GCN_STRUCTURAL_IR_COMPLETE":
            violations.append(f"ir_status:{sha}:{d.get('status')!r}")
        if (d.get("parse_accounting") or {}).get("status") != "D1_GCN_STRUCTURAL_PARSE_ACCOUNTING_EXACT":
            violations.append(f"parse_status:{sha}")

        for x in ins:
            op = x["opcode"]
            defs = x.get("defs") or []
            uses = x.get("uses") or []

            for r in defs + uses:
                if not valid_structural_reg(r):
                    violations.append(f"invalid_structural_reg:{sha}:{x['index']}:{r}")

            vd = [r for r in defs if is_vgpr(r)]
            vu = [r for r in uses if is_vgpr(r)]
            if vd:
                c["vgpr_def_instruction_count"] += 1
                c["vgpr_def_register_count"] += len(vd)
                def_ops[op] += 1
                def_arity[len(vd)] += 1
                fam = family(op)
                def_families[fam] += 1
                pc["vgpr_def_instructions"] += 1
                pc["vgpr_def_registers"] += len(vd)
                c["candidate_exec_gated_write_instruction_count"] += 1
                c["candidate_exec_gated_write_register_count"] += len(vd)
                remember("vgpr_def_family", fam, sha, x)
                if fam == "other":
                    c["vgpr_def_other_family_instruction_count"] += 1
                    remember("other_family_vgpr_def", op, sha, x)
                if len(vd) > 1:
                    c["multi_vgpr_def_instruction_count"] += 1
                    remember("multi_vgpr_def", op, sha, x)
            if vu:
                c["vgpr_use_instruction_count"] += 1
                c["vgpr_use_register_count"] += len(vu)
                use_ops[op] += 1
                use_arity[len(vu)] += 1
                pc["vgpr_use_instructions"] += 1
                pc["vgpr_use_registers"] += len(vu)
            both = sorted(set(vd) & set(vu), key=lambda s: int(s[1:]))
            if both:
                c["vgpr_rmw_instruction_count"] += 1
                c["vgpr_rmw_register_count"] += len(both)
                rmw_ops[op] += 1
                remember("vgpr_rmw", op, sha, x)

            if vd:
                c["max_vgpr_defs_per_instruction"] = max(c["max_vgpr_defs_per_instruction"], len(vd))
            if vu:
                c["max_vgpr_uses_per_instruction"] = max(c["max_vgpr_uses_per_instruction"], len(vu))

        programs.append({
            "gcn_sha256": sha,
            "instruction_count": len(ins),
            "vgpr_counts": dict(sorted(pc.items())),
        })

    if total_ins != EXPECTED_INSTRUCTIONS:
        violations.append(f"instruction_count:{total_ins}!={EXPECTED_INSTRUCTIONS}")

    # Materialize zeros for durable, fail-closed downstream accounting.
    for k in (
        "vgpr_def_instruction_count",
        "vgpr_def_register_count",
        "vgpr_use_instruction_count",
        "vgpr_use_register_count",
        "candidate_exec_gated_write_instruction_count",
        "candidate_exec_gated_write_register_count",
        "multi_vgpr_def_instruction_count",
        "vgpr_rmw_instruction_count",
        "vgpr_rmw_register_count",
        "vgpr_def_other_family_instruction_count",
        "max_vgpr_defs_per_instruction",
        "max_vgpr_uses_per_instruction",
    ):
        c.setdefault(k, 0)

    coverage = {
        "exact_program_count": len(paths),
        "exact_instruction_count": total_ins,
        **dict(sorted(c.items())),
        "vgpr_def_opcode_counts": dict(sorted(def_ops.items())),
        "vgpr_use_opcode_counts": dict(sorted(use_ops.items())),
        "vgpr_def_arity_counts": {str(k): v for k, v in sorted(def_arity.items())},
        "vgpr_use_arity_counts": {str(k): v for k, v in sorted(use_arity.items())},
        "vgpr_def_family_counts": dict(sorted(def_families.items())),
        "vgpr_rmw_opcode_counts": dict(sorted(rmw_ops.items())),
        "shader_expression_semantic_promotions": 0,
    }
    return {
        "schema": SCHEMA,
        "status": STATUS if not violations else "D1_GCN_VGPR_SSA_FRONTIER_WITH_VIOLATIONS",
        "sources": {"ir_dir": str(ir_dir)},
        "coverage": coverage,
        "examples": [v for _, v in sorted(examples.items())],
        "programs": programs,
        "violations": violations,
        "semantic_boundary": {
            "structural_vgpr_def_use_census": "MEASURED",
            "exec_mask_symbolic_dataflow": "SOURCE_CLOSED_PREREQUISITE",
            "condition_symbolic_dataflow": "SOURCE_CLOSED_PREREQUISITE",
            "lane_aware_vgpr_ssa": "NEXT_GATE",
            "shader_expression_semantics": "WITHHELD",
            "shader_expression_semantic_promotions": 0,
        },
        "policy": (
            "Every structural VGPR definition/use in the exact global D1 corpus is "
            "inventoried before SSA promotion. VGPR definitions are only labeled "
            "candidate EXEC-gated writes here; no lane value or shader expression "
            "meaning is inferred by this frontier census."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ir-dir", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()
    out = build(a.ir_dir)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": out["status"],
        "coverage": out["coverage"],
        "violation_count": len(out["violations"]),
    }, indent=2, sort_keys=True))
    return 0 if not out["violations"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
