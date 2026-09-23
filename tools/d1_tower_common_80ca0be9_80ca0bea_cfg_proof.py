#!/usr/bin/env python3
"""Exact CFG-aware closure for Tower common sibling shaders 80CA0BE9/80CA0BEA.

The pair shares an identical nested lane selector. It constructs an exact geometric
scalar from API12[28:30] and interpolants, then selects one of three API0 coefficient
triplets according to two predicates. The selected scalar Q is squared and becomes
an input to either:
- 80CA0BEA: alpha-only MRT0;
- 80CA0BE9: RGB expansion plus alpha using API0[24:32] and API13[6:7].

No texture is serialized or sampled by either material. Human meanings for the
interpolants, coefficient banks, scalar Q, and render pass remain withheld.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

CFG={
'80CA0BE9':{
 'material':'80CA0BC6','native_shader':'80CA0BF7',
 'native_sha256':'ce904b9dc9e47fe09b413e902f6486eaa611c7401e5c2af71d8c60fdc4551819',
 'gcn_sha256':'86282025ea6bbe21ca42153702d14fbf443b5f2d605cf96f5f15d11663170b70',
 'gcn_bytes':480,'terminal':'0000000001D4',
 'api':{'0':[8,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32],
        '12':[28,29,30,31],'13':[6,7]},
 'anchors':['v_cmp_lt_f32    vcc, 1.0, v3','v_cmp_lt_f32    vcc, 0, v0',
            's_buffer_load_dwordx4 s[8:11], s[4:7], 0x10',
            's_buffer_load_dwordx4 s[8:11], s[4:7], 0x14',
            's_buffer_load_dwordx4 s[8:11], s[4:7], 0xc',
            'v_mad_f32       v1, s9, abs(v0), v1 clamp',
            'v_mul_f32       v0, v1, v1',
            's_buffer_load_dwordx4 s[0:3], s[4:7], 0x18',
            's_buffer_load_dword s8, s[4:7], 0x20',
            's_buffer_load_dwordx4 s[4:7], s[4:7], 0x1c',
            's_buffer_load_dwordx2 s[10:11], s[12:15], 0x6',
            'exp             mrt0, v2, v2, v0, v0 done compr vm'],
},
'80CA0BEA':{
 'material':'80CA0BC7','native_shader':'80CA0BF8',
 'native_sha256':'c7d99b384b4a0d5f2116793c2db2e1b37e4c8d7ae4ba5447241a172481bcf754',
 'gcn_sha256':'60767700462e51c3fe138fc1ee2786879d1f0d2937d827d3a2a8bc0972b9f64a',
 'gcn_bytes':412,'terminal':'000000000190',
 'api':{'0':[8,12,13,14,15,16,17,18,19,20,21,22,23,27],
        '12':[28,29,30,31]},
 'anchors':['v_cmp_lt_f32    vcc, 1.0, v3','v_cmp_lt_f32    vcc, 0, v0',
            's_buffer_load_dwordx4 s[8:11], s[4:7], 0x10',
            's_buffer_load_dwordx4 s[8:11], s[4:7], 0x14',
            's_buffer_load_dwordx4 s[8:11], s[4:7], 0xc',
            'v_mad_f32       v1, s9, abs(v0), v1 clamp',
            'v_mul_f32       v0, v1, v1',
            's_buffer_load_dword s0, s[4:7], 0x1b',
            'exp             mrt0, v2, v2, v0, v0 done compr vm'],
},
}

COMMON={
 'D':'normalize_legacy((API12[28]-attr4.x, API12[29]-attr4.y, API12[30]-attr4.z))',
 'B0':'dot(D,attr0.xyz)',
 'B1':'dot(D,attr1.xyz)',
 'B2':'dot(D,attr2.xyz)',
 'Y':'mad(neg(mul(API0[8],B2)),rcp(B0),attr3.y)',
 'X':'mad(neg(mul(API0[8],B1)),rcp(B0),attr3.x)',
 'outer_predicate':'gt(Y,1)',
 'inner_predicate':'gt(X,0)',
 'Q_outer_inner':'square(clamp(mad(API0[17],abs(add(API0[18],Y)),API0[16])))',
 'Q_outer_else':'square(clamp(mad(API0[21],abs(add(API0[22],Y)),API0[20])))',
 'Q_else':'square(clamp(mad(API0[13],abs(add(API0[14],Y)),API0[12])))',
 'Q':'select(gt(Y,1),select(gt(X,0),Q_outer_inner,Q_outer_else),Q_else)',
}
OUT={
'80CA0BEA':{
 'MRT0.rgb':'(0,0,0)',
 'MRT0.a':'mul(API0[27],Q)',
},
'80CA0BE9':{
 'A':'mul(API0[27],Q)',
 'G':'mul(mul(API13[6],API13[7]),A)',
 'MRT0.r':'mul(mul(API0[24],Q),mul(API0[28],API0[32]),G)',
 'MRT0.g':'mul(mul(API0[25],Q),mul(API0[29],API0[32]),G)',
 'MRT0.b':'mul(mul(API0[26],Q),mul(API0[30],API0[32]),G)',
 'MRT0.a':'A',
},
}

def main():
 ap=argparse.ArgumentParser()
 for n in ('manifest','shader-report','image-usage','cbuffer-usage','disasm-dir','out'):
  ap.add_argument('--'+n,type=Path,required=True)
 a=ap.parse_args()
 m=json.loads(a.manifest.read_text());sr=json.loads(a.shader_report.read_text())
 iu=json.loads(a.image_usage.read_text());cb=json.loads(a.cbuffer_usage.read_text())
 v=[];rows=[]
 if m.get('status')!='D1_WORLD_VISIBLE_MATERIAL_TEXTURE_EXPORT' or m.get('material_decode_errors') or m.get('texture_errors'):v.append('manifest not exact')
 if sr.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or sr.get('error_count'):v.append('shader report not exact')
 if iu.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':v.append('image usage not exact')
 if cb.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or cb.get('missing_usage'):v.append('cbuffer usage not exact')
 sby={norm(x['shader']):x for x in sr.get('shaders',[])};iby={norm(x['shader']):x for x in iu.get('shaders',[])};cby={norm(x['shader']):x for x in cb.get('shaders',[])}
 mats=m.get('materials') or {};freq={norm(k):int(x) for k,x in (m.get('pixel_shader_frequency') or {}).items()}
 for sh,cfg in CFG.items():
  e=[];s=sby.get(sh);i=iby.get(sh);c=cby.get(sh)
  if freq.get(sh)!=1:e.append(f'frequency {freq.get(sh)} != 1')
  mm=[(norm(k),x) for k,x in mats.items() if norm(x.get('pixel_shader'))==sh]
  if len(mm)!=1:e.append(f'material row count {len(mm)} != 1')
  else:
   mh,mr=mm[0]
   if mh!=cfg['material']:e.append(f'material {mh} != {cfg["material"]}')
   binds=[x for x in (mr.get('bindings') or []) if x.get('stage')=='ps']
   if binds:e.append(f'expected no serialized PS texture bindings, got {binds}')
  if not s:e.append('shader row missing')
  else:
   for k,w in [('native_shader',cfg['native_shader']),('native_sha256',cfg['native_sha256']),('gcn_sha256',cfg['gcn_sha256']),('gcn_bytes',cfg['gcn_bytes'])]:
    if s.get(k)!=w:e.append(f'{k} drift {s.get(k)!r} != {w!r}')
  if not i:e.append('image usage row missing')
  elif i.get('image_instruction_count')!=0 or i.get('used_texture_indices')!=[]:e.append(f'unexpected image usage {i}')
  if not c:e.append('cbuffer row missing')
  else:
   got={str(k):[int(z) for z in q] for k,q in (c.get('api_slot_read_dwords') or {}).items()}
   if got!=cfg['api']:e.append(f'cbuffer read set {got} != {cfg["api"]}')
   if c.get('unresolved_load_count')!=0:e.append('unresolved cbuffer load')
  p=a.disasm_dir/f'PS_{sh}.s'
  if not p.exists():p=a.disasm_dir/f'PS_{sh}_GFX700.s'
  txt=p.read_text(errors='replace') if p.exists() else ''
  miss=[x for x in cfg['anchors'] if x not in txt]
  if miss:e.append(f'missing native anchors {miss}')
  rows.append({'shader':sh,'visible_material_count':1,'material':cfg['material'],
               'native_shader':cfg['native_shader'],'gcn_sha256':cfg['gcn_sha256'],
               'common_cfg_equation':COMMON,'terminal_equation':OUT[sh],
               'terminal_mrt0_export_address':cfg['terminal'],'violations':e})
  v.extend(f'{sh}: {x}' for x in e)
 out={'schema':'d1_tower_common_80ca0be9_80ca0bea_cfg_proof/v1',
      'status':'D1_TOWER_COMMON_80CA0BE9_80CA0BEA_CFG_PROOF_EXACT' if len(rows)==2 and not v else 'D1_TOWER_COMMON_80CA0BE9_80CA0BEA_CFG_PROOF_PARTIAL',
      'shader_family_count':len(rows),'visible_material_count':2,'rows':rows,'violations':v,
      'semantic_boundary':{
       'nested_lane_selector':'EXACT_NATIVE_GCN_STRUCTURE',
       'coefficient_banks':'EXACT_API_SLOT_DWORD_IDENTITY_HUMAN_MEANING_WITHHELD',
       'terminal_equations':'EXACT_OPERATION_PRESERVING_CFG_REDUCTION',
       'texture_inputs':'NONE_SERIALIZED_OR_SAMPLED',
       'API13_product':'EXACT_SHADER_INPUT_IDENTITY_PRODUCER_LIVE_VALUE_WITHHELD',
       'human_pass_semantics':'WITHHELD'},
      'policy':'The branch-selected scalar Q and terminal equations are preserved as native operation structure. Coefficient and interpolant meanings remain unnamed.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'rows':rows,'violations':v},indent=2))
 return 0 if out['status'].endswith('_EXACT') else 2
if __name__=='__main__':raise SystemExit(main())
