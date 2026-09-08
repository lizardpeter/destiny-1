#!/usr/bin/env python3
"""Composite independently rendered Tower cell layers into shared-camera views."""
from __future__ import annotations

import argparse, json
from pathlib import Path
from PIL import Image, ImageDraw


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
            reps.append((float(d.get('sort_depth') or 0.0), d, png))
        if len(reps) != 10:
            raise SystemExit(f'{view}: expected 10 layers, got {len(reps)}')
        # Far-to-near whole-cell order.  Cells are spatial map partitions, so
        # this is a practical diagnostic composite, not a replacement for a
        # unified depth buffer.
        reps.sort(key=lambda x: x[0], reverse=True)
        first = Image.open(reps[0][2]).convert('RGBA')
        size = first.size
        canvas = Image.new('RGBA', size, (18, 24, 34, 255))
        for _, d, png in reps:
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
            'cell_order_far_to_near': [int(d['cell']) for _, d, _ in reps],
        })

    # Contact sheet of all completed shared-camera composites.
    ims = [Image.open(a.out_dir / r['file']).convert('RGB') for r in rows]
    tw, th = 640, 360
    sheet = Image.new('RGB', (tw, th * len(ims)), (15, 18, 25))
    draw = ImageDraw.Draw(sheet)
    for i, (im, r) in enumerate(zip(ims, rows)):
        thumb = im.copy(); thumb.thumbnail((tw, th))
        x = (tw - thumb.width)//2; y = i*th + (th-thumb.height)//2
        sheet.paste(thumb, (x, y))
        draw.rectangle((8, i*th+8, 250, i*th+36), fill=(0,0,0))
        draw.text((16, i*th+14), r['view'], fill=(255,255,255))
    contact = a.out_dir / 'D1_TOWER_ALL10_CONTACT_SHEET.jpg'
    sheet.save(contact, quality=92, optimize=True)

    rep = {
        'status': 'D1_TOWER_ALL10_SHARED_CAMERA_COMPOSITES',
        'views': rows,
        'contact_sheet': {'file': contact.name, 'bytes': contact.stat().st_size},
        'policy': 'Diagnostic far-to-near alpha composite of ten independently rendered world-space cell layers. Geometry/materials/transforms are exact inputs; inter-cell depth is approximated at whole-cell ordering, so this is not a retail framebuffer claim.'
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(rep, indent=2) + '\n')
    print(json.dumps(rep, indent=2))


if __name__ == '__main__':
    main()
