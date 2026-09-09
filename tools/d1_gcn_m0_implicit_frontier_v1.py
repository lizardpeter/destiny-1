#!/usr/bin/env python3
"""Source-backed implicit-M0 consumer census for the exact Destiny 1 GFX7 corpus.

Structural def/use text does not expose architectural M0 dependencies. This layer closes
that gap before ordinary scalar SSA: VINTRP, relative-GPR indexing, LDS-memory DS forms,
FLAT LDS bounds, LDS_DIRECT, and send-message forms are inventoried explicitly. Forms
whose M0 dependency cannot be decided from the frozen source rules fail closed.
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

SCHEMA = "d1_gcn_m0_implicit_frontier/v1"
STATUS = "D1_GCN_M0_IMPLICIT_FRONTIER_EXACT"
EXPECTED_PROGRAMS = 26464
EXPECTED_INSTRUCTIONS = 4896165

AMD = {
    "vendor": "Advanced Micro Devices, Inc.",
    "title": "AMD Sea Islands Series Instruction Set Architecture",
    "document_id": "70653",
    "revision": "1.3",
    "release_date": "2013-12-01",
    "architecture": "GCN 2 / GFX7 / Sea Islands",
    "official_url": "https://docs.amd.com/v/u/en-US/sea-islands-instruction-set-architecture_0",
}

INTERP = {"v_interp_mov_f32", "v_interp_p1_f32", "v_interp_p2_f32"}
RELATIVE_GPR = {
    "v_movrels_b32", "v_movereld_b32", "v_movrelsd_b32",
    "s_movrels_b32", "s_movrels_b64", "s_movereld_b32", "s_movereld_b64",
}
# DS_SWIZZLE is explicitly not an LDS-memory-bank access and therefore does not consume
# M0's LDS size/clamp value for result semantics. Other observed DS forms are treated as
# LDS/GDS-memory operations and therefore M0-dependent unless a later source rule says otherwise.
DS_NON_MEMORY = {"ds_swizzle_b32"}


def source(locator: str) -> dict:
    return {**AMD, "locator": locator}


def classify_instruction(x: dict) -> tuple[str | None, str | None]:
    op = x["opcode"]
    operands = x.get("operands") or []
    assembly = x.get("assembly") or ""
    if op in INTERP:
        return "VINTRP_AUTOMATIC_M0", None
    if op in RELATIVE_GPR or "movrel" in op:
        if op in RELATIVE_GPR:
            return "RELATIVE_GPR_INDEX_M0", None
        return None, "UNCLASSIFIED_RELATIVE_GPR_FORM"
    if op.startswith("ds_"):
        if op in DS_NON_MEMORY:
            return "DS_NON_MEMORY_NO_M0_VALUE_DEPENDENCY", None
        return "LDS_DS_M0_BOUNDS", None
    if op.startswith("flat_"):
        return "FLAT_LDS_SIZE_M0", None
    if "lds_direct" in assembly.lower() or any("lds_direct" in str(z).lower() for z in operands):
        return "LDS_DIRECT_ADDRESS_M0", None
    if op.startswith("s_sendmsg") or op.startswith("s_sendmsg_rtn"):
        return None, "SENDMSG_REQUIRES_MESSAGE_SUBTYPE_CLASSIFICATION"
    return None, None


def build(ir_dir: Path) -> dict:
    violations: list[str] = []
    paths = sorted(ir_dir.glob("*.json"))
    if len(paths) != EXPECTED_PROGRAMS:
        violations.append(f"ir_file_count:{len(paths)}!={EXPECTED_PROGRAMS}")

    total_ins = 0
    category_counts = collections.Counter()
    opcode_counts: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    program_counts = collections.Counter()
    unresolved = []
    examples: dict[tuple[str, str], dict] = {}
    explicit_m0_defs = 0
    explicit_m0_uses = 0

    for p in paths:
        sha = p.stem.lower()
        d = json.loads(p.read_text())
        if d.get("status") != "D1_GCN_STRUCTURAL_IR_COMPLETE":
            violations.append(f"ir_status:{sha}:{d.get('status')!r}")
        if (d.get("parse_accounting") or {}).get("status") != "D1_GCN_STRUCTURAL_PARSE_ACCOUNTING_EXACT":
            violations.append(f"parse_status:{sha}")
        ins = d.get("instructions") or []
        total_ins += len(ins)
        seen_categories = set()
        for x in ins:
            defs = x.get("defs") or []
            uses = x.get("uses") or []
            if "m0" in defs:
                explicit_m0_defs += 1
            if "m0" in uses:
                explicit_m0_uses += 1
            category, problem = classify_instruction(x)
            if problem:
                unresolved.append({
                    "gcn_sha256": sha,
                    "instruction": x["index"],
                    "address": x["address_hex"],
                    "opcode": x["opcode"],
                    "operands": x.get("operands") or [],
                    "problem": problem,
                })
                continue
            if category:
                category_counts[category] += 1
                opcode_counts[category][x["opcode"]] += 1
                seen_categories.add(category)
                examples.setdefault((category, x["opcode"]), {
                    "category": category,
                    "gcn_sha256": sha,
                    "instruction": x["index"],
                    "address": x["address_hex"],
                    "opcode": x["opcode"],
                    "operands": x.get("operands") or [],
                })
        for c in seen_categories:
            program_counts[c] += 1

    if total_ins != EXPECTED_INSTRUCTIONS:
        violations.append(f"instruction_count:{total_ins}!={EXPECTED_INSTRUCTIONS}")
    if unresolved:
        violations.extend(
            f"unresolved:{r['gcn_sha256']}:{r['instruction']}:{r['opcode']}:{r['problem']}"
            for r in unresolved[:50]
        )

    # Structural M0 uses are expected to be zero at this boundary; all consumers below are
    # architectural implicit uses. If this changes, the generic parser has acquired explicit
    # M0 use information and this adapter must be reconciled rather than double-counting it.
    if explicit_m0_uses != 0:
        violations.append(f"unexpected_structural_m0_uses:{explicit_m0_uses}")

    implicit_value_use_categories = {
        k: v for k, v in category_counts.items()
        if k != "DS_NON_MEMORY_NO_M0_VALUE_DEPENDENCY"
    }
    implicit_value_use_count = sum(implicit_value_use_categories.values())
    coverage = {
        "exact_program_count": len(paths),
        "exact_instruction_count": total_ins,
        "explicit_m0_def_instruction_count": explicit_m0_defs,
        "structural_explicit_m0_use_instruction_count": explicit_m0_uses,
        "implicit_m0_value_use_instruction_count": implicit_value_use_count,
        "implicit_m0_category_counts": dict(sorted(category_counts.items())),
        "implicit_m0_value_use_category_counts": dict(sorted(implicit_value_use_categories.items())),
        "implicit_m0_program_counts": dict(sorted(program_counts.items())),
        "implicit_m0_opcode_counts": {
            k: dict(sorted(v.items())) for k, v in sorted(opcode_counts.items())
        },
        "unresolved_m0_sensitive_instruction_count": len(unresolved),
        "shader_expression_semantic_promotions": 0,
    }
    return {
        "schema": SCHEMA,
        "status": STATUS if not violations else "D1_GCN_M0_IMPLICIT_FRONTIER_WITH_VIOLATIONS",
        "source": AMD,
        "source_rules": {
            "VINTRP_AUTOMATIC_M0": source("Ch. 10 Parameter Interpolation: M0 use is automatic and must contain new_prim_mask + lds_param_offset"),
            "RELATIVE_GPR_INDEX_M0": source("Ch. 5/6 relative GPR indexing: S/V_MOVREL forms index SGPR/VGPR by M0"),
            "LDS_DS_M0_BOUNDS": source("Ch. 10 LDS Access: LDS operations use M0 size to clamp final address"),
            "DS_NON_MEMORY_NO_M0_VALUE_DEPENDENCY": source("Ch. 12 DS_SWIZZLE_B32: explicitly does not read or write DS memory banks"),
            "FLAT_LDS_SIZE_M0": source("Ch. 9 FLAT: implied M0[16:0] is LDS segment byte size used for address clamping"),
            "LDS_DIRECT_ADDRESS_M0": source("Instruction operand encoding SRC_LDS_DIRECT: LDS direct source address comes from M0"),
            "SENDMSG_REQUIRES_MESSAGE_SUBTYPE_CLASSIFICATION": source("Ch. 3 M0 memory descriptor: EMIT/CUT send-message data uses M0 and EXEC"),
        },
        "coverage": coverage,
        "examples": [v for _, v in sorted(examples.items())],
        "unresolved": unresolved,
        "violations": violations,
        "semantic_boundary": {
            "m0_structural_def_surface": "GLOBAL_EXACT" if not violations else "NOT_PROMOTED",
            "m0_implicit_consumer_surface": "GLOBAL_EXACT" if not violations else "NOT_PROMOTED",
            "ordinary_sgpr_m0_value_ssa": "NEXT_GATE" if not violations else "WITHHELD",
            "opcode_result_value_semantics": "WITHHELD",
            "shader_expression_semantics": "WITHHELD",
            "shader_expression_semantic_promotions": 0,
        },
        "policy": "M0 dependencies absent from assembly def/use text are promoted only where the Sea Islands ISA defines them. Any observed relative-GPR/send-message form outside the source-closed registry fails closed. DS_SWIZZLE is recorded as a DS-family non-memory operation, not as an M0 value consumer.",
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
