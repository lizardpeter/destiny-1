#!/usr/bin/env python3
"""Find exact RIP-relative xrefs to selected D1 PS4 virtual addresses/ranges.

A hit proves only that an instruction's resolved RIP-relative memory target falls
on a supplied exact-build address/range. It does not prove the semantic identity
of that storage.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, deque
from pathlib import Path

from capstone import Cs, CS_ARCH_X86, CS_MODE_64, CS_AC_READ, CS_AC_WRITE
from capstone.x86 import X86_OP_MEM, X86_REG_RIP

from d1_executable_probe import parse_elf64_header, parse_elf64_program_headers


def access_name(access: int) -> str:
    parts = []
    if access & CS_AC_READ:
        parts.append("read")
    if access & CS_AC_WRITE:
        parts.append("write")
    return "+".join(parts) if parts else "unknown"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("executable", type=Path)
    ap.add_argument("--target", action="append", default=[])
    ap.add_argument(
        "--range",
        dest="ranges",
        action="append",
        default=[],
        help="inclusive start:end virtual-address range",
    )
    ap.add_argument("--context-before", type=int, default=8)
    ap.add_argument("--context-after", type=int, default=12)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    targets = {int(x, 0) for x in a.target}
    ranges = []
    for value in a.ranges:
        left, right = value.split(":", 1)
        start, end = int(left, 0), int(right, 0)
        if end < start:
            raise ValueError(f"invalid range {value}")
        ranges.append((start, end))

    if not targets and not ranges:
        raise ValueError("at least one --target or --range is required")

    def match_target(value: int) -> list[str]:
        labels = []
        if value in targets:
            labels.append(f"target:{hex(value)}")
        for start, end in ranges:
            if start <= value <= end:
                labels.append(f"range:{hex(start)}:{hex(end)}")
        return labels

    raw = a.executable.read_bytes()
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

    history = deque(maxlen=max(0, a.context_before))
    pending = []
    hits = []
    target_counts = Counter()
    access_counts = Counter()

    for segment_index, segment in enumerate(executable):
        file_offset = int(segment["absolute_file_offset"])
        size = int(segment["file_size"])
        va = int(segment["virtual_address"], 16)
        data = raw[file_offset:file_offset + size]
        history.clear()

        for insn in md.disasm(data, va):
            if insn.id == 0:
                history.clear()
                continue

            base = {
                "address": int(insn.address),
                "address_hex": hex(int(insn.address)),
                "size": int(insn.size),
                "bytes_hex": bytes(insn.bytes).hex(),
                "mnemonic": insn.mnemonic,
                "op_str": insn.op_str,
            }

            for item in list(pending):
                item["context_after"].append(base)
                item["_remaining"] -= 1
                if item["_remaining"] <= 0:
                    item.pop("_remaining", None)
                    pending.remove(item)

            refs = []
            for operand_index, op in enumerate(insn.operands):
                if op.type != X86_OP_MEM or op.mem.base != X86_REG_RIP:
                    continue
                resolved = int(insn.address + insn.size + int(op.mem.disp))
                labels = match_target(resolved)
                if not labels:
                    continue
                access = access_name(int(op.access))
                refs.append({
                    "operand_index": operand_index,
                    "resolved_target": resolved,
                    "resolved_target_hex": hex(resolved),
                    "labels": labels,
                    "access": access,
                })
                target_counts[hex(resolved)] += 1
                access_counts[access] += 1

            if refs:
                item = dict(base)
                item["segment_index"] = segment_index
                item["rip_refs"] = refs
                item["context_before"] = list(history)
                item["context_after"] = []
                item["_remaining"] = max(0, a.context_after)
                hits.append(item)
                if item["_remaining"]:
                    pending.append(item)
                else:
                    item.pop("_remaining", None)

            history.append(base)

    for item in hits:
        item.pop("_remaining", None)

    report = {
        "schema": "d1_executable_rip_target_xrefs/v1",
        "executable_sha256": hashlib.sha256(raw).hexdigest(),
        "file_size": len(raw),
        "targets": [hex(x) for x in sorted(targets)],
        "ranges": [
            {"start": hex(start), "end": hex(end)}
            for start, end in ranges
        ],
        "hit_count": len(hits),
        "resolved_target_counts": dict(target_counts),
        "access_counts": dict(access_counts),
        "hits": hits,
        "policy": (
            "Resolved RIP-relative address evidence is exact-build only. Matching "
            "a candidate snapshot/global range does not identify Frame, DeferredLight "
            "or another semantic scope without independent dataflow."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "status": "D1_EXECUTABLE_RIP_TARGET_XREFS",
        "hit_count": len(hits),
        "resolved_target_counts": dict(target_counts),
        "access_counts": dict(access_counts),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
