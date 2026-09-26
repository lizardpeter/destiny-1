#!/usr/bin/env python3
"""Fingerprint and structurally inspect Destiny 1 PS4 executable artifacts.

This tool does not decrypt retail PS4 content. It records identity/provenance and
non-destructive structural evidence for an already-available SELF/ELF so later
disassembly and graph evidence remain exact-build specific.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

PS4_SELF_MAGIC = bytes.fromhex("4f153d1d")
ELF_MAGIC = b"\x7fELF"
ELF_SCAN_LIMIT = 0x10000

KNOWN_BUILDS = {
    "7271fcb926401df8defb126cb8eb2b247134138b81e401bbacb2ab60791b795": {
        "game": "Destiny 1",
        "platform": "PS4",
        "title_id": "CUSA00219",
        "app_version": "01.29",
        "artifact": "decrypted_eboot",
        "evidence_state": "publicly_reported_fingerprint",
    }
}

GRAPHICS_HEARTBEAT_CODE_OFFSET = 0xFAAF4

ELF_MACHINE_NAMES = {
    0x3E: "x86_64",
}

PT_NAMES = {
    0: "PT_NULL",
    1: "PT_LOAD",
    2: "PT_DYNAMIC",
    3: "PT_INTERP",
    4: "PT_NOTE",
    5: "PT_SHLIB",
    6: "PT_PHDR",
    7: "PT_TLS",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def classify(prefix: bytes) -> str:
    if prefix.startswith(PS4_SELF_MAGIC):
        return "ps4_self"
    if prefix.startswith(ELF_MAGIC):
        return "elf"
    return "unknown"


def parse_self_header(prefix: bytes) -> dict[str, Any] | None:
    if len(prefix) < 0x1C or not prefix.startswith(PS4_SELF_MAGIC):
        return None
    version, mode, endian, attributes = prefix[4:8]
    key_type = struct.unpack_from("<I", prefix, 8)[0]
    header_size, metadata_size = struct.unpack_from("<HH", prefix, 12)
    declared_file_size = struct.unpack_from("<Q", prefix, 16)[0]
    entry_count, flags = struct.unpack_from("<HH", prefix, 24)
    return {
        "version": version,
        "mode": mode,
        "endian": endian,
        "attributes": attributes,
        "key_type": key_type,
        "header_size": header_size,
        "metadata_size": metadata_size,
        "declared_file_size": declared_file_size,
        "entry_count": entry_count,
        "flags": flags,
    }


def find_embedded_elf(data: bytes) -> int | None:
    if data.startswith(ELF_MAGIC):
        return 0
    offset = data.find(ELF_MAGIC)
    return offset if offset >= 0 else None


def _elf_endian(ident: bytes) -> str:
    if len(ident) < 6:
        raise ValueError("truncated ELF ident")
    if ident[5] == 1:
        return "<"
    if ident[5] == 2:
        return ">"
    raise ValueError(f"unsupported ELF data encoding {ident[5]}")


def parse_elf64_header(data: bytes, base_offset: int = 0) -> dict[str, Any] | None:
    if len(data) < base_offset + 64 or data[base_offset:base_offset + 4] != ELF_MAGIC:
        return None

    ident = data[base_offset:base_offset + 16]
    if ident[4] != 2:
        return {
            "offset": base_offset,
            "class": ident[4],
            "supported": False,
            "reason": "only ELF64 is structurally decoded",
        }

    endian = _elf_endian(ident)
    values = struct.unpack_from(endian + "HHIQQQIHHHHHH", data, base_offset + 16)
    (
        e_type,
        e_machine,
        e_version,
        e_entry,
        e_phoff,
        e_shoff,
        e_flags,
        e_ehsize,
        e_phentsize,
        e_phnum,
        e_shentsize,
        e_shnum,
        e_shstrndx,
    ) = values

    return {
        "offset": base_offset,
        "class": 64,
        "endianness": "little" if endian == "<" else "big",
        "type": e_type,
        "machine": e_machine,
        "machine_name": ELF_MACHINE_NAMES.get(e_machine, f"0x{e_machine:X}"),
        "version": e_version,
        "entry": f"0x{e_entry:X}",
        "program_header_offset": e_phoff,
        "section_header_offset": e_shoff,
        "flags": e_flags,
        "header_size": e_ehsize,
        "program_header_entry_size": e_phentsize,
        "program_header_count": e_phnum,
        "section_header_entry_size": e_shentsize,
        "section_header_count": e_shnum,
        "section_name_index": e_shstrndx,
        "supported": True,
    }


def parse_elf64_program_headers(
    data: bytes, elf_header: dict[str, Any]
) -> list[dict[str, Any]]:
    if not elf_header.get("supported"):
        return []

    base = int(elf_header["offset"])
    phoff = int(elf_header["program_header_offset"])
    phentsize = int(elf_header["program_header_entry_size"])
    phnum = int(elf_header["program_header_count"])
    endian = "<" if elf_header["endianness"] == "little" else ">"

    if phentsize < 56:
        return []

    out: list[dict[str, Any]] = []
    for index in range(phnum):
        offset = base + phoff + index * phentsize
        if offset + 56 > len(data):
            break
        (
            p_type,
            p_flags,
            p_offset,
            p_vaddr,
            p_paddr,
            p_filesz,
            p_memsz,
            p_align,
        ) = struct.unpack_from(endian + "IIQQQQQQ", data, offset)
        out.append(
            {
                "index": index,
                "type": p_type,
                "type_name": PT_NAMES.get(p_type, f"0x{p_type:X}"),
                "flags": p_flags,
                "readable": bool(p_flags & 4),
                "writable": bool(p_flags & 2),
                "executable": bool(p_flags & 1),
                "file_offset": p_offset,
                "absolute_file_offset": base + p_offset,
                "virtual_address": f"0x{p_vaddr:X}",
                "physical_address": f"0x{p_paddr:X}",
                "file_size": p_filesz,
                "memory_size": p_memsz,
                "alignment": p_align,
            }
        )
    return out


def printable_ascii_strings(
    data: bytes, min_length: int = 5
) -> list[dict[str, Any]]:
    if min_length < 1:
        raise ValueError("min_length must be >= 1")

    out: list[dict[str, Any]] = []
    start: int | None = None
    for index, byte in enumerate(data + b"\x00"):
        printable = 0x20 <= byte <= 0x7E or byte in (0x09,)
        if printable and start is None:
            start = index
        elif not printable and start is not None:
            if index - start >= min_length:
                raw = data[start:index]
                out.append(
                    {
                        "file_offset": start,
                        "length": len(raw),
                        "text": raw.decode("ascii"),
                    }
                )
            start = None
    return out


def probe(path: Path, include_strings: bool = False, min_string_length: int = 5) -> dict[str, Any]:
    raw = path.read_bytes()
    prefix = raw[:ELF_SCAN_LIMIT]
    digest = hashlib.sha256(raw).hexdigest()
    elf_offset = find_embedded_elf(prefix)
    elf_header = parse_elf64_header(raw, elf_offset) if elf_offset is not None else None
    program_headers = (
        parse_elf64_program_headers(raw, elf_header) if elf_header is not None else []
    )

    report: dict[str, Any] = {
        "schema": "d1_executable_probe/v2",
        "path": str(path),
        "file_size": len(raw),
        "sha256": digest,
        "container": classify(prefix),
        "self_header": parse_self_header(prefix),
        "embedded_elf_offset": elf_offset,
        "elf_header": elf_header,
        "program_headers": program_headers,
        "executable_segments": [
            segment for segment in program_headers if segment["executable"]
        ],
        "known_build": KNOWN_BUILDS.get(digest),
        "research_anchors": {
            "graphics_heartbeat_code_offset": f"0x{GRAPHICS_HEARTBEAT_CODE_OFFSET:X}",
            "note": (
                "Public CUSA00219 runtime reports associate this code-offset "
                "neighborhood with the Graphics Heartbeat failure path. Treat "
                "it as build evidence, not a recovered function name."
            ),
        },
    }

    if include_strings:
        strings = printable_ascii_strings(raw, min_string_length)
        report["strings"] = strings
        report["string_count"] = len(strings)
        report["string_min_length"] = min_string_length

    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("executable", type=Path)
    parser.add_argument("-o", "--out", type=Path)
    parser.add_argument(
        "--strings",
        action="store_true",
        help="include offset-stable printable ASCII strings in the JSON report",
    )
    parser.add_argument("--min-string-length", type=int, default=5)
    args = parser.parse_args()

    report = probe(args.executable, args.strings, args.min_string_length)
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
