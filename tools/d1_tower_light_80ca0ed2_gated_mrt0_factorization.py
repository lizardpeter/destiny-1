#!/usr/bin/env python3
"""Fail-closed gated terminal MRT0 factorization for Tower light PS 80CA0ED2.

Exact native arithmetic only:
    Q = clamp(q_in * API0[44] + API0[45])
    H = clamp(-h_in * API0[68] + API0[69])
    L = clamp(l_a*l_b + l_c)
    P = clamp(p_in + 0.5)^2
    V.rgb = API0[40:42] * P + API0[72:74] * (L * t2.y)
    K = API0[76] * Q^2 * H
    G = API0[84]*g0 + API0[85]*g1 + API0[86]*g2 + API0[87]
    MRT0.rgb = V.rgb * K if G > 0 else 0
    MRT0.a = 0

The shader also samples t3.x, but exact native dataflow confines that sample to
the MRT1 path; t3 does not reach MRT0.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

SHADER='80CA0ED2';NATIVE='80CA0EDD'
NATIVE_SHA='ef8f7cf68fc000625cbb454cc2382c2764902aa42d7cfa1a882dcf0aa528afc1'
GCN_SHA='ddf03ea70f1e3eff7c8e150b59f7d4ff2c6d02fb816f0f316c92b9cec424f211'
GCN_BYTES=984;EXPECTED_INSTANCES=11;EXPECTED_MATERIALS=11;EXPECTED_TERMINAL='0000000003CC'

ANCHORS=[
 '/*000000000238: f09c0100 00a30a14*/ image_sample_lz v10, v[20:23], s[12:19], s[20:23]',
 '/*000000000244: f09c0300 01061111*/ image_sample_lz v[17:18], v[17:20], s[24:31], s[32:35] dmask:3',
 '/*00000000024c: c2860540         */ s_buffer_load_dwordx4 s[12:15], s[4:7], 0x40',
 '/*000000000250: c241052c         */ s_buffer_load_dwordx2 s[2:3], s[4:7], 0x2c',
 '/*000000000254: c2480544         */ s_buffer_load_dwordx2 s[16:17], s[4:7], 0x44',
 '/*000000000258: c28a0554         */ s_buffer_load_dwordx4 s[20:23], s[4:7], 0x54',
 '/*000000000264: c28c0528         */ s_buffer_load_dwordx4 s[24:27], s[4:7], 0x28',
 '/*000000000274: c28e0548         */ s_buffer_load_dwordx4 s[28:31], s[4:7], 0x48',
 '/*000000000278: c200854c         */ s_buffer_load_dword s1, s[4:7], 0x4c',
 '/*00000000027c: c2020551         */ s_buffer_load_dword s4, s[4:7], 0x51',
 '/*0000000002bc: d282080b 042c0509*/ v_mad_f32       v11, v9, s2, v11 clamp',
 '/*0000000002cc: d2820801 04060105*/ v_mad_f32       v1, v5, v0, v1 clamp',
 '/*0000000002d8: d2060804 0001e107*/ v_add_f32       v4, v7, 0.5 clamp',
 '/*0000000002e0: d2200805 00021b0d*/ v_max_f32       v5, v13, v13 clamp',
 '/*0000000002ec: 100e170b         */ v_mul_f32       v7, v11, v11',
 '/*0000000002f0: d2820806 2418210e*/ v_mad_f32       v6, -v14, s16, v6 clamp',
 '/*0000000002fc: 10080904         */ v_mul_f32       v4, v4, v4',
 '/*000000000304: 100a0b0a         */ v_mul_f32       v5, v10, v5',
 '/*000000000310: 10022501         */ v_mul_f32       v1, v1, v18',
 '/*000000000318: 10100818         */ v_mul_f32       v8, s24, v4',
 '/*00000000031c: 10120819         */ v_mul_f32       v9, s25, v4',
 '/*000000000320: 1008081a         */ v_mul_f32       v4, s26, v4',
 '/*000000000330: 100c0d07         */ v_mul_f32       v6, v7, v6',
 '/*000000000338: 3e10021c         */ v_mac_f32       v8, s28, v1',
 '/*00000000033c: 3e12021d         */ v_mac_f32       v9, s29, v1',
 '/*000000000340: 3e08021e         */ v_mac_f32       v4, s30, v1',
 '/*000000000350: 10000c01         */ v_mul_f32       v0, s1, v6',
 '/*000000000358: 06040617         */ v_add_f32       v2, s23, v3',
 '/*00000000035c: 10060108         */ v_mul_f32       v3, v8, v0',
 '/*000000000360: 100c0109         */ v_mul_f32       v6, v9, v0',
 '/*000000000364: 10000104         */ v_mul_f32       v0, v4, v0',
 '/*000000000374: 7c0c0480         */ v_cmp_ge_f32    vcc, 0, v2',
 '/*000000000378: d2000000 01a90100*/ v_cndmask_b32   v0, v0, 0, vcc',
 '/*000000000380: d2000002 01a90106*/ v_cndmask_b32   v2, v6, 0, vcc',
 '/*000000000388: d2000003 01a90103*/ v_cndmask_b32   v3, v3, 0, vcc',
 '/*0000000003c4: 5e020503         */ v_cvt_pkrtz_f16_f32 v1, v3, v2',
 '/*0000000003c8: 5e000d00         */ v_cvt_pkrtz_f16_f32 v0, v0, v6',
 '/*0000000003cc: f8001c0f 00000001*/ exp             mrt0, v1, v1, v0, v0 done compr vm',
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
   ('000000000238','image_sample_lz',[3],'x'),
   ('000000000244','image_sample_lz',[2],'xy'),
  ]
  if got!=exp:v.append(f'image instruction scope drift {got!r}')

 cr=next((x for x in c.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if c.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or not cr:v.append('cbuffer usage not exact/present')
 else:
  by={x.get('address'):x for x in cr.get('loads',[])}
  expected={
   '00000000024C':(0,[64,65,66,67],[12,13,14,15]),
   '000000000250':(0,[44,45],[2,3]),
   '000000000254':(0,[68,69],[16,17]),
   '000000000258':(0,[84,85,86,87],[20,21,22,23]),
   '000000000264':(0,[40,41,42,43],[24,25,26,27]),
   '000000000274':(0,[72,73,74,75],[28,29,30,31]),
   '000000000278':(0,[76],[1]),
   '00000000027C':(0,[81],[4]),
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
  shared={(0,x,'000000000048') for x in 'xyz'}|{(1,'x','000000000040'),(2,'y','000000000244')}
  for ch,base,mod in [('R',40,72),('G',41,73),('B',42,74)]:
   q=tr['channels'][ch]['value_slice']
   tex={(int(x['texture_index']),x['channel'],x['sample_address']) for x in q.get('texture_sample_channels',[])}
   if tex!=shared:v.append(f'{ch}: terminal texture leaf drift {sorted(tex)}')
   cb={str(k):set(z) for k,z in q.get('cbuffer_dwords',{}).items()}
   if set(cb)-{'0'}:v.append(f'{ch}: unexpected non-API0 MRT0 cbuffer leaves {cb}')
   required={44,45,68,69,base,mod,76,84,85,86,87}
   if not required.issubset(cb.get('0',set())):
    v.append(f'{ch}: terminal coefficient leaves missing {sorted(required-cb.get("0",set()))}')
   if 43 in cb.get('0',set()) or 75 in cb.get('0',set()) or 81 in cb.get('0',set()):
    v.append(f'{ch}: MRT1-only coefficient leaked into MRT0 {cb}')
  aq=tr['channels']['A']['value_slice']
  if aq.get('literals')!=['0'] or aq.get('texture_sample_channels') or aq.get('cbuffer_dwords') or aq.get('unknown_registers'):
   v.append(f'alpha is not exact zero-only {aq}')
  union=tr.get('mrt0_value_union') or {}
  alltex={(int(x['texture_index']),x['channel']) for x in union.get('texture_sample_channels',[])}
  if any(t==3 for t,_ in alltex):v.append(f't3 unexpectedly reaches MRT0 {sorted(alltex)}')
  if (0,'w') in alltex or (2,'x') in alltex:v.append(f'dead sampled channel reached MRT0 unexpectedly {sorted(alltex)}')
  if '12' in (union.get('cbuffer_dwords') or {}):v.append('API12 unexpectedly reaches MRT0')
  api0=set((union.get('cbuffer_dwords') or {}).get('0',[]))
  if 43 in api0 or 75 in api0 or 81 in api0:v.append(f'MRT1-only coefficient reached MRT0 {sorted(api0)}')

 missing=[x for x in ANCHORS if x not in asm]
 if missing:v.append(f'missing exact native anchors {missing}')

 out={
  'schema':'d1_tower_light_80ca0ed2_gated_mrt0_factorization/v1',
  'status':'D1_TOWER_LIGHT_80CA0ED2_GATED_MRT0_FACTORIZATION_EXACT' if not v else 'D1_TOWER_LIGHT_80CA0ED2_GATED_MRT0_FACTORIZATION_PARTIAL',
  'shader':SHADER,'native_shader':NATIVE,'gcn_sha256':GCN_SHA,
  'instance_count':EXPECTED_INSTANCES,'unique_material_count':len(mats),
  'exact_tail_symbols':{
   'Q':'v11 after 0x2BC = clamp(q_in*API0[44]+API0[45])',
   'H':'v6 after 0x2F0 = clamp(-h_in*API0[68]+API0[69])',
   'L':'v1 after 0x2CC = clamp(l_a*l_b+l_c)',
   'P':'v4 after 0x2FC = clamp(p_in+0.5)^2',
   'B':'API0[40:42].rgb','M':'API0[72:74].rgb','S':'API0[76]','T':'t2.y',
   'G':'API0[84]*g0 + API0[85]*g1 + API0[86]*g2 + API0[87]',
  },
  'exact_terminal_equation':{
   'vector_pre_scale':'V.rgb = API0[40:42].rgb*P + API0[72:74].rgb*(L*t2.y)',
   'scalar_scale':'K = API0[76] * Q^2 * H',
   'gate':'G > 0',
   'mrt0_rgb':'V.rgb * K if G > 0 else (0,0,0)',
   'mrt0_a':'0',
   'vector_form':'MRT0.rgb = (API0[40:42].rgb*P + API0[72:74].rgb*(L*t2.y)) * API0[76] * Q^2 * H when G > 0, else 0',
  },
  'predicate_proof':{'compare':'v_cmp_ge_f32 vcc, 0, G','false_when':'G <= 0','kept_when':'G > 0'},
  'negative_proof':{
   't3_x_reaches_mrt0':False,'t0_alpha_reaches_mrt0':False,'t2_x_reaches_mrt0':False,
   'api0_dword43_reaches_mrt0':False,'api0_dword75_reaches_mrt0':False,
   'api0_dword81_reaches_mrt0':False,'api12_reaches_mrt0':False,
  },
  'semantic_boundary':{
   'terminal_arithmetic':'EXACT_NATIVE_GCN',
   'serialized_ps_texture_bindings':'NONE_FOR_11_FAMILY_MATERIALS',
   'renderer_t0_t1_t2_t3_human_semantics':'WITHHELD',
   'symbols_Q_H_L_P_G_human_semantics':'WITHHELD',
   'portable_light_model_mapping':'WITHHELD',
  },
  'violations':v,
  'policy':'Exact native GCN arithmetic and gate predicate only. The sampled t3.x path is proven MRT0-dead for this family; renderer inputs and symbolic intermediates remain semantically unnamed.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True)
 a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'equation':out['exact_terminal_equation'],'negative_proof':out['negative_proof'],'violations':v},indent=2))
 return 0 if not v else 2

if __name__=='__main__':raise SystemExit(main())
