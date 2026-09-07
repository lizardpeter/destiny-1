#!/usr/bin/env python3
"""Build the exact selected Material plan for a closed D1 activity visual graph.

Inputs:
- activity model visual dependency closure: exact inline Material identities plus
  external-variant parts that intentionally remain unresolved at the model-only layer;
- activity model material bindings: exact owning EntityResource variant selection.

The output is the union of non-null inline Materials and non-null owner-selected
Materials. Explicit null Material sentinels are source-proven non-renderable parts and
never become material dependencies. External variant models without an exact owning
binding remain an explicit frontier rather than being guessed.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

NULLS = {"00000000", "FFFFFFFF"}


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--visual-closure", type=Path, required=True)
    ap.add_argument("--material-bindings", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    visual = json.loads(a.visual_closure.read_text(encoding="utf-8"))
    bindings = json.loads(a.material_bindings.read_text(encoding="utf-8"))
    violations: list[str] = []

    if visual.get("schema") != "d1_remote_activity_model_visual_dependency_closure/v1":
        violations.append(f"unexpected_visual_schema:{visual.get('schema')!r}")
    if visual.get("status") != "D1_REMOTE_ACTIVITY_MODEL_VISUAL_DEPENDENCY_CLOSURE_COMPLETE":
        violations.append("visual_closure_not_complete")
    if visual.get("violations"):
        violations.append("visual_closure_contains_violations")

    if bindings.get("schema") not in {
        "d1_remote_activity_model_material_bindings/v1",
        "d1_remote_activity_model_material_bindings/v2",
    }:
        violations.append(f"unexpected_material_binding_schema:{bindings.get('schema')!r}")
    if bindings.get("status") != "D1_REMOTE_ACTIVITY_MODEL_MATERIAL_BINDINGS_COMPLETE":
        violations.append("material_bindings_not_complete")
    if bindings.get("violations"):
        violations.append("material_bindings_contains_violations")
    if bindings.get("validated_pair_count") != bindings.get("model_parent_pair_count"):
        violations.append("not_all_model_parent_pairs_validated")

    inline = {
        norm(x)
        for x in visual.get("inline_materials", [])
        if x and norm(x) not in NULLS
    }
    owner_selected = {
        norm(x)
        for x in bindings.get("selected_materials", [])
        if x and norm(x) not in NULLS
    }
    union = sorted(inline | owner_selected)

    external_models = {
        norm(x.get("model"))
        for x in visual.get("external_variant_parts", [])
        if x.get("model") and norm(x.get("model")) not in NULLS
    }
    bound_models = {
        norm(x.get("model"))
        for x in bindings.get("bindings", [])
        if x.get("model") and norm(x.get("model")) not in NULLS
    }
    unresolved_models = sorted(external_models - bound_models)

    declared_inline = int(visual.get("inline_material_count", len(inline)))
    if declared_inline != len(inline):
        violations.append(f"inline_material_count_mismatch:{declared_inline}!={len(inline)}")
    declared_selected = int(bindings.get("unique_selected_material_count", len(owner_selected)))
    if declared_selected != len(owner_selected):
        violations.append(
            f"owner_selected_material_count_mismatch:{declared_selected}!={len(owner_selected)}"
        )

    status = (
        "D1_ACTIVITY_SELECTED_MATERIAL_PLAN_COMPLETE"
        if not violations and not unresolved_models
        else "D1_ACTIVITY_SELECTED_MATERIAL_PLAN_PARTIAL"
    )
    out = {
        "schema": "d1_activity_selected_material_plan/v1",
        "status": status,
        "source_visual_closure": str(a.visual_closure),
        "source_material_bindings": str(a.material_bindings),
        "inline_material_count": len(inline),
        "owner_selected_material_count": len(owner_selected),
        "unique_material_count": len(union),
        "materials": union,
        "visual_external_variant_part_count": int(visual.get("external_variant_part_count", 0)),
        "owner_external_variant_part_count": int(bindings.get("external_variant_part_count", 0)),
        "explicit_null_material_part_count": int(bindings.get("explicit_null_material_part_count", 0)),
        "renderable_material_part_count": int(bindings.get("renderable_material_part_count", 0)),
        "unresolved_external_variant_models": unresolved_models,
        "violations": violations,
        "policy": (
            "The plan is the exact union of non-null inline model Materials and non-null Materials selected through "
            "source-owned EntityResource variant maps. 00000000/FFFFFFFF Material sentinels are retained upstream as "
            "explicit non-renderable parts and never promoted as dependencies. External variants without exact owner "
            "bindings remain unresolved; no material identity is guessed from model order, package adjacency, names, "
            "or visual similarity."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(
        "STATUS", out["status"],
        "INLINE", out["inline_material_count"],
        "OWNER_SELECTED", out["owner_selected_material_count"],
        "UNIQUE", out["unique_material_count"],
        "NULL_PARTS", out["explicit_null_material_part_count"],
        "UNRESOLVED_VARIANT_MODELS", len(unresolved_models),
        "VIOLATIONS", len(violations),
    )
    return 0 if status == "D1_ACTIVITY_SELECTED_MATERIAL_PLAN_COMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
