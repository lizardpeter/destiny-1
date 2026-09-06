#!/usr/bin/env python3
"""Resolve D1 Investment EntityParent tags directly from the split TAR via HTTP ranges.

This avoids downloading multi-hundred-MiB Investment package members.  The caller
provides the exact TAR data offsets for the physical package siblings that were
already checksum-validated by d1_split_tar_extract.py.  The tool reads only:

* the logical-view PKG header / entry table / block table;
* the compressed Tiger blocks needed by requested EntityParent entries.

For Destiny 1 Rise of Iron the Investment EntityParent struct is 0x18 bytes and
its EntityDataROI FileHash is at +0x10 (Charm D2Class_A36F8080 D1 layout).
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import struct
import sys
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from d1_pkg_probe import BLOCK_SIZE, parse_header, parse_entries, parse_blocks
from d1_oodle_probe import Oodle3
from d1_split_tar_extract import SplitHttpTar


def filehash_pkg_index(v: int) -> tuple[int, int]:
    pkg = ((v >> 13) & 0x3FF) + ((((v >> 23) & 3) - 1) * 0x400)
    return pkg, v & 0x1FFF


def tag_hash(pkg_id: int, index: int) -> str:
    return f"{(0x80800000 + (pkg_id << 13) + (index % 8192)) & 0xFFFFFFFF:08X}"


def _align_up(v: int, a: int) -> int:
    return ((v + a - 1) // a) * a


@dataclass(frozen=True)
class Member:
    name: str
    data_offset: int
    size: int
    pkg_id: int
    patch_id: int


def parse_member(text: str) -> Member:
    # NAME:DATA_OFFSET:SIZE ; package id and patch id are inferred from the name.
    name, off_s, size_s = text.rsplit(":", 2)
    m = re.search(r"_([0-9a-fA-F]{4})_([0-9]+)\.pkg$", name)
    if not m:
        raise argparse.ArgumentTypeError(f"cannot infer package/patch id from {name!r}")
    return Member(name, int(off_s, 0), int(size_s, 0), int(m.group(1), 16), int(m.group(2)))


class RemoteLogicalPackage:
    def __init__(self, archive: SplitHttpTar, members: dict[int, Member], runtime: Path):
        self.archive = archive
        self.members = dict(members)
        self.runtime = runtime
        self.oodle = Oodle3(runtime)
        self.block_cache: dict[int, bytes] = {}
        latest = max(self.members)
        self.view = self.members[latest]
        head = archive.read_at(self.view.data_offset, 0x140)
        self.h = parse_header(io.BytesIO(head))
        if self.h["pkg_id"] != self.view.pkg_id:
            raise RuntimeError(f"{self.view.name}: header pkg id {self.h['pkg_id']:04X} != name {self.view.pkg_id:04X}")
        et = archive.read_at(self.view.data_offset + self.h["entry_table_offset"], self.h["entry_table_count"] * 16)
        bt = archive.read_at(self.view.data_offset + self.h["block_table_offset"], self.h["block_table_count"] * 32)
        self.entries = parse_entries(et, self.h["pkg_id"])
        self.blocks = parse_blocks(bt)
        self.block_used_end = [0] * len(self.blocks)
        for e in self.entries:
            remaining = int(e["file_size"])
            bi = int(e["starting_block"])
            off = int(e["starting_block_offset"])
            while remaining > 0 and bi < len(self.blocks):
                n = min(remaining, BLOCK_SIZE - off)
                self.block_used_end[bi] = max(self.block_used_end[bi], off + n)
                remaining -= n
                bi += 1
                off = 0

    def expected_raw_len(self, index: int) -> int:
        used = self.block_used_end[index]
        if used <= 0:
            return BLOCK_SIZE
        return min(BLOCK_SIZE, _align_up(used, 0x4000))

    def block(self, index: int) -> bytes:
        if index in self.block_cache:
            return self.block_cache[index]
        b = self.blocks[index]
        owner = self.members.get(int(b["patch_id"]))
        if owner is None:
            raise FileNotFoundError(f"pkg {self.h['pkg_id']:04X} block {index} requires missing patch {b['patch_id']}")
        raw = self.archive.read_at(owner.data_offset + int(b["offset"]), int(b["size"]))
        got = hashlib.sha1(raw).hexdigest()
        if got.lower() != b["sha1"].lower():
            raise RuntimeError(f"pkg {self.h['pkg_id']:04X} block {index} SHA1 mismatch: {got} != {b['sha1']}")
        if b["encrypted"]:
            raise RuntimeError(f"pkg {self.h['pkg_id']:04X} block {index} is encrypted; sparse resolver has no decrypt step")
        if b["compressed"]:
            expected = self.expected_raw_len(index)
            dec = self.oodle.decompress(raw, raw_capacity=expected)
            if len(dec) != expected:
                raise RuntimeError(
                    f"pkg {self.h['pkg_id']:04X} block {index} decoded {len(dec)} bytes, expected {expected}"
                )
        else:
            dec = raw
        if len(dec) > BLOCK_SIZE:
            raise RuntimeError(f"pkg {self.h['pkg_id']:04X} block {index} oversized after decode")
        if len(dec) < BLOCK_SIZE:
            dec += b"\0" * (BLOCK_SIZE - len(dec))
        self.block_cache[index] = dec
        return dec

    def entry(self, index: int) -> bytes:
        e = self.entries[index]
        remain = int(e["file_size"])
        bi = int(e["starting_block"])
        off = int(e["starting_block_offset"])
        out = bytearray()
        while remain:
            blk = self.block(bi)
            n = min(remain, BLOCK_SIZE - off)
            out += blk[off:off+n]
            remain -= n
            bi += 1
            off = 0
        return bytes(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("arrangements", type=Path, help="JSON from d1_investment_arrangement_probe.py")
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--part-count", type=int, default=10)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--member", action="append", type=parse_member, required=True,
                    help="physical member as NAME:DATA_OFFSET:SIZE; repeatable")
    ap.add_argument("--find-entity", action="append", default=[])
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args()

    base = args.base_url.rstrip("/")
    urls = [f"{base}/packages.tar.{i:03d}" for i in range(1, args.part_count + 1)]
    archive = SplitHttpTar(urls, retries=6, timeout=90)

    groups: dict[int, dict[int, Member]] = {}
    for m in args.member:
        groups.setdefault(m.pkg_id, {})[m.patch_id] = m
    views = {pkg: RemoteLogicalPackage(archive, siblings, args.runtime) for pkg, siblings in sorted(groups.items())}

    src = json.loads(args.arrangements.read_text())
    arrangements = src["arrangements"]
    parent_hashes = sorted({p for row in arrangements for p in row.get("entity_parent_hashes", []) if p})
    wanted = {x.upper().removeprefix("0X") for x in args.find_entity}

    resolved: dict[str, dict] = {}
    errors: list[dict] = []
    for n, ph in enumerate(parent_hashes, 1):
        v = int(ph, 16)
        pkg_id, index = filehash_pkg_index(v)
        rec = {"parent_hash": ph, "package_id": pkg_id, "file_index": index, "resolved": False}
        r = views.get(pkg_id)
        if r is None:
            rec["reason"] = "package family not supplied"
            resolved[ph] = rec
            continue
        if index >= len(r.entries):
            rec["reason"] = "file index outside logical entry table"
            resolved[ph] = rec
            continue
        e = r.entries[index]
        if e["tag_hash"].upper() != ph:
            rec["reason"] = f"logical tag mismatch: {e['tag_hash']}"
            resolved[ph] = rec
            continue
        rec.update({"reference": e["reference"].upper(), "size": e["file_size"], "entry_b": e["entry_b"]})
        try:
            b = r.entry(index)
            if len(b) < 0x14:
                raise RuntimeError(f"payload too short: {len(b)}")
            entity = struct.unpack_from("<I", b, 0x10)[0]
            epkg, eidx = filehash_pkg_index(entity) if entity not in (0, 0xFFFFFFFF) else (-1, -1)
            rec.update({
                "resolved": True,
                "entity_data_hash": f"{entity:08X}",
                "entity_data_package_id": epkg,
                "entity_data_file_index": eidx,
                "payload_sha256": hashlib.sha256(b).hexdigest(),
            })
        except Exception as ex:
            rec["reason"] = repr(ex)
            errors.append({"parent_hash": ph, "error": repr(ex)})
        resolved[ph] = rec
        if n % 500 == 0:
            print(f"resolved/scanned {n}/{len(parent_hashes)} parents", flush=True)

    matches = []
    for row in arrangements:
        entities = []
        for p in row.get("entity_parent_hashes", []):
            if p and p in resolved and resolved[p].get("resolved"):
                entities.append(resolved[p]["entity_data_hash"])
        hit = sorted(wanted & set(entities)) if wanted else []
        if hit:
            matches.append({
                "arrangement_index": row["arrangement_index"],
                "source": row.get("source"),
                "matched_entities": hit,
                "assignment_hashes": row.get("assignment_hashes", []),
                "entity_parent_hashes": row.get("entity_parent_hashes", []),
                "final_entity_hashes": entities,
            })

    report = {
        "parent_count": len(parent_hashes),
        "resolved_count": sum(bool(x.get("resolved")) for x in resolved.values()),
        "error_count": len(errors),
        "wanted_entities": sorted(wanted),
        "matches": matches,
        "parents": resolved,
        "errors": errors,
        "logical_views": {
            f"{pkg:04X}": {
                "view": r.view.name,
                "patch_id": r.view.patch_id,
                "entry_count": len(r.entries),
                "block_count": len(r.blocks),
            }
            for pkg, r in views.items()
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"parents {report['resolved_count']}/{report['parent_count']} resolved; errors {report['error_count']}")
    print(f"reverse matches for {sorted(wanted)}: {len(matches)}")
    for m in matches:
        print("MATCH", m["arrangement_index"], m["entity_parent_hashes"], m["final_entity_hashes"])
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
