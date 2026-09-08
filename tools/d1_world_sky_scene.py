#!/usr/bin/env python3
"""Instantiate source-owned D1 map sky EntityModels from exact SkyRecord matrices.

The input is the loss-preserving ``d1_world_map_lighting_census.py`` report and the
textured EntityModel GLBs produced by the sky visual/texture closure.

Pinned Charm behavior (MontagueM/Charm@50d36ee1f9ecadad7522504c20b1f3f9c97e30af,
Charm/ActivityMapEntityView.xaml.cs) for D1 ``SMapSkyEntResource`` is:

* iterate every map data entry carrying the sky resource;
* iterate every ``SMapSkyEntities.Unk08`` SkyRecord in source order;
* construct ``System.Numerics.Matrix4x4`` directly from the four vectors at
  SkyRecord +0x00..+0x3F;
* decompose that matrix to scale/quaternion/translation;
* add the record's EntityModel to the sky scene;
* do not apply the outer SMapDataEntry transform and do not choose a default sky.

A System.Numerics transform is row-vector convention. Rather than numerically
round-tripping through decomposition/recomposition, this adapter preserves the exact
source matrix and converts it to glTF column convention using the same proven D1
Z-up -> glTF Y-up basis used by the world entity scene:

    gltf_matrix = D1_ZUP_TO_GLTF_YUP @ source_row_matrix.T

This is algebraically equivalent for the affine rotation/scale/translation matrices
Charm decomposes, while retaining the serialized matrix values losslessly in the
report. Collection payloads are decoded once in the census, but occurrences are
replayed separately so repeated map-entry references are never collapsed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import trimesh

from d1_world_articulated_scene_v2 import A

CENSUS_STATUS = "D1_WORLD_MAP_LIGHTING_CENSUS_COMPLETE"
SKY_CLASS = "80801BDA"
NULLS = {"00000000", "FFFFFFFF"}


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def source_matrix(vectors: object) -> np.ndarray:
    if not isinstance(vectors, list) or len(vectors) != 4:
        raise ValueError("SkyRecord must contain exactly four source matrix vectors")
    rows = []
    for i, row in enumerate(vectors):
        if not isinstance(row, list) or len(row) != 4:
            raise ValueError(f"SkyRecord matrix row {i} is not a Vector4")
        vals = [float(x) for x in row]
        if not all(math.isfinite(x) for x in vals):
            raise ValueError(f"SkyRecord matrix row {i} contains non-finite values")
        rows.append(vals)
    m = np.asarray(rows, dtype=np.float64)
    # System.Numerics affine matrices used by Matrix4x4.Decompose carry the
    # homogeneous column [0,0,0,1]. Fail closed if a future record is not affine.
    if not np.allclose(m[:3, 3], 0.0, atol=1e-5) or not math.isclose(float(m[3, 3]), 1.0, abs_tol=1e-5):
        raise ValueError(f"SkyRecord matrix is not affine System.Numerics form: last column={m[:,3].tolist()}")
    det = float(np.linalg.det(m[:3, :3]))
    if not math.isfinite(det) or abs(det) < 1e-10:
        raise ValueError(f"SkyRecord matrix has non-decomposable linear determinant {det}")
    return m


def model_path(model_dir: Path, tag: str) -> Path | None:
    exact = model_dir / f"{tag}_SKY_EXACT_TEXTURES.glb"
    if exact.exists():
        return exact
    plain = model_dir / f"{tag}.glb"
    if plain.exists():
        return plain
    matches = sorted(model_dir.glob(f"{tag}*.glb"))
    return matches[0] if len(matches) == 1 else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lighting-census", type=Path, required=True)
    ap.add_argument("--model-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    a = ap.parse_args()

    census = json.loads(a.lighting_census.read_text(encoding="utf-8"))
    if census.get("status") != CENSUS_STATUS:
        raise SystemExit(f"lighting census is not complete: {census.get('status')!r}")
    if census.get("violations") or census.get("missing_dependency_package_ids"):
        raise SystemExit("lighting census contains unresolved evidence")

    collections = {norm(x.get("hash")): x for x in census.get("sky_collections", [])}
    model_resources = {norm(x.get("hash")): x for x in census.get("sky_model_resources", [])}
    if len(collections) != int(census.get("unique_sky_collection_count", -1)):
        raise SystemExit("sky collection count mismatch")
    if len(model_resources) != int(census.get("decoded_sky_model_resource_count", -1)):
        raise SystemExit("sky model-resource count mismatch")

    resource_to_model: dict[str, str] = {}
    for rh, row in sorted(model_resources.items()):
        em = row.get("entity_model") or {}
        mh = norm(em.get("hash"))
        if mh in NULLS or not em.get("exists") or not em.get("class_matches"):
            raise SystemExit(f"{rh}: sky model resource lacks exact EntityModel")
        resource_to_model[rh] = mh

    declared_models = {norm(x) for x in census.get("sky_entity_models", [])}
    if set(resource_to_model.values()) != declared_models:
        raise SystemExit("sky EntityModel set does not match decoded SkyModelResources")

    model_sources = {}
    missing_models = []
    for mh in sorted(declared_models):
        p = model_path(a.model_dir, mh)
        if p is None:
            missing_models.append(mh)
            continue
        src = trimesh.load(p, force="scene", process=False)
        if not src.geometry:
            raise SystemExit(f"{mh}: sky model GLB contains no geometry")
        model_sources[mh] = {
            "path": p,
            "sha256": sha256(p),
            "geometries": {name: geom.copy() for name, geom in src.geometry.items()},
        }
    if missing_models:
        raise SystemExit("missing sky model GLBs: " + ",".join(missing_models))

    scene = trimesh.Scene()
    geom_map: dict[str, list[str]] = {}
    for mh, src in sorted(model_sources.items()):
        names = []
        for gi, (old_name, geom) in enumerate(src["geometries"].items()):
            name = f"D1_SKY_MODEL_{mh}_g{gi:03d}__{old_name}"
            scene.geometry[name] = geom
            names.append(name)
        geom_map[mh] = names

    sky_occurrences = [x for x in census.get("occurrences", []) if norm(x.get("resource_class")) == SKY_CLASS]
    if len(sky_occurrences) != int(census.get("sky_resource_occurrences", -1)):
        raise SystemExit("sky resource occurrence count mismatch")

    placement_rows = []
    geometry_node_count = 0
    per_collection_occurrences: dict[str, int] = {}
    for oi, occ in enumerate(sky_occurrences):
        ch = norm(occ.get("resource_target"))
        collection = collections.get(ch)
        if collection is None:
            raise SystemExit(f"sky occurrence {oi}: collection {ch} not decoded")
        per_collection_occurrences[ch] = per_collection_occurrences.get(ch, 0) + 1
        records = collection.get("sky_records") or []
        if len(records) != int(collection.get("sky_record_count", -1)):
            raise SystemExit(f"{ch}: sky record count mismatch")
        for record in records:
            ri = int(record.get("index"))
            sr = record.get("sky_model_resource") or {}
            rh = norm(sr.get("hash"))
            if not sr.get("exists") or not sr.get("class_matches") or rh not in resource_to_model:
                raise SystemExit(f"{ch}:{ri}: unresolved SkyModelResource {rh}")
            mh = resource_to_model[rh]
            m = source_matrix(record.get("matrix_like_vectors"))
            n = A @ m.T
            nodes = []
            for gi, gname in enumerate(geom_map[mh]):
                node = f"D1_SKY_occ{oi:03d}_{ch}_rec{ri:04d}_{mh}_g{gi:03d}"
                scene.graph.update(
                    frame_to=node,
                    matrix=n,
                    geometry=gname,
                    metadata={
                        "d1SkyOccurrenceIndex": oi,
                        "d1MapDataTable": occ.get("map_data_table"),
                        "d1MapEntryIndex": occ.get("entry_index"),
                        "d1WorldID": occ.get("world_id"),
                        "d1SkyCollection": ch,
                        "d1SkyRecordIndex": ri,
                        "d1SkyModelResource": rh,
                        "d1EntityModel": mh,
                        "d1SkyRecordMatrixRows": record.get("matrix_like_vectors"),
                        "d1SkyBoundsLikeVectors": record.get("bounds_like_vectors"),
                        "d1OuterMapRotationPreservedNotApplied": occ.get("outer_rotation"),
                        "d1OuterMapTranslationPreservedNotApplied": occ.get("outer_translation"),
                    },
                )
                nodes.append(node)
                geometry_node_count += 1
            placement_rows.append({
                "occurrence_index": oi,
                "map_data_table": occ.get("map_data_table"),
                "map_entry_index": occ.get("entry_index"),
                "world_id": occ.get("world_id"),
                "sky_collection": ch,
                "sky_record_index": ri,
                "sky_model_resource": rh,
                "entity_model": mh,
                "source_record_sha256": record.get("record_sha256"),
                "source_matrix_rows": record.get("matrix_like_vectors"),
                "bounds_like_vectors": record.get("bounds_like_vectors"),
                "gltf_matrix": n.tolist(),
                "outer_map_rotation_preserved_not_applied": occ.get("outer_rotation"),
                "outer_map_translation_preserved_not_applied": occ.get("outer_translation"),
                "geometry_node_count": len(nodes),
                "nodes": nodes,
            })

    unique_record_count = sum(int(x.get("sky_record_count", 0)) for x in collections.values())
    if unique_record_count != int(census.get("sky_record_count", -1)):
        raise SystemExit("unique decoded sky record count mismatch")
    expected_instances = sum(
        int(collections[norm(o.get("resource_target"))].get("sky_record_count", 0))
        for o in sky_occurrences
    )
    if len(placement_rows) != expected_instances:
        raise SystemExit(f"sky occurrence replay mismatch {len(placement_rows)} != {expected_instances}")

    a.out.parent.mkdir(parents=True, exist_ok=True)
    scene.export(a.out)
    report = {
        "schema_version": 1,
        "status": "D1_WORLD_SKY_SCENE_COMPLETE",
        "source_sky_resource_occurrence_count": len(sky_occurrences),
        "unique_sky_collection_count": len(collections),
        "unique_decoded_sky_record_count": unique_record_count,
        "replayed_sky_record_instance_count": len(placement_rows),
        "unique_sky_model_resource_count": len(resource_to_model),
        "unique_entity_model_count": len(declared_models),
        "scene_geometry_variants": len(scene.geometry),
        "scene_geometry_nodes": geometry_node_count,
        "per_collection_occurrence_counts": dict(sorted(per_collection_occurrences.items())),
        "bounds": scene.bounds.tolist() if scene.bounds is not None else None,
        "glb": str(a.out),
        "glb_bytes": a.out.stat().st_size,
        "glb_sha256": sha256(a.out),
        "model_sources": {
            mh: {
                "path": str(src["path"]),
                "sha256": src["sha256"],
                "geometry_count": len(src["geometries"]),
            }
            for mh, src in sorted(model_sources.items())
        },
        "placements": placement_rows,
        "coordinate_adapter": "node_gltf = D1_ZUP_TO_GLTF_YUP @ transpose(serialized SkyRecord System.Numerics row matrix)",
        "source_behavior": "Charm ActivityMapEntityView iterates every SMapSkyEntResource occurrence and every SkyRecord, decomposes the four-vector Matrix4x4, and adds its EntityModel; the outer SMapDataEntry transform is not applied.",
        "policy": "No sky collection, record, time-of-day state, transform, model, material, or texture is inferred. Repeated collection occurrences are replayed separately; geometry is shared only as a storage optimization.",
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in (
        "status", "source_sky_resource_occurrence_count", "unique_sky_collection_count",
        "unique_decoded_sky_record_count", "replayed_sky_record_instance_count",
        "unique_sky_model_resource_count", "unique_entity_model_count", "scene_geometry_variants",
        "scene_geometry_nodes", "per_collection_occurrence_counts", "bounds", "glb_bytes", "glb_sha256"
    )}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
