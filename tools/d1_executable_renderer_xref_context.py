#!/usr/bin/env python3
"""Disassemble exact D1 PS4 renderer-string xref neighborhoods.

This is a focused exact-build executable pass. It takes the renderer string/xref
frontier, selects graphics-qualified anchors, and uses Capstone to decode a
bounded neighborhood around every RIP-relative xref. Direct call/jump targets,
RIP-relative memory references, scalar immediates and nearby renderer strings are
retained. Function boundaries are NOT inferred here.

Install dependency:
  python -m pip install capstone
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from capstone import Cs, CS_ARCH_X86, CS_MODE_64
from capstone.x86 import X86_OP_IMM, X86_OP_MEM, X86_REG_RIP

from d1_executable_probe import (
    parse_elf64_header,
    parse_elf64_program_headers,
    printable_ascii_strings,
)


STRONG_PATTERNS = (
    re.compile(r"^<launch package render globals>$", re.I),
    re.compile(r"^object render globals$", re.I),
    re.compile(r"feature renderer", re.I),
    re.compile(r"^graphics:", re.I),
    re.compile(r"gpu exception", re.I),
    re.compile(r"gpu main resources", re.I),
    re.compile(r"gpu plate bit resources", re.I),
    re.compile(r"gpu blitter ring buffer", re.I),
    re.compile(r"shadow buffer", re.I),
    re.compile(r"ambient occlusion .*container", re.I),
    re.compile(r"^gbuffer_", re.I),
    re.compile(r"^autoexposure$", re.I),
    re.compile(r"^render_submit_lights_view_job$", re.I),
    re.compile(r"^render_submit_", re.I),
    re.compile(r"^render_setup_", re.I),
    re.compile(r"^final_combine_output_surface$", re.I),
    re.compile(r"^shadow_depth_stencil$", re.I),
    re.compile(r"^stencil$", re.I),
    re.compile(r"^renderer$", re.I),
    re.compile(r"^material$", re.I),
    re.compile(r"^texture$", re.I),
    re.compile(r"^shadow$", re.I),
)

SECONDARY_PATTERNS = (
    re.compile(r"render target", re.I),
    re.compile(r"command buffer", re.I),
    re.compile(r"surface", re.I),
    re.compile(r"shader", re.I),
    re.compile(r"sampler", re.I),
    re.compile(r"depth", re.I),
    re.compile(r"blend", re.I),
)


def selected_anchor(text: str) -> tuple[bool, str | None]:
    if any(p.search(text) for p in STRONG_PATTERNS):
        return True, "strong"
    if any(p.search(text) for p in SECONDARY_PATTERNS):
        # Avoid obvious non-graphics subsystems for generic words.
        lower = text.lower()
        if lower.startswith(("networking:", "physics:", "audio:", "ui:")):
            return False, None
        return True, "secondary"
    return False, None


def va_to_file(va: int, segments: list[dict]) -> int | None:
    for segment in segments:
        seg_va = int(segment["virtual_address"], 16)
        seg_size = int(segment["file_size"])
        if seg_va <= va < seg_va + seg_size:
            return int(segment["absolute_file_offset"]) + (va - seg_va)
    return None


def executable_segment_for_va(va: int, segments: list[dict]) -> dict | None:
    for segment in segments:
        if not segment.get("executable"):
            continue
        seg_va = int(segment["virtual_address"], 16)
        seg_size = int(segment["file_size"])
        if seg_va <= va < seg_va + seg_size:
            return segment
    return None


def string_index(raw: bytes, segments: list[dict]) -> dict[int, str]:
    out: dict[int, str] = {}
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


def disassemble_window(
    raw: bytes,
    segments: list[dict],
    strings: dict[int, str],
    center_va: int,
    before: int,
    after: int,
) -> dict:
    segment = executable_segment_for_va(center_va, segments)
    if segment is None:
        return {"status": "XREF_NOT_IN_EXECUTABLE_SEGMENT", "instructions": []}

    seg_va = int(segment["virtual_address"], 16)
    seg_file = int(segment["absolute_file_offset"])
    seg_size = int(segment["file_size"])
    start_va = max(seg_va, center_va - before)
    end_va = min(seg_va + seg_size, center_va + after)
    start_file = seg_file + (start_va - seg_va)
    data = raw[start_file : start_file + (end_va - start_va)]

    md = Cs(CS_ARCH_X86, CS_MODE_64)
    md.detail = True
    rows = []
    direct_calls = []
    direct_jumps = []
    rip_refs = []
    d1_hash_literals = []
    small_state_literals = []

    for insn in md.disasm(data, start_va):
        operands = []
        for op in insn.operands:
            if op.type == X86_OP_IMM:
                value = int(op.imm) & 0xFFFFFFFFFFFFFFFF
                operands.append({"type": "imm", "value": value, "hex": hex(value)})
                if 0x80800000 <= value <= 0x827FFFFF:
                    d1_hash_literals.append({
                        "instruction_va": insn.address,
                        "value": value,
                        "hex": hex(value),
                    })
                if value <= 0x100:
                    small_state_literals.append({
                        "instruction_va": insn.address,
                        "value": value,
                        "hex": hex(value),
                    })
            elif op.type == X86_OP_MEM:
                mem = op.mem
                item = {
                    "type": "mem",
                    "base": int(mem.base),
                    "index": int(mem.index),
                    "scale": int(mem.scale),
                    "disp": int(mem.disp),
                }
                if mem.base == X86_REG_RIP:
                    target = insn.address + insn.size + int(mem.disp)
                    item["rip_target"] = target
                    ref = {
                        "instruction_va": insn.address,
                        "target_va": target,
                    }
                    if target in strings:
                        ref["string"] = strings[target]
                    rip_refs.append(ref)
                operands.append(item)
            else:
                operands.append({"type": int(op.type)})

        if insn.mnemonic == "call" and insn.operands and insn.operands[0].type == X86_OP_IMM:
            direct_calls.append({
                "instruction_va": insn.address,
                "target_va": int(insn.operands[0].imm) & 0xFFFFFFFFFFFFFFFF,
            })
        if insn.mnemonic.startswith("j") and insn.operands and insn.operands[0].type == X86_OP_IMM:
            direct_jumps.append({
                "instruction_va": insn.address,
                "target_va": int(insn.operands[0].imm) & 0xFFFFFFFFFFFFFFFF,
                "mnemonic": insn.mnemonic,
            })

        rows.append({
            "address": insn.address,
            "address_hex": hex(insn.address),
            "offset_from_xref": insn.address - center_va,
            "mnemonic": insn.mnemonic,
            "op_str": insn.op_str,
            "size": insn.size,
            "operands": operands,
        })

    # Independently decode from the exact validated xref address. The broad
    # window can begin mid-instruction and Capstone stops at the first invalid
    # byte; the center-forward stream guarantees the xref and following control
    # flow are still available.
    center_file = va_to_file(center_va, segments)
    center_forward = []
    if center_file is not None:
        center_data = raw[center_file : min(len(raw), center_file + after)]
        for insn in md.disasm(center_data, center_va):
            center_forward.append({
                "address": insn.address,
                "address_hex": hex(insn.address),
                "offset_from_xref": insn.address - center_va,
                "mnemonic": insn.mnemonic,
                "op_str": insn.op_str,
                "size": insn.size,
            })
            if len(center_forward) >= 160:
                break

    return {
        "status": "DISASSEMBLED",
        "window": {
            "center_va": center_va,
            "start_va": start_va,
            "end_va": end_va,
            "before": before,
            "after": after,
        },
        "instruction_count": len(rows),
        "instructions": rows,
        "center_forward_instruction_count": len(center_forward),
        "center_forward_instructions": center_forward,
        "direct_calls": direct_calls,
        "direct_jumps": direct_jumps,
        "rip_references": rip_refs,
        "d1_hash_literals": d1_hash_literals,
        "small_state_literals": small_state_literals,
    }


def analyze(
    executable: Path,
    renderer_strings_path: Path,
    *,
    before: int = 512,
    after: int = 768,
    max_xrefs_per_string: int = 24,
) -> dict:
    raw = executable.read_bytes()
    header = parse_elf64_header(raw)
    if header is None or not header.get("supported"):
        raise ValueError("expected supported ELF64 executable")
    segments = parse_elf64_program_headers(raw, header)
    strings = string_index(raw, segments)

    frontier = json.loads(renderer_strings_path.read_text(encoding="utf-8"))
    if frontier.get("schema") != "d1_executable_renderer_strings/v1":
        raise ValueError("unexpected renderer string frontier schema")
    if frontier.get("executable_sha256") != hashlib.sha256(raw).hexdigest():
        raise ValueError("renderer string frontier SHA does not match executable")

    anchors = []
    total_windows = 0
    for row in frontier.get("strings", []):
        selected, strength = selected_anchor(row.get("text", ""))
        if not selected:
            continue
        xrefs = row.get("candidate_lea_xrefs", [])[:max_xrefs_per_string]
        if not xrefs:
            continue
        neighborhoods = []
        for xref in xrefs:
            va = int(xref["virtual_address"])
            neighborhoods.append(
                disassemble_window(raw, segments, strings, va, before, after)
            )
        total_windows += len(neighborhoods)
        anchors.append({
            "text": row["text"],
            "categories": row.get("categories", []),
            "strength": strength,
            "xref_count": len(xrefs),
            "xrefs": xrefs,
            "neighborhoods": neighborhoods,
        })

    anchors.sort(key=lambda row: (
        0 if row["strength"] == "strong" else 1,
        -row["xref_count"],
        row["text"].lower(),
    ))
    return {
        "schema": "d1_executable_renderer_xref_context/v1",
        "executable_sha256": hashlib.sha256(raw).hexdigest(),
        "file_size": len(raw),
        "policy": (
            "Neighborhoods are exact Capstone disassembly around validated "
            "RIP-relative string-xref byte patterns. Bounded windows are not "
            "function boundaries; semantics require subsequent control/data-flow proof."
        ),
        "counts": {
            "selected_anchor_count": len(anchors),
            "disassembly_window_count": total_windows,
        },
        "anchors": anchors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("executable", type=Path)
    parser.add_argument("--renderer-strings", type=Path, required=True)
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument("--before", type=lambda x: int(x, 0), default=512)
    parser.add_argument("--after", type=lambda x: int(x, 0), default=768)
    parser.add_argument("--max-xrefs-per-string", type=int, default=24)
    args = parser.parse_args()

    report = analyze(
        args.executable,
        args.renderer_strings,
        before=args.before,
        after=args.after,
        max_xrefs_per_string=args.max_xrefs_per_string,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "D1_EXECUTABLE_RENDERER_XREF_CONTEXT",
        **report["counts"],
        "output": str(args.output),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
