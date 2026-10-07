#!/usr/bin/env python3
"""Execute only the verified finite mode-2 Atmosphere arithmetic fragment.

The ELF is mapped solely to retain RIP-relative constants. The executed path
has no calls; its exit is replaced by RET. This does not activate a game map.
"""
import argparse
import ctypes
import hashlib
import json
import mmap
import platform
import struct
from pathlib import Path
from capstone import Cs, CS_ARCH_X86, CS_MODE_64
from d1_global_lighting_settings_defaults import EXPECTED_SHA256


def f32(x):
    return ctypes.c_float(x).value


def probe(path):
    if platform.machine() not in ("x86_64", "AMD64") or " avx " not in Path("/proc/cpuinfo").read_text():
        raise RuntimeError("requires Linux x86-64 AVX")
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_SHA256
    start, end = 0x842C71, 0x842FE6
    dis = Cs(CS_ARCH_X86, CS_MODE_64)
    prefix = list(dis.disasm(raw[start + 0x4000:0x842CE8 + 0x4000], start))
    assert prefix[-1].address == 0x842CE3 and prefix[-1].op_str == "0x842f7c"
    assert any(i.address == 0x842CC9 and i.op_str == "dword ptr [r14 + 0x88], 2" for i in prefix)
    executed = prefix + list(dis.disasm(raw[0x842F7C + 0x4000:end + 0x4000], 0x842F7C))
    assert all(i.mnemonic != "call" for i in executed)
    assert raw[end + 0x4000:end + 0x4000 + 7].hex() == "418bbe8c000000"
    kernel = mmap.mmap(-1, len(raw), prot=7)
    kernel.write(raw)
    kernel[end + 0x4000] = 0xC3
    target = ctypes.addressof(ctypes.c_char.from_buffer(kernel)) + start + 0x4000
    wrapper = bytes.fromhex("5341564889fb4989f648b8") + struct.pack("<Q", target) + bytes.fromhex("ffd0415e5bc3")
    trampoline = mmap.mmap(-1, len(wrapper), prot=7)
    trampoline.write(wrapper)
    call = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p)(ctypes.addressof(ctypes.c_char.from_buffer(trampoline)))
    settings = ctypes.create_string_buffer(0xF0)
    struct.pack_into("<I", settings, 0x88, 2)
    eps = struct.unpack_from("<f", raw, 0x1663F2C + 0x4000)[0]
    offsets = [0x90, 0x98, 0xF4, 0xB0, 0xD8, 0xA8, 0xAC]
    inputs = [
        [0, 0, 0, 0, 0, 0, 0],
        [1000, 2000, 180, .5, 1.5, 5, 5],
        [2000, 4000, 360, -1, -2, 5, 6],
        [-1000, 3000, -90, .00001, .0002, -7, -7],
        [123.5, 2345.75, 719.5, .25, .75, 1, 1.00001],
    ]
    cases = []
    for values in inputs:
        block = ctypes.create_string_buffer(0x130)
        for off, value in zip(offsets, values):
            struct.pack_into("<f", block, off, value)
        before = bytes(block)
        q = [f32(x) for x in values]
        expected = [f32(f32(q[0] / 2000) - 1), f32(f32(q[1] / 2000) - 1),
                    f32(q[2] / 360), max(eps, q[3]), max(eps, q[4]), q[5],
                    f32(q[5] + eps) if q[5] == q[6] else q[6]]
        expected_bytes = bytearray(before)
        for off, value in zip(offsets + [0x128], expected + [.0625]):
            struct.pack_into("<f", expected_bytes, off, value)
        call(block, settings)
        assert bytes(block) == expected_bytes, (values, bytes(block).hex(), expected_bytes.hex())
        cases.append({"input": {hex(o): q[i] for i, o in enumerate(offsets)},
                      "native_output": {hex(o): struct.unpack_from("<f", block, o)[0] for o in offsets + [0x128]}})
    return {"schema": "d1-atmosphere-mode2-native-oracle-v1", "sha256": EXPECTED_SHA256,
            "arithmetic_start_va": hex(start), "arithmetic_end_va": hex(end),
            "settings_mode_offset": "0x88", "mode": 2,
            "executed_source": [{"va": hex(i.address), "bytes": i.bytes.hex(), "mnemonic": i.mnemonic, "operands": i.op_str} for i in executed],
            "formulas": {"0x90": "f32(f32(channel/2000)-1)", "0x98": "f32(f32(channel/2000)-1)",
                         "0xf4": "channel/360", "0xb0": "max(0.0001,channel)", "0xd8": "max(0.0001,channel)",
                         "0xac": "if lower==upper then f32(lower+0.0001)", "0x128": "0.0625"},
            "cases": cases, "all_native_outputs_match": True,
            "scope": "Finite mode-2 arithmetic only. Map mode/settings ownership, live channels and LUTs remain unestablished. General-path imported helper 0x12aaaa0 is unnamed."}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("eboot", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    result = probe(args.eboot)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"mode": result["mode"], "cases": len(result["cases"]), "all_native_outputs_match": result["all_native_outputs_match"]}))
