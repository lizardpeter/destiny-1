#!/usr/bin/env python3
"""Scan eboot.bin for compiled engine-type layouts (field block: u64 member count, u32 type id
0x8080xxxx, u32 size, i32 array count, then 0x28-byte members {i32 offset, ..., u8 kind @0x10,
u32 member type @0x14, params @0x18}). Usage: d1_engine_type_layout_scan.py eboot.bin out.json"""
import struct, json, sys
eb = open(sys.argv[1], 'rb').read()
q = lambda o: struct.unpack_from('<Q', eb, o)[0]
u = lambda o: struct.unpack_from('<I', eb, o)[0]
i32 = lambda o: struct.unpack_from('<i', eb, o)[0]
found = {}
o = 8
L = len(eb) - 0x40
while o < L:
    o = eb.find(b'\x80\x80', o + 1)
    if o < 0: break
    f = o - 10  # u32 type id ends with 80 80; field block f = (id offset) - 8
    if (o - 2) % 4: continue
    tid = u(o - 2); f = o - 2 - 8
    if f < 0: continue
    cnt = q(f); size = u(f + 0xc); acount = i32(f + 0x18)
    if not (0 < cnt <= 400 and 0 < size < 0x200000): continue
    # members: kinds plausible
    ok = True; ms = []
    n = 1 if acount > 0 else cnt
    for k in range(n):
        m = f + 0x20 + k * 0x28
        if m + 0x28 > len(eb): ok = False; break
        off = i32(m); kind = eb[m + 0x10]; mt = u(m + 0x14)
        if not (0 <= off <= size and kind < 32 and (mt == 0xffffffff or 0x80800000 <= mt < 0x80810000)): ok = False; break
        ms.append(dict(off=off, kind=kind, type=f'{mt:08X}', params=eb[m+0x18:m+0x28].hex()))
    if not ok: continue
    found.setdefault(f'{tid:08X}', dict(at=hex(f), size=size, count=cnt, array=acount, members=ms))
json.dump(found, open(sys.argv[2], 'w'), indent=0)
print(len(found), 'class layouts')
