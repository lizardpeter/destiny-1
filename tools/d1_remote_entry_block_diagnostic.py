#!/usr/bin/env python3
"""Diagnose exact Tiger blocks backing remote D1 FileHash entries.

This is intentionally below the asset-schema layer.  For every requested
FileHash and every verified physical snapshot of its package family, record:

* entry-table metadata;
* every Tiger block touched by the entry;
* block patch owner, flags, compressed size and SHA-1;
* exact raw prefix/suffix and entropy;
* Oodle decode result and decoded prefix when applicable.

The tool never substitutes another entry or changes package ownership.  It is
for distinguishing bad package-member catalogs, encryption/flag cases, and
compression-decoder failures from higher-level asset parsing mistakes.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_investment_arrangement_probe import filehash_pkg_index
from d1_oodle_probe import Oodle3
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_split_tar_extract import SplitHttpTar


def norm(v: str) -> str:
    v = v.upper().removeprefix('0X').zfill(8)
    int(v, 16)
    return v


def entropy(data: bytes) -> float:
    if not data:
        return 0.0
    n = len(data)
    c = collections.Counter(data)
    return -sum((k/n) * math.log2(k/n) for k in c.values())


def block_indices(entry: dict) -> list[int]:
    remain = int(entry['file_size'])
    bi = int(entry['starting_block'])
    off = int(entry['starting_block_offset'])
    out = []
    while remain:
        out.append(bi)
        n = min(remain, 0x40000 - off)
        remain -= n
        bi += 1
        off = 0
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--tag-hash', action='append', required=True)
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    wanted = [norm(x) for x in a.tag_hash]
    catalogs = load_catalogs(a.member_catalog)
    base = a.base_url.rstrip('/')
    arc = SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    oodle = Oodle3(a.runtime)
    rows = []

    for tag in wanted:
        pkg, idx = filehash_pkg_index(int(tag, 16))
        fam = catalogs.get(pkg)
        rec = {'tag_hash': tag, 'package_id': f'{pkg:04X}', 'file_index': idx, 'snapshots': []}
        if fam is None:
            rec['error'] = 'package absent from supplied catalogs'
            rows.append(rec)
            continue
        for patch in sorted(fam, reverse=True):
            snap = {'patch_id': patch, 'member': fam[patch].name}
            try:
                # A snapshot can legally require any earlier sibling block.
                v = RemoteLogicalPackage(arc, {p:m for p,m in fam.items() if p <= patch}, a.runtime)
                snap['view'] = v.view.name
                snap['entry_count'] = len(v.entries)
                if idx >= len(v.entries):
                    snap['error'] = f'file index outside entry table ({len(v.entries)})'
                    rec['snapshots'].append(snap)
                    continue
                e = v.entries[idx]
                snap['entry'] = {
                    'tag_hash': e['tag_hash'].upper(),
                    'reference': e['reference'].upper(),
                    'type': e['type'], 'subtype': e['subtype'],
                    'entry_b': e['entry_b'],
                    'starting_block': e['starting_block'],
                    'starting_block_offset': e['starting_block_offset'],
                    'file_size': e['file_size'],
                }
                if e['tag_hash'].upper() != tag:
                    snap['error'] = f"logical tag mismatch {e['tag_hash']}"
                    rec['snapshots'].append(snap)
                    continue
                snap['blocks'] = []
                for bi in block_indices(e):
                    b = v.blocks[bi]
                    br = {
                        'block_index': bi,
                        'offset': b['offset'], 'size': b['size'],
                        'patch_id': b['patch_id'], 'flags': b['flags'],
                        'compressed': b['compressed'], 'encrypted': b['encrypted'],
                        'key1_flag': b['key1_flag'], 'unknown_0x8': b['unknown_0x8'],
                        'expected_sha1': b['sha1'],
                    }
                    owner = v.members.get(int(b['patch_id']))
                    if owner is None:
                        br['error'] = f"missing physical patch {b['patch_id']}"
                        snap['blocks'].append(br)
                        continue
                    br['owner_member'] = owner.name
                    raw = arc.read_at(owner.data_offset + int(b['offset']), int(b['size']))
                    br['actual_sha1'] = hashlib.sha1(raw).hexdigest()
                    br['sha1_ok'] = br['actual_sha1'].lower() == b['sha1'].lower()
                    br['raw_entropy_bits_per_byte'] = entropy(raw)
                    br['raw_prefix_hex'] = raw[:64].hex()
                    br['raw_suffix_hex'] = raw[-32:].hex()
                    if b['compressed']:
                        try:
                            dec = oodle.decompress(raw)
                            br['oodle_ok'] = True
                            br['decoded_size'] = len(dec)
                            br['decoded_prefix_hex'] = dec[:64].hex()
                        except Exception as ex:
                            br['oodle_ok'] = False
                            br['oodle_error'] = repr(ex)
                    else:
                        br['oodle_ok'] = None
                        br['decoded_size'] = len(raw)
                        br['decoded_prefix_hex'] = raw[:64].hex()
                    snap['blocks'].append(br)
                try:
                    payload = v.entry(idx)
                    snap['entry_read_ok'] = True
                    snap['entry_payload_size'] = len(payload)
                    snap['entry_payload_sha256'] = hashlib.sha256(payload).hexdigest()
                    snap['entry_payload_prefix_hex'] = payload[:64].hex()
                except Exception as ex:
                    snap['entry_read_ok'] = False
                    snap['entry_read_error'] = repr(ex)
            except Exception as ex:
                snap['error'] = repr(ex)
            rec['snapshots'].append(snap)
        rows.append(rec)

    report = {
        'schema': 'd1_remote_entry_block_diagnostic/v1',
        'requested': wanted,
        'entries': rows,
        'policy': 'All metadata and bytes come from exact FileHash package/index and checksum-validated split-TAR member ranges; no asset fallback or semantic inference is performed.',
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + '\n')
    for r in rows:
        print('\nENTRY', r['tag_hash'], 'pkg', r['package_id'], 'index', r['file_index'])
        for s in r.get('snapshots', []):
            print(' SNAP', s['patch_id'], s.get('member'), 'entry_read', s.get('entry_read_ok'), s.get('entry_read_error') or s.get('error',''))
            for b in s.get('blocks', []):
                print('  BLOCK', b['block_index'], 'owner', b.get('owner_member'), 'flags', hex(b['flags']),
                      'size', b['size'], 'sha', b.get('sha1_ok'), 'compressed', b['compressed'],
                      'encrypted', b['encrypted'], 'key1', b['key1_flag'], 'unk8', b['unknown_0x8'],
                      'oodle', b.get('oodle_ok'), b.get('oodle_error',''), 'prefix', b.get('raw_prefix_hex','')[:32])
    print('wrote', a.output)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
