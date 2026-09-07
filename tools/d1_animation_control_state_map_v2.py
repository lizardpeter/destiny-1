#!/usr/bin/env python3
"""Decode D1 ROI 80802C0E selector tables including the retail null-tail form.

This is a source-narrow extension of ``d1_animation_control_state_map``. Ordinary
ranges and the already-proven 0x0000FFFF empty sentinel retain their previous
semantics. A second retail form is accepted only when all of these conditions hold:

* packed count == 2;
* start is the final declared animation-list index;
* the requested range ends exactly one item past the declared list; and
* the serialized u32 immediately after the declared FileHash list is zero.

That form is emitted as ``range_with_implicit_null_tail``. The final in-bank clip
remains selected and the null tail is represented separately. Zero is never promoted
to an animation FileHash. Every other out-of-range selector remains fatal.

The rule was established by the Wrath retail census: 2,297 selector records across
45 exact source-owned controls contained 2 such one-past-zero records and no other
out-of-bounds form. The census is evidence for the shape, not a hard-coded control
allowlist.
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
from d1_fnv1_action_probe import DEFAULTS, fnv1

CONTROL_REF = "80802C0E"
CLIP_REF = "808005A1"
EMPTY_SELECTION_SENTINEL = 0x0000FFFF


def _u32(b: bytes, o: int) -> int:
    if o < 0 or o + 4 > len(b):
        raise ValueError(f"u32 OOB at 0x{o:X}/0x{len(b):X}")
    return struct.unpack_from("<I", b, o)[0]


def _f32(b: bytes, o: int) -> float:
    if o < 0 or o + 4 > len(b):
        raise ValueError(f"f32 OOB at 0x{o:X}/0x{len(b):X}")
    return struct.unpack_from("<f", b, o)[0]


def _rel_array(b: bytes, count_off: int, ptr_off: int):
    count = _u32(b, count_off)
    rel = _u32(b, ptr_off)
    hdr = ptr_off + rel
    if hdr < 0 or hdr + 0x10 > len(b):
        raise ValueError(f"array header out of range: 0x{hdr:X}")
    repeated = _u32(b, hdr)
    if repeated != count:
        raise ValueError(
            f"count mismatch field={count} header={repeated} at 0x{hdr:X}"
        )
    elem_class = _u32(b, hdr + 8)
    return count, hdr, hdr + 0x10, elem_class


def decode_control(
    payload: bytes,
    reader: EntryReader | None = None,
    names: list[str] | None = None,
):
    if len(payload) < 0x80:
        raise ValueError("control payload too small")

    anim_count, anim_hdr, anim_data, anim_elem_class = _rel_array(
        payload, 0x08, 0x10
    )
    state_count, state_hdr, state_data, state_elem_class = _rel_array(
        payload, 0x68, 0x70
    )
    anim_end = anim_data + 4 * anim_count
    if anim_end > len(payload):
        raise ValueError("animation list exceeds payload")
    if state_data + 0x20 * state_count > len(payload):
        raise ValueError("state table exceeds payload")

    boundary_word = _u32(payload, anim_end) if anim_end + 4 <= len(payload) else None
    hash_to_name = {fnv1(s): s for s in (names or DEFAULTS)}
    by_hash = (
        {int(e["tag_hash"], 16): e for e in reader.entries}
        if reader is not None
        else {}
    )

    animations = []
    for i in range(anim_count):
        h = _u32(payload, anim_data + i * 4)
        tag = f"{h:08X}"
        row = {"index": i, "tag_hash": tag}
        e = by_hash.get(h)
        if e is not None:
            row["entry"] = {
                "index": e["index"],
                "reference": e["reference"].upper(),
                "type": e["type"],
                "subtype": e["subtype"],
                "size": e["file_size"],
            }
        animations.append(row)

    states = []
    invalid = []
    empty_sentinels = 0
    implicit_null_tails = 0
    for i in range(state_count):
        base = state_data + i * 0x20
        h = _u32(payload, base + 0x10)
        packed = _u32(payload, base + 0x18)
        count = (packed >> 16) & 0xFFFF
        start = packed & 0xFFFF
        end = start + count

        is_empty_sentinel = packed == EMPTY_SELECTION_SENTINEL
        in_declared_bank = end <= len(animations)
        is_implicit_null_tail = (
            not is_empty_sentinel
            and count == 2
            and len(animations) > 0
            and start == len(animations) - 1
            and end == len(animations) + 1
            and boundary_word == 0
        )

        if is_empty_sentinel:
            selected = []
            selection_kind = "empty_sentinel"
            empty_sentinels += 1
            range_valid = True
            implicit_null_count = 0
        elif in_declared_bank:
            selected = animations[start:end]
            selection_kind = "range"
            range_valid = True
            implicit_null_count = 0
        elif is_implicit_null_tail:
            selected = animations[start:]
            selection_kind = "range_with_implicit_null_tail"
            range_valid = True
            implicit_null_count = 1
            implicit_null_tails += 1
        else:
            selected = []
            selection_kind = "invalid_range"
            range_valid = False
            implicit_null_count = 0
            invalid.append(
                {
                    "record_index": i,
                    "state_hash": f"{h:08X}",
                    "packed_selection": f"{packed:08X}",
                    "selection_start": start,
                    "selection_count": count,
                    "declared_bank_count": len(animations),
                    "boundary_word": (
                        None if boundary_word is None else f"{boundary_word:08X}"
                    ),
                }
            )

        states.append(
            {
                "record_index": i,
                "record_offset": base,
                "state_hash": f"{h:08X}",
                "state_name": hash_to_name.get(h),
                "scalar_f32": _f32(payload, base + 0x14),
                "packed_selection": f"{packed:08X}",
                "selection_count": count,
                "selection_start": start,
                "selection_kind": selection_kind,
                "selection_range_valid": range_valid,
                "implicit_null_count": implicit_null_count,
                "selected_animations": selected,
            }
        )

    if invalid:
        raise ValueError(
            f"{len(invalid)} selector ranges exceed animation list outside the "
            f"source-proven null-tail form: {invalid[:3]}"
        )

    return {
        "animation_list": {
            "count": anim_count,
            "header_offset": anim_hdr,
            "data_offset": anim_data,
            "data_end_offset": anim_end,
            "element_class": f"{anim_elem_class:08X}",
            "boundary_word_u32": (
                None if boundary_word is None else f"{boundary_word:08X}"
            ),
            "items": animations,
        },
        "state_table": {
            "count": state_count,
            "header_offset": state_hdr,
            "data_offset": state_data,
            "element_class": f"{state_elem_class:08X}",
            "record_stride": 0x20,
            "empty_sentinel_count": empty_sentinels,
            "implicit_null_tail_count": implicit_null_tails,
            "records": states,
        },
        "evidence_policy": (
            "FileHash list, state hashes and packed count/start indices are binary "
            "decoded. 0x0000FFFF is the retail-proven explicit empty selector. A "
            "one-past range is accepted only for count=2 at the final declared bank "
            "entry when the immediately following serialized u32 is zero; that zero "
            "is preserved as an implicit null choice and is never promoted to a clip. "
            "All other out-of-range forms fail. Names appear only for exact FNV1 "
            "preimages; scalar_f32 semantics remain intentionally unnamed."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pkg", type=Path)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--control-tag", required=True)
    ap.add_argument("--name", action="append", default=[])
    ap.add_argument("-o", "--output", type=Path)
    a = ap.parse_args()

    r = EntryReader(a.pkg, a.runtime)
    tag = a.control_tag.upper()
    h = int(tag, 16)
    by_hash = {int(e["tag_hash"], 16): e for e in r.entries}
    e = by_hash.get(h)
    if e is None:
        raise SystemExit(f"{tag} is not present in package {r.h['pkg_id']:04X}")
    if e["tag_hash"].upper() != tag:
        raise SystemExit(f"entry mismatch: expected {tag}, got {e['tag_hash']}")
    if e["reference"].upper() != CONTROL_REF:
        raise SystemExit(f"{tag} ref {e['reference']}, expected {CONTROL_REF}")

    names = list(dict.fromkeys(DEFAULTS + a.name))
    out = {
        "control": {
            "tag_hash": tag,
            "index": e["index"],
            "reference": e["reference"].upper(),
            "size": e["file_size"],
        },
        **decode_control(r.entry(e["index"]), r, names),
    }
    text = json.dumps(out, indent=2)
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(text + "\n", encoding="utf-8")
        print("wrote", a.output)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
