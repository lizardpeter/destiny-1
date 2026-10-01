#!/usr/bin/env python3
"""Audit D1 Rise-of-Iron TFX raw opcodes against distinct bytecode revisions.

This report deliberately separates:
  * raw exact-retail opcode/framing evidence,
  * Bungie GDC 2017 example identities (a real but different bytecode revision),
  * a strategy-aware community D1 Rise-of-Iron table,
  * independently closed retail semantics.

It does not promote the community table by itself.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

GDC_2017 = {
    0x43: {"name": "PopOutput", "operand_bytes": 1},
    0x45: {"name": "PushTemp", "operand_bytes": 1},
    0x46: {"name": "PopTemp", "operand_bytes": 1},
    0x4D: {"name": "PushObjectChannelVector", "operand_bytes": 1},
}

ROI_LINEAGE = {
    0x42: {"name": "PopOutput", "operand_bytes": 1},
    0x43: {"name": "PopOutputMat4", "operand_bytes": 1},
    0x44: {"name": "PushTemp", "operand_bytes": 1},
    0x45: {"name": "PopTemp", "operand_bytes": 1},
    0x46: {"name": "SetShaderTexture", "operand_bytes": 1},
    0x47: {"name": "SetShaderSampler", "operand_bytes": 1},
    0x49: {"name": "PushSampler", "operand_bytes": 1},
    # The lineage interpreter parses object-channel values as a uint32. Flag
    # any retail 0x4A presence for a framing-specific proof before promotion.
    0x4A: {"name": "PushObjectChannelVector", "operand_bytes": 4},
    0x4B: {"name": "PushGlobalChannelVector", "operand_bytes": 1},
    0x4E: {"name": "Unk50", "operand_bytes": 1},
    0x50: {"name": "PushTexDimensions", "operand_bytes": 2},
    0x51: {"name": "PushTexTileParams", "operand_bytes": 2},
    0x52: {"name": "PushTexTileCount", "operand_bytes": 2},
}

RETAIL_CLOSED = {
    0x42: {
        "behavior": "one-byte output-vector target; scoped evaluator pops one Vec4 and writes target",
        "operand_bytes": 1,
        "evidence": "Tower lights + 809DCD66 + Xur 80876579 + Xur 80876952",
    },
    0x49: {
        "behavior": "first byte of exact ROI PS resource-assignment prefix 49/index/47/destination",
        "operand_bytes": 1,
        "evidence": "Xur + three-NPC exact material state",
    },
    0x47: {
        "behavior": "second opcode of exact ROI PS resource-assignment prefix 49/index/47/destination",
        "operand_bytes": 1,
        "evidence": "Xur + three-NPC exact material state",
    },
}


def opnum(row: dict) -> int:
    return int(row["opcode"], 16)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    src = json.loads(args.inventory.read_text())
    raw_hist = Counter()
    by_opcode_program = defaultdict(set)
    operands = defaultdict(Counter)
    neighbor = defaultdict(Counter)
    framing = defaultdict(Counter)
    programs = src.get("buffers", [])

    for program in programs:
        ph = str(program.get("buffer_hash"))
        ops = program.get("ops", [])
        for i, row in enumerate(ops):
            op = opnum(row)
            raw_hist[op] += 1
            by_opcode_program[op].add(ph)
            raw = bytes.fromhex(row.get("raw_hex", ""))
            operand_len = max(0, len(raw) - 1)
            framing[op][operand_len] += 1
            if row.get("operand_bytes"):
                operands[op][tuple(int(x) for x in row["operand_bytes"])] += 1
            prev = opnum(ops[i-1]) if i else None
            nxt = opnum(ops[i+1]) if i+1 < len(ops) else None
            neighbor[op][(prev, nxt)] += 1

    focus = {}
    for op in range(0x3F, 0x53):
        count = raw_hist[op]
        if not count:
            continue
        observed_framing = {str(k): v for k, v in sorted(framing[op].items())}
        lineage = ROI_LINEAGE.get(op)
        gdc = GDC_2017.get(op)
        focus[f"0x{op:02X}"] = {
            "raw_occurrences": count,
            "program_count": len(by_opcode_program[op]),
            "observed_operand_byte_histogram": observed_framing,
            "top_operands": [
                {
                    "bytes_hex": "".join(f"{x:02X}" for x in operand),
                    "count": n,
                }
                for operand, n in operands[op].most_common(32)
            ],
            "top_neighbors": [
                {
                    "previous": None if a is None else f"0x{a:02X}",
                    "next": None if b is None else f"0x{b:02X}",
                    "count": n,
                }
                for (a, b), n in neighbor[op].most_common(24)
            ],
            "gdc_2017_identity": gdc,
            "roi_strategy_lineage_identity": lineage,
            "retail_closed": RETAIL_CLOSED.get(op),
            "roi_lineage_framing_matches_current_inventory": (
                None if lineage is None
                else all(int(k) == int(lineage["operand_bytes"]) for k in observed_framing)
            ),
        }

    # This is the key revision discriminator. Retail 0x42 matches the RoI table's
    # PopOutput location and contradicts treating GDC 0x43 as universal for RoI.
    revision = {
        "retail_0x42_output_target_occurrences": raw_hist[0x42],
        "retail_0x43_occurrences": raw_hist[0x43],
        "retail_0x4b_occurrences": raw_hist[0x4B],
        "gdc_object_channel_opcode": "0x4D",
        "roi_lineage_object_channel_opcode": "0x4A",
        "conclusion": (
            "Bungie GDC 2017 identities are authoritative for the bytecode revision "
            "shown in that presentation, but exact Rise-of-Iron retail 0x42 output-write "
            "dataflow demonstrates that the GDC numbering cannot be applied universally "
            "to this corpus. The strategy-aware RoI table is a revision hypothesis to "
            "validate opcode-by-opcode against retail framing/dataflow."
        ),
    }

    violations = []
    if raw_hist[0x42] == 0:
        violations.append("expected exact Tower corpus to contain raw 0x42 output writes")
    for op, ident in ROI_LINEAGE.items():
        if raw_hist[op] and not all(
            int(k) == ident["operand_bytes"] for k in framing[op]
        ):
            violations.append(
                f"raw 0x{op:02X} observed framing conflicts with RoI lineage "
                f"{ident['name']} width {ident['operand_bytes']}: {dict(framing[op])}"
            )

    report = {
        "schema": "d1_roi_tfx_opcode_revision_audit/v1",
        "status": "D1_ROI_TFX_OPCODE_REVISION_AUDIT" if not violations else "D1_ROI_TFX_OPCODE_REVISION_AUDIT_WITH_CONFLICTS",
        "source_inventory_status": src.get("status"),
        "program_count": len(programs),
        "raw_opcode_histogram": {f"0x{k:02X}": v for k, v in sorted(raw_hist.items())},
        "focus_0x3f_0x52": focus,
        "revision_assessment": revision,
        "source_tables": {
            "bungie_gdc_2017": "Destiny Shader Pipeline compiled-bytecode example: 0x43 PopOutput, 0x45 PushTemp, 0x46 PopTemp, 0x4D PushObjectChannelVector",
            "roi_lineage": "Rhys-Kovacevic/charm_exporter@4bdce74798549f50d3687732d47ec5183a516069 TfxBytecode_D1",
        },
        "violations": violations,
        "policy": (
            "Raw retail bytes and independent dataflow outrank table names. "
            "The GDC table and RoI lineage table are kept revision-scoped. "
            "No opcode is promoted solely because a community table names it."
        ),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "status": report["status"],
        "program_count": report["program_count"],
        "focus": {
            k: {
                "occurrences": v["raw_occurrences"],
                "programs": v["program_count"],
                "framing": v["observed_operand_byte_histogram"],
                "gdc": v["gdc_2017_identity"],
                "roi": v["roi_strategy_lineage_identity"],
                "retail": v["retail_closed"],
            }
            for k, v in focus.items()
        },
        "violations": violations,
    }, indent=2))
    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
