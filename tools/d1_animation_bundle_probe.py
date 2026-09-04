#!/usr/bin/env python3
"""Classify D1 0x8080222A animation-bundle/proxy neighborhoods.

This tool deliberately does *not* assign an original Bungie type name to
0x8080222A and does not decode undocumented wrapper fields.  It recognizes the
retail pattern observed around Vex animation assets using only byte-proven or
schema-independent evidence:

* package entry class/order around a 0x8080222A structured tag;
* nearby s_entity_model (0x80801AB5) and s_animation_clip (0x808005A1) tags;
* the literal Havok serialization marker ``hk_2012.2.0-r1``;
* already-supported EntityResource decoding for skeleton/model roles and
  runtime-rig/composition discriminator classes;
* aligned 32-bit wrapper dwords that match nearby TagHashes;
* optional caller-supplied known animation hashes, matched as raw dwords only.

The output says "proxy pattern" rather than "final render model".  A model next
to this wrapper must not be automatically textured as a visible entity model
unless a separate ordinary model-parent/render-ownership path is proven.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Iterable

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_entry_extract import EntryReader
from d1_entity_model_probe import D1_ENTITY_MODEL_CLASS
from d1_entity_resource_probe import ENTITY_RESOURCE_CLASS, parse_resource

ANIMATION_BUNDLE_WRAPPER_CLASS = "8080222A"
ANIMATION_CLIP_CLASS = "808005A1"
RUNTIME_RIG_DISCRIMINATOR = "808008B2"
RUNTIME_RIG_INFO = "8080099B"
COMPOSITION_DISCRIMINATOR = "8080079A"
COMPOSITION_INFO = "80800610"
POST_ANIMATION_CONTROL_CLASS = "80802C0E"
HAVOK_MARKER = b"hk_2012.2.0-r1"
MODEL_PROMOTION_WINDOW = 4
HAVOK_PROMOTION_WINDOW = 8


def norm_hash(value: str) -> str:
    value = value.strip().upper().removeprefix("0X")
    if not value or len(value) > 8:
        raise argparse.ArgumentTypeError(f"not a 32-bit hexadecimal value: {value!r}")
    try:
        n = int(value, 16)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"not hexadecimal: {value!r}") from exc
    return f"{n:08X}"


def aligned_u32_matches(payload: bytes, hashes: Iterable[str]) -> dict[str, list[int]]:
    """Return 4-byte-aligned offsets for caller-selected 32-bit values."""
    wanted = {int(norm_hash(h), 16): norm_hash(h) for h in hashes}
    if not wanted:
        return {}
    out: dict[str, list[int]] = {text: [] for text in wanted.values()}
    limit = len(payload) - (len(payload) % 4)
    for off in range(0, limit, 4):
        value = struct.unpack_from("<I", payload, off)[0]
        text = wanted.get(value)
        if text is not None:
            out[text].append(off)
    return {key: offsets for key, offsets in out.items() if offsets}


def classify_pattern(
    *,
    model_count: int,
    clip_count: int,
    havok_count: int,
    known_animation_hash_match_count: int,
) -> dict:
    """Pure evidence classifier used by the CLI and synthetic regression tests."""
    has_model = model_count > 0
    has_animation_side = clip_count > 0 or havok_count > 0

    if has_model and clip_count > 0 and havok_count > 0 and known_animation_hash_match_count > 0:
        strength = "hash_correlated_animation_bundle_proxy_pattern"
    elif has_model and clip_count > 0 and havok_count > 0:
        strength = "strong_animation_bundle_proxy_pattern"
    elif has_model and has_animation_side:
        strength = "animation_bundle_proxy_pattern"
    elif has_model:
        strength = "wrapper_plus_model_unresolved"
    else:
        strength = "wrapper_only_unresolved"

    return {
        "classification": strength,
        "proxy_candidate": has_model and has_animation_side,
        "final_render_model_proven": False,
        "reason": (
            "0x8080222A forward bundle sequence has an entity model plus animation-side evidence; "
            "ordinary render ownership must be proven separately"
            if has_model and has_animation_side
            else "insufficient forward-sequence evidence to classify as an animation proxy"
        ),
    }


def entry_brief(entry: dict) -> dict:
    return {
        "entry_index": entry["index"],
        "tag_hash": entry["tag_hash"].upper(),
        "reference": entry["reference"].upper(),
        "type": entry["type"],
        "subtype": entry["subtype"],
        "size": entry["file_size"],
    }


def inspect_neighborhood(
    reader: EntryReader,
    wrapper_index: int,
    *,
    backward: int,
    forward: int,
    known_animation_hashes: list[str],
) -> dict:
    entries = reader.entries
    lo = max(0, wrapper_index - backward)
    hi = min(len(entries), wrapper_index + forward + 1)
    wrapper_entry = entries[wrapper_index]
    wrapper_payload = reader.entry(wrapper_index)

    rows: list[dict] = []
    model_rows: list[dict] = []
    clip_rows: list[dict] = []
    havok_rows: list[dict] = []
    skeleton_rows: list[dict] = []
    runtime_rig_rows: list[dict] = []
    composition_rows: list[dict] = []
    ordinary_model_parent_rows: list[dict] = []
    post_animation_control_rows: list[dict] = []

    for idx in range(lo, hi):
        e = entries[idx]
        row = entry_brief(e)
        row["relative_index"] = idx - wrapper_index
        row["available"] = reader.available(idx)

        payload = None
        if row["available"]:
            try:
                payload = reader.entry(idx)
            except Exception as exc:
                row["read_error"] = repr(exc)

        ref = row["reference"]
        if ref == D1_ENTITY_MODEL_CLASS:
            model_rows.append(row.copy())
        if ref == ANIMATION_CLIP_CLASS:
            clip_rows.append(row.copy())
        if ref == POST_ANIMATION_CONTROL_CLASS:
            post_animation_control_rows.append(row.copy())
        if payload is not None and HAVOK_MARKER in payload:
            havok = row.copy()
            havok["marker_offset"] = payload.find(HAVOK_MARKER)
            havok_rows.append(havok)
            row["havok_marker_offset"] = havok["marker_offset"]

        if ref == ENTITY_RESOURCE_CLASS and payload is not None:
            try:
                parsed = parse_resource(payload, reader.h["platform"])
                role = parsed.get("semantic_role")
                unk10 = parsed.get("unk10", {}).get("class_hash")
                unk18 = parsed.get("unk18", {}).get("class_hash")
                row["entity_resource"] = {
                    "semantic_role": role,
                    "unk10_class": unk10,
                    "unk18_class": unk18,
                    "embedded_model_tag_hash": parsed.get("embedded_model_tag_hash"),
                }
                if role == "entity_skeleton":
                    skeleton_rows.append(row.copy())
                if unk10 == RUNTIME_RIG_DISCRIMINATOR and unk18 == RUNTIME_RIG_INFO:
                    runtime_rig_rows.append(row.copy())
                if unk10 == COMPOSITION_DISCRIMINATOR and unk18 == COMPOSITION_INFO:
                    composition_rows.append(row.copy())
                if role == "entity_model" and parsed.get("embedded_model_tag_hash"):
                    ordinary_model_parent_rows.append(row.copy())
            except Exception as exc:
                row["entity_resource_parse_error"] = repr(exc)

        rows.append(row)

    nearby_hashes = [row["tag_hash"] for row in rows]
    nearby_tag_matches = aligned_u32_matches(wrapper_payload, nearby_hashes)
    known_animation_matches = aligned_u32_matches(wrapper_payload, known_animation_hashes)

    models_after = [row for row in model_rows if row["relative_index"] > 0]
    nearest_model = min(models_after, key=lambda row: row["relative_index"], default=None)
    immediate_model = next((row for row in models_after if row["relative_index"] == 1), None)

    # Promotion evidence is intentionally narrower than the diagnostic
    # neighborhood.  This prevents a distant, unrelated model or prior clip
    # from turning a wrapper into a false proxy classification.
    promotion_models = [
        row for row in model_rows if 0 < row["relative_index"] <= MODEL_PROMOTION_WINDOW
    ]
    promotion_clips = [row for row in clip_rows if row["relative_index"] > 0]
    promotion_havok = [
        row for row in havok_rows if 0 < row["relative_index"] <= HAVOK_PROMOTION_WINDOW
    ]

    classification = classify_pattern(
        model_count=len(promotion_models),
        clip_count=len(promotion_clips),
        havok_count=len(promotion_havok),
        known_animation_hash_match_count=sum(len(v) for v in known_animation_matches.values()),
    )

    evidence = []
    if immediate_model:
        evidence.append(f"immediate next entry is s_entity_model {immediate_model['tag_hash']}")
    elif promotion_models:
        model = min(promotion_models, key=lambda row: row["relative_index"])
        evidence.append(
            f"forward s_entity_model {model['tag_hash']} is +{model['relative_index']} entries"
        )
    elif nearest_model:
        evidence.append(
            f"nearest forward s_entity_model {nearest_model['tag_hash']} is +{nearest_model['relative_index']} entries (outside promotion window)"
        )
    if promotion_clips:
        evidence.append(
            f"{len(promotion_clips)} forward s_animation_clip entr{'y' if len(promotion_clips) == 1 else 'ies'}"
        )
    if promotion_havok:
        evidence.append(
            f"{len(promotion_havok)} forward payload(s) within +{HAVOK_PROMOTION_WINDOW} contain literal {HAVOK_MARKER.decode('ascii')}"
        )
    if known_animation_matches:
        evidence.append(
            "wrapper contains caller-supplied known animation hash dword(s): "
            + ", ".join(sorted(known_animation_matches))
        )
    if skeleton_rows:
        evidence.append(f"{len(skeleton_rows)} nearby skeleton EntityResource(s)")
    if runtime_rig_rows:
        evidence.append(f"{len(runtime_rig_rows)} nearby 808008B2->8080099B runtime-rig EntityResource(s)")
    if composition_rows:
        evidence.append(f"{len(composition_rows)} nearby 8080079A->80800610 composition EntityResource(s)")

    return {
        "wrapper": entry_brief(wrapper_entry),
        "wrapper_sha256": hashlib.sha256(wrapper_payload).hexdigest(),
        "wrapper_size": len(wrapper_payload),
        "neighborhood_range": {"start_entry_index": lo, "end_entry_index_inclusive": hi - 1},
        "promotion_windows": {
            "model_forward_entries": MODEL_PROMOTION_WINDOW,
            "havok_forward_entries": HAVOK_PROMOTION_WINDOW,
            "clips_must_be_forward": True,
        },
        "classification": classification,
        "evidence": evidence,
        "nearest_forward_model": nearest_model,
        "immediate_forward_model": immediate_model,
        "promotion_models": promotion_models,
        "promotion_animation_clips": promotion_clips,
        "promotion_havok_payloads": promotion_havok,
        "models": model_rows,
        "animation_clips": clip_rows,
        "havok_payloads": havok_rows,
        "skeleton_resources": skeleton_rows,
        "runtime_rig_resources": runtime_rig_rows,
        "composition_resources": composition_rows,
        "ordinary_model_parent_resources": ordinary_model_parent_rows,
        "post_animation_control_entries": post_animation_control_rows,
        "wrapper_aligned_nearby_taghash_matches": nearby_tag_matches,
        "wrapper_aligned_known_animation_hash_matches": known_animation_matches,
        "entries": rows,
    }


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Classify schema-free D1 0x8080222A animation-bundle/proxy neighborhoods"
    )
    ap.add_argument("pkg", type=Path)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--backward", type=int, default=12, help="entries before wrapper to include (default: 12)")
    ap.add_argument("--forward", type=int, default=16, help="entries after wrapper to include (default: 16)")
    ap.add_argument(
        "--known-animation-hash",
        type=norm_hash,
        action="append",
        default=[],
        help="raw 32-bit animation hash to cross-check inside wrapper; repeatable",
    )
    ap.add_argument("--wrapper-tag", type=norm_hash, action="append", default=[])
    ap.add_argument("-o", "--output", type=Path)
    args = ap.parse_args()

    if args.backward < 0 or args.forward < 0:
        ap.error("--backward and --forward must be >= 0")

    reader = EntryReader(args.pkg, args.runtime)
    wanted_tags = set(args.wrapper_tag)
    wrappers = [
        e
        for e in reader.entries
        if e["type"] == 16
        and e["subtype"] == 0
        and e["reference"].upper() == ANIMATION_BUNDLE_WRAPPER_CLASS
        and (not wanted_tags or e["tag_hash"].upper() in wanted_tags)
    ]

    rows = []
    unavailable = []
    errors = []
    for e in wrappers:
        if not reader.available(e["index"]):
            unavailable.append(entry_brief(e))
            continue
        try:
            rows.append(
                inspect_neighborhood(
                    reader,
                    e["index"],
                    backward=args.backward,
                    forward=args.forward,
                    known_animation_hashes=args.known_animation_hash,
                )
            )
        except Exception as exc:
            errors.append({**entry_brief(e), "error": repr(exc)})

    counts: dict[str, int] = {}
    for row in rows:
        key = row["classification"]["classification"]
        counts[key] = counts.get(key, 0) + 1

    report = {
        "package": str(reader.pkg),
        "platform": reader.h["platform"],
        "package_id": reader.h["pkg_id"],
        "package_patch_id": reader.h["patch_id"],
        "wrapper_class": ANIMATION_BUNDLE_WRAPPER_CLASS,
        "semantic_name_claimed": False,
        "method": "schema-free neighborhood + raw aligned-dword correlation",
        "known_animation_hashes": args.known_animation_hash,
        "wrapper_count": len(wrappers),
        "decoded_wrapper_count": len(rows),
        "classification_counts": counts,
        "unavailable_wrappers": unavailable,
        "errors": errors,
        "bundles": rows,
    }

    text = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
        print(f"wrote {args.output}")
    else:
        print(text)


if __name__ == "__main__":
    main()
