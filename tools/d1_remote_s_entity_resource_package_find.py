#!/usr/bin/env python3
"""Sparse-scan D1 ROI s_entity Resource[] arrays for cross-package targets.

D1 Rise of Iron SEntity (reference/class 0x80800734) stores a
DynamicArrayUnloaded of entity-resource entries at +0x20.  The row type is D1
0x80800715 / 0x0C bytes in the current Charm schema, and the first dword is a
FileHash Resource.  The resource may live in another package and can even be a
non-EntityResource in D1.

This tool is intentionally schema-level: it reports every s_entity whose
Resource[] contains a FileHash belonging to --target-package-id.  It does not
assume a specific child tag, resource class, render model, or assembly role.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_investment_arrangement_probe import dyn_header, filehash_pkg_index, h32
from d1_remote_investment_parent_probe import RemoteLogicalPackage, parse_member
from d1_split_tar_extract import SplitHttpTar

S_ENTITY_REF = "80800734"
RESOURCE_ARRAY_OFFSET = 0x20
RESOURCE_ROW_SIZE = 0x0C


def u32(b: bytes, o: int) -> int:
    if o < 0 or o + 4 > len(b):
        raise ValueError(f"u32 out of bounds at 0x{o:X}/0x{len(b):X}")
    return int.from_bytes(b[o:o+4], "little")


def parse_entity_resources(b: bytes) -> list[dict]:
    count, data = dyn_header(b, RESOURCE_ARRAY_OFFSET)
    out = []
    for i in range(count):
        o = data + i * RESOURCE_ROW_SIZE
        if o + RESOURCE_ROW_SIZE > len(b):
            raise ValueError(
                f"entity resource row {i}/{count} exceeds payload: 0x{o:X}+0x{RESOURCE_ROW_SIZE:X} > 0x{len(b):X}"
            )
        resource = u32(b, o)
        if resource in (0, 0xFFFFFFFF):
            pkg = idx = None
        else:
            pkg, idx = filehash_pkg_index(resource)
        out.append({
            "resource_index": i,
            "resource_hash": h32(resource),
            "resource_package_id": pkg,
            "resource_file_index": idx,
            "raw_row_hex": b[o:o+RESOURCE_ROW_SIZE].hex(),
        })
    return out


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

    entities = [e for e in r.entries if e["reference"].upper() == S_ENTITY_REF]
    storage_counts = collections.Counter((e["type"], e["subtype"]) for e in entities)
    resource_pkg_counts = collections.Counter()
    hits = []
    errors = []
    parsed_entities = 0
    resource_occurrences = 0

    for n, e in enumerate(entities, 1):
        try:
            b = r.entry(e["index"])
            resources = parse_entity_resources(b)
            parsed_entities += 1
            matching = []
            for x in resources:
                resource_occurrences += 1
                pkg = x["resource_package_id"]
                if pkg is not None:
                    resource_pkg_counts[pkg] += 1
                if pkg == a.target_package_id:
                    matching.append(x)
            if matching:
                row = {
                    "entity_hash": e["tag_hash"].upper(),
                    "entity_entry_index": e["index"],
                    "entity_entry_type": e["type"],
                    "entity_entry_subtype": e["subtype"],
                    "entity_size": e["file_size"],
                    "resource_count": len(resources),
                    "matching_resource_count": len(matching),
                    "matching_resources": matching,
                    "all_resources": resources,
                }
                hits.append(row)
                print("S_ENTITY_TARGET_RESOURCE", json.dumps(row, separators=(",", ":")), flush=True)
        except Exception as ex:
            errors.append({
                "entity_hash": e["tag_hash"].upper(),
                "entry_index": e["index"],
                "error": repr(ex),
            })
        if n % 500 == 0:
            print(
                f"{a.package_id:04X}: {n}/{len(entities)} s_entity; parsed={parsed_entities} "
                f"target_entities={len(hits)} blocks={len(r.block_cache)}",
                flush=True,
            )

    report = {
        "package_id": a.package_id,
        "logical_view": r.view.name,
        "entry_count": len(r.entries),
        "target_package_id": a.target_package_id,
        "s_entity_candidates": len(entities),
        "s_entity_storage_counts": {
            f"type{t}_subtype{s}": v for (t, s), v in sorted(storage_counts.items())
        },
        "parsed_s_entity_count": parsed_entities,
        "resource_occurrence_count": resource_occurrences,
        "resource_package_counts": {
            f"{k:04X}": v for k, v in sorted(resource_pkg_counts.items())
        },
        "target_entity_hit_count": len(hits),
        "target_resource_occurrence_count": sum(x["matching_resource_count"] for x in hits),
        "hits": hits,
        "remote_blocks_read": len(r.block_cache),
        "error_count": len(errors),
        "errors": errors[:200],
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k not in ("hits", "errors")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
