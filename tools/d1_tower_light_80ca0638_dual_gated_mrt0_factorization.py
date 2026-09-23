#!/usr/bin/env python3
"""Fail-closed dual-gated terminal MRT0 factorization for Tower light PS 80CA0638.

Exact native arithmetic:
    Q = clamp(q_in * API0[32] + API0[33])
    H = clamp(-h_in * API0[56] + API0[57])
    L = clamp(l_a*l_b + l_c)
    G0 = API0[72]*g00 + API0[73]*g01 + API0[74]*g02 + API0[75]
    G1 = API0[76]*g10 + API0[77]*g11 + API0[78]*g12 + API0[79]
    BASE.rgb = API0[60:62] * Q^2 * H * API0[64] * L * t2.y
    MRT0.rgb = BASE.rgb iff G0 > 0 and G1 > 0, else 0
    MRT0.a = 0

The symbolic native inputs and renderer resource meanings remain withheld.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

SHADER='80CA0638';NATIVE='80CA076D'
NATIVE_SHA='bb2a24680521c751a1b4fa0fd374ba03401e76e9a4cd67ceaa75b208377388ee'
GCN_SHA='81821c32c47636e4d1f071800a41eb017c78997fe0b847fa7746771abdcd4da8'
GCN_BYTES=832;EXPECTED_INSTANCES=3;EXPECTED_MATERIALS=3;EXPECTED_TERMINAL='000000000334'
ANCHORS=[
 '/*0000000001d4: f09c0300 00021010*/ image_sample_lz v[16:17], v[16:19], s[8:15], s[0:3] dmask:3',
 '/*0000000001dc: c2800534         */ s_buffer_load_dwordx4 s[0:3], s[4:7], 0x34',
 '/*0000000001e0: c2440520         */ s_buffer_load_dwordx2 s[8:9], s[4:7], 0x20',
 '/*0000000001e4: c2450538         */ s_buffer_load_dwordx2 s[10:11], s[4:7], 0x38',
 '/*0000000001e8: c2860548         */ s_buffer_load_dwordx4 s[12:15], s[4:7], 0x48',
 '/*0000000001ec: c288054c         */ s_buffer_load_dwordx4 s[16:19], s[4:7], 0x4c',
 '/*0000000001f8: c28a053c         */ s_buffer_load_dwordx4 s[20:23], s[4:7], 0x3c',
 '/*00000000020c: c2010540         */ s_buffer_load_dword s2, s[4:7], 0x40',
 '/*000000000224: c2008545         */ s_buffer_load_dword s1, s[4:7], 0x45',
 '/*000000000228: d282080b 042c1109*/ v_mad_f32       v11, v9, s8, v11 clamp',
 '/*00000000024c: 1010170b         */ v_mul_f32       v8, v11, v11',
 '/*000000000250: d2820807 241c150d*/ v_mad_f32       v7, -v13, s10, v7 clamp',
 '/*000000000258: d2820801 04060105*/ v_mad_f32       v1, v5, v0, v1 clamp',
 '/*000000000270: 10080f08         */ v_mul_f32       v4, v8, v7',
 '/*000000000284: 10040814         */ v_mul_f32       v2, s20, v4',
 '/*000000000288: 100a0815         */ v_mul_f32       v5, s21, v4',
 '/*00000000028c: 10080816         */ v_mul_f32       v4, s22, v4',
 '/*000000000290: 060c0c0f         */ v_add_f32       v6, s15, v6',
 '/*000000000294: 06060613         */ v_add_f32       v3, s19, v3',
 '/*000000000298: 10022301         */ v_mul_f32       v1, v1, v17',
 '/*0000000002ac: 10040402         */ v_mul_f32       v2, s2, v2',
 '/*0000000002b0: 100a0a02         */ v_mul_f32       v5, s2, v5',
 '/*0000000002b4: 10080802         */ v_mul_f32       v4, s2, v4',
 '/*0000000002b8: d0060002 00010103*/ v_cmp_le_f32    s[2:3], v3, 0',
 '/*0000000002c0: 7c0c0c80         */ v_cmp_ge_f32    vcc, 0, v6',
 '/*0000000002c4: 10040501         */ v_mul_f32       v2, v1, v2',
 '/*0000000002c8: 10060b01         */ v_mul_f32       v3, v1, v5',
 '/*0000000002cc: 10020901         */ v_mul_f32       v1, v1, v4',
 '/*0000000002dc: 88ea6a02         */ s_or_b64        vcc, s[2:3], vcc',
 '/*0000000002e0: d2000001 01a90101*/ v_cndmask_b32   v1, v1, 0, vcc',
 '/*0000000002e8: d2000003 01a90103*/ v_cndmask_b32   v3, v3, 0, vcc',
 '/*0000000002f0: d2000002 01a90102*/ v_cndmask_b32   v2, v2, 0, vcc',
 '/*00000000032c: 5e000702         */ v_cvt_pkrtz_f16_f32 v0, v2, v3',
 '/*000000000330: 5e020d01         */ v_cvt_pkrtz_f16_f32 v1, v1, v6',
 '/*000000000334: f8001c0f 00000100*/ exp             mrt0, v0, v0, v1, v1 done compr vm',
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
  exp=[('000000000040','image_load_mip',[1],'x'),('000000000048','image_sample',[0],'xyzw'),('0000000001D4','image_sample_lz',[2],'xy')]
  if got!=exp:v.append(f'image instruction scope drift {got!r}')

 cr=next((x for x in c.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if c.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or not cr:v.append('cbuffer usage not exact/present')
 else:
  by={x.get('address'):x for x in cr.get('loads',[])}
  expected={
   '0000000001DC':(0,[52,53,54,55],[0,1,2,3]),
   '0000000001E0':(0,[32,33],[8,9]),
   '0000000001E4':(0,[56,57],[10,11]),
   '0000000001E8':(0,[72,73,74,75],[12,13,14,15]),
   '0000000001EC':(0,[76,77,78,79],[16,17,18,19]),
   '0000000001F8':(0,[60,61,62,63],[20,21,22,23]),
   '00000000020C':(0,[64],[2]),
   '000000000224':(0,[69],[1]),
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
  if tr.get('terminal_mrt0_operands')!=['v0','v0','v1','v1']:v.append('terminal operands drift')
  required_tex={(0,x,'000000000048') for x in 'xyz'}|{(1,'x','000000000040'),(2,'y','0000000001D4')}
  for ch,colordw in [('R',60),('G',61),('B',62)]:
   q=tr['channels'][ch]['value_slice']
   tex={(int(x['texture_index']),x['channel'],x['sample_address']) for x in q.get('texture_sample_channels',[])}
   if tex!=required_tex:v.append(f'{ch}: terminal texture leaf drift {sorted(tex)}')
   cbq={str(k):set(z) for k,z in (q.get('cbuffer_dwords') or {}).items()}
   if set(cbq)-{'0'}:v.append(f'{ch}: unexpected non-API0 MRT0 cbuffer leaves {cbq}')
   required={32,33,56,57,colordw,64}
   if not required.issubset(cbq.get('0',set())):
    v.append(f'{ch}: terminal coefficient leaves missing {sorted(required-cbq.get("0",set()))}')
  aq=tr['channels']['A']['value_slice']
  if aq.get('literals')!=['0'] or aq.get('texture_sample_channels') or aq.get('cbuffer_dwords') or aq.get('unknown_registers'):
   v.append(f'alpha is not exact zero-only {aq}')
  union=tr.get('mrt0_value_union') or {}
  alltex={(int(x['texture_index']),x['channel']) for x in union.get('texture_sample_channels',[])}
  if (0,'w') in alltex or (2,'x') in alltex:v.append(f'dead sampled channel reached MRT0 unexpectedly {sorted(alltex)}')
  api0=set((union.get('cbuffer_dwords') or {}).get('0',[]))
  for dead in (63,69):
   if dead in api0:v.append(f'API0[{dead}] unexpectedly reaches MRT0 value slice')
  if '12' in (union.get('cbuffer_dwords') or {}):v.append('API12 unexpectedly reaches MRT0')

 missing=[x for x in ANCHORS if x not in asm]
 if missing:v.append(f'missing exact native anchors {missing}')

 out={
  'schema':'d1_tower_light_80ca0638_dual_gated_mrt0_factorization/v1',
  'status':'D1_TOWER_LIGHT_80CA0638_DUAL_GATED_MRT0_FACTORIZATION_EXACT' if not v else 'D1_TOWER_LIGHT_80CA0638_DUAL_GATED_MRT0_FACTORIZATION_PARTIAL',
  'shader':SHADER,'native_shader':NATIVE,'gcn_sha256':GCN_SHA,
  'instance_count':EXPECTED_INSTANCES,'unique_material_count':len(mats),
  'exact_tail_symbols':{
   'Q':'v11 after 0x228 = clamp(q_in*API0[32]+API0[33])',
   'H':'v7 after 0x250 = clamp(-h_in*API0[56]+API0[57])',
   'L':'v1 after 0x258 = clamp(l_a*l_b+l_c)',
   'C':'API0[60:62].rgb','S':'API0[64]','T':'t2.y',
   'G0':'API0[72]*g00 + API0[73]*g01 + API0[74]*g02 + API0[75]',
   'G1':'API0[76]*g10 + API0[77]*g11 + API0[78]*g12 + API0[79]',
  },
  'exact_terminal_equation':{
   'base_rgb':'API0[60:62].rgb * Q^2 * H * API0[64] * L * t2.y',
   'gate':'G0 > 0 AND G1 > 0',
   'mrt0_rgb':'BASE.rgb if G0 > 0 and G1 > 0 else (0,0,0)',
   'mrt0_a':'0',
   'vector_form':'MRT0.rgb = API0[60:62].rgb * Q^2 * H * API0[64] * L * t2.y iff G0 > 0 and G1 > 0, else 0',
  },
  'predicate_proof':{
   'first_compare':'v_cmp_le_f32 s[2:3], G1, 0',
   'second_compare':'v_cmp_ge_f32 vcc, 0, G0',
   'combine':'s_or_b64 vcc, s[2:3], vcc',
   'zero_when':'G0 <= 0 OR G1 <= 0',
   'kept_when':'G0 > 0 AND G1 > 0',
  },
  'negative_proof':{
   't0_alpha_reaches_mrt0':False,'t2_x_reaches_mrt0':False,
   'api0_dword63_reaches_mrt0_value':False,'api0_dword69_reaches_mrt0_value':False,
   'api12_reaches_mrt0':False,
  },
  'semantic_boundary':{
   'terminal_arithmetic':'EXACT_NATIVE_GCN',
   'dual_gate_predicate':'EXACT_NATIVE_GCN',
   'serialized_ps_texture_bindings':'NONE_FOR_3_FAMILY_MATERIALS',
   'renderer_t0_t1_t2_human_semantics':'WITHHELD',
   'symbols_Q_H_L_G0_G1_human_semantics':'WITHHELD',
   'portable_light_model_mapping':'WITHHELD',
  },
  'violations':v,
  'policy':'Exact native GCN arithmetic and dual gate predicate only. Gate coefficients are proven by native anchors/cbuffer provenance; predicate SGPR/VCC dataflow is not misrepresented as ordinary MRT0 value leaves.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'equation':out['exact_terminal_equation'],'predicate':out['predicate_proof'],'violations':v},indent=2))
 return 0 if not v else 2

if __name__=='__main__':raise SystemExit(main())
