#!/usr/bin/env python3
"""Fail-closed terminal MRT0 factorization for Tower light PS 80CA0636.

Exact native arithmetic only:
    Q = clamp(q_in * API0[44] + API0[45])
    H = clamp(-h_in * API0[68] + API0[69])
    L = clamp(l_a*l_b + l_c)
    U = clamp(u_in + 0.5)
    V.rgb = API0[40:42] * U^2 + API0[72:74] * (L * t2.y)
    MRT0.rgb = V.rgb * API0[76] * Q^2 * H
    MRT0.a = 0
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
SHADER='80CA0636';NATIVE='80CA076B'
NATIVE_SHA='85ba53d04390e6700e540c77480343f16bc519b70a1a71821bc282f30e8086fa'
GCN_SHA='b6937ad149ce2131d2daec283332ffb37d93ca9bfed65371e1989718749fbacb'
GCN_BYTES=912;EXPECTED_INSTANCES=41;EXPECTED_MATERIALS=23;EXPECTED_TERMINAL='000000000384'
ANCHORS=[
 '/*000000000238: f09c0100 00a30212*/ image_sample_lz v2, v[18:21], s[12:19], s[20:23]',
 '/*000000000244: f09c0300 01060c0c*/ image_sample_lz v[12:13], v[12:15], s[24:31], s[32:35] dmask:3',
 '/*00000000024c: c2860540         */ s_buffer_load_dwordx4 s[12:15], s[4:7], 0x40',
 '/*000000000250: c241052c         */ s_buffer_load_dwordx2 s[2:3], s[4:7], 0x2c',
 '/*000000000254: c2480544         */ s_buffer_load_dwordx2 s[16:17], s[4:7], 0x44',
 '/*000000000260: c28a0528         */ s_buffer_load_dwordx4 s[20:23], s[4:7], 0x28',
 '/*000000000270: c28c0548         */ s_buffer_load_dwordx4 s[24:27], s[4:7], 0x48',
 '/*000000000274: c200854c         */ s_buffer_load_dword s1, s[4:7], 0x4c',
 '/*000000000278: c2020551         */ s_buffer_load_dword s4, s[4:7], 0x51',
 '/*0000000002b8: d282080b 042c0509*/ v_mad_f32       v11, v9, s2, v11 clamp',
 '/*0000000002c8: d2820801 04060105*/ v_mad_f32       v1, v5, v0, v1 clamp',
 '/*0000000002d4: d2060803 0001e107*/ v_add_f32       v3, v7, 0.5 clamp',
 '/*0000000002e4: 100c170b         */ v_mul_f32       v6, v11, v11',
 '/*0000000002e8: d2820804 2410210a*/ v_mad_f32       v4, -v10, s16, v4 clamp',
 '/*0000000002f4: 10060703         */ v_mul_f32       v3, v3, v3',
 '/*000000000304: 10021b01         */ v_mul_f32       v1, v1, v13',
 '/*00000000030c: 100a0614         */ v_mul_f32       v5, s20, v3',
 '/*000000000310: 100e0615         */ v_mul_f32       v7, s21, v3',
 '/*000000000314: 10060616         */ v_mul_f32       v3, s22, v3',
 '/*000000000324: 10080906         */ v_mul_f32       v4, v6, v4',
 '/*000000000328: 3e0a0218         */ v_mac_f32       v5, s24, v1',
 '/*00000000032c: 3e0e0219         */ v_mac_f32       v7, s25, v1',
 '/*000000000330: 3e06021a         */ v_mac_f32       v3, s26, v1',
 '/*000000000340: 10000801         */ v_mul_f32       v0, s1, v4',
 '/*000000000348: 10080105         */ v_mul_f32       v4, v5, v0',
 '/*00000000034c: 100a0107         */ v_mul_f32       v5, v7, v0',
 '/*000000000350: 10000103         */ v_mul_f32       v0, v3, v0',
 '/*000000000360: 7e040280         */ v_mov_b32       v2, 0',
 '/*00000000037c: 5e020b04         */ v_cvt_pkrtz_f16_f32 v1, v4, v5',
 '/*000000000380: 5e000500         */ v_cvt_pkrtz_f16_f32 v0, v0, v2',
 '/*000000000384: f8001c0f 00000001*/ exp             mrt0, v1, v1, v0, v0 done compr vm',
]
def norm(x):return str(x).upper().removeprefix('0X').zfill(8)
def main()->int:
 ap=argparse.ArgumentParser()
 for n in ('material-manifest','shader-report','image-usage','cbuffer-usage','terminal-mrt0','disasm','out'):ap.add_argument('--'+n,type=Path,required=True)
 a=ap.parse_args();v=[];m=json.loads(a.material_manifest.read_text());s=json.loads(a.shader_report.read_text());i=json.loads(a.image_usage.read_text());c=json.loads(a.cbuffer_usage.read_text());t=json.loads(a.terminal_mrt0.read_text());asm=a.disasm.read_text(errors='replace')
 if m.get('status')!='D1_WORLD_LIGHT_MATERIAL_MANIFEST_COMPLETE':v.append('material manifest not exact')
 if int((m.get('pixel_shader_frequency') or {}).get(SHADER,-1))!=EXPECTED_INSTANCES:v.append('instance count drift')
 mats=(m.get('pixel_shader_materials') or {}).get(SHADER,[])
 if len(mats)!=EXPECTED_MATERIALS:v.append(f'unique material count drift {len(mats)} != {EXPECTED_MATERIALS}')
 if any(int((m.get('materials') or {}).get(x,{}).get('ps_texture_count',-1))!=0 for x in mats):v.append('serialized PS texture binding unexpectedly present')
 sr=next((x for x in s.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if s.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or not sr:v.append('shader report not exact/present')
 else:
  for k,z in {'native_shader':NATIVE,'native_sha256':NATIVE_SHA,'gcn_sha256':GCN_SHA,'gcn_bytes':GCN_BYTES}.items():
   if sr.get(k)!=z:v.append(f'{k} drift {sr.get(k)!r} != {z!r}')
 ir=next((x for x in i.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if i.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT' or not ir:v.append('image usage not exact/present')
 else:
  got=[(x['address'],x['opcode'],[q['texture_index'] for q in x.get('resources',[])],x['dmask_channels']) for x in ir.get('instructions',[])]
  exp=[('000000000040','image_load_mip',[1],'x'),('000000000048','image_sample',[0],'xyzw'),('000000000238','image_sample_lz',[3],'x'),('000000000244','image_sample_lz',[2],'xy')]
  if got!=exp:v.append(f'image instruction scope drift {got!r}')
 cr=next((x for x in c.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if c.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or not cr:v.append('cbuffer usage not exact/present')
 else:
  by={x.get('address'):x for x in cr.get('loads',[])}
  expected={'00000000024C':(0,[64,65,66,67],[12,13,14,15]),'000000000250':(0,[44,45],[2,3]),'000000000254':(0,[68,69],[16,17]),'000000000260':(0,[40,41,42,43],[20,21,22,23]),'000000000270':(0,[72,73,74,75],[24,25,26,27]),'000000000274':(0,[76],[1]),'000000000278':(0,[81],[4])}
  for addr,(api,dw,dst) in expected.items():
   q=by.get(addr)
   if not q or q.get('api_slot')!=api or q.get('dword_indices')!=dw or q.get('destination')!=dst:v.append(f'{addr}: cbuffer provenance drift {q}')
 tr=next((x for x in t.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if t.get('status')!='D1_GCN_TERMINAL_MRT0_DEPENDENCY_CENSUS_EXACT' or not tr:v.append('terminal MRT0 slice not exact/present')
 else:
  if tr.get('terminal_mrt0_export_address')!=EXPECTED_TERMINAL or not tr.get('terminal_mrt0_compressed'):v.append('terminal export identity drift')
  if tr.get('terminal_mrt0_operands')!=['v1','v1','v0','v0']:v.append('terminal operands drift')
  family={(0,x,'000000000048') for x in 'xyz'}|{(1,'x','000000000040'),(2,'y','000000000244')}
  for ch,b,mx in [('R',40,72),('G',41,73),('B',42,74)]:
   q=tr['channels'][ch]['value_slice'];tex={(int(x['texture_index']),x['channel'],x['sample_address']) for x in q.get('texture_sample_channels',[])}
   if tex!=family:v.append(f'{ch}: terminal texture leaf drift {sorted(tex)}')
   cb={str(k):set(z) for k,z in q.get('cbuffer_dwords',{}).items()}
   if set(cb)-{'0'}:v.append(f'{ch}: unexpected non-API0 MRT0 cbuffer leaves {cb}')
   required={b,mx,44,45,64,65,66,68,69,76}
   if not required.issubset(cb.get('0',set())):v.append(f'{ch}: terminal coefficient leaves missing {sorted(required-cb.get("0",set()))}')
   if 43 in cb.get('0',set()) or 67 in cb.get('0',set()) or 75 in cb.get('0',set()) or 81 in cb.get('0',set()):v.append(f'{ch}: non-MRT0 coefficient leaked into MRT0 {cb}')
  aq=tr['channels']['A']['value_slice']
  if aq.get('literals')!=['0'] or aq.get('texture_sample_channels') or aq.get('cbuffer_dwords') or aq.get('unknown_registers'):v.append(f'alpha is not exact zero-only {aq}')
  union=tr.get('mrt0_value_union') or {};alltex={(int(x['texture_index']),x['channel']) for x in union.get('texture_sample_channels',[])}
  if (0,'w') in alltex or (2,'x') in alltex or any(ti==3 for ti,_ in alltex):v.append(f'dead sampled channel/resource reached MRT0 unexpectedly {sorted(alltex)}')
  if '12' in (union.get('cbuffer_dwords') or {}):v.append('API12 unexpectedly reaches MRT0')
 missing=[x for x in ANCHORS if x not in asm]
 if missing:v.append(f'missing exact native anchors {missing}')
 out={'schema':'d1_tower_light_80ca0636_mrt0_factorization/v1','status':'D1_TOWER_LIGHT_80CA0636_MRT0_FACTORIZATION_EXACT' if not v else 'D1_TOWER_LIGHT_80CA0636_MRT0_FACTORIZATION_PARTIAL','shader':SHADER,'native_shader':NATIVE,'gcn_sha256':GCN_SHA,'instance_count':EXPECTED_INSTANCES,'unique_material_count':len(mats),
 'exact_tail_symbols':{'Q':'v11 after 0x2B8 = clamp(q_in*API0[44]+API0[45])','H':'v4 after 0x2E8 = clamp(-h_in*API0[68]+API0[69])','L':'v1 after 0x2C8 = clamp(l_a*l_b+l_c)','U':'v3 after 0x2D4 = clamp(u_in+0.5)','B':'API0[40:42].rgb','M':'API0[72:74].rgb','S':'API0[76]','T':'t2.y'},
 'exact_terminal_equation':{'vector_pre_scale':'V.rgb = API0[40:42].rgb*U^2 + API0[72:74].rgb*(L*t2.y)','scalar_scale':'K = API0[76] * Q^2 * H','mrt0_rgb':'MRT0.rgb = V.rgb * K','mrt0_a':'0','vector_form':'MRT0.rgb = (API0[40:42].rgb*U^2 + API0[72:74].rgb*(L*t2.y)) * API0[76] * Q^2 * H'},
 'negative_proof':{'t0_alpha_reaches_mrt0':False,'t2_x_reaches_mrt0':False,'t3_reaches_mrt0':False,'api0_dword43_reaches_mrt0':False,'api0_dword67_reaches_mrt0':False,'api0_dword75_reaches_mrt0':False,'api0_dword81_reaches_mrt0':False,'api12_reaches_mrt0':False},
 'semantic_boundary':{'terminal_arithmetic':'EXACT_NATIVE_GCN','serialized_ps_texture_bindings':'NONE_FOR_23_FAMILY_MATERIALS','renderer_t0_t1_t2_t3_human_semantics':'WITHHELD','symbols_Q_H_L_U_human_semantics':'WITHHELD','portable_light_model_mapping':'WITHHELD'},'violations':v,'policy':'Exact native GCN arithmetic only; renderer inputs and native symbolic intermediates remain semantically unnamed without primary evidence.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'equation':out['exact_terminal_equation'],'negative_proof':out['negative_proof'],'violations':v},indent=2));return 0 if not v else 2
if __name__=='__main__':raise SystemExit(main())
