#!/usr/bin/env python3
"""Export every serialized D1 model part/LOD/material variant losslessly.

This is the forensic companion to d1_remote_model_export.py. The ordinary remote
exporter intentionally deduplicates parts that share one index range, which is
useful for visual previews. This tool passes unique_ranges=False to the validated
D1 geometry decoder so every serialized mesh part is preserved independently.

Because trimesh reuses a scene node name when duplicate index ranges receive the
same historical geometry name, the exported scene is immediately rebuilt with
one unique node per emitted geometry and validated after round-trip. Material
identity/LOD/part provenance remains authoritative in the adjacent JSON report.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import trimesh

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_entity_model_export import export_model
from d1_investment_arrangement_probe import filehash_pkg_index
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_remote_model_export import MultiPackageReader
from d1_split_tar_extract import SplitHttpTar


def norm(v: str) -> str:
    return str(v).upper().removeprefix('0X').zfill(8)


def models_from_plan(path: Path) -> list[str]:
    d = json.loads(path.read_text())
    vals = d.get('model_hashes')
    if vals is None:
        vals = []
        for row in d.get('models', []):
            if isinstance(row, str):
                vals.append(row)
            elif isinstance(row, dict):
                vals.append(row.get('model') or row.get('tag_hash'))
    out = []
    seen = set()
    for v in vals:
        if not v:
            continue
        h = norm(v)
        if h not in seen:
            seen.add(h)
            out.append(h)
    return out


def rebuild_unique_nodes(path: Path) -> tuple[int, int]:
    src = trimesh.load(path, force='scene', process=False)
    fixed = trimesh.Scene()
    for i, (name, geom) in enumerate(src.geometry.items()):
        n = f'{i:05d}_{name}'
        fixed.add_geometry(geom.copy(), geom_name=n, node_name=n)
    fixed.export(path)
    check = trimesh.load(path, force='scene', process=False)
    geoms = len(check.geometry)
    nodes = len(check.graph.nodes_geometry)
    if nodes != geoms:
        raise RuntimeError(f'{path.name}: round-trip node/geometry mismatch {nodes}!={geoms}')
    return geoms, sum(len(g.faces) for g in check.geometry.values())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--model-plan', type=Path)
    ap.add_argument('--model', action='append', default=[])
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--out-dir', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    selected = []
    seen = set()
    if a.model_plan:
        for h in models_from_plan(a.model_plan):
            if h not in seen:
                seen.add(h); selected.append(h)
    for raw in a.model:
        h = norm(raw)
        if h not in seen:
            seen.add(h); selected.append(h)
    if not selected:
        raise SystemExit('no models selected')

    catalogs = load_catalogs(a.member_catalog)
    model_pkgs = {filehash_pkg_index(int(h, 16))[0] for h in selected}
    missing = sorted(model_pkgs - set(catalogs))
    if missing:
        raise SystemExit('missing model package catalogs: ' + ','.join(f'{x:04X}' for x in missing))

    base = a.base_url.rstrip('/')
    arc = SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    views = {pkg: RemoteLogicalPackage(arc, fam, a.runtime) for pkg, fam in sorted(catalogs.items())}
    multi = MultiPackageReader(views)
    a.out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    total_serialized_groups = 0
    total_triangles = 0
    for h in selected:
        glb = a.out_dir / f'{h}_ALL_PART_VARIANTS.glb'
        js = a.out_dir / f'{h}_ALL_PART_VARIANTS.json'
        rep = export_model(multi, h, glb, js, unique_ranges=False)
        expected = sum(len(m.get('primitive_groups', [])) for m in rep['meshes'])
        geoms, tris = rebuild_unique_nodes(glb)
        if geoms != expected:
            raise RuntimeError(f'{h}: emitted geometry mismatch {geoms}!={expected}')
        serialized_part_indices = sorted({pi for m in rep['meshes'] for g in m.get('primitive_groups', []) for pi in g.get('part_indices', [])})
        rows.append({
            'model': h,
            'mesh_count': rep['mesh_count'],
            'drawable_serialized_part_variant_count': expected,
            'drawable_serialized_part_indices': serialized_part_indices,
            'geometry_count': geoms,
            'triangle_count_with_variants': tris,
            'glb': str(glb),
            'geometry_report': str(js),
        })
        total_serialized_groups += expected
        total_triangles += tris
        print(h, 'meshes', rep['mesh_count'], 'serialized_drawable_parts', expected, 'triangles_with_variants', tris)

    out = {
        'schema': 'd1_remote_model_export_all_parts/v1',
        'status': 'D1_REMOTE_MODEL_EXPORT_ALL_PARTS_COMPLETE',
        'model_count': len(rows),
        'drawable_serialized_part_variant_count': total_serialized_groups,
        'triangle_count_with_variants': total_triangles,
        'catalog_package_ids': [f'{x:04X}' for x in sorted(views)],
        'models': rows,
        'policy': (
            'Every model is exact-source selected. Every non-empty serialized mesh part is exported independently, '
            'including duplicate index ranges used by different LOD/material/external-identifier variants. No LOD, '
            'pass, or material variant is removed from the forensic geometry archive. Adjacent JSON retains part/LOD/material provenance.'
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k:v for k,v in out.items() if k != 'models'}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
