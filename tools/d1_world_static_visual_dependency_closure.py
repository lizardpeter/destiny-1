#!/usr/bin/env python3
"""Close cross-package dependencies for every baked-static cell in a D1 world.

Input is a closed ``d1_world_static_map_resource_chain_census`` plus a package
directory that already contains the Activity/map-root corpus.  This stage derives
all additional physical package families needed by the baked-static structural and
geometry path, entirely from serialized FileHashes:

  SStaticMapData -> D1 StaticMapData
    -> instance-transform FileHash
    -> StaticTable TagHashes
      -> material FileHashes
      -> vertex0 / vertex1 / index reference-file FileHashes
        -> each reference-file entry's backing FileHash

Package families are recovered through the archive-wide Activity/package index, so
there is no TAR header scan and no map-specific package list.  The closure repeats
until every discovered baked cell passes the existing source-derived binary static
validator and every reference-file header has a resolvable backing FileHash.

The emitted validation JSON is intentionally compatible with
``d1_world_static_visual_export.py`` so every discovered baked cell can immediately
be exported without a Tower-specific schema-validation artifact.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import d1_tower_map_schema_validate_v5 as v5
from d1_world_activity_manifest_dependency_plan import filehash_package_id

NULLS = {'00000000', 'FFFFFFFF'}
PKG_RX = re.compile(r'_([0-9A-Fa-f]{4})_[0-9]+\.pkg$', re.IGNORECASE)


def norm(x: object) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def pid_from_hash(h: str) -> str:
    return f'{filehash_package_id(norm(h)):04x}'


def pid_from_name(name: str) -> str | None:
    m = PKG_RX.search(Path(name).name)
    return m.group(1).lower() if m else None


def snapshots(root: Path) -> list[Path]:
    return sorted(p.resolve() for p in root.glob('*.pkg') if p.is_file())


def make_corpus(root: Path, runtime: Path):
    files = snapshots(root)
    if not files:
        raise RuntimeError('package directory contains no .pkg snapshots')
    return v5.v3.base.Corpus(files, runtime.resolve())


def run_recovery(index: Path, package_list: Path, package_dir: Path, ids: set[str], have: set[str], work: Path, pass_no: int) -> list[str]:
    new = sorted({x.lower().zfill(4) for x in ids} - have)
    if not new:
        return []
    report = work / f'package_recovery_{pass_no:02d}.json'
    stdout = work / f'package_recovery_{pass_no:02d}.stdout.txt'
    cmd = [sys.executable, str(HERE / 'd1_recover_indexed_package_families.py'),
           '--index', str(index), '--package-list', str(package_list),
           '--out-dir', str(package_dir), '--report', str(report)]
    for p in new:
        cmd += ['--package-id', p]
    cp = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout.write_text(cp.stdout)
    if cp.returncode:
        raise RuntimeError(f'indexed package recovery failed rc={cp.returncode}; see {stdout}')
    d = json.loads(report.read_text())
    if d.get('status') != 'D1_INDEXED_PACKAGE_FAMILY_RECOVERY_COMPLETE':
        raise RuntimeError('indexed package recovery did not complete')
    have.update(new)
    return new


def baked_pairs(chain: dict) -> list[dict]:
    by_pair: dict[tuple[str, str], dict] = {}
    for table in chain.get('tables', []):
        for row in table.get('entries', []):
            if not row.get('chain_closed') or row.get('static_map_kind') != 'direct_d1_baked_static':
                continue
            sm = norm((row.get('static_map') or {}).get('hash'))
            d1 = norm((row.get('d1_static_map_data') or {}).get('hash'))
            if sm in NULLS or d1 in NULLS:
                continue
            key = (sm, d1)
            rec = by_pair.setdefault(key, {'static_map_data': sm, 'd1_static_map_data': d1, 'owners': []})
            rec['owners'].append({'map_data_table': row.get('map_data_table'), 'index': row.get('index')})
    return [by_pair[k] for k in sorted(by_pair)]


def collect_from_validation(vr: dict, required: set[str], buffer_headers: set[str], material_hashes: set[str]) -> dict:
    found = {'instance_transform': None, 'static_tables': [], 'materials': [], 'buffer_headers': []}
    th = norm(vr.get('instance_transforms')) if vr.get('instance_transforms') else None
    if th and th not in NULLS:
        required.add(pid_from_hash(th)); found['instance_transform'] = th
    for thash in vr.get('static_table_hashes', []) or []:
        h = norm(thash)
        if h not in NULLS:
            required.add(pid_from_hash(h)); found['static_tables'].append(h)
    for table in vr.get('static_tables', []) or []:
        for mh in table.get('material_hashes', []) or []:
            h = norm(mh)
            if h not in NULLS:
                required.add(pid_from_hash(h)); material_hashes.add(h); found['materials'].append(h)
        for mesh in table.get('mesh_entries', []) or []:
            for field in ('vertices0', 'vertices1', 'indices'):
                h = norm(mesh.get(field))
                if h in NULLS:
                    continue
                required.add(pid_from_hash(h)); buffer_headers.add(h); found['buffer_headers'].append(h)
    for k in ('static_tables', 'materials', 'buffer_headers'):
        found[k] = sorted(set(found[k]))
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--index', type=Path, required=True)
    ap.add_argument('--package-list', type=Path, required=True)
    ap.add_argument('--chain-json', type=Path, required=True)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--package-dir', type=Path, required=True)
    ap.add_argument('--work-dir', type=Path, required=True)
    ap.add_argument('--validation-out', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    ap.add_argument('--max-passes', type=int, default=10)
    a = ap.parse_args()

    chain = json.loads(a.chain_json.read_text())
    if chain.get('status') != 'D1_WORLD_STATIC_MAP_RESOURCE_CHAIN_CLOSED':
        raise SystemExit('static-map resource chain is not closed')
    pairs = baked_pairs(chain)
    if not pairs:
        raise SystemExit('closed chain contains no direct D1 baked-static cells')

    a.package_dir.mkdir(parents=True, exist_ok=True)
    a.work_dir.mkdir(parents=True, exist_ok=True)
    have = {p for p in (pid_from_name(x.name) for x in snapshots(a.package_dir)) if p}
    required = set(have)
    for x in pairs:
        required.add(pid_from_hash(x['static_map_data']))
        required.add(pid_from_hash(x['d1_static_map_data']))

    recovery_no = 0
    initially_added = run_recovery(a.index, a.package_list, a.package_dir, required, have, a.work_dir, recovery_no)
    recovery_no += int(bool(initially_added))
    passes = []
    buffer_headers: set[str] = set()
    material_hashes: set[str] = set()
    final_validations: dict[str, dict] = {}
    stop_reason = None

    for pass_no in range(a.max_passes):
        c = make_corpus(a.package_dir, a.runtime)
        before_required = set(required)
        cell_rows = []
        validations = {}
        for pair in pairs:
            d1 = pair['d1_static_map_data']
            vr = v5.v3.base.validate_static_data_d1(c, d1)
            validations[d1] = vr
            deps = collect_from_validation(vr, required, buffer_headers, material_hashes)
            cell_rows.append({'static_map_data': pair['static_map_data'], 'd1_static_map_data': d1,
                              'validation_ok': bool(vr.get('ok')), 'violations': vr.get('violations', []),
                              'dependencies': deps})

        new_before_backings = run_recovery(a.index, a.package_list, a.package_dir, required, have, a.work_dir, recovery_no)
        recovery_no += int(bool(new_before_backings))
        if new_before_backings:
            c = make_corpus(a.package_dir, a.runtime)
            # Re-validate after table/material/header packages arrive so mesh rows are complete.
            validations = {}
            buffer_headers.clear(); material_hashes.clear()
            for pair in pairs:
                vr = v5.v3.base.validate_static_data_d1(c, pair['d1_static_map_data'])
                validations[pair['d1_static_map_data']] = vr
                collect_from_validation(vr, required, buffer_headers, material_hashes)

        # Reference-file headers encode their exact backing FileHash as the file-entry Reference.
        backing_edges = []
        unresolved_headers = []
        for hh in sorted(buffer_headers):
            meta = c.entry_meta(hh)
            row = {'header': hh, 'header_package_id': pid_from_hash(hh), 'meta': meta,
                   'backing': None, 'backing_package_id': None}
            if meta is None:
                unresolved_headers.append(hh)
            else:
                backing = norm(meta.get('reference'))
                row['backing'] = backing
                if backing in NULLS:
                    row['error'] = 'null_backing_reference'
                    unresolved_headers.append(hh)
                else:
                    row['backing_package_id'] = pid_from_hash(backing)
                    required.add(row['backing_package_id'])
            backing_edges.append(row)

        new_backings = run_recovery(a.index, a.package_list, a.package_dir, required, have, a.work_dir, recovery_no)
        recovery_no += int(bool(new_backings))
        if new_backings:
            c = make_corpus(a.package_dir, a.runtime)

        final_validations = {pair['d1_static_map_data']: v5.v3.base.validate_static_data_d1(c, pair['d1_static_map_data']) for pair in pairs}
        all_valid = all(v.get('ok') for v in final_validations.values())
        backing_payload_missing = []
        for edge in backing_edges:
            bh = edge.get('backing')
            if not bh or bh in NULLS:
                continue
            b, src = c.payload(bh)
            edge['backing_payload_source'] = src
            edge['backing_payload_bytes'] = None if b is None else len(b)
            if b is None:
                backing_payload_missing.append(bh)

        row = {
            'pass': pass_no,
            'required_package_ids': sorted(required),
            'new_package_ids_before_backings': new_before_backings,
            'new_package_ids_for_backings': new_backings,
            'buffer_header_count': len(buffer_headers),
            'material_count': len(material_hashes),
            'unresolved_buffer_headers': unresolved_headers,
            'backing_payload_missing': sorted(set(backing_payload_missing)),
            'all_baked_static_validations_ok': all_valid,
            'cell_validation': [{'d1_static_map_data': h, 'ok': bool(v.get('ok')), 'violations': v.get('violations', [])}
                                for h, v in sorted(final_validations.items())],
            'backing_edges': backing_edges,
        }
        passes.append(row)

        if all_valid and not unresolved_headers and not backing_payload_missing:
            stop_reason = 'closed_all_baked_static_geometry_dependencies'
            break
        if not (new_before_backings or new_backings or required - before_required):
            stop_reason = 'partial_no_dependency_progress'
            break
    else:
        stop_reason = 'max_passes_reached'

    c = make_corpus(a.package_dir, a.runtime)
    validation_rows = []
    failures = []
    for pair in pairs:
        sm = pair['static_map_data']
        outer = v5.v3.base.validate_static_map_data(c, sm)
        if not outer.get('ok'):
            failures.append({'static_map_data': sm, 'violations': outer.get('violations', []), 'error': outer.get('error')})
        validation_rows.append(outer)

    closed = not failures and stop_reason == 'closed_all_baked_static_geometry_dependencies'
    validation_doc = {
        'schema_version': 1,
        'evidence_status': 'GENERIC_ACTIVITY_DRIVEN_BAKED_STATIC_DEPENDENCY_CLOSURE',
        'static_map_data': validation_rows,
        'static_map_data_d1': [final_validations[h] for h in sorted(final_validations)],
        'policy': 'Compatibility validation surface generated only after source-driven cross-package baked-static geometry dependency closure. No map-specific package list is used.'
    }
    a.validation_out.parent.mkdir(parents=True, exist_ok=True)
    a.validation_out.write_text(json.dumps(validation_doc, indent=2, default=list) + '\n')

    report = {
        'schema_version': 1,
        'status': 'D1_WORLD_STATIC_VISUAL_DEPENDENCY_CLOSURE_COMPLETE' if closed else 'D1_WORLD_STATIC_VISUAL_DEPENDENCY_CLOSURE_PARTIAL',
        'source_chain': str(a.chain_json),
        'baked_cell_count': len(pairs),
        'baked_cells': pairs,
        'initial_package_ids': sorted({p for p in (pid_from_name(x.name) for x in snapshots(a.package_dir)) if p}),
        'final_package_ids': sorted(have),
        'required_package_ids': sorted(required),
        'buffer_header_count': len(buffer_headers),
        'material_count': len(material_hashes),
        'buffer_headers': sorted(buffer_headers),
        'materials': sorted(material_hashes),
        'stop_reason': stop_reason,
        'validation_failures': failures,
        'passes': passes,
        'validation_out': str(a.validation_out),
        'policy': (
            'All added package IDs come from serialized SStaticMapData/D1StaticMapData/StaticTable material or buffer FileHashes, '
            'or from reference-file backing FileHashes stored in current entry metadata. Physical ranges come from the exact archive-wide index.'
        ),
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in (
        'status','baked_cell_count','final_package_ids','buffer_header_count','material_count','stop_reason','validation_failures'
    )}, indent=2))
    return 0 if closed else 2


if __name__ == '__main__':
    raise SystemExit(main())
