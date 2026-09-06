#!/usr/bin/env python3
"""Census exact D1 skin storage for source-owned articulated world entities.

Input is the exporter-ready plan from d1_world_articulated_entity_plan.py.  For
every distinct model/skeleton family, this tool resolves the exact retail
s_entity_model and primary vertex streams through the cross-package Corpus and
classifies how skin influences are stored.

The only decoded forms are forms already independently retail-validated in this
repository for D1 PS4 assets when mesh.old_weights == FFFFFFFF:

* primary stride 0x08: int16 lane 3 is one rigid joint index;
* primary stride 0x0C:
    - ordinary non-negative int16 lane 3 is one rigid joint index;
    - lane 3 == +/-0x7FFF means bytes 8..9 are two U8 joint indices and
      bytes 10..11 are two U8 weights;
* primary stride 0x10: bytes 8..11 are four U8 weights and bytes 12..15
  are four U8 joint indices.

For weighted forms, raw U8 weights must sum to exactly 255.  Every nonzero
influence must address a joint inside the source-decoded skeleton bone count.
No malformed influence is repaired and no unsupported/separate old-weight
format is guessed.  Such meshes are emitted as an explicit frontier instead.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import d1_tower_map_schema_validate_v5 as v5
from d1_entity_model_probe import parse_model

ENTITY_MODEL_CLASS = '80801AB5'
NULLS = {'00000000', 'FFFFFFFF'}
SENTINELS = {32767, -32767}
PINNED_PROJECT_PROOF = (
    'Retail-validated D1 PS4 inline skin forms from '
    'd1_guardian_combined_skin_animation.py, d1_model_joint_probe.py, '
    'd1_remote_rigid_joint_domain.py, and D1_GUARDIAN_FULL_SKIN_SOLVED_2026-09-05.md'
)


def norm(x):
    return str(x).upper().removeprefix('0X').zfill(8)


def s16(b, o):
    return struct.unpack_from('<h', b, o)[0]


def linked_payload(c, h):
    h = norm(h)
    if h in NULLS:
        return {'hash': h, 'null': True}, None, None
    meta = c.entry_meta(h)
    head, src = c.payload(h)
    out = {'hash': h, 'meta': meta, 'source': src, 'null': False}
    if meta is None or head is None:
        out['error'] = 'header_unavailable'
        return out, None, None
    backing = norm(meta.get('reference', 'FFFFFFFF'))
    out['backing_hash'] = backing
    if backing in NULLS:
        out['error'] = 'header_has_null_backing'
        return out, head, None
    pmeta = c.entry_meta(backing)
    payload, psrc = c.payload(backing)
    out['backing_meta'] = pmeta
    out['backing_source'] = psrc
    if pmeta is None or payload is None:
        out['error'] = 'backing_unavailable'
        return out, head, None
    return out, head, payload


def decode_inline(payload: bytes, stride: int, bone_count: int) -> dict:
    out = {
        'storage': 'inline_primary',
        'stride': stride,
        'bone_count': bone_count,
        'vertex_count': 0,
        'mode_counts': Counter(),
        'bone_reference_counts': Counter(),
        'bone_domain': set(),
        'weight_sum_min': None,
        'weight_sum_max': None,
        'violations': [],
    }
    if stride not in (0x08, 0x0C, 0x10):
        out['storage'] = 'unsupported_inline_stride'
        out['frontier'] = f'inline skin stride 0x{stride:X} is not source-closed by the project'
        return out
    if len(payload) % stride:
        out['violations'].append(f'primary_payload_size_{len(payload)}_not_divisible_by_stride_{stride}')
        return out
    n = len(payload) // stride
    out['vertex_count'] = n
    sums = []
    for vi in range(n):
        off = vi * stride
        wpos = s16(payload, off + 6)
        if stride == 0x08:
            if wpos in SENTINELS:
                out['violations'].append(f'vertex[{vi}]:sentinel_in_0x08_rigid_lane')
                continue
            if wpos < 0:
                out['violations'].append(f'vertex[{vi}]:negative_rigid_joint_{wpos}')
                continue
            influences = [(wpos, 255)]
            out['mode_counts']['rigid_lane3'] += 1
            sums.append(255)
        elif stride == 0x0C:
            if wpos in SENTINELS:
                inds = list(payload[off + 8:off + 10])
                vals = list(payload[off + 10:off + 12])
                influences = list(zip(inds, vals))
                out['mode_counts']['inline2'] += 1
                sums.append(sum(vals))
                if sum(vals) != 255:
                    out['violations'].append(
                        f'vertex[{vi}]:inline2_weight_sum_{sum(vals)}_not_255:'
                        f'indices={inds}:weights={vals}'
                    )
            elif wpos >= 0:
                influences = [(wpos, 255)]
                out['mode_counts']['rigid_lane3'] += 1
                sums.append(255)
            else:
                out['violations'].append(f'vertex[{vi}]:negative_non_sentinel_joint_{wpos}')
                continue
        else:
            vals = list(payload[off + 8:off + 12])
            inds = list(payload[off + 12:off + 16])
            influences = list(zip(inds, vals))
            out['mode_counts']['inline4'] += 1
            sums.append(sum(vals))
            if sum(vals) != 255:
                out['violations'].append(
                    f'vertex[{vi}]:inline4_weight_sum_{sum(vals)}_not_255:'
                    f'indices={inds}:weights={vals}'
                )
        for joint, weight in influences:
            if weight == 0:
                continue
            if not (0 <= int(joint) < bone_count):
                out['violations'].append(
                    f'vertex[{vi}]:nonzero_joint_{joint}_outside_skeleton_{bone_count}'
                )
                continue
            out['bone_domain'].add(int(joint))
            out['bone_reference_counts'][str(int(joint))] += 1
    out['mode_counts'] = dict(out['mode_counts'])
    out['bone_domain'] = sorted(out['bone_domain'])
    out['bone_reference_counts'] = dict(out['bone_reference_counts'])
    if sums:
        out['weight_sum_min'] = min(sums)
        out['weight_sum_max'] = max(sums)
    out['validation_ok'] = not out['violations']
    return out


def family_inputs(plan: dict) -> list[dict]:
    by_key = {}
    candidates_by_entity = {x['entity']: x for x in plan.get('candidates', [])}
    for fam in plan.get('families', []):
        entities = [candidates_by_entity[e] for e in fam.get('entities', []) if e in candidates_by_entity]
        models = sorted({norm(m) for e in entities for m in e.get('models', [])})
        skeleton_rows = [s for e in entities for s in e.get('skeletons', [])]
        skeleton_resources = sorted({norm(s['resource_hash']) for s in skeleton_rows if s.get('resource_hash')})
        bone_counts = sorted({int(s['bone_count']) for s in skeleton_rows if isinstance(s.get('bone_count'), int)})
        rigs = sorted({norm(r) for e in entities for r in e.get('runtime_rig_resources', [])})
        row = {
            'family_key': fam.get('family_key'),
            'entities': sorted(e['entity'] for e in entities),
            'models': models,
            'skeleton_resources': skeleton_resources,
            'bone_counts': bone_counts,
            'runtime_rig_resources': rigs,
            'runtime_placement_count': sum(e.get('runtime_placement_count', 0) for e in entities),
            'serialized_placement_reference_count': sum(e.get('serialized_placement_reference_count', 0) for e in entities),
        }
        key = (tuple(models), tuple(skeleton_resources), tuple(bone_counts), tuple(rigs))
        if key not in by_key:
            by_key[key] = row
        else:
            old = by_key[key]
            old['entities'] = sorted(set(old['entities']) | set(row['entities']))
            old['runtime_placement_count'] += row['runtime_placement_count']
            old['serialized_placement_reference_count'] += row['serialized_placement_reference_count']
    return list(by_key.values())


def inspect_family(c, fam):
    out = dict(fam)
    out['meshes'] = []
    out['violations'] = []
    out['frontiers'] = []
    if len(fam['models']) != 1:
        out['violations'].append(f'family_model_count_{len(fam["models"])}_not_1')
        return out
    if len(fam['bone_counts']) != 1:
        out['violations'].append(f'family_bone_count_domain_{fam["bone_counts"]}_not_unique')
        return out
    model_hash = fam['models'][0]
    bone_count = fam['bone_counts'][0]
    mm = c.entry_meta(model_hash)
    mb, msrc = c.payload(model_hash)
    out['model'] = model_hash
    out['model_meta'] = mm
    out['model_source'] = msrc
    if mm is None or norm(mm.get('reference', '')) != ENTITY_MODEL_CLASS or mb is None:
        out['violations'].append('model_missing_class_or_payload')
        return out
    try:
        model = parse_model(mb, 'PS4')
    except Exception as ex:
        out['violations'].append('model_parse:' + repr(ex))
        return out
    out['model_mesh_count'] = model['mesh_count']
    for mi, mesh in enumerate(model['meshes']):
        row = {
            'mesh_index': mi,
            'vertices1': norm(mesh['vertices1']),
            'vertices2': norm(mesh['vertices2']),
            'old_weights': norm(mesh['old_weights']),
            'indices': norm(mesh['indices']),
            'bone_count': bone_count,
            'violations': [],
        }
        link, head, payload = linked_payload(c, mesh['vertices1'])
        row['primary_stream'] = link
        if head is None or payload is None or len(head) < 6:
            row['violations'].append('primary_stream_unavailable_or_short')
        else:
            stride = s16(head, 4)
            row['primary_stride'] = stride
            row['primary_payload_size'] = len(payload)
            if row['old_weights'] in NULLS:
                skin = decode_inline(payload, stride, bone_count)
                row['skin'] = skin
                row['violations'].extend(skin.get('violations', []))
                if skin.get('frontier'):
                    row['frontier'] = skin['frontier']
                    out['frontiers'].append(f'mesh[{mi}]:' + skin['frontier'])
            else:
                wlink, whead, wpayload = linked_payload(c, row['old_weights'])
                row['old_weights_stream'] = wlink
                row['skin'] = {
                    'storage': 'separate_old_weights',
                    'frontier': 'separate D1 OldWeights stream present; byte semantics intentionally not guessed',
                    'header_size': None if whead is None else len(whead),
                    'payload_size': None if wpayload is None else len(wpayload),
                    'stride': None if whead is None or len(whead) < 6 else s16(whead, 4),
                }
                out['frontiers'].append(f'mesh[{mi}]:separate_old_weights:{row["old_weights"]}')
                if whead is None or wpayload is None:
                    row['violations'].append('separate_old_weights_stream_unavailable')
        if row['violations']:
            out['violations'].extend(f'mesh[{mi}]:{x}' for x in row['violations'])
        out['meshes'].append(row)
    out['mesh_count'] = len(out['meshes'])
    out['inline_mesh_count'] = sum((m.get('skin') or {}).get('storage') == 'inline_primary' for m in out['meshes'])
    out['separate_old_weights_mesh_count'] = sum((m.get('skin') or {}).get('storage') == 'separate_old_weights' for m in out['meshes'])
    out['unsupported_inline_mesh_count'] = sum((m.get('skin') or {}).get('storage') == 'unsupported_inline_stride' for m in out['meshes'])
    out['validation_ok'] = not out['violations']
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', type=Path, action='append', required=True)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--articulated-plan', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    plan = json.loads(a.articulated_plan.read_text())
    c = v5.v3.base.Corpus([p.resolve() for p in a.snapshot], a.runtime.resolve())
    raw_families = family_inputs(plan)
    families = [inspect_family(c, f) for f in raw_families]
    violations = [f'family[{i}]:{x}' for i, f in enumerate(families) for x in f.get('violations', [])]
    frontiers = [f'family[{i}]:{x}' for i, f in enumerate(families) for x in f.get('frontiers', [])]
    mode_counts = Counter()
    bone_domains = {}
    for f in families:
        for m in f.get('meshes', []):
            s = m.get('skin') or {}
            for k, v in (s.get('mode_counts') or {}).items():
                mode_counts[k] += v
            if s.get('bone_domain') is not None:
                bone_domains[f'{f.get("model")}:mesh{m["mesh_index"]}'] = s.get('bone_domain')
    separate = sum(f.get('separate_old_weights_mesh_count', 0) for f in families)
    unsupported = sum(f.get('unsupported_inline_mesh_count', 0) for f in families)
    status = 'D1_WORLD_ARTICULATED_SKIN_CENSUS_PARTIAL' if violations else (
        'D1_WORLD_ARTICULATED_SKIN_CENSUS_FRONTIER' if frontiers else 'D1_WORLD_ARTICULATED_SKIN_CENSUS_COMPLETE'
    )
    out = {
        'schema_version': 1,
        'status': status,
        'project_proof_basis': PINNED_PROJECT_PROOF,
        'family_count': len(families),
        'unique_model_count': len({f.get('model') for f in families if f.get('model')}),
        'mesh_count': sum(f.get('mesh_count', 0) for f in families),
        'inline_mesh_count': sum(f.get('inline_mesh_count', 0) for f in families),
        'separate_old_weights_mesh_count': separate,
        'unsupported_inline_mesh_count': unsupported,
        'runtime_placement_count': sum(f.get('runtime_placement_count', 0) for f in families),
        'serialized_placement_reference_count': sum(f.get('serialized_placement_reference_count', 0) for f in families),
        'mode_vertex_counts': dict(mode_counts),
        'bone_domains': bone_domains,
        'families': families,
        'frontiers': frontiers,
        'violations': violations,
        'policy': (
            'Only previously retail-validated D1 PS4 inline skin encodings are decoded. '
            'Every nonzero influence must fit the source-owned skeleton. Separate OldWeights or unknown strides remain explicit frontiers; no influences are fabricated.'
        ),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in (
        'status', 'family_count', 'unique_model_count', 'mesh_count', 'inline_mesh_count',
        'separate_old_weights_mesh_count', 'unsupported_inline_mesh_count', 'runtime_placement_count',
        'serialized_placement_reference_count', 'mode_vertex_counts', 'frontiers', 'violations')}, indent=2))
    return 2 if violations else 0


if __name__ == '__main__':
    raise SystemExit(main())
