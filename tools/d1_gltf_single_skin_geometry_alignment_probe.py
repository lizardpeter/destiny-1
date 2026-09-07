#!/usr/bin/env python3
"""Measure native-model geometry versus skeleton alignment for standalone skinned GLBs.

This is the one-skin counterpart to d1_gltf_skin_geometry_alignment_probe.py. The
standalone spawned-actor model exports do not carry d1Model extras on every mesh node,
so selecting by mesh-node metadata would incorrectly find nothing. Instead this probe
requires exactly one skin, takes its model provenance from the skeleton root, and
aggregates every skinned mesh node using that skin.

The output is diagnostic. It is designed to catch the concrete parser-basis mismatch
where D1 geometry is tall on native Z while the parser-converted skeleton is tall on Y.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from d1_gltf_layer_merge import read_glb
from d1_gltf_skin_bind_identity_probe import accessor, globals_


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('glb', type=Path)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    doc, binary = read_glb(a.glb)
    nodes = doc.get('nodes', [])
    skins = doc.get('skins', [])
    if len(skins) != 1:
        raise SystemExit(f'expected exactly one skin, found {len(skins)}')
    skin = skins[0]
    root = int(skin['skeleton'])
    root_extras = nodes[root].get('extras') or {}
    model = str(root_extras.get('d1Model', '')).upper()
    skeleton = str(root_extras.get('d1Skeleton', '')).upper()
    runtime_rig = str(root_extras.get('d1RuntimeRig', '')).upper()
    if not model or not skeleton:
        raise SystemExit('single-skin skeleton root lacks exact D1 model/skeleton provenance')

    mesh_nodes = [(i, n) for i, n in enumerate(nodes)
                  if n.get('mesh') is not None and n.get('skin') == 0]
    if not mesh_nodes:
        raise SystemExit('no mesh nodes bound to the single skin')

    G = globals_(doc)
    root_inv = np.linalg.inv(G[root])
    joints = [int(x) for x in skin['joints']]
    joint_pos = np.stack([(root_inv @ G[j])[:3, 3] for j in joints], axis=0)

    # Standalone actor GLBs share each mesh exactly once, but deduplicate defensively.
    unique_meshes = {int(n['mesh']): n for _, n in mesh_nodes}
    sumw = np.zeros(len(joints), dtype=np.float64)
    sumpos = np.zeros((len(joints), 3), dtype=np.float64)
    mins = np.full((len(joints), 3), np.inf)
    maxs = np.full((len(joints), 3), -np.inf)
    refs = np.zeros(len(joints), dtype=np.int64)
    geom_min = np.full(3, np.inf)
    geom_max = np.full(3, -np.inf)
    vertex_total = 0

    for mi, node in sorted(unique_meshes.items()):
        mesh = doc['meshes'][mi]
        for prim in mesh.get('primitives', []):
            attrs = prim['attributes']
            for req in ('POSITION', 'JOINTS_0', 'WEIGHTS_0'):
                if req not in attrs:
                    raise SystemExit(f'mesh {mi}: missing {req}')
            pos = accessor(doc, binary, attrs['POSITION']).astype(np.float64)
            ji = accessor(doc, binary, attrs['JOINTS_0']).astype(np.int64)
            wt = accessor(doc, binary, attrs['WEIGHTS_0']).astype(np.float64)
            if len(pos) != len(ji) or len(pos) != len(wt):
                raise SystemExit(f'mesh {mi}: position/skin row-count mismatch')
            vertex_total += len(pos)
            geom_min = np.minimum(geom_min, pos.min(axis=0))
            geom_max = np.maximum(geom_max, pos.max(axis=0))
            for lane in range(4):
                for vi, (j, w) in enumerate(zip(ji[:, lane], wt[:, lane])):
                    if w <= 0:
                        continue
                    if not 0 <= j < len(joints):
                        raise SystemExit(f'mesh {mi}: joint ordinal {j} outside {len(joints)}')
                    sumw[j] += w
                    sumpos[j] += pos[vi] * w
                    refs[j] += 1
                    mins[j] = np.minimum(mins[j], pos[vi])
                    maxs[j] = np.maximum(maxs[j], pos[vi])

    rows = []
    distances = []
    for j in range(len(joints)):
        node = nodes[joints[j]]
        ex = node.get('extras') or {}
        jp = joint_pos[j]
        if sumw[j] > 0:
            centroid = sumpos[j] / sumw[j]
            distance = float(np.linalg.norm(centroid - jp))
            distances.append(distance)
            inside = bool(np.all(jp >= mins[j]) and np.all(jp <= maxs[j]))
            aabb_distance = float(np.linalg.norm(np.maximum(np.maximum(mins[j] - jp, jp - maxs[j]), 0.0)))
            row = {
                'joint_ordinal': j,
                'joint_node': joints[j],
                'name': node.get('name'),
                'bone_hash': ex.get('d1BoneHash'),
                'joint_position': jp.tolist(),
                'weight_sum': float(sumw[j]),
                'influence_references': int(refs[j]),
                'weighted_vertex_centroid': centroid.tolist(),
                'centroid_distance': distance,
                'influenced_vertex_aabb': [mins[j].tolist(), maxs[j].tolist()],
                'joint_inside_influenced_aabb': inside,
                'distance_to_influenced_aabb': aabb_distance,
            }
        else:
            row = {
                'joint_ordinal': j,
                'joint_node': joints[j],
                'name': node.get('name'),
                'bone_hash': ex.get('d1BoneHash'),
                'joint_position': jp.tolist(),
                'weight_sum': 0.0,
                'influence_references': 0,
            }
        rows.append(row)

    sk_min = joint_pos.min(axis=0)
    sk_max = joint_pos.max(axis=0)
    out = {
        'schema_version': 1,
        'status': 'D1_GLTF_SINGLE_SKIN_GEOMETRY_ALIGNMENT_DIAGNOSTIC_COMPLETE',
        'glb': str(a.glb),
        'model': model,
        'skeleton': skeleton,
        'runtime_rig': runtime_rig,
        'tested_mesh_count': len(unique_meshes),
        'skinned_mesh_node_count': len(mesh_nodes),
        'vertex_instances_aggregated': vertex_total,
        'joint_count': len(joints),
        'geometry_bounds': [geom_min.tolist(), geom_max.tolist()],
        'skeleton_joint_bounds': [sk_min.tolist(), sk_max.tolist()],
        'geometry_extent': (geom_max - geom_min).tolist(),
        'skeleton_extent': (sk_max - sk_min).tolist(),
        'influenced_joint_count': sum(x['weight_sum'] > 0 for x in rows),
        'centroid_distance_min': None if not distances else min(distances),
        'centroid_distance_median': None if not distances else float(np.median(distances)),
        'centroid_distance_max': None if not distances else max(distances),
        'joints': rows,
        'policy': (
            'Spatial diagnostic only. Model identity is taken from the exact single-skin '
            'skeleton-root provenance, not inferred from geometry. Proximity is not used '
            'to assign semantic bone names.'
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in (
        'status','model','skeleton','joint_count','tested_mesh_count',
        'geometry_extent','skeleton_extent','influenced_joint_count',
        'centroid_distance_min','centroid_distance_median','centroid_distance_max'
    )}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
