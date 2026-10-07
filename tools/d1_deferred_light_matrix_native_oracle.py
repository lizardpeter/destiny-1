#!/usr/bin/env python3
"""Probe the isolated retail DeferredLight[8] matrix arithmetic, not game code.

Requires Linux x86-64 AVX, GNU gcc/objcopy, and the owner's verified 01.33 ELF.
The contiguous arithmetic fragment has no calls or RIP-relative data reads.
Its only modification is replacing the following instruction with RET. Inputs
are the authored LightData +0x20 matrix, instance matrix and camera position.
"""
import argparse
import ctypes
import hashlib
import json
import mmap
import platform
import struct
import subprocess
import tempfile
from pathlib import Path
from capstone import Cs, CS_ARCH_X86, CS_MODE_64
from d1_global_lighting_settings_defaults import EXPECTED_SHA256


def inverse_transpose(m):
    a = [[float(m[r][c]) for c in range(4)] + [float(r == c) for c in range(4)] for r in range(4)]
    for c in range(4):
        p = max(range(c, 4), key=lambda r: abs(a[r][c]))
        a[c], a[p] = a[p], a[c]
        d = a[c][c]
        if d == 0:
            raise ValueError("singular source matrix")
        a[c] = [v / d for v in a[c]]
        for r in range(4):
            if r != c:
                k = a[r][c]
                a[r] = [a[r][i] - k * a[c][i] for i in range(8)]
    return [[a[c][r + 4] for c in range(4)] for r in range(4)]


def probe(path):
    if platform.machine() not in ("x86_64", "AMD64") or " avx " not in Path("/proc/cpuinfo").read_text():
        raise RuntimeError("requires Linux x86-64 AVX")
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_SHA256
    start, end = 0x7F7F61, 0x7F840D
    fragment = raw[start + 0x4000:end + 0x4000]
    dis = list(Cs(CS_ARCH_X86, CS_MODE_64).disasm(fragment, start))
    assert dis[-1].address == 0x7F8404
    assert all(i.mnemonic not in ("call", "jmp", "ret") and "rip" not in i.op_str for i in dis)
    kernel = mmap.mmap(-1, len(fragment) + 1, prot=7)
    kernel.write(fragment + b"\xc3")
    address = ctypes.addressof(ctypes.c_char.from_buffer(kernel))
    asm = f""".intel_syntax noprefix
.text
.global wrapper
wrapper:
 push rbp
 push rbx
 push r15
 sub rsp, 0x400
 lea rbp, [rsp+0x300]
 mov r15, rdi
 lea rax, [rsi+0x20]
 vmovups xmm0, [rdx]
 vmovaps [rbp-0x70], xmm0
 vmovups xmm0, [rdx+0x10]
 vmovaps [rbp-0x60], xmm0
 vmovups xmm0, [rdx+0x20]
 vmovaps [rbp-0x50], xmm0
 vmovups xmm0, [rdx+0x30]
 vmovaps [rbp-0x40], xmm0
 vmovups xmm0, [rcx]
 vmovaps [rbp-0x1c0], xmm0
 vmovups xmm0, [rcx+0x10]
 vmovaps [rbp-0x240], xmm0
 vmovups xmm0, [rcx+0x20]
 vmovaps [rbp-0x250], xmm0
 vmovups xmm0, [rcx+0x30]
 vmovaps [rbp-0x260], xmm0
 mov edx, 0x3f800000
 vmovd xmm0, edx
 vshufps xmm0, xmm0, xmm0, 0
 vmovaps [rbp-0x1b0], xmm0
 mov edx, 0x30
 movabs r11, {address}
 call r11
 add rsp, 0x400
 pop r15
 pop rbx
 pop rbp
 ret
"""
    with tempfile.TemporaryDirectory() as td:
        src, obj, binary = [Path(td) / name for name in ("wrapper.s", "wrapper.o", "wrapper.bin")]
        src.write_text(asm)
        subprocess.run(["gcc", "-c", str(src), "-o", str(obj)], check=True)
        subprocess.run(["objcopy", "-O", "binary", "-j", ".text", str(obj), str(binary)], check=True)
        wrapper = binary.read_bytes()
    trampoline = mmap.mmap(-1, len(wrapper), prot=7)
    trampoline.write(wrapper)
    call = ctypes.CFUNCTYPE(None, *([ctypes.c_void_p] * 4))(ctypes.addressof(ctypes.c_char.from_buffer(trampoline)))
    def aligned(values):
        data = struct.pack("<" + "f" * len(values), *values)
        buf = ctypes.create_string_buffer(len(data) + 15)
        ptr = (ctypes.addressof(buf) + 15) & ~15
        ctypes.memmove(ptr, data, len(data))
        return buf, ptr
    matrices = [
        [[2,0,0,0],[0,3,0,0],[0,0,4,0],[1,2,3,1]],
        [[2,0,0,0],[0,3,0,0],[0,0,4,0.25],[1,2,3,1]],
        [[1,2,0,0.125],[0,1,1,0],[2,0,3,0],[1,-2,3,1]],
    ]
    instances = [
        [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]],
        [[0,2,0,0],[-2,0,0,0],[0,0,2,0],[10,-20,5,1]],
    ]
    cases = []
    for volume in matrices:
        for world in instances:
            for camera in ([0,0,0], [7,-9,11]):
                translation = [[1,0,0,0],[0,1,0,0],[0,0,1,0],[-camera[0],-camera[1],-camera[2],1]]
                buffers = [aligned([v for row in m for v in row]) for m in (volume, world, translation)]
                output, ptr = aligned([0] * 80)
                call(ptr, *[p for _, p in buffers])
                observed = struct.unpack("<16f", ctypes.string_at(ptr + 0x80, 64))
                absolute = [[sum(volume[r][k] * world[k][c] for k in range(4)) for c in range(4)] for r in range(4)]
                inv_t = inverse_transpose(absolute)
                inv = [[inv_t[c][r] for c in range(4)] for r in range(4)]
                expected = [inv[r][c] if r < 3 else inv[3][c] + sum(inv[k][c] * camera[k] for k in range(3)) for r in range(4) for c in range(4)]
                error = max(abs(a-b) for a,b in zip(observed, expected))
                assert error < 0.00005, (observed, expected, error)
                cases.append({"volume": volume, "instance": world, "camera": camera,
                              "native_output": [list(observed[r*4:r*4+4]) for r in range(4)], "max_absolute_error": error})
    return {"schema": "d1-deferred-light-matrix-native-oracle-v1", "sha256": EXPECTED_SHA256,
            "arithmetic_start_va": hex(start), "arithmetic_end_va": hex(end),
            "source_volume_offsets": ["0x20", "0x30", "0x40", "0x50"],
            "extern_output_offsets": ["0x80", "0x90", "0xa0", "0xb0"],
            "contract": "inverse(volume * instance * translation(-camera))",
            "fragment_sha256": hashlib.sha256(fragment).hexdigest(), "cases": cases}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("eboot", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    result = probe(args.eboot)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"cases": len(result["cases"]), "max_error": max(c["max_absolute_error"] for c in result["cases"])}))
