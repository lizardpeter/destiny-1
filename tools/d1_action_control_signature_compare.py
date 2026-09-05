#!/usr/bin/env python3
"""Compare decoded D1 80802C0E action controls without inferring ownership.

Inputs are JSON reports produced by d1_animation_control_state_map.py.  The goal is
strictly structural: expose which exact action StringHashes, selector indices, and
selected clip FileHashes agree or differ across controls.

A matching action set or matching clips are *not* an ownership edge.  This tool is
therefore useful for eliminating false equivalence between a weapon-pattern-owned
control and a shared first-person control while keeping any similarity explicitly
classified as diagnostic evidence only.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def _rows(report: dict) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for row in report["state_table"]["records"]:
        h = row["state_hash"].upper()
        selected = [x["tag_hash"].upper() for x in row.get("selected_animations", [])]
        out[h] = {
            "record_index": row["record_index"],
            "state_name": row.get("state_name"),
            "selection_start": row["selection_start"],
            "selection_count": row["selection_count"],
            "clips": selected,
        }
    return out


def control_signature(report: dict) -> dict:
    rows = _rows(report)
    return {
        "control": report.get("control", {}),
        "animation_count": report["animation_list"]["count"],
        "state_count": report["state_table"]["count"],
        "action_hashes": sorted(rows),
        "actions": rows,
    }


def compare_controls(left: dict, right: dict) -> dict:
    a = _rows(left)
    b = _rows(right)
    common = sorted(set(a) & set(b))
    left_only = sorted(set(a) - set(b))
    right_only = sorted(set(b) - set(a))
    comparisons = []
    for h in common:
        x, y = a[h], b[h]
        comparisons.append({
            "state_hash": h,
            "state_name": x.get("state_name") or y.get("state_name"),
            "left_record_index": x["record_index"],
            "right_record_index": y["record_index"],
            "same_record_index": x["record_index"] == y["record_index"],
            "left_selection_count": x["selection_count"],
            "right_selection_count": y["selection_count"],
            "same_selection_count": x["selection_count"] == y["selection_count"],
            "left_clips": x["clips"],
            "right_clips": y["clips"],
            "same_exact_clips": x["clips"] == y["clips"],
        })

    exact_clip_matches = [x for x in comparisons if x["same_exact_clips"]]
    exact_index_matches = [x for x in comparisons if x["same_record_index"]]
    return {
        "left_control": left.get("control", {}),
        "right_control": right.get("control", {}),
        "left_state_count": left["state_table"]["count"],
        "right_state_count": right["state_table"]["count"],
        "left_animation_count": left["animation_list"]["count"],
        "right_animation_count": right["animation_list"]["count"],
        "common_action_count": len(common),
        "left_only_action_count": len(left_only),
        "right_only_action_count": len(right_only),
        "left_only_action_hashes": left_only,
        "right_only_action_hashes": right_only,
        "same_action_hash_set": not left_only and not right_only,
        "exact_clip_match_count": len(exact_clip_matches),
        "exact_record_index_match_count": len(exact_index_matches),
        "common_actions": comparisons,
        "ownership_equivalence_proven": False,
        "policy": (
            "This comparison is diagnostic only. Matching action hashes, selector indices, "
            "selection counts, or clip FileHashes do not prove that two controls share an owner "
            "or that one selects the other. Only a serialized/table ownership edge may promote "
            "a shared-viewmodel assignment."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("left", type=Path)
    ap.add_argument("right", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args()
    left = json.loads(args.left.read_text())
    right = json.loads(args.right.read_text())
    out = compare_controls(left, right)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in (
        "left_state_count", "right_state_count", "left_animation_count",
        "right_animation_count", "common_action_count", "left_only_action_count",
        "right_only_action_count", "same_action_hash_set", "exact_clip_match_count",
        "exact_record_index_match_count", "ownership_equivalence_proven",
    )}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
