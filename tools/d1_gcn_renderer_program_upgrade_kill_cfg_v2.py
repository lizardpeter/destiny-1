#!/usr/bin/env python3
"""Upgrade an exact partial renderer-program IR with CFG-aware kill-mask proof v2.

This is a selective-checkpoint adapter. It does not rebuild already-green expression,
loop, cbuffer, MIMG or terminal-MRT layers. It accepts one immutable renderer program
and one independently exact v2 kill/branch contract, replaces only the superseded
linear kill metadata, promotes only newly source/CFG-closed control instructions, and
recomputes the coverage ledger from instruction rows.
"""
from __future__ import annotations
import argparse, collections, json
from pathlib import Path


def contiguous(values):
    vals = sorted(set(values))
    if not vals:
        return []
    out = []
    a = b = vals[0]
    for x in vals[1:]:
        if x == b + 1:
            b = x
        else:
            out.append((a, b))
            a = b = x
    out.append((a, b))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--program", type=Path, required=True)
    ap.add_argument("--kill-cfg-v2", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    d = json.load(open(a.program))
    kv2 = json.load(open(a.kill_cfg_v2))
    violations = []

    try:
        assert d["status"] == "D1_GCN_RENDERER_PROGRAM_IR_EXACT_PARTIAL"
        assert not d["violations"]
        assert kv2["status"] == "D1_GCN_EXPORT_KILL_CFG_CONTRACT_COMPLETE"
        assert not kv2["violations"]

        p = d["program"]
        assert p["pixel_shader"] == kv2["shader"]
        assert p["material"] == kv2["material"]
        n = p["instruction_count"]
        rows = p["instruction_resolution"]
        assert n == 456 and len(rows) == n

        before = p["coverage"]
        assert before["primary_resolution_counts"] == {
            "CONTROL_EXACT": 16,
            "EXPRESSION_EXACT": 161,
            "INPUT_PROVENANCE_EXACT": 19,
            "RECURRENCE_EXACT": 36,
            "STRUCTURAL_ONLY": 224,
        }, before
        assert before["exact_nonstructural_instruction_count"] == 232
        assert len(kv2["contracts"]) == 1

        for r in rows:
            r["evidence_tags"] = [
                x for x in r.get("evidence_tags", [])
                if x != "PERSISTENT_EXPORT_KILL"
            ]

        promoted_control = set()
        for q in kv2["contracts"]:
            pred = q["predicate"]
            br = q["branch"]
            fall = q["mrt1_paths"][0]
            zero = q["mrt1_paths"][1]
            mrt0 = q["mrt0"]

            exact_control = {
                int(q["mask_initialized_instruction"]),
                int(pred["sample_instruction"]),
                int(pred["threshold_load_instruction"]),
                int(pred["difference_instruction"]),
                int(pred["compare_instruction"]),
                int(q["kill_instruction"]),
                int(br["instruction"]),
                int(fall["mask_apply_instruction"]),
                int(fall["wqm_instruction"]),
                int(mrt0["mask_restore_instruction"]),
            }
            promoted_control |= exact_control
            for i in exact_control:
                rows[i]["evidence_tags"].append("PERSISTENT_EXPORT_KILL_CFG_V2")

            rows[int(br["prebranch_exec_writer_instruction"])]["evidence_tags"].append(
                "PERSISTENT_EXPORT_KILL_CFG_V2_PREBRANCH_EXEC"
            )
            rows[int(br["target_instruction"])]["evidence_tags"].append(
                "PERSISTENT_EXPORT_KILL_CFG_V2_ZERO_MASK_TARGET"
            )
            rows[int(fall["export_instruction"])]["evidence_tags"].append(
                "PERSISTENT_EXPORT_KILL_CFG_V2_MRT1_PATH_SENSITIVE"
            )
            rows[int(zero["export_instruction"])]["evidence_tags"].append(
                "PERSISTENT_EXPORT_KILL_CFG_V2_MRT1_PATH_SENSITIVE"
            )
            rows[int(mrt0["export_instruction"])]["evidence_tags"].append(
                "PERSISTENT_EXPORT_KILL_CFG_V2_MRT0_ALWAYS_MASKED"
            )

        newly_promoted = []
        for i in sorted(promoted_control):
            if rows[i]["primary_resolution"] == "STRUCTURAL_ONLY":
                rows[i]["primary_resolution"] = "CONTROL_EXACT"
                newly_promoted.append(i)

        for r in rows:
            r["evidence_tags"] = sorted(set(r["evidence_tags"]))

        assert newly_promoted == [335, 338], newly_promoted

        p["persistent_export_kills"] = kv2["contracts"]
        p["persistent_export_kill_contract_version"] = 2

        counts = collections.Counter(r["primary_resolution"] for r in rows)
        structural = {
            int(r["instruction"])
            for r in rows
            if r["primary_resolution"] == "STRUCTURAL_ONLY"
        }
        spans = []
        for lo, hi in contiguous(structural):
            sub = rows[lo : hi + 1]
            ops = collections.Counter(r["opcode"] for r in sub)
            spans.append(
                {
                    "start_instruction": lo,
                    "end_instruction": hi,
                    "instruction_count": hi - lo + 1,
                    "opcode_histogram": dict(sorted(ops.items())),
                    "boundary": "STRUCTURAL_ONLY_NO_VALUE_EXPRESSION_PROMOTION",
                }
            )

        cov = p["coverage"]
        cov["primary_resolution_counts"] = dict(sorted(counts.items()))
        cov["exact_nonstructural_instruction_count"] = n - counts["STRUCTURAL_ONLY"]
        cov["structural_only_instruction_count"] = counts["STRUCTURAL_ONLY"]
        cov["structural_only_spans"] = spans
        cov["kill_cfg_v2_newly_promoted_control_instructions"] = newly_promoted

        assert cov["primary_resolution_counts"] == {
            "CONTROL_EXACT": 18,
            "EXPRESSION_EXACT": 161,
            "INPUT_PROVENANCE_EXACT": 19,
            "RECURRENCE_EXACT": 36,
            "STRUCTURAL_ONLY": 222,
        }, cov
        assert cov["exact_nonstructural_instruction_count"] == 234
        assert cov["structural_only_instruction_count"] == 222

        d["schema_version"] = max(int(d.get("schema_version", 1)), 3)
        d["semantic_boundary"]["persistent_export_kill_cfg"] = "EXACT_PATH_AWARE_V2"
        d["semantic_boundary"]["mrt1_zero_mask_export_meaning"] = "WITHHELD"
        d["semantic_boundary"]["full_mrt_value_expression_tree"] = "INCOMPLETE"
        d["semantic_boundary"]["remaining_straight_line_value_dataflow"] = "NEXT_GATE"
    except Exception as exc:
        violations.append(repr(exc))

    d["violations"] = violations
    if violations:
        d["status"] = "D1_GCN_RENDERER_PROGRAM_IR_PARTIAL_VIOLATION"

    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(d, indent=2) + "\n")
    print(
        json.dumps(
            {
                "status": d.get("status"),
                "violations": violations,
                "coverage": d.get("program", {}).get("coverage"),
            },
            indent=2,
        )
    )
    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
