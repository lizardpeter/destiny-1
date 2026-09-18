#!/usr/bin/env python3
"""Parse every current D1 ROI s_gear_dye (80801AF4) from an exact class census.

This is a whole-current-corpus inventory. It validates each retained payload
against the exact SDye_D1 parser already used by the Investment dye resolver,
then indexes serialized decal/detail-diffuse/detail-normal resources and colors.

It does NOT assign any dye to an entity, stage part, runtime API slot, or shader
resource table. Optional --probe-texture values answer only whether an exact
Texture TagHash is serialized in any SDye_D1 field and in which field/records.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from d1_investment_dye_resolver import DYE_CLASS, parse_dye_payload

DYE_CLASS_HEX = f"{DYE_CLASS:08X}"


def norm(x: object) -> str:
    return str(x).upper().removeprefix("0X").zfill(8)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--census", type=Path, required=True)
    ap.add_argument("--payload-dir", type=Path, required=True)
    ap.add_argument("--probe-texture", action="append", default=[])
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    census = json.loads(a.census.read_text())
    v: list[str] = []
    if census.get("status") != "D1_REMOTE_REFERENCE_CLASS_CENSUS_EXACT" or census.get("violations"):
        v.append("class_census_not_exact")
    refs = census.get("reference_counts") or {}
    expected = int(refs.get(DYE_CLASS_HEX, 0))
    if expected <= 0:
        v.append(f"no_{DYE_CLASS_HEX}_entries")
    if set(refs) != {DYE_CLASS_HEX}:
        v.append(f"unexpected_reference_set:{sorted(refs)}")
    if int(census.get("matching_entry_count", -1)) != expected:
        v.append("matching_entry_count_disagrees_with_reference_count")

    rows = []
    slot_hist = Counter()
    size_hist = Counter()
    texture_fields: dict[str, list[dict]] = defaultdict(list)
    payload_sha_to_dyes: dict[str, list[str]] = defaultdict(list)

    for src in census.get("rows", []):
        h = norm(src.get("tag_hash"))
        if norm(src.get("reference")) != DYE_CLASS_HEX:
            v.append(f"{h}:class_drift")
            continue
        p = a.payload_dir / f"{h}.bin"
        if not p.is_file():
            v.append(f"{h}:payload_missing")
            continue
        b = p.read_bytes()
        sha = hashlib.sha256(b).hexdigest()
        if sha != src.get("payload_sha256"):
            v.append(f"{h}:payload_sha256_mismatch")
        if len(b) != int(src.get("payload_bytes", -1)):
            v.append(f"{h}:payload_size_mismatch")
        try:
            dye = parse_dye_payload(b)
        except Exception as ex:
            v.append(f"{h}:parse:{ex!r}")
            continue
        if dye["payload_sha256"] != sha:
            v.append(f"{h}:parser_sha_mismatch")
        slot = int(dye["slot_type_index"])
        slot_hist[str(slot)] += 1
        size_hist[str(len(b))] += 1
        payload_sha_to_dyes[sha].append(h)
        for field in ("decal_texture_hash", "detail_diffuse_texture_hash", "detail_normal_texture_hash"):
            tex = norm(dye[field])
            if tex not in {"00000000", "FFFFFFFF"}:
                texture_fields[tex].append({"dye": h, "field": field, "slot_type_index": slot})
        rows.append({
            "dye": h,
            "package_id": src.get("package_id"),
            "entry_index": src.get("entry_index"),
            "payload_bytes": len(b),
            "payload_sha256": sha,
            "slot_type_index": slot,
            "decal_texture_hash": norm(dye["decal_texture_hash"]),
            "detail_diffuse_texture_hash": norm(dye["detail_diffuse_texture_hash"]),
            "detail_normal_texture_hash": norm(dye["detail_normal_texture_hash"]),
            "decal_blend_option": dye["decal_blend_option"],
            "decal_alpha_map_transform": dye["decal_alpha_map_transform"],
            "specular_properties": dye["specular_properties"],
            "detail_transform": dye["detail_transform"],
            "detail_normal_contribution_strength": dye["detail_normal_contribution_strength"],
            "primary_color": dye["primary_color"],
            "secondary_color": dye["secondary_color"],
            "subsurface_scattering_strength": dye["subsurface_scattering_strength"],
        })

    if len(rows) != expected:
        v.append(f"decoded_count:{len(rows)} expected:{expected}")

    probes = {}
    for q in sorted({norm(x) for x in a.probe_texture}):
        hits = texture_fields.get(q, [])
        probes[q] = {
            "serialized_hit_count": len(hits),
            "unique_dye_count": len({x["dye"] for x in hits}),
            "fields": dict(Counter(x["field"] for x in hits)),
            "slot_type_histogram": dict(Counter(str(x["slot_type_index"]) for x in hits)),
            "hits": hits,
        }

    duplicate_payloads = [
        {"payload_sha256": sha, "dyes": sorted(ds), "count": len(ds)}
        for sha, ds in sorted(payload_sha_to_dyes.items()) if len(ds) > 1
    ]
    exact = not v
    out = {
        "schema": "d1_global_sdye_inventory/v1",
        "status": "D1_GLOBAL_SDYE_INVENTORY_EXACT" if exact else "D1_GLOBAL_SDYE_INVENTORY_VIOLATIONS",
        "class_reference": DYE_CLASS_HEX,
        "census_package_family_count": census.get("package_family_count"),
        "dye_occurrence_count": len(rows),
        "unique_dye_count": len({x["dye"] for x in rows}),
        "unique_payload_sha256_count": len(payload_sha_to_dyes),
        "slot_type_histogram": dict(sorted(slot_hist.items(), key=lambda kv: int(kv[0]))),
        "payload_size_histogram": dict(sorted(size_hist.items(), key=lambda kv: int(kv[0]))),
        "unique_serialized_texture_count": len(texture_fields),
        "serialized_texture_field_occurrence_count": sum(len(x) for x in texture_fields.values()),
        "texture_field_histogram": dict(Counter(
            h["field"] for hs in texture_fields.values() for h in hs
        )),
        "probe_textures": probes,
        "duplicate_payload_groups": duplicate_payloads,
        "rows": sorted(rows, key=lambda x: (x["dye"], x["package_id"], x["entry_index"])),
        "violations": v,
        "gates": {
            "all_current_dye_payloads_parsed": exact,
            "entity_or_actor_ownership_closed": False,
            "stage_part_slot_to_concrete_dye_closed": False,
            "runtime_shader_binding_closed": False,
        },
        "policy": (
            "FileEntry.Reference=80801AF4 establishes current s_gear_dye membership and the existing exact "
            "SDye_D1 parser establishes serialized fields. Texture equality is reported only as a field-level "
            "cross-corpus join; it does not prove entity ownership, live dye selection, API15 contents, or t# binding."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({
        k: out[k] for k in (
            "status", "dye_occurrence_count", "unique_dye_count",
            "unique_payload_sha256_count", "slot_type_histogram",
            "unique_serialized_texture_count", "texture_field_histogram",
            "probe_textures", "violations",
        )
    }, indent=2))
    return 0 if exact else 2


if __name__ == "__main__":
    raise SystemExit(main())
