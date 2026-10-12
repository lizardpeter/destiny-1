#!/usr/bin/env python3
"""Recover Itanium C++ RTTI: classes, base classes and vtables (with virtual slots).

Pointers in the PIE eboot live in the SCE RELA table, so we read them from relocs.tsv
(RELATIVE: addend is the target VA; R_X86_64_64: named import symbol).

usage: rtti.py EBOOT META_DIR OUT_DIR
writes classes.tsv, bases.tsv, vtables.tsv (vtable_va, class, slot, target_va)
"""
import os, struct, subprocess, sys

def main(eboot, meta, out):
    d = open(eboot, 'rb').read()
    os.makedirs(out, exist_ok=True)
    rel, sym = {}, {}
    for ln in open(f'{meta}/relocs.tsv'):
        w, t, add, s = ln.rstrip('\n').split('\t')
        w = int(w, 16)
        if t == '8':
            rel[w] = int(add, 16)
        elif t == '1':
            sym[w] = s
    funcs = {}
    for ln in open(f'{meta}/functions.tsv'):
        s, z = ln.split()
        funcs[int(s, 16)] = int(z, 16)
    TEXT_END = 0x12aa720

    def cstr(va):
        o = va + 0x4000
        return d[o:d.index(b'\0', o)].decode('latin1')

    kinds = {}
    for w, s in sym.items():
        if 'class_type_info' in s:
            kind = 'si' if '__si_' in s else 'vmi' if '__vmi_' in s else 'base'
            kinds[w] = kind
    classes, bases = {}, []
    for ti, kind in kinds.items():
        if ti + 8 not in rel:
            continue
        mangled = cstr(rel[ti + 8])
        classes[ti] = (mangled, kind)
    names = {}
    try:
        dem = subprocess.run(['c++filt', '-t'], input='\n'.join(m for m, _ in classes.values()),
                             capture_output=True, text=True).stdout.split('\n')
        for (ti, (m, k)), n in zip(classes.items(), dem):
            names[ti] = n
    except FileNotFoundError:
        names = {ti: m for ti, (m, k) in classes.items()}
    for ti, (m, kind) in classes.items():
        if kind == 'si' and ti + 16 in rel:
            bases.append((ti, rel[ti + 16], 0, 'public'))
        elif kind == 'vmi':
            flags, cnt = struct.unpack_from('<II', d, ti + 16 + 0x4000)
            for i in range(cnt):
                p = ti + 24 + i * 16
                of, = struct.unpack_from('<q', d, p + 8 + 0x4000)
                if p in rel:
                    bases.append((ti, rel[p], of >> 8, ('virtual ' if of & 1 else '') + ('public' if of & 2 else 'private')))
    # vtables: a RELATIVE pointer to a typeinfo, preceded by offset-to-top, followed by fn ptrs
    vtables = []
    for w, tgt in rel.items():
        if tgt in classes and w - 8 not in rel and (w - 8) not in sym and w not in kinds:
            # skip typeinfo base-class records (those sit inside a typeinfo object)
            if any(w - k in classes for k in (16, 24, 40, 56, 72)) and not 0 <= struct.unpack_from('<q', d, w - 8 + 0x4000)[0] <= 0:
                pass
            top, = struct.unpack_from('<q', d, w - 8 + 0x4000)
            if top > 0 or top < -0x100000:
                continue
            slots, p = [], w + 8
            while True:
                t = rel.get(p)
                if t is not None and t < TEXT_END and t in funcs:
                    slots.append(t)
                elif t is None and p not in sym and struct.unpack_from('<Q', d, p + 0x4000)[0] == 0 and slots:
                    slots.append(0)  # pure virtual / null slot
                elif p in sym and 'pure_virtual' in sym[p]:
                    slots.append(-1)
                else:
                    break
                p += 8
            while slots and slots[-1] == 0:
                slots.pop()
            vtables.append((w + 8, tgt, -top, slots))
    with open(f'{out}/classes.tsv', 'w') as f:
        for ti, (m, k) in sorted(classes.items()):
            f.write(f'{ti:x}\t{k}\t{m}\t{names.get(ti, m)}\n')
    with open(f'{out}/bases.tsv', 'w') as f:
        for c, b, off, acc in bases:
            f.write(f'{c:x}\t{b:x}\t{off}\t{acc}\t{names.get(c)}\t{names.get(b)}\n')
    nslots = 0
    with open(f'{out}/vtables.tsv', 'w') as f:
        for vt, ti, top, slots in sorted(vtables):
            for i, s in enumerate(slots):
                f.write(f'{vt:x}\t{ti:x}\t{top}\t{i}\t{s & 0xFFFFFFFFFFFFFFFF:x}\t{names.get(ti)}\n')
                nslots += 1
    vfuncs = {s for _, _, _, sl in vtables for s in sl if s > 0}
    print(f'classes={len(classes)} bases={len(bases)} vtables={len(vtables)} slots={nslots} distinct_virtual_fns={len(vfuncs)}')


if __name__ == '__main__':
    main(*sys.argv[1:4])
