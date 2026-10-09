#!/usr/bin/env python3
"""Train the D1 Oodle 2.3 native DLL for LLVM PGO using exact .bin/.raw pairs.

This process deliberately exits after training so the instrumentation runtime
flushes *.profraw before llvm-profdata merges the profile.
"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import sys
from pathlib import Path


def run(dll: Path, fixtures: Path, iterations: int) -> None:
    if sys.platform != "win32":
        raise SystemExit("OodleLZ_Decompress compatibility DLL training requires Windows.")
    if iterations < 1:
        raise SystemExit("--iterations must be at least one.")
    if not dll.is_file() or not fixtures.is_dir():
        raise SystemExit("Missing DLL or fixtures directory.")
    library = ctypes.WinDLL(str(dll.resolve()))
    decode = library.OodleLZ_Decompress
    decode.restype = ctypes.c_int64
    decode.argtypes = [
        ctypes.c_void_p, ctypes.c_int64,
        ctypes.c_void_p, ctypes.c_int64,
        ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
        ctypes.c_uint32,
    ]
    cases = []
    for packed in sorted(fixtures.glob("*.bin")):
        raw_file = packed.with_suffix(".raw")
        if not raw_file.is_file():
            raise SystemExit(f"Missing expected output: {raw_file}")
        compressed = packed.read_bytes()
        expected = raw_file.read_bytes()
        if not compressed or not expected:
            raise SystemExit(f"Empty frame or output: {packed}")
        source = ctypes.create_string_buffer(compressed)
        target = ctypes.create_string_buffer(len(expected))
        cases.append((packed.name, source, len(compressed), target, expected))
    if not cases:
        raise SystemExit(f"No .bin/.raw fixture pairs found in {fixtures}")

    def call(case):
        name, source, src_len, target, expected = case
        result = decode(
            ctypes.cast(source, ctypes.c_void_p),
            src_len,
            ctypes.cast(target, ctypes.c_void_p),
            len(expected),
            1, 0, 0, None, None, None, None, None, None, 3,
        )
        if result != len(expected):
            raise RuntimeError(f"{name}: decoder returned {result}, expected {len(expected)}")
        return target.raw[:len(expected)]

    for case in cases:
        got = call(case)
        if got != case[-1]:
            raise RuntimeError(f"{case[0]}: output SHA-256 mismatch; "
                               f"got {hashlib.sha256(got).hexdigest()}")
    print(f"PGO_EXACT_FIXTURES_VERIFIED {len(cases)}")

    for _ in range(iterations):
        for case in cases:
            # Only return code in the training loop: output was already checked
            # against each exact .raw fixture above.
            call_result = decode(
                ctypes.cast(case[1], ctypes.c_void_p),
                case[2], ctypes.cast(case[3], ctypes.c_void_p),
                len(case[4]), 1, 0, 0, None, None, None, None, None, None, 3,
            )
            if call_result != len(case[4]):
                raise RuntimeError(f"Training decode failed for {case[0]}: {call_result}")
    print(f"PGO_TRAINING_CALLS {iterations * len(cases)}")
    # Exit and unload the DLL so LLVM writes the raw profile to disk.


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dll", type=Path, required=True)
    parser.add_argument("--fixtures", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=140)
    args = parser.parse_args()
    run(args.dll, args.fixtures, args.iterations)
