#!/usr/bin/env python3
"""Close high-coverage Tower sky terminal MRT0 equations.

This proof covers nine exact native pixel-shader families accounting for 35/74
visible Tower sky material rows. It validates retail shader identity, serialized
material t# scope, exact image/cbuffer provenance, terminal value leaves, native
instruction anchors, and then emits source-faithful terminal equations.

No human sky/pass semantics are assigned.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

def norm(x): return str(x).upper().removeprefix('0X').zfill(8)

CFG={
'80B9F981':{
 'freq':6,'native':'80B9F987','native_sha':'a7102cfb9947128d3f55f5bc07a3193b7430affc42359eb12d3e937638a49d95',
 'gcn_sha':'0e9550d83707d6e9b21c3ab6339774ab3c24ad2a9ee723b8d0937a7fc718738d','gcn_bytes':348,
 'mode':'RGB_TRIPLE_SAMPLE','terminal':'000000000150','bindings':[0,1,2],
 'anchors':['v_mul_f32       v4, v9, v13','v_mul_f32       v3, v4, v3','v_mul_f32       v0, s16, v0','v_mul_f32       v4, v3, v4','v_mul_f32       v0, v0, v4'],
},
'80B9F983':{
 'freq':1,'native':'80B9F989','native_sha':'fac2e0ddedd583b8185da4b80eb74c32e791dd7dfa72a75bf64a9b429c90207e',
 'gcn_sha':'4bc4ca5ad058554b4b1cccd094550f24a45bc3a4dc2d00c7ec939172b78ca6d7','gcn_bytes':332,
 'mode':'RGB_TRIPLE_SAMPLE','terminal':'000000000140','bindings':[0,1,2],
 'anchors':['v_mul_f32       v3, v9, v3','v_mul_f32       v3, v3, v13','v_mul_f32       v0, s16, v0','v_mul_f32       v5, v3, v5','v_mul_f32       v0, v0, v5'],
},
'80B9F982':{
 'freq':6,'native':'80B9F988','native_sha':'51f12b9e3142c3b3401d8fe502d591d752b8c093d2ba147ae884245b5d591e25',
 'gcn_sha':'52a8a33c32111d3904d1b05c0e2c787e69f24db2a4b9aeeed91608642117f39b','gcn_bytes':216,
 'mode':'ALPHA_TRIPLE_SAMPLE','terminal':'0000000000CC','bindings':[0,1,2],
 'anchors':['v_mul_f32       v1, v1, v3','v_mul_f32       v0, v1, v0','v_mul_f32       v0, s0, v0','v_mul_f32       v0, s1, v0'],
},
'80B9F984':{
 'freq':1,'native':'80B9F98A','native_sha':'79e28a51c78ac003c385397e60adde8b34a72b7dfba4d86bd7e3d1525b2e3b73',
 'gcn_sha':'0359b911da85cb45a46a08ee79be82f319b7a4b09b28c2253a97d1dbd0641b22','gcn_bytes':212,
 'mode':'ALPHA_TRIPLE_SAMPLE','terminal':'0000000000C8','bindings':[0,1,2],
 'anchors':['v_mul_f32       v0, v1, v0','v_mul_f32       v0, v0, v2','v_mul_f32       v0, s0, v0','v_mul_f32       v0, s1, v0'],
},
'80B9F3E3':{
 'freq':5,'native':'80AA9B12','native_sha':'d6e08453466d59e03354fd921a2e9293c6d3c1a68872b2742118efae77ce8019',
 'gcn_sha':'dc0a20e87786570191f752a33ad113945bd13e21aa35b19ad6ba951de430670d','gcn_bytes':220,
 'mode':'RGB_SINGLE_SAMPLE_A','terminal':'0000000000D0','bindings':[0],
 'anchors':['v_mul_f32       v3, s15, v3','v_mul_f32       v0, s12, v0','v_mul_f32       v5, v3, v5','v_mul_f32       v0, v0, v5'],
},
'80AD2939':{
 'freq':4,'native':'80AAE1FA','native_sha':'a833db46604916f5b8c2d210a0a23ab36d607441220b847bac488d05ccb11f07',
 'gcn_sha':'c207d2732a4b30b8b75116a392d56180356da1f3dbc8147492198b9b674319fc','gcn_bytes':188,
 'mode':'RGB_SINGLE_SAMPLE_B','terminal':'0000000000B0','bindings':[0],
 'anchors':['v_mul_f32       v3, s7, v3','v_mul_f32       v0, s4, v0','v_mul_f32       v5, v3, v5','v_mul_f32       v0, v0, v5'],
},
'80BA2CA6':{
 'freq':5,'native':'80AAE1FF','native_sha':'bc5134f64a5c10d84e77b1e54f600880b985c62a17b3aece0581d109af46f0fd',
 'gcn_sha':'76d7b03c4a4d42eaf99e7c90a5fb78a99e7f537a91c0fed8b34485474678af32','gcn_bytes':100,
 'mode':'ALPHA_SINGLE_T0W','terminal':'000000000058','bindings':[0],
 'anchors':['image_sample    v0, v[0:3], s[4:11], s[12:15] dmask:8','v_mul_f32       v0, s0, v0'],
},
'80BA231C':{
 'freq':5,'native':'80AA9F01','native_sha':'1b673ff24f52121c1436c8115ec3ada4c0f5cc989645d70cf0fd419c1f575d19',
 'gcn_sha':'3a022151e99e34bed0faae568635aec1d619280b21ef30997446b767f77e1316','gcn_bytes':120,
 'mode':'ALPHA_SINGLE_T0W','terminal':'00000000006C','bindings':[0],
 'anchors':['image_sample    v0, v[1:4], s[4:11], s[12:15] dmask:8','v_mul_f32       v0, s0, v0'],
},
'80B9F776':{
 'freq':2,'native':'80B9F777','native_sha':'e411edf5bf6f696b1484d6840a2d4883906647411a15251029d27632adfe8144',
 'gcn_sha':'cb79a91e0a8924eaa7fe8b35ded81c6c7d7d64d1f1b54a4e9afbe2f4718d32fe','gcn_bytes':100,
 'mode':'ALPHA_SINGLE_T1X','terminal':'000000000058','bindings':[0,1],
 'anchors':['image_sample    v0, v[0:3], s[4:11], s[12:15]','v_mul_f32       v0, s0, v0'],
},
}

def zero_only(q):
 return q.get('literals')==['0'] and not q.get('texture_sample_channels') and not q.get('cbuffer_dwords') and not q.get('interpolants') and not q.get('unknown_registers')

def texleaves(q):
 return {(int(x['texture_index']),x['channel']) for x in q.get('texture_sample_channels',[])}

def cbuf(q):
 return {str(k):set(int(x) for x in v) for k,v in (q.get('cbuffer_dwords') or {}).items()}

def expected(mode,ch):
 if mode=='ALPHA_TRIPLE_SAMPLE':
  return ({(0,'w'),(1,'w'),(2,'w')},{'0':{19,23}}) if ch=='A' else (set(),{})
 if mode=='RGB_TRIPLE_SAMPLE':
  if ch=='A':return set(),{}
  lane={'R':'x','G':'y','B':'z'}[ch]; ci={'R':(16,20,24),'G':(17,21,25),'B':(18,22,26)}[ch]
  return ({(0,lane),(1,lane),(2,lane),(0,'w'),(1,'w'),(2,'w')},{'0':set(ci)|{19,23,28},'13':{6,7}})
 if mode=='RGB_SINGLE_SAMPLE_A':
  if ch=='A':return set(),{}
  lane={'R':'x','G':'y','B':'z'}[ch]; ci={'R':(8,16),'G':(9,17),'B':(10,18)}[ch]
  return ({(0,lane),(0,'w')},{'0':set(ci)|{11,20},'13':{6,7}})
 if mode=='RGB_SINGLE_SAMPLE_B':
  if ch=='A':return set(),{}
  lane={'R':'x','G':'y','B':'z'}[ch]; ci={'R':(8,12),'G':(9,13),'B':(10,14)}[ch]
  return ({(0,lane),(0,'w')},{'0':set(ci)|{11,16},'13':{6,7}})
 if mode=='ALPHA_SINGLE_T0W':
  return ({(0,'w')},{'0':{11}}) if ch=='A' else (set(),{})
 if mode=='ALPHA_SINGLE_T1X':
  return ({(1,'x')},{'0':{11}}) if ch=='A' else (set(),{})
 raise ValueError(mode)

def equation(mode):
 if mode=='ALPHA_TRIPLE_SAMPLE':
  return {'mrt0_rgb':'0','mrt0_a':'API0[19] * API0[23] * t0.a * t1.a * t2.a'}
 if mode=='RGB_TRIPLE_SAMPLE':
  return {
   'P':'t0.a * t1.a * t2.a * API0[19] * API0[23] * API0[28] * API13[6] * API13[7]',
   'mrt0_r':'t0.r * t1.r * t2.r * API0[16] * API0[20] * API0[24] * P',
   'mrt0_g':'t0.g * t1.g * t2.g * API0[17] * API0[21] * API0[25] * P',
   'mrt0_b':'t0.b * t1.b * t2.b * API0[18] * API0[22] * API0[26] * P','mrt0_a':'0'}
 if mode=='RGB_SINGLE_SAMPLE_A':
  return {
   'P':'t0.a * API0[11] * API0[20] * API13[6] * API13[7]',
   'mrt0_r':'t0.r * API0[8] * API0[16] * P','mrt0_g':'t0.g * API0[9] * API0[17] * P',
   'mrt0_b':'t0.b * API0[10] * API0[18] * P','mrt0_a':'0'}
 if mode=='RGB_SINGLE_SAMPLE_B':
  return {
   'P':'t0.a * API0[11] * API0[16] * API13[6] * API13[7]',
   'mrt0_r':'t0.r * API0[8] * API0[12] * P','mrt0_g':'t0.g * API0[9] * API0[13] * P',
   'mrt0_b':'t0.b * API0[10] * API0[14] * P','mrt0_a':'0'}
 if mode=='ALPHA_SINGLE_T0W':return {'mrt0_rgb':'0','mrt0_a':'API0[11] * t0.a'}
 if mode=='ALPHA_SINGLE_T1X':return {'mrt0_rgb':'0','mrt0_a':'API0[11] * t1.x'}
 raise ValueError(mode)

def main():
 ap=argparse.ArgumentParser()
 for n in ('material-manifest','shader-report','image-usage','cbuffer-usage','terminal-mrt0','disasm-dir','out'):
  ap.add_argument('--'+n,type=Path,required=True)
 a=ap.parse_args()
 m=json.loads(a.material_manifest.read_text());sr=json.loads(a.shader_report.read_text())
 iu=json.loads(a.image_usage.read_text());cb=json.loads(a.cbuffer_usage.read_text());tm=json.loads(a.terminal_mrt0.read_text())
 v=[];rows=[]
 if m.get('status')!='D1_WORLD_VISIBLE_MATERIAL_TEXTURE_EXPORT' or m.get('material_decode_errors') or m.get('texture_errors'):v.append('material manifest not exact')
 if sr.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or sr.get('error_count'):v.append('shader report not exact')
 if iu.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':v.append('image usage not exact')
 if cb.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or cb.get('missing_usage'):v.append('cbuffer usage not exact')
 if tm.get('status')!='D1_GCN_TERMINAL_MRT0_DEPENDENCY_CENSUS_EXACT':v.append('terminal MRT0 not exact')
 sby={norm(x['shader']):x for x in sr.get('shaders',[])}; iby={norm(x['shader']):x for x in iu.get('shaders',[])}
 cby={norm(x['shader']):x for x in cb.get('shaders',[])}; tby={norm(x['shader']):x for x in tm.get('shaders',[])}
 freq={norm(k):int(x) for k,x in (m.get('pixel_shader_frequency') or {}).items()}
 mats=m.get('materials') or {}
 for sh,cfg in CFG.items():
  errs=[]
  if freq.get(sh)!=cfg['freq']:errs.append(f"material frequency {freq.get(sh)} != {cfg['freq']}")
  mm=[x for x in mats.values() if norm(x.get('pixel_shader'))==sh]
  if len(mm)!=cfg['freq']:errs.append(f'material row count {len(mm)} != {cfg["freq"]}')
  for x in mm:
   inds=sorted(int(q['texture_index']) for q in (x.get('bindings') or []) if q.get('stage')=='ps')
   if inds!=cfg['bindings']:errs.append(f'material {x.get("material")} binding indices {inds} != {cfg["bindings"]}')
  s=sby.get(sh)
  if not s:errs.append('shader report row missing')
  else:
   for k,z in [('native_shader',cfg['native']),('native_sha256',cfg['native_sha']),('gcn_sha256',cfg['gcn_sha']),('gcn_bytes',cfg['gcn_bytes'])]:
    if s.get(k)!=z:errs.append(f'{k} drift {s.get(k)!r} != {z!r}')
  t=tby.get(sh)
  if not t:errs.append('terminal row missing')
  else:
   if t.get('terminal_mrt0_export_address')!=cfg['terminal'] or not t.get('terminal_mrt0_compressed'):errs.append('terminal export drift')
   for ch in ('R','G','B','A'):
    q=t['channels'][ch]['value_slice']; et,ec=expected(cfg['mode'],ch)
    if ch!='A' and cfg['mode'].startswith('ALPHA_'):
     if not zero_only(q):errs.append(f'{ch}: expected exact zero-only output {q}')
     continue
    if ch=='A' and cfg['mode'].startswith('RGB_'):
     if not zero_only(q):errs.append(f'A: expected exact zero-only output {q}')
     continue
    if texleaves(q)!=et:errs.append(f'{ch}: texture leaves {sorted(texleaves(q))} != {sorted(et)}')
    got=cbuf(q)
    if got!=ec:errs.append(f'{ch}: cbuffer leaves {got} != {ec}')
    if q.get('unknown_registers'):errs.append(f'{ch}: unknown leaves {q["unknown_registers"]}')
  p=a.disasm_dir/f'PS_{sh}.s'
  if not p.exists():p=a.disasm_dir/f'PS_{sh}_GFX700.s'
  if not p.exists():errs.append('disassembly missing')
  else:
   txt=p.read_text(errors='replace')
   miss=[x for x in cfg['anchors'] if x not in txt]
   if miss:errs.append(f'missing native anchors {miss}')
  rows.append({'shader':sh,'visible_material_count':cfg['freq'],'mode':cfg['mode'],
               'gcn_sha256':cfg['gcn_sha'],'exact_terminal_equation':equation(cfg['mode']),'violations':errs})
  v.extend(f'{sh}: {e}' for e in errs)
 out={
  'schema':'d1_tower_sky_high_coverage_mrt0_factorization/v1',
  'status':'D1_TOWER_SKY_HIGH_COVERAGE_MRT0_FACTORIZATION_EXACT' if len(rows)==len(CFG) and not v else 'D1_TOWER_SKY_HIGH_COVERAGE_MRT0_FACTORIZATION_PARTIAL',
  'shader_family_count':len(rows),'visible_material_count':sum(x['visible_material_count'] for x in rows),
  'visible_material_fraction':sum(x['visible_material_count'] for x in rows)/74,
  'rows':rows,'violations':v,
  'semantic_boundary':{
   'terminal_arithmetic':'EXACT_NATIVE_GCN',
   'serialized_material_resources':'EXACT_SOURCE_MATERIALS',
   'API13_live_values_and_producer':'WITHHELD',
   'sky_pass_or_element_role':'WITHHELD',
  },
  'policy':'Equations are exact terminal numerical arithmetic for the pinned retail shader identities. Texture t# names and API slots remain structural identities; no cloud/sun/fog/mask/color-pass meaning is inferred.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'families':len(rows),'materials':out['visible_material_count'],
                   'fraction':out['visible_material_fraction'],
                   'rows':[{'shader':x['shader'],'mode':x['mode'],'equation':x['exact_terminal_equation'],'violations':x['violations']} for x in rows],
                   'violations':v},indent=2))
 return 0 if out['status']=='D1_TOWER_SKY_HIGH_COVERAGE_MRT0_FACTORIZATION_EXACT' else 2
if __name__=='__main__':raise SystemExit(main())
