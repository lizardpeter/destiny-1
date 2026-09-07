#!/usr/bin/env python3
"""Source-close D1 ROI activity-owned composition audio dependencies.

The activity/entity dependency closure already proves which EntityResources are
reachable through source-typed ownership paths. This tool adds the independently
source-pinned D1 composition audio schema without promoting arbitrary aligned hashes.

Pinned D1 Charm schema (MontagueM/Charm@50d36ee...):

  EntityResource 80800861
    Unk10 class 8080079A                 (S9A078080 discriminator)
    Unk18 class 80800610                 (D1 10068080 composition info)
      +0x110 DynamicArray<D1 29068080>    WwiseSounds1
      +0x130 DynamicArray<D1 29068080>    WwiseSounds2

  D1 29068080 is an 0x08-byte record containing one ResourcePointer at +0x00.
  Its pointed D1 001F8080 structure (class 80801F00) stores WwiseSound at +0x20.

QuickTag's D1v2 parser independently identifies Wwise event tags as reference
8080080A and parses them as:
  +0x34 FileHash bank tag
  +0x38 u64 stream count
  +0x70 FileHash[count] Wwise streams
D1v2 Wwise stream payloads are package type/subtype 8/21.

Only this exact schema path is emitted as TYPED_EXACT audio ownership. Other
8080080A sightings in typed-path resources are retained as unclosed frontiers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_entity_resource_probe import ENTITY_RESOURCE_CLASS, parse_resource
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_split_tar_extract import SplitHttpTar

COMPOSITION_DISCRIMINATOR = "8080079A"
COMPOSITION_INFO = "80800610"
COMPOSITION_SOUND_RECORD_CLASS = "80800629"  # D1 schema string 29068080
COMPOSITION_SOUND_TARGET_CLASS = "80801F00"  # D1 schema string 001F8080
WWISE_EVENT_REF = "8080080A"
WWISE_STREAM_TYPE = 8
WWISE_STREAM_SUBTYPE = 21
NULLS = {"00000000", "FFFFFFFF"}

CHARM_SOURCE = (
    "MontagueM/Charm@50d36ee1f9ecadad7522504c20b1f3f9c97e30af "
    "Tiger/Schema/Entity/EntityStructs.cs + Tiger/SchemaTypes.cs"
)
QUICKTAG_SOURCE = (
    "v4nguard/quicktag main src/gui/audio_list.rs + src/gui/audio_events.rs"
)


def norm(x) -> str:
    return str(x).upper().removeprefix("0X").zfill(8)


def u32(b: bytes, o: int) -> int:
    if o < 0 or o + 4 > len(b):
        raise ValueError(f"u32 OOB 0x{o:X}/0x{len(b):X}")
    return struct.unpack_from("<I", b, o)[0]


def i32(b: bytes, o: int) -> int:
    if o < 0 or o + 4 > len(b):
        raise ValueError(f"i32 OOB 0x{o:X}/0x{len(b):X}")
    return struct.unpack_from("<i", b, o)[0]


def i64(b: bytes, o: int) -> int:
    if o < 0 or o + 8 > len(b):
        raise ValueError(f"i64 OOB 0x{o:X}/0x{len(b):X}")
    return struct.unpack_from("<q", b, o)[0]


def u64(b: bytes, o: int) -> int:
    if o < 0 or o + 8 > len(b):
        raise ValueError(f"u64 OOB 0x{o:X}/0x{len(b):X}")
    return struct.unpack_from("<Q", b, o)[0]


def dyn(b: bytes, field: int, stride: int) -> dict:
    if field < 0 or field + 0x10 > len(b):
        return {"ok": False, "field_offset": field, "error": "descriptor_oob"}
    count = i32(b, field)
    unknown = u32(b, field + 4)
    rel = i64(b, field + 8)
    # Charm RelativePointer base is its own field (+8), DynamicArray adds +0x10.
    absolute = field + 8 + rel + 0x10
    end = absolute + max(count, 0) * stride
    ok = count >= 0 and 0 <= absolute <= len(b) and 0 <= end <= len(b)
    return {
        "ok": ok,
        "field_offset": field,
        "count": count,
        "unknown_u32": f"{unknown:08X}",
        "relative": rel,
        "absolute": absolute,
        "end": end,
        "stride": stride,
        "error": None if ok else "array_bounds_or_negative_count",
    }


def meta_row(m: dict | None) -> dict | None:
    if m is None:
        return None
    return {
        "tag_hash": norm(m.get("tag_hash")),
        "index": int(m.get("index", m.get("entry_index", -1))),
        "reference": norm(m.get("reference", "FFFFFFFF")),
        "type": int(m.get("type", -1)),
        "subtype": int(m.get("subtype", -1)),
        "file_size": int(m.get("file_size", -1)),
    }


def exact(c: RemoteCorpus, h: str, expected_ref: str | None = None):
    h = norm(h)
    m = c.entry_meta(h)
    b, src = c.payload(h)
    if m is None or b is None:
        raise KeyError(f"{h}: exact payload unavailable")
    if expected_ref is not None and norm(m.get("reference")) != norm(expected_ref):
        raise ValueError(
            f"{h}: reference {norm(m.get('reference'))} != {norm(expected_ref)}"
        )
    return m, b, str(src)


def parse_event(c: RemoteCorpus, event_hash: str, cache: dict[str, dict]) -> dict:
    event_hash = norm(event_hash)
    if event_hash in cache:
        return cache[event_hash]
    m, b, src = exact(c, event_hash, WWISE_EVENT_REF)
    row = {
        "event": event_hash,
        "meta": meta_row(m),
        "payload_source": src,
        "payload_sha256": hashlib.sha256(b).hexdigest(),
        "payload_size": len(b),
        "violations": [],
        "streams": [],
    }
    if len(b) < 0x70:
        row["violations"].append("event_payload_shorter_than_0x70")
        cache[event_hash] = row
        return row
    bank = f"{u32(b, 0x34):08X}"
    count = u64(b, 0x38)
    row["bank_tag_hash"] = bank
    row["bank_meta"] = meta_row(c.entry_meta(bank)) if bank not in NULLS else None
    row["stream_count"] = int(count)
    end = 0x70 + int(count) * 4
    if end > len(b):
        row["violations"].append(
            f"event_stream_array_oob end=0x{end:X} size=0x{len(b):X}"
        )
        cache[event_hash] = row
        return row
    for i in range(int(count)):
        off = 0x70 + i * 4
        h = f"{u32(b, off):08X}"
        sm = c.entry_meta(h) if h not in NULLS else None
        srow = {
            "index": i,
            "field_offset": off,
            "field_offset_hex": f"0x{off:X}",
            "stream": h,
            "meta": meta_row(sm),
            "is_null": h in NULLS,
        }
        if h not in NULLS:
            if sm is None:
                srow["violation"] = "stream_unresolved"
                row["violations"].append(f"stream_{i}_{h}_unresolved")
            elif int(sm.get("type", -1)) != WWISE_STREAM_TYPE or int(
                sm.get("subtype", -1)
            ) != WWISE_STREAM_SUBTYPE:
                srow["violation"] = "stream_type_subtype_mismatch"
                row["violations"].append(
                    f"stream_{i}_{h}_type_subtype_{sm.get('type')}_{sm.get('subtype')}"
                )
            else:
                try:
                    _sm, sb, ssrc = exact(c, h)
                    srow["payload_source"] = ssrc
                    srow["payload_size"] = len(sb)
                    srow["payload_sha256"] = hashlib.sha256(sb).hexdigest()
                except Exception as ex:
                    srow["violation"] = repr(ex)
                    row["violations"].append(f"stream_{i}_{h}_payload:{ex!r}")
        row["streams"].append(srow)
    row["validation_ok"] = not row["violations"]
    cache[event_hash] = row
    return row


def parse_sound_array(
    c: RemoteCorpus,
    payload: bytes,
    parent_base: int,
    relative_field: int,
    array_name: str,
    event_cache: dict[str, dict],
) -> dict:
    field = parent_base + relative_field
    arr = dyn(payload, field, 0x08)
    out = {
        "array_name": array_name,
        "field_offset_in_composition_info": relative_field,
        "field_offset": field,
        "field_offset_hex": f"0x{field:X}",
        "descriptor": arr,
        "records": [],
        "violations": [],
    }
    if not arr["ok"]:
        out["violations"].append(f"{array_name}_descriptor_invalid")
        return out
    for i in range(arr["count"]):
        ro = arr["absolute"] + i * 0x08
        rel = i64(payload, ro)
        rec = {
            "index": i,
            "record_offset": ro,
            "record_offset_hex": f"0x{ro:X}",
            "relative_pointer": rel,
            "null_pointer": rel == 0,
        }
        if rel == 0:
            out["records"].append(rec)
            continue
        target = ro + rel
        rec["target_offset"] = target
        rec["target_offset_hex"] = f"0x{target:X}"
        if target < 4 or target + 0x24 > len(payload):
            rec["violation"] = "sound_resource_pointer_target_oob"
            out["violations"].append(f"{array_name}_{i}_target_oob")
            out["records"].append(rec)
            continue
        target_class = f"{u32(payload, target - 4):08X}"
        rec["target_class"] = target_class
        rec["target_class_matches"] = target_class == COMPOSITION_SOUND_TARGET_CLASS
        if not rec["target_class_matches"]:
            rec["violation"] = "sound_resource_pointer_class_mismatch"
            out["violations"].append(
                f"{array_name}_{i}_class_{target_class}_expected_{COMPOSITION_SOUND_TARGET_CLASS}"
            )
            out["records"].append(rec)
            continue
        event_hash = f"{u32(payload, target + 0x20):08X}"
        rec["wwise_sound_field_offset"] = target + 0x20
        rec["wwise_sound_field_offset_hex"] = f"0x{target + 0x20:X}"
        rec["event"] = event_hash
        rec["event_is_null"] = event_hash in NULLS
        if event_hash not in NULLS:
            try:
                ev = parse_event(c, event_hash, event_cache)
                rec["event_reference"] = ev["meta"]["reference"]
                rec["event_validation_ok"] = ev.get("validation_ok", False)
                if not rec["event_validation_ok"]:
                    out["violations"].append(f"{array_name}_{i}_{event_hash}_event_invalid")
            except Exception as ex:
                rec["violation"] = repr(ex)
                out["violations"].append(f"{array_name}_{i}_{event_hash}:{ex!r}")
        out["records"].append(rec)
    out["validation_ok"] = not out["violations"]
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--entity-closure", type=Path, required=True)
    ap.add_argument("--member-catalog", type=Path, action="append", required=True)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--part-count", type=int, default=10)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    closure = json.loads(a.entity_closure.read_text(encoding="utf-8"))
    if closure.get("status") != "D1_ENTITY_DEPENDENCY_CLOSURE_COMPLETE":
        raise SystemExit("entity closure is not complete")
    if closure.get("truncated"):
        raise SystemExit("entity closure is truncated")

    cats = load_catalogs(a.member_catalog)
    arc = SplitHttpTar(
        [f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1, a.part_count + 1)],
        retries=6,
        timeout=90,
    )
    c = RemoteCorpus(arc, cats, a.runtime)

    typed_nodes = [
        n
        for n in closure.get("nodes", [])
        if n.get("path_class") in {"TYPED_EXACT_ROOT", "TYPED_EXACT_PATH"}
    ]
    compositions = [
        n
        for n in typed_nodes
        if norm(n.get("entry", {}).get("reference", "FFFFFFFF")) == ENTITY_RESOURCE_CLASS
        and norm(n.get("unk10_class", "FFFFFFFF")) == COMPOSITION_DISCRIMINATOR
        and norm(n.get("unk18_class", "FFFFFFFF")) == COMPOSITION_INFO
    ]

    # Audit all exact Wwise event sightings in typed-path ERs. Only source-pinned
    # composition arrays below are promoted to typed audio ownership.
    aligned_event_sightings = []
    for n in typed_nodes:
        for x in n.get("aligned_resolved_tags", []) or []:
            if norm((x.get("entry") or {}).get("reference", "FFFFFFFF")) == WWISE_EVENT_REF:
                aligned_event_sightings.append(
                    {
                        "source_resource": norm(n["tag_hash"]),
                        "source_pair": [n.get("unk10_class"), n.get("unk18_class")],
                        "source_offset": int(x["offset"]),
                        "event": norm(x["tag_hash"]),
                        "evidence_class": "UNTYPED_ALIGNED_DISCOVERY",
                    }
                )

    event_cache: dict[str, dict] = {}
    rows = []
    violations = []
    typed_event_edges = []
    for n in compositions:
        h = norm(n["tag_hash"])
        row = {
            "resource": h,
            "source_path_class": n.get("path_class"),
            "pair": [COMPOSITION_DISCRIMINATOR, COMPOSITION_INFO],
            "violations": [],
        }
        try:
            m, b, src = exact(c, h, ENTITY_RESOURCE_CLASS)
            pr = parse_resource(b, "PS4")
            row["meta"] = meta_row(m)
            row["payload_source"] = src
            row["payload_sha256"] = hashlib.sha256(b).hexdigest()
            row["payload_size"] = len(b)
            row["unk10"] = pr.get("unk10")
            row["unk18"] = pr.get("unk18")
            if norm((pr.get("unk10") or {}).get("class_hash", "FFFFFFFF")) != COMPOSITION_DISCRIMINATOR:
                row["violations"].append("composition_discriminator_mismatch")
            p18 = pr.get("unk18") or {}
            if norm(p18.get("class_hash", "FFFFFFFF")) != COMPOSITION_INFO:
                row["violations"].append("composition_info_class_mismatch")
            base = p18.get("target_offset")
            if not isinstance(base, int):
                row["violations"].append("composition_info_target_missing")
            else:
                a1 = parse_sound_array(c, b, base, 0x110, "WwiseSounds1", event_cache)
                a2 = parse_sound_array(c, b, base, 0x130, "WwiseSounds2", event_cache)
                row["wwise_arrays"] = [a1, a2]
                row["violations"].extend(a1["violations"])
                row["violations"].extend(a2["violations"])
                for arr in (a1, a2):
                    for rec in arr.get("records", []):
                        eh = rec.get("event")
                        if eh and eh not in NULLS and rec.get("event_validation_ok"):
                            typed_event_edges.append(
                                {
                                    "subject": h,
                                    "predicate": "COMPOSITION_WWISE_EVENT",
                                    "object": eh,
                                    "array": arr["array_name"],
                                    "array_index": rec["index"],
                                    "field_offset": rec["wwise_sound_field_offset"],
                                    "field_offset_hex": rec["wwise_sound_field_offset_hex"],
                                    "evidence_class": "TYPED_EXACT",
                                }
                            )
        except Exception as ex:
            row["violations"].append(repr(ex))
        if row["violations"]:
            violations.extend({"resource": h, "error": x} for x in row["violations"])
        row["validation_ok"] = not row["violations"]
        rows.append(row)

    typed_events = sorted({x["object"] for x in typed_event_edges})
    typed_streams = sorted(
        {
            s["stream"]
            for h in typed_events
            for s in event_cache[h].get("streams", [])
            if not s.get("is_null") and not s.get("violation")
        }
    )
    event_bank_tags = sorted(
        {
            event_cache[h].get("bank_tag_hash")
            for h in typed_events
            if event_cache[h].get("bank_tag_hash") not in NULLS
        }
    )

    aligned_by_pair = Counter(
        f"{x['source_pair'][0]}->{x['source_pair'][1]}" for x in aligned_event_sightings
    )
    typed_edge_keys = {
        (x["subject"], x["field_offset"], x["object"]) for x in typed_event_edges
    }
    promoted_aligned = [
        x
        for x in aligned_event_sightings
        if (x["source_resource"], x["source_offset"], x["event"]) in typed_edge_keys
    ]
    frontier_sightings = [
        x
        for x in aligned_event_sightings
        if (x["source_resource"], x["source_offset"], x["event"]) not in typed_edge_keys
    ]

    out = {
        "schema": "d1_remote_activity_audio_composition_closure/v1",
        "status": (
            "D1_REMOTE_ACTIVITY_AUDIO_COMPOSITION_CLOSURE_COMPLETE"
            if not violations
            else "D1_REMOTE_ACTIVITY_AUDIO_COMPOSITION_CLOSURE_WITH_VIOLATIONS"
        ),
        "source_entity_closure": str(a.entity_closure),
        "pinned_sources": {"composition_schema": CHARM_SOURCE, "wwise_event_schema": QUICKTAG_SOURCE},
        "composition_pair": [COMPOSITION_DISCRIMINATOR, COMPOSITION_INFO],
        "composition_sound_record_class": COMPOSITION_SOUND_RECORD_CLASS,
        "composition_sound_target_class": COMPOSITION_SOUND_TARGET_CLASS,
        "wwise_event_reference": WWISE_EVENT_REF,
        "wwise_stream_type_subtype": [WWISE_STREAM_TYPE, WWISE_STREAM_SUBTYPE],
        "typed_path_node_count": len(typed_nodes),
        "composition_resource_count": len(compositions),
        "validated_composition_resource_count": sum(x["validation_ok"] for x in rows),
        "typed_event_edge_count": len(typed_event_edges),
        "unique_typed_event_count": len(typed_events),
        "unique_typed_stream_count": len(typed_streams),
        "unique_event_bank_tag_count": len(event_bank_tags),
        "aligned_event_sighting_count": len(aligned_event_sightings),
        "unique_aligned_event_count": len({x["event"] for x in aligned_event_sightings}),
        "aligned_event_sighting_class_pair_counts": dict(aligned_by_pair),
        "aligned_sightings_promoted_by_exact_schema_count": len(promoted_aligned),
        "unclosed_aligned_event_sighting_count": len(frontier_sightings),
        "unclosed_aligned_event_unique_count": len({x["event"] for x in frontier_sightings}),
        "typed_event_hashes": typed_events,
        "typed_stream_hashes": typed_streams,
        "event_bank_tags": event_bank_tags,
        "typed_event_edges": typed_event_edges,
        "events": {h: event_cache[h] for h in typed_events},
        "composition_resources": rows,
        "unclosed_aligned_event_sightings": frontier_sightings,
        "violations": violations,
        "violation_count": len(violations),
        "proof_policy": (
            "Only exact activity-owned typed-path EntityResources matching the pinned D1 composition pair "
            "8080079A->80800610 are traversed as audio owners. WwiseSounds1/+0x110 and WwiseSounds2/+0x130 "
            "are parsed as Charm DynamicArray records, each nested ResourcePointer must resolve to D1 class "
            "80801F00, and its +0x20 FileHash must resolve to exact Wwise event reference 8080080A. Event "
            "streams are then parsed using the independent QuickTag D1v2 offsets and must resolve to type/subtype "
            "8/21. Other aligned 8080080A sightings remain discovery-only frontiers. No sound/event semantic name "
            "or playback behavior is inferred."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(
        "STATUS", out["status"],
        "COMPOSITIONS", out["composition_resource_count"],
        "VALID", out["validated_composition_resource_count"],
        "EVENT_EDGES", out["typed_event_edge_count"],
        "EVENTS", out["unique_typed_event_count"],
        "STREAMS", out["unique_typed_stream_count"],
        "ALIGNED", out["aligned_event_sighting_count"],
        "PROMOTED", out["aligned_sightings_promoted_by_exact_schema_count"],
        "FRONTIER", out["unclosed_aligned_event_sighting_count"],
        "VIOLATIONS", out["violation_count"],
    )
    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
