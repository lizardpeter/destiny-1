#!/usr/bin/env python3
"""Derive the exact EntityModel set owned by one D1 activity entity closure.

Input is ``d1_remote_entity_dependency_closure/v1``. Only model nodes reached on
source-typed paths are admitted. Untyped aligned FileHash discovery can therefore
never promote a model into an export plan.

The plan preserves exact incoming typed ownership edges and articulated-entity
skeleton summaries so later geometry/rig/animation assembly can keep provenance.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

NULLS = {"00000000", "FFFFFFFF"}
MODEL_KIND = "s_entity_model"


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--entity-closure", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    src = json.loads(a.entity_closure.read_text(encoding="utf-8"))
    violations: list[str] = []
    if src.get("schema") != "d1_remote_entity_dependency_closure/v1":
        violations.append(f"unexpected_schema:{src.get('schema')!r}")
    if src.get("status") != "D1_ENTITY_DEPENDENCY_CLOSURE_COMPLETE":
        violations.append("entity_dependency_closure_not_complete")
    if src.get("violations"):
        violations.append("entity_dependency_closure_contains_violations")
    if src.get("truncated"):
        violations.append("entity_dependency_closure_truncated")

    nodes = {norm(n.get("tag_hash")): n for n in src.get("nodes", []) if n.get("tag_hash")}
    incoming: dict[str, list[dict]] = defaultdict(list)
    for e in src.get("edges", []):
        if e.get("evidence_class") != "TYPED_EXACT":
            continue
        th = norm(e.get("object"))
        incoming[th].append(e)

    articulated_by_model: dict[str, list[dict]] = defaultdict(list)
    for ent in src.get("articulated_entities", []):
        if not str(ent.get("path_class", "")).startswith("TYPED_EXACT"):
            continue
        for raw in ent.get("embedded_models", []):
            mh = norm(raw)
            if mh in NULLS:
                continue
            articulated_by_model[mh].append(
                {
                    "entity_hash": norm(ent.get("tag_hash")),
                    "entity_depth": ent.get("depth"),
                    "skeletons": ent.get("skeletons", []),
                    "specific_name_string_hashes": ent.get("specific_name_string_hashes", []),
                    "generic_name_tags": ent.get("generic_name_tags", []),
                }
            )

    models = []
    for h, n in sorted(nodes.items()):
        if n.get("kind") != MODEL_KIND:
            continue
        path = str(n.get("path_class", ""))
        if not path.startswith("TYPED_EXACT"):
            continue
        models.append(
            {
                "model": h,
                "package_id": n.get("package_id"),
                "depth": n.get("depth"),
                "path_class": path,
                "entry": n.get("entry"),
                "incoming_typed_edges": incoming.get(h, []),
                "articulated_owners": articulated_by_model.get(h, []),
            }
        )

    model_hashes = [m["model"] for m in models]
    # Any model named by an articulated exact owner must have been reached as an exact
    # model node as well; otherwise the recursive closure was incomplete for our use.
    missing_articulated = sorted(set(articulated_by_model) - set(model_hashes))
    if missing_articulated:
        violations.append("articulated_models_missing_from_typed_model_nodes:" + ",".join(missing_articulated))

    out = {
        "schema": "d1_activity_entity_model_plan/v1",
        "status": "D1_ACTIVITY_ENTITY_MODEL_PLAN_COMPLETE" if not violations else "D1_ACTIVITY_ENTITY_MODEL_PLAN_WITH_VIOLATIONS",
        "source_entity_closure": str(a.entity_closure),
        "source_seed_count": len(src.get("seeds", [])),
        "source_node_count": src.get("node_count"),
        "source_typed_edge_count": src.get("typed_edge_count"),
        "model_count": len(models),
        "models": models,
        "model_hashes": model_hashes,
        "articulated_model_count": len(set(articulated_by_model)),
        "articulated_entity_count": len(src.get("articulated_entities", [])),
        "violations": violations,
        "policy": (
            "Only s_entity_model nodes reached through TYPED_EXACT paths in the exact recursive entity closure "
            "are admitted. UNTYPED_LITERAL discovery never creates model ownership. Articulated owner/skeleton "
            "metadata is carried forward only from source-typed entity resources."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(
        "STATUS", out["status"],
        "MODELS", out["model_count"],
        "ARTICULATED_MODELS", out["articulated_model_count"],
        "ARTICULATED_ENTITIES", out["articulated_entity_count"],
        "VIOLATIONS", len(violations),
    )
    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
