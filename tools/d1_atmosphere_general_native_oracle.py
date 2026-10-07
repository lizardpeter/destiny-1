#!/usr/bin/env python3
"""Probe verified Atmosphere arithmetic with explicitly substituted host expf.

This is an arithmetic/call-routing oracle, not a retail libc or map render test.
The exact PLT relocation and cryptographic NID identify expf. All source code
except that imported thunk and the fragment's terminal RET remains unchanged.
"""
import argparse
import base64
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


def f32(x):
    return ctypes.c_float(x).value


def inverse(m):
    a = [[float(m[r][c]) for c in range(4)] + [float(r == c) for c in range(4)] for r in range(4)]
    for c in range(4):
        p = max(range(c, 4), key=lambda r: abs(a[r][c]))
        a[c], a[p] = a[p], a[c]
        d = a[c][c]
        assert d != 0
        a[c] = [v / d for v in a[c]]
        for r in range(4):
            if r != c:
                k = a[r][c]
                a[r] = [a[r][i] - k * a[c][i] for i in range(8)]
    return [row[4:] for row in a]


def import_identity(raw):
    phoff = struct.unpack_from("<Q", raw, 32)[0]
    ents, num = struct.unpack_from("<HH", raw, 54)
    segments = [struct.unpack_from("<IIQQQQQQ", raw, phoff + ents * i) for i in range(num)]
    dynamic = next(s for s in segments if s[0] == 2)
    dynlib = next(s for s in segments if s[0] == 0x61000000)
    tags = dict(struct.unpack_from("<QQ", raw, o) for o in range(dynamic[2], dynamic[2] + dynamic[5], 16))
    base = dynlib[2]
    strings = raw[base + tags[0x61000035]:base + tags[0x61000035] + tags[0x61000037]]
    hits = []
    for i in range(tags[0x6100002D] // 24):
        off, info, addend = struct.unpack_from("<QQq", raw, base + tags[0x61000029] + i * 24)
        if off == 0x1A20290:
            si = info >> 32
            ni = struct.unpack_from("<I", raw, base + tags[0x61000039] + si * tags[0x6100003B])[0]
            name = strings[ni:strings.index(b"\0", ni)].decode()
            hits.append({"relocation_index": i, "got_va": hex(off), "symbol_index": si,
                         "symbol_name": name, "relocation_type": info & 0xFFFFFFFF, "addend": addend})
    assert len(hits) == 1 and hits[0]["symbol_name"] == "8zsu04XNsZ4#w#r"
    assert hits[0]["relocation_index"] == 0x2E
    salt = bytes.fromhex("518D64A635DED8C1E6B039B1C3E55230")
    computed = base64.b64encode(hashlib.sha1(b"expf" + salt).digest()[:8][::-1]).decode().rstrip("=").replace("/", "-")
    assert computed == hits[0]["symbol_name"].split("#")[0]
    return {**hits[0], "resolved_name": "expf", "nid_salt_hex": salt.hex(), "computed_nid": computed,
            "source_mapping_url": "https://github.com/shadps4-emu/shadPS4/blob/945dbc3cc3eee80ac3e053b438502ed936fa6bb2/src/core/libraries/libc_internal/libc_internal_math.cpp"}


def probe(path):
    if platform.machine() not in ("x86_64", "AMD64") or " avx " not in Path("/proc/cpuinfo").read_text():
        raise RuntimeError("requires Linux x86-64 AVX")
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_SHA256
    identity = import_identity(raw)
    start, end = 0x842C71, 0x842FE6
    dis = list(Cs(CS_ARCH_X86, CS_MODE_64).disasm(raw[start + 0x4000:end + 0x4000], start))
    assert [(i.address, i.op_str) for i in dis if i.mnemonic == "call"] == [(0x842EDA, "0x12aaaa0"), (0x842F20, "0x12aaaa0")]
    assert raw[end + 0x4000:end + 0x4000 + 7].hex() == "418bbe8c000000"
    libm = ctypes.CDLL("libm.so.6")
    expf = libm.expf
    expf.argtypes, expf.restype = [ctypes.c_float], ctypes.c_float
    helper_address = ctypes.cast(expf, ctypes.c_void_p).value
    log = ctypes.create_string_buffer(12)
    kernel = mmap.mmap(-1, len(raw), prot=7)
    kernel.write(raw)
    kernel[end + 0x4000] = 0xC3
    address = ctypes.addressof(ctypes.c_char.from_buffer(kernel))
    asm = f""".intel_syntax noprefix
.text
.global wrapper
wrapper:
 push rbp
 push rbx
 push r14
 push r15
 sub rsp, 0x108
 lea rbp, [rsp+0x80]
 mov rbx, rdi
 mov r14, rsi
 mov r15, rdx
 movabs rax, {address + start + 0x4000}
 call rax
 add rsp, 0x108
 pop r15
 pop r14
 pop rbx
 pop rbp
 ret
helper:
 movabs rax, {ctypes.addressof(log)}
 mov ecx, [rax]
 movss [rax+rcx*4+4], xmm0
 inc dword ptr [rax]
 movabs rax, {helper_address}
 jmp rax
"""
    with tempfile.TemporaryDirectory() as td:
        src, obj, binary = [Path(td) / name for name in ("wrapper.s", "wrapper.o", "wrapper.bin")]
        src.write_text(asm)
        subprocess.run(["gcc", "-c", str(src), "-o", str(obj)], check=True)
        subprocess.run(["objcopy", "-O", "binary", "-j", ".text", str(obj), str(binary)], check=True)
        wrapper = binary.read_bytes()
    trampoline = mmap.mmap(-1, len(wrapper), prot=7)
    trampoline.write(wrapper)
    wrapper_address = ctypes.addressof(ctypes.c_char.from_buffer(trampoline))
    # RET immediately precedes helper; locate the verified movabs log address.
    marker = b"\x48\xb8" + struct.pack("<Q", ctypes.addressof(log))
    helper_offset = wrapper.index(marker)
    thunk = b"\x48\xb8" + struct.pack("<Q", wrapper_address + helper_offset) + b"\xff\xe0"
    kernel[0x12AAAA0 + 0x4000:0x12AAAA0 + 0x4000 + len(thunk)] = thunk
    call = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p)(wrapper_address)
    matrices = [
        [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]],
        [[1,0,0,0],[0,1,0,0],[0,0,1,0],[7,-9,-120,1]],
        [[0,2,0,0],[-2,0,0,0],[0,0,4,0],[10,-20,-40,1]],
        [[1,2,0,0],[0,1,1,0],[2,0,3,0],[1,-2,3,1]],
        [[2,0,0,0],[0,3,0,0],[0,0,4,.25],[1,2,-30,1]],
    ]
    configs = [
        {0x90:1000,0x94:2,0x98:3000,0x9C:3,0xF4:180,0xB0:.5,0xB4:20,0xD8:.75,0xDC:30,0xD4:2,0xA4:3,0xA8:5,0xAC:5},
        {0x90:2000,0x94:2,0x98:2000,0x9C:3,0xF4:360,0xB0:0,0xB4:0,0xD8:0,0xDC:0,0xD4:0,0xA4:0,0xA8:5,0xAC:6},
        {0x90:0,0x94:5,0x98:4000,0x9C:7,0xF4:-90,0xB0:1000,0xB4:-1000,0xD8:1000,0xDC:-1000,0xD4:2,0xA4:3,0xA8:-7,0xAC:-7},
        {0x90:123.5,0x94:1.25,0x98:2345.75,0x9C:.75,0xF4:719.5,0xB0:-100,0xB4:1000,0xD8:-100,0xDC:1000,0xD4:2,0xA4:3,0xA8:1,0xAC:1.00001},
    ]
    eps = struct.unpack_from("<f", raw, 0x1663F2C + 0x4000)[0]
    cases = []
    for mi, matrix in enumerate(matrices):
        matrix_buf = ctypes.create_string_buffer(79)
        matrix_ptr = (ctypes.addressof(matrix_buf) + 15) & ~15
        ctypes.memmove(matrix_ptr, struct.pack("<16f", *[v for row in matrix for v in row]), 64)
        expected_z = inverse(matrix)[3][2]
        for ci, config in enumerate(configs):
            mode = [0,1,3,4][ci]
            block = ctypes.create_string_buffer(0x130)
            settings = ctypes.create_string_buffer(0xF0)
            struct.pack_into("<I", settings, 0x88, mode)
            for off, value in config.items():
                struct.pack_into("<f", block, off, value)
            before = bytes(block)
            log.raw = bytes(12)
            call(block, settings, matrix_ptr)
            count, arg0, arg1 = struct.unpack("<Iff", log.raw)
            assert count == 2
            q = {k:f32(v) for k,v in config.items()}
            q[0x90] = f32(f32(q[0x90]/2000)-1)
            q[0x98] = f32(f32(q[0x98]/2000)-1)
            q[0xF4] = f32(q[0xF4]/360)
            for g, density in [(0x90,0x94),(0x98,0x9C)]:
                g2 = f32(q[g]*q[g])
                q[density] = f32(f32(f32(f32(1-g2)/f32(2+g2))*1.5)*q[density])
            expected_args = []
            for slope, origin in [(0xD8,0xDC),(0xB0,0xB4)]:
                arg = min(64., f32(f32(f32(f32(expected_z)-q[origin])*q[slope])*f32(-.001)))
                expected_args.append(arg)
            assert max(abs(a-b) for a,b in zip([arg0,arg1], expected_args)) <= 2e-5 * max(1, *map(abs, expected_args))
            # Use recorded native arguments to distinguish matrix roundoff from
            # the density transform. Imported libc is deliberately host expf.
            q[0xD4] = f32(expf(arg0)*q[0xD4])
            q[0xA4] = f32(expf(arg1)*q[0xA4])
            q[0xD8] = max(eps, eps if q[0xD4] == 0 else q[0xD8])
            q[0xB0] = max(eps, eps if q[0xA4] == 0 else q[0xB0])
            if q[0xA8] == q[0xAC]:
                q[0xAC] = f32(q[0xA8] + eps)
            q[0x128] = .0625
            expected = bytearray(before)
            for off, value in q.items():
                struct.pack_into("<f", expected, off, value)
            assert bytes(block) == expected, (mi, ci, q)
            cases.append({"matrix":matrix,"mode":mode,"input":{hex(k):v for k,v in config.items()},
                          "inverse_matrix_row3_z_reference":expected_z, "native_expf_arguments":[arg0,arg1],
                          "native_outputs":{hex(k):struct.unpack_from("<f", block,k)[0] for k in q}})
    return {"schema":"d1-atmosphere-general-native-oracle-v1", "sha256":EXPECTED_SHA256,
            "start_va":hex(start),"end_va":hex(end),"import_identity":identity,
            "substitution":"Only imported expf thunk replaced with logging stub tail-calling host libm.so.6 expf; retail libc rounding unvalidated",
            "contract":{"camera_scalar":"inverse(input_matrix)[3][2]","scattering_gain":"1.5*(1-g*g)/(2+g*g)",
                        "density_0xd4":"old*expf(min(64,(camera_scalar-channel_0xdc)*channel_0xd8*(-0.001)))",
                        "density_0xa4":"old*expf(min(64,(camera_scalar-channel_0xb4)*channel_0xb0*(-0.001)))",
                        "coefficient_clamps":"zero density resets associated coefficient to epsilon; then max(epsilon,coefficient)"},
            "source":[{"va":hex(i.address),"bytes":i.bytes.hex(),"mnemonic":i.mnemonic,"operands":i.op_str} for i in dis],
            "cases":cases,"all_native_outputs_match":True,
            "remaining":["map settings ownership","input matrix semantic owner","live channel evaluation","LUT contents","retail libc expf bitwise rounding","render validation"]}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("eboot", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    result = probe(args.eboot)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"cases":len(result["cases"]),"all_native_outputs_match":result["all_native_outputs_match"],"helper":result["import_identity"]["resolved_name"]}))
