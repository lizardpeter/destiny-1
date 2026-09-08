#!/usr/bin/env python3
"""Build the runtime placement view for Activity-owned D1 map entities.

Input is ``d1_world_map_entity_owner_dependency_closure.py`` output. Serialized map
entries are preserved losslessly, but repeated *real* WorldIDs are collapsed only
when Entity TagHash, transform and DataResource class agree exactly. The retail
``FFFFFFFFFFFFFFFF`` WorldID is treated as a sentinel/no-identity value, so each
such serialization remains an independent runtime placement.

The resulting manifest intentionally matches the ``unique_world_placements``
contract consumed by ``d1_world_articulated_entity_plan.py`` while retaining the
map-table source references required for provenance.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

SENTINELS = {"FFFFFFFFFFFFFFFF"}
NULLS = {"00000000", "FFFFFFFF"}
EXPECTED_STATUS = "D1_WORLD_MAP_ENTITY_OWNER_DEPENDENCY_CLOSURE_COMPLETE"


def norm_hash(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def norm_world(v: object) -> str:
    s = str(v).upper().removeprefix("0X")
    try:
        return f"{int(s, 16):016X}"
    except ValueError:
        return s.zfill(16)


def source_ref(row: dict) -> dict:
    return {
        "source_kind": "activity_map_data_table",
        "source_hash": row.get("map_data_table"),
        "index": row.get("entry_index"),
        "record_offset": row.get("record_offset"),
    }


def signature(row: dict):
    return (
        norm_hash(row.get("entity_hash")),
        tuple(row.get("rotation") or []),
        tuple(row.get("translation") or []),
        row.get("resource_class"),
    )


def runtime_row(rows: list[dict], identity_kind: str) -> dict:
    first = rows[0]
    wid = norm_world(first.get("world_id"))
    return {
        "world_id": int(wid, 16) if all(c in "0123456789ABCDEF" for c in wid) else None,
        "world_id_hex": wid,
        "world_id_identity_kind": identity_kind,
        "entity_hash": norm_hash(first.get("entity_hash")),
        "rotation": first.get("rotation"),
        "translation": first.get("translation"),
        "data_resource_class": first.get("resource_class"),
        "serialized_reference_count": len(rows),
        "duplicate_serialization_count": max(0, len(rows) - 1),
        "serializations_consistent": len({signature(x) for x in rows}) == 1,
        "source_references": [source_ref(x) for x in rows],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--owner-closure", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    src = json.loads(a.owner_closure.read_text(encoding="utf-8"))
    violations: list[str] = []
    if src.get("status") != EXPECTED_STATUS:
        violations.append(f"owner_closure_status:{src.get('status')!r}")
    if src.get("violations"):
        violations.append("owner_closure_contains_violations")

    serialized = []
    for row in src.get("placements", []):
        h = norm_hash(row.get("entity_hash"))
        if h in NULLS:
            continue
        copied = dict(row)
        copied["entity_hash"] = h
        copied["world_id"] = norm_world(row.get("world_id"))
        serialized.append(copied)

    by_world: dict[str, list[dict]] = defaultdict(list)
    sentinel_rows: list[dict] = []
    for row in serialized:
        wid = row["world_id"]
        if wid in SENTINELS:
            sentinel_rows.append(row)
        else:
            by_world[wid].append(row)

    runtime: list[dict] = []
    conflicting_world_ids = []
    for wid in sorted(by_world):
        rows = by_world[wid]
        rr = runtime_row(rows, "real_world_id")
        if not rr["serializations_consistent"]:
            conflicting_world_ids.append(wid)
            violations.append(f"world_id_conflicting_serializations:{wid}")
        runtime.append(rr)

    for row in sentinel_rows:
        runtime.append(runtime_row([row], "sentinel_no_identity"))

    unique_entities = sorted({norm_hash(x.get("entity_hash")) for x in serialized})
    runtime_entity_counts = Counter(x["entity_hash"] for x in runtime)
    serialized_entity_counts = Counter(x["entity_hash"] for x in serialized)
    status = (
        "D1_WORLD_MAP_ENTITY_RUNTIME_PLACEMENTS_COMPLETE"
        if not violations
        else "D1_WORLD_MAP_ENTITY_RUNTIME_PLACEMENTS_PARTIAL"
    )
    out = {
        "schema_version": 1,
        "status": status,
        "source_owner_closure": str(a.owner_closure),
        "serialized_entity_placement_reference_count": len(serialized),
        "unique_runtime_world_placement_count": len(runtime),
        "sentinel_world_id_runtime_placement_count": len(sentinel_rows),
        "duplicate_serialized_placement_reference_count": sum(x["duplicate_serialization_count"] for x in runtime),
        "unique_entity_hash_count": len(unique_entities),
        "unique_entity_hashes": unique_entities,
        "runtime_entity_placement_counts": dict(sorted(runtime_entity_counts.items())),
        "entity_reference_counts": dict(sorted(serialized_entity_counts.items())),
        "unique_world_placements": runtime,
        "serialized_placements": serialized,
        "conflicting_world_ids": conflicting_world_ids,
        "violations": violations,
        "policy": (
            "All serialized Activity map entries remain preserved. Real WorldIDs collapse only when Entity, transform and "
            "DataResource class agree exactly. FFFFFFFFFFFFFFFF is a sentinel/no-identity WorldID and is never used to "
            "merge distinct serializations. This manifest supplies the standard unique_world_placements contract for "
            "downstream articulated world-entity planning."
        ),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in (
        "status",
        "serialized_entity_placement_reference_count",
        "unique_runtime_world_placement_count",
        "sentinel_world_id_runtime_placement_count",
        "duplicate_serialized_placement_reference_count",
        "unique_entity_hash_count",
        "conflicting_world_ids",
        "violations",
    )}, indent=2))
    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
