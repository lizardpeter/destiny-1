#!/usr/bin/env python3
"""Disassemble exact x86-64 code windows at requested D1 eboot virtual addresses.

This is an exact-build helper for following call targets discovered by the
renderer xref pass without assigning function names. It preserves direct
calls/jumps, RIP-relative references, scalar literals, and nearby strings.

Example:
  python tools/d1_executable_code_windows.py eboot.bin \
    --address 0x8186c0 --address 0x818930 -o helpers.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from capstone import Cs, CS_ARCH_X86, CS_MODE_64
from capstone.x86 import X86_OP_IMM, X86_OP_MEM, X86_REG_RIP

from d1_executable_probe import (
    parse_elf64_header,
    parse_elf64_program_headers,
    printable_ascii_strings,
)


def va_to_file(va: int, segments: list[dict]) -> int | None:
    for segment in segments:
        seg_va = int(segment["virtual_address"], 16)
        seg_size = int(segment["file_size"])
        if seg_va <= va < seg_va + seg_size:
            return int(segment["absolute_file_offset"]) + va - seg_va
    return None


def string_index(raw: bytes, segments: list[dict]) -> dict[int, str]:
    out = {}
    for row in printable_ascii_strings(raw, min_length=5):
        va = None
        for segment in segments:
            base = int(segment["absolute_file_offset"])
            size = int(segment["file_size"])
            if base <= row["file_offset"] < base + size:
                va = int(segment["virtual_address"], 16) + row["file_offset"] - base
                break
        if va is not None:
            out[va] = row["text"]
    return out


def decode(
    raw: bytes,
    segments: list[dict],
    strings: dict[int, str],
    start_va: int,
    size: int,
    max_instructions: int,
) -> dict:
    file_offset = va_to_file(start_va, segments)
    if file_offset is None:
        return {
            "start_va": start_va,
            "status": "UNMAPPED_VIRTUAL_ADDRESS",
            "instructions": [],
        }

    md = Cs(CS_ARCH_X86, CS_MODE_64)
    md.detail = True
    data = raw[file_offset:min(len(raw), file_offset + size)]
    rows = []
    calls = []
    jumps = []
    rip_refs = []
    d1_hashes = []
    constants = []

    for insn in md.disasm(data, start_va):
        op_rows = []
        for op in insn.operands:
            if op.type == X86_OP_IMM:
                value = int(op.imm) & 0xFFFFFFFFFFFFFFFF
                op_rows.append({"type": "imm", "value": value, "hex": hex(value)})
                constants.append({
                    "instruction_va": insn.address,
                    "value": value,
                    "hex": hex(value),
                })
                if 0x80800000 <= value <= 0x827FFFFF:
                    d1_hashes.append({
                        "instruction_va": insn.address,
                        "value": value,
                        "hex": hex(value),
                    })
            elif op.type == X86_OP_MEM:
                item = {
                    "type": "mem",
                    "base": int(op.mem.base),
                    "index": int(op.mem.index),
                    "scale": int(op.mem.scale),
                    "disp": int(op.mem.disp),
                }
                if op.mem.base == X86_REG_RIP:
                    target = insn.address + insn.size + int(op.mem.disp)
                    item["rip_target"] = target
                    ref = {
                        "instruction_va": insn.address,
                        "target_va": target,
                    }
                    if target in strings:
                        ref["string"] = strings[target]
                    rip_refs.append(ref)
                op_rows.append(item)
            else:
                op_rows.append({"type": int(op.type)})

        if insn.mnemonic == "call" and insn.operands and insn.operands[0].type == X86_OP_IMM:
            calls.append({
                "instruction_va": insn.address,
                "target_va": int(insn.operands[0].imm) & 0xFFFFFFFFFFFFFFFF,
            })
        if insn.mnemonic.startswith("j") and insn.operands and insn.operands[0].type == X86_OP_IMM:
            jumps.append({
                "instruction_va": insn.address,
                "target_va": int(insn.operands[0].imm) & 0xFFFFFFFFFFFFFFFF,
                "mnemonic": insn.mnemonic,
            })

        rows.append({
            "address": insn.address,
            "address_hex": hex(insn.address),
            "offset": insn.address - start_va,
            "mnemonic": insn.mnemonic,
            "op_str": insn.op_str,
            "size": insn.size,
            "operands": op_rows,
        })
        if len(rows) >= max_instructions:
            break
        if insn.mnemonic == "ret" and len(rows) >= 4:
            break

    return {
        "start_va": start_va,
        "start_va_hex": hex(start_va),
        "status": "DISASSEMBLED" if rows else "NO_INSTRUCTIONS",
        "instruction_count": len(rows),
        "instructions": rows,
        "direct_calls": calls,
        "direct_jumps": jumps,
        "rip_references": rip_refs,
        "d1_hash_literals": d1_hashes,
        "scalar_literals": constants,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("executable", type=Path)
    parser.add_argument("--address", action="append", required=True)
    parser.add_argument("--size", type=lambda x: int(x, 0), default=0x1000)
    parser.add_argument("--max-instructions", type=int, default=512)
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args()

    raw = args.executable.read_bytes()
    header = parse_elf64_header(raw)
    if header is None or not header.get("supported"):
        raise ValueError("expected supported ELF64 executable")
    segments = parse_elf64_program_headers(raw, header)
    strings = string_index(raw, segments)
    addresses = [int(value, 0) for value in args.address]

    report = {
        "schema": "d1_executable_code_windows/v1",
        "executable_sha256": hashlib.sha256(raw).hexdigest(),
        "file_size": len(raw),
        "policy": (
            "Requested virtual addresses and decoded instructions are exact-build "
            "evidence. A start address is not promoted as a function boundary or "
            "semantic identity without independent control-flow/decompiler proof."
        ),
        "windows": [
            decode(
                raw,
                segments,
                strings,
                address,
                args.size,
                args.max_instructions,
            )
            for address in addresses
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "D1_EXECUTABLE_CODE_WINDOWS",
        "window_count": len(report["windows"]),
        "output": str(args.output),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
