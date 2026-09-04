#!/usr/bin/env python3
"""Locate named members in an HTTP split TAR by scanning aligned TAR headers.

Unlike d1_split_tar_extract.py, which walks the TAR forward by following each
member's recorded size, this helper is for cases where a later calibrated TAR
offset is already known and the desired member is somewhere before it. It reads
large HTTP Range chunks backwards, tests only 512-byte-aligned candidates, and
requires both ustar magic and a valid TAR checksum before accepting a header.

This is intentionally a locator only. Feed a discovered exact header offset back
to d1_split_tar_extract.py --start-offset for checksum-preserving extraction.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from d1_split_tar_extract import BLOCK, SplitHttpTar, parse_tar_number, tar_header_checksum_ok, tar_name


def auto_int(text: str) -> int:
    return int(text, 0)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-prefix', default='packages.tar.')
    ap.add_argument('--part-count', type=int, required=True)
    ap.add_argument('--target', action='append', required=True)
    ap.add_argument('--before-offset', type=auto_int, required=True,
                    help='exclusive calibrated logical offset to scan backward from')
    ap.add_argument('--scan-bytes', type=auto_int, required=True)
    ap.add_argument('--chunk-size', type=auto_int, default=8 << 20)
    ap.add_argument('--manifest', type=Path)
    ap.add_argument('--retries', type=int, default=3)
    ap.add_argument('--timeout', type=int, default=60)
    args = ap.parse_args()

    if args.before_offset % BLOCK:
        raise SystemExit('--before-offset must be 512-byte aligned')
    if args.chunk_size <= 0 or args.chunk_size % BLOCK:
        raise SystemExit('--chunk-size must be a positive multiple of 512')

    base = args.base_url.rstrip('/')
    urls = [f'{base}/{args.part_prefix}{i:03d}' for i in range(1, args.part_count + 1)]
    arc = SplitHttpTar(urls, retries=args.retries, timeout=args.timeout)
    wanted = {Path(x).name for x in args.target}

    hi = min(args.before_offset, arc.logical_size)
    lo = max(0, hi - args.scan_bytes)
    lo -= lo % BLOCK
    found: dict[str, dict] = {}
    scanned = 0

    chunk_end = hi
    while chunk_end > lo and found.keys() < wanted:
        chunk_start = max(lo, chunk_end - args.chunk_size)
        chunk_start -= chunk_start % BLOCK
        size = chunk_end - chunk_start
        data = arc.read_at(chunk_start, size)
        scanned += size
        # Search from high to low so the nearest previous occurrence wins first.
        for rel in range(size - BLOCK, -1, -BLOCK):
            header = data[rel:rel + BLOCK]
            if header[257:262] != b'ustar' or not tar_header_checksum_ok(header):
                continue
            name = tar_name(header)
            base_name = name.rsplit('/', 1)[-1]
            if base_name not in wanted or base_name in found:
                continue
            member_size = parse_tar_number(header[124:136])
            off = chunk_start + rel
            found[base_name] = {
                'archive_name': name,
                'header_offset': off,
                'data_offset': off + BLOCK,
                'size': member_size,
            }
            print(f'FOUND {base_name}: header=0x{off:X}, data=0x{off+BLOCK:X}, size={member_size}', flush=True)
        chunk_end = chunk_start

    report = {
        'logical_size': arc.logical_size,
        'before_offset': args.before_offset,
        'scan_low_offset': lo,
        'bytes_scanned': scanned,
        'targets': sorted(wanted),
        'found': found,
        'missing': sorted(wanted - found.keys()),
    }
    text = json.dumps(report, indent=2)
    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(text + '\n')
        print(f'wrote {args.manifest}')
    else:
        print(text)
    return 0 if not report['missing'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
