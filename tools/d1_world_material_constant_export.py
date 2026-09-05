#!/usr/bin/env python3
"""Export exact PS4 D1 material vec4 constant containers for a world manifest.

The world texture manifest already records each visible material's VS/PS
Vector4Container TagHash.  In Rise of Iron PS4 these hashes resolve to subtype
32:7 GPU headers.  The 16-byte header's +0x08 dword is the vec4 count and its
FileEntry.Reference points to a raw count*16 payload.

This tool follows that chain through the same multi-package Corpus used by world
export, decodes IEEE-754 float4 values while preserving raw u32 words, and keeps
material->constant-container provenance exact.  No shader-semantic naming is
performed here.
"""
from __future__ import annotations

import argparse
import json
import math
import struct
import sys
from collections import defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import d1_tower_map_schema_validate_v5 as v5


def norm(h:str)->str:
    return str(h).upper().removeprefix('0X').zfill(8)


def safe_float(v:float):
    if math.isfinite(v): return v
    if math.isnan(v): return 'nan'
    return 'inf' if v>0 else '-inf'


def decode_vec4s(b:bytes):
    if len(b)%16: raise ValueError(f'payload size {len(b)} is not vec4 aligned')
    out=[]
    for i in range(len(b)//16):
        raw=struct.unpack_from('<4I',b,i*16)
        flt=struct.unpack_from('<4f',b,i*16)
        out.append({
            'index':i,
            'float4':[safe_float(x) for x in flt],
            'u32_hex':[f'{x:08X}' for x in raw],
        })
    return out


def export_container(c,h:str):
    h=norm(h);meta=c.entry_meta(h);hb,src=c.payload(h)
    row={'container':h,'meta':meta,'source':src}
    if meta is None:
        row['error']='container metadata unavailable';return row
    row['type']=meta.get('type');row['subtype']=meta.get('subtype')
    row['reference']=norm(meta.get('reference','FFFFFFFF'))
    if hb is None:
        row['error']='container payload unavailable';return row
    row['header_bytes']=len(hb)
    if len(hb)!=16:
        row['error']=f'expected 16-byte PS4 vector header, got {len(hb)}';return row
    count=struct.unpack_from('<I',hb,8)[0]
    row.update({
        'word0':f'{struct.unpack_from("<I",hb,0)[0]:08X}',
        'word1':f'{struct.unpack_from("<I",hb,4)[0]:08X}',
        'vector_count':count,
        'marker':f'{struct.unpack_from("<I",hb,12)[0]:08X}',
        'expected_payload_bytes':count*16,
    })
    ph=row['reference'];pmeta=c.entry_meta(ph);pb,psrc=c.payload(ph)
    row['payload_meta']=pmeta;row['payload_source']=psrc
    if pmeta is None:
        row['error']='referenced vec4 payload metadata unavailable';return row
    if pb is None:
        row['error']='referenced vec4 payload unavailable';return row
    row['payload_bytes']=len(pb)
    if len(pb)!=count*16:
        row['error']=f'payload size mismatch: expected {count*16}, got {len(pb)}';return row
    try:
        row['vectors']=decode_vec4s(pb)
    except Exception as ex:
        row['error']=repr(ex)
    return row


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--snapshot',type=Path,action='append',required=True)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--manifest',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()

    manifest=json.loads(a.manifest.read_text())
    c=v5.v3.base.Corpus([p.resolve() for p in a.snapshot],a.runtime.resolve())
    refs=defaultdict(list)
    material_links={}
    for mh,m in manifest.get('materials',{}).items():
        const=m.get('constants') or {}
        rec={}
        for stage,key in [('vs','vs_vector4_container'),('ps','ps_vector4_container')]:
            h=norm(const.get(key,'FFFFFFFF'))
            rec[stage]=h
            if h!='FFFFFFFF': refs[h].append({'material':mh,'stage':stage,'pixel_shader':m.get('pixel_shader'),'vertex_shader':m.get('vertex_shader')})
        material_links[mh]=rec

    containers={}
    for i,h in enumerate(sorted(refs),1):
        print(f'CONSTANT {i}/{len(refs)} {h}',flush=True)
        containers[h]=export_container(c,h)

    errors=[h for h,r in containers.items() if r.get('error')]
    ps_visible=sum(1 for m in manifest.get('materials',{}).values() if norm((m.get('constants') or {}).get('ps_vector4_container','FFFFFFFF'))!='FFFFFFFF')
    out={
        'schema_version':1,
        'status':'D1_WORLD_MATERIAL_CONSTANT_EXPORT' if not errors else 'D1_WORLD_MATERIAL_CONSTANT_EXPORT_PARTIAL',
        'visible_material_count':len(manifest.get('materials',{})),
        'materials_with_external_ps_constants':ps_visible,
        'unique_constant_containers':len(containers),
        'decoded_constant_containers':len(containers)-len(errors),
        'constant_errors':len(errors),
        'error_containers':errors,
        'material_constants':material_links,
        'container_references':dict(refs),
        'containers':containers,
        'policy':'Exact PS4 subtype-32:7 header -> raw vec4 payload recovery. Float interpretations retain raw u32 words; no shader-semantic role is inferred here.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','visible_material_count','materials_with_external_ps_constants','unique_constant_containers','decoded_constant_containers','constant_errors')},indent=2))
    return 0 if not errors else 2

if __name__=='__main__':raise SystemExit(main())
