#!/usr/bin/env python3
"""Trace exact literal owner/backlink evidence for D1 articulated resources.

Unlike the broad character-family census, this probe scans *every readable
entry payload* in a logical package family (subject only to a configurable size
cap) for aligned 32-bit FileHash/TagHash literals.  It is intended to answer a
narrow ownership question such as:

    which retail records serialize this model parent, skeleton, runtime rig,
    composition, animation control, wrapper, or clip together?

The scanner does not use package adjacency, entry-index proximity, names, bone
counts, or class similarity as evidence.  A reported relationship is a literal
aligned dword present in a decoded retail payload.
"""
from __future__ import annotations

import argparse
import collections
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_entry_extract import EntryReader


def scan_aligned_targets(payload: bytes, targets: dict[int, str]) -> list[dict]:
    """Return exact aligned dword target hits in one payload."""
    hits = []
    end = len(payload) - (len(payload) % 4)
    for off in range(0, end, 4):
        value = struct.unpack_from("<I", payload, off)[0]
        name = targets.get(value)
        if name is not None:
            hits.append({"offset": off, "target": name})
    return hits


def summarize_sources(source_rows: list[dict], target_names: list[str]) -> dict:
    """Build per-target backlinks plus exact co-occurrence groups."""
    backlinks = {t: [] for t in target_names}
    cooccurrence_hist = collections.Counter()
    cooccurrences = []

    for row in source_rows:
        distinct = sorted({h["target"] for h in row["hits"]})
        for target in distinct:
            offsets = [h["offset"] for h in row["hits"] if h["target"] == target]
            backlinks[target].append({
                "source": row["source"],
                "offsets": offsets,
                "cooccurring_targets": [x for x in distinct if x != target],
            })
        if len(distinct) >= 2:
            key = tuple(distinct)
            cooccurrence_hist[key] += 1
            cooccurrences.append({
                "source": row["source"],
                "targets": distinct,
                "hits": row["hits"],
            })

    return {
        "backlinks": backlinks,
        "cooccurrences": cooccurrences,
        "cooccurrence_groups": [
            {"targets": list(k), "source_count": n}
            for k, n in sorted(
                cooccurrence_hist.items(), key=lambda kv: (-kv[1], kv[0])
            )
        ],
    }


def scan_package(
    pkg: Path,
    runtime: Path,
    target_names: list[str],
    *,
    max_entry_size: int = 4_000_000,
) -> dict:
    r = EntryReader(pkg, runtime)
    normalized = [x.upper() for x in target_names]
    target_values = {int(x, 16): x for x in normalized}
    source_rows = []
    scanned = 0
    skipped_large = 0
    read_errors = []

    for e in r.entries:
        if not r.available(e["index"]):
            continue
        size = int(e["file_size"])
        if size <= 0:
            continue
        if size > max_entry_size:
            skipped_large += 1
            continue
        try:
            payload = r.entry(e["index"])
        except Exception as ex:
            read_errors.append({
                "entry_index": e["index"],
                "tag_hash": e["tag_hash"].upper(),
                "error": repr(ex),
            })
            continue
        scanned += 1
        hits = scan_aligned_targets(payload, target_values)
        if not hits:
            continue
        source_rows.append({
            "source": {
                "entry_index": e["index"],
                "tag_hash": e["tag_hash"].upper(),
                "reference": e["reference"].upper(),
                "type": e["type"],
                "subtype": e["subtype"],
                "size": size,
            },
            "hits": hits,
        })

    summary = summarize_sources(source_rows, normalized)
    return {
        "schema": "d1_character_owner_backlinks/v1",
        "package": str(r.pkg),
        "platform": r.h["platform"],
        "package_id": r.h["pkg_id"],
        "package_patch_id": r.h["patch_id"],
        "targets": normalized,
        "max_entry_size": max_entry_size,
        "scanned_entry_count": scanned,
        "skipped_large_entry_count": skipped_large,
        "read_error_count": len(read_errors),
        "source_with_hit_count": len(source_rows),
        "source_rows": source_rows,
        **summary,
        "read_errors": read_errors,
        "policy": (
            "Only exact aligned 32-bit target literals in decoded retail payloads are reported. "
            "Co-occurrence proves serialization in the same source payload, not semantic ownership by itself. "
            "Absence does not exclude indirect, indexed, cross-package, or non-literal ownership."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pkg", type=Path)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--target", action="append", required=True, help="8-hex TagHash/FileHash; repeat")
    ap.add_argument("--max-entry-size", type=int, default=4_000_000)
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args()

    for t in args.target:
        if len(t) != 8:
            ap.error(f"target must be 8 hex digits: {t!r}")
        try:
            int(t, 16)
        except ValueError:
            ap.error(f"target must be hex: {t!r}")

    out = scan_package(
        args.pkg,
        args.runtime,
        args.target,
        max_entry_size=args.max_entry_size,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "targets": out["targets"],
        "scanned_entry_count": out["scanned_entry_count"],
        "source_with_hit_count": out["source_with_hit_count"],
        "backlink_counts": {k: len(v) for k, v in out["backlinks"].items()},
        "cooccurrence_groups": out["cooccurrence_groups"][:20],
        "read_error_count": out["read_error_count"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
