#!/usr/bin/env python3
"""Attach exact persistent-kill value/SCC-branch links to a renderer program.

This is a selective-checkpoint adapter. It never reconstructs or weakens existing
proof tiers. Only STRUCTURAL_ONLY rows explicitly named by an exact kill-control
extension may be promoted, after which coverage is recomputed from the authoritative
instruction-resolution ledger.
"""
from __future__ import annotations

import argparse
import collections
import copy
import json
from pathlib import Path


def contiguous(values):
    vals = sorted(set(values))
    if not vals:
        return []
    out = []
    lo = hi = vals[0]
    for x in vals[1:]:
        if x == hi + 1:
            hi = x
        else:
            out.append((lo, hi))
            lo = hi = x
    out.append((lo, hi))
    return out


def recompute_spans(program, old_spans):
    rows = program["instruction_resolution"]
    structural = [r["instruction"] for r in rows if r["primary_resolution"] == "STRUCTURAL_ONLY"]
    result = []
    for lo, hi in contiguous(structural):
        # Promotions can only split/remove prior structural spans, never create new
        # structural instructions. Preserve exact image/branch/EXEC metadata by
        # slicing the unique old containing span.
        parents = [s for s in old_spans if int(s["start_instruction"]) <= lo and hi <= int(s["end_instruction"])]
        if len(parents) != 1:
            raise ValueError(f"new structural span {lo}-{hi}: expected one old containing span, got {len(parents)}")
        parent = copy.deepcopy(parents[0])
        subset = rows[lo:hi + 1]
        ops = collections.Counter(r["opcode"] for r in subset)
        parent["start_instruction"] = lo
        parent["end_instruction"] = hi
        parent["instruction_count"] = hi - lo + 1
        parent["opcode_histogram"] = dict(sorted(ops.items()))
        for key in ("image_instructions", "branch_instructions", "exec_write_instructions"):
            if key in parent:
                parent[key] = [int(i) for i in parent[key] if lo <= int(i) <= hi]
        result.append(parent)
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--program", type=Path, required=True)
    ap.add_argument("--kill-control-extension", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    d = json.load(open(a.program))
    ext = json.load(open(a.kill_control_extension))
    violations = []

    try:
        assert d["status"] == "D1_GCN_RENDERER_PROGRAM_IR_EXACT_PARTIAL" and not d.get("violations")
        assert ext["status"] == "D1_GCN_EXPORT_KILL_CONTROL_EXTENSION_EXACT" and not ext.get("violations")
        p = d["program"]
        assert str(p["pixel_shader"]).upper() == str(ext["shader"]).upper()
        assert str(p["material"]).upper() == str(ext["material"]).upper()
        rows = p["instruction_resolution"]
        n = int(p["instruction_count"])
        assert len(rows) == n and [int(r["instruction"]) for r in rows] == list(range(n))
        old_spans = copy.deepcopy(p["coverage"]["structural_only_spans"])

        promoted_expression = []
        promoted_control = []
        payloads = []
        for q in ext["extensions"]:
            v = q["predicate_value"]
            b = q["scc_branch"]
            vi, bi = int(v["instruction"]), int(b["instruction"])
            assert vi != bi and 0 <= vi < n and 0 <= bi < n
            vr, br = rows[vi], rows[bi]
            assert vr["primary_resolution"] == "STRUCTURAL_ONLY", vr
            assert br["primary_resolution"] == "STRUCTURAL_ONLY", br
            assert vr["opcode"] == v["opcode"] == "v_subrev_f32"
            assert br["opcode"] == b["opcode"] == "s_cbranch_scc0"
            assert int(b["scc_writer_instruction"]) == int(q["kill_instruction"])
            assert b["scc_writer_opcode"] == "s_andn2_b64"
            assert b["exact_condition"] == "updated_persistent_export_mask == 0"
            assert b["encoded_target_address_hex"] == b["target_address_hex"]

            vr["primary_resolution"] = "EXPRESSION_EXACT"
            vr["evidence_tags"] = sorted(set(vr.get("evidence_tags", [])) | {
                "PERSISTENT_EXPORT_KILL_PREDICATE_VALUE_EXACT"
            })
            br["primary_resolution"] = "CONTROL_EXACT"
            br["evidence_tags"] = sorted(set(br.get("evidence_tags", [])) | {
                "PERSISTENT_EXPORT_KILL_SCC_BRANCH_EXACT"
            })
            promoted_expression.append(vi)
            promoted_control.append(bi)
            payloads.append(q)

        assert promoted_expression and promoted_control
        assert len(set(promoted_expression + promoted_control)) == len(promoted_expression) + len(promoted_control)

        counts = collections.Counter(r["primary_resolution"] for r in rows)
        structural = int(counts["STRUCTURAL_ONLY"])
        exact = n - structural
        cov = p["coverage"]
        cov["primary_resolution_counts"] = dict(sorted(counts.items()))
        cov["exact_nonstructural_instruction_count"] = exact
        cov["exact_nonstructural_fraction"] = exact / n
        cov["structural_only_instruction_count"] = structural
        cov["structural_only_fraction"] = structural / n
        cov["structural_only_spans"] = recompute_spans(p, old_spans)
        cov["kill_control_promoted_instruction_count"] = len(promoted_expression) + len(promoted_control)
        cov["kill_control_expression_instructions"] = sorted(promoted_expression)
        cov["kill_control_branch_instructions"] = sorted(promoted_control)

        p["persistent_export_kill_control_extensions"] = payloads
        d.setdefault("semantic_boundary", {})["persistent_export_kill_predicate_value"] = "EXACT"
        d["semantic_boundary"]["persistent_export_kill_scc_branch"] = "EXACT_CFG_REACHING_DEF_AND_SIMM16_TARGET"
        d["semantic_boundary"]["persistent_export_kill_visual_role"] = "WITHHELD"
    except Exception as exc:
        violations.append(repr(exc))

    if violations:
        out = {
            "schema_version": 1,
            "status": "D1_GCN_RENDERER_PROGRAM_KILL_CONTROL_PROMOTION_PARTIAL",
            "violations": violations,
        }
        rc = 2
    else:
        d["schema_version"] = max(3, int(d.get("schema_version", 0)))
        d["violations"] = []
        out = d
        rc = 0

    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({
        "status": out.get("status"),
        "violations": out.get("violations"),
        "coverage": out.get("program", {}).get("coverage"),
    }, indent=2))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
