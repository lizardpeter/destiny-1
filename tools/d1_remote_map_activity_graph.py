#!/usr/bin/env python3
"""Resolve one exact named D1 SActivity_ROI map root remotely.

This is the split-TAR counterpart to d1_world_activity_map_root_census.py. It uses
the same source-pinned D1 layout and only changes the corpus backend:

  named SActivity_ROI / 8080052E
    -> BubbleDefinition / 808091E0
      -> MapContainer / 80808A54
        -> SMapDataTable / 808009A2

It complements d1_remote_activity_graph_extract.py: scenario roots describe activity
logic/dynamic entities, while map roots expose the underlying bubble/static-map graph.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_investment_arrangement_probe import filehash_pkg_index
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_split_tar_extract import SplitHttpTar
import d1_world_activity_map_root_census as roots


def norm(x: object) -> str:
    return str(x).upper().removeprefix("0X").zfill(8)


def package_of(h: str) -> int:
    return filehash_pkg_index(int(norm(h), 16))[0]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--activity-hash", required=True)
    ap.add_argument("--activity-name", required=True)
    ap.add_argument("--activity-class", default=roots.ACTIVITY_ROI)
    ap.add_argument("--member-catalog", type=Path, action="append", required=True)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--part-count", type=int, default=10)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    ah = norm(a.activity_hash)
    ac = norm(a.activity_class)
    if roots.canonical_named_class(ac) != roots.ACTIVITY_ROI:
        raise SystemExit(f"map activity class must be {roots.ACTIVITY_ROI}, got {ac}")

    catalogs = load_catalogs(a.member_catalog)
    base = a.base_url.rstrip("/")
    arc = SplitHttpTar(
        [f"{base}/packages.tar.{i:03d}" for i in range(1, a.part_count + 1)],
        retries=6,
        timeout=90,
    )
    c = RemoteCorpus(arc, catalogs, a.runtime)
    named = {
        "tag_hash": ah,
        "name": a.activity_name,
        "aliases": [a.activity_name],
        "index": 0,
        "named_table_indices": [0],
        "class_hash_raw_uint": ac,
        "class_hash_canonical": roots.ACTIVITY_ROI,
        "source_package_id": f"{package_of(ah):04X}",
    }
    parsed = roots.parse_activity(c, named)
    summary = roots.component_summary(parsed)
    violations = list(parsed.get("violations", []))
    report = {
        "schema": "d1_remote_map_activity_graph/v1",
        "status": (
            "D1_REMOTE_MAP_ACTIVITY_GRAPH_EXACT"
            if not violations and parsed.get("validation_ok")
            else "D1_REMOTE_MAP_ACTIVITY_GRAPH_WITH_VIOLATIONS"
        ),
        "activity": {
            "tag_hash": ah,
            "name": a.activity_name,
            "class_hash": roots.ACTIVITY_ROI,
            "package_id": f"{package_of(ah):04X}",
        },
        "summary": summary,
        "parsed": parsed,
        "violations": violations,
        "policy": (
            "The root identity is supplied from an exact current named-tag record. "
            "BubbleDefinition, MapContainer and SMapDataTable edges are decoded only through "
            "the source-pinned D1 SActivity_ROI schemas. Names are provenance and do not add "
            "ownership edges."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        "STATUS", report["status"],
        "ACTIVITY", ah,
        "BUBBLES", summary.get("bubble_count"),
        "MAP_CONTAINERS", summary.get("map_container_count"),
        "MAP_TABLES", summary.get("map_data_table_count"),
        "MAP_ENTRIES", summary.get("total_map_entries"),
        "VIOLATIONS", len(violations),
    )
    return 0 if report["status"] == "D1_REMOTE_MAP_ACTIVITY_GRAPH_EXACT" else 2


if __name__ == "__main__":
    raise SystemExit(main())
