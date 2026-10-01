#!/usr/bin/env python3
"""Evidence-first census for unresolved D1 Tower light TFX opcode 0x4B.

Consumes d1_tfx_program_inventory.py output. This tool does not name opcode 0x4B.
It records the exact one-byte operand, local opcode context, and tests only the
possible stack-depth effects {-1, 0, +1} against the source-closed Tower light
evaluator subset. A hypothesis is reported as structurally compatible only when
all otherwise-supported 0x4B programs avoid underflow and end with an empty
stack. Compatibility is evidence, not an opcode-semantic promotion.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

# (minimum stack depth, stack delta) for the exact evaluator subset in
# Rust-test/src/native_vulkan_destiny1_light_program_eval.rs.
STACK = {
    0x03: (2, -1),  # Multiply
    0x0E: (2, -1),  # Merge_3_1
    0x10: (3, -2),  # Lerp
    0x12: (3, -2),  # MultiplyAdd
    0x1F: (1, 0),   # VecRotCos
    0x21: (1, 0),   # PermuteAllX
    0x22: (1, 0),   # Permute
    0x23: (1, 0),   # Saturate
    0x27: (1, 0),   # Triangle
    0x28: (1, 0),   # Jitter
    0x29: (1, 0),   # Wander
    0x2A: (1, 0),   # Rand
    0x34: (0, +1),  # PushConstantVec4
    0x35: (1, 0),   # LerpConstant
    0x3C: (0, +1),  # PushExternInputFloat
    0x42: (1, -1),  # evidence-scoped output store
}

HYPOTHESES = {
    # A strategy-aware D1 Rise of Iron lineage table maps raw D1 0x4B to
    # PushGlobalChannelVector. That would be a one-Vec4 push. Keep the generic
    # structural name here so corpus compatibility remains separate from the
    # external semantic lead.
    "push_one": (0, +1),
    "side_effect_no_stack": (0, 0),
    "replace_top": (1, 0),
    "consume_one": (1, -1),
}

D1_LINEAGE_LEAD = {
    "repository": "Rhys-Kovacevic/charm_exporter",
    "commit": "4bdce74798549f50d3687732d47ec5183a516069",
    "path": "Tiger/Schema/Shaders/TFX/OpCodes.cs",
    "strategy_table": "TfxBytecode_D1 / Destiny 1 Rise of Iron",
    "raw_opcode": "0x4B",
    "mapped_name": "PushGlobalChannelVector",
    "operand_width": 1,
    "expected_stack_effect": "push_one_vec4",
    "runtime_table_source": "D1 render globals loaded from bootstrap FileHash 0020AF80; ordered GlobalChannelDefaults",
    "authority": "corroborating lineage only; exact D1 retail Tower corpus must independently validate stack behavior and operand/index domain",
}


def opnum(row: dict) -> int:
    return int(row["opcode"], 16)


def simulate(ops: list[dict], hypothesis: tuple[int, int]) -> dict:
    depth = 0
    max_depth = 0
    unknown = []
    underflow = []
    for index, row in enumerate(ops):
        opcode = opnum(row)
        if opcode == 0x4B:
            need, delta = hypothesis
        else:
            entry = STACK.get(opcode)
            if entry is None:
                unknown.append({
                    "index": index,
                    "offset": row.get("offset"),
                    "opcode": f"0x{opcode:02X}",
                    "name": row.get("name"),
                })
                continue
            need, delta = entry
        if depth < need:
            underflow.append({
                "index": index,
                "offset": row.get("offset"),
                "opcode": f"0x{opcode:02X}",
                "depth_before": depth,
                "required": need,
            })
            # Keep walking from zero so all failures are visible.
            depth = 0
        else:
            depth += delta
        max_depth = max(max_depth, depth)
    return {
        "final_depth": depth,
        "max_depth": max_depth,
        "underflow": underflow,
        "other_unmodeled_opcodes": unknown,
        "structurally_closed": not underflow and not unknown and depth == 0,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    src = json.loads(args.inventory.read_text())
    operand_occ = Counter()
    operand_programs: dict[int, set[str]] = defaultdict(set)
    neighbors = Counter()
    positions = Counter()
    blocked = []
    exact_occurrence_count = 0

    for program in src.get("buffers", []):
        ops = program.get("ops", [])
        uses = []
        for i, row in enumerate(ops):
            if opnum(row) != 0x4B:
                continue
            operand = int(row["operand_bytes"][0])
            prev = opnum(ops[i - 1]) if i else None
            nxt = opnum(ops[i + 1]) if i + 1 < len(ops) else None
            occurrence = {
                "offset": row.get("offset"),
                "operand": operand,
                "operand_hex": f"0x{operand:02X}",
                "previous_opcode": None if prev is None else f"0x{prev:02X}",
                "previous_name": None if i == 0 else ops[i - 1].get("name"),
                "next_opcode": None if nxt is None else f"0x{nxt:02X}",
                "next_name": None if i + 1 >= len(ops) else ops[i + 1].get("name"),
            }
            uses.append(occurrence)
            exact_occurrence_count += 1
            operand_occ[operand] += 1
            operand_programs[operand].add(program.get("buffer_hash"))
            neighbors[(prev, nxt)] += 1
            positions[i] += 1
        if not uses:
            continue

        hypotheses = {
            name: simulate(ops, effect)
            for name, effect in HYPOTHESES.items()
        }
        blocked.append({
            "buffer_hash": program.get("buffer_hash"),
            "program_sha256": program.get("program_sha256"),
            "instruction_count": len(ops),
            "unk4b_uses": uses,
            "hypotheses": hypotheses,
        })

    compatible_all = []
    for name in HYPOTHESES:
        considered = [
            row["hypotheses"][name]
            for row in blocked
            if not row["hypotheses"][name]["other_unmodeled_opcodes"]
        ]
        if considered and len(considered) == len(blocked) and all(
            row["structurally_closed"] for row in considered
        ):
            compatible_all.append(name)

    out = {
        "format": "d1-tower-light-unk4b-forensic-census-v1",
        "status": "FORENSIC_HYPOTHESES_ONLY_SEMANTICS_WITHHELD",
        "source_inventory_status": src.get("status"),
        "program_count": src.get("unique_program_count"),
        "unk4b_program_count": len(blocked),
        "unk4b_occurrence_count": exact_occurrence_count,
        "operand_histogram": {
            f"0x{k:02X}": {
                "occurrences": operand_occ[k],
                "program_count": len(operand_programs[k]),
                "programs": sorted(operand_programs[k]),
            }
            for k in sorted(operand_occ)
        },
        "neighbor_histogram": {
            f"{('START' if a is None else f'0x{a:02X}')}->0x4B->{('END' if b is None else f'0x{b:02X}')}": count
            for (a, b), count in sorted(
                neighbors.items(),
                key=lambda item: (
                    -item[1],
                    -1 if item[0][0] is None else item[0][0],
                    -1 if item[0][1] is None else item[0][1],
                ),
            )
        },
        "instruction_index_histogram": dict(sorted(positions.items())),
        "d1_lineage_lead": D1_LINEAGE_LEAD,
        "stack_effect_hypotheses": {
            "definitions": {
                name: {"minimum_depth": effect[0], "delta": effect[1]}
                for name, effect in HYPOTHESES.items()
            },
            "compatible_across_every_blocked_program": compatible_all,
        "push_global_channel_vector_lineage_stack_compatible": "push_one" in compatible_all,
            "push_global_channel_vector_lineage_stack_compatible": "push_one" in compatible_all,
            "policy": (
                "Stack-depth compatibility is necessary but not sufficient evidence. "
                "Do not assign a D1 opcode name or runtime source from this test alone."
            ),
        },
        "blocked_programs": blocked,
        "proof_boundary": (
            "The D1 corpus independently fixes 0x4B framing at one following u8. "
            "This report only narrows stack effect and operand/context structure. "
            "A strategy-aware D1 Rise of Iron lineage table specifically maps raw "
            "D1 0x4B to PushGlobalChannelVector and uses an ordered render-global "
            "channel table. That is stronger than generic later-Tiger opcode proximity, "
            "but it is still not promoted without exact Tower stack/index/dataflow proof."
        ),
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({
        "status": out["status"],
        "unk4b_program_count": out["unk4b_program_count"],
        "unk4b_occurrence_count": out["unk4b_occurrence_count"],
        "operand_histogram": out["operand_histogram"],
        "neighbor_histogram": out["neighbor_histogram"],
        "compatible_across_every_blocked_program": compatible_all,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
