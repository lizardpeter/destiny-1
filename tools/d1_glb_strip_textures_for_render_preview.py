#!/usr/bin/env python3
"""Create a render-preview GLB that preserves geometry/transforms/material factors but removes texture references.

The BIN chunk is retained byte-for-byte. This is only a low-memory diagnostic render proxy,
never an authoritative export artifact.
"""
from __future__ import annotations
import argparse, json, struct
from pathlib import Path

GLB_MAGIC=0x46546C67
JSON_CHUNK=0x4E4F534A
BIN_CHUNK=0x004E4942

def cli():
    ap=argparse.ArgumentParser()
    ap.add_argument('src',type=Path)
    ap.add_argument('dst',type=Path)
    return ap.parse_args()

def main():
    a=cli(); raw=a.src.read_bytes()
    if len(raw)<20: raise SystemExit('GLB too small')
    magic,ver,total=struct.unpack_from('<III',raw,0)
    if magic!=GLB_MAGIC or ver!=2 or total!=len(raw): raise SystemExit('invalid GLB header')
    off=12; chunks=[]
    while off<len(raw):
        ln,typ=struct.unpack_from('<II',raw,off); off+=8
        chunks.append((typ,raw[off:off+ln])); off+=ln
    if not chunks or chunks[0][0]!=JSON_CHUNK: raise SystemExit('missing JSON chunk')
    doc=json.loads(chunks[0][1].decode('utf-8').rstrip(' \t\r\n\x00'))
    doc.pop('images',None); doc.pop('textures',None); doc.pop('samplers',None)
    for m in doc.get('materials',[]):
        for k in ('normalTexture','occlusionTexture','emissiveTexture'):
            m.pop(k,None)
        p=m.get('pbrMetallicRoughness')
        if isinstance(p,dict):
            p.pop('baseColorTexture',None); p.pop('metallicRoughnessTexture',None)
        # Preserve material factors, alpha state and double-sided state.
    j=json.dumps(doc,separators=(',',':'),ensure_ascii=False).encode('utf-8')
    j+=b' ' *((4-len(j)%4)%4)
    out=bytearray(struct.pack('<III',GLB_MAGIC,2,0))
    out+=struct.pack('<II',len(j),JSON_CHUNK)+j
    for typ,payload in chunks[1:]:
        out+=struct.pack('<II',len(payload),typ)+payload
    struct.pack_into('<I',out,8,len(out))
    a.dst.parent.mkdir(parents=True,exist_ok=True); a.dst.write_bytes(out)
    print(json.dumps({'status':'D1_GLTF_RENDER_PREVIEW_PROXY_COMPLETE','source_bytes':len(raw),'output_bytes':len(out),'materials':len(doc.get('materials',[])),'meshes':len(doc.get('meshes',[])),'nodes':len(doc.get('nodes',[])),'images_removed':True,'bin_chunk_retained_byte_for_byte':True},indent=2))

if __name__=='__main__': main()
