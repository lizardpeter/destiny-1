#!/usr/bin/env python3
"""Close all package dependencies needed for one D1 Activity map-root graph.

Input is an Activity TagHash from the archive-wide ``d1_remote_activity_index``.
The closure is source-driven:

1. recover the Activity's exact physical package family from the global index;
2. decode SActivity_ROI and read its serialized ChildMapReference Bubble TagHashes;
3. recover package families encoded by those Bubble TagHashes;
4. derive shared-manifest package dependencies from ordinary file-entry References;
5. run the source-typed Activity -> Bubble -> MapContainer -> MapDataTable census;
6. whenever a newly visible typed Tag or manifest-parent FileHash belongs to an
   unrecovered package, recover that exact family from the global index;
7. repeat until the ownership census closes or no dependency progress is possible.

No destination/package filename is a semantic input. Package IDs arise only from the
selected named Activity owner, serialized typed Tag hashes, or manifest-parent FileHashes.
The global index is trusted for physical offsets only when its exact packages.txt SHA-256
matches the current package list.
"""
from __future__ import annotations

import argparse
import json
import shutil
import struct
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import d1_tower_map_schema_validate_v5 as v5
import d1_world_map_data_layer_census as layer
from d1_world_activity_manifest_dependency_plan import filehash_package_id

BUBBLE_CLASS = '808091E0'
CONTAINER_CLASS = '80808A54'
TABLE_CLASS = '808009A2'
NULLS = {'00000000', 'FFFFFFFF'}


def norm(x: object) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def pid_hex(tag_hash: str) -> str:
    return f'{filehash_package_id(norm(tag_hash)):04x}'


def snapshots(root: Path) -> list[Path]:
    return sorted(p.resolve() for p in root.glob('*.pkg') if p.is_file())


def corpus(pkg_dir: Path, runtime: Path):
    files = snapshots(pkg_dir)
    if not files:
        raise RuntimeError('no recovered package snapshots')
    return v5.v3.base.Corpus(files, runtime.resolve())


def run_tool(cmd: list[str], stdout_path: Path, *, allow_nonzero: bool = False) -> int:
    cp = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    stdout_path.write_text(cp.stdout)
    if cp.returncode and not allow_nonzero:
        raise RuntimeError(f'command failed rc={cp.returncode}: {cmd}\nsee {stdout_path}')
    return cp.returncode


def activity_row(index: dict, activity: str) -> dict:
    h = norm(activity)
    hits = [x for x in index.get('current_d1_activities', []) if norm(x.get('tag_hash')) == h]
    if len(hits) != 1:
        raise RuntimeError(f'Activity {h} occurs {len(hits)} times in global index')
    return hits[0]


def recover_new(index_path: Path, package_list: Path, ids: set[str], have: set[str],
                pkg_dir: Path, work_dir: Path, pass_no: int) -> list[str]:
    new = sorted({x.lower().zfill(4) for x in ids} - have)
    if not new:
        return []
    report = work_dir / f'recovery_{pass_no:02d}.json'
    stdout = work_dir / f'recovery_{pass_no:02d}.stdout.txt'
    cmd = [sys.executable, str(HERE / 'd1_recover_indexed_package_families.py'),
           '--index', str(index_path), '--package-list', str(package_list),
           '--out-dir', str(pkg_dir), '--report', str(report)]
    for p in new:
        cmd += ['--package-id', p]
    run_tool(cmd, stdout)
    d = json.loads(report.read_text())
    if d.get('status') != 'D1_INDEXED_PACKAGE_FAMILY_RECOVERY_COMPLETE':
        raise RuntimeError(f'indexed family recovery incomplete: {d.get("status")}')
    have.update(new)
    return new


def extract_activity_bubbles(c, activity: str) -> dict:
    h = norm(activity)
    b, src = c.payload(h)
    if b is None or len(b) < 0x28:
        raise RuntimeError(f'{h}: Activity payload unavailable/short')
    arr = layer.dyn(b, 0x10, 0x04)
    if not arr['ok']:
        raise RuntimeError(f'{h}: Activity Bubble DynamicArray bounds failed: {arr}')
    tags = []
    for i in range(arr['count']):
        tag = f'{struct.unpack_from("<I", b, arr["absolute"] + i * 4)[0]:08X}'
        if tag not in NULLS:
            tags.append(tag)
    return {'activity': h, 'payload_source': src, 'payload_bytes': len(b),
            'bubbles_array': arr, 'bubble_tags': list(dict.fromkeys(tags))}


def add_manifest_parent_dependencies(c, typed: dict[str, str], required: set[str], evidence: list[dict]):
    """For known source-typed Tags, derive manifest parent package IDs from entry References."""
    for h, expected_class in sorted(typed.items()):
        if h in NULLS:
            continue
        required.add(pid_hex(h))
        meta = c.entry_meta(h)
        row = {'tag': h, 'expected_class': expected_class, 'tag_package_id': pid_hex(h),
               'meta': meta, 'ordinary_reference': None, 'manifest_parent_package_id': None}
        if meta is not None:
            ref = norm(meta.get('reference', ''))
            row['ordinary_reference'] = ref
            if ref not in NULLS and ref != expected_class:
                try:
                    mpid = pid_hex(ref)
                except ValueError as ex:
                    row['manifest_parent_error'] = str(ex)
                else:
                    required.add(mpid)
                    row['manifest_parent_package_id'] = mpid
        evidence.append(row)


def discover_typed_tags(root: dict, activity_bubbles: list[str]) -> dict[str, str]:
    typed: dict[str, str] = {norm(x): BUBBLE_CLASS for x in activity_bubbles if norm(x) not in NULLS}
    for ar in root.get('activities', []):
        for br in ar.get('bubble_references', []):
            bh = norm(br.get('bubble_definition'))
            if bh not in NULLS:
                typed[bh] = BUBBLE_CLASS
            bv = br.get('bubble_validation') or {}
            for cr in bv.get('map_containers', []):
                ch = norm(cr.get('map_container'))
                if ch not in NULLS:
                    typed[ch] = CONTAINER_CLASS
                cv = cr.get('container_validation') or {}
                for tr in cv.get('map_data_tables', []):
                    th = norm(tr.get('map_data_table'))
                    if th not in NULLS:
                        typed[th] = TABLE_CLASS
    return typed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--index', type=Path, required=True)
    ap.add_argument('--package-list', type=Path, required=True)
    ap.add_argument('--activity', required=True)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--package-dir', type=Path, required=True)
    ap.add_argument('--work-dir', type=Path, required=True)
    ap.add_argument('--root-out', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    ap.add_argument('--max-passes', type=int, default=10)
    a = ap.parse_args()

    index = json.loads(a.index.read_text())
    if index.get('status') != 'D1_REMOTE_ACTIVITY_INDEX_COMPLETE':
        raise SystemExit('global Activity index is not complete')
    ar = activity_row(index, a.activity)
    activity = norm(ar['tag_hash'])
    owner_pid = str(ar['source_package_id']).lower().zfill(4)

    a.package_dir.mkdir(parents=True, exist_ok=True)
    a.work_dir.mkdir(parents=True, exist_ok=True)
    have: set[str] = set()
    required: set[str] = {owner_pid}
    recovery_pass = 0
    recovered = recover_new(a.index, a.package_list, required, have, a.package_dir, a.work_dir, recovery_pass)
    recovery_pass += 1

    c = corpus(a.package_dir, a.runtime)
    activity_payload = extract_activity_bubbles(c, activity)
    bubble_tags = activity_payload['bubble_tags']
    required.update(pid_hex(x) for x in bubble_tags)
    newly = recover_new(a.index, a.package_list, required, have, a.package_dir, a.work_dir, recovery_pass)
    recovery_pass += 1

    # With the Bubble file entries present, derive any D1 shared-manifest families
    # needed to resolve their source-typed class identity.
    manifest_json = a.work_dir / 'activity_manifest_dependency_plan.json'
    files = snapshots(a.package_dir)
    cmd = [sys.executable, str(HERE / 'd1_world_activity_manifest_dependency_plan.py')]
    for p in files:
        cmd += ['--snapshot', str(p)]
    cmd += ['--runtime', str(a.runtime), '--activity', activity,
            '--out', str(manifest_json), '--package-id-list', str(a.work_dir / 'manifest_package_ids.txt')]
    run_tool(cmd, a.work_dir / 'activity_manifest_dependency_plan.stdout.txt')
    manifest = json.loads(manifest_json.read_text())
    if manifest.get('status') != 'D1_WORLD_ACTIVITY_MANIFEST_DEPENDENCY_PLAN_COMPLETE':
        raise SystemExit('Activity manifest dependency plan did not close: ' + json.dumps(manifest.get('violations')))
    required.update(str(x).lower().zfill(4) for x in manifest.get('manifest_package_ids', []))
    recover_new(a.index, a.package_list, required, have, a.package_dir, a.work_dir, recovery_pass)
    recovery_pass += 1

    passes = []
    typed: dict[str, str] = {norm(x): BUBBLE_CLASS for x in bubble_tags}
    final_root = None
    stop_reason = None
    for i in range(a.max_passes):
        c = corpus(a.package_dir, a.runtime)
        manifest_evidence: list[dict] = []
        before_required = set(required)
        add_manifest_parent_dependencies(c, typed, required, manifest_evidence)
        added_by_meta = sorted(required - before_required)
        added_recovery = recover_new(a.index, a.package_list, required, have, a.package_dir, a.work_dir, recovery_pass)
        if added_recovery:
            recovery_pass += 1
            c = corpus(a.package_dir, a.runtime)

        root_json = a.work_dir / f'activity_map_roots_pass_{i:02d}.json'
        cmd = [sys.executable, str(HERE / 'd1_world_activity_map_root_census.py')]
        for p in snapshots(a.package_dir):
            cmd += ['--snapshot', str(p)]
        cmd += ['--runtime', str(a.runtime), '--activity', activity, '--out', str(root_json)]
        rc = run_tool(cmd, a.work_dir / f'activity_map_roots_pass_{i:02d}.stdout.txt', allow_nonzero=True)
        if not root_json.exists():
            raise RuntimeError(f'Activity root census emitted no JSON on pass {i}')
        root = json.loads(root_json.read_text())
        final_root = root
        before_typed = set(typed)
        typed.update(discover_typed_tags(root, bubble_tags))
        new_typed = sorted(set(typed) - before_typed)
        newly_required = set()
        for h in new_typed:
            newly_required.add(pid_hex(h))
        required.update(newly_required)
        newly_recovered = recover_new(a.index, a.package_list, required, have, a.package_dir, a.work_dir, recovery_pass)
        if newly_recovered:
            recovery_pass += 1
        row = {
            'pass': i,
            'root_census_returncode': rc,
            'root_status': root.get('status'),
            'violations': root.get('violations', []),
            'typed_tag_count': len(typed),
            'new_typed_tags': new_typed,
            'manifest_dependency_evidence': manifest_evidence,
            'package_ids_added_from_typed_meta': added_by_meta,
            'package_ids_recovered_before_census': added_recovery,
            'package_ids_recovered_after_census': newly_recovered,
            'reachable_bubbles': root.get('reachable_bubble_count'),
            'reachable_containers': root.get('reachable_map_container_count'),
            'reachable_tables': root.get('reachable_map_data_table_count'),
            'total_map_entries': root.get('total_reachable_map_entries'),
        }
        passes.append(row)
        if root.get('status') == 'D1_WORLD_ACTIVITY_MAP_ROOT_CENSUS_COMPLETE' and root.get('selected_activities') == [activity]:
            stop_reason = 'closed_activity_map_root_census_complete'
            break
        if not (new_typed or added_by_meta or added_recovery or newly_recovered):
            stop_reason = 'partial_no_new_dependency_progress'
            break
    else:
        stop_reason = 'max_passes_reached'

    if final_root is None:
        raise RuntimeError('Activity root census never ran')
    closed = final_root.get('status') == 'D1_WORLD_ACTIVITY_MAP_ROOT_CENSUS_COMPLETE' and final_root.get('selected_activities') == [activity]
    a.root_out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(a.work_dir / f'activity_map_roots_pass_{passes[-1]["pass"]:02d}.json', a.root_out)

    report = {
        'schema_version': 1,
        'status': 'D1_WORLD_ACTIVITY_ROOT_DEPENDENCY_CLOSURE_COMPLETE' if closed else 'D1_WORLD_ACTIVITY_ROOT_DEPENDENCY_CLOSURE_PARTIAL',
        'activity': activity,
        'activity_name': ar.get('name'),
        'activity_aliases': ar.get('aliases'),
        'activity_owner_package_id': owner_pid,
        'activity_payload': activity_payload,
        'manifest_dependency_plan': manifest,
        'stop_reason': stop_reason,
        'recovered_package_ids': sorted(have),
        'recovered_package_family_count': len(have),
        'typed_tags': [{'tag': h, 'expected_class': typed[h], 'package_id': pid_hex(h)} for h in sorted(typed)],
        'passes': passes,
        'final_root_summary': {
            k: final_root.get(k) for k in (
                'status','selected_activities','reachable_bubble_count','bubble_definitions',
                'reachable_map_container_count','map_containers','reachable_map_data_table_count',
                'map_data_tables','map_data_table_entry_counts','total_reachable_map_entries','violations'
            )
        },
        'policy': (
            'The selected Activity is source-typed by the global current named-tag index. All physical package additions are derived from '
            'the Activity owner, serialized Bubble/MapContainer/MapDataTable TagHashes, or ordinary manifest-parent FileHash References. '
            'No destination/package filename or appearance semantic is used for world ownership.'
        ),
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({
        'status': report['status'],
        'activity': activity,
        'stop_reason': stop_reason,
        'recovered_package_ids': report['recovered_package_ids'],
        'final_root_summary': report['final_root_summary'],
    }, indent=2))
    return 0 if closed else 2


if __name__ == '__main__':
    raise SystemExit(main())
