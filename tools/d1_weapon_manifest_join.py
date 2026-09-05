#!/usr/bin/env python3
"""Join byte-proven D1 retail tables into per-inventory weapon manifests.

This tool is intentionally a resolver, not an exporter.  It combines:

  inventory census
    InventoryItemHash -> inventory definition -> art arrangement index / weapon pattern index

  art-arrangement table
    arrangement index -> assignment hashes -> EntityParent -> EntityDataROI

  weapon-pattern table
    weapon pattern index -> WeaponTypeHash / PatternHash / sandbox pattern s_entity

  optional shared-context catalog
    exact inventory/pattern/type assignment -> shared viewmodel owner/rig/control/wrapper

The result is a machine-readable manifest with explicit evidence classes and
unresolved edges.  Missing relationships are never filled from adjacency,
matching node counts, or weapon-type similarity.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SCHEMA = "d1_resolved_weapon_manifest/v1"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def evidence(kind: str, source: str, detail: str, **extra) -> dict:
    out = {"kind": kind, "source": source, "detail": detail}
    out.update(extra)
    return out


def load_inventory_rows(paths: list[Path]) -> list[dict]:
    rows = []
    seen = set()
    for path in paths:
        src = load_json(path)
        candidates = src.get("matches") if isinstance(src, dict) and "matches" in src else src.get("rows") if isinstance(src, dict) else src
        if not isinstance(candidates, list):
            raise ValueError(f"{path}: expected matches/rows list")
        for row in candidates:
            h = row.get("inventory_item_hash")
            if not h:
                continue
            h = h.upper()
            if h in seen:
                raise ValueError(f"duplicate inventory item {h} across census inputs")
            seen.add(h)
            q = dict(row)
            q["inventory_item_hash"] = h
            q["__source"] = str(path)
            rows.append(q)
    return rows


def arrangement_index(src: dict) -> dict[int, dict]:
    arr = src.get("arrangements", [])
    out = {}
    for row in arr:
        idx = int(row["arrangement_index"])
        if idx in out:
            raise ValueError(f"duplicate arrangement index {idx}")
        out[idx] = row
    return out


def pattern_index(src: dict) -> dict[int, dict]:
    rows = src.get("patterns", [])
    out = {}
    for row in rows:
        idx = int(row["weapon_pattern_index"])
        if idx in out:
            raise ValueError(f"duplicate weapon pattern index {idx}")
        out[idx] = row
    return out


def resolved_arrangement_entities(row: dict) -> tuple[list[str], list[dict]]:
    entities = []
    unresolved = []
    if "entities" in row:
        for i, rec in enumerate(row.get("entities", [])):
            if isinstance(rec, dict) and rec.get("resolved") and rec.get("entity_data_hash"):
                h = rec["entity_data_hash"].upper()
                if h not in entities:
                    entities.append(h)
            else:
                unresolved.append({"slot": i, "reason": (rec or {}).get("reason") if isinstance(rec, dict) else "entity parent unresolved"})
    else:
        # Arrangement-only reports can still describe the exact parent hashes, but
        # final EntityDataROI needs an asset-dir resolution pass before export.
        for i, ph in enumerate(row.get("entity_parent_hashes", [])):
            unresolved.append({"slot": i, "entity_parent_hash": ph, "reason": "arrangement report lacks resolved EntityDataROI"})
    return entities, unresolved


def choose_shared_context(item: dict, pattern: dict | None, catalog: dict | None) -> tuple[dict | None, list[dict]]:
    if not catalog:
        return None, []
    profiles = catalog.get("profiles", {})
    candidates = []
    inv = item["inventory_item_hash"]
    ia = catalog.get("inventory_assignments", {}).get(inv)
    if ia:
        candidates.append(("exact_inventory_item", ia, f"inventory:{inv}"))
    if pattern:
        pidx = str(pattern.get("weapon_pattern_index"))
        pa = catalog.get("pattern_assignments", {}).get(pidx)
        if pa:
            candidates.append(("weapon_pattern_index", pa, f"pattern:{pidx}"))
        wt = pattern.get("weapon_type_hash")
        if wt:
            wa = catalog.get("weapon_type_assignments", {}).get(wt.upper())
            if wa:
                candidates.append(("weapon_type_hash", wa, f"weapon_type:{wt.upper()}"))
    if not candidates:
        return None, []

    # Highest-specificity assignment wins, but disagreement is a hard error.
    priority = {"exact_inventory_item": 3, "weapon_pattern_index": 2, "weapon_type_hash": 1}
    names = {x[1].get("profile") for x in candidates}
    if len(names) != 1:
        raise ValueError(f"conflicting shared-context assignments for {inv}: {candidates}")
    chosen = max(candidates, key=lambda x: priority[x[0]])
    profile_name = chosen[1]["profile"]
    profile = profiles.get(profile_name)
    if profile is None:
        raise ValueError(f"assignment references missing profile {profile_name}")
    out = {"profile": profile_name, **profile, "assignment_scope": chosen[0], "assignment_reason": chosen[1].get("reason")}
    ev = [evidence("SHARED_CONTEXT_ASSIGNMENT", chosen[2], chosen[1].get("reason", "catalog assignment"), profile=profile_name)]
    for d in profile.get("evidence", []):
        ev.append(evidence("OWNER_RESOURCE", f"profile:{profile_name}", d))
    return out, ev


def build_manifest(item: dict, arrangements: dict[int, dict], patterns: dict[int, dict], catalog: dict | None) -> dict:
    inv = item["inventory_item_hash"]
    ev = [
        evidence("SERIALIZED_REFERENCE", item["__source"],
                 "80A5FFBE InventoryItemHash resolves to this retail inventory definition FileHash",
                 inventory_item_hash=inv, item_file_hash=item.get("item_file_hash")),
    ]
    unresolved = []

    raw_arts = item.get("arrangements", [])
    art_indices = []
    art_classes = []
    for x in raw_arts:
        idx = int(x.get("art_arrangement_index", -1))
        if idx < 0:
            continue
        art_indices.append(idx)
        art_classes.append({"class_hash": x.get("class_hash"), "art_arrangement_index": idx})
        ev.append(evidence("SERIALIZED_REFERENCE", item["__source"],
                           "inventory equippingBlock serializes gearArtArrangementIndex",
                           art_arrangement_index=idx, class_hash=x.get("class_hash")))

    visual_groups = []
    for idx in art_indices:
        ar = arrangements.get(idx)
        if ar is None:
            unresolved.append({"edge": "art_arrangement_index->arrangement", "key": idx, "reason": "arrangement index absent from supplied arrangement report"})
            continue
        ents, unresolved_slots = resolved_arrangement_entities(ar)
        visual_groups.append({
            "art_arrangement_index": idx,
            "source": ar.get("source"),
            "assignment_hashes": ar.get("assignment_hashes", []),
            "entity_parent_hashes": ar.get("entity_parent_hashes", []),
            "entity_data_hashes": ents,
            "unresolved_entity_slots": unresolved_slots,
        })
        ev.append(evidence("ART_ARRANGEMENT", "80A5FFA7+80A7E1DD",
                           "retail art-arrangement row selects assignment/EntityParent chain",
                           art_arrangement_index=idx, entity_data_hashes=ents))
        for q in unresolved_slots:
            unresolved.append({"edge": "arrangement->EntityDataROI", "art_arrangement_index": idx, **q})

    pidx = item.get("weapon_pattern_index")
    pattern = None
    if isinstance(pidx, int) and pidx >= 0:
        pattern = patterns.get(pidx)
        ev.append(evidence("SERIALIZED_REFERENCE", item["__source"],
                           "inventory equippingBlock serializes weaponSandboxPatternIndex",
                           weapon_pattern_index=pidx))
        if pattern is None:
            unresolved.append({"edge": "weapon_pattern_index->pattern", "key": pidx, "reason": "pattern index absent from supplied weapon-pattern report"})
    else:
        unresolved.append({"edge": "inventory->weapon_pattern_index", "reason": "inventory definition has no nonnegative weaponSandboxPatternIndex"})

    internal = None
    if pattern:
        internal = {
            "weapon_pattern_index": pidx,
            "pattern_global_tag_id_hash": pattern.get("pattern_global_tag_id_hash"),
            "weapon_content_group_hash": pattern.get("weapon_content_group_hash"),
            "weapon_type_hash": pattern.get("weapon_type_hash"),
            "pattern_hash": pattern.get("pattern_hash"),
            "sandbox_assignment_found": pattern.get("sandbox_assignment_found"),
            "pattern_entity": pattern.get("entity_relation_hash"),
            "pattern_entity_package_id": pattern.get("entity_relation_package_id"),
            "pattern_entity_file_index": pattern.get("entity_relation_file_index"),
        }
        ev.append(evidence("WEAPON_PATTERN_JOIN", "80A5FFA9+80A7E1DC",
                           "weapon pattern row joins PatternGlobalTagIdHash to sandbox pattern EntityRelation FileHash",
                           weapon_pattern_index=pidx, weapon_type_hash=pattern.get("weapon_type_hash"), pattern_entity=pattern.get("entity_relation_hash")))
        if not pattern.get("sandbox_assignment_found") or not pattern.get("entity_relation_hash"):
            unresolved.append({"edge": "weapon_pattern->sandbox_pattern_entity", "key": pidx, "reason": "sandbox assignment missing"})

    shared, shared_ev = choose_shared_context(item, pattern, catalog)
    ev.extend(shared_ev)
    if shared is None:
        unresolved.append({"edge": "weapon_runtime_context->shared_viewmodel_owner",
                           "reason": "no byte-proven exact inventory/pattern/type context assignment in supplied catalog"})

    status = {
        "inventory_resolved": True,
        "art_arrangement_indices_resolved": bool(art_indices) and all(arrangements.get(x) is not None for x in art_indices),
        "visual_entity_selection_resolved": bool(visual_groups) and all(v["entity_data_hashes"] and not v["unresolved_entity_slots"] for v in visual_groups),
        "weapon_pattern_resolved": pattern is not None and bool(pattern.get("entity_relation_hash")),
        "shared_viewmodel_context_resolved": shared is not None,
    }
    status["resolution_complete_for_current_graph"] = all(status.values())

    return {
        "schema": SCHEMA,
        "asset_kind": "weapon_candidate",
        "inventory_item_hash": inv,
        "inventory_definition": {
            "file_hash": item.get("item_file_hash"),
            "package_id": item.get("item_package_id"),
            "file_index": item.get("item_file_index"),
            "entry_reference": item.get("entry_reference"),
        },
        "equipping": {
            "art_arrangements": art_classes,
            "weapon_pattern_index": pidx,
        },
        "visual": {"arrangements": visual_groups},
        "internal_weapon_pattern": internal,
        "shared_viewmodel": shared,
        "status": status,
        "unresolved_edges": unresolved,
        "evidence": ev,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory-census", action="append", type=Path, required=True,
                    help="full-census JSON from d1_remote_inventory_art_arrangement_find.py; repeatable")
    ap.add_argument("--arrangements", type=Path, required=True,
                    help="JSON from d1_investment_arrangement_probe.py with parent resolution when available")
    ap.add_argument("--weapon-patterns", type=Path, required=True,
                    help="JSON from d1_weapon_pattern_assignment_probe.py")
    ap.add_argument("--shared-context-catalog", type=Path)
    ap.add_argument("--only-with-pattern", action="store_true",
                    help="emit only inventory definitions with a nonnegative weaponSandboxPatternIndex")
    ap.add_argument("--inventory-hash", action="append", default=[], help="optional exact InventoryItemHash filter")
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args()

    items = load_inventory_rows(args.inventory_census)
    arr_src = load_json(args.arrangements)
    pat_src = load_json(args.weapon_patterns)
    catalog = load_json(args.shared_context_catalog) if args.shared_context_catalog else None
    arr_by = arrangement_index(arr_src)
    pat_by = pattern_index(pat_src)
    wanted = {x.upper().replace("0X", "") for x in args.inventory_hash}

    manifests = []
    for item in items:
        if args.only_with_pattern and not (isinstance(item.get("weapon_pattern_index"), int) and item["weapon_pattern_index"] >= 0):
            continue
        if wanted and item["inventory_item_hash"] not in wanted:
            continue
        manifests.append(build_manifest(item, arr_by, pat_by, catalog))

    counters = {
        "manifest_count": len(manifests),
        "weapon_pattern_resolved": sum(m["status"]["weapon_pattern_resolved"] for m in manifests),
        "visual_entity_selection_resolved": sum(m["status"]["visual_entity_selection_resolved"] for m in manifests),
        "shared_viewmodel_context_resolved": sum(m["status"]["shared_viewmodel_context_resolved"] for m in manifests),
        "resolution_complete_for_current_graph": sum(m["status"]["resolution_complete_for_current_graph"] for m in manifests),
    }
    unresolved_by_edge = {}
    for m in manifests:
        for u in m["unresolved_edges"]:
            edge = u["edge"]
            unresolved_by_edge[edge] = unresolved_by_edge.get(edge, 0) + 1

    out = {
        "schema": "d1_resolved_weapon_manifest_set/v1",
        "policy": "Only serialized/table/owner-catalog relationships are joined. Unproven pairings remain explicit unresolved edges.",
        "inputs": {
            "inventory_census": [str(x) for x in args.inventory_census],
            "arrangements": str(args.arrangements),
            "weapon_patterns": str(args.weapon_patterns),
            "shared_context_catalog": str(args.shared_context_catalog) if args.shared_context_catalog else None,
        },
        "summary": {**counters, "unresolved_by_edge": unresolved_by_edge},
        "manifests": manifests,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
