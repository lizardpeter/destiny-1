#!/usr/bin/env python3
"""Resolve exact D1 activity EntityModel materials through owning EntityResources.

The recursive activity entity closure already records each exact ``s_entity`` resource
and, for model-parent EntityResources, the parser-proven embedded EntityModel. This
adapter turns those ownership records into exact (model, parent EntityResource) pairs
and applies the source-pinned D1 material selection logic from
``d1_world_entity_model_material_bindings.bind_model`` against the remote universal
package corpus.

This closes both direct model materials and external VariantShaderIndex materials.
No model/material proximity, package adjacency, name, or visual similarity is used.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_split_tar_extract import SplitHttpTar
from d1_world_entity_model_material_bindings import bind_model

NULLS = {"00000000", "FFFFFFFF"}


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--entity-closure", type=Path, required=True)
    ap.add_argument("--member-catalog", type=Path, action="append", required=True)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--part-count", type=int, default=10)
    ap.add_argument("--runtime", type=Path, required=True)
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

    # Exact ownership pairs come only from source-parsed s_entity resource records.
    pair_owners: dict[tuple[str, str], set[str]] = defaultdict(set)
    pair_evidence: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for node in src.get("nodes", []):
        if node.get("kind") != "s_entity":
            continue
        if not str(node.get("path_class", "")).startswith("TYPED_EXACT"):
            continue
        eh = norm(node.get("tag_hash"))
        for rr in node.get("resources", []):
            er = rr.get("entity_resource") or {}
            if er.get("semantic_role") != "entity_model":
                continue
            parent = norm(rr.get("resource_hash"))
            model = norm(er.get("embedded_model_tag_hash"))
            if parent in NULLS or model in NULLS:
                violations.append(f"{eh}:entity_model_resource_missing_parent_or_model")
                continue
            key = (model, parent)
            pair_owners[key].add(eh)
            pair_evidence[key].append(
                {
                    "entity": eh,
                    "entity_depth": node.get("depth"),
                    "resource_index": rr.get("resource_index"),
                    "resource_hash": parent,
                    "embedded_model": model,
                    "resolution_status": rr.get("resolution_status"),
                }
            )

    catalogs = load_catalogs(a.member_catalog)
    base = a.base_url.rstrip("/")
    arc = SplitHttpTar(
        [f"{base}/packages.tar.{i:03d}" for i in range(1, a.part_count + 1)],
        retries=6,
        timeout=90,
    )
    c = RemoteCorpus(arc, catalogs, a.runtime)

    bindings = []
    selected = Counter()
    selection_counts = Counter()
    for (model, parent) in sorted(pair_owners):
        row = bind_model(c, model, parent)
        row["owning_entities"] = sorted(pair_owners[(model, parent)])
        row["owning_entity_count"] = len(row["owning_entities"])
        row["ownership_evidence"] = pair_evidence[(model, parent)]
        if row.get("violations"):
            violations.extend(f"{model}/{parent}:{x}" for x in row["violations"])
        for mesh in row.get("meshes", []):
            for part in mesh.get("parts", []):
                selection_counts[part.get("selection", "unknown")] += 1
                sm = part.get("selected_material") or {}
                h = norm(sm.get("hash")) if sm.get("hash") else None
                if h and h not in NULLS:
                    selected[h] += 1
        bindings.append(row)

    out = {
        "schema": "d1_remote_activity_model_material_bindings/v1",
        "status": "D1_REMOTE_ACTIVITY_MODEL_MATERIAL_BINDINGS_COMPLETE" if not violations else "D1_REMOTE_ACTIVITY_MODEL_MATERIAL_BINDINGS_WITH_VIOLATIONS",
        "source_entity_closure": str(a.entity_closure),
        "model_parent_pair_count": len(bindings),
        "validated_pair_count": sum(bool(x.get("validation_ok")) for x in bindings),
        "owning_entity_count": len({e for xs in pair_owners.values() for e in xs}),
        "part_count": sum(int(x.get("part_count", 0)) for x in bindings),
        "external_variant_part_count": sum(int(x.get("external_variant_part_count", 0)) for x in bindings),
        "selection_counts": dict(selection_counts),
        "unique_selected_material_count": len(selected),
        "selected_material_reference_counts": dict(sorted(selected.items())),
        "selected_materials": sorted(selected),
        "bindings": bindings,
        "violations": violations,
        "policy": (
            "Model-parent ownership is admitted only from exact source-parsed s_entity resource records whose "
            "EntityResource semantic role is entity_model and whose embedded model hash is parser-proven. Material "
            "selection then uses the source-pinned D1 external-material map/range semantics. No package adjacency, "
            "developer name, or visual similarity creates a binding."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(
        "STATUS", out["status"],
        "PAIRS", out["model_parent_pair_count"],
        "VALID", out["validated_pair_count"],
        "OWNERS", out["owning_entity_count"],
        "PARTS", out["part_count"],
        "EXTERNAL_VARIANTS", out["external_variant_part_count"],
        "MATERIALS", out["unique_selected_material_count"],
        "VIOLATIONS", len(violations),
    )
    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
