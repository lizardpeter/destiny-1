#!/usr/bin/env python3
"""Census D1 80802C0E selector ranges against declared animation-list bounds.

This is a structural proof tool for the generic activity animation path. It consumes
an exact actor animation control plan, reopens every selected 80802C0E control, parses
the two source-calibrated dynamic arrays without interpreting state names, and classifies
all packed selector ranges into:

- empty_sentinel: packed 0x0000FFFF;
- in_declared_bank: start+count <= declared animation-list count;
- one_past_bank_to_zero: exactly one logical slot extends beyond the declared list and
  the contiguous serialized word at that slot is literal 00000000;
- other_out_of_bounds: every other overrun shape.

The one-past-zero class is evidence only. This tool does not promote that zero word to
an array member or silently alter selection semantics. It exists to establish whether
the retail corpus uses a recurring implicit-null boundary convention.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_split_tar_extract import SplitHttpTar

CONTROL_REF = "80802C0E"
ANIM_ARRAY_COUNT_OFF = 0x08
ANIM_ARRAY_PTR_OFF = 0x10
SELECTOR_COUNT_OFF = 0x68
SELECTOR_PTR_OFF = 0x70
SELECTOR_STRIDE = 0x20


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def u32(b: bytes, off: int) -> int:
    if off < 0 or off + 4 > len(b):
        raise ValueError(f"u32_oob:0x{off:X}/0x{len(b):X}")
    return struct.unpack_from("<I", b, off)[0]


def rel_array(b: bytes, count_off: int, ptr_off: int, stride: int) -> dict:
    count = u32(b, count_off)
    rel = u32(b, ptr_off)
    header = ptr_off + rel
    if header < 0 or header + 0x10 > len(b):
        raise ValueError(f"array_header_oob:0x{header:X}")
    repeated = u32(b, header)
    elem_class = u32(b, header + 8)
    data = header + 0x10
    end = data + count * stride
    if end > len(b):
        raise ValueError(f"array_payload_oob:0x{end:X}/0x{len(b):X}")
    return {
        "count": count,
        "relative": rel,
        "header": header,
        "repeated_count": repeated,
        "element_class": f"{elem_class:08X}",
        "data": data,
        "end": end,
        "stride": stride,
        "count_matches": count == repeated,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--control-plan", type=Path, required=True)
    ap.add_argument("--member-catalog", type=Path, action="append", required=True)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--part-count", type=int, default=10)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    plan = json.loads(a.control_plan.read_text(encoding="utf-8"))
    violations: list[str] = []
    if plan.get("schema") != "d1_activity_actor_animation_control_plan/v1":
        violations.append(f"unexpected_control_plan_schema:{plan.get('schema')!r}")
    if plan.get("status") != "D1_ACTIVITY_ACTOR_ANIMATION_CONTROL_PLAN_COMPLETE":
        violations.append("control_plan_not_complete")

    catalogs = load_catalogs(a.member_catalog)
    base = a.base_url.rstrip("/")
    arc = SplitHttpTar(
        [f"{base}/packages.tar.{i:03d}" for i in range(1, a.part_count + 1)],
        retries=6,
        timeout=90,
    )
    c = RemoteCorpus(arc, catalogs, a.runtime)

    rows = []
    totals = Counter()
    state_hashes = Counter()
    class_shape_counts = Counter()

    for ch0 in plan.get("control_hashes", []):
        ch = norm(ch0)
        row = {"control": ch, "violations": [], "selectors": []}
        try:
            meta = c.entry_meta(ch)
            b, src = c.payload(ch)
            if meta is None or b is None or norm(meta.get("reference", "FFFFFFFF")) != CONTROL_REF:
                raise ValueError("control_missing_or_wrong_class")
            row["source"] = str(src)
            aa = rel_array(b, ANIM_ARRAY_COUNT_OFF, ANIM_ARRAY_PTR_OFF, 4)
            ss = rel_array(b, SELECTOR_COUNT_OFF, SELECTOR_PTR_OFF, SELECTOR_STRIDE)
            row["animation_array"] = aa
            row["selector_array"] = ss
            if not aa["count_matches"]:
                row["violations"].append("animation_array_repeated_count_mismatch")
            if not ss["count_matches"]:
                row["violations"].append("selector_array_repeated_count_mismatch")

            local_counts = Counter()
            for i in range(ss["count"]):
                off = ss["data"] + i * SELECTOR_STRIDE
                state = f"{u32(b, off + 0x10):08X}"
                packed = u32(b, off + 0x18)
                count = (packed >> 16) & 0xFFFF
                start = packed & 0xFFFF
                logical_end = start + count
                rec = {
                    "record_index": i,
                    "record_offset": off,
                    "state_hash": state,
                    "packed_selection": f"{packed:08X}",
                    "selection_start": start,
                    "selection_count": count,
                    "logical_end_exclusive": logical_end,
                    "declared_bank_count": aa["count"],
                }
                if packed == 0x0000FFFF:
                    cls = "empty_sentinel"
                elif logical_end <= aa["count"]:
                    cls = "in_declared_bank"
                elif logical_end == aa["count"] + 1 and start < aa["count"]:
                    missing_off = aa["data"] + aa["count"] * 4
                    rec["one_past_serialized_offset"] = missing_off
                    if missing_off + 4 <= len(b):
                        trailing = u32(b, missing_off)
                        rec["one_past_serialized_word"] = f"{trailing:08X}"
                        cls = "one_past_bank_to_zero" if trailing == 0 else "other_out_of_bounds"
                    else:
                        cls = "other_out_of_bounds"
                else:
                    cls = "other_out_of_bounds"
                rec["classification"] = cls
                local_counts[cls] += 1
                totals[cls] += 1
                state_hashes[state] += 1
                row["selectors"].append(rec)
            row["classification_counts"] = dict(local_counts)
            row["boundary_selector_count"] = local_counts["one_past_bank_to_zero"]
            row["other_oob_selector_count"] = local_counts["other_out_of_bounds"]
            class_shape_counts[(aa["count"], ss["count"], local_counts["one_past_bank_to_zero"], local_counts["other_out_of_bounds"])] += 1
        except Exception as ex:
            row["violations"].append(repr(ex))
        violations.extend(f"{ch}:{x}" for x in row["violations"])
        rows.append(row)

    boundary = [
        {"control": r["control"], **s}
        for r in rows for s in r.get("selectors", [])
        if s["classification"] == "one_past_bank_to_zero"
    ]
    other_oob = [
        {"control": r["control"], **s}
        for r in rows for s in r.get("selectors", [])
        if s["classification"] == "other_out_of_bounds"
    ]
    out = {
        "schema": "d1_remote_activity_animation_selector_boundary_census/v1",
        "status": "COMPLETE" if not violations else "WITH_VIOLATIONS",
        "source_control_plan": str(a.control_plan),
        "control_count": len(rows),
        "selector_count": sum(len(r.get("selectors", [])) for r in rows),
        "classification_counts": dict(totals),
        "one_past_bank_to_zero_count": len(boundary),
        "other_out_of_bounds_count": len(other_oob),
        "one_past_bank_to_zero_records": boundary,
        "other_out_of_bounds_records": other_oob,
        "unique_state_hash_count": len(state_hashes),
        "control_shape_counts": {str(k): v for k, v in class_shape_counts.items()},
        "controls": rows,
        "violation_count": len(violations),
        "violations": violations,
        "policy": (
            "This is structural evidence only. A one-past-bank selector is classified specially only when exactly one "
            "logical slot exceeds the declared animation-list count and the contiguous serialized word is literal zero. "
            "That zero is not promoted into the dynamic array by this census. All other overruns remain distinct."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(
        "STATUS", out["status"],
        "CONTROLS", out["control_count"],
        "SELECTORS", out["selector_count"],
        "IN_BANK", totals["in_declared_bank"],
        "EMPTY", totals["empty_sentinel"],
        "ONE_PAST_ZERO", len(boundary),
        "OTHER_OOB", len(other_oob),
        "VIOLATIONS", len(violations),
    )
    for x in boundary:
        print("BOUNDARY_ZERO", x["control"], x["record_index"], x["state_hash"], x["packed_selection"])
    for x in other_oob[:20]:
        print("OTHER_OOB", x)
    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
