#!/usr/bin/env python3
"""Decode D1 PS4 type 32/subtype 9 VS/DS-family shader headers.

The original D1 decoder promoted every 32:9 -> 1:9 pair to VertexShader from
Tiger subtype alone.  The exact current-retail corpus disproves that assumption:
OrbShdr identifies both VertexShader and DomainShader programs in this family.

Public GNM structure evidence supplies the stage-neutral layout used here:
``GnmShaderBinaryInfo`` distinguishes ``VS_VS`` from ``DS_VS`` while a domain
shader that outputs vertices uses the same ``GnmVsShader`` structure as a normal
vertex shader.  Destiny wraps that GnmVsShader at byte +0x14.

Retail corpus invariants are kept separate from public GNM structure facts:
* VertexShader records repeat GnmShaderCommonData.shadersize at D1 wrapper +0x04.
* DomainShader records have zero D1 wrapper words at +0x00 and +0x04.
* Both stages carry an exact GnmShaderCommonData.shadersize equal to the end of
  the 28-byte OrbShdr ShaderBinaryInfo and an exact input-usage-slot count.

No semantic names are invented for native vertex-link semantics.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_ps4_shader_binary_probe import find_footer, parse_binary_info
from d1_ps4_vertex_shader_header import (
    parse_input_usage_slot,
    parse_vertex_input_semantic,
    parse_vertex_export_semantic,
)

FAMILY_HEADER_TYPE = 32
FAMILY_HEADER_SUBTYPE = 9
FAMILY_NATIVE_TYPE = 1
FAMILY_NATIVE_SUBTYPE = 9
GNMX_BASE = 0x14
GNMX_USAGE_BASE = 0x3C
ALLOWED_ORB_STAGES = {"VertexShader", "DomainShader"}


def u32(b: bytes, o: int) -> int:
    if o < 0 or o + 4 > len(b):
        raise ValueError((o, len(b)))
    return struct.unpack_from("<I", b, o)[0]


def parse_header(
    b: bytes,
    native_payload: bytes | None = None,
    expected_stage: str | None = None,
) -> dict:
    if len(b) < GNMX_USAGE_BASE:
        raise ValueError(f"VS/DS family header only {len(b)} bytes")
    if expected_stage is not None and expected_stage not in ALLOWED_ORB_STAGES:
        raise ValueError(f"unsupported VS/DS family stage {expected_stage!r}")

    wrapper0 = u32(b, 0x00)
    wrapper_size = u32(b, 0x04)
    common0 = u32(b, GNMX_BASE)
    shader_size = common0 & 0x7FFFFF
    uses_srt = bool((common0 >> 23) & 1)
    usage_count = (common0 >> 24) & 0xFF
    embedded_cb_dqwords, scratch_dw = struct.unpack_from("<HH", b, 0x18)

    input_count, export_count, gs_mode, fetch_control = struct.unpack_from("<4B", b, 0x38)
    usage_start = GNMX_USAGE_BASE
    input_start = usage_start + usage_count * 4
    export_start = input_start + input_count * 4
    known_end = export_start + export_count * 2
    if known_end > len(b):
        raise ValueError(
            f"header tables exceed payload: usage={usage_count} input={input_count} "
            f"export={export_count} known_end=0x{known_end:X} size=0x{len(b):X}"
        )

    inputs = [
        parse_vertex_input_semantic(b, input_start + i * 4, i)
        for i in range(input_count)
    ]
    exports = [
        parse_vertex_export_semantic(b, export_start + i * 2, i)
        for i in range(export_count)
    ]

    stage_regs = {
        "spi_shader_pgm_lo_vs": f"{u32(b, 0x1C):08X}",
        "spi_shader_pgm_hi_vs": f"{u32(b, 0x20):08X}",
        "spi_shader_pgm_rsrc1_vs": f"{u32(b, 0x24):08X}",
        "spi_shader_pgm_rsrc2_vs": f"{u32(b, 0x28):08X}",
        "spi_vs_out_config": f"{u32(b, 0x2C):08X}",
        "spi_shader_pos_format": f"{u32(b, 0x30):08X}",
        "pa_cl_vs_out_cntl": f"{u32(b, 0x34):08X}",
    }

    row = {
        "schema": "d1_ps4_vs_ds_shader_header/v1",
        "header_size": len(b),
        "family": {
            "header_type_subtype": "32:9",
            "native_type_subtype": "1:9",
            "public_gnm_layout": "GnmVsShader",
            "public_gnm_binary_types": ["VS_VS", "DS_VS"],
        },
        "expected_orb_stage": expected_stage,
        "tiger_wrapper": {
            "word0": f"{wrapper0:08X}",
            "shader_size_repeat": wrapper_size,
            "bytes_08_13_hex": b[0x08:0x14].hex(),
        },
        "gnm_vs_shader": {
            "base_offset": GNMX_BASE,
            "shader_size": shader_size,
            "uses_srt": uses_srt,
            "num_input_usage_slots": usage_count,
            "embedded_constant_buffer_size_dqwords": embedded_cb_dqwords,
            "scratch_size_dwords_per_thread": scratch_dw,
            "stage_registers": stage_regs,
            "num_input_semantics": input_count,
            "num_export_semantics": export_count,
            "gs_mode_or_num_input_semantics_cs": gs_mode,
            "fetch_control": fetch_control,
            "vertex_offset_user_register": fetch_control & 0x0F,
            "instance_offset_user_register": (fetch_control >> 4) & 0x0F,
            "input_usage_slots": [
                parse_input_usage_slot(b, usage_start + i * 4, i)
                for i in range(usage_count)
            ],
            "input_semantics": inputs,
            "export_semantics": exports,
        },
        "table_offsets": {
            "usage_start": usage_start,
            "input_start": input_start,
            "export_start": export_start,
            "known_end": known_end,
        },
        "trailing_bytes_hex": b[known_end:].hex(),
        "checks": {
            "tables_in_bounds": known_end <= len(b),
            "input_semantic_ids_unique": len({x["semantic"] for x in inputs}) == input_count,
            "input_semantic_byte3_zero": all(x["byte3"] == 0 for x in inputs),
            "vertex_wrapper_size_repeat_matches_common": wrapper_size == shader_size,
            "domain_wrapper_words_zero": wrapper0 == 0 and wrapper_size == 0,
        },
        "source_boundary": {
            "shared_gnm_vs_shader_layout": "PUBLIC_SOURCE_BACKED",
            "orb_stage_identity": "NATIVE_SHADER_BINARY_INFO",
            "d1_outer_wrapper_stage_invariants": "EXACT_RETAIL_CORPUS",
        },
    }

    if native_payload is not None:
        footer, loc = find_footer(native_payload)
        nc = {"orbshdr_locator": loc, "resolved": footer is not None}
        if footer is not None:
            info = parse_binary_info(native_payload, footer)
            nc.update({
                "binary_info": info,
                "orb_stage_allowed_for_family": info["stage"] in ALLOWED_ORB_STAGES,
                "stage_matches_expected": expected_stage is None or info["stage"] == expected_stage,
                "gnm_shader_size_matches_orbshdr_end": shader_size == footer + 28,
                "usage_count_matches_orbshdr": usage_count == info["num_input_usage_slots"],
            })
        row["native_checks"] = nc

    if expected_stage == "VertexShader":
        row["stage_wrapper_check"] = {
            "name": "vertex_wrapper_size_repeat_matches_common",
            "exact": wrapper_size == shader_size,
        }
    elif expected_stage == "DomainShader":
        row["stage_wrapper_check"] = {
            "name": "domain_wrapper_words_zero",
            "exact": wrapper0 == 0 and wrapper_size == 0,
        }
    return row


def self_test() -> None:
    # Synthetic GnmVsShader-shaped D1 wrapper. Native-byte integration is exercised
    # by the retail corpus reclassifier rather than faking an OrbShdr payload here.
    b = bytearray(0x48)
    shader_size = 0x234
    usage_count = 1
    struct.pack_into("<I", b, 0x14, shader_size | (usage_count << 24))
    struct.pack_into("<HH", b, 0x18, 0, 0)
    b[0x38:0x3C] = bytes([1, 1, 0, 0])
    b[0x3C:0x40] = bytes([0x13, 0, 4, 0])
    b[0x40:0x44] = bytes([3, 2, 4, 0])
    b[0x44:0x46] = bytes([3, 1])

    struct.pack_into("<I", b, 0x04, shader_size)
    vs = parse_header(bytes(b), expected_stage="VertexShader")
    assert vs["stage_wrapper_check"]["exact"]
    assert vs["gnm_vs_shader"]["num_input_usage_slots"] == 1
    assert vs["table_offsets"]["known_end"] == 0x46

    struct.pack_into("<I", b, 0x04, 0)
    ds = parse_header(bytes(b), expected_stage="DomainShader")
    assert ds["stage_wrapper_check"]["exact"]
    assert ds["family"]["public_gnm_layout"] == "GnmVsShader"
    print("D1_PS4_VS_DS_SHADER_HEADER_SELF_TEST_OK")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("header", type=Path, nargs="?")
    ap.add_argument("--native", type=Path)
    ap.add_argument("--stage", choices=sorted(ALLOWED_ORB_STAGES))
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("-o", "--output", type=Path)
    a = ap.parse_args()
    if a.self_test:
        self_test()
        return 0
    if a.header is None:
        ap.error("header is required unless --self-test is used")
    out = parse_header(
        a.header.read_bytes(),
        a.native.read_bytes() if a.native else None,
        a.stage,
    )
    text = json.dumps(out, indent=2) + "\n"
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(text)
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
