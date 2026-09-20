#!/usr/bin/env python3
"""Fail-closed terminal MRT0 factorization for Tower light PS 80CA10A0.

Exact native arithmetic only:
    Q = clamp(q_in * API0[52] + API0[53])
    H = clamp(-h_in * API0[84] + API0[85])
    L = clamp(l_a*l_b + l_c)
    U = clamp(u_in + 0.5)
    V.rgb = API0[48:50] * U^2 + API0[88:90] * (L * t2.y)
    MRT0.rgb = V.rgb * API0[92] * H * Q^2
    MRT0.a = 0
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
SHADER='80CA10A0';NATIVE='80CA10A1'
NATIVE_SHA='8163c4ef7af4781426ce1e4283018e008034ac11032e841f982c0d814f30fceb'
GCN_SHA='c0a8ebf2b9399e2fdbbfd32075ddee143c11436b218ac98692fa8fee9b8336e3'
GCN_BYTES=1008;EXPECTED_INSTANCES=41;EXPECTED_MATERIALS=31;EXPECTED_TERMINAL='0000000003E4'
ANCHORS=[
 '/*000000000298: f09c0100 00a30312*/ image_sample_lz v3, v[18:21], s[12:19], s[20:23]',
 '/*0000000002a4: f09c0300 01060707*/ image_sample_lz v[7:8], v[7:10], s[24:31], s[32:35] dmask:3',
 '/*0000000002ac: c2860548         */ s_buffer_load_dwordx4 s[12:15], s[4:7], 0x48',
 '/*0000000002b0: c2410534         */ s_buffer_load_dwordx2 s[2:3], s[4:7], 0x34',
 '/*0000000002b4: c2480554         */ s_buffer_load_dwordx2 s[16:17], s[4:7], 0x54',
 '/*0000000002c0: c28a0530         */ s_buffer_load_dwordx4 s[20:23], s[4:7], 0x30',
 '/*0000000002d0: c28c0558         */ s_buffer_load_dwordx4 s[24:27], s[4:7], 0x58',
 '/*0000000002d4: c200855c         */ s_buffer_load_dword s1, s[4:7], 0x5c',
 '/*0000000002d8: c2020561         */ s_buffer_load_dword s4, s[4:7], 0x61',
 '/*000000000318: d2820800 04021305*/ v_mad_f32       v0, v5, v9, v0 clamp',
 '/*00000000032c: d2060809 0001e10c*/ v_add_f32       v9, v12, 0.5 clamp',
 '/*00000000033c: d2820806 04180501*/ v_mad_f32       v6, v1, s2, v6 clamp',
 '/*000000000348: d2820805 2414210a*/ v_mad_f32       v5, -v10, s16, v5 clamp',
 '/*000000000350: 10041309         */ v_mul_f32       v2, v9, v9',
 '/*00000000035c: 10080d06         */ v_mul_f32       v4, v6, v6',
 '/*000000000364: 10001100         */ v_mul_f32       v0, v0, v8',
 '/*00000000036c: 100c0414         */ v_mul_f32       v6, s20, v2',
 '/*000000000370: 100e0415         */ v_mul_f32       v7, s21, v2',
 '/*000000000374: 10040416         */ v_mul_f32       v2, s22, v2',
 '/*000000000384: 10080905         */ v_mul_f32       v4, v5, v4',
 '/*000000000388: 3e0c0018         */ v_mac_f32       v6, s24, v0',
 '/*00000000038c: 3e0e0019         */ v_mac_f32       v7, s25, v0',
 '/*000000000390: 3e04001a         */ v_mac_f32       v2, s26, v0',
 '/*0000000003a0: 10000801         */ v_mul_f32       v0, s1, v4',
 '/*0000000003a8: 10080106         */ v_mul_f32       v4, v6, v0',
 '/*0000000003ac: 100a0107         */ v_mul_f32       v5, v7, v0',
 '/*0000000003b0: 10000102         */ v_mul_f32       v0, v2, v0',
 '/*0000000003c0: 7e060280         */ v_mov_b32       v3, 0',
 '/*0000000003dc: 5e020b04         */ v_cvt_pkrtz_f16_f32 v1, v4, v5',
 '/*0000000003e0: 5e000700         */ v_cvt_pkrtz_f16_f32 v0, v0, v3',
 '/*0000000003e4: f8001c0f 00000001*/ exp             mrt0, v1, v1, v0, v0 done compr vm',
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
  exp=[('000000000040','image_load_mip',[1],'x'),('000000000048','image_sample',[0],'xyzw'),('000000000298','image_sample_lz',[3],'x'),('0000000002A4','image_sample_lz',[2],'xy')]
  if got!=exp:v.append(f'image instruction scope drift {got!r}')
 cr=next((x for x in c.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if c.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or not cr:v.append('cbuffer usage not exact/present')
 else:
  by={x.get('address'):x for x in cr.get('loads',[])}
  expected={'0000000002AC':(0,[72,73,74,75],[12,13,14,15]),'0000000002B0':(0,[52,53],[2,3]),'0000000002B4':(0,[84,85],[16,17]),'0000000002C0':(0,[48,49,50,51],[20,21,22,23]),'0000000002D0':(0,[88,89,90,91],[24,25,26,27]),'0000000002D4':(0,[92],[1]),'0000000002D8':(0,[97],[4])}
  for addr,(api,dw,dst) in expected.items():
   q=by.get(addr)
   if not q or q.get('api_slot')!=api or q.get('dword_indices')!=dw or q.get('destination')!=dst:v.append(f'{addr}: cbuffer provenance drift {q}')
 tr=next((x for x in t.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if t.get('status')!='D1_GCN_TERMINAL_MRT0_DEPENDENCY_CENSUS_EXACT' or not tr:v.append('terminal MRT0 slice not exact/present')
 else:
  if tr.get('terminal_mrt0_export_address')!=EXPECTED_TERMINAL or not tr.get('terminal_mrt0_compressed'):v.append('terminal export identity drift')
  if tr.get('terminal_mrt0_operands')!=['v1','v1','v0','v0']:v.append('terminal operands drift')
  family={(0,x,'000000000048') for x in 'xyz'}|{(1,'x','000000000040'),(2,'y','0000000002A4')}
  for ch,b,mx in [('R',48,88),('G',49,89),('B',50,90)]:
   q=tr['channels'][ch]['value_slice'];tex={(int(x['texture_index']),x['channel'],x['sample_address']) for x in q.get('texture_sample_channels',[])}
   if tex!=family:v.append(f'{ch}: terminal texture leaf drift {sorted(tex)}')
   cb={str(k):set(z) for k,z in q.get('cbuffer_dwords',{}).items()}
   if set(cb)-{'0'}:v.append(f'{ch}: unexpected non-API0 MRT0 cbuffer leaves {cb}')
   required={b,mx,52,53,72,73,74,84,85,92}
   if not required.issubset(cb.get('0',set())):v.append(f'{ch}: terminal coefficient leaves missing {sorted(required-cb.get("0",set()))}')
   if 51 in cb.get('0',set()) or 75 in cb.get('0',set()) or 91 in cb.get('0',set()) or 97 in cb.get('0',set()):v.append(f'{ch}: non-MRT0 coefficient leaked into MRT0 {cb}')
  aq=tr['channels']['A']['value_slice']
  if aq.get('literals')!=['0'] or aq.get('texture_sample_channels') or aq.get('cbuffer_dwords') or aq.get('unknown_registers'):v.append(f'alpha is not exact zero-only {aq}')
  union=tr.get('mrt0_value_union') or {};alltex={(int(x['texture_index']),x['channel']) for x in union.get('texture_sample_channels',[])}
  if (0,'w') in alltex or (2,'x') in alltex or any(ti==3 for ti,_ in alltex):v.append(f'dead sampled channel/resource reached MRT0 unexpectedly {sorted(alltex)}')
  if '12' in (union.get('cbuffer_dwords') or {}):v.append('API12 unexpectedly reaches MRT0')
 missing=[x for x in ANCHORS if x not in asm]
 if missing:v.append(f'missing exact native anchors {missing}')
 out={'schema':'d1_tower_light_80ca10a0_mrt0_factorization/v1','status':'D1_TOWER_LIGHT_80CA10A0_MRT0_FACTORIZATION_EXACT' if not v else 'D1_TOWER_LIGHT_80CA10A0_MRT0_FACTORIZATION_PARTIAL','shader':SHADER,'native_shader':NATIVE,'gcn_sha256':GCN_SHA,'instance_count':EXPECTED_INSTANCES,'unique_material_count':len(mats),
 'exact_tail_symbols':{'Q':'v6 after 0x33C = clamp(q_in*API0[52]+API0[53])','H':'v5 after 0x348 = clamp(-h_in*API0[84]+API0[85])','L':'v0 after 0x318 = clamp(l_a*l_b+l_c)','U':'v9 after 0x32C = clamp(u_in+0.5)','B':'API0[48:50].rgb','M':'API0[88:90].rgb','S':'API0[92]','T':'t2.y'},
 'exact_terminal_equation':{'vector_pre_scale':'V.rgb = API0[48:50].rgb*U^2 + API0[88:90].rgb*(L*t2.y)','scalar_scale':'K = API0[92] * H * Q^2','mrt0_rgb':'MRT0.rgb = V.rgb * K','mrt0_a':'0','vector_form':'MRT0.rgb = (API0[48:50].rgb*U^2 + API0[88:90].rgb*(L*t2.y)) * API0[92] * H * Q^2'},
 'negative_proof':{'t0_alpha_reaches_mrt0':False,'t2_x_reaches_mrt0':False,'t3_reaches_mrt0':False,'api0_dword51_reaches_mrt0':False,'api0_dword75_reaches_mrt0':False,'api0_dword91_reaches_mrt0':False,'api0_dword97_reaches_mrt0':False,'api12_reaches_mrt0':False},
 'semantic_boundary':{'terminal_arithmetic':'EXACT_NATIVE_GCN','serialized_ps_texture_bindings':'NONE_FOR_31_FAMILY_MATERIALS','renderer_t0_t1_t2_t3_human_semantics':'WITHHELD','symbols_Q_H_L_U_human_semantics':'WITHHELD','portable_light_model_mapping':'WITHHELD'},'violations':v,'policy':'Exact native GCN arithmetic only; renderer inputs and native symbolic intermediates remain semantically unnamed without primary evidence.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'equation':out['exact_terminal_equation'],'negative_proof':out['negative_proof'],'violations':v},indent=2));return 0 if not v else 2
if __name__=='__main__':raise SystemExit(main())
