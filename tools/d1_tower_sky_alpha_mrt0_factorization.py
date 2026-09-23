#!/usr/bin/env python3
"""Close the next exact alpha-only Tower sky MRT0 families.

Covers eleven native pixel-shader families accounting for 12/74 visible sky
material rows. Each equation is validated against pinned retail shader identity,
source material binding scope, exact terminal value leaves, and native instruction
anchors.

The output remains numerical/structural only; no mask/attenuation/cloud semantic
is assigned to alpha.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

CFG={
'80B9F729':{
 'freq':2,'native':'80B9F742','native_sha':'96152b90823208574756b425d0bc99dfe5589724aebea4cb85fa997a3bf843e1',
 'gcn_sha':'0329f6184d5485826edfdd65a0011554a9a866e1d1e67fd779818ce3d0af410d','gcn_bytes':184,'terminal':'0000000000AC',
 'bindings':[0,1,2],'tex':[(0,'x'),(1,'x'),(2,'x')],'cb':{},'eq':'t0.x * t1.x * t2.x',
 'anchors':['v_mul_f32       v0, v0, v1','v_mul_f32       v0, v2, v0']},
'80AAE110':{
 'freq':1,'native':'80AAE173','native_sha':'3e4f4de9a0d636f99c7a01f5211458465dd736d1071432d14f343b0ac8551b26',
 'gcn_sha':'55e173215b4d9a1bdef4ff503e341a0a6cef2fb81cdd02a92183c00ea580a6f1','gcn_bytes':84,'terminal':'000000000048',
 'bindings':[0],'tex':[(0,'w')],'cb':{},'eq':'t0.a',
 'anchors':['image_sample    v0, v[0:3], s[4:11], s[12:15] dmask:8']},
'80B9E854':{
 'freq':1,'native':'80B9E856','native_sha':'3bac5e40967492c1e5ed0c9c905f907a65dc55e822eb0159630e777f4b5bb826',
 'gcn_sha':'76887cb04f474cddfa240148d23f12ee5a45f144f3cc5c4d279c9adbc06b3761','gcn_bytes':180,'terminal':'0000000000A8',
 'bindings':[0,1],'tex':[(0,'w'),(1,'w')],'cb':{'0':[19]},'eq':'clamp(API0[19] * t0.a * t1.a)',
 'anchors':['v_mul_f32       v0, v0, v1','v_mul_f32       v0, v0, s0 clamp']},
'80B9EA22':{
 'freq':1,'native':'80B9EA3B','native_sha':'0bae98e9e4afe7a943593e0cbd5e264635bd2fbb7e8b605d676dbe2452d81caf',
 'gcn_sha':'7e31ce92ba3d492b7e25e6034427a1b7c019a743b2af8ee66cd4563f42710ca1','gcn_bytes':144,'terminal':'000000000084',
 'bindings':[0,1],'tex':[(0,'w'),(1,'w')],'cb':{'0':[11]},'eq':'API0[11] * t0.a * t1.a',
 'anchors':['v_mul_f32       v0, s0, v0','v_mul_f32       v0, v0, v1']},
'80B9EA2C':{
 'freq':1,'native':'80B9EA45','native_sha':'c776b92de8a46361dbe9af712fed35bdd741ae81e8b00936593e3b9225429b50',
 'gcn_sha':'6055fa4ddf6dc67e890a67ede03faf1f534f8279f6bbe0e5aaa1976d36e7fff9','gcn_bytes':152,'terminal':'00000000008C',
 'bindings':[0,1,2],'tex':[(1,'x'),(2,'x')],'cb':{'0':[11]},'eq':'API0[11] * t1.x * t2.x',
 'anchors':['v_mul_f32       v0, v1, v0','v_mul_f32       v0, s0, v0']},
'80B9EA2D':{
 'freq':1,'native':'80B9EA46','native_sha':'55154436d06b530926090c0c47971393e6f218cee67b3c7ba6caf88c6f8552a8',
 'gcn_sha':'39c51c063774b14e18286f5bbfa950cdbd5731c7fd1f2e73c6e6898523f654f6','gcn_bytes':144,'terminal':'000000000084',
 'bindings':[0,1],'tex':[(0,'w'),(1,'w')],'cb':{'0':[15]},'eq':'API0[15] * t0.a * t1.a',
 'anchors':['v_mul_f32       v0, v0, v1','v_mul_f32       v0, s0, v0']},
'80B9F71C':{
 'freq':1,'native':'80B9F736','native_sha':'da1aaa65d0cfabbbc7ef5d55bd045af24123436122a31bedb69f62d57047ba99',
 'gcn_sha':'752c7b38c7048055733da531d5f7d5adf4dcba83d15d9f60d956008521edd689','gcn_bytes':44,'terminal':'000000000020',
 'bindings':[],'tex':[],'cb':{'0':[20]},'eq':'API0[20]',
 'anchors':['s_buffer_load_dword s0, s[4:7], 0x14','v_mov_b32       v1, s0']},
'80B9F725':{
 'freq':1,'native':'80B9F73E','native_sha':'cb868afdef6d04083b8f104eae1124f843a6f81aed98dee6b2479240d7fbddde',
 'gcn_sha':'c422fc8d6ad0109cd5f7b5a02b19d29befc3ab5cbf8935dcb911ba567520184d','gcn_bytes':48,'terminal':'000000000024',
 'bindings':[0,1],'tex':[],'cb':{'0':[20]},'eq':'clamp(API0[20])',
 'anchors':['s_buffer_load_dword s0, s[4:7], 0x14','v_max_f32       v0, s0, s0 clamp']},
'80B9F986':{
 'freq':1,'native':'80B9F98C','native_sha':'e94c579fa5ddb9ac34152deeca0556cdd13a3ad9cc650f7f40d403cf794099a2',
 'gcn_sha':'7fb46ab45cb0cae0193a8be08f0a9cc4f1873071f741b8062d3f31a8b14926fd','gcn_bytes':264,'terminal':'0000000000FC',
 'bindings':[0,1,2,3],'tex':[(0,'w'),(1,'w'),(2,'w'),(3,'w')],'cb':{'0':[23]},
 'eq':'clamp(API0[23] * t0.a * t1.a * t2.a * t3.a)',
 'anchors':['v_mul_f32       v1, v1, v3','v_mul_f32       v1, v1, v4','v_mul_f32       v1, s0, v1','v_mul_f32       v0, v1, v0 clamp']},
'80B9FC89':{
 'freq':1,'native':'80B9FC8D','native_sha':'7d9690c3e923c4f5c72d97c30a84388e3089842c3b9f63a9a515c6aedcedccb1',
 'gcn_sha':'2f6d179a329d9d7561993b15e02fb96e0e3985bae645d2c32ded6f50a12755db','gcn_bytes':128,'terminal':'000000000074',
 'bindings':[0],'tex':[(0,'w')],'cb':{'0':[11]},'eq':'API0[11] * t0.a',
 'anchors':['image_sample    v0, v[0:3], s[4:11], s[12:15] dmask:8','v_mul_f32       v0, s0, v0']},
'80B9EA15':{
 'freq':1,'native':'80B9EA30','native_sha':'82250677f86a928d254aa9948c33924114831646e3183eebb94e789d71615613',
 'gcn_sha':'01d5239f4ccb4340045ec42023147196328b787bbe8add3715b048e03cb5e03a','gcn_bytes':220,'terminal':'0000000000D0',
 'bindings':[0,1,2],'tex':[(0,'w'),(1,'x'),(2,'w')],'cb':{'0':[27]},
 'eq':'API0[27] * t0.a * t1.x * t2.a',
 'anchors':['v_mul_f32       v0, v0, v1','v_mul_f32       v0, s4, v0','v_mul_f32       v0, v3, v0']},
}

def zero_only(q):
 return q.get('literals')==['0'] and not q.get('texture_sample_channels') and not q.get('cbuffer_dwords') and not q.get('interpolants') and not q.get('unknown_registers')
def tex(q):return sorted((int(x['texture_index']),x['channel']) for x in q.get('texture_sample_channels',[]))
def cb(q):return {str(k):[int(x) for x in v] for k,v in sorted((q.get('cbuffer_dwords') or {}).items(),key=lambda kv:int(kv[0]))}

def main():
 ap=argparse.ArgumentParser()
 for n in ('material-manifest','shader-report','terminal-mrt0','disasm-dir','out'):
  ap.add_argument('--'+n,type=Path,required=True)
 a=ap.parse_args()
 m=json.loads(a.material_manifest.read_text());sr=json.loads(a.shader_report.read_text());tm=json.loads(a.terminal_mrt0.read_text())
 v=[];rows=[]
 if m.get('status')!='D1_WORLD_VISIBLE_MATERIAL_TEXTURE_EXPORT' or m.get('material_decode_errors') or m.get('texture_errors'):v.append('material manifest not exact')
 if sr.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or sr.get('error_count'):v.append('shader report not exact')
 if tm.get('status')!='D1_GCN_TERMINAL_MRT0_DEPENDENCY_CENSUS_EXACT' or tm.get('violations'):v.append('terminal MRT0 not exact')
 sby={norm(x['shader']):x for x in sr.get('shaders',[])};tby={norm(x['shader']):x for x in tm.get('shaders',[])}
 freq={norm(k):int(x) for k,x in (m.get('pixel_shader_frequency') or {}).items()};mats=m.get('materials') or {}
 for sh,cfg in CFG.items():
  errs=[]
  if freq.get(sh)!=cfg['freq']:errs.append(f"frequency {freq.get(sh)} != {cfg['freq']}")
  mm=[x for x in mats.values() if norm(x.get('pixel_shader'))==sh]
  if len(mm)!=cfg['freq']:errs.append('material row count drift')
  for x in mm:
   inds=sorted(int(q['texture_index']) for q in (x.get('bindings') or []) if q.get('stage')=='ps')
   if inds!=cfg['bindings']:errs.append(f'binding index drift {inds} != {cfg["bindings"]}')
  s=sby.get(sh)
  if not s:errs.append('shader report row missing')
  else:
   for k,z in [('native_shader',cfg['native']),('native_sha256',cfg['native_sha']),('gcn_sha256',cfg['gcn_sha']),('gcn_bytes',cfg['gcn_bytes'])]:
    if s.get(k)!=z:errs.append(f'{k} drift {s.get(k)!r} != {z!r}')
  t=tby.get(sh)
  if not t:errs.append('terminal row missing')
  else:
   if t.get('terminal_mrt0_export_address')!=cfg['terminal'] or not t.get('terminal_mrt0_compressed'):errs.append('terminal identity drift')
   for ch in ('R','G','B'):
    if not zero_only(t['channels'][ch]['value_slice']):errs.append(f'{ch}: not exact zero-only')
   aq=t['channels']['A']['value_slice']
   if tex(aq)!=sorted(cfg['tex']):errs.append(f'alpha texture leaves {tex(aq)} != {sorted(cfg["tex"])}')
   if cb(aq)!=cfg['cb']:errs.append(f'alpha cbuffer leaves {cb(aq)} != {cfg["cb"]}')
   if aq.get('unknown_registers'):errs.append(f'alpha unknown leaves {aq["unknown_registers"]}')
  p=a.disasm_dir/f'PS_{sh}.s'
  if not p.exists():p=a.disasm_dir/f'PS_{sh}_GFX700.s'
  if not p.exists():errs.append('disassembly missing')
  else:
   txt=p.read_text(errors='replace');miss=[x for x in cfg['anchors'] if x not in txt]
   if miss:errs.append(f'missing native anchors {miss}')
  rows.append({'shader':sh,'visible_material_count':cfg['freq'],'exact_terminal_equation':{'mrt0_rgb':'0','mrt0_a':cfg['eq']},'violations':errs})
  v.extend(f'{sh}: {x}' for x in errs)
 out={
  'schema':'d1_tower_sky_alpha_mrt0_factorization/v1',
  'status':'D1_TOWER_SKY_ALPHA_MRT0_FACTORIZATION_EXACT' if len(rows)==len(CFG) and not v else 'D1_TOWER_SKY_ALPHA_MRT0_FACTORIZATION_PARTIAL',
  'shader_family_count':len(rows),'visible_material_count':sum(x['visible_material_count'] for x in rows),
  'visible_material_fraction':sum(x['visible_material_count'] for x in rows)/74,
  'rows':rows,'violations':v,
  'semantic_boundary':{'terminal_arithmetic':'EXACT_NATIVE_GCN','alpha_human_semantic':'WITHHELD','sky_pass_role':'WITHHELD'},
  'policy':'Exact terminal alpha arithmetic only. Alpha is not labeled mask/attenuation/cloud/transparency without independent evidence.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'families':len(rows),'materials':out['visible_material_count'],'fraction':out['visible_material_fraction'],'rows':rows,'violations':v},indent=2))
 return 0 if out['status']=='D1_TOWER_SKY_ALPHA_MRT0_FACTORIZATION_EXACT' else 2
if __name__=='__main__':raise SystemExit(main())
