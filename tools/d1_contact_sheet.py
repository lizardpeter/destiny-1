#!/usr/bin/env python3
"""Build labeled contact sheets for bulk D1 image/texture inventories."""
from __future__ import annotations

import argparse
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def fit(im: Image.Image, w: int, h: int) -> Image.Image:
    im = im.convert('RGBA')
    im.thumbnail((w, h), Image.Resampling.LANCZOS)
    canvas = Image.new('RGBA', (w, h), (24, 25, 29, 255))
    canvas.alpha_composite(im, ((w-im.width)//2, (h-im.height)//2))
    return canvas


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('input',type=Path)
    ap.add_argument('--glob',default='*.png')
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--thumb-width',type=int,default=192)
    ap.add_argument('--thumb-height',type=int,default=128)
    ap.add_argument('--label-height',type=int,default=34)
    ap.add_argument('--columns',type=int,default=5)
    ap.add_argument('--max-images',type=int,default=500)
    a=ap.parse_args()
    paths=sorted(a.input.rglob(a.glob))[:a.max_images]
    if not paths:
        raise SystemExit(f'no images matching {a.glob!r} below {a.input}')
    cols=max(1,a.columns); rows=math.ceil(len(paths)/cols)
    cell_w=a.thumb_width; cell_h=a.thumb_height+a.label_height
    sheet=Image.new('RGB',(cols*cell_w,rows*cell_h),(18,19,22))
    draw=ImageDraw.Draw(sheet); font=ImageFont.load_default()
    for i,p in enumerate(paths):
        x=(i%cols)*cell_w; y=(i//cols)*cell_h
        try:
            im=Image.open(p); im.load(); tile=fit(im,a.thumb_width,a.thumb_height).convert('RGB')
            sheet.paste(tile,(x,y))
        except Exception as ex:
            draw.rectangle((x,y,x+cell_w-1,y+a.thumb_height-1),fill=(55,30,30))
            draw.text((x+5,y+5),type(ex).__name__,font=font,fill=(255,220,220))
        name=p.stem
        if len(name)>30: name=name[:27]+'...'
        draw.text((x+5,y+a.thumb_height+5),name,font=font,fill=(225,225,230))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    sheet.save(a.out,quality=90)
    print(f'wrote {a.out}: {len(paths)} images, {sheet.width}x{sheet.height}')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
