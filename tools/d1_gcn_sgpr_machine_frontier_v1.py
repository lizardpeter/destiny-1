#!/usr/bin/env python3
"""Exact ordinary SGPR/M0 definition-use frontier over the Destiny 1 GFX7 corpus.

EXEC, VCC and SCC are intentionally excluded because their machine/dataflow layers are
already closed separately. This census establishes the remaining scalar register identity
surface before scalar value SSA is attempted; it does not assign opcode-result meaning.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
from pathlib import Path

SCHEMA = "d1_gcn_sgpr_machine_frontier/v1"
STATUS = "D1_GCN_SGPR_MACHINE_FRONTIER_EXACT"
EXPECTED_PROGRAMS = 26464
EXPECTED_INSTRUCTIONS = 4896165
SREG = re.compile(r"^s(\d+)$")
SRANGE = re.compile(r"^s\[(\d+):(\d+)\]$")
EXCLUDED = {"exec", "exec_lo", "exec_hi", "vcc", "vcc_lo", "vcc_hi", "scc"}


def ordinary_scalar(reg: str) -> bool:
    return bool(SREG.fullmatch(reg or "")) or reg == "m0"


def build(ir_dir: Path) -> dict:
    violations: list[str] = []
    paths = sorted(ir_dir.glob("*.json"))
    if len(paths) != EXPECTED_PROGRAMS:
        violations.append(f"ir_file_count:{len(paths)}!={EXPECTED_PROGRAMS}")

    totals = collections.Counter()
    def_ops = collections.Counter()
    def_entries = collections.Counter()
    use_ops = collections.Counter()
    use_entries = collections.Counter()
    def_width = collections.Counter()
    use_width = collections.Counter()
    m0_def_ops = collections.Counter()
    m0_use_ops = collections.Counter()
    examples: dict[tuple[str, str], dict] = {}
    program_rows: list[dict] = []
    total_ins = 0
    max_sgpr = -1

    def remember(role: str, op: str, sha: str, x: dict, regs: list[str]) -> None:
        examples.setdefault((role, op), {
            "role": role,
            "gcn_sha256": sha,
            "instruction": x["index"],
            "address": x["address_hex"],
            "opcode": op,
            "operands": x.get("operands") or [],
            "registers": regs,
        })

    for p in paths:
        sha = p.stem.lower()
        d = json.loads(p.read_text())
        if d.get("status") != "D1_GCN_STRUCTURAL_IR_COMPLETE":
            violations.append(f"ir_status:{sha}:{d.get('status')!r}")
        if (d.get("parse_accounting") or {}).get("status") != "D1_GCN_STRUCTURAL_PARSE_ACCOUNTING_EXACT":
            violations.append(f"parse_status:{sha}")
        ins = d.get("instructions") or []
        total_ins += len(ins)
        pc = collections.Counter()
        program_max = -1
        for x in ins:
            defs = x.get("defs") or []
            uses = x.get("uses") or []
            if any(SRANGE.fullmatch(r or "") for r in defs):
                violations.append(f"range_def_not_normalized:{sha}:{x['index']}")
            if any(SRANGE.fullmatch(r or "") for r in uses):
                violations.append(f"range_use_not_normalized:{sha}:{x['index']}")
            sd = [r for r in defs if ordinary_scalar(r)]
            su = [r for r in uses if ordinary_scalar(r)]
            op = x["opcode"]
            if sd:
                totals["sgpr_def_instruction_count"] += 1
                totals["sgpr_def_entry_count"] += len(sd)
                def_width[len(sd)] += 1
                def_ops[op] += 1
                def_entries[op] += len(sd)
                pc["defs"] += len(sd)
                remember("def", op, sha, x, sd)
            if su:
                totals["sgpr_use_instruction_count"] += 1
                totals["sgpr_use_entry_count"] += len(su)
                use_width[len(su)] += 1
                use_ops[op] += 1
                use_entries[op] += len(su)
                pc["uses"] += len(su)
                remember("use", op, sha, x, su)
            if "m0" in sd:
                totals["m0_def_instruction_count"] += 1
                m0_def_ops[op] += 1
            if "m0" in su:
                totals["m0_use_instruction_count"] += 1
                m0_use_ops[op] += 1
            for r in [*sd, *su]:
                m = SREG.fullmatch(r)
                if m:
                    idx = int(m.group(1))
                    max_sgpr = max(max_sgpr, idx)
                    program_max = max(program_max, idx)
            # The previously closed special-status registers must never leak into this frontier.
            if any(r in EXCLUDED for r in sd + su):
                violations.append(f"excluded_status_leak:{sha}:{x['index']}:{sd}:{su}")
        program_rows.append({
            "gcn_sha256": sha,
            "instruction_count": len(ins),
            "ordinary_scalar_def_entry_count": pc["defs"],
            "ordinary_scalar_use_entry_count": pc["uses"],
            "max_sgpr_index": program_max,
        })

    if total_ins != EXPECTED_INSTRUCTIONS:
        violations.append(f"instruction_count:{total_ins}!={EXPECTED_INSTRUCTIONS}")
    totals["max_sgpr_index"] = max_sgpr

    coverage = {
        "exact_program_count": len(paths),
        "exact_instruction_count": total_ins,
        **dict(sorted(totals.items())),
        "sgpr_def_width_histogram": {str(k): v for k, v in sorted(def_width.items())},
        "sgpr_use_width_histogram": {str(k): v for k, v in sorted(use_width.items())},
        "sgpr_def_opcode_count": len(def_ops),
        "sgpr_def_opcode_counts": dict(sorted(def_ops.items())),
        "sgpr_def_entry_opcode_counts": dict(sorted(def_entries.items())),
        "sgpr_use_opcode_count": len(use_ops),
        "sgpr_use_opcode_counts": dict(sorted(use_ops.items())),
        "sgpr_use_entry_opcode_counts": dict(sorted(use_entries.items())),
        "m0_def_opcode_counts": dict(sorted(m0_def_ops.items())),
        "m0_use_opcode_counts": dict(sorted(m0_use_ops.items())),
        "shader_expression_semantic_promotions": 0,
    }
    return {
        "schema": SCHEMA,
        "status": STATUS if not violations else "D1_GCN_SGPR_MACHINE_FRONTIER_WITH_VIOLATIONS",
        "sources": {"ir_dir": str(ir_dir)},
        "coverage": coverage,
        "examples": [v for _, v in sorted(examples.items())],
        "programs": program_rows,
        "violations": violations,
        "semantic_boundary": {
            "exec_symbolic_dataflow": "GLOBAL_EXACT_SEPARATE_LAYER",
            "condition_mask_and_scc_dataflow": "GLOBAL_EXACT_SEPARATE_LAYER",
            "ordinary_sgpr_m0_identity_surface": "GLOBAL_EXACT" if not violations else "NOT_PROMOTED",
            "ordinary_sgpr_value_ssa": "NEXT_GATE" if not violations else "WITHHELD",
            "opcode_result_value_semantics": "WITHHELD",
            "shader_expression_semantics": "WITHHELD",
            "shader_expression_semantic_promotions": 0,
        },
        "policy": (
            "Every normalized ordinary SGPR and M0 structural definition/use is enumerated exactly. EXEC, VCC and SCC are "
            "excluded because their dedicated symbolic layers are already closed. This frontier records register identity only; "
            "scalar opcode result values and shader/material meaning are not inferred."
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
    print(json.dumps({"status": out["status"], "coverage": out["coverage"], "violations": out["violations"][:20]}, indent=2, sort_keys=True))
    return 0 if not out["violations"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
