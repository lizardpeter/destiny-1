#!/usr/bin/env python3
"""Source-correlated inventory of every current D1 ROI s_scope payload.

Input authority:
  * global current FileEntry.Reference census: class 80801C47 == s_scope;
  * exact recovered payload bytes + SHA-256;
  * pinned quicktag raw-string table parser for tag 0x80800065.

For D1 Rise of Iron, quicktag's raw-string reader treats 0x80800065 as:
  u32 tag 0x80800065
  u64 little-endian buffer_size
  buffer_size bytes containing NUL-delimited strings

Every current s_scope payload currently contains exactly one such terminal raw
string table.  This tool promotes only that serialized raw name.  A scope name
does not prove what runtime constant-buffer/API slot it feeds.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

SCOPE_CLASS = "80801C47"
RAW_STRING_TAG = 0x80800065
EXPECTED_COUNT = 23


def parse_raw_string_blob(data: bytes, marker: int) -> dict:
    if marker + 12 > len(data):
        raise ValueError("raw string header truncated")
    tag = struct.unpack_from("<I", data, marker)[0]
    if tag != RAW_STRING_TAG:
        raise ValueError(f"raw string marker drift {tag:08X}")
    n = struct.unpack_from("<Q", data, marker + 4)[0]
    start = marker + 12
    end = start + n
    if end > len(data):
        raise ValueError(f"raw string buffer overruns payload: {end}>{len(data)}")
    raw = data[start:end]
    strings = []
    off = 0
    for part in raw.split(b"\0"):
        if part:
            try:
                s = part.decode("utf-8")
            except UnicodeDecodeError as ex:
                raise ValueError(f"raw string is not UTF-8: {ex}") from ex
            strings.append({"offset": start + off, "text": s})
        off += len(part) + 1
    return {
        "marker_offset": marker,
        "buffer_size": n,
        "buffer_start": start,
        "buffer_end": end,
        "ends_at_payload_end": end == len(data),
        "strings": strings,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--census", type=Path, required=True)
    ap.add_argument("--payload-dir", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    d = json.loads(a.census.read_text())
    v: list[str] = []
    if d.get("status") != "D1_REMOTE_REFERENCE_CLASS_CENSUS_EXACT" or d.get("violations"):
        v.append("global_scope_census_not_exact")
    if int(d.get("matching_entry_count", -1)) != EXPECTED_COUNT:
        v.append(f"scope_count:{d.get('matching_entry_count')}")
    if d.get("reference_counts") != {SCOPE_CLASS: EXPECTED_COUNT}:
        v.append(f"reference_counts:{d.get('reference_counts')}")
    if d.get("package_counts") != {"0172": EXPECTED_COUNT}:
        v.append(f"package_counts:{d.get('package_counts')}")

    rows = []
    names = []
    for r in d.get("rows", []):
        h = str(r.get("tag_hash", "")).upper()
        if str(r.get("reference", "")).upper() != SCOPE_CLASS:
            v.append(f"{h}:class_drift")
        p = a.payload_dir / f"{h}.bin"
        if not p.is_file():
            v.append(f"{h}:payload_missing")
            continue
        b = p.read_bytes()
        sha = hashlib.sha256(b).hexdigest()
        if sha != r.get("payload_sha256"):
            v.append(f"{h}:sha256_mismatch:{sha}")
        if len(b) != int(r.get("payload_bytes", -1)) or len(b) != int(r.get("declared_size", -2)):
            v.append(f"{h}:size_mismatch")

        markers = [
            off for off in range(0, len(b) - 3)
            if struct.unpack_from("<I", b, off)[0] == RAW_STRING_TAG
        ]
        if len(markers) != 1:
            v.append(f"{h}:raw_string_marker_count:{len(markers)}")
            continue
        try:
            raw = parse_raw_string_blob(b, markers[0])
        except Exception as ex:
            v.append(f"{h}:raw_string_parse:{ex}")
            continue
        if not raw["ends_at_payload_end"]:
            v.append(f"{h}:raw_string_table_not_terminal")
        if len(raw["strings"]) != 1:
            v.append(f"{h}:raw_string_count:{len(raw['strings'])}")
        name = raw["strings"][0]["text"] if len(raw["strings"]) == 1 else None
        if name is not None:
            names.append(name)
        rows.append({
            "tag_hash": h,
            "package_id": r.get("package_id"),
            "entry_index": r.get("entry_index"),
            "payload_bytes": len(b),
            "payload_sha256": sha,
            "scope_name": name,
            "raw_string_table": raw,
            "resolved_aligned_filehash_edges": r.get("resolved_aligned_filehash_edges", []),
        })

    if len(rows) != EXPECTED_COUNT:
        v.append(f"parsed_scope_count:{len(rows)}")
    if len(set(names)) != len(names):
        v.append("duplicate_scope_names")
    exact = not v
    dye_like = sorted(n for n in names if "dye" in n.lower() or "gear" in n.lower())

    out = {
        "schema": "d1_scope_inventory/v1",
        "status": "D1_CURRENT_SCOPE_INVENTORY_EXACT" if exact else "D1_CURRENT_SCOPE_INVENTORY_VIOLATIONS",
        "source_class": SCOPE_CLASS,
        "scope_count": len(rows),
        "scope_names": sorted(names),
        "rows": sorted(rows, key=lambda x: x["tag_hash"]),
        "raw_string_layout": {
            "tag": "80800065",
            "size_encoding": "u64 little-endian for D1 Rise of Iron",
            "strings": "NUL-delimited buffer",
            "source": "v4nguard/quicktag crates/scanner/src/lib.rs read_raw_string_blob",
            "source_commit": "bdad2e92442439bb0f71c67aca608b7ca0a8c74c",
            "source_blob_sha1": "56e50ee0118e399e6db73d420c0ef70cc715857c",
        },
        "gear_or_dye_named_scopes": dye_like,
        "gates": {
            "all_current_scope_payloads_recovered": exact,
            "all_current_scope_raw_names_closed": exact,
            "gear_or_dye_scope_identified_by_serialized_name": bool(dye_like),
            "api15_runtime_value_closed": False,
            "runtime_t4_binding_closed": False,
        },
        "correction": (
            "The complete current class-80801C47 population contains no serialized scope name containing "
            "'gear' or 'dye'. Therefore the prior search strategy of identifying the API15/t4 producer by "
            "looking for a literally gear/dye-named s_scope is not supported by current retail bytes."
        ) if exact and not dye_like else None,
        "violations": v,
        "policy": (
            "Raw scope names are serialized source-correlated identities, not proof of API-slot ownership. "
            "Absence of a gear/dye name rejects only the name-based search heuristic; it does not prove that "
            "none of these scopes participates indirectly in gear/dye rendering."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({
        "status": out["status"],
        "scope_count": out["scope_count"],
        "scope_names": out["scope_names"],
        "gear_or_dye_named_scopes": dye_like,
        "gates": out["gates"],
        "violations": v,
    }, indent=2))
    return 0 if exact else 2


if __name__ == "__main__":
    raise SystemExit(main())
