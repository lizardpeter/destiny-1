#!/usr/bin/env python3
"""Close seven remaining RGB-only Tower sky MRT0 families exactly.

These are source-material siblings or simple multiplicative families selected from
the exact 43-family Tower sky corpus.  Every row pins retail shader identity,
source material binding scope, terminal dependency leaves, and native arithmetic
anchors before emitting an algebraic terminal equation.

Equations are numerical/structural only.  No cloud/sun/fog/pass semantic is assigned.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

def norm(x): return str(x).upper().removeprefix('0X').zfill(8)

CFG={
'80AADBAA':{
 'freq':1,'native':'80AADBB8','native_sha':'1b4473003269b66adc355393db54e1e586e44a91ac9324cd016a5b89fa177beb',
 'gcn_sha':'68a61a8e61f5f6e31c488c474b21023095b27a7779eb93e9faf8a9f21a2a703f','gcn_bytes':160,
 'terminal':'000000000094','bindings':[0],
 'tex':{'R':[(0,'w'),(0,'x')],'G':[(0,'w'),(0,'y')],'B':[(0,'w'),(0,'z')]},
 'cb':{'R':{'0':[8,12],'13':[6,7]},'G':{'0':[9,12],'13':[6,7]},'B':{'0':[10,12],'13':[6,7]}},
 'eq':{
   'P':'t0.a * API0[12] * API13[6] * API13[7]',
   'mrt0_r':'t0.r * API0[8] * P','mrt0_g':'t0.g * API0[9] * P','mrt0_b':'t0.b * API0[10] * P','mrt0_a':'0'},
 'anchors':['v_mul_f32       v0, s8, v0','v_mul_f32       v1, s9, v1','v_mul_f32       v2, s10, v2',
            'v_mul_f32       v0, v3, v0','exp             mrt0']},
'80B9E853':{
 'freq':1,'native':'80B9E855','native_sha':'e562844d48d405427cc78c9f1698b20730de94131a5b1dbf9dca53dfbead685e',
 'gcn_sha':'c596efcbb5aaa760882b87c299c48d25fe98bb97cae28723ceea97c22a8b1ec1','gcn_bytes':288,
 'terminal':'000000000114','bindings':[0,1],
 'tex':{
  'R':[(0,'w'),(0,'x'),(1,'w'),(1,'x')],'G':[(0,'w'),(0,'y'),(1,'w'),(1,'y')],
  'B':[(0,'w'),(0,'z'),(1,'w'),(1,'z')]},
 'cb':{
  'R':{'0':[16,19,20,24],'13':[6,7]},'G':{'0':[17,19,21,24],'13':[6,7]},
  'B':{'0':[18,19,22,24],'13':[6,7]}},
 'eq':{
  'A0':'clamp(t0.a * t1.a * API0[19])',
  'P':'API0[24] * API13[6] * API13[7] * A0',
  'mrt0_r':'clamp(t0.r * t1.r * API0[16]) * API0[20] * P',
  'mrt0_g':'clamp(t0.g * t1.g * API0[17]) * API0[21] * P',
  'mrt0_b':'clamp(t0.b * t1.b * API0[18]) * API0[22] * P','mrt0_a':'0'},
 'anchors':['v_mul_f32       v0, v0, v4','v_mul_f32       v0, v0, s4 clamp',
            'v_mul_f32       v3, v3, s7 clamp','v_mul_f32       v0, v0, v3','exp             mrt0']},
'80B9EA21':{
 'freq':1,'native':'80B9EA3A','native_sha':'5fe9e8ac69203ebf5d41b67626dc9a44b84e18eea310dcd5e7ffb197679e3606',
 'gcn_sha':'fffe112b656bc87afcde9ba3e773845ffc1a7a5782a5f45bd2b6ff2ddd87d695','gcn_bytes':260,
 'terminal':'0000000000F8','bindings':[0,1],
 'tex':{
  'R':[(0,'w'),(0,'x'),(1,'w'),(1,'x')],'G':[(0,'w'),(0,'y'),(1,'w'),(1,'y')],
  'B':[(0,'w'),(0,'z'),(1,'w'),(1,'z')]},
 'cb':{
  'R':{'0':[8,11,16,20],'13':[6,7]},'G':{'0':[9,11,17,20],'13':[6,7]},
  'B':{'0':[10,11,18,20],'13':[6,7]}},
 'eq':{
  'A0':'t0.a * t1.a * API0[11]','P':'API0[20] * A0 * API13[6] * API13[7]',
  'mrt0_r':'t0.r * t1.r * API0[8] * API0[16] * P',
  'mrt0_g':'t0.g * t1.g * API0[9] * API0[17] * P',
  'mrt0_b':'t0.b * t1.b * API0[10] * API0[18] * P','mrt0_a':'0'},
 'anchors':['v_mul_f32       v3, v7, v3','v_mul_f32       v0, v4, v0',
            'v_mul_f32       v0, v0, v4','exp             mrt0']},
'80B9EA28':{
 'freq':1,'native':'80B9EA41','native_sha':'ae9b1c7ce3d6110e72c0aa897cf76cf96e317db5c8e539685226699e135accee',
 'gcn_sha':'628d0378816536209fb16fd48365b997fdbef38bcd36e37b66ac7faa5c1773bc','gcn_bytes':256,
 'terminal':'0000000000F4','bindings':[0,1],
 'tex':{
  'R':[(0,'w'),(0,'x'),(1,'w'),(1,'x')],'G':[(0,'w'),(0,'y'),(1,'w'),(1,'y')],
  'B':[(0,'w'),(0,'z'),(1,'w'),(1,'z')]},
 'cb':{
  'R':{'0':[12,15,16,20],'13':[6,7]},'G':{'0':[13,15,17,20],'13':[6,7]},
  'B':{'0':[14,15,18,20],'13':[6,7]}},
 'eq':{
  'A0':'t0.a * t1.a * API0[15]','P':'API0[20] * A0 * API13[6] * API13[7]',
  'mrt0_r':'t0.r * t1.r * API0[12] * API0[16] * P',
  'mrt0_g':'t0.g * t1.g * API0[13] * API0[17] * P',
  'mrt0_b':'t0.b * t1.b * API0[14] * API0[18] * P','mrt0_a':'0'},
 'anchors':['v_mul_f32       v3, v7, v3','v_mul_f32       v3, s15, v3',
            'v_mul_f32       v0, s12, v0','v_mul_f32       v0, v0, v4','exp             mrt0']},
'80B9F724':{
 'freq':1,'native':'80B9F73D','native_sha':'5d01dba8949df9c059836b061930e4a6eb9f8e1d68911ee168edaf889cf8c799',
 'gcn_sha':'d52bf19ed9e1a207b6b7842ac77f768f9ca36a6475416f85f802e6e267f00487','gcn_bytes':304,
 'terminal':'000000000124','bindings':[0,1],
 'tex':{'R':[(0,'x'),(1,'x')],'G':[(0,'x'),(1,'y')],'B':[(0,'x'),(1,'z')]},
 'cb':{
  'R':{'0':[8,12,16,20,24,28],'13':[6,7]},'G':{'0':[9,12,17,20,25,28],'13':[6,7]},
  'B':{'0':[10,12,18,20,26,28],'13':[6,7]}},
 'eq':{
  'K_r':'API0[8] + API0[12] * (t0.x - API0[8])',
  'K_g':'API0[9] + API0[12] * (t0.x - API0[9])',
  'K_b':'API0[10] + API0[12] * (t0.x - API0[10])',
  'P':'clamp(API0[20]) * API0[28] * API13[6] * API13[7]',
  'mrt0_r':'clamp(t1.r * API0[16] * K_r) * API0[24] * P',
  'mrt0_g':'clamp(t1.g * API0[17] * K_g) * API0[25] * P',
  'mrt0_b':'clamp(t1.b * API0[18] * K_b) * API0[26] * P','mrt0_a':'0'},
 'anchors':['v_mad_f32       v1, v2, s0, -v1','v_add_f32       v1, s8, v1',
            'v_mul_f32       v1, v2, v1 clamp','v_max_f32       v3, s0, s0 clamp','exp             mrt0']},
'80B9F985':{
 'freq':1,'native':'80B9F98B','native_sha':'e8095590de6660036c8f36fd5dbd2b34fe3bf08a53f60e21c177dfad5cdfa25a',
 'gcn_sha':'83c7137754111e7a2238f59ef23ebe71420a37c6e2e30aef1e5de420867deb15','gcn_bytes':400,
 'terminal':'000000000184','bindings':[0,1,2,3],
 'tex':{
  'R':[(0,'w'),(0,'x'),(1,'w'),(1,'x'),(2,'w'),(2,'x'),(3,'w'),(3,'x')],
  'G':[(0,'w'),(0,'y'),(1,'w'),(1,'y'),(2,'w'),(2,'y'),(3,'w'),(3,'y')],
  'B':[(0,'w'),(0,'z'),(1,'w'),(1,'z'),(2,'w'),(2,'z'),(3,'w'),(3,'z')]},
 'cb':{
  'R':{'0':[20,23,24,28],'13':[6,7]},'G':{'0':[21,23,25,28],'13':[6,7]},
  'B':{'0':[22,23,26,28],'13':[6,7]}},
 'eq':{
  'A0':'clamp(t0.a * t1.a * t2.a * API0[23] * t3.a)',
  'P':'API0[28] * API13[6] * API13[7] * A0',
  'mrt0_r':'clamp(t0.r * t1.r * t2.r * API0[20] * t3.r) * API0[24] * P',
  'mrt0_g':'clamp(t0.g * t1.g * t2.g * API0[21] * t3.g) * API0[25] * P',
  'mrt0_b':'clamp(t0.b * t1.b * t2.b * API0[22] * t3.b) * API0[26] * P','mrt0_a':'0'},
 'anchors':['v_mul_f32       v0, v8, v12','v_mul_f32       v0, v0, v3',
            'v_mul_f32       v0, v0, s4','v_mul_f32       v0, v0, v16 clamp',
            'v_mul_f32       v3, v3, v19 clamp','exp             mrt0']},
'80B9F71A':{
 'freq':1,'native':'80B9F734','native_sha':'6e56fe8ccc817eab868694467d4693d7a22eee137b3f86d819d1d1aa7fd7a0c1',
 'gcn_sha':'a380b59b4638afa0e382c55b6079262214b7dd7bf157495110492ed4d32e5420','gcn_bytes':232,
 'terminal':'0000000000DC','bindings':[0],
 'tex':{'R':[(0,'x')],'G':[(0,'y')],'B':[(0,'z')]},
 'cb':{
  'R':{'0':[12,16,20,24,28],'13':[6,7]},'G':{'0':[13,17,20,25,28],'13':[6,7]},
  'B':{'0':[14,18,20,26,28],'13':[6,7]}},
 'eq':{
  'P':'API0[20] * API0[28] * API13[6] * API13[7]',
  'mrt0_r':'t0.r * API0[12] * API0[16] * API0[24] * P',
  'mrt0_g':'t0.g * API0[13] * API0[17] * API0[25] * P',
  'mrt0_b':'t0.b * API0[14] * API0[18] * API0[26] * P','mrt0_a':'0'},
 'anchors':['v_mul_f32       v0, s12, v0','v_mul_f32       v0, s7, v0',
            'v_mul_f32       v0, s1, v0','v_mul_f32       v0, s0, v0',
            'v_mul_f32       v0, s2, v0','exp             mrt0']},
}

def zero_only(q):
 return q.get('literals')==['0'] and not q.get('texture_sample_channels') and not q.get('cbuffer_dwords') and not q.get('interpolants') and not q.get('unknown_registers')
def tex(q): return sorted((int(x['texture_index']),x['channel']) for x in q.get('texture_sample_channels',[]))
def cb(q): return {str(k):[int(x) for x in v] for k,v in sorted((q.get('cbuffer_dwords') or {}).items(),key=lambda kv:int(kv[0]))}

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
  if len(mm)!=cfg['freq']:errs.append(f"material row count {len(mm)} != {cfg['freq']}")
  for x in mm:
   inds=sorted(int(q['texture_index']) for q in (x.get('bindings') or []) if q.get('stage')=='ps')
   if inds!=cfg['bindings']:errs.append(f"material {x.get('material')} binding indices {inds} != {cfg['bindings']}")
  s=sby.get(sh)
  if not s:errs.append('shader report row missing')
  else:
   for k,z in [('native_shader',cfg['native']),('native_sha256',cfg['native_sha']),('gcn_sha256',cfg['gcn_sha']),('gcn_bytes',cfg['gcn_bytes'])]:
    if s.get(k)!=z:errs.append(f'{k} drift {s.get(k)!r} != {z!r}')
  t=tby.get(sh)
  if not t:errs.append('terminal row missing')
  else:
   if t.get('terminal_mrt0_export_address')!=cfg['terminal'] or not t.get('terminal_mrt0_compressed'):errs.append('terminal export drift')
   for ch in ('R','G','B'):
    q=t['channels'][ch]['value_slice']
    if tex(q)!=sorted(cfg['tex'][ch]):errs.append(f"{ch}: texture leaves {tex(q)} != {sorted(cfg['tex'][ch])}")
    if cb(q)!=cfg['cb'][ch]:errs.append(f"{ch}: cbuffer leaves {cb(q)} != {cfg['cb'][ch]}")
    if q.get('unknown_registers'):errs.append(f"{ch}: unknown leaves {q['unknown_registers']}")
   if not zero_only(t['channels']['A']['value_slice']):errs.append(f"A: expected zero-only {t['channels']['A']['value_slice']}")
  p=a.disasm_dir/f'PS_{sh}.s'
  if not p.exists():p=a.disasm_dir/f'PS_{sh}_GFX700.s'
  if not p.exists():errs.append('disassembly missing')
  else:
   txt=p.read_text(errors='replace')
   miss=[x for x in cfg['anchors'] if x not in txt]
   if miss:errs.append(f'missing native anchors {miss}')
  rows.append({'shader':sh,'visible_material_count':cfg['freq'],'gcn_sha256':cfg['gcn_sha'],
               'exact_terminal_equation':cfg['eq'],'violations':errs})
  v.extend(f'{sh}: {e}' for e in errs)
 out={
  'schema':'d1_tower_sky_rgb_sibling_mrt0_factorization/v1',
  'status':'D1_TOWER_SKY_RGB_SIBLING_MRT0_FACTORIZATION_EXACT' if len(rows)==len(CFG) and not v else 'D1_TOWER_SKY_RGB_SIBLING_MRT0_FACTORIZATION_PARTIAL',
  'shader_family_count':len(rows),'visible_material_count':sum(x['visible_material_count'] for x in rows),
  'visible_material_fraction':sum(x['visible_material_count'] for x in rows)/74,
  'rows':rows,'violations':v,
  'semantic_boundary':{
   'terminal_arithmetic':'EXACT_NATIVE_GCN_ALGEBRA',
   'serialized_material_resources':'EXACT_SOURCE_MATERIALS',
   'API13_live_values_and_producer':'WITHHELD',
   'sky_human_semantics':'WITHHELD',
   'portable_renderer_equivalence':'NOT_IMPLIED',
  },
  'policy':'Algebraic terminal equations are emitted only after exact identity, binding, leaf, zero-alpha, and native-anchor validation. Human sky roles and live API13 values remain withheld.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'families':len(rows),'materials':out['visible_material_count'],
                   'fraction':out['visible_material_fraction'],
                   'rows':[{'shader':x['shader'],'equation':x['exact_terminal_equation'],'violations':x['violations']} for x in rows],
                   'violations':v},indent=2))
 return 0 if out['status']=='D1_TOWER_SKY_RGB_SIBLING_MRT0_FACTORIZATION_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
