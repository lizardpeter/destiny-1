#!/usr/bin/env python3
"""Decode the D1 ROI retail InventoryItemHash -> inventory-definition FileHash map.

The source table is retail investment tag 80A5FFBE.  Each 0x18-byte row contains
at least the public/API InventoryItemHash at +0x00 and the FileHash of the D1
inventory item definition at +0x10.

This promotes the byte-proven decoder that previously lived only inside a
one-off workflow into a reusable bulk-ripping primitive.
"""
from __future__ import annotations

import argparse
import collections
import json
import struct
from pathlib import Path

from d1_entry_extract import EntryReader
from d1_investment_arrangement_probe import dyn_header, filehash_pkg_index

INVENTORY_ITEM_MAP = "80A5FFBE"
ROW_STRIDE = 0x18


def decode_inventory_item_map(reader: EntryReader) -> dict:
    by = {e["tag_hash"].upper(): e for e in reader.entries}
    e = by.get(INVENTORY_ITEM_MAP)
    if e is None:
        raise KeyError(f"{INVENTORY_ITEM_MAP} not present in {reader.pkg}")
    if not reader.available(e["index"]):
        raise RuntimeError(f"{INVENTORY_ITEM_MAP} is not resident in supplied logical view")
    b = reader.entry(e["index"])
    count, data = dyn_header(b, 0x08)
    if data + count * ROW_STRIDE > len(b):
        raise ValueError("inventory item map rows exceed payload")

    rows = []
    package_counts = collections.Counter()
    seen_inventory = set()
    for i in range(count):
        o = data + i * ROW_STRIDE
        inventory_hash = struct.unpack_from("<I", b, o + 0x00)[0]
        item_file_hash = struct.unpack_from("<I", b, o + 0x10)[0]
        pkg, idx = filehash_pkg_index(item_file_hash)
        if inventory_hash in seen_inventory:
            raise ValueError(f"duplicate InventoryItemHash {inventory_hash:08X}")
        seen_inventory.add(inventory_hash)
        package_counts[pkg] += 1
        rows.append({
            "map_index": i,
            "inventory_item_hash": f"{inventory_hash:08X}",
            "item_file_hash": f"{item_file_hash:08X}",
            "item_package_id": pkg,
            "item_file_index": idx,
        })

    return {
        "tag_hash": INVENTORY_ITEM_MAP,
        "entry_index": e["index"],
        "reference": e["reference"].upper(),
        "entry_size": len(b),
        "row_stride": ROW_STRIDE,
        "row_count": count,
        "package_counts": {f"{k:04X}": v for k, v in sorted(package_counts.items())},
        "rows": rows,
        "evidence_policy": "InventoryItemHash and definition FileHash are read directly from 80A5FFBE retail rows; no item-name/type inference is performed.",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pkg", type=Path, help="logical investment_globals_012f view containing 80A5FFBE")
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path)
    args = ap.parse_args()

    out = decode_inventory_item_map(EntryReader(args.pkg, args.runtime))
    text = json.dumps(out, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n")
        print(f"wrote {args.output}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
