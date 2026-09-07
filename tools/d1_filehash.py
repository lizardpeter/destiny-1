#!/usr/bin/env python3
"""Source-validated Destiny 1 Tiger FileHash decoding helpers.

D1 FileHashes are not a single linear ``0x80800000 + package*0x2000 + index``
namespace. Later package ranges wrap bank bits into the high part of the hash.
The package decoder is the ROI-era Tiger layout already validated by the project:

    package = ((v >> 13) & 0x3FF) + ((((v >> 23) & 3) - 1) * 0x400)
    index   = v & 0x1FFF

This module exists so universal activity/world/export tools do not accidentally
reintroduce the older low-namespace-only subtraction formula.
"""
from __future__ import annotations

NULLS = {0x00000000, 0xFFFFFFFF}


def norm(value: object) -> str:
    return str(value).upper().removeprefix("0X").zfill(8)


def decode_int(v: int) -> tuple[int, int]:
    v &= 0xFFFFFFFF
    pkg = ((v >> 13) & 0x3FF) + ((((v >> 23) & 3) - 1) * 0x400)
    idx = v & 0x1FFF
    return pkg, idx


def decode(value: object) -> tuple[int, int]:
    return decode_int(int(norm(value), 16))


def package_id(value: object) -> int:
    return decode(value)[0]


def entry_index(value: object) -> int:
    return decode(value)[1]


def package_hex(value: object) -> str:
    return f"{package_id(value):04X}"


def plausible_int(v: int) -> bool:
    """Return whether the encoded package bank is non-negative.

    Exact membership still requires checking the decoded package/index against the
    verified current package catalog. This predicate is only a cheap prefilter for
    byte scans; it never establishes that a value is a real FileHash.
    """
    if (v & 0xFFFFFFFF) in NULLS:
        return False
    pkg, _ = decode_int(v)
    return pkg >= 0


if __name__ == "__main__":
    # Cross-bank canaries from exact current named tags.
    expected = {
        "80C98019": (0x024C, 0x0019),
        "8108E004": (0x0447, 0x0004),
        "8179E047": (0x07CF, 0x0047),
        "8192C003": (0x0896, 0x0003),
        "8194C002": (0x08A6, 0x0002),
    }
    for h, want in expected.items():
        got = decode(h)
        assert got == want, (h, got, want)
        print(h, f"PACKAGE={got[0]:04X}", f"INDEX={got[1]:04X}")
