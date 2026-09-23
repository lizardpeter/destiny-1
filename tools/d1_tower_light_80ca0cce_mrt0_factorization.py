#!/usr/bin/env python3
"""Fail-closed terminal MRT0 factorization for Tower light PS 80CA0CCE.

Exact native terminal form:
    Q = clamp(q_in * API0[36] + API0[37])
    H = clamp(-h_in * API0[60] + API0[61])
    L = exact native clamped scalar reaching t2.y
    V.rgb = API0[32:34] + API0[64:66] * (L*t2.y)
    K = API0[68] * Q^2 * H
    MRT0.rgb = V.rgb * K
    MRT0.a = 0

API0[73] and the parallel branch feed MRT1 only.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
SHADER='80CA0CCE';NATIVE='80CA0CD0'
NATIVE_SHA='eda704f5886d7288ca19a2c99a05d7b126bdd160ab2ff3d703f98499bcc6ed03'
GCN_SHA='ec2183266a982dc0427cdbc99bde4899b92b8c1a6a37e59b4b2a339a8fc400c1'
GCN_BYTES=748;EXPECTED_INSTANCES=2;EXPECTED_MATERIALS=2;EXPECTED_TERMINAL='0000000002E0'
ANCHORS=[
 '/*0000000001d4: f09c0300 00020c0c*/ image_sample_lz v[12:13], v[12:15], s[8:15], s[0:3] dmask:3',
 '/*0000000001dc: c2800538         */ s_buffer_load_dwordx4 s[0:3], s[4:7], 0x38',
 '/*0000000001e0: c2440524         */ s_buffer_load_dwordx2 s[8:9], s[4:7], 0x24',
 '/*0000000001e4: c245053c         */ s_buffer_load_dwordx2 s[10:11], s[4:7], 0x3c',
 '/*0000000001f0: c2860520         */ s_buffer_load_dwordx4 s[12:15], s[4:7], 0x20',
 '/*0000000001f4: c2880540         */ s_buffer_load_dwordx4 s[16:19], s[4:7], 0x40',
 '/*000000000208: c2010544         */ s_buffer_load_dword s2, s[4:7], 0x44',
 '/*000000000220: c2008549         */ s_buffer_load_dword s1, s[4:7], 0x49',
 '/*000000000224: d2820803 040c1109*/ v_mad_f32       v3, v9, s8, v3 clamp',
 '/*000000000240: 10060703         */ v_mul_f32       v3, v3, v3',
 '/*000000000244: d2820807 241c1508*/ v_mad_f32       v7, -v8, s10, v7 clamp',
 '/*00000000024c: d2820801 04060105*/ v_mad_f32       v1, v5, v0, v1 clamp',
 '/*00000000025c: 10040f03         */ v_mul_f32       v2, v3, v7',
 '/*000000000264: 10021b01         */ v_mul_f32       v1, v1, v13',
 '/*00000000026c: 7e06020c         */ v_mov_b32       v3, s12',
 '/*000000000270: 7e08020d         */ v_mov_b32       v4, s13',
 '/*000000000274: 7e0a020e         */ v_mov_b32       v5, s14',
 '/*000000000278: 100c0410         */ v_mul_f32       v6, s16, v2',
 '/*00000000027c: 100e0411         */ v_mul_f32       v7, s17, v2',
 '/*000000000280: 10100412         */ v_mul_f32       v8, s18, v2',
 '/*000000000284: 3e060210         */ v_mac_f32       v3, s16, v1',
 '/*000000000288: 3e080211         */ v_mac_f32       v4, s17, v1',
 '/*00000000028c: 3e0a0212         */ v_mac_f32       v5, s18, v1',
 '/*0000000002a0: 10040402         */ v_mul_f32       v2, s2, v2',
 '/*0000000002a4: 10060503         */ v_mul_f32       v3, v3, v2',
 '/*0000000002a8: 10080504         */ v_mul_f32       v4, v4, v2',
 '/*0000000002ac: 10040505         */ v_mul_f32       v2, v5, v2',
 '/*0000000002d8: 5e000903         */ v_cvt_pkrtz_f16_f32 v0, v3, v4',
 '/*0000000002dc: 5e020d02         */ v_cvt_pkrtz_f16_f32 v1, v2, v6',
 '/*0000000002e0: f8001c0f 00000100*/ exp             mrt0, v0, v0, v1, v1 done compr vm',
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
 if any(int((m.get('materials') or {}).get(x,{}).get('ps_texture_count',-1))!=0 for x in mats):v.append('serialized PS texture binding unexpectedly present')
 sr=next((x for x in s.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if s.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or not sr:v.append('shader report not exact/present')
 else:
  for k,z in {'native_shader':NATIVE,'native_sha256':NATIVE_SHA,'gcn_sha256':GCN_SHA,'gcn_bytes':GCN_BYTES}.items():
   if sr.get(k)!=z:v.append(f'{k} drift')
 ir=next((x for x in i.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if i.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT' or not ir:v.append('image usage not exact/present')
 else:
  got=[(x['address'],x['opcode'],[q['texture_index'] for q in x.get('resources',[])],x['dmask_channels']) for x in ir.get('instructions',[])]
  exp=[('000000000040','image_load_mip',[1],'x'),('000000000048','image_sample',[0],'xyzw'),('0000000001D4','image_sample_lz',[2],'xy')]
  if got!=exp:v.append(f'image scope drift {got!r}')
 cr=next((x for x in c.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if c.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or not cr:v.append('cbuffer usage not exact/present')
 else:
  by={x.get('address'):x for x in cr.get('loads',[])}
  expected={'0000000001DC':(0,[56,57,58,59],[0,1,2,3]),'0000000001E0':(0,[36,37],[8,9]),'0000000001E4':(0,[60,61],[10,11]),'0000000001F0':(0,[32,33,34,35],[12,13,14,15]),'0000000001F4':(0,[64,65,66,67],[16,17,18,19]),'000000000208':(0,[68],[2]),'000000000220':(0,[73],[1])}
  for addr,(api,dw,dst) in expected.items():
   q=by.get(addr)
   if not q or q.get('api_slot')!=api or q.get('dword_indices')!=dw or q.get('destination')!=dst:v.append(f'{addr}: cbuffer drift {q}')
 tr=next((x for x in t.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if t.get('status')!='D1_GCN_TERMINAL_MRT0_DEPENDENCY_CENSUS_EXACT' or not tr:v.append('terminal MRT0 slice not exact/present')
 else:
  if tr.get('terminal_mrt0_export_address')!=EXPECTED_TERMINAL or tr.get('terminal_mrt0_operands')!=['v0','v0','v1','v1']:v.append('terminal export drift')
  texreq={(0,x,'000000000048') for x in 'xyz'}|{(1,'x','000000000040'),(2,'y','0000000001D4')}
  for ch,b,mv in [('R',32,64),('G',33,65),('B',34,66)]:
   q=tr['channels'][ch]['value_slice'];tex={(int(x['texture_index']),x['channel'],x['sample_address']) for x in q.get('texture_sample_channels',[])}
   if tex!=texreq:v.append(f'{ch}: texture leaf drift {sorted(tex)}')
   cbq={str(k):set(z) for k,z in (q.get('cbuffer_dwords') or {}).items()};req={b,mv,36,37,60,61,68}
   if set(cbq)-{'0'} or not req.issubset(cbq.get('0',set())):v.append(f'{ch}: cbuffer leaf drift {cbq}')
  aq=tr['channels']['A']['value_slice']
  if aq.get('literals')!=['0'] or aq.get('texture_sample_channels') or aq.get('cbuffer_dwords') or aq.get('unknown_registers'):v.append('alpha drift')
  union=tr.get('mrt0_value_union') or {};alltex={(int(x['texture_index']),x['channel']) for x in union.get('texture_sample_channels',[])}
  if (0,'w') in alltex or (2,'x') in alltex:v.append('dead sampled channel reaches MRT0')
  api0=set((union.get('cbuffer_dwords') or {}).get('0',[]))
  for dead in (35,67,73):
   if dead in api0:v.append(f'API0[{dead}] reaches MRT0')
  if '12' in (union.get('cbuffer_dwords') or {}):v.append('API12 reaches MRT0')
 missing=[x for x in ANCHORS if x not in asm]
 if missing:v.append(f'missing native anchors {missing}')
 out={'schema':'d1_tower_light_80ca0cce_mrt0_factorization/v1','status':'D1_TOWER_LIGHT_80CA0CCE_MRT0_FACTORIZATION_EXACT' if not v else 'D1_TOWER_LIGHT_80CA0CCE_MRT0_FACTORIZATION_PARTIAL','shader':SHADER,'native_shader':NATIVE,'gcn_sha256':GCN_SHA,'instance_count':EXPECTED_INSTANCES,'unique_material_count':len(mats),
 'exact_tail_symbols':{'Q':'clamp(q_in*API0[36]+API0[37])','H':'clamp(-h_in*API0[60]+API0[61])','L':'exact native clamped scalar','B':'API0[32:34].rgb','M':'API0[64:66].rgb','S':'API0[68]','T':'t2.y'},
 'exact_terminal_equation':{'vector_pre_scale':'V.rgb = API0[32:34].rgb + API0[64:66].rgb*(L*t2.y)','scalar_scale':'K = API0[68] * Q^2 * H','mrt0_rgb':'MRT0.rgb = V.rgb * K','mrt0_a':'0','vector_form':'MRT0.rgb = (API0[32:34].rgb + API0[64:66].rgb*(L*t2.y)) * API0[68] * Q^2 * H'},
 'negative_proof':{'t0_alpha_reaches_mrt0':False,'t2_x_reaches_mrt0':False,'api0_dword35_reaches_mrt0':False,'api0_dword67_reaches_mrt0':False,'api0_dword73_reaches_mrt0':False,'api12_reaches_mrt0':False},
 'semantic_boundary':{'terminal_arithmetic':'EXACT_NATIVE_GCN','serialized_ps_texture_bindings':'NONE_FOR_2_FAMILY_MATERIALS','renderer_t0_t1_t2_human_semantics':'WITHHELD'},'violations':v}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'equation':out['exact_terminal_equation'],'violations':v},indent=2));return 0 if not v else 2
if __name__=='__main__':raise SystemExit(main())
