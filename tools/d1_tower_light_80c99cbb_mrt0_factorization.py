#!/usr/bin/env python3
"""Fail-closed terminal MRT0 factorization for singleton Tower light PS 80C99CBB."""
from __future__ import annotations
import argparse,json
from pathlib import Path

SHADER='80C99CBB';NATIVE='80C99F18'
NATIVE_SHA='ac511b183e7e5c3befde3527f417140e4af5b46e028db4b74823b209c2c59dd5'
GCN_SHA='9d0261d0fd9b5427e82d83bc0cc2df61750d1425a5f9dcce1a8280d62a13a06d'
GCN_BYTES=720;EXPECTED_TERMINAL='0000000002C4'
DEAD_API0=[31,39,43,67,75]

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def main():
 ap=argparse.ArgumentParser()
 for n in ('material-manifest','shader-report','image-usage','cbuffer-usage','terminal-mrt0','disasm','out'):ap.add_argument('--'+n,type=Path,required=True)
 a=ap.parse_args();v=[]
 m=json.loads(a.material_manifest.read_text());s=json.loads(a.shader_report.read_text());i=json.loads(a.image_usage.read_text());c=json.loads(a.cbuffer_usage.read_text());t=json.loads(a.terminal_mrt0.read_text());asm=a.disasm.read_text(errors='replace')
 if m.get('status')!='D1_WORLD_LIGHT_MATERIAL_MANIFEST_COMPLETE':v.append('material manifest not exact')
 mats=(m.get('pixel_shader_materials') or {}).get(SHADER,[])
 if int((m.get('pixel_shader_frequency') or {}).get(SHADER,-1))!=1 or len(mats)!=1:v.append('frequency/material count drift')
 if any(int((m.get('materials') or {}).get(x,{}).get('ps_texture_count',-1))!=0 for x in mats):v.append('serialized PS texture binding unexpectedly present')
 sr=next((x for x in s.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if s.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or not sr:v.append('shader report not exact/present')
 else:
  for k,z in {'native_shader':NATIVE,'native_sha256':NATIVE_SHA,'gcn_sha256':GCN_SHA,'gcn_bytes':GCN_BYTES}.items():
   if sr.get(k)!=z:v.append(f'{k} drift')
 ir=next((x for x in i.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 expimg=[('000000000040','image_load_mip',[1],'x'),('000000000048','image_sample',[0],'xyzw'),('0000000001D4','image_sample_lz',[2],'y')]
 got=[] if not ir else [(x['address'],x['opcode'],[q['texture_index'] for q in x.get('resources',[])],x['dmask_channels']) for x in ir.get('instructions',[])]
 if i.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT' or got!=expimg:v.append(f'image provenance drift {got}')
 cr=next((x for x in c.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 expected={'0000000001DC':(0,[36,37,38,39],[0,1,2,3]),'0000000001E0':(0,[64,65,66,67],[8,9,10,11]),'0000000001E8':(0,[32],[3]),'0000000001EC':(0,[44,45],[12,13]),'0000000001F0':(0,[68,69],[14,15]),'0000000001F8':(0,[40,41,42,43],[16,17,18,19]),'000000000204':(0,[72,73,74,75],[20,21,22,23]),'000000000208':(0,[76],[1])}
 if c.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or not cr:v.append('cbuffer usage not exact/present')
 else:
  by={x['address']:x for x in cr.get('loads',[])}
  for addr,(api,dw,dst) in expected.items():
   q=by.get(addr)
   if not q or q.get('api_slot')!=api or q.get('dword_indices')!=dw or q.get('destination')!=dst:v.append(f'{addr}: cbuffer drift {q}')
 tr=next((x for x in t.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if t.get('status')!='D1_GCN_TERMINAL_MRT0_DEPENDENCY_CENSUS_EXACT' or not tr:v.append('terminal slice not exact/present')
 else:
  if tr.get('terminal_mrt0_export_address')!=EXPECTED_TERMINAL or tr.get('terminal_mrt0_operands')!=['v2','v2','v0','v0'] or not tr.get('terminal_mrt0_compressed'):v.append('terminal export drift')
  fam={(0,x,'000000000048') for x in 'xyz'}|{(1,'x','000000000040'),(2,'y','0000000001D4')}
  expcb={'R':[12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,32,36,37,38,40,44,45,64,65,66,68,69,72,76],
         'G':[12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,32,36,37,38,41,44,45,64,65,66,68,69,73,76],
         'B':[12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,32,36,37,38,42,44,45,64,65,66,68,69,74,76]}
  for ch in 'RGB':
   q=tr['channels'][ch]['value_slice'];tex={(int(x['texture_index']),x['channel'],x['sample_address']) for x in q.get('texture_sample_channels',[])}
   if tex!=fam:v.append(f'{ch}: texture leaf drift {sorted(tex)}')
   if q.get('cbuffer_dwords')!={'0':expcb[ch]}:v.append(f'{ch}: cbuffer leaf drift {q.get("cbuffer_dwords")}')
   if q.get('unknown_registers')!=['v2','v3']:v.append(f'{ch}: native input frontier drift {q.get("unknown_registers")}')
  aq=tr['channels']['A']['value_slice']
  if aq.get('literals')!=['0'] or aq.get('texture_sample_channels') or aq.get('cbuffer_dwords') or aq.get('unknown_registers'):v.append('alpha drift')
  union=tr.get('mrt0_value_union') or {};api0=set((union.get('cbuffer_dwords') or {}).get('0',[]));alltex={(int(x['texture_index']),x['channel']) for x in union.get('texture_sample_channels',[])}
  if (0,'w') in alltex or (2,'x') in alltex:v.append('dead sampled channel reaches MRT0')
  for d in DEAD_API0:
   if d in api0:v.append(f'API0[{d}] reaches MRT0')
  if '12' in (union.get('cbuffer_dwords') or {}):v.append('API12 reaches MRT0')
 anchors=['/*000000000238: d282080b 042c1909*/ v_mad_f32       v11, v9, s12, v11 clamp','/*00000000024c: d2060804 0001e10a*/ v_add_f32       v4, v10, 0.5 clamp','/*000000000254: 100c170b         */ v_mul_f32       v6, v11, v11','/*000000000258: d2820803 240c1d08*/ v_mad_f32       v3, -v8, s14, v3 clamp','/*000000000260: d2820801 04060105*/ v_mad_f32       v1, v5, v0, v1 clamp','/*000000000268: 10000904         */ v_mul_f32       v0, v4, v4','/*000000000270: 10020501         */ v_mul_f32       v1, v1, v2','/*000000000274: 10040010         */ v_mul_f32       v2, s16, v0','/*000000000278: 10080011         */ v_mul_f32       v4, s17, v0','/*00000000027c: 10000012         */ v_mul_f32       v0, s18, v0','/*000000000280: 10060706         */ v_mul_f32       v3, v6, v3','/*000000000284: 3e040214         */ v_mac_f32       v2, s20, v1','/*000000000288: 3e080215         */ v_mac_f32       v4, s21, v1','/*00000000028c: 3e000216         */ v_mac_f32       v0, s22, v1','/*000000000290: 10020601         */ v_mul_f32       v1, s1, v3','/*000000000294: 10040302         */ v_mul_f32       v2, v2, v1','/*000000000298: 10060304         */ v_mul_f32       v3, v4, v1','/*00000000029c: 10000300         */ v_mul_f32       v0, v0, v1','/*0000000002c4: f8001c0f 00000002*/ exp             mrt0, v2, v2, v0, v0 done compr vm']
 miss=[x for x in anchors if x not in asm]
 if miss:v.append(f'missing anchors {miss}')
 out={'schema':'d1_tower_light_80c99cbb_mrt0_factorization/v1','status':'D1_TOWER_LIGHT_80C99CBB_MRT0_FACTORIZATION_EXACT' if not v else 'D1_TOWER_LIGHT_80C99CBB_MRT0_FACTORIZATION_PARTIAL','shader':SHADER,'instance_count':1,'unique_material_count':len(mats),
 'exact_tail_symbols':{'Q':'clamp(q_in*API0[44]+API0[45])','R':'clamp(-r_in*API0[68]+API0[69])','B':'(exact native API0[32]-driven gate)^2','P':'exact native clamped scalar','T':'t2.y'},
 'exact_terminal_equation':{'vector_pre_scale':'V.rgb = API0[40:42].rgb*B + API0[72:74].rgb*(P*t2.y)','scalar_scale':'K = API0[76] * Q^2 * R','mrt0_rgb':'V.rgb * K','mrt0_a':'0','vector_form':'MRT0.rgb = [API0[40:42]*B + API0[72:74]*(P*t2.y)] * API0[76] * Q^2 * R'},
 'native_input_frontier':['v2','v3'],'renderer_texture_value_frontier':['t0.rgb','t1.x','t2.y'],
 'negative_proof':{'t0_alpha_reaches_mrt0':False,'t2_x_reaches_mrt0':False,**{f'api0_dword{d}_reaches_mrt0':False for d in DEAD_API0},'api12_reaches_mrt0':False},
 'mrt1_boundary':'MRT1 is written as exact zero in the pinned native program and carries no positive semantic claim here',
 'semantic_boundary':{'terminal_arithmetic':'EXACT_NATIVE_GCN','renderer_resource_human_semantics':'WITHHELD','symbols_Q_R_B_P_human_semantics':'WITHHELD','portable_light_model_mapping':'WITHHELD'},'violations':v}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'equation':out['exact_terminal_equation'],'violations':v},indent=2));return 0 if not v else 2
if __name__=='__main__':raise SystemExit(main())
