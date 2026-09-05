#!/usr/bin/env python3
"""Classify resolved D1 weapon manifests into deterministic export queues.

This is the gate between the resolver and the actual asset exporters.  A weapon
is never sent to a stage whose ownership inputs are unresolved.  The output is
therefore safe to consume in bulk CI jobs: each queue contains only manifests
that have all prerequisites for that layer, while blockers remain explicit.

Current layers:
  visual       inventory -> arrangement -> EntityDataROI
  internal     inventory -> weapon pattern -> sandbox pattern s_entity
  shared       exact runtime context -> shared viewmodel owner/rig/control/wrapper
  full_weapon  all three layers above

Geometry/material/texture and action export workers can consume these queues
independently; resolving shared animation context is not required to rip static
visuals, and vice versa.
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest_set", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args()

    src = json.loads(args.manifest_set.read_text())
    manifests = src.get("manifests", [])
    queues = {"visual": [], "internal": [], "shared": [], "full_weapon": []}
    blocked = []
    blockers = collections.Counter()

    for m in manifests:
        inv = m["inventory_item_hash"]
        st = m.get("status", {})
        visual = bool(st.get("visual_entity_selection_resolved"))
        internal = bool(st.get("weapon_pattern_resolved"))
        shared = bool(st.get("shared_viewmodel_context_resolved"))

        common = {
            "inventory_item_hash": inv,
            "inventory_definition": m.get("inventory_definition"),
            "art_arrangement_indices": [x.get("art_arrangement_index") for x in m.get("equipping", {}).get("art_arrangements", [])],
            "weapon_pattern_index": m.get("equipping", {}).get("weapon_pattern_index"),
        }
        if visual:
            queues["visual"].append({**common, "visual": m.get("visual")})
        if internal:
            queues["internal"].append({**common, "internal_weapon_pattern": m.get("internal_weapon_pattern")})
        if shared:
            queues["shared"].append({**common, "shared_viewmodel": m.get("shared_viewmodel")})
        if visual and internal and shared:
            queues["full_weapon"].append({**common, "visual": m.get("visual"), "internal_weapon_pattern": m.get("internal_weapon_pattern"), "shared_viewmodel": m.get("shared_viewmodel")})

        if not (visual and internal and shared):
            us = m.get("unresolved_edges", [])
            for u in us:
                blockers[u.get("edge", "UNKNOWN")] += 1
            blocked.append({
                **common,
                "visual_ready": visual,
                "internal_ready": internal,
                "shared_ready": shared,
                "unresolved_edges": us,
            })

    out = {
        "schema": "d1_weapon_export_readiness/v1",
        "source": str(args.manifest_set),
        "summary": {
            "manifest_count": len(manifests),
            "visual_ready": len(queues["visual"]),
            "internal_ready": len(queues["internal"]),
            "shared_ready": len(queues["shared"]),
            "full_weapon_ready": len(queues["full_weapon"]),
            "blocked_full_weapon": len(blocked),
            "blockers_by_edge": dict(blockers.most_common()),
        },
        "queues": queues,
        "blocked": blocked,
        "policy": "Queues are monotonic evidence gates. No exporter stage is scheduled from inferred adjacency, count similarity, or weapon-type similarity.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
