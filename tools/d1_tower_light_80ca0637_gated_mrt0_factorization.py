#!/usr/bin/env python3
"""Fail-closed gated terminal MRT0 factorization for Tower light PS 80CA0637.

Exact native terminal form:
    Q = clamp(q_in * API0[56] + API0[57])
    H = exact native clamp ending at 0x360, including API0[88:89]
    L = exact native scalar reaching t2.y modulation
    P = clamp(p_native + 0.5)^2
    V.rgb = API0[52:54] + API0[92:94]*(L*t2.y) + API0[48:50]*P
    K = API0[96] * Q^2 * H
    G = API0[104]*g0 + API0[105]*g1 + API0[106]*g2 + API0[107]
    MRT0.rgb = V.rgb * K if G > 0 else 0
    MRT0.a = 0

The extra t3.x sample is confined to the MRT1 branch. Native symbolic inputs and
renderer-resource semantics remain withheld.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

SHADER='80CA0637';NATIVE='80CA076C'
NATIVE_SHA='dc5e556d23eb3364bb8a6829602bdfc8f7508ec4c4bddaa451bac6bdf2c9aa29'
GCN_SHA='2ee26c5aed19cd3185dd14754403fd1ebe901ddd5ca6a11f50c99d7cbea2d9f4'
GCN_BYTES=1096;EXPECTED_INSTANCES=6;EXPECTED_MATERIALS=6;EXPECTED_TERMINAL='00000000043C'
ANCHORS=[
 '/*000000000294: f09c0300 00a31214*/ image_sample_lz v[18:19], v[20:23], s[12:19], s[20:23] dmask:3',
 '/*0000000002a4: f09c0100 01060114*/ image_sample_lz v1, v[20:23], s[24:31], s[32:35]',
 '/*0000000002ac: c286054c         */ s_buffer_load_dwordx4 s[12:15], s[4:7], 0x4c',
 '/*0000000002b0: c2410538         */ s_buffer_load_dwordx2 s[2:3], s[4:7], 0x38',
 '/*0000000002b4: c2480558         */ s_buffer_load_dwordx2 s[16:17], s[4:7], 0x58',
 '/*0000000002b8: c28a0568         */ s_buffer_load_dwordx4 s[20:23], s[4:7], 0x68',
 '/*0000000002bc: c28c0534         */ s_buffer_load_dwordx4 s[24:27], s[4:7], 0x34',
 '/*0000000002c4: c28e055c         */ s_buffer_load_dwordx4 s[28:31], s[4:7], 0x5c',
 '/*0000000002c8: c2900530         */ s_buffer_load_dwordx4 s[32:35], s[4:7], 0x30',
 '/*0000000002d8: c2008560         */ s_buffer_load_dword s1, s[4:7], 0x60',
 '/*0000000002dc: c2020565         */ s_buffer_load_dword s4, s[4:7], 0x65',
 '/*000000000310: d2200008 78000000*/ v_max_f32       v8, -s0, -s0 div:2',
 '/*00000000031c: d2820802 040a0f05*/ v_mad_f32       v2, v5, v7, v2 clamp',
 '/*000000000330: 3e101400         */ v_mac_f32       v8, s0, v10',
 '/*00000000033c: d282080b 042c0500*/ v_mad_f32       v11, v0, s2, v11 clamp',
 '/*000000000348: 10060b02         */ v_mul_f32       v3, v2, v5',
 '/*000000000350: 10042702         */ v_mul_f32       v2, v2, v19',
 '/*000000000354: 7e0a0218         */ v_mov_b32       v5, s24',
 '/*000000000358: 7e140219         */ v_mov_b32       v10, s25',
 '/*00000000035c: 7e18021a         */ v_mov_b32       v12, s26',
 '/*000000000360: d2820806 24182109*/ v_mad_f32       v6, -v9, s16, v6 clamp',
 '/*000000000368: d2060808 0001e108*/ v_add_f32       v8, v8, 0.5 clamp',
 '/*000000000378: 100e170b         */ v_mul_f32       v7, v11, v11',
 '/*000000000384: 3e0a041c         */ v_mac_f32       v5, s28, v2',
 '/*000000000388: 3e14041d         */ v_mac_f32       v10, s29, v2',
 '/*00000000038c: 3e18041e         */ v_mac_f32       v12, s30, v2',
 '/*000000000390: 10041108         */ v_mul_f32       v2, v8, v8',
 '/*0000000003a0: 100c0f06         */ v_mul_f32       v6, v6, v7',
 '/*0000000003a8: 3e0a0420         */ v_mac_f32       v5, s32, v2',
 '/*0000000003ac: 3e140421         */ v_mac_f32       v10, s33, v2',
 '/*0000000003b0: 3e180422         */ v_mac_f32       v12, s34, v2',
 '/*0000000003c0: 10040c01         */ v_mul_f32       v2, s1, v6',
 '/*0000000003c8: 06000017         */ v_add_f32       v0, s23, v0',
 '/*0000000003cc: 100a0505         */ v_mul_f32       v5, v5, v2',
 '/*0000000003d0: 100c050a         */ v_mul_f32       v6, v10, v2',
 '/*0000000003d4: 1004050c         */ v_mul_f32       v2, v12, v2',
 '/*0000000003e4: 7c0c0080         */ v_cmp_ge_f32    vcc, 0, v0',
 '/*0000000003e8: d2000000 01a90102*/ v_cndmask_b32   v0, v2, 0, vcc',
 '/*0000000003f0: d2000002 01a90106*/ v_cndmask_b32   v2, v6, 0, vcc',
 '/*0000000003f8: d2000003 01a90105*/ v_cndmask_b32   v3, v5, 0, vcc',
 '/*000000000434: 5e020503         */ v_cvt_pkrtz_f16_f32 v1, v3, v2',
 '/*000000000438: 5e000d00         */ v_cvt_pkrtz_f16_f32 v0, v0, v6',
 '/*00000000043c: f8001c0f 00000001*/ exp             mrt0, v1, v1, v0, v0 done compr vm',
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
   ('000000000294','image_sample_lz',[2],'xy'),
   ('0000000002A4','image_sample_lz',[3],'x'),
  ]
  if got!=exp:v.append(f'image instruction scope drift {got!r}')

 cr=next((x for x in c.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if c.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or not cr:v.append('cbuffer usage not exact/present')
 else:
  by={x.get('address'):x for x in cr.get('loads',[])}
  expected={
   '0000000002AC':(0,[76,77,78,79],[12,13,14,15]),
   '0000000002B0':(0,[56,57],[2,3]),
   '0000000002B4':(0,[88,89],[16,17]),
   '0000000002B8':(0,[104,105,106,107],[20,21,22,23]),
   '0000000002BC':(0,[52,53,54,55],[24,25,26,27]),
   '0000000002C4':(0,[92,93,94,95],[28,29,30,31]),
   '0000000002C8':(0,[48,49,50,51],[32,33,34,35]),
   '0000000002D8':(0,[96],[1]),
   '0000000002DC':(0,[101],[4]),
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
  required_tex={(0,x,'000000000048') for x in 'xyz'}|{(1,'x','000000000040'),(2,'y','000000000294')}
  for ch,base,mod,pcoef in [('R',52,92,48),('G',53,93,49),('B',54,94,50)]:
   q=tr['channels'][ch]['value_slice']
   tex={(int(x['texture_index']),x['channel'],x['sample_address']) for x in q.get('texture_sample_channels',[])}
   if tex!=required_tex:v.append(f'{ch}: terminal texture leaf drift {sorted(tex)}')
   cbq={str(k):set(z) for k,z in (q.get('cbuffer_dwords') or {}).items()}
   if set(cbq)-{'0'}:v.append(f'{ch}: unexpected non-API0 MRT0 cbuffer leaves {cbq}')
   required={base,mod,pcoef,56,57,76,77,78,88,89,96,104,105,106,107}
   if not required.issubset(cbq.get('0',set())):
    v.append(f'{ch}: terminal coefficient leaves missing {sorted(required-cbq.get("0",set()))}')
  aq=tr['channels']['A']['value_slice']
  if aq.get('literals')!=['0'] or aq.get('texture_sample_channels') or aq.get('cbuffer_dwords') or aq.get('unknown_registers'):
   v.append(f'alpha is not exact zero-only {aq}')
  union=tr.get('mrt0_value_union') or {}
  alltex={(int(x['texture_index']),x['channel']) for x in union.get('texture_sample_channels',[])}
  if any(ti==3 for ti,_ in alltex):v.append(f't3 unexpectedly reaches MRT0 {sorted(alltex)}')
  if (0,'w') in alltex or (2,'x') in alltex:v.append(f'dead sampled channel reached MRT0 unexpectedly {sorted(alltex)}')
  api0=set((union.get('cbuffer_dwords') or {}).get('0',[]))
  for dead in (51,55,79,95,101):
   if dead in api0:v.append(f'API0[{dead}] unexpectedly reaches MRT0')
  if '12' in (union.get('cbuffer_dwords') or {}):v.append('API12 unexpectedly reaches MRT0')

 missing=[x for x in ANCHORS if x not in asm]
 if missing:v.append(f'missing exact native anchors {missing}')

 out={
  'schema':'d1_tower_light_80ca0637_gated_mrt0_factorization/v1',
  'status':'D1_TOWER_LIGHT_80CA0637_GATED_MRT0_FACTORIZATION_EXACT' if not v else 'D1_TOWER_LIGHT_80CA0637_GATED_MRT0_FACTORIZATION_PARTIAL',
  'shader':SHADER,'native_shader':NATIVE,'gcn_sha256':GCN_SHA,
  'instance_count':EXPECTED_INSTANCES,'unique_material_count':len(mats),
  'exact_tail_symbols':{
   'Q':'v11 after 0x33C = clamp(q_in*API0[56]+API0[57])',
   'H':'v6 after 0x360 = exact clamped native scalar including API0[88:89]',
   'L':'v2 after 0x31C = exact native clamped scalar; upstream semantics withheld',
   'P':'v2 after 0x390 = clamp(p_native+0.5)^2',
   'T':'t2.y',
   'B':'API0[52:54].rgb','M':'API0[92:94].rgb','R':'API0[48:50].rgb','S':'API0[96]',
   'G':'API0[104]*g0 + API0[105]*g1 + API0[106]*g2 + API0[107]',
  },
  'exact_terminal_equation':{
   'vector_pre_scale':'V.rgb = API0[52:54].rgb + API0[92:94].rgb*(L*t2.y) + API0[48:50].rgb*P',
   'scalar_scale':'K = API0[96] * Q^2 * H',
   'gate':'G > 0',
   'mrt0_rgb':'V.rgb * K if G > 0 else (0,0,0)',
   'mrt0_a':'0',
   'vector_form':'MRT0.rgb = (API0[52:54].rgb + API0[92:94].rgb*(L*t2.y) + API0[48:50].rgb*P) * API0[96] * Q^2 * H when G > 0, else 0',
  },
  'predicate_proof':{'compare':'v_cmp_ge_f32 vcc, 0, G','false_when':'G <= 0','kept_when':'G > 0'},
  'negative_proof':{
   't3_x_reaches_mrt0':False,'t0_alpha_reaches_mrt0':False,'t2_x_reaches_mrt0':False,
   'api0_dword51_reaches_mrt0':False,'api0_dword55_reaches_mrt0':False,
   'api0_dword79_reaches_mrt0':False,'api0_dword95_reaches_mrt0':False,
   'api0_dword101_reaches_mrt0':False,'api12_reaches_mrt0':False,
  },
  'semantic_boundary':{
   'terminal_arithmetic':'EXACT_NATIVE_GCN',
   'serialized_ps_texture_bindings':'NONE_FOR_6_FAMILY_MATERIALS',
   'renderer_t0_t1_t2_t3_human_semantics':'WITHHELD',
   'symbols_Q_H_L_P_G_human_semantics':'WITHHELD',
   'portable_light_model_mapping':'WITHHELD',
  },
  'violations':v,
  'policy':'Exact native GCN terminal arithmetic and gate predicate. t3 is proven MRT0-dead; renderer resources and native symbolic intermediates remain semantically unnamed.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'equation':out['exact_terminal_equation'],'negative_proof':out['negative_proof'],'violations':v},indent=2))
 return 0 if not v else 2

if __name__=='__main__':raise SystemExit(main())
