#!/usr/bin/env python3
"""Locate named members in the remote Destiny split TAR without a full walk.

Useful when a later calibrated package offset is known but an earlier package
family must be recovered.  The tool range-reads aligned chunks, checks only
512-byte TAR-header candidates, validates ustar magic and checksum, and reports
exact logical header/data offsets.  It does not download package payloads.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from d1_split_tar_extract import BLOCK, SplitHttpTar, parse_tar_number, tar_header_checksum_ok, tar_name


def auto_int(text: str) -> int:
    return int(text, 0)


def scan_chunk(data: bytes, logical_start: int, wanted: set[str]) -> list[dict]:
    rows = []
    usable = len(data) - (len(data) % BLOCK)
    for rel in range(0, usable, BLOCK):
        h = data[rel:rel + BLOCK]
        if h[257:262] != b"ustar" or not tar_header_checksum_ok(h):
            continue
        name = tar_name(h)
        base = name.rsplit("/", 1)[-1]
        if base not in wanted:
            continue
        off = logical_start + rel
        rows.append({
            "archive_name": name,
            "basename": base,
            "header_offset": off,
            "data_offset": off + BLOCK,
            "size": parse_tar_number(h[124:136]),
        })
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--part-prefix", default="packages.tar.")
    ap.add_argument("--part-count", type=int, required=True)
    ap.add_argument("--target", action="append", required=True)
    ap.add_argument("--before-offset", type=auto_int, required=True,
                    help="scan strictly before this logical offset")
    ap.add_argument("--window", type=auto_int, default=1 << 30,
                    help="maximum bytes to scan backwards (default 1 GiB)")
    ap.add_argument("--chunk-size", type=auto_int, default=8 << 20)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    if args.before_offset % BLOCK:
        raise SystemExit("--before-offset must be 512-byte aligned")
    chunk = (args.chunk_size // BLOCK) * BLOCK
    if chunk <= 0:
        raise SystemExit("--chunk-size must be at least 512")

    base = args.base_url.rstrip("/")
    urls = [f"{base}/{args.part_prefix}{i:03d}" for i in range(1, args.part_count + 1)]
    arc = SplitHttpTar(urls)
    wanted = {Path(x).name for x in args.target}
    found: dict[str, dict] = {}
    hi = min(args.before_offset, arc.logical_size)
    lo_limit = max(0, hi - args.window)
    scanned = 0

    while hi > lo_limit and set(found) != wanted:
        lo = max(lo_limit, hi - chunk)
        lo -= lo % BLOCK
        size = hi - lo
        if size <= 0:
            break
        print(f"scan 0x{lo:X}..0x{hi:X} ({size} bytes)", flush=True)
        data = arc.read_at(lo, size)
        for row in scan_chunk(data, lo, wanted - set(found)):
            found[row["basename"]] = row
            print(
                f"FOUND {row['basename']}: header=0x{row['header_offset']:X}, "
                f"data=0x{row['data_offset']:X}, size={row['size']}",
                flush=True,
            )
        scanned += size
        hi = lo

    report = {
        "base_url": base,
        "logical_size": arc.logical_size,
        "before_offset": args.before_offset,
        "window": args.window,
        "bytes_scanned": scanned,
        "targets": sorted(wanted),
        "found": {k: found[k] for k in sorted(found)},
        "missing": sorted(wanted - set(found)),
    }
    text = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n")
        print(f"wrote {args.output}")
    else:
        print(text)
    return 0 if not report["missing"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
