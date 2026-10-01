#!/usr/bin/env python3
"""Decode exact D1 GlobalChannelDefaults payloads without assigning channel semantics.

Source/lineage structure:
  +0x08 DynamicArray<SStringHash>  (stride 4)
  +0x18 DynamicArray<Vec4>         (stride 16)

For D1 this layout is treated as a hypothesis until the exact retail payload
passes independent DynamicArray bounds/count checks and both arrays agree in
length. The tool preserves raw indices, StringHashes and Vec4 defaults and
extracts caller-requested indices such as the raw RoI TFX 0x4B operand domain.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
from pathlib import Path


def u32(b: bytes, o: int) -> int:
    if o < 0 or o + 4 > len(b):
        raise ValueError(f"u32 OOB at 0x{o:X}/0x{len(b):X}")
    return struct.unpack_from("<I", b, o)[0]


def i64(b: bytes, o: int) -> int:
    if o < 0 or o + 8 > len(b):
        raise ValueError(f"i64 OOB at 0x{o:X}/0x{len(b):X}")
    return struct.unpack_from("<q", b, o)[0]


def dyn(b: bytes, field: int, stride: int, label: str) -> dict:
    if field < 0 or field + 0x10 > len(b):
        raise ValueError(f"{label} descriptor OOB at 0x{field:X}")
    count = u32(b, field)
    unknown04 = u32(b, field + 4)
    rel = i64(b, field + 8)
    data = field + rel + 0x18
    end = data + count * stride
    ok = count == 0 or (0 <= data <= end <= len(b))
    if not ok:
        raise ValueError(
            f"{label}: count={count} rel={rel} -> [0x{data:X},0x{end:X}) outside 0x{len(b):X}"
        )
    return {
        "field_offset": field,
        "field_offset_hex": f"0x{field:X}",
        "count": count,
        "unknown04": unknown04,
        "relative": rel,
        "data_offset": data,
        "data_offset_hex": f"0x{data:X}",
        "end_offset": end,
        "end_offset_hex": f"0x{end:X}",
        "stride": stride,
        "bounds_ok": True,
    }


def vec4(b: bytes, o: int) -> list[float]:
    v = list(struct.unpack_from("<4f", b, o))
    if not all(math.isfinite(x) for x in v):
        raise ValueError(f"non-finite Vec4 at 0x{o:X}: {v}")
    return v


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("payload", type=Path)
    ap.add_argument("--tag-hash")
    ap.add_argument("--index", action="append", default=[])
    ap.add_argument(
        "--require-requested-in-range",
        action="store_true",
        help="fail if any --index value is outside the exact retail channel table",
    )
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    b = a.payload.read_bytes()
    hashes = dyn(b, 0x08, 4, "ChannelHashes")
    values = dyn(b, 0x18, 16, "ChannelDefaults")
    if hashes["count"] != values["count"]:
        raise ValueError(
            f"parallel array count mismatch: hashes={hashes['count']} values={values['count']}"
        )
    count = hashes["count"]
    if count == 0:
        raise ValueError("GlobalChannelDefaults exact payload contains zero channels")

    rows = []
    for i in range(count):
        h = u32(b, hashes["data_offset"] + i * 4)
        v = vec4(b, values["data_offset"] + i * 16)
        rows.append({
            "index": i,
            "index_hex": f"0x{i:02X}",
            "string_hash": f"{h:08X}",
            "default_vec4": v,
        })

    requested = []
    for raw in a.index:
        idx = int(raw, 0)
        if idx < 0 or idx >= count:
            requested.append({
                "index": idx,
                "index_hex": f"0x{idx:X}",
                "in_range": False,
            })
        else:
            requested.append({"in_range": True, **rows[idx]})

    if a.require_requested_in_range:
        missing = [row for row in requested if not row["in_range"]]
        if missing:
            raise ValueError(
                "requested channel indices outside exact retail table: "
                + ", ".join(row["index_hex"] for row in missing)
            )

    out = {
        "schema": "d1_global_channel_defaults_exact/v1",
        "status": "EXACT_RETAIL_PARALLEL_ARRAYS_CLOSED",
        "tag_hash": a.tag_hash,
        "payload_file": a.payload.name,
        "payload_size": len(b),
        "payload_sha256": hashlib.sha256(b).hexdigest(),
        "layout": {
            "channel_hashes": hashes,
            "channel_defaults": values,
            "parallel_counts_equal": True,
            "channel_count": count,
        },
        "requested_indices": requested,
        "requested_indices_all_in_range": all(row["in_range"] for row in requested),
        "channels": rows,
        "proof_boundary": (
            "Exact D1 retail bytes independently validate two parallel DynamicArray "
            "descriptors at +0x08 and +0x18 with strides 4 and 16 and equal counts. "
            "Rows are promoted only as ordered (StringHash, default Vec4) pairs. "
            "Human-facing channel names and the claim that RoI TFX 0x4B reads this "
            "table remain separate until joined by exact runtime/index dataflow."
        ),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({
        "status": out["status"],
        "tag_hash": a.tag_hash,
        "channel_count": count,
        "requested_indices": requested,
        "payload_sha256": out["payload_sha256"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
