#!/usr/bin/env python3
"""List the executable's imports: one row per address the dynamic linker writes an imported symbol into.

    python3 tools/ghidra/imports.py <eboot.elf> <out imports.tsv>

A PS4 executable keeps its dynamic tables in the SCE dynlib segment (program header type 0x61000000), which
Ghidra does not read, and names every import by NID (a hash) instead of by name. This reads the relocation
tables from that segment and resolves NIDs with evidence/generated/d1_import_surface.json.
ApplyImports.java labels the slots and their jump stubs from the result, so pseudocode shows memcpy and
sceKernelMapDirectMemory instead of anonymous pointers.
"""
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PT_DYNAMIC, PT_SCE_DYNLIBDATA = 2, 0x61000000
DT_SCE_JMPREL, DT_SCE_PLTRELSZ = 0x61000029, 0x6100002D
DT_SCE_RELA, DT_SCE_RELASZ = 0x6100002F, 0x61000031
DT_SCE_STRTAB, DT_SCE_SYMTAB, DT_SCE_SYMTABSZ = 0x61000035, 0x61000039, 0x6100003F


def main():
    d = Path(sys.argv[1]).read_bytes()
    phoff, = struct.unpack_from("<Q", d, 0x20)
    phentsize, phnum = struct.unpack_from("<HH", d, 0x36)
    dyn = dlib = None
    for i in range(phnum):
        t, _fl, off, _va, _pa, fsz, _msz, _al = struct.unpack_from("<IIQQQQQQ", d, phoff + i * phentsize)
        if t == PT_DYNAMIC:
            dyn = (off, fsz)
        if t == PT_SCE_DYNLIBDATA:
            dlib = off
    if dyn is None or dlib is None:
        sys.exit("no dynamic table or SCE dynlib segment")
    tags = {}
    for o in range(dyn[0], dyn[0] + dyn[1], 16):
        t, v = struct.unpack_from("<qQ", d, o)
        tags.setdefault(t, v)
    strtab, symtab = dlib + tags[DT_SCE_STRTAB], dlib + tags[DT_SCE_SYMTAB]

    def cstr(o):
        return d[o:d.index(b"\0", o)].decode("latin1")

    syms = []
    for o in range(0, tags[DT_SCE_SYMTABSZ], 24):
        name, = struct.unpack_from("<I", d, symtab + o)
        syms.append(cstr(strtab + name))
    known = {r["nid"]: r for r in json.loads(
        (ROOT / "evidence/generated/d1_import_surface.json").read_text())["imports"]}

    rows = []
    for table, size, kind in ((DT_SCE_RELA, DT_SCE_RELASZ, "data"), (DT_SCE_JMPREL, DT_SCE_PLTRELSZ, "plt")):
        base = dlib + tags[table]
        for o in range(0, tags[size], 24):
            off, info, _add = struct.unpack_from("<QQq", d, base + o)
            si = info >> 32
            if not si or si >= len(syms):
                continue  # relative relocation, no symbol
            nid = syms[si].split("#")[0]
            k = known.get(nid, {})
            rows.append((off, kind, nid, k.get("library") or "", k.get("name") or ""))
    rows.sort()
    with open(sys.argv[2], "w", newline="\n") as f:
        f.write("slot_va\ttable\tnid\tlibrary\tname\n")
        for off, kind, nid, lib, name in rows:
            f.write(f"{off:08x}\t{kind}\t{nid}\t{lib}\t{name}\n")
    named = sum(1 for r in rows if r[4])
    print(f"imports: {len(rows)} slots, {len({r[2] for r in rows})} symbols, {named} slots named")


if __name__ == "__main__":
    main()
