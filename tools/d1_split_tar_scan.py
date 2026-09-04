#!/usr/bin/env python3
"""Find TAR members in a bounded logical window of an HTTP split TAR.

Unlike d1_split_tar_extract.py, this does not require a known starting header.
It range-reads a bounded window, searches for ustar magic, reconstructs the
512-byte candidate header, then requires both 512-byte alignment and a valid
TAR checksum before accepting a member.  It is intended for calibrating exact
member offsets near an already-known archive location without walking the full
52+ GiB corpus.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from d1_split_tar_extract import (
    BLOCK,
    SplitHttpTar,
    parse_tar_number,
    tar_header_checksum_ok,
    tar_name,
)


def auto_int(s: str) -> int:
    return int(s, 0)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--part-count", type=int, default=10)
    ap.add_argument("--start", type=auto_int, required=True)
    ap.add_argument("--end", type=auto_int, required=True)
    ap.add_argument("--chunk-size", type=auto_int, default=32 << 20)
    ap.add_argument("--contains", action="append", default=[], help="case-sensitive basename substring; repeatable")
    ap.add_argument("--target", action="append", default=[], help="exact basename; repeatable")
    ap.add_argument("--all", action="store_true", help="emit every validated TAR header in the window")
    ap.add_argument("--retries", type=int, default=5)
    ap.add_argument("--timeout", type=int, default=90)
    ap.add_argument("-o", "--output", type=Path)
    a = ap.parse_args()

    if a.start < 0 or a.end <= a.start:
        raise SystemExit("require 0 <= start < end")
    if a.start % BLOCK or a.end % BLOCK:
        raise SystemExit("start/end must be 512-byte aligned")
    base = a.base_url.rstrip("/")
    arc = SplitHttpTar([f"{base}/packages.tar.{i:03d}" for i in range(1, a.part_count + 1)], retries=a.retries, timeout=a.timeout)
    end = min(a.end, arc.logical_size)
    targets = {Path(x).name for x in a.target}
    rows: dict[int, dict] = {}

    # Include one header of overlap before each non-first chunk so a candidate
    # whose header straddles a chunk boundary is still reconstructed exactly.
    pos = a.start
    while pos < end:
        read_start = max(a.start, pos - (BLOCK if pos > a.start else 0))
        read_end = min(end, pos + a.chunk_size)
        buf = arc.read_at(read_start, read_end - read_start)
        search = 0
        while True:
            p = buf.find(b"ustar", search)
            if p < 0:
                break
            h_off = read_start + p - 257
            local = p - 257
            search = p + 1
            if h_off < a.start or h_off + BLOCK > end or h_off % BLOCK:
                continue
            if local < 0 or local + BLOCK > len(buf):
                header = arc.read_at(h_off, BLOCK)
            else:
                header = buf[local:local + BLOCK]
            if not tar_header_checksum_ok(header):
                continue
            name = tar_name(header)
            base_name = name.rsplit("/", 1)[-1]
            size = parse_tar_number(header[124:136])
            wanted = a.all or base_name in targets or any(s in base_name for s in a.contains)
            if wanted:
                rows[h_off] = {
                    "archive_name": name,
                    "basename": base_name,
                    "header_offset": h_off,
                    "data_offset": h_off + BLOCK,
                    "size": size,
                }
        print(f"scanned 0x{pos:X}..0x{read_end:X}; matches={len(rows)}", flush=True)
        pos += a.chunk_size

    ordered = [rows[k] for k in sorted(rows)]
    found_names = {r["basename"] for r in ordered}
    report = {
        "logical_size": arc.logical_size,
        "start": a.start,
        "end": end,
        "chunk_size": a.chunk_size,
        "contains": a.contains,
        "targets": sorted(targets),
        "missing_targets": sorted(targets - found_names),
        "match_count": len(ordered),
        "matches": ordered,
    }
    text = json.dumps(report, indent=2)
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(text + "\n")
        print(f"wrote {a.output}")
    print("=== MATCHES ===")
    for r in ordered:
        print(f"{r['basename']}: header=0x{r['header_offset']:X} data=0x{r['data_offset']:X} size={r['size']}")
    if targets and report["missing_targets"]:
        print("missing targets:", report["missing_targets"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
