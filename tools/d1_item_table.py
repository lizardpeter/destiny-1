#!/usr/bin/env python3
"""D1 inventory item table: client item index -> public InventoryItemHash, name, type, slot, tier, class.

The client indexes items by their row in the inventory item map 80A5FFBE (definitions manager
vtable +0x168; +0x410 returns the definition tag of a row): 0x18-byte rows {u32
InventoryItemHash, ..., u32 definition FileHash @+0x10}. Item loadouts (0x80801855 member 6)
and inventory items (0x80801732 +0x24) carry this index.

The table is written in index order without whitespace padding (backend/data/items.json).

Display strings follow the layout Charm uses for DESTINY1_RISE_OF_IRON
(MontagueM/Charm Tiger/Schema/Investment/InvestmentStructs.cs):
  80A5FF9C (class 808034C7): +0x08 rows of 0x10 {u32 0, u32 strings tag @+0x08}, same order
      (the client's 0x549570 table)
  strings tag (class 80803484, 0xB4): +0x78 name, +0x80 item type, +0x88 flavour text
      (string index references {i32 bank index, u32 string hash})
  80A5E21A (class 80803473 rows, 0x18): {u32 bank hash, ..., u32 LocalizedStrings tag @+0x10}
  LocalizedStrings 8080035A: +0x08 string hashes (u32); +0x18 English data 808008BE:
      +0x08 parts (0x20: rel ptr @+0x08, u16 bytes @+0x14, u16 cipher @+0x18),
      +0x48 combinations (0x10: rel ptr to first part, i64 part count)

usage: d1_item_table.py <packages dir> --runtime <oodle runtime dir> -o items.json
"""
from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from d1_entry_extract import EntryReader  # noqa: E402
from d1_global_strings_resolve import decode_part_bytes  # noqa: E402

ITEM_MAP = 0x80A5FFBE
# armor equip flags (+0x164) per class: gauntlets, chest, class item, helmet, legs = lo..lo+4
CLASS_EQUIP_FLAGS = {'titan': 2510, 'hunter': 2488, 'warlock': 2517}
ITEM_STRINGS = 0x80A5FF9C
STRING_BANKS = 0x80A5E21A


def u32(b, o): return struct.unpack_from('<I', b, o)[0]
def i32(b, o): return struct.unpack_from('<i', b, o)[0]
def i64(b, o): return struct.unpack_from('<q', b, o)[0]


def dyn(b: bytes, off: int) -> tuple[int, int]:
    """(count, absolute offset of the first element) of a serialized dynamic array."""
    return i32(b, off), off + 8 + i64(b, off + 8) + 0x10


class Packages:
    """FileHash -> entry bytes, newest generation of each package."""

    def __init__(self, root: Path, runtime: Path):
        self.files: dict[int, Path] = {}
        gen: dict[int, int] = {}
        for p in root.glob('*.pkg'):
            m = re.search(r'_([0-9a-f]{4})_(\d+)\.pkg$', p.name)
            if not m:
                continue
            if '_en_' not in p.name and re.search(r'_(fr|de|it|es|ja|pt|br|mx)_', p.name):
                continue
            pid, g = int(m.group(1), 16), int(m.group(2))
            if g >= gen.get(pid, -1):
                gen[pid] = g
                self.files[pid] = p
        self.runtime = runtime
        self.readers: dict[int, EntryReader] = {}

    def entry(self, h: int) -> bytes | None:
        if h in (0, 0xFFFFFFFF) or h < 0x80800000:
            return None
        pid, idx = (h - 0x80800000) >> 13, h & 0x1FFF
        if pid not in self.files:
            return None
        if pid not in self.readers:
            self.readers[pid] = EntryReader(self.files[pid], self.runtime)
        r = self.readers[pid]
        if idx >= len(r.entries) or not r.available(idx):
            return None
        return r.entry(idx)


class Strings:
    def __init__(self, pk: Packages):
        self.pk = pk
        b = pk.entry(STRING_BANKS)
        n, a = dyn(b, 0x08)
        self.banks = [u32(b, a + i * 0x18 + 0x10) for i in range(n)]
        self.cache: dict[int, dict[int, str]] = {}

    def bank(self, i: int) -> dict[int, str]:
        if i in self.cache:
            return self.cache[i]
        out: dict[int, str] = {}
        ls = self.pk.entry(self.banks[i]) if 0 <= i < len(self.banks) else None
        if ls:
            n, a = dyn(ls, 0x08)
            hashes = [u32(ls, a + k * 4) for k in range(n)]
            d = self.pk.entry(u32(ls, 0x18))
            if d:
                _, parts = dyn(d, 0x08)
                cn, combos = dyn(d, 0x48)
                for k in range(min(n, cn)):
                    co = combos + k * 0x10
                    start, count = co + i64(d, co), i64(d, co + 8)
                    s = []
                    for j in range(count):
                        po = start + j * 0x20
                        p = po + 8 + i64(d, po + 8)
                        bl, shift = struct.unpack_from('<H', d, po + 0x14)[0], struct.unpack_from('<H', d, po + 0x18)[0]
                        s.append(decode_part_bytes(d[p:p + bl], shift))
                    out[hashes[k]] = ''.join(s)
        self.cache[i] = out
        return out

    def ref(self, b: bytes, off: int) -> str | None:
        i, h = i32(b, off), u32(b, off + 4)
        if i == 0xFFFF or i < 0:
            return None
        return self.bank(i).get(h)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('packages', type=Path)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()
    pk = Packages(a.packages, a.runtime.resolve())
    strings = Strings(pk)
    m = pk.entry(ITEM_MAP)
    n, rows = dyn(m, 0x08)
    s = pk.entry(ITEM_STRINGS)
    sn, srows = dyn(s, 0x08)
    items = []
    for i in range(n):
        h = u32(m, rows + i * 0x18)
        row = {'index': i, 'hash': h, 'definition': f'{u32(m, rows + i * 0x18 + 0x10):08X}'}
        if i < sn:
            st = pk.entry(u32(s, srows + i * 0x10 + 8))
            if st and len(st) >= 0x94:
                name, kind = strings.ref(st, 0x78), strings.ref(st, 0x80)
                if name:
                    row['name'] = name.strip()
                if kind:
                    row['type'] = kind.strip()
        d = pk.entry(u32(m, rows + i * 0x18 + 0x10))
        if d and len(d) >= 0x168:
            # definition: +0x88 u8 equipment slot code (2 primary .. 6 subclass, 7 helmet),
            # +0x89 u8 required level (0xFF none), +0x8A u8 tier (1 basic .. 4 legendary,
            # 5 exotic), +0x164 i32 unlock flag required to equip (per class and armor slot)
            row['slot'], row['level'], row['tier'] = d[0x88], d[0x89], d[0x8A]
            flag = i32(d, 0x164)
            for cls, lo in CLASS_EQUIP_FLAGS.items():
                if lo <= flag <= lo + 4:
                    row['class'] = cls
        items.append(row)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text('[\n' + ',\n'.join(json.dumps(r, ensure_ascii=False) for r in items) + '\n]\n')
    named = sum(1 for r in items if r.get('name'))
    print(f'{len(items)} items, {named} named -> {a.output}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
