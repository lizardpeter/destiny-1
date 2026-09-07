#!/usr/bin/env python3
"""Correct parent-name validation for the Xur D912 location/group closure.

The retail string scanner reports the byte offset of the literal C string and its
computed Bungie FNV1-32 StringHash.  Therefore parent +0x5F0 contains the literal
branch name bytes, not the four-byte hash.  This wrapper changes only that canary;
all D912/SD614/S2B grouping and E6/E7/E8 fail-closed policy remains unchanged.
"""
from __future__ import annotations

import hashlib

import d1_remote_xur_d912_location_group_closure as base


def fnv1_32(text: str) -> int:
    h = 0x811C9DC5
    for b in text.encode('utf-8'):
        h = (h * 0x01000193) & 0xFFFFFFFF
        h ^= b
    return h


def parent_check(c, d912: str, parent: str, branch_hash: str, branch_name: str):
    m = c.entry_meta(parent)
    b, src = c.payload(parent)
    out = {
        'parent': parent,
        'expected_class': base.PARENT_CLASS,
        'branch_string_hash': branch_hash,
        'branch_name_exact_retail_preimage': branch_name,
        'payload_source': src,
        'violations': [],
    }
    if m is None or base.norm(m.get('reference', '')) != base.PARENT_CLASS or b is None:
        out['violations'].append('parent_missing_class_or_payload')
        return out
    out['bytes'] = len(b)
    out['sha256'] = hashlib.sha256(b).hexdigest()
    encoded = branch_name.encode('ascii') + b'\x00'
    if len(b) < max(0x544, 0x5F0 + len(encoded)):
        out['violations'].append('parent_shorter_than_required_fields')
        return out
    out['d912_backlink_offset'] = 0x540
    out['d912_backlink_value'] = f'{base.u32(b, 0x540):08X}'
    out['branch_literal_offset'] = 0x5F0
    out['branch_literal_value'] = b[0x5F0:0x5F0 + len(encoded)].rstrip(b'\x00').decode('ascii', errors='strict')
    out['branch_literal_exact'] = b[0x5F0:0x5F0 + len(encoded)] == encoded
    out['computed_fnv1_32'] = f'{fnv1_32(branch_name):08X}'
    out['computed_hash_matches_retail_stringhash'] = out['computed_fnv1_32'] == branch_hash
    if out['d912_backlink_value'] != d912:
        out['violations'].append(f'parent_0x540_{out["d912_backlink_value"]}_not_{d912}')
    if not out['branch_literal_exact']:
        out['violations'].append(f'parent_0x5F0_literal_{out["branch_literal_value"]!r}_not_{branch_name!r}')
    if not out['computed_hash_matches_retail_stringhash']:
        out['violations'].append(f'fnv1_{out["computed_fnv1_32"]}_not_{branch_hash}')
    return out


base.parent_check = parent_check

if __name__ == '__main__':
    raise SystemExit(base.main())
