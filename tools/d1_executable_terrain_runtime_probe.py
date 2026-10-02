#!/usr/bin/env python3
"""Recover exact D1 PS4 terrain renderer runtime ownership from the retail eboot.

This probe joins:
  * authored terrain renderer labels in the exact executable,
  * mapped absolute/relative label-pointer tables,
  * x86-64 RIP-relative code references into those table neighborhoods,
  * the existing exact-build Ghidra function/call graph.

It is deliberately conservative. A nearby immediate 14/0xE0/0x1C0 is reported as
an observation only; it is not promoted as the terrain T14 producer without a
closed dataflow from the STerrain dyemap to the shader resource table.
"""
from __future__ import annotations

import argparse
import bisect
import gzip
import hashlib
import json
import struct
from pathlib import Path

from capstone import Cs, CS_ARCH_X86, CS_MODE_64
from capstone.x86 import X86_OP_IMM, X86_OP_MEM, X86_REG_RIP

from d1_executable_probe import parse_elf64_header, parse_elf64_program_headers
from d1_executable_renderer_label_tables import scan as scan_label_tables

LABELS = (
    "terrain_feature_renderer",
    "editor_terrain_tile_renderer",
    "?chunked_terrain",
    "static_objects_renderer",
    "dynamic_objects_renderer",
    "chunked_instance_renderer",
    "rigid_objects_renderer",
    "skinned_objects_renderer",
    "speedtree feature renderer",
)

INTERESTING_IMMEDIATES = {0xE, 0xE0, 0x1C0, 14, 224, 448}


def v2f(va: int, segments: list[dict]) -> int | None:
    for seg in segments:
        base = int(seg["virtual_address"], 16)
        size = int(seg["file_size"])
        if base <= va < base + size:
            return int(seg["absolute_file_offset"]) + va - base
    return None


def load_graph(path: Path) -> dict:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as fh:
        return json.load(fh)


def build_function_index(graph: dict):
    ranges = []
    by_entry = {}
    for fn in graph.get("functions", []):
        entry = int(fn["entry"], 16)
        by_entry[entry] = fn
        for row in fn.get("body_ranges", []):
            ranges.append((int(row["min"], 16), int(row["max"], 16) + 1, entry))
    ranges.sort()
    starts = [r[0] for r in ranges]
    return ranges, starts, by_entry


def owner_of(addr: int, ranges, starts, by_entry):
    i = bisect.bisect_right(starts, addr) - 1
    for j in range(max(0, i - 2), min(len(ranges), i + 3)):
        lo, hi, entry = ranges[j]
        if lo <= addr < hi:
            return by_entry.get(entry)
    return None


def function_callers(graph: dict) -> dict[int, list[int]]:
    callers: dict[int, list[int]] = {}
    for fn in graph.get("functions", []):
        src = int(fn["entry"], 16)
        for dst_s in fn.get("called_function_entries", []):
            dst = int(dst_s, 16)
            callers.setdefault(dst, []).append(src)
    return callers


def string_va_index(graph: dict) -> dict[int, str]:
    out = {}
    for row in graph.get("strings", []):
        try:
            out[int(row["address"], 16)] = row.get("text", "")
        except Exception:
            pass
    return out


def function_entry_index(graph: dict) -> dict[int, str]:
    return {int(row["entry"], 16): row["name"] for row in graph.get("functions", [])}


def data_window(raw: bytes, segments: list[dict], center_va: int, *,
                radius: int, function_entries: dict[int, str],
                string_vas: dict[int, str]) -> dict:
    start_va = max(0, center_va - radius)
    end_va = center_va + radius
    start_file = v2f(start_va, segments)
    end_file = v2f(end_va - 1, segments)
    if start_file is None or end_file is None:
        return {"center_va": center_va, "status": "UNMAPPED"}
    end_file += 1
    payload = raw[start_file:end_file]
    qwords = []
    for off in range(0, len(payload) - 7, 8):
        va = start_va + off
        value = struct.unpack_from("<Q", payload, off)[0]
        kind = None
        name = None
        if value in function_entries:
            kind = "exact_function_pointer"
            name = function_entries[value]
        elif value in string_vas:
            kind = "exact_string_pointer"
            name = string_vas[value]
        elif v2f(value, segments) is not None:
            kind = "mapped_pointer"
        if kind:
            qwords.append({
                "slot_va": va,
                "slot_va_hex": hex(va),
                "value": value,
                "value_hex": hex(value),
                "kind": kind,
                "name": name,
            })
    return {
        "center_va": center_va,
        "center_va_hex": hex(center_va),
        "start_va": start_va,
        "start_va_hex": hex(start_va),
        "end_va": end_va,
        "end_va_hex": hex(end_va),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "pointer_qwords": qwords,
        "hex": payload.hex(),
        "status": "EXACT_WINDOW",
    }


def executable_segments(segments: list[dict]) -> list[dict]:
    return [s for s in segments if s.get("executable") and int(s.get("file_size", 0)) > 0]


def scan_code_references(raw: bytes, segments: list[dict], target_vas: list[int],
                         ranges, starts, by_entry, *, radius: int) -> list[dict]:
    if not target_vas:
        return []
    lo_target = min(target_vas) - radius
    hi_target = max(target_vas) + radius
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    md.detail = True
    hits = []
    seen = set()
    for seg in executable_segments(segments):
        foff = int(seg["absolute_file_offset"])
        size = int(seg["file_size"])
        va0 = int(seg["virtual_address"], 16)
        blob = raw[foff:foff + size]
        for insn in md.disasm(blob, va0):
            refs = []
            for op in insn.operands:
                if op.type == X86_OP_MEM and op.mem.base == X86_REG_RIP:
                    target = insn.address + insn.size + op.mem.disp
                    if lo_target <= target <= hi_target:
                        refs.append(("rip_mem", target))
                elif op.type == X86_OP_IMM:
                    target = int(op.imm) & 0xFFFFFFFFFFFFFFFF
                    if lo_target <= target <= hi_target:
                        refs.append(("imm", target))
            for kind, target in refs:
                nearest = min(target_vas, key=lambda x: abs(x - target))
                if abs(nearest - target) > radius:
                    continue
                key = (insn.address, target, kind)
                if key in seen:
                    continue
                seen.add(key)
                owner = owner_of(insn.address, ranges, starts, by_entry)
                hits.append({
                    "instruction_va": insn.address,
                    "instruction_va_hex": hex(insn.address),
                    "mnemonic": insn.mnemonic,
                    "op_str": insn.op_str,
                    "reference_kind": kind,
                    "target_va": target,
                    "target_va_hex": hex(target),
                    "nearest_table_va": nearest,
                    "nearest_table_va_hex": hex(nearest),
                    "delta": target - nearest,
                    "function_entry": int(owner["entry"], 16) if owner else None,
                    "function_entry_hex": hex(int(owner["entry"], 16)) if owner else None,
                    "function_name": owner.get("name") if owner else None,
                })
    return hits


def disassemble_function(raw: bytes, segments: list[dict], fn: dict) -> list[dict]:
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    md.detail = True
    out = []
    for body in fn.get("body_ranges", []):
        lo = int(body["min"], 16)
        hi = int(body["max"], 16) + 1
        foff = v2f(lo, segments)
        if foff is None:
            continue
        blob = raw[foff:foff + (hi - lo)]
        for insn in md.disasm(blob, lo):
            imms = []
            mem_disps = []
            for op in insn.operands:
                if op.type == X86_OP_IMM:
                    imms.append(int(op.imm))
                elif op.type == X86_OP_MEM:
                    mem_disps.append(int(op.mem.disp))
            interesting = [
                value for value in imms + mem_disps
                if abs(value) in INTERESTING_IMMEDIATES
            ]
            out.append({
                "address": insn.address,
                "address_hex": hex(insn.address),
                "mnemonic": insn.mnemonic,
                "op_str": insn.op_str,
                "interesting_slot_like_values": interesting,
            })
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("executable", type=Path)
    ap.add_argument("--codegraph", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--table-radius", type=lambda x: int(x, 0), default=0x180)
    ap.add_argument("--xref-radius", type=lambda x: int(x, 0), default=0x200)
    args = ap.parse_args()

    raw = args.executable.read_bytes()
    header = parse_elf64_header(raw)
    if not header or not header.get("supported"):
        raise SystemExit("expected supported ELF64 eboot")
    segments = parse_elf64_program_headers(raw, header)
    graph = load_graph(args.codegraph)
    ranges, starts, by_entry = build_function_index(graph)
    callers = function_callers(graph)
    strings = string_va_index(graph)
    fentries = function_entry_index(graph)

    table_report = scan_label_tables(args.executable, LABELS, cluster_distance=0x400)
    terrain_hits = []
    target_vas = []
    for label in ("terrain_feature_renderer", "editor_terrain_tile_renderer", "?chunked_terrain"):
        row = table_report["labels"].get(label, {})
        for hit in row.get("pointer_hits", []):
            va = hit.get("reference_virtual_address")
            if va is not None:
                target_vas.append(int(va))
                terrain_hits.append(hit)

    windows = [
        data_window(
            raw, segments, va, radius=args.table_radius,
            function_entries=fentries, string_vas=strings,
        )
        for va in sorted(set(target_vas))
    ]

    code_refs = scan_code_references(
        raw, segments, sorted(set(target_vas)), ranges, starts, by_entry,
        radius=args.xref_radius,
    )
    candidate_entries = sorted({
        row["function_entry"] for row in code_refs if row["function_entry"] is not None
    })

    functions = []
    for entry in candidate_entries:
        fn = by_entry[entry]
        instructions = disassemble_function(raw, segments, fn)
        functions.append({
            "entry": entry,
            "entry_hex": hex(entry),
            "name": fn.get("name"),
            "prototype": fn.get("prototype"),
            "instruction_bytes_sha256": fn.get("instruction_bytes_sha256"),
            "mnemonic_sequence_sha256": fn.get("mnemonic_sequence_sha256"),
            "called_function_entries": fn.get("called_function_entries", []),
            "caller_entries": [hex(x) for x in sorted(callers.get(entry, []))],
            "slot_like_instruction_count": sum(
                bool(i["interesting_slot_like_values"]) for i in instructions
            ),
            "slot_like_instructions": [
                i for i in instructions if i["interesting_slot_like_values"]
            ],
            "instructions": instructions,
        })

    report = {
        "schema": "d1_executable_terrain_runtime_probe/v1",
        "status": "D1_TERRAIN_RUNTIME_PRODUCER_FRONTIER",
        "executable_sha256": hashlib.sha256(raw).hexdigest(),
        "codegraph_program": graph.get("program"),
        "labels": list(LABELS),
        "terrain_pointer_hits": terrain_hits,
        "terrain_pointer_hit_count": len(terrain_hits),
        "terrain_data_windows": windows,
        "code_references_to_terrain_table_neighborhoods": code_refs,
        "candidate_function_count": len(functions),
        "candidate_functions": functions,
        "t14_proof_boundary": (
            "This report discovers exact executable owners around terrain renderer "
            "metadata. Constants 14/0xE0/0x1C0 are observations only. T14 is not "
            "promoted as STerrain dyemap until a concrete producer path is traced "
            "from the terrain resource/dyemap value into the pixel resource table."
        ),
        "label_table_policy": table_report.get("policy"),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": report["status"],
        "terrain_pointer_hit_count": len(terrain_hits),
        "code_reference_count": len(code_refs),
        "candidate_function_count": len(functions),
        "candidates": [
            {
                "entry": f["entry_hex"],
                "slot_like_instruction_count": f["slot_like_instruction_count"],
                "calls": len(f["called_function_entries"]),
                "callers": len(f["caller_entries"]),
            }
            for f in functions[:32]
        ],
        "output": str(args.out),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
