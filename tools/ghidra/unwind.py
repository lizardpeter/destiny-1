#!/usr/bin/env python3
"""List every function the executable's unwind table describes.

    python3 tools/ghidra/unwind.py <eboot.elf> <out unwind.tsv>

The executable has no section headers, so Ghidra does not find .eh_frame, and on its own it only discovers
functions that something calls or references directly. Functions reached only through vtables or callbacks
are missed (about one in six here). The unwind table lists the start and length of every function compiled
with unwind information; CreateUnwindFunctions.java creates a function at each before analysis.

Reads the PT_GNU_EH_FRAME segment (.eh_frame_hdr): its sorted lookup table gives each function's start and
the address of its FDE, and the FDE gives the length.
"""
import struct
import sys
from pathlib import Path

PT_LOAD, PT_GNU_EH_FRAME = 1, 0x6474E550


def main():
    d = Path(sys.argv[1]).read_bytes()
    phoff, = struct.unpack_from("<Q", d, 0x20)
    phentsize, phnum = struct.unpack_from("<HH", d, 0x36)
    loads, hdr = [], None
    for i in range(phnum):
        t, _fl, off, va, _pa, fsz, _msz, _al = struct.unpack_from("<IIQQQQQQ", d, phoff + i * phentsize)
        if t == PT_LOAD:
            loads.append((va, off, fsz))
        if t == PT_GNU_EH_FRAME:
            hdr = va
    if hdr is None:
        sys.exit("no PT_GNU_EH_FRAME segment")

    def at(va):
        for base, off, fsz in loads:
            if base <= va < base + fsz:
                return off + (va - base)
        sys.exit(f"address {va:#x} is not in the file")

    o = at(hdr)
    version, ptr_enc, count_enc, table_enc = d[o:o + 4]
    # the layout every GNU-style linker writes: pc-relative frame pointer, 4-byte count, table relative to the header
    if (version, ptr_enc, count_enc, table_enc) != (1, 0x1B, 0x03, 0x3B):
        sys.exit(f"unexpected .eh_frame_hdr encodings {version} {ptr_enc:#x} {count_enc:#x} {table_enc:#x}")
    count, = struct.unpack_from("<I", d, o + 8)
    rows, unsized = [], 0
    for i in range(count):
        start, fde = (hdr + x for x in struct.unpack_from("<ii", d, o + 12 + i * 8))
        f = at(fde)
        length, cie_delta = struct.unpack_from("<Ii", d, f)
        size = 0
        if length not in (0, 0xFFFFFFFF) and cie_delta:
            # pc_begin and pc_range follow the CIE pointer; with the usual pc-relative 4-byte encoding the range
            # is a plain 4-byte length. Check pc_begin decodes to the table's start before trusting it.
            begin, rng = struct.unpack_from("<iI", d, f + 8)
            if fde + 8 + begin == start:
                size = rng
        unsized += size == 0
        rows.append((start, size))
    rows.sort()
    with open(sys.argv[2], "w", newline="\n") as out:
        out.write("va\tsize\n")
        for start, size in rows:
            out.write(f"{start:08x}\t{size}\n")
    total = sum(s for _, s in rows)
    print(f"unwind: {len(rows)} functions, {total} bytes of code, {unsized} without a length")


if __name__ == "__main__":
    main()
