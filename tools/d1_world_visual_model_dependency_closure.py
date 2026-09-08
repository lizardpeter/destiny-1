#!/usr/bin/env python3
"""Close EntityModel stream/backing dependencies for a D1 all-visual world plan.

``d1_world_entity_model_visual_dependency_closure.py`` already implements the exact
indexed EntityModel -> vertex/index header -> backing buffer + inline Material closure,
but its historical input contract is the table-scoped/common model plan. This adapter
changes only that plan boundary: it validates a completed
``d1_world_visual_entity_plan.py`` report, projects its exact ``unique_models`` set into
the existing model-plan schema, runs the proven closer, and restores provenance to the
original all-visual plan in the final report.

No model, material, package, or stream dependency is discovered by this adapter.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPECTED = "D1_WORLD_VISUAL_ENTITY_PLAN_COMPLETE"


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", type=Path, required=True)
    ap.add_argument("--package-list", type=Path, required=True)
    ap.add_argument("--visual-plan", type=Path, required=True)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--package-dir", type=Path, required=True)
    ap.add_argument("--work-dir", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--max-passes", type=int, default=8)
    a = ap.parse_args()

    src = json.loads(a.visual_plan.read_text(encoding="utf-8"))
    if src.get("status") != EXPECTED:
        raise SystemExit(f"visual plan is not complete: {src.get('status')!r}")
    if src.get("violations"):
        raise SystemExit("visual plan contains violations")
    models = sorted({norm(x) for x in src.get("unique_models", [])})
    if len(models) != int(src.get("unique_model_count", -1)) or not models:
        raise SystemExit("visual plan unique model set/count mismatch or empty")

    a.work_dir.mkdir(parents=True, exist_ok=True)
    a.report.parent.mkdir(parents=True, exist_ok=True)
    compat = a.work_dir / "visual_model_plan_compat.json"
    compat_doc = {
        "schema_version": 1,
        "status": "D1_WORLD_COMMON_MODEL_PLAN_COMPLETE",
        "source_census": str(a.visual_plan),
        "source_census_status": src.get("status"),
        "source_record_count": src.get("visual_model_instance_count"),
        "resolved_model_reference_records": src.get("visual_model_instance_count"),
        "unique_model_count": len(models),
        "models": models,
        "model_reference_histogram": src.get("model_runtime_instance_reference_counts", {}),
        "models_by_map_data_table": {},
        "models_by_static_map_data": {},
        "unresolved_records": [],
        "violations": [],
        "policy": (
            "Compatibility projection only. Model membership is copied exactly from the completed all-visual entity plan; "
            "this document performs no discovery or selection."
        ),
    }
    compat.write_text(json.dumps(compat_doc, indent=2) + "\n", encoding="utf-8")

    raw_report = a.work_dir / "visual_model_dependency_closure.raw.json"
    stdout = a.work_dir / "visual_model_dependency_closure.stdout.txt"
    cmd = [
        sys.executable,
        str(HERE / "d1_world_entity_model_visual_dependency_closure.py"),
        "--index", str(a.index),
        "--package-list", str(a.package_list),
        "--model-plan", str(compat),
        "--runtime", str(a.runtime),
        "--package-dir", str(a.package_dir),
        "--work-dir", str(a.work_dir / "indexed_model_closure"),
        "--report", str(raw_report),
        "--max-passes", str(a.max_passes),
    ]
    cp = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout.write_text(cp.stdout, encoding="utf-8")
    if not raw_report.exists():
        raise SystemExit(f"underlying model dependency closer emitted no report rc={cp.returncode}; see {stdout}")
    raw = json.loads(raw_report.read_text(encoding="utf-8"))

    out = dict(raw)
    out["schema_version"] = 2
    out["status"] = (
        "D1_WORLD_VISUAL_MODEL_DEPENDENCY_CLOSURE_COMPLETE"
        if raw.get("status") == "D1_WORLD_ENTITY_MODEL_VISUAL_DEPENDENCY_CLOSURE_COMPLETE"
        else "D1_WORLD_VISUAL_MODEL_DEPENDENCY_CLOSURE_PARTIAL"
    )
    out["source_visual_plan"] = str(a.visual_plan)
    out["source_visual_plan_status"] = src.get("status")
    out["compatibility_model_plan"] = str(compat)
    out["underlying_closure_status"] = raw.get("status")
    out["visual_candidate_count"] = src.get("visual_candidate_count")
    out["visual_runtime_placement_count"] = src.get("visual_runtime_placement_count")
    out["visual_model_instance_count"] = src.get("visual_model_instance_count")
    out["unique_model_parent_pair_count"] = src.get("unique_model_parent_pair_count")
    out["policy"] = (
        "EntityModel membership is copied losslessly from the completed all-visual world plan. Stream headers, backing "
        "buffers and inline Materials are then closed only by the established indexed EntityModel dependency closer. "
        "The compatibility plan performs no semantic discovery."
    )
    a.report.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({k: out.get(k) for k in (
        "status","underlying_closure_status","model_count","visual_candidate_count",
        "visual_runtime_placement_count","visual_model_instance_count",
        "unique_model_parent_pair_count","final_package_ids","stop_reason"
    )}, indent=2))
    return 0 if out["status"] == "D1_WORLD_VISUAL_MODEL_DEPENDENCY_CLOSURE_COMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
