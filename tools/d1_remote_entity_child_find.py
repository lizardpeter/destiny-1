#!/usr/bin/env python3
"""Sparse-scan one D1 package family for EntityChildren resources.

This is a proof-oriented remote scanner for final-era Destiny 1 PS4 Tiger packages.
It reads the logical package entry/block tables plus only blocks needed by
EntityResource entries (class/reference 0x80800861).  For ROI EntityChildren the
source-pinned Charm layout is:

  EntityResource.Unk10 -> class 0x80802663 (D1 schema 63268080)
  EntityResource.Unk18 -> class 0x80802708 (D1 schema 08278080)
  parent + 0x100       -> DynamicArray<S712B8080>, stride 0xA0
  S712B8080 + 0x20     -> child Entity FileHash
  S712B8080 + 0x88     -> DynamicArray<S93278080>, stride 0x40
  S93278080 + 0x10     -> Rotation Vector4
  S93278080 + 0x20     -> Translation Vector4

The child/transform offsets are pinned to MontagueM/Charm commit
50d36ee1f9ecadad7522504c20b1f3f9c97e30af, Tiger/Schema/Entity/EntityStructs.cs,
and the consumption path is pinned to Entity.GetEntityChildren() in Entity.cs.
No child socket/bone semantic is inferred from these transforms.

No proprietary Oodle binary is stored by this tool; the caller supplies a
runtime directory, as with the other package probes in this repository.
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

from d1_investment_arrangement_probe import dyn_header, filehash_pkg_index
from d1_remote_investment_parent_probe import RemoteLogicalPackage, parse_member
from d1_split_tar_extract import SplitHttpTar

ENTITY_RESOURCE_REF = "80800861"
D1_ENTITY_CHILDREN_DISCRIMINATOR = 0x80802663
D1_ENTITY_CHILDREN_PARENT = 0x80802708
D1_CHILD_ENTRY_SIZE = 0xA0
D1_CHILD_ENTITY_OFFSET = 0x20
D1_CHILD_TRANSFORMS_OFFSET = 0x88
D1_CHILD_TRANSFORM_SIZE = 0x40
D1_CHILD_TRANSFORM_ROTATION_OFFSET = 0x10
D1_CHILD_TRANSFORM_TRANSLATION_OFFSET = 0x20
PINNED_CHARM = (
    "MontagueM/Charm@50d36ee1f9ecadad7522504c20b1f3f9c97e30af "
    "Tiger/Schema/Entity/EntityStructs.cs + Tiger/Schema/Entity/Entity.cs"
)


def u32(b: bytes, o: int) -> int:
    if o < 0 or o + 4 > len(b):
        raise ValueError(f"u32 out of bounds at 0x{o:X}/0x{len(b):X}")
    return struct.unpack_from("<I", b, o)[0]


def i64(b: bytes, o: int) -> int:
    if o < 0 or o + 8 > len(b):
        raise ValueError(f"i64 out of bounds at 0x{o:X}/0x{len(b):X}")
    return struct.unpack_from("<q", b, o)[0]


def f4(b: bytes, o: int) -> list[float]:
    if o < 0 or o + 16 > len(b):
        raise ValueError(f"Vector4 out of bounds at 0x{o:X}/0x{len(b):X}")
    return list(struct.unpack_from("<4f", b, o))


def resource_ptr(b: bytes, field_off: int) -> tuple[int | None, int | None]:
    rel = i64(b, field_off)
    if rel == 0:
        return None, None
    target = field_off + rel
    if target < 4 or target > len(b):
        raise ValueError(f"resource pointer +0x{field_off:X} -> 0x{target:X} outside entry")
    cls = u32(b, target - 4)
    return target, cls


def parse_child_transforms(b: bytes, child_entry_off: int) -> dict:
    field = child_entry_off + D1_CHILD_TRANSFORMS_OFFSET
    count, data = dyn_header(b, field)
    rows = []
    for i in range(count):
        o = data + i * D1_CHILD_TRANSFORM_SIZE
        if o < 0 or o + D1_CHILD_TRANSFORM_SIZE > len(b):
            raise ValueError(
                f"child transform {i}/{count} at 0x{o:X} exceeds resource size 0x{len(b):X}"
            )
        rows.append({
            "index": i,
            "entry_offset": o,
            "rotation": f4(b, o + D1_CHILD_TRANSFORM_ROTATION_OFFSET),
            "translation": f4(b, o + D1_CHILD_TRANSFORM_TRANSLATION_OFFSET),
        })
    return {
        "array_field": field,
        "count": count,
        "data_offset": data,
        "stride": D1_CHILD_TRANSFORM_SIZE,
        "items": rows,
    }


def parse_children_resource(b: bytes) -> dict | None:
    if len(b) < 0x20:
        return None
    t10, c10 = resource_ptr(b, 0x10)
    if c10 != D1_ENTITY_CHILDREN_DISCRIMINATOR:
        return None
    t18, c18 = resource_ptr(b, 0x18)
    if c18 != D1_ENTITY_CHILDREN_PARENT or t18 is None:
        raise ValueError(
            f"EntityChildren discriminator has unexpected parent class {c18!r}"
        )
    field = t18 + 0x100
    count, data = dyn_header(b, field)
    children = []
    for i in range(count):
        o = data + i * D1_CHILD_ENTRY_SIZE
        if o + D1_CHILD_ENTITY_OFFSET + 4 > len(b):
            raise ValueError(
                f"child {i}/{count} at 0x{o:X} exceeds resource size 0x{len(b):X}"
            )
        entity = u32(b, o + D1_CHILD_ENTITY_OFFSET)
        transforms = parse_child_transforms(b, o)
        children.append({
            "index": i,
            "entry_offset": o,
            "entity_hash": f"{entity:08X}",
            "package_id": filehash_pkg_index(entity)[0] if entity not in (0, 0xFFFFFFFF) else None,
            "file_index": filehash_pkg_index(entity)[1] if entity not in (0, 0xFFFFFFFF) else None,
            "transform_count": transforms["count"],
            "transforms": transforms["items"],
            "transforms_array": {k: v for k, v in transforms.items() if k != "items"},
        })
    return {
        "discriminator_class": f"{c10:08X}",
        "parent_class": f"{c18:08X}",
        "parent_offset": t18,
        "children_array_field": field,
        "child_count": count,
        "children": children,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--package-id", type=lambda x: int(x, 0), required=True)
    ap.add_argument("--find-child", action="append", default=[])
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
    wanted = {x.upper().removeprefix("0X") for x in a.find_child}

    candidates = [
        e for e in r.entries
        if e["type"] == 16 and e["subtype"] == 0 and e["reference"].upper() == ENTITY_RESOURCE_REF
    ]
    child_resources = []
    hits = []
    errors = []
    child_pkg_counts = collections.Counter()
    transform_count_histogram = collections.Counter()

    for n, e in enumerate(candidates, 1):
        try:
            b = r.entry(e["index"])
            parsed = parse_children_resource(b)
            if parsed is None:
                continue
            row = {
                "resource_tag": e["tag_hash"].upper(),
                "entry_index": e["index"],
                "size": e["file_size"],
                **parsed,
            }
            child_resources.append(row)
            for ch in parsed["children"]:
                transform_count_histogram[ch["transform_count"]] += 1
                if ch["package_id"] is not None:
                    child_pkg_counts[ch["package_id"]] += 1
                if ch["entity_hash"] in wanted:
                    hit = {
                        "resource_tag": row["resource_tag"],
                        "resource_entry_index": row["entry_index"],
                        **ch,
                    }
                    hits.append(hit)
                    print("TARGET CHILD", hit, flush=True)
        except Exception as ex:
            errors.append({
                "resource_tag": e["tag_hash"].upper(),
                "entry_index": e["index"],
                "error": repr(ex),
            })
        if n % 500 == 0:
            print(
                f"{a.package_id:04X}: {n}/{len(candidates)} EntityResources; "
                f"child resources={len(child_resources)} blocks={len(r.block_cache)}",
                flush=True,
            )

    rep = {
        "schema_version": 2,
        "status": "D1_ENTITY_CHILDREN_TRANSFORMS_CENSUS",
        "pinned_source": PINNED_CHARM,
        "package_id": a.package_id,
        "logical_view": r.view.name,
        "entry_count": len(r.entries),
        "entity_resource_candidates": len(candidates),
        "entity_children_resource_count": len(child_resources),
        "remote_blocks_read": len(r.block_cache),
        "wanted_children": sorted(wanted),
        "hits": hits,
        "child_package_counts": {f"{k:04X}": v for k, v in sorted(child_pkg_counts.items())},
        "child_transform_count_histogram": {str(k): v for k, v in sorted(transform_count_histogram.items())},
        "child_resources": child_resources,
        "error_count": len(errors),
        "errors": errors[:200],
        "policy": (
            "Child Entity FileHashes and transforms are decoded only from Charm's exact D1 ROI EntityChildren layout. "
            "The transform array is preserved literally; no hand/socket/bone semantic is assigned by this tool."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(rep, indent=2) + "\n")
    print(json.dumps({k: v for k, v in rep.items() if k not in ("child_resources", "errors")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
