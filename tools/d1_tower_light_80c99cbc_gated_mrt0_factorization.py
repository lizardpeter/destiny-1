#!/usr/bin/env python3
"""Fail-closed gated terminal MRT0 factorization for Tower light PS 80C99CBC."""
from __future__ import annotations
import argparse,json
from pathlib import Path
SHADER='80C99CBC';NATIVE='80C99F19'
NATIVE_SHA='c37e6ede6451b80d769b0b5ff96f0da9479398144115c727a9765ccdcc765d62'
GCN_SHA='a335cf7b1371efdcf1aa2c3240b784648bc3f186d0db89d8eb7be08e357c2d75'
GCN_BYTES=856;EXPECTED_INSTANCES=2;EXPECTED_MATERIALS=2;EXPECTED_TERMINAL='00000000034C'
ANCHORS=[
 '/*000000000234: f09c0300 00021010*/ image_sample_lz v[16:17], v[16:19], s[8:15], s[0:3] dmask:3',
 '/*00000000023c: c2400528         */ s_buffer_load_dwordx2 s[0:1], s[4:7], 0x28',
 '/*000000000240: c2840558         */ s_buffer_load_dwordx4 s[8:11], s[4:7], 0x58',
 '/*000000000248: c286054c         */ s_buffer_load_dwordx4 s[12:15], s[4:7], 0x4c',
 '/*000000000254: c2010550         */ s_buffer_load_dword s2, s[4:7], 0x50',
 '/*000000000264: c2018555         */ s_buffer_load_dword s3, s[4:7], 0x55',
 '/*000000000280: d2820802 040a0305*/ v_mad_f32       v2, v5, v1, v2 clamp',
 '/*00000000028c: d2820807 041c0100*/ v_mad_f32       v7, v0, s0, v7 clamp',
 '/*000000000294: 10000609         */ v_mul_f32       v0, s9, v3',
 '/*00000000029c: 10060f07         */ v_mul_f32       v3, v7, v7',
 '/*0000000002a0: 3e000808         */ v_mac_f32       v0, s8, v4',
 '/*0000000002ac: 1008060c         */ v_mul_f32       v4, s12, v3',
 '/*0000000002b0: 100a060d         */ v_mul_f32       v5, s13, v3',
 '/*0000000002b4: 1006060e         */ v_mul_f32       v3, s14, v3',
 '/*0000000002b8: 3e001a0a         */ v_mac_f32       v0, s10, v13',
 '/*0000000002bc: 10042302         */ v_mul_f32       v2, v2, v17',
 '/*0000000002cc: 10080802         */ v_mul_f32       v4, s2, v4',
 '/*0000000002d0: 100a0a02         */ v_mul_f32       v5, s2, v5',
 '/*0000000002d4: 10060602         */ v_mul_f32       v3, s2, v3',
 '/*0000000002d8: 0600000b         */ v_add_f32       v0, s11, v0',
 '/*0000000002dc: 10080902         */ v_mul_f32       v4, v2, v4',
 '/*0000000002e0: 100a0b02         */ v_mul_f32       v5, v2, v5',
 '/*0000000002e4: 10040702         */ v_mul_f32       v2, v2, v3',
 '/*0000000002f4: 7c0c0080         */ v_cmp_ge_f32    vcc, 0, v0',
 '/*0000000002f8: d2000000 01a90102*/ v_cndmask_b32   v0, v2, 0, vcc',
 '/*000000000300: d2000002 01a90105*/ v_cndmask_b32   v2, v5, 0, vcc',
 '/*000000000308: d2000004 01a90104*/ v_cndmask_b32   v4, v4, 0, vcc',
 '/*000000000344: 5e020504         */ v_cvt_pkrtz_f16_f32 v1, v4, v2',
 '/*000000000348: 5e000d00         */ v_cvt_pkrtz_f16_f32 v0, v0, v6',
 '/*00000000034c: f8001c0f 00000001*/ exp             mrt0, v1, v1, v0, v0 done compr vm',
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
  exp=[('000000000040','image_load_mip',[1],'x'),('000000000048','image_sample',[0],'xyzw'),('000000000234','image_sample_lz',[2],'xy')]
  if got!=exp:v.append(f'image scope drift {got!r}')
 cr=next((x for x in c.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if c.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or not cr:v.append('cbuffer usage not exact/present')
 else:
  by={x.get('address'):x for x in cr.get('loads',[])}
  expected={'00000000023C':(0,[40,41],[0,1]),'000000000240':(0,[88,89,90,91],[8,9,10,11]),'000000000248':(0,[76,77,78,79],[12,13,14,15]),'000000000254':(0,[80],[2]),'000000000264':(0,[85],[3])}
  for addr,(api,dw,dst) in expected.items():
   q=by.get(addr)
   if not q or q.get('api_slot')!=api or q.get('dword_indices')!=dw or q.get('destination')!=dst:v.append(f'{addr}: cbuffer drift {q}')
 tr=next((x for x in t.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if t.get('status')!='D1_GCN_TERMINAL_MRT0_DEPENDENCY_CENSUS_EXACT' or not tr:v.append('terminal MRT0 slice not exact/present')
 else:
  if tr.get('terminal_mrt0_export_address')!=EXPECTED_TERMINAL or tr.get('terminal_mrt0_operands')!=['v1','v1','v0','v0']:v.append('terminal export drift')
  texreq={(0,x,'000000000048') for x in 'xyz'}|{(1,'x','000000000040'),(2,'y','000000000234')}
  for ch,col in [('R',76),('G',77),('B',78)]:
   q=tr['channels'][ch]['value_slice'];tex={(int(x['texture_index']),x['channel'],x['sample_address']) for x in q.get('texture_sample_channels',[])}
   if tex!=texreq:v.append(f'{ch}: texture leaf drift {sorted(tex)}')
   cbq={str(k):set(z) for k,z in (q.get('cbuffer_dwords') or {}).items()};req={40,41,col,80}
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
 out={'schema':'d1_tower_light_80c99cbc_gated_mrt0_factorization/v1','status':'D1_TOWER_LIGHT_80C99CBC_GATED_MRT0_FACTORIZATION_EXACT' if not v else 'D1_TOWER_LIGHT_80C99CBC_GATED_MRT0_FACTORIZATION_PARTIAL','shader':SHADER,'native_shader':NATIVE,'gcn_sha256':GCN_SHA,'instance_count':EXPECTED_INSTANCES,'unique_material_count':len(mats),
 'exact_tail_symbols':{'Q':'clamp(q_in*API0[40]+API0[41])','L':'exact native clamped scalar','C':'API0[76:78].rgb','S':'API0[80]','T':'t2.y','G':'API0[88]*g0+API0[89]*g1+API0[90]*g2+API0[91]'},
 'exact_terminal_equation':{'base_rgb':'API0[76:78].rgb * Q^2 * API0[80] * L * t2.y','gate':'G > 0','mrt0_rgb':'BASE.rgb if G > 0 else (0,0,0)','mrt0_a':'0','vector_form':'MRT0.rgb = API0[76:78].rgb * Q^2 * API0[80] * L * t2.y when G > 0, else 0'},
 'predicate_proof':{'compare':'v_cmp_ge_f32 vcc, 0, G','false_when':'G <= 0','kept_when':'G > 0'},
 'negative_proof':{'t0_alpha_reaches_mrt0':False,'t2_x_reaches_mrt0':False,'api0_dword79_reaches_mrt0':False,'api0_dword85_reaches_mrt0':False,'api12_reaches_mrt0':False},
 'semantic_boundary':{'terminal_arithmetic':'EXACT_NATIVE_GCN','gate_predicate':'EXACT_NATIVE_GCN','serialized_ps_texture_bindings':'NONE_FOR_2_FAMILY_MATERIALS','renderer_resource_human_semantics':'WITHHELD'},'violations':v}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'equation':out['exact_terminal_equation'],'violations':v},indent=2));return 0 if not v else 2
if __name__=='__main__':raise SystemExit(main())
