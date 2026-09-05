#!/usr/bin/env python3
"""Render compact contact sheets for high-frequency D1 world pixel shaders.

Each sheet shows representative visible materials and their exact PS t# resources.
The images are an audit aid for semantic reverse engineering; labels preserve the
shader/register/hash identity and no texture role is guessed here.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def pick_png(tex:dict, root:Path)->Path|None:
    if tex.get('png'):
        p=root/tex['png']
        if p.exists(): return p
    for f in tex.get('faces',[]):
        if f.get('png'):
            p=root/f['png']
            if p.exists(): return p
    return None


def fit(im:Image.Image,w:int,h:int)->Image.Image:
    im=im.convert('RGBA')
    im.thumbnail((w,h),Image.Resampling.LANCZOS)
    canvas=Image.new('RGBA',(w,h),(32,32,32,255))
    canvas.alpha_composite(im,((w-im.width)//2,(h-im.height)//2))
    return canvas.convert('RGB')


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('manifest',type=Path)
    ap.add_argument('--texture-dir',type=Path,required=True)
    ap.add_argument('--out-dir',type=Path,required=True)
    ap.add_argument('--top-shaders',type=int,default=30)
    ap.add_argument('--materials-per-shader',type=int,default=4)
    ap.add_argument('--thumb',type=int,default=160)
    a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    d=json.loads(a.manifest.read_text());tex=d['textures']
    byshader=defaultdict(list)
    for mh,m in d['materials'].items():
        if 'pixel_shader' in m: byshader[m['pixel_shader']].append((mh,m))
    ordered=sorted(byshader.items(),key=lambda kv:(-len(kv[1]),kv[0]))[:a.top_shaders]
    font=ImageFont.load_default();index=[]
    for ps,mats in ordered:
        mats=sorted(mats)[:a.materials_per_shader]
        maxslots=max(1,max(sum(1 for b in m.get('bindings',[]) if b.get('stage')=='ps') for _,m in mats))
        cellw=a.thumb+20;cellh=a.thumb+58
        left=180;top=42
        W=left+maxslots*cellw+10;H=top+len(mats)*cellh+10
        sh=Image.new('RGB',(W,H),(20,20,20));dr=ImageDraw.Draw(sh)
        dr.text((10,10),f'PS {ps}   visible materials={len(byshader[ps])}',fill='white',font=font)
        sample=[]
        for ri,(mh,m) in enumerate(mats):
            y=top+ri*cellh;dr.text((10,y+8),mh,fill='white',font=font)
            bindings=sorted((b for b in m.get('bindings',[]) if b.get('stage')=='ps'),key=lambda b:int(b['texture_index']))
            srow=[]
            for ci,b in enumerate(bindings):
                x=left+ci*cellw;t=tex.get(b['texture'],{});p=pick_png(t,a.texture_dir)
                if p:
                    try: tile=fit(Image.open(p),a.thumb,a.thumb)
                    except Exception: tile=Image.new('RGB',(a.thumb,a.thumb),(96,0,0))
                else: tile=Image.new('RGB',(a.thumb,a.thumb),(96,0,0))
                sh.paste(tile,(x,y))
                hi=t.get('header_info') or {};fmt=t.get('format_name') or '?'
                label=f"t{b['texture_index']} {b['texture']}\n{hi.get('width','?')}x{hi.get('height','?')} {fmt} a{hi.get('array_size','?')}"
                dr.multiline_text((x,y+a.thumb+3),label,fill='white',font=font,spacing=1)
                srow.append({'texture_index':int(b['texture_index']),'texture':b['texture'],'format':fmt,'width':hi.get('width'),'height':hi.get('height'),'array_size':hi.get('array_size'),'png':str(p) if p else None})
            sample.append({'material':mh,'bindings':srow})
        out=a.out_dir/f'PS_{ps}.png';sh.save(out,optimize=True)
        index.append({'pixel_shader':ps,'visible_material_count':len(byshader[ps]),'sheet':out.name,'samples':sample})
        print('SHEET',ps,len(byshader[ps]),out,flush=True)
    (a.out_dir/'index.json').write_text(json.dumps({'status':'D1_SHADER_TEXTURE_CONTACT_SHEETS_EXACT_BINDINGS','sheets':index},indent=2)+'\n')
    return 0

if __name__=='__main__': raise SystemExit(main())
