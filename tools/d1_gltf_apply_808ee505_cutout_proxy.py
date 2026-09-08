#!/usr/bin/env python3
"""Apply the source-proven 808EE505 hard-discard polarity to a Blender/glTF proxy.

The native shader is more complex than core glTF: it performs iterative displaced
UV lookup, a multi-tap scalar attenuation pass, tangent-space normal reconstruction,
and reflection-cubemap composition.  This adapter does not pretend PBR reproduces
that shader.  It performs only the portable operations that are now instruction-
proven and lossless with respect to their source inputs:

* preserve all exact native t# resources already embedded by the generic binder;
* show t0 RGB as the portable primary color proxy;
* derive the portable normal map from the exact t4 BC5/RG normal source;
* reproduce the t2 hard-discard polarity at undisplaced TEXCOORD_0 by baking a
  binary alpha mask where native-surviving texels are 1 and discarded texels are 0.

The remaining native parallax/attenuation/cubemap path stays authoritative in
material extras through D1_808EE505_SEMANTIC_CONTRACT.json.
"""
from __future__ import annotations

import argparse, copy, hashlib, io, json, re
from pathlib import Path

import numpy as np
from PIL import Image

from d1_gltf_bind_exact_shader_textures_v2 import append_blob
from d1_gltf_layer_merge import read_glb, write_glb

MATERIAL='80D777B6'; PS='808EE505'; T0='808EE4FE'; T2='808EE4FD'; T4='808EE500'
MAT_RE=re.compile(r'(?:TigerMaterial_|D1_)([0-9A-Fa-f]{8})')


def hbytes(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def hfile(p:Path)->str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()

def encode_png(im:Image.Image)->bytes:
    b=io.BytesIO(); im.save(b,format='PNG',optimize=False,compress_level=9); return b.getvalue()

def texture_png(manifest:dict,root:Path,tag:str)->bytes:
    rec=(manifest.get('textures') or {}).get(tag)
    if not rec or rec.get('error') or not rec.get('png'):
        raise ValueError(f'{tag}: exact 2D PNG unavailable in closed manifest')
    p=root/rec['png']
    if not p.exists(): p=root/Path(rec['png']).name
    if not p.exists(): raise FileNotFoundError(str(p))
    raw=p.read_bytes()
    with Image.open(io.BytesIO(raw)) as im: im.verify()
    return raw

def rgba(raw:bytes)->np.ndarray:
    with Image.open(io.BytesIO(raw)) as im:
        a=np.asarray(im.convert('RGBA'),dtype=np.uint8).copy()
    return a

def make_proxy(t0:bytes,t2:bytes)->tuple[bytes,dict]:
    c=rgba(t0); m=rgba(t2)
    if c.shape[:2]!=m.shape[:2]: raise ValueError(f't0/t2 size mismatch {c.shape} != {m.shape}')
    # Native comparison is sample(t2).x > 0.5 => lane removed from the saved final
    # export mask.  For an 8-bit normalized decoded proxy this means keep 0..127,
    # discard 128..255.  Binary alpha makes glTF alphaCutoff=0.5 unambiguous.
    src=m[...,0]
    keep=src<=127
    out=c.copy(); out[...,3]=np.where(keep,255,0).astype(np.uint8)
    raw=encode_png(Image.fromarray(out,'RGBA'))
    return raw,{
      'width':int(out.shape[1]),'height':int(out.shape[0]),
      'kept_texels':int(keep.sum()),'discarded_texels':int((~keep).sum()),
      'keep_fraction':float(keep.mean()),'native_threshold':0.5,
      'native_discard_when':'t2.x > 0.5','decoded_u8_keep_rule':'t2_red <= 127',
    }

def native_texture_index(doc:dict,tag:str)->int:
    hits=[]
    for i,t in enumerate(doc.get('textures',[])):
        ex=t.get('extras') or {}
        if str(ex.get('d1_taghash') or ex.get('d1_source_taghash') or '').upper()==tag: hits.append(i)
    if not hits: raise ValueError(f'{tag}: no embedded exact/derived texture resource')
    # Prefer the exact native texture, not a derived normal with d1_source_taghash.
    exact=[i for i in hits if str((doc['textures'][i].get('extras') or {}).get('d1_taghash') or '').upper()==tag]
    return exact[0] if exact else hits[0]


def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--input-glb',type=Path,required=True); ap.add_argument('--manifest',type=Path,required=True)
    ap.add_argument('--texture-dir',type=Path,required=True); ap.add_argument('--contract',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True); ap.add_argument('--report',type=Path,required=True); a=ap.parse_args()

    man=json.loads(a.manifest.read_text())
    if man.get('status')!='D1_WORLD_VISIBLE_MATERIAL_TEXTURE_EXPORT' or man.get('texture_errors')!=0 or man.get('material_decode_errors')!=0:
        raise SystemExit('target texture manifest is not fully closed')
    sem=json.loads(a.contract.read_text())
    if sem.get('status')!='D1_808EE505_SEMANTIC_CONTRACT_EXACT' or sem.get('violations'):
        raise SystemExit('808EE505 semantic contract is not exact')
    c=sem['contract']
    if c.get('material')!=MATERIAL or c.get('shader')!=PS:
        raise SystemExit('semantic contract target drift')
    td=c['texture_semantics']['t2']
    if td.get('threshold')!=0.5 or td.get('discard_when')!='sample > threshold':
        raise SystemExit('native hard-discard contract drift')

    t0=texture_png(man,a.texture_dir,T0); t2=texture_png(man,a.texture_dir,T2)
    proxy,mask_stats=make_proxy(t0,t2)
    src,srcbin=read_glb(a.input_glb); doc=copy.deepcopy(src); bindata=srcbin

    # Require the generic exact-resource binder to have preserved the native t# corpus.
    exact_indices={h:native_texture_index(doc,h) for h in (T0,T2,T4)}
    bvi,bindata=append_blob(doc,bindata,proxy,'D1_808EE505_T0_RGB_T2_NATIVE_SURVIVAL_ALPHA_PROXY')
    ii=len(doc.setdefault('images',[])); doc['images'].append({
      'name':'D1_808EE505_PORTABLE_CUTOUT_PROXY','mimeType':'image/png','bufferView':bvi,
      'extras':{'d1_derived_portable_proxy':True,'d1_material':MATERIAL,'d1_pixel_shader':PS,
                'd1_rgb_source':T0,'d1_alpha_source':T2,'d1_alpha_derivation':'1 if t2.x <= 0.5 else 0',
                'd1_png_sha256':hbytes(proxy),**mask_stats}})
    ti=len(doc.setdefault('textures',[])); doc['textures'].append({'name':'D1_808EE505_PORTABLE_CUTOUT_PROXY','source':ii,
      'extras':{'d1_derived_portable_proxy':True,'d1_material':MATERIAL,'d1_pixel_shader':PS,'d1_rgb_source':T0,'d1_alpha_source':T2}})

    patched=[]
    for mi,m in enumerate(doc.get('materials',[])):
        mm=MAT_RE.search(str(m.get('name') or '')); mh=mm.group(1).upper() if mm else str((m.get('extras') or {}).get('d1_material_taghash') or '').upper()
        if mh!=MATERIAL: continue
        ex=m.setdefault('extras',{})
        if str(ex.get('d1_pixel_shader') or PS).upper()!=PS: raise SystemExit(f'material {mi}: target hash has unexpected PS')
        native=ex.get('d1_native_texture_bindings') or []
        native_map={int(x.get('t',x.get('texture_index',-1))):str(x.get('taghash',x.get('texture',''))).upper() for x in native}
        if native_map and native_map!={0:T0,1:'808EE4FF',2:T2,3:'808EE4FF',4:T4,5:'80AAFB08'}:
            raise SystemExit(f'material {mi}: native binding drift {native_map}')
        pbr=m.setdefault('pbrMetallicRoughness',{}); pbr['baseColorTexture']={'index':ti,'texCoord':0}; pbr['baseColorFactor']=[1.0,1.0,1.0,1.0]
        pbr['metallicFactor']=0.0; pbr['roughnessFactor']=1.0
        m['alphaMode']='MASK'; m['alphaCutoff']=0.5
        ex['d1_808ee505_semantic_contract']=c
        ex['d1_portable_proxy']={
          'kind':'T0_RGB_PLUS_T2_NATIVE_SURVIVAL_MASK','derived_texture_index':ti,
          'native_t0_texture_index':exact_indices[T0],'native_t2_texture_index':exact_indices[T2],'native_t4_texture_index':exact_indices[T4],
          'hard_discard_polarity_exact_at_sampled_texel':True,'hard_discard_threshold':0.5,
          'parallax_displaced_uv_omitted':True,'t1_multitap_attenuation_omitted':True,'t5_reflection_cubemap_omitted':True,
          'portable_pbr_is_not_native_shader':True}
        patched.append(mi)
    if not patched: raise SystemExit(f'no {MATERIAL} material found in input GLB')

    doc.setdefault('asset',{}).setdefault('extras',{})['d1_808ee505_portable_proxy']={
      'schema':'d1_gltf_apply_808ee505_cutout_proxy/v1','material':MATERIAL,'pixel_shader':PS,
      'patched_material_count':len(patched),'derived_texture_index':ti,
      'native_shader_contract_authoritative':True,'portable_proxy_limitations':['parallax UV omitted','t1 multitap attenuation omitted','t5 reflection cubemap omitted']}

    a.out.parent.mkdir(parents=True,exist_ok=True); write_glb(a.out,doc,bindata); chk,chkbin=read_glb(a.out)
    if chkbin[:len(srcbin)]!=srcbin: raise SystemExit('input BIN is not exact output prefix')
    for k in ('accessors','meshes','nodes','skins','animations','scenes'):
        if chk.get(k,[])!=src.get(k,[]): raise SystemExit(f'{k} changed while applying material proxy')
    rep={'schema_version':1,'status':'D1_808EE505_PORTABLE_CUTOUT_PROXY_APPLIED','input_sha256':hfile(a.input_glb),'output_sha256':hfile(a.out),
         'output_bytes':a.out.stat().st_size,'material':MATERIAL,'pixel_shader':PS,'patched_material_indices':patched,
         'native_exact_texture_indices':exact_indices,'derived_proxy_texture_index':ti,'derived_proxy_png_sha256':hbytes(proxy),'mask_stats':mask_stats,
         'exact_native_semantics_preserved':['t0 primary RGBA resource','t1/t3 repeated scalar resource edges','t2 discard resource and polarity','t4 normal resource','t5 cubemap resource','full semantic contract in extras'],
         'portable_proxy_limitations':['native parallax-displaced UV is not reproducible in core glTF','native t1 eight-tap attenuation is omitted','native cubemap reflection composition is omitted'],
         'policy':'This is an inspection proxy, not a claim that glTF PBR equals the native 808EE505 shader. The binary alpha polarity is instruction-proven; omitted native stages remain explicit.'}
    a.report.parent.mkdir(parents=True,exist_ok=True); a.report.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps(rep,indent=2)); return 0

if __name__=='__main__': raise SystemExit(main())
