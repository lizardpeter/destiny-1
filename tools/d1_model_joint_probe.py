#!/usr/bin/env python3
"""Probe native rigid-joint indices for selected local D1 s_entity_model assets.

For PS4 D1 meshes with old_weights == FFFFFFFF, the project has retail-validated
primary vertex stream int16 lane 3 as the rigid joint index.  This tool applies
that proven representation to caller-selected model hashes while deliberately
leaving separately weighted meshes unresolved.
"""
from __future__ import annotations

import argparse
import collections
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from d1_entry_extract import EntryReader
from d1_entity_model_probe import D1_ENTITY_MODEL_CLASS, parse_model


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('pkg', type=Path)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--tag-hash', action='append', required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    r = EntryReader(a.pkg, a.runtime)
    by = {e['tag_hash'].upper(): e for e in r.entries}
    rows = []
    union = set()
    distribution = collections.Counter()
    errors = []

    for raw in a.tag_hash:
        tag = raw.upper().removeprefix('0X')
        e = by.get(tag)
        rec = {'tag_hash': tag}
        if e is None:
            rec.update({'resolved': False, 'reason': 'tag absent from package entry table'})
            rows.append(rec)
            continue
        rec.update({'entry_index': e['index'], 'reference': e['reference'].upper(), 'size': e['file_size']})
        if e['reference'].upper() != D1_ENTITY_MODEL_CLASS:
            rec.update({'resolved': False, 'reason': f"entry reference is {e['reference']}, not {D1_ENTITY_MODEL_CLASS}"})
            rows.append(rec)
            continue
        try:
            model = parse_model(r.entry(e['index']), r.h['platform'])
            meshes = []
            model_union = set()
            model_dist = collections.Counter()
            for mi, mesh in enumerate(model['meshes']):
                mrow = {'mesh_index': mi, 'old_weights': mesh['old_weights']}
                if mesh['old_weights'].upper() != 'FFFFFFFF':
                    mrow['representation'] = 'weighted_not_decoded'
                    meshes.append(mrow)
                    continue
                vh = by.get(mesh['vertices1'].upper())
                if vh is None:
                    mrow.update({'representation': 'rigid', 'error': 'vertex header absent'})
                    meshes.append(mrow)
                    continue
                vp = by.get(vh['reference'].upper())
                if vp is None:
                    mrow.update({'representation': 'rigid', 'error': f"vertex payload {vh['reference']} absent"})
                    meshes.append(mrow)
                    continue
                hb = r.entry(vh['index'])
                pb = r.entry(vp['index'])
                stride = struct.unpack_from('<h', hb, 4)[0]
                if stride < 8 or stride > 128 or stride % 2:
                    raise ValueError(f'{tag} mesh {mi}: invalid primary stride {stride}')
                if len(pb) % stride:
                    raise ValueError(f'{tag} mesh {mi}: payload {len(pb)} not divisible by stride {stride}')
                vals = [struct.unpack_from('<h', pb, off + 6)[0] for off in range(0, len(pb), stride)]
                dist = collections.Counter(vals)
                model_union.update(vals)
                model_dist.update(vals)
                union.update(vals)
                distribution.update(vals)
                mrow.update({
                    'representation': 'rigid_primary_stream_lane3',
                    'vertices1': mesh['vertices1'],
                    'vertex_payload': vh['reference'].upper(),
                    'stride': stride,
                    'vertex_count': len(vals),
                    'joint_values': sorted(dist),
                    'joint_distribution': {str(k): v for k, v in sorted(dist.items())},
                })
                meshes.append(mrow)
            rec.update({
                'resolved': True,
                'mesh_count': model['mesh_count'],
                'rigid_mesh_count': sum(x.get('representation') == 'rigid_primary_stream_lane3' for x in meshes),
                'weighted_mesh_count': sum(x.get('representation') == 'weighted_not_decoded' for x in meshes),
                'joint_domain': sorted(model_union),
                'joint_distribution': {str(k): v for k, v in sorted(model_dist.items())},
                'meshes': meshes,
            })
        except Exception as ex:
            rec.update({'resolved': False, 'error': repr(ex)})
            errors.append({'tag_hash': tag, 'error': repr(ex)})
        rows.append(rec)

    report = {
        'schema': 'd1_model_joint_probe/v1',
        'package': str(r.pkg),
        'package_id': f"{int(r.h['pkg_id']):04X}",
        'model_count': len(rows),
        'resolved_model_count': sum(bool(x.get('resolved')) for x in rows),
        'joint_domain': sorted(union),
        'joint_distribution': {str(k): v for k, v in sorted(distribution.items())},
        'models': rows,
        'errors': errors,
        'policy': 'Only meshes with old_weights==FFFFFFFF are interpreted; lane-3 rigid joint semantics are inherited from the project retail Gjallarhorn validation. Weighted meshes are not guessed.',
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('package_id','model_count','resolved_model_count','joint_domain')}, indent=2))
    for x in rows:
        print(x['tag_hash'], 'meshes', x.get('mesh_count'), 'rigid', x.get('rigid_mesh_count'), 'weighted', x.get('weighted_mesh_count'), 'joints', x.get('joint_domain'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
