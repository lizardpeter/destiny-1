#!/usr/bin/env python3
"""Resolve all D1 art-arrangement EntityParent FileHashes remotely.

Input is the JSON produced by d1_investment_arrangement_probe.py.  The parent
FileHashes already encode their package id and entry index.  This tool:

  1. derives every required package family from those FileHashes,
  2. discovers every physical patch member for those families from packages.txt,
  3. locates those members in the split TAR,
  4. opens one logical RemoteLogicalPackage per package id, and
  5. resolves EntityParent +0x10 -> EntityDataROI FileHash.

No filename affinity or package adjacency is used to decide ownership: package
ids and file indices come directly from the serialized parent FileHashes.
"""
from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_investment_arrangement_probe import filehash_pkg_index, h32
from d1_remote_investment_parent_probe import RemoteLogicalPackage, parse_member
from d1_split_tar_extract import SplitHttpTar

# Exact TAR header immediately preceding ps4_investment_assets_0135_0.pkg.
# Its data begins at 0x5996C3200, so the ustar header is 0x200 bytes earlier.
# This is the earliest package family referenced by the retail art-arrangement
# parent set we have observed, and unlike a rounded address it is a validated
# 512-byte TAR header boundary.
DEFAULT_INVESTMENT_ASSETS_TAR_HEADER = 0x5996C3000


def u32(b: bytes, o: int) -> int:
    return struct.unpack_from("<I", b, o)[0]


def discover_family_names(packages_txt: str, package_ids: set[int]) -> dict[int, list[str]]:
    out = {p: [] for p in package_ids}
    rx = re.compile(r"^ps4_investment_assets_([0-9a-fA-F]{4})_(\d+)\.pkg$")
    for line in packages_txt.splitlines():
        name = Path(line.strip()).name
        m = rx.fullmatch(name)
        if not m:
            continue
        pkg = int(m.group(1), 16)
        if pkg in out:
            out[pkg].append(name)
    missing = [f"{p:04X}" for p, names in out.items() if not names]
    if missing:
        raise ValueError(f"packages.txt has no investment_assets members for required package ids: {missing}")
    for names in out.values():
        names.sort(key=lambda x: int(re.search(r"_(\d+)\.pkg$", x).group(1)))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("arrangements_json", type=Path)
    ap.add_argument("--packages-list", type=Path, required=True)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--part-count", type=int, default=10)
    ap.add_argument("--start-offset", type=lambda x: int(x, 0), default=DEFAULT_INVESTMENT_ASSETS_TAR_HEADER,
                    help="exact validated TAR header offset at/before required investment_assets families")
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args()

    src = json.loads(args.arrangements_json.read_text())
    rows = src.get("arrangements", [])
    parent_hashes = sorted({
        ph.upper()
        for row in rows
        for ph in row.get("entity_parent_hashes", [])
        if ph not in (None, "00000000", "FFFFFFFF")
    })
    package_ids = {filehash_pkg_index(int(ph, 16))[0] for ph in parent_hashes}
    family_names = discover_family_names(args.packages_list.read_text(errors="replace"), package_ids)
    wanted = {n for names in family_names.values() for n in names}

    base = args.base_url.rstrip("/")
    arc = SplitHttpTar([f"{base}/packages.tar.{i:03d}" for i in range(1, args.part_count + 1)], retries=6, timeout=90)
    found, headers = arc.find(wanted, start_offset=args.start_offset)
    missing_members = sorted(wanted - set(found))
    if missing_members:
        raise RuntimeError(f"split TAR did not locate required package members: {missing_members}")

    remotes: dict[int, RemoteLogicalPackage] = {}
    family_manifest = {}
    for pkg, names in sorted(family_names.items()):
        specs = []
        member_rows = []
        for name in names:
            f = found[name]
            spec = parse_member(f"{name}:0x{f['data_offset']:X}:{f['size']}")
            specs.append(spec)
            member_rows.append({"name": name, "header_offset": f["header_offset"], "data_offset": f["data_offset"], "size": f["size"], "patch_id": spec.patch_id})
        remotes[pkg] = RemoteLogicalPackage(arc, {m.patch_id: m for m in specs}, args.runtime)
        family_manifest[f"{pkg:04X}"] = {"members": member_rows, "logical_view": remotes[pkg].view.name}

    parent_resolution = {}
    errors = []
    for n, ph in enumerate(parent_hashes, 1):
        v = int(ph, 16)
        pkg, idx = filehash_pkg_index(v)
        rr = remotes[pkg]
        rec = {"parent_hash": ph, "package_id": pkg, "file_index": idx, "resolved": False}
        try:
            if idx >= len(rr.entries):
                raise ValueError("parent file index beyond logical entry table")
            e = rr.entries[idx]
            rec.update({"entry_index": e["index"], "tag_hash": e["tag_hash"].upper(), "reference": e["reference"].upper(), "size": e["file_size"]})
            if e["tag_hash"].upper() != ph:
                raise ValueError(f"logical entry tag mismatch {e['tag_hash']}")
            b = rr.entry(idx)
            if len(b) < 0x14:
                raise ValueError("EntityParent payload shorter than +0x10 EntityDataROI field")
            entity_data = u32(b, 0x10)
            epkg, eidx = filehash_pkg_index(entity_data) if entity_data not in (0, 0xFFFFFFFF) else (-1, -1)
            rec.update({
                "resolved": entity_data not in (0, 0xFFFFFFFF),
                "payload_size": len(b),
                "entity_data_hash": h32(entity_data),
                "entity_data_package_id": epkg if epkg >= 0 else None,
                "entity_data_file_index": eidx if eidx >= 0 else None,
            })
            if not rec["resolved"]:
                rec["reason"] = "EntityDataROI is null/sentinel"
        except Exception as ex:
            rec["reason"] = repr(ex)
            errors.append({"parent_hash": ph, "error": repr(ex)})
        parent_resolution[ph] = rec
        if n % 500 == 0:
            print(f"parents {n}/{len(parent_hashes)} resolved={sum(x.get('resolved',False) for x in parent_resolution.values())}", flush=True)

    out_rows = []
    unresolved_slots = 0
    for row in rows:
        q = dict(row)
        q["entities"] = []
        for ph in row.get("entity_parent_hashes", []):
            if ph is None:
                q["entities"].append(None)
                unresolved_slots += 1
            else:
                rec = parent_resolution.get(ph.upper())
                q["entities"].append(rec)
                if not rec or not rec.get("resolved"):
                    unresolved_slots += 1
        out_rows.append(q)

    resolved_count = sum(x.get("resolved", False) for x in parent_resolution.values())
    out = dict(src)
    out["arrangements"] = out_rows
    out["parent_resolution"] = parent_resolution
    out["remote_parent_resolution"] = {
        "required_package_ids": [f"{p:04X}" for p in sorted(package_ids)],
        "package_families": family_manifest,
        "tar_start_header": f"0x{args.start_offset:X}",
        "tar_headers_scanned": headers,
        "unique_parent_count": len(parent_hashes),
        "resolved_parent_count": resolved_count,
        "unresolved_parent_count": len(parent_hashes) - resolved_count,
        "unresolved_arrangement_slots": unresolved_slots,
        "remote_blocks_read": {f"{p:04X}": len(rr.block_cache) for p, rr in sorted(remotes.items())},
        "errors": errors[:500],
        "evidence_policy": "Every package family/index is derived from the serialized EntityParent FileHash. EntityDataROI is read directly from parent +0x10.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: v for k, v in out["remote_parent_resolution"].items() if k not in ("package_families", "errors", "remote_blocks_read")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
