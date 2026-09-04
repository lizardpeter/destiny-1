#!/usr/bin/env python3
"""Census a Destiny 1 Tiger logical package family without guessing patch precedence.

A physical `*_N.pkg` member supplies its own entry/block tables, while block records
can point at sibling patch members.  This tool discovers every numeric sibling,
opens each through EntryReader, and reports the union of TagHashes plus duplicate
metadata/content relationships.

It intentionally does NOT choose a winning duplicate when physical members disagree.
The purpose is to establish the retail patch/override rules from evidence first.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from d1_entry_extract import EntryReader

MEMBER_RE = re.compile(r"^(?P<base>.+)_(?P<patch>\d+)\.pkg$", re.IGNORECASE)


def family_members(path: Path) -> list[tuple[int, Path]]:
    path = path.resolve()
    m = MEMBER_RE.match(path.name)
    if not m:
        raise ValueError(f"expected numeric patch-member filename, got {path.name}")
    base = m.group("base")
    out = []
    for p in path.parent.glob(f"{base}_*.pkg"):
        mm = MEMBER_RE.match(p.name)
        if mm and mm.group("base") == base:
            out.append((int(mm.group("patch")), p.resolve()))
    if not out:
        raise FileNotFoundError(f"no family members found for {path}")
    return sorted(out)


def entry_meta(e: dict) -> tuple:
    return (
        int(e["type"]), int(e["subtype"]), e["reference"].upper(),
        int(e["file_size"]), int(e["starting_block"]), int(e["starting_block_offset"]),
        e["entry_b"].upper(),
    )


def safe_payload(reader: EntryReader, e: dict) -> dict:
    row = {"available": reader.available(e["index"])}
    if not row["available"]:
        return row
    try:
        b = reader.entry(e["index"])
        row.update(payload_size=len(b), sha256=hashlib.sha256(b).hexdigest())
    except Exception as ex:
        row["error"] = repr(ex)
    return row


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pkg", type=Path, help="any numeric member of the logical family")
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--tag-hash", action="append", default=[])
    ap.add_argument("--reference", action="append", default=[], help="filter/report entries whose reference/class hash matches")
    ap.add_argument("--include-payload-hashes", action="store_true", help="hash all duplicate/selected payloads; slower")
    ap.add_argument("-o", "--output", type=Path)
    args = ap.parse_args()

    members = family_members(args.pkg)
    readers = []
    for patch, path in members:
        r = EntryReader(path, args.runtime)
        readers.append((patch, r))

    pkg_ids = {int(r.h["pkg_id"]) for _, r in readers}
    platforms = {r.h["platform"] for _, r in readers}
    if len(pkg_ids) != 1 or len(platforms) != 1:
        raise RuntimeError(f"family header mismatch pkg_ids={pkg_ids} platforms={platforms}")

    occurrences: dict[str, list[dict]] = defaultdict(list)
    ref_counts = Counter()
    member_rows = []
    for patch, r in readers:
        member_rows.append({
            "patch_member": patch,
            "path": str(r.pkg),
            "entry_count": len(r.entries),
            "block_count": len(r.blocks),
        })
        for e in r.entries:
            h = e["tag_hash"].upper()
            ref_counts[e["reference"].upper()] += 1
            occurrences[h].append({
                "patch_member": patch,
                "reader": r,
                "entry": e,
            })

    wanted = {x.upper().removeprefix("0X") for x in args.tag_hash}
    refs = {x.upper().removeprefix("0X") for x in args.reference}

    duplicate_rows = []
    identical_meta_duplicates = 0
    conflicting_meta_duplicates = 0
    for h, occs in sorted(occurrences.items()):
        if len(occs) < 2:
            continue
        metas = {entry_meta(x["entry"]) for x in occs}
        same = len(metas) == 1
        identical_meta_duplicates += int(same)
        conflicting_meta_duplicates += int(not same)
        row = {
            "tag_hash": h,
            "occurrence_count": len(occs),
            "metadata_identical": same,
            "occurrences": [],
        }
        for x in occs:
            e = x["entry"]
            rr = {
                "patch_member": x["patch_member"],
                "entry_index": e["index"],
                "type": e["type"], "subtype": e["subtype"],
                "reference": e["reference"], "file_size": e["file_size"],
                "starting_block": e["starting_block"],
                "starting_block_offset": e["starting_block_offset"],
                "entry_b": e["entry_b"],
                "available": x["reader"].available(e["index"]),
            }
            if args.include_payload_hashes:
                rr.update(safe_payload(x["reader"], e))
            row["occurrences"].append(rr)
        duplicate_rows.append(row)

    selected = []
    for h, occs in sorted(occurrences.items()):
        if wanted and h not in wanted:
            continue
        if refs and not any(x["entry"]["reference"].upper() in refs for x in occs):
            continue
        if not wanted and not refs:
            continue
        row = {"tag_hash": h, "occurrences": []}
        for x in occs:
            e = x["entry"]
            rr = {
                "patch_member": x["patch_member"], "entry_index": e["index"],
                "type": e["type"], "subtype": e["subtype"], "reference": e["reference"],
                "file_size": e["file_size"], "starting_block": e["starting_block"],
                "starting_block_offset": e["starting_block_offset"], "entry_b": e["entry_b"],
            }
            rr.update(safe_payload(x["reader"], e))
            row["occurrences"].append(rr)
        selected.append(row)

    missing = sorted(wanted - set(occurrences))
    report = {
        "platform": next(iter(platforms)),
        "pkg_id": next(iter(pkg_ids)),
        "family_members": member_rows,
        "union_tag_hash_count": len(occurrences),
        "total_physical_entry_occurrences": sum(len(x) for x in occurrences.values()),
        "duplicate_tag_hash_count": len(duplicate_rows),
        "duplicate_metadata_identical_count": identical_meta_duplicates,
        "duplicate_metadata_conflicting_count": conflicting_meta_duplicates,
        "reference_frequency": dict(sorted(ref_counts.items())),
        "requested_missing": missing,
        "selected": selected,
        "duplicates": duplicate_rows,
        "policy": "census only; no duplicate/override precedence inferred",
    }
    text = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n")
        print(f"wrote {args.output}")
    else:
        print(text)


if __name__ == "__main__":
    main()
