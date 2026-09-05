#!/usr/bin/env python3
"""Bind a rigid D1 model GLB to an exact retail skeleton/rig/animation clip.

This is deliberately conservative: every vertex in the input GLB is assigned to
one caller-supplied skeleton joint.  It is intended for D1 assets whose retail
vertex stream has already been proven to contain one uniform rigid joint index
(e.g. a helmet whose entire model is joint 18).  It does NOT infer weights and
must not be used for models containing multiple joints or unresolved sentinel
values.

The skeleton inverse-bind matrices and animation are decoded from retail D1
resources.  The animation path is the same validated sequence used elsewhere in
this repository:
    read_animation -> decode_animation -> rig_retarget -> convert_obj_to_local

The resulting GLB keeps the original geometry/materials, adds a glTF skin using
the exact D1 bind pose, adds JOINTS_0/WEIGHTS_0, and serializes the retargeted
local animation on the skeleton hierarchy.
"""
from __future__ import annotations

import argparse
import io
import json
import struct
import sys
import tempfile
from pathlib import Path

import numpy as np
from pygltflib import (
    GLTF2, Node, Skin, BufferView, Accessor, Animation, AnimationSampler,
    AnimationChannel, AnimationChannelTarget,
)

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from d1_entry_extract import EntryReader

FLOAT = 5126
UNSIGNED_SHORT = 5123
ARRAY_BUFFER = 34962


def align4(buf: bytearray) -> None:
    while len(buf) & 3:
        buf.append(0)


def append_accessor(g: GLTF2, blob: bytearray, data: np.ndarray, *, component_type: int,
                    accessor_type: str, target: int | None = None,
                    with_minmax: bool = False) -> int:
    align4(blob)
    off = len(blob)
    raw = data.tobytes(order='C')
    blob.extend(raw)
    view_idx = len(g.bufferViews)
    g.bufferViews.append(BufferView(buffer=0, byteOffset=off, byteLength=len(raw), target=target))
    count = int(data.shape[0])
    acc = Accessor(bufferView=view_idx, byteOffset=0, componentType=component_type,
                   count=count, type=accessor_type)
    if with_minmax:
        if accessor_type == 'SCALAR':
            acc.min = [float(np.min(data))]
            acc.max = [float(np.max(data))]
        elif accessor_type.startswith('VEC'):
            acc.min = [float(x) for x in np.min(data, axis=0)]
            acc.max = [float(x) for x in np.max(data, axis=0)]
    idx = len(g.accessors)
    g.accessors.append(acc)
    return idx


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('input_glb', type=Path)
    ap.add_argument('--pkg', type=Path, required=True, help='package containing skeleton/rig/clip logical view')
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--parser-root', type=Path, required=True)
    ap.add_argument('--skeleton', required=True)
    ap.add_argument('--rig', required=True)
    ap.add_argument('--clip', required=True)
    ap.add_argument('--joint-index', type=int, required=True)
    ap.add_argument('--animation-name')
    ap.add_argument('--fps', type=float, default=30.0)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    a = ap.parse_args()

    sys.path.insert(0, str(a.parser_root.resolve()))
    from tag.game_version import Game_Version
    from tag_readers.read_skeleton import read_skeleton, transform_to_np_matrix
    from tag_readers.read_rig import read_runtime_rig
    from tag_readers.read_animation import read_animation
    from animation_decoding.decode_animation import decode_animation
    from runtime_rig.rig_retarget import rig_retarget
    from animation_export.convert_animation_object_to_local import convert_obj_to_local
    from matrix_operations.numpy_matrix_operations import np_decompose_matrix
    from fnv_hashes.bones_names import convert_hash_to_bungie_name

    r = EntryReader(a.pkg, a.runtime)
    by = {e['tag_hash'].upper(): e for e in r.entries}
    skh = a.skeleton.upper().removeprefix('0X')
    righ = a.rig.upper().removeprefix('0X')
    cliph = a.clip.upper().removeprefix('0X')
    for h in (skh, righ, cliph):
        if h not in by:
            raise KeyError(f'{h} is not present in {a.pkg}')
    ver = Game_Version.D1_ROI
    sk = read_skeleton(io.BytesIO(r.entry(by[skh]['index'])), ver)
    rig = read_runtime_rig(io.BytesIO(r.entry(by[righ]['index'])), ver)
    with tempfile.NamedTemporaryFile() as f:
        f.write(r.entry(by[cliph]['index'])); f.flush(); f.seek(0)
        anim = read_animation(f, ver)
    decoded = decode_animation(anim)
    retargeted = rig_retarget(anim, decoded, sk, rig)
    local = convert_obj_to_local(anim, retargeted, sk)

    node_count = len(sk.node_defs)
    rig_count = len(rig.controls_relations)
    if not (0 <= a.joint_index < node_count):
        raise ValueError(f'joint {a.joint_index} outside skeleton node count {node_count}')
    h = anim.animation_header
    if int(h.node_count) != node_count:
        raise ValueError(f'clip node count {int(h.node_count)} != skeleton {node_count}')
    if int(h.rig_control_count) != rig_count:
        raise ValueError(f'clip rig controls {int(h.rig_control_count)} != runtime rig {rig_count}')
    if len(retargeted) != node_count or len(local) != node_count:
        raise ValueError(f'retarget/local tracks {len(retargeted)}/{len(local)} != nodes {node_count}')

    g = GLTF2().load_binary(str(a.input_glb))
    if len(g.buffers) != 1:
        raise ValueError(f'expected one-buffer GLB, found {len(g.buffers)}')
    blob = bytearray(g.binary_blob() or b'')
    original_blob_bytes = len(blob)
    original_node_count = len(g.nodes)
    original_mesh_count = len(g.meshes)
    original_scene_roots = list(g.scenes[g.scene or 0].nodes or [])

    # Exact D1 hierarchical bind pose.
    world = [transform_to_np_matrix(x) for x in sk.default_obj_space_tr]
    inv_world = [transform_to_np_matrix(x) for x in sk.default_inv_obj_space_tr]
    bone_nodes: list[int] = []
    bone_names: list[str] = []
    for i, nd in enumerate(sk.node_defs):
        parent = int(nd.parent_node_index)
        mat = inv_world[parent] @ world[i] if parent >= 0 else world[i]
        scale, rot, trans = np_decompose_matrix(mat)
        name = convert_hash_to_bungie_name(int(nd.bone_hash))
        if not name:
            name = f'{int(nd.bone_hash) & 0xffffffff:08X}'
        # Preserve uniqueness even if a name dictionary aliases two hashes.
        if name in bone_names:
            name = f'{name}_{int(nd.bone_hash) & 0xffffffff:08X}'
        bone_names.append(name)
        idx = len(g.nodes)
        g.nodes.append(Node(name=name, children=[], translation=[float(x) for x in trans],
                            rotation=[float(x) for x in rot.as_quat()], scale=[float(x) for x in scale],
                            extras={'d1BoneIndex': i, 'd1BoneHash': f'{int(nd.bone_hash) & 0xffffffff:08X}'}))
        bone_nodes.append(idx)
    root_idx = len(g.nodes)
    g.nodes.append(Node(name='D1_Guardian_Skeleton', children=[], translation=[0,0,0],
                        rotation=[0,0,0,1], scale=[1,1,1],
                        extras={'d1Skeleton': skh, 'd1RuntimeRig': righ}))
    for i, nd in enumerate(sk.node_defs):
        parent = int(nd.parent_node_index)
        if parent >= 0:
            g.nodes[bone_nodes[parent]].children.append(bone_nodes[i])
        else:
            g.nodes[root_idx].children.append(bone_nodes[i])

    inv_bind = np.stack([np.asarray(m.T, dtype='<f4') for m in inv_world], axis=0)
    ibm_acc = append_accessor(g, blob, inv_bind, component_type=FLOAT, accessor_type='MAT4')
    skin_idx = len(g.skins)
    g.skins.append(Skin(joints=bone_nodes, inverseBindMatrices=ibm_acc, skeleton=root_idx,
                        name=f'D1_{skh}_skin'))

    # Rigidly bind every original mesh primitive to the caller-proven retail joint.
    bound_primitive_count = 0
    bound_vertex_count = 0
    for mesh in g.meshes[:original_mesh_count]:
        for prim in mesh.primitives:
            pos_acc_idx = prim.attributes.POSITION
            if pos_acc_idx is None:
                continue
            count = int(g.accessors[pos_acc_idx].count)
            joints = np.zeros((count, 4), dtype='<u2')
            joints[:, 0] = a.joint_index
            weights = np.zeros((count, 4), dtype='<f4')
            weights[:, 0] = 1.0
            jacc = append_accessor(g, blob, joints, component_type=UNSIGNED_SHORT,
                                   accessor_type='VEC4', target=ARRAY_BUFFER)
            wacc = append_accessor(g, blob, weights, component_type=FLOAT,
                                   accessor_type='VEC4', target=ARRAY_BUFFER)
            prim.attributes.JOINTS_0 = jacc
            prim.attributes.WEIGHTS_0 = wacc
            bound_primitive_count += 1
            bound_vertex_count += count
    bound_mesh_nodes = []
    for i, node in enumerate(g.nodes[:original_node_count]):
        if node.mesh is not None:
            node.skin = skin_idx
            bound_mesh_nodes.append(i)

    # Serialize exact local animation into the same buffer.
    channels = []
    samplers = []
    animated_bones = 0
    frame_max = 0
    for bi, track in enumerate(local):
        node_idx = bone_nodes[bi]
        for path, values, kind in (
            ('translation', track.translations, 'VEC3'),
            ('rotation', track.rotations, 'VEC4'),
            ('scale', track.scales, 'VEC3'),
        ):
            arr = np.asarray(values, dtype='<f4')
            if arr.size == 0:
                continue
            if arr.ndim != 2:
                arr = arr.reshape((-1, 4 if kind == 'VEC4' else 3))
            times = (np.arange(arr.shape[0], dtype='<f4') / float(a.fps)).astype('<f4')
            tacc = append_accessor(g, blob, times, component_type=FLOAT, accessor_type='SCALAR', with_minmax=True)
            vacc = append_accessor(g, blob, arr, component_type=FLOAT, accessor_type=kind)
            si = len(samplers)
            samplers.append(AnimationSampler(input=tacc, output=vacc, interpolation='LINEAR'))
            channels.append(AnimationChannel(sampler=si, target=AnimationChannelTarget(node=node_idx, path=path)))
            frame_max = max(frame_max, arr.shape[0])
        animated_bones += 1
    anim_name = a.animation_name or f'D1_{cliph}'
    g.animations.append(Animation(name=anim_name, channels=channels, samplers=samplers,
                                  extras={'d1Clip': cliph, 'd1Skeleton': skh, 'd1RuntimeRig': righ,
                                          'd1FrameCount': int(h.frame_count), 'd1Fps': float(a.fps)}))

    # Keep original geometry roots and add skeleton beside them.
    scene_idx = g.scene or 0
    roots = list(g.scenes[scene_idx].nodes or [])
    if root_idx not in roots:
        roots.append(root_idx)
    g.scenes[scene_idx].nodes = roots
    g.extras = {
        **(g.extras or {}),
        'd1RigidBindingProof': {
            'skeleton': skh, 'runtimeRig': righ, 'clip': cliph,
            'jointIndex': a.joint_index, 'jointName': bone_names[a.joint_index],
            'policy': 'Uniform joint assignment supplied only after independent retail vertex-lane validation.'
        }
    }
    g.buffers[0].byteLength = len(blob)
    g.set_binary_blob(bytes(blob))
    a.out.parent.mkdir(parents=True, exist_ok=True)
    g.save_binary(str(a.out))

    rep = {
        'schema': 'd1_gltf_bind_rigid_animation/v1',
        'input': str(a.input_glb), 'output': str(a.out), 'output_bytes': a.out.stat().st_size,
        'skeleton': skh, 'skeleton_node_count': node_count,
        'runtime_rig': righ, 'runtime_rig_control_count': rig_count,
        'clip': cliph, 'clip_frame_count': int(h.frame_count),
        'decoded_track_count': len(decoded), 'retargeted_track_count': len(retargeted),
        'local_track_count': len(local), 'joint_index': a.joint_index,
        'joint_name': bone_names[a.joint_index],
        'bound_mesh_node_count': len(bound_mesh_nodes), 'bound_primitive_count': bound_primitive_count,
        'bound_vertex_count': bound_vertex_count, 'animation_channel_count': len(channels),
        'animation_sampler_count': len(samplers), 'original_mesh_count': original_mesh_count,
        'original_scene_roots': original_scene_roots, 'original_binary_bytes': original_blob_bytes,
        'final_binary_bytes': len(blob),
        'policy': 'No weights are inferred. Every exported mesh vertex receives exactly the caller-proven uniform rigid joint with weight 1.0; bind matrices and local animation tracks come from exact retail D1 resources.'
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(rep, indent=2) + '\n')
    print(json.dumps(rep, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
