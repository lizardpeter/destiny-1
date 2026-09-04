#!/usr/bin/env python3
"""Compose D1 ROI texture plates from a d1_texture_plate_probe report.

The composition rule is source-confirmed by Charm's D1 path: each source
texture is resized to the transform Scale and copied at transform Translation
onto a square power-of-two plate.  By default this tool refuses to resample;
that keeps proof builds byte-layout driven.  Pass --allow-resize only when a
fixture genuinely requires source resampling and record that as a portable
reconstruction choice.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def find_source_png(texture_dir: Path, tag_hash: str) -> Path:
    matches = sorted(
        p for p in texture_dir.glob(f'{tag_hash}_*.png')
        if '_face' not in p.stem
    )
    if len(matches) != 1:
        raise RuntimeError(f'{tag_hash}: expected one 2D PNG in {texture_dir}, found {[p.name for p in matches]}')
    return matches[0]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--plate-report', type=Path, required=True)
    ap.add_argument('--texture-dir', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--allow-resize', action='store_true')
    args = ap.parse_args()

    rep = json.loads(args.plate_report.read_text())
    args.out.mkdir(parents=True, exist_ok=True)
    out_rows = []

    for semantic, plate in rep['plates'].items():
        dim = int(plate['plate_dimension_pow2'])
        if dim <= 0:
            continue
        canvas = Image.new('RGBA', (dim, dim), (0, 0, 0, 0))
        placements = []
        for tr in plate.get('transforms', []):
            tag = tr['texture']
            src_path = find_source_png(args.texture_dir, tag)
            src = Image.open(src_path).convert('RGBA')
            want = tuple(int(x) for x in tr['scale'])
            resized = False
            if src.size != want:
                if not args.allow_resize:
                    raise RuntimeError(f'{semantic}/{tag}: source size {src.size} != exact placement scale {want}; refusing implicit resample')
                src = src.resize(want, Image.Resampling.LANCZOS)
                resized = True
            xy = tuple(int(x) for x in tr['translation'])
            canvas.alpha_composite(src, dest=xy)
            placements.append({
                'texture': tag,
                'source_png': src_path.name,
                'source_size': list(Image.open(src_path).size),
                'translation': list(xy),
                'scale': list(want),
                'resized': resized,
            })
        out_path = args.out / f"{rep['header']['tag_hash']}_{semantic}_plate.png"
        canvas.save(out_path)
        out_rows.append({
            'semantic': semantic,
            'plate_tag_hash': plate['tag_hash'],
            'dimension': dim,
            'output_png': out_path.name,
            'sha256': sha256_file(out_path),
            'placements': placements,
        })

    manifest = {
        'plate_report': str(args.plate_report),
        'texture_dir': str(args.texture_dir),
        'allow_resize': bool(args.allow_resize),
        'plates': out_rows,
    }
    (args.out / 'texture_plate_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
