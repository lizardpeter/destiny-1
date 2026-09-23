#!/usr/bin/env python3
"""Fail-closed terminal MRT0 factorization for singleton Tower light PS 80AADB46."""
from __future__ import annotations
import argparse,json
from pathlib import Path
SHADER='80AADB46';NATIVE='80AADB47'
NATIVE_SHA='176d52e0f0cd8b12990de96af6809026414884b1e9f9e9fe29ff203d2b98773b'
GCN_SHA='6706c9d4b1a3ca07b9ee887970a5dc96aa646c0ff8671642ed87b1daa56f41d7'
GCN_BYTES=708;EXPECTED_TERMINAL='0000000002B8'
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
 expimg=[('000000000040','image_load_mip',[1],'x'),('000000000048','image_sample',[0],'xyzw'),('0000000001D4','image_sample_lz',[2],'xy')]
 if not ir or [(x['address'],x['opcode'],[q['texture_index'] for q in x.get('resources',[])],x['dmask_channels']) for x in ir.get('instructions',[])]!=expimg:v.append('image provenance drift')
 cr=next((x for x in c.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 expected={'0000000001DC':(0,[36,37],[0,1]),'0000000001E4':(0,[32,33,34,35],[8,9,10,11]),'0000000001E8':(0,[56,57,58,59],[12,13,14,15]),'0000000001F4':(0,[60],[2]),'000000000204':(0,[65],[3])}
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
  texreq={(0,x,'000000000048') for x in 'xyz'}|{(1,'x','000000000040'),(2,'y','0000000001D4')}
  for ch,b,mod in [('R',32,56),('G',33,57),('B',34,58)]:
   q=tr['channels'][ch]['value_slice'];tex={(int(x['texture_index']),x['channel'],x['sample_address']) for x in q.get('texture_sample_channels',[])}
   if tex!=texreq:v.append(f'{ch}: texture leaf drift {sorted(tex)}')
   cbq={str(k):set(z) for k,z in (q.get('cbuffer_dwords') or {}).items()}
   if set(cbq)-{'0'} or not {b,mod,36,37,60}.issubset(cbq.get('0',set())):v.append(f'{ch}: cbuffer leaf drift {cbq}')
  aq=tr['channels']['A']['value_slice']
  if aq.get('literals')!=['0'] or aq.get('texture_sample_channels') or aq.get('cbuffer_dwords') or aq.get('unknown_registers'):v.append('alpha drift')
  union=tr.get('mrt0_value_union') or {};api0=set((union.get('cbuffer_dwords') or {}).get('0',[]));alltex={(int(x['texture_index']),x['channel']) for x in union.get('texture_sample_channels',[])}
  if (0,'w') in alltex or (2,'x') in alltex:v.append('dead sampled channel reaches MRT0')
  for dead in (35,59,65):
   if dead in api0:v.append(f'API0[{dead}] reaches MRT0')
  if '12' in (union.get('cbuffer_dwords') or {}):v.append('API12 reaches MRT0')
 anchors=['/*000000000220: d2820804 04100109*/ v_mad_f32       v4, v9, s0, v4 clamp','/*000000000228: d2820801 04060105*/ v_mad_f32       v1, v5, v0, v1 clamp','/*000000000234: 10040904         */ v_mul_f32       v2, v4, v4','/*000000000240: 10021b01         */ v_mul_f32       v1, v1, v13','/*000000000248: 7e060208         */ v_mov_b32       v3, s8','/*000000000260: 3e06020c         */ v_mac_f32       v3, s12, v1','/*000000000278: 10040402         */ v_mul_f32       v2, s2, v2','/*00000000027c: 10060503         */ v_mul_f32       v3, v3, v2','/*0000000002b8: f8001c0f 00000100*/ exp             mrt0, v0, v0, v1, v1 done compr vm']
 miss=[x for x in anchors if x not in asm]
 if miss:v.append(f'missing anchors {miss}')
 out={'schema':'d1_tower_light_80aadb46_mrt0_factorization/v1','status':'D1_TOWER_LIGHT_80AADB46_MRT0_FACTORIZATION_EXACT' if not v else 'D1_TOWER_LIGHT_80AADB46_MRT0_FACTORIZATION_PARTIAL','shader':SHADER,'instance_count':1,'unique_material_count':len(mats),
 'exact_terminal_equation':{'vector_pre_scale':'V.rgb = API0[32:34].rgb + API0[56:58].rgb*(L*t2.y)','scalar_scale':'K = API0[60] * Q^2','mrt0_rgb':'MRT0.rgb = V.rgb * K','mrt0_a':'0','vector_form':'MRT0.rgb = (API0[32:34].rgb + API0[56:58].rgb*(L*t2.y)) * API0[60] * Q^2'},
 'symbols':{'Q':'clamp(q_in*API0[36]+API0[37])','L':'exact native clamped scalar','T':'t2.y'},'negative_proof':{'t0_alpha_reaches_mrt0':False,'t2_x_reaches_mrt0':False,'api0_dword35_reaches_mrt0':False,'api0_dword59_reaches_mrt0':False,'api0_dword65_reaches_mrt0':False,'api12_reaches_mrt0':False},'semantic_boundary':{'terminal_arithmetic':'EXACT_NATIVE_GCN','renderer_resource_human_semantics':'WITHHELD'},'violations':v}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'equation':out['exact_terminal_equation'],'violations':v},indent=2));return 0 if not v else 2
if __name__=='__main__':raise SystemExit(main())
