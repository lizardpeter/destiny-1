#!/usr/bin/env python3
"""Reuse exact registered D1 VS interface semantics for Crota.

The repository's native shader semantic registry closes two bounded VS GCN
programs used by Crota:
  809DE9AB -> 24392d... four-influence DQ skinning
  809DF743 -> a5ad94... single-palette DQ transform

Both source proofs establish the same post-fetch/export contract:
  param0 = transformed normal N (+ scalar w)
  param1 = transformed tangent T
  param2 = handed bitangent B
  param3 = transformed UV pair duplicated
  param4 = transformed position P

This tool joins that exact-GCN reuse contract to Crota's exact VS->PS raw GNM
linkage. Fetch-shader source offsets/formats remain a separate gate.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

PROGRAMS={
 '809DE9AB':{
   'gcn_sha256':'24392dbd8f217a832456372a8d9c24d3ef365ab5a0b8bcd362882ca845052964',
   'source_proof_status':'D1_XUR_VS_24392DBD_FOUR_INFLUENCE_DQ_EXACT',
   'semantic_class':'four_influence_dual_quaternion_skinning',
   'handler':'tools/d1_xur_vs_8087695b_four_influence_semantic_proof.py',
 },
 '809DF743':{
   'gcn_sha256':'a5ad940fbf21746563f6585b889ac91b4220c94a3559e768028c894454bcdc12',
   'source_proof_status':'D1_XUR_VS_A5AD940F_DATAFLOW_SEMANTICS_EXACT',
   'semantic_class':'single_palette_dual_quaternion_transform',
   'handler':'tools/d1_xur_vs_8087695c_family_semantic_proof.py',
 },
}
PARAM={
 0:{'symbol':'N','semantic':'TRANSFORMED_NORMAL_XYZ','w':'SOURCE_OWNED_SATURATED_SCALAR'},
 1:{'symbol':'T','semantic':'TRANSFORMED_TANGENT_XYZ','w':'TANGENT_Z_DUPLICATED'},
 2:{'symbol':'B','semantic':'HANDED_TRANSFORMED_BITANGENT_XYZ','w':'ONE'},
 3:{'symbol':'UV','semantic':'API11_AFFINE_SOURCE_UV_XY_DUPLICATED_TO_ZW','w':'UV_Y'},
 4:{'symbol':'P','semantic':'TRANSFORMED_POSITION_XYZ','w':'ONE'},
}

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--extract-report',type=Path,required=True)
 ap.add_argument('--linkage',type=Path,required=True)
 ap.add_argument('--registry',type=Path,required=True)
 ap.add_argument('--out',type=Path,required=True)
 a=ap.parse_args()
 ex=json.loads(a.extract_report.read_text());lk=json.loads(a.linkage.read_text());rg=json.loads(a.registry.read_text());v=[];rows=[]
 if ex.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or ex.get('error_count'):v.append('shader extract not exact')
 if lk.get('status')!='D1_GNM_VS_PS_LINKAGE_EXACT' or lk.get('violations'):v.append('VS/PS linkage not exact')
 if rg.get('status')!='D1_NATIVE_SHADER_SEMANTIC_REGISTRY_V1_EXACT' or rg.get('violations'):v.append('semantic registry not exact')
 eby={norm(x['shader']):x for x in ex.get('shaders',[])}
 regby={str(x['gcn_sha256']).lower():x for x in rg.get('entries',[]) if x.get('stage')=='vs'}

 for vs,spec in PROGRAMS.items():
  e=eby.get(vs)
  if not e:v.append(f'{vs}: extract row missing');continue
  gh=str(e.get('gcn_sha256','')).lower()
  if gh!=spec['gcn_sha256']:v.append(f'{vs}: GCN {gh} != {spec["gcn_sha256"]}')
  rr=regby.get(spec['gcn_sha256'])
  if not rr:v.append(f'{vs}: registry GCN row missing');continue
  if vs not in [norm(x) for x in rr.get('shader_headers',[])]:v.append(f'{vs}: registry header membership missing')
  for k in ('source_proof_status','semantic_class','handler'):
   if rr.get(k)!=spec[k]:v.append(f'{vs}: registry {k} drift {rr.get(k)!r} != {spec[k]!r}')

 for link in lk.get('links',[]):
  vs=norm(link['vertex_shader'])
  if vs not in PROGRAMS:continue
  ps=norm(link['pixel_shader'])
  attrs=[]
  for x in link.get('consumed_linkage',[]):
   pi=x.get('vs_param_index')
   if pi is None:
    v.append(f'{vs}:{ps}: attr{x.get("attr_index")} has no VS param producer');continue
   pi=int(pi)
   if pi not in PARAM:
    v.append(f'{vs}:{ps}: param{pi} outside registered interface');continue
   attrs.append({
     'ps_attr_index':int(x['attr_index']),
     'raw_gnm_semantic_id':int(x['semantic']),
     'vs_param_index':pi,
     **PARAM[pi],
   })
  rows.append({
    'vertex_shader':vs,'vertex_gcn_sha256':PROGRAMS[vs]['gcn_sha256'],
    'vertex_semantic_class':PROGRAMS[vs]['semantic_class'],
    'source_proof_status':PROGRAMS[vs]['source_proof_status'],
    'pixel_shader':ps,'consumed_attributes':attrs,
  })

 if not rows:v.append('no Crota registered VS linkage rows')
 # Critical procedural coordinate join.
 proc=[r for r in rows if r['pixel_shader']=='8108E955']
 proc_summary=[]
 for r in proc:
  a1=[x for x in r['consumed_attributes'] if x['ps_attr_index']==1]
  if len(a1)!=1:v.append(f"{r['vertex_shader']}:8108E955 attr1 row count {len(a1)}");continue
  q=a1[0]
  if q['vs_param_index']!=1 or q['semantic']!='TRANSFORMED_TANGENT_XYZ':
   v.append(f"{r['vertex_shader']}:8108E955 attr1 does not map to transformed tangent: {q}")
  proc_summary.append({
    'vertex_shader':r['vertex_shader'],'vertex_gcn_sha256':r['vertex_gcn_sha256'],
    'pixel_shader':'8108E955','ps_attr_index':1,'vs_param_index':1,
    'coordinate_source':'TRANSFORMED_TANGENT_XY',
    'raw_gnm_link_semantic_id':q['raw_gnm_semantic_id'],
  })
 if {x['vertex_shader'] for x in proc_summary}!={'809DE9AB','809DF743'}:
  v.append(f'8108E955 expected both Crota VS families, got {[x["vertex_shader"] for x in proc_summary]}')

 # Angular shaders all consume attr0/attr2; promote their shared vector roles too.
 angular=[]
 for r in rows:
  if r['pixel_shader'] not in {'8108E953','8108E955','8108E956','80AAE1CD','8108E958','8108E959'}:continue
  byattr={x['ps_attr_index']:x for x in r['consumed_attributes']}
  if 0 in byattr and 2 in byattr:
   if byattr[0]['semantic']!='TRANSFORMED_NORMAL_XYZ' or byattr[2]['semantic']!='HANDED_TRANSFORMED_BITANGENT_XYZ':
    v.append(f"{r['vertex_shader']}:{r['pixel_shader']}: angular basis semantic drift")
   angular.append({
     'vertex_shader':r['vertex_shader'],'pixel_shader':r['pixel_shader'],
     'attr0':'TRANSFORMED_NORMAL_XYZ','attr2':'HANDED_TRANSFORMED_BITANGENT_XYZ',
     'raw_semantic_ids':{'attr0':byattr[0]['raw_gnm_semantic_id'],'attr2':byattr[2]['raw_gnm_semantic_id']},
   })

 out={
  'schema':'d1_crota_vs_semantic_reuse/v1',
  'status':'D1_CROTA_VS_SEMANTIC_REUSE_EXACT' if not v else 'D1_CROTA_VS_SEMANTIC_REUSE_PARTIAL',
  'programs':PROGRAMS,'param_contract':PARAM,
  'link_rows':rows,
  'procedural_8108E955_attr1_coordinate':proc_summary,
  'angular_basis_rows':angular,
  'violations':v,
  'semantic_boundary':{
   'post_fetch_VS_interface':'EXACT_REUSED_BY_STAGE_PLUS_BOUNDED_GCN_SHA256',
   'PS_attr_to_VS_param':'EXACT_RAW_GNM_SEMANTIC_LINKAGE',
   '8108E955_t0_coordinate_first_two_lanes':'TRANSFORMED_TANGENT_XY',
   'angular_attr0':'TRANSFORMED_NORMAL_XYZ',
   'angular_attr2':'HANDED_TRANSFORMED_BITANGENT_XYZ',
   'fetch_shader_source_offsets_formats':'WITHHELD',
   'API11_API12_engine_names':'WITHHELD',
  },
  'policy':'Interface semantics are reused only because Crota resolves to the exact bounded GCN SHA registered by the prior source-closed VS proofs. Literal fetch layouts and global buffer names are not transferred.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'procedural':proc_summary,'angular':angular,'violations':v},indent=2))
 return 0 if out['status']=='D1_CROTA_VS_SEMANTIC_REUSE_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
