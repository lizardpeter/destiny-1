#!/usr/bin/env python3
"""Create a GLB animation subset/reorder without touching geometry or binary payloads.

Useful for D1 validation previews because many generic glTF viewers auto-play only the
first animation. Accessors/bufferViews that become unused are intentionally retained;
this keeps the operation lossless with respect to the chosen animation records and
avoids rewriting binary resources.
"""
from __future__ import annotations
import argparse,json,struct
from pathlib import Path

JSON_CHUNK=0x4E4F534A
BIN_CHUNK=0x004E4942

def read_glb(path:Path):
    b=path.read_bytes()
    if len(b)<12: raise ValueError('GLB too small')
    magic,version,total=struct.unpack_from('<4sII',b,0)
    if magic!=b'glTF' or version!=2 or total!=len(b): raise ValueError('invalid GLB v2 header')
    p=12;chunks=[]
    while p<total:
        if p+8>total: raise ValueError('truncated chunk header')
        n,t=struct.unpack_from('<II',b,p);p+=8
        if p+n>total: raise ValueError('truncated chunk')
        chunks.append((t,b[p:p+n]));p+=n
    if not chunks or chunks[0][0]!=JSON_CHUNK: raise ValueError('first GLB chunk is not JSON')
    j=json.loads(chunks[0][1].rstrip(b' \t\r\n\0').decode('utf-8'))
    return j,chunks[1:]

def write_glb(path:Path,j,rest):
    raw=json.dumps(j,separators=(',',':'),ensure_ascii=False).encode('utf-8')
    raw+=b' '*((-len(raw))%4)
    chunks=[(JSON_CHUNK,raw),*rest]
    body=b''.join(struct.pack('<II',len(c),t)+c for t,c in chunks)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(struct.pack('<4sII',b'glTF',2,12+len(body))+body)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('input',type=Path)
    ap.add_argument('--animation',action='append',required=True,help='Exact animation name to retain; repeat to set output order')
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    j,rest=read_glb(a.input)
    anims=j.get('animations',[])
    by={}
    for x in anims:
        n=x.get('name')
        if n in by: raise ValueError(f'duplicate animation name {n!r}')
        by[n]=x
    missing=[n for n in a.animation if n not in by]
    if missing: raise ValueError(f'animations not found: {missing}; available={list(by)}')
    if len(set(a.animation))!=len(a.animation): raise ValueError('requested animation names must be unique')
    j['animations']=[by[n] for n in a.animation]
    j.setdefault('extras',{})['d1AnimationSubset']={'source':a.input.name,'animations':a.animation,'binaryResourcesRewritten':False}
    write_glb(a.out,j,rest)
    print(json.dumps({'input':str(a.input),'output':str(a.out),'animations':a.animation,'output_bytes':a.out.stat().st_size},indent=2))
if __name__=='__main__':main()
