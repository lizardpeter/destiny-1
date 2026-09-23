#!/usr/bin/env python3
"""Fail-closed gated terminal MRT0 factorization for singleton Tower light PS 80C99CBD.

Exact native terminal form only.  The shader also writes MRT1; that path is retained
as a boundary and is not assigned human semantics here.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

SHADER='80C99CBD';NATIVE='80C99F1A'
NATIVE_SHA='b426c9b95669330f7430250c7376b8d57911b463f83448801246d1c37a9dd481'
GCN_SHA='89a33de5c33318c22cb6efb9cf574949d58e48ae67fc82fa6dda76fb877a08f7'
GCN_BYTES=1044;EXPECTED_TERMINAL='000000000408'
DEAD_API0=[47,51,91,97]

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def main():
 ap=argparse.ArgumentParser()
 for n in ('material-manifest','shader-report','image-usage','cbuffer-usage','terminal-mrt0','disasm','out'):
  ap.add_argument('--'+n,type=Path,required=True)
 a=ap.parse_args();v=[]
 m=json.loads(a.material_manifest.read_text());s=json.loads(a.shader_report.read_text())
 i=json.loads(a.image_usage.read_text());c=json.loads(a.cbuffer_usage.read_text())
 t=json.loads(a.terminal_mrt0.read_text());asm=a.disasm.read_text(errors='replace')

 if m.get('status')!='D1_WORLD_LIGHT_MATERIAL_MANIFEST_COMPLETE':v.append('material manifest not exact')
 mats=(m.get('pixel_shader_materials') or {}).get(SHADER,[])
 if int((m.get('pixel_shader_frequency') or {}).get(SHADER,-1))!=1 or len(mats)!=1:v.append('frequency/material count drift')
 if any(int((m.get('materials') or {}).get(x,{}).get('ps_texture_count',-1))!=0 for x in mats):v.append('serialized PS texture binding unexpectedly present')

 sr=next((x for x in s.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if s.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or not sr:v.append('shader report not exact/present')
 else:
  for k,z in {'native_shader':NATIVE,'native_sha256':NATIVE_SHA,'gcn_sha256':GCN_SHA,'gcn_bytes':GCN_BYTES}.items():
   if sr.get(k)!=z:v.append(f'{k} drift {sr.get(k)!r} != {z!r}')

 ir=next((x for x in i.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 expimg=[('000000000040','image_load_mip',[1],'x'),('000000000048','image_sample',[0],'xyzw'),('000000000298','image_sample_lz',[3],'x'),('0000000002A4','image_sample_lz',[2],'xy')]
 got=[] if not ir else [(x['address'],x['opcode'],[q['texture_index'] for q in x.get('resources',[])],x['dmask_channels']) for x in ir.get('instructions',[])]
 if i.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT' or got!=expimg:v.append(f'image provenance drift {got!r}')

 cr=next((x for x in c.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 expected={
  '0000000001FC':(0,[40],[0]),'0000000002AC':(0,[52,53],[2,3]),
  '0000000002B0':(0,[100,101,102,103],[12,13,14,15]),
  '0000000002BC':(0,[48,49,50,51],[16,17,18,19]),
  '0000000002CC':(0,[88,89,90,91],[20,21,22,23]),
  '0000000002D0':(0,[92],[1]),'0000000002D4':(0,[97],[4]),
 }
 if c.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or not cr:v.append('cbuffer usage not exact/present')
 else:
  by={x['address']:x for x in cr.get('loads',[])}
  for addr,(api,dw,dst) in expected.items():
   q=by.get(addr)
   if not q or q.get('api_slot')!=api or q.get('dword_indices')!=dw or q.get('destination')!=dst:v.append(f'{addr}: cbuffer drift {q}')

 tr=next((x for x in t.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if t.get('status')!='D1_GCN_TERMINAL_MRT0_DEPENDENCY_CENSUS_EXACT' or not tr:v.append('terminal slice not exact/present')
 else:
  if tr.get('terminal_mrt0_export_address')!=EXPECTED_TERMINAL or tr.get('terminal_mrt0_operands')!=['v1','v1','v0','v0'] or not tr.get('terminal_mrt0_compressed'):v.append('terminal export drift')
  fam={(0,x,'000000000048') for x in 'xyz'}|{(1,'x','000000000040'),(2,'y','0000000002A4')}
  expcb={
   'R':[12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,40,44,45,46,48,52,53,88,92,100,101,102,103],
   'G':[12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,40,44,45,46,49,52,53,89,92,100,101,102,103],
   'B':[12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,40,44,45,46,50,52,53,90,92,100,101,102,103],
  }
  for ch in 'RGB':
   q=tr['channels'][ch]['value_slice']
   tex={(int(x['texture_index']),x['channel'],x['sample_address']) for x in q.get('texture_sample_channels',[])}
   if tex!=fam:v.append(f'{ch}: texture leaf drift {sorted(tex)}')
   if q.get('cbuffer_dwords')!={'0':expcb[ch]}:v.append(f'{ch}: exact cbuffer leaf set drift {q.get("cbuffer_dwords")}')
   if q.get('unknown_registers')!=['v2','v3']:v.append(f'{ch}: native input frontier drift {q.get("unknown_registers")}')
  aq=tr['channels']['A']['value_slice']
  if aq.get('literals')!=['0'] or aq.get('texture_sample_channels') or aq.get('cbuffer_dwords') or aq.get('unknown_registers'):v.append('alpha drift')
  union=tr.get('mrt0_value_union') or {};api0=set((union.get('cbuffer_dwords') or {}).get('0',[]));alltex={(int(x['texture_index']),x['channel']) for x in union.get('texture_sample_channels',[])}
  if (0,'w') in alltex or (2,'x') in alltex or any(x[0]==3 for x in alltex):v.append('dead sampled channel reaches MRT0')
  for d in DEAD_API0:
   if d in api0:v.append(f'API0[{d}] reaches MRT0')
  if '12' in (union.get('cbuffer_dwords') or {}):v.append('API12 reaches MRT0')

 anchors=[
  '/*000000000304: d2820800 04021305*/ v_mad_f32       v0, v5, v9, v0 clamp',
  '/*000000000310: d2060805 0001e10a*/ v_add_f32       v5, v10, 0.5 clamp',
  '/*00000000032c: 10040500         */ v_mul_f32       v2, v0, v2',
  '/*000000000330: 100a0b05         */ v_mul_f32       v5, v5, v5',
  '/*00000000033c: d2820808 04200501*/ v_mad_f32       v8, v1, s2, v8 clamp',
  '/*00000000034c: 10002500         */ v_mul_f32       v0, v0, v18',
  '/*000000000354: 10040a10         */ v_mul_f32       v2, s16, v5',
  '/*000000000358: 10080a11         */ v_mul_f32       v4, s17, v5',
  '/*00000000035c: 100a0a12         */ v_mul_f32       v5, s18, v5',
  '/*00000000036c: 10101108         */ v_mul_f32       v8, v8, v8',
  '/*000000000374: 3e040014         */ v_mac_f32       v2, s20, v0',
  '/*000000000378: 3e080015         */ v_mac_f32       v4, s21, v0',
  '/*00000000037c: 3e0a0016         */ v_mac_f32       v5, s22, v0',
  '/*00000000038c: 10001001         */ v_mul_f32       v0, s1, v8',
  '/*000000000394: 0606060f         */ v_add_f32       v3, s15, v3',
  '/*000000000398: 10040102         */ v_mul_f32       v2, v2, v0',
  '/*00000000039c: 10080104         */ v_mul_f32       v4, v4, v0',
  '/*0000000003a0: 10000105         */ v_mul_f32       v0, v5, v0',
  '/*0000000003b0: 7c0c0680         */ v_cmp_ge_f32    vcc, 0, v3',
  '/*0000000003b4: d2000000 01a90100*/ v_cndmask_b32   v0, v0, 0, vcc',
  '/*0000000003bc: d2000003 01a90104*/ v_cndmask_b32   v3, v4, 0, vcc',
  '/*0000000003c4: d2000002 01a90102*/ v_cndmask_b32   v2, v2, 0, vcc',
  '/*000000000408: f8001c0f 00000001*/ exp             mrt0, v1, v1, v0, v0 done compr vm',
 ]
 miss=[x for x in anchors if x not in asm]
 if miss:v.append(f'missing native anchors {miss}')

 out={
  'schema':'d1_tower_light_80c99cbd_gated_mrt0_factorization/v1',
  'status':'D1_TOWER_LIGHT_80C99CBD_GATED_MRT0_FACTORIZATION_EXACT' if not v else 'D1_TOWER_LIGHT_80C99CBD_GATED_MRT0_FACTORIZATION_PARTIAL',
  'shader':SHADER,'instance_count':1,'unique_material_count':len(mats),
  'exact_tail_symbols':{
   'B':'v5^2 after exact API0[40]-driven clamped branch',
   'P':'exact native clamped/reciprocal scalar carried by v0 before multiplication by t2.y',
   'T':'t2.y',
   'Q':'clamp(q_in*API0[52]+API0[53])',
   'G':'API0[100]*g0 + API0[101]*g1 + API0[102]*g2 + API0[103]',
  },
  'exact_terminal_equation':{
   'vector_pre_scale':'V.rgb = API0[48:50].rgb*B + API0[88:90].rgb*(P*t2.y)',
   'scalar_scale':'K = API0[92] * Q^2',
   'gate':'G > 0',
   'mrt0_rgb':'V.rgb * K if G > 0 else (0,0,0)',
   'mrt0_a':'0',
   'vector_form':'MRT0.rgb = [API0[48:50]*B + API0[88:90]*(P*t2.y)] * API0[92] * Q^2 when G > 0, else 0',
  },
  'predicate_proof':{'compare':'v_cmp_ge_f32 vcc, 0, G','zero_selected_when':'G <= 0','kept_when':'G > 0'},
  'native_input_frontier':['v2','v3'],'renderer_texture_value_frontier':['t0.rgb','t1.x','t2.y'],
  'negative_proof':{
   't0_alpha_reaches_mrt0':False,'t2_x_reaches_mrt0':False,'t3_reaches_mrt0':False,
   **{f'api0_dword{d}_reaches_mrt0':False for d in DEAD_API0},'api12_reaches_mrt0':False,
  },
  'mrt1_boundary':'SHADER_WRITES_MRT1_BUT_THIS_PROOF REDUCES MRT0 ONLY',
  'semantic_boundary':{
   'terminal_arithmetic_and_gate':'EXACT_NATIVE_GCN','renderer_resource_human_semantics':'WITHHELD',
   'symbols_B_P_Q_G_human_semantics':'WITHHELD','mrt1_semantics':'WITHHELD','portable_light_model_mapping':'WITHHELD',
  },
  'violations':v,
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'equation':out['exact_terminal_equation'],'negative_proof':out['negative_proof'],'violations':v},indent=2))
 return 0 if not v else 2

if __name__=='__main__':raise SystemExit(main())
