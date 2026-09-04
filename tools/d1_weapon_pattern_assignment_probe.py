#!/usr/bin/env python3
"""Decode the Destiny 1 ROI weapon-pattern -> sandbox-pattern entity join.

Retail D1 chain (independently corroborated by Charm):

  80A5FFA9
    D1 AA528080-like outer table
    DynamicArrayUnloaded<BC338080> at +0x08
    each row is 0x20 bytes:
      +0x00 PatternGlobalTagIdHash
      +0x04 WeaponContentGroupHash
      +0x08 WeaponTypeHash
      +0x0C PatternHash

  80A7E1DC
    D1 41038080 sandbox-pattern assignment map
    DynamicArrayUnloaded<D7058080> at +0x08
    each row is 0x08 bytes:
      +0x00 ApiHash (PatternGlobalTagIdHash lookup key)
      +0x04 EntityRelationHashROI (FileHash)

Charm's D1 path binary-searches 80A7E1DC by PatternGlobalTagIdHash and accepts
the relation when its entry reference is 0x80800734 (s_entity).  This tool
reconstructs that join directly from retail package bytes and optionally
validates the resulting FileHashes against a recovered logical target package.

No appearance/assembly semantics are inferred here: this establishes the
retail pattern entity selected for each weapon-pattern index.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_entry_extract import EntryReader
from d1_investment_arrangement_probe import dyn_header, entry_payload, filehash_pkg_index, h32

WEAPON_PATTERN_TABLE = "80A5FFA9"
SANDBOX_PATTERN_ASSIGNMENTS = "80A7E1DC"
D1_S_ENTITY_REFERENCE = "80800734"


def u32(b: bytes, o: int) -> int:
    if o < 0 or o + 4 > len(b):
        raise ValueError(f"u32 out of bounds at 0x{o:X} / 0x{len(b):X}")
    return struct.unpack_from("<I", b, o)[0]


def parse_weapon_patterns(b: bytes) -> list[dict]:
    count, data = dyn_header(b, 0x08)
    rows: list[dict] = []
    for i in range(count):
        o = data + i * 0x20
        if o + 0x20 > len(b):
            raise ValueError(f"weapon pattern {i} exceeds entry at 0x{o:X}")
        pgtid = u32(b, o + 0x00)
        wcg = u32(b, o + 0x04)
        wtype = u32(b, o + 0x08)
        pattern = u32(b, o + 0x0C)
        rows.append({
            "weapon_pattern_index": i,
            "pattern_global_tag_id_hash": h32(pgtid),
            "weapon_content_group_hash": h32(wcg),
            "weapon_type_hash": h32(wtype),
            "pattern_hash": h32(pattern),
            "raw_tail_hex": b[o + 0x10:o + 0x20].hex(),
        })
    return rows


def parse_sandbox_assignments(b: bytes) -> list[dict]:
    count, data = dyn_header(b, 0x08)
    rows: list[dict] = []
    prev = None
    for i in range(count):
        o = data + i * 8
        if o + 8 > len(b):
            raise ValueError(f"sandbox assignment {i} exceeds entry at 0x{o:X}")
        api_hash = u32(b, o)
        relation = u32(b, o + 4)
        if prev is not None and api_hash < prev:
            raise ValueError(
                f"sandbox assignment table is not sorted at row {i}: {api_hash:08X} < {prev:08X}"
            )
        prev = api_hash
        pkg, idx = filehash_pkg_index(relation) if relation not in (0, 0xFFFFFFFF) else (-1, -1)
        rows.append({
            "assignment_index": i,
            "api_hash": h32(api_hash),
            "entity_relation_hash": h32(relation),
            "entity_relation_package_id": pkg if pkg >= 0 else None,
            "entity_relation_file_index": idx if idx >= 0 else None,
        })
    return rows


def validate_target_relation(reader: EntryReader, relation_hash: str) -> dict:
    by = {e["tag_hash"].upper(): e for e in reader.entries}
    e = by.get(relation_hash.upper())
    if e is None:
        return {
            "resolved": False,
            "reason": "relation hash absent from supplied target logical snapshot",
        }
    rec = {
        "resolved": True,
        "entry_index": e["index"],
        "reference": e["reference"].upper(),
        "size": e["file_size"],
        "available": reader.available(e["index"]),
        "is_s_entity": e["reference"].upper() == D1_S_ENTITY_REFERENCE,
    }
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("weapon_pattern_pkg", type=Path, help="012f logical view containing 80A5FFA9")
    ap.add_argument("sandbox_assignment_pkg", type=Path, help="013f logical view containing 80A7E1DC")
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--target-package-id", type=lambda x: int(x, 0), help="filter entity relations to one package id")
    ap.add_argument("--target-entity", action="append", default=[], help="filter/report exact relation FileHash; repeatable")
    ap.add_argument("--target-pkg", type=Path, help="optional recovered logical package used to validate target relation references")
    ap.add_argument("-o", "--output", type=Path)
    args = ap.parse_args()

    pr = EntryReader(args.weapon_pattern_pkg, args.runtime)
    sr = EntryReader(args.sandbox_assignment_pkg, args.runtime)
    pe, pb = entry_payload(pr, WEAPON_PATTERN_TABLE)
    se, sb = entry_payload(sr, SANDBOX_PATTERN_ASSIGNMENTS)

    patterns = parse_weapon_patterns(pb)
    assignments = parse_sandbox_assignments(sb)
    assignment_by_api = {x["api_hash"]: x for x in assignments}
    if len(assignment_by_api) != len(assignments):
        raise ValueError("duplicate ApiHash keys in sandbox assignment table")

    target_reader = EntryReader(args.target_pkg, args.runtime) if args.target_pkg else None
    target_entities = {x.upper().replace("0X", "") for x in args.target_entity}

    joined: list[dict] = []
    missing = 0
    for p in patterns:
        a = assignment_by_api.get(p["pattern_global_tag_id_hash"])
        row = dict(p)
        if a is None:
            row.update({
                "sandbox_assignment_found": False,
                "entity_relation_hash": None,
                "entity_relation_package_id": None,
                "entity_relation_file_index": None,
            })
            missing += 1
        else:
            row.update({
                "sandbox_assignment_found": True,
                "sandbox_assignment_index": a["assignment_index"],
                "entity_relation_hash": a["entity_relation_hash"],
                "entity_relation_package_id": a["entity_relation_package_id"],
                "entity_relation_file_index": a["entity_relation_file_index"],
            })
            if target_reader and (
                args.target_package_id is None
                or a["entity_relation_package_id"] == args.target_package_id
            ):
                row["target_relation_validation"] = validate_target_relation(
                    target_reader, a["entity_relation_hash"]
                )
        joined.append(row)

    matches = []
    for row in joined:
        hit = True
        if args.target_package_id is not None:
            hit = hit and row.get("entity_relation_package_id") == args.target_package_id
        if target_entities:
            hit = hit and row.get("entity_relation_hash") in target_entities
        if (args.target_package_id is not None or target_entities) and hit:
            matches.append(row)

    report = {
        "weapon_pattern_table": {
            "tag_hash": WEAPON_PATTERN_TABLE,
            "entry_index": pe["index"],
            "reference": pe["reference"].upper(),
            "size": pe["file_size"],
            "row_count": len(patterns),
        },
        "sandbox_pattern_assignments": {
            "tag_hash": SANDBOX_PATTERN_ASSIGNMENTS,
            "entry_index": se["index"],
            "reference": se["reference"].upper(),
            "size": se["file_size"],
            "row_count": len(assignments),
            "sorted_by_api_hash": True,
        },
        "join": {
            "joined_pattern_count": len(joined),
            "missing_assignment_count": missing,
            "resolved_assignment_count": len(joined) - missing,
        },
        "target_package_id": args.target_package_id,
        "target_entities": sorted(target_entities),
        "match_count": len(matches),
        "matches": matches,
        "patterns": joined,
    }

    text = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n")
        print(f"wrote {args.output}")
    else:
        print(text)

    print(
        json.dumps(
            {
                "weapon_pattern_rows": len(patterns),
                "sandbox_assignment_rows": len(assignments),
                "resolved": len(joined) - missing,
                "missing": missing,
                "match_count": len(matches),
            },
            indent=2,
        ),
        file=sys.stderr,
    )
    for m in matches:
        print(
            "PATTERN MATCH",
            m["weapon_pattern_index"],
            m["pattern_global_tag_id_hash"],
            m["entity_relation_hash"],
            m.get("target_relation_validation"),
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
