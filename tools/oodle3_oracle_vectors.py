#!/usr/bin/env python3
"""Generate deterministic, non-game Oodle 3 oracle vectors on Windows.

The proprietary DLL is supplied at runtime and never committed.  Compressed
vectors are derived only from deterministic synthetic byte strings so they can
be used for clean-room differential testing.
"""
from __future__ import annotations

import argparse
import base64
import ctypes
import hashlib
import json
import random
from pathlib import Path

EXPECTED_SHA256 = "682c0aad216fae443e0f9561876cfabfddaeffcd48e5990613ad2cf47c49fa62"


def h(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pattern(name: str, n: int) -> bytes:
    if name == "zeros":
        return bytes(n)
    if name == "ones":
        return b"\xff" * n
    if name == "ramp":
        return bytes((i & 0xff) for i in range(n))
    if name == "period3":
        p = b"ABC"
        return (p * ((n + 2) // 3))[:n]
    if name == "period31":
        p = bytes((i * 73 + 19) & 0xff for i in range(31))
        return (p * ((n + 30) // 31))[:n]
    if name == "sparse":
        b = bytearray(n)
        for i in range(0, n, 257):
            b[i] = (i // 257 * 29 + 7) & 0xff
        return bytes(b)
    if name == "records":
        out = bytearray()
        i = 0
        while len(out) < n:
            out += (i & 0xffffffff).to_bytes(4, "little")
            out += ((i * 0x9E3779B1) & 0xffffffff).to_bytes(4, "little")
            out += b"DESTINY-OODLE-RE"
            i += 1
        return bytes(out[:n])
    if name == "random":
        r = random.Random(0xD3571A1)
        return bytes(r.randrange(256) for _ in range(n))
    if name == "longmatch":
        seed = bytes((i * 11 + 3) & 0xff for i in range(min(n, 4096)))
        if n <= len(seed):
            return seed[:n]
        gap_len = min(32768, max(0, n - len(seed)))
        gap = bytes((i * 167 + 5) & 0xff for i in range(gap_len))
        out = seed + gap + seed
        while len(out) < n:
            out += seed
        return out[:n]
    raise ValueError(name)


class Oodle:
    def __init__(self, dll: Path):
        digest = h(dll.read_bytes())
        if digest != EXPECTED_SHA256:
            raise RuntimeError(f"unexpected DLL SHA-256 {digest}")
        self.dll = ctypes.WinDLL(str(dll.resolve()))

        self.decompress = self.dll.OodleLZ_Decompress
        self.decompress.restype = ctypes.c_int64
        self.decompress.argtypes = [
            ctypes.c_void_p, ctypes.c_int64,
            ctypes.c_void_p, ctypes.c_int64,
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
            ctypes.c_void_p, ctypes.c_void_p,
            ctypes.c_void_p, ctypes.c_void_p,
            ctypes.c_void_p, ctypes.c_void_p,
            ctypes.c_uint32,
        ]

        self.compress = self.dll.OodleLZ_Compress
        self.compress.restype = ctypes.c_int64
        self.compress.argtypes = [
            ctypes.c_int32,
            ctypes.c_void_p, ctypes.c_int64,
            ctypes.c_void_p,
            ctypes.c_int32,
            ctypes.c_void_p,
            ctypes.c_void_p, ctypes.c_int64,
        ]

        self.get_name = getattr(self.dll, "OodleLZ_Compressor_GetName", None)
        if self.get_name:
            self.get_name.restype = ctypes.c_char_p
            self.get_name.argtypes = [ctypes.c_int32]

    def compressor_names(self) -> dict[int, str]:
        out = {}
        if not self.get_name:
            return out
        for i in range(-1, 32):
            try:
                p = self.get_name(i)
                if p:
                    s = p.decode("ascii", "replace")
                    if s and "invalid" not in s.lower() and "unknown" not in s.lower():
                        out[i] = s
            except Exception:
                pass
        return out

    @staticmethod
    def bound(n: int) -> int:
        return n + 274 * ((n + 0x3FFFF) // 0x40000) + 4096

    def encode(self, compressor: int, raw: bytes, level: int) -> bytes:
        src = ctypes.create_string_buffer(raw)
        dst = ctypes.create_string_buffer(self.bound(len(raw)))
        got = self.compress(
            compressor,
            ctypes.cast(src, ctypes.c_void_p), len(raw),
            ctypes.cast(dst, ctypes.c_void_p),
            level,
            None,
            None, 0,
        )
        if got <= 0 or got > len(dst):
            raise RuntimeError(f"compressor={compressor} returned {got}")
        return dst.raw[:got]

    def decode(self, comp: bytes, raw_len: int) -> bytes:
        src = ctypes.create_string_buffer(comp)
        dst = ctypes.create_string_buffer(raw_len)
        got = self.decompress(
            ctypes.cast(src, ctypes.c_void_p), len(comp),
            ctypes.cast(dst, ctypes.c_void_p), raw_len,
            1, 0, 1,
            None, None, None, None, None, None,
            3,
        )
        if got != raw_len:
            raise RuntimeError(f"decompress returned {got}, expected {raw_len}")
        return dst.raw[:got]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("dll", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--compressor", type=int, action="append")
    ap.add_argument("--level", type=int, default=4)
    args = ap.parse_args()

    oo = Oodle(args.dll)
    names = oo.compressor_names()
    compressor_ids = args.compressor or sorted(k for k in names if k != 3)
    if not compressor_ids:
        # Historical legacy Oodle IDs. Failures are recorded rather than assumed.
        compressor_ids = [0, 1, 2, 4, 5, 6, 7, 8, 9, 10]

    cases = [
        ("zeros", 64), ("ramp", 64), ("period3", 257), ("period31", 1024),
        ("sparse", 4096), ("records", 16384), ("longmatch", 65536),
        ("random", 65536), ("period31", 0x3fff), ("period31", 0x4000),
        ("period31", 0x4001), ("records", 0x10000), ("sparse", 0x3ffff),
        ("sparse", 0x40000),
    ]

    out_dir = args.output.parent / (args.output.stem + "_vectors")
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "schema": "d1_oodle3_oracle_vectors_v1",
        "dll_sha256": EXPECTED_SHA256,
        "compressor_names": {str(k): v for k, v in names.items()},
        "level": args.level,
        "vectors": [],
        "compressor_failures": [],
    }

    for cid in compressor_ids:
        for pname, n in cases:
            raw = pattern(pname, n)
            try:
                comp = oo.encode(cid, raw, args.level)
                dec = oo.decode(comp, len(raw))
                if dec != raw:
                    raise RuntimeError("round-trip bytes differ")
            except Exception as ex:
                report["compressor_failures"].append({
                    "compressor": cid, "name": names.get(cid), "pattern": pname,
                    "raw_size": n, "error": repr(ex),
                })
                # If the first tiny case fails, this codec is probably not encodable.
                if n == 64 and pname == "zeros":
                    break
                continue

            fn = f"c{cid}_{pname}_{n}.bin"
            (out_dir / fn).write_bytes(comp)
            report["vectors"].append({
                "compressor": cid,
                "compressor_name": names.get(cid),
                "level": args.level,
                "pattern": pname,
                "raw_size": n,
                "raw_sha256": h(raw),
                "compressed_size": len(comp),
                "compressed_sha256": h(comp),
                "compressed_prefix_hex": comp[:96].hex(),
                "compressed_file": fn,
                "compressed_base64": base64.b64encode(comp).decode("ascii") if len(comp) <= 8192 else None,
            })

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "compressor_names": report["compressor_names"],
        "vectors": len(report["vectors"]),
        "failures": len(report["compressor_failures"]),
        "output": str(args.output),
        "vector_dir": str(out_dir),
    }, indent=2))
    return 0 if report["vectors"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
