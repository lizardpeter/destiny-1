#!/usr/bin/env python3
"""Instantiate every exact D1 visual EntityModel/parent pair in world space.

Input is ``d1_world_visual_entity_plan.py`` plus pair-keyed GLBs from
``d1_world_visual_model_export.py``. Each candidate may own one or multiple exact
model-parent pairs; every pair is instantiated at every inherited source placement.
Real WorldIDs remain unique identities. Retail sentinel WorldIDs are handled by the
same source-reference identity rule as ``d1_world_articulated_scene_v2.py``.

No model, parent, transform, scale, WorldID, or placement is inferred.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import trimesh

from d1_world_articulated_scene_v2 import A, d1_row_matrix, placement_identity

PLAN_STATUS = "D1_WORLD_VISUAL_ENTITY_PLAN_COMPLETE"


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def pair_id(model: object, parent: object) -> str:
    return f"{norm(model)}__{norm(parent)}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--visual-plan", type=Path, required=True)
    ap.add_argument("--model-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    a = ap.parse_args()

    plan = json.loads(a.visual_plan.read_text(encoding="utf-8"))
    if plan.get("status") != PLAN_STATUS or plan.get("violations"):
        raise SystemExit(f"visual plan is not complete: {plan.get('status')!r}")

    declared_pairs = {
        pair_id(x.get("model"), x.get("parent_resource")):
        (norm(x.get("model")), norm(x.get("parent_resource")))
        for x in plan.get("unique_model_parent_pairs", [])
    }
    if len(declared_pairs) != int(plan.get("unique_model_parent_pair_count", -1)):
        raise SystemExit("visual plan model-parent pair count mismatch")

    pair_sources = {}
    missing = []
    for pid, (model, parent) in sorted(declared_pairs.items()):
        path = a.model_dir / f"{pid}.glb"
        if not path.exists():
            missing.append(pid)
            continue
        src = trimesh.load(path, force="scene", process=False)
        if not src.geometry:
            raise SystemExit(f"{pid}: pair GLB contains no geometry")
        pair_sources[pid] = {
            "model": model,
            "parent_resource": parent,
            "path": path,
            "sha256": sha256(path),
            "geometries": {name: geom.copy() for name, geom in src.geometry.items()},
        }
    if missing:
        raise SystemExit("missing visual pair GLBs: " + ",".join(missing))

    scene = trimesh.Scene()
    geom_map = {}
    for pid, src in sorted(pair_sources.items()):
        names = []
        for gi, (old_name, geom) in enumerate(src["geometries"].items()):
            name = f"{pid}__g{gi:03d}__{old_name}"
            scene.geometry[name] = geom
            names.append(name)
        geom_map[pid] = names

    placement_rows = []
    used_real_world_ids: set[str] = set()
    used_placement_keys: set[str] = set()
    pair_instance_count = 0
    node_count = 0
    sentinel_count = 0

    for candidate in plan.get("candidates", []):
        entity = norm(candidate.get("entity"))
        pairs = candidate.get("model_parent_pairs") or []
        if not pairs:
            raise SystemExit(f"{entity}: visual candidate has no model-parent pair")
        pair_keys = []
        for pair in pairs:
            pid = pair_id(pair.get("model"), pair.get("parent_resource"))
            if pid not in pair_sources:
                raise SystemExit(f"{entity}: undeclared/unavailable pair {pid}")
            pair_keys.append(pid)

        for placement in candidate.get("placements", []):
            try:
                wid, identity_key, identity_kind, sentinel_source = placement_identity(
                    placement, used_real_world_ids, used_placement_keys
                )
            except ValueError as ex:
                raise SystemExit(f"{entity}: {ex}") from ex
            if wid == "FFFFFFFFFFFFFFFF":
                sentinel_count += 1
            M = d1_row_matrix(placement["rotation"], placement["translation"])
            N = A @ M.T
            instantiated_pairs = []
            for pid in pair_keys:
                src = pair_sources[pid]
                pair_nodes = []
                pair_instance_count += 1
                safe_identity = identity_key.replace(":", "_").replace("/", "_")
                for gi, geom_name in enumerate(geom_map[pid]):
                    node_name = f"D1_VIS_{safe_identity}_{entity}_{pid}_g{gi:03d}"
                    scene.graph.update(
                        frame_to=node_name,
                        matrix=N,
                        geometry=geom_name,
                        metadata={
                            "d1PlacementIdentity": identity_key,
                            "d1PlacementIdentityKind": identity_kind,
                            "d1WorldID": wid,
                            "d1WorldIDIsSentinel": wid == "FFFFFFFFFFFFFFFF",
                            "d1Entity": entity,
                            "d1Model": src["model"],
                            "d1ModelParentResource": src["parent_resource"],
                            "d1PairId": pid,
                            "d1RotationXYZW": placement["rotation"],
                            "d1Translation": placement["translation"],
                            "d1SerializedSourceIdentity": sentinel_source,
                        },
                    )
                    pair_nodes.append(node_name)
                    node_count += 1
                instantiated_pairs.append({
                    "pair_id": pid,
                    "model": src["model"],
                    "parent_resource": src["parent_resource"],
                    "node_count": len(pair_nodes),
                    "nodes": pair_nodes,
                })
            placement_rows.append({
                "placement_identity": identity_key,
                "placement_identity_kind": identity_kind,
                "world_id": placement.get("world_id"),
                "world_id_hex": wid,
                "world_id_is_sentinel": wid == "FFFFFFFFFFFFFFFF",
                "sentinel_serialized_source_identity": sentinel_source,
                "entity": entity,
                "rotation_xyzw": placement["rotation"],
                "translation": placement["translation"],
                "serialized_reference_count": placement.get("serialized_reference_count"),
                "duplicate_serialization_count": placement.get("duplicate_serialization_count"),
                "source_references": placement.get("source_references", []),
                "d1_row_matrix": M.tolist(),
                "gltf_matrix": N.tolist(),
                "pair_count": len(instantiated_pairs),
                "pairs": instantiated_pairs,
            })

    expected_placements = int(plan.get("visual_runtime_placement_count", -1))
    expected_pair_instances = int(plan.get("visual_model_instance_count", -1))
    if len(placement_rows) != expected_placements:
        raise SystemExit(f"visual placement coverage mismatch {len(placement_rows)} != {expected_placements}")
    if pair_instance_count != expected_pair_instances:
        raise SystemExit(f"visual pair instance coverage mismatch {pair_instance_count} != {expected_pair_instances}")

    a.out.parent.mkdir(parents=True, exist_ok=True)
    scene.export(a.out)
    report = {
        "schema_version": 1,
        "status": "D1_WORLD_VISUAL_ENTITY_SCENE_COMPLETE",
        "visual_candidate_count": plan.get("visual_candidate_count"),
        "runtime_placement_count": len(placement_rows),
        "real_world_id_placement_count": len(used_real_world_ids),
        "sentinel_world_id_placement_count": sentinel_count,
        "unique_placement_identity_count": len(used_placement_keys),
        "model_parent_pair_count": len(declared_pairs),
        "model_pair_instance_count": pair_instance_count,
        "unique_model_count": len({x[0] for x in declared_pairs.values()}),
        "scene_geometry_variants": len(scene.geometry),
        "scene_geometry_nodes": node_count,
        "bounds": scene.bounds.tolist() if scene.bounds is not None else None,
        "glb": str(a.out),
        "glb_bytes": a.out.stat().st_size,
        "glb_sha256": sha256(a.out),
        "pair_sources": {
            pid: {
                "model": src["model"],
                "parent_resource": src["parent_resource"],
                "path": str(src["path"]),
                "sha256": src["sha256"],
                "geometry_count": len(src["geometries"]),
            }
            for pid, src in sorted(pair_sources.items())
        },
        "coordinate_adapter": "node_gltf = D1_ZUP_TO_GLTF_YUP @ transpose(System.Numerics.CreateFromQuaternion+Translation row matrix)",
        "placements": placement_rows,
        "policy": (
            "Every model instance is an exact EntityResource->EntityModel pair from the all-visual plan at an inherited "
            "source placement. Real WorldIDs are unique identities; sentinel WorldIDs remain retail sentinel values and are "
            "keyed by exact serialized source identity. Multi-model entities are instantiated without cross-product guessing."
        ),
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in (
        "status","visual_candidate_count","runtime_placement_count","real_world_id_placement_count",
        "sentinel_world_id_placement_count","model_parent_pair_count","model_pair_instance_count",
        "unique_model_count","scene_geometry_variants","scene_geometry_nodes","bounds","glb_bytes","glb_sha256"
    )}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
