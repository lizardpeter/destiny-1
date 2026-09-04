#!/usr/bin/env python3
"""Compose the six byte-proven Gjallarhorn arrangement-1229 texture plate sets.

The mappings below are copied from retail TexturePlateHeader/TexturePlate records
and are intentionally explicit.  Every source image must already be exported at
exactly the serialized placement size; this tool refuses to resample.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image

PLATES = {
    '80A39C90': {
        'albedo': ('80A39C94', 2048, [('80A3DB32',1536,0,512,1280),('80A3DB33',1536,1280,512,512)]),
        'normal': ('80A39C95', 2048, [('80A3DB34',1536,0,512,1280),('80A3DB35',1536,1280,512,512)]),
        'gstack': ('80A39C96', 2048, [('80A3DB36',1536,0,512,1280),('80A3DB37',1536,1280,512,512)]),
    },
    '80A398B5': {
        'albedo': ('80A398B9', 2048, [('80A3DB41',0,0,1536,1024)]),
        'normal': ('80A398BA', 2048, [('80A3DB42',0,0,1536,1024)]),
        'gstack': ('80A398BB', 2048, [('80A3DB43',0,0,1536,1024)]),
    },
    '80A38D5D': {
        'albedo': ('80A38D61', 2048, [('80A3DB4D',1536,1792,512,256)]),
        'normal': ('80A38D62', 2048, [('80A3DB4E',1536,1792,512,256)]),
        'gstack': ('80A38D63', 2048, [('80A3DB4F',1536,1792,512,256)]),
    },
    '80A39407': {
        'albedo': ('80A3940C', 1024, [('80A3DB61',0,0,1024,1024)]),
        'normal': ('80A3940D', 1024, [('80A3DB62',0,0,1024,1024)]),
        'gstack': ('80A3940E', 1024, [('80A3DB63',0,0,1024,1024)]),
    },
    '80A3947C': {
        'albedo': ('80A3947D', 2048, [('80A3DB73',0,1024,1536,256),('80A3DB74',0,1280,1536,768)]),
        'normal': ('80A3947E', 2048, [('80A3DB75',0,1024,1536,256),('80A3DB76',0,1280,1536,768)]),
        'gstack': ('80A3947F', 2048, [('80A3DB77',0,1024,1536,256),('80A3DB78',0,1280,1536,768)]),
    },
    '80A7E1B4': {
        'albedo': ('80A39975', 512, [('80A3DB53',0,0,512,512)]),
        'normal': ('80A7FA34', 512, [('80A019BE',0,0,512,512)]),
        'gstack': ('80A3D276', 512, [('80A3D8F6',0,0,512,512)]),
    },
}


def source_png(roots: list[Path], tag: str) -> Path:
    hits=[]
    for root in roots:
        hits.extend(root.glob(f'{tag}_*.png'))
    # Texture exporter may also emit cubemap faces; none are valid plate sources here.
    hits=[p for p in hits if '_face' not in p.stem]
    uniq=sorted(set(hits))
    if len(uniq)!=1:
        raise RuntimeError(f'{tag}: expected exactly one source PNG, found {[str(x) for x in uniq]}')
    return uniq[0]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--texture-dir',type=Path,action='append',required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--report',type=Path,required=True)
    a=ap.parse_args(); a.out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for header,roles in PLATES.items():
        for role,(plate_tag,dim,placements) in roles.items():
            canvas=Image.new('RGBA',(dim,dim),(0,0,0,0)); src_rows=[]
            for tag,x,y,w,h in placements:
                p=source_png(a.texture_dir,tag)
                im=Image.open(p); im.load(); im=im.convert('RGBA')
                if im.size!=(w,h):
                    raise RuntimeError(f'{header}/{role}/{tag}: source {im.size} != serialized placement {(w,h)}; refusing resample')
                if x<0 or y<0 or x+w>dim or y+h>dim:
                    raise RuntimeError(f'{header}/{role}/{tag}: placement outside {dim}x{dim}')
                canvas.paste(im,(x,y))
                src_rows.append({'texture':tag,'source':str(p),'source_size':[w,h],'translation':[x,y],'scale':[w,h],'sha256':sha256(p)})
            out=a.out/f'{header}_{role}_plate.png';canvas.save(out)
            rows.append({'header_tag':header,'role':role,'plate_tag':plate_tag,'dimension':dim,'sources':src_rows,'output':str(out),'sha256':sha256(out)})
            print('COMPOSED',header,role,plate_tag,dim,out)
    report={'arrangement':1229,'plate_header_count':len(PLATES),'plate_image_count':len(rows),'plates':rows,'policy':'no resampling; source PNG dimensions must equal serialized transform scale'}
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,indent=2)+'\n')
    assert len(rows)==18
    return 0

if __name__=='__main__': raise SystemExit(main())
