#!/usr/bin/env python3
"""Build a loss-preserving visual plan for source-owned D1 world entities.

Unlike ``d1_world_articulated_entity_plan.py``, this plan does not require a skeleton.
Every placed SEntity with at least one source-parsed ``entity_model`` EntityResource is
a visual candidate. Exact EntityResource -> EntityModel ownership pairs are preserved
individually, so multi-model entities and the same EntityModel under distinct parent
material maps are not collapsed or guessed.

Input placement identity comes from a source-owned runtime placement manifest. Real
WorldIDs may already be deduplicated there; sentinel/no-identity serializations remain
independent placements. This tool does not alter those decisions.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

NULLS = {"00000000", "FFFFFFFF"}
DEP_STATUS = "D1_WORLD_ENTITY_DEPENDENCY_CENSUS_COMPLETE"
PLACEMENT_STATUS = "D1_WORLD_MAP_ENTITY_RUNTIME_PLACEMENTS_COMPLETE"
MODEL_CLASS = "80801AB5"


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def placements_by_entity(doc: dict) -> dict[str, list[dict]]:
    rows = doc.get("unique_world_placements") or []
    out: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        h = norm(row.get("entity_hash"))
        if h not in NULLS:
            out[h].append(row)
    return out


def exact_model_pairs(entity: dict) -> tuple[list[dict], list[str]]:
    pairs = []
    violations = []
    seen = set()
    for row in entity.get("resources", []):
        er = row.get("entity_resource") or {}
        if er.get("semantic_role") != "entity_model":
            continue
        parent = norm(row.get("resource_hash"))
        model = norm(er.get("embedded_model_tag_hash"))
        target = row.get("embedded_model") or {}
        if parent in NULLS or model in NULLS:
            violations.append(f"null_model_pair:{parent}->{model}")
            continue
        if not target.get("class_matches"):
            violations.append(f"model_unavailable_or_class_mismatch:{parent}->{model}")
            continue
        key = (parent, model)
        if key in seen:
            continue
        seen.add(key)
        pairs.append({
            "parent_resource": parent,
            "model": model,
            "parent_resource_index": row.get("index"),
            "parent_resource_record_offset": row.get("record_offset"),
            "model_target": target,
        })
    return pairs, violations


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--placements", type=Path, required=True)
    ap.add_argument("--entity-dependencies", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    p = json.loads(a.placements.read_text(encoding="utf-8"))
    d = json.loads(a.entity_dependencies.read_text(encoding="utf-8"))
    violations: list[str] = []
    if p.get("status") != PLACEMENT_STATUS:
        violations.append(f"placement_status:{p.get('status')!r}")
    if p.get("violations"):
        violations.append("placements_contain_violations")
    if d.get("status") != DEP_STATUS:
        violations.append(f"dependency_status:{d.get('status')!r}")
    if d.get("violations"):
        violations.append("dependencies_contain_violations")
    if d.get("unresolved_dependency_hashes"):
        violations.append("dependencies_still_unresolved")

    by_place = placements_by_entity(p)
    dep_by_entity = {norm(x.get("entity")): x for x in d.get("entities", []) if x.get("entity")}
    missing = sorted(set(by_place) - set(dep_by_entity))
    if missing:
        violations.append("placement_entities_missing_from_dependency_census:" + ",".join(missing))

    candidates = []
    all_pairs = {}
    model_refs = Counter()
    parent_refs = Counter()
    class_counts = Counter()
    for entity_hash in sorted(by_place):
        erow = dep_by_entity.get(entity_hash)
        if erow is None:
            continue
        composition = erow.get("composition") or {}
        class_counts[composition.get("classification", "unknown")] += 1
        pairs, pair_violations = exact_model_pairs(erow)
        if pair_violations:
            violations.extend(f"{entity_hash}:{x}" for x in pair_violations)
        if not pairs:
            continue
        for pair in pairs:
            key = (pair["model"], pair["parent_resource"])
            all_pairs[key] = {
                "model": pair["model"],
                "parent_resource": pair["parent_resource"],
            }
            model_refs[pair["model"]] += len(by_place[entity_hash])
            parent_refs[pair["parent_resource"]] += len(by_place[entity_hash])
        candidates.append({
            "entity": entity_hash,
            "classification": composition.get("classification"),
            "has_skeleton": bool(composition.get("has_skeleton")),
            "has_runtime_rig": bool(composition.get("has_runtime_rig")),
            "bone_counts": composition.get("bone_counts", []),
            "specific_name_hashes": composition.get("specific_name_hashes", []),
            "generic_name_hashes": composition.get("generic_name_hashes", []),
            "model_parent_pairs": pairs,
            "models": sorted({x["model"] for x in pairs}),
            "model_parent_resources": sorted({x["parent_resource"] for x in pairs}),
            "model_parent_pair_count": len(pairs),
            "placement_count": len(by_place[entity_hash]),
            "placements": by_place[entity_hash],
        })

    candidate_entities = {x["entity"] for x in candidates}
    nonvisual_entities = sorted(set(by_place) - candidate_entities)
    visual_runtime_placements = sum(x["placement_count"] for x in candidates)
    visual_model_instances = sum(x["placement_count"] * x["model_parent_pair_count"] for x in candidates)
    pair_rows = [all_pairs[k] for k in sorted(all_pairs)]
    unique_models = sorted({x["model"] for x in pair_rows})
    unique_parents = sorted({x["parent_resource"] for x in pair_rows})

    status = "D1_WORLD_VISUAL_ENTITY_PLAN_COMPLETE" if not violations else "D1_WORLD_VISUAL_ENTITY_PLAN_PARTIAL"
    out = {
        "schema_version": 1,
        "status": status,
        "source_placements": str(a.placements),
        "source_entity_dependencies": str(a.entity_dependencies),
        "placed_unique_entity_count": len(by_place),
        "placed_runtime_placement_count": sum(len(v) for v in by_place.values()),
        "dependency_entity_composition_class_counts": dict(sorted(class_counts.items())),
        "visual_candidate_count": len(candidates),
        "visual_candidate_entities": sorted(candidate_entities),
        "nonvisual_entity_count": len(nonvisual_entities),
        "nonvisual_entities": nonvisual_entities,
        "visual_runtime_placement_count": visual_runtime_placements,
        "visual_model_instance_count": visual_model_instances,
        "unique_model_parent_pair_count": len(pair_rows),
        "unique_model_parent_pairs": pair_rows,
        "unique_model_count": len(unique_models),
        "unique_models": unique_models,
        "unique_model_parent_resource_count": len(unique_parents),
        "unique_model_parent_resources": unique_parents,
        "model_runtime_instance_reference_counts": dict(sorted(model_refs.items())),
        "model_parent_runtime_instance_reference_counts": dict(sorted(parent_refs.items())),
        "candidates": candidates,
        "missing_placement_entities": missing,
        "violations": violations,
        "policy": (
            "Visual ownership is admitted only from a parsed source-owned SEntity EntityResource whose semantic role is "
            "entity_model and whose embedded EntityModel target is exact class 80801AB5. Skeleton presence is recorded but "
            "is not required. Parent-resource/model pairs remain distinct so external material maps are never cross-wired. "
            "Every runtime placement is inherited unchanged from the source placement manifest."
        ),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in (
        "status","placed_unique_entity_count","placed_runtime_placement_count",
        "dependency_entity_composition_class_counts","visual_candidate_count","nonvisual_entity_count",
        "visual_runtime_placement_count","visual_model_instance_count","unique_model_parent_pair_count",
        "unique_model_count","unique_model_parent_resource_count","missing_placement_entities","violations"
    )}, indent=2))
    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
