#!/usr/bin/env python3
"""Fail-closed terminal MRT0 factorization for Tower light PS 80CA0295.

Exact terminal form:
    Q = clamp(q_in * API0[48] + API0[49])
    H = exact clamped native scalar ending at 0x2E4, including API0[68:70,72:73]
    L = exact native clamped scalar reaching t2.y
    P = clamp(p_native + 0.5)^2
    V.rgb = API0[44:46] + API0[76:78]*(L*t2.y) + API0[40:42]*P
    K = API0[80] * Q^2 * H
    MRT0.rgb = V.rgb * K
    MRT0.a = 0

The t3.x sample and API0[85] branch are MRT1-only.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
SHADER='80CA0295';NATIVE='80CA02E9'
NATIVE_SHA='c011b3c6502dc6744cb66b304e119072b71382624f56a14c859eb7521bdf7854'
GCN_SHA='3da11b06e5e8cf55238fff7dc463b7a520235ef5132c1f8b19a6580bd35b9219'
GCN_BYTES=928;EXPECTED_INSTANCES=2;EXPECTED_MATERIALS=2;EXPECTED_TERMINAL='000000000394'
ANCHORS=[
 '/*000000000234: f09c0300 00a31113*/ image_sample_lz v[17:18], v[19:22], s[12:19], s[20:23] dmask:3',
 '/*000000000244: f09c0100 01060213*/ image_sample_lz v2, v[19:22], s[24:31], s[32:35]',
 '/*00000000024c: c2860544         */ s_buffer_load_dwordx4 s[12:15], s[4:7], 0x44',
 '/*000000000250: c2410530         */ s_buffer_load_dwordx2 s[2:3], s[4:7], 0x30',
 '/*000000000254: c2480548         */ s_buffer_load_dwordx2 s[16:17], s[4:7], 0x48',
 '/*000000000258: c28a052c         */ s_buffer_load_dwordx4 s[20:23], s[4:7], 0x2c',
 '/*000000000260: c28c054c         */ s_buffer_load_dwordx4 s[24:27], s[4:7], 0x4c',
 '/*000000000264: c28e0528         */ s_buffer_load_dwordx4 s[28:31], s[4:7], 0x28',
 '/*000000000274: c2008550         */ s_buffer_load_dword s1, s[4:7], 0x50',
 '/*000000000278: c2020555         */ s_buffer_load_dword s4, s[4:7], 0x55',
 '/*0000000002b8: d2820807 041c0509*/ v_mad_f32       v7, v9, s2, v7 clamp',
 '/*0000000002c8: d2820801 04060105*/ v_mad_f32       v1, v5, v0, v1 clamp',
 '/*0000000002e0: 100a0f07         */ v_mul_f32       v5, v7, v7',
 '/*0000000002e4: d2820806 2418210a*/ v_mad_f32       v6, -v10, s16, v6 clamp',
 '/*0000000002f4: 10022501         */ v_mul_f32       v1, v1, v18',
 '/*0000000002f8: 7e0e0214         */ v_mov_b32       v7, s20',
 '/*0000000002fc: 7e100215         */ v_mov_b32       v8, s21',
 '/*000000000300: 7e120216         */ v_mov_b32       v9, s22',
 '/*000000000304: d2060804 0001e104*/ v_add_f32       v4, v4, 0.5 clamp',
 '/*000000000318: 3e0e0218         */ v_mac_f32       v7, s24, v1',
 '/*00000000031c: 3e100219         */ v_mac_f32       v8, s25, v1',
 '/*000000000320: 3e12021a         */ v_mac_f32       v9, s26, v1',
 '/*000000000324: 10020904         */ v_mul_f32       v1, v4, v4',
 '/*000000000338: 3e0e021c         */ v_mac_f32       v7, s28, v1',
 '/*00000000033c: 3e10021d         */ v_mac_f32       v8, s29, v1',
 '/*000000000340: 3e12021e         */ v_mac_f32       v9, s30, v1',
 '/*000000000350: 10000a01         */ v_mul_f32       v0, s1, v5',
 '/*000000000358: 100a0107         */ v_mul_f32       v5, v7, v0',
 '/*00000000035c: 100c0108         */ v_mul_f32       v6, v8, v0',
 '/*000000000360: 10000109         */ v_mul_f32       v0, v9, v0',
 '/*00000000038c: 5e020d05         */ v_cvt_pkrtz_f16_f32 v1, v5, v6',
 '/*000000000390: 5e000500         */ v_cvt_pkrtz_f16_f32 v0, v0, v2',
 '/*000000000394: f8001c0f 00000001*/ exp             mrt0, v1, v1, v0, v0 done compr vm',
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
  exp=[('000000000040','image_load_mip',[1],'x'),('000000000048','image_sample',[0],'xyzw'),('000000000234','image_sample_lz',[2],'xy'),('000000000244','image_sample_lz',[3],'x')]
  if got!=exp:v.append(f'image scope drift {got!r}')
 cr=next((x for x in c.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if c.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or not cr:v.append('cbuffer usage not exact/present')
 else:
  by={x.get('address'):x for x in cr.get('loads',[])}
  expected={'00000000024C':(0,[68,69,70,71],[12,13,14,15]),'000000000250':(0,[48,49],[2,3]),'000000000254':(0,[72,73],[16,17]),'000000000258':(0,[44,45,46,47],[20,21,22,23]),'000000000260':(0,[76,77,78,79],[24,25,26,27]),'000000000264':(0,[40,41,42,43],[28,29,30,31]),'000000000274':(0,[80],[1]),'000000000278':(0,[85],[4])}
  for addr,(api,dw,dst) in expected.items():
   q=by.get(addr)
   if not q or q.get('api_slot')!=api or q.get('dword_indices')!=dw or q.get('destination')!=dst:v.append(f'{addr}: cbuffer drift {q}')
 tr=next((x for x in t.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if t.get('status')!='D1_GCN_TERMINAL_MRT0_DEPENDENCY_CENSUS_EXACT' or not tr:v.append('terminal MRT0 slice not exact/present')
 else:
  if tr.get('terminal_mrt0_export_address')!=EXPECTED_TERMINAL or tr.get('terminal_mrt0_operands')!=['v1','v1','v0','v0']:v.append('terminal export drift')
  reqtex={(0,x,'000000000048') for x in 'xyz'}|{(1,'x','000000000040'),(2,'y','000000000234')}
  for ch,b,mv,p in [('R',44,76,40),('G',45,77,41),('B',46,78,42)]:
   q=tr['channels'][ch]['value_slice'];tex={(int(x['texture_index']),x['channel'],x['sample_address']) for x in q.get('texture_sample_channels',[])}
   if tex!=reqtex:v.append(f'{ch}: texture leaf drift {sorted(tex)}')
   cbq={str(k):set(z) for k,z in (q.get('cbuffer_dwords') or {}).items()};req={b,mv,p,48,49,68,69,70,72,73,80}
   if set(cbq)-{'0'} or not req.issubset(cbq.get('0',set())):v.append(f'{ch}: cbuffer leaf drift {cbq}')
  aq=tr['channels']['A']['value_slice']
  if aq.get('literals')!=['0'] or aq.get('texture_sample_channels') or aq.get('cbuffer_dwords') or aq.get('unknown_registers'):v.append('alpha drift')
  union=tr.get('mrt0_value_union') or {};alltex={(int(x['texture_index']),x['channel']) for x in union.get('texture_sample_channels',[])}
  if any(ti==3 for ti,_ in alltex):v.append('t3 unexpectedly reaches MRT0')
  if (0,'w') in alltex or (2,'x') in alltex:v.append('dead sampled channel reaches MRT0')
  api0=set((union.get('cbuffer_dwords') or {}).get('0',[]))
  for dead in (43,47,71,79,85):
   if dead in api0:v.append(f'API0[{dead}] reaches MRT0')
  if '12' in (union.get('cbuffer_dwords') or {}):v.append('API12 reaches MRT0')
 missing=[x for x in ANCHORS if x not in asm]
 if missing:v.append(f'missing native anchors {missing}')
 out={'schema':'d1_tower_light_80ca0295_mrt0_factorization/v1','status':'D1_TOWER_LIGHT_80CA0295_MRT0_FACTORIZATION_EXACT' if not v else 'D1_TOWER_LIGHT_80CA0295_MRT0_FACTORIZATION_PARTIAL','shader':SHADER,'native_shader':NATIVE,'gcn_sha256':GCN_SHA,'instance_count':EXPECTED_INSTANCES,'unique_material_count':len(mats),
 'exact_tail_symbols':{'Q':'clamp(q_in*API0[48]+API0[49])','H':'exact clamped native scalar including API0[68:70,72:73]','L':'exact native clamped scalar','P':'clamp(p_native+0.5)^2','B':'API0[44:46].rgb','M':'API0[76:78].rgb','R':'API0[40:42].rgb','S':'API0[80]','T':'t2.y'},
 'exact_terminal_equation':{'vector_pre_scale':'V.rgb = API0[44:46].rgb + API0[76:78].rgb*(L*t2.y) + API0[40:42].rgb*P','scalar_scale':'K = API0[80] * Q^2 * H','mrt0_rgb':'MRT0.rgb = V.rgb * K','mrt0_a':'0','vector_form':'MRT0.rgb = (API0[44:46].rgb + API0[76:78].rgb*(L*t2.y) + API0[40:42].rgb*P) * API0[80] * Q^2 * H'},
 'negative_proof':{'t3_x_reaches_mrt0':False,'t0_alpha_reaches_mrt0':False,'t2_x_reaches_mrt0':False,'api0_dword43_reaches_mrt0':False,'api0_dword47_reaches_mrt0':False,'api0_dword71_reaches_mrt0':False,'api0_dword79_reaches_mrt0':False,'api0_dword85_reaches_mrt0':False,'api12_reaches_mrt0':False},
 'semantic_boundary':{'terminal_arithmetic':'EXACT_NATIVE_GCN','serialized_ps_texture_bindings':'NONE_FOR_2_FAMILY_MATERIALS','renderer_t0_t1_t2_t3_human_semantics':'WITHHELD','symbols_Q_H_L_P_human_semantics':'WITHHELD'},'violations':v}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'equation':out['exact_terminal_equation'],'violations':v},indent=2));return 0 if not v else 2
if __name__=='__main__':raise SystemExit(main())
