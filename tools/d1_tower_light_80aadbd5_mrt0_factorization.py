#!/usr/bin/env python3
"""Fail-closed terminal MRT0 factorization for Tower light PS 80AADBD5.

Exact native terminal form:
    Q = clamp(q_in * API0[44] + API0[45])
    P = clamp(p_native + 0.5)^2
    L = exact native clamped scalar reaching t2.y modulation
    V.rgb = API0[40:42] * P + API0[64:66] * (L*t2.y)
    K = API0[68] * Q^2
    MRT0.rgb = V.rgb * K
    MRT0.a = 0

The sampled t3.x branch is confined to MRT1.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
SHADER='80AADBD5';NATIVE='80AADBD6'
NATIVE_SHA='ed917fa1087a5dcbee3ce40923be3773ff2a02e2198cdb634a399c1e8caf5072'
GCN_SHA='c7848f035104d669e467df4c1ee0060f41e844fcaba962a48dc96003d2c7195b'
GCN_BYTES=876;EXPECTED_INSTANCES=2;EXPECTED_MATERIALS=2;EXPECTED_TERMINAL='000000000360'
ANCHORS=[
 '/*000000000238: f09c0100 00a30212*/ image_sample_lz v2, v[18:21], s[12:19], s[20:23]',
 '/*000000000244: f09c0300 01060c0c*/ image_sample_lz v[12:13], v[12:15], s[24:31], s[32:35] dmask:3',
 '/*00000000024c: c241052c         */ s_buffer_load_dwordx2 s[2:3], s[4:7], 0x2c',
 '/*000000000258: c2860528         */ s_buffer_load_dwordx4 s[12:15], s[4:7], 0x28',
 '/*000000000268: c2880540         */ s_buffer_load_dwordx4 s[16:19], s[4:7], 0x40',
 '/*00000000026c: c2008544         */ s_buffer_load_dword s1, s[4:7], 0x44',
 '/*000000000270: c2020549         */ s_buffer_load_dword s4, s[4:7], 0x49',
 '/*000000000284: d2200007 78000000*/ v_max_f32       v7, -s0, -s0 div:2',
 '/*0000000002a8: d2820801 04060105*/ v_mad_f32       v1, v5, v0, v1 clamp',
 '/*0000000002b4: d2060803 0001e107*/ v_add_f32       v3, v7, 0.5 clamp',
 '/*0000000002c4: d2820804 04100509*/ v_mad_f32       v4, v9, s2, v4 clamp',
 '/*0000000002d0: 10060703         */ v_mul_f32       v3, v3, v3',
 '/*0000000002dc: 10080904         */ v_mul_f32       v4, v4, v4',
 '/*0000000002e4: 10021b01         */ v_mul_f32       v1, v1, v13',
 '/*0000000002ec: 100a060c         */ v_mul_f32       v5, s12, v3',
 '/*0000000002f0: 100c060d         */ v_mul_f32       v6, s13, v3',
 '/*0000000002f4: 1006060e         */ v_mul_f32       v3, s14, v3',
 '/*000000000304: 3e0a0210         */ v_mac_f32       v5, s16, v1',
 '/*000000000308: 3e0c0211         */ v_mac_f32       v6, s17, v1',
 '/*00000000030c: 3e060212         */ v_mac_f32       v3, s18, v1',
 '/*00000000031c: 10000801         */ v_mul_f32       v0, s1, v4',
 '/*000000000324: 10080105         */ v_mul_f32       v4, v5, v0',
 '/*000000000328: 100a0106         */ v_mul_f32       v5, v6, v0',
 '/*00000000032c: 10000103         */ v_mul_f32       v0, v3, v0',
 '/*000000000358: 5e020b04         */ v_cvt_pkrtz_f16_f32 v1, v4, v5',
 '/*00000000035c: 5e000500         */ v_cvt_pkrtz_f16_f32 v0, v0, v2',
 '/*000000000360: f8001c0f 00000001*/ exp             mrt0, v1, v1, v0, v0 done compr vm',
]
def norm(x):return str(x).upper().removeprefix('0X').zfill(8)
def main()->int:
 ap=argparse.ArgumentParser()
 for n in ('material-manifest','shader-report','image-usage','cbuffer-usage','terminal-mrt0','disasm','out'):ap.add_argument('--'+n,type=Path,required=True)
 a=ap.parse_args();v=[]
 m=json.loads(a.material_manifest.read_text());s=json.loads(a.shader_report.read_text());i=json.loads(a.image_usage.read_text());c=json.loads(a.cbuffer_usage.read_text());t=json.loads(a.terminal_mrt0.read_text());asm=a.disasm.read_text(errors='replace')
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
  exp=[('000000000040','image_load_mip',[1],'x'),('000000000048','image_sample',[0],'xyzw'),('000000000238','image_sample_lz',[3],'x'),('000000000244','image_sample_lz',[2],'xy')]
  if got!=exp:v.append(f'image instruction scope drift {got!r}')
 cr=next((x for x in c.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if c.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or not cr:v.append('cbuffer usage not exact/present')
 else:
  by={x.get('address'):x for x in cr.get('loads',[])}
  expected={'00000000024C':(0,[44,45],[2,3]),'000000000258':(0,[40,41,42,43],[12,13,14,15]),'000000000268':(0,[64,65,66,67],[16,17,18,19]),'00000000026C':(0,[68],[1]),'000000000270':(0,[73],[4])}
  for addr,(api,dw,dst) in expected.items():
   q=by.get(addr)
   if not q or q.get('api_slot')!=api or q.get('dword_indices')!=dw or q.get('destination')!=dst:v.append(f'{addr}: cbuffer provenance drift {q}')
 tr=next((x for x in t.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if t.get('status')!='D1_GCN_TERMINAL_MRT0_DEPENDENCY_CENSUS_EXACT' or not tr:v.append('terminal MRT0 slice not exact/present')
 else:
  if tr.get('terminal_mrt0_export_address')!=EXPECTED_TERMINAL or not tr.get('terminal_mrt0_compressed'):v.append('terminal export identity drift')
  if tr.get('terminal_mrt0_operands')!=['v1','v1','v0','v0']:v.append('terminal operands drift')
  required_tex={(0,x,'000000000048') for x in 'xyz'}|{(1,'x','000000000040'),(2,'y','000000000244')}
  for ch,pcoef,mod in [('R',40,64),('G',41,65),('B',42,66)]:
   q=tr['channels'][ch]['value_slice'];tex={(int(x['texture_index']),x['channel'],x['sample_address']) for x in q.get('texture_sample_channels',[])}
   if tex!=required_tex:v.append(f'{ch}: terminal texture leaf drift {sorted(tex)}')
   cbq={str(k):set(z) for k,z in (q.get('cbuffer_dwords') or {}).items()}
   if set(cbq)-{'0'}:v.append(f'{ch}: unexpected non-API0 leaves')
   required={pcoef,mod,44,45,68}
   if not required.issubset(cbq.get('0',set())):v.append(f'{ch}: terminal coefficient leaves missing {sorted(required-cbq.get("0",set()))}')
  aq=tr['channels']['A']['value_slice']
  if aq.get('literals')!=['0'] or aq.get('texture_sample_channels') or aq.get('cbuffer_dwords') or aq.get('unknown_registers'):v.append('alpha is not exact zero-only')
  union=tr.get('mrt0_value_union') or {};alltex={(int(x['texture_index']),x['channel']) for x in union.get('texture_sample_channels',[])}
  if any(ti==3 for ti,_ in alltex):v.append(f't3 unexpectedly reaches MRT0 {sorted(alltex)}')
  if (0,'w') in alltex or (2,'x') in alltex:v.append(f'dead sampled channel reached MRT0 {sorted(alltex)}')
  api0=set((union.get('cbuffer_dwords') or {}).get('0',[]))
  for dead in (43,67,73):
   if dead in api0:v.append(f'API0[{dead}] unexpectedly reaches MRT0')
  if '12' in (union.get('cbuffer_dwords') or {}):v.append('API12 unexpectedly reaches MRT0')
 missing=[x for x in ANCHORS if x not in asm]
 if missing:v.append(f'missing native anchors {missing}')
 out={'schema':'d1_tower_light_80aadbd5_mrt0_factorization/v1','status':'D1_TOWER_LIGHT_80AADBD5_MRT0_FACTORIZATION_EXACT' if not v else 'D1_TOWER_LIGHT_80AADBD5_MRT0_FACTORIZATION_PARTIAL','shader':SHADER,'native_shader':NATIVE,'gcn_sha256':GCN_SHA,'instance_count':EXPECTED_INSTANCES,'unique_material_count':len(mats),
 'exact_tail_symbols':{'Q':'clamp(q_in*API0[44]+API0[45])','P':'clamp(p_native+0.5)^2','L':'exact native clamped scalar','T':'t2.y','R':'API0[40:42].rgb','M':'API0[64:66].rgb','S':'API0[68]'},
 'exact_terminal_equation':{'vector_pre_scale':'V.rgb = API0[40:42].rgb*P + API0[64:66].rgb*(L*t2.y)','scalar_scale':'K = API0[68] * Q^2','mrt0_rgb':'MRT0.rgb = V.rgb * K','mrt0_a':'0','vector_form':'MRT0.rgb = (API0[40:42].rgb*P + API0[64:66].rgb*(L*t2.y)) * API0[68] * Q^2'},
 'negative_proof':{'t3_x_reaches_mrt0':False,'t0_alpha_reaches_mrt0':False,'t2_x_reaches_mrt0':False,'api0_dword43_reaches_mrt0':False,'api0_dword67_reaches_mrt0':False,'api0_dword73_reaches_mrt0':False,'api12_reaches_mrt0':False},
 'semantic_boundary':{'terminal_arithmetic':'EXACT_NATIVE_GCN','serialized_ps_texture_bindings':'NONE_FOR_2_FAMILY_MATERIALS','renderer_resource_human_semantics':'WITHHELD','portable_light_model_mapping':'WITHHELD'},'violations':v}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'equation':out['exact_terminal_equation'],'violations':v},indent=2));return 0 if not v else 2
if __name__=='__main__':raise SystemExit(main())
