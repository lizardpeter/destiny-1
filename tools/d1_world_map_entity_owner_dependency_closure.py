#!/usr/bin/env python3
"""Close exact D1 Activity map-entry Entity owners across package families.

Input is a complete ``d1_world_map_data_layer_census.py`` report. Every non-null
``SMapDataEntry.Entity`` TagHash is already source-owned by the Activity map graph,
so this adapter may use those exact hashes to derive physical Tiger package IDs.
It then recovers only those current package families through the verified global
Activity/package index and validates each entity TagHash against the expanded corpus.

This layer deliberately does *not* require the entity to be SEntity/80800734. The
map format owns a TagHash; class semantics are reported exactly and later adapters
may select only source-appropriate classes. This keeps static carrier entities,
visual entities, scripting carriers, and unknown classes loss-preserved.

No developer name, package filename, proximity, model resemblance, resource class,
or historical entity list can create an entity owner here.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import d1_tower_map_schema_validate_v5 as v5
from d1_filehash import package_hex

NULLS = {"00000000", "FFFFFFFF"}
EXPECTED_CENSUS_STATUS = "D1_WORLD_MAP_DATA_LAYER_CENSUS"


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def package_paths(root: Path) -> list[Path]:
    return sorted(p.resolve() for p in root.glob("*.pkg") if p.is_file())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", type=Path, required=True)
    ap.add_argument("--package-list", type=Path, required=True)
    ap.add_argument("--map-layer-json", type=Path, required=True)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--package-dir", type=Path, required=True)
    ap.add_argument("--work-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    a = ap.parse_args()

    src = json.loads(a.map_layer_json.read_text(encoding="utf-8"))
    violations: list[str] = []
    if src.get("status") != EXPECTED_CENSUS_STATUS:
        violations.append(f"map_layer_status:{src.get('status')!r}")
    if src.get("violations"):
        violations.append("map_layer_contains_violations")

    placements: list[dict] = []
    for table in src.get("tables", []):
        th = norm(table.get("map_data_table"))
        for row in table.get("entries", []):
            h = norm(row.get("entity_hash"))
            if h in NULLS:
                continue
            placements.append(
                {
                    "map_data_table": th,
                    "entry_index": row.get("index"),
                    "record_offset": row.get("record_offset"),
                    "entity_hash": h,
                    "rotation": row.get("rotation"),
                    "translation": row.get("translation"),
                    "world_id": row.get("world_id"),
                    "resource_class": row.get("resource_class"),
                    "resource_class_name": row.get("resource_class_name"),
                }
            )

    if not placements:
        violations.append("no_non_null_map_entity_hashes")

    by_entity: dict[str, list[dict]] = defaultdict(list)
    for row in placements:
        by_entity[row["entity_hash"]].append(row)
    unique_hashes = sorted(by_entity)
    package_ids = sorted({package_hex(h).lower() for h in unique_hashes})

    a.work_dir.mkdir(parents=True, exist_ok=True)
    a.package_dir.mkdir(parents=True, exist_ok=True)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.report.parent.mkdir(parents=True, exist_ok=True)

    recovery_report = a.work_dir / "entity_owner_package_recovery.json"
    cmd = [
        sys.executable,
        str(HERE / "d1_recover_indexed_package_families.py"),
        "--index", str(a.index),
        "--package-list", str(a.package_list),
    ]
    for pid in package_ids:
        cmd += ["--package-id", pid]
    cmd += [
        "--out-dir", str(a.package_dir),
        "--report", str(recovery_report),
    ]
    cp = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (a.work_dir / "entity_owner_package_recovery.stdout.txt").write_text(cp.stdout, encoding="utf-8")
    if cp.returncode != 0:
        raise SystemExit(
            f"indexed package recovery failed rc={cp.returncode}; "
            f"see {a.work_dir / 'entity_owner_package_recovery.stdout.txt'}"
        )

    rec = json.loads(recovery_report.read_text(encoding="utf-8"))
    if rec.get("status") != "D1_INDEXED_PACKAGE_FAMILY_RECOVERY_COMPLETE":
        violations.append(f"package_recovery_status:{rec.get('status')!r}")
    if rec.get("requested_package_ids") != package_ids:
        violations.append("package_recovery_requested_ids_mismatch")

    snapshots = package_paths(a.package_dir)
    if not snapshots:
        violations.append("expanded_package_corpus_empty")
        meta_by_hash = {}
    else:
        corpus = v5.v3.base.Corpus(snapshots, a.runtime.resolve())
        meta_by_hash = {h: corpus.entry_meta(h) for h in unique_hashes}

    missing = sorted(h for h, meta in meta_by_hash.items() if meta is None)
    if missing:
        violations.append("unresolved_entity_hashes_after_owner_package_recovery")

    class_by_hash = {
        h: (None if meta_by_hash.get(h) is None else norm(meta_by_hash[h].get("reference")))
        for h in unique_hashes
    }
    placement_class_counts = Counter(class_by_hash[row["entity_hash"]] or "MISSING" for row in placements)
    unique_class_counts = Counter(class_by_hash[h] or "MISSING" for h in unique_hashes)
    per_entity = []
    for h in unique_hashes:
        rows = by_entity[h]
        per_entity.append(
            {
                "entity_hash": h,
                "package_id": package_hex(h).lower(),
                "reference_class": class_by_hash[h],
                "meta": meta_by_hash.get(h),
                "placement_count": len(rows),
                "map_data_tables": sorted({x["map_data_table"] for x in rows}),
                "world_ids": sorted({str(x.get("world_id")) for x in rows}),
            }
        )

    for row in placements:
        row["entity_package_id"] = package_hex(row["entity_hash"]).lower()
        row["entity_reference_class"] = class_by_hash[row["entity_hash"]]
        row["entity_exists"] = meta_by_hash.get(row["entity_hash"]) is not None

    status = (
        "D1_WORLD_MAP_ENTITY_OWNER_DEPENDENCY_CLOSURE_COMPLETE"
        if not violations
        else "D1_WORLD_MAP_ENTITY_OWNER_DEPENDENCY_CLOSURE_PARTIAL"
    )
    out = {
        "schema_version": 1,
        "status": status,
        "source_map_layer_json": str(a.map_layer_json),
        "source_map_data_table_count": src.get("map_data_table_count"),
        "source_entry_count": src.get("entry_count"),
        "placement_count": len(placements),
        "unique_entity_count": len(unique_hashes),
        "entity_owner_package_family_count": len(package_ids),
        "entity_owner_package_ids": package_ids,
        "placement_entity_reference_class_counts": dict(sorted(placement_class_counts.items())),
        "unique_entity_reference_class_counts": dict(sorted(unique_class_counts.items())),
        "unique_entity_hashes": unique_hashes,
        "entities": per_entity,
        "placements": placements,
        "per_entity_placement_counts": {h: len(by_entity[h]) for h in unique_hashes},
        "unresolved_entity_hashes": missing,
        "violations": violations,
        "policy": (
            "Every entity owner originates as the exact non-null SMapDataEntry Entity TagHash from the supplied "
            "Activity-owned map-layer census. Physical package IDs are derived only with the source-validated "
            "universal D1 FileHash decoder and recovered through the archive-index integrity gate. Entity class "
            "is observed after recovery and is never assumed to be SEntity."
        ),
    }
    a.out.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

    report = {
        "schema_version": 1,
        "status": status,
        "source_map_layer_status": src.get("status"),
        "placement_count": len(placements),
        "unique_entity_count": len(unique_hashes),
        "derived_package_ids": package_ids,
        "package_recovery_report": str(recovery_report),
        "package_recovery_status": rec.get("status"),
        "package_recovery_member_count": rec.get("member_count"),
        "expanded_snapshot_count": len(snapshots),
        "unresolved_entity_hashes": missing,
        "violations": violations,
        "policy": out["policy"],
    }
    a.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": status,
        "placement_count": len(placements),
        "unique_entity_count": len(unique_hashes),
        "entity_owner_package_family_count": len(package_ids),
        "entity_owner_package_ids": package_ids,
        "placement_entity_reference_class_counts": dict(sorted(placement_class_counts.items())),
        "unique_entity_reference_class_counts": dict(sorted(unique_class_counts.items())),
        "unresolved_entity_hash_count": len(missing),
        "violations": violations,
    }, indent=2))
    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
