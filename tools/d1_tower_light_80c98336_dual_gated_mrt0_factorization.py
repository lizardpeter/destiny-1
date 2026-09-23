#!/usr/bin/env python3
"""Fail-closed dual-gated terminal MRT0 factorization for singleton Tower light PS 80C98336."""
from __future__ import annotations
import argparse,json
from pathlib import Path
SHADER='80C98336';NATIVE='80C98395'
NATIVE_SHA='78b225a8bd9183bae7ea98c629499e15bb5069e6763c99025eec6fcdb0a3eaad'
GCN_SHA='db14b3fbc6b4f6a4dd102432062e95855ba167e100cd3c1e0f4aafd8f687a4f0'
GCN_BYTES=908;EXPECTED_TERMINAL='000000000380'
def norm(x):return str(x).upper().removeprefix('0X').zfill(8)
def main():
 ap=argparse.ArgumentParser()
 for n in ('material-manifest','shader-report','image-usage','cbuffer-usage','terminal-mrt0','disasm','out'):ap.add_argument('--'+n,type=Path,required=True)
 a=ap.parse_args();v=[];m=json.loads(a.material_manifest.read_text());s=json.loads(a.shader_report.read_text());i=json.loads(a.image_usage.read_text());c=json.loads(a.cbuffer_usage.read_text());t=json.loads(a.terminal_mrt0.read_text());asm=a.disasm.read_text(errors='replace')
 mats=(m.get('pixel_shader_materials') or {}).get(SHADER,[])
 if int((m.get('pixel_shader_frequency') or {}).get(SHADER,-1))!=1 or len(mats)!=1:v.append('frequency/material count drift')
 if any(int((m.get('materials') or {}).get(x,{}).get('ps_texture_count',-1))!=0 for x in mats):v.append('serialized PS texture binding unexpectedly present')
 sr=next((x for x in s.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if not sr or s.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT':v.append('shader report not exact')
 else:
  for k,z in {'native_shader':NATIVE,'native_sha256':NATIVE_SHA,'gcn_sha256':GCN_SHA,'gcn_bytes':GCN_BYTES}.items():
   if sr.get(k)!=z:v.append(f'{k} drift')
 ir=next((x for x in i.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 expimg=[('000000000040','image_load_mip',[1],'x'),('000000000048','image_sample',[0],'xyzw'),('000000000234','image_sample_lz',[2],'xy')]
 if not ir or [(x['address'],x['opcode'],[q['texture_index'] for q in x.get('resources',[])],x['dmask_channels']) for x in ir.get('instructions',[])]!=expimg:v.append('image provenance drift')
 cr=next((x for x in c.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 expected={'00000000023C':(0,[44,45],[0,1]),'000000000240':(0,[92,93,94,95],[8,9,10,11]),'000000000244':(0,[96,97,98,99],[12,13,14,15]),'00000000024C':(0,[40,41,42,43],[16,17,18,19]),'000000000250':(0,[80,81,82,83],[20,21,22,23]),'00000000025C':(0,[84],[2]),'00000000026C':(0,[89],[3])}
 if not cr:v.append('cbuffer row missing')
 else:
  by={x['address']:x for x in cr.get('loads',[])}
  for addr,(api,dw,dst) in expected.items():
   q=by.get(addr)
   if not q or q.get('api_slot')!=api or q.get('dword_indices')!=dw or q.get('destination')!=dst:v.append(f'{addr}: cbuffer drift {q}')
 tr=next((x for x in t.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if not tr or t.get('status')!='D1_GCN_TERMINAL_MRT0_DEPENDENCY_CENSUS_EXACT':v.append('terminal slice missing/not exact')
 else:
  if tr.get('terminal_mrt0_export_address')!=EXPECTED_TERMINAL or tr.get('terminal_mrt0_operands')!=['v0','v0','v1','v1']:v.append('terminal export drift')
  texreq={(0,x,'000000000048') for x in 'xyz'}|{(1,'x','000000000040'),(2,'y','000000000234')}
  for ch,b,mod in [('R',40,80),('G',41,81),('B',42,82)]:
   q=tr['channels'][ch]['value_slice'];tex={(int(x['texture_index']),x['channel'],x['sample_address']) for x in q.get('texture_sample_channels',[])}
   if tex!=texreq:v.append(f'{ch}: texture leaf drift {sorted(tex)}')
   cbq={str(k):set(z) for k,z in (q.get('cbuffer_dwords') or {}).items()};req={b,mod,44,45,84}
   if set(cbq)-{'0'} or not req.issubset(cbq.get('0',set())):v.append(f'{ch}: cbuffer leaf drift {cbq}')
  aq=tr['channels']['A']['value_slice']
  if aq.get('literals')!=['0'] or aq.get('texture_sample_channels') or aq.get('cbuffer_dwords') or aq.get('unknown_registers'):v.append('alpha drift')
  union=tr.get('mrt0_value_union') or {};alltex={(int(x['texture_index']),x['channel']) for x in union.get('texture_sample_channels',[])}
  if (0,'w') in alltex or (2,'x') in alltex:v.append('dead sampled channel reaches MRT0')
  api0=set((union.get('cbuffer_dwords') or {}).get('0',[]))
  for dead in (43,83,89):
   if dead in api0:v.append(f'API0[{dead}] reaches MRT0 value')
  if '12' in (union.get('cbuffer_dwords') or {}):v.append('API12 reaches MRT0')
 anchors=['/*00000000029c: d2820807 041c0100*/ v_mad_f32       v7, v0, s0, v7 clamp','/*0000000002b0: 10020f07         */ v_mul_f32       v1, v7, v7','/*0000000002c0: 10042302         */ v_mul_f32       v2, v2, v17','/*0000000002c8: 7e080210         */ v_mov_b32       v4, s16','/*0000000002e8: 3e080414         */ v_mac_f32       v4, s20, v2','/*000000000300: 10020202         */ v_mul_f32       v1, s2, v1','/*000000000304: d0060000 00010103*/ v_cmp_le_f32    s[0:1], v3, 0','/*00000000030c: 7c0c1080         */ v_cmp_ge_f32    vcc, 0, v8','/*000000000328: 88ea6a00         */ s_or_b64        vcc, s[0:1], vcc','/*000000000380: f8001c0f 00000100*/ exp             mrt0, v0, v0, v1, v1 done compr vm']
 miss=[x for x in anchors if x not in asm]
 if miss:v.append(f'missing anchors {miss}')
 out={'schema':'d1_tower_light_80c98336_dual_gated_mrt0_factorization/v1','status':'D1_TOWER_LIGHT_80C98336_DUAL_GATED_MRT0_FACTORIZATION_EXACT' if not v else 'D1_TOWER_LIGHT_80C98336_DUAL_GATED_MRT0_FACTORIZATION_PARTIAL','shader':SHADER,'instance_count':1,'unique_material_count':len(mats),
 'exact_terminal_equation':{'vector_pre_scale':'V.rgb = API0[40:42].rgb + API0[80:82].rgb*(L*t2.y)','scalar_scale':'K = API0[84] * Q^2','gate':'G0 > 0 AND G1 > 0','mrt0_rgb':'V.rgb * K iff both gates are positive, else 0','mrt0_a':'0','vector_form':'MRT0.rgb = (API0[40:42].rgb + API0[80:82].rgb*(L*t2.y)) * API0[84] * Q^2 iff G0 > 0 and G1 > 0, else 0'},
 'symbols':{'Q':'clamp(q_in*API0[44]+API0[45])','L':'exact native clamped scalar','G0':'API0[92:95] linear plane','G1':'API0[96:99] linear plane'},'predicate_proof':{'first_compare':'G1 <= 0','second_compare':'G0 <= 0','combine':'OR','kept_when':'G0 > 0 AND G1 > 0'},'negative_proof':{'t0_alpha_reaches_mrt0':False,'t2_x_reaches_mrt0':False,'api0_dword43_reaches_mrt0':False,'api0_dword83_reaches_mrt0':False,'api0_dword89_reaches_mrt0':False,'api12_reaches_mrt0':False},'semantic_boundary':{'terminal_arithmetic':'EXACT_NATIVE_GCN','dual_gate_predicate':'EXACT_NATIVE_GCN','renderer_resource_human_semantics':'WITHHELD'},'violations':v}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'equation':out['exact_terminal_equation'],'violations':v},indent=2));return 0 if not v else 2
if __name__=='__main__':raise SystemExit(main())
