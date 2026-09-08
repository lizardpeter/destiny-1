#!/usr/bin/env python3
"""Composite independently rendered Tower cell layers into shared-camera views."""
from __future__ import annotations

import argparse, json
from pathlib import Path
from PIL import Image, ImageDraw

CLASS_ORDER = {'far_background': 0, 'outer': 1, 'core': 2}


def cli():
    ap = argparse.ArgumentParser()
    ap.add_argument('--layer-dir', type=Path, required=True)
    ap.add_argument('--out-dir', type=Path, required=True)
    ap.add_argument('--view', action='append', required=True)
    ap.add_argument('--report', type=Path, required=True)
    return ap.parse_args()


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

        # The far-background cell is deliberately drawn before the outer layer,
        # and both are drawn before the compact Tower core.  Within each class,
        # use camera depth far-to-near.  This avoids letting cell08's enormous
        # scenery scale overwrite local geometry merely because its centroid is
        # not a useful proxy for every pixel in that cell.
        reps.sort(key=lambda x: (x[0], -x[1]))
        first = Image.open(reps[0][3]).convert('RGBA')
        size = first.size
        canvas = Image.new('RGBA', size, (18, 24, 34, 255))
        for _, _, d, png in reps:
            im = Image.open(png).convert('RGBA')
            if im.size != size:
                raise SystemExit(f'{png}: size mismatch {im.size} != {size}')
            canvas.alpha_composite(im)
        out = a.out_dir / f'D1_TOWER_ALL10_{view}.png'
        canvas.convert('RGB').save(out, quality=95)
        rows.append({
            'view': view,
            'file': out.name,
            'bytes': out.stat().st_size,
            'size': list(size),
            'cell_order_far_background_to_core': [int(d['cell']) for _, _, d, _ in reps],
            'layer_classes': [str(d.get('layer_class', 'core')) for _, _, d, _ in reps],
        })

    ims = [Image.open(a.out_dir / r['file']).convert('RGB') for r in rows]
    tw, th = 640, 360
    sheet = Image.new('RGB', (tw, th * len(ims)), (15, 18, 25))
    draw = ImageDraw.Draw(sheet)
    for i, (im, r) in enumerate(zip(ims, rows)):
        thumb = im.copy(); thumb.thumbnail((tw, th))
        x = (tw - thumb.width)//2; y = i*th + (th-thumb.height)//2
        sheet.paste(thumb, (x, y))
        draw.rectangle((8, i*th+8, 280, i*th+36), fill=(0,0,0))
        draw.text((16, i*th+14), r['view'], fill=(255,255,255))
    contact = a.out_dir / 'D1_TOWER_ALL10_CONTACT_SHEET.jpg'
    sheet.save(contact, quality=92, optimize=True)

    rep = {
        'status': 'D1_TOWER_ALL10_SHARED_CAMERA_COMPOSITES',
        'views': rows,
        'contact_sheet': {'file': contact.name, 'bytes': contact.stat().st_size},
        'policy': 'Diagnostic alpha composite of ten independently rendered Blender-space cell layers. Cell08 far-background is composited first, then cell07 outer, then core; inter-cell per-pixel depth remains approximate, so this is not a retail framebuffer claim.'
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(rep, indent=2) + '\n')
    print(json.dumps(rep, indent=2))


if __name__ == '__main__':
    main()
