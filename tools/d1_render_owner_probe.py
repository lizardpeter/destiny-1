#!/usr/bin/env python3
"""Probe D1 ROI entity-model parent resources and their render context.

For every resident outer EntityResource (class 0x80800861), this tool finds
standard D1 model-parent resources:

    Unk10 ResourcePointer -> class 0x80801A80 (model discriminator)
    Unk18 ResourcePointer -> class 0x80801A9C (model parent)

It then records the embedded model FileHash, TexturePlatesROI,
ExternalMaterialsMap, and ExternalMaterials. This is intended for resolving
VariantShaderIndex-based D1 mesh parts without guessing material/texture
bindings.
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

ENTITY_RESOURCE_CLASS = "80800861"
D1_MODEL_DISCRIMINATOR = 0x80801A80
D1_MODEL_PARENT = 0x80801A9C

MODEL_OFF = 0x15C
TEXTURE_PLATES_ARRAY_OFF = 0x1A8
EXTERNAL_MAP_ARRAY_OFF = 0x230
EXTERNAL_MATERIALS_ARRAY_OFF = 0x270
TEXTURE_PLATE_ENTRY_SIZE = 0x30
TEXTURE_PLATE_TAG_OFF = 0x28
EXTERNAL_MAP_ENTRY_SIZE = 0x0C


def u32(b: bytes, o: int) -> int:
    return struct.unpack_from("<I", b, o)[0]


def i32(b: bytes, o: int) -> int:
    return struct.unpack_from("<i", b, o)[0]


def q64(b: bytes, o: int) -> int:
    return struct.unpack_from("<q", b, o)[0]


def resource_ptr(b: bytes, o: int) -> dict:
    if o + 8 > len(b):
        return {"field_offset": o, "error": "field out of bounds"}
    rel = q64(b, o)
    if rel == 0:
        return {"field_offset": o, "relative": 0, "null": True}
    target = o + rel
    d = {
        "field_offset": o,
        "relative": rel,
        "target_offset": target,
        "null": False,
    }
    if target < 4 or target > len(b):
        d["error"] = "target out of bounds"
        return d
    d["class_hash"] = f"{u32(b, target - 4):08X}"
    return d


def dynamic_array(b: bytes, field: int, elem_size: int) -> dict:
    """Decode Charm-style D1 DynamicArray<T>.

    D1 layout used by the entity-model parent:
      +0x00 u32 count
      +0x08 signed relative qword

    The RelativePointer field is based at field+8 and Charm applies the
    DynamicArray extra offset 0x10, so:
      data = (field + 8) + rel + 0x10
    """
    if field + 16 > len(b):
        return {"field_offset": field, "error": "array header out of bounds"}
    count = u32(b, field)
    rel = q64(b, field + 8)
    data = (field + 8) + rel + 0x10
    d = {
        "field_offset": field,
        "count": count,
        "relative": rel,
        "data_offset": data,
        "element_size": elem_size,
    }
    if count and (data < 0 or data + count * elem_size > len(b)):
        d["error"] = "array data out of bounds"
    return d


def parse_parent_resource(b: bytes) -> dict | None:
    p10 = resource_ptr(b, 0x10)
    p18 = resource_ptr(b, 0x18)
    if p10.get("class_hash") != f"{D1_MODEL_DISCRIMINATOR:08X}":
        return None
    if p18.get("class_hash") != f"{D1_MODEL_PARENT:08X}":
        return None
    base = p18.get("target_offset")
    if not isinstance(base, int) or base + MODEL_OFF + 4 > len(b):
        return {"error": "model parent payload out of bounds", "unk10": p10, "unk18": p18}

    out = {
        "unk10": p10,
        "unk18": p18,
        "parent_offset": base,
        "embedded_model_tag_hash": f"{u32(b, base + MODEL_OFF):08X}",
    }

    plate = dynamic_array(b, base + TEXTURE_PLATES_ARRAY_OFF, TEXTURE_PLATE_ENTRY_SIZE)
    out["texture_plates_roi"] = plate
    plate_rows = []
    if not plate.get("error"):
        for i in range(plate["count"]):
            o = plate["data_offset"] + i * TEXTURE_PLATE_ENTRY_SIZE
            plate_rows.append({
                "index": i,
                "entry_offset": o,
                "texture_plate_header_tag_hash": f"{u32(b, o + TEXTURE_PLATE_TAG_OFF):08X}",
            })
    out["texture_plates_roi_entries"] = plate_rows

    extmap = dynamic_array(b, base + EXTERNAL_MAP_ARRAY_OFF, EXTERNAL_MAP_ENTRY_SIZE)
    out["external_materials_map"] = extmap
    map_rows = []
    if not extmap.get("error"):
        for i in range(extmap["count"]):
            o = extmap["data_offset"] + i * EXTERNAL_MAP_ENTRY_SIZE
            map_rows.append({
                "variant_shader_index": i,
                "material_count": i32(b, o),
                "material_start_index": i32(b, o + 4),
                "unk08": i32(b, o + 8),
            })
    out["external_materials_map_entries"] = map_rows

    mats = dynamic_array(b, base + EXTERNAL_MATERIALS_ARRAY_OFF, 4)
    out["external_materials"] = mats
    mat_rows = []
    if not mats.get("error"):
        for i in range(mats["count"]):
            o = mats["data_offset"] + i * 4
            mat_rows.append(f"{u32(b, o):08X}")
    out["external_material_tag_hashes"] = mat_rows

    # Record the exact current Charm-style variant-0 selection for convenience,
    # while keeping the complete banks above so no information is discarded.
    selected = []
    for row in map_rows:
        c = row["material_count"]
        s = row["material_start_index"]
        material = None
        if c > 0 and 0 <= s < len(mat_rows):
            material = mat_rows[s]
        selected.append({
            "variant_shader_index": row["variant_shader_index"],
            "first_material_tag_hash": material,
        })
    out["first_material_per_variant"] = selected
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pkg", type=Path)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--model-tag", help="optional embedded model TagHash filter")
    ap.add_argument("-o", "--output", type=Path)
    args = ap.parse_args()

    target = args.model_tag.upper().removeprefix("0X") if args.model_tag else None
    r = EntryReader(args.pkg, args.runtime)
    rows = []

    for e in r.entries:
        if e["type"] != 16 or e["subtype"] != 0 or e["reference"].upper() != ENTITY_RESOURCE_CLASS:
            continue
        row = {
            "entry_index": e["index"],
            "tag_hash": e["tag_hash"],
            "size": e["file_size"],
            "available": r.available(e["index"]),
        }
        if not row["available"]:
            continue
        try:
            parsed = parse_parent_resource(r.entry(e["index"]))
        except Exception as ex:
            row["error"] = repr(ex)
            rows.append(row)
            continue
        if parsed is None:
            continue
        row.update(parsed)
        if target and row.get("embedded_model_tag_hash") != target:
            continue
        rows.append(row)

    report = {
        "package": str(r.pkg),
        "platform": r.h["platform"],
        "target_model_tag_hash": target,
        "model_parent_count": len(rows),
        "model_parents": rows,
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
