#!/usr/bin/env python3
"""Build a deterministic extraction queue from the exact D1 named-activity inventory.

The queue does not infer gameplay semantics from binary structures. `authored_name_family`
is only a convenience classification of Bungie's serialized named alias for scheduling,
reporting and canary selection. Parsing is selected solely by source-pinned named class:
  8080052E -> map_activity_graph
  80800616 -> scenario_activity_graph

Every admitted root remains in the queue, including names that do not match a known
prefix family.
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

MAP_CLASS = "8080052E"
SCENARIO_CLASS = "80800616"


def authored_family(name: str | None, cls: str) -> str:
    s = (name or "").lower()
    if cls == MAP_CLASS:
        return "map_root"
    rules = (
        (("moon_raid_", "venus_raid_", "raid_"), "raid_named"),
        (("strike_",), "strike_named"),
        (("patrol_", "hiveship_patrol", "plaguelands_patrol"), "patrol_named"),
        (("ambient_pvp_",), "pvp_ambient_named"),
        (("pvp_",), "pvp_named"),
        (("social_", "mercury_social"), "social_named"),
        (("arena_",), "arena_named"),
        (("mission_",), "mission_named"),
        (("quest_",), "quest_named"),
        (("act_",), "act_named"),
        (("ambient_",), "ambient_named"),
        (("cine_", "cinematic_"), "cinematic_named"),
    )
    for prefixes, label in rules:
        if s.startswith(prefixes):
            return label
    if "_portal_" in s or s.startswith(("cosmo_portal", "mars_portal", "moon_portal", "venus_portal")):
        return "portal_named"
    return "other_named"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    src = json.loads(a.inventory.read_text(encoding="utf-8"))
    if src.get("schema") != "d1_remote_named_activity_inventory/v1":
        raise SystemExit(f"unexpected inventory schema {src.get('schema')!r}")
    if src.get("status") != "D1_REMOTE_NAMED_ACTIVITY_INVENTORY_EXACT" or src.get("violations"):
        raise SystemExit("input inventory is not exact")

    rows = []
    counts = collections.Counter()
    methods = collections.Counter()
    for index, root in enumerate(src.get("activity_roots", [])):
        cls = root["class_hash_canonical"]
        if cls == MAP_CLASS:
            method = "map_activity_graph"
        elif cls == SCENARIO_CLASS:
            method = "scenario_activity_graph"
        else:
            raise SystemExit(f"unexpected admitted activity class {cls}")
        family = authored_family(root.get("name"), cls)
        counts[family] += 1
        methods[method] += 1
        rows.append({
            "queue_index": index,
            "tag_hash": root["tag_hash"],
            "class_hash": cls,
            "extraction_method": method,
            "authored_name": root.get("name"),
            "aliases": root.get("aliases", []),
            "authored_name_family": family,
            "tag_encoded_package_id": root.get("tag_encoded_package_id"),
            "registration_package_ids": root.get("registration_package_ids", []),
            "cross_package_registration": any(
                r.get("registered_by_package_id") != root.get("tag_encoded_package_id")
                for r in root.get("registrations", [])
            ),
        })

    if len(rows) != src.get("activity_root_count"):
        raise SystemExit("queue lost activity roots")
    if len({x["tag_hash"] for x in rows}) != len(rows):
        raise SystemExit("queue contains duplicate activity root hashes")

    report = {
        "schema": "d1_activity_extraction_queue/v1",
        "status": "D1_ACTIVITY_EXTRACTION_QUEUE_EXACT",
        "input_activity_root_count": src["activity_root_count"],
        "queue_count": len(rows),
        "extraction_method_counts": dict(methods),
        "authored_name_family_counts": dict(sorted(counts.items())),
        "queue": rows,
        "policy": (
            "Every exact named activity root is retained. Extraction method is determined only "
            "by the source-pinned named class. authored_name_family is a scheduling/reporting "
            "classification over serialized Bungie names and does not alter parsing or establish "
            "binary gameplay semantics. Unknown name patterns remain other_named rather than "
            "being guessed."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("STATUS", report["status"], "QUEUE", len(rows), "METHODS", dict(methods), "NAME_FAMILIES", dict(counts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
