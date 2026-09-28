#!/usr/bin/env python3
"""Scan the exact D1 PS4 executable for renderer state-vector consumers.

The retail renderer keeps a mutable state vector at object offsets +0x15D0..+0x15D4.
Writer sites are already source-executable evidence; this probe finds *all* direct
x86-64 memory references to those displacements so reads can be followed into the
native state application path instead of inferred from later Tiger implementations.

This tool deliberately reports raw instruction/access evidence only. It does not
assign blend/depth/raster/depth-bias lane names or selector semantics.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, deque
from pathlib import Path

from capstone import (
    Cs,
    CS_ARCH_X86,
    CS_MODE_64,
    CS_AC_READ,
    CS_AC_WRITE,
)
from capstone.x86 import X86_OP_MEM

from d1_executable_probe import parse_elf64_header, parse_elf64_program_headers

TARGET_DISPS = {0x15D0, 0x15D1, 0x15D2, 0x15D3, 0x15D4}


def access_name(access: int) -> str:
    parts = []
    if access & CS_AC_READ:
        parts.append("read")
    if access & CS_AC_WRITE:
        parts.append("write")
    return "+".join(parts) if parts else "unknown"


def row_for(insn) -> dict:
    refs = []
    for oi, op in enumerate(insn.operands):
        if op.type != X86_OP_MEM or int(op.mem.disp) not in TARGET_DISPS:
            continue
        refs.append({
            "operand_index": oi,
            "disp": int(op.mem.disp),
            "disp_hex": hex(int(op.mem.disp)),
            "base_reg": insn.reg_name(op.mem.base) if op.mem.base else None,
            "index_reg": insn.reg_name(op.mem.index) if op.mem.index else None,
            "scale": int(op.mem.scale),
            "access": access_name(int(op.access)),
        })
    return {
        "address": int(insn.address),
        "address_hex": hex(int(insn.address)),
        "size": int(insn.size),
        "bytes_hex": bytes(insn.bytes).hex(),
        "mnemonic": insn.mnemonic,
        "op_str": insn.op_str,
        "state_refs": refs,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("executable", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--context-before", type=int, default=10)
    ap.add_argument("--context-after", type=int, default=16)
    args = ap.parse_args()

    raw = args.executable.read_bytes()
    header = parse_elf64_header(raw)
    if header is None or not header.get("supported"):
        raise ValueError("expected supported ELF64 executable")
    segments = parse_elf64_program_headers(raw, header)
    executable = [s for s in segments if s.get("executable") and int(s.get("file_size", 0)) > 0]

    md = Cs(CS_ARCH_X86, CS_MODE_64)
    md.detail = True
    md.skipdata = True

    hits = []
    access_counts = Counter()
    disp_counts = Counter()

    for segment in executable:
        file_offset = int(segment["absolute_file_offset"])
        size = int(segment["file_size"])
        va = int(segment["virtual_address"], 16)
        data = raw[file_offset:file_offset + size]

        history = deque(maxlen=max(0, args.context_before))
        pending = []

        for insn in md.disasm(data, va):
            # Capstone emits synthetic data pseudo-instructions when SKIPDATA
            # crosses embedded data. Detail/operands are intentionally unavailable
            # for those records, so preserve them only as disassembly boundaries.
            if insn.id == 0:
                history.clear()
                continue

            base_row = {
                "address": int(insn.address),
                "address_hex": hex(int(insn.address)),
                "size": int(insn.size),
                "bytes_hex": bytes(insn.bytes).hex(),
                "mnemonic": insn.mnemonic,
                "op_str": insn.op_str,
            }

            # Complete forward context for prior hits.
            for item in list(pending):
                item["context_after"].append(base_row)
                item["_remaining"] -= 1
                if item["_remaining"] <= 0:
                    del item["_remaining"]
                    pending.remove(item)

            refs = []
            for oi, op in enumerate(insn.operands):
                if op.type != X86_OP_MEM:
                    continue
                disp = int(op.mem.disp)
                if disp not in TARGET_DISPS:
                    continue
                acc = access_name(int(op.access))
                refs.append({
                    "operand_index": oi,
                    "disp": disp,
                    "disp_hex": hex(disp),
                    "base_reg": insn.reg_name(op.mem.base) if op.mem.base else None,
                    "index_reg": insn.reg_name(op.mem.index) if op.mem.index else None,
                    "scale": int(op.mem.scale),
                    "access": acc,
                })
                access_counts[acc] += 1
                disp_counts[hex(disp)] += 1

            if refs:
                item = dict(base_row)
                item["state_refs"] = refs
                item["context_before"] = list(history)
                item["context_after"] = []
                item["_remaining"] = max(0, args.context_after)
                hits.append(item)
                if item["_remaining"]:
                    pending.append(item)
                else:
                    del item["_remaining"]

            history.append(base_row)

    # Strip any unfinished bookkeeping at EOF.
    for item in hits:
        item.pop("_remaining", None)

    report = {
        "schema": "d1_executable_renderer_state4_xrefs/v1",
        "executable_sha256": hashlib.sha256(raw).hexdigest(),
        "file_size": len(raw),
        "target_displacements": [hex(x) for x in sorted(TARGET_DISPS)],
        "hit_count": len(hits),
        "access_counts": dict(access_counts),
        "displacement_counts": dict(disp_counts),
        "policy": (
            "Direct exact-build x86 memory-reference evidence only. Offsets are "
            "reported without assigning fixed-function lane names, selector-table "
            "meaning, or pass identity."
        ),
        "hits": hits,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "D1_EXECUTABLE_RENDERER_STATE4_XREFS",
        "sha256": report["executable_sha256"],
        "hit_count": report["hit_count"],
        "access_counts": report["access_counts"],
        "displacement_counts": report["displacement_counts"],
        "output": str(args.output),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
