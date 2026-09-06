#!/usr/bin/env python3
"""Place exact D1 articulated model exports into a world-space glTF scene.

SMapDataEntry stores Rotation as an XYZW quaternion and Translation as Vector4.
D1/Charm uses System.Numerics row-vector transforms.  We therefore construct the
same row-vector Matrix4x4 from the serialized quaternion/translation, transpose
it for glTF column-vector nodes, then apply the already proven Tower basis:

    node_gltf = D1_ZUP_TO_GLTF_YUP @ M_d1.T

No position, rotation, scale, or duplicate WorldID is inferred.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import trimesh

A = np.array([
    [1., 0., 0., 0.],
    [0., 0., 1., 0.],
    [0., -1., 0., 0.],
    [0., 0., 0., 1.],
], dtype=np.float64)


def norm(h):
    return str(h).upper().removeprefix('0X').zfill(8)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def d1_row_matrix(rotation, translation):
    if len(rotation) != 4 or len(translation) < 3:
        raise ValueError('rotation must be XYZW and translation must contain XYZ')
    x, y, z, w = [float(v) for v in rotation]
    tx, ty, tz = [float(v) for v in translation[:3]]
    vals = [x,y,z,w,tx,ty,tz]
    if not all(math.isfinite(v) for v in vals):
        raise ValueError('non-finite placement transform')
    qn = math.sqrt(x*x + y*y + z*z + w*w)
    if not (0.999 <= qn <= 1.001):
        raise ValueError(f'non-unit serialized quaternion norm {qn}')
    # Normalize only the floating representation within retail roundoff; this is
    # mathematically the same rotation and prevents accumulated matrix drift.
    x /= qn; y /= qn; z /= qn; w /= qn
    xx=x*x; yy=y*y; zz=z*z; xy=x*y; xz=x*z; yz=y*z; wx=w*x; wy=w*y; wz=w*z
    return np.array([
        [1.0-2.0*(yy+zz), 2.0*(xy+wz),     2.0*(xz-wy),     0.0],
        [2.0*(xy-wz),     1.0-2.0*(xx+zz), 2.0*(yz+wx),     0.0],
        [2.0*(xz+wy),     2.0*(yz-wx),     1.0-2.0*(xx+yy), 0.0],
        [tx,               ty,               tz,               1.0],
    ], dtype=np.float64)


def load_models(model_dir: Path, tags: set[str]):
    out = {}
    missing = []
    for tag in sorted(tags):
        p = model_dir / f'{tag}.glb'
        if not p.exists():
            missing.append(tag)
            continue
        scene = trimesh.load(p, force='scene', process=False)
        if not scene.geometry:
            raise ValueError(f'{tag}: exported GLB contains no geometry')
        out[tag] = {
            'path': p,
            'sha256': sha256(p),
            'geometries': {name: g.copy() for name, g in scene.geometry.items()},
        }
    return out, missing


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--articulated-plan', type=Path, required=True)
    ap.add_argument('--model-dir', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    a = ap.parse_args()

    plan = json.loads(a.articulated_plan.read_text())
    if plan.get('status') != 'D1_WORLD_ARTICULATED_ENTITY_PLAN_COMPLETE':
        raise SystemExit('articulated plan is not complete')
    candidates = plan.get('candidates', [])
    tags = set()
    for c in candidates:
        models = [norm(x) for x in c.get('models', [])]
        if len(models) != 1:
            raise SystemExit(f"{c.get('entity')}: placement scene requires exact singleton model")
        tags.add(models[0])
    models, missing = load_models(a.model_dir, tags)
    if missing:
        raise SystemExit('missing articulated model GLBs: ' + ','.join(missing))

    scene = trimesh.Scene()
    geom_map = {}
    for tag, model in sorted(models.items()):
        for gi, (old_name, geom) in enumerate(model['geometries'].items()):
            name = f'{tag}__g{gi:03d}__{old_name}'
            scene.geometry[name] = geom
            geom_map.setdefault(tag, []).append(name)

    placement_rows = []
    world_ids = set()
    node_count = 0
    for c in candidates:
        entity = norm(c['entity'])
        tag = norm(c['models'][0])
        for p in c.get('placements', []):
            wid = str(p.get('world_id_hex') or '').upper().zfill(16)
            if not wid or wid in world_ids:
                raise SystemExit(f'duplicate or missing runtime WorldID {wid!r}')
            world_ids.add(wid)
            M = d1_row_matrix(p['rotation'], p['translation'])
            N = A @ M.T
            nodes = []
            for gi, geom_name in enumerate(geom_map[tag]):
                node_name = f'D1_ART_{wid}_{entity}_{tag}_g{gi:03d}'
                scene.graph.update(
                    frame_to=node_name,
                    matrix=N,
                    geometry=geom_name,
                    metadata={
                        'd1WorldID': wid,
                        'd1Entity': entity,
                        'd1Model': tag,
                        'd1RotationXYZW': p['rotation'],
                        'd1Translation': p['translation'],
                    },
                )
                nodes.append(node_name)
                node_count += 1
            placement_rows.append({
                'world_id': p.get('world_id'),
                'world_id_hex': wid,
                'entity': entity,
                'model': tag,
                'rotation_xyzw': p['rotation'],
                'translation': p['translation'],
                'serialized_reference_count': p.get('serialized_reference_count'),
                'duplicate_serialization_count': p.get('duplicate_serialization_count'),
                'source_references': p.get('source_references', []),
                'd1_row_matrix': M.tolist(),
                'gltf_matrix': N.tolist(),
                'node_count': len(nodes),
                'nodes': nodes,
            })

    expected = int(plan.get('runtime_placement_count', -1))
    if len(placement_rows) != expected:
        raise SystemExit(f'placement coverage mismatch {len(placement_rows)} != {expected}')
    a.out.parent.mkdir(parents=True, exist_ok=True)
    scene.export(a.out)
    report = {
        'schema_version': 1,
        'status': 'D1_WORLD_ARTICULATED_SCENE_COMPLETE',
        'candidate_count': len(candidates),
        'unique_model_count': len(tags),
        'runtime_placement_count': len(placement_rows),
        'unique_world_id_count': len(world_ids),
        'scene_geometry_variants': len(scene.geometry),
        'scene_geometry_nodes': node_count,
        'bounds': scene.bounds.tolist() if scene.bounds is not None else None,
        'glb': str(a.out),
        'glb_bytes': a.out.stat().st_size,
        'glb_sha256': sha256(a.out),
        'model_sources': {k: {'path': str(v['path']), 'sha256': v['sha256'], 'geometry_count': len(v['geometries'])} for k,v in models.items()},
        'coordinate_adapter': 'node_gltf = D1_ZUP_TO_GLTF_YUP @ transpose(System.Numerics.CreateFromQuaternion+Translation row matrix)',
        'placements': placement_rows,
        'policy': (
            'Every scene instance is one exact unique runtime WorldID from the source-owned articulated plan. '
            'Serialized XYZW rotation and XYZ translation are preserved; duplicate serializations are not replayed. '
            'No semantic NPC label, placement, orientation, scale, or model is inferred.'
        ),
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('status','candidate_count','unique_model_count','runtime_placement_count','scene_geometry_variants','scene_geometry_nodes','bounds','glb_bytes','glb_sha256')}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
