#!/usr/bin/env python3
"""Find exact direct-call xrefs to selected virtual addresses in a D1 PS4 eboot.

This scans only executable ELF segments with Capstone and records direct
near-call immediates whose resolved target exactly equals a caller-supplied VA.
It makes no function-boundary or semantic claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

from capstone import Cs, CS_ARCH_X86, CS_MODE_64
from capstone.x86 import X86_OP_IMM

from d1_executable_probe import parse_elf64_header, parse_elf64_program_headers


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("executable", type=Path)
    ap.add_argument("--target", action="append", required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    targets = {int(x, 0) for x in a.target}
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

    hits: dict[int, list[dict]] = defaultdict(list)
    decoded = 0
    direct_calls = 0

    for segment_index, segment in enumerate(executable):
        file_offset = int(segment["absolute_file_offset"])
        size = int(segment["file_size"])
        va = int(segment["virtual_address"], 16)
        data = raw[file_offset:file_offset + size]
        for insn in md.disasm(data, va):
            if insn.id == 0:
                continue
            decoded += 1
            if insn.mnemonic != "call" or not insn.operands:
                continue
            op = insn.operands[0]
            if op.type != X86_OP_IMM:
                continue
            direct_calls += 1
            target = int(op.imm) & 0xFFFFFFFFFFFFFFFF
            if target not in targets:
                continue
            hits[target].append({
                "callsite_va": int(insn.address),
                "callsite_va_hex": hex(int(insn.address)),
                "instruction_size": int(insn.size),
                "bytes_hex": bytes(insn.bytes).hex(),
                "segment_index": segment_index,
            })

    rows = []
    for target in sorted(targets):
        xrefs = sorted(hits.get(target, []), key=lambda x: x["callsite_va"])
        rows.append({
            "target_va": target,
            "target_va_hex": hex(target),
            "direct_call_xref_count": len(xrefs),
            "xrefs": xrefs,
        })

    report = {
        "schema": "d1_executable_direct_call_xrefs/v1",
        "executable_sha256": hashlib.sha256(raw).hexdigest(),
        "file_size": len(raw),
        "decoded_instruction_count": decoded,
        "direct_call_instruction_count": direct_calls,
        "targets": rows,
        "policy": (
            "Every reported edge is an exact direct x86-64 call-immediate target "
            "in an executable ELF segment. The callsite is not assigned to a "
            "function or semantic owner without separate boundary/decompiler evidence."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "status": "D1_EXECUTABLE_DIRECT_CALL_XREFS",
        "targets": [
            {
                "target": r["target_va_hex"],
                "xref_count": r["direct_call_xref_count"],
                "callsites": [x["callsite_va_hex"] for x in r["xrefs"][:20]],
            }
            for r in rows
        ],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
