#!/usr/bin/env python3
"""Place exact D1 articulated model exports into a world-space glTF scene.

This v2 adapter preserves the retail D1 sentinel WorldID ``FFFFFFFFFFFFFFFF``.
A real WorldID remains a unique runtime identity and duplicate real IDs fail closed.
A sentinel is explicitly *not* an identity, so each sentinel placement receives a
stable scene key derived only from its exact serialized source reference
(table/resource hash, row index and record offset). The retail WorldID itself remains
unchanged in metadata and is never replaced with a fabricated numeric ID.

SMapDataEntry stores Rotation as an XYZW quaternion and Translation as Vector4.
D1/Charm uses System.Numerics row-vector transforms, so the same proven adapter is
used as v1:

    node_gltf = D1_ZUP_TO_GLTF_YUP @ M_d1.T
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
SENTINEL_WORLD_IDS = {"FFFFFFFFFFFFFFFF"}


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
    vals = [x, y, z, w, tx, ty, tz]
    if not all(math.isfinite(v) for v in vals):
        raise ValueError('non-finite placement transform')
    qn = math.sqrt(x*x + y*y + z*z + w*w)
    if not (0.999 <= qn <= 1.001):
        raise ValueError(f'non-unit serialized quaternion norm {qn}')
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


def source_identity(p: dict) -> tuple[str, dict]:
    refs = p.get('source_references') or []
    if len(refs) != 1:
        raise ValueError(
            'sentinel/no-identity placement must preserve exactly one serialized source reference; '
            f'got {len(refs)}'
        )
    r = refs[0]
    source_hash = norm(r.get('source_hash'))
    index = r.get('index')
    record_offset = r.get('record_offset')
    if index is None or record_offset is None:
        raise ValueError(f'sentinel source reference lacks index/record_offset: {r!r}')
    key = f'SENTINEL_{source_hash}_{int(index):06d}_{int(record_offset):08X}'
    return key, {
        'source_kind': r.get('source_kind'),
        'source_hash': source_hash,
        'index': int(index),
        'record_offset': int(record_offset),
    }


def placement_identity(p: dict, used_real_world_ids: set[str], used_keys: set[str]):
    wid = str(p.get('world_id_hex') or '').upper().removeprefix('0X').zfill(16)
    if not wid:
        raise ValueError('missing runtime WorldID field')
    if wid in SENTINEL_WORLD_IDS:
        if int(p.get('serialized_reference_count', 1)) != 1:
            raise ValueError('sentinel/no-identity runtime placement was unexpectedly deduplicated')
        key, src = source_identity(p)
        kind = 'sentinel_serialized_source_identity'
    else:
        if wid in used_real_world_ids:
            raise ValueError(f'duplicate real runtime WorldID {wid}')
        used_real_world_ids.add(wid)
        key = f'WORLDID_{wid}'
        src = None
        kind = 'real_world_id'
    if key in used_keys:
        raise ValueError(f'duplicate placement identity key {key}')
    used_keys.add(key)
    return wid, key, kind, src


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
    used_real_world_ids: set[str] = set()
    used_keys: set[str] = set()
    node_count = 0
    sentinel_count = 0
    for c in candidates:
        entity = norm(c['entity'])
        tag = norm(c['models'][0])
        for p in c.get('placements', []):
            try:
                wid, identity_key, identity_kind, sentinel_source = placement_identity(
                    p, used_real_world_ids, used_keys
                )
            except ValueError as ex:
                raise SystemExit(f'{entity}/{tag}: {ex}') from ex
            if wid in SENTINEL_WORLD_IDS:
                sentinel_count += 1
            M = d1_row_matrix(p['rotation'], p['translation'])
            N = A @ M.T
            nodes = []
            safe_key = identity_key.replace(':', '_').replace('/', '_')
            for gi, geom_name in enumerate(geom_map[tag]):
                node_name = f'D1_ART_{safe_key}_{entity}_{tag}_g{gi:03d}'
                scene.graph.update(
                    frame_to=node_name,
                    matrix=N,
                    geometry=geom_name,
                    metadata={
                        'd1PlacementIdentity': identity_key,
                        'd1PlacementIdentityKind': identity_kind,
                        'd1WorldID': wid,
                        'd1WorldIDIsSentinel': wid in SENTINEL_WORLD_IDS,
                        'd1Entity': entity,
                        'd1Model': tag,
                        'd1RotationXYZW': p['rotation'],
                        'd1Translation': p['translation'],
                        'd1SerializedSourceIdentity': sentinel_source,
                    },
                )
                nodes.append(node_name)
                node_count += 1
            placement_rows.append({
                'placement_identity': identity_key,
                'placement_identity_kind': identity_kind,
                'world_id': p.get('world_id'),
                'world_id_hex': wid,
                'world_id_is_sentinel': wid in SENTINEL_WORLD_IDS,
                'sentinel_serialized_source_identity': sentinel_source,
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
        'schema_version': 2,
        'status': 'D1_WORLD_ARTICULATED_SCENE_COMPLETE_SENTINEL_SAFE',
        'candidate_count': len(candidates),
        'unique_model_count': len(tags),
        'runtime_placement_count': len(placement_rows),
        'real_world_id_placement_count': len(used_real_world_ids),
        'sentinel_world_id_placement_count': sentinel_count,
        'unique_placement_identity_count': len(used_keys),
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
            'Real WorldIDs are unique runtime identities and duplicate real IDs fail closed. FFFFFFFFFFFFFFFF is preserved '
            'as a retail sentinel/no-identity value; each such placement is keyed only by its exact serialized source '
            'table/index/record offset. No WorldID, model, placement, transform, or semantic entity label is fabricated.'
        ),
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in (
        'status','candidate_count','unique_model_count','runtime_placement_count',
        'real_world_id_placement_count','sentinel_world_id_placement_count',
        'unique_placement_identity_count','scene_geometry_variants','scene_geometry_nodes',
        'bounds','glb_bytes','glb_sha256')}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
