#!/usr/bin/env python3
"""Resolve D1 Investment dye indices through inline F41A8080 resources.

This is the follow-up to d1_investment_dye_resolver.py.  Retail evidence from
Spektar Pandion showed that the D1 63348080 relation payload does not store a
final external dye FileHash at +0x10.  Instead, the bytes converge on the
numeric F41A8080 class hash itself.  D1 ResourcePointer serialization already
used elsewhere in this repository defines:

    target = pointer_field_offset + rel64
    resource_class = u32(target - 4)

Therefore this resolver searches each exact 63348080 relation payload for a
ResourcePointer whose target-4 class is F41A8080 and whose target contains at
least the complete 0xD0-byte SDye_D1 structure.  It requires exactly one such
pointer.  No visual or semantic guessing is used.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

from d1_investment_arrangement_probe import dyn_header, filehash_pkg_index
from d1_investment_dye_resolver import (
    ART_DYE_REFERENCE_TAG,
    DYE_ASSIGNMENTS_TAG,
    DYE_CHANNELS_TAG,
    DYE_CLASS,
    KNOWN_CHANNELS,
    RELATION_CLASS,
    choose_views,
    h32,
    manifest_reference,
    parse_dye_payload,
    tagged_payload,
    entry_for_hash,
    u32,
)


def i64(b: bytes, o: int) -> int:
    if o < 0 or o + 8 > len(b):
        raise ValueError(f"i64 out of bounds at 0x{o:X}/0x{len(b):X}")
    return struct.unpack_from("<q", b, o)[0]


def find_inline_resource_pointers(b: bytes, resource_class: int, minimum_payload: int) -> list[dict]:
    """Find exact serialized D1 ResourcePointers to one class in one payload.

    We scan 4-byte-aligned candidate fields because D1 resource-pointer-bearing
    structs observed in the retail data are naturally aligned, while still
    allowing offsets such as 0x0C.  A hit must satisfy the complete pointer
    equation and have enough bytes for the requested resource structure.
    """
    hits = []
    for field in range(0, max(0, len(b) - 7), 4):
        rel = i64(b, field)
        target = field + rel
        if target < 4 or target + minimum_payload > len(b):
            continue
        if u32(b, target - 4) != resource_class:
            continue
        hits.append({
            "pointer_field_offset": field,
            "relative_offset": rel,
            "resource_class_offset": target - 4,
            "resource_target_offset": target,
            "resource_class_hash": h32(resource_class),
        })
    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("asset_dir", type=Path)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--dye-index", action="append", type=int, default=[])
    ap.add_argument("--channel-index", action="append", type=int, default=[])
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    dye_indices = sorted(set(a.dye_index))
    channel_indices = sorted(set(a.channel_index))
    if not dye_indices:
        raise SystemExit("at least one --dye-index is required")

    views = choose_views(a.asset_dir, a.runtime)
    _, art_e, art_b = tagged_payload(views, ART_DYE_REFERENCE_TAG)
    _, ch_e, ch_b = tagged_payload(views, DYE_CHANNELS_TAG)
    _, as_e, as_b = tagged_payload(views, DYE_ASSIGNMENTS_TAG)

    art_count, art_data = dyn_header(art_b, 0x08)
    ch_count, ch_data = dyn_header(ch_b, 0x08)
    as_count, as_data = dyn_header(as_b, 0x08)

    art_rows = [u32(art_b, art_data + i * 4) for i in range(art_count)]
    ch_rows = [u32(ch_b, ch_data + i * 4) for i in range(ch_count)]
    assignments: dict[int, list[int]] = {}
    for i in range(as_count):
        o = as_data + i * 8
        assignments.setdefault(u32(as_b, o), []).append(u32(as_b, o + 4))

    channels = []
    for idx in channel_indices:
        if idx < 0 or idx >= ch_count:
            raise IndexError(f"channel index {idx} outside {ch_count} rows")
        hv = ch_rows[idx]
        channels.append({
            "channel_index": idx,
            "channel_hash": h32(hv),
            "channel_hash_u32": hv,
            "known_name": KNOWN_CHANNELS.get(hv),
        })

    dyes = []
    unresolved_packages = set()
    for idx in dye_indices:
        if idx < 0 or idx >= art_count:
            raise IndexError(f"dye index {idx} outside {art_count} rows")
        manifest_hash = art_rows[idx]
        relations = assignments.get(manifest_hash, [])
        rec = {
            "dye_index": idx,
            "dye_manifest_hash": h32(manifest_hash),
            "assignment_match_count": len(relations),
            "relation_hashes": [h32(x) for x in relations],
            "resolved": False,
        }
        if len(relations) != 1:
            rec["error"] = f"expected one assignment relation, found {len(relations)}"
            dyes.append(rec)
            continue

        relation_hash = relations[0]
        pkg, _ = filehash_pkg_index(relation_hash)
        if pkg not in views:
            unresolved_packages.add(pkg)
            rec["error"] = f"relation package {pkg:04X} not supplied"
            dyes.append(rec)
            continue

        try:
            _, relation_e, relation_b = entry_for_hash(views, relation_hash)
            relation_manifest = manifest_reference(views, relation_e)
            relation_class = int(relation_manifest["effective_class_hash"], 16)
            if relation_class != RELATION_CLASS:
                raise RuntimeError(
                    f"relation class {h32(relation_class)} / {relation_manifest['effective_class_charm_display']} "
                    "is not D1 63348080"
                )

            hits = find_inline_resource_pointers(relation_b, DYE_CLASS, 0xD0)
            if len(hits) != 1:
                raise RuntimeError(
                    f"expected exactly one inline F41A8080 ResourcePointer, found {len(hits)}; "
                    f"relation_bytes={len(relation_b)} prefix={relation_b[:96].hex()}"
                )
            hit = hits[0]
            target = hit["resource_target_offset"]
            dye_bytes = relation_b[target:target + 0xD0]
            dye = parse_dye_payload(dye_bytes)
            texture_pkgs = sorted({
                x for x in dye["texture_package_ids"].values() if x is not None
            })

            rec.update({
                "resolved": True,
                "resolution_mode": "inline_resource_pointer",
                "relation_hash": h32(relation_hash),
                "relation_package_id": f"{pkg:04X}",
                "relation_entry_reference": relation_e["reference"].upper(),
                "relation_manifest": relation_manifest,
                "relation_payload_size": len(relation_b),
                "relation_payload_sha256": hashlib.sha256(relation_b).hexdigest(),
                "inline_resource_pointer": hit,
                "dye_class_hash": h32(DYE_CLASS),
                "dye_class_charm_display": "F41A8080",
                "dye_payload_sha256": hashlib.sha256(dye_bytes).hexdigest(),
                "dye": dye,
                "referenced_texture_package_ids": [f"{x:04X}" for x in texture_pkgs],
            })
        except Exception as ex:
            rec["error"] = repr(ex)
        dyes.append(rec)

    rep = {
        "schema": "d1_investment_dye_inline_resolver/v1",
        "global_tables": {
            "art_dye_reference": {"tag_hash": ART_DYE_REFERENCE_TAG, "reference": art_e["reference"].upper(), "row_count": art_count},
            "dye_channels": {"tag_hash": DYE_CHANNELS_TAG, "reference": ch_e["reference"].upper(), "row_count": ch_count},
            "dye_manifest_assignments": {"tag_hash": DYE_ASSIGNMENTS_TAG, "reference": as_e["reference"].upper(), "row_count": as_count},
        },
        "requested_dye_indices": dye_indices,
        "requested_channel_indices": channel_indices,
        "channels": channels,
        "dyes": dyes,
        "resolved_dye_count": sum(bool(x.get("resolved")) for x in dyes),
        "unresolved_package_ids": [f"{x:04X}" for x in sorted(unresolved_packages)],
        "logical_views": {
            f"{pkg:04X}": {"package": r.pkg.name, "patch_id": r.h["patch_id"]}
            for pkg, r in sorted(views.items())
        },
        "evidence_policy": (
            "Dye indices and channel indices come from retail equippingBlock arrays. Dye manifests and relations come "
            "from the retail Investment tables. The final SDye_D1 is accepted only when exactly one serialized "
            "ResourcePointer in the proven 63348080 relation satisfies target=field+rel64 and u32(target-4)=F41A8080. "
            "No GStack interpretation, color transform, or visual inference is performed."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(rep, indent=2) + "\n")
    print(json.dumps({
        "channels": channels,
        "resolved_dye_count": rep["resolved_dye_count"],
        "unresolved_package_ids": rep["unresolved_package_ids"],
    }, indent=2))
    for d in dyes:
        print("DYE", json.dumps(d, separators=(",", ":")))
    return 0 if rep["resolved_dye_count"] == len(dye_indices) else 2


if __name__ == "__main__":
    raise SystemExit(main())
