#!/usr/bin/env python3
"""Probe D1 ROI Tiger Oodle-3 compressed blocks.

Supports:
  * Windows: load oo2core_3_win64.dll directly.
  * Linux: load liblinoodle3.so; keep oo2core_3_win64.dll beside it/in cwd.

The tool resolves Tiger patch-family block ownership, verifies the stored SHA-1,
invokes OodleLZ_Decompress, and records decompressed size/hash/prefix. It does
not distribute Oodle binaries.

D1 ROI package blocks have a 0x40000-byte logical address-space capacity, but a
compressed block's real Oodle output length can be shorter and that length is
not serialized in the Tiger block table.  The source-backed allocation quantum
is 0x4000.  `decompress_block()` therefore tests only legal 0x4000-aligned raw
sizes, largest to smallest, and accepts a decode only when Oodle returns exactly
the requested length.  Package readers zero-pad the proven decoded bytes back to
0x40000 only after this step.
"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import platform
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from d1_pkg_probe import BLOCK_SIZE, parse_header, parse_blocks, read_table, patch_path

OODLE_BLOCK_QUANTUM = 0x4000


def sha1_hex(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Oodle3:
    def __init__(self, runtime: Path):
        runtime = runtime.resolve()
        self.runtime = runtime
        if platform.system() == "Windows":
            if runtime.is_dir():
                lib_path = runtime / "oo2core_3_win64.dll"
            else:
                lib_path = runtime
            loader = ctypes.WinDLL
        else:
            # liblinoodle3.so exports an OodleLZ_Decompress-compatible bridge and
            # expects the matching oo2core_3_win64.dll to be available at runtime.
            if runtime.is_dir():
                lib_path = runtime / "liblinoodle3.so"
            else:
                lib_path = runtime
            loader = ctypes.CDLL
        if not lib_path.exists():
            raise FileNotFoundError(f"Oodle runtime not found: {lib_path}")

        self._old_cwd = Path.cwd()
        os.chdir(lib_path.parent)
        try:
            self.lib = loader(str(lib_path))
        finally:
            os.chdir(self._old_cwd)

        try:
            fn = self.lib.OodleLZ_Decompress
        except AttributeError as e:
            raise RuntimeError(f"{lib_path} does not export OodleLZ_Decompress") from e

        fn.restype = ctypes.c_int64
        fn.argtypes = [
            ctypes.c_void_p, ctypes.c_int64,
            ctypes.c_void_p, ctypes.c_int64,
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
            ctypes.c_void_p, ctypes.c_void_p,
            ctypes.c_void_p, ctypes.c_void_p,
            ctypes.c_void_p, ctypes.c_void_p,
            ctypes.c_uint32,
        ]
        self.fn = fn

    def decompress(self, comp: bytes, raw_capacity: int = BLOCK_SIZE) -> bytes:
        src = ctypes.create_string_buffer(comp)
        dst = ctypes.create_string_buffer(raw_capacity)
        # Match tiger-pkg's Oodle 3 call: fuzzSafe=Yes, checkCRC=No,
        # verbosity=Minimal, threadPhase=All, all optional buffers/callbacks null.
        # A D1 ROI call-matrix validation also proved these flags byte-identical
        # to Charm's fuzzSafe=0/checkCRC=0/verbosity=0 call on both full and short
        # retail blocks. Raw destination length, not these flags, is the material
        # variable for the package-block issue.
        n = self.fn(
            ctypes.cast(src, ctypes.c_void_p), len(comp),
            ctypes.cast(dst, ctypes.c_void_p), raw_capacity,
            1, 0, 1,
            None, None, None, None, None, None,
            3,
        )
        if n <= 0:
            raise RuntimeError(f"OodleLZ_Decompress failed with return value {n}")
        if n > raw_capacity:
            raise RuntimeError(f"Oodle returned impossible size {n} > {raw_capacity}")
        return dst.raw[:n]

    def decompress_block(self, comp: bytes, *, max_raw_size: int = BLOCK_SIZE,
                         quantum: int = OODLE_BLOCK_QUANTUM) -> bytes:
        """Decode one D1 ROI Tiger package block with unknown exact raw length.

        Tiger records the compressed stored size but not the real decompressed
        length for a partial logical block.  D1/Oodle package consumers search
        exact destination lengths in 0x4000-byte steps.  Try only those legal
        lengths, largest first, and require Oodle to fill the selected output
        exactly.  The caller remains responsible for padding to the 0x40000
        logical address-space capacity after a successful shorter decode.
        """
        if max_raw_size <= 0 or max_raw_size > BLOCK_SIZE:
            raise ValueError(f"invalid D1 block max raw size {max_raw_size}")
        if quantum <= 0 or max_raw_size % quantum:
            raise ValueError(f"invalid D1 Oodle block quantum/max size: {quantum}/{max_raw_size}")
        failures = []
        for raw_size in range(max_raw_size, quantum - 1, -quantum):
            try:
                dec = self.decompress(comp, raw_capacity=raw_size)
            except Exception as ex:
                failures.append((raw_size, repr(ex)))
                continue
            if len(dec) == raw_size:
                return dec
            failures.append((raw_size, f"partial return {len(dec)}"))
        tail = ", ".join(f"{size:#x}:{err}" for size, err in failures[-4:])
        raise RuntimeError(
            f"OodleLZ_Decompress failed for every legal D1 package-block raw size "
            f"{max_raw_size:#x}..{quantum:#x} step {quantum:#x}; last attempts: {tail}"
        )


def read_pkg_blocks(pkg: Path):
    with pkg.open("rb") as f:
        h = parse_header(f)
        bt = read_table(f, h["block_table_offset"], h["block_table_count"], 32)
    return h, parse_blocks(bt)


def stored_block(pkg: Path, block: dict) -> tuple[Path, bytes]:
    owner = patch_path(pkg, block["patch_id"])
    if not owner.exists():
        raise FileNotFoundError(
            f"block {block['index']} belongs to patch {block['patch_id']}, "
            f"but sibling package is missing: {owner}"
        )
    with owner.open("rb") as f:
        f.seek(block["offset"])
        raw = f.read(block["size"])
    if len(raw) != block["size"]:
        raise EOFError(f"short read for block {block['index']}: {len(raw)} != {block['size']}")
    return owner, raw


def probe_one(pkg: Path, blocks: list[dict], block_index: int, oodle: Oodle3) -> dict:
    b = blocks[block_index]
    owner, stored = stored_block(pkg, b)
    stored_sha1 = sha1_hex(stored)
    if stored_sha1.lower() != b["sha1"].lower():
        raise RuntimeError(
            f"stored SHA-1 mismatch for block {block_index}: "
            f"expected {b['sha1']}, got {stored_sha1}"
        )

    if b["compressed"]:
        dec = oodle.decompress_block(stored)
        mode = "oodle3_variable_d1_block"
    else:
        dec = stored
        mode = "raw"

    return {
        "block_index": block_index,
        "owner_package": str(owner),
        "patch_id": b["patch_id"],
        "flags": b["flags"],
        "compressed": b["compressed"],
        "stored_size": len(stored),
        "stored_sha1": stored_sha1,
        "stored_prefix_hex": stored[:32].hex(),
        "decode_mode": mode,
        "decompressed_size": len(dec),
        "decompressed_sha1": sha1_hex(dec),
        "decompressed_sha256": sha256_hex(dec),
        "decompressed_prefix_hex": dec[:64].hex(),
        "logical_block_capacity": BLOCK_SIZE,
        "oodle_block_quantum": OODLE_BLOCK_QUANTUM,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pkg", type=Path)
    ap.add_argument("--runtime", type=Path, required=True,
                    help="Windows: oo2core_3_win64.dll or containing dir; Linux: liblinoodle3.so or containing dir")
    ap.add_argument("--block", type=int, action="append",
                    help="block index to test; repeatable. Default: first resident compressed block")
    ap.add_argument("--count", type=int, default=1,
                    help="when --block is omitted, test this many resident compressed blocks")
    ap.add_argument("-o", "--output", type=Path)
    args = ap.parse_args()

    pkg = args.pkg.resolve()
    h, blocks = read_pkg_blocks(pkg)
    oodle = Oodle3(args.runtime)

    if args.block:
        indices = args.block
    else:
        indices = []
        for b in blocks:
            if not b["compressed"]:
                continue
            if patch_path(pkg, b["patch_id"]).exists():
                indices.append(b["index"])
                if len(indices) >= args.count:
                    break
    if not indices:
        raise SystemExit("No testable resident blocks found")

    results = [probe_one(pkg, blocks, i, oodle) for i in indices]
    report = {
        "package": str(pkg),
        "platform": h["platform"],
        "package_id": h["pkg_id"],
        "package_patch_id": h["patch_id"],
        "runtime": str(args.runtime.resolve()),
        "results": results,
    }
    text = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
        print(f"wrote {args.output}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
