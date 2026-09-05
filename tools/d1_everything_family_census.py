#!/usr/bin/env python3
"""Loss-preserving census of every entry in one Destiny 1 PS4 Tiger package family.

This deliberately records *facts before semantics*.  It unions all supplied physical
patch snapshots, records every physical entry occurrence, decodes only payload
structures already understood by this project, and can scan structured payloads for
aligned literal references to other TagHashes in the same supplied corpus.

A literal edge means only "these four bytes equal this known TagHash at this aligned
offset".  It is useful reverse-engineering evidence, but it is NOT automatically an
ownership, placement, material, animation, or runtime relationship.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from d1_entry_extract import EntryReader, decode_known

# Only names that have already been byte-validated elsewhere in this repository.
KNOWN_REFERENCE_LABELS = {
    "80800734": "s_entity",
    "80800861": "EntityResource",
    "80801AB5": "s_entity_model",
    "808005A1": "s_animation_clip",
    "8080222A": "animation/control structured wrapper",
    "808008B2": "runtime-rig payload (schema partial)",
    "808006BD": "skeleton EntityResource payload link (role validated; schema partial)",
    "8080049A": "skeleton hierarchy/transforms (role validated; schema partial)",
}


def norm_hash(s: str) -> str:
    return s.upper().removeprefix("0X").zfill(8)


def occurrence_row(snapshot_index: int, snapshot: Path, r: EntryReader, e: dict) -> dict:
    return {
        "snapshot_index": snapshot_index,
        "snapshot": snapshot.name,
        "package_id": f"{int(r.h['pkg_id']):04X}",
        "platform": r.h["platform"],
        "entry_index": int(e["index"]),
        "tag_hash": e["tag_hash"].upper(),
        "type": int(e["type"]),
        "subtype": int(e["subtype"]),
        "reference": e["reference"].upper(),
        "reference_label": KNOWN_REFERENCE_LABELS.get(e["reference"].upper()),
        "file_size": int(e["file_size"]),
        "starting_block": int(e["starting_block"]),
        "starting_block_offset": int(e["starting_block_offset"]),
        "entry_b": e["entry_b"].upper(),
        "available": bool(r.available(e["index"])),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", type=Path, action="append", required=True,
                    help="physical *_N.pkg snapshot; repeat newest/oldest in any order")
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--payload-hash-max", type=int, default=2 * 1024 * 1024,
                    help="hash/decode resident payloads no larger than this many bytes")
    ap.add_argument("--literal-scan-max", type=int, default=4 * 1024 * 1024,
                    help="scan aligned dwords in resident type-16 payloads up to this size")
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    snapshots = [p.resolve() for p in args.snapshot]
    readers: list[tuple[Path, EntryReader]] = []
    for p in snapshots:
        readers.append((p, EntryReader(p, args.runtime)))

    package_ids = sorted({int(r.h["pkg_id"]) for _, r in readers})
    platforms = sorted({r.h["platform"] for _, r in readers})

    occurrences: list[dict] = []
    union: dict[str, list[int]] = defaultdict(list)
    ref_counts = Counter()
    type_counts = Counter()
    snapshot_rows = []

    # First pass: metadata only, so the TagHash universe is known before payload scans.
    for si, (path, r) in enumerate(readers):
        snapshot_rows.append({
            "snapshot_index": si,
            "snapshot": path.name,
            "package_id": f"{int(r.h['pkg_id']):04X}",
            "platform": r.h["platform"],
            "entry_count": len(r.entries),
            "block_count": len(r.blocks),
        })
        for e in r.entries:
            row = occurrence_row(si, path, r, e)
            oi = len(occurrences)
            occurrences.append(row)
            union[row["tag_hash"]].append(oi)
            ref_counts[row["reference"]] += 1
            type_counts[f"{row['type']}:{row['subtype']}"] += 1

    known_hash_ints = {int(h, 16): h for h in union}
    literal_edges = []
    payload_errors = []
    payload_scanned = 0
    payload_hashed = 0

    # Second pass: only resident payloads.  Failures are retained per occurrence.
    for oi, row in enumerate(occurrences):
        if not row["available"]:
            continue
        if row["file_size"] > max(args.payload_hash_max, args.literal_scan_max):
            continue
        _, r = readers[row["snapshot_index"]]
        e = r.entries[row["entry_index"]]
        try:
            b = r.entry(e["index"])
        except Exception as ex:
            row["payload_error"] = repr(ex)
            payload_errors.append({"occurrence_index": oi, "error": repr(ex)})
            continue

        if len(b) <= args.payload_hash_max:
            row["payload_sha256"] = hashlib.sha256(b).hexdigest()
            payload_hashed += 1
            try:
                decoded = decode_known(e, b, r.h["platform"])
                # Keep only fields added by the proven decoder, not duplicated metadata.
                skip = {"index", "tag_hash", "type", "subtype", "size", "reference", "entry_b", "sha256", "prefix"}
                known = {k: v for k, v in decoded.items() if k not in skip}
                if known:
                    row["known_decode"] = known
            except Exception as ex:
                row["known_decode_error"] = repr(ex)

        if row["type"] == 16 and len(b) <= args.literal_scan_max:
            payload_scanned += 1
            hits = defaultdict(list)
            # Aligned little-endian dwords only.  This is deliberately conservative.
            for off in range(0, len(b) - 3, 4):
                val = struct.unpack_from("<I", b, off)[0]
                target = known_hash_ints.get(val)
                if target is not None:
                    hits[target].append(off)
            for target, offsets in sorted(hits.items()):
                literal_edges.append({
                    "source_occurrence_index": oi,
                    "source_snapshot": row["snapshot"],
                    "source_entry_index": row["entry_index"],
                    "source_tag_hash": row["tag_hash"],
                    "source_reference": row["reference"],
                    "target_tag_hash": target,
                    "count": len(offsets),
                    "aligned_offsets": offsets,
                    "evidence_kind": "aligned_literal_taghash",
                    "semantic_policy": "co-reference evidence only; ownership/role not inferred",
                })

    # Union rows retain every physical occurrence instead of silently selecting a patch winner.
    union_rows = []
    for h, indexes in sorted(union.items()):
        refs = sorted({occurrences[i]["reference"] for i in indexes})
        ts = sorted({f"{occurrences[i]['type']}:{occurrences[i]['subtype']}" for i in indexes})
        sizes = sorted({occurrences[i]["file_size"] for i in indexes})
        payload_shas = sorted({occurrences[i].get("payload_sha256") for i in indexes if occurrences[i].get("payload_sha256")})
        union_rows.append({
            "tag_hash": h,
            "occurrence_count": len(indexes),
            "occurrence_indexes": indexes,
            "references": refs,
            "reference_labels": sorted({KNOWN_REFERENCE_LABELS[x] for x in refs if x in KNOWN_REFERENCE_LABELS}),
            "type_subtypes": ts,
            "file_sizes": sizes,
            "resident_occurrence_count": sum(1 for i in indexes if occurrences[i]["available"]),
            "payload_sha256s": payload_shas,
            "metadata_conflicts_across_snapshots": len(refs) > 1 or len(ts) > 1 or len(sizes) > 1,
            "payload_conflicts_across_snapshots": len(payload_shas) > 1,
        })

    summary = {
        "snapshot_count": len(readers),
        "package_ids": [f"{x:04X}" for x in package_ids],
        "platforms": platforms,
        "physical_entry_occurrences": len(occurrences),
        "union_tag_hash_count": len(union_rows),
        "available_occurrences": sum(1 for r in occurrences if r["available"]),
        "payload_hashed_occurrences": payload_hashed,
        "structured_payloads_literal_scanned": payload_scanned,
        "literal_edge_count": len(literal_edges),
        "payload_error_count": len(payload_errors),
        "known_reference_counts": {
            h: {"label": label, "count": ref_counts.get(h, 0)}
            for h, label in KNOWN_REFERENCE_LABELS.items() if ref_counts.get(h, 0)
        },
        "s_entity_model_occurrences": ref_counts.get("80801AB5", 0),
        "s_animation_clip_occurrences": ref_counts.get("808005A1", 0),
        "s_entity_occurrences": ref_counts.get("80800734", 0),
        "entity_resource_occurrences": ref_counts.get("80800861", 0),
    }

    report = {
        "summary": summary,
        "snapshots": snapshot_rows,
        "reference_frequency": dict(sorted(ref_counts.items())),
        "type_subtype_frequency": dict(sorted(type_counts.items())),
        "known_reference_labels": KNOWN_REFERENCE_LABELS,
        "union_entries": union_rows,
        "physical_occurrences": occurrences,
        "literal_edges": literal_edges,
        "payload_errors": payload_errors,
        "policy": {
            "patch_precedence": "not inferred; every supplied physical occurrence is preserved",
            "literal_edges": "aligned literal TagHash equality is co-reference evidence only",
            "class_names": "only previously byte-validated labels are named; all other references remain hashes",
        },
    }
    (args.out / "everything_census.json").write_text(json.dumps(report, indent=2) + "\n")

    with (args.out / "union_entries.csv").open("w", newline="") as f:
        fields = ["tag_hash", "occurrence_count", "resident_occurrence_count", "references", "type_subtypes", "file_sizes", "metadata_conflicts_across_snapshots", "payload_conflicts_across_snapshots"]
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for r in union_rows:
            w.writerow({k: ";".join(map(str, r[k])) if isinstance(r[k], list) else r[k] for k in fields})

    with (args.out / "literal_edges.csv").open("w", newline="") as f:
        fields = ["source_snapshot", "source_entry_index", "source_tag_hash", "source_reference", "target_tag_hash", "count", "aligned_offsets", "evidence_kind"]
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for r in literal_edges:
            rr = {k: r[k] for k in fields}; rr["aligned_offsets"] = ";".join(hex(x) for x in r["aligned_offsets"])
            w.writerow(rr)

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
