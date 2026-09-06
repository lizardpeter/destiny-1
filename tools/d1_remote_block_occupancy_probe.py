#!/usr/bin/env python3
"""Measure D1 Tiger logical-block occupancy and test justified Oodle raw lengths.

A Tiger block has nominal logical capacity 0x40000, but OodleLZ_Decompress takes
an exact raw length.  This probe determines the byte ranges actually referenced
by the package entry table for a target block and tests only output lengths that
are directly derived from those serialized ranges.

The same FileHash is evaluated independently in every verified physical
snapshot of its package family.  This matters because a block reused from patch
1 may have a different logical block index in patch 5; the physical producer's
entry table is therefore reported separately from the latest consumer table.

No asset bytes are synthesized and no arbitrary raw-length brute force is done.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_investment_arrangement_probe import filehash_pkg_index
from d1_oodle_probe import Oodle3
from d1_pkg_probe import BLOCK_SIZE
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_split_tar_extract import SplitHttpTar


def norm(v: str) -> str:
    v = v.upper().removeprefix('0X').zfill(8)
    int(v, 16)
    return v


def entry_block_slices(entry: dict):
    """Yield (block_index, local_start, local_end, file_start, file_end)."""
    remain = int(entry['file_size'])
    bi = int(entry['starting_block'])
    local = int(entry['starting_block_offset'])
    file_pos = 0
    while remain > 0:
        take = min(remain, BLOCK_SIZE - local)
        yield bi, local, local + take, file_pos, file_pos + take
        remain -= take
        file_pos += take
        bi += 1
        local = 0


def merge_ranges(ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not ranges:
        return []
    out = []
    for a, b in sorted(ranges):
        if not out or a > out[-1][1]:
            out.append([a, b])
        else:
            out[-1][1] = max(out[-1][1], b)
    return [(int(a), int(b)) for a, b in out]


def align_up(v: int, a: int) -> int:
    return ((v + a - 1) // a) * a


def occupancy(entries: list[dict], target_block: int) -> dict:
    rows = []
    for e in entries:
        for bi, lo, hi, flo, fhi in entry_block_slices(e):
            if bi != target_block:
                continue
            rows.append({
                'entry_index': int(e['index']),
                'tag_hash': e['tag_hash'].upper(),
                'reference': e['reference'].upper(),
                'type': int(e['type']),
                'subtype': int(e['subtype']),
                'file_size': int(e['file_size']),
                'starting_block': int(e['starting_block']),
                'starting_block_offset': int(e['starting_block_offset']),
                'block_slice_start': lo,
                'block_slice_end': hi,
                'block_slice_size': hi - lo,
                'file_slice_start': flo,
                'file_slice_end': fhi,
                'continues_from_previous_block': bi > int(e['starting_block']),
                'continues_to_next_block': fhi < int(e['file_size']),
            })
            break
    merged = merge_ranges([(x['block_slice_start'], x['block_slice_end']) for x in rows])
    covered = sum(b - a for a, b in merged)
    max_end = max((x['block_slice_end'] for x in rows), default=0)
    min_start = min((x['block_slice_start'] for x in rows), default=None)
    gaps = []
    cursor = 0
    for a, b in merged:
        if a > cursor:
            gaps.append([cursor, a])
        cursor = max(cursor, b)
    if cursor < BLOCK_SIZE:
        gaps.append([cursor, BLOCK_SIZE])
    candidates = {BLOCK_SIZE}
    if max_end > 0:
        candidates.add(max_end)
        for a in (0x10, 0x100, 0x1000, 0x10000):
            x = align_up(max_end, a)
            if 0 < x <= BLOCK_SIZE:
                candidates.add(x)
    return {
        'entry_slice_count': len(rows),
        'entry_slices': rows,
        'merged_referenced_ranges': [list(x) for x in merged],
        'referenced_byte_count': covered,
        'min_referenced_offset': min_start,
        'max_referenced_end': max_end,
        'trailing_unreferenced_bytes': BLOCK_SIZE - max_end if max_end else BLOCK_SIZE,
        'gaps': gaps,
        'has_entry_continuing_from_previous': any(x['continues_from_previous_block'] for x in rows),
        'has_entry_continuing_to_next': any(x['continues_to_next_block'] for x in rows),
        'derived_raw_length_candidates': sorted(candidates),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--tag-hash', action='append', required=True,
                    help='FileHash whose starting/touched block will be inspected; repeatable')
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
    results = []

    for tag in wanted:
        pkg, idx = filehash_pkg_index(int(tag, 16))
        fam = catalogs.get(pkg)
        rec = {'tag_hash': tag, 'package_id': f'{pkg:04X}', 'file_index': idx, 'snapshots': []}
        if fam is None:
            rec['error'] = 'package absent from supplied member catalogs'
            results.append(rec)
            continue
        for patch in sorted(fam):
            snap = {'snapshot_patch_id': patch, 'snapshot_member': fam[patch].name}
            try:
                view = RemoteLogicalPackage(arc, {p:m for p,m in fam.items() if p <= patch}, a.runtime)
                if idx >= len(view.entries):
                    snap['error'] = f'file index outside {len(view.entries)} entries'
                    rec['snapshots'].append(snap)
                    continue
                e = view.entries[idx]
                if e['tag_hash'].upper() != tag:
                    snap['error'] = f"logical tag mismatch {e['tag_hash']}"
                    rec['snapshots'].append(snap)
                    continue
                target_blocks = sorted({bi for bi, *_ in entry_block_slices(e)})
                snap['entry'] = {
                    'reference': e['reference'].upper(), 'type': e['type'], 'subtype': e['subtype'],
                    'file_size': e['file_size'], 'starting_block': e['starting_block'],
                    'starting_block_offset': e['starting_block_offset'], 'touched_blocks': target_blocks,
                }
                block_rows = []
                for bi in target_blocks:
                    b = view.blocks[bi]
                    owner = view.members.get(int(b['patch_id']))
                    br = {
                        'logical_block_index': bi,
                        'physical_patch_id': int(b['patch_id']),
                        'flags': int(b['flags']),
                        'compressed': bool(b['compressed']),
                        'encrypted': bool(b['encrypted']),
                        'stored_offset': int(b['offset']),
                        'stored_size': int(b['size']),
                        'expected_sha1': b['sha1'],
                        'occupancy': occupancy(view.entries, bi),
                    }
                    if owner is None:
                        br['error'] = f"missing owner patch {b['patch_id']}"
                        block_rows.append(br)
                        continue
                    br['physical_owner_member'] = owner.name
                    raw = arc.read_at(owner.data_offset + int(b['offset']), int(b['size']))
                    br['actual_sha1'] = hashlib.sha1(raw).hexdigest()
                    br['sha1_ok'] = br['actual_sha1'].lower() == b['sha1'].lower()
                    br['stored_prefix_hex'] = raw[:32].hex()
                    attempts = []
                    if b['encrypted']:
                        attempts.append({'skipped': 'encrypted'})
                    elif not b['compressed']:
                        attempts.append({'raw_length': len(raw), 'success': True, 'mode': 'uncompressed'})
                    else:
                        for raw_len in br['occupancy']['derived_raw_length_candidates']:
                            ar = {'requested_raw_length': raw_len}
                            try:
                                dec = oodle.decompress(raw, raw_capacity=raw_len)
                                ar.update({
                                    'success': True,
                                    'returned_length': len(dec),
                                    'sha256': hashlib.sha256(dec).hexdigest(),
                                    'prefix_hex': dec[:32].hex(),
                                })
                            except Exception as ex:
                                ar.update({'success': False, 'error': repr(ex)})
                            attempts.append(ar)
                    br['decode_attempts'] = attempts
                    block_rows.append(br)
                snap['blocks'] = block_rows
            except Exception as ex:
                snap['error'] = repr(ex)
            rec['snapshots'].append(snap)
        results.append(rec)

    report = {
        'schema': 'd1_remote_block_occupancy_probe/v1',
        'logical_block_capacity': BLOCK_SIZE,
        'entries': results,
        'policy': (
            'Candidate Oodle raw lengths are limited to the exact maximum serialized entry end in the block, '
            'that end rounded upward to 0x10/0x100/0x1000/0x10000, and the canonical 0x40000 Tiger capacity. '
            'No arbitrary length brute force is performed.'
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + '\n')
    for rec in results:
        print('\nTAG', rec['tag_hash'], 'pkg', rec['package_id'], 'index', rec['file_index'])
        for s in rec.get('snapshots', []):
            print(' SNAPSHOT', s['snapshot_patch_id'], s['snapshot_member'], s.get('error',''))
            for b in s.get('blocks', []):
                oc=b['occupancy']
                print('  BLOCK',b['logical_block_index'],'owner',b.get('physical_owner_member'),'stored',b['stored_size'],
                      'max_end',oc['max_referenced_end'],'trailing',oc['trailing_unreferenced_bytes'],
                      'slices',oc['entry_slice_count'],'continues_next',oc['has_entry_continuing_to_next'])
                for x in b['decode_attempts']:
                    print('   DECODE',x)
    print('wrote', a.output)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
