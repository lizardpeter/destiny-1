#!/usr/bin/env python3
"""Destiny 1 Rise of Iron Tiger .pkg structural probe.

Pure-standard-library parser for the outer Tiger package tables used by D1 ROI
on PS4/Xbox One. It does not decompress Oodle payloads; it inventories and
validates the package structure so unknown asset schemas can be reversed on top.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import struct
from pathlib import Path

BLOCK_SIZE = 0x40000
PLATFORMS = {
    0: "Tool32", 1: "Win32", 2: "Win64", 3: "X360", 4: "PS3", 5: "Tool64",
    6: "Win64v1", 7: "PS4", 8: "XboxOne", 9: "Stadia", 10: "PS5", 11: "Scarlett",
}
LANGUAGES = {
    0: "None", 1: "English", 2: "French", 3: "Italian", 4: "German",
    5: "Spanish", 6: "Japanese", 7: "Portuguese", 8: "Russian", 9: "Polish",
    10: "SimplifiedChinese", 11: "TraditionalChinese", 12: "SpanishLatAm", 13: "Korean",
}


def u16(b: bytes, o: int) -> int: return struct.unpack_from('<H', b, o)[0]
def u32(b: bytes, o: int) -> int: return struct.unpack_from('<I', b, o)[0]
def u64(b: bytes, o: int) -> int: return struct.unpack_from('<Q', b, o)[0]


def tag_hash(pkg_id: int, entry_index: int) -> int:
    return (0x80800000 + (pkg_id << 13) + (entry_index % 8192)) & 0xFFFFFFFF


def decode_cstr(raw: bytes) -> str:
    return raw.split(b'\0', 1)[0].decode('utf-8', errors='replace')


def parse_header(f) -> dict:
    f.seek(0)
    b = f.read(0x140)
    if len(b) < 0x110:
        raise ValueError(f"file too small for D1 ROI header: {len(b)} bytes")
    h = {
        'version': u16(b, 0x00),
        'platform_code': u16(b, 0x02),
        'pkg_id': u16(b, 0x04),
        'unk6': u16(b, 0x06),
        'unk8': u64(b, 0x08),
        'build_time_raw': u64(b, 0x10),
        'unk_buildid': u32(b, 0x18),
        'version_major': u16(b, 0x1C),
        'version_minor': u16(b, 0x1E),
        'patch_id': u16(b, 0x20),
        'language_code': u16(b, 0x22),
        'tool_string': decode_cstr(b[0x24:0xA4]),
        'unka4': u32(b, 0xA4),
        'unka8': u32(b, 0xA8),
        'unkac': u32(b, 0xAC),
        'header_signature_offset': u32(b, 0xB0),
        'entry_table_count': u32(b, 0xB4),
        'entry_table_offset': u32(b, 0xB8),
        'entry_table_hash': b[0xBC:0xD0].hex(),
        'block_table_count': u32(b, 0xD0),
        'block_table_offset': u32(b, 0xD4),
        'block_table_hash': b[0xD8:0xEC].hex(),
        'named_tag_table_count': u32(b, 0xEC),
        'named_tag_table_offset': u32(b, 0xF0),
        'named_tag_table_hash': b[0xF4:0x108].hex(),
        'file_size_header': u32(b, 0x13C) if len(b) >= 0x140 else None,
    }
    h['platform'] = PLATFORMS.get(h['platform_code'], f"Unknown({h['platform_code']})")
    h['language'] = LANGUAGES.get(h['language_code'], f"Unknown({h['language_code']})")
    return h


def read_table(f, offset: int, count: int, stride: int) -> bytes:
    f.seek(offset)
    data = f.read(count * stride)
    if len(data) != count * stride:
        raise ValueError(f"truncated table @0x{offset:X}: expected {count*stride}, got {len(data)}")
    return data


def parse_entries(data: bytes, pkg_id: int) -> list[dict]:
    out = []
    for i in range(len(data)//16):
        ref, thing, bi = struct.unpack_from('<IIQ', data, i*16)
        out.append({
            'index': i,
            'tag_hash': f"{tag_hash(pkg_id, i):08X}",
            'reference': f"{ref:08X}",
            'entry_b': f"{thing:08X}",
            'type': thing & 0xFF,
            'subtype': (thing >> 24) & 0xFF,
            'starting_block': bi & 0x3FFF,
            'starting_block_offset': ((bi >> 14) & 0x3FFF) << 4,
            'file_size': (bi >> 28) & 0x3FFFFFFF,
        })
    return out


def parse_blocks(data: bytes) -> list[dict]:
    out = []
    for i in range(len(data)//32):
        off, size, patch, flags = struct.unpack_from('<IIHH', data, i*32)
        sha = data[i*32+12:i*32+32]
        out.append({
            'index': i, 'offset': off, 'size': size, 'patch_id': patch,
            'flags': flags,
            'compressed': bool(flags & 0x1),
            'encrypted': bool(flags & 0x2),
            'key1_flag': bool(flags & 0x4),
            'unknown_0x8': bool(flags & 0x8),
            'sha1': sha.hex(),
        })
    return out


def parse_named(data: bytes) -> list[dict]:
    out = []
    for i in range(len(data)//68):
        tag, cls = struct.unpack_from('<II', data, i*68)
        name = decode_cstr(data[i*68+8:i*68+68])
        out.append({'index': i, 'tag_hash': f"{tag:08X}", 'class_hash': f"{cls:08X}", 'name': name})
    return out


def sha1_hex(b: bytes) -> str: return hashlib.sha1(b).hexdigest()


def patch_path(current: Path, patch_id: int) -> Path:
    # Destiny internal packages use ..._<patch>.pkg. Connector downloads may
    # materialize the same bytes as ..._<patch>.pkg.bin; preserve that suffix.
    import re
    m = re.match(r'^(.*)_([0-9]+)(\.pkg(?:\.bin)?)$', current.name, re.IGNORECASE)
    if m:
        return current.with_name(f"{m.group(1)}_{patch_id}{m.group(3)}")
    return current


def verify_blocks(pkg: Path, blocks: list[dict]) -> dict:
    handles = {}
    verified = mismatched = missing = 0
    details = []
    try:
        for b in blocks:
            p = patch_path(pkg, b['patch_id'])
            if not p.exists():
                missing += 1
                details.append({'block': b['index'], 'status': 'missing_patch', 'path': str(p)})
                continue
            key = str(p)
            if key not in handles:
                handles[key] = p.open('rb')
            fh = handles[key]
            fh.seek(b['offset'])
            raw = fh.read(b['size'])
            got = sha1_hex(raw)
            if got.lower() == b['sha1'].lower():
                verified += 1
            else:
                mismatched += 1
                details.append({'block': b['index'], 'status': 'sha1_mismatch', 'expected': b['sha1'], 'actual': got})
    finally:
        for fh in handles.values(): fh.close()
    return {'verified': verified, 'mismatched': mismatched, 'missing_patch_blocks': missing, 'details': details}


def counter_dict(items):
    return {str(k): v for k, v in sorted(collections.Counter(items).items(), key=lambda kv: (-kv[1], str(kv[0])))}


def main():
    ap = argparse.ArgumentParser(description='Probe Destiny 1 Rise of Iron Tiger package structure')
    ap.add_argument('pkg', type=Path)
    ap.add_argument('-o', '--output', type=Path, help='write JSON report')
    ap.add_argument('--verify-blocks', action='store_true', help='SHA-1 verify raw block payloads; sibling patch PKGs are used automatically')
    ap.add_argument('--full-entries', action='store_true', help='include all file entry records in JSON')
    args = ap.parse_args()

    pkg = args.pkg
    actual_size = pkg.stat().st_size
    with pkg.open('rb') as f:
        h = parse_header(f)
        if h['version'] != 24:
            raise SystemExit(f"Not a known D1 ROI v24 package (version={h['version']}).")
        if h['platform_code'] not in (7, 8):
            print(f"WARNING: platform is {h['platform']} ({h['platform_code']}), not PS4/XboxOne")
        et = read_table(f, h['entry_table_offset'], h['entry_table_count'], 16)
        bt = read_table(f, h['block_table_offset'], h['block_table_count'], 32)
        nt = read_table(f, h['named_tag_table_offset'], h['named_tag_table_count'], 68)

    entries = parse_entries(et, h['pkg_id'])
    blocks = parse_blocks(bt)
    named = parse_named(nt)

    # structural checks
    entry_bad_block = [e['index'] for e in entries if e['starting_block'] >= len(blocks)]
    entry_overruns = []
    for e in entries:
        span = e['starting_block_offset'] + e['file_size']
        needed = max(1, (span + BLOCK_SIZE - 1)//BLOCK_SIZE)
        if e['starting_block'] + needed > len(blocks):
            entry_overruns.append(e['index'])

    report = {
        'path': str(pkg), 'actual_size': actual_size, 'header': h,
        'table_validation': {
            'entry_sha1_actual': sha1_hex(et), 'entry_sha1_matches': sha1_hex(et) == h['entry_table_hash'],
            'block_sha1_actual': sha1_hex(bt), 'block_sha1_matches': sha1_hex(bt) == h['block_table_hash'],
            'named_sha1_actual': sha1_hex(nt), 'named_sha1_matches': sha1_hex(nt) == h['named_tag_table_hash'],
        },
        'summary': {
            'entry_count': len(entries), 'block_count': len(blocks), 'named_tag_count': len(named),
            'entry_type_subtype_counts': counter_dict((e['type'], e['subtype']) for e in entries),
            'top_reference_hashes': dict(collections.Counter(e['reference'] for e in entries).most_common(40)),
            'block_flag_counts': counter_dict(b['flags'] for b in blocks),
            'block_patch_counts': counter_dict(b['patch_id'] for b in blocks),
            'compressed_blocks': sum(b['compressed'] for b in blocks),
            'encrypted_blocks': sum(b['encrypted'] for b in blocks),
            'unknown_0x8_blocks': sum(b['unknown_0x8'] for b in blocks),
            'entry_invalid_starting_blocks': entry_bad_block,
            'entry_block_span_overruns': entry_overruns,
            'header_size_matches_actual': h['file_size_header'] == actual_size if h['file_size_header'] is not None else None,
        },
        'named_tags': named,
    }
    if args.full_entries:
        report['entries'] = entries
        report['blocks'] = blocks
    if args.verify_blocks:
        report['block_verification'] = verify_blocks(pkg, blocks)

    text = json.dumps(report, indent=2)
    if args.output:
        args.output.write_text(text, encoding='utf-8')
        print(f"wrote {args.output}")
    else:
        print(text)

if __name__ == '__main__':
    main()
