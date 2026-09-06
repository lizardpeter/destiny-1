#!/usr/bin/env python3
"""Skin and animate the six source-owned D1 Tower Family-E placements.

This tool is deliberately scoped to the already-closed Tower 67-bone family:

    EntityModel 80CA0CFC
    skeleton    809D8613
    runtime rig 809D856E

It starts from the proven articulated Tower GLB.  The GLB already preserves each
selected retail draw range plus the exact source vertex-index list in mesh extras.
For the 26 shared Family-E meshes we reopen the exact 00EC retail primary streams,
decode only the project-closed D1 inline skin forms, and append JOINTS_0/WEIGHTS_0.

Each of the six existing WorldID placements receives its own 67-joint skeleton at
the exact existing placement matrix.  The clip for that skeleton is selected only
from a CLOSED d1_tower_family_e_animation_ownership report.  This currently means
one Tower-local 80C7AE98 placement and five 809D8572 placements.

No NPC/vendor label, state name, loop behavior, synchronization behavior, missing
weight, or animation is inferred.  Six separate glTF Animation objects are emitted
so the export does not imply that the game starts all six clips simultaneously.

Retail skin weights remain authoritative as U8 values whose four lanes sum exactly
255.  glTF FLOAT weights are a transport encoding only: every emitted float32 lane
must be bit-identical to float32(raw_u8 / 255).  The tool never renormalizes those
float values merely to force their floating-point accumulation to equal 1.0.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import struct
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from pygltflib import (
    GLTF2, Node, Skin, Animation, AnimationSampler, AnimationChannel,
    AnimationChannelTarget,
)

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from d1_entry_extract import EntryReader
from d1_gltf_bind_rigid_animation import append_accessor

MODEL = '80CA0CFC'
SKELETON = '809D8613'
RIG = '809D856E'
ENTITY_RESOURCE_REF = '80800861'
CLIP_REF = '808005A1'
FLOAT = 5126
UNSIGNED_SHORT = 5123
ARRAY_BUFFER = 34962
SENTINELS = {32767, -32767}


def norm(x) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(8 << 20), b''):
            h.update(b)
    return h.hexdigest()


def entry_map(r: EntryReader) -> dict[str, dict]:
    return {norm(e['tag_hash']): e for e in r.entries}


def exact_payload(r: EntryReader, by: dict[str, dict], tag: str,
                  expected_ref: str | None = None) -> tuple[dict, bytes]:
    tag = norm(tag)
    e = by.get(tag)
    if e is None:
        raise ValueError(f'{tag}: absent from package {int(r.h["pkg_id"]):04X}')
    if expected_ref is not None and norm(e['reference']) != norm(expected_ref):
        raise ValueError(f'{tag}: reference {norm(e["reference"])} != {norm(expected_ref)}')
    if not r.available(e['index']):
        raise ValueError(f'{tag}: payload unavailable in package {int(r.h["pkg_id"]):04X}')
    return e, r.entry(e['index'])


def exact_float32_weights(raw_weights: np.ndarray) -> np.ndarray:
    """Return the exact portable float32 encoding of retail U8/255 weights.

    This function deliberately does not renormalize.  The authoritative invariant
    is the source U8 sum of 255, not a mathematically exact float32 sum of 1.0.
    """
    raw = np.asarray(raw_weights, dtype=np.uint8)
    if raw.ndim != 2 or raw.shape[1] != 4:
        raise ValueError(f'raw weight array must be Nx4 U8, got {raw.shape}')
    sums = np.sum(raw.astype(np.uint16), axis=1, dtype=np.uint16)
    if not np.all(sums == 255):
        bad = np.flatnonzero(sums != 255)
        i = int(bad[0]) if len(bad) else -1
        raise ValueError(f'raw U8 weight sum drift at row {i}: {int(sums[i]) if i >= 0 else None}')
    return (raw.astype(np.float32) / np.float32(255.0)).astype('<f4', copy=False)


def decode_inline_arrays(payload: bytes, stride: int, bone_count: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    """Decode only retail-closed D1 primary-stream skin forms."""
    if stride not in (0x08, 0x0C, 0x10):
        raise ValueError(f'unsupported D1 inline skin stride 0x{stride:X}')
    if len(payload) % stride:
        raise ValueError(f'payload size {len(payload)} not divisible by stride 0x{stride:X}')
    n = len(payload) // stride
    joints = np.zeros((n, 4), dtype='<u2')
    raw_weights = np.zeros((n, 4), dtype=np.uint8)
    modes = Counter()
    domain = set()
    sums = []
    for vi in range(n):
        off = vi * stride
        wpos = struct.unpack_from('<h', payload, off + 6)[0]
        if stride == 0x08:
            if wpos in SENTINELS or wpos < 0:
                raise ValueError(f'vertex {vi}: invalid rigid lane3 joint {wpos} for stride 0x08')
            inds = [wpos, 0, 0, 0]
            vals = [255, 0, 0, 0]
            modes['rigid_lane3'] += 1
        elif stride == 0x0C:
            if wpos in SENTINELS:
                inds = list(payload[off + 8:off + 10]) + [0, 0]
                vals = list(payload[off + 10:off + 12]) + [0, 0]
                modes['inline2'] += 1
            elif wpos >= 0:
                inds = [wpos, 0, 0, 0]
                vals = [255, 0, 0, 0]
                modes['rigid_lane3'] += 1
            else:
                raise ValueError(f'vertex {vi}: negative non-sentinel lane3 joint {wpos}')
        else:
            vals = list(payload[off + 8:off + 12])
            inds = list(payload[off + 12:off + 16])
            modes['inline4'] += 1
        total = sum(vals)
        sums.append(total)
        if total != 255:
            raise ValueError(f'vertex {vi}: raw weight sum {total} != 255; indices={inds} weights={vals}')
        for k, (joint, weight) in enumerate(zip(inds, vals)):
            if weight == 0:
                continue
            if not 0 <= int(joint) < bone_count:
                raise ValueError(f'vertex {vi}: joint {joint} outside skeleton {bone_count}')
            joints[vi, k] = int(joint)
            domain.add(int(joint))
        raw_weights[vi] = np.asarray(vals, dtype=np.uint8)
    weights = exact_float32_weights(raw_weights)
    float_sums = np.sum(weights, axis=1, dtype=np.float32)
    float_errors = np.abs(float_sums - np.float32(1.0))
    meta = {
        'vertex_count': n,
        'stride': stride,
        'mode_counts': dict(modes),
        'bone_domain': sorted(domain),
        'weight_sum_min': min(sums) if sums else None,
        'weight_sum_max': max(sums) if sums else None,
        'float32_weight_sum_min': float(np.min(float_sums)) if n else None,
        'float32_weight_sum_max': float(np.max(float_sums)) if n else None,
        'float32_weight_sum_abs_error_max': float(np.max(float_errors)) if n else 0.0,
        'float_encoding': 'bit_exact_float32(raw_u8 / 255); no renormalization',
    }
    return joints, raw_weights, weights, meta


def family_skin_row(doc: dict) -> dict:
    if doc.get('violations'):
        raise ValueError('skin census has global violations')
    rows = [f for f in doc.get('families', []) if norm(f.get('model', '')) == MODEL or
            [norm(x) for x in f.get('models', [])] == [MODEL]]
    if len(rows) != 1:
        raise ValueError(f'expected one {MODEL} skin family, got {len(rows)}')
    f = rows[0]
    if f.get('violations') or f.get('frontiers'):
        raise ValueError(f'{MODEL}: skin census is not closed: violations={f.get("violations")} frontiers={f.get("frontiers")}')
    if f.get('bone_counts') != [67] or [norm(x) for x in f.get('skeleton_resources', [])] != [SKELETON]:
        raise ValueError(f'{MODEL}: unexpected skeleton family')
    if [norm(x) for x in f.get('runtime_rig_resources', [])] != [RIG]:
        raise ValueError(f'{MODEL}: unexpected runtime rig family')
    if int(f.get('runtime_placement_count', -1)) != 6:
        raise ValueError(f'{MODEL}: expected six runtime placements')
    return f


def decode_all_family_streams(r: EntryReader, skin_family: dict, bone_count: int) -> dict[int, dict]:
    by = entry_map(r)
    out = {}
    meshes = skin_family.get('meshes', [])
    if len(meshes) != 4:
        raise ValueError(f'{MODEL}: expected four source meshes, got {len(meshes)}')
    for m in meshes:
        mi = int(m['mesh_index'])
        if norm(m.get('old_weights', 'FFFFFFFF')) != 'FFFFFFFF':
            raise ValueError(f'{MODEL} mesh {mi}: separate OldWeights unexpectedly present')
        ps = m.get('primary_stream') or {}
        header_tag = norm(ps.get('hash'))
        backing_tag = norm(ps.get('backing_hash') or ps.get('backing'))
        stride = int(m['primary_stride'])
        he, hb = exact_payload(r, by, header_tag)
        if norm(he['reference']) != backing_tag:
            raise ValueError(f'{MODEL} mesh {mi}: header {header_tag} reference {norm(he["reference"])} != {backing_tag}')
        actual_stride = struct.unpack_from('<h', hb, 4)[0]
        if actual_stride != stride:
            raise ValueError(f'{MODEL} mesh {mi}: source stride {actual_stride} != census {stride}')
        be, payload = exact_payload(r, by, backing_tag)
        joints, raw_weights, weights, meta = decode_inline_arrays(payload, stride, bone_count)
        expected = m.get('skin') or {}
        if int(expected.get('vertex_count', -1)) != meta['vertex_count']:
            raise ValueError(f'{MODEL} mesh {mi}: vertex count drift {meta["vertex_count"]} != {expected.get("vertex_count")}')
        if dict(expected.get('mode_counts') or {}) != meta['mode_counts']:
            raise ValueError(f'{MODEL} mesh {mi}: mode-count drift {meta["mode_counts"]} != {expected.get("mode_counts")}')
        if [int(x) for x in expected.get('bone_domain', [])] != meta['bone_domain']:
            raise ValueError(f'{MODEL} mesh {mi}: bone-domain drift')
        if expected.get('weight_sum_min') != meta['weight_sum_min'] or expected.get('weight_sum_max') != meta['weight_sum_max']:
            raise ValueError(f'{MODEL} mesh {mi}: weight-sum invariant drift')
        out[mi] = {
            'joints': joints,
            'raw_weights': raw_weights,
            'weights': weights,
            'meta': meta,
            'header_tag': header_tag,
            'backing_tag': backing_tag,
            'header_entry_index': int(he['index']),
            'backing_entry_index': int(be['index']),
            'backing_size': int(be['file_size']),
        }
    return out


def read_animation_filebacked(read_animation, payload: bytes, version):
    with tempfile.NamedTemporaryFile() as f:
        f.write(payload); f.flush(); f.seek(0)
        return read_animation(f, version)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('input_glb', type=Path)
    ap.add_argument('--model-report', type=Path, required=True)
    ap.add_argument('--skin-census', type=Path, required=True)
    ap.add_argument('--ownership-report', type=Path, required=True)
    ap.add_argument('--source-pkg', type=Path, required=True, help='exact 00EC_5 member with logical siblings staged beside it')
    ap.add_argument('--tower-animation-pkg', type=Path, required=True, help='exact 023D_5 member with logical siblings staged beside it')
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--parser-root', type=Path, required=True)
    ap.add_argument('--fps', type=float, default=30.0)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    a = ap.parse_args()

    ownership = json.loads(a.ownership_report.read_text())
    if ownership.get('status') != 'D1_TOWER_FAMILY_E_ANIMATION_OWNERSHIP_CLOSED' or ownership.get('violations'):
        raise ValueError('Family-E animation ownership report is not closed')
    fam = ownership.get('family') or {}
    if norm(fam.get('entity_model')) != MODEL or norm(fam.get('skeleton_resource')) != SKELETON or norm(fam.get('runtime_rig_resource')) != RIG:
        raise ValueError('ownership report family identity drift')
    if int(fam.get('skeleton_node_count', -1)) != 67 or int(fam.get('runtime_rig_control_count', -1)) != 67:
        raise ValueError('ownership report 67/67 dimension drift')
    if int(fam.get('runtime_placement_count', -1)) != 6 or int(fam.get('unique_world_id_count', -1)) != 6:
        raise ValueError('ownership report placement-count drift')

    world_to_owner = {}
    for entity, row in ownership.get('entities', {}).items():
        entity = norm(entity)
        if row.get('selection_status') != 'owner_selected':
            raise ValueError(f'{entity}: selection is not owner_selected')
        clip = norm(row.get('expected_animation_clip'))
        for wid in row.get('world_ids', []):
            wid = str(wid).upper()
            if wid in world_to_owner:
                raise ValueError(f'duplicate WorldID in ownership report: {wid}')
            world_to_owner[wid] = {'entity': entity, 'clip': clip}
    if len(world_to_owner) != 6:
        raise ValueError(f'ownership report yielded {len(world_to_owner)} WorldIDs, expected 6')

    model_doc = json.loads(a.model_report.read_text())
    if model_doc.get('status') != 'D1_WORLD_ARTICULATED_MODEL_SET_COMPLETE':
        raise ValueError('model report is not complete')
    mrows = [x for x in model_doc.get('models', []) if norm(x.get('model')) == MODEL]
    if len(mrows) != 1:
        raise ValueError(f'model report expected one {MODEL} row')
    mrow = mrows[0]
    if (int(mrow.get('mesh_count', -1)), int(mrow.get('stage0_selected_range_count', -1)),
        int(mrow.get('geometry_count', -1)), int(mrow.get('triangle_count', -1))) != (4, 26, 26, 20575):
        raise ValueError(f'{MODEL}: exact geometry checkpoint drift')
    if int(mrow.get('active_material_count', -1)) != 8:
        raise ValueError(f'{MODEL}: active material count drift')
    range_by_name = {str(x['name']): x for x in mrow.get('ranges', [])}
    if len(range_by_name) != 26:
        raise ValueError(f'{MODEL}: expected 26 unique range report names')

    skin_doc = json.loads(a.skin_census.read_text())
    skin_family = family_skin_row(skin_doc)

    source = EntryReader(a.source_pkg, a.runtime)
    tower = EntryReader(a.tower_animation_pkg, a.runtime)
    source_by = entry_map(source); tower_by = entry_map(tower)

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

    _, skb = exact_payload(source, source_by, SKELETON, ENTITY_RESOURCE_REF)
    sk = read_skeleton(io.BytesIO(skb), ver)
    _, rb = exact_payload(source, source_by, RIG, ENTITY_RESOURCE_REF)
    rig = read_runtime_rig(io.BytesIO(rb), ver)
    node_count = len(sk.node_defs); control_count = len(rig.controls_relations)
    if (node_count, control_count) != (67, 67):
        raise ValueError(f'live skeleton/rig dimensions {(node_count, control_count)} != (67,67)')

    source_streams = decode_all_family_streams(source, skin_family, node_count)

    # Decode every unique owner-selected clip through the production retarget path.
    clip_cache = {}
    for clip in sorted({x['clip'] for x in world_to_owner.values()}):
        if clip in source_by:
            reader, by = source, source_by
        elif clip in tower_by:
            reader, by = tower, tower_by
        else:
            raise ValueError(f'owner-selected clip {clip} absent from both exact source members')
        _, cb = exact_payload(reader, by, clip, CLIP_REF)
        anim = read_animation_filebacked(read_animation, cb, ver)
        h = anim.animation_header
        expected_clip = ownership.get('clips', {}).get(clip)
        if expected_clip is None:
            raise ValueError(f'ownership report lacks clip row {clip}')
        if (int(h.frame_count), int(h.node_count), int(h.rig_control_count)) != (
            int(expected_clip['frame_count']), 67, 67
        ):
            raise ValueError(f'{clip}: live clip dimensions/frame count drift')
        decoded = decode_animation(anim)
        retargeted = rig_retarget(anim, decoded, sk, rig)
        local = convert_obj_to_local(anim, retargeted, sk)
        if len(decoded) != 67 or len(retargeted) != 67 or len(local) != 67:
            raise ValueError(f'{clip}: decoded/retarget/local track counts are not 67')
        clip_cache[clip] = {
            'animation': anim, 'header': h, 'decoded': decoded,
            'retargeted': retargeted, 'local': local,
            'frame_count': int(h.frame_count),
            'reader_package_id': f'{int(reader.h["pkg_id"]):04X}',
        }

    g = GLTF2().load_binary(str(a.input_glb))
    if len(g.buffers) != 1:
        raise ValueError(f'expected one-buffer articulated GLB, got {len(g.buffers)}')
    if g.skins is None: g.skins = []
    if g.animations is None: g.animations = []
    original_blob = bytes(g.binary_blob() or b'')
    blob = bytearray(original_blob)
    original_counts = {
        'meshes': len(g.meshes), 'nodes': len(g.nodes), 'materials': len(g.materials or []),
        'textures': len(g.textures or []), 'images': len(g.images or []),
        'skins': len(g.skins), 'animations': len(g.animations), 'binary_bytes': len(original_blob),
    }
    if original_counts['meshes'] != 86 or original_counts['nodes'] != 332:
        raise ValueError(f'articulated source topology drift: {original_counts}')
    if original_counts['skins'] or original_counts['animations']:
        raise ValueError('input articulated layer is not the proven bind-pose/no-animation checkpoint')

    # Add exact skin attributes once to the 26 meshes shared by all six placements.
    family_mesh_indices = []
    seen_ranges = set()
    unique_bound_vertices = 0
    unique_triangles = 0
    bind_rows = []
    float32_weight_sum_abs_error_max = 0.0
    for gi, mesh in enumerate(g.meshes):
        ex = mesh.extras or {}
        if norm(ex.get('model', '')) != MODEL:
            continue
        family_mesh_indices.append(gi)
        if len(mesh.primitives) != 1:
            raise ValueError(f'gltf mesh {gi} {mesh.name}: expected one primitive')
        prim = mesh.primitives[0]
        if prim.attributes.POSITION is None or prim.indices is None:
            raise ValueError(f'gltf mesh {gi} {mesh.name}: missing POSITION/indices')
        range_name = str(mesh.name).split('__')[-1]
        rr = range_by_name.get(range_name)
        if rr is None:
            raise ValueError(f'gltf mesh {gi}: range {range_name} absent from model report')
        seen_ranges.add(range_name)
        mi = int(ex.get('mesh_index'))
        if mi != int(rr['mesh_index']):
            raise ValueError(f'{range_name}: source mesh mismatch {mi} != {rr["mesh_index"]}')
        src_indices = [int(x) for x in ex.get('source_vertex_indices', [])]
        pos_count = int(g.accessors[prim.attributes.POSITION].count)
        if len(src_indices) != pos_count or int(rr['source_vertex_count']) != pos_count:
            raise ValueError(f'{range_name}: source-index/POSITION/report count mismatch')
        if not src_indices or len(set(src_indices)) != len(src_indices):
            raise ValueError(f'{range_name}: source vertex indices absent or duplicated')
        stream = source_streams.get(mi)
        if stream is None:
            raise ValueError(f'{range_name}: no exact skin stream for source mesh {mi}')
        if min(src_indices) < 0 or max(src_indices) >= stream['meta']['vertex_count']:
            raise ValueError(f'{range_name}: source vertex index outside exact primary stream')
        joints = stream['joints'][src_indices]
        raw_weights = stream['raw_weights'][src_indices]
        weights = stream['weights'][src_indices]

        # Retail truth is the exact four U8 lanes.  Prove the selected rows still
        # sum to exactly 255, then prove the glTF FLOAT transport bytes are exactly
        # float32(raw/255).  Do not renormalize the portable floats.
        raw_sums = np.sum(raw_weights.astype(np.uint16), axis=1, dtype=np.uint16)
        if not np.all(raw_sums == 255):
            bad = np.flatnonzero(raw_sums != 255)
            i = int(bad[0]) if len(bad) else -1
            raise ValueError(f'{range_name}: selected raw U8 weight sum drift at row {i}')
        expected_weights = exact_float32_weights(raw_weights)
        if not np.array_equal(weights.view(np.uint32), expected_weights.view(np.uint32)):
            raise ValueError(f'{range_name}: emitted float32 weights are not bit-exact U8/255 conversions')
        float_sums = np.sum(weights, axis=1, dtype=np.float32)
        float_errors = np.abs(float_sums - np.float32(1.0))
        range_float_error = float(np.max(float_errors)) if len(float_errors) else 0.0
        float32_weight_sum_abs_error_max = max(float32_weight_sum_abs_error_max, range_float_error)

        jacc = append_accessor(g, blob, joints, component_type=UNSIGNED_SHORT,
                               accessor_type='VEC4', target=ARRAY_BUFFER)
        wacc = append_accessor(g, blob, weights, component_type=FLOAT,
                               accessor_type='VEC4', target=ARRAY_BUFFER)
        prim.attributes.JOINTS_0 = jacc
        prim.attributes.WEIGHTS_0 = wacc
        tri_count = int(g.accessors[prim.indices].count) // 3
        if int(g.accessors[prim.indices].count) % 3:
            raise ValueError(f'{range_name}: glTF triangle index count is not divisible by 3')
        if tri_count != int(rr['triangle_count']):
            raise ValueError(f'{range_name}: glTF/report triangle drift {tri_count} != {rr["triangle_count"]}')
        unique_bound_vertices += pos_count
        unique_triangles += tri_count
        bind_rows.append({
            'gltf_mesh_index': gi, 'gltf_mesh_name': mesh.name, 'range_name': range_name,
            'source_mesh_index': mi, 'source_vertex_count': pos_count,
            'source_vertex_min': min(src_indices), 'source_vertex_max': max(src_indices),
            'triangle_count': tri_count, 'primary_stride': stream['meta']['stride'],
            'skin_modes': stream['meta']['mode_counts'],
            'bone_domain': sorted(set(int(x) for x in joints[raw_weights > 0])),
            'raw_u8_weight_sum_min': int(np.min(raw_sums)),
            'raw_u8_weight_sum_max': int(np.max(raw_sums)),
            'float32_weight_sum_min': float(np.min(float_sums)),
            'float32_weight_sum_max': float(np.max(float_sums)),
            'float32_weight_sum_abs_error_max': range_float_error,
            'float32_conversion_bit_exact': True,
            'portable_float_renormalized': False,
        })
    if len(family_mesh_indices) != 26 or seen_ranges != set(range_by_name):
        raise ValueError(f'Family-E glTF range coverage is not exact 26/26')
    if unique_triangles != 20575:
        raise ValueError(f'Family-E unique triangle total {unique_triangles} != 20575')

    # Recover the six existing exact placement groups.
    placement_nodes = defaultdict(list)
    all_world_ids = set()
    for ni, node in enumerate(g.nodes[:original_counts['nodes']]):
        ex = node.extras or {}
        wid = ex.get('d1WorldID')
        if wid:
            all_world_ids.add(str(wid).upper())
        if norm(ex.get('d1Model', '')) == MODEL:
            placement_nodes[str(wid).upper()].append(ni)
    if set(placement_nodes) != set(world_to_owner):
        raise ValueError(f'GLB/ownership WorldID mismatch: glb={sorted(placement_nodes)} ownership={sorted(world_to_owner)}')
    for wid, nodes in placement_nodes.items():
        if len(nodes) != 26:
            raise ValueError(f'{wid}: expected 26 geometry nodes, got {len(nodes)}')
        matrices = [g.nodes[n].matrix for n in nodes]
        if any(m is None for m in matrices) or any(m != matrices[0] for m in matrices[1:]):
            raise ValueError(f'{wid}: Family-E placement nodes do not share one exact matrix')
        entities = {norm((g.nodes[n].extras or {}).get('d1Entity')) for n in nodes}
        if entities != {world_to_owner[wid]['entity']}:
            raise ValueError(f'{wid}: GLB entity {entities} != ownership {world_to_owner[wid]["entity"]}')

    # Exact D1 bind hierarchy shared numerically; each placement gets unique joint nodes.
    world_bind = [transform_to_np_matrix(x) for x in sk.default_obj_space_tr]
    inv_world = [transform_to_np_matrix(x) for x in sk.default_inv_obj_space_tr]
    local_bind = []
    bone_base_names = []
    for i, nd in enumerate(sk.node_defs):
        parent = int(nd.parent_node_index)
        mat = inv_world[parent] @ world_bind[i] if parent >= 0 else world_bind[i]
        scale, rot, trans = np_decompose_matrix(mat)
        local_bind.append((
            [float(x) for x in trans], [float(x) for x in rot.as_quat()], [float(x) for x in scale]
        ))
        name = convert_hash_to_bungie_name(int(nd.bone_hash)) or f'{int(nd.bone_hash) & 0xffffffff:08X}'
        bone_base_names.append(name)
    inv_bind = np.stack([np.asarray(m.T, dtype='<f4') for m in inv_world], axis=0)
    ibm_acc = append_accessor(g, blob, inv_bind, component_type=FLOAT, accessor_type='MAT4')

    scene_idx = g.scene or 0
    scene_roots = list(g.scenes[scene_idx].nodes or [])
    placement_bones = {}
    placement_skin = {}
    added_skeleton_roots = []
    for wid in sorted(world_to_owner):
        entity = world_to_owner[wid]['entity']; clip = world_to_owner[wid]['clip']
        geom_nodes = placement_nodes[wid]
        matrix = [float(x) for x in g.nodes[geom_nodes[0]].matrix]
        bones = []
        used_names = set()
        for bi, nd in enumerate(sk.node_defs):
            base = bone_base_names[bi]
            name = base if base not in used_names else f'{base}_{int(nd.bone_hash) & 0xffffffff:08X}'
            used_names.add(name)
            trans, rot, scale = local_bind[bi]
            idx = len(g.nodes)
            g.nodes.append(Node(
                name=f'D1_FAM_E_{wid}_{name}', children=[], translation=trans,
                rotation=rot, scale=scale,
                extras={'d1WorldID': wid, 'd1Entity': entity, 'd1Model': MODEL,
                        'd1Skeleton': SKELETON, 'd1RuntimeRig': RIG,
                        'd1BoneIndex': bi, 'd1BoneHash': f'{int(nd.bone_hash) & 0xffffffff:08X}'}
            ))
            bones.append(idx)
        root_idx = len(g.nodes)
        g.nodes.append(Node(
            name=f'D1_FAM_E_{wid}_SKELETON_ROOT', children=[], matrix=matrix,
            extras={'d1WorldID': wid, 'd1Entity': entity, 'd1Model': MODEL,
                    'd1Skeleton': SKELETON, 'd1RuntimeRig': RIG,
                    'd1OwnerSelectedClip': clip,
                    'd1PlacementMatrixSource': 'existing articulated GLB geometry nodes'}
        ))
        for bi, nd in enumerate(sk.node_defs):
            parent = int(nd.parent_node_index)
            if parent >= 0:
                g.nodes[bones[parent]].children.append(bones[bi])
            else:
                g.nodes[root_idx].children.append(bones[bi])
        skin_idx = len(g.skins)
        g.skins.append(Skin(
            joints=bones, inverseBindMatrices=ibm_acc, skeleton=root_idx,
            name=f'D1_FAM_E_{wid}_{SKELETON}_skin'
        ))
        for ni in geom_nodes:
            if g.nodes[ni].skin is not None:
                raise ValueError(f'{wid}: geometry node {ni} unexpectedly already skinned')
            g.nodes[ni].skin = skin_idx
        scene_roots.append(root_idx)
        placement_bones[wid] = bones
        placement_skin[wid] = skin_idx
        added_skeleton_roots.append(root_idx)
    g.scenes[scene_idx].nodes = scene_roots

    # Append clip sample/output accessors once per unique clip.  Each placement gets
    # a separate Animation object so no simultaneous-start or loop semantic is implied.
    clip_templates = {}
    clip_binary = {}
    for clip, c in clip_cache.items():
        templates = []
        time_cache = {}
        output_cache = {}
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
                    time_cache[count] = append_accessor(
                        g, blob, times, component_type=FLOAT,
                        accessor_type='SCALAR', with_minmax=True
                    )
                key = (bi, path)
                output_cache[key] = append_accessor(
                    g, blob, arr, component_type=FLOAT, accessor_type=kind
                )
                templates.append((bi, path, time_cache[count], output_cache[key], count))
        clip_templates[clip] = templates
        clip_binary[clip] = {
            'frame_count': c['frame_count'], 'template_channel_count': len(templates),
            'unique_time_accessor_lengths': sorted(time_cache),
            'decoded_track_count': len(c['decoded']), 'retargeted_track_count': len(c['retargeted']),
            'local_track_count': len(c['local']), 'source_package_id': c['reader_package_id'],
        }

    animation_rows = []
    sorted_world_ids = sorted(world_to_owner)
    for wid in sorted_world_ids:
        entity = world_to_owner[wid]['entity']; clip = world_to_owner[wid]['clip']
        bones = placement_bones[wid]
        samplers = []; channels = []
        for bi, path, tacc, vacc, count in clip_templates[clip]:
            si = len(samplers)
            samplers.append(AnimationSampler(input=tacc, output=vacc, interpolation='LINEAR'))
            channels.append(AnimationChannel(
                sampler=si,
                target=AnimationChannelTarget(node=bones[bi], path=path)
            ))
        anim_idx = len(g.animations)
        g.animations.append(Animation(
            name=f'D1_FAM_E_{wid}_{clip}', samplers=samplers, channels=channels,
            extras={
                'd1WorldID': wid, 'd1Entity': entity, 'd1Model': MODEL,
                'd1Skeleton': SKELETON, 'd1RuntimeRig': RIG,
                'd1OwnerSelectedClip': clip,
                'd1FrameCount': clip_cache[clip]['frame_count'], 'd1Fps': float(a.fps),
                'd1StateSemantic': 'UNRESOLVED', 'd1LoopSemantic': 'UNRESOLVED',
                'd1SelectionEvidence': 'D1_TOWER_FAMILY_E_ANIMATION_OWNERSHIP_CLOSED'
            }
        ))
        animation_rows.append({
            'animation_index': anim_idx, 'world_id': wid, 'entity': entity, 'clip': clip,
            'frame_count': clip_cache[clip]['frame_count'], 'channel_count': len(channels),
            'sampler_count': len(samplers), 'skin_index': placement_skin[wid],
            'skeleton_root_node': added_skeleton_roots[sorted_world_ids.index(wid)],
        })

    g.extras = {
        **(g.extras or {}),
        'd1TowerFamilyEAnimatedProof': {
            'model': MODEL, 'skeleton': SKELETON, 'runtimeRig': RIG,
            'runtimePlacements': 6, 'selectedRanges': 26, 'uniqueTriangles': 20575,
            'worldIDClipMap': {wid: world_to_owner[wid]['clip'] for wid in sorted_world_ids},
            'ownershipStatus': ownership['status'],
            'rawWeightInvariant': 'four U8 lanes sum exactly 255',
            'floatWeightEncoding': 'bit-exact float32(raw_u8/255), never renormalized',
            'float32WeightSumAbsErrorMax': float32_weight_sum_abs_error_max,
            'stateSemantic': 'UNRESOLVED', 'loopSemantic': 'UNRESOLVED',
            'policy': 'Skin bytes are exact D1 retail inline forms. Portable float weights are exact U8/255 encodings, not renormalized. Clip choice is source-owner-selected. No NPC/vendor/state/loop/synchronization semantic is inferred.'
        }
    }
    g.buffers[0].byteLength = len(blob)
    g.set_binary_blob(bytes(blob))
    a.out.parent.mkdir(parents=True, exist_ok=True)
    g.save_binary(str(a.out))

    # Reopen and enforce the append-only/topology contract.
    outg = GLTF2().load_binary(str(a.out))
    final_blob = bytes(outg.binary_blob() or b'')
    prefix_exact = final_blob[:len(original_blob)] == original_blob
    final_counts = {
        'meshes': len(outg.meshes), 'nodes': len(outg.nodes), 'materials': len(outg.materials or []),
        'textures': len(outg.textures or []), 'images': len(outg.images or []),
        'skins': len(outg.skins or []), 'animations': len(outg.animations or []),
        'binary_bytes': len(final_blob),
    }
    if not prefix_exact:
        raise ValueError('original GLB binary chunk is not an exact prefix after animation append')
    if final_counts['meshes'] != original_counts['meshes'] or final_counts['materials'] != original_counts['materials'] or final_counts['textures'] != original_counts['textures'] or final_counts['images'] != original_counts['images']:
        raise ValueError(f'visual resource counts changed unexpectedly: {original_counts} -> {final_counts}')
    if final_counts['nodes'] != original_counts['nodes'] + 6 * 68:
        raise ValueError(f'node count {final_counts["nodes"]} != original + six 67-bone skeletons/root nodes')
    if final_counts['skins'] != 6 or final_counts['animations'] != 6:
        raise ValueError(f'expected six skins and six owner-selected animations, got {final_counts}')
    out_family_meshes = [m for m in outg.meshes if norm((m.extras or {}).get('model', '')) == MODEL]
    if len(out_family_meshes) != 26 or any(
        p.attributes.JOINTS_0 is None or p.attributes.WEIGHTS_0 is None
        for m in out_family_meshes for p in m.primitives
    ):
        raise ValueError('output Family-E meshes are not exactly 26 fully skinned primitives')
    out_family_nodes = [n for n in outg.nodes[:original_counts['nodes']] if norm((n.extras or {}).get('d1Model', '')) == MODEL]
    if len(out_family_nodes) != 156 or any(n.skin is None for n in out_family_nodes):
        raise ValueError('output does not skin all 156 original Family-E placement geometry nodes')

    rep = {
        'schema_version': 2,
        'status': 'D1_TOWER_FAMILY_E_ANIMATED_LAYER_COMPLETE',
        'input': str(a.input_glb), 'input_sha256': sha256_file(a.input_glb),
        'output': str(a.out), 'output_bytes': a.out.stat().st_size,
        'output_sha256': sha256_file(a.out),
        'model': MODEL, 'source_mesh_count': 4, 'selected_range_count': 26,
        'unique_triangle_count': unique_triangles,
        'scene_placement_triangle_count': unique_triangles * 6,
        'unique_bound_vertex_rows': unique_bound_vertices,
        'runtime_placement_count': 6, 'placement_geometry_node_count': 156,
        'skeleton': SKELETON, 'skeleton_node_count': node_count,
        'runtime_rig': RIG, 'runtime_rig_control_count': control_count,
        'source_streams': {
            str(mi): {k: v[k] for k in ('meta','header_tag','backing_tag','header_entry_index','backing_entry_index','backing_size')}
            for mi, v in sorted(source_streams.items())
        },
        'mesh_bindings': bind_rows,
        'raw_u8_weight_sum_exact_255': True,
        'float32_conversion_bit_exact': True,
        'portable_float_weights_renormalized': False,
        'float32_weight_sum_abs_error_max': float32_weight_sum_abs_error_max,
        'weight_fidelity_policy': (
            'Retail U8 weight lanes are authoritative and must sum exactly 255. '
            'glTF FLOAT weights are emitted as bit-exact float32(U8/255) conversions. '
            'No post-conversion renormalization is allowed merely to force a float32 sum of exactly 1.0.'
        ),
        'world_id_owner_map': world_to_owner,
        'clip_decode': clip_binary,
        'animations': animation_rows,
        'original_counts': original_counts, 'final_counts': final_counts,
        'original_binary_exact_prefix': prefix_exact,
        'other_articulated_world_id_count': len(all_world_ids - set(world_to_owner)),
        'state_semantics_proven': False, 'loop_semantics_proven': False,
        'synchronization_semantics_proven': False,
        'policy': (
            'The proven exact-texture articulated layer is preserved and only appended to. '
            'All 26 shared Family-E mesh primitives receive source-indexed JOINTS_0/WEIGHTS_0 from exact retail D1 primary streams. '
            'Retail U8 weights remain authoritative; portable float32 weights are exact U8/255 conversions and are never renormalized. '
            'Six independent skeletons use the existing exact placement matrices. Each WorldID receives only its source-owner-selected retail clip. '
            'Six separate glTF animations avoid implying simultaneous playback, loop behavior, state names, or NPC/vendor semantics.'
        ),
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(rep, indent=2) + '\n')
    print(json.dumps({
        k: rep[k] for k in (
            'status','output_bytes','output_sha256','selected_range_count','unique_triangle_count',
            'runtime_placement_count','placement_geometry_node_count','skeleton_node_count',
            'runtime_rig_control_count','raw_u8_weight_sum_exact_255','float32_conversion_bit_exact',
            'portable_float_weights_renormalized','float32_weight_sum_abs_error_max',
            'original_counts','final_counts','original_binary_exact_prefix',
            'other_articulated_world_id_count'
        )
    }, indent=2))
    print('WORLD_ID_OWNER_MAP', json.dumps(rep['world_id_owner_map'], sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
