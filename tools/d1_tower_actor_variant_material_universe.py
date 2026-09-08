#!/usr/bin/env python3
"""Derive the exact active Material universe from Tower actor signature GLBs.

Only glTF Material records actually referenced by mesh primitives are counted. Unused
legacy/member-0 Material records left in the GLB are deliberately ignored. Every
referenced material must have an exact D1_<8-hex> name. The result is emitted both as
an audit report and in the minimal visual-json shape consumed by
`d1_close_world_texture_dependencies.py`.
"""
from __future__ import annotations
import argparse,collections,json,re,struct
from pathlib import Path

MAT_RE=re.compile(r'^D1_([0-9A-Fa-f]{8})$')
VAR_RE=re.compile(r'^([0-9A-Fa-f]{8})_SIG(\d+)_SKINNED_NATIVE_D1\.glb$')

def read_json(path:Path):
 b=path.read_bytes();
 if len(b)<20: raise ValueError(f'{path}: short GLB')
 magic,ver,total=struct.unpack_from('<4sII',b,0)
 if magic!=b'glTF' or ver!=2 or total!=len(b): raise ValueError(f'{path}: invalid GLB')
 n,t=struct.unpack_from('<I4s',b,12)
 if t!=b'JSON': raise ValueError(f'{path}: missing JSON chunk')
 return json.loads(b[20:20+n].decode('utf-8').rstrip('\x00 '))

def pid(h:str)->str:
 return f'{((int(h,16)-0x80800000)>>13)&0x7ff:04x}'

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input-dir',type=Path,required=True);ap.add_argument('--signatures',type=Path,required=True);ap.add_argument('--selector-output',type=Path,required=True);ap.add_argument('--report',type=Path,required=True);a=ap.parse_args()
 sig=json.loads(a.signatures.read_text());viol=[]
 if sig.get('status')!='D1_TOWER_ACTOR_VISIBLE_MATERIAL_SIGNATURES_COMPLETE' or sig.get('violations'):viol.append('signature_report_not_green')
 files=sorted(a.input_dir.glob('*_SIG*_SKINNED_NATIVE_D1.glb'));rows=[];union=set();models=collections.Counter()
 for p in files:
  mm=VAR_RE.match(p.name)
  if not mm: viol.append(f'unexpected_variant_filename:{p.name}');continue
  model=mm.group(1).upper();si=int(mm.group(2));models[model]+=1
  try:d=read_json(p)
  except Exception as ex: viol.append(f'{p.name}:{ex!r}');continue
  mats=d.get('materials',[]);refs=[]
  for mi,m in enumerate(d.get('meshes',[])):
   for pi,pr in enumerate(m.get('primitives',[])):
    if 'material' not in pr: viol.append(f'{p.name}:mesh{mi}:prim{pi}:no_material');continue
    idx=int(pr['material'])
    if idx<0 or idx>=len(mats): viol.append(f'{p.name}:mesh{mi}:prim{pi}:material_index_oob:{idx}');continue
    name=str(mats[idx].get('name') or '');x=MAT_RE.match(name)
    if not x: viol.append(f'{p.name}:mesh{mi}:prim{pi}:non_D1_material:{name!r}');continue
    refs.append(x.group(1).upper())
  active=sorted(set(refs));union.update(active)
  rows.append({'model':model,'signature_index':si,'glb':p.name,'primitive_count':len(refs),'active_material_count':len(active),'active_materials':active})
 expected_variants=int(sig.get('total_unique_visible_external_signature_count',-1))
 if len(rows)!=expected_variants:viol.append(f'expected_{expected_variants}_variants_got_{len(rows)}')
 exp_counts={r['model']:int(r.get('unique_visible_external_signature_count') or 0) for r in sig.get('models',[])}
 if dict(sorted(models.items()))!=dict(sorted(exp_counts.items())):viol.append(f'per_model_variant_counts:{dict(models)}:{exp_counts}')
 ids=sorted({pid(h) for h in union})
 selector={'materials':{h:{'visual':True,'source':'active_primitive_in_closed_actor_signature_variant'} for h in sorted(union)}}
 a.selector_output.parent.mkdir(parents=True,exist_ok=True);a.selector_output.write_text(json.dumps(selector,indent=2)+'\n')
 out={'schema_version':1,'status':'D1_TOWER_ACTOR_VARIANT_ACTIVE_MATERIAL_UNIVERSE_COMPLETE' if not viol else 'D1_TOWER_ACTOR_VARIANT_ACTIVE_MATERIAL_UNIVERSE_VIOLATIONS','variant_count':len(rows),'actor_model_count':len(models),'active_material_count':len(union),'active_materials':sorted(union),'required_material_package_ids':ids,'variants':rows,'violations':viol,'policy':'Only Material indices referenced by primitives in the 30 closed signature GLBs are admitted. Unreferenced material records are excluded even if present in the glTF material table.'}
 a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'variant_count':len(rows),'actor_model_count':len(models),'active_material_count':len(union),'required_material_package_ids':ids,'violations':viol},indent=2))
 return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
