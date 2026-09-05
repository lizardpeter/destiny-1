#!/usr/bin/env python3
"""Probe rigid Guardian gear joint indices across verified remote D1 package families.

Real Guardian s_entity_model resources can reference vertex/index streams in other
package families. This tool reuses the exact MultiPackageReader used by the remote
model exporter and applies the project's retail-validated PS4 rigid-joint lane:
for meshes with old_weights == FFFFFFFF, primary vertex stream int16 lane 3 is the
stored rigid joint index.

The output intentionally reports numeric joint indices only. Mapping those indices
to a skeleton is a separate evidence step so this tool does not silently assume a
particular player rig.
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

from d1_entity_model_probe import D1_ENTITY_MODEL_CLASS, parse_model
from d1_investment_arrangement_probe import filehash_pkg_index
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_remote_model_export import MultiPackageReader, models_from_report
from d1_split_tar_extract import SplitHttpTar


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--report', type=Path, required=True,
                    help='d1_playable_guardian_entity_resource_resolve/v1 report')
    ap.add_argument('--body-role', choices=('masculine', 'feminine'), required=True)
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    source = json.loads(a.report.read_text())
    selected = models_from_report(source, a.body_role)
    if not selected:
        raise SystemExit('no models selected from report/body role')

    catalogs = load_catalogs(a.member_catalog)
    model_pkgs = {filehash_pkg_index(int(x['tag_hash'], 16))[0] for x in selected}
    missing = sorted(model_pkgs - set(catalogs))
    if missing:
        raise SystemExit('missing member catalogs for model package(s): ' + ', '.join(f'{x:04X}' for x in missing))

    base = a.base_url.rstrip('/')
    arc = SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    views = {pkg: RemoteLogicalPackage(arc, fam, a.runtime) for pkg, fam in sorted(catalogs.items())}
    r = MultiPackageReader(views)
    by = {e['tag_hash'].upper(): e for e in r.entries}

    rows = []
    all_dist = collections.Counter()
    errors = []
    for sel in selected:
        tag = sel['tag_hash'].upper()
        rec = {**sel, 'tag_hash': tag}
        e = by.get(tag)
        if e is None:
            rec.update(resolved=False, reason='model hash absent from verified logical views')
            rows.append(rec)
            continue
        rec.update(entry_index=e['index'], reference=e['reference'].upper(), size=e['file_size'])
        if e['reference'].upper() != D1_ENTITY_MODEL_CLASS:
            rec.update(resolved=False, reason=f"entry reference is {e['reference']}, not {D1_ENTITY_MODEL_CLASS}")
            rows.append(rec)
            continue
        try:
            model = parse_model(r.entry(e['index']), 'PS4')
            meshes = []
            model_dist = collections.Counter()
            for mi, mesh in enumerate(model['meshes']):
                mrow = {'mesh_index': mi, 'old_weights': mesh['old_weights']}
                if mesh['old_weights'].upper() != 'FFFFFFFF':
                    mrow['representation'] = 'weighted_not_decoded'
                    meshes.append(mrow)
                    continue
                vh = by.get(mesh['vertices1'].upper())
                if vh is None:
                    raise KeyError(f"{tag} mesh {mi}: missing vertex header {mesh['vertices1']}")
                vp = by.get(vh['reference'].upper())
                if vp is None:
                    raise KeyError(f"{tag} mesh {mi}: missing vertex payload {vh['reference']}")
                hb = r.entry(vh['index'])
                pb = r.entry(vp['index'])
                if len(hb) < 6:
                    raise ValueError(f'{tag} mesh {mi}: short vertex header')
                stride = struct.unpack_from('<h', hb, 4)[0]
                if stride < 8 or stride > 128 or stride % 2:
                    raise ValueError(f'{tag} mesh {mi}: invalid primary stride {stride}')
                if len(pb) % stride:
                    raise ValueError(f'{tag} mesh {mi}: payload {len(pb)} not divisible by stride {stride}')
                vals = [struct.unpack_from('<h', pb, off + 6)[0] for off in range(0, len(pb), stride)]
                dist = collections.Counter(vals)
                model_dist.update(dist)
                all_dist.update(dist)
                mrow.update({
                    'representation': 'rigid_primary_stream_lane3',
                    'vertices1': mesh['vertices1'].upper(),
                    'vertex_header_package': f"{int(vh.get('_source_package_id', -1)):04X}" if vh.get('_source_package_id') is not None else None,
                    'vertex_payload': vh['reference'].upper(),
                    'vertex_payload_package': f"{int(vp.get('_source_package_id', -1)):04X}" if vp.get('_source_package_id') is not None else None,
                    'stride': stride,
                    'vertex_count': len(vals),
                    'joint_values': sorted(dist),
                    'joint_distribution': {str(k): v for k, v in sorted(dist.items())},
                })
                meshes.append(mrow)
            pkg, idx = filehash_pkg_index(int(tag, 16))
            rec.update({
                'resolved': True,
                'package_id': f'{pkg:04X}',
                'file_index': idx,
                'mesh_count': model['mesh_count'],
                'rigid_mesh_count': sum(x.get('representation') == 'rigid_primary_stream_lane3' for x in meshes),
                'weighted_mesh_count': sum(x.get('representation') == 'weighted_not_decoded' for x in meshes),
                'joint_domain': sorted(model_dist),
                'joint_distribution': {str(k): v for k, v in sorted(model_dist.items())},
                'meshes': meshes,
            })
        except Exception as ex:
            rec.update(resolved=False, error=repr(ex))
            errors.append({'tag_hash': tag, 'error': repr(ex)})
        rows.append(rec)

    report = {
        'schema': 'd1_remote_guardian_joint_probe/v1',
        'body_role': a.body_role,
        'selected_model_count': len(selected),
        'resolved_model_count': sum(bool(x.get('resolved')) for x in rows),
        'model_owner_package_ids': [f'{x:04X}' for x in sorted(model_pkgs)],
        'available_cross_package_family_ids': [f'{x:04X}' for x in sorted(views)],
        'joint_domain': sorted(all_dist),
        'joint_distribution': {str(k): v for k, v in sorted(all_dist.items())},
        'models': rows,
        'errors': errors,
        'policy': (
            'Only old_weights==FFFFFFFF meshes are interpreted. Stored rigid joint indices use the '
            'retail-validated PS4 primary-stream int16 lane 3. Vertex resources are resolved by exact '
            'FileHash across verified package families. This report does not assume or assign a skeleton.'
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('body_role','selected_model_count','resolved_model_count','joint_domain')}, indent=2))
    for x in rows:
        ex = (x.get('examples') or [{}])[0]
        print(ex.get('name', 'unnamed'), x['tag_hash'], 'rigid', x.get('rigid_mesh_count'),
              'weighted', x.get('weighted_mesh_count'), 'joints', x.get('joint_domain'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
