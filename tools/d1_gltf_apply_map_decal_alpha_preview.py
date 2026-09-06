#!/usr/bin/env python3
"""Apply a conservative glTF transparency preview to D1 map-decal materials.

The common embedded-model layer is exported through the source-crosschecked D1 call
Model.Load(MostDetailed, null, transparentsOnly=true).  The current texture binder
was then forcing every portable base-color material back to alphaMode=OPAQUE, which
is internally contradictory and makes alpha-backed effect cards render as giant
solid sheets in Blender.

This adapter does NOT claim that D1's exact blend equation is ordinary alpha blend.
It simply stops the portable preview from discarding the known transparent-pass
classification: every material in the already-selected map-decal GLB is marked
alphaMode=BLEND.  Native shader/t# metadata remains authoritative in material extras.
The binary chunk, meshes, accessors, textures and images are untouched.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from d1_gltf_layer_merge import read_glb, write_glb


def sha(p:Path)->str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()


def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--input-glb',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--report',type=Path,required=True);ap.add_argument('--expect-materials',type=int)
    a=ap.parse_args();doc,bin_data=read_glb(a.input_glb)
    mats=doc.get('materials',[])
    if a.expect_materials is not None and len(mats)!=a.expect_materials:raise SystemExit(f'material count {len(mats)} != {a.expect_materials}')
    rows=[];base=0;changed=0
    for i,m in enumerate(mats):
        ex=m.get('extras') or {};mh=str(ex.get('d1_material_taghash') or m.get('name') or '')
        pbr=m.get('pbrMetallicRoughness') or {};has_base='baseColorTexture' in pbr
        if has_base:base+=1
        old=m.get('alphaMode','OPAQUE')
        m['alphaMode']='BLEND'
        m.setdefault('extras',{})['d1_portable_alpha_adapter']='MAP_DECAL_TRANSPARENTS_ONLY_TO_GLTF_BLEND_PREVIEW'
        m['extras']['d1_exact_blend_equation']='UNRESOLVED'
        if old!='BLEND':changed+=1
        rows.append({'material_index':i,'material':mh,'had_portable_base_texture':has_base,'old_alpha_mode':old,'new_alpha_mode':'BLEND'})
    doc.setdefault('asset',{'version':'2.0'}).setdefault('extras',{})['d1_map_decal_alpha_preview']={
      'material_count':len(mats),'portable_base_material_count':base,
      'source_selection':'Model.Load(MostDetailed, null, transparentsOnly=true)',
      'adapter':'glTF alphaMode BLEND preview only','exact_d1_blend_equation':'UNRESOLVED'}
    a.out.parent.mkdir(parents=True,exist_ok=True);write_glb(a.out,doc,bin_data)
    check,checkbin=read_glb(a.out)
    if checkbin!=bin_data:raise SystemExit('binary chunk changed')
    if check.get('meshes',[])!=doc.get('meshes',[]):raise SystemExit('mesh array changed during alpha-only adapter')
    rep={'schema_version':1,'status':'D1_GLTF_MAP_DECAL_ALPHA_PREVIEW_APPLIED','input':str(a.input_glb),'input_sha256':sha(a.input_glb),'output':str(a.out),'output_sha256':sha(a.out),'output_bytes':a.out.stat().st_size,'material_count':len(mats),'changed_material_count':changed,'portable_base_material_count':base,'binary_exact':True,'materials':rows,'policy':'All input materials already came from the D1 transparentsOnly map-decal selection. BLEND is a portable Blender/glTF preview approximation only; native D1 blend/test/additive semantics remain unresolved and are not overwritten.'}
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(rep,indent=2)+'\n');print(json.dumps({k:rep[k] for k in ('status','material_count','changed_material_count','portable_base_material_count','binary_exact','output_bytes','output_sha256')},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
