#!/usr/bin/env python3
"""Export exact D1 s_entity_model assets directly from verified split-TAR ranges.

The tool can consume a d1_playable_guardian_entity_resource_resolve/v1 report
and select all embedded models for one body role, or accept explicit --model
FileHashes.  Geometry decoding is delegated to the project's validated generic
D1 entity-model exporter; RemoteLogicalPackage supplies the exact logical Tiger
bytes without downloading whole package families.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import trimesh

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_investment_arrangement_probe import filehash_pkg_index
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_split_tar_extract import SplitHttpTar
from d1_entity_model_export import export_model


def models_from_report(report: dict, body_role: str | None) -> list[dict]:
    rows = []
    seen = set()
    if body_role:
        for arr in report.get('arrangements', []):
            for branch in arr.get('resolved_body_assignments', []):
                if branch.get('body_role') != body_role:
                    continue
                ent = branch.get('entity_resolution') or {}
                for res in ent.get('resources', []):
                    m = res.get('embedded_model') or {}
                    tag = m.get('tag_hash')
                    if tag and m.get('resolved') and tag not in seen:
                        seen.add(tag)
                        rows.append({
                            'tag_hash': tag,
                            'className': arr.get('className'),
                            'arrangement_index': arr.get('arrangement_index'),
                            'body_role': body_role,
                            'examples': arr.get('examples', []),
                            'entity_hash': ent.get('entity_hash'),
                            'entity_resource_hash': res.get('resource_hash'),
                        })
    else:
        for m in report.get('models', []):
            tag = m.get('tag_hash')
            if tag and m.get('resolved') and tag not in seen:
                seen.add(tag)
                rows.append({'tag_hash': tag})
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--report', type=Path, help='Guardian entity-resource resolution report')
    ap.add_argument('--body-role', choices=('masculine', 'feminine'))
    ap.add_argument('--model', action='append', default=[])
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--out-dir', type=Path, required=True)
    ap.add_argument('--combined-glb', type=Path)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    selected = []
    if a.report:
        selected.extend(models_from_report(json.loads(a.report.read_text()), a.body_role))
    known = {x['tag_hash'].upper() for x in selected}
    for raw in a.model:
        tag = raw.upper().removeprefix('0X')
        if tag not in known:
            selected.append({'tag_hash': tag, 'source': 'explicit_cli'})
            known.add(tag)
    if not selected:
        raise SystemExit('no models selected')

    catalogs = load_catalogs(a.member_catalog)
    needed = {filehash_pkg_index(int(x['tag_hash'], 16))[0] for x in selected}
    missing = sorted(needed - set(catalogs))
    if missing:
        raise SystemExit('missing member catalogs for model package(s): ' + ', '.join(f'{x:04X}' for x in missing))

    base = a.base_url.rstrip('/')
    arc = SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    views = {pkg: RemoteLogicalPackage(arc, catalogs[pkg], a.runtime) for pkg in sorted(needed)}

    a.out_dir.mkdir(parents=True, exist_ok=True)
    exported = []
    combined = trimesh.Scene()

    for row in selected:
        tag = row['tag_hash'].upper()
        pkg, idx = filehash_pkg_index(int(tag, 16))
        view = views[pkg]
        # d1_entity_model_export only needs .pkg as provenance text in addition to
        # the shared .h/.entries/.entry interface, so provide a synthetic Path.
        view.pkg = Path(view.view.name)
        glb = a.out_dir / f'{tag}.glb'
        rep_path = a.out_dir / f'{tag}.json'
        rep = export_model(view, tag, glb, rep_path)
        exported.append({**row, 'package_id': pkg, 'file_index': idx, 'glb': str(glb), 'geometry_report': str(rep_path),
                         'mesh_count': rep['mesh_count'], 'geometry_count': rep['geometry_count'],
                         'triangle_count': rep['triangle_count'], 'bounds': rep['bounds']})
        scene = trimesh.load(glb, force='scene', process=False)
        for gi, (name, geom) in enumerate(scene.geometry.items()):
            cname = f'{tag}_{gi}_{name}'
            combined.add_geometry(geom.copy(), geom_name=cname, node_name=cname)

    combined_path = a.combined_glb
    if combined_path:
        combined_path.parent.mkdir(parents=True, exist_ok=True)
        combined.export(combined_path)

    report = {
        'schema': 'd1_remote_model_export/v1',
        'selected_model_count': len(selected),
        'exported_model_count': len(exported),
        'body_role': a.body_role,
        'package_ids': [f'{x:04X}' for x in sorted(needed)],
        'total_geometry_count': sum(x['geometry_count'] for x in exported),
        'total_triangle_count': sum(x['triangle_count'] for x in exported),
        'combined_glb': str(combined_path) if combined_path else None,
        'combined_bounds': combined.bounds.tolist() if combined.bounds is not None else None,
        'models': exported,
        'policy': 'Every model FileHash originates from an exact retail s_entity -> EntityResource -> embedded s_entity_model edge. Geometry is decoded from the exact logical package view; no model selection or placement is guessed.',
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'models'}, indent=2))
    for x in exported:
        print(x['tag_hash'], f"pkg={x['package_id']:04X}", 'meshes', x['mesh_count'], 'geoms', x['geometry_count'], 'triangles', x['triangle_count'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
