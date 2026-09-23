#!/usr/bin/env python3
"""Fail-closed textured terminal MRT0 factorization for Tower light PS 80CA0293.

Exact native terminal form:
    Q = clamp(q_in * API0[32] + API0[33])
    H = clamp(-h_in * API0[72] + API0[73])
    L = exact native clamped scalar reaching t2.y modulation
    BASE.rgb = API0[76:78] * Q^2 * H * API0[80] * L * t2.y
    MRT0.rgb = BASE.rgb * t3.rgb
    MRT0.a = 0

Both exact family materials serialize t3 = 80CA0256. API0[85] and the
alternate t2.x branch are MRT1-only.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
SHADER='80CA0293';NATIVE='80CA02C2'
NATIVE_SHA='d7a38ad8fdd0b3750eaae66f1a45167688ccab33d4e6caae0de1228ea45bdfac'
GCN_SHA='c5ce236218d07b1879fa6627c208d3dc9cfab05995887995647ed9ebcf14fe2c'
GCN_BYTES=872;EXPECTED_INSTANCES=2;EXPECTED_MATERIALS=2;EXPECTED_TERMINAL='00000000035C'
EXPECTED_T3='80CA0256'
ANCHORS=[
 '/*000000000234: f09c0300 01061012*/ image_sample_lz v[16:17], v[18:21], s[24:31], s[32:35] dmask:3',
 '/*000000000248: f0800700 00021212*/ image_sample    v[18:20], v[18:21], s[8:15], s[0:3] dmask:7',
 '/*000000000250: c2800544         */ s_buffer_load_dwordx4 s[0:3], s[4:7], 0x44',
 '/*000000000254: c2440520         */ s_buffer_load_dwordx2 s[8:9], s[4:7], 0x20',
 '/*000000000258: c2450548         */ s_buffer_load_dwordx2 s[10:11], s[4:7], 0x48',
 '/*000000000264: c286054c         */ s_buffer_load_dwordx4 s[12:15], s[4:7], 0x4c',
 '/*000000000278: c2010550         */ s_buffer_load_dword s2, s[4:7], 0x50',
 '/*0000000002ac: c2000555         */ s_buffer_load_dword s0, s[4:7], 0x55',
 '/*000000000290: d2820808 04201109*/ v_mad_f32       v8, v9, s8, v8 clamp',
 '/*0000000002b0: 10061108         */ v_mul_f32       v3, v8, v8',
 '/*0000000002b4: d2820807 241c1504*/ v_mad_f32       v7, -v4, s10, v7 clamp',
 '/*0000000002bc: d2820801 04060105*/ v_mad_f32       v1, v5, v0, v1 clamp',
 '/*0000000002cc: 10040f03         */ v_mul_f32       v2, v3, v7',
 '/*0000000002d8: 1006040c         */ v_mul_f32       v3, s12, v2',
 '/*0000000002dc: 1008040d         */ v_mul_f32       v4, s13, v2',
 '/*0000000002e0: 1004040e         */ v_mul_f32       v2, s14, v2',
 '/*0000000002e4: 10022301         */ v_mul_f32       v1, v1, v17',
 '/*0000000002f8: 10060602         */ v_mul_f32       v3, s2, v3',
 '/*0000000002fc: 10080802         */ v_mul_f32       v4, s2, v4',
 '/*000000000300: 10040402         */ v_mul_f32       v2, s2, v2',
 '/*000000000304: 10060701         */ v_mul_f32       v3, v1, v3',
 '/*000000000308: 10080901         */ v_mul_f32       v4, v1, v4',
 '/*00000000030c: 10020501         */ v_mul_f32       v1, v1, v2',
 '/*000000000320: 10060712         */ v_mul_f32       v3, v18, v3',
 '/*000000000324: 10080913         */ v_mul_f32       v4, v19, v4',
 '/*000000000328: 10020314         */ v_mul_f32       v1, v20, v1',
 '/*000000000354: 5e000903         */ v_cvt_pkrtz_f16_f32 v0, v3, v4',
 '/*000000000358: 5e020d01         */ v_cvt_pkrtz_f16_f32 v1, v1, v6',
 '/*00000000035c: f8001c0f 00000100*/ exp             mrt0, v0, v0, v1, v1 done compr vm',
]
def norm(x):return str(x).upper().removeprefix('0X').zfill(8)
def main()->int:
 ap=argparse.ArgumentParser()
 for n in ('material-manifest','shader-report','image-usage','cbuffer-usage','terminal-mrt0','disasm','out'):ap.add_argument('--'+n,type=Path,required=True)
 a=ap.parse_args();v=[];m=json.loads(a.material_manifest.read_text());s=json.loads(a.shader_report.read_text());i=json.loads(a.image_usage.read_text());c=json.loads(a.cbuffer_usage.read_text());t=json.loads(a.terminal_mrt0.read_text());asm=a.disasm.read_text(errors='replace')
 if m.get('status')!='D1_WORLD_LIGHT_MATERIAL_MANIFEST_COMPLETE':v.append('material manifest not exact')
 if int((m.get('pixel_shader_frequency') or {}).get(SHADER,-1))!=EXPECTED_INSTANCES:v.append('instance count drift')
 mats=(m.get('pixel_shader_materials') or {}).get(SHADER,[])
 if len(mats)!=EXPECTED_MATERIALS:v.append('material count drift')
 for mh in mats:
  mr=(m.get('materials') or {}).get(mh,{})
  ps=[x for x in mr.get('bindings',[]) if x.get('stage')=='ps']
  if int(mr.get('ps_texture_count',-1))!=1 or len(ps)!=1 or int(ps[0].get('texture_index',-1))!=3 or norm(ps[0].get('texture'))!=EXPECTED_T3:
   v.append(f'{mh}: expected exact serialized t3={EXPECTED_T3}, got {ps}')
 sr=next((x for x in s.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if s.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or not sr:v.append('shader report not exact/present')
 else:
  for k,z in {'native_shader':NATIVE,'native_sha256':NATIVE_SHA,'gcn_sha256':GCN_SHA,'gcn_bytes':GCN_BYTES}.items():
   if sr.get(k)!=z:v.append(f'{k} drift')
 ir=next((x for x in i.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if i.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT' or not ir:v.append('image usage not exact/present')
 else:
  got=[(x['address'],x['opcode'],[q['texture_index'] for q in x.get('resources',[])],x['dmask_channels']) for x in ir.get('instructions',[])]
  exp=[('000000000040','image_load_mip',[1],'x'),('000000000048','image_sample',[0],'xyzw'),('000000000234','image_sample_lz',[2],'xy'),('000000000248','image_sample',[3],'xyz')]
  if got!=exp:v.append(f'image scope drift {got!r}')
 cr=next((x for x in c.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if c.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or not cr:v.append('cbuffer usage not exact/present')
 else:
  by={x.get('address'):x for x in cr.get('loads',[])}
  expected={'000000000250':(0,[68,69,70,71],[0,1,2,3]),'000000000254':(0,[32,33],[8,9]),'000000000258':(0,[72,73],[10,11]),'000000000264':(0,[76,77,78,79],[12,13,14,15]),'000000000278':(0,[80],[2]),'0000000002AC':(0,[85],[0])}
  for addr,(api,dw,dst) in expected.items():
   q=by.get(addr)
   if not q or q.get('api_slot')!=api or q.get('dword_indices')!=dw or q.get('destination')!=dst:v.append(f'{addr}: cbuffer drift {q}')
 tr=next((x for x in t.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if t.get('status')!='D1_GCN_TERMINAL_MRT0_DEPENDENCY_CENSUS_EXACT' or not tr:v.append('terminal MRT0 slice not exact/present')
 else:
  if tr.get('terminal_mrt0_export_address')!=EXPECTED_TERMINAL or tr.get('terminal_mrt0_operands')!=['v0','v0','v1','v1']:v.append('terminal export drift')
  for ch,col,tch in [('R',76,'x'),('G',77,'y'),('B',78,'z')]:
   q=tr['channels'][ch]['value_slice'];tex={(int(x['texture_index']),x['channel'],x['sample_address']) for x in q.get('texture_sample_channels',[])}
   reqtex={(0,x,'000000000048') for x in 'xyz'}|{(1,'x','000000000040'),(2,'y','000000000234'),(3,tch,'000000000248')}
   if tex!=reqtex:v.append(f'{ch}: texture leaf drift {sorted(tex)}')
   cbq={str(k):set(z) for k,z in (q.get('cbuffer_dwords') or {}).items()};req={32,33,72,73,col,80}
   if set(cbq)-{'0'} or not req.issubset(cbq.get('0',set())):v.append(f'{ch}: cbuffer leaf drift {cbq}')
  aq=tr['channels']['A']['value_slice']
  if aq.get('literals')!=['0'] or aq.get('texture_sample_channels') or aq.get('cbuffer_dwords') or aq.get('unknown_registers'):v.append('alpha drift')
  union=tr.get('mrt0_value_union') or {};alltex={(int(x['texture_index']),x['channel']) for x in union.get('texture_sample_channels',[])}
  if (0,'w') in alltex or (2,'x') in alltex:v.append('dead sampled channel reaches MRT0')
  api0=set((union.get('cbuffer_dwords') or {}).get('0',[]))
  for dead in (79,85):
   if dead in api0:v.append(f'API0[{dead}] reaches MRT0')
  if '12' in (union.get('cbuffer_dwords') or {}):v.append('API12 reaches MRT0')
 missing=[x for x in ANCHORS if x not in asm]
 if missing:v.append(f'missing native anchors {missing}')
 out={'schema':'d1_tower_light_80ca0293_textured_mrt0_factorization/v1','status':'D1_TOWER_LIGHT_80CA0293_TEXTURED_MRT0_FACTORIZATION_EXACT' if not v else 'D1_TOWER_LIGHT_80CA0293_TEXTURED_MRT0_FACTORIZATION_PARTIAL','shader':SHADER,'native_shader':NATIVE,'gcn_sha256':GCN_SHA,'instance_count':EXPECTED_INSTANCES,'unique_material_count':len(mats),'serialized_t3_texture':EXPECTED_T3,
 'exact_tail_symbols':{'Q':'clamp(q_in*API0[32]+API0[33])','H':'clamp(-h_in*API0[72]+API0[73])','L':'exact native clamped scalar','C':'API0[76:78].rgb','S':'API0[80]','T':'t2.y','M':'t3.rgb'},
 'exact_terminal_equation':{'base_rgb':'API0[76:78].rgb * Q^2 * H * API0[80] * L * t2.y','mrt0_rgb':'BASE.rgb * t3.rgb','mrt0_a':'0','vector_form':'MRT0.rgb = API0[76:78].rgb * Q^2 * H * API0[80] * L * t2.y * t3.rgb'},
 'negative_proof':{'t0_alpha_reaches_mrt0':False,'t2_x_reaches_mrt0':False,'api0_dword79_reaches_mrt0':False,'api0_dword85_reaches_mrt0':False,'api12_reaches_mrt0':False},
 'semantic_boundary':{'terminal_arithmetic':'EXACT_NATIVE_GCN','serialized_t3_binding':'EXACT_80CA0256_FOR_BOTH_MATERIALS','serialized_t3_texture_role':'WITHHELD','renderer_t0_t1_t2_human_semantics':'WITHHELD'},'violations':v}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'equation':out['exact_terminal_equation'],'violations':v},indent=2));return 0 if not v else 2
if __name__=='__main__':raise SystemExit(main())
