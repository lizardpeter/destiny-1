#!/usr/bin/env python3
"""Fail-closed semantic probe for Xur switch-bearing direct EntityResources.

This probe distinguishes serialized switch definition/permutation banks from a genuine
instantiated selector/configuration consumer. It never promotes raw key/value
co-occurrence, descriptor adjacency, default-member proximity, or an untyped FileHash
to live state.

Current targets:
- 80C88CE2: source-closed model-owner/static permutation definition resource.
- 80C885CC: direct Xur EntityResource carrying 26170C92 structures whose semantic
  ownership is being closed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from d1_entity_resource_probe import ENTITY_RESOURCE_CLASS, parse_resource
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_split_tar_extract import SplitHttpTar

KEYS = ["51E7A18D", "4C58EF8F", "26170C92", "6EECD523"]
VALUES = {
    "51E7A18D": ["6DFE676D"],
    "4C58EF8F": [
        "237B2A6A", "4AC210DE", "562B37AD", "5869948C", "5EE47B3A",
        "6093B6B7", "676A29BB", "693AC432", "6C4E2617", "7365B554",
        "AE1880F4", "C2D87ACF", "D5A2FB2C", "D93AF609", "E32027FC",
    ],
    "26170C92": [
        "31BAEAC2", "4AC210DE", "562B37AD", "5EE47B3A", "6093B6B7",
        "676A29BB", "693AC432", "6C4E2617", "7365B554", "742F9CDE",
        "871AC0EA", "9932E645", "AE1880F4", "D93AF609", "E32027FC",
    ],
    "6EECD523": ["4B375162", "6CC50CB8", "871AC0EA"],
}
MATERIALS = ["80C885E6", "80C885E7", "80C885E8", "80C885E9", "80C885EA"]


def norm(x: str) -> str:
    return str(x).upper().removeprefix("0X").zfill(8)


def le(h: str) -> bytes:
    return struct.pack("<I", int(h, 16))


def offsets(blob: bytes, needle: bytes) -> list[int]:
    out: list[int] = []
    start = 0
    while True:
        off = blob.find(needle, start)
        if off < 0:
            return out
        out.append(off)
        start = off + 1


def context(blob: bytes, off: int, n: int = 32) -> str:
    lo = max(0, off - n)
    hi = min(len(blob), off + 8 + n)
    return blob[lo:hi].hex()


def u32_window(blob: bytes, off: int, radius_words: int = 10) -> list[dict]:
    lo = max(0, (off // 4 - radius_words) * 4)
    hi = min(len(blob) - (len(blob) % 4), (off // 4 + radius_words + 2) * 4)
    out = []
    for p in range(lo, hi, 4):
        v = struct.unpack_from("<I", blob, p)[0]
        row = {"offset": p, "offset_hex": f"0x{p:X}", "u32": f"{v:08X}"}
        if 0x80800000 <= v <= 0x817FFFFF:
            row["current_filehash_range"] = True
        if p == off:
            row["target"] = True
        out.append(row)
    return out


def pointer_summary(p: dict) -> dict:
    return {
        "field_offset": p.get("field_offset"),
        "relative": p.get("relative"),
        "target_offset": p.get("target_offset"),
        "null": p.get("null"),
        "class_hash": p.get("class_hash"),
        "class_name": p.get("class_name"),
        "error": p.get("error"),
    }


def classify_hit(blob: bytes, off: int, er: dict) -> dict:
    regions = []
    for name in ("unk08", "unk10", "unk18"):
        p = er.get(name) or {}
        t = p.get("target_offset")
        if isinstance(t, int) and off >= t:
            regions.append({"pointer": name, "relative_to_target": off - t})
    return {
        "offset": off,
        "offset_hex": f"0x{off:X}",
        "aligned4": off % 4 == 0,
        "pointer_regions": regions,
        "context_hex": context(blob, off),
        "u32_window": u32_window(blob, off),
    }


def aligned_filehashes(blob: bytes) -> list[dict]:
    out = []
    end = len(blob) - (len(blob) % 4)
    for off in range(0, end, 4):
        v = struct.unpack_from("<I", blob, off)[0]
        if 0x80800000 <= v <= 0x817FFFFF:
            out.append({"offset": off, "offset_hex": f"0x{off:X}", "tag_hash": f"{v:08X}"})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--resource", action="append", required=True)
    ap.add_argument("--member-catalog", type=Path, action="append", required=True)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--part-count", type=int, default=10)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    cats = load_catalogs(a.member_catalog)
    arc = SplitHttpTar(
        [f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1, a.part_count + 1)],
        retries=6,
        timeout=90,
    )
    corpus = RemoteCorpus(arc, cats, a.runtime)

    rows = []
    violations = []
    for raw in a.resource:
        h = norm(raw)
        try:
            meta = corpus.entry_meta(h)
            blob, source = corpus.payload(h)
            if meta is None or blob is None:
                raise ValueError("exact payload unavailable")
            if norm(meta.get("reference", "00000000")) != ENTITY_RESOURCE_CLASS:
                raise ValueError(f"expected EntityResource reference {ENTITY_RESOURCE_CLASS}, got {meta.get('reference')}")
            er = parse_resource(blob, "PS4")

            key_hits = {}
            pair_hits = []
            material_hits = {}
            for k in KEYS:
                hs = [classify_hit(blob, o, er) for o in offsets(blob, le(k))]
                if hs:
                    key_hits[k] = hs
                for v in VALUES[k]:
                    for o in offsets(blob, le(k) + le(v)):
                        pair_hits.append({
                            "key": k,
                            "value": v,
                            **classify_hit(blob, o, er),
                        })
            for m in MATERIALS:
                hs = [classify_hit(blob, o, er) for o in offsets(blob, le(m))]
                if hs:
                    material_hits[m] = hs

            rows.append({
                "tag_hash": h,
                "reference": norm(meta.get("reference")),
                "type": meta.get("type"),
                "subtype": meta.get("subtype"),
                "bytes": len(blob),
                "sha256": hashlib.sha256(blob).hexdigest(),
                "source": source,
                "semantic_role": er.get("semantic_role"),
                "declared_file_size": er.get("declared_file_size"),
                "unk08": pointer_summary(er.get("unk08") or {}),
                "unk10": pointer_summary(er.get("unk10") or {}),
                "unk18": pointer_summary(er.get("unk18") or {}),
                "key_hits": key_hits,
                "adjacent_key_value_pairs": pair_hits,
                "material_hits": material_hits,
                "aligned_filehashes": aligned_filehashes(blob),
                "consumer_semantics_proven": False,
            })
        except Exception as ex:
            rows.append({"tag_hash": h, "error": repr(ex)})
            violations.append(f"{h}:{ex!r}")

    by_hash = {r["tag_hash"]: r for r in rows if "error" not in r}
    static = by_hash.get("80C88CE2")
    cand = by_hash.get("80C885CC")

    candidate_summary = None
    if cand is not None:
        candidate_summary = {
            "tag_hash": "80C885CC",
            "semantic_role": cand.get("semantic_role"),
            "unk08_class": (cand.get("unk08") or {}).get("class_hash"),
            "unk10_class": (cand.get("unk10") or {}).get("class_hash"),
            "unk18_class": (cand.get("unk18") or {}).get("class_hash"),
            "key_hit_counts": {k: len(v) for k, v in cand.get("key_hits", {}).items()},
            "pair_hit_count": len(cand.get("adjacent_key_value_pairs", [])),
            "material_hit_counts": {k: len(v) for k, v in cand.get("material_hits", {}).items()},
            "same_discriminator_as_static_model_owner": bool(
                static and (cand.get("unk10") or {}).get("class_hash") == (static.get("unk10") or {}).get("class_hash")
            ),
            "same_parent_class_as_static_model_owner": bool(
                static and (cand.get("unk18") or {}).get("class_hash") == (static.get("unk18") or {}).get("class_hash")
            ),
            "consumer_semantics_proven": False,
        }

    report = {
        "schema": "d1_remote_xur_switch_resource_semantic_probe/v2",
        "status": "D1_XUR_SWITCH_RESOURCE_SEMANTIC_FRONTIER" if not violations else "D1_XUR_SWITCH_RESOURCE_SEMANTIC_PROBE_VIOLATIONS",
        "resources": rows,
        "candidate_80C885CC": candidate_summary,
        "gates": {
            "E6_80C885E6_live_selection_proven": False,
            "E7_80C885E7_live_selection_proven": False,
            "E8_80C885E8_live_selection_proven": False,
        },
        "violations": violations,
        "policy": (
            "Raw key/value/material occurrence, adjacency, null/default descriptor proximity, and untyped FileHash equality are discovery evidence only. "
            "A gate may pass only after the owning resource schema establishes selector/configuration consumer semantics and the retail evaluation path is closed."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "status": report["status"],
        "candidate_80C885CC": candidate_summary,
        "gates": report["gates"],
        "violations": violations,
    }, indent=2))
    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
