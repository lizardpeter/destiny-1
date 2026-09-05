#!/usr/bin/env python3
"""Inspect D1 Guardian mesh vertex/weight representations across package families.

This is a forensic companion to d1_remote_guardian_joint_probe.  It records, per
mesh, the exact primary-stream joint-lane distribution plus all four model-side
resource fields (vertices1, vertices2, old_weights, unk_resource, indices), and
resolves each resource's entry metadata and linked payload metadata through the
verified multi-package logical view.

It does not assign semantics to old_weights, unk_resource, or the 0x7FFF lane
value.  The goal is to identify the byte-level alternate representation used by
meshes that cannot be explained by the already-validated simple rigid lane.
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

from d1_entity_model_probe import parse_model
from d1_investment_arrangement_probe import filehash_pkg_index
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_remote_model_export import MultiPackageReader, models_from_report
from d1_split_tar_extract import SplitHttpTar


def meta(by: dict[str, dict], tag: str, r: MultiPackageReader) -> dict:
    h = tag.upper()
    if h in ('FFFFFFFF', '00000000'):
        return {'tag_hash': h, 'present': False}
    e = by.get(h)
    if e is None:
        pkg, idx = filehash_pkg_index(int(h, 16))
        return {'tag_hash': h, 'present': False, 'package_id': f'{pkg:04X}', 'file_index': idx}
    row = {
        'tag_hash': h, 'present': True, 'entry_index': e['index'],
        'package_id': f"{int(e.get('_source_package_id', -1)):04X}" if e.get('_source_package_id') is not None else None,
        'type': e['type'], 'subtype': e['subtype'], 'size': e['file_size'],
        'reference': e['reference'].upper(),
    }
    linked = by.get(e['reference'].upper())
    if linked is not None:
        row['linked_payload'] = {
            'tag_hash': linked['tag_hash'].upper(), 'entry_index': linked['index'],
            'package_id': f"{int(linked.get('_source_package_id', -1)):04X}" if linked.get('_source_package_id') is not None else None,
            'type': linked['type'], 'subtype': linked['subtype'], 'size': linked['file_size'],
            'reference': linked['reference'].upper(),
        }
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--report', type=Path, required=True)
    ap.add_argument('--body-role', choices=('masculine', 'feminine'), required=True)
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    selected = models_from_report(json.loads(a.report.read_text()), a.body_role)
    catalogs = load_catalogs(a.member_catalog)
    base = a.base_url.rstrip('/')
    arc = SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    views = {pkg: RemoteLogicalPackage(arc, fam, a.runtime) for pkg, fam in sorted(catalogs.items())}
    r = MultiPackageReader(views)
    by = {e['tag_hash'].upper(): e for e in r.entries}

    rows = []
    all_unk = collections.Counter()
    all_old = collections.Counter()
    for sel in selected:
        tag = sel['tag_hash'].upper()
        e = by[tag]
        model = parse_model(r.entry(e['index']), 'PS4')
        mrow = {**sel, 'tag_hash': tag, 'mesh_count': model['mesh_count'], 'meshes': []}
        for mi, mesh in enumerate(model['meshes']):
            resources = {field: meta(by, mesh[field], r) for field in ('vertices1','vertices2','old_weights','unk_resource','indices')}
            vh = by.get(mesh['vertices1'].upper())
            lane_dist = collections.Counter()
            stride0 = None
            if vh is not None:
                vp = by.get(vh['reference'].upper())
                if vp is not None:
                    hb = r.entry(vh['index']); pb = r.entry(vp['index'])
                    stride0 = struct.unpack_from('<h', hb, 4)[0]
                    if stride0 >= 8 and len(pb) % stride0 == 0:
                        lane_dist.update(struct.unpack_from('<h', pb, off + 6)[0] for off in range(0, len(pb), stride0))
            vh2 = by.get(mesh['vertices2'].upper())
            stride1 = None
            if vh2 is not None:
                hb2 = r.entry(vh2['index'])
                if len(hb2) >= 6:
                    stride1 = struct.unpack_from('<h', hb2, 4)[0]
            all_unk[mesh['unk_resource'].upper()] += 1
            all_old[mesh['old_weights'].upper()] += 1
            mrow['meshes'].append({
                'mesh_index': mi,
                'vertices1': mesh['vertices1'].upper(), 'vertices2': mesh['vertices2'].upper(),
                'old_weights': mesh['old_weights'].upper(), 'unk_resource': mesh['unk_resource'].upper(),
                'indices': mesh['indices'].upper(), 'stride0': stride0, 'stride1': stride1,
                'vertex_count': sum(lane_dist.values()),
                'joint_lane_values': sorted(lane_dist),
                'joint_lane_distribution': {str(k): v for k, v in sorted(lane_dist.items())},
                'contains_7fff': 32767 in lane_dist,
                'all_7fff': bool(lane_dist) and set(lane_dist) == {32767},
                'resources': resources,
            })
        rows.append(mrow)

    rep = {
        'schema': 'd1_guardian_vertex_representation_probe/v1',
        'body_role': a.body_role,
        'model_count': len(rows),
        'old_weights_values': dict(all_old),
        'unk_resource_values': dict(all_unk),
        'models': rows,
        'policy': 'No semantics are assigned to 0x7FFF, old_weights, or unk_resource. Metadata and lane values are read from exact retail resources across verified logical package views.',
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(rep, indent=2) + '\n')
    print(json.dumps({k: rep[k] for k in ('body_role','model_count','old_weights_values','unk_resource_values')}, indent=2))
    for m in rows:
        ex = (m.get('examples') or [{}])[0]
        print('\nMODEL', ex.get('name'), m['tag_hash'])
        for x in m['meshes']:
            ur = x['resources']['unk_resource']
            print(' mesh',x['mesh_index'],'stride',x['stride0'],x['stride1'],'lane',x['joint_lane_values'],
                  'old',x['old_weights'],'unk',x['unk_resource'],'unk_ref',ur.get('reference'),
                  'unk_linked', (ur.get('linked_payload') or {}).get('reference'),
                  'all7fff',x['all_7fff'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
