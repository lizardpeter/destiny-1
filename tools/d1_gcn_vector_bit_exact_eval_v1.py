#!/usr/bin/env python3
"""Bit-exact executable helpers for the source-closed Destiny 1 GFX7 integer VALU subset.

Inputs and outputs are architectural bit patterns, not host-language signed values.  The
public evaluate() entry point always returns one tuple element per architectural VGPR result
component.  This module deliberately implements only the 12 opcodes already frozen as
BIT_EXACT_REPLAY_READY by d1_gcn_vector_formula_semantics_v1.
"""
from __future__ import annotations

import struct
from typing import Iterable

import d1_gcn_vector_formula_semantics_v1 as sem

U32_MASK = 0xFFFF_FFFF
U64_MASK = 0xFFFF_FFFF_FFFF_FFFF


def u32(x: int) -> int:
    return int(x) & U32_MASK


def u64(x: int) -> int:
    return int(x) & U64_MASK


def i32(x: int) -> int:
    x = u32(x)
    return x - (1 << 32) if x & 0x8000_0000 else x


def signext24(x: int) -> int:
    x = int(x) & 0x00FF_FFFF
    return x - (1 << 24) if x & 0x0080_0000 else x


def literal_u32(token: str) -> int:
    """Convert an exact CLRX scalar literal token to its 32-bit architectural bit pattern."""
    t = token.strip()
    if not t:
        raise ValueError("empty literal token")
    if t.lower().startswith(("0x", "+0x", "-0x")):
        return u32(int(t, 0))
    if any(c in t.lower() for c in (".", "e")):
        return struct.unpack("<I", struct.pack("<f", float(t)))[0]
    return u32(int(t, 10))


def evaluate(opcode: str, sources: Iterable[int]) -> tuple[int, ...]:
    s = tuple(int(x) for x in sources)
    if opcode not in EVALUATOR_OPCODES:
        raise KeyError(f"opcode is not bit-exact executable here: {opcode}")

    if opcode == "v_and_b32":
        if len(s) != 2: raise ValueError("v_and_b32 expects 2 sources")
        return (u32(s[0]) & u32(s[1]),)
    if opcode == "v_or_b32":
        if len(s) != 2: raise ValueError("v_or_b32 expects 2 sources")
        return (u32(s[0]) | u32(s[1]),)
    if opcode == "v_lshlrev_b32":
        if len(s) != 2: raise ValueError("v_lshlrev_b32 expects 2 sources")
        return (u32(u32(s[1]) << (u32(s[0]) & 0x1F)),)
    if opcode == "v_lshrrev_b32":
        if len(s) != 2: raise ValueError("v_lshrrev_b32 expects 2 sources")
        return (u32(s[1]) >> (u32(s[0]) & 0x1F),)
    if opcode == "v_lshl_b64":
        if len(s) != 2: raise ValueError("v_lshl_b64 expects 2 sources")
        r = u64(u64(s[0]) << (u32(s[1]) & 0x3F))
        return (u32(r), u32(r >> 32))
    if opcode == "v_max_i32":
        if len(s) != 2: raise ValueError("v_max_i32 expects 2 sources")
        return (u32(s[0] if i32(s[0]) >= i32(s[1]) else s[1]),)
    if opcode == "v_mov_b32":
        if len(s) != 1: raise ValueError("v_mov_b32 expects 1 source")
        return (u32(s[0]),)
    if opcode == "v_mul_hi_u32":
        if len(s) != 2: raise ValueError("v_mul_hi_u32 expects 2 sources")
        return (u32((u32(s[0]) * u32(s[1])) >> 32),)
    if opcode == "v_mul_i32_i24":
        if len(s) != 2: raise ValueError("v_mul_i32_i24 expects 2 sources")
        return (u32(signext24(s[0]) * signext24(s[1])),)
    if opcode == "v_mul_lo_i32":
        if len(s) != 2: raise ValueError("v_mul_lo_i32 expects 2 sources")
        return (u32(i32(s[0]) * i32(s[1])),)
    if opcode == "v_mul_lo_u32":
        if len(s) != 2: raise ValueError("v_mul_lo_u32 expects 2 sources")
        return (u32(u32(s[0]) * u32(s[1])),)
    if opcode == "v_mad_i32_i24":
        if len(s) != 3: raise ValueError("v_mad_i32_i24 expects 3 sources")
        return (u32(signext24(s[0]) * signext24(s[1]) + i32(s[2])),)
    raise AssertionError(opcode)


EVALUATOR_OPCODES = frozenset({
    "v_and_b32", "v_lshl_b64", "v_lshlrev_b32", "v_lshrrev_b32",
    "v_mad_i32_i24", "v_max_i32", "v_mov_b32", "v_mul_hi_u32",
    "v_mul_i32_i24", "v_mul_lo_i32", "v_mul_lo_u32", "v_or_b32",
})


def validate() -> list[str]:
    problems: list[str] = []
    if EVALUATOR_OPCODES != frozenset(sem.BIT_EXACT_REPLAY_READY):
        problems.append(
            f"evaluator_surface_mismatch:missing={sorted(set(sem.BIT_EXACT_REPLAY_READY)-set(EVALUATOR_OPCODES))}:"
            f"extra={sorted(set(EVALUATOR_OPCODES)-set(sem.BIT_EXACT_REPLAY_READY))}"
        )
    vectors = [
        ("v_and_b32", (0xFFFF0000, 0x0F0F0F0F), (0x0F0F0000,)),
        ("v_or_b32", (0x80000000, 1), (0x80000001,)),
        ("v_lshlrev_b32", (31, 1), (0x80000000,)),
        ("v_lshrrev_b32", (31, 0x80000000), (1,)),
        ("v_lshl_b64", (1, 63), (0, 0x80000000)),
        ("v_max_i32", (0xFFFFFFFF, 0), (0,)),
        ("v_mov_b32", (0xDEADBEEF,), (0xDEADBEEF,)),
        ("v_mul_hi_u32", (0xFFFFFFFF, 0xFFFFFFFF), (0xFFFFFFFE,)),
        ("v_mul_i32_i24", (0x00FFFFFF, 2), (0xFFFFFFFE,)),
        ("v_mul_lo_i32", (0xFFFFFFFF, 2), (0xFFFFFFFE,)),
        ("v_mul_lo_u32", (0xFFFFFFFF, 2), (0xFFFFFFFE,)),
        ("v_mad_i32_i24", (0x00FFFFFF, 2, 1), (0xFFFFFFFF,)),
    ]
    for op, srcs, expected in vectors:
        got = evaluate(op, srcs)
        if got != expected:
            problems.append(f"self_test:{op}:{got!r}!={expected!r}")
    if literal_u32("1.0") != 0x3F800000:
        problems.append("literal_f32_1")
    if literal_u32("-1") != 0xFFFFFFFF:
        problems.append("literal_i32_minus1")
    return problems


if __name__ == "__main__":
    import json
    out = {
        "schema": "d1_gcn_vector_bit_exact_eval/v1",
        "status": "D1_GCN_VECTOR_BIT_EXACT_EVALUATOR_SOURCE_CLOSED" if not validate() else "WITH_VIOLATIONS",
        "opcodes": sorted(EVALUATOR_OPCODES),
        "violations": validate(),
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    raise SystemExit(0 if not out["violations"] else 2)
