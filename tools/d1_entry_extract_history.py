#!/usr/bin/env python3
"""EntryReader variant with a verified one-block Oodle history fallback.

Destiny 1 Tiger packages contain some Oodle-compressed logical blocks that cannot be
decoded independently but do decode when the immediately preceding 0x40000-byte
logical block is supplied as Oodle's decBufBase history.

Safety boundary:
- stored block SHA-1 is verified before any decode attempt;
- normal independent decoding is always tried first;
- history fallback is attempted only after independent Oodle failure;
- history is exactly the immediately preceding logical block from the SAME block table;
- the previous block is itself obtained through the same verified reader, allowing a
  contiguous history chain where required;
- no TagHash generation/class fallback is implemented here. Higher-level Corpus
  policy still decides which physical occurrence may supply a resource.
"""
from __future__ import annotations

import ctypes
import hashlib
from pathlib import Path

from d1_entry_extract import EntryReader
from d1_pkg_probe import BLOCK_SIZE, patch_path


class HistoryEntryReader(EntryReader):
    def __init__(self, pkg: Path, runtime: Path):
        super().__init__(pkg, runtime)
        self.history_fallbacks: list[dict] = []

    def _stored_block(self, i: int):
        b = self.blocks[i]
        owner = patch_path(self.pkg, b['patch_id'])
        if not owner.exists():
            raise FileNotFoundError(str(owner))
        with owner.open('rb') as f:
            f.seek(b['offset'])
            raw = f.read(b['size'])
        got = hashlib.sha1(raw).hexdigest()
        if got.lower() != b['sha1'].lower():
            raise RuntimeError(f'block {i} sha1 mismatch {got} != {b["sha1"]}')
        return b, owner, raw

    def _history_decode(self, i: int, raw: bytes, previous: bytes) -> bytes:
        if len(previous) != BLOCK_SIZE:
            raise RuntimeError(f'previous block {i-1} has {len(previous)} bytes, expected {BLOCK_SIZE}')
        total = BLOCK_SIZE * 2
        buf = ctypes.create_string_buffer(total)
        ctypes.memmove(ctypes.addressof(buf), previous, BLOCK_SIZE)
        src = ctypes.create_string_buffer(raw)
        base_addr = ctypes.addressof(buf)
        raw_addr = base_addr + BLOCK_SIZE
        n = self.oodle.fn(
            ctypes.cast(src, ctypes.c_void_p), len(raw),
            ctypes.c_void_p(raw_addr), BLOCK_SIZE,
            1, 0, 1,
            ctypes.c_void_p(base_addr), total,
            None, None, None, 0,
            3,
        )
        if n <= 0:
            raise RuntimeError(f'Oodle history decode failed for block {i} with return value {int(n)}')
        produced = int(n) - BLOCK_SIZE if int(n) > BLOCK_SIZE else int(n)
        if produced < 0 or produced > BLOCK_SIZE:
            raise RuntimeError(f'Oodle history decode block {i} returned impossible size {int(n)} -> {produced}')
        out = ctypes.string_at(raw_addr, produced)
        if len(out) > BLOCK_SIZE:
            raise RuntimeError(f'block {i} history decode oversized')
        if len(out) < BLOCK_SIZE:
            out += b'\0' * (BLOCK_SIZE - len(out))
        return out

    def block(self, i: int) -> bytes:
        if i in self.cache:
            return self.cache[i]
        b, owner, raw = self._stored_block(i)
        if not b['compressed']:
            dec = raw
            if len(dec) > BLOCK_SIZE:
                raise RuntimeError(f'block {i} oversized')
            if len(dec) < BLOCK_SIZE:
                dec += b'\0' * (BLOCK_SIZE - len(dec))
            self.cache[i] = dec
            return dec

        try:
            dec = self.oodle.decompress(raw)
            mode = 'independent'
        except Exception as independent_error:
            if i <= 0:
                raise
            previous = self.block(i - 1)
            try:
                dec = self._history_decode(i, raw, previous)
            except Exception as history_error:
                raise RuntimeError(
                    f'block {i} failed independent decode ({independent_error!r}) and '
                    f'immediate-previous-block history decode ({history_error!r})'
                ) from history_error
            mode = 'previous_logical_block_history'
            self.history_fallbacks.append({
                'block_index': i,
                'patch_id': int(b['patch_id']),
                'owner': owner.name,
                'stored_size': len(raw),
                'stored_sha1': b['sha1'],
                'decoded_sha256': hashlib.sha256(dec).hexdigest(),
                'history_block_index': i - 1,
                'policy': 'IMMEDIATE_PREVIOUS_LOGICAL_BLOCK_ONLY',
            })

        if len(dec) > BLOCK_SIZE:
            raise RuntimeError(f'block {i} oversized after {mode} decode')
        if len(dec) < BLOCK_SIZE:
            dec += b'\0' * (BLOCK_SIZE - len(dec))
        self.cache[i] = dec
        return dec
