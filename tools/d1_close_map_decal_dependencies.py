#!/usr/bin/env python3
"""Recursively close D1 map decal dependencies through the global package index.

The completed map-layer census supplies only Activity-owned SMapDecalsResource rows.
``d1_world_map_decal_census.py`` then exposes serialized SMapDecals collection,
Material and SOcclusionBounds FileHashes. This driver recovers only package families
named by those exact hashes and reruns until the decal census is complete or no new
progress is possible.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def snapshots(root: Path) -> list[Path]:
    return sorted(p.resolve() for p in root.glob('*.pkg') if p.is_file())


def run(cmd: list[str], log: Path, allow_nonzero: bool = False) -> int:
    cp = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(cp.stdout)
    if cp.returncode and not allow_nonzero:
        raise RuntimeError(f'command failed rc={cp.returncode}: {cmd}\nsee {log}')
    return cp.returncode


def recover(index: Path, package_list: Path, package_dir: Path, work_dir: Path,
            package_ids: list[str], pass_no: int) -> list[str]:
    ids = sorted(set(str(x).lower().zfill(4) for x in package_ids))
    if not ids:
        return []
    report = work_dir / f'recovery_{pass_no:02d}.json'
    cmd = [sys.executable, str(HERE / 'd1_recover_indexed_package_families.py'),
           '--index', str(index), '--package-list', str(package_list),
           '--out-dir', str(package_dir), '--report', str(report)]
    for p in ids:
        cmd += ['--package-id', p]
    run(cmd, work_dir / f'recovery_{pass_no:02d}.stdout.txt')
    d = json.loads(report.read_text())
    if d.get('status') != 'D1_INDEXED_PACKAGE_FAMILY_RECOVERY_COMPLETE':
        raise RuntimeError(f'indexed package recovery incomplete: {d.get("status")}')
    return ids


def census(a, pass_no: int) -> tuple[dict, Path, int]:
    out = a.work_dir / f'decal_census_{pass_no:02d}.json'
    cmd = [sys.executable, str(HERE / 'd1_world_map_decal_census.py')]
    for p in snapshots(a.package_dir):
        cmd += ['--snapshot', str(p)]
    cmd += ['--runtime', str(a.runtime), '--layer-census', str(a.layer_census), '--out', str(out)]
    rc = run(cmd, a.work_dir / f'decal_census_{pass_no:02d}.stdout.txt', allow_nonzero=True)
    if not out.exists():
        raise RuntimeError(f'decal census pass {pass_no} emitted no JSON')
    return json.loads(out.read_text()), out, rc


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--index', type=Path, required=True)
    ap.add_argument('--package-list', type=Path, required=True)
    ap.add_argument('--layer-census', type=Path, required=True)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--package-dir', type=Path, required=True)
    ap.add_argument('--work-dir', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    ap.add_argument('--max-passes', type=int, default=12)
    a = ap.parse_args()

    idx = json.loads(a.index.read_text())
    if idx.get('status') != 'D1_REMOTE_ACTIVITY_INDEX_COMPLETE':
        raise SystemExit('global Activity index is not complete')
    a.package_dir.mkdir(parents=True, exist_ok=True)
    a.work_dir.mkdir(parents=True, exist_ok=True)
    initial = len(snapshots(a.package_dir))
    if not initial:
        raise SystemExit('package-dir has no source-owned decal collection families')

    passes = []
    recovered: set[str] = set()
    final = None
    final_path = None
    stop = None
    for i in range(a.max_passes):
        d, p, rc = census(a, i)
        final, final_path = d, p
        missing = sorted(str(x).lower().zfill(4) for x in d.get('missing_dependency_package_ids', {}))
        new = sorted(set(missing) - recovered)
        row = {
            'pass': i,
            'snapshot_count': len(snapshots(a.package_dir)),
            'census_returncode': rc,
            'census_status': d.get('status'),
            'decal_resource_occurrences': d.get('decal_resource_occurrences'),
            'unique_decal_collection_count': d.get('unique_decal_collection_count'),
            'decal_resource_record_count': d.get('decal_resource_record_count'),
            'decal_location_count': d.get('decal_location_count'),
            'projected_decal_count': d.get('projected_decal_count'),
            'unique_material_count': d.get('unique_material_count'),
            'missing_package_ids': missing,
            'new_package_ids': new,
            'violations': d.get('violations', []),
        }
        passes.append(row)
        if d.get('status') == 'D1_WORLD_MAP_DECAL_CENSUS_COMPLETE':
            stop = 'closed_map_decal_dependencies_complete'
            break
        if not new:
            stop = 'partial_no_new_dependency_progress'
            break
        recover(a.index, a.package_list, a.package_dir, a.work_dir, new, i)
        recovered.update(new)
    else:
        stop = 'max_passes_reached'

    if final is None or final_path is None:
        raise RuntimeError('decal census never ran')
    a.out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(final_path, a.out)
    closed = final.get('status') == 'D1_WORLD_MAP_DECAL_CENSUS_COMPLETE'
    report = {
        'schema_version': 1,
        'status': 'D1_WORLD_MAP_DECAL_DEPENDENCY_CLOSURE_COMPLETE' if closed else 'D1_WORLD_MAP_DECAL_DEPENDENCY_CLOSURE_PARTIAL',
        'stop_reason': stop,
        'initial_snapshot_count': initial,
        'final_snapshot_count': len(snapshots(a.package_dir)),
        'recovered_package_ids': sorted(recovered),
        'passes': passes,
        'final_decal_summary': {k: final.get(k) for k in (
            'status','source_map_data_table_count','source_entry_count','decal_resource_occurrences',
            'nonnull_decal_collection_occurrences','explicit_null_decal_collection_occurrences',
            'unique_decal_collection_count','decal_resource_record_count','decal_location_count',
            'projected_decal_count','unique_material_count','material_reference_counts',
            'missing_dependency_package_ids','violations'
        )},
        'policy': (
            'Every recovered package family is selected only by a serialized SMapDecals collection, Material or '
            'SOcclusionBounds FileHash emitted by the source-pinned decal parser. No package filename, material name, '
            'projection appearance or Blender heuristic is used as dependency evidence.'
        ),
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({
        'status': report['status'], 'stop_reason': stop,
        'recovered_package_ids': report['recovered_package_ids'],
        'final_decal_summary': report['final_decal_summary'],
    }, indent=2))
    return 0 if closed else 2


if __name__ == '__main__':
    raise SystemExit(main())
