#!/usr/bin/env python3
"""Probe Destiny 1 Rise of Iron entity texture-plate resources.

D1 model parents expose TexturePlatesROI entries whose +0x28 field points to a
0x80801C3C texture-plate header (Charm schema 3C1C8080).  That header contains
three TexturePlate FileHashes at +0x24/+0x28/+0x2C: albedo, normal and gstack.
Each TexturePlate is class 0x80800147 (Charm schema 47018080) and contains a
DynamicArray of 0x14-byte placement records:

    +0x00 FileHash texture
    +0x04 i32 translation_x
    +0x08 i32 translation_y
    +0x0C i32 scale_x
    +0x10 i32 scale_y

This tool records exact plate composition provenance without rendering guesses.
"""
from __future__ import annotations

import argparse
import json
import math
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from d1_entry_extract import EntryReader

HEADER_CLASS = "80801C3C"
PLATE_CLASS = "80800147"
TRANSFORM_SIZE = 0x14


def u32(b: bytes, o: int) -> int:
    return struct.unpack_from("<I", b, o)[0]


def i32(b: bytes, o: int) -> int:
    return struct.unpack_from("<i", b, o)[0]


def q64(b: bytes, o: int) -> int:
    return struct.unpack_from("<q", b, o)[0]


def dynamic_array(b: bytes, field: int, elem_size: int) -> dict:
    if field + 16 > len(b):
        return {"field_offset": field, "error": "array header out of bounds"}
    count = u32(b, field)
    rel = q64(b, field + 8)
    data = (field + 8) + rel + 0x10
    out = {
        "field_offset": field,
        "count": count,
        "relative": rel,
        "data_offset": data,
        "element_size": elem_size,
    }
    if count and (data < 0 or data + count * elem_size > len(b)):
        out["error"] = "array data out of bounds"
    return out


def filehash_package_id(tag_hash: str) -> int | None:
    h = int(tag_hash, 16)
    high = (h >> 23) & 3
    if high == 0:
        return None
    return ((h >> 13) & 0x3FF) + ((high - 1) * 0x400)


def filehash_entry_index(tag_hash: str) -> int:
    return int(tag_hash, 16) & 0x1FFF


def ceil_pow2(v: int) -> int:
    if v <= 0:
        return 0
    return 1 << (v - 1).bit_length()


def parse_plate(reader: EntryReader, by_hash: dict[str, dict], tag_hash: str) -> dict:
    tag_hash = tag_hash.upper()
    row = {
        "tag_hash": tag_hash,
        "filehash_package_id": filehash_package_id(tag_hash),
        "filehash_entry_index": filehash_entry_index(tag_hash),
    }
    e = by_hash.get(tag_hash)
    if e is None:
        row["present_in_package"] = False
        return row
    row.update({
        "present_in_package": True,
        "entry_index": e["index"],
        "entry_type": e["type"],
        "entry_subtype": e["subtype"],
        "class_hash": e["reference"].upper(),
        "declared_file_size": e["file_size"],
        "available": reader.available(e["index"]),
    })
    if not row["available"]:
        return row
    b = reader.entry(e["index"])
    row["actual_file_size"] = len(b)
    if e["reference"].upper() != PLATE_CLASS:
        row["warning"] = f"expected texture plate class {PLATE_CLASS}"
    arr = dynamic_array(b, 0x10, TRANSFORM_SIZE)
    row["plate_transforms"] = arr
    transforms = []
    max_dim = 0
    if not arr.get("error"):
        for i in range(arr["count"]):
            o = arr["data_offset"] + i * TRANSFORM_SIZE
            texture = f"{u32(b, o):08X}"
            tx, ty = i32(b, o + 4), i32(b, o + 8)
            sx, sy = i32(b, o + 0xC), i32(b, o + 0x10)
            max_dim = max(max_dim, tx + sx, ty + sy)
            transforms.append({
                "index": i,
                "offset": o,
                "texture": texture,
                "texture_filehash_package_id": filehash_package_id(texture),
                "texture_filehash_entry_index": filehash_entry_index(texture),
                "translation": [tx, ty],
                "scale": [sx, sy],
            })
    row["transforms"] = transforms
    row["plate_dimension_source_max"] = max_dim
    row["plate_dimension_pow2"] = ceil_pow2(max_dim)
    return row


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pkg", type=Path)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--header-tag", required=True, help="D1 texture-plate header FileHash")
    ap.add_argument("-o", "--output", type=Path)
    args = ap.parse_args()

    r = EntryReader(args.pkg, args.runtime)
    if r.h["platform"] != "PS4":
        raise ValueError("texture plate probe currently targets D1 ROI PS4")
    by_hash = {e["tag_hash"].upper(): e for e in r.entries}
    h = args.header_tag.upper().removeprefix("0X").zfill(8)
    he = by_hash.get(h)
    if he is None:
        raise KeyError(f"texture-plate header {h} not present in package")
    if not r.available(he["index"]):
        raise RuntimeError(f"texture-plate header {h} is unavailable")
    hb = r.entry(he["index"])
    if len(hb) < 0x30:
        raise ValueError(f"short texture-plate header {h}: {len(hb)} bytes")

    header = {
        "tag_hash": h,
        "entry_index": he["index"],
        "class_hash": he["reference"].upper(),
        "declared_file_size": he["file_size"],
        "actual_file_size": len(hb),
        "file_size_field": struct.unpack_from("<Q", hb, 0)[0],
        "albedo_plate": f"{u32(hb, 0x24):08X}",
        "normal_plate": f"{u32(hb, 0x28):08X}",
        "gstack_plate": f"{u32(hb, 0x2C):08X}",
    }
    if he["reference"].upper() != HEADER_CLASS:
        header["warning"] = f"expected texture-plate header class {HEADER_CLASS}"

    plates = {
        "albedo": parse_plate(r, by_hash, header["albedo_plate"]),
        "normal": parse_plate(r, by_hash, header["normal_plate"]),
        "gstack": parse_plate(r, by_hash, header["gstack_plate"]),
    }
    texture_hashes = []
    for plate in plates.values():
        for t in plate.get("transforms", []):
            if t["texture"] not in texture_hashes:
                texture_hashes.append(t["texture"])

    report = {
        "package": str(r.pkg),
        "platform": r.h["platform"],
        "package_id": r.h.get("pkg_id"),
        "header": header,
        "plates": plates,
        "source_texture_hashes": texture_hashes,
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
