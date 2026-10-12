#!/usr/bin/env python3
"""Census of x86-64 instructions in D1's game code that matter when running it on a PC.

The PS4 CPU (AMD Jaguar) is x86-64, so the game's code can run natively on a PC
host; a "recompilation" is mostly relinking plus patching what differs between
the console and the host. This tool linear-sweeps the executable segment of
eboot.bin and of the game-shipped sce_module/*.prx files and counts:

  * sse4a        EXTRQ / INSERTQ / MOVNTSS / MOVNTSD — AMD-only, fault on Intel;
  * approx       RCPPS / RSQRTPS / RCPSS / RSQRTSS (+ VEX forms) — results differ
                 bit-for-bit between AMD and Intel;
  * fs_tcb       `mov r64, fs:[0]` — PS4 thread control block access;
  * fs_other     any other FS-segment operand;
  * system       SYSCALL / INT / RDTSC / RDTSCP / CPUID / XGETBV / RDRAND;
  * isa          extensions the host must have: AVX (VEX encodings), F16C, BMI1,
                 LZCNT, POPCNT, MOVBE, AES-NI, PCLMULQDQ — and ones Jaguar lacks
                 (AVX2, FMA3/FMA4, XOP, TBM), which should be zero; a non-zero
                 value there means the sweep decoded data as code;
  * indirect     calls/jumps through a register or memory operand.

Coverage against shadPS4 comes from `src/core/cpu_patches.cpp` (its patch table).

    python tools/eboot/d1_x86_portability_census.py --eboot eboot.bin \
        --sce-module sce_module --shadps4 /path/shadPS4 --out evidence/generated/d1_x86_portability.json
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import struct
from pathlib import Path

from capstone import CS_ARCH_X86, CS_MODE_64, Cs

SSE4A = {"extrq", "insertq", "movntss", "movntsd"}
APPROX = {"rcpps", "rsqrtps", "rcpss", "rsqrtss", "vrcpps", "vrsqrtps", "vrcpss", "vrsqrtss"}
SYSTEM = {"syscall", "int", "int3", "rdtsc", "rdtscp", "cpuid", "xgetbv", "rdrand", "rdseed", "hlt", "ud2"}
F16C = {"vcvtph2ps", "vcvtps2ph"}
BMI1 = {"andn", "bextr", "blsi", "blsmsk", "blsr", "tzcnt"}
BMI2 = {"bzhi", "mulx", "pdep", "pext", "rorx", "sarx", "shlx", "shrx"}
AES = {"aesenc", "aesenclast", "aesdec", "aesdeclast", "aesimc", "aeskeygenassist",
       "vaesenc", "vaesenclast", "vaesdec", "vaesdeclast", "vaesimc", "vaeskeygenassist"}
CLMUL = {"pclmulqdq", "vpclmulqdq"}
AVX2_ONLY = {"vpbroadcastb", "vpbroadcastw", "vpbroadcastd", "vpbroadcastq", "vbroadcasti128", "vperm2i128",
             "vpermd", "vpermq", "vpermps", "vpermpd", "vinserti128", "vextracti128", "vpmaskmovd",
             "vpmaskmovq", "vpsllvd", "vpsllvq", "vpsravd", "vpsrlvd", "vpsrlvq", "vpgatherdd", "vgatherdps"}
XOP_PREFIX = ("vpcmov", "vpperm", "vprot", "vpsha", "vpshl", "vfrcz", "vpmacs", "vpmadcs", "vphadd", "vphsub",
              "vpcom")


def exec_segment(path: Path):
    """Return (sha256, text_va, text_bytes, eh_frame_hdr_va)."""
    d = path.read_bytes()
    phoff, = struct.unpack_from("<Q", d, 0x20)
    phnum, = struct.unpack_from("<H", d, 0x38)
    seg, ehdr = None, None
    for i in range(phnum):
        t, fl, off, va, pa, fs, ms, al = struct.unpack_from("<IIQQQQQQ", d, phoff + i * 56)
        if t == 1 and fl & 1 and seg is None:
            seg = (va, d[off:off + fs])
        elif t == 0x6474E550:
            ehdr = va
    if seg is None:
        raise ValueError(f"{path}: no executable segment")
    return hashlib.sha256(d).hexdigest(), seg[0], seg[1], ehdr


def _uleb(b, o):
    v = s = 0
    while True:
        x = b[o]; o += 1; v |= (x & 0x7F) << s; s += 7
        if x < 0x80:
            return v, o


def _sleb(b, o):
    v = s = 0
    while True:
        x = b[o]; o += 1; v |= (x & 0x7F) << s; s += 7
        if x < 0x80:
            if x & 0x40:
                v -= 1 << s
            return v, o


def _enc(b, o, enc, base_va, data_va=0):
    """Read a DW_EH_PE-encoded pointer at offset o (va = base_va + o)."""
    fmt = enc & 0x0F
    size = {0x00: 8, 0x02: 2, 0x03: 4, 0x04: 8, 0x0A: 2, 0x0B: 4, 0x0C: 8}[fmt]
    code = {0x00: "<Q", 0x02: "<H", 0x03: "<I", 0x04: "<Q", 0x0A: "<h", 0x0B: "<i", 0x0C: "<q"}[fmt]
    v, = struct.unpack_from(code, b, o)
    app = enc & 0x70
    if app == 0x10:
        v += base_va + o
    elif app == 0x30:
        v += data_va
    return v & 0xFFFFFFFFFFFFFFFF, o + size


def functions_from_eh(base: int, seg: bytes, ehdr_va: int):
    """Function (start, length) pairs from .eh_frame_hdr's sorted FDE table."""
    o = ehdr_va - base
    ver, ptr_enc, cnt_enc, tab_enc = seg[o:o + 4]
    _, p = _enc(seg, o + 4, ptr_enc, base)
    count, p = _enc(seg, p, cnt_enc, base)
    cie_cache, out = {}, []
    for i in range(count):
        _, p = _enc(seg, p, tab_enc, base, ehdr_va)
        fde_va, p = _enc(seg, p, tab_enc, base, ehdr_va)
        f = fde_va - base
        length, = struct.unpack_from("<I", seg, f)
        cie_ptr, = struct.unpack_from("<I", seg, f + 4)
        cie = f + 4 - cie_ptr
        if cie not in cie_cache:
            q = cie + 9  # length(4) id(4) version(1)
            aug_end = seg.index(b"\0", q)
            aug = seg[q:aug_end].decode("latin1"); q = aug_end + 1
            _, q = _uleb(seg, q); _, q = _sleb(seg, q); _, q = _uleb(seg, q)  # code align, data align, RA
            renc = 0
            if aug.startswith("z"):
                _, q = _uleb(seg, q)
                for ch in aug[1:]:
                    if ch == "R":
                        renc = seg[q]; q += 1
                    elif ch == "P":
                        penc = seg[q]; q += 1
                        _, q = _enc(seg, q, penc, base)
                    elif ch == "L":
                        q += 1
            cie_cache[cie] = renc
        renc = cie_cache[cie]
        start, q = _enc(seg, f + 8, renc, base)
        rng, _ = _enc(seg, q, renc & 0x0F, base)
        out.append((start, rng))
    return out


def code_end(text: bytes) -> int:
    """End of the PLT, which follows the last function; the rest of the RX segment is .rodata."""
    plt = re.compile(rb"\xff\x25....\x68....\xe9....", re.S)
    last = None
    for m in plt.finditer(text):
        if last is None or m.start() == last + 16:
            last = m.start()
        elif m.start() > last + 16 and last is not None and m.start() - last > 0x1000:
            break
    return (last + 16) if last is not None else len(text)


def jump_tables(text: bytes, base: int, end: int):
    """clang relative jump tables placed inside .text: lea rT,[rip+tab]; movsxd rX,[rT+rI*4]; add rX,rT; jmp rX.
    Returns [(start, end)] offsets of table bytes so the sweep can skip them."""
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    lea = re.compile(r"(r\w+), \[rip ([+-]) (0x[0-9a-f]+)\]")
    spans = []
    for m in re.finditer(rb"[\x48-\x4f]\x63[\x04\x0c\x14\x1c\x24\x2c\x34\x3c][\x80-\xbf]", text[:end]):
        a = m.start()
        tab = None
        for back in range(7, 40):
            for addr, size, mn, ops in md.disasm_lite(text[a - back:a], base + a - back):
                if mn == "lea":
                    q = lea.fullmatch(ops)
                    if q:
                        disp = int(q.group(3), 16) * (1 if q.group(2) == "+" else -1)
                        tab = addr + size + disp - base
            if tab is not None:
                break
        if tab is None or not (0 <= tab < end):
            continue
        n = 0
        while tab + 4 * n + 4 <= end and n < 4096:
            v, = struct.unpack_from("<i", text, tab + 4 * n)
            if not (-0x40000 < v < 0):  # clang places the table after the targets it jumps to
                break
            n += 1
        if n:
            spans.append((tab, tab + 4 * n))
    return spans


def census(base: int, text: bytes, funcs=None):
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    md.skipdata = True
    if funcs:
        return census_funcs(md, base, text, funcs)
    end = code_end(text)
    spans = sorted(jump_tables(text, base, end))
    table_bytes = sum(e - s for s, e in spans)
    # sweep each code run between jump tables
    runs, pos = [], 0
    for s, e in spans:
        if s > pos:
            runs.append((pos, s))
        pos = max(pos, e)
    runs.append((pos, end))
    return sweep(md, base, text, runs, {"code_bytes": end, "jump_tables": len(spans), "jump_table_bytes": table_bytes,
                                        "method": "linear sweep of code region minus jump tables"})


def census_funcs(md, base, text, funcs):
    franges = sorted({(s - base, s - base + n) for s, n in funcs if 0 <= s - base < len(text) and n > 0})
    end = max(e for _, e in franges)
    spans = sorted(jump_tables(text, base, end))
    runs = []
    j = 0
    for s, e in franges:  # subtract jump-table bytes that clang placed inside function ranges
        cur = s
        while j < len(spans) and spans[j][1] <= s:
            j += 1
        k = j
        while k < len(spans) and spans[k][0] < e:
            ts, te = spans[k]
            if ts > cur:
                runs.append((cur, ts))
            cur = max(cur, te)
            k += 1
        if cur < e:
            runs.append((cur, e))
    return sweep(md, base, text, runs, {"functions": len(franges), "function_bytes": sum(e - s for s, e in franges),
                                        "jump_tables": len(spans), "jump_table_bytes": sum(e - s for s, e in spans),
                                        "method": "per-function ranges from .eh_frame_hdr minus in-text jump tables"})


def sweep(md, base, text, runs, layout):
    c = collections.Counter()
    samples = collections.defaultdict(list)
    vex_mn = collections.Counter()
    decoded = skipped = 0
    for rs, re_ in runs:
        for addr, size, mn, ops in md.disasm_lite(text[rs:re_], base + rs):
            if mn == ".byte":
                skipped += size
                continue
            decoded += size
            cat = None
            if mn in SSE4A:
                cat = "sse4a"
            elif mn in APPROX:
                cat = "approx:" + mn
            elif "fs:" in ops:
                cat = "fs_tcb" if mn == "mov" and re.fullmatch(r"r\w+, qword ptr fs:\[0\]", ops) else "fs_other"
            elif mn in SYSTEM:
                cat = "system:" + mn
            elif mn in F16C:
                cat = "isa:f16c"
            elif mn in BMI1:
                cat = "isa:bmi1:" + mn
            elif mn in BMI2:
                cat = "isa:bmi2 (not on Jaguar)"
            elif mn == "lzcnt":
                cat = "isa:lzcnt"
            elif mn == "popcnt":
                cat = "isa:popcnt"
            elif mn == "movbe":
                cat = "isa:movbe"
            elif mn in AES:
                cat = "isa:aes"
            elif mn in CLMUL:
                cat = "isa:pclmul"
            elif mn in AVX2_ONLY or (mn.startswith("vfmadd") or mn.startswith("vfmsub") or mn.startswith("vfnmadd")
                                    or mn.startswith("vfnmsub")):
                cat = "isa:avx2/fma3 (not on Jaguar)"
            elif mn.startswith(XOP_PREFIX):
                cat = "isa:xop (not on Jaguar)"
            elif mn in ("call", "jmp") and not re.fullmatch(r"0x[0-9a-f]+", ops):
                cat = f"indirect:{mn}"
            if mn.startswith("v") and "ymm" in ops or (mn.startswith("v") and "xmm" in ops):
                vex_mn["vex"] += 1
            if cat:
                c[cat] += 1
                if len(samples[cat]) < 5:
                    samples[cat].append(f"{addr:#x}: {mn} {ops}")
    c["isa:avx (vex-encoded)"] = vex_mn["vex"]
    return c, samples, decoded, skipped, layout


def shad_patches(shad: Path) -> set[str]:
    t = (shad / "src/core/cpu_patches.cpp").read_text(errors="ignore")
    m = re.search(r"Patches\s*=\s*\{(.*?)\n\};", t, re.S)
    return {x.lower() for x in re.findall(r"ZYDIS_MNEMONIC_([A-Z0-9]+)", m.group(1))} if m else set()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eboot", type=Path, required=True)
    ap.add_argument("--sce-module", type=Path)
    ap.add_argument("--shadps4", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    files = [a.eboot] + (sorted(a.sce_module.glob("*.prx")) if a.sce_module else [])
    patched = shad_patches(a.shadps4) if a.shadps4 else set()
    out = {"schema": "d1_x86_portability/v1", "modules": [], "shadps4_patched_mnemonics": sorted(patched)}
    total = collections.Counter()
    for f in files:
        sha, base, text, ehdr = exec_segment(f)
        funcs = functions_from_eh(base, text, ehdr) if ehdr is not None else None
        c, samples, dec, skip, layout = census(base, text, funcs)
        total.update(c)
        out["modules"].append({"file": f.name, "sha256": sha, "text_bytes": len(text), **layout, "decoded_bytes": dec,
                               "undecodable_bytes": skip, "counts": dict(sorted(c.items())), "samples": samples})
        print(f.name, json.dumps(dict(sorted(c.items()))))
    out["total"] = dict(sorted(total.items()))
    out["notes"] = [
        "Linear sweep: bytes inside code that are really data can decode as instructions; the 'not on Jaguar' rows act as a canary for that.",
        "fs_tcb is the PS4 TLS/TCB idiom shadPS4 rewrites; fs_other are other FS-relative operands.",
        "approx instructions run on any x86 host but give different low bits on Intel than on the PS4's AMD CPU.",
    ]
    a.out.write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
