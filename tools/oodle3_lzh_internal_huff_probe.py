#!/usr/bin/env python3
"""Probe exact internal LZH Huffman setup state in the verified Oodle 3 DLL.

This is diagnostic tooling for the clean-room Rust reimplementation.  It calls
one internal routine by RVA on deterministic synthetic data and records only
derived state/metadata, not machine code.
"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
from pathlib import Path

SHA = "682c0aad216fae443e0f9561876cfabfddaeffcd48e5990613ad2cf47c49fa62"
RVA_LZH_HUFF_SETUP = 0x5D5E0
LZH_COMPRESSOR = 0
LEVEL = 4


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def ptr_u64(addr: int) -> int:
    return int(ctypes.c_uint64.from_address(addr).value)


def u32(addr: int) -> int:
    return int(ctypes.c_uint32.from_address(addr).value)


def i32(addr: int) -> int:
    return int(ctypes.c_int32.from_address(addr).value)


def qword(addr: int) -> int:
    return int(ctypes.c_uint64.from_address(addr).value)


class Runtime:
    def __init__(self, dll_path: Path):
        if sha(dll_path.read_bytes()) != SHA:
            raise RuntimeError("DLL hash mismatch")
        self.dll = ctypes.WinDLL(str(dll_path.resolve()))
        self.base = int(self.dll._handle)
        self.compress = self.dll.OodleLZ_Compress
        self.compress.restype = ctypes.c_int64
        self.compress.argtypes = [
            ctypes.c_int32, ctypes.c_void_p, ctypes.c_int64, ctypes.c_void_p,
            ctypes.c_int32, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int64,
        ]

    def enc(self, raw: bytes) -> bytes:
        src = ctypes.create_string_buffer(raw)
        dst = ctypes.create_string_buffer(len(raw) + 8192)
        got = int(self.compress(
            LZH_COMPRESSOR,
            ctypes.cast(src, ctypes.c_void_p), len(raw),
            ctypes.cast(dst, ctypes.c_void_p),
            LEVEL, None, None, 0,
        ))
        if got <= 0:
            raise RuntimeError(f"compress returned {got}")
        return dst.raw[:got]

    def setup(self, payload: bytes):
        decoder = ctypes.create_string_buffer(0x20000)
        comp = ctypes.create_string_buffer(payload)
        used = ctypes.c_int32(-1)

        fn_t = ctypes.CFUNCTYPE(
            ctypes.c_int,
            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_int32),
        )
        fn = fn_t(self.base + RVA_LZH_HUFF_SETUP)
        dec_addr = ctypes.addressof(decoder)
        comp_addr = ctypes.addressof(comp)
        ok = int(fn(
            ctypes.c_void_p(dec_addr),
            ctypes.c_void_p(comp_addr),
            ctypes.c_void_p(comp_addr + len(payload)),
            ctypes.byref(used),
        ))

        state = ptr_u64(dec_addr + 0x60)
        result = {
            "ok": ok,
            "consumed": int(used.value),
            "decoder_address_mod16": dec_addr & 0xF,
            "state_offset_from_decoder": state - dec_addr if state else None,
        }
        if not ok or not state:
            return result

        result["header_fields"] = {
            "num_symbols_0x284": u32(state + 0x284),
            "field_0x288": i32(state + 0x288),
            "table_bits_0x28c": i32(state + 0x28C),
            "field_0x290": i32(state + 0x290),
            "field_0x294": i32(state + 0x294),
            "field_0x298": i32(state + 0x298),
            "field_0x29c": i32(state + 0x29C),
        }

        for off in range(0x00, 0x200, 8):
            result.setdefault("qwords_0x000_0x1ff", []).append({
                "offset": off,
                "value": qword(state + off),
            })

        ptrs = {}
        for off in (0x2A0, 0x2A8, 0x2B0, 0x2B8, 0x2C0):
            p = ptr_u64(state + off)
            ptrs[f"0x{off:x}"] = {
                "offset_from_state": p - state if p else None,
            }
        result["internal_pointers"] = ptrs

        nsyms = result["header_fields"]["num_symbols_0x284"]
        table_bits = result["header_fields"]["table_bits_0x28c"]
        p_a = ptr_u64(state + 0x2A0)
        p_b = ptr_u64(state + 0x2A8)
        p_c = ptr_u64(state + 0x2B0)
        p_len = ptr_u64(state + 0x2B8)
        p_sym = ptr_u64(state + 0x2C0)

        def bounded_bytes(p: int, n: int):
            if not p or n <= 0 or n > 1_000_000:
                return None
            return bytes((ctypes.c_uint8 * n).from_address(p))

        if p_a and p_b and p_b >= p_a and p_b - p_a <= 16384:
            b = bounded_bytes(p_a, p_b - p_a)
            result["array_2a0_to_2a8"] = {
                "size": len(b),
                "sha256": sha(b),
                "hex": b.hex(),
            }
        if p_b and p_c and p_c >= p_b and p_c - p_b <= 16384:
            b = bounded_bytes(p_b, p_c - p_b)
            result["array_2a8_to_2b0"] = {
                "size": len(b),
                "sha256": sha(b),
                "hex": b.hex(),
            }

        if p_len and p_sym and table_bits > 0 and table_bits <= 16:
            count = 1 << table_bits
            lens = bounded_bytes(p_len, count)
            syms_raw = bounded_bytes(p_sym, count * 2)
            syms = [
                int.from_bytes(syms_raw[i:i+2], "little")
                for i in range(0, len(syms_raw), 2)
            ]
            result["fast_table"] = {
                "count": count,
                "length_histogram": {
                    str(k): lens.count(k) for k in sorted(set(lens))
                },
                "lengths_hex": lens.hex(),
                "symbols": syms,
            }

        # The construction uses 713 symbols; save a compact view of likely
        # per-symbol metadata around each variable-length array.
        result["state_prefix_sha256"] = sha(bytes(
            (ctypes.c_uint8 * 0x2D0).from_address(state)
        ))
        return result


def payload_from_stream(comp: bytes, raw_len: int) -> bytes:
    if comp[:2] != b"\x8c\x07":
        raise RuntimeError(f"expected compressed LZH frame, got {comp[:8].hex()}")
    if len(comp) < 4:
        raise RuntimeError("truncated frame")
    word = int.from_bytes(comp[2:4], "big")
    size_code = word & 0x3FFF
    if size_code == 0x3FFF:
        raise RuntimeError("selected vector encoded as special quantum")
    n = size_code + 1
    payload = comp[4:4+n]
    if len(payload) != n:
        raise RuntimeError("truncated payload")
    return payload


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("dll", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args()

    rt = Runtime(args.dll)
    vectors = {
        "ABC_257": (b"ABC" * 86)[:257],
        "AB_257": (b"AB" * 129)[:257],
        "ramp_384": bytes(i & 0xFF for i in range(384)),
        "records_257": (b"\x00\x00\x00\x00D1LZH\x01\x00\x00\x00D1LZH" * 32)[:257],
    }

    report = {
        "schema": "d1_oodle3_lzh_internal_huff_probe_v1",
        "dll_sha256": SHA,
        "setup_rva": RVA_LZH_HUFF_SETUP,
        "vectors": {},
    }
    for name, raw in vectors.items():
        comp = rt.enc(raw)
        payload = payload_from_stream(comp, len(raw))
        report["vectors"][name] = {
            "raw_len": len(raw),
            "comp_len": len(comp),
            "comp_hex": comp.hex() if len(comp) <= 512 else None,
            "payload_len": len(payload),
            "payload_hex": payload.hex() if len(payload) <= 512 else None,
            "setup": rt.setup(payload),
        }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        name: {
            "payload_len": row["payload_len"],
            "setup_ok": row["setup"]["ok"],
            "consumed": row["setup"]["consumed"],
            "state_offset": row["setup"].get("state_offset_from_decoder"),
        }
        for name, row in report["vectors"].items()
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
