#!/usr/bin/env python3
"""Exact D1 ROI Investment dye resolver.

Retail Spektar evidence closes the final D1 chain as:

  equippingBlock DyeIndex
    -> 80A5FFA8 ArtDyeReference[DyeIndex] -> DyeManifestHash
    -> 80A7E1DC assignment map -> relation FileHash
    -> relation metadata GetReferenceFromManifest() == 63348080
    -> 24-byte generic relation payload, FileHash at +0x10
    -> final dye entry
    -> final dye entry metadata Reference == F41A8080 directly
    -> entry payload is SDye_D1 (0xD0 schema)

The last distinction matters: the final DyeD1 entry is not another D1 manifest
wrapper.  Its package entry Reference is the F41A8080 class itself.  This was
established from the exact 24-byte relation payloads and final entry metadata,
not inferred from filenames or appearance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
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
    entry_for_hash,
    h32,
    manifest_reference,
    parse_dye_payload,
    tagged_payload,
    u32,
)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("asset_dir", type=Path)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--dye-index", action="append", type=int, default=[])
    ap.add_argument("--channel-index", action="append", type=int, default=[])
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    dyes_req = sorted(set(a.dye_index))
    channels_req = sorted(set(a.channel_index))
    if not dyes_req:
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
    for idx in channels_req:
        if idx < 0 or idx >= ch_count:
            raise IndexError(f"channel index {idx} outside {ch_count} rows")
        hv = ch_rows[idx]
        channels.append({
            "channel_index": idx,
            "channel_hash": h32(hv),
            "channel_hash_u32": hv,
            "known_name": KNOWN_CHANNELS.get(hv),
        })

    rows = []
    unresolved_pkgs: set[int] = set()
    for idx in dyes_req:
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
            rows.append(rec)
            continue

        relation_hash = relations[0]
        rpkg, _ = filehash_pkg_index(relation_hash)
        if rpkg not in views:
            unresolved_pkgs.add(rpkg)
            rec["error"] = f"relation package {rpkg:04X} not supplied"
            rows.append(rec)
            continue

        try:
            _, relation_e, relation_b = entry_for_hash(views, relation_hash)
            relation_manifest = manifest_reference(views, relation_e)
            relation_class = int(relation_manifest["effective_class_hash"], 16)
            if relation_class != RELATION_CLASS:
                raise RuntimeError(
                    f"relation effective class {h32(relation_class)} / "
                    f"{relation_manifest['effective_class_charm_display']} != 63348080"
                )
            if len(relation_b) != 0x18:
                raise RuntimeError(f"expected 0x18-byte D1 generic relation parent, got {len(relation_b):#x}")

            dye_hash = u32(relation_b, 0x10)
            dpkg, _ = filehash_pkg_index(dye_hash)
            if dpkg not in views:
                unresolved_pkgs.add(dpkg)
                rec.update({
                    "relation_hash": h32(relation_hash),
                    "relation_manifest": relation_manifest,
                    "dye_file_hash": h32(dye_hash),
                    "error": f"final dye package {dpkg:04X} not supplied",
                })
                rows.append(rec)
                continue

            _, dye_e, dye_b = entry_for_hash(views, dye_hash)
            direct_ref = int(dye_e["reference"], 16)
            if direct_ref != DYE_CLASS:
                raise RuntimeError(
                    f"final dye {h32(dye_hash)} direct metadata reference {h32(direct_ref)} "
                    "is not F41A8080/80801AF4"
                )
            dye = parse_dye_payload(dye_b)
            texture_pkgs = sorted({x for x in dye["texture_package_ids"].values() if x is not None})

            rec.update({
                "resolved": True,
                "resolution_mode": "generic_relation_to_direct_dye_entry",
                "relation_hash": h32(relation_hash),
                "relation_package_id": f"{rpkg:04X}",
                "relation_manifest": relation_manifest,
                "relation_payload_size": len(relation_b),
                "relation_payload_sha256": hashlib.sha256(relation_b).hexdigest(),
                "relation_payload_hex": relation_b.hex(),
                "dye_file_hash": h32(dye_hash),
                "dye_package_id": f"{dpkg:04X}",
                "dye_entry_direct_reference": h32(direct_ref),
                "dye_entry_direct_reference_charm_display": "F41A8080",
                "dye": dye,
                "referenced_texture_package_ids": [f"{x:04X}" for x in texture_pkgs],
            })
        except Exception as ex:
            rec["error"] = repr(ex)
        rows.append(rec)

    report = {
        "schema": "d1_investment_dye_exact_resolver/v1",
        "global_tables": {
            "art_dye_reference": {"tag_hash": ART_DYE_REFERENCE_TAG, "reference": art_e["reference"].upper(), "row_count": art_count},
            "dye_channels": {"tag_hash": DYE_CHANNELS_TAG, "reference": ch_e["reference"].upper(), "row_count": ch_count},
            "dye_manifest_assignments": {"tag_hash": DYE_ASSIGNMENTS_TAG, "reference": as_e["reference"].upper(), "row_count": as_count},
        },
        "requested_dye_indices": dyes_req,
        "requested_channel_indices": channels_req,
        "channels": channels,
        "dyes": rows,
        "resolved_dye_count": sum(bool(x.get("resolved")) for x in rows),
        "unresolved_package_ids": [f"{x:04X}" for x in sorted(unresolved_pkgs)],
        "logical_views": {
            f"{pkg:04X}": {"package": r.pkg.name, "patch_id": r.h["patch_id"]}
            for pkg, r in sorted(views.items())
        },
        "evidence_policy": (
            "Every edge is decoded from retail bytes. Final SDye_D1 acceptance requires an exact 0x18 relation parent, "
            "a serialized +0x10 FileHash, and a final package-entry Reference equal to F41A8080 directly. No shader, "
            "GStack, gamma, or appearance inference is performed."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "channels": channels,
        "resolved_dye_count": report["resolved_dye_count"],
        "unresolved_package_ids": report["unresolved_package_ids"],
    }, indent=2))
    for row in rows:
        print("DYE", json.dumps(row, separators=(",", ":")))
    return 0 if report["resolved_dye_count"] == len(dyes_req) else 2


if __name__ == "__main__":
    raise SystemExit(main())
