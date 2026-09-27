#!/usr/bin/env python3
"""Find candidate x86-64 RIP-relative LEA references to exact ELF strings.

This is an executable evidence probe, not a function-boundary/decompiler pass.
Every result is namespaced by the complete executable SHA-256 and records both
file and ELF virtual addresses. Byte-pattern hits require disassembly review
before being promoted to an instruction or code-to-asset relationship.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

from d1_executable_probe import parse_elf64_header, parse_elf64_program_headers


def file_to_virtual(offset: int, segments: list[dict]) -> int | None:
    for segment in segments:
        base = segment["absolute_file_offset"]
        if base <= offset < base + segment["file_size"]:
            return int(segment["virtual_address"], 16) + offset - base
    return None


def probe(path: Path, terms: list[str]) -> dict:
    raw = path.read_bytes()
    header = parse_elf64_header(raw)
    if header is None or not header.get("supported") or header["machine_name"] != "x86_64":
        raise ValueError("expected a plain x86-64 ELF64 executable")
    segments = parse_elf64_program_headers(raw, header)
    rows = {}
    by_va = {}
    for term in terms:
        needle = term.encode("utf-8")
        matches = []
        start = 0
        while (at := raw.find(needle, start)) >= 0:
            va = file_to_virtual(at, segments)
            if va is not None:
                matches.append({"file_offset": at, "virtual_address": va, "candidate_lea_xrefs": []})
            start = at + 1
        rows[term] = matches
        for match in matches:
            by_va.setdefault(match["virtual_address"], []).append(match)
    # Only REX.W LEA RIP+disp32 patterns. This is a candidate scan rather than
    # a full instruction decoder, so a false hit inside another instruction is
    # possible and retained as such.
    for segment in segments:
        if not segment["executable"]:
            continue
        start = segment["absolute_file_offset"]
        end = min(len(raw), start + segment["file_size"])
        data = raw[start:end]
        base_va = int(segment["virtual_address"], 16)
        for match in re.finditer(b"[\\x48\\x4c]\\x8d", data):
            index = match.start()
            if index + 7 > len(data) or data[index + 2] & 0xC7 != 0x05:
                continue
            displacement = struct.unpack_from("<i", data, index + 3)[0]
            target = base_va + index + 7 + displacement
            for row in by_va.get(target, []):
                row["candidate_lea_xrefs"].append({
                    "file_offset": start + index,
                    "virtual_address": base_va + index,
                    "target_virtual_address": target,
                    "status": "BYTE_PATTERN_CANDIDATE_REQUIRES_DISASSEMBLY",
                })
    return {
        "schema": "d1_elf_rip_string_xrefs/v1",
        "executable_sha256": hashlib.sha256(raw).hexdigest(),
        "file_size": len(raw),
        "elf_entry": header["entry"],
        "terms": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("executable", type=Path)
    parser.add_argument("--string", dest="terms", action="append", required=True)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()
    encoded = json.dumps(probe(args.executable, args.terms), indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded)
    else:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
