#!/usr/bin/env python3
"""LZH-focused differential oracle for the exact D1 Oodle 3 runtime.

All inputs are deterministic synthetic bytes.  The report is designed to expose
legacy LZH framing and payload sensitivity without embedding or redistributing
the proprietary DLL.
"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
from pathlib import Path

EXPECTED_SHA256 = "682c0aad216fae443e0f9561876cfabfddaeffcd48e5990613ad2cf47c49fa62"
LZH = 0
LEVEL = 4


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Runtime:
    def __init__(self, dll: Path):
        if sha(dll.read_bytes()) != EXPECTED_SHA256:
            raise RuntimeError("reference DLL hash mismatch")
        self.lib = ctypes.WinDLL(str(dll.resolve()))
        self.compress = self.lib.OodleLZ_Compress
        self.compress.restype = ctypes.c_int64
        self.compress.argtypes = [
            ctypes.c_int32, ctypes.c_void_p, ctypes.c_int64, ctypes.c_void_p,
            ctypes.c_int32, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int64,
        ]
        self.decompress = self.lib.OodleLZ_Decompress
        self.decompress.restype = ctypes.c_int64
        self.decompress.argtypes = [
            ctypes.c_void_p, ctypes.c_int64, ctypes.c_void_p, ctypes.c_int64,
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32,
        ]

    def enc(self, raw: bytes) -> bytes:
        src = ctypes.create_string_buffer(raw)
        cap = len(raw) + 8192
        dst = ctypes.create_string_buffer(cap)
        got = self.compress(
            LZH, ctypes.cast(src, ctypes.c_void_p), len(raw),
            ctypes.cast(dst, ctypes.c_void_p), LEVEL, None, None, 0,
        )
        if got <= 0 or got > cap:
            raise RuntimeError(f"compress returned {got}")
        return dst.raw[:got]

    def dec(self, comp: bytes, raw_len: int, fill: int = 0xCD):
        src = ctypes.create_string_buffer(comp)
        dst = ctypes.create_string_buffer(raw_len)
        ctypes.memset(ctypes.addressof(dst), fill, raw_len)
        got = self.decompress(
            ctypes.cast(src, ctypes.c_void_p), len(comp),
            ctypes.cast(dst, ctypes.c_void_p), raw_len,
            1, 0, 0, None, None, None, None, None, None, 3,
        )
        return int(got), dst.raw[:raw_len]


def make_pattern(kind: str, n: int) -> bytes:
    if kind == "A":
        return b"A" * n
    if kind == "AB":
        return (b"AB" * ((n + 1) // 2))[:n]
    if kind == "ABC":
        return (b"ABC" * ((n + 2) // 3))[:n]
    if kind == "ramp":
        return bytes(i & 0xFF for i in range(n))
    if kind == "literal_then_A":
        p = bytes(range(min(64, n)))
        return (p + b"A" * n)[:n]
    if kind == "records":
        out = bytearray()
        i = 0
        while len(out) < n:
            out += (i & 0xFFFFFFFF).to_bytes(4, "little")
            out += b"D1LZH"
            i += 1
        return bytes(out[:n])
    raise ValueError(kind)


def quantum_summary(comp: bytes, raw_len: int):
    if len(comp) < 2:
        return []
    if comp[0] == 0xCC:
        return [{"kind": "whole_stored", "raw_len": raw_len, "payload_len": len(comp) - 2}]
    if comp[0] != 0x8C or comp[1] != 7:
        return [{"kind": "other_outer", "prefix": comp[:8].hex()}]
    p = 2
    rp = 0
    out = []
    while rp < raw_len and p + 2 <= len(comp):
        qraw = min(0x4000, raw_len - rp)
        word = int.from_bytes(comp[p:p+2], "big")
        p += 2
        lo = word & 0x3FFF
        flags = word >> 14
        if lo != 0x3FFF:
            n = lo + 1
            kind = "compressed"
        elif flags == 1:
            n = qraw
            kind = "stored"
        else:
            out.append({"raw_offset": rp, "raw_len": qraw, "word": word, "kind": "special_unknown", "flags": flags})
            break
        out.append({
            "raw_offset": rp,
            "raw_len": qraw,
            "header_word": word,
            "flags": flags,
            "kind": kind,
            "payload_offset": p,
            "payload_len": n,
            "payload_prefix": comp[p:p+min(n, 32)].hex(),
        })
        p += n
        rp += qraw
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("dll", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args()

    rt = Runtime(args.dll)
    sizes = list(range(1, 33)) + [
        40, 48, 64, 80, 96, 112, 128, 160, 192, 224, 256, 257, 258,
        320, 384, 512, 768, 1024, 2048, 4096, 8192, 16383, 16384, 16385,
    ]
    kinds = ["A", "AB", "ABC", "ramp", "literal_then_A", "records"]
    cases = []

    for kind in kinds:
        for n in sizes:
            raw = make_pattern(kind, n)
            comp = rt.enc(raw)
            got, dec = rt.dec(comp, len(raw))
            if got != len(raw) or dec != raw:
                raise RuntimeError(f"round trip failed: {kind} {n} got={got}")
            cases.append({
                "pattern": kind,
                "raw_len": n,
                "raw_sha256": sha(raw),
                "comp_len": len(comp),
                "comp_sha256": sha(comp),
                "outer": comp[:2].hex(),
                "prefix_hex": comp[:64].hex(),
                "full_hex": comp.hex() if len(comp) <= 256 else None,
                "quanta": quantum_summary(comp, len(raw)),
            })

    target_raw = make_pattern("ABC", 257)
    target_comp = rt.enc(target_raw)
    if target_comp[:2] != b"\x8c\x07":
        raise RuntimeError(f"mutation target did not encode as LZH: {target_comp[:8].hex()}")

    mutations = []
    for byte_i in range(2, len(target_comp)):
        for bit in range(8):
            m = bytearray(target_comp)
            m[byte_i] ^= 1 << bit
            got, dec = rt.dec(bytes(m), len(target_raw))
            diffs = [i for i, (a, b) in enumerate(zip(dec, target_raw)) if a != b] if got == len(target_raw) else []
            mutations.append({
                "byte_offset": byte_i,
                "bit": bit,
                "returned": got,
                "success": got == len(target_raw),
                "exact": got == len(target_raw) and dec == target_raw,
                "diff_count": len(diffs),
                "first_diff": diffs[0] if diffs else None,
                "last_diff": diffs[-1] if diffs else None,
                "output_sha256": sha(dec) if got == len(target_raw) else None,
            })

    truncations = []
    for n in range(2, len(target_comp) + 1):
        got, dec = rt.dec(target_comp[:n], len(target_raw))
        truncations.append({
            "comp_len": n,
            "returned": got,
            "exact": got == len(target_raw) and dec == target_raw,
        })

    report = {
        "schema": "d1_oodle3_lzh_micro_oracle_v1",
        "dll_sha256": EXPECTED_SHA256,
        "compressor": "LZH",
        "compressor_enum": LZH,
        "level": LEVEL,
        "case_count": len(cases),
        "cases": cases,
        "mutation_target": {
            "raw_pattern": "ABC",
            "raw_len": len(target_raw),
            "raw_sha256": sha(target_raw),
            "comp_len": len(target_comp),
            "comp_hex": target_comp.hex(),
            "quanta": quantum_summary(target_comp, len(target_raw)),
        },
        "bit_mutations": mutations,
        "truncations": truncations,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "cases": len(cases),
        "mutation_bits": len(mutations),
        "target_comp_len": len(target_comp),
        "output": str(args.output),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
