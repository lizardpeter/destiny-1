#!/usr/bin/env python3
"""Recursively close D1 map light/sky dependencies through the global package index.

The input map-data layer census supplies only source-owned SMapDataEntry rows. This tool
runs the evidence-bounded ``d1_world_map_lighting_census_v2.py``, recovers package
families named by serialized FileHashes, and reruns until the light/sky census is
complete or no dependency progress is possible.

No package filename, destination name, light appearance, or Blender heuristic is used.
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
    ids = sorted(set(x.lower().zfill(4) for x in package_ids))
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


def run_census(a, pass_no: int) -> tuple[dict, Path, int]:
    out = a.work_dir / f'lighting_census_{pass_no:02d}.json'
    cmd = [sys.executable, str(HERE / 'd1_world_map_lighting_census_v2.py')]
    for p in snapshots(a.package_dir):
        cmd += ['--snapshot', str(p)]
    cmd += ['--runtime', str(a.runtime), '--layer-census', str(a.layer_census), '--out', str(out)]
    rc = run(cmd, a.work_dir / f'lighting_census_{pass_no:02d}.stdout.txt', allow_nonzero=True)
    if not out.exists():
        raise RuntimeError(f'lighting census pass {pass_no} emitted no JSON')
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
    initial_snapshot_count = len(snapshots(a.package_dir))
    if not initial_snapshot_count:
        raise SystemExit('package-dir has no Activity/root packages; close Activity roots first')

    passes = []
    recovered_ids: set[str] = set()
    final = None
    final_path = None
    stop_reason = None

    for i in range(a.max_passes):
        d, p, rc = run_census(a, i)
        final, final_path = d, p
        missing = sorted(str(x).lower().zfill(4) for x in d.get('missing_dependency_package_ids', {}))
        new = sorted(set(missing) - recovered_ids)
        row = {
            'pass': i,
            'snapshot_count': len(snapshots(a.package_dir)),
            'census_returncode': rc,
            'census_status': d.get('status'),
            'light_resource_occurrences': d.get('light_resource_occurrences'),
            'sky_resource_occurrences': d.get('sky_resource_occurrences'),
            'light_record_count': d.get('light_record_count'),
            'transform_record_count': d.get('transform_record_count'),
            'sky_record_count': d.get('sky_record_count'),
            'decoded_light_buffer_count': d.get('decoded_light_buffer_count'),
            'decoded_sky_model_resource_count': d.get('decoded_sky_model_resource_count'),
            'sky_entity_model_hash_count': d.get('sky_entity_model_hash_count'),
            'missing_package_ids': missing,
            'new_package_ids': new,
            'violations': d.get('violations', []),
        }
        passes.append(row)
        if d.get('status') == 'D1_WORLD_MAP_LIGHTING_CENSUS_COMPLETE':
            stop_reason = 'closed_light_sky_dependencies_complete'
            break
        if not new:
            stop_reason = 'partial_no_new_dependency_progress'
            break
        recover(a.index, a.package_list, a.package_dir, a.work_dir, new, i)
        recovered_ids.update(new)
    else:
        stop_reason = 'max_passes_reached'

    if final is None or final_path is None:
        raise RuntimeError('lighting census never ran')
    a.out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(final_path, a.out)
    closed = final.get('status') == 'D1_WORLD_MAP_LIGHTING_CENSUS_COMPLETE'
    report = {
        'schema_version': 3,
        'status': 'D1_WORLD_MAP_LIGHTING_DEPENDENCY_CLOSURE_COMPLETE' if closed else 'D1_WORLD_MAP_LIGHTING_DEPENDENCY_CLOSURE_PARTIAL',
        'stop_reason': stop_reason,
        'initial_snapshot_count': initial_snapshot_count,
        'final_snapshot_count': len(snapshots(a.package_dir)),
        'recovered_package_ids': sorted(recovered_ids),
        'passes': passes,
        'final_lighting_summary': {
            k: final.get(k) for k in (
                'status','source_map_data_table_count','source_entry_count','light_resource_occurrences',
                'sky_resource_occurrences','unique_light_collection_count','unique_sky_collection_count',
                'light_record_count','transform_record_count','parallel_collection_count','sky_record_count',
                'light_buffer_hash_count','decoded_light_buffer_count','sky_model_resource_hash_count',
                'decoded_sky_model_resource_count','sky_entity_model_hash_count','sky_entity_models',
                'missing_dependency_package_ids','violations'
            )
        },
        'policy': (
            'Every recovered package family is selected only by a serialized FileHash package id emitted by the source-pinned light/sky parser. '
            'The only short-structure compatibility rule is the exact retail-proven 80CA0CAF 0x60 empty sky collection. '
            'No package filename, visual appearance, or Blender heuristic is used as semantic evidence.'
        ),
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({
        'status': report['status'], 'stop_reason': stop_reason,
        'recovered_package_ids': report['recovered_package_ids'],
        'final_lighting_summary': report['final_lighting_summary'],
    }, indent=2))
    return 0 if closed else 2


if __name__ == '__main__':
    raise SystemExit(main())
