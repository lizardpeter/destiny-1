#!/usr/bin/env python3
"""Execute the verified, isolated D1 01.33 opcode 0x2A arithmetic kernel.

Linux x86-64 with AVX only. The source kernel has no calls or side effects
outside its output Vec4. Replace only its final VM dispatch jump with RET,
preserve all arithmetic and RIP-relative constants, and supply its registers.
The owner-provided executable is never distributed by this tool.
"""
import argparse
import ctypes
import hashlib
import json
import mmap
import platform
import struct
from pathlib import Path

from d1_global_lighting_settings_defaults import EXPECTED_SHA256


def probe(path):
    if platform.machine() not in ("x86_64", "AMD64") or " avx " not in Path("/proc/cpuinfo").read_text():
        raise RuntimeError("native oracle requires Linux x86-64 AVX")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != EXPECTED_SHA256:
        raise ValueError("wrong executable SHA256")
    jump_base = 0x82B288
    displacement = struct.unpack_from("<i", raw, jump_base + 0x4000 + (0x2A - 1) * 4)[0]
    assert jump_base + displacement == 0x829C92
    exit_offset = 0x829D61 + 0x4000
    assert raw[exit_offset:exit_offset + 5] == bytes.fromhex("e9c2140000")
    image = mmap.mmap(-1, len(raw), prot=mmap.PROT_READ | mmap.PROT_WRITE | mmap.PROT_EXEC)
    image.write(raw)
    image[exit_offset:exit_offset + 5] = b"\xc3\x90\x90\x90\x90"
    image_base = ctypes.addressof(ctypes.c_char.from_buffer(image))
    kernel = image_base + 0x829C92 + 0x4000
    # Preserve r13/r14; top = xmm10, output = r14, program counter = r13.
    wrapper = bytes.fromhex("415541564531ed4989f6c578101748b8") + struct.pack("<Q", kernel)
    wrapper += bytes.fromhex("ffd0415e415dc3")
    trampoline = mmap.mmap(-1, len(wrapper), prot=mmap.PROT_READ | mmap.PROT_WRITE | mmap.PROT_EXEC)
    trampoline.write(wrapper)
    call = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p)(ctypes.addressof(ctypes.c_char.from_buffer(trampoline)))
    output = ctypes.create_string_buffer(32)
    output_address = (ctypes.addressof(output) + 15) & ~15
    cases = []
    for x in [0.0, -0.0, 0.5, -0.5, 1.0, 2.0, 3.0, -1.0, -2.0, -5.5, 31.0, 127.0, 1024.0, 8191.0, 8388608.0]:
        source = ctypes.create_string_buffer(struct.pack("<4f", x, 42.0, -123.0, 999.0))
        call(ctypes.addressof(source), output_address)
        bits = struct.unpack("<4I", ctypes.string_at(output_address, 16))
        assert len(set(bits)) == 1
        cases.append({"input_x_bits": f"0x{struct.unpack('<I', struct.pack('<f', x))[0]:08x}",
                      "input_x": x, "output_bits": [f"0x{word:08x}" for word in bits]})
    return {"schema": "d1-tfx-rand-native-oracle-v1", "sha256": EXPECTED_SHA256,
            "handler_va": "0x829c92", "exit_jump_va": "0x829d61",
            "patch": "only final dispatch jump changed to ret+nops; arithmetic unchanged",
            "kernel_bytes": raw[0x829C92 + 0x4000:exit_offset + 5].hex(),
            "coefficient_bits": [f"0x{word:08x}" for word in struct.unpack_from("<4I", raw, 0x1662F80 + 0x4000)],
            "coefficient_order": "floor(x) times each coefficient, then (lane0+lane2)+(lane1+lane3)",
            "cases": cases}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("eboot", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    result = probe(args.eboot)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["cases"]))
