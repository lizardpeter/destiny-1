#!/usr/bin/env python3
"""Resolve Destiny 1 ROI map-entry resource chains without guessing ownership.

Source-derived D1 layout under test:
  SMapDataTable (808009A2)
    DynamicArray<SMapDataEntry> at +0x08, element size 0x90
  SMapDataEntry
    entity FileHash at +0x00
    rotation Vector4 at +0x20
    translation Vector4 at +0x30
    WorldID u64 at +0x80
    ResourcePointer at +0x88

ResourcePointer is an 8-byte signed relative pointer whose base is the pointer field
itself.  When nonzero, the pointed resource's class hash is the u32 immediately at
absolute-4.  For the D1 static-map resource class 80801AEA, the pointed structure has
an exact Tag/FileHash to StaticMapParent at +0x0C.  A StaticMapParent (80801AC6) has
an exact StaticMapData Tag/FileHash at +0x08, expected class 808008B4.

This tool records every physical table occurrence and every target candidate across
patch snapshots.  It never silently chooses a patch winner.  A chain is promoted to
`serialized_static_map_chain` only when all three serialized/class checks succeed:
ResourcePointer class -> StaticMapParent target class -> StaticMapData target class.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from d1_entry_extract import EntryReader

C = {
    "s_entity": "80800734",
    "map_data_table": "808009A2",
    "map_data_resource": "80801AEA",
    "static_map_parent": "80801AC6",
    "static_map_data": "808008B4",
}


def gen_of(p: Path) -> int:
    m = re.search(r"_(\d+)\.pkg$", p.name)
    return int(m.group(1)) if m else -1


def hx(v: int) -> str:
    return f"{v & 0xffffffff:08X}"


def u32(b: bytes, o: int) -> int:
    return struct.unpack_from("<I", b, o)[0]


def i32(b: bytes, o: int) -> int:
    return struct.unpack_from("<i", b, o)[0]


def i64(b: bytes, o: int) -> int:
    return struct.unpack_from("<q", b, o)[0]


def u64(b: bytes, o: int) -> int:
    return struct.unpack_from("<Q", b, o)[0]


def f4(b: bytes, o: int):
    return [float(x) for x in struct.unpack_from("<4f", b, o)]


def dyn_array(b: bytes, off: int, elem_size: int) -> dict:
    if off + 0x10 > len(b):
        return {"ok": False, "error": "header_oob", "field_offset": off}
    count = i32(b, off)
    unknown04 = u32(b, off + 4)
    rel = i64(b, off + 8)
    absolute = off + 8 + rel + 0x10
    end = absolute + max(count, 0) * elem_size
    ok = count >= 0 and absolute >= 0 and end <= len(b)
    return {
        "ok": ok, "field_offset": off, "count": count,
        "unknown04": unknown04, "relative": rel, "absolute": absolute,
        "end": end, "elem_size": elem_size, "payload_size": len(b),
    }


class Corpus:
    def __init__(self, paths: list[Path], runtime: Path):
        self.readers = []
        self.occ = defaultdict(list)
        for p in sorted(paths, key=lambda x: (x.name, gen_of(x))):
            r = EntryReader(p, runtime)
            self.readers.append((p, r))
            for e in r.entries:
                self.occ[e["tag_hash"].upper()].append((gen_of(p), p, r, e))
        for h in self.occ:
            self.occ[h].sort(key=lambda x: (x[0], x[1].name), reverse=True)

    def meta(self, x) -> dict:
        g, p, r, e = x
        return {
            "snapshot": p.name,
            "generation": g,
            "package_id": f"{int(r.h['pkg_id']):04X}",
            "entry_index": int(e["index"]),
            "tag_hash": e["tag_hash"].upper(),
            "reference": e["reference"].upper(),
            "type": int(e["type"]),
            "subtype": int(e["subtype"]),
            "size": int(e["file_size"]),
            "available": bool(r.available(e["index"])),
        }

    def target_candidates(self, h: str, expected_reference: str | None = None,
                          parse_payload=None) -> list[dict]:
        rows = []
        for x in self.occ.get(h.upper(), []):
            g, p, r, e = x
            m = self.meta(x)
            m["expected_reference"] = expected_reference
            m["class_matches"] = expected_reference is None or m["reference"] == expected_reference
            if m["available"]:
                try:
                    b = r.entry(e["index"])
                    m["payload_sha256"] = hashlib.sha256(b).hexdigest()
                    if parse_payload is not None:
                        m["parsed"] = parse_payload(b)
                except Exception as ex:
                    m["payload_error"] = repr(ex)
            rows.append(m)
        return rows


def parse_resource_pointer(b: bytes, field_off: int) -> dict:
    if field_off + 8 > len(b):
        return {"ok": False, "error": "pointer_field_oob", "field_offset": field_off}
    rel = i64(b, field_off)
    rep = {"field_offset": field_off, "relative": rel, "is_null": rel == 0}
    if rel == 0:
        rep.update({"ok": True, "absolute": None, "resource_class_hash": None})
        return rep
    absolute = field_off + rel
    class_off = absolute - 4
    rep["absolute"] = absolute
    rep["resource_class_offset"] = class_off
    if class_off < 0 or class_off + 4 > len(b) or absolute < 0 or absolute > len(b):
        rep.update({"ok": False, "error": "resource_pointer_oob"})
        return rep
    rep["resource_class_hash"] = hx(u32(b, class_off))
    rep["ok"] = True
    return rep


def parse_static_parent_payload(b: bytes) -> dict:
    if len(b) < 0x0C:
        return {"ok": False, "error": "static_parent_short", "payload_size": len(b)}
    return {
        "ok": True,
        "payload_size": len(b),
        "static_map_data": hx(u32(b, 0x08)),
        "unknown_0c": hx(u32(b, 0x0C)) if len(b) >= 0x10 else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", type=Path, action="append", required=True)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--max-entries", type=int, default=200000)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    corpus = Corpus([p.resolve() for p in args.snapshot], args.runtime.resolve())
    table_occurrences = []
    flat_entries = []
    static_chains = []
    pointer_class_counts = Counter()
    entity_target_class_counts = Counter()
    failures = []

    for p, r in corpus.readers:
        for e in r.entries:
            if e["reference"].upper() != C["map_data_table"]:
                continue
            meta = {
                "snapshot": p.name, "generation": gen_of(p),
                "package_id": f"{int(r.h['pkg_id']):04X}",
                "entry_index": int(e["index"]), "tag_hash": e["tag_hash"].upper(),
                "reference": e["reference"].upper(), "size": int(e["file_size"]),
                "available": bool(r.available(e["index"])),
            }
            row = {**meta, "entries": [], "violations": []}
            if not meta["available"]:
                row["violations"].append("payload unavailable")
                table_occurrences.append(row)
                continue
            try:
                b = r.entry(e["index"])
            except Exception as ex:
                row["violations"].append(repr(ex)); table_occurrences.append(row); continue
            row["payload_sha256"] = hashlib.sha256(b).hexdigest()
            a = dyn_array(b, 0x08, 0x90)
            row["data_entries_array"] = a
            if not a["ok"]:
                row["violations"].append("data_entries_dynamic_array_bounds")
                table_occurrences.append(row)
                continue
            if a["count"] > args.max_entries:
                row["violations"].append("entry_count_exceeds_guard")
                table_occurrences.append(row)
                continue

            for i in range(a["count"]):
                o = a["absolute"] + i * 0x90
                entity_hash = hx(u32(b, o))
                rotation = f4(b, o + 0x20)
                translation = f4(b, o + 0x30)
                world_id = u64(b, o + 0x80)
                rp = parse_resource_pointer(b, o + 0x88)
                if rp.get("resource_class_hash"):
                    pointer_class_counts[rp["resource_class_hash"]] += 1
                entity_candidates = corpus.target_candidates(entity_hash, C["s_entity"])
                for ec in entity_candidates:
                    entity_target_class_counts[ec["reference"]] += 1

                erow = {
                    "table_snapshot": p.name,
                    "table_generation": gen_of(p),
                    "table_tag_hash": e["tag_hash"].upper(),
                    "map_entry_index": i,
                    "entry_absolute_offset": o,
                    "entity_hash": entity_hash,
                    "entity_candidates": entity_candidates,
                    "rotation": rotation,
                    "translation": translation,
                    "transform_finite": all(math.isfinite(x) for x in rotation + translation),
                    "world_id": f"{world_id:016X}",
                    "data_resource_pointer": rp,
                    "serialized_static_map_chain": None,
                }

                if rp.get("ok") and not rp.get("is_null") and rp.get("resource_class_hash") == C["map_data_resource"]:
                    absr = int(rp["absolute"])
                    if absr + 0x10 <= len(b):
                        parent_hash = hx(u32(b, absr + 0x0C))
                        parent_candidates = corpus.target_candidates(parent_hash, C["static_map_parent"], parse_static_parent_payload)
                        chain = {
                            "resource_class_hash": C["map_data_resource"],
                            "resource_absolute_offset": absr,
                            "static_map_parent_hash": parent_hash,
                            "static_map_parent_candidates": parent_candidates,
                            "validated_targets": [],
                            "status": "serialized_resource_pointer_only",
                        }
                        for pc in parent_candidates:
                            if not pc.get("class_matches") or not pc.get("parsed", {}).get("ok"):
                                continue
                            smh = pc["parsed"]["static_map_data"]
                            smc = corpus.target_candidates(smh, C["static_map_data"])
                            valid_sm = [x for x in smc if x.get("class_matches")]
                            chain["validated_targets"].append({
                                "parent_snapshot": pc["snapshot"],
                                "parent_generation": pc["generation"],
                                "static_map_data_hash": smh,
                                "static_map_data_candidates": smc,
                                "static_map_data_class_match_count": len(valid_sm),
                            })
                        if chain["validated_targets"] and any(x["static_map_data_class_match_count"] > 0 for x in chain["validated_targets"]):
                            chain["status"] = "serialized_static_map_chain"
                            static_chains.append({
                                "table_snapshot": p.name,
                                "table_tag_hash": e["tag_hash"].upper(),
                                "map_entry_index": i,
                                "world_id": f"{world_id:016X}",
                                "rotation": rotation,
                                "translation": translation,
                                "static_map_parent_hash": parent_hash,
                                "targets": chain["validated_targets"],
                            })
                        erow["serialized_static_map_chain"] = chain
                    else:
                        erow["serialized_static_map_chain"] = {"status": "map_data_resource_short_or_oob"}

                row["entries"].append(erow)
                flat_entries.append(erow)
            table_occurrences.append(row)

    unique_chain_keys = set()
    unique_static_maps = set()
    for c in static_chains:
        for t in c["targets"]:
            if t["static_map_data_class_match_count"]:
                unique_chain_keys.add((c["table_tag_hash"], c["map_entry_index"], c["static_map_parent_hash"], t["static_map_data_hash"]))
                unique_static_maps.add(t["static_map_data_hash"])

    summary = {
        "physical_map_data_table_occurrences": len(table_occurrences),
        "parsed_map_entry_occurrences": len(flat_entries),
        "resource_pointer_class_frequency": dict(pointer_class_counts.most_common()),
        "static_map_resource_pointer_occurrences": pointer_class_counts.get(C["map_data_resource"], 0),
        "serialized_static_map_chain_occurrences": len(static_chains),
        "unique_serialized_static_map_chains": len(unique_chain_keys),
        "unique_static_map_data_targets": len(unique_static_maps),
        "unique_static_map_data_hashes": sorted(unique_static_maps),
        "entries_with_entity_target_candidates": sum(bool(x["entity_candidates"]) for x in flat_entries),
        "finite_transform_entries": sum(x["transform_finite"] for x in flat_entries),
        "failure_count": len(failures),
    }
    report = {
        "evidence_status": "SOURCE_DERIVED_OFFSETS_WITH_SERIALIZED_CHAIN_VALIDATION",
        "summary": summary,
        "class_constants": C,
        "table_occurrences": table_occurrences,
        "static_map_chains": static_chains,
        "policy": {
            "patch_precedence": "none inferred; every physical occurrence and target candidate is retained",
            "static_chain_promotion": "requires ResourcePointer class 80801AEA, serialized parent Tag resolving to class 80801AC6, and serialized StaticMapData Tag resolving to class 808008B4",
            "transforms": "rotation/translation values are recorded from source-derived offsets; semantics are not promoted by plausibility alone",
            "entity_hash": "candidate entity occurrences are recorded; no entity ownership is inferred from table proximity",
        },
    }
    (args.out / "tower_map_entry_chains.json").write_text(json.dumps(report, indent=2) + "\n")
    (args.out / "tower_map_entry_summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    with (args.out / "tower_static_map_chains.csv").open("w", newline="") as f:
        fields = ["table_snapshot","table_tag_hash","map_entry_index","world_id","static_map_parent_hash","static_map_data_hash"]
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        seen = set()
        for c in static_chains:
            for t in c["targets"]:
                if not t["static_map_data_class_match_count"]: continue
                rr = {k:c[k] for k in fields if k in c}; rr["static_map_data_hash"] = t["static_map_data_hash"]
                key=tuple(rr.get(k) for k in fields)
                if key in seen: continue
                seen.add(key); w.writerow(rr)

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
