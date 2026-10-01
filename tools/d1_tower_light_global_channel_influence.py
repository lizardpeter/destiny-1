#!/usr/bin/env python3
"""Exact downstream influence census for D1 Tower light raw RoI TFX 0x4B inputs.

Consumes the exact Tower light TFX inventory and lighting census. The analysis
is deliberately semantic-light:
  * raw 0x4B pushes one Vec4 selected by its one-byte operand;
  * raw 0x42 stores one stack Vec4 into the exact eight-Vec4 Buffer2 state;
  * raw 0x44/0x45 are the current-RoI temp-bank push/pop relationship;
  * known arithmetic follows the source-closed D1 evaluator behavior.

The report answers which BufferData outputs and LightData records each raw
0x4B index can influence. Human-facing global-channel names remain withheld.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
from collections import Counter, defaultdict
from pathlib import Path

CHANNELS = (0x11, 0x28, 0x30, 0x60)


def opnum(row: dict) -> int:
    return int(row["opcode"], 16)


def const_expr(row: dict) -> str:
    i = int(row["operand_bytes"][0])
    value = row.get("buffer1_candidate")
    return f"C{i}" if value is None else f"C{i}{value}"


def merge_deps(*items: dict) -> set[int]:
    out: set[int] = set()
    for item in items:
        out |= item["channels"]
    return out


def val(expr: str, channels=()) -> dict:
    return {"expr": expr, "channels": set(channels)}


def pop(stack: list[dict], source_hash: str, offset: int, label: str) -> dict:
    if not stack:
        raise ValueError(f"{source_hash} {label} stack underflow at 0x{offset:X}")
    return stack.pop()


def permute_expr(expr: str, fields: int) -> str:
    dims = "xyzw"
    swiz = "".join(dims[(fields >> shift) & 3] for shift in (6, 4, 2, 0))
    return f"permute({expr},.{swiz})"


def analyze_program(program: dict) -> dict:
    stack: list[dict] = []
    temps: dict[int, dict] = {}
    outputs: dict[int, dict] = {}
    channel_uses = Counter()
    source_hash = program["buffer_hash"]

    for row in program["ops"]:
        op = opnum(row)
        at = int(row["offset"])
        args = row.get("operand_bytes", [])

        if op == 0x34:
            stack.append(val(const_expr(row)))
        elif op == 0x35:
            index = int(args[0])
            t = pop(stack, source_hash, at, "LerpConstant")
            stack.append(val(
                f"lerp(C{index},C{index+1},{t['expr']})",
                t["channels"],
            ))
        elif op == 0x3C:
            extern_id, element = map(int, args)
            stack.append(val(f"Extern[{extern_id}:{element}]"))
        elif op == 0x4B:
            index = int(args[0])
            if index not in CHANNELS:
                raise ValueError(
                    f"{source_hash} raw 0x4B uses unexpected index 0x{index:02X}"
                )
            channel_uses[index] += 1
            stack.append(val(f"G{index:02X}", {index}))
        elif op == 0x44:
            index = int(args[0])
            if index not in temps:
                raise ValueError(
                    f"{source_hash} PushTemp {index} before PopTemp at 0x{at:X}"
                )
            temp = temps[index]
            stack.append(val(temp["expr"], temp["channels"]))
        elif op == 0x45:
            index = int(args[0])
            temps[index] = pop(stack, source_hash, at, "PopTemp")
        elif op == 0x42:
            target = int(args[0])
            outputs[target] = pop(stack, source_hash, at, "OutputStore")
        elif op in (0x01, 0x03, 0x0B, 0x0E):
            b = pop(stack, source_hash, at, row["name"])
            a = pop(stack, source_hash, at, row["name"])
            deps = merge_deps(a, b)
            if op == 0x01:
                expr = f"({a['expr']}+{b['expr']})"
            elif op == 0x03:
                expr = f"({a['expr']}*{b['expr']})"
            elif op == 0x0B:
                expr = f"dot({a['expr']},{b['expr']})"
            else:
                expr = f"merge3_1({a['expr']},{b['expr']})"
            stack.append(val(expr, deps))
        elif op == 0x21:
            a = pop(stack, source_hash, at, "PermuteAllX")
            stack.append(val(f"splatX({a['expr']})", a["channels"]))
        elif op == 0x22:
            a = pop(stack, source_hash, at, "Permute")
            stack.append(val(permute_expr(a["expr"], int(args[0])), a["channels"]))
        elif op == 0x23:
            a = pop(stack, source_hash, at, "Saturate")
            stack.append(val(f"saturate({a['expr']})", a["channels"]))
        elif op == 0x29:
            a = pop(stack, source_hash, at, "Wander")
            stack.append(val(f"wander({a['expr']})", a["channels"]))
        else:
            raise ValueError(
                f"{source_hash} opcode 0x{op:02X} at 0x{at:X} is outside "
                "the exact 0x4B-program analysis subset"
            )

    if stack:
        raise ValueError(f"{source_hash} ends with {len(stack)} stack value(s)")

    influenced = defaultdict(list)
    for target, result in outputs.items():
        for channel in result["channels"]:
            influenced[channel].append({
                "target": target,
                "formula": result["expr"],
            })

    return {
        "buffer_hash": source_hash,
        "program_sha256": program["program_sha256"],
        "channel_occurrences": {
            f"0x{k:02X}": v for k, v in sorted(channel_uses.items())
        },
        "influenced_outputs": {
            f"0x{k:02X}": sorted(v, key=lambda row: row["target"])
            for k, v in sorted(influenced.items())
        },
    }


def u32(raw: bytes, offset: int) -> int:
    return struct.unpack_from("<I", raw, offset)[0]


def f32x4(raw: bytes, offset: int) -> tuple[float, float, float, float]:
    return struct.unpack_from("<4f", raw, offset)


def volume_kind(raw: bytes) -> str:
    row = f32x4(raw, 0x50)
    if (
        abs(row[0]) <= 1e-5
        and abs(row[1]) <= 1e-5
        and abs(row[2]) <= 1e-5
        and abs(row[3] - 1.0) <= 1e-5
    ):
        return "AFFINE"
    return "PROJECTIVE"


def light_records(lighting: dict) -> list[dict]:
    out = []
    for collection in lighting["light_collections"]:
        collection_hash = collection["hash"]
        for light in collection["lights"]:
            raw = bytes.fromhex(light["record_hex"])
            if len(raw) != 0x90:
                raise ValueError(
                    f"{collection_hash}/{light['index']} LightData is {len(raw):#x}, "
                    "expected 0x90"
                )
            material = u32(raw, 0x80)
            buffer_hash = u32(raw, 0x84)
            out.append({
                "collection_hash": collection_hash,
                "record_index": int(light["index"]),
                "record_sha256": light["record_sha256"],
                "material_hash": f"{material:08X}",
                "buffer_hash": f"{buffer_hash:08X}",
                "flags88": f"{u32(raw, 0x88):08X}",
                "flags8c": f"{u32(raw, 0x8C):08X}",
                "volume_kind": volume_kind(raw),
            })
    return out


def channel_lane_shape(formulas: list[str], channel_hex: str) -> dict:
    token = f"G{channel_hex[2:]}"
    x_only = 0
    vector_xyz = 0
    raw_other = 0
    for formula in formulas:
        if token not in formula:
            continue
        compact = formula.replace(" ", "")
        if (
            f"splatX({token})" in compact
            or f"permute({token},.xxxx)" in compact
            or f"splatX(permute(" in compact and token in compact
        ):
            x_only += 1
        if f"permute({token},.xyzz)" in compact:
            vector_xyz += 1
        if f"permute({token}," not in compact and f"splatX({token})" not in compact:
            raw_other += 1
    if vector_xyz and not raw_other and not x_only:
        classification = "VECTOR_XYZ_LIKE"
    elif x_only and not vector_xyz and not raw_other:
        classification = "SCALAR_X_LIKE"
    elif x_only and not vector_xyz:
        classification = "SCALAR_X_DOMINANT"
    elif vector_xyz and not x_only:
        classification = "VECTOR_XYZ_DOMINANT"
    else:
        classification = "MIXED_OR_UNRESOLVED"
    return {
        "classification": classification,
        "x_only_formula_count": x_only,
        "xyz_formula_count": vector_xyz,
        "other_formula_count": raw_other,
        "proof_boundary": (
            "This is only lane-use structure. SCALAR_X_LIKE does not assign an "
            "intensity/exposure semantic; VECTOR_XYZ_LIKE does not assign a "
            "direction/position/color semantic."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", type=Path, required=True)
    ap.add_argument("--lighting-census", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    inv = json.loads(a.inventory.read_text())
    lighting = json.loads(a.lighting_census.read_text())

    analyzed = []
    for program in inv["buffers"]:
        if not any(opnum(row) == 0x4B for row in program["ops"]):
            continue
        analyzed.append(analyze_program(program))

    if len(analyzed) != 86:
        raise ValueError(f"expected 86 0x4B BufferData, got {len(analyzed)}")

    buffer_channel = {}
    for row in analyzed:
        channels = sorted(row["influenced_outputs"])
        if len(channels) != 1:
            raise ValueError(
                f"{row['buffer_hash']} does not have clean single-channel influence: "
                f"{channels}"
            )
        buffer_channel[row["buffer_hash"]] = channels[0]

    records = light_records(lighting)
    if len(records) != 737:
        raise ValueError(f"expected 737 LightData records, got {len(records)}")

    stats = {}
    for channel in CHANNELS:
        ch = f"0x{channel:02X}"
        buffers = [r for r in analyzed if ch in r["influenced_outputs"]]
        buffer_hashes = {r["buffer_hash"] for r in buffers}
        related_records = [r for r in records if r["buffer_hash"] in buffer_hashes]
        formulas = []
        target_counter = Counter()
        pattern_counter = Counter()
        templates = defaultdict(lambda: {
            "buffer_hashes": [],
            "output_targets": [],
            "formulas": [],
        })
        for row in buffers:
            outputs = row["influenced_outputs"][ch]
            targets = tuple(sorted(x["target"] for x in outputs))
            pattern_counter[targets] += 1
            for x in outputs:
                target_counter[x["target"]] += 1
                formulas.append(x["formula"])
            t = templates[row["program_sha256"]]
            t["buffer_hashes"].append(row["buffer_hash"])
            t["output_targets"] = list(targets)
            t["formulas"] = [x["formula"] for x in outputs]

        material_hashes = sorted({r["material_hash"] for r in related_records})
        volumes = Counter(r["volume_kind"] for r in related_records)
        template_rows = []
        for sha, t in sorted(templates.items()):
            template_rows.append({
                "program_sha256": sha,
                "buffer_count": len(t["buffer_hashes"]),
                "buffer_hashes": sorted(t["buffer_hashes"]),
                "output_targets": t["output_targets"],
                "formulas": t["formulas"],
            })

        stats[ch] = {
            "buffer_count": len(buffers),
            "unique_program_count": len(templates),
            "light_record_count": len(related_records),
            "unique_material_count": len(material_hashes),
            "material_hashes": material_hashes,
            "volume_kind_counts": dict(sorted(volumes.items())),
            "output_target_counts": {
                str(k): v for k, v in sorted(target_counter.items())
            },
            "output_target_patterns": {
                ",".join(map(str, k)): v for k, v in sorted(pattern_counter.items())
            },
            "lane_use": channel_lane_shape(formulas, ch),
            "program_templates": template_rows,
            "records": related_records,
        }

    # Exact pinned corpus regression.
    expected = {
        "0x11": (3, 3, 4, 3),
        "0x28": (62, 3, 160, 98),
        "0x30": (20, 5, 23, 20),
        "0x60": (1, 1, 1, 1),
    }
    for ch, values in expected.items():
        got = (
            stats[ch]["buffer_count"],
            stats[ch]["unique_program_count"],
            stats[ch]["light_record_count"],
            stats[ch]["unique_material_count"],
        )
        if got != values:
            raise ValueError(f"{ch} regression: got {got}, expected {values}")

    if stats["0x28"]["volume_kind_counts"] != {"AFFINE": 102, "PROJECTIVE": 58}:
        raise ValueError(f"0x28 volume regression: {stats['0x28']['volume_kind_counts']}")
    if stats["0x30"]["volume_kind_counts"] != {"AFFINE": 23}:
        raise ValueError(f"0x30 volume regression: {stats['0x30']['volume_kind_counts']}")
    if stats["0x11"]["volume_kind_counts"] != {"AFFINE": 3, "PROJECTIVE": 1}:
        raise ValueError(f"0x11 volume regression: {stats['0x11']['volume_kind_counts']}")
    if stats["0x60"]["volume_kind_counts"] != {"AFFINE": 1}:
        raise ValueError(f"0x60 volume regression: {stats['0x60']['volume_kind_counts']}")

    total_buffers = sum(v["buffer_count"] for v in stats.values())
    total_records = sum(v["light_record_count"] for v in stats.values())
    if total_buffers != 86 or total_records != 188:
        raise ValueError(
            f"channel partition regression: {total_buffers} buffers / {total_records} records"
        )

    out = {
        "schema": "d1_tower_light_global_channel_influence/v1",
        "status": "EXACT_RETAIL_0X4B_DOWNSTREAM_INFLUENCE_CLOSED",
        "source_inventory_sha256": hashlib.sha256(a.inventory.read_bytes()).hexdigest(),
        "source_lighting_census_sha256": hashlib.sha256(
            a.lighting_census.read_bytes()
        ).hexdigest(),
        "corpus": {
            "tower_bufferdata_count": int(inv["buffer_count"]),
            "tower_light_record_count": int(lighting["light_record_count"]),
            "raw_0x4b_buffer_count": total_buffers,
            "raw_0x4b_light_record_count": total_records,
            "raw_0x4b_indices": [f"0x{x:02X}" for x in CHANNELS],
            "clean_single_channel_partition": True,
        },
        "channels": stats,
        "priority": [
            {
                "index": "0x28",
                "reason": "62 BufferData / 160 LightData records / 98 materials; dominant exact 0x4B fanout",
            },
            {
                "index": "0x30",
                "reason": "20 BufferData / 23 LightData records / 20 materials; exact affine-only fanout",
            },
            {
                "index": "0x11",
                "reason": "3 BufferData / 4 LightData records / 3 materials",
            },
            {
                "index": "0x60",
                "reason": "1 BufferData / 1 LightData record / 1 material",
            },
        ],
        "proof_boundary": (
            "Exact current-retail Tower bytecode closes channel dependency, output "
            "slot, LightData ownership, material ownership, and affine/projective "
            "volume class. Lane-use classifications describe only how raw Vec4 lanes "
            "participate in the TFX math. No human-facing channel name or live runtime "
            "producer/value is assigned by this report."
        ),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({
        "status": out["status"],
        "channels": {
            ch: {
                "buffers": x["buffer_count"],
                "programs": x["unique_program_count"],
                "records": x["light_record_count"],
                "materials": x["unique_material_count"],
                "volumes": x["volume_kind_counts"],
                "targets": x["output_target_counts"],
                "lane_use": x["lane_use"]["classification"],
            }
            for ch, x in stats.items()
        },
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
