#!/usr/bin/env python3
"""Class-correct Tower dynamic/activity adapter for the generic D1 asset target.

Tower has one 8080052E map/world root plus multiple 80800616 scenario roots.  The
base fresh target historically (and incorrectly) fed the map root to the scenario
parser.  This adapter changes only Tower seed discovery:

* read the current activity index produced by the caller;
* select current 80800616 rows whose authored aliases identify city_tower scenario
  clients (including ambient_city_tower);
* run the generic activity graph + typed dependency-seed tools independently for
  every selected scenario;
* union only their exact closure_seed_hashes;
* continue through the unchanged shared entity/model/material/texture/animation
  pipeline in d1_fresh_activity_asset_target.py.

Authored scenario names select the Tower activity group only.  They never create an
asset ownership edge; all downstream roots come from source-typed scenario graphs.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import d1_fresh_activity_asset_target as base

SCENARIO_CLASS = "80800616"


def _norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def _is_tower_scenario(row: dict) -> bool:
    if _norm(row.get("class_hash_canonical", "")) != SCENARIO_CLASS:
        return False
    names = []
    if row.get("name"):
        names.append(str(row["name"]))
    names.extend(str(x) for x in (row.get("aliases") or []) if x)
    for raw in names:
        n = raw.lower()
        if not n.endswith(":scenario_client"):
            continue
        if n.startswith("city_tower_") or n == "ambient_city_tower:scenario_client":
            return True
    return False


def tower_seed_target(a, out: Path):
    if a.target != "tower-activity":
        return _ORIGINAL_SEED_TARGET(a, out)

    idx_path = Path(os.environ.get("D1_ACTIVITY_INDEX", ""))
    if not idx_path.is_file():
        raise ValueError("D1_ACTIVITY_INDEX must point to the current-run activity index")
    idx = json.loads(idx_path.read_text(encoding="utf-8"))
    if idx.get("status") != "D1_REMOTE_ACTIVITY_INDEX_COMPLETE" or idx.get("violations"):
        raise ValueError("current activity index is not exact")

    selected = [x for x in idx.get("current_unknown_activities", []) if _is_tower_scenario(x)]
    selected.sort(key=lambda x: x["tag_hash"])
    if not selected:
        raise ValueError("current activity index contains no Tower 80800616 scenario roots")

    common = [
        "--member-catalog", str(a.member_catalog),
        "--base-url", a.base_url,
        "--part-count", str(a.part_count),
        "--runtime", str(a.runtime),
    ]
    scenario_root = out / "tower_scenarios"
    scenario_root.mkdir(parents=True, exist_ok=True)
    union = []
    seen = set()
    scenarios = []

    for row in selected:
        h = _norm(row["tag_hash"])
        name = str(row.get("name") or (row.get("aliases") or [h])[0])
        graph = scenario_root / h / "graph"
        graph.mkdir(parents=True, exist_ok=True)
        base.run([
            base.tool("d1_remote_activity_graph_extract.py"),
            "--activity-hash", h,
            "--activity-name", name,
            "--activity-class", SCENARIO_CLASS,
            *common,
            "--output-dir", str(graph),
        ], out / "logs" / f"tower_scenario_{h}_graph.txt")
        manifest = base.load(graph / "activity_graph_manifest.json")
        if manifest.get("status") != "D1_REMOTE_ACTIVITY_GRAPH_EXACT":
            raise ValueError(f"Tower scenario {h} graph is not exact")

        seed_path = scenario_root / h / "dependency_seeds.json"
        base.run([
            base.tool("d1_activity_asset_dependency_seeds.py"),
            "--graph-dir", str(graph), "-o", str(seed_path),
        ], out / "logs" / f"tower_scenario_{h}_seeds.txt")
        seeds = base.load(seed_path)
        if seeds.get("status") != "D1_ACTIVITY_ASSET_DEPENDENCY_SEEDS_EXACT":
            raise ValueError(f"Tower scenario {h} seed set is not exact: {seeds.get('violations')}")
        roots = [_norm(x) for x in seeds.get("closure_seed_hashes", [])]
        for x in roots:
            if x not in seen:
                seen.add(x)
                union.append(x)
        scenarios.append({
            "activity_hash": h,
            "activity_name": name,
            "aliases": row.get("aliases") or [],
            "source_package_id": row.get("source_package_id"),
            "graph_counts": manifest.get("counts"),
            "seed_group_counts": seeds.get("counts"),
            "closure_seed_count": len(roots),
        })

    if not union:
        raise ValueError("Tower scenario group yielded zero typed closure seeds")
    evidence = {
        "seed_mode": "current_index_multi_scenario_typed_asset_union",
        "activity_index": str(idx_path),
        "scenario_class": SCENARIO_CLASS,
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
        "root_count": len(union),
        "roots": union,
        "policy": (
            "Tower scenario membership is selected only among current named 80800616 roots. "
            "Authored names group scenarios but never create asset ownership. Every extraction root "
            "is emitted by the generic exact activity graph and typed dependency-seed parser. The "
            "8080052E Tower map root is intentionally excluded from the scenario parser and remains "
            "the authority of the independent static/world pipeline."
        ),
    }
    (out / "seed_evidence.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print("TOWER_SCENARIOS", len(scenarios), "TYPED_UNION_ROOTS", len(union), flush=True)
    for x in scenarios:
        print("TOWER_SCENARIO", x["activity_hash"], x["activity_name"], "SEEDS", x["closure_seed_count"], flush=True)
    return union, evidence


_ORIGINAL_SEED_TARGET = base.seed_target
base.seed_target = tower_seed_target

if __name__ == "__main__":
    raise SystemExit(base.main())
