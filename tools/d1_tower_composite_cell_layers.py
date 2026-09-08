#!/usr/bin/env python3
"""Composite independently rendered Tower cell layers into shared-camera views."""
from __future__ import annotations

import argparse, json
from pathlib import Path
from PIL import Image, ImageDraw

CLASS_ORDER = {'far_background': 0, 'outer': 1, 'core': 2}
VARIANTS = (
    ('core_only', {'core'}),
    ('core_outer', {'core', 'outer'}),
    ('all10', {'core', 'outer', 'far_background'}),
)


def cli():
    ap = argparse.ArgumentParser()
    ap.add_argument('--layer-dir', type=Path, required=True)
    ap.add_argument('--out-dir', type=Path, required=True)
    ap.add_argument('--view', action='append', required=True)
    ap.add_argument('--report', type=Path, required=True)
    return ap.parse_args()


def composite(reps, out, include):
    chosen = [x for x in reps if str(x[2].get('layer_class', 'core')) in include]
    if not chosen:
        raise SystemExit(f'no layers selected for {out.name}')
    chosen.sort(key=lambda x: (x[0], -x[1]))
    first = Image.open(chosen[0][3]).convert('RGBA')
    size = first.size
    canvas = Image.new('RGBA', size, (18, 24, 34, 255))
    for _, _, d, png in chosen:
        im = Image.open(png).convert('RGBA')
        if im.size != size:
            raise SystemExit(f'{png}: size mismatch {im.size} != {size}')
        canvas.alpha_composite(im)
    canvas.convert('RGB').save(out, quality=95)
    return {
        'file': out.name,
        'bytes': out.stat().st_size,
        'size': list(size),
        'cells': [int(d['cell']) for _, _, d, _ in chosen],
        'layer_classes': [str(d.get('layer_class', 'core')) for _, _, d, _ in chosen],
    }


def main():
    a = cli()
    a.out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for view in a.view:
        reps = []
        for rp in sorted(a.layer_dir.glob(f'cell??_{view}.json')):
            d = json.load(open(rp))
            if d.get('status') != 'D1_TOWER_SHARED_LAYER_RENDER_COMPLETE':
                raise SystemExit(f'bad layer report: {rp}')
            png = a.layer_dir / d['output']
            if not png.is_file() or png.stat().st_size < 4000:
                raise SystemExit(f'missing layer PNG: {png}')
            cls = str(d.get('layer_class', 'core'))
            reps.append((CLASS_ORDER.get(cls, 2), float(d.get('sort_depth') or 0.0), d, png))
        if len(reps) != 10:
            raise SystemExit(f'{view}: expected 10 layers, got {len(reps)}')

        variants = []
        for variant, include in VARIANTS:
            prefix = {'core_only':'CORE_ONLY','core_outer':'CORE_OUTER','all10':'ALL10'}[variant]
            out = a.out_dir / f'D1_TOWER_{prefix}_{view}.png'
            row = composite(reps, out, include)
            row['variant'] = variant
            variants.append(row)
        rows.append({'view': view, 'variants': variants})

    flat = [(r['view'], v) for r in rows for v in r['variants']]
    tw, th = 640, 360
    sheet = Image.new('RGB', (tw, th * len(flat)), (15, 18, 25))
    draw = ImageDraw.Draw(sheet)
    for i, (view, v) in enumerate(flat):
        im = Image.open(a.out_dir / v['file']).convert('RGB')
        thumb = im.copy(); thumb.thumbnail((tw, th))
        x = (tw - thumb.width)//2; y = i*th + (th-thumb.height)//2
        sheet.paste(thumb, (x, y))
        draw.rectangle((8, i*th+8, 340, i*th+36), fill=(0,0,0))
        draw.text((16, i*th+14), f"{view} / {v['variant']}", fill=(255,255,255))
    contact = a.out_dir / 'D1_TOWER_LAYER_COMPARISON_CONTACT_SHEET.jpg'
    sheet.save(contact, quality=92, optimize=True)

    rep = {
        'status': 'D1_TOWER_LAYER_COMPARISON_COMPOSITES',
        'views': rows,
        'contact_sheet': {'file': contact.name, 'bytes': contact.stat().st_size},
        'policy': 'Diagnostic alpha composites from ten independently rendered Blender-space cell layers. Core-only, core+outer, and all-ten variants expose the contribution of cell07 outer and cell08 far-background separately. Inter-cell per-pixel depth remains approximate; this is not a retail framebuffer claim.'
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(rep, indent=2) + '\n')
    print(json.dumps(rep, indent=2))


if __name__ == '__main__':
    main()
