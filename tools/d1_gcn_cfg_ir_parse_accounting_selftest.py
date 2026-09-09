#!/usr/bin/env python3
"""Deterministic self-test for fail-closed CLRX native-line parse accounting."""
from __future__ import annotations

import tempfile
from pathlib import Path

import d1_gcn_cfg_ir_v2 as structural


def parse_text(text: str):
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "fixture.s"
        path.write_text(text)
        return structural.parse_accounted(path)


def expect_value_error(text: str, needle: str) -> None:
    try:
        parse_text(text)
    except ValueError as exc:
        if needle not in str(exc):
            raise AssertionError(f"expected {needle!r} in {exc!r}") from exc
    else:
        raise AssertionError("malformed address-bearing line was silently accepted")


def main() -> int:
    valid = """\
; non-native CLRX text remains ignorable at this layer
.Lentry:
/*000000000000: 7E000280*/ v_mov_b32 v0, v1
/*000000000004: D1190000 00020501*/ v_add_i32 v0, vcc, v1, v2
.Ldone:
/*00000000000C: BF810000*/ s_endpgm
"""
    ins, accounting = parse_text(valid)
    assert accounting["status"] == structural.PARSE_ACCOUNTING_STATUS
    assert accounting["native_instruction_line_count"] == 3
    assert accounting["ir_instruction_count"] == 3
    assert accounting["encoded_byte_count"] == 16
    assert accounting["unaccounted_native_instruction_line_count"] == 0
    assert accounting["duplicate_ir_instruction_count"] == 0
    assert [x["index"] for x in ins] == [0, 1, 2]
    assert [x["address"] for x in ins] == [0, 4, 12]
    assert [x["byte_size"] for x in ins] == [4, 8, 4]
    assert ins[0]["encoding_words"] == ["7e000280"]
    assert ins[1]["encoding_words"] == ["d1190000", "00020501"]
    assert ins[2]["encoding_words"] == ["bf810000"]
    assert ins[0]["labels"] == [".Lentry"]
    assert ins[2]["labels"] == [".Ldone"]

    expect_value_error(
        "/*000000000000: BF81000*/ s_endpgm\n",
        "invalid CLRX encoding word",
    )
    expect_value_error(
        "/*000000000000: BF810000*/\n",
        "has no instruction text",
    )
    expect_value_error(
        "/*000000000000: GGGGGGGG*/ s_endpgm\n",
        "invalid CLRX encoding word",
    )

    print(
        "D1_GCN_STRUCTURAL_PARSE_ACCOUNTING_SELFTEST_EXACT",
        {
            "instructions": len(ins),
            "encoded_bytes": accounting["encoded_byte_count"],
            "widths": [x["byte_size"] for x in ins],
            "negative_cases": 3,
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
