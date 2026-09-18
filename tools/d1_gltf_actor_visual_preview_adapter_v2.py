#!/usr/bin/env python3
"""Prepare a Blender-visible D1 actor GLB without discarding texture previews.

The production actor GLBs already contain exact native shader texture resources and
an evidence-scoped portable PBR preview.  The previous conservative adapter was too
aggressive for visual inspection: it removed every portable base/normal whose role
was not instruction-level PROVEN, making most actors neutral gray.

This adapter changes only one unsafe generic-glTF semantic:
  COLOR_0 -> _D1_COLOR

The decoded D1 RGBA accessor is preserved byte-for-byte, but generic glTF PBR no
longer multiplies baseColor/alpha by it.  Existing material PBR bindings, images,
textures, normals, exact native binding metadata, skin, nodes and animations are
otherwise preserved exactly.  STRONG_FORMAT_CANDIDATE preview bindings remain
preview-only evidence and are not promoted to canonical D1 shader semantics.
"""
from __future__ import annotations

import argparse, copy, hashlib, json, struct
from pathlib import Path

MAGIC=0x46546C67; JSON_CHUNK=0x4E4F534A; BIN_CHUNK=0x004E4942


def read_glb(path:Path):
    raw=path.read_bytes(); magic,ver,total=struct.unpack_from('<III',raw,0)
    if magic!=MAGIC or ver!=2 or total!=len(raw): raise ValueError('invalid GLB2')
    o=12; chunks=[]
    while o<len(raw):
        n,t=struct.unpack_from('<II',raw,o);o+=8;chunks.append((t,raw[o:o+n]));o+=n
    if len(chunks)!=2 or chunks[0][0]!=JSON_CHUNK or chunks[1][0]!=BIN_CHUNK:
        raise ValueError('expected JSON+BIN GLB')
    doc=json.loads(chunks[0][1].rstrip(b' \t\r\n\0').decode('utf-8'))
    return doc,chunks[1][1],raw


def write_glb(path:Path,doc:dict,bin_chunk:bytes):
    jb=json.dumps(doc,separators=(',',':'),ensure_ascii=False).encode(); jb+=b' '*((-len(jb))&3)
    bb=bin_chunk+b'\0'*((-len(bin_chunk))&3); total=12+8+len(jb)+8+len(bb)
    out=bytearray(struct.pack('<III',MAGIC,2,total)); out+=struct.pack('<II',len(jb),JSON_CHUNK)+jb; out+=struct.pack('<II',len(bb),BIN_CHUNK)+bb
    path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(out)


def sha(b:bytes): return hashlib.sha256(b).hexdigest()


def material_preview_counts(doc:dict):
    mats=doc.get('materials') or []
    return {
        'material_count':len(mats),
        'base_texture_count':sum(1 for m in mats if 'baseColorTexture' in (m.get('pbrMetallicRoughness') or {})),
        'normal_texture_count':sum(1 for m in mats if 'normalTexture' in m),
        'proven_base_count':sum(1 for m in mats if str((m.get('extras') or {}).get('d1_preview_base_confidence') or '').upper()=='PROVEN'),
        'strong_base_count':sum(1 for m in mats if str((m.get('extras') or {}).get('d1_preview_base_confidence') or '').upper()=='STRONG_FORMAT_CANDIDATE'),
        'medium_base_count':sum(1 for m in mats if str((m.get('extras') or {}).get('d1_preview_base_confidence') or '').upper()=='MEDIUM_PREVIEW_CANDIDATE'),
    }


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--input-glb',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); ap.add_argument('--report',type=Path,required=True); a=ap.parse_args()
    src,bin_chunk,raw=read_glb(a.input_glb); doc=copy.deepcopy(src); before=material_preview_counts(src)
    changed=[]
    for mi,m in enumerate(doc.get('meshes') or []):
        for pi,p in enumerate(m.get('primitives') or []):
            attrs=p.get('attributes') or {}
            if 'COLOR_0' in attrs:
                if '_D1_COLOR' in attrs: raise SystemExit(f'mesh {mi} primitive {pi}: both COLOR_0 and _D1_COLOR')
                acc=attrs.pop('COLOR_0'); attrs['_D1_COLOR']=acc
                changed.append({'mesh':mi,'primitive':pi,'accessor':acc})
    doc.setdefault('asset',{}).setdefault('extras',{})['d1ActorVisualPreviewV2']={
        'status':'D1_ACTOR_VISUAL_PREVIEW_V2',
        'standardColor0Withheld':True,
        'customColorAttribute':'_D1_COLOR',
        'renamedColorPrimitiveCount':len(changed),
        'portablePbrBindingsPreserved':True,
        'policy':'Existing evidence-scoped portable PBR previews are preserved. COLOR_0 is demoted only to prevent generic glTF multiplication by an unproven D1 RGBA semantic.'
    }
    write_glb(a.out,doc,bin_chunk)
    chk,chkbin,_=read_glb(a.out); after=material_preview_counts(chk)
    violations=[]
    if chkbin!=bin_chunk: violations.append('bin_chunk_changed')
    for k in ('accessors','nodes','skins','materials','images','textures','animations'):
        if chk.get(k,[])!=src.get(k,[]): violations.append(f'{k}_changed')
    # Mesh JSON differs only by the attribute key. Restore the custom key in a
    # copy and require exact equality with source meshes.
    restored=copy.deepcopy(chk.get('meshes') or [])
    for m in restored:
        for p in m.get('primitives') or []:
            attrs=p.get('attributes') or {}
            if '_D1_COLOR' in attrs:
                if 'COLOR_0' in attrs: violations.append('restored_mesh_has_both_color_keys')
                attrs['COLOR_0']=attrs.pop('_D1_COLOR')
    if restored!=(src.get('meshes') or []): violations.append('mesh_change_beyond_COLOR_0_rename')
    if before!=after: violations.append(f'portable_preview_counts_changed:{before}:{after}')
    if violations: raise SystemExit(';'.join(violations))
    rep={'schema_version':2,'status':'D1_ACTOR_VISUAL_PREVIEW_V2_COMPLETE','violations':[],
         'input':str(a.input_glb),'input_sha256':sha(raw),'output':str(a.out),'output_sha256':hashlib.sha256(a.out.read_bytes()).hexdigest(),
         'bin_sha256':sha(bin_chunk),'bin_byte_identical':True,'renamed_COLOR_0_primitive_count':len(changed),
         'preview_counts_before':before,'preview_counts_after':after,'color_changes':changed,
         'policy':'Visual inspection adapter only. Existing PBR texture candidates remain explicitly evidence-scoped; no shader semantic is promoted.'}
    a.report.parent.mkdir(parents=True,exist_ok=True); a.report.write_text(json.dumps(rep,indent=2)+'\n'); print(json.dumps({k:rep[k] for k in ('status','renamed_COLOR_0_primitive_count','preview_counts_before','output_sha256')},indent=2))

if __name__=='__main__': main()
