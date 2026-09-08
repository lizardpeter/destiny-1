#!/usr/bin/env python3
"""Close exact package dependencies for selected D1 shader resources.

The shader header FileHash selects one indexed package family.  The recovered
header's FileEntry.Reference then selects the exact native Orbis payload FileHash,
which may live in another family.  This tool follows those serialized edges and
recovers only the required current retail package families.

No shader byte scanning, filename guessing, or destination-specific assumption is
used.  The result is a reusable source corpus for native GCN extraction, Blender
semantic analysis, and the Rust renderer's shader IR work.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import d1_tower_map_schema_validate_v5 as v5
from d1_filehash import package_hex

NULLS = {'00000000', 'FFFFFFFF'}
PKG_RX = re.compile(r'_([0-9A-Fa-f]{4})_[0-9]+\.pkg$', re.IGNORECASE)


def norm(x) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def snapshots(root: Path) -> list[Path]:
    return sorted(p.resolve() for p in root.glob('*.pkg') if p.is_file())


def package_ids_in_dir(root: Path) -> set[str]:
    out = set()
    for p in snapshots(root):
        m = PKG_RX.search(p.name)
        if m:
            out.add(m.group(1).lower())
    return out


def corpus(root: Path, runtime: Path):
    files = snapshots(root)
    if not files:
        raise RuntimeError('package directory contains no snapshots')
    return v5.v3.base.Corpus(files, runtime.resolve())


def recover(index: Path, plist: Path, outdir: Path, ids: set[str], work: Path, label: str) -> dict | None:
    have = package_ids_in_dir(outdir)
    wanted = sorted({str(x).lower().zfill(4) for x in ids} - have)
    if not wanted:
        return None
    rp = work / f'{label}_recovery.json'
    sp = work / f'{label}_recovery.stdout.txt'
    cmd = [sys.executable, str(HERE / 'd1_recover_indexed_package_families.py'),
           '--index', str(index), '--package-list', str(plist),
           '--out-dir', str(outdir), '--report', str(rp)]
    for pid in wanted:
        cmd += ['--package-id', pid]
    cp = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    sp.write_text(cp.stdout)
    if cp.returncode:
        raise RuntimeError(f'{label} package recovery failed rc={cp.returncode}; see {sp}')
    d = json.loads(rp.read_text())
    if d.get('status') != 'D1_INDEXED_PACKAGE_FAMILY_RECOVERY_COMPLETE':
        raise RuntimeError(f'{label} package recovery did not close')
    return d


def dig(b: bytes | None) -> dict:
    return {'bytes': None if b is None else len(b),
            'sha256': None if b is None else hashlib.sha256(b).hexdigest()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--index', type=Path, required=True)
    ap.add_argument('--package-list', type=Path, required=True)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--package-dir', type=Path, required=True)
    ap.add_argument('--shader', action='append', required=True)
    ap.add_argument('--work-dir', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    a = ap.parse_args()

    shaders = sorted({norm(x) for x in a.shader})
    a.package_dir.mkdir(parents=True, exist_ok=True)
    a.work_dir.mkdir(parents=True, exist_ok=True)

    header_ids = {package_hex(h).lower() for h in shaders}
    header_rec = recover(a.index, a.package_list, a.package_dir, header_ids, a.work_dir, 'headers')
    c = corpus(a.package_dir, a.runtime)

    rows = []
    violations = []
    native_ids = set()
    for h in shaders:
        meta = c.entry_meta(h)
        hb, hsrc = c.payload(h)
        row = {'shader': h, 'header_package_id': package_hex(h).lower(),
               'header_meta': meta, 'header_source': hsrc,
               'header_payload': dig(hb), 'violations': []}
        if meta is None:
            row['violations'].append('header_meta_unavailable')
            native = 'FFFFFFFF'
        else:
            native = norm(meta.get('reference', 'FFFFFFFF'))
        row['native_payload_hash'] = native
        if hb is None:
            row['violations'].append('header_payload_unavailable')
        if native in NULLS:
            row['violations'].append('native_payload_reference_null')
        else:
            pid = package_hex(native).lower()
            native_ids.add(pid)
            row['native_payload_package_id'] = pid
        rows.append(row)

    native_rec = recover(a.index, a.package_list, a.package_dir, native_ids, a.work_dir, 'native_payloads')
    c = corpus(a.package_dir, a.runtime)
    for row in rows:
        native = row['native_payload_hash']
        if native in NULLS:
            continue
        nmeta = c.entry_meta(native)
        nb, nsrc = c.payload(native)
        row['native_payload_meta'] = nmeta
        row['native_payload_source'] = nsrc
        row['native_payload'] = dig(nb)
        if nmeta is None:
            row['violations'].append('native_payload_meta_unavailable')
        if nb is None:
            row['violations'].append('native_payload_unavailable')
        if row['violations']:
            violations.extend(f"{row['shader']}:{x}" for x in row['violations'])

    final_ids = sorted(package_ids_in_dir(a.package_dir))
    out = {
        'schema_version': 1,
        'status': 'D1_INDEXED_SHADER_DEPENDENCY_CLOSURE_COMPLETE' if not violations else 'D1_INDEXED_SHADER_DEPENDENCY_CLOSURE_PARTIAL',
        'shader_count': len(rows),
        'header_package_ids': sorted(header_ids),
        'native_payload_package_ids': sorted(native_ids),
        'final_package_ids': final_ids,
        'header_recovery_status': None if header_rec is None else header_rec.get('status'),
        'native_recovery_status': None if native_rec is None else native_rec.get('status'),
        'shaders': rows,
        'violations': violations,
        'policy': 'Only package IDs derived from selected shader FileHashes and their exact FileEntry.Reference native-payload FileHashes are recovered through the current archive-wide package index.',
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({
        'status': out['status'],
        'shader_count': out['shader_count'],
        'header_package_ids': out['header_package_ids'],
        'native_payload_package_ids': out['native_payload_package_ids'],
        'final_package_ids': out['final_package_ids'],
        'violations': out['violations'],
    }, indent=2))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
