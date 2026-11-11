#!/usr/bin/env python3
"""Attach recovered names to D1 global channel StringHashes (FNV-1 32).

Executable evidence (CUSA00219 01.33 eboot):
  * find_global_channel @ 0x816240 linearly searches the GlobalChannelDefaults
    hash array for a u32 key and returns its index.
  * c_sun_manager::resolve_channels @ 0x8B1F10 (vtable 0x1949560 slot 2) looks up
    eight keys whose constants are written by a static initializer at 0x8B2B00..;
    one of them, 0x5C579DFA, is FNV-1 32 of "sun_light_direction", a string
    that also appears verbatim in the binary (debug printf at 0x1666C90).

So channel names are FNV-1 32 (offset basis 0x811C9DC5, prime 0x01000193,
multiply-then-xor). The other names below are dictionary preimages: each was
found by brute force over a domain vocabulary and is re-verified here. A 32-bit
preimage is not proof of the original string, so every name carries a status:

  STRONGLY_SUPPORTED  meaningful name, fits the channel's role/default/neighbours
  HYPOTHESIS          plausible but unconfirmed (could be a dictionary collision)

Numbered families (e.g. indices 34..47) are recognised from the FNV-1 structure:
members differ only in the final character(s). Their shared prefix state is
reported; a prefix name is attached only when a preimage was found.

Usage:
  python tools/d1_global_channel_names.py \
      evidence/generated/d1_current_global_channel_defaults_decoded.json \
      evidence/generated/d1_global_channel_names.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

FNV_BASIS = 0x811C9DC5
FNV_PRIME = 0x01000193
INV_PRIME = pow(FNV_PRIME, -1, 1 << 32)

# name -> (status, note)
NAMES = {
    "sun_light_direction": ("STRONGLY_SUPPORTED", "string present in binary; c_sun_manager +0x8"),
    "sun_atmosphere_direction": ("STRONGLY_SUPPORTED", "c_sun_manager +0xC"),
    "sun_ambient_direction": ("STRONGLY_SUPPORTED", "c_sun_manager +0x10; written as scale * -sun_light_direction.xy"),
    "sun_intensity": ("STRONGLY_SUPPORTED", "c_sun_manager +0x20; default 10"),
    "sun_shadow_intensity": ("STRONGLY_SUPPORTED", "c_sun_manager +0x24; default 1"),
    "sun_color": ("STRONGLY_SUPPORTED", "default (1,1,1,1); next to sun_intensity"),
    "sun_glow_color": ("STRONGLY_SUPPORTED", "default (1,1,1,1); next to sun_glow_intensity"),
    "sun_glow_intensity": ("STRONGLY_SUPPORTED", ""),
    "sun_transmission_color": ("STRONGLY_SUPPORTED", "paired with sun_transmission_intensity"),
    "sun_transmission_intensity": ("STRONGLY_SUPPORTED", ""),
    "inscatter_intensity": ("STRONGLY_SUPPORTED", ""),
    "fog_density": ("STRONGLY_SUPPORTED", ""),
    "fog_height_falloff": ("STRONGLY_SUPPORTED", ""),
    "fog_start_height": ("STRONGLY_SUPPORTED", ""),
    "up_ambient_color": ("STRONGLY_SUPPORTED", "paired with up_ambient_intensity"),
    "up_ambient_intensity": ("STRONGLY_SUPPORTED", ""),
    "down_ambient_color": ("STRONGLY_SUPPORTED", "paired with down_ambient_intensity"),
    "down_ambient_intensity": ("STRONGLY_SUPPORTED", ""),
    "sky_color_override": ("STRONGLY_SUPPORTED", ""),
    "skybox_sun_color": ("STRONGLY_SUPPORTED", "paired with skybox_sun_intensity"),
    "skybox_sun_intensity": ("STRONGLY_SUPPORTED", ""),
    "character_lighting_scale": ("STRONGLY_SUPPORTED", "default 1"),
    "lighting_cinematic_override": ("STRONGLY_SUPPORTED", "default (1,0,0,0)"),
    "ao_ambient_weight": ("STRONGLY_SUPPORTED", "adjacent to ao_sun_weight"),
    "ao_sun_weight": ("STRONGLY_SUPPORTED", ""),
    "ao_character_bias": ("HYPOTHESIS", "c_sun_manager +0x28 zeroes it under a renderer flag; role fit unclear"),
    "snow_ao_scale": ("HYPOTHESIS", ""),
    "snow_ao_bias": ("HYPOTHESIS", ""),
}

# Numbered-family prefixes (prefix includes the trailing separator).
FAMILY_PREFIXES = {
    "sky_colour_tint_": ("HYPOTHESIS", "two-digit suffixes 01..24 match indices 34-39,42-47,70-75,79-84; British spelling differs from the other *_color channels"),
}

# Preimages that hit a hash but are rejected as dictionary collisions.
REJECTED = {
    "sea_hero_receive": "collides with sun_glow_color (0x056007C7)",
    "tonemap_cosmodrome_indoor": "nonsensical combination; index 61 left unnamed",
}


def fnv1(s: str, h: int = FNV_BASIS) -> int:
    for c in s.encode():
        h = ((h * FNV_PRIME) & 0xFFFFFFFF) ^ c
    return h


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("defaults_json", type=Path)
    ap.add_argument("out_json", type=Path)
    a = ap.parse_args()

    d = json.loads(a.defaults_json.read_text())
    by_hash = {}
    for name, (status, note) in NAMES.items():
        by_hash[f"{fnv1(name):08X}"] = (name, status, note)
    fam = {}
    for pre, (status, note) in FAMILY_PREFIXES.items():
        for n in range(100):
            fam[f"{fnv1(f'{n:02d}', fnv1(pre)):08X}"] = (f"{pre}{n:02d}", status, note)

    rows, named = [], 0
    for c in d["channels"]:
        h = c["string_hash"]
        hit = by_hash.get(h) or fam.get(h)
        row = {
            "index": c["index"],
            "index_hex": c["index_hex"],
            "string_hash": h,
            "default_vec4": c["default_vec4"],
            "name": hit[0] if hit else None,
            "name_status": hit[1] if hit else "UNKNOWN",
        }
        if hit and hit[2]:
            row["note"] = hit[2]
        named += bool(hit)
        rows.append(row)

    unused = sorted(n for n in NAMES if f"{fnv1(n):08X}" not in {c["string_hash"] for c in d["channels"]})
    out = {
        "schema": "d1_global_channel_names/v1",
        "hash": "FNV-1 32 (basis 0x811C9DC5, prime 0x01000193, multiply then xor)",
        "hash_evidence": "0x5C579DFA == fnv1('sun_light_direction'); constant used by c_sun_manager::resolve_channels 0x8B1F10 via find_global_channel 0x816240",
        "source_defaults": str(a.defaults_json),
        "source_tag_hash": d.get("tag_hash"),
        "channel_count": len(rows),
        "named_count": named,
        "names_not_in_this_tag": unused,
        "rejected_preimages": REJECTED,
        "tfx_4b_frontier": [r for r in rows if r["index"] in (0x11, 0x28, 0x30, 0x60)],
        "channels": rows,
        "proof_boundary": "Names are 32-bit hash preimages from a dictionary search, not recovered strings, except sun_light_direction. Index order is per-tag data, so these indices hold only for tag "
        + str(d.get("tag_hash")),
    }
    a.out_json.write_text(json.dumps(out, indent=2) + "\n")
    print(f"named {named}/{len(rows)} -> {a.out_json}")


if __name__ == "__main__":
    main()
