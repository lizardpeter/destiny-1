#!/usr/bin/env python3
"""Decode Destiny 1 ROI Investment art-arrangement -> entity assignment chains.

This follows the D1 structures independently confirmed in Charm:

  80A5FFA7 (D7348080)
    ArtArrangementEntityAssignments[] (33348080, 0x18)
      single assignment hashes OR MultipleEntityAssignments[] (635D8080)
        -> C1338080 resource -> EntityAssignments[] (A3338080)

  80A7E1DD (AA3A8080)
    EntityArrangementMap[] (A93A8080, 0x08)
      assignment hash -> EntityParent FileHash

  EntityParent (D1 A36F-like non-8080 struct, 0x18)
    +0x10 EntityDataROI FileHash

The final EntityDataROI may be an s_entity (reference 80800734).  This tool
keeps arrangement/assignment/parent/entity hashes separate and does not infer
render semantics.
"""
from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from d1_entry_extract import EntryReader

ENTITY_ASSIGNMENT_TAG = "80A5FFA7"
ENTITY_ASSIGNMENTS_MAP = "80A7E1DD"


def u32(b: bytes, o: int) -> int:
    if o < 0 or o + 4 > len(b):
        raise ValueError(f"u32 out of bounds at 0x{o:X} / 0x{len(b):X}")
    return struct.unpack_from("<I", b, o)[0]


def i64(b: bytes, o: int) -> int:
    if o < 0 or o + 8 > len(b):
        raise ValueError(f"i64 out of bounds at 0x{o:X} / 0x{len(b):X}")
    return struct.unpack_from("<q", b, o)[0]


def h32(v: int) -> str:
    return f"{v & 0xFFFFFFFF:08X}"


def filehash_pkg_index(v: int) -> tuple[int, int]:
    pkg = ((v >> 13) & 0x3FF) + ((((v >> 23) & 3) - 1) * 0x400)
    return pkg, v & 0x1FFF


def dyn_header(b: bytes, field_off: int) -> tuple[int, int]:
    """Return (count,data_offset) for the D1 DynamicArray serialization.

    Charm's RelativePointer base is the address of the int64 itself.  DynamicArray
    adds 0x10 to that pointer, therefore:
      data = (field_off + 8) + rel64 + 0x10
           = field_off + rel64 + 0x18
    """
    count = u32(b, field_off)
    rel = i64(b, field_off + 8)
    data = field_off + rel + 0x18
    if count and (data < 0 or data >= len(b)):
        raise ValueError(
            f"dynamic array at 0x{field_off:X}: count={count} points outside entry to 0x{data:X}"
        )
    return count, data


def resource_in_table_target(b: bytes, pointer_off: int) -> int:
    """Resolve D1 ResourceInTablePointer: target = pointer field address + rel64."""
    rel = i64(b, pointer_off)
    target = pointer_off + rel
    if target < 0 or target >= len(b):
        raise ValueError(
            f"resource-in-table pointer at 0x{pointer_off:X} points outside entry to 0x{target:X}"
        )
    return target


def entry_payload(reader: EntryReader, tag: str) -> tuple[dict, bytes]:
    by = {e["tag_hash"].upper(): e for e in reader.entries}
    e = by.get(tag.upper())
    if e is None:
        raise KeyError(f"tag {tag} not present in {reader.pkg}")
    if not reader.available(e["index"]):
        raise RuntimeError(f"tag {tag} entry {e['index']} is not resident with supplied package siblings")
    return e, reader.entry(e["index"])


def parse_assignment_map(b: bytes) -> dict[int, int]:
    # D1 AA3A8080: long FileSize; DynamicArrayUnloaded<A93A8080> at +0x08.
    count, data = dyn_header(b, 0x08)
    out: dict[int, int] = {}
    for i in range(count):
        o = data + i * 8
        assignment = u32(b, o)
        parent = u32(b, o + 4)
        if assignment in out and out[assignment] != parent:
            raise ValueError(f"assignment {h32(assignment)} maps to multiple parents")
        out[assignment] = parent
    return out


def parse_arrangements(b: bytes, assignment_map: dict[int, int]) -> list[dict]:
    # D1 D7348080: long FileSize; DynamicArrayUnloaded<33348080> at +0x08.
    count, data = dyn_header(b, 0x08)
    rows: list[dict] = []
    for idx in range(count):
        o = data + idx * 0x18
        if o + 0x18 > len(b):
            raise ValueError(f"arrangement {idx} exceeds entry at 0x{o:X}")
        masculine = u32(b, o)
        feminine = u32(b, o + 4)
        multi_count, multi_data = dyn_header(b, o + 8)
        assignments: list[int] = []
        source = "single"
        if multi_count == 0:
            # Match Charm: both valid single hashes are accepted.
            for v in (feminine, masculine):
                if v not in (0, 0xFFFFFFFF) and v not in assignments:
                    assignments.append(v)
        else:
            source = "multiple"
            for mi in range(multi_count):
                ptr_off = multi_data + mi * 8
                resource = resource_in_table_target(b, ptr_off)
                # D1 C1338080: int64 Unk00; DynamicArray<A3338080> at +0x08.
                acount, adata = dyn_header(b, resource + 8)
                for ai in range(acount):
                    v = u32(b, adata + ai * 4)
                    if v not in (0, 0xFFFFFFFF) and v not in assignments:
                        assignments.append(v)
        parents = [assignment_map.get(v) for v in assignments]
        rows.append({
            "arrangement_index": idx,
            "source": source,
            "masculine_single_assignment": h32(masculine),
            "feminine_single_assignment": h32(feminine),
            "multiple_resource_count": multi_count,
            "assignment_hashes": [h32(v) for v in assignments],
            "entity_parent_hashes": [h32(v) if v is not None else None for v in parents],
            "unresolved_assignment_hashes": [h32(a) for a, p in zip(assignments, parents) if p is None],
        })
    return rows


def choose_views(asset_dir: Path, runtime: Path) -> dict[int, EntryReader]:
    """Open the highest numbered recovered physical snapshot for each package id."""
    candidates: dict[int, tuple[int, Path]] = {}
    for p in asset_dir.glob("*.pkg"):
        m = re.search(r"_([0-9]+)\.pkg$", p.name)
        if not m:
            continue
        patch = int(m.group(1))
        try:
            r = EntryReader(p, runtime)
        except Exception:
            continue
        pkg_id = int(r.h["pkg_id"])
        prev = candidates.get(pkg_id)
        if prev is None or patch > prev[0]:
            candidates[pkg_id] = (patch, p)
    return {pkg_id: EntryReader(p, runtime) for pkg_id, (_, p) in candidates.items()}


def resolve_parents(rows: list[dict], asset_dir: Path, runtime: Path) -> dict[str, dict]:
    views = choose_views(asset_dir, runtime)
    cache: dict[str, dict] = {}
    parent_hashes = {
        p for row in rows for p in row["entity_parent_hashes"] if p is not None
    }
    for ph in sorted(parent_hashes):
        pv = int(ph, 16)
        pkg_id, index = filehash_pkg_index(pv)
        rec = {
            "parent_hash": ph,
            "package_id": pkg_id,
            "file_index": index,
            "resolved": False,
        }
        r = views.get(pkg_id)
        if r is None:
            rec["reason"] = "package family not recovered"
            cache[ph] = rec
            continue
        by = {e["tag_hash"].upper(): e for e in r.entries}
        e = by.get(ph)
        if e is None:
            rec["reason"] = "parent tag absent from selected logical snapshot"
            cache[ph] = rec
            continue
        rec.update({
            "entry_index": e["index"],
            "reference": e["reference"].upper(),
            "size": e["file_size"],
            "available": r.available(e["index"]),
        })
        if not r.available(e["index"]):
            rec["reason"] = "parent entry block not resident"
            cache[ph] = rec
            continue
        b = r.entry(e["index"])
        if len(b) < 0x14:
            rec["reason"] = "parent payload shorter than D1 EntityDataROI field"
            cache[ph] = rec
            continue
        entity_data = u32(b, 0x10)
        epkg, eidx = filehash_pkg_index(entity_data) if entity_data not in (0, 0xFFFFFFFF) else (-1, -1)
        rec.update({
            "resolved": True,
            "entity_data_hash": h32(entity_data),
            "entity_data_package_id": epkg,
            "entity_data_file_index": eidx,
        })
        cache[ph] = rec
    return cache


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("assignment_pkg", type=Path, help="012f logical view containing 80A5FFA7")
    ap.add_argument("assignment_map_pkg", type=Path, help="013f logical view containing 80A7E1DD")
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--asset-dir", type=Path, help="directory of recovered investment_assets package siblings")
    ap.add_argument("--find-entity", action="append", default=[], help="final EntityDataROI hash to reverse-find; repeatable")
    ap.add_argument("-o", "--output", type=Path)
    args = ap.parse_args()

    ar = EntryReader(args.assignment_pkg, args.runtime)
    mr = EntryReader(args.assignment_map_pkg, args.runtime)
    ae, ab = entry_payload(ar, ENTITY_ASSIGNMENT_TAG)
    me, mb = entry_payload(mr, ENTITY_ASSIGNMENTS_MAP)
    amap = parse_assignment_map(mb)
    arrangements = parse_arrangements(ab, amap)

    parent_resolution = {}
    if args.asset_dir:
        parent_resolution = resolve_parents(arrangements, args.asset_dir, args.runtime)
        for row in arrangements:
            row["entities"] = [
                parent_resolution.get(p) if p else None for p in row["entity_parent_hashes"]
            ]

    wanted = {x.upper().replace("0X", "") for x in args.find_entity}
    matches = []
    if wanted and parent_resolution:
        for row in arrangements:
            finals = {
                x.get("entity_data_hash") for x in row.get("entities", [])
                if isinstance(x, dict) and x.get("resolved")
            }
            hit = sorted(wanted & finals)
            if hit:
                matches.append({
                    "arrangement_index": row["arrangement_index"],
                    "matched_entities": hit,
                    "assignment_hashes": row["assignment_hashes"],
                    "entity_parent_hashes": row["entity_parent_hashes"],
                    "final_entity_hashes": sorted(finals),
                })

    report = {
        "assignment_tag": {
            "tag_hash": ENTITY_ASSIGNMENT_TAG,
            "entry_index": ae["index"],
            "reference": ae["reference"],
            "size": ae["file_size"],
        },
        "assignment_map": {
            "tag_hash": ENTITY_ASSIGNMENTS_MAP,
            "entry_index": me["index"],
            "reference": me["reference"],
            "size": me["file_size"],
            "mapping_count": len(amap),
        },
        "arrangement_count": len(arrangements),
        "arrangements": arrangements,
        "parent_resolution": parent_resolution,
        "find_entity": sorted(wanted),
        "matches": matches,
    }
    text = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n")
        print(f"wrote {args.output}")
    else:
        print(text)
    if wanted:
        print(f"reverse matches: {len(matches)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
