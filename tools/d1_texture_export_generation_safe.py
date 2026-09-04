#!/usr/bin/env python3
"""Generation-safe wrapper around d1_texture_export.

Destiny 1 logical package file-index slots can be repurposed between physical
patch snapshots.  A TagHash that is valid in one snapshot may therefore point at
an unrelated or undecodable backing chain in a newer table.  This wrapper tries
caller-supplied snapshots newest-to-oldest for each requested texture and accepts
only an export that produces exactly one PNG with no decoder error.

The chosen snapshot is recorded per texture.  No cross-package dependency trick
is used for same-family *_N siblings; each candidate snapshot is opened as the
primary logical package while its sibling files remain beside it for block patch
resolution.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from d1_entry_extract import EntryReader
from d1_texture_export import export_reader


def norm_hash(value: str) -> str:
    value = value.strip().upper().removeprefix('0X')
    if len(value) != 8:
        raise argparse.ArgumentTypeError(f'expected 8 hex digits, got {value!r}')
    int(value, 16)
    return value


def copy_outputs(attempt_dir: Path, outdir: Path, row: dict) -> dict:
    copied = []
    for key in ('dds', 'png'):
        name = row.get(key)
        if name:
            src = attempt_dir / name
            if not src.is_file():
                raise FileNotFoundError(src)
            dst = outdir / src.name
            shutil.copy2(src, dst)
            copied.append(dst.name)
    for key in ('face_dds', 'face_pngs'):
        for name in row.get(key) or []:
            src = attempt_dir / name
            if not src.is_file():
                raise FileNotFoundError(src)
            dst = outdir / src.name
            shutil.copy2(src, dst)
            copied.append(dst.name)
    return {'copied_files': copied}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', type=Path, action='append', required=True,
                    help='candidate logical snapshots in newest-to-oldest order')
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--tag-hash', type=norm_hash, action='append', required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    attempts_root = args.out / '.attempts'
    attempts_root.mkdir(parents=True, exist_ok=True)

    readers = []
    for p in args.snapshot:
        readers.append((p, EntryReader(p, args.runtime)))

    resolved = []
    failures = []
    for tag in args.tag_hash:
        tag_attempts = []
        accepted = None
        for snap_path, reader in readers:
            adir = attempts_root / tag / snap_path.stem
            if adir.exists():
                shutil.rmtree(adir)
            adir.mkdir(parents=True, exist_ok=True)
            rec = {'snapshot': str(snap_path)}
            try:
                report = export_reader(reader, adir, tag_hashes=[tag], dependencies=[])
                rec['missing_requested'] = report.get('missing_requested')
                rec['texture_count'] = report.get('texture_count')
                if report.get('missing_requested'):
                    rec['reject'] = 'tag missing from this snapshot'
                    tag_attempts.append(rec)
                    continue
                if report.get('texture_count') != 1 or len(report.get('textures', [])) != 1:
                    rec['reject'] = 'did not produce exactly one texture row'
                    tag_attempts.append(rec)
                    continue
                row = report['textures'][0]
                rec['row'] = row
                png = row.get('png')
                if not png or row.get('png_error'):
                    rec['reject'] = f"PNG export failed: {row.get('png_error')!r}"
                    tag_attempts.append(rec)
                    continue
                if not (adir / png).is_file():
                    rec['reject'] = 'manifest PNG does not exist'
                    tag_attempts.append(rec)
                    continue
                copied = copy_outputs(adir, args.out, row)
                rec.update(copied)
                rec['accepted'] = True
                tag_attempts.append(rec)
                accepted = {
                    'tag_hash': tag,
                    'chosen_snapshot': str(snap_path),
                    'texture': row,
                    **copied,
                    'attempts': tag_attempts,
                }
                break
            except Exception as exc:
                rec['error'] = repr(exc)
                tag_attempts.append(rec)
        if accepted is None:
            failures.append({'tag_hash': tag, 'attempts': tag_attempts})
        else:
            resolved.append(accepted)
            print('GENSAFE_TEXTURE', tag, '->', accepted['chosen_snapshot'], accepted['texture'].get('png'))

    manifest = {
        'mode': 'generation-safe per-TagHash snapshot fallback',
        'snapshots_newest_to_oldest': [str(p) for p in args.snapshot],
        'requested_count': len(args.tag_hash),
        'resolved_count': len(resolved),
        'failed_count': len(failures),
        'textures': resolved,
        'failures': failures,
        'missing_requested': [x['tag_hash'] for x in failures],
    }
    (args.out / 'texture_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    if failures:
        raise SystemExit(f"failed to export {len(failures)} texture(s): {[x['tag_hash'] for x in failures]}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
