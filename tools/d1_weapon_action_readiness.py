#!/usr/bin/env python3
"""Join resolved D1 weapon manifests to exact pattern-owned action bundles.

The generic weapon resolver and the pattern-action resolver deliberately solve
separate graph layers. This tool is the evidence gate between them: it maps an
inventory weapon to action-bundle candidates only through the already-proven
weapon_pattern_index join.

No weapon-type, adjacency, clip-similarity, CA-profile, or animation-name
inference is permitted here. Shared first-person ownership and pattern-owned
action bundles remain separate evidence dimensions until an exact graph edge is
proven between them.
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path


def build_readiness(manifest_source: dict, action_source: dict) -> dict:
    manifests = manifest_source.get("manifests", [])
    patterns = action_source.get("patterns", [])

    by_pattern: dict[int, dict] = {}
    duplicate_pattern_rows = []
    for row in patterns:
        idx = row.get("weapon_pattern_index")
        if idx is None:
            continue
        if idx in by_pattern:
            duplicate_pattern_rows.append(idx)
            continue
        by_pattern[idx] = row

    queues = {
        "pattern_action_bundle_ready": [],
        "shared_and_pattern_action_ready": [],
        "full_animated_weapon_candidate": [],
    }
    blocked = []
    blockers = collections.Counter()

    for m in manifests:
        inv = m.get("inventory_item_hash")
        idx = m.get("equipping", {}).get("weapon_pattern_index")
        st = m.get("status", {})
        visual = bool(st.get("visual_entity_selection_resolved"))
        internal = bool(st.get("weapon_pattern_resolved"))
        shared = bool(st.get("shared_viewmodel_context_resolved"))

        action_row = by_pattern.get(idx) if idx is not None else None
        bundles = list((action_row or {}).get("action_bundles", []))
        action_ready = bool(action_row) and bool(bundles)

        common = {
            "inventory_item_hash": inv,
            "inventory_definition": m.get("inventory_definition"),
            "weapon_pattern_index": idx,
            "art_arrangement_indices": [
                x.get("art_arrangement_index")
                for x in m.get("equipping", {}).get("art_arrangements", [])
            ],
        }

        action_payload = {
            **common,
            "pattern_entity": (action_row or {}).get("pattern_entity"),
            "weapon_type_hash": (action_row or {}).get("weapon_type_hash"),
            "action_bundles": bundles,
            "action_bundle_count": len(bundles),
        }

        if action_ready:
            queues["pattern_action_bundle_ready"].append(action_payload)
        if shared and action_ready:
            queues["shared_and_pattern_action_ready"].append({
                **action_payload,
                "shared_viewmodel": m.get("shared_viewmodel"),
                "shared_pattern_equivalence_proven": False,
            })
        if visual and internal and shared and action_ready:
            queues["full_animated_weapon_candidate"].append({
                **action_payload,
                "visual": m.get("visual"),
                "internal_weapon_pattern": m.get("internal_weapon_pattern"),
                "shared_viewmodel": m.get("shared_viewmodel"),
                "shared_pattern_equivalence_proven": False,
            })

        reasons = []
        if idx is None:
            reasons.append("missing_weapon_pattern_index")
        elif action_row is None:
            reasons.append("weapon_pattern_absent_from_action_resolution")
        elif not bundles:
            reasons.append("weapon_pattern_has_no_exact_action_bundle")
        if not visual:
            reasons.append("visual_entity_selection_unresolved")
        if not internal:
            reasons.append("weapon_pattern_unresolved")
        if not shared:
            reasons.append("shared_viewmodel_context_unresolved")

        if reasons:
            for reason in reasons:
                blockers[reason] += 1
            blocked.append({
                **common,
                "visual_ready": visual,
                "internal_ready": internal,
                "shared_ready": shared,
                "pattern_action_bundle_ready": action_ready,
                "blockers": reasons,
            })

    return {
        "schema": "d1_weapon_action_readiness/v1",
        "summary": {
            "manifest_count": len(manifests),
            "resolved_action_pattern_count": len(by_pattern),
            "pattern_action_bundle_ready": len(queues["pattern_action_bundle_ready"]),
            "shared_and_pattern_action_ready": len(queues["shared_and_pattern_action_ready"]),
            "full_animated_weapon_candidate": len(queues["full_animated_weapon_candidate"]),
            "blocked_count": len(blocked),
            "blockers_by_reason": dict(blockers.most_common()),
            "duplicate_action_pattern_rows": sorted(set(duplicate_pattern_rows)),
        },
        "queues": queues,
        "blocked": blocked,
        "policy": (
            "Inventory weapons join to pattern-owned action bundles only by exact weapon_pattern_index. "
            "A shared first-person owner and a pattern-owned action bundle may coexist for the same weapon, "
            "but this tool does not claim their controls/wrappers/clips are equivalent without a direct retail graph edge."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("weapon_manifests", type=Path)
    ap.add_argument("pattern_action_bundles", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args()

    manifests = json.loads(args.weapon_manifests.read_text())
    actions = json.loads(args.pattern_action_bundles.read_text())
    out = build_readiness(manifests, actions)
    out["sources"] = {
        "weapon_manifests": str(args.weapon_manifests),
        "pattern_action_bundles": str(args.pattern_action_bundles),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
