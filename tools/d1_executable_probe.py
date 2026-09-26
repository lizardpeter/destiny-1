#!/usr/bin/env python3
"""Fingerprint and identify Destiny 1 PS4 executable artifacts.

This tool does not decrypt retail PS4 content. It records identity/provenance for
an already-available executable artifact so later disassembly and graph evidence
remain build-specific.
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


def probe(path: Path) -> dict[str, Any]:
    with path.open("rb") as fh:
        prefix = fh.read(0x40)
    digest = sha256_file(path)
    return {
        "schema": "d1_executable_probe/v1",
        "path": str(path),
        "file_size": path.stat().st_size,
        "sha256": digest,
        "container": classify(prefix),
        "self_header": parse_self_header(prefix),
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("executable", type=Path)
    parser.add_argument("-o", "--out", type=Path)
    args = parser.parse_args()

    report = probe(args.executable)
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
