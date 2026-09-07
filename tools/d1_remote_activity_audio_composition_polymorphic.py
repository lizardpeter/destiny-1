#!/usr/bin/env python3
"""D1 ROI composition-audio adapter for polymorphic ResourcePointer arrays.

Charm's D1 composition schema exposes WwiseSounds1/+0x110 and
WwiseSounds2/+0x130 as DynamicArray<D1 29068080>.  Each record contains a
ResourcePointer, but the array is polymorphic: Charm only follows records whose
pointed value is the D1 001F8080 Wwise wrapper and ignores other valid pointed
classes.  The generic closure originally treated those valid non-audio variants
as class mismatches.

This adapter changes only that behavior.  Bounds failures remain violations;
non-Wwise target classes are preserved as exact variants and are not promoted as
audio.  D1 001F8080 targets still require +0x20 -> exact 8080080A Wwise event,
and event streams still require D1 type/subtype 8/21.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import d1_remote_activity_audio_composition_closure as base


def parse_sound_array(c, payload, parent_base, relative_field, array_name, event_cache):
    field = parent_base + relative_field
    arr = base.dyn(payload, field, 0x08)
    out = {
        "array_name": array_name,
        "field_offset_in_composition_info": relative_field,
        "field_offset": field,
        "field_offset_hex": f"0x{field:X}",
        "descriptor": arr,
        "records": [],
        "violations": [],
        "non_audio_variant_count": 0,
        "non_audio_variant_class_counts": {},
    }
    if not arr["ok"]:
        out["violations"].append(f"{array_name}_descriptor_invalid")
        return out

    for i in range(arr["count"]):
        ro = arr["absolute"] + i * 0x08
        rel = base.i64(payload, ro)
        rec = {
            "index": i,
            "record_offset": ro,
            "record_offset_hex": f"0x{ro:X}",
            "relative_pointer": rel,
            "null_pointer": rel == 0,
        }
        if rel == 0:
            rec["variant_kind"] = "null_pointer"
            out["records"].append(rec)
            continue

        target = ro + rel
        rec["target_offset"] = target
        rec["target_offset_hex"] = f"0x{target:X}"
        if target < 4 or target + 4 > len(payload):
            rec["violation"] = "resource_pointer_target_oob"
            out["violations"].append(f"{array_name}_{i}_target_oob")
            out["records"].append(rec)
            continue

        target_class = f"{base.u32(payload, target - 4):08X}"
        rec["target_class"] = target_class
        rec["target_class_matches_wwise_wrapper"] = (
            target_class == base.COMPOSITION_SOUND_TARGET_CLASS
        )

        # Source-authentic D1 behavior: the composition arrays are polymorphic.
        # Only D1 001F8080 is a Wwise wrapper; all other well-formed pointer
        # targets remain exact non-audio variants rather than parse failures.
        if target_class != base.COMPOSITION_SOUND_TARGET_CLASS:
            rec["variant_kind"] = "non_wwise_polymorphic_resource"
            out["non_audio_variant_count"] += 1
            cc = out["non_audio_variant_class_counts"]
            cc[target_class] = cc.get(target_class, 0) + 1
            out["records"].append(rec)
            continue

        rec["variant_kind"] = "wwise_wrapper"
        if target + 0x24 > len(payload):
            rec["violation"] = "wwise_wrapper_target_oob"
            out["violations"].append(f"{array_name}_{i}_wwise_wrapper_oob")
            out["records"].append(rec)
            continue

        event_hash = f"{base.u32(payload, target + 0x20):08X}"
        rec["wwise_sound_field_offset"] = target + 0x20
        rec["wwise_sound_field_offset_hex"] = f"0x{target + 0x20:X}"
        rec["event"] = event_hash
        rec["event_is_null"] = event_hash in base.NULLS
        if event_hash not in base.NULLS:
            try:
                ev = base.parse_event(c, event_hash, event_cache)
                rec["event_reference"] = ev["meta"]["reference"]
                rec["event_validation_ok"] = ev.get("validation_ok", False)
                if not rec["event_validation_ok"]:
                    out["violations"].append(
                        f"{array_name}_{i}_{event_hash}_event_invalid"
                    )
            except Exception as ex:
                rec["violation"] = repr(ex)
                out["violations"].append(f"{array_name}_{i}_{event_hash}:{ex!r}")
        out["records"].append(rec)

    out["validation_ok"] = not out["violations"]
    return out


base.parse_sound_array = parse_sound_array

if __name__ == "__main__":
    raise SystemExit(base.main())
