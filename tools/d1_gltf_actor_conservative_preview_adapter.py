#!/usr/bin/env python3
"""Prepare a conservative portable Blender preview of a D1 actor GLB.

The exact actor exporter preserves decoded D1 RGBA vertex fields as glTF COLOR_0.
That is lossless as data, but generic glTF PBR gives COLOR_0 a stronger meaning:
it multiplies base color/alpha. Until native D1 shader use is proven to be display
colour, portable PBR must not assume that semantic.

Likewise, the exact texture binder embeds every native VS/PS texture and records
semantic confidence, but its portable preview may bind STRONG_FORMAT_CANDIDATE
base textures. For an inspection file we prefer an evidence-conservative view:
only PROVEN base/normal preview slots remain visible. Weaker candidates remain
embedded and fully described in extras, but the portable material is neutral gray.

This adapter changes JSON semantics only. Accessor identities and the entire BIN
chunk are preserved byte-for-byte.
"""
from __future__ import annotations

import argparse, hashlib, json, struct
from pathlib import Path

MAGIC=0x46546C67; JSON_CHUNK=0x4E4F534A; BIN_CHUNK=0x004E4942


def read_glb(path:Path):
    raw=path.read_bytes()
    magic,ver,total=struct.unpack_from('<III',raw,0)
    if magic!=MAGIC or ver!=2 or total!=len(raw): raise ValueError('invalid GLB2')
    o=12; chunks=[]
    while o<len(raw):
        n,t=struct.unpack_from('<II',raw,o);o+=8;chunks.append((t,raw[o:o+n]));o+=n
    if len(chunks)!=2 or chunks[0][0]!=JSON_CHUNK or chunks[1][0]!=BIN_CHUNK: raise ValueError('expected JSON+BIN GLB')
    doc=json.loads(chunks[0][1].rstrip(b' \t\r\n\0').decode('utf-8'))
    return doc,chunks[1][1],raw


def write_glb(path:Path,doc:dict,bin_chunk:bytes):
    jb=json.dumps(doc,separators=(',',':'),ensure_ascii=False).encode('utf-8');jb+=b' '*((-len(jb))&3)
    bb=bin_chunk+b'\0'*((-len(bin_chunk))&3)
    total=12+8+len(jb)+8+len(bb)
    out=bytearray(struct.pack('<III',MAGIC,2,total));out+=struct.pack('<II',len(jb),JSON_CHUNK)+jb;out+=struct.pack('<II',len(bb),BIN_CHUNK)+bb
    path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(out)


def sha(b:bytes): return hashlib.sha256(b).hexdigest()


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input-glb',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--report',type=Path,required=True);a=ap.parse_args()
    doc,bin_chunk,raw=read_glb(a.input_glb);bin_sha=sha(bin_chunk)

    color_rows=[]
    for mi,m in enumerate(doc.get('meshes') or []):
        for pi,p in enumerate(m.get('primitives') or []):
            attrs=p.setdefault('attributes',{})
            if 'COLOR_0' in attrs:
                if '_D1_COLOR' in attrs: raise SystemExit(f'mesh {mi} primitive {pi}: both COLOR_0 and _D1_COLOR present')
                acc=attrs.pop('COLOR_0');attrs['_D1_COLOR']=acc
                color_rows.append({'mesh':mi,'primitive':pi,'accessor':acc})

    material_rows=[];proven_base=0;neutralized=0;normal_removed=0
    for mi,m in enumerate(doc.get('materials') or []):
        ex=m.get('extras') or {}
        bc=str(ex.get('d1_preview_base_confidence') or 'NONE').upper()
        nc=str(ex.get('d1_preview_normal_confidence') or 'NONE').upper()
        pbr=m.setdefault('pbrMetallicRoughness',{})
        had_base='baseColorTexture' in pbr
        had_normal='normalTexture' in m
        if bc=='PROVEN' and had_base:
            pbr['baseColorFactor']=[1.0,1.0,1.0,1.0];proven_base+=1;base_status='PROVEN_PORTABLE_BASE_RETAINED'
        else:
            if had_base: pbr.pop('baseColorTexture',None)
            pbr['baseColorFactor']=[0.62,0.62,0.62,1.0];neutralized+=1;base_status='PORTABLE_BASE_WITHHELD_NEUTRAL'
        if nc!='PROVEN' and had_normal:
            m.pop('normalTexture',None);normal_removed+=1
        # Actor transparency census already proves this exact production universe opaque.
        m['alphaMode']='OPAQUE';pbr['metallicFactor']=0.0;pbr['roughnessFactor']=1.0
        material_rows.append({'material_index':mi,'name':m.get('name'),'base_confidence':bc,'normal_confidence':nc,'had_base_texture':had_base,'had_normal_texture':had_normal,'base_status':base_status})

    doc.setdefault('asset',{}).setdefault('extras',{})['d1ActorConservativePortablePreview']={
        'status':'D1_ACTOR_CONSERVATIVE_PORTABLE_PREVIEW',
        'standardColor0Withheld':True,'customColorAttribute':'_D1_COLOR',
        'renamedColorPrimitiveCount':len(color_rows),'provenBaseMaterialCount':proven_base,
        'neutralizedMaterialCount':neutralized,'removedNonProvenNormalCount':normal_removed,
        'policy':'Exact native textures/bindings remain embedded. Standard glTF COLOR_0 and non-PROVEN base/normal preview semantics are withheld rather than guessed.'}
    write_glb(a.out,doc,bin_chunk)
    chk,chkbin,_=read_glb(a.out)
    if chkbin!=bin_chunk: raise SystemExit('BIN chunk changed')
    if chk.get('accessors')!=doc.get('accessors') or chk.get('skins')!=doc.get('skins') or chk.get('animations')!=doc.get('animations') or chk.get('nodes')!=doc.get('nodes'):
        raise SystemExit('non-preview structural arrays changed after save/reload')
    rep={'schema_version':1,'status':'D1_ACTOR_CONSERVATIVE_PORTABLE_PREVIEW_COMPLETE','input':str(a.input_glb),'input_sha256':sha(raw),'output':str(a.out),'output_sha256':hashlib.sha256(a.out.read_bytes()).hexdigest(),'bin_sha256':bin_sha,'bin_byte_identical':True,'renamed_COLOR_0_primitive_count':len(color_rows),'proven_base_material_count':proven_base,'neutralized_material_count':neutralized,'removed_nonproven_normal_count':normal_removed,'materials':material_rows,'color_changes':color_rows,'policy':'Inspection adapter only; no native shader semantic is promoted.'}
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(rep,indent=2)+'\n');print(json.dumps({k:rep[k] for k in ('status','renamed_COLOR_0_primitive_count','proven_base_material_count','neutralized_material_count','removed_nonproven_normal_count','output_sha256')},indent=2))

if __name__=='__main__': main()
