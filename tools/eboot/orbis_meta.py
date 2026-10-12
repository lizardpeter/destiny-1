#!/usr/bin/env python3
"""Extract Orbis (PS4) ELF metadata the stock ELF loader ignores.

Outputs (TSV, addresses are eboot virtual addresses, hex):
  functions.tsv  start  size            -- from .eh_frame_hdr / FDEs (exact bounds)
  imports.tsv    got_slot  nid  lib  name   -- JMPREL (PLT) imports, NID resolved
  relocs.tsv     where  type  sym/addend    -- full SCE RELA table
  libs.tsv       index  name  kind          -- needed libraries / modules

usage: orbis_meta.py EBOOT AEROLIB_INL OUTDIR
"""
import os, re, struct, sys

def main(eboot, aerolib, out):
    d = open(eboot, 'rb').read()
    os.makedirs(out, exist_ok=True)
    phoff, = struct.unpack_from('<Q', d, 0x20)
    phnum, = struct.unpack_from('<H', d, 0x38)
    phs = [struct.unpack_from('<IIQQQQQQ', d, phoff + i * 56) for i in range(phnum)]
    loads = [p for p in phs if p[0] == 1]
    dyn = next(p for p in phs if p[0] == 2)
    dynlib = next(p for p in phs if p[0] == 0x61000000)
    eh = next(p for p in phs if p[0] == 0x6474E550)

    def v2o(va):
        for p in loads:
            if p[3] <= va < p[3] + p[6]:
                return va - p[3] + p[2]
        raise ValueError(hex(va))

    # ---- functions from eh_frame_hdr
    off, hv = eh[2], eh[3]
    n, = struct.unpack_from('<I', d, off + 8)
    funcs = []
    for i in range(n):
        loc, fde = struct.unpack_from('<ii', d, off + 12 + i * 8)
        fo = v2o(hv + fde)
        pcbeg, pcr = struct.unpack_from('<iI', d, fo + 8)
        start = hv + fde + 8 + pcbeg
        assert start == hv + loc, (hex(start), hex(hv + loc))
        funcs.append((start, pcr))
    funcs.sort()
    with open(f'{out}/functions.tsv', 'w') as f:
        f.writelines(f'{s:x}\t{z:x}\n' for s, z in funcs)

    # ---- dynamic tags
    tags = {}
    needed, modules, libs = [], [], []
    for i in range(dyn[5] // 16):
        t, v = struct.unpack_from('<qQ', d, dyn[2] + i * 16)
        if t == 0:
            break
        if t == 1: needed.append(v)
        elif t in (0x6100000D, 0x61000049): modules.append(v)  # NEEDED/IMPORT_MODULE
        elif t in (0x6100000F, 0x61000013, 0x61000015, 0x61000017, 0x61000019, 0x6100001B, 0x6100001D, 0x6100001F, 0x61000021, 0x61000023, 0x61000025 - 0): pass
        tags.setdefault(t, v)
        if t in (0x61000015, 0x61000017, 0x61000013, 0x61000011):  # export/import lib
            libs.append((t, v))
    base = dynlib[2]
    stro, strsz = tags[0x61000035], tags[0x61000037]
    syo, sysz = tags[0x61000039], tags[0x6100003F]
    jro, jrsz = tags[0x61000029], tags[0x6100002D]
    rao, rasz = tags[0x6100002F], tags[0x61000031]
    strtab = d[base + stro: base + stro + strsz]
    cstr = lambda o: strtab[o:strtab.index(b'\0', o)].decode()

    # library id -> name (lib entries carry name offset in low 32 bits, id in top 16)
    libname = {}
    for t, v in libs:
        libname[(v >> 48) & 0xFFFF] = cstr(v & 0xFFFFFFFF)
    with open(f'{out}/libs.tsv', 'w') as f:
        for k, v in sorted(libname.items()):
            f.write(f'{k}\t{v}\n')

    syms = []
    for i in range(sysz // 24):
        nm, info, oth, shn, val, sz = struct.unpack_from('<IBBHQQ', d, base + syo + i * 24)
        syms.append((cstr(nm), info, val))

    nidmap = {}
    for m in re.finditer(r'STUB\("([^"]+)",\s*([^)]+)\)', open(aerolib).read()):
        nidmap[m.group(1)] = m.group(2).strip()
    b64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-'

    def decode(sym):
        p = sym.split('#')
        nid = p[0]
        lib = libname.get(sum(b64.index(c) << (6 * (len(p[1]) - 1 - k)) for k, c in enumerate(p[1])), p[1]) if len(p) > 1 else ''
        return nid, lib, nidmap.get(nid, '')

    resolved = 0
    with open(f'{out}/imports.tsv', 'w') as f:
        for i in range(jrsz // 24):
            r_off, r_info, add = struct.unpack_from('<QQq', d, base + jro + i * 24)
            nm = syms[r_info >> 32][0]
            nid, lib, name = decode(nm)
            resolved += bool(name)
            f.write(f'{r_off:x}\t{nid}\t{lib}\t{name}\n')
    nimp = jrsz // 24
    types = {}
    with open(f'{out}/relocs.tsv', 'w') as f:
        for i in range(rasz // 24):
            r_off, r_info, add = struct.unpack_from('<QQq', d, base + rao + i * 24)
            t = r_info & 0xFFFFFFFF
            types[t] = types.get(t, 0) + 1
            s = r_info >> 32
            tgt = decode(syms[s][0])[2] or syms[s][0] if s else ''
            f.write(f'{r_off:x}\t{t}\t{add & 0xFFFFFFFFFFFFFFFF:x}\t{tgt}\n')
    print(f'functions={len(funcs)} imports={nimp} resolved={resolved} relocs={rasz // 24} types={types} libs={len(libname)}')


if __name__ == '__main__':
    main(*sys.argv[1:4])
