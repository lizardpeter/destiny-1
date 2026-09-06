#!/usr/bin/env python3
"""Recursively close source-owned D1 world/entity package dependencies.

The input placement manifest comes from d1_world_activity_entity_resource_census.py.
This driver repeatedly runs d1_world_entity_dependency_census.py, converts every
unresolved Tiger FileHash into its package-id namespace, recovers exactly the
current physical package family for each newly required package id, and reruns
until the dependency graph closes or no new package id can be added.

No package filename is treated as semantic ownership evidence. Expansion is driven
only by unresolved serialized FileHash/TagHash values emitted by the dependency
census. Optional prior member catalogs are used only as byte-location accelerators;
the current packages.txt family membership must match the catalog exactly before an
offset is trusted. Uncatalogued package IDs fall back to a validated split-TAR scan.
Every recovered member records its offset, size and freshly measured SHA-256.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from d1_split_tar_extract import SplitHttpTar

NULLS = {'00000000', 'FFFFFFFF'}


def norm(x: str) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def pkgid_from_hash(h: str) -> str | None:
    h = norm(h)
    if h in NULLS:
        return None
    # Keep the project-wide D1 FileHash/package mapping. For the 0x8080xxxx
    # namespace used by current world dependencies this reduces to the familiar
    # package-id field, but writing the bit expression avoids an 0x80800000-only
    # assumption if this driver is later reused more broadly.
    v = int(h, 16)
    pkg = ((v >> 13) & 0x3FF) + ((((v >> 23) & 3) - 1) * 0x400)
    if pkg < 0:
        return None
    return f'{pkg:04x}'


def pkgid_from_name(name: str) -> str | None:
    m = re.search(r'_([0-9a-fA-F]{4})_[0-9]+\.pkg$', Path(name).name)
    return m.group(1).lower() if m else None


def current_family_names(package_list: Path, ids: set[str]) -> dict[str, list[str]]:
    names = {Path(x.strip()).name for x in package_list.read_text(errors='replace').splitlines() if x.strip()}
    out = {i: sorted(n for n in names if pkgid_from_name(n) == i) for i in sorted(ids)}
    missing = [i for i, rows in out.items() if not rows]
    if missing:
        raise RuntimeError(f'package ids absent from current packages.txt: {missing}')
    return out


def load_member_catalogs(paths: list[Path]) -> tuple[dict[str, dict[str, dict]], list[dict]]:
    """Merge flexible historical member catalogs by package id and basename."""
    merged: dict[str, dict[str, dict]] = {}
    provenance = []
    for path in paths:
        doc = json.loads(path.read_text())
        fams = doc.get('families', {})
        provenance.append({
            'path': str(path),
            'schema': doc.get('schema') or doc.get('schema_version'),
            'status': doc.get('status'),
            'source': doc.get('source'),
            'provenance': doc.get('provenance'),
        })
        for fid, rows in fams.items():
            fid = str(fid).lower().zfill(4)
            dst = merged.setdefault(fid, {})
            for row in rows:
                name = Path(row['name']).name
                off = row.get('data_offset')
                size = row.get('size')
                if off is None or size is None:
                    continue
                parsed_off = int(off, 0) if isinstance(off, str) else int(off)
                parsed_size = int(size, 0) if isinstance(size, str) else int(size)
                normalized = {'name': name, 'data_offset': parsed_off, 'size': parsed_size,
                              'catalog': str(path)}
                old = dst.get(name)
                if old and (old['data_offset'], old['size']) != (parsed_off, parsed_size):
                    raise RuntimeError(f'conflicting member catalog rows for {name}: {old} vs {normalized}')
                dst[name] = normalized
    return merged, provenance


def catalog_family_locations(fid: str, current_names: list[str], catalogs: dict[str, dict[str, dict]]) -> dict[str, dict] | None:
    rows = catalogs.get(fid)
    if not rows:
        return None
    # A historical catalog is usable only if it describes the complete current
    # physical family. This prevents stale patch-generation catalogs from silently
    # constructing the wrong logical package.
    if sorted(rows) != sorted(current_names):
        return None
    return {name: rows[name] for name in current_names}


def run_census(runtime: Path, placements: Path, snapshots: list[Path], out: Path) -> dict:
    cmd = [sys.executable, str(HERE / 'd1_world_entity_dependency_census.py')]
    for p in snapshots:
        cmd += ['--snapshot', str(p)]
    cmd += ['--runtime', str(runtime), '--placements', str(placements), '--out', str(out)]
    cp = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout = out.with_suffix(out.suffix + '.stdout.txt')
    stdout.write_text(cp.stdout)
    if cp.returncode not in (0, 2):
        raise RuntimeError(f'dependency census failed rc={cp.returncode}; see {stdout}')
    return json.loads(out.read_text())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', type=Path, action='append', required=True,
                    help='Initial world/dependency package snapshot. Repeatable.')
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--placements', type=Path, required=True)
    ap.add_argument('--package-list', type=Path, required=True)
    ap.add_argument('--member-catalog', type=Path, action='append', default=[],
                    help='Optional previously proven physical member-offset catalog. Repeatable.')
    ap.add_argument('--expansion-dir', type=Path, required=True)
    ap.add_argument('--work-dir', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True,
                    help='Final closed/partial dependency census JSON.')
    ap.add_argument('--report', type=Path, required=True,
                    help='Recursive package-expansion provenance report.')
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
    stop_reason = None
    final = None

    for pass_index in range(a.max_passes):
        census_path = a.work_dir / f'entity_dependency_pass_{pass_index:02d}.json'
        dep = run_census(a.runtime.resolve(), a.placements.resolve(), snapshots, census_path)
        unresolved = [norm(x) for x in dep.get('unresolved_dependency_hashes', []) if norm(x) not in NULLS]
        unresolved_ids = sorted({x for x in (pkgid_from_hash(h) for h in unresolved) if x})
        new_ids = [x for x in unresolved_ids if x not in present_ids]
        row = {
            'pass': pass_index,
            'status': dep.get('status'),
            'snapshot_count': len(snapshots),
            'present_package_ids': sorted(present_ids),
            'unresolved_dependency_hash_count': len(unresolved),
            'unresolved_dependency_hashes': unresolved,
            'unresolved_package_ids': unresolved_ids,
            'new_package_ids': new_ids,
            'census': str(census_path),
            'recovered_members': [],
            'location_modes': {},
        }
        passes.append(row)
        final = dep

        if not unresolved:
            stop_reason = 'closed_no_unresolved_dependencies'
            break
        if not new_ids:
            stop_reason = 'unresolved_dependencies_but_no_new_package_ids'
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
                'selection_basis': 'unresolved_serialized_filehash_package_id',
            }
            recovered_members.append(member)
            row['recovered_members'].append(member)
            snapshots.append(dst.resolve())
        present_ids.update(new_ids)
    else:
        stop_reason = 'max_passes_reached'

    if final is None:
        raise RuntimeError('no dependency census pass executed')

    a.out.write_text(json.dumps(final, indent=2) + '\n')
    report = {
        'schema_version': 2,
        'status': 'D1_WORLD_ENTITY_DEPENDENCY_EXPANSION_CLOSED'
                  if final.get('status', '').endswith('_COMPLETE')
                  else 'D1_WORLD_ENTITY_DEPENDENCY_EXPANSION_PARTIAL',
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
        'final_dependency_status': final.get('status'),
        'final_unresolved_dependency_hashes': final.get('unresolved_dependency_hashes', []),
        'final_unresolved_dependency_package_ids': final.get('unresolved_dependency_package_ids', {}),
        'policy': (
            'Package expansion is driven only by unresolved serialized dependency hashes. '
            'Filename text is used only to map a derived package id to current physical family members. '
            'Prior member catalogs accelerate byte location only when their complete family membership equals current packages.txt; '
            'otherwise the tool falls back to split-TAR discovery. No filename or catalog assigns semantic ownership.'
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
        'final_dependency_status': report['final_dependency_status'],
        'final_unresolved_dependency_package_ids': report['final_unresolved_dependency_package_ids'],
    }, indent=2))
    return 0 if report['status'].endswith('_CLOSED') else 2


if __name__ == '__main__':
    raise SystemExit(main())
