#!/usr/bin/env python3
"""Build a cleaner Crota Blender preview from the source-closed R7 color-stage GLB.

R7 already selects the correct six disjoint group-2 color surfaces. This adapter fixes
one remaining portable-PBR mistake: PS 8108E955's BC4/control resources are not native
base-color maps and must not multiply Blender Base Color. For those procedural armor
materials we show the exact source cbuffer color vector only. Direct native color
samples (8108E951 / 8108E952) remain texture-backed.

Optional diagnostic-unlit mode adds KHR_materials_unlit to the active color materials
so geometry/UV/color can be inspected without Blender lighting confounds. This is
explicitly a viewport diagnostic, not a claim about native Destiny lighting.
"""
from __future__ import annotations
import argparse,copy,hashlib,json,struct
from pathlib import Path

PROC={'8108E7A9','8108E7B2'}
ATLAS={'8108E7AA','8108E7B3'}
DETAIL={'8108E7B1'}
ACTIVE=PROC|ATLAS|DETAIL
PROC_FACTOR=[0.18661969900131226,1.0,0.8700880408287048,1.0]
DETAIL_FACTOR=[0.22183096408843994,1.0,0.9177990555763245,1.0]

def read_glb(p:Path):
 b=p.read_bytes(); assert b[:4]==b'glTF'; jl,jt=struct.unpack_from('<II',b,12); assert jt==0x4e4f534a
 d=json.loads(b[20:20+jl].decode().rstrip(' \x00')); bo=20+jl; bl,bt=struct.unpack_from('<II',b,bo); assert bt==0x004e4942
 return d,b[bo+8:bo+8+bl]

def write_glb(p:Path,d:dict,blob:bytes):
 j=json.dumps(d,separators=(',',':'),ensure_ascii=False).encode(); j+=b' '*((4-len(j)%4)%4)
 bb=blob+b'\x00'*((4-len(blob)%4)%4); out=bytearray(struct.pack('<4sII',b'glTF',2,12+8+len(j)+8+len(bb)))
 out+=struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(bb),0x004e4942)+bb
 p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(out)

def mat_tag(m): return str((m.get('extras') or {}).get('d1_material_taghash','')).upper()

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('input',type=Path); ap.add_argument('--mode',choices=('pbr','diagnostic-unlit'),required=True); ap.add_argument('--out',type=Path,required=True); ap.add_argument('--report',type=Path,required=True); a=ap.parse_args()
 src,blob=read_glb(a.input); d=copy.deepcopy(src)
 root=d['scenes'][int(d.get('scene',0))]['nodes'][0]; visible=[]
 for ni in d['nodes'][root].get('children',[]):
  n=d['nodes'][ni]
  if n.get('mesh') is None: continue
  prim=d['meshes'][int(n['mesh'])]['primitives'][0]; mi=prim.get('material');
  if mi is None: raise SystemExit(f'{n.get("name")}: no material')
  tag=mat_tag(d['materials'][int(mi)]); visible.append((ni,int(mi),tag))
 if len(visible)!=6: raise SystemExit(f'expected six R7 active color surfaces, got {len(visible)}')
 if set(x[2] for x in visible)!=ACTIVE: raise SystemExit(f'active material drift {set(x[2] for x in visible)}')

 if a.mode=='diagnostic-unlit':
  used=set(d.get('extensionsUsed') or []); used.add('KHR_materials_unlit'); d['extensionsUsed']=sorted(used)
 rows=[]
 for mi,m in enumerate(d.get('materials',[])):
  tag=mat_tag(m)
  if tag not in ACTIVE: continue
  pbr=m.setdefault('pbrMetallicRoughness',{}); pbr['metallicFactor']=0.0; pbr['roughnessFactor']=0.82
  if tag in PROC:
   old=pbr.pop('baseColorTexture',None); pbr['baseColorFactor']=PROC_FACTOR
   fix='PS8108E955_EXACT_CBUFFER_COLOR_NO_FALSE_BC4_ALBEDO'
  elif tag in ATLAS:
   tex=pbr.get('baseColorTexture');
   if not tex: raise SystemExit(f'{tag}: exact 8108E951 color texture missing')
   pbr['baseColorFactor']=[1.0,1.0,1.0,1.0]; old=None; fix='PS8108E956_DIRECT_8108E951_COLOR_SAMPLE'
  else:
   tex=pbr.get('baseColorTexture');
   if not tex: raise SystemExit(f'{tag}: exact 8108E952 detail texture missing')
   pbr['baseColorFactor']=DETAIL_FACTOR; old=None; fix='PS8108E953_DIRECT_8108E952_COLOR_SAMPLE_WITH_SOURCE_TINT'
  m['emissiveFactor']=[0.0,0.0,0.0]
  if a.mode=='diagnostic-unlit': m['extensions']={**(m.get('extensions') or {}),'KHR_materials_unlit':{}}
  else:
   exts=dict(m.get('extensions') or {}); exts.pop('KHR_materials_unlit',None); m['extensions']=exts
  ex=m.setdefault('extras',{}); ex['d1_r8_preview_fix']=fix; ex['d1_r8_preview_mode']=a.mode
  rows.append({'material_index':mi,'material':tag,'fix':fix,'baseColorFactor':pbr.get('baseColorFactor'),'baseColorTexture':pbr.get('baseColorTexture')})

 d.setdefault('asset',{}).setdefault('extras',{})['d1CrotaR8NativeColorPreview']={
  'schema':'d1_crota_r8_native_color_preview/v1','mode':a.mode,
  'visibleColorSurfaceCount':6,'proceduralMaterials':sorted(PROC),'directAtlasMaterials':sorted(ATLAS),'detailMaterials':sorted(DETAIL),
  'ps8108e955Policy':'Exact source cbuffer color vector is shown without falsely treating BC4/control texture 8108E7B6 as albedo.',
  'group3Policy':'R7 already leaves group-3 alpha/auxiliary render variants inactive; native GCN group-2 shaders are the full-color family.',
 }
 write_glb(a.out,d,blob); chk,blob2=read_glb(a.out)
 if blob2!=blob: raise SystemExit('BIN chunk changed')
 if len(chk.get('meshes',[]))!=len(src.get('meshes',[])) or len(chk.get('skins',[]))!=len(src.get('skins',[])) or len(chk.get('animations',[]))!=len(src.get('animations',[])): raise SystemExit('geometry/skin/animation structure changed')
 rep={'schema':'d1_crota_r8_native_color_preview/v1','status':'D1_CROTA_R8_NATIVE_COLOR_PREVIEW_COMPLETE','mode':a.mode,'visible_surfaces':6,'material_rows':rows,'animation_count':len(chk.get('animations',[])),'output':str(a.out),'bytes':a.out.stat().st_size,'sha256':hashlib.sha256(a.out.read_bytes()).hexdigest(),'binary_unchanged':True}
 a.report.parent.mkdir(parents=True,exist_ok=True); a.report.write_text(json.dumps(rep,indent=2)+'\n'); print(json.dumps(rep,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
