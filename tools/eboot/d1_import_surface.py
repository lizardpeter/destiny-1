#!/usr/bin/env python3
"""Catalog the PS4 system-library surface Destiny 1 needs, and check it against shadPS4.

A static recompilation translates the game's own code (eboot.bin plus the
decrypted modules the game ships in sce_module/) and must reimplement every
function it imports from the console firmware. This tool lists that boundary:

  * every imported symbol (NID) of eboot.bin and of each game-shipped .prx,
    with its library/module, NID name, PLT stub and direct call-site count;
  * imports satisfied by another game-shipped module (libc -> libSceFios2 …)
    are marked `game_module` — they are recompiled, not reimplemented;
  * for the rest, whether a shadPS4 checkout registers it (LIB_FUNCTION /
    LIB_OBJ) and whether the registered body is trivial (a likely stub).

Inputs are local paths; nothing is downloaded. No game bytes are written.

    python tools/eboot/d1_import_surface.py \
        --eboot /path/eboot.bin --sce-module /path/sce_module \
        --shadps4 /path/shadPS4 --out evidence/generated/d1_import_surface.json

"Trivial" is a heuristic: a body that makes no calls besides logging and is
either marked STUBBED or at most three lines. It flags no-ops and stubs but also catches genuine one-line accessors
(e.g. returning &errno), so treat it as an upper bound on stubs.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import re
import struct
from pathlib import Path

ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-"
EXPECTED_EBOOT = "672f03411c0503dfbcda804cbb9fb27cdd9a8d73a8bcb71bf0c4f688073b0833"
DT_NEEDED_MODULE, DT_IMPORT_LIB, DT_EXPORT_LIB = 0x6100000F, 0x61000015, 0x61000013
DT_STRTAB, DT_SYMTAB, DT_SYMTABSZ = 0x61000035, 0x61000039, 0x6100003F
DT_JMPREL, DT_PLTRELSZ, DT_RELA, DT_RELASZ = 0x61000029, 0x6100002D, 0x6100002F, 0x61000031


def decode_id(s: str) -> int:
    v = 0
    for c in s:
        v = v * 64 + ALPHA.index(c)
    return v


class Module:
    def __init__(self, path: Path):
        d = path.read_bytes()
        self.path, self.sha256 = path, hashlib.sha256(d).hexdigest()
        if d[:4] != b"\x7fELF":
            raise ValueError(f"{path} is not a decrypted ELF")
        phoff, = struct.unpack_from("<Q", d, 0x20)
        phnum, = struct.unpack_from("<H", d, 0x38)
        loads, dyn, dlib = [], None, None
        for i in range(phnum):
            t, fl, off, va, pa, fs, ms, al = struct.unpack_from("<IIQQQQQQ", d, phoff + i * 56)
            if t == 1:
                loads.append((va, off, fs, ms, fl))
            elif t == 2:
                dyn = (off, fs)
            elif t == 0x61000000:
                dlib = off
        tags = collections.defaultdict(list)
        for i in range(0, dyn[1], 16):
            tag, val = struct.unpack_from("<qQ", d, dyn[0] + i)
            tags[tag & 0xFFFFFFFFFFFFFFFF].append(val)
        so = dlib + tags[DT_STRTAB][0]
        s = lambda o: d[so + o:d.index(b"\0", so + o)].decode("latin1")
        self.needed = {v >> 48: s(v & 0xFFFFFFFF) for v in tags[DT_NEEDED_MODULE]}
        self.libs = {v >> 48: s(v & 0xFFFFFFFF) for v in tags[DT_IMPORT_LIB]}
        self.exports = [s(v & 0xFFFFFFFF) for v in tags[DT_EXPORT_LIB]]
        syms = []
        sb = dlib + tags[DT_SYMTAB][0]
        for i in range(0, tags[DT_SYMTABSZ][0], 24):
            nm, info, oth, shndx, val, sz = struct.unpack_from("<IBBHQQ", d, sb + i)
            syms.append((s(nm), shndx, val))
        # executable image (first RX load) for stub/call scanning
        va, off, fs, ms, fl = next(l for l in loads if l[4] & 1)
        self.text_va, self.text = va, d[off:off + fs]
        self.slots = collections.defaultdict(list)  # symbol -> GOT slot VAs
        for start, size in ((tags[DT_RELA][0], tags[DT_RELASZ][0]), (tags[DT_JMPREL][0], tags[DT_PLTRELSZ][0])):
            for i in range(0, size, 24):
                off_, info, add = struct.unpack_from("<QQq", d, dlib + start + i)
                typ, si = info & 0xFFFFFFFF, info >> 32
                if typ in (1, 6, 7) and si < len(syms):
                    name, shndx, val = syms[si]
                    if not val and "#" in name:
                        self.slots[name].append(off_)

    def call_counts(self):
        """PLT stubs (jmp [rip+slot]) and E8 call sites into them."""
        slot_to_sym = {v: k for k, vs in self.slots.items() for v in vs}
        t, base = self.text, self.text_va
        stubs = {}
        for m in re.finditer(rb"\xff\x25", t):
            i = m.start()
            if i + 6 > len(t):
                continue
            disp, = struct.unpack_from("<i", t, i + 2)
            tgt = base + i + 6 + disp
            if tgt in slot_to_sym:
                stubs[base + i] = slot_to_sym[tgt]
        calls = collections.Counter()
        for m in re.finditer(rb"\xe8", t):
            i = m.start()
            if i + 5 > len(t):
                continue
            rel, = struct.unpack_from("<i", t, i + 1)
            tgt = base + i + 5 + rel
            if tgt in stubs:
                calls[stubs[tgt]] += 1
        per_sym = collections.defaultdict(list)
        for a, sym in stubs.items():
            per_sym[sym].append(a)
        return per_sym, calls


def load_nid_names(shad: Path) -> dict:
    names = {}
    for line in (shad / "src/core/aerolib/aerolib.inl").read_text(errors="ignore").splitlines():
        m = re.match(r'STUB\("([^"]+)",\s*([^)]+)\)', line)
        if m:
            names[m.group(1)] = m.group(2).strip()
    return names


class ShadCoverage:
    REG = re.compile(r'LIB_(FUNCTION|OBJ)\(\s*"([^"]+)"\s*,\s*"([^"]+)"\s*,\s*\d+\s*,\s*"([^"]+)"\s*,\s*([^)]+?)\s*\)', re.S)

    def __init__(self, shad: Path):
        self.src = {}
        for root, _, fs in os.walk(shad / "src/core/libraries"):
            for f in fs:
                if f.endswith((".cpp", ".h")):
                    p = os.path.join(root, f)
                    self.src[p] = open(p, errors="ignore").read()
        self.reg = collections.defaultdict(list)
        for p, t in self.src.items():
            for m in self.REG.finditer(t):
                fn = m.group(5).strip().replace("&", "").strip()
                self.reg[m.group(2)].append((m.group(1), m.group(3), fn, p))
        self.commit = None
        head = shad / ".git/HEAD"
        if head.exists():
            ref = head.read_text().strip()
            if ref.startswith("ref: ") and (shad / ".git" / ref[5:]).exists():
                self.commit = (shad / ".git" / ref[5:]).read_text().strip()
            elif not ref.startswith("ref: "):
                self.commit = ref

    def body(self, fn, prefer):
        rx = re.compile(r"\b" + re.escape(fn.split("::")[-1]) + r"\s*\([^;{]*\)\s*(?:noexcept\s*)?\{")
        for p in [prefer] + [q for q in self.src if q != prefer]:
            t = self.src[p]
            m = rx.search(t)
            if not m:
                continue
            i, depth = m.end(), 1
            while depth and i < len(t):
                depth += {"{": 1, "}": -1}.get(t[i], 0)
                i += 1
            return t[m.end():i - 1]
        return None

    def classify(self, nid, lib):
        regs = self.reg.get(nid, [])
        r = next((x for x in regs if x[1] == lib), regs[0] if regs else None)
        if not r:
            return "missing", None
        kind, _, fn, p = r
        if kind == "OBJ" or fn.startswith("ORBIS("):
            return "implemented", fn
        b = self.body(fn, p)
        if b is None:
            return "implemented", fn
        lines = [x.strip() for x in b.splitlines() if x.strip() and not x.strip().startswith("//")]
        calls = [c for x in lines if not x.startswith("LOG_")
                 for c in re.findall(r"\b([A-Za-z_][\w:]*)\s*\(", x)
                 if c not in ("return", "sizeof", "static_cast", "reinterpret_cast", "if", "fmt::ptr")]
        if not calls and ("STUBBED" in b or len(lines) <= 3):
            return "trivial", fn
        return "implemented", fn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eboot", type=Path, required=True)
    ap.add_argument("--sce-module", type=Path)
    ap.add_argument("--shadps4", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    mods = [Module(a.eboot)]
    if mods[0].sha256 != EXPECTED_EBOOT:
        print(f"warning: eboot sha256 {mods[0].sha256} is not the 01.33 reference")
    if a.sce_module:
        mods += [Module(p) for p in sorted(a.sce_module.glob("*.prx")) + sorted(a.sce_module.glob("*.sprx"))]
    game_libs = {lib for m in mods for lib in m.exports}
    names = load_nid_names(a.shadps4)
    cov = ShadCoverage(a.shadps4)

    out_mods, rows = [], []
    for m in mods:
        per_sym, calls = m.call_counts()
        out_mods.append({"file": m.path.name, "sha256": m.sha256, "exports": m.exports,
                         "needed_modules": sorted(set(m.needed.values())), "import_libraries": sorted(set(m.libs.values()))})
        for sym in sorted(m.slots):
            nid, l, mm = sym.split("#")
            lib = m.libs.get(decode_id(l), f"?{decode_id(l)}")
            module = m.needed.get(decode_id(mm), f"?{decode_id(mm)}")
            if lib in game_libs:
                status, fn = "game_module", None
            else:
                status, fn = cov.classify(nid, lib)
            rows.append({"importer": m.path.name, "nid": nid, "name": names.get(nid), "library": lib, "module": module,
                         "plt_stubs": [hex(x) for x in per_sym.get(sym, [])], "call_sites": calls.get(sym, 0),
                         "status": status, "shadps4_symbol": fn})

    def summarize(sel):
        s = collections.defaultdict(lambda: {"imports": collections.Counter(), "call_sites": collections.Counter()})
        for r in sel:
            s[r["library"]]["imports"][r["status"]] += 1
            s[r["library"]]["call_sites"][r["status"]] += r["call_sites"]
        return {k: {"imports": dict(v["imports"]), "call_sites": dict(v["call_sites"])}
                for k, v in sorted(s.items(), key=lambda kv: -sum(kv[1]["call_sites"].values()))}

    firmware = [r for r in rows if r["status"] != "game_module"]
    unique = {}
    for r in firmware:
        unique.setdefault((r["library"], r["nid"]), r)
    totals = collections.Counter(r["status"] for r in unique.values())
    result = {
        "schema": "d1_import_surface/v1",
        "modules": out_mods,
        "game_shipped_libraries": sorted(game_libs),
        "shadps4_commit": cov.commit,
        "firmware_surface": {
            "unique_imports": len(unique),
            "by_status": dict(totals),
            "call_sites": dict(collections.Counter({s: sum(r["call_sites"] for r in firmware if r["status"] == s) for s in totals})),
            "by_library": summarize(firmware),
        },
        "missing": sorted(({"library": r["library"], "name": r["name"], "nid": r["nid"], "importer": r["importer"],
                            "call_sites": r["call_sites"]} for r in firmware if r["status"] == "missing"),
                          key=lambda r: (-r["call_sites"], r["library"])),
        "imports": rows,
        "notes": [
            "call_sites counts direct E8 calls into PLT stubs; calls through function pointers or GOT loads are not counted.",
            "status 'trivial' is a heuristic upper bound on stubs (also matches one-line accessors).",
            "game_module imports are satisfied by a decrypted module the game ships and are recompiled with the game.",
        ],
    }
    a.out.write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result["firmware_surface"]["by_status"]), "unique firmware imports:", len(unique))


if __name__ == "__main__":
    main()
