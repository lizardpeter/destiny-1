#!/usr/bin/env python3
"""Fail-closed dual-gated terminal MRT0 factorization for singleton Tower light PS 80C99CBA."""
from __future__ import annotations
import argparse,json
from pathlib import Path

SHADER='80C99CBA';NATIVE='80C99F17'
NATIVE_SHA='f5ff494b4e8fc7fd53d1c7d21720ef78257ecefd62f2e1311a2b1ad440a43e6c'
GCN_SHA='55e23e3de7667363e8a30e0ef5a6299420547f58e47480c0c0d6f16cf4e78ca3'
GCN_BYTES=1016;EXPECTED_TERMINAL='0000000003EC'
DEAD_API0=[31,39,43,67,75,81]

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
 expimg=[('000000000040','image_load_mip',[1],'x'),('000000000048','image_sample',[0],'xyzw'),('000000000238','image_sample_lz',[3],'x'),('000000000244','image_sample_lz',[2],'xy')]
 got=[] if not ir else [(x['address'],x['opcode'],[q['texture_index'] for q in x.get('resources',[])],x['dmask_channels']) for x in ir.get('instructions',[])]
 if i.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT' or got!=expimg:v.append(f'image provenance drift {got}')

 cr=next((x for x in c.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 expected={'00000000024C':(0,[64,65,66,67],[12,13,14,15]),'000000000250':(0,[44,45],[2,3]),'000000000254':(0,[84,85,86,87],[16,17,18,19]),'000000000258':(0,[88,89,90,91],[20,21,22,23]),'00000000025C':(0,[68,69],[24,25]),'000000000268':(0,[40,41,42,43],[28,29,30,31]),'000000000278':(0,[72,73,74,75],[32,33,34,35]),'00000000027C':(0,[76],[1]),'000000000280':(0,[81],[4])}
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
  fam={(0,x,'000000000048') for x in 'xyz'}|{(1,'x','000000000040'),(2,'y','000000000244')}
  expcb={'R':[12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,32,36,37,38,40,44,45,64,65,66,68,69,72,76,84,85,86,87],
         'G':[12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,32,36,37,38,41,44,45,64,65,66,68,69,73,76,84,85,86,87],
         'B':[12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,32,36,37,38,42,44,45,64,65,66,68,69,74,76,84,85,86,87]}
  for ch in 'RGB':
   q=tr['channels'][ch]['value_slice'];tex={(int(x['texture_index']),x['channel'],x['sample_address']) for x in q.get('texture_sample_channels',[])}
   if tex!=fam:v.append(f'{ch}: texture leaf drift {sorted(tex)}')
   if q.get('cbuffer_dwords')!={'0':expcb[ch]}:v.append(f'{ch}: cbuffer leaf drift {q.get("cbuffer_dwords")}')
   if q.get('unknown_registers')!=['v2','v3']:v.append(f'{ch}: native input frontier drift {q.get("unknown_registers")}')
  aq=tr['channels']['A']['value_slice']
  if aq.get('literals')!=['0'] or aq.get('texture_sample_channels') or aq.get('cbuffer_dwords') or aq.get('unknown_registers'):v.append('alpha drift')
  union=tr.get('mrt0_value_union') or {};api0=set((union.get('cbuffer_dwords') or {}).get('0',[]));alltex={(int(x['texture_index']),x['channel']) for x in union.get('texture_sample_channels',[])}
  if (0,'w') in alltex or (2,'x') in alltex or any(x[0]==3 for x in alltex):v.append('dead sampled channel reaches MRT0')
  for d in DEAD_API0:
   if d in api0:v.append(f'API0[{d}] reaches MRT0')
  if '12' in (union.get('cbuffer_dwords') or {}):v.append('API12 reaches MRT0')

 anchors=[
  '/*0000000002c8: d282080b 042c0509*/ v_mad_f32       v11, v9, s2, v11 clamp',
  '/*0000000002d8: d2820801 04060105*/ v_mad_f32       v1, v5, v0, v1 clamp',
  '/*0000000002e4: d2060804 0001e107*/ v_add_f32       v4, v7, 0.5 clamp',
  '/*0000000002fc: 100e170b         */ v_mul_f32       v7, v11, v11',
  '/*000000000300: d2820808 2420310e*/ v_mad_f32       v8, -v14, s24, v8 clamp',
  '/*00000000030c: 10080904         */ v_mul_f32       v4, v4, v4',
  '/*000000000324: 10022501         */ v_mul_f32       v1, v1, v18',
  '/*00000000032c: 1004081c         */ v_mul_f32       v2, s28, v4',
  '/*000000000330: 1012081d         */ v_mul_f32       v9, s29, v4',
  '/*000000000334: 1008081e         */ v_mul_f32       v4, s30, v4',
  '/*000000000344: 100e1107         */ v_mul_f32       v7, v7, v8',
  '/*000000000348: 060c0c13         */ v_add_f32       v6, s19, v6',
  '/*00000000034c: 06060617         */ v_add_f32       v3, s23, v3',
  '/*000000000350: 3e040220         */ v_mac_f32       v2, s32, v1',
  '/*000000000354: 3e120221         */ v_mac_f32       v9, s33, v1',
  '/*000000000358: 3e080222         */ v_mac_f32       v4, s34, v1',
  '/*000000000368: 10000e01         */ v_mul_f32       v0, s1, v7',
  '/*000000000370: d0060000 00010103*/ v_cmp_le_f32    s[0:1], v3, 0',
  '/*000000000378: 7c0c0c80         */ v_cmp_ge_f32    vcc, 0, v6',
  '/*000000000394: 88ea6a00         */ s_or_b64        vcc, s[0:1], vcc',
  '/*000000000398: d2000000 01a90100*/ v_cndmask_b32   v0, v0, 0, vcc',
  '/*0000000003a0: d2000003 01a90103*/ v_cndmask_b32   v3, v3, 0, vcc',
  '/*0000000003a8: d2000002 01a90102*/ v_cndmask_b32   v2, v2, 0, vcc',
  '/*0000000003ec: f8001c0f 00000001*/ exp             mrt0, v1, v1, v0, v0 done compr vm',
 ]
 miss=[x for x in anchors if x not in asm]
 if miss:v.append(f'missing anchors {miss}')

 out={'schema':'d1_tower_light_80c99cba_dual_gated_mrt0_factorization/v1',
      'status':'D1_TOWER_LIGHT_80C99CBA_DUAL_GATED_MRT0_FACTORIZATION_EXACT' if not v else 'D1_TOWER_LIGHT_80C99CBA_DUAL_GATED_MRT0_FACTORIZATION_PARTIAL',
      'shader':SHADER,'instance_count':1,'unique_material_count':len(mats),
      'exact_tail_symbols':{
       'Q':'clamp(q_in*API0[44]+API0[45])','R':'clamp(-r_in*API0[68]+API0[69])',
       'B':'exact native clamped branch squared at 0x30C','P':'exact native clamped scalar before multiplication by t2.y','T':'t2.y',
       'G0':'API0[84]*g00 + API0[85]*g01 + API0[86]*g02 + API0[87]',
       'G1':'API0[88]*g10 + API0[89]*g11 + API0[90]*g12 + API0[91]',
      },
      'exact_terminal_equation':{
       'vector_pre_scale':'V.rgb = API0[40:42].rgb*B + API0[72:74].rgb*(P*t2.y)',
       'scalar_scale':'K = API0[76] * Q^2 * R','gate':'G0 > 0 AND G1 > 0',
       'mrt0_rgb':'V.rgb*K iff both gates are positive, else (0,0,0)','mrt0_a':'0',
       'vector_form':'MRT0.rgb = [API0[40:42]*B + API0[72:74]*(P*t2.y)] * API0[76] * Q^2 * R iff G0 > 0 and G1 > 0, else 0',
      },
      'predicate_proof':{'first_compare':'G1 <= 0','second_compare':'G0 <= 0','combine':'OR','kept_when':'G0 > 0 AND G1 > 0'},
      'native_input_frontier':['v2','v3'],'renderer_texture_value_frontier':['t0.rgb','t1.x','t2.y'],
      'negative_proof':{'t0_alpha_reaches_mrt0':False,'t2_x_reaches_mrt0':False,'t3_reaches_mrt0':False,**{f'api0_dword{d}_reaches_mrt0':False for d in DEAD_API0},'api12_reaches_mrt0':False},
      'mrt1_boundary':'SHADER_WRITES_MRT1_BUT_THIS PROOF REDUCES MRT0 ONLY',
      'semantic_boundary':{'terminal_arithmetic_and_dual_gate':'EXACT_NATIVE_GCN','renderer_resource_human_semantics':'WITHHELD','gate_human_semantics':'WITHHELD','mrt1_semantics':'WITHHELD','portable_light_model_mapping':'WITHHELD'},
      'violations':v}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'equation':out['exact_terminal_equation'],'predicate':out['predicate_proof'],'violations':v},indent=2))
 return 0 if not v else 2

if __name__=='__main__':raise SystemExit(main())
