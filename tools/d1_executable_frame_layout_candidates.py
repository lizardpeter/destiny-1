#!/usr/bin/env python3
"""Rank exact D1 eboot code neighborhoods that structurally resemble a Frame extern layout.

This probe does NOT import later-engine field names into Destiny 1.  A continued
Tiger implementation provides only a search oracle: scalar Frame fields occur at
0x14, 0x18, 0x1c, 0x20, 0x24 and 0x28.  The exact D1 retail executable is scanned
for code regions where one non-stack base register accesses several of those
offsets close together, with +0x1c required.

The output is candidate evidence for follow-up disassembly/decompilation.  It
does not claim that any candidate base is D1 Frame, nor that +0x1c is exposure.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from capstone import (
    Cs,
    CS_ARCH_X86,
    CS_MODE_64,
    CS_AC_READ,
    CS_AC_WRITE,
)
from capstone.x86 import (
    X86_OP_MEM,
    X86_REG_RBP,
    X86_REG_RIP,
    X86_REG_RSP,
)

from d1_executable_probe import parse_elf64_header, parse_elf64_program_headers

# Continued-Tiger layout oracle only.  Names are deliberately omitted here.
FRAME_ORACLE_OFFSETS = {
    0x00, 0x04, 0x0C, 0x10, 0x14, 0x18, 0x1C,
    0x20, 0x24, 0x28, 0x2C, 0x40, 0x70,
}
CORE_NEIGHBORS = {0x14, 0x18, 0x20, 0x24, 0x28}


def access_name(access: int) -> str:
    parts = []
    if access & CS_AC_READ:
        parts.append("read")
    if access & CS_AC_WRITE:
        parts.append("write")
    return "+".join(parts) if parts else "unknown"


def base_row(insn) -> dict:
    return {
        "address": int(insn.address),
        "address_hex": hex(int(insn.address)),
        "size": int(insn.size),
        "bytes_hex": bytes(insn.bytes).hex(),
        "mnemonic": insn.mnemonic,
        "op_str": insn.op_str,
    }


def candidate_score(offsets: set[int], center_accesses: list[str], ref_count: int) -> int:
    score = len(offsets) * 3 + ref_count
    if 0x14 in offsets:
        score += 7
    if 0x18 in offsets:
        score += 9
    if 0x28 in offsets:
        score += 9
    if 0x20 in offsets:
        score += 3
    if 0x24 in offsets:
        score += 3
    if any("write" in access for access in center_accesses):
        score += 6
    return score


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("executable", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--cluster-span", type=lambda x: int(x, 0), default=0x180)
    ap.add_argument("--min-distinct-offsets", type=int, default=3)
    ap.add_argument("--max-candidates", type=int, default=500)
    args = ap.parse_args()

    raw = args.executable.read_bytes()
    header = parse_elf64_header(raw)
    if header is None or not header.get("supported"):
        raise ValueError("expected supported ELF64 executable")
    segments = parse_elf64_program_headers(raw, header)
    executable = [
        s for s in segments
        if s.get("executable") and int(s.get("file_size", 0)) > 0
    ]

    md = Cs(CS_ARCH_X86, CS_MODE_64)
    md.detail = True
    md.skipdata = True

    # First pass deliberately stores only compact matching references.  The
    # previous implementation retained disassembly context for every matching
    # instruction, which turned a forensic filter into an unnecessary
    # whole-executable memory/time sink.  Detailed code windows are a follow-up
    # operation on the ranked candidates.
    all_refs: list[dict] = []
    offset_counts = Counter()
    access_counts = Counter()
    region_id = 0

    for segment_index, segment in enumerate(executable):
        file_offset = int(segment["absolute_file_offset"])
        size = int(segment["file_size"])
        va = int(segment["virtual_address"], 16)
        data = raw[file_offset:file_offset + size]

        for insn in md.disasm(data, va):
            if insn.id == 0:
                region_id += 1
                continue

            for op in insn.operands:
                if op.type != X86_OP_MEM:
                    continue
                disp = int(op.mem.disp)
                if disp not in FRAME_ORACLE_OFFSETS:
                    continue
                if op.mem.base in (0, X86_REG_RIP, X86_REG_RSP, X86_REG_RBP):
                    continue
                base = insn.reg_name(op.mem.base)
                access = access_name(int(op.access))
                all_refs.append({
                    "address": int(insn.address),
                    "address_hex": hex(int(insn.address)),
                    "region_id": region_id,
                    "segment_index": segment_index,
                    "base_reg": base,
                    "disp": disp,
                    "disp_hex": hex(disp),
                    "access": access,
                    "mnemonic": insn.mnemonic,
                    "op_str": insn.op_str,
                })
                offset_counts[hex(disp)] += 1
                access_counts[access] += 1

            # A return is a conservative local-region boundary.  This is not a
            # claim that every decoded span starts at a true function entry.
            if insn.mnemonic.startswith("ret"):
                region_id += 1

    by_region_base: dict[tuple[int, int, str], list[dict]] = defaultdict(list)
    for ref in all_refs:
        by_region_base[
            (ref["segment_index"], ref["region_id"], ref["base_reg"])
        ].append(ref)
    for refs in by_region_base.values():
        refs.sort(key=lambda row: row["address"])

    candidates = []
    seen = set()
    for center in all_refs:
        if center["disp"] != 0x1C:
            continue
        key = (
            center["segment_index"],
            center["region_id"],
            center["base_reg"],
            center["address"],
        )
        if key in seen:
            continue
        seen.add(key)
        refs = by_region_base[
            (center["segment_index"], center["region_id"], center["base_reg"])
        ]
        nearby = [
            ref for ref in refs
            if abs(ref["address"] - center["address"]) <= args.cluster_span
        ]
        offsets = {ref["disp"] for ref in nearby}
        if len(offsets) < args.min_distinct_offsets:
            continue
        if not (offsets & CORE_NEIGHBORS):
            continue
        center_accesses = [
            ref["access"] for ref in nearby
            if ref["address"] == center["address"] and ref["disp"] == 0x1C
        ]
        candidates.append({
            "score": candidate_score(offsets, center_accesses, len(nearby)),
            "center_address": center["address"],
            "center_address_hex": center["address_hex"],
            "base_reg": center["base_reg"],
            "center_accesses": center_accesses,
            "distinct_offsets": [hex(value) for value in sorted(offsets)],
            "ref_count": len(nearby),
            "span_start_hex": hex(min(ref["address"] for ref in nearby)),
            "span_end_hex": hex(max(ref["address"] for ref in nearby)),
            "refs": nearby,
            "center_instruction": {
                "mnemonic": center["mnemonic"],
                "op_str": center["op_str"],
            },
        })

    candidates.sort(
        key=lambda row: (
            -row["score"],
            -len(row["distinct_offsets"]),
            row["center_address"],
        )
    )
    candidates = candidates[:args.max_candidates]

    report = {
        "schema": "d1_executable_frame_layout_candidates/v1",
        "executable_sha256": hashlib.sha256(raw).hexdigest(),
        "file_size": len(raw),
        "oracle": {
            "source": "continued Tiger Frame layout; search heuristic only",
            "required_offset": "0x1c",
            "candidate_offsets": [hex(x) for x in sorted(FRAME_ORACLE_OFFSETS)],
            "core_neighbor_offsets": [hex(x) for x in sorted(CORE_NEIGHBORS)],
        },
        "policy": (
            "Exact D1 retail x86 memory-access evidence is reported. The initial "
            "ranker intentionally omits broad disassembly context; detailed windows "
            "must be captured only for selected candidates. Continued-Tiger offsets "
            "are used only to rank structural candidates. No candidate is "
            "identified as D1 Frame, and no D1 field meaning (including exposure) "
            "is promoted without independent D1 producer/consumer proof."
        ),
        "scan": {
            "cluster_span": args.cluster_span,
            "min_distinct_offsets": args.min_distinct_offsets,
            "raw_matching_ref_count": len(all_refs),
            "candidate_count": len(candidates),
            "offset_counts": dict(offset_counts),
            "access_counts": dict(access_counts),
        },
        "candidates": candidates,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "D1_EXECUTABLE_FRAME_LAYOUT_CANDIDATES",
        "sha256": report["executable_sha256"],
        "candidate_count": len(candidates),
        "top": [
            {
                "score": row["score"],
                "center": row["center_address_hex"],
                "base": row["base_reg"],
                "offsets": row["distinct_offsets"],
            }
            for row in candidates[:12]
        ],
        "output": str(args.output),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
