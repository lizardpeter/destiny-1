#!/usr/bin/env python3
"""Print the (kind, name) object table of a class 0x8080076E activity content tag (Charm S6E078080,
the array Charm leaves as SD3078080): count @0x50, 16-byte entries from 0x60 {u32 kind, u32, u64
relative string offset}. Usage: d1_activity_object_table.py <decoded tag .bin>"""
import struct,sys
b=open(sys.argv[1],'rb').read()
cnt,off=struct.unpack_from('<QQ',b,0x18)  # dyn array: count @0x18, rel offset @0x20? try both
def cstr(o): return b[o:b.index(b'\0',o)].decode('latin1')
# header at 0x10: u32? use the array at 0x50 (count at 0x50 per dump: 0x62, class 808007d3 at 0x58)
n=struct.unpack_from('<I',b,0x50)[0]; base=0x60
for i in range(n):
    k,_,rel=struct.unpack_from('<IIQ',b,base+16*i)
    for cand in (base+16*i+8+rel, base+16*i+rel):
        try:
            s=cstr(cand)
            if s.isprintable() and len(s)>2: print(f'{k:#04x} {s}'); break
        except Exception: pass
    else: print(f'{k:#04x} ? rel {rel:#x}')
