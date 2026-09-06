#!/usr/bin/env python3
"""Append exact runtime-rig family skins/actions to an existing Tower articulated GLB.

This is the r9 follow-on to the Family-E r8 builder. It is intentionally scoped to
families whose ownership report is CLOSED and whose skin census has no frontier.
For each selected family it:

* preserves the input GLB binary chunk as an exact prefix;
* reopens the exact retail primary streams and emits bit-exact float32(U8/255)
  JOINTS_0/WEIGHTS_0 without renormalization;
* creates one exact source skeleton/skin per runtime WorldID;
* decodes every selector-selected clip through the pinned production
  decode -> rig_retarget -> local conversion path;
* exposes every selected clip as a separate glTF Animation on every family
  placement when the source owner closes only to a selected action set.

It never chooses a startup/default action, loop behavior, synchronization, actor
identity, or human-readable state name unless that semantic is already exact in the
ownership report. An incompatible or ambiguous clip fails closed.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from pygltflib import GLTF2, Node, Skin, Animation, AnimationSampler, AnimationChannel, AnimationChannelTarget

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_entry_extract import EntryReader
from d1_gltf_bind_rigid_animation import append_accessor
from d1_tower_family_e_animated_layer import (
    norm, entry_map, exact_payload, exact_float32_weights, decode_inline_arrays,
    read_animation_filebacked, ENTITY_RESOURCE_REF, CLIP_REF,
    FLOAT, UNSIGNED_SHORT, ARRAY_BUFFER,
)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(8 << 20), b''):
            h.update(b)
    return h.hexdigest()


def parse_assignment(s: str) -> tuple[str, Path]:
    if '=' not in s:
        raise argparse.ArgumentTypeError('ownership must be FAMILY=path.json')
    fam, path = s.split('=', 1)
    fam = fam.strip().upper()
    if not fam:
        raise argparse.ArgumentTypeError('empty family id')
    return fam, Path(path)


def find_model_row(doc: dict, model: str) -> dict:
    rows = [x for x in doc.get('models', []) if norm(x.get('model', '')) == model]
    if len(rows) != 1:
        raise ValueError(f'{model}: expected one model-report row, got {len(rows)}')
    row = rows[0]
    if int(row.get('stage0_selected_range_count', -1)) != len(row.get('ranges', [])):
        raise ValueError(f'{model}: selected-range count/report row mismatch')
    if int(row.get('geometry_count', -1)) != len(row.get('ranges', [])):
        raise ValueError(f'{model}: geometry-count/report row mismatch')
    if sum(int(x['triangle_count']) for x in row.get('ranges', [])) != int(row.get('triangle_count', -1)):
        raise ValueError(f'{model}: triangle total/report row mismatch')
    return row


def find_skin_family(doc: dict, model: str, skeleton: str, rig: str, bone_count: int, placements: int) -> dict:
    rows = []
    for f in doc.get('families', []):
        models = [norm(x) for x in f.get('models', [])]
        if norm(f.get('model', '')) == model or model in models:
            rows.append(f)
    if len(rows) != 1:
        raise ValueError(f'{model}: expected one skin-census family, got {len(rows)}')
    f = rows[0]
    if f.get('violations') or f.get('frontiers'):
        raise ValueError(f'{model}: skin family not closed: violations={f.get("violations")} frontiers={f.get("frontiers")}')
    if f.get('bone_counts') != [bone_count]:
        raise ValueError(f'{model}: skin bone-count drift {f.get("bone_counts")} != {[bone_count]}')
    if [norm(x) for x in f.get('skeleton_resources', [])] != [skeleton]:
        raise ValueError(f'{model}: skin skeleton drift')
    if [norm(x) for x in f.get('runtime_rig_resources', [])] != [rig]:
        raise ValueError(f'{model}: skin runtime-rig drift')
    if int(f.get('runtime_placement_count', -1)) != placements:
        raise ValueError(f'{model}: skin placement-count drift')
    return f


def decode_family_streams(r: EntryReader, skin_family: dict, bone_count: int) -> dict[int, dict]:
    by = entry_map(r)
    out = {}
    for m in skin_family.get('meshes', []):
        mi = int(m['mesh_index'])
        if norm(m.get('old_weights', 'FFFFFFFF')) != 'FFFFFFFF':
            raise ValueError(f'mesh {mi}: separate OldWeights is not closed for this builder')
        ps = m.get('primary_stream') or {}
        header_tag = norm(ps.get('hash'))
        backing_tag = norm(ps.get('backing_hash') or ps.get('backing'))
        stride = int(m['primary_stride'])
        he, hb = exact_payload(r, by, header_tag)
        if norm(he['reference']) != backing_tag:
            raise ValueError(f'mesh {mi}: primary header {header_tag} reference {norm(he["reference"])} != {backing_tag}')
        actual_stride = int.from_bytes(hb[4:6], 'little', signed=True)
        if actual_stride != stride:
            raise ValueError(f'mesh {mi}: source stride {actual_stride} != census {stride}')
        be, payload = exact_payload(r, by, backing_tag)
        joints, raw_weights, weights, meta = decode_inline_arrays(payload, stride, bone_count)
        expected = m.get('skin') or {}
        if int(expected.get('vertex_count', -1)) != meta['vertex_count']:
            raise ValueError(f'mesh {mi}: vertex-count drift')
        if dict(expected.get('mode_counts') or {}) != meta['mode_counts']:
            raise ValueError(f'mesh {mi}: skin mode-count drift {meta["mode_counts"]} != {expected.get("mode_counts")}')
        if [int(x) for x in expected.get('bone_domain', [])] != meta['bone_domain']:
            raise ValueError(f'mesh {mi}: skin bone-domain drift')
        if (expected.get('weight_sum_min'), expected.get('weight_sum_max')) != (255, 255):
            raise ValueError(f'mesh {mi}: census raw-weight invariant not exact 255')
        out[mi] = {
            'joints': joints, 'raw_weights': raw_weights, 'weights': weights, 'meta': meta,
            'header_tag': header_tag, 'backing_tag': backing_tag,
            'header_entry_index': int(he['index']), 'backing_entry_index': int(be['index']),
            'backing_size': int(be['file_size']),
        }
    return out


def ownership_info(fam_id: str, path: Path) -> dict:
    d = json.loads(path.read_text())
    expected_status = f'D1_TOWER_FAMILY_{fam_id}_ANIMATION_OWNER_CONTROL_CLOSED'
    if d.get('status') != expected_status or d.get('violations'):
        raise ValueError(f'Family {fam_id}: ownership report is not CLOSED: {d.get("status")} {d.get("violations")}')
    if d.get('selection_status') != 'owner_control_selected_set_closed':
        raise ValueError(f'Family {fam_id}: selected-set closure missing')
    f = d.get('family') or {}
    model = norm(f.get('entity_model'))
    skeleton = norm(f.get('skeleton_resource'))
    rig = norm(f.get('runtime_rig_resource'))
    bone_count = int(f.get('skeleton_node_count', -1))
    control_count = int(f.get('runtime_rig_control_count', -1))
    placements = int(f.get('runtime_placement_count', -1))
    if placements != int(f.get('unique_world_id_count', -2)):
        raise ValueError(f'Family {fam_id}: WorldID count is not unique')
    selected = [norm(x) for x in d.get('unique_selected_clip_hashes', [])]
    if not selected:
        raise ValueError(f'Family {fam_id}: empty selected clip set')
    for clip in selected:
        row = (d.get('clips') or {}).get(clip)
        if not row or not row.get('exact_family_compatible'):
            raise ValueError(f'Family {fam_id}: selected clip {clip} is not exact-family-compatible')
    world_to_entity = {}
    for entity, row in (d.get('entities') or {}).items():
        for wid in row.get('world_ids', []):
            wid = str(wid).upper()
            if wid in world_to_entity:
                raise ValueError(f'Family {fam_id}: duplicate WorldID {wid}')
            world_to_entity[wid] = norm(entity)
    if len(world_to_entity) != placements:
        raise ValueError(f'Family {fam_id}: entity report yielded {len(world_to_entity)} WorldIDs != {placements}')

    states_by_clip = defaultdict(list)
    control = d.get('animation_control') or {}
    for state in (control.get('state_table') or {}).get('records', []):
        for x in state.get('selected_animations', []):
            clip = norm(x.get('tag_hash'))
            if clip in selected:
                states_by_clip[clip].append({
                    'state_hash': str(state.get('state_hash')).upper(),
                    'state_name': state.get('state_name'),
                    'scalar_f32': float(state.get('scalar_f32')),
                    'selection_kind': state.get('selection_kind'),
                })
    if set(states_by_clip) != set(selected):
        raise ValueError(f'Family {fam_id}: selected clip/state coverage drift')
    return {
        'id': fam_id, 'doc': d, 'path': str(path), 'model': model, 'skeleton': skeleton, 'rig': rig,
        'bone_count': bone_count, 'control_count': control_count, 'placements': placements,
        'selected_clips': sorted(selected), 'world_to_entity': world_to_entity,
        'states_by_clip': {k: v for k, v in states_by_clip.items()},
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('input_glb', type=Path)
    ap.add_argument('--model-report', type=Path, required=True)
    ap.add_argument('--skin-census', type=Path, required=True)
    ap.add_argument('--ownership', action='append', type=parse_assignment, required=True,
                    help='repeat FAMILY=closed_ownership.json')
    ap.add_argument('--activity-pkg', type=Path, required=True)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--parser-root', type=Path, required=True)
    ap.add_argument('--fps', type=float, default=30.0)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    a = ap.parse_args()

    assignments = dict(a.ownership)
    if len(assignments) != len(a.ownership):
        raise ValueError('duplicate --ownership family')
    if not assignments:
        raise ValueError('no families selected')

    model_doc = json.loads(a.model_report.read_text())
    if model_doc.get('status') != 'D1_WORLD_ARTICULATED_MODEL_SET_COMPLETE':
        raise ValueError('model report is not complete')
    skin_doc = json.loads(a.skin_census.read_text())
    if skin_doc.get('violations'):
        raise ValueError('skin census has global violations')

    families = [ownership_info(fid, path) for fid, path in sorted(assignments.items())]
    activity = EntryReader(a.activity_pkg, a.runtime)
    aby = entry_map(activity)

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

    # Load and pin the existing animated articulated checkpoint.
    g = GLTF2().load_binary(str(a.input_glb))
    if len(g.buffers) != 1:
        raise ValueError(f'expected one-buffer GLB, got {len(g.buffers)}')
    if g.skins is None: g.skins = []
    if g.animations is None: g.animations = []
    original_blob = bytes(g.binary_blob() or b'')
    blob = bytearray(original_blob)
    original_counts = {
        'accessors': len(g.accessors or []), 'bufferViews': len(g.bufferViews or []),
        'meshes': len(g.meshes or []), 'nodes': len(g.nodes or []),
        'materials': len(g.materials or []), 'textures': len(g.textures or []), 'images': len(g.images or []),
        'skins': len(g.skins), 'animations': len(g.animations), 'binary_bytes': len(original_blob),
    }
    if (original_counts['meshes'], original_counts['nodes'], original_counts['materials'],
        original_counts['textures'], original_counts['images'], original_counts['skins'],
        original_counts['animations']) != (86, 740, 35, 70, 70, 6, 6):
        raise ValueError(f'input is not exact Family-E animated r8 topology: {original_counts}')

    scene_idx = g.scene or 0
    scene_roots = list(g.scenes[scene_idx].nodes or [])
    family_reports = {}
    total_new_nodes = total_new_skins = total_new_animations = 0
    global_float_error = 0.0

    for fam in families:
        fid = fam['id']; model = fam['model']; skeleton_tag = fam['skeleton']; rig_tag = fam['rig']
        bone_count = fam['bone_count']; control_count = fam['control_count']
        model_row = find_model_row(model_doc, model)
        ranges = model_row.get('ranges', [])
        range_by_name = {str(x['name']): x for x in ranges}
        if len(range_by_name) != len(ranges):
            raise ValueError(f'Family {fid}: duplicate model range name')
        skin_family = find_skin_family(skin_doc, model, skeleton_tag, rig_tag, bone_count, fam['placements'])
        streams = decode_family_streams(activity, skin_family, bone_count)

        _, skb = exact_payload(activity, aby, skeleton_tag, ENTITY_RESOURCE_REF)
        sk = read_skeleton(io.BytesIO(skb), ver)
        _, rb = exact_payload(activity, aby, rig_tag, ENTITY_RESOURCE_REF)
        rig = read_runtime_rig(io.BytesIO(rb), ver)
        if (len(sk.node_defs), len(rig.controls_relations)) != (bone_count, control_count):
            raise ValueError(f'Family {fid}: live skeleton/rig dimension drift')

        # Decode selected clips through the exact production retarget path.
        clip_cache = {}
        for clip in fam['selected_clips']:
            _, cb = exact_payload(activity, aby, clip, CLIP_REF)
            anim = read_animation_filebacked(read_animation, cb, ver)
            h = anim.animation_header
            expected = fam['doc']['clips'][clip]
            if (int(h.frame_count), int(h.node_count), int(h.rig_control_count)) != (
                int(expected['frame_count']), bone_count, control_count
            ):
                raise ValueError(f'Family {fid} clip {clip}: live header drift')
            decoded = decode_animation(anim)
            retargeted = rig_retarget(anim, decoded, sk, rig)
            local = convert_obj_to_local(anim, retargeted, sk)
            if (len(decoded), len(retargeted), len(local)) != (control_count, bone_count, bone_count):
                raise ValueError(f'Family {fid} clip {clip}: production retarget dimensions drift')
            clip_cache[clip] = {
                'animation': anim, 'header': h, 'decoded': decoded, 'retargeted': retargeted,
                'local': local, 'frame_count': int(h.frame_count),
            }

        # Add exact skin attributes to this family's shared glTF range meshes.
        family_mesh_indices = []
        seen_ranges = set()
        bind_rows = []
        family_float_error = 0.0
        unique_triangles = 0
        for gi, mesh in enumerate(g.meshes):
            if norm((mesh.extras or {}).get('model', '')) != model:
                continue
            family_mesh_indices.append(gi)
            if len(mesh.primitives) != 1:
                raise ValueError(f'Family {fid} mesh {gi}: expected one primitive')
            prim = mesh.primitives[0]
            if prim.attributes.JOINTS_0 is not None or prim.attributes.WEIGHTS_0 is not None:
                raise ValueError(f'Family {fid} mesh {gi}: skin attributes already present')
            range_name = str(mesh.name).split('__')[-1]
            rr = range_by_name.get(range_name)
            if rr is None:
                raise ValueError(f'Family {fid} mesh {gi}: range {range_name} absent from model report')
            seen_ranges.add(range_name)
            mi = int((mesh.extras or {}).get('mesh_index'))
            if mi != int(rr['mesh_index']):
                raise ValueError(f'Family {fid} {range_name}: source mesh index drift')
            src_indices = [int(x) for x in (mesh.extras or {}).get('source_vertex_indices', [])]
            pos_count = int(g.accessors[prim.attributes.POSITION].count)
            if len(src_indices) != pos_count or int(rr['source_vertex_count']) != pos_count:
                raise ValueError(f'Family {fid} {range_name}: source-index/POSITION/report count mismatch')
            if not src_indices or len(set(src_indices)) != len(src_indices):
                raise ValueError(f'Family {fid} {range_name}: source vertex indices absent or duplicated')
            stream = streams.get(mi)
            if stream is None or min(src_indices) < 0 or max(src_indices) >= stream['meta']['vertex_count']:
                raise ValueError(f'Family {fid} {range_name}: source vertex index outside exact stream')
            joints = stream['joints'][src_indices]
            raw_weights = stream['raw_weights'][src_indices]
            weights = stream['weights'][src_indices]
            raw_sums = np.sum(raw_weights.astype(np.uint16), axis=1, dtype=np.uint16)
            if not np.all(raw_sums == 255):
                raise ValueError(f'Family {fid} {range_name}: raw U8 weight sum drift')
            expected_weights = exact_float32_weights(raw_weights)
            if not np.array_equal(weights.view(np.uint32), expected_weights.view(np.uint32)):
                raise ValueError(f'Family {fid} {range_name}: float32 weight encoding drift')
            float_sums = np.sum(weights, axis=1, dtype=np.float32)
            err = float(np.max(np.abs(float_sums - np.float32(1.0)))) if len(float_sums) else 0.0
            family_float_error = max(family_float_error, err); global_float_error = max(global_float_error, err)
            prim.attributes.JOINTS_0 = append_accessor(g, blob, joints, component_type=UNSIGNED_SHORT, accessor_type='VEC4', target=ARRAY_BUFFER)
            prim.attributes.WEIGHTS_0 = append_accessor(g, blob, weights, component_type=FLOAT, accessor_type='VEC4', target=ARRAY_BUFFER)
            tri_count = int(g.accessors[prim.indices].count) // 3
            if int(g.accessors[prim.indices].count) % 3 or tri_count != int(rr['triangle_count']):
                raise ValueError(f'Family {fid} {range_name}: triangle-count drift')
            unique_triangles += tri_count
            bind_rows.append({
                'gltf_mesh_index': gi, 'range_name': range_name, 'source_mesh_index': mi,
                'source_vertex_count': pos_count, 'triangle_count': tri_count,
                'primary_stride': stream['meta']['stride'], 'skin_modes': stream['meta']['mode_counts'],
                'raw_u8_weight_sum_min': int(np.min(raw_sums)), 'raw_u8_weight_sum_max': int(np.max(raw_sums)),
                'float32_weight_sum_abs_error_max': err,
                'float32_conversion_bit_exact': True, 'portable_float_renormalized': False,
            })
        if len(family_mesh_indices) != len(ranges) or seen_ranges != set(range_by_name):
            raise ValueError(f'Family {fid}: glTF range coverage mismatch {len(family_mesh_indices)}/{len(ranges)}')
        if unique_triangles != int(model_row['triangle_count']):
            raise ValueError(f'Family {fid}: unique triangle total drift')

        # Recover exact existing placement geometry nodes before appending new nodes.
        placement_nodes = defaultdict(list)
        for ni, node in enumerate(g.nodes[:original_counts['nodes']]):
            ex = node.extras or {}
            if norm(ex.get('d1Model', '')) == model:
                wid = str(ex.get('d1WorldID', '')).upper()
                placement_nodes[wid].append(ni)
        if set(placement_nodes) != set(fam['world_to_entity']):
            raise ValueError(f'Family {fid}: GLB/ownership WorldID mismatch')
        for wid, nodes in placement_nodes.items():
            if len(nodes) != len(ranges):
                raise ValueError(f'Family {fid} {wid}: geometry-node count {len(nodes)} != ranges {len(ranges)}')
            matrices = [g.nodes[n].matrix for n in nodes]
            if any(m is None for m in matrices) or any(m != matrices[0] for m in matrices[1:]):
                raise ValueError(f'Family {fid} {wid}: placement matrices disagree')
            entities = {norm((g.nodes[n].extras or {}).get('d1Entity')) for n in nodes}
            if entities != {fam['world_to_entity'][wid]}:
                raise ValueError(f'Family {fid} {wid}: GLB/entity ownership mismatch')

        # Build bind hierarchy once numerically, then instantiate per placement.
        world_bind = [transform_to_np_matrix(x) for x in sk.default_obj_space_tr]
        inv_world = [transform_to_np_matrix(x) for x in sk.default_inv_obj_space_tr]
        local_bind = []
        bone_base_names = []
        for bi, nd in enumerate(sk.node_defs):
            parent = int(nd.parent_node_index)
            mat = inv_world[parent] @ world_bind[bi] if parent >= 0 else world_bind[bi]
            scale, rot, trans = np_decompose_matrix(mat)
            local_bind.append(([float(x) for x in trans], [float(x) for x in rot.as_quat()], [float(x) for x in scale]))
            bone_base_names.append(convert_hash_to_bungie_name(int(nd.bone_hash)) or f'{int(nd.bone_hash) & 0xffffffff:08X}')
        inv_bind = np.stack([np.asarray(m.T, dtype='<f4') for m in inv_world], axis=0)
        ibm_acc = append_accessor(g, blob, inv_bind, component_type=FLOAT, accessor_type='MAT4')

        placement_bones = {}; placement_skin = {}; placement_root = {}
        for wid in sorted(fam['world_to_entity']):
            entity = fam['world_to_entity'][wid]
            geom_nodes = placement_nodes[wid]
            matrix = [float(x) for x in g.nodes[geom_nodes[0]].matrix]
            bones = []; used_names = set()
            for bi, nd in enumerate(sk.node_defs):
                base = bone_base_names[bi]
                name = base if base not in used_names else f'{base}_{int(nd.bone_hash) & 0xffffffff:08X}'
                used_names.add(name)
                trans, rot, scale = local_bind[bi]
                idx = len(g.nodes)
                g.nodes.append(Node(
                    name=f'D1_FAM_{fid}_{wid}_{name}', children=[], translation=trans, rotation=rot, scale=scale,
                    extras={'d1WorldID': wid, 'd1Entity': entity, 'd1Model': model,
                            'd1Skeleton': skeleton_tag, 'd1RuntimeRig': rig_tag,
                            'd1BoneIndex': bi, 'd1BoneHash': f'{int(nd.bone_hash) & 0xffffffff:08X}'}
                ))
                bones.append(idx)
            root_idx = len(g.nodes)
            g.nodes.append(Node(
                name=f'D1_FAM_{fid}_{wid}_SKELETON_ROOT', children=[], matrix=matrix,
                extras={'d1WorldID': wid, 'd1Entity': entity, 'd1Model': model,
                        'd1Skeleton': skeleton_tag, 'd1RuntimeRig': rig_tag,
                        'd1SelectedActionSet': list(fam['selected_clips']),
                        'd1DefaultAction': 'UNRESOLVED',
                        'd1PlacementMatrixSource': 'existing articulated GLB geometry nodes'}
            ))
            for bi, nd in enumerate(sk.node_defs):
                parent = int(nd.parent_node_index)
                if parent >= 0:
                    g.nodes[bones[parent]].children.append(bones[bi])
                else:
                    g.nodes[root_idx].children.append(bones[bi])
            skin_idx = len(g.skins)
            g.skins.append(Skin(joints=bones, inverseBindMatrices=ibm_acc, skeleton=root_idx,
                                name=f'D1_FAM_{fid}_{wid}_{skeleton_tag}_skin'))
            for ni in geom_nodes:
                if g.nodes[ni].skin is not None:
                    raise ValueError(f'Family {fid} {wid}: geometry node {ni} already skinned')
                g.nodes[ni].skin = skin_idx
            scene_roots.append(root_idx)
            placement_bones[wid] = bones; placement_skin[wid] = skin_idx; placement_root[wid] = root_idx

        # Append clip channel accessors once per unique clip, then instantiate one
        # Animation object per WorldID x selected action. This exposes source states
        # without implying a default or simultaneous playback.
        clip_templates = {}; clip_binary = {}
        for clip, c in clip_cache.items():
            templates = []; time_cache = {}
            for bi, track in enumerate(c['local']):
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
                        times = (np.arange(count, dtype='<f4') / float(a.fps)).astype('<f4')
                        time_cache[count] = append_accessor(g, blob, times, component_type=FLOAT, accessor_type='SCALAR', with_minmax=True)
                    vacc = append_accessor(g, blob, arr, component_type=FLOAT, accessor_type=kind)
                    templates.append((bi, path, time_cache[count], vacc, count))
            clip_templates[clip] = templates
            clip_binary[clip] = {
                'frame_count': c['frame_count'], 'template_channel_count': len(templates),
                'decoded_track_count': len(c['decoded']), 'retargeted_track_count': len(c['retargeted']),
                'local_track_count': len(c['local']), 'states': fam['states_by_clip'][clip],
            }

        animation_rows = []
        for wid in sorted(fam['world_to_entity']):
            entity = fam['world_to_entity'][wid]; bones = placement_bones[wid]
            for clip in fam['selected_clips']:
                samplers = []; channels = []
                for bi, path, tacc, vacc, _count in clip_templates[clip]:
                    si = len(samplers)
                    samplers.append(AnimationSampler(input=tacc, output=vacc, interpolation='LINEAR'))
                    channels.append(AnimationChannel(sampler=si, target=AnimationChannelTarget(node=bones[bi], path=path)))
                states = fam['states_by_clip'][clip]
                anim_idx = len(g.animations)
                g.animations.append(Animation(
                    name=f'D1_FAM_{fid}_{wid}_{clip}', samplers=samplers, channels=channels,
                    extras={
                        'd1WorldID': wid, 'd1Entity': entity, 'd1Model': model,
                        'd1Skeleton': skeleton_tag, 'd1RuntimeRig': rig_tag,
                        'd1OwnerSelectedClip': clip, 'd1FrameCount': clip_cache[clip]['frame_count'],
                        'd1Fps': float(a.fps),
                        'd1StateHashes': [x['state_hash'] for x in states],
                        'd1StateNames': [x['state_name'] for x in states],
                        'd1DefaultState': 'UNRESOLVED', 'd1LoopSemantic': 'UNRESOLVED',
                        'd1SelectionEvidence': fam['doc']['status'],
                    }
                ))
                animation_rows.append({
                    'animation_index': anim_idx, 'world_id': wid, 'entity': entity, 'clip': clip,
                    'frame_count': clip_cache[clip]['frame_count'], 'state_records': states,
                    'channel_count': len(channels), 'sampler_count': len(samplers),
                    'skin_index': placement_skin[wid], 'skeleton_root_node': placement_root[wid],
                })

        fam_new_nodes = fam['placements'] * (bone_count + 1)
        fam_new_skins = fam['placements']
        fam_new_anims = fam['placements'] * len(fam['selected_clips'])
        total_new_nodes += fam_new_nodes; total_new_skins += fam_new_skins; total_new_animations += fam_new_anims
        family_reports[fid] = {
            'ownership_report': fam['path'], 'ownership_status': fam['doc']['status'],
            'model': model, 'skeleton': skeleton_tag, 'skeleton_node_count': bone_count,
            'runtime_rig': rig_tag, 'runtime_rig_control_count': control_count,
            'runtime_placement_count': fam['placements'], 'world_ids': sorted(fam['world_to_entity']),
            'selected_clip_hashes': fam['selected_clips'], 'states_by_clip': fam['states_by_clip'],
            'source_mesh_count': int(model_row['mesh_count']), 'selected_range_count': len(ranges),
            'unique_triangle_count': unique_triangles,
            'placement_geometry_node_count': fam['placements'] * len(ranges),
            'source_streams': {str(mi): {k: v[k] for k in ('meta','header_tag','backing_tag','header_entry_index','backing_entry_index','backing_size')} for mi,v in sorted(streams.items())},
            'mesh_bindings': bind_rows, 'float32_weight_sum_abs_error_max': family_float_error,
            'clip_decode': clip_binary, 'animations': animation_rows,
            'new_nodes': fam_new_nodes, 'new_skins': fam_new_skins, 'new_animations': fam_new_anims,
        }

    g.scenes[scene_idx].nodes = scene_roots
    g.extras = {
        **(g.extras or {}),
        'd1TowerRuntimeRigAnimatedR9Proof': {
            'families': sorted(family_reports),
            'inputCheckpoint': 'Family-E animated r8 articulated layer',
            'rawWeightInvariant': 'four U8 lanes sum exactly 255',
            'floatWeightEncoding': 'bit-exact float32(raw_u8/255), never renormalized',
            'defaultState': 'UNRESOLVED', 'loopSemantic': 'UNRESOLVED', 'synchronizationSemantic': 'UNRESOLVED',
            'policy': 'Every selector-selected action is exported separately per source-owned placement. No default action or playback semantic is inferred.'
        }
    }
    g.buffers[0].byteLength = len(blob)
    g.set_binary_blob(bytes(blob))
    a.out.parent.mkdir(parents=True, exist_ok=True)
    g.save_binary(str(a.out))

    outg = GLTF2().load_binary(str(a.out))
    final_blob = bytes(outg.binary_blob() or b'')
    prefix_exact = final_blob[:len(original_blob)] == original_blob
    final_counts = {
        'accessors': len(outg.accessors or []), 'bufferViews': len(outg.bufferViews or []),
        'meshes': len(outg.meshes or []), 'nodes': len(outg.nodes or []),
        'materials': len(outg.materials or []), 'textures': len(outg.textures or []), 'images': len(outg.images or []),
        'skins': len(outg.skins or []), 'animations': len(outg.animations or []), 'binary_bytes': len(final_blob),
    }
    if not prefix_exact:
        raise ValueError('input r8 binary chunk is not an exact prefix after r9 append')
    if (final_counts['meshes'], final_counts['materials'], final_counts['textures'], final_counts['images']) != (
        original_counts['meshes'], original_counts['materials'], original_counts['textures'], original_counts['images']
    ):
        raise ValueError(f'visual resource counts changed unexpectedly: {original_counts} -> {final_counts}')
    if final_counts['nodes'] != original_counts['nodes'] + total_new_nodes:
        raise ValueError(f'node count drift: {final_counts["nodes"]} != {original_counts["nodes"]}+{total_new_nodes}')
    if final_counts['skins'] != original_counts['skins'] + total_new_skins:
        raise ValueError('skin count drift')
    if final_counts['animations'] != original_counts['animations'] + total_new_animations:
        raise ValueError('animation count drift')

    # Prove every selected family geometry node is skinned and every appended action targets valid nodes.
    for fid, fr in family_reports.items():
        model = fr['model']
        meshes = [m for m in outg.meshes if norm((m.extras or {}).get('model', '')) == model]
        if len(meshes) != fr['selected_range_count'] or any(
            p.attributes.JOINTS_0 is None or p.attributes.WEIGHTS_0 is None for m in meshes for p in m.primitives
        ):
            raise ValueError(f'Family {fid}: output mesh skin attributes incomplete')
        nodes = [n for n in outg.nodes[:original_counts['nodes']] if norm((n.extras or {}).get('d1Model', '')) == model]
        if len(nodes) != fr['placement_geometry_node_count'] or any(n.skin is None for n in nodes):
            raise ValueError(f'Family {fid}: output placement geometry skin assignment incomplete')

    rep = {
        'schema_version': 1,
        'status': 'D1_TOWER_RUNTIME_RIG_FAMILIES_ANIMATED_R9_COMPLETE',
        'input': str(a.input_glb), 'input_sha256': sha256_file(a.input_glb),
        'output': str(a.out), 'output_bytes': a.out.stat().st_size, 'output_sha256': sha256_file(a.out),
        'families': family_reports,
        'raw_u8_weight_sum_exact_255': True,
        'float32_conversion_bit_exact': True,
        'portable_float_weights_renormalized': False,
        'float32_weight_sum_abs_error_max': global_float_error,
        'original_counts': original_counts, 'final_counts': final_counts,
        'input_binary_exact_prefix': prefix_exact,
        'state_default_proven': False, 'loop_semantics_proven': False, 'synchronization_semantics_proven': False,
        'policy': 'The exact Family-E animated r8 layer is retained and F/G are appended from exact retail skin streams, skeletons, runtime rigs, owner-selected action sets, and production retargeting. Multiple selected actions remain separate glTF animations. No default/loop/synchronization/actor semantic is inferred.',
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(rep, indent=2) + '\n')
    print(json.dumps({
        'status': rep['status'], 'output_bytes': rep['output_bytes'], 'output_sha256': rep['output_sha256'],
        'families': {k: {x:v[x] for x in ('runtime_placement_count','selected_clip_hashes','selected_range_count','unique_triangle_count','new_nodes','new_skins','new_animations')} for k,v in family_reports.items()},
        'original_counts': original_counts, 'final_counts': final_counts,
        'input_binary_exact_prefix': prefix_exact,
        'float32_weight_sum_abs_error_max': global_float_error,
    }, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
