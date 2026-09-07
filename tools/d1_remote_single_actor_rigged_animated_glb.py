#!/usr/bin/env python3
"""Build one exact D1 PS4 articulated actor GLB from source-closed evidence.

The input geometry GLB must come from d1_world_articulated_model_export.export_one,
so every primitive is already the exact stage-0/highest-detail range selected through
the owning EntityResource material binding and preserves source_vertex_indices.

This adapter adds only source-proven data:
- JOINTS_0 / WEIGHTS_0 from exact retail primary streams;
- source skeleton hierarchy and inverse bind matrices;
- every selector-selected animation clip from one exact 80802C0E control after the
  pinned D1 decode -> runtime-rig retarget -> local conversion path.

It never chooses a default/startup clip, loop mode, synchronization rule, state name,
material texture semantic, placement, or actor identity. Those remain external proof
inputs. The original geometry GLB binary chunk must survive as an exact prefix.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

import numpy as np
from pygltflib import (
    GLTF2, Node, Skin, Animation, AnimationSampler, AnimationChannel,
    AnimationChannelTarget,
)

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_split_tar_extract import SplitHttpTar
from d1_remote_activity_placements import RemoteCorpus
from d1_gltf_bind_rigid_animation import append_accessor, FLOAT, UNSIGNED_SHORT, ARRAY_BUFFER
from d1_tower_spawned_actor_skin_bind import payload, source_stream
from d1_tower_family_e_animated_layer import exact_float32_weights

CLIP_REF = '808005A1'
ENTITY_RESOURCE_REF = '80800861'


def norm(x) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(8 << 20), b''):
            h.update(b)
    return h.hexdigest()


def exact(c: RemoteCorpus, h: str, expected_ref: str | None = None):
    h = norm(h)
    m = c.entry_meta(h)
    b, src = c.payload(h)
    if m is None or b is None:
        raise KeyError(f'{h}: exact payload unavailable')
    ref = norm(m.get('reference', 'FFFFFFFF'))
    if expected_ref is not None and ref != norm(expected_ref):
        raise ValueError(f'{h}: reference {ref} != {norm(expected_ref)}')
    return m, b, str(src)


def filebacked(read_animation, payload_bytes: bytes, version):
    with tempfile.NamedTemporaryFile() as f:
        f.write(payload_bytes); f.flush(); f.seek(0)
        return read_animation(f, version)


def one_skin_family(doc: dict, model: str, skeleton: str, rig: str, bones: int) -> dict:
    if doc.get('status') != 'D1_CROTA_EXACT_SKIN_CENSUS_COMPLETE':
        raise ValueError(f'skin census status not closed: {doc.get("status")}')
    if doc.get('violations') or doc.get('frontiers'):
        raise ValueError('skin census contains global violation/frontier')
    rows = [x for x in doc.get('families', []) if norm(x.get('model', '')) == model or model in [norm(y) for y in x.get('models', [])]]
    if len(rows) != 1:
        raise ValueError(f'{model}: expected exactly one skin family, got {len(rows)}')
    f = rows[0]
    if f.get('violations') or f.get('frontiers'):
        raise ValueError(f'{model}: skin family not closed')
    if [int(x) for x in f.get('bone_counts', [])] != [bones]:
        raise ValueError(f'{model}: bone-count drift {f.get("bone_counts")}')
    if [norm(x) for x in f.get('skeleton_resources', [])] != [skeleton]:
        raise ValueError(f'{model}: skeleton-resource drift')
    if [norm(x) for x in f.get('runtime_rig_resources', [])] != [rig]:
        raise ValueError(f'{model}: runtime-rig-resource drift')
    if int(f.get('separate_old_weights_mesh_count', 0)) != 0:
        raise ValueError(f'{model}: this exact single-actor exporter requires the already-closed inline forms')
    if int(f.get('inline_mesh_count', -1)) != int(f.get('mesh_count', -2)):
        raise ValueError(f'{model}: not all model meshes are exact inline skin forms')
    return f


def model_row(doc: dict, model: str) -> dict:
    if doc.get('status') == 'D1_WORLD_ARTICULATED_MODEL_EXPORT_COMPLETE':
        row = doc
    else:
        rows = [x for x in doc.get('models', []) if norm(x.get('model', '')) == model]
        if len(rows) != 1:
            raise ValueError(f'{model}: expected one exact model report row, got {len(rows)}')
        row = rows[0]
    if norm(row.get('model', '')) != model:
        raise ValueError(f'model report identity drift: {row.get("model")}')
    if row.get('status') != 'D1_WORLD_ARTICULATED_MODEL_EXPORT_COMPLETE':
        raise ValueError(f'model export not complete: {row.get("status")}')
    if int(row.get('stage0_selected_range_count', -1)) != len(row.get('ranges', [])):
        raise ValueError('stage0 selected-range report count drift')
    if int(row.get('geometry_count', -1)) != len(row.get('ranges', [])):
        raise ValueError('geometry/range count drift')
    if sum(int(x['triangle_count']) for x in row.get('ranges', [])) != int(row.get('triangle_count', -1)):
        raise ValueError('triangle total drift')
    return row


def animation_evidence(doc: dict, entity: str, skeleton: str, rig: str, control: str) -> tuple[dict, dict, dict, list[str], dict[str, list[dict]]]:
    if doc.get('schema') != 'd1_remote_spawned_actor_animation_options/v3' or doc.get('status') != 'D1_ACTIVITY_ACTOR_ANIMATION_OPTIONS_COMPLETE':
        raise ValueError(f'animation options not source-closed v3: {doc.get("schema")} {doc.get("status")}')
    if doc.get('violations') or doc.get('frontiers') or int(doc.get('retarget_pair_failure_count', -1)) != 0:
        raise ValueError('animation options contain violation/frontier/retarget failure')
    erows = [x for x in doc.get('entities', []) if norm(x.get('entity')) == entity]
    if len(erows) != 1:
        raise ValueError(f'{entity}: expected one animation entity row, got {len(erows)}')
    erow = erows[0]
    controls = [norm(x) for x in erow.get('control_hashes', [])]
    if controls != [control]:
        raise ValueError(f'{entity}: exact control set drift {controls} != {[control]}')
    targets = [x for x in doc.get('targets', []) if norm(x.get('skeleton')) == skeleton and norm(x.get('runtime_rig')) == rig and norm(x.get('control')) == control]
    if len(targets) != 1:
        raise ValueError(f'{entity}: expected one target validation, got {len(targets)}')
    target = targets[0]
    if not target.get('all_selector_selected_clips_retarget_success') or int(target.get('retarget_failure_count', -1)) != 0:
        raise ValueError('target is not fully native-retarget closed')
    ci = (doc.get('controls') or {}).get(control)
    if not ci:
        raise ValueError(f'missing decoded control {control}')
    selected = sorted({norm(x) for x in ci.get('selector_selected_clip_hashes', [])})
    target_clips = {norm(x['clip']): x for x in target.get('clips', [])}
    if set(selected) != set(target_clips):
        raise ValueError(f'selected clip/target validation set drift {len(selected)}/{len(target_clips)}')
    if any(not target_clips[x].get('retarget_success') for x in selected):
        raise ValueError('selected clip contains failed native retarget')
    states = defaultdict(list)
    for st in (ci.get('state_table') or {}).get('records', []):
        for a in st.get('selected_animations', []):
            clip = norm(a.get('tag_hash'))
            if clip in target_clips:
                states[clip].append({
                    'record_index': int(st.get('record_index', -1)),
                    'state_hash': str(st.get('state_hash')).upper(),
                    'state_name': st.get('state_name'),
                    'scalar_f32': float(st.get('scalar_f32')),
                    'selection_kind': st.get('selection_kind'),
                    'animation_list_index': int(a.get('index', -1)),
                })
    if set(states) != set(selected):
        raise ValueError('state-record selected clip coverage drift')
    return erow, target, ci, selected, dict(states)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('input_glb', type=Path)
    ap.add_argument('--entity', required=True)
    ap.add_argument('--model', required=True)
    ap.add_argument('--skeleton', required=True)
    ap.add_argument('--runtime-rig', required=True)
    ap.add_argument('--control', required=True)
    ap.add_argument('--bone-count', type=int, required=True)
    ap.add_argument('--model-report', type=Path, required=True)
    ap.add_argument('--skin-census', type=Path, required=True)
    ap.add_argument('--animation-options', type=Path, required=True)
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--parser-root', type=Path, required=True)
    ap.add_argument('--fps', type=float, default=30.0)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    a = ap.parse_args()

    entity, model, skeleton, rig, control = map(norm, (a.entity, a.model, a.skeleton, a.runtime_rig, a.control))
    mr = model_row(json.loads(a.model_report.read_text()), model)
    sf = one_skin_family(json.loads(a.skin_census.read_text()), model, skeleton, rig, a.bone_count)
    adoc = json.loads(a.animation_options.read_text())
    erow, target, ci, selected_clips, states_by_clip = animation_evidence(adoc, entity, skeleton, rig, control)
    if int(target.get('skeleton_node_count', -1)) != a.bone_count:
        raise ValueError('animation target skeleton count drift')

    cats = load_catalogs(a.member_catalog)
    arc = SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    c = RemoteCorpus(arc, cats, a.runtime)

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
    ver = Game_Version.D1_ROI

    _, sb, ssrc = exact(c, skeleton, ENTITY_RESOURCE_REF)
    sk = read_skeleton(io.BytesIO(sb), ver)
    _, rb, rsrc = exact(c, rig, ENTITY_RESOURCE_REF)
    runtime_rig = read_runtime_rig(io.BytesIO(rb), ver)
    if len(sk.node_defs) != a.bone_count:
        raise ValueError(f'live skeleton nodes {len(sk.node_defs)} != {a.bone_count}')
    live_controls = len(runtime_rig.controls_relations)
    if live_controls != int(target.get('runtime_rig_control_count', -1)):
        raise ValueError(f'live runtime-rig controls {live_controls} != target {target.get("runtime_rig_control_count")}')

    streams = {int(x['mesh_index']): source_stream(c, x, a.bone_count) for x in sf.get('meshes', [])}
    if len(streams) != int(sf.get('mesh_count', -1)):
        raise ValueError('source skin stream coverage drift')

    g = GLTF2().load_binary(str(a.input_glb))
    if len(g.buffers or []) != 1:
        raise ValueError('input GLB must contain exactly one buffer')
    if g.skins is None: g.skins = []
    if g.animations is None: g.animations = []
    if g.skins or g.animations:
        raise ValueError('input geometry GLB is already skinned or animated')
    original_blob = bytes(g.binary_blob() or b'')
    blob = bytearray(original_blob)
    original_nodes = len(g.nodes or [])
    original_meshes = len(g.meshes or [])
    range_by_name = {str(x['name']): x for x in mr.get('ranges', [])}
    if len(range_by_name) != len(mr.get('ranges', [])):
        raise ValueError('duplicate exact range names')

    seen = set(); bind_rows = []; total_bound_vertices = 0; float_error = 0.0
    for gi, gm in enumerate(g.meshes or []):
        if len(gm.primitives) != 1:
            raise ValueError(f'gltf mesh {gi}: expected one primitive')
        ex = gm.extras or {}
        if norm(ex.get('model', model)) != model:
            raise ValueError(f'gltf mesh {gi}: model extra drift')
        rr = range_by_name.get(str(gm.name)) or range_by_name.get(str(gm.name).split('__')[-1])
        if rr is None:
            raise ValueError(f'gltf mesh {gi}: range {gm.name!r} absent from exact report')
        seen.add(str(rr['name']))
        mi = int(ex.get('mesh_index', rr['mesh_index']))
        if mi != int(rr['mesh_index']):
            raise ValueError(f'{rr["name"]}: mesh-index drift')
        prim = gm.primitives[0]
        if prim.attributes.POSITION is None:
            raise ValueError(f'{rr["name"]}: missing POSITION')
        n = int(g.accessors[prim.attributes.POSITION].count)
        src = [int(x) for x in ex.get('source_vertex_indices', [])]
        if len(src) != n or int(rr.get('source_vertex_count', -1)) != n:
            raise ValueError(f'{rr["name"]}: source vertex mapping/count drift')
        if not src or len(set(src)) != len(src):
            raise ValueError(f'{rr["name"]}: source indices absent/duplicated')
        st = streams.get(mi)
        if st is None or min(src) < 0 or max(src) >= int(st['meta']['vertex_count']):
            raise ValueError(f'{rr["name"]}: source vertex index outside exact skin stream')
        joints = st['joints'][src]
        raw = st['raw'][src]
        weights = st['weights'][src]
        sums = np.sum(raw.astype(np.uint16), axis=1, dtype=np.uint16)
        if not np.all(sums == 255):
            raise ValueError(f'{rr["name"]}: raw U8 weight sum drift')
        expected_weights = exact_float32_weights(raw)
        if not np.array_equal(weights.view(np.uint32), expected_weights.view(np.uint32)):
            raise ValueError(f'{rr["name"]}: portable float weight encoding drift')
        fs = np.sum(weights, axis=1, dtype=np.float32)
        err = float(np.max(np.abs(fs - np.float32(1.0)))) if len(fs) else 0.0
        float_error = max(float_error, err)
        prim.attributes.JOINTS_0 = append_accessor(g, blob, joints, component_type=UNSIGNED_SHORT, accessor_type='VEC4', target=ARRAY_BUFFER)
        prim.attributes.WEIGHTS_0 = append_accessor(g, blob, weights, component_type=FLOAT, accessor_type='VEC4', target=ARRAY_BUFFER)
        total_bound_vertices += n
        bind_rows.append({
            'gltf_mesh_index': gi, 'range_name': rr['name'], 'source_mesh_index': mi,
            'vertex_count': n, 'primary_stride': st['stride'], 'skin_modes': st['meta']['mode_counts'],
            'raw_weight_sum_min': int(np.min(sums)), 'raw_weight_sum_max': int(np.max(sums)),
            'float32_weight_sum_abs_error_max': err,
        })
    if seen != set(range_by_name):
        raise ValueError(f'exact range coverage drift {len(seen)}/{len(range_by_name)}')
    if len(g.meshes or []) != len(range_by_name):
        raise ValueError('gltf mesh/range count drift')

    world = [transform_to_np_matrix(x) for x in sk.default_obj_space_tr]
    inv = [transform_to_np_matrix(x) for x in sk.default_inv_obj_space_tr]
    bone_nodes = []; used_names = set()
    for bi, nd in enumerate(sk.node_defs):
        parent = int(nd.parent_node_index)
        mat = inv[parent] @ world[bi] if parent >= 0 else world[bi]
        scale, rot, trans = np_decompose_matrix(mat)
        base = convert_hash_to_bungie_name(int(nd.bone_hash)) or f'{int(nd.bone_hash) & 0xffffffff:08X}'
        name = base if base not in used_names else f'{base}_{int(nd.bone_hash) & 0xffffffff:08X}'
        used_names.add(name)
        idx = len(g.nodes)
        g.nodes.append(Node(
            name=name, children=[], translation=[float(x) for x in trans], rotation=[float(x) for x in rot.as_quat()], scale=[float(x) for x in scale],
            extras={'d1Entity': entity, 'd1Model': model, 'd1Skeleton': skeleton, 'd1RuntimeRig': rig,
                    'd1BoneIndex': bi, 'd1BoneHash': f'{int(nd.bone_hash) & 0xffffffff:08X}'}
        ))
        bone_nodes.append(idx)
    root = len(g.nodes)
    g.nodes.append(Node(
        name=f'D1_{entity}_CROTA_SKELETON_ROOT', children=[], translation=[0,0,0], rotation=[0,0,0,1], scale=[1,1,1],
        extras={'d1Entity': entity, 'd1EntityName': 'Crota, Son of Oryx', 'd1EntityNameHash': '64C53DB9',
                'd1Model': model, 'd1Skeleton': skeleton, 'd1RuntimeRig': rig, 'd1AnimationControl': control,
                'd1DefaultAction': 'UNRESOLVED', 'd1LoopSemantic': 'UNRESOLVED'}
    ))
    for bi, nd in enumerate(sk.node_defs):
        parent = int(nd.parent_node_index)
        if parent >= 0:
            g.nodes[bone_nodes[parent]].children.append(bone_nodes[bi])
        else:
            g.nodes[root].children.append(bone_nodes[bi])
    ib = np.stack([np.asarray(x.T, dtype='<f4') for x in inv], axis=0)
    ibacc = append_accessor(g, blob, ib, component_type=FLOAT, accessor_type='MAT4')
    skin_idx = len(g.skins)
    g.skins.append(Skin(joints=bone_nodes, inverseBindMatrices=ibacc, skeleton=root, name=f'D1_{entity}_{skeleton}_skin'))
    bound_nodes = 0
    for node in g.nodes[:original_nodes]:
        if node.mesh is not None:
            if node.skin is not None:
                raise ValueError('geometry node already has skin')
            node.skin = skin_idx; bound_nodes += 1
    scene = g.scenes[g.scene or 0]
    scene.nodes = list(scene.nodes or []) + [root]

    clip_expected = {norm(x['clip']): x for x in target.get('clips', [])}
    clip_rows = []
    for clip in selected_clips:
        _, cb, csrc = exact(c, clip, CLIP_REF)
        anim = filebacked(read_animation, cb, ver)
        h = anim.animation_header
        exp = clip_expected[clip]
        if int(h.frame_count) != int(exp['frame_count']):
            raise ValueError(f'{clip}: frame-count drift {int(h.frame_count)} != {exp["frame_count"]}')
        decoded = decode_animation(anim)
        retargeted = rig_retarget(anim, decoded, sk, runtime_rig)
        local = convert_obj_to_local(anim, retargeted, sk)
        if (len(decoded), len(retargeted), len(local)) != (live_controls, a.bone_count, a.bone_count):
            raise ValueError(f'{clip}: native retarget dimensions drift')
        samplers = []; channels = []; time_cache = {}
        for bi, track in enumerate(local):
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
                count = int(arr.shape[0])
                if count not in time_cache:
                    times = (np.arange(count, dtype='<f4') / np.float32(a.fps)).astype('<f4')
                    time_cache[count] = append_accessor(g, blob, times, component_type=FLOAT, accessor_type='SCALAR', with_minmax=True)
                vacc = append_accessor(g, blob, arr, component_type=FLOAT, accessor_type=kind)
                si = len(samplers)
                samplers.append(AnimationSampler(input=time_cache[count], output=vacc, interpolation='LINEAR'))
                channels.append(AnimationChannel(sampler=si, target=AnimationChannelTarget(node=bone_nodes[bi], path=path)))
        states = states_by_clip[clip]
        ai = len(g.animations)
        g.animations.append(Animation(
            name=f'D1_CROTA_{clip}', samplers=samplers, channels=channels,
            extras={'d1Entity': entity, 'd1EntityName': 'Crota, Son of Oryx', 'd1OwnerSelectedClip': clip,
                    'd1FrameCount': int(h.frame_count), 'd1FpsTransport': float(a.fps),
                    'd1StateHashes': [x['state_hash'] for x in states],
                    'd1StateNames': [x['state_name'] for x in states],
                    'd1StateScalars': [x['scalar_f32'] for x in states],
                    'd1DefaultState': 'UNRESOLVED', 'd1LoopSemantic': 'UNRESOLVED',
                    'd1SelectionEvidence': 'exact 8108E5C0 selector state table + native retarget v3'}
        ))
        clip_rows.append({'animation_index': ai, 'clip': clip, 'frame_count': int(h.frame_count), 'channel_count': len(channels), 'sampler_count': len(samplers), 'state_records': states, 'source': csrc})
        print('ANIMATION', clip, 'FRAMES', int(h.frame_count), 'CHANNELS', len(channels), 'STATES', len(states), flush=True)

    g.extras = {
        **(g.extras or {}),
        'd1CrotaExactRiggedAnimatedProof': {
            'entity': entity, 'entityName': 'Crota, Son of Oryx', 'entityNameHash': '64C53DB9',
            'model': model, 'skeleton': skeleton, 'runtimeRig': rig, 'animationControl': control,
            'selectedClipCount': len(selected_clips), 'defaultState': 'UNRESOLVED', 'loopSemantic': 'UNRESOLVED',
            'materialTextureSemantics': 'NOT_GUESSED',
            'policy': 'Geometry/material selection, skin, skeleton, rig, and all animations are source-closed independently. Every selector-selected clip is exposed separately; no startup/default playback semantic is inferred.'
        }
    }
    g.buffers[0].byteLength = len(blob)
    g.set_binary_blob(bytes(blob))
    a.out.parent.mkdir(parents=True, exist_ok=True)
    g.save_binary(str(a.out))

    chk = GLTF2().load_binary(str(a.out))
    final_blob = bytes(chk.binary_blob() or b'')
    prefix_exact = final_blob[:len(original_blob)] == original_blob
    if not prefix_exact:
        raise ValueError('input geometry binary chunk is not an exact prefix of final GLB')
    if len(chk.skins or []) != 1 or len((chk.skins or [])[0].joints or []) != a.bone_count:
        raise ValueError('saved skin/joint topology drift')
    if len(chk.animations or []) != len(selected_clips):
        raise ValueError('saved animation count drift')

    out = {
        'schema': 'd1_remote_single_actor_rigged_animated_glb/v1',
        'status': 'D1_SINGLE_ACTOR_RIGGED_ANIMATED_GLB_COMPLETE',
        'entity': entity, 'entity_name_hash': '64C53DB9', 'entity_name': 'Crota, Son of Oryx',
        'model': model, 'skeleton': skeleton, 'skeleton_node_count': a.bone_count,
        'runtime_rig': rig, 'runtime_rig_control_count': live_controls, 'animation_control': control,
        'input_glb': str(a.input_glb), 'output_glb': str(a.out),
        'input_sha256': sha256(a.input_glb), 'output_sha256': sha256(a.out),
        'input_binary_bytes': len(original_blob), 'output_binary_bytes': len(final_blob), 'binary_prefix_exact': True,
        'source_model_mesh_count': int(mr['mesh_count']), 'selected_range_count': len(range_by_name),
        'triangle_count': int(mr['triangle_count']), 'active_materials': mr.get('active_materials', []), 'active_material_count': int(mr.get('active_material_count', -1)),
        'bound_mesh_node_count': bound_nodes, 'bound_vertex_count': total_bound_vertices,
        'skin_index': skin_idx, 'joint_node_count': len(bone_nodes), 'float32_weight_sum_abs_error_max': float_error,
        'skin_bindings': bind_rows,
        'selector_state_count': int(target.get('selector_state_count', -1)),
        'animation_list_entry_count': int(target.get('animation_list_count', -1)),
        'unique_animation_list_clip_count': int(adoc.get('unique_animation_list_clip_count', -1)),
        'selected_clip_count': len(selected_clips), 'selected_clip_hashes': selected_clips,
        'animation_count': len(chk.animations or []), 'animations': clip_rows,
        'native_retarget_success_count': int(target.get('retarget_success_count', -1)),
        'native_retarget_failure_count': int(target.get('retarget_failure_count', -1)),
        'skeleton_source': ssrc, 'runtime_rig_source': rsrc,
        'policy': 'JOINTS/WEIGHTS are exact retail primary-stream values selected by source_vertex_indices; U8 sums are 255 and FLOAT transport is bit-exact U8/255. Hierarchy/inverse binds are exact source skeleton data. Every exact selector-selected clip is decoded and natively retargeted again during export. No default action, state meaning, loop behavior, synchronization behavior, placement, or texture-register-to-PBR semantic is guessed.'
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(out, indent=2) + '\n')
    print('STATUS', out['status'], 'MODEL', model, 'RANGES', out['selected_range_count'], 'TRIANGLES', out['triangle_count'], 'BONES', out['skeleton_node_count'], 'RIG_CONTROLS', out['runtime_rig_control_count'], 'ANIMATIONS', out['animation_count'], 'BOUND_VERTICES', out['bound_vertex_count'], 'SHA', out['output_sha256'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
