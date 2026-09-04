#!/usr/bin/env python3
"""Sparse-scan a D1 logical package family for exact raw FileHash backlinks.

This intentionally makes almost no schema assumptions.  It searches decompressed
entry payloads for exact little-endian u32 FileHash values and records every
containing entry + byte offset.  By default only Tiger type-16 structured
entries are scanned; --all-types widens the census.

The physical _N siblings supplied with --member are one logical package
namespace.  RemoteLogicalPackage follows each block's patch_id to the proper
physical sibling, matching the rest of the D1 reversal tooling.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_remote_investment_parent_probe import RemoteLogicalPackage, parse_member
from d1_split_tar_extract import SplitHttpTar


def all_offsets(blob: bytes, needle: bytes) -> list[int]:
    out: list[int] = []
    start = 0
    while True:
        p = blob.find(needle, start)
        if p < 0:
            return out
        out.append(p)
        start = p + 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--package-id", type=lambda x: int(x, 0), required=True)
    ap.add_argument("--target", action="append", required=True,
                    help="8-hex FileHash to search for; repeatable")
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--part-count", type=int, default=10)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--member", action="append", type=parse_member, required=True)
    ap.add_argument("--all-types", action="store_true",
                    help="scan every logical entry instead of only type 16")
    ap.add_argument("--max-entry-size", type=lambda x: int(x, 0), default=0,
                    help="optional byte cap; 0 means unlimited")
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    if any(m.pkg_id != a.package_id for m in a.member):
        raise SystemExit("all --member package ids must equal --package-id")
    targets = sorted({x.upper().removeprefix("0X") for x in a.target})
    if any(len(x) != 8 for x in targets):
        raise SystemExit(f"targets must be 8 hex digits: {targets}")
    needles = {x: struct.pack("<I", int(x, 16)) for x in targets}

    base = a.base_url.rstrip("/")
    archive = SplitHttpTar(
        [f"{base}/packages.tar.{i:03d}" for i in range(1, a.part_count + 1)],
        retries=6,
        timeout=90,
    )
    r = RemoteLogicalPackage(archive, {m.patch_id: m for m in a.member}, a.runtime)

    candidates = []
    for e in r.entries:
        if not a.all_types and e["type"] != 16:
            continue
        if a.max_entry_size and int(e["file_size"]) > a.max_entry_size:
            continue
        candidates.append(e)

    hits = []
    errors = []
    refs = collections.Counter()
    types = collections.Counter()
    for n, e in enumerate(candidates, 1):
        try:
            b = r.entry(e["index"])
        except Exception as ex:
            errors.append({
                "tag_hash": e["tag_hash"].upper(),
                "entry_index": e["index"],
                "reference": e["reference"].upper(),
                "type": e["type"],
                "subtype": e["subtype"],
                "size": e["file_size"],
                "error": repr(ex),
            })
            continue
        found = []
        for target, needle in needles.items():
            offs = all_offsets(b, needle)
            if offs:
                found.append({"target": target, "offsets": offs, "count": len(offs)})
        if found:
            row = {
                "tag_hash": e["tag_hash"].upper(),
                "entry_index": e["index"],
                "reference": e["reference"].upper(),
                "type": e["type"],
                "subtype": e["subtype"],
                "size": e["file_size"],
                "entry_b": e.get("entry_b"),
                "payload_sha256": hashlib.sha256(b).hexdigest(),
                "hits": found,
            }
            hits.append(row)
            refs[row["reference"]] += 1
            types[f"{row['type']}:{row['subtype']}"] += 1
            print("BACKLINK", json.dumps(row, separators=(",", ":")), flush=True)
        if n % 500 == 0:
            print(
                f"{a.package_id:04X}: scanned {n}/{len(candidates)} candidates; "
                f"hits={len(hits)} blocks={len(r.block_cache)} errors={len(errors)}",
                flush=True,
            )

    report = {
        "package_id": a.package_id,
        "logical_view": r.view.name,
        "entry_count": len(r.entries),
        "scan_scope": "all_entries" if a.all_types else "type16_only",
        "max_entry_size": a.max_entry_size or None,
        "candidate_count": len(candidates),
        "targets": targets,
        "hit_entry_count": len(hits),
        "hit_occurrence_count": sum(x["count"] for row in hits for x in row["hits"]),
        "hit_reference_counts": dict(refs),
        "hit_type_counts": dict(types),
        "remote_blocks_read": len(r.block_cache),
        "hits": hits,
        "error_count": len(errors),
        "errors": errors[:300],
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k not in ("hits", "errors")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
