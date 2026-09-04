#!/usr/bin/env python3
"""Probe exact D1 entry payloads and literal FileHash edges.

For each requested tag this records entry metadata, payload SHA-256, a bounded
prefix, known decoder output when available, and every aligned dword whose value
is the FileHash of another entry in the same logical package snapshot.  This is
a conservative graph probe: literal edges are byte-proven, while it does not
assign a semantic field name unless an existing parser already does so.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_entry_extract import EntryReader, decode_known
from d1_entity_resource_probe import parse_resource

ENTITY_RESOURCE_REF = "80800861"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pkg", type=Path)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--tag", action="append", required=True)
    ap.add_argument("--prefix-bytes", type=lambda x: int(x, 0), default=0x400)
    ap.add_argument("-o", "--output", type=Path)
    a = ap.parse_args()

    r = EntryReader(a.pkg, a.runtime)
    by = {e["tag_hash"].upper(): e for e in r.entries}
    by_int = {int(h, 16): e for h, e in by.items()}
    reports = []

    for requested in a.tag:
        tag = requested.upper().replace("0X", "")
        e = by.get(tag)
        if e is None:
            reports.append({"tag_hash": tag, "present": False})
            continue
        rec = {
            "tag_hash": tag,
            "present": True,
            "entry_index": e["index"],
            "reference": e["reference"].upper(),
            "type": e["type"],
            "subtype": e["subtype"],
            "file_size": e["file_size"],
            "patch_id": e.get("patch_id"),
            "available": r.available(e["index"]),
        }
        if not rec["available"]:
            reports.append(rec)
            continue

        b = r.entry(e["index"])
        rec["payload_size"] = len(b)
        rec["payload_sha256"] = hashlib.sha256(b).hexdigest()
        rec["prefix_hex"] = b[:a.prefix_bytes].hex()

        try:
            rec["decode_known"] = decode_known(e, b, r.h["platform"])
        except Exception as ex:
            rec["decode_known_error"] = repr(ex)

        if rec["reference"] == ENTITY_RESOURCE_REF:
            try:
                rec["entity_resource"] = parse_resource(b, r.h["platform"])
            except Exception as ex:
                rec["entity_resource_error"] = repr(ex)

        edges = []
        for off in range(0, len(b) - 3, 4):
            v = struct.unpack_from("<I", b, off)[0]
            target = by_int.get(v)
            if target is None:
                continue
            edges.append({
                "offset": off,
                "offset_hex": f"0x{off:X}",
                "target_hash": target["tag_hash"].upper(),
                "target_entry_index": target["index"],
                "target_reference": target["reference"].upper(),
                "target_type": target["type"],
                "target_subtype": target["subtype"],
                "target_size": target["file_size"],
                "target_available": r.available(target["index"]),
            })
        rec["aligned_literal_edges"] = edges
        reports.append(rec)

    out = {
        "package": str(a.pkg),
        "package_id": r.h["pkg_id"],
        "platform": r.h["platform"],
        "targets": reports,
    }
    text = json.dumps(out, indent=2)
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(text + "\n")
        print(f"wrote {a.output}")
    else:
        print(text)

    for x in reports:
        print(
            "TAG",
            x["tag_hash"],
            "present", x.get("present"),
            "index", x.get("entry_index"),
            "ref", x.get("reference"),
            "size", x.get("file_size"),
            "edges", len(x.get("aligned_literal_edges", [])),
            file=sys.stderr,
        )
        for edge in x.get("aligned_literal_edges", []):
            print(
                " EDGE",
                edge["offset_hex"],
                edge["target_hash"],
                edge["target_reference"],
                file=sys.stderr,
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
