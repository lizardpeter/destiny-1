#!/usr/bin/env python3
"""Sparse-extract named Destiny package files from an HTTP-hosted split TAR.

The Cohae Destiny archive publishes the final package corpus as large
``packages.tar.001`` ... split volumes rather than individual .pkg URLs. TAR
headers are only 512 bytes and encode each member's payload size, so the archive
can be walked with HTTP Range requests without downloading tens of gigabytes.

This tool:
  * discovers each split-volume size using ``Range: bytes=0-0``;
  * treats the volumes as one logical byte stream;
  * walks only TAR headers, jumping over payloads by their recorded sizes;
  * can resume a previously calibrated walk from ``--start-offset``;
  * validates the standard TAR header checksum at every visited member;
  * downloads only explicitly requested members, even across split boundaries;
  * records exact logical TAR offsets and SHA-256 hashes in a JSON manifest.

Examples:

  python tools/d1_split_tar_extract.py \
    --base-url https://crypt.cohae.dev/destiny/ps4/packages/latest \
    --part-count 10 \
    --target ps4_arch_vex_com01_0767_1.pkg \
    --target ps4_arch_vex_com01_0767_4.pkg \
    --out recovered

After a prior manifest/log has calibrated the first family member's TAR header,
a repeat analysis can start there while retaining checksum validation:

  python tools/d1_split_tar_extract.py ... \
    --start-offset 0x105C6E000 \
    --target ps4_arch_vex_com01_0767_0.pkg ...
"""
from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import re
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BLOCK = 512
USER_AGENT = "d1-split-tar-extract/1.1"


def parse_tar_number(field: bytes) -> int:
    field = field.rstrip(b"\0 ").lstrip(b" ")
    if not field:
        return 0
    if field[0] & 0x80:
        raw = bytearray(field)
        raw[0] &= 0x7F
        return int.from_bytes(raw, "big")
    return int(field, 8)


def tar_header_checksum_ok(header: bytes) -> bool:
    if len(header) != BLOCK:
        return False
    try:
        expected = parse_tar_number(header[148:156])
    except Exception:
        return False
    temp = bytearray(header)
    temp[148:156] = b"        "
    return sum(temp) == expected


def tar_name(header: bytes) -> str:
    name = header[:100].split(b"\0", 1)[0].decode("utf-8", "replace")
    prefix = header[345:500].split(b"\0", 1)[0].decode("utf-8", "replace")
    return f"{prefix}/{name}" if prefix else name


class SplitHttpTar:
    def __init__(self, urls: list[str], retries: int = 3, timeout: int = 60):
        self.urls = urls
        self.retries = retries
        self.timeout = timeout
        self.sizes = [self._discover_size(url) for url in urls]
        self.starts = [0]
        for size in self.sizes:
            self.starts.append(self.starts[-1] + size)

    @property
    def logical_size(self) -> int:
        return self.starts[-1]

    def _request(self, url: str, start: int, end: int):
        req = Request(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Range": f"bytes={start}-{end}",
            },
        )
        last = None
        for attempt in range(self.retries):
            try:
                return urlopen(req, timeout=self.timeout)
            except (HTTPError, URLError, TimeoutError) as ex:
                last = ex
                if attempt + 1 < self.retries:
                    time.sleep(min(2 ** attempt, 4))
        raise RuntimeError(f"range request failed for {url}: {last!r}")

    def _discover_size(self, url: str) -> int:
        with self._request(url, 0, 0) as resp:
            status = getattr(resp, "status", None)
            if status != 206:
                raise RuntimeError(f"HTTP Range unsupported for {url}: status={status}")
            content_range = resp.headers.get("Content-Range", "")
            m = re.fullmatch(r"bytes 0-0/(\d+)", content_range)
            if not m:
                raise RuntimeError(f"unexpected Content-Range for {url}: {content_range!r}")
            one = resp.read()
            if len(one) != 1:
                raise RuntimeError(f"expected one byte from size probe for {url}, got {len(one)}")
            return int(m.group(1))

    def _part_for(self, logical_offset: int) -> int:
        i = bisect.bisect_right(self.starts, logical_offset) - 1
        if i < 0 or i >= len(self.urls):
            raise EOFError(f"logical offset outside split stream: {logical_offset}")
        return i

    def read_at(self, logical_offset: int, size: int) -> bytes:
        out = bytearray()
        off = logical_offset
        remain = size
        while remain:
            part = self._part_for(off)
            local = off - self.starts[part]
            take = min(remain, self.sizes[part] - local)
            if take <= 0:
                raise EOFError((logical_offset, size, off, remain))
            with self._request(self.urls[part], local, local + take - 1) as resp:
                if getattr(resp, "status", None) != 206:
                    raise RuntimeError(f"range request returned HTTP {getattr(resp, 'status', None)}")
                data = resp.read()
            if len(data) != take:
                raise EOFError(f"short range read: expected {take}, got {len(data)}")
            out += data
            off += take
            remain -= take
        return bytes(out)

    def copy_to(self, logical_offset: int, size: int, dst: Path, chunk_size: int = 8 << 20) -> str:
        dst.parent.mkdir(parents=True, exist_ok=True)
        sha = hashlib.sha256()
        off = logical_offset
        remain = size
        with dst.open("wb") as f:
            while remain:
                part = self._part_for(off)
                local = off - self.starts[part]
                take = min(remain, self.sizes[part] - local, chunk_size)
                with self._request(self.urls[part], local, local + take - 1) as resp:
                    if getattr(resp, "status", None) != 206:
                        raise RuntimeError(f"range request returned HTTP {getattr(resp, 'status', None)}")
                    data = resp.read()
                if len(data) != take:
                    raise EOFError(f"short extraction read: expected {take}, got {len(data)}")
                f.write(data)
                sha.update(data)
                off += take
                remain -= take
        if dst.stat().st_size != size:
            raise RuntimeError(f"extracted size mismatch for {dst}: {dst.stat().st_size} != {size}")
        return sha.hexdigest()

    def find(self, wanted_basenames: set[str], start_offset: int = 0) -> tuple[dict[str, dict], int]:
        if start_offset < 0 or start_offset % BLOCK:
            raise ValueError(f"start offset must be a non-negative 512-byte boundary: {start_offset:#x}")
        if start_offset >= self.logical_size:
            raise ValueError(f"start offset outside split stream: {start_offset:#x}")
        found: dict[str, dict] = {}
        off = start_offset
        headers = 0
        zero_headers = 0
        while off + BLOCK <= self.logical_size:
            header = self.read_at(off, BLOCK)
            if header == b"\0" * BLOCK:
                zero_headers += 1
                if zero_headers >= 2:
                    break
                off += BLOCK
                continue
            zero_headers = 0
            if header[257:262] != b"ustar":
                raise RuntimeError(
                    f"invalid TAR header at logical 0x{off:X}: magic={header[257:263]!r}; "
                    "--start-offset must point at an exact TAR header boundary"
                )
            if not tar_header_checksum_ok(header):
                raise RuntimeError(f"TAR checksum mismatch at logical 0x{off:X}")
            name = tar_name(header)
            member_size = parse_tar_number(header[124:136])
            headers += 1
            base = name.rsplit("/", 1)[-1]
            if base in wanted_basenames:
                found[base] = {
                    "archive_name": name,
                    "header_offset": off,
                    "data_offset": off + BLOCK,
                    "size": member_size,
                }
                print(
                    f"FOUND {base}: header=0x{off:X}, data=0x{off + BLOCK:X}, size={member_size}",
                    flush=True,
                )
                if found.keys() >= wanted_basenames:
                    break
            off += BLOCK + ((member_size + BLOCK - 1) // BLOCK) * BLOCK
        return found, headers


def auto_int(text: str) -> int:
    return int(text, 0)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True, help="directory containing packages.tar.NNN")
    ap.add_argument("--part-prefix", default="packages.tar.")
    ap.add_argument("--part-count", type=int, required=True)
    ap.add_argument("--target", action="append", required=True, help="archive basename to extract; repeatable")
    ap.add_argument("--start-offset", type=auto_int, default=0,
                    help="known logical TAR header offset to resume walking from (decimal or 0x...); still validated")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--manifest", type=Path)
    ap.add_argument("--retries", type=int, default=3)
    ap.add_argument("--timeout", type=int, default=60)
    args = ap.parse_args()

    base = args.base_url.rstrip("/")
    urls = [f"{base}/{args.part_prefix}{i:03d}" for i in range(1, args.part_count + 1)]
    wanted = {Path(x).name for x in args.target}
    archive = SplitHttpTar(urls, retries=args.retries, timeout=args.timeout)
    print(f"logical split-TAR size: {archive.logical_size} bytes", flush=True)
    if args.start_offset:
        print(f"resuming TAR walk at validated header 0x{args.start_offset:X}", flush=True)

    found, header_count = archive.find(wanted, start_offset=args.start_offset)
    missing = sorted(wanted - found.keys())
    if missing:
        raise SystemExit(f"requested members not found after {header_count} TAR headers: {missing}")

    args.out.mkdir(parents=True, exist_ok=True)
    for name in sorted(wanted):
        row = found[name]
        dst = args.out / name
        row["output"] = str(dst)
        row["sha256"] = archive.copy_to(row["data_offset"], row["size"], dst)
        print(f"EXTRACTED {name}: {row['size']} bytes sha256={row['sha256']}", flush=True)

    manifest = {
        "base_url": base,
        "part_prefix": args.part_prefix,
        "part_count": args.part_count,
        "part_sizes": archive.sizes,
        "logical_size": archive.logical_size,
        "start_offset": args.start_offset,
        "tar_headers_scanned": header_count,
        "members": {name: found[name] for name in sorted(found)},
    }
    manifest_path = args.manifest or (args.out / "split_tar_extract_manifest.json")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
