#!/usr/bin/env python3
"""Bake the source-backed Bungie D1 Spasm change-color path into a GLB.

This deliberately implements only the plate-albedo + GStack.R + u_change_color
portion that is already source-closed from Bungie's archived Spasm shader.
Dye detail diffuse/normal is NOT approximated when exact TEXCOORD_2 is absent.
The output uses KHR_materials_unlit so arbitrary viewer lighting cannot hide the
baked color result. It is a diagnostic, not a PS4 deferred-shader claim.
"""
from __future__ import annotations
import argparse, io, json, re, struct
from pathlib import Path
import numpy as np
from PIL import Image

JSON_CHUNK=0x4E4F534A
BIN_CHUNK=0x004E4942
NAME_RE=re.compile(r'(?P<tag>[0-9A-F]{8})_mesh(?P<mesh>\d+)_range(?P<off>\d+)_(?P<count>\d+)', re.I)
DYE_FOR_SLOT={0:8752,1:8753,2:8754}

def read_glb(p:Path):
    raw=p.read_bytes(); magic,ver,total=struct.unpack_from('<4sII',raw,0)
    if magic!=b'glTF' or ver!=2 or total!=len(raw): raise ValueError('not a valid GLB v2')
    pos=12; g=None; bin_blob=None
    while pos<len(raw):
        ln,typ=struct.unpack_from('<II',raw,pos); pos+=8; data=raw[pos:pos+ln]; pos+=ln
        if typ==JSON_CHUNK: g=json.loads(data.decode('utf-8').rstrip('\x00 '))
        elif typ==BIN_CHUNK: bin_blob=bytearray(data)
    if g is None or bin_blob is None: raise ValueError('GLB must contain JSON and BIN chunks')
    if len(g.get('buffers',[]))!=1: raise ValueError('expected one-buffer GLB')
    return g,bin_blob

def write_glb(p:Path,g:dict,blob:bytearray):
    g['buffers'][0]['byteLength']=len(blob)
    js=json.dumps(g,separators=(',',':'),ensure_ascii=False).encode('utf-8'); js+=b' '*((4-len(js)%4)%4)
    bb=bytes(blob); bb+=b'\x00'*((4-len(bb)%4)%4)
    total=12+8+len(js)+8+len(bb)
    out=bytearray(struct.pack('<4sII',b'glTF',2,total)); out+=struct.pack('<II',len(js),JSON_CHUNK)+js; out+=struct.pack('<II',len(bb),BIN_CHUNK)+bb
    p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(out)

def image_bytes(g,blob,image_index):
    im=g['images'][image_index]
    if 'bufferView' not in im: raise ValueError(f'image {image_index} is not bufferView-backed')
    bv=g['bufferViews'][im['bufferView']]
    if bv.get('buffer',0)!=0: raise ValueError('image bufferView not in buffer 0')
    off=int(bv.get('byteOffset',0)); ln=int(bv['byteLength']); return bytes(blob[off:off+ln])

def append_bytes(g,blob,data:bytes,name:str):
    pad=(-len(blob))%4
    if pad: blob.extend(b'\x00'*pad)
    off=len(blob); blob.extend(data); idx=len(g.setdefault('bufferViews',[]))
    g['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':len(data),'name':name}); return idx

def load_stage_selectors(path:Path):
    d=json.loads(path.read_text()); out={}
    if d.get('conflict_count')!=0: raise ValueError('stage selector report contains conflicts')
    for m in d['models']:
        for mesh in m['meshes']:
            for gr in mesh['groups']:
                if not gr.get('resolved'): raise ValueError(f"unresolved selector {gr['name']}")
                out[gr['name'].upper()]=int(gr['gear_dye_change_color_index'])
    return out,d

def load_dyes(path:Path):
    d=json.loads(path.read_text()); dyes={int(x['dye_index']):x['dye'] for x in d['dyes'] if x.get('resolved')}
    if set(DYE_FOR_SLOT.values())-set(dyes): raise ValueError('missing one of exact Spektar dyes 8752/8753/8754')
    for slot,di in DYE_FOR_SLOT.items():
        if int(dyes[di]['slot_type_index'])!=slot: raise ValueError(f'dye {di} slot mismatch')
    return dyes,d

def selector_color(selector:int,dyes):
    if not 0<=selector<=5: raise ValueError(f'change-color selector {selector} is not armor primary/secondary')
    slot=selector//2; secondary=selector&1; di=DYE_FOR_SLOT[slot]; dye=dyes[di]
    key='secondary_color' if secondary else 'primary_color'; return np.asarray(dye[key][:3],dtype=np.float32),di,key

def overlay(back,front): return front*np.clip(back*4.0,0.0,1.0)+np.clip(back-0.25,0.0,1.0)

def bake(albedo_png:bytes,gstack_png:bytes,color):
    a=np.asarray(Image.open(io.BytesIO(albedo_png)).convert('RGBA'),dtype=np.float32)/255.0
    gs=np.asarray(Image.open(io.BytesIO(gstack_png)).convert('RGBA'),dtype=np.float32)/255.0
    if a.shape[:2]!=gs.shape[:2]: raise ValueError(f'albedo/GStack dimensions differ: {a.shape} {gs.shape}')
    base=np.power(a[...,:3],2.2); front=np.asarray(color,dtype=np.float32).reshape(1,1,3); dyed=overlay(base,front); mask=gs[...,0:1]
    mixed=base*(1.0-mask)+dyed*mask; srgb=np.power(np.clip(mixed,0.0,1.0),1.0/2.2)
    rgba=np.concatenate([srgb,np.ones((*srgb.shape[:2],1),dtype=np.float32)],axis=2)
    out=Image.fromarray(np.rint(np.clip(rgba,0,1)*255).astype(np.uint8),'RGBA'); bio=io.BytesIO(); out.save(bio,format='PNG',optimize=False)
    return bio.getvalue(), {'width':out.width,'height':out.height,'mask_min':float(mask.min()),'mask_max':float(mask.max()),'mask_mean':float(mask.mean())}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('input_glb',type=Path); ap.add_argument('--stage-dyes',type=Path,required=True); ap.add_argument('--exact-dyes',type=Path,required=True)
    ap.add_argument('-o','--out',type=Path,required=True); ap.add_argument('--report',type=Path,required=True); a=ap.parse_args()
    g,blob=read_glb(a.input_glb); selectors,sd=load_stage_selectors(a.stage_dyes); dyes,dd=load_dyes(a.exact_dyes)
    active=[]
    for ni,n in enumerate(g['nodes']):
        if n.get('mesh') is None: continue
        mi=int(n['mesh']); mesh=g['meshes'][mi]; name=(mesh.get('name') or n.get('name') or ''); mat=NAME_RE.search(name)
        if not mat: raise ValueError(f'active mesh name cannot map to D1 range: {name!r}')
        key=f"{mat.group('tag').upper()}_mesh{int(mat.group('mesh'))}_range{int(mat.group('off'))}_{int(mat.group('count'))}".upper()
        if key not in selectors: raise ValueError(f'active range {key} missing exact stage selector')
        if len(mesh['primitives'])!=1: raise ValueError(f'{name}: expected one primitive')
        active.append((ni,mi,name,key,int(selectors[key]),mesh['primitives'][0]))
    baked_cache={}; rows=[]
    for ni,mi,name,key,selector,prim in active:
        oldmat_i=int(prim['material']); oldmat=g['materials'][oldmat_i]; ex=oldmat.get('extras') or {}
        if 'd1GStackTextureIndex' not in ex: raise ValueError(f'{name}: old material has no exact GStack texture')
        albedo_tex=int(oldmat['pbrMetallicRoughness']['baseColorTexture']['index']); gs_tex=int(ex['d1GStackTextureIndex']); cache_key=(oldmat_i,selector)
        color,di,color_role=selector_color(selector,dyes)
        if cache_key not in baked_cache:
            albedo_img=int(g['textures'][albedo_tex]['source']); gs_img=int(g['textures'][gs_tex]['source']); png,stats=bake(image_bytes(g,blob,albedo_img),image_bytes(g,blob,gs_img),color)
            plate=ex.get('d1TexturePlateHeader','UNKNOWN'); bv=append_bytes(g,blob,png,f'{plate}_selector{selector}_spasm_change_color_png')
            ii=len(g['images']); g.setdefault('images',[]).append({'bufferView':bv,'mimeType':'image/png','name':f'{plate}_selector{selector}_spasm_change_color'})
            ti=len(g['textures']); g.setdefault('textures',[]).append({'source':ii,'sampler':g['textures'][albedo_tex].get('sampler',0),'name':f'{plate}_selector{selector}_spasm_change_color'})
            nm=f"D1_{plate}_selector{selector}_dye{di}_{color_role}_SPASM_CHANGE_COLOR_UNLIT"
            newmat={'name':nm,'pbrMetallicRoughness':{'baseColorFactor':[1,1,1,1],'baseColorTexture':{'index':ti,'texCoord':0},'metallicFactor':0.0,'roughnessFactor':1.0},
              'emissiveFactor':[0,0,0],'alphaMode':'OPAQUE','doubleSided':bool(oldmat.get('doubleSided',False)),'extensions':{'KHR_materials_unlit':{}},
              'extras':{'d1PreviewPolicy':'Bungie archived Spasm plate-albedo + GStack.R + u_change_color path baked exactly; dye detail texture pass omitted pending exact TEXCOORD_2; KHR_materials_unlit prevents viewer lighting from obscuring this color diagnostic.',
                'd1OriginalMaterialIndex':oldmat_i,'d1TexturePlateHeader':plate,'d1GStackTextureIndex':gs_tex,'d1GearDyeChangeColorIndex':selector,'d1DyeIndex':di,'d1DyeColorRole':color_role,
                'd1ChangeColor':[float(x) for x in color],'d1SpasmFormula':'linear=albedo^2.2; overlay=changeColor*clamp(linear*4,0,1)+clamp(linear-.25,0,1); mixed=mix(linear,overlay,gstack.r); out=mixed^(1/2.2)',
                'd1DyeDetailStatus':'not_applied_exact_TEXCOORD_2_not_yet_exported'}}
            newmat_i=len(g['materials']); g['materials'].append(newmat); baked_cache[cache_key]=(newmat_i,stats,nm)
        newmat_i,stats,nm=baked_cache[cache_key]; prim['material']=newmat_i
        rows.append({'node':ni,'mesh':mi,'name':name,'range_key':key,'selector':selector,'dye_index':di,'color_role':color_role,'change_color':[float(x) for x in color], 'old_material':oldmat_i,'new_material':newmat_i,'new_material_name':nm,**stats})
    used=g.setdefault('extensionsUsed',[])
    if 'KHR_materials_unlit' not in used: used.append('KHR_materials_unlit')
    g['extras']={**(g.get('extras') or {}),'d1SpasmChangeColorDiagnostic':{'active_primitive_count':len(active),'baked_material_count':len(baked_cache),'source':'Bungie archived D1 Spasm GearShader fragment path',
      'exact':'plate albedo, GStack.R change-color mask, exact per-stage selector, exact Spektar primary/secondary dye colors','omitted':'dye detail diffuse/normal because exact a_texcoord2/TEXCOORD_2 is not present in this GLB; lighting/specular intentionally omitted in unlit diagnostic'}}
    write_glb(a.out,g,blob)
    rep={'schema':'d1_guardian_spasm_change_color_bake/v1','input':str(a.input_glb),'output':str(a.out),'output_bytes':a.out.stat().st_size,'active_primitive_count':len(active),'baked_material_count':len(baked_cache),'rows':rows,'policy':g['extras']['d1SpasmChangeColorDiagnostic']}
    a.report.parent.mkdir(parents=True,exist_ok=True); a.report.write_text(json.dumps(rep,indent=2)+'\n'); print(json.dumps({'active':len(active),'baked_materials':len(baked_cache),'bytes':a.out.stat().st_size},indent=2))
if __name__=='__main__': main()
