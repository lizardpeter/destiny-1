#!/usr/bin/env python3
"""Recursively close D1 articulated-world material package dependencies.

The exact owning-parent material resolver can discover external Material FileHashes
that are not part of the SEntity/EntityResource dependency graph.  This driver
runs that resolver, derives Tiger package IDs only from unresolved serialized
selected-material FileHashes, recovers the complete current physical family for
each newly required package ID, and reruns until material binding closes or no
new package family can be added.

Package filenames are never used to infer semantic ownership.  They are used only
after a serialized FileHash has already supplied its package-id namespace, so the
current packages.txt membership can be materialized from the split public TAR.
Prior member catalogs are accepted only when their complete family membership
matches the current archive, exactly as in d1_expand_world_entity_dependencies.py.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_expand_world_entity_dependencies import (
    NULLS,
    norm,
    pkgid_from_hash,
    pkgid_from_name,
    current_family_names,
    load_member_catalogs,
    catalog_family_locations,
)
from d1_split_tar_extract import SplitHttpTar


def run_bindings(runtime: Path, plan: Path, snapshots: list[Path], out: Path, pass_index: int) -> dict:
    cmd = [sys.executable, str(HERE / 'd1_world_entity_model_material_bindings.py')]
    for p in snapshots:
        cmd += ['--snapshot', str(p)]
    cmd += ['--runtime', str(runtime), '--articulated-plan', str(plan), '--out', str(out)]
    cp = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout = out.with_suffix(out.suffix + f'.pass{pass_index:02d}.stdout.txt')
    stdout.write_text(cp.stdout)
    if cp.returncode not in (0, 2):
        raise RuntimeError(f'material binding resolver failed rc={cp.returncode}; see {stdout}')
    return json.loads(out.read_text())


def unresolved_selected_material_hashes(doc: dict) -> list[str]:
    """Return only unresolved material hashes actually selected by Charm semantics."""
    out = set()
    for binding in doc.get('bindings', []):
        for mesh in binding.get('meshes', []):
            for part in mesh.get('parts', []):
                selected = part.get('selected_material') or {}
                h = norm(selected.get('hash', 'FFFFFFFF'))
                if h in NULLS:
                    continue
                if selected.get('class_matches'):
                    continue
                out.add(h)
    return sorted(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', type=Path, action='append', required=True,
                    help='Initial world/entity package snapshot. Repeatable.')
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--articulated-plan', type=Path, required=True)
    ap.add_argument('--package-list', type=Path, required=True)
    ap.add_argument('--member-catalog', type=Path, action='append', default=[])
    ap.add_argument('--expansion-dir', type=Path, required=True)
    ap.add_argument('--work-dir', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True,
                    help='Final complete/partial material-binding report.')
    ap.add_argument('--report', type=Path, required=True,
                    help='Material package-expansion provenance report.')
    ap.add_argument('--base-url', default='https://crypt.cohae.dev/destiny/ps4/packages/latest')
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--max-passes', type=int, default=8)
    a = ap.parse_args()

    initial = [p.resolve() for p in a.snapshot]
    snapshots = list(initial)
    present_ids = {x for x in (pkgid_from_name(p.name) for p in snapshots) if x}
    a.expansion_dir.mkdir(parents=True, exist_ok=True)
    a.work_dir.mkdir(parents=True, exist_ok=True)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.report.parent.mkdir(parents=True, exist_ok=True)
    catalogs, catalog_provenance = load_member_catalogs(a.member_catalog)

    archive = SplitHttpTar(
        [f'{a.base_url.rstrip("/")}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)],
        retries=6,
        timeout=120,
    )

    passes = []
    recovered_members = []
    final = None
    stop_reason = None

    for pass_index in range(a.max_passes):
        pass_out = a.work_dir / f'material_bindings_pass_{pass_index:02d}.json'
        material = run_bindings(a.runtime.resolve(), a.articulated_plan.resolve(), snapshots, pass_out, pass_index)
        unresolved = unresolved_selected_material_hashes(material)
        unresolved_ids = sorted({x for x in (pkgid_from_hash(h) for h in unresolved) if x})
        new_ids = [x for x in unresolved_ids if x not in present_ids]
        row = {
            'pass': pass_index,
            'status': material.get('status'),
            'snapshot_count': len(snapshots),
            'present_package_ids': sorted(present_ids),
            'unresolved_selected_material_hash_count': len(unresolved),
            'unresolved_selected_material_hashes': unresolved,
            'unresolved_package_ids': unresolved_ids,
            'new_package_ids': new_ids,
            'material_bindings': str(pass_out),
            'recovered_members': [],
            'location_modes': {},
        }
        passes.append(row)
        final = material

        if material.get('status') == 'D1_WORLD_ENTITY_MODEL_MATERIAL_BINDINGS_COMPLETE':
            stop_reason = 'closed_material_bindings_complete'
            break
        if not unresolved:
            stop_reason = 'partial_without_unresolved_selected_material_hashes'
            break
        if not new_ids:
            stop_reason = 'unresolved_materials_but_no_new_package_ids'
            break

        families = current_family_names(a.package_list, set(new_ids))
        locations: dict[str, dict] = {}
        scan_wanted = set()
        for fid, names in families.items():
            cat = catalog_family_locations(fid, names, catalogs)
            if cat is not None:
                locations.update(cat)
                row['location_modes'][fid] = 'validated_prior_member_catalog'
            else:
                scan_wanted.update(names)
                row['location_modes'][fid] = 'validated_split_tar_scan'

        if scan_wanted:
            found, headers = archive.find(scan_wanted)
            missing = sorted(scan_wanted - set(found))
            if missing:
                raise RuntimeError(f'current package members not found in split TAR: {missing}')
            row['tar_headers_scanned'] = headers
            locations.update(found)
        else:
            row['tar_headers_scanned'] = 0

        for name in sorted({n for rows in families.values() for n in rows}):
            info = locations[name]
            dst = a.expansion_dir / name
            sha = archive.copy_to(int(info['data_offset']), int(info['size']), dst)
            member = {
                'pass': pass_index,
                'package_id': pkgid_from_name(name),
                'name': name,
                'data_offset': int(info['data_offset']),
                'size': int(info['size']),
                'sha256': sha,
                'output': str(dst),
                'location_mode': row['location_modes'][pkgid_from_name(name)],
                'member_catalog': info.get('catalog') if isinstance(info, dict) else None,
                'selection_basis': 'unresolved_selected_external_material_filehash_package_id',
            }
            recovered_members.append(member)
            row['recovered_members'].append(member)
            snapshots.append(dst.resolve())
        present_ids.update(new_ids)
    else:
        stop_reason = 'max_passes_reached'

    if final is None:
        raise RuntimeError('no material binding pass executed')

    a.out.write_text(json.dumps(final, indent=2) + '\n')
    closed = final.get('status') == 'D1_WORLD_ENTITY_MODEL_MATERIAL_BINDINGS_COMPLETE'
    report = {
        'schema_version': 1,
        'status': 'D1_WORLD_MATERIAL_DEPENDENCY_EXPANSION_CLOSED' if closed
                  else 'D1_WORLD_MATERIAL_DEPENDENCY_EXPANSION_PARTIAL',
        'stop_reason': stop_reason,
        'initial_snapshot_count': len(initial),
        'final_snapshot_count': len(snapshots),
        'initial_package_ids': sorted({x for x in (pkgid_from_name(p.name) for p in initial) if x}),
        'final_package_ids': sorted(present_ids),
        'recovered_package_ids': sorted({x['package_id'] for x in recovered_members if x.get('package_id')}),
        'recovered_member_count': len(recovered_members),
        'recovered_members': recovered_members,
        'member_catalog_provenance': catalog_provenance,
        'passes': passes,
        'final_material_binding_status': final.get('status'),
        'final_violations': final.get('violations', []),
        'policy': (
            'Expansion is driven only by unresolved serialized Material FileHashes selected through the exact '
            'owning EntityResource external-material map. Filename text is used only to materialize the current '
            'physical family for a FileHash-derived package id. No material identity, package adjacency, or '
            'visual similarity is guessed.'
        ),
    }
    a.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({
        'status': report['status'],
        'stop_reason': stop_reason,
        'passes': len(passes),
        'recovered_package_ids': report['recovered_package_ids'],
        'recovered_member_count': report['recovered_member_count'],
        'location_modes_by_pass': [p.get('location_modes', {}) for p in passes],
        'final_material_binding_status': report['final_material_binding_status'],
        'final_violations': report['final_violations'],
    }, indent=2))
    return 0 if closed else 2


if __name__ == '__main__':
    raise SystemExit(main())
