#!/usr/bin/env python3
"""Compose every exact D1 texture-plate header in a remote plate census.

Consumes d1_remote_texture_plate_probe/v1 and source PNGs from the validated D1
texture exporter. Each source image must exactly match its serialized placement
scale by default. No plate placement or role is inferred.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image

ROLES=('albedo','normal','gstack')


def sha256(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()

def find_png(root:Path,tag:str)->Path:
    hits=sorted(p for p in root.glob(f'{tag}_*.png') if '_face' not in p.stem)
    if len(hits)!=1:raise RuntimeError(f'{tag}: expected one source PNG, found {[p.name for p in hits]}')
    return hits[0]


def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--plate-report',type=Path,required=True);ap.add_argument('--texture-dir',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--allow-resize',action='store_true');ap.add_argument('--report',type=Path,required=True)
    a=ap.parse_args();src=json.loads(a.plate_report.read_text());a.out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for h in src.get('headers',[]):
        if h.get('error'):raise RuntimeError(f"{h.get('tag_hash')}: {h['error']}")
        header=h['tag_hash'].upper();plates=h['plates']
        if set(plates)!=set(ROLES):raise RuntimeError(f'{header}: incomplete plate roles {list(plates)}')
        for role in ROLES:
            p=plates[role];dim=int(p['plate_dimension_pow2'])
            if dim<=0:raise RuntimeError(f'{header}/{role}: invalid dimension {dim}')
            canvas=Image.new('RGBA',(dim,dim),(0,0,0,0));placements=[]
            for tr in p.get('transforms',[]):
                tag=tr['texture'].upper();path=find_png(a.texture_dir,tag);im=Image.open(path);im.load();im=im.convert('RGBA')
                want=tuple(int(x) for x in tr['scale']);resized=False
                if im.size!=want:
                    if not a.allow_resize:raise RuntimeError(f'{header}/{role}/{tag}: source size {im.size} != serialized scale {want}')
                    im=im.resize(want,Image.Resampling.LANCZOS);resized=True
                xy=tuple(int(x) for x in tr['translation'])
                if xy[0]<0 or xy[1]<0 or xy[0]+want[0]>dim or xy[1]+want[1]>dim:
                    raise RuntimeError(f'{header}/{role}/{tag}: placement {xy}+{want} outside {dim}x{dim}')
                canvas.alpha_composite(im,dest=xy)
                placements.append({'texture':tag,'source_png':path.name,'source_size':list(Image.open(path).size),'translation':list(xy),'scale':list(want),'resized':resized,'source_sha256':sha256(path)})
            out=a.out/f'{header}_{role}_plate.png';canvas.save(out)
            rows.append({'header_tag':header,'role':role,'plate_tag':p['tag_hash'].upper(),'dimension':dim,'output_png':out.name,'sha256':sha256(out),'placements':placements})
            print('COMPOSED',header,role,p['tag_hash'],dim,len(placements),out)
    rep={'schema':'d1_texture_plate_compose_set/v1','header_count':len(src.get('headers',[])),'plate_image_count':len(rows),'allow_resize':bool(a.allow_resize),'plates':rows,
         'policy':'Every role, source texture, placement and dimension comes from serialized D1 texture-plate records; resampling is forbidden unless explicitly requested.'}
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(rep,indent=2)+'\n')
    if len(rows)!=len(src.get('headers',[]))*3:raise RuntimeError('plate image count does not equal 3 roles per header')
    return 0

if __name__=='__main__':raise SystemExit(main())
