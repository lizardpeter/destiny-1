#!/usr/bin/env python3
"""Resolve Destiny 1 ROI inventory dye indices to exact SDye_D1 payloads.

This is an asset-first, byte-level resolver for the D1 Investment dye chain used
by inventory equipping blocks:

  equippingBlock 20108080
    ChannelIndex -> global dye-channel table 80A5E249
    DyeIndex     -> ArtDyeReference table 80A5FFA8
                  -> DyeManifestHash
                  -> global manifest assignment table 80A7E1DC
                  -> D1 63348080 relation parent
                  -> EntityDataROI
                  -> SDye_D1 F41A8080 payload

Charm writes the source schema/class literals in display byte order.  The
on-disk numeric class hashes used below are therefore byte-swapped:

  63348080 -> 80803463
  F41A8080 -> 80801AF4

The tool does not reinterpret GStack channels and does not gamma-convert dye
colors.  Floats are emitted exactly as serialized so renderer policy can remain
separate from extraction/provenance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from d1_entry_extract import EntryReader
from d1_investment_arrangement_probe import dyn_header, filehash_pkg_index

ART_DYE_REFERENCE_TAG = "80A5FFA8"      # Charm literal A8FFA580, D1 20348080
DYE_CHANNELS_TAG = "80A5E249"           # Charm literal 49E2A580, D1 F6178080
DYE_ASSIGNMENTS_TAG = "80A7E1DC"        # Charm literal DCE1A780, D1 41038080
RELATION_CLASS = 0x80803463              # Charm display/source literal 63348080
DYE_CLASS = 0x80801AF4                   # Charm display/source literal F41A8080

KNOWN_CHANNELS = {
    662199250: "ArmorPlate",
    1367384683: "ArmorSuit",
    218592586: "ArmorCloth",
    1667433279: "Weapon1",
    1667433278: "Weapon2",
    1667433277: "Weapon3",
    3073305669: "ShipUpper",
    3073305668: "ShipDecals",
    3073305671: "ShipLower",
    1971582085: "SparrowUpper",
    1971582084: "SparrowEngine",
    1971582087: "SparrowLower",
    373026848: "GhostMain",
    373026849: "GhostHighlights",
    373026850: "GhostDecals",
}


def u32(b: bytes, o: int) -> int:
    if o < 0 or o + 4 > len(b):
        raise ValueError(f"u32 out of bounds at 0x{o:X}/0x{len(b):X}")
    return struct.unpack_from("<I", b, o)[0]


def i32(b: bytes, o: int) -> int:
    if o < 0 or o + 4 > len(b):
        raise ValueError(f"i32 out of bounds at 0x{o:X}/0x{len(b):X}")
    return struct.unpack_from("<i", b, o)[0]


def vec4(b: bytes, o: int) -> list[float]:
    if o < 0 or o + 16 > len(b):
        raise ValueError(f"vec4 out of bounds at 0x{o:X}/0x{len(b):X}")
    return list(struct.unpack_from("<4f", b, o))


def h32(v: int) -> str:
    return f"{v & 0xFFFFFFFF:08X}"


def charm_display(v: int) -> str:
    return int(v & 0xFFFFFFFF).to_bytes(4, "little").hex().upper()


def choose_views(asset_dir: Path, runtime: Path) -> dict[int, EntryReader]:
    candidates: dict[int, tuple[int, Path]] = {}
    rx = re.compile(r"_([0-9a-fA-F]{4})_([0-9]+)\.pkg$")
    for p in asset_dir.glob("*.pkg"):
        m = rx.search(p.name)
        if not m:
            continue
        pkg, patch = int(m.group(1), 16), int(m.group(2))
        old = candidates.get(pkg)
        if old is None or patch > old[0]:
            candidates[pkg] = (patch, p)
    return {pkg: EntryReader(path, runtime) for pkg, (_, path) in sorted(candidates.items())}


def entry_for_hash(views: dict[int, EntryReader], file_hash: int) -> tuple[EntryReader, dict, bytes]:
    pkg, idx = filehash_pkg_index(file_hash)
    r = views.get(pkg)
    if r is None:
        raise FileNotFoundError(f"package {pkg:04X} not supplied for {h32(file_hash)}")
    if idx >= len(r.entries):
        raise IndexError(f"{h32(file_hash)} index {idx} beyond package {pkg:04X} entry table")
    e = r.entries[idx]
    if e["tag_hash"].upper() != h32(file_hash):
        raise RuntimeError(f"{h32(file_hash)} logical tag mismatch: {e['tag_hash']}")
    if not r.available(idx):
        raise FileNotFoundError(f"{h32(file_hash)} requires an unavailable patch sibling")
    return r, e, r.entry(idx)


def tagged_payload(views: dict[int, EntryReader], tag: str) -> tuple[EntryReader, dict, bytes]:
    return entry_for_hash(views, int(tag, 16))


def manifest_reference(views: dict[int, EntryReader], e: dict) -> dict:
    """Replicate D1 GetReferenceFromManifest for one entry.

    D1 package metadata's Reference field points to a 48018080 'parent' tag.
    S48018080 stores the effective class hash at +0x0C and the neighboring tag
    FileHash at +0x10.
    """
    ref_hash = int(e["reference"], 16)
    rr, re, rb = entry_for_hash(views, ref_hash)
    if len(rb) < 0x14:
        raise RuntimeError(f"manifest-reference wrapper {h32(ref_hash)} shorter than 0x14")
    cls = u32(rb, 0x0C)
    neighbor = u32(rb, 0x10)
    return {
        "metadata_reference_hash": h32(ref_hash),
        "wrapper_reference": re["reference"].upper(),
        "wrapper_payload_sha256": hashlib.sha256(rb).hexdigest(),
        "effective_class_hash": h32(cls),
        "effective_class_charm_display": charm_display(cls),
        "neighbor_tag_hash": h32(neighbor),
    }


def parse_dye_payload(b: bytes) -> dict:
    if len(b) < 0xD0:
        raise RuntimeError(f"SDye_D1 payload shorter than 0xD0: {len(b)}")
    decal = u32(b, 0x20)
    detail_diffuse = u32(b, 0x60)
    detail_normal = u32(b, 0x64)
    return {
        "payload_size": len(b),
        "file_size_field": struct.unpack_from("<q", b, 0x00)[0],
        "slot_type_index": i32(b, 0x10),
        "decal_texture_hash": h32(decal),
        "decal_alpha_map_transform": vec4(b, 0x30),
        "decal_blend_option": i32(b, 0x40),
        "specular_properties": vec4(b, 0x50),
        "detail_diffuse_texture_hash": h32(detail_diffuse),
        "detail_normal_texture_hash": h32(detail_normal),
        "detail_transform": vec4(b, 0x70),
        "detail_normal_contribution_strength": vec4(b, 0x80),
        "primary_color": vec4(b, 0x90),
        "secondary_color": vec4(b, 0xA0),
        "subsurface_scattering_strength": vec4(b, 0xB0),
        "texture_package_ids": {
            "decal": filehash_pkg_index(decal)[0] if decal not in (0, 0xFFFFFFFF) else None,
            "detail_diffuse": filehash_pkg_index(detail_diffuse)[0] if detail_diffuse not in (0, 0xFFFFFFFF) else None,
            "detail_normal": filehash_pkg_index(detail_normal)[0] if detail_normal not in (0, 0xFFFFFFFF) else None,
        },
        "payload_sha256": hashlib.sha256(b).hexdigest(),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("asset_dir", type=Path, help="directory containing recovered D1 package siblings")
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--dye-index", action="append", type=int, default=[])
    ap.add_argument("--channel-index", action="append", type=int, default=[])
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args()

    dye_indices = sorted(set(args.dye_index))
    channel_indices = sorted(set(args.channel_index))
    if not dye_indices:
        raise SystemExit("at least one --dye-index is required")

    views = choose_views(args.asset_dir, args.runtime)
    if 0x012F not in views or 0x013F not in views:
        raise SystemExit(f"expected 012F and 013F package views; have {[f'{x:04X}' for x in views]}")

    _, art_e, art_b = tagged_payload(views, ART_DYE_REFERENCE_TAG)
    _, channel_e, channel_b = tagged_payload(views, DYE_CHANNELS_TAG)
    _, assign_e, assign_b = tagged_payload(views, DYE_ASSIGNMENTS_TAG)

    art_count, art_data = dyn_header(art_b, 0x08)
    channel_count, channel_data = dyn_header(channel_b, 0x08)
    assign_count, assign_data = dyn_header(assign_b, 0x08)

    art_rows = [u32(art_b, art_data + i * 4) for i in range(art_count)]
    channel_rows = [u32(channel_b, channel_data + i * 4) for i in range(channel_count)]
    assignments: dict[int, list[int]] = {}
    assignment_rows = []
    for i in range(assign_count):
        o = assign_data + i * 8
        api_hash, relation_hash = u32(assign_b, o), u32(assign_b, o + 4)
        assignments.setdefault(api_hash, []).append(relation_hash)
        assignment_rows.append((api_hash, relation_hash))

    channels = []
    for idx in channel_indices:
        if idx < 0 or idx >= channel_count:
            raise IndexError(f"channel index {idx} out of bounds for {channel_count} rows")
        v = channel_rows[idx]
        channels.append({
            "channel_index": idx,
            "channel_hash": h32(v),
            "channel_hash_u32": v,
            "known_name": KNOWN_CHANNELS.get(v),
        })

    dyes = []
    unresolved_package_ids: set[int] = set()
    for idx in dye_indices:
        if idx < 0 or idx >= art_count:
            raise IndexError(f"dye index {idx} out of bounds for {art_count} ArtDyeReference rows")
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
            rec["error"] = f"expected exactly one assignment, got {len(relations)}"
            dyes.append(rec)
            continue
        relation_hash = relations[0]
        rpkg, _ = filehash_pkg_index(relation_hash)
        if rpkg not in views:
            unresolved_package_ids.add(rpkg)
            rec["error"] = f"relation package {rpkg:04X} not supplied"
            dyes.append(rec)
            continue
        try:
            _, relation_e, relation_b = entry_for_hash(views, relation_hash)
            relation_manifest = manifest_reference(views, relation_e)
            relation_class = int(relation_manifest["effective_class_hash"], 16)
            if relation_class != RELATION_CLASS:
                raise RuntimeError(
                    f"relation {h32(relation_hash)} effective class {h32(relation_class)} "
                    f"({relation_manifest['effective_class_charm_display']}) != D1 63348080"
                )
            if len(relation_b) < 0x14:
                raise RuntimeError(f"relation parent {h32(relation_hash)} shorter than 0x14")
            dye_hash = u32(relation_b, 0x10)
            dpkg, _ = filehash_pkg_index(dye_hash)
            if dpkg not in views:
                unresolved_package_ids.add(dpkg)
                rec.update({
                    "relation_hash": h32(relation_hash),
                    "relation_manifest": relation_manifest,
                    "dye_file_hash": h32(dye_hash),
                    "error": f"dye package {dpkg:04X} not supplied",
                })
                dyes.append(rec)
                continue
            _, dye_e, dye_b = entry_for_hash(views, dye_hash)
            dye_manifest = manifest_reference(views, dye_e)
            dye_class = int(dye_manifest["effective_class_hash"], 16)
            if dye_class != DYE_CLASS:
                raise RuntimeError(
                    f"dye {h32(dye_hash)} effective class {h32(dye_class)} "
                    f"({dye_manifest['effective_class_charm_display']}) != D1 F41A8080"
                )
            rec.update({
                "resolved": True,
                "relation_hash": h32(relation_hash),
                "relation_package_id": f"{rpkg:04X}",
                "relation_manifest": relation_manifest,
                "relation_payload_sha256": hashlib.sha256(relation_b).hexdigest(),
                "dye_file_hash": h32(dye_hash),
                "dye_package_id": f"{dpkg:04X}",
                "dye_manifest": dye_manifest,
                "dye": parse_dye_payload(dye_b),
            })
        except Exception as ex:
            rec["error"] = repr(ex)
        dyes.append(rec)

    report = {
        "schema": "d1_investment_dye_resolver/v1",
        "global_tables": {
            "art_dye_reference": {
                "tag_hash": ART_DYE_REFERENCE_TAG,
                "reference": art_e["reference"].upper(),
                "row_count": art_count,
                "payload_sha256": hashlib.sha256(art_b).hexdigest(),
            },
            "dye_channels": {
                "tag_hash": DYE_CHANNELS_TAG,
                "reference": channel_e["reference"].upper(),
                "row_count": channel_count,
                "payload_sha256": hashlib.sha256(channel_b).hexdigest(),
            },
            "dye_manifest_assignments": {
                "tag_hash": DYE_ASSIGNMENTS_TAG,
                "reference": assign_e["reference"].upper(),
                "row_count": assign_count,
                "payload_sha256": hashlib.sha256(assign_b).hexdigest(),
            },
        },
        "requested_dye_indices": dye_indices,
        "requested_channel_indices": channel_indices,
        "channels": channels,
        "dyes": dyes,
        "resolved_dye_count": sum(bool(x.get("resolved")) for x in dyes),
        "unresolved_package_ids": [f"{x:04X}" for x in sorted(unresolved_package_ids)],
        "logical_views": {
            f"{pkg:04X}": {
                "package": r.pkg.name,
                "patch_id": r.h["patch_id"],
                "entries": len(r.entries),
                "blocks": len(r.blocks),
            }
            for pkg, r in sorted(views.items())
        },
        "policy": (
            "All indices, manifest hashes, relation FileHashes, manifest effective classes, final dye FileHashes, "
            "and SDye_D1 floats are read directly from retail bytes. No GStack semantic inference or color-space "
            "conversion is performed here."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "art_dye_rows": art_count,
        "channel_rows": channel_count,
        "assignment_rows": assign_count,
        "channels": channels,
        "resolved_dyes": report["resolved_dye_count"],
        "unresolved_package_ids": report["unresolved_package_ids"],
    }, indent=2))
    for d in dyes:
        print("DYE", json.dumps(d, separators=(",", ":")))
    return 0 if report["resolved_dye_count"] == len(dye_indices) else 2


if __name__ == "__main__":
    raise SystemExit(main())
