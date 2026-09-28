#!/usr/bin/env python3
"""Extract exact Destiny 1 retail fixed-function selector-table records.

This tool is deliberately narrow and evidence-preserving. It accepts only the
owner-provided CUSA00219 executable fingerprint used by the renderer RE corpus
and reads selector records from table addresses already proven by exact D1 code:

* rasterizer/clip-cull: 0x15D2390, 16-byte records, exactly 9 records;
* depth-bias/polygon-offset: 0x15D2420, 12-byte records.

The output preserves raw bytes, little-endian dwords and float reinterpretations.
It does NOT name individual record fields or translate them to Vulkan state.
Those promotions require the corresponding helper/packet dataflow proof.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

from d1_executable_code_windows import va_to_file
from d1_executable_probe import parse_elf64_header, parse_elf64_program_headers

EXACT_SHA256 = "672f03411c0503dfbcda804cbb9fb27cdd9a8d73a8bcb71bf0c4f688073b0833"
EXACT_SIZE = 29_249_016

RASTERIZER_TABLE_VA = 0x15D2390
RASTERIZER_STRIDE = 0x10
RASTERIZER_COUNT = 9

DEPTH_BIAS_TABLE_VA = 0x15D2420
DEPTH_BIAS_STRIDE = 0x0C

# These defaults are not guesses about meaning. They are the low-seven selector
# indices present in executable-proven pass vectors:
#   rasterizer: 0x81 / 0x82 -> 1 / 2
#   depth-bias: 0x81 -> 1
DEFAULT_RASTERIZER_INDICES = (1, 2)
DEFAULT_DEPTH_BIAS_INDICES = (1,)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decode_record(raw: bytes, *, index: int, va: int) -> dict:
    if len(raw) % 4:
        raise ValueError("fixed-function record length must be dword-aligned")
    dwords = list(struct.unpack("<" + "I" * (len(raw) // 4), raw))
    floats = list(struct.unpack("<" + "f" * (len(raw) // 4), raw))
    return {
        "selector_index": index,
        "virtual_address": f"0x{va:X}",
        "size": len(raw),
        "raw_hex": raw.hex().upper(),
        "dwords_u32": dwords,
        "dwords_hex": [f"{x:08X}" for x in dwords],
        "float_reinterpretation": floats,
    }


def read_record(
    exe: bytes,
    segments: list[dict],
    *,
    table_va: int,
    stride: int,
    index: int,
) -> dict:
    if index < 0 or index > 0x7F:
        raise ValueError(f"selector index {index} outside low-seven-bit range")
    va = table_va + index * stride
    off = va_to_file(va, segments)
    if off is None:
        raise ValueError(f"selector record VA 0x{va:X} is not file-backed")
    raw = exe[off : off + stride]
    if len(raw) != stride:
        raise ValueError(
            f"selector record VA 0x{va:X} truncated: {len(raw)} != {stride}"
        )
    row = decode_record(raw, index=index, va=va)
    row["file_offset"] = off
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("executable", type=Path)
    ap.add_argument(
        "--rasterizer-index",
        action="append",
        type=lambda x: int(x, 0),
        help="low-seven-bit rasterizer selector index; defaults to exact observed 1 and 2",
    )
    ap.add_argument(
        "--depth-bias-index",
        action="append",
        type=lambda x: int(x, 0),
        help="low-seven-bit depth-bias selector index; defaults to exact observed 1",
    )
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    exe = a.executable.read_bytes()
    sha = hashlib.sha256(exe).hexdigest()
    violations: list[str] = []
    if len(exe) != EXACT_SIZE:
        violations.append(f"size:{len(exe)}!={EXACT_SIZE}")
    if sha != EXACT_SHA256:
        violations.append(f"sha256:{sha}!={EXACT_SHA256}")
    if violations:
        raise ValueError(
            "refusing non-pinned executable for exact D1 fixed-function tables: "
            + "; ".join(violations)
        )

    header = parse_elf64_header(exe)
    if header is None or not header.get("supported"):
        raise ValueError("expected the pinned executable to be a supported ELF64")
    segments = parse_elf64_program_headers(exe, header)

    raster_indices = sorted(
        set(a.rasterizer_index or DEFAULT_RASTERIZER_INDICES)
    )
    depth_bias_indices = sorted(
        set(a.depth_bias_index or DEFAULT_DEPTH_BIAS_INDICES)
    )

    if any(index >= RASTERIZER_COUNT for index in raster_indices):
        raise ValueError(
            f"rasterizer selector exceeds exact 9-record table: {raster_indices}"
        )

    rasterizer = [
        read_record(
            exe,
            segments,
            table_va=RASTERIZER_TABLE_VA,
            stride=RASTERIZER_STRIDE,
            index=index,
        )
        for index in raster_indices
    ]
    depth_bias = [
        read_record(
            exe,
            segments,
            table_va=DEPTH_BIAS_TABLE_VA,
            stride=DEPTH_BIAS_STRIDE,
            index=index,
        )
        for index in depth_bias_indices
    ]

    out = {
        "schema": "d1_executable_fixed_function_table_extract/v1",
        "status": "D1_EXACT_FIXED_FUNCTION_SELECTOR_RECORDS_EXTRACTED",
        "executable": {
            "sha256": sha,
            "size": len(exe),
        },
        "tables": {
            "rasterizer_clip_cull": {
                "table_va": f"0x{RASTERIZER_TABLE_VA:X}",
                "record_stride": RASTERIZER_STRIDE,
                "record_count_proven": RASTERIZER_COUNT,
                "helper_va": "0x7DE590",
                "emitted_context_registers": [
                    "0x204 PA_CL_CLIP_CNTL",
                    "0x205 PA_SU_SC_MODE_CNTL",
                ],
                "records": rasterizer,
            },
            "depth_bias_polygon_offset": {
                "table_va": f"0x{DEPTH_BIAS_TABLE_VA:X}",
                "record_stride": DEPTH_BIAS_STRIDE,
                "record_count_proven": None,
                "helper_va": "0x7DE640",
                "emitted_context_registers": [
                    "0x2E0 PA_SU_POLY_OFFSET_FRONT_SCALE",
                    "0x2E1 PA_SU_POLY_OFFSET_FRONT_OFFSET",
                    "0x2E2 PA_SU_POLY_OFFSET_BACK_SCALE",
                    "0x2E3 PA_SU_POLY_OFFSET_BACK_OFFSET",
                ],
                "records": depth_bias,
            },
        },
        "policy": (
            "Raw exact-build selector records only. Dword and float views are "
            "reinterpretations, not semantic field assignments. Vulkan/Orbis "
            "state promotion requires independent helper/packet dataflow closure."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": out["status"],
                "rasterizer_indices": raster_indices,
                "depth_bias_indices": depth_bias_indices,
                "output": str(a.output),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
