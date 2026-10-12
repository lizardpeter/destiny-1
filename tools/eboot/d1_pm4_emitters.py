#!/usr/bin/env python3
"""Find the PM4 packets Destiny 1's eboot can emit and check them against shadPS4.

Destiny imports only ~15 libSceGnmDriver functions; command buffers are built by
Sony's Gnm user-mode library linked statically into eboot.bin. Its builder
functions write PM4 type-3 headers as immediates:

    0xC0000000 | (count << 16) | (IT_OPCODE << 8) | (shader_type << 1) | predicate

This tool linear-sweeps the executable text with capstone, keeps immediates that
look like type-3 headers with a small count (also the low/high halves of
`movabs`), and keeps only functions inside the Gnm builder ranges (located by
the dense cluster of IT_SET_CONTEXT_REG headers). Each builder is listed with
the opcodes it writes and its direct E8 callers.

shadPS4 coverage is read from `src/video_core/amdgpu/liverpool.cpp`: an opcode
is `handled` if it has a `case PM4ItOpcode::X:` in the graphics or constant-engine
processors, `warn_only` if that case only logs "Unimplemented"/"unhandled", and
`fatal` otherwise (the processors hit UNREACHABLE on unknown type-3 opcodes).

    python tools/eboot/d1_pm4_emitters.py --eboot /path/eboot.bin \
        --shadps4 /path/shadPS4 --out evidence/generated/d1_pm4_emitters.json
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import struct
from pathlib import Path

from capstone import CS_ARCH_X86, CS_MODE_64, Cs

EXPECTED_EBOOT = "672f03411c0503dfbcda804cbb9fb27cdd9a8d73a8bcb71bf0c4f688073b0833"


def text_segment(d: bytes):
    phoff, = struct.unpack_from("<Q", d, 0x20)
    phnum, = struct.unpack_from("<H", d, 0x38)
    for i in range(phnum):
        t, fl, off, va, pa, fs, ms, al = struct.unpack_from("<IIQQQQQQ", d, phoff + i * 56)
        if t == 1 and fl & 1:
            return va, d[off:off + fs]
    raise ValueError("no executable segment")


def func_start(text: bytes, base: int, addr: int, maxback=0x8000):
    a = (addr - base) & ~0xF
    while a >= 0 and a > addr - base - maxback:
        if text[a:a + 4] == b"\x55\x48\x89\xe5":
            return base + a
        a -= 0x10
    return None


def opcode_names(shad: Path) -> dict[int, str]:
    t = (shad / "src/video_core/amdgpu/pm4_opcodes.h").read_text(errors="ignore")
    out = {}
    for name, val in re.findall(r"^\s*([A-Za-z0-9]+)\s*=\s*(0x[0-9A-Fa-f]+)\s*,", t, re.M):
        out.setdefault(int(val, 16), name)
    return out


def shad_handling(shad: Path) -> dict[str, str]:
    t = (shad / "src/video_core/amdgpu/liverpool.cpp").read_text(errors="ignore")
    out = {}
    for m in re.finditer(r"case PM4ItOpcode::(\w+):\s*\{?(.*?)(?=case PM4ItOpcode::|default:)", t, re.S):
        name, body = m.group(1), m.group(2)
        warn = re.search(r'LOG_WARNING\([^;]*"(Unimplemented|unhandled)', body) and body.count(";") <= 4
        if out.get(name) != "handled":
            out[name] = "warn_only" if warn else "handled"
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eboot", type=Path, required=True)
    ap.add_argument("--shadps4", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    d = a.eboot.read_bytes()
    base, text = text_segment(d)
    names = opcode_names(a.shadps4)
    handling = shad_handling(a.shadps4)

    md = Cs(CS_ARCH_X86, CS_MODE_64)
    md.skipdata = True
    rx = re.compile(r"(?<![-\w])0x([0-9a-f]+)")
    hits = []
    step = 0x100000
    for off in range(0, len(text), step):
        for addr, size, mn, ops in md.disasm_lite(text[off:off + step + 16], base + off):
            if addr >= base + off + step:
                break
            if "0x" not in ops or mn.startswith("j") or mn == "call" or "-0x" in ops:
                continue
            if mn not in ("mov", "movabs", "or", "lea", "add"):
                continue
            for h in rx.findall(ops):
                v = int(h, 16)
                for w in ([v & 0xFFFFFFFF, v >> 32] if v > 0xFFFFFFFF else [v]):
                    op, cnt = (w >> 8) & 0xFF, (w >> 16) & 0x3FFF
                    if (w >> 30) == 3 and (w & 0xFC) == 0 and cnt < 0x400 and op in names:
                        hits.append((addr, op, cnt))

    # Gnm builder ranges: 64 KiB windows dense in SET_CONTEXT_REG headers, plus their neighbours
    dense = collections.Counter(addr >> 16 for addr, op, _ in hits if op == 0x69)
    windows = {w for w, n in dense.items() if n >= 8}
    windows |= {w + 1 for w in windows} | {w - 1 for w in windows}

    # direct call index (E8 rel32) for caller counts
    callers = collections.defaultdict(list)
    for m in re.finditer(rb"\xe8", text):
        i = m.start()
        if i + 5 <= len(text):
            rel, = struct.unpack_from("<i", text, i + 1)
            callers[base + i + 5 + rel].append(base + i)

    builders = collections.defaultdict(lambda: {"opcodes": set()})
    stray = collections.Counter()
    for addr, op, cnt in hits:
        if (addr >> 16) in windows:
            f = func_start(text, base, addr)
            builders[f]["opcodes"].add(names[op])
        else:
            stray[names[op]] += 1
    # constant-engine builders live apart from the draw builders; include any function writing
    # CE-only opcodes even outside the dense windows
    ce_ops = {0x81, 0x83, 0x84, 0x86, 0x88}
    for addr, op, cnt in hits:
        if op in ce_ops and (addr >> 16) not in windows:
            f = func_start(text, base, addr)
            builders[f]["opcodes"].add(names[op])

    rows = []
    for f, b in sorted(builders.items(), key=lambda kv: kv[0] or 0):
        c = callers.get(f, [])
        rows.append({"function": hex(f) if f else None, "opcodes": sorted(b["opcodes"]), "direct_callers": len(c),
                     "caller_sample": [hex(x) for x in c[:6]]})
    emitted = collections.defaultdict(lambda: {"builders": 0, "called_builders": 0})
    for r in rows:
        for o in r["opcodes"]:
            emitted[o]["builders"] += 1
            emitted[o]["called_builders"] += r["direct_callers"] > 0
    summary = []
    for o, v in sorted(emitted.items()):
        summary.append({"opcode": o, **v, "shadps4": handling.get(o, "fatal")})
    result = {
        "schema": "d1_pm4_emitters/v1",
        "gnm_windows": [hex(w << 16) for w in sorted(windows)],
        "opcodes": summary,
        "builders": rows,
        "notes": [
            "Opcodes are recovered from immediate header constants; packets whose opcode is computed at run time would be missed.",
            "direct_callers counts E8 calls only; builders reached through pointers or tail jumps show 0.",
            "shadps4 status is per opcode. Sub-mode asserts inside a handled opcode (e.g. DMA_DATA src/dst combinations) are checked separately in findings/LOG.md.",
        ],
    }
    a.out.write_text(json.dumps(result, indent=1) + "\n")
    for s in summary:
        print(f"{s['opcode']:22s} builders {s['builders']:3d} called {s['called_builders']:3d}  shadPS4 {s['shadps4']}")


if __name__ == "__main__":
    main()
