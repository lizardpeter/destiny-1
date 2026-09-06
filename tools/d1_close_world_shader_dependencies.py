#!/usr/bin/env python3
"""Recursively close D1 native pixel-shader dependencies for an exact material manifest.

The manifest supplies source-proven D1 pixel-shader FileHashes. This tool recovers only
package families derived from those serialized hashes, runs the exact OrbShdr-bounded
shader extractor, then follows any native-shader FileHashes exposed by the shader header
metadata until extraction closes or no dependency progress is possible.

No package filename semantics, shader-name guessing, or visual classification is used.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from d1_world_activity_manifest_dependency_plan import filehash_package_id


def norm(x: object) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def pid(h: str) -> str:
    return f'{filehash_package_id(norm(h)):04x}'


def snapshots(root: Path) -> list[Path]:
    return sorted(p.resolve() for p in root.glob('*.pkg') if p.is_file())


def run(cmd: list[str], log: Path, allow_nonzero: bool = False) -> int:
    cp = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(cp.stdout)
    if cp.returncode and not allow_nonzero:
        raise RuntimeError(f'command failed rc={cp.returncode}: {cmd}\nsee {log}')
    return cp.returncode


def recover(a, ids: list[str], pass_no: int) -> list[str]:
    ids = sorted(set(x.lower().zfill(4) for x in ids))
    if not ids:
        return []
    rep = a.work_dir / f'recovery_{pass_no:02d}.json'
    cmd = [sys.executable, str(HERE / 'd1_recover_indexed_package_families.py'),
           '--index', str(a.index), '--package-list', str(a.package_list),
           '--out-dir', str(a.package_dir), '--report', str(rep)]
    for x in ids:
        cmd += ['--package-id', x]
    run(cmd, a.work_dir / f'recovery_{pass_no:02d}.stdout.txt')
    d = json.loads(rep.read_text())
    if d.get('status') != 'D1_INDEXED_PACKAGE_FAMILY_RECOVERY_COMPLETE':
        raise RuntimeError(f'indexed recovery incomplete: {d.get("status")}')
    return ids


def extract(a, pass_no: int) -> tuple[dict, int, Path]:
    out_dir = a.work_dir / f'pass_{pass_no:02d}' / 'gcn'
    report = a.work_dir / f'pass_{pass_no:02d}' / 'shader_report.json'
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(HERE / 'd1_world_shader_extract.py')]
    for p in snapshots(a.package_dir):
        cmd += ['--snapshot', str(p)]
    cmd += ['--runtime', str(a.runtime), '--manifest', str(a.manifest),
            '--top', '100000', '--out-dir', str(out_dir), '--report', str(report)]
    rc = run(cmd, a.work_dir / f'pass_{pass_no:02d}' / 'stdout.txt', allow_nonzero=True)
    if not report.exists():
        raise RuntimeError('shader extractor emitted no report')
    return json.loads(report.read_text()), rc, out_dir


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--index', type=Path, required=True)
    ap.add_argument('--package-list', type=Path, required=True)
    ap.add_argument('--manifest', type=Path, required=True)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--package-dir', type=Path, required=True)
    ap.add_argument('--work-dir', type=Path, required=True)
    ap.add_argument('--out-dir', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    ap.add_argument('--max-passes', type=int, default=8)
    a = ap.parse_args()
    a.package_dir.mkdir(parents=True, exist_ok=True)
    a.work_dir.mkdir(parents=True, exist_ok=True)

    manifest = json.loads(a.manifest.read_text())
    freq = {norm(k): int(v) for k, v in manifest.get('pixel_shader_frequency', {}).items()}
    if not freq:
        raise SystemExit('manifest has no pixel_shader_frequency')

    header_ids = sorted(set(pid(h) for h in freq))
    recovered: set[str] = set()
    passes = []
    recover(a, header_ids, -1)
    recovered.update(header_ids)

    final = None
    final_gcn = None
    stop_reason = None
    for i in range(a.max_passes):
        d, rc, gcn = extract(a, i)
        final, final_gcn = d, gcn
        missing_native_ids = set()
        dependency_errors = []
        structural_errors = []
        for row in d.get('shaders', []):
            err = row.get('error')
            if not err:
                continue
            native = norm(row.get('native_shader', 'FFFFFFFF'))
            if err == 'native shader payload unavailable' and native not in {'00000000','FFFFFFFF'}:
                try:
                    missing_native_ids.add(pid(native))
                    dependency_errors.append({'shader': row.get('shader'), 'native_shader': native, 'package_id': pid(native)})
                except Exception:
                    structural_errors.append(row)
            else:
                structural_errors.append(row)
        new = sorted(missing_native_ids - recovered)
        passes.append({
            'pass': i,
            'extract_returncode': rc,
            'status': d.get('status'),
            'selected_count': d.get('selected_count'),
            'error_count': d.get('error_count'),
            'dependency_errors': dependency_errors,
            'structural_errors': structural_errors,
            'new_package_ids': new,
        })
        if d.get('status') == 'D1_WORLD_PIXEL_SHADER_GCN_EXACT' and int(d.get('error_count', 0)) == 0:
            stop_reason = 'all_native_pixel_shaders_closed'
            break
        if structural_errors:
            stop_reason = 'non_dependency_shader_error'
            break
        if not new:
            stop_reason = 'partial_no_new_dependency_progress'
            break
        recover(a, new, i)
        recovered.update(new)
    else:
        stop_reason = 'max_passes_reached'

    if final is None or final_gcn is None:
        raise RuntimeError('shader extraction never ran')
    closed = final.get('status') == 'D1_WORLD_PIXEL_SHADER_GCN_EXACT' and int(final.get('error_count', 0)) == 0
    if a.out_dir.exists():
        shutil.rmtree(a.out_dir)
    a.out_dir.mkdir(parents=True, exist_ok=True)
    for p in final_gcn.glob('*'):
        if p.is_file():
            shutil.copy2(p, a.out_dir / p.name)
    shutil.copy2(a.work_dir / f'pass_{passes[-1]["pass"]:02d}' / 'shader_report.json', a.out_dir / 'shader_report.json')

    rep = {
        'schema_version': 1,
        'status': 'D1_WORLD_PIXEL_SHADER_DEPENDENCY_CLOSURE_COMPLETE' if closed else 'D1_WORLD_PIXEL_SHADER_DEPENDENCY_CLOSURE_PARTIAL',
        'stop_reason': stop_reason,
        'source_pixel_shader_count': len(freq),
        'source_pixel_shader_instance_frequency': freq,
        'initial_header_package_ids': header_ids,
        'recovered_package_ids': sorted(recovered),
        'passes': passes,
        'final_shader_status': final.get('status'),
        'final_selected_count': final.get('selected_count'),
        'final_error_count': final.get('error_count'),
        'final_total_gcn_bytes': sum(int(x.get('gcn_bytes', 0)) for x in final.get('shaders', [])),
        'policy': 'All package recovery is derived only from source material shader FileHashes and native shader references exposed by exact header metadata.',
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(rep, indent=2) + '\n')
    print(json.dumps(rep, indent=2))
    return 0 if closed else 2


if __name__ == '__main__':
    raise SystemExit(main())
