#!/usr/bin/env python3
"""Fail-closed terminal MRT0 factorization for Tower light PS 80C98958.

Exact terminal arithmetic:
    Q = clamp(q_in * API0[52] + API0[53])
    P = clamp(p_native + 0.5)^2
    L = native clamped scalar at 0x300
    V.rgb = API0[48:50] * P + API0[88:90] * (L * t2.y)
    MRT0.rgb = V.rgb * API0[92] * Q^2
    MRT0.a = 0

p_native and L have exact native dataflow upstream, but their human meanings are
withheld. The shader also samples t3.x; exact terminal slicing proves t3.x reaches
MRT1 only and is absent from MRT0.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

SHADER='80C98958';NATIVE='80C98959'
NATIVE_SHA='8bfa9715450b7968e7e385b09acbc436e9eb963ac2ae1114cf4126b1e25e0f93'
GCN_SHA='5612626d7b9253a37a8f43170032ca4b3519970a0faf2fb2f78d8281cdd311dc'
GCN_BYTES=972;EXPECTED_INSTANCES=9;EXPECTED_MATERIALS=6;EXPECTED_TERMINAL='0000000003C0'
EXPECTED_CB={
 'R':list(range(12,37))+[40,44,45,46,48,52,53,88,92],
 'G':list(range(12,37))+[40,44,45,46,49,52,53,89,92],
 'B':list(range(12,37))+[40,44,45,46,50,52,53,90,92],
}
ANCHORS=[
 '/*000000000298: f09c0100 00a30312*/ image_sample_lz v3, v[18:21], s[12:19], s[20:23]',
 '/*0000000002a4: f09c0300 01060707*/ image_sample_lz v[7:8], v[7:10], s[24:31], s[32:35] dmask:3',
 '/*0000000002ac: c2410534         */ s_buffer_load_dwordx2 s[2:3], s[4:7], 0x34',
 '/*0000000002b8: c2860530         */ s_buffer_load_dwordx4 s[12:15], s[4:7], 0x30',
 '/*0000000002c8: c2880558         */ s_buffer_load_dwordx4 s[16:19], s[4:7], 0x58',
 '/*0000000002cc: c200855c         */ s_buffer_load_dword s1, s[4:7], 0x5c',
 '/*0000000002d0: c2020561         */ s_buffer_load_dword s4, s[4:7], 0x61',
 '/*0000000002e4: d220000a 78000000*/ v_max_f32       v10, -s0, -s0 div:2',
 '/*0000000002fc: 3e140800         */ v_mac_f32       v10, s0, v4',
 '/*000000000300: d2820800 04021305*/ v_mad_f32       v0, v5, v9, v0 clamp',
 '/*00000000030c: d2060805 0001e10a*/ v_add_f32       v5, v10, 0.5 clamp',
 '/*000000000328: 100a0b05         */ v_mul_f32       v5, v5, v5',
 '/*000000000334: d2820806 04180501*/ v_mad_f32       v6, v1, s2, v6 clamp',
 '/*000000000340: 10001100         */ v_mul_f32       v0, v0, v8',
 '/*000000000348: 10040a0c         */ v_mul_f32       v2, s12, v5',
 '/*00000000034c: 10080a0d         */ v_mul_f32       v4, s13, v5',
 '/*000000000350: 100a0a0e         */ v_mul_f32       v5, s14, v5',
 '/*000000000360: 100c0d06         */ v_mul_f32       v6, v6, v6',
 '/*000000000364: 3e040010         */ v_mac_f32       v2, s16, v0',
 '/*000000000368: 3e080011         */ v_mac_f32       v4, s17, v0',
 '/*00000000036c: 3e0a0012         */ v_mac_f32       v5, s18, v0',
 '/*00000000037c: 10000c01         */ v_mul_f32       v0, s1, v6',
 '/*000000000384: 10040102         */ v_mul_f32       v2, v2, v0',
 '/*000000000388: 10080104         */ v_mul_f32       v4, v4, v0',
 '/*00000000038c: 10000105         */ v_mul_f32       v0, v5, v0',
 '/*00000000039c: 7e060280         */ v_mov_b32       v3, 0',
 '/*0000000003b8: 5e020902         */ v_cvt_pkrtz_f16_f32 v1, v2, v4',
 '/*0000000003bc: 5e000700         */ v_cvt_pkrtz_f16_f32 v0, v0, v3',
 '/*0000000003c0: f8001c0f 00000001*/ exp             mrt0, v1, v1, v0, v0 done compr vm',
]

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def main()->int:
 ap=argparse.ArgumentParser()
 for n in ('material-manifest','shader-report','image-usage','cbuffer-usage','terminal-mrt0','disasm','out'):
  ap.add_argument('--'+n,type=Path,required=True)
 a=ap.parse_args();v=[]
 m=json.loads(a.material_manifest.read_text());s=json.loads(a.shader_report.read_text())
 i=json.loads(a.image_usage.read_text());c=json.loads(a.cbuffer_usage.read_text())
 t=json.loads(a.terminal_mrt0.read_text());asm=a.disasm.read_text(errors='replace')

 if m.get('status')!='D1_WORLD_LIGHT_MATERIAL_MANIFEST_COMPLETE':v.append('material manifest not exact')
 if int((m.get('pixel_shader_frequency') or {}).get(SHADER,-1))!=EXPECTED_INSTANCES:v.append('instance count drift')
 mats=(m.get('pixel_shader_materials') or {}).get(SHADER,[])
 if len(mats)!=EXPECTED_MATERIALS:v.append(f'unique material count drift {len(mats)} != {EXPECTED_MATERIALS}')
 if any(int((m.get('materials') or {}).get(x,{}).get('ps_texture_count',-1))!=0 for x in mats):
  v.append('serialized PS texture binding unexpectedly present')

 sr=next((x for x in s.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if s.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or not sr:v.append('shader report not exact/present')
 else:
  for k,z in {'native_shader':NATIVE,'native_sha256':NATIVE_SHA,'gcn_sha256':GCN_SHA,'gcn_bytes':GCN_BYTES}.items():
   if sr.get(k)!=z:v.append(f'{k} drift {sr.get(k)!r} != {z!r}')

 ir=next((x for x in i.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if i.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT' or not ir:v.append('image usage not exact/present')
 else:
  got=[(x['address'],x['opcode'],[q['texture_index'] for q in x.get('resources',[])],x['dmask_channels']) for x in ir.get('instructions',[])]
  exp=[
   ('000000000040','image_load_mip',[1],'x'),
   ('000000000048','image_sample',[0],'xyzw'),
   ('000000000298','image_sample_lz',[3],'x'),
   ('0000000002A4','image_sample_lz',[2],'xy'),
  ]
  if got!=exp:v.append(f'image instruction scope drift {got!r}')

 cr=next((x for x in c.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if c.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or not cr:v.append('cbuffer usage not exact/present')
 else:
  by={x.get('address'):x for x in cr.get('loads',[])}
  expected={
   '0000000002AC':(0,[52,53],[2,3]),
   '0000000002B8':(0,[48,49,50,51],[12,13,14,15]),
   '0000000002C8':(0,[88,89,90,91],[16,17,18,19]),
   '0000000002CC':(0,[92],[1]),
   '0000000002D0':(0,[97],[4]),
  }
  for addr,(api,dw,dst) in expected.items():
   q=by.get(addr)
   if not q or q.get('api_slot')!=api or q.get('dword_indices')!=dw or q.get('destination')!=dst:
    v.append(f'{addr}: cbuffer provenance drift {q}')

 tr=next((x for x in t.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if t.get('status')!='D1_GCN_TERMINAL_MRT0_DEPENDENCY_CENSUS_EXACT' or not tr:v.append('terminal MRT0 slice not exact/present')
 else:
  if tr.get('terminal_mrt0_export_address')!=EXPECTED_TERMINAL or not tr.get('terminal_mrt0_compressed'):
   v.append('terminal export identity drift')
  if tr.get('terminal_mrt0_operands')!=['v1','v1','v0','v0']:v.append('terminal operands drift')
  expected_tex={(0,x,'000000000048') for x in 'xyz'}|{(1,'x','000000000040'),(2,'y','0000000002A4')}
  for ch in 'RGB':
   q=tr['channels'][ch]['value_slice']
   tex={(int(x['texture_index']),x['channel'],x['sample_address']) for x in q.get('texture_sample_channels',[])}
   if tex!=expected_tex:v.append(f'{ch}: terminal texture leaf drift {sorted(tex)}')
   cbq=q.get('cbuffer_dwords') or {}
   if cbq!={'0':EXPECTED_CB[ch]}:v.append(f'{ch}: exact cbuffer leaf set drift {cbq!r}')
   if q.get('unknown_registers')!=['v2','v3']:v.append(f'{ch}: native input frontier drift {q.get("unknown_registers")}')
  aq=tr['channels']['A']['value_slice']
  if aq.get('literals')!=['0'] or aq.get('texture_sample_channels') or aq.get('cbuffer_dwords') or aq.get('unknown_registers'):
   v.append(f'alpha is not exact zero-only {aq}')
  union=tr.get('mrt0_value_union') or {}
  alltex={(int(x['texture_index']),x['channel']) for x in union.get('texture_sample_channels',[])}
  if any(ti==3 for ti,_ in alltex):v.append(f't3 unexpectedly reaches MRT0 {sorted(alltex)}')
  if (0,'w') in alltex or (2,'x') in alltex:v.append(f'dead sampled channel reached MRT0 unexpectedly {sorted(alltex)}')
  api0=set((union.get('cbuffer_dwords') or {}).get('0',[]))
  for dead in (47,51,91,97):
   if dead in api0:v.append(f'API0[{dead}] unexpectedly reaches MRT0')
  if '12' in (union.get('cbuffer_dwords') or {}):v.append('API12 unexpectedly reaches MRT0')

 missing=[x for x in ANCHORS if x not in asm]
 if missing:v.append(f'missing exact native anchors {missing}')

 out={
  'schema':'d1_tower_light_80c98958_mrt0_factorization/v1',
  'status':'D1_TOWER_LIGHT_80C98958_MRT0_FACTORIZATION_EXACT' if not v else 'D1_TOWER_LIGHT_80C98958_MRT0_FACTORIZATION_PARTIAL',
  'shader':SHADER,'native_shader':NATIVE,'gcn_sha256':GCN_SHA,
  'instance_count':EXPECTED_INSTANCES,'unique_material_count':len(mats),
  'exact_tail_symbols':{
   'Q':'v6 after 0x334 = clamp(q_in*API0[52]+API0[53])',
   'P':'v5 after 0x328 = clamp(p_native+0.5)^2; p_native is exact v10 after 0x2FC and depends on API0[40,44,45,46] plus upstream native inputs',
   'L':'v0 after 0x300 = exact clamped native scalar; upstream semantics withheld',
   'T':'t2.y',
   'B':'API0[48:50].rgb','M':'API0[88:90].rgb','S':'API0[92]',
  },
  'exact_terminal_equation':{
   'vector_pre_scale':'V.rgb = API0[48:50].rgb*P + API0[88:90].rgb*(L*t2.y)',
   'scalar_scale':'K = API0[92] * Q^2',
   'mrt0_rgb':'MRT0.rgb = V.rgb * K',
   'mrt0_a':'0',
   'vector_form':'MRT0.rgb = (API0[48:50].rgb*P + API0[88:90].rgb*(L*t2.y)) * API0[92] * Q^2',
  },
  'negative_proof':{
   't3_x_reaches_mrt0':False,'t0_alpha_reaches_mrt0':False,'t2_x_reaches_mrt0':False,
   'api0_dword47_reaches_mrt0':False,'api0_dword51_reaches_mrt0':False,
   'api0_dword91_reaches_mrt0':False,'api0_dword97_reaches_mrt0':False,
   'api12_reaches_mrt0':False,
  },
  'native_input_frontier':['v2','v3'],
  'semantic_boundary':{
   'terminal_arithmetic':'EXACT_NATIVE_GCN',
   'serialized_ps_texture_bindings':'NONE_FOR_6_FAMILY_MATERIALS',
   'renderer_t0_t1_t2_t3_human_semantics':'WITHHELD',
   'symbols_Q_P_L_human_semantics':'WITHHELD',
   'unresolved_native_input_registers':'EXACTLY_V2_V3_AT_ANALYZER_FRONTIER',
   'portable_light_model_mapping':'WITHHELD',
  },
  'violations':v,
  'policy':'Exact terminal GCN algebra and exact dependency leaves. P and L intentionally summarize source-closed upstream arithmetic whose engine meaning is not established; no light type or renderer-resource role is inferred.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True)
 a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'equation':out['exact_terminal_equation'],'negative_proof':out['negative_proof'],'violations':v},indent=2))
 return 0 if not v else 2

if __name__=='__main__':raise SystemExit(main())
