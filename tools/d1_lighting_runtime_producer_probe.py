#!/usr/bin/env python3
"""Targeted exact-build reverse probe for D1 lighting runtime producers.

This probe intentionally does not assign semantics from later Tiger versions.
It uses two exact D1 facts already established in this repository:

* the runtime snapshot copied block is at 0x27BE440 and the copied +0x1C
  scalar is therefore 0x27BE45C;
* D1 TFX addressing proves DeferredLight element 4/12 matrices are at
  +0x40/+0xC0 and float element 64 is at +0x100.

The scan finds exact x86-64 code references to the snapshot storage and ranks
non-stack object/base-register clusters that access +0x100 together with the
other proven DeferredLight offsets. Candidates are evidence for focused
decompilation; they are not promoted as semantic producers by this script.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict, deque
from pathlib import Path

from capstone import Cs, CS_ARCH_X86, CS_MODE_64, CS_AC_READ, CS_AC_WRITE
from capstone.x86 import X86_OP_MEM, X86_REG_RIP, X86_REG_RSP, X86_REG_RBP

from d1_executable_probe import parse_elf64_header, parse_elf64_program_headers

SNAPSHOT_ROOT = 0x27BD1D0
COPIED_BLOCK = 0x27BE440
COPIED_BLOCK_END = 0x27BE474
COPIED_SCALAR_1C = 0x27BE45C

# Exact D1 TFX byte offsets, not later-engine field names.
DEFERRED_LIGHT_OFFSETS = {0x40, 0xC0, 0x100}


def access_name(access: int) -> str:
    parts = []
    if access & CS_AC_READ:
        parts.append("read")
    if access & CS_AC_WRITE:
        parts.append("write")
    return "+".join(parts) if parts else "unknown"


def effective_access(insn, operand_index: int, access: int) -> str:
    m = insn.mnemonic.lower()
    if operand_index == 0 and (m.startswith("mov") or m.startswith("vmov")):
        return "write"
    if m.startswith(("cmp", "test", "comis", "ucomis", "vcomis", "vucomis")):
        return "read"
    return access_name(access)


def row(insn) -> dict:
    calls = []
    if insn.mnemonic == "call" and insn.operands:
        op = insn.operands[0]
        if getattr(op, "type", None) == 2:  # X86_OP_IMM
            calls.append(hex(int(op.imm) & 0xFFFFFFFFFFFFFFFF))
    return {
        "address": int(insn.address),
        "address_hex": hex(int(insn.address)),
        "bytes_hex": bytes(insn.bytes).hex(),
        "mnemonic": insn.mnemonic,
        "op_str": insn.op_str,
        "direct_calls": calls,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("executable", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--context-before", type=int, default=12)
    ap.add_argument("--context-after", type=int, default=20)
    ap.add_argument("--max-candidates", type=int, default=80)
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

    snapshot_hits = []
    snapshot_target_counts = Counter()
    displacement_hits = []
    disp_counts = Counter()
    region_id = 0

    for segment_index, segment in enumerate(executable):
        file_offset = int(segment["absolute_file_offset"])
        size = int(segment["file_size"])
        va = int(segment["virtual_address"], 16)
        data = raw[file_offset:file_offset + size]
        history = deque(maxlen=max(0, args.context_before))
        pending = []

        for insn in md.disasm(data, va):
            if insn.id == 0:
                history.clear()
                region_id += 1
                continue

            base = row(insn)
            for item in list(pending):
                item["context_after"].append(base)
                item["_remaining"] -= 1
                if item["_remaining"] <= 0:
                    item.pop("_remaining", None)
                    pending.remove(item)

            local_refs = []
            exact_snapshot_refs = []
            for oi, op in enumerate(insn.operands):
                if op.type != X86_OP_MEM:
                    continue
                access = effective_access(insn, oi, int(op.access))
                disp = int(op.mem.disp)

                if op.mem.base == X86_REG_RIP:
                    target = int(insn.address + insn.size + disp)
                    labels = []
                    if target == SNAPSHOT_ROOT:
                        labels.append("snapshot_root")
                    if target == COPIED_BLOCK:
                        labels.append("copied_block")
                    if target == COPIED_SCALAR_1C:
                        labels.append("copied_block_plus_0x1c")
                    if COPIED_BLOCK <= target <= COPIED_BLOCK_END:
                        labels.append("copied_block_range")
                    if labels:
                        exact_snapshot_refs.append({
                            "operand_index": oi,
                            "resolved_target": target,
                            "resolved_target_hex": hex(target),
                            "labels": labels,
                            "access": access,
                        })
                        snapshot_target_counts[hex(target)] += 1

                if disp in DEFERRED_LIGHT_OFFSETS and op.mem.base not in (
                    0, X86_REG_RIP, X86_REG_RSP, X86_REG_RBP
                ):
                    ref = {
                        "address": int(insn.address),
                        "address_hex": hex(int(insn.address)),
                        "region_id": region_id,
                        "segment_index": segment_index,
                        "base_reg": insn.reg_name(op.mem.base),
                        "operand_index": oi,
                        "disp": disp,
                        "disp_hex": hex(disp),
                        "mem_size": int(op.size),
                        "access": access,
                        "mnemonic": insn.mnemonic,
                        "op_str": insn.op_str,
                    }
                    local_refs.append(ref)
                    displacement_hits.append(ref)
                    disp_counts[hex(disp)] += 1

            if exact_snapshot_refs:
                item = dict(base)
                item.update({
                    "segment_index": segment_index,
                    "region_id": region_id,
                    "snapshot_refs": exact_snapshot_refs,
                    "context_before": list(history),
                    "context_after": [],
                    "_remaining": max(0, args.context_after),
                })
                snapshot_hits.append(item)
                if item["_remaining"]:
                    pending.append(item)
                else:
                    item.pop("_remaining", None)

            history.append(base)
            if insn.mnemonic.startswith("ret"):
                region_id += 1

    for item in snapshot_hits:
        item.pop("_remaining", None)

    groups = defaultdict(list)
    for ref in displacement_hits:
        groups[(ref["segment_index"], ref["region_id"], ref["base_reg"])].append(ref)

    candidates = []
    for (segment_index, rid, base_reg), refs in groups.items():
        offsets = {x["disp"] for x in refs}
        if 0x100 not in offsets:
            continue
        refs.sort(key=lambda x: x["address"])
        read_count = sum("read" in x["access"] for x in refs)
        write_count = sum("write" in x["access"] for x in refs)
        offset100 = [x for x in refs if x["disp"] == 0x100]
        score = 20 + len(refs)
        if 0xC0 in offsets:
            score += 35
        if 0x40 in offsets:
            score += 35
        if offsets == DEFERRED_LIGHT_OFFSETS:
            score += 50
        if write_count:
            score += 20
        if read_count:
            score += 10
        # Prefer scalar/SIMD float traffic but keep all candidates.
        floatish = sum(
            any(t in x["mnemonic"].lower() for t in ("ss", "ps", "vmov", "movaps", "movups"))
            for x in refs
        )
        score += min(floatish, 20) * 2
        candidates.append({
            "score": score,
            "segment_index": segment_index,
            "region_id": rid,
            "base_reg": base_reg,
            "distinct_offsets": [hex(x) for x in sorted(offsets)],
            "ref_count": len(refs),
            "read_ref_count": read_count,
            "write_ref_count": write_count,
            "floatish_ref_count": floatish,
            "span_start_hex": hex(refs[0]["address"]),
            "span_end_hex": hex(refs[-1]["address"]),
            "plus_0x100_refs": offset100,
            "refs": refs,
        })

    candidates.sort(key=lambda x: (-x["score"], x["span_start_hex"]))
    candidates = candidates[:args.max_candidates]

    report = {
        "schema": "d1_lighting_runtime_producer_probe/v1",
        "status": "EXACT_BUILD_STRUCTURAL_PRODUCER_FRONTIER",
        "executable_sha256": hashlib.sha256(raw).hexdigest(),
        "file_size": len(raw),
        "exact_inputs": {
            "runtime_snapshot_root": hex(SNAPSHOT_ROOT),
            "runtime_snapshot_copied_block": hex(COPIED_BLOCK),
            "runtime_snapshot_copied_plus_0x1c": hex(COPIED_SCALAR_1C),
            "deferred_light_tfx_byte_offsets": [hex(x) for x in sorted(DEFERRED_LIGHT_OFFSETS)],
            "deferred_light_offset_derivation": {
                "matrix_element_4": "4 * 16 = 0x40",
                "matrix_element_12": "12 * 16 = 0xC0",
                "float_element_64": "64 * 4 = 0x100",
            },
        },
        "snapshot_storage": {
            "hit_count": len(snapshot_hits),
            "resolved_target_counts": dict(snapshot_target_counts),
            "hits": snapshot_hits,
        },
        "deferred_light_structural_scan": {
            "displacement_counts": dict(disp_counts),
            "candidate_count": len(candidates),
            "candidates": candidates,
        },
        "policy": (
            "All x86 references are exact-build evidence. The snapshot address identity is "
            "structural storage evidence only. A +0x100 object access is not called "
            "DeferredLight unless its producer/consumer dataflow is independently tied to "
            "the D1 TFX extern block. Joint +0x40/+0xC0/+0x100 access is ranked because "
            "those byte offsets are independently proven by the D1 retail TFX VM."
        ),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "snapshot_hit_count": len(snapshot_hits),
        "snapshot_target_counts": dict(snapshot_target_counts),
        "deferred_candidates": [
            {
                "score": x["score"],
                "base": x["base_reg"],
                "span": [x["span_start_hex"], x["span_end_hex"]],
                "offsets": x["distinct_offsets"],
                "reads": x["read_ref_count"],
                "writes": x["write_ref_count"],
            }
            for x in candidates[:20]
        ],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
