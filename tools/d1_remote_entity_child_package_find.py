#!/usr/bin/env python3
"""Sparse-scan one D1 package family for EntityChildren targeting a package id.

This is the package-level companion to d1_remote_entity_child_find.py. It uses
the exact same final-era ROI EntityChildren structure, but matches every child
FileHash whose decoded package id equals --target-package-id. This is useful
when the concrete child tag is not yet known but the component package family
is known (for example, determining which Investment-facing visual entity owns
children in gear_weapons_011c).
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_remote_entity_child_find import (
    ENTITY_RESOURCE_REF,
    parse_children_resource,
)
from d1_remote_investment_parent_probe import RemoteLogicalPackage, parse_member
from d1_split_tar_extract import SplitHttpTar


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--package-id", type=lambda x: int(x, 0), required=True)
    ap.add_argument("--target-package-id", type=lambda x: int(x, 0), required=True)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--part-count", type=int, default=10)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--member", action="append", type=parse_member, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    if any(m.pkg_id != a.package_id for m in a.member):
        raise SystemExit("all --member package ids must equal --package-id")

    base = a.base_url.rstrip("/")
    arc = SplitHttpTar(
        [f"{base}/packages.tar.{i:03d}" for i in range(1, a.part_count + 1)],
        retries=6,
        timeout=90,
    )
    r = RemoteLogicalPackage(arc, {m.patch_id: m for m in a.member}, a.runtime)

    candidates = [
        e for e in r.entries
        if e["type"] == 16
        and e["subtype"] == 0
        and e["reference"].upper() == ENTITY_RESOURCE_REF
    ]

    child_resources = []
    hits = []
    errors = []
    all_child_pkg_counts = collections.Counter()

    for n, e in enumerate(candidates, 1):
        try:
            b = r.entry(e["index"])
            parsed = parse_children_resource(b)
            if parsed is None:
                continue
            matching_children = []
            for ch in parsed["children"]:
                pkg = ch.get("package_id")
                if pkg is not None:
                    all_child_pkg_counts[pkg] += 1
                if pkg == a.target_package_id:
                    matching_children.append(ch)
            row = {
                "resource_tag": e["tag_hash"].upper(),
                "entry_index": e["index"],
                "size": e["file_size"],
                "child_count": parsed["child_count"],
                "children": parsed["children"],
                "matching_children": matching_children,
                "matching_child_count": len(matching_children),
            }
            child_resources.append(row)
            if matching_children:
                hit = {
                    "resource_tag": row["resource_tag"],
                    "resource_entry_index": row["entry_index"],
                    "resource_size": row["size"],
                    "total_child_count": row["child_count"],
                    "matching_children": matching_children,
                }
                hits.append(hit)
                print("TARGET CHILD PACKAGE", json.dumps(hit, sort_keys=True), flush=True)
        except Exception as ex:
            errors.append({
                "resource_tag": e["tag_hash"].upper(),
                "entry_index": e["index"],
                "error": repr(ex),
            })
        if n % 500 == 0:
            print(
                f"{a.package_id:04X}: {n}/{len(candidates)} EntityResources; "
                f"children={len(child_resources)} target_hits={len(hits)} "
                f"blocks={len(r.block_cache)}",
                flush=True,
            )

    report = {
        "package_id": a.package_id,
        "logical_view": r.view.name,
        "entry_count": len(r.entries),
        "target_package_id": a.target_package_id,
        "entity_resource_candidates": len(candidates),
        "entity_children_resource_count": len(child_resources),
        "target_resource_hit_count": len(hits),
        "target_child_occurrence_count": sum(
            len(x["matching_children"]) for x in hits
        ),
        "remote_blocks_read": len(r.block_cache),
        "child_package_counts": {
            f"{k:04X}": v for k, v in sorted(all_child_pkg_counts.items())
        },
        "hits": hits,
        "error_count": len(errors),
        "errors": errors[:200],
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "errors"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
