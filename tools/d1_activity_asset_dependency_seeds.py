#!/usr/bin/env python3
"""Build exact asset/dependency seed sets from one extracted D1 scenario activity graph.

This is intentionally activity-category agnostic. It consumes the exact component
reports emitted by d1_remote_activity_graph_extract.py and separates:

* placement EntitySK roots serialized by Activity map data;
* scripted EntitySK roots, including scripted-only entities with no runtime WorldID row;
* EntityResource owners reached through exact F603 edges;
* parser-proven typed targets such as embedded models, generic-name tags,
  scripted tables and dialogue entities;
* structural activity context (resource parents, S6E stages, map data tables,
  and F603s), which is preserved but is not mislabeled as a visual asset.

The resulting ``closure_seed_hashes`` are safe inputs to the recursive
``d1_remote_entity_dependency_closure.py`` walker. No developer string, activity
name, package filename, proximity, or visual resemblance creates an ownership edge.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

NULLS = {"00000000", "FFFFFFFF"}


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def good_hash(v: object) -> str | None:
    if v is None:
        return None
    h = norm(v)
    if h in NULLS:
        return None
    try:
        int(h, 16)
    except ValueError:
        return None
    return h


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph-dir", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    root = a.graph_dir
    manifest = load(root / "activity_graph_manifest.json")
    placements = load(root / "activity_placements.json")
    f603 = load(root / "activity_f603_resources.json")
    scripted = load(root / "activity_scripted_entities.json")

    violations: list[str] = []
    if manifest.get("status") != "D1_REMOTE_ACTIVITY_GRAPH_EXACT":
        violations.append("activity_graph_manifest_not_exact")
    if placements.get("status") != "D1_REMOTE_ACTIVITY_PLACEMENTS_COMPLETE" or placements.get("violations"):
        violations.append("activity_placements_not_exact")
    if f603.get("status") != "D1_REMOTE_ACTIVITY_F603_RESOURCE_CENSUS_EXACT" or f603.get("violations"):
        violations.append("activity_f603_census_not_exact")
    if scripted.get("status") != "D1_REMOTE_ACTIVITY_SCRIPTED_ENTITY_CENSUS_COMPLETE" or scripted.get("violations"):
        violations.append("activity_scripted_entity_census_not_exact")

    identities = []
    for d, key in ((manifest, "activity"), (placements, "activity"), (f603, "activity"), (scripted, "activity")):
        r = d.get(key) or {}
        identities.append((good_hash(r.get("tag_hash")), r.get("name"), good_hash(r.get("class_hash"))))
    base = identities[0]
    for i, ident in enumerate(identities[1:], 1):
        # Component tools can omit a name/class field, but any present value must agree.
        if ident[0] != base[0]:
            violations.append(f"activity_hash_mismatch_component_{i}")
        if ident[1] is not None and base[1] is not None and ident[1] != base[1]:
            violations.append(f"activity_name_mismatch_component_{i}")
        if ident[2] is not None and base[2] is not None and ident[2] != base[2]:
            violations.append(f"activity_class_mismatch_component_{i}")

    evidence: list[dict] = []
    groups: dict[str, set[str]] = defaultdict(set)

    def add(group: str, value: object, source: str, predicate: str, subject: object | None = None, attrs: dict | None = None):
        h = good_hash(value)
        if h is None:
            return None
        groups[group].add(h)
        row = {
            "source_component": source,
            "predicate": predicate,
            "object": h,
            "evidence_class": "TYPED_EXACT",
        }
        sh = good_hash(subject)
        if sh is not None:
            row["subject"] = sh
        if attrs:
            row["attrs"] = attrs
        evidence.append(row)
        return h

    # Runtime placement roots. Sentinel WorldIDs remain individual placements in the
    # source report, but the entity identity itself is still an exact EntitySK FileHash.
    placement_entities = placements.get("unique_entity_hashes")
    if placement_entities is None:
        placement_entities = list((placements.get("runtime_entity_counts") or {}).keys())
    for value in placement_entities:
        h = add("placement_entities", value, "activity_placements", "ACTIVITY_PLACES_ENTITY", base[0])
        if h:
            groups["s_entities"].add(h)

    # Scripted tables can contain entities not represented by an ordinary runtime
    # WorldID placement. Preserve the scripted population independently and then union it
    # into s_entities for recursive dependency closure.
    for value, n in (scripted.get("scripted_entity_hash_counts") or {}).items():
        h = add("scripted_entities", value, "activity_scripted_entities", "SCRIPTED_TABLE_REFERENCES_ENTITY", None, {"serialized_record_count": n})
        if h:
            groups["s_entities"].add(h)
    groups["scripted_only_entities"] = groups["scripted_entities"] - groups["placement_entities"]

    for h in scripted.get("unique_scripted_tables", []):
        add("scripted_tables", h, "activity_scripted_entities", "ACTIVITY_OWNS_SCRIPTED_TABLE", base[0])

    # Every F603 -> EntityResource edge is source-pinned. Parser-proven target fields
    # are promoted separately; unresolved class pairs remain only EntityResource seeds.
    for r in f603.get("rows", []):
        fh = good_hash(r.get("f603"))
        erh = good_hash(r.get("entity_resource_hash"))
        if fh:
            add("f603_resources", fh, "activity_f603_resources", "ACTIVITY_REFERENCES_F603", base[0])
        if erh:
            add("entity_resources", erh, "activity_f603_resources", "F603_ENTITY_RESOURCE", fh)
        typed = (
            ("embedded_models", "embedded_model_tag_hash", "ENTITY_RESOURCE_MODEL"),
            ("generic_name_tags", "entity_name_tag_hash", "ENTITY_RESOURCE_GENERIC_NAME"),
            ("scripted_tables", "scripted_entity_table_tag_hash", "ENTITY_RESOURCE_SCRIPTED_TABLE"),
            ("dialogue_entities", "dialogue_entity_tag_hash", "ENTITY_RESOURCE_DIALOGUE_ENTITY"),
        )
        for group, key, pred in typed:
            add(group, r.get(key), "activity_f603_resources", pred, erh)

    # Preserve the complete activity structural context without pretending these tags
    # are model/material/audio assets.
    for h in placements.get("unique_resource_parents", []):
        add("resource_parents", h, "activity_placements", "ACTIVITY_RESOURCE_PARENT", base[0])
    for h in placements.get("unique_s6e_resources", []):
        add("s6e_resources", h, "activity_placements", "ACTIVITY_S6E_RESOURCE", base[0])
    for h in placements.get("unique_map_data_tables", []):
        add("map_data_tables", h, "activity_placements", "ACTIVITY_MAP_DATA_TABLE", base[0])
    for h in placements.get("unique_f603_entity_resources", []):
        add("f603_resources", h, "activity_placements", "ACTIVITY_F603_RESOURCE", base[0])

    # Recursive entity closure starts from actual entities and source-typed resources.
    # Structural activity carriers are intentionally excluded because their own schemas
    # are already handled by the activity graph extractor, not the entity walker.
    closure_groups = (
        "s_entities",
        "entity_resources",
        "embedded_models",
        "generic_name_tags",
        "scripted_tables",
        "dialogue_entities",
    )
    closure = sorted(set().union(*(groups[g] for g in closure_groups)))

    out = {
        "schema": "d1_activity_asset_dependency_seeds/v1",
        "status": "D1_ACTIVITY_ASSET_DEPENDENCY_SEEDS_EXACT" if not violations else "D1_ACTIVITY_ASSET_DEPENDENCY_SEEDS_WITH_VIOLATIONS",
        "activity": {
            "tag_hash": base[0],
            "name": base[1],
            "class_hash": base[2],
        },
        "counts": {k: len(v) for k, v in sorted(groups.items())},
        "seed_groups": {k: sorted(v) for k, v in sorted(groups.items())},
        "closure_seed_count": len(closure),
        "closure_seed_hashes": closure,
        "exact_edge_evidence": evidence,
        "violations": violations,
        "policy": (
            "Asset/dependency seeds are admitted only from exact activity placements, exact scripted records, "
            "literal F603->EntityResource edges, or parser-proven typed EntityResource targets. Placement entities "
            "and scripted entities remain independently enumerable; their union is the s_entity closure population. "
            "Structural activity carriers are preserved separately. No activity category, developer name, package "
            "filename, proximity, model shape, or visual resemblance creates an ownership edge."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print("STATUS", out["status"], "ACTIVITY", base[0], "GROUPS", out["counts"], "CLOSURE_SEEDS", len(closure), "VIOLATIONS", len(violations))
    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
