#!/usr/bin/env python3
"""Apply evidence-scoped texture previews to a D1 world GLB.

Canonical extraction remains untouched: this adapter consumes an already-exported
world GLB plus the exact material->shader->t# manifest and a separate role
inventory.  It can bind only STRONG_FORMAT_CANDIDATE base textures, or optionally
include MEDIUM_PREVIEW_CANDIDATE materials.  No preview inference is written back
as canonical D1 shader semantics.

BC5 normal candidates are converted from stored XY into a portable RGB tangent
normal by reconstructing +Z.  Alpha is intentionally kept OPAQUE because D1
surface alpha is not universally transparency.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image

MAT_RE=re.compile(r'TigerMaterial_([0-9A-Fa-f]{8})')


def image_path(texrec:dict,root:Path)->Path|None:
    p=texrec.get('png')
    if p:
        q=root/p
        if q.exists(): return q
    return None


def bc5_to_rgb_normal(im:Image.Image)->Image.Image:
    a=np.asarray(im.convert('RGB'),dtype=np.float32)/255.0
    x=a[...,0]*2.0-1.0;y=a[...,1]*2.0-1.0
    z=np.sqrt(np.maximum(0.0,1.0-x*x-y*y))
    out=np.stack(((x*0.5+0.5),(y*0.5+0.5),(z*0.5+0.5)),axis=-1)
    return Image.fromarray(np.clip(out*255.0+0.5,0,255).astype(np.uint8),'RGB')


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--input-glb',type=Path,required=True)
    ap.add_argument('--manifest',type=Path,required=True)
    ap.add_argument('--roles',type=Path,required=True)
    ap.add_argument('--texture-dir',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--report',type=Path,required=True)
    ap.add_argument('--include-medium-base',action='store_true')
    ap.add_argument('--bind-normal-candidates',action='store_true')
    a=ap.parse_args()

    manifest=json.loads(a.manifest.read_text());roles=json.loads(a.roles.read_text())
    tex=manifest['textures'];sem=roles['materials']
    scene=trimesh.load(a.input_glb,force='scene',process=False)

    image_cache={};normal_cache={};material_cache={};maps={};unresolved=[]
    allowed={'STRONG_FORMAT_CANDIDATE'}
    if a.include_medium_base: allowed.add('MEDIUM_PREVIEW_CANDIDATE')

    def load_base(th:str):
        if th in image_cache:return image_cache[th]
        p=image_path(tex.get(th,{}),a.texture_dir)
        if not p:return None
        im=Image.open(p);im.load();image_cache[th]=im
        return im

    def load_normal(th:str):
        if th in normal_cache:return normal_cache[th]
        p=image_path(tex.get(th,{}),a.texture_dir)
        if not p:return None
        im=Image.open(p);im.load();n=bc5_to_rgb_normal(im);normal_cache[th]=n
        return n

    textured_geom=0;normal_geom=0
    for gname,g in scene.geometry.items():
        old=getattr(getattr(g,'visual',None),'material',None);name=getattr(old,'name',None) or ''
        mm=MAT_RE.search(name)
        if not mm: unresolved.append({'geometry':gname,'reason':'material hash absent','material_name':name});continue
        mh=mm.group(1).upper();r=sem.get(mh)
        if not r: unresolved.append({'geometry':gname,'material':mh,'reason':'role inventory missing'});continue
        conf=r.get('preview_base_confidence','NONE');base=r.get('preview_base_color') if conf in allowed else None
        normal=r.get('preview_normal') if a.bind_normal_candidates and r.get('preview_normal_confidence')=='STRONG_FORMAT_CANDIDATE' else None
        if not base: continue
        key=(mh,base,normal)
        mat=material_cache.get(key)
        if mat is None:
            bi=load_base(base)
            if bi is None:
                unresolved.append({'geometry':gname,'material':mh,'texture':base,'reason':'base PNG unavailable'});continue
            ni=load_normal(normal) if normal else None
            mat=trimesh.visual.material.PBRMaterial(
                name=f'TigerMaterial_{mh}_PREVIEW',baseColorTexture=bi,normalTexture=ni,
                metallicFactor=0.0,roughnessFactor=1.0,doubleSided=False,alphaMode='OPAQUE')
            material_cache[key]=mat
            maps[mh]={
                'base_texture':base,'base_confidence':conf,
                'normal_texture':normal if ni is not None else None,
                'normal_confidence':r.get('preview_normal_confidence') if ni is not None else 'NONE',
            }
        uv=getattr(g.visual,'uv',None)
        g.visual=trimesh.visual.TextureVisuals(uv=uv,material=mat)
        textured_geom+=1
        if maps[mh].get('normal_texture'):normal_geom+=1

    a.out.parent.mkdir(parents=True,exist_ok=True);scene.export(a.out,file_type='glb')
    chk=trimesh.load(a.out,force='scene',process=False)
    rep={
      'schema_version':1,'status':'D1_WORLD_TEXTURED_PREVIEW_ADAPTER',
      'input_glb':str(a.input_glb),'input_sha256':hashlib.sha256(a.input_glb.read_bytes()).hexdigest(),
      'output_glb':str(a.out),'output_sha256':hashlib.sha256(a.out.read_bytes()).hexdigest(),'output_bytes':a.out.stat().st_size,
      'geometry_count':len(scene.geometry),'node_count':len(scene.graph.nodes_geometry),
      'reload_geometry_count':len(chk.geometry),'reload_node_count':len(chk.graph.nodes_geometry),
      'textured_geometry_count':textured_geom,'normal_mapped_geometry_count':normal_geom,
      'textured_material_count':len(maps),'material_mappings':maps,'unresolved_geometry':unresolved,
      'include_medium_base':a.include_medium_base,'bind_normal_candidates':a.bind_normal_candidates,
      'preview_fallback_pbr':{'metallicFactor':0.0,'roughnessFactor':1.0,'alphaMode':'OPAQUE'},
      'policy':'Preview role hints never replace exact D1 shader/register semantics. Alpha stays opaque until per-shader transparency/blend behavior is proven. BC5 normal candidates are portable +Z reconstructions only when explicitly enabled.',
    }
    if rep['reload_node_count']!=rep['node_count']:raise SystemExit('reload node count mismatch')
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps({k:rep[k] for k in ('geometry_count','node_count','textured_geometry_count','normal_mapped_geometry_count','textured_material_count','output_bytes')},indent=2))
    return 0

if __name__=='__main__':raise SystemExit(main())
