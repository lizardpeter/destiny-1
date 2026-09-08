#!/usr/bin/env python3
"""Export every exact D1 visual world EntityModel/owning-parent pair.

Geometry and retail stage/LOD/material selection are delegated to the already proven
``d1_world_articulated_model_export.export_one`` implementation. The difference is
identity: this adapter keys exports by ``(EntityModel, owning EntityResource)`` rather
than by model alone, so the same model may safely appear under distinct external
material maps in another Activity.

Input must be a completed ``d1_world_visual_entity_plan.py`` report and completed
parent-aware ``d1_world_entity_model_material_bindings.py`` output. No model-parent
cross product is constructed here; only exact pairs already present in the visual plan
are exported.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import d1_tower_map_schema_validate_v5 as v5
from d1_world_articulated_model_export import export_one

PLAN_STATUS = "D1_WORLD_VISUAL_ENTITY_PLAN_COMPLETE"
BIND_STATUS = "D1_WORLD_ENTITY_MODEL_MATERIAL_BINDINGS_COMPLETE"


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def exact_pairs(plan: dict) -> list[tuple[str, str]]:
    declared = plan.get("unique_model_parent_pairs") or []
    pairs = []
    for row in declared:
        m = norm(row.get("model"))
        p = norm(row.get("parent_resource"))
        pairs.append((m, p))
    out = sorted(set(pairs))
    if len(out) != int(plan.get("unique_model_parent_pair_count", -1)):
        raise ValueError("visual plan model-parent pair count mismatch")
    return out


def binding_pairs(doc: dict) -> dict[tuple[str, str], dict]:
    if doc.get("status") != BIND_STATUS:
        raise ValueError(f"material bindings are not complete: {doc.get('status')!r}")
    out = {}
    for row in doc.get("bindings", []):
        key = (norm(row.get("model")), norm(row.get("parent_resource")))
        if key in out:
            raise ValueError(f"duplicate material binding pair {key}")
        if not row.get("validation_ok"):
            raise ValueError(f"material binding pair is not valid {key}")
        out[key] = row
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", type=Path, action="append", required=True)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--visual-plan", type=Path, required=True)
    ap.add_argument("--material-bindings", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    a = ap.parse_args()

    plan = json.loads(a.visual_plan.read_text(encoding="utf-8"))
    if plan.get("status") != PLAN_STATUS or plan.get("violations"):
        raise SystemExit(f"visual plan is not complete: {plan.get('status')!r}")
    pairs = exact_pairs(plan)
    bindings = binding_pairs(json.loads(a.material_bindings.read_text(encoding="utf-8")))
    missing = sorted(set(pairs) - set(bindings))
    extra = sorted(set(bindings) - set(pairs))
    if missing:
        raise SystemExit("missing exact pair bindings: " + repr(missing))
    # Extra bindings are permitted only if the resolver reported source-owned pairs that
    # are not placed in this visual plan; they are not exported and remain provenance.

    corpus = v5.v3.base.Corpus([p.resolve() for p in a.snapshot], a.runtime.resolve())
    a.out_dir.mkdir(parents=True, exist_ok=True)
    work = a.out_dir / ".pair_work"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)

    rows = []
    errors = []
    for model, parent in pairs:
        pair_id = f"{model}__{parent}"
        pair_work = work / pair_id
        try:
            rep = export_one(corpus, model, bindings[(model, parent)], pair_work)
            src_glb = pair_work / f"{model}.glb"
            src_json = pair_work / f"{model}.json"
            dst_glb = a.out_dir / f"{pair_id}.glb"
            dst_json = a.out_dir / f"{pair_id}.json"
            shutil.move(str(src_glb), str(dst_glb))
            rep["schema_version"] = 2
            rep["status"] = "D1_WORLD_VISUAL_MODEL_PAIR_EXPORT_COMPLETE"
            rep["parent_resource"] = parent
            rep["pair_id"] = pair_id
            rep["glb"] = str(dst_glb)
            rep["glb_bytes"] = dst_glb.stat().st_size
            rep["selection_policy"] = (
                rep.get("selection_policy", "") + " Owning EntityResource identity is part of the export key; "
                "the same EntityModel under a different parent material map is exported as a distinct pair."
            ).strip()
            dst_json.write_text(json.dumps(rep, indent=2) + "\n", encoding="utf-8")
            if src_json.exists():
                src_json.unlink()
            rows.append(rep)
        except Exception as ex:
            errors.append({"model": model, "parent_resource": parent, "error": repr(ex)})

    if work.exists():
        shutil.rmtree(work)
    active = sorted({h for row in rows for h in row.get("active_materials", [])})
    out = {
        "schema_version": 1,
        "status": (
            "D1_WORLD_VISUAL_MODEL_PAIR_SET_COMPLETE"
            if not errors and len(rows) == len(pairs)
            else "D1_WORLD_VISUAL_MODEL_PAIR_SET_PARTIAL"
        ),
        "source_visual_plan": str(a.visual_plan),
        "source_material_bindings": str(a.material_bindings),
        "requested_pair_count": len(pairs),
        "exported_pair_count": len(rows),
        "unique_model_count": len({m for m, _p in pairs}),
        "unique_parent_resource_count": len({p for _m, p in pairs}),
        "geometry_count": sum(int(r.get("geometry_count", 0)) for r in rows),
        "triangle_count": sum(int(r.get("triangle_count", 0)) for r in rows),
        "active_material_count": len(active),
        "active_materials": active,
        "pairs": rows,
        "unplaced_extra_binding_pairs": [list(x) for x in extra],
        "errors": errors,
        "policy": (
            "Only exact model-parent pairs from the completed visual entity plan are exported. Geometry/stage/LOD selection "
            "and each selected Material come from the established source-driven articulated model exporter and the exact "
            "owning-parent binding. Pair identity prevents external material maps from being cross-wired when models are reused."
        ),
    }
    a.summary.parent.mkdir(parents=True, exist_ok=True)
    a.summary.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in (
        "status","requested_pair_count","exported_pair_count","unique_model_count",
        "unique_parent_resource_count","geometry_count","triangle_count","active_material_count","errors"
    )}, indent=2))
    return 0 if out["status"] == "D1_WORLD_VISUAL_MODEL_PAIR_SET_COMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
