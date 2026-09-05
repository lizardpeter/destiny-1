#!/usr/bin/env python3
"""Extract exact native PS4 shader code for world-material pixel shaders.

Unlike the single-package historical probe, this tool resolves shader headers and
native payloads through the same cross-package Corpus used by the world exporter.
It consumes a material texture manifest, selects the highest-frequency pixel
shaders (or explicit hashes), validates OrbShdr framing, records resource usage,
and dumps bounded GCN code bytes for disassembly/dataflow analysis.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import d1_tower_map_schema_validate_v5 as v5
from d1_ps4_shader_binary_probe import find_footer, parse_binary_info, parse_usage


def norm(h:str)->str:
    return h.upper().removeprefix('0X').zfill(8)


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--snapshot',type=Path,action='append',required=True)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--manifest',type=Path,required=True)
    ap.add_argument('--shader',action='append',default=[])
    ap.add_argument('--top',type=int,default=40)
    ap.add_argument('--out-dir',type=Path,required=True)
    ap.add_argument('--report',type=Path,required=True)
    a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)

    d=json.loads(a.manifest.read_text())
    freq={norm(k):int(v) for k,v in d.get('pixel_shader_frequency',{}).items()}
    if a.shader:
        selected=[norm(x) for x in a.shader]
    else:
        selected=[k for k,_ in sorted(freq.items(),key=lambda kv:(-kv[1],kv[0]))[:a.top]]
    c=v5.v3.base.Corpus([p.resolve() for p in a.snapshot],a.runtime.resolve())

    rows=[];errors=[]
    for i,sh in enumerate(selected,1):
        meta=c.entry_meta(sh);hb,hsrc=c.payload(sh)
        row={'shader':sh,'visible_material_count':freq.get(sh,0),'header_meta':meta,'header_source':hsrc}
        print(f'SHADER {i}/{len(selected)} {sh}',flush=True)
        if meta is None or hb is None:
            row['error']='shader header unavailable';rows.append(row);errors.append(row);continue
        native=norm(meta.get('reference','FFFFFFFF'))
        nb,nsrc=c.payload(native);nmeta=c.entry_meta(native)
        row.update({'native_shader':native,'native_meta':nmeta,'native_source':nsrc,'header_bytes':len(hb)})
        if nb is None:
            row['error']='native shader payload unavailable';rows.append(row);errors.append(row);continue
        row['native_bytes']=len(nb);row['native_sha256']=hashlib.sha256(nb).hexdigest()
        footer,checks=find_footer(nb);row['orbshdr_locator']=checks
        if footer is None:
            row['error']='OrbShdr footer unresolved';rows.append(row);errors.append(row);continue
        try:
            info=parse_binary_info(nb,footer);usage=parse_usage(nb,footer,info)
        except Exception as ex:
            row['error']=f'OrbShdr parse failed: {ex!r}';rows.append(row);errors.append(row);continue
        n=int(info['code_length_bytes'])
        if n<=0 or n>footer or n>len(nb):
            row['error']=f'invalid bounded code length {n} footer={footer} payload={len(nb)}';rows.append(row);errors.append(row);continue
        code=nb[:n];fn=f'PS_{sh}_gcn.bin';(a.out_dir/fn).write_bytes(code)
        row.update({'binary_info':info,'usage':usage,'gcn_file':fn,'gcn_bytes':n,'gcn_sha256':hashlib.sha256(code).hexdigest()})
        rows.append(row)

    rep={
      'schema_version':1,'status':'D1_WORLD_PIXEL_SHADER_GCN_EXACT' if not errors else 'D1_WORLD_PIXEL_SHADER_GCN_PARTIAL',
      'selected_count':len(selected),'error_count':len(errors),'shaders':rows,
      'policy':'Shader selection comes from exact visible material frequency; native payload and code bounds are validated through FileHash + OrbShdr metadata.',
    }
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps({'selected_count':len(selected),'error_count':len(errors),'total_gcn_bytes':sum(r.get('gcn_bytes',0) for r in rows)},indent=2))
    return 0 if not errors else 2

if __name__=='__main__': raise SystemExit(main())
