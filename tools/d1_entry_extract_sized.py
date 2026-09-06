#!/usr/bin/env python3
"""Destiny 1 Tiger EntryReader with serialized-coverage block raw sizing.

D1 Tiger logical blocks are at most 0x40000 decompressed bytes, but patch-family
blocks are not necessarily a full 0x40000. Oodle requires the exact raw length.

For each logical block this reader derives the highest byte referenced by the
snapshot's serialized FileEntry table and rounds that end upward to the observed
D1 allocation quantum 0x4000, capped at 0x40000. Compressed blocks are decoded
with that raw length, then zero-padded to 0x40000 only for the existing logical
addressing API.

Evidence motivating this rule:
- Tower 024C block 636: max serialized end 0x24E0, correct Oodle rawLen 0x4000;
- Tower 024C block 725: max serialized end 0x2EB40, correct Oodle rawLen 0x30000;
- Investment 013F block 114/99: max serialized end 0x351EC, correct rawLen 0x38000;
- these partial blocks fail when rawLen is incorrectly forced to 0x40000.

Safety:
- stored block SHA-1 remains mandatory;
- no bytes are invented inside the decoded raw range;
- only address-space padding after the proven decoded raw length is zero-filled;
- no TagHash generation/class fallback semantics are changed here.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from d1_entry_extract import EntryReader
from d1_pkg_probe import BLOCK_SIZE, patch_path

RAW_QUANTUM = 0x4000


def align_up(v: int, a: int) -> int:
    return ((v + a - 1) // a) * a


class SizedEntryReader(EntryReader):
    def __init__(self, pkg: Path, runtime: Path):
        super().__init__(pkg, runtime)
        self.block_used_end = [0] * len(self.blocks)
        for e in self.entries:
            remaining = int(e['file_size'])
            bi = int(e['starting_block'])
            off = int(e['starting_block_offset'])
            while remaining > 0 and bi < len(self.blocks):
                n = min(remaining, BLOCK_SIZE - off)
                self.block_used_end[bi] = max(self.block_used_end[bi], off + n)
                remaining -= n
                bi += 1
                off = 0
        self.block_decode_meta: dict[int, dict] = {}

    def expected_raw_len(self, i: int) -> int:
        used = self.block_used_end[i]
        if used <= 0:
            # A block not referenced by this snapshot's FileEntry table is outside
            # the evidence needed by entry(); preserve legacy full-block behavior.
            return BLOCK_SIZE
        return min(BLOCK_SIZE, align_up(used, RAW_QUANTUM))

    def block(self, i: int) -> bytes:
        if i in self.cache:
            return self.cache[i]
        b = self.blocks[i]
        owner = patch_path(self.pkg, b['patch_id'])
        if not owner.exists():
            raise FileNotFoundError(str(owner))
        with owner.open('rb') as f:
            f.seek(b['offset'])
            raw = f.read(b['size'])
        got_sha1 = hashlib.sha1(raw).hexdigest()
        if got_sha1.lower() != b['sha1'].lower():
            raise RuntimeError(f'block {i} sha1 mismatch')

        expected = self.expected_raw_len(i)
        if b['compressed']:
            dec = self.oodle.decompress(raw, raw_capacity=expected)
            if len(dec) != expected:
                raise RuntimeError(
                    f'block {i} decoded {len(dec)} bytes, serialized-coverage raw length is {expected}'
                )
        else:
            dec = raw
            if len(dec) > BLOCK_SIZE:
                raise RuntimeError(f'block {i} oversized')
            # Uncompressed block storage itself provides the exact byte length;
            # do not require it to equal the coverage-derived aligned size.

        decoded_len = len(dec)
        self.block_decode_meta[i] = {
            'block_index': i,
            'patch_id': int(b['patch_id']),
            'owner': owner.name,
            'compressed': bool(b['compressed']),
            'stored_size': len(raw),
            'stored_sha1': b['sha1'],
            'max_serialized_used_end': int(self.block_used_end[i]),
            'expected_raw_len': int(expected),
            'decoded_raw_len': int(decoded_len),
            'raw_quantum': RAW_QUANTUM,
        }
        if len(dec) < BLOCK_SIZE:
            dec = dec + b'\0' * (BLOCK_SIZE - len(dec))
        self.cache[i] = dec
        return dec
