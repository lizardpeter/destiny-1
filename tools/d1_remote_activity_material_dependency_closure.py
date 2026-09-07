#!/usr/bin/env python3
"""Close exact D1 activity Material dependencies across the universal PS4 corpus.

Input is ``d1_activity_selected_material_plan/v1`` produced after exact model-part
material selection. For every selected Material this tool preserves the serialized
retail dependency graph without assigning portable PBR meanings that the shader has
not proved:

  Material / 80801AD7
    -> vertex shader + pixel shader TagHashes
    -> VS/PS TFX bytes, samplers and Vector4 containers
    -> VS/PS texture bindings with their serialized register/index
    -> Texture2D header (32:1/32:2)
       -> direct backing, or 65:1 streamed hop -> 5:1 full-resolution backing

Texture roles remain ``vertex:tN`` / ``pixel:tN``. A register is not called diffuse,
normal, roughness, etc. merely because it occupies a familiar slot. FileHash routing
uses the centralized bank-aware D1 Tiger decoder through RemoteCorpus/d1_filehash.
Unknown shader/resource semantics are retained as exact opaque dependencies rather
than guessed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from d1_material_decode import PS4_MATERIAL_CLASS,parse_material
from d1_texture_export import decode_header,expected_base_size,FORMAT_NAME
from d1_filehash import package_hex
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_split_tar_extract import SplitHttpTar

NULLS={'00000000','FFFFFFFF'}
TEXTURE_HEADERS={(32,1),(32,2)}
STREAM_HOP=(65,1)
FULL_BACKING=(5,1)


def norm(v:object)->str:
 return str(v).upper().removeprefix('0X').zfill(8)

def digest(b:bytes|None)->dict:
 return {'bytes':None if b is None else len(b),'sha256':None if b is None else hashlib.sha256(b).hexdigest()}

def meta(c:RemoteCorpus,h:str)->dict|None:
 h=norm(h);m=c.entry_meta(h)
 if m is None:return None
 return {'tag_hash':h,'package_id':package_hex(h),'index':m.get('index'),'type':m.get('type'),'subtype':m.get('subtype'),
         'reference':norm(m.get('reference','FFFFFFFF')),'file_size':m.get('file_size')}

def exact_tag(c:RemoteCorpus,h:str)->dict:
 h=norm(h)
 if h in NULLS:return {'tag_hash':h,'is_null_sentinel':True,'meta':None,'payload':digest(None)}
 m=meta(c,h)
 try:b,src=c.payload(h)
 except Exception as ex:return {'tag_hash':h,'meta':m,'payload_source':None,'payload':digest(None),'error':'payload:'+repr(ex)}
 return {'tag_hash':h,'meta':m,'payload_source':src,'payload':digest(b)}

def texture_chain(c:RemoteCorpus,h:str)->tuple[dict,list[str],list[dict]]:
 """Resolve one serialized material texture TagHash without semantic-role guessing."""
 h=norm(h);viol=[];edges=[]
 out={'texture':h,'header':exact_tag(c,h),'storage_chain':[],'violations':viol}
 hm=(out['header'].get('meta') or {})
 if (hm.get('type'),hm.get('subtype')) not in TEXTURE_HEADERS:
  viol.append(f'texture_header_type_subtype_not_32_1_or_32_2:{hm.get("type")}:{hm.get("subtype")}')
  return out,viol,edges
 try:hb,hsrc=c.payload(h)
 except Exception as ex:
  viol.append('texture_header_payload:'+repr(ex));return out,viol,edges
 if hb is None:
  viol.append('texture_header_payload_missing');return out,viol,edges
 try:hi=decode_header(hb)
 except Exception as ex:
  viol.append('texture_header_decode:'+repr(ex));return out,viol,edges
 hi['format_name']=FORMAT_NAME.get(hi['surface_format'],f'GCN{hi["surface_format"]:02X}')
 hi['expected_base_size']=expected_base_size(hi['width'],hi['height'],hi['surface_format'],hi['array_size'])
 out['header_info']=hi
 cur=h;curm=hm;seen={h}
 for hop in range(2):
  nxt=norm(curm.get('reference','FFFFFFFF'))
  if nxt in NULLS:break
  if nxt in seen:
   viol.append(f'texture_storage_cycle:{nxt}');break
  seen.add(nxt);tag=exact_tag(c,nxt);nm=tag.get('meta') or {}
  rec={'hop':hop+1,**tag};out['storage_chain'].append(rec)
  edges.append({'subject':cur,'predicate':'FILE_ENTRY_REFERENCE','object':nxt,'evidence_class':'TYPED_EXACT',
                'attrs':{'texture_header':h,'hop':hop+1,'target_type':nm.get('type'),'target_subtype':nm.get('subtype')}})
  if nm=={} or tag['payload']['bytes'] is None:
   viol.append(f'texture_storage_target_unavailable:{nxt}');break
  if (nm.get('type'),nm.get('subtype'))==FULL_BACKING:
   break
  if hop==0 and (nm.get('type'),nm.get('subtype'))==STREAM_HOP:
   cur=nxt;curm=nm;continue
  # Direct payload modes exist; preserve the exact target instead of inventing a
  # second hop. Only the validated 65:1 shape authorizes following another link.
  break
 if out['storage_chain']:
  final=out['storage_chain'][-1]
  out['final_payload_hash']=final['tag_hash']
  out['final_payload_type_subtype']=[(final.get('meta') or {}).get('type'),(final.get('meta') or {}).get('subtype')]
  expected=hi.get('expected_base_size');actual=(final.get('payload') or {}).get('bytes')
  out['base_size_validation']={'expected':expected,'actual':actual,'sufficient':None if expected is None or actual is None else actual>=expected}
  if expected is not None and actual is not None and actual<expected:
   viol.append(f'full_resolution_payload_short:{actual}<{expected}')
 else:
  out['final_payload_hash']=None
  viol.append('texture_has_no_resolved_storage_target')
 return out,viol,edges

def main()->int:
 ap=argparse.ArgumentParser()
 ap.add_argument('--selected-material-plan',type=Path,required=True)
 ap.add_argument('--member-catalog',type=Path,action='append',required=True)
 ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
 ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True)
 a=ap.parse_args()
 plan=json.loads(a.selected_material_plan.read_text())
 plan_viol=[]
 if plan.get('schema')!='d1_activity_selected_material_plan/v1':plan_viol.append('unexpected_selected_material_plan_schema')
 if plan.get('status') not in {'D1_ACTIVITY_SELECTED_MATERIAL_PLAN_COMPLETE','D1_ACTIVITY_SELECTED_MATERIAL_PLAN_PARTIAL'}:plan_viol.append('selected_material_plan_invalid_status')
 mats=sorted({norm(x) for x in plan.get('materials',[]) if norm(x) not in NULLS})
 if int(plan.get('unique_material_count',len(mats)))!=len(mats):plan_viol.append('selected_material_count_mismatch')
 catalogs=load_catalogs(a.member_catalog)
 base=a.base_url.rstrip('/')
 arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
 c=RemoteCorpus(arc,catalogs,a.runtime)
 rows=[];viol=list(plan_viol);edges=[];textures=set();shaders=set();constants=set()
 for mh in mats:
  row={'material':mh,'package_id':package_hex(mh),'tag':exact_tag(c,mh),'violations':[],'dependencies':{}}
  mm=row['tag'].get('meta') or {}
  try:mb,msrc=c.payload(mh)
  except Exception as ex:mb=None;row['violations'].append('material_payload:'+repr(ex))
  if norm(mm.get('reference','FFFFFFFF'))!=PS4_MATERIAL_CLASS or mb is None:
   row['violations'].append('material_missing_or_class_mismatch')
  else:
   try:d=parse_material(mb,'PS4')
   except Exception as ex:row['violations'].append('material_parse:'+repr(ex));d=None
   if d is not None:
    row['material_fields']={'declared_file_size':d['declared_file_size'],'actual_file_size':d['actual_file_size'],
                            'unk08':d['unk08'],'unk0c':d['unk0c'],'unk10':d['unk10'],'unk20':d['unk20'],'unk20_hex':d['unk20_hex']}
    stage_rows={}
    for stage,prefix in [('vertex','vs'),('pixel','ps')]:
     sh=norm(d[f'{"vertex" if stage=="vertex" else "pixel"}_shader']);shaders.add(sh)
     shader=exact_tag(c,sh);edges.append({'subject':mh,'predicate':f'{stage.upper()}_SHADER','object':sh,'evidence_class':'TYPED_EXACT'})
     if sh not in NULLS and (shader.get('meta') is None or shader['payload']['bytes'] is None):row['violations'].append(f'{stage}_shader_unavailable:{sh}')
     ch=norm(d[f'{prefix}_vector4_container']);const=exact_tag(c,ch)
     if ch not in NULLS:
      constants.add(ch);edges.append({'subject':mh,'predicate':f'{stage.upper()}_VECTOR4_CONTAINER','object':ch,'evidence_class':'TYPED_EXACT'})
      cm=const.get('meta') or {};cr=norm(cm.get('reference','FFFFFFFF'))
      if cr not in NULLS:
       cback=exact_tag(c,cr);const['referenced_payload']=cback;edges.append({'subject':ch,'predicate':'FILE_ENTRY_REFERENCE','object':cr,'evidence_class':'TYPED_EXACT','attrs':{'role':f'{stage}_vector4_payload'}})
     texrows=[]
     arr=d[f'{prefix}_textures']
     for ti in arr.get('items',[]):
      th=norm(ti['texture']);textures.add(th)
      tr,tviol,tedges=texture_chain(c,th);tr['texture_index']=int(ti['texture_index']);tr['register']=f't{int(ti["texture_index"])}';tr['binding_role']=f'{stage}:t{int(ti["texture_index"])}'
      texrows.append(tr);edges.append({'subject':mh,'predicate':f'{stage.upper()}_TEXTURE_BINDING','object':th,'evidence_class':'TYPED_EXACT','attrs':{'texture_index':int(ti['texture_index']),'register':tr['register']}});edges.extend(tedges)
      row['violations'].extend(f'{stage}:{tr["register"]}:{x}' for x in tviol)
     stage_rows[stage]={'shader':shader,'texture_count':len(texrows),'textures':texrows,
                        'tfx_bytecode':d[f'{prefix}_tfx_bytecode'],'samplers':d[f'{prefix}_samplers'],'vector4_container':const}
    row['dependencies']=stage_rows
  if row['violations']:viol.extend(f'{mh}:{x}' for x in row['violations'])
  rows.append(row)
 frontier=sorted(set(plan.get('unresolved_external_variant_models',[])))
 if viol:status='D1_REMOTE_ACTIVITY_MATERIAL_DEPENDENCY_CLOSURE_WITH_VIOLATIONS'
 elif frontier:status='D1_REMOTE_ACTIVITY_MATERIAL_DEPENDENCY_CLOSURE_PARTIAL_VARIANT_FRONTIER'
 else:status='D1_REMOTE_ACTIVITY_MATERIAL_DEPENDENCY_CLOSURE_COMPLETE'
 out={'schema':'d1_remote_activity_material_dependency_closure/v1','status':status,
      'source_selected_material_plan':str(a.selected_material_plan),'selected_material_plan_status':plan.get('status'),
      'material_count':len(mats),'materials':mats,'unique_texture_count':len(textures),'textures':sorted(textures),
      'unique_shader_count':len(shaders-NULLS),'shaders':sorted(shaders-NULLS),'unique_vector4_container_count':len(constants-NULLS),'vector4_containers':sorted(constants-NULLS),
      'unresolved_external_variant_models':frontier,'rows':rows,'typed_edges':edges,'typed_edge_count':len(edges),'violations':viol,
      'policy':('Every dependency is serialized by an exact selected retail Material or by a validated FileEntry reference chain. Texture register identity, shaders, TFX, samplers and constant resources are preserved exactly. Texture register numbers are not promoted to PBR semantics. The validated streamed texture shape is 32:1/32:2 -> 65:1 -> 5:1, while direct backing targets are preserved without inventing a second hop. Unresolved external material variants remain an explicit frontier.')}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
 print('STATUS',status,'MATERIALS',len(mats),'TEXTURES',len(textures),'SHADERS',len(shaders-NULLS),'VEC4',len(constants-NULLS),'EDGES',len(edges),'VARIANT_FRONTIER',len(frontier),'VIOLATIONS',len(viol))
 return 0 if not viol else 2

if __name__=='__main__':raise SystemExit(main())
