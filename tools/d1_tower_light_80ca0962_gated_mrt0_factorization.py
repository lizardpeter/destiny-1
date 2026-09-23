#!/usr/bin/env python3
"""Fail-closed gated terminal MRT0 factorization for Tower light PS 80CA0962.

Exact native tail:
    Q = clamp(q_in * API0[44] + API0[45])
    L = clamp(l_a*l_b + l_c)
    V.rgb = API0[40:42] + API0[80:82] * (L * t2.y)
    K = API0[84] * Q^2
    G = API0[92]*g0 + API0[93]*g1 + API0[94]*g2 + API0[95]
    MRT0.rgb = V.rgb * K if G > 0 else 0
    MRT0.a = 0

The native q/l/g inputs and renderer resources remain semantically unnamed.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

SHADER='80CA0962';NATIVE='80CA096A'
NATIVE_SHA='20a78376557bd789db33157d0db7a65c9dfd22b1b82ab06cdfd1d63d5efb1644'
GCN_SHA='901a8eb11440726fcb643ac21f1857e5b150870b1c98f1d352995f2a968a22cc'
GCN_BYTES=876;EXPECTED_INSTANCES=8;EXPECTED_MATERIALS=8;EXPECTED_TERMINAL='000000000360'
ANCHORS=[
 '/*000000000234: f09c0300 00021010*/ image_sample_lz v[16:17], v[16:19], s[8:15], s[0:3] dmask:3',
 '/*00000000023c: c240052c         */ s_buffer_load_dwordx2 s[0:1], s[4:7], 0x2c',
 '/*000000000240: c284055c         */ s_buffer_load_dwordx4 s[8:11], s[4:7], 0x5c',
 '/*000000000248: c2860528         */ s_buffer_load_dwordx4 s[12:15], s[4:7], 0x28',
 '/*00000000024c: c2880550         */ s_buffer_load_dwordx4 s[16:19], s[4:7], 0x50',
 '/*000000000258: c2010554         */ s_buffer_load_dword s2, s[4:7], 0x54',
 '/*000000000268: c2018559         */ s_buffer_load_dword s3, s[4:7], 0x59',
 '/*000000000284: d2820802 040a0305*/ v_mad_f32       v2, v5, v1, v2 clamp',
 '/*000000000290: d2820807 041c0100*/ v_mad_f32       v7, v0, s0, v7 clamp',
 '/*000000000298: 10000609         */ v_mul_f32       v0, s9, v3',
 '/*0000000002a0: 10060f07         */ v_mul_f32       v3, v7, v7',
 '/*0000000002a4: 3e000808         */ v_mac_f32       v0, s8, v4',
 '/*0000000002ac: 10042302         */ v_mul_f32       v2, v2, v17',
 '/*0000000002b4: 7e08020c         */ v_mov_b32       v4, s12',
 '/*0000000002b8: 7e0a020d         */ v_mov_b32       v5, s13',
 '/*0000000002bc: 7e0c020e         */ v_mov_b32       v6, s14',
 '/*0000000002c0: 100e0610         */ v_mul_f32       v7, s16, v3',
 '/*0000000002c4: 10100611         */ v_mul_f32       v8, s17, v3',
 '/*0000000002c8: 10120612         */ v_mul_f32       v9, s18, v3',
 '/*0000000002cc: 3e001a0a         */ v_mac_f32       v0, s10, v13',
 '/*0000000002d0: 3e080410         */ v_mac_f32       v4, s16, v2',
 '/*0000000002d4: 3e0a0411         */ v_mac_f32       v5, s17, v2',
 '/*0000000002d8: 3e0c0412         */ v_mac_f32       v6, s18, v2',
 '/*0000000002e8: 10060602         */ v_mul_f32       v3, s2, v3',
 '/*0000000002ec: 0600000b         */ v_add_f32       v0, s11, v0',
 '/*0000000002f0: 10080704         */ v_mul_f32       v4, v4, v3',
 '/*0000000002f4: 100a0705         */ v_mul_f32       v5, v5, v3',
 '/*0000000002f8: 10060706         */ v_mul_f32       v3, v6, v3',
 '/*000000000308: 7c0c0080         */ v_cmp_ge_f32    vcc, 0, v0',
 '/*00000000031c: d2000002 01a90102*/ v_cndmask_b32   v2, v2, 0, vcc',
 '/*00000000032c: d2000005 01a90105*/ v_cndmask_b32   v5, v5, 0, vcc',
 '/*000000000334: d2000004 01a90104*/ v_cndmask_b32   v4, v4, 0, vcc',
 '/*000000000358: 5e000b04         */ v_cvt_pkrtz_f16_f32 v0, v4, v5',
 '/*00000000035c: 5e020d03         */ v_cvt_pkrtz_f16_f32 v1, v3, v6',
 '/*000000000360: f8001c0f 00000100*/ exp             mrt0, v0, v0, v1, v1 done compr vm',
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
  exp=[('000000000040','image_load_mip',[1],'x'),('000000000048','image_sample',[0],'xyzw'),('000000000234','image_sample_lz',[2],'xy')]
  if got!=exp:v.append(f'image instruction scope drift {got!r}')

 cr=next((x for x in c.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if c.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or not cr:v.append('cbuffer usage not exact/present')
 else:
  by={x.get('address'):x for x in cr.get('loads',[])}
  expected={
   '00000000023C':(0,[44,45],[0,1]),
   '000000000240':(0,[92,93,94,95],[8,9,10,11]),
   '000000000248':(0,[40,41,42,43],[12,13,14,15]),
   '00000000024C':(0,[80,81,82,83],[16,17,18,19]),
   '000000000258':(0,[84],[2]),
   '000000000268':(0,[89],[3]),
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
  expected_tex={(0,x,'000000000048') for x in 'xyz'}|{(1,'x','000000000040'),(2,'y','000000000234')}
  for ch,base,mod in [('R',40,80),('G',41,81),('B',42,82)]:
   q=tr['channels'][ch]['value_slice']
   tex={(int(x['texture_index']),x['channel'],x['sample_address']) for x in q.get('texture_sample_channels',[])}
   if tex!=expected_tex:v.append(f'{ch}: terminal texture leaf drift {sorted(tex)}')
   cbq={str(k):set(z) for k,z in (q.get('cbuffer_dwords') or {}).items()}
   if set(cbq)-{'0'}:v.append(f'{ch}: unexpected non-API0 MRT0 cbuffer leaves {cbq}')
   required={40,41,42,44,45,80,81,82,84,92,93,94,95}
   if not required.issubset(cbq.get('0',set())):
    v.append(f'{ch}: terminal coefficient leaves missing {sorted(required-cbq.get("0",set()))}')
  aq=tr['channels']['A']['value_slice']
  if aq.get('literals')!=['0'] or aq.get('texture_sample_channels') or aq.get('cbuffer_dwords') or aq.get('unknown_registers'):
   v.append(f'alpha is not exact zero-only {aq}')
  union=tr.get('mrt0_value_union') or {}
  alltex={(int(x['texture_index']),x['channel']) for x in union.get('texture_sample_channels',[])}
  if (0,'w') in alltex or (2,'x') in alltex:v.append(f'dead sampled channel reached MRT0 unexpectedly {sorted(alltex)}')
  api0=set((union.get('cbuffer_dwords') or {}).get('0',[]))
  for dead in (43,83,89):
   if dead in api0:v.append(f'API0[{dead}] unexpectedly reaches MRT0')
  if '12' in (union.get('cbuffer_dwords') or {}):v.append('API12 unexpectedly reaches MRT0')

 missing=[x for x in ANCHORS if x not in asm]
 if missing:v.append(f'missing exact native anchors {missing}')

 out={
  'schema':'d1_tower_light_80ca0962_gated_mrt0_factorization/v1',
  'status':'D1_TOWER_LIGHT_80CA0962_GATED_MRT0_FACTORIZATION_EXACT' if not v else 'D1_TOWER_LIGHT_80CA0962_GATED_MRT0_FACTORIZATION_PARTIAL',
  'shader':SHADER,'native_shader':NATIVE,'gcn_sha256':GCN_SHA,
  'instance_count':EXPECTED_INSTANCES,'unique_material_count':len(mats),
  'exact_tail_symbols':{
   'Q':'v7 after 0x290 = clamp(q_in*API0[44]+API0[45])',
   'L':'v2 after 0x284 = clamp(l_a*l_b+l_c)',
   'B':'API0[40:42].rgb','M':'API0[80:82].rgb','S':'API0[84]','T':'t2.y',
   'G':'API0[92]*g0 + API0[93]*g1 + API0[94]*g2 + API0[95]',
  },
  'exact_terminal_equation':{
   'vector_pre_scale':'V.rgb = API0[40:42].rgb + API0[80:82].rgb*(L*t2.y)',
   'scalar_scale':'K = API0[84] * Q^2',
   'gate':'G > 0',
   'mrt0_rgb':'V.rgb * K if G > 0 else (0,0,0)',
   'mrt0_a':'0',
   'vector_form':'MRT0.rgb = (API0[40:42].rgb + API0[80:82].rgb*(L*t2.y)) * API0[84] * Q^2 when G > 0, else 0',
  },
  'predicate_proof':{'compare':'v_cmp_ge_f32 vcc, 0, G','false_when':'G <= 0','kept_when':'G > 0'},
  'negative_proof':{
   't0_alpha_reaches_mrt0':False,'t2_x_reaches_mrt0':False,
   'api0_dword43_reaches_mrt0':False,'api0_dword83_reaches_mrt0':False,
   'api0_dword89_reaches_mrt0':False,'api12_reaches_mrt0':False,
  },
  'semantic_boundary':{
   'terminal_arithmetic':'EXACT_NATIVE_GCN',
   'serialized_ps_texture_bindings':'NONE_FOR_8_FAMILY_MATERIALS',
   'renderer_t0_t1_t2_human_semantics':'WITHHELD',
   'symbols_Q_L_G_human_semantics':'WITHHELD',
   'portable_light_model_mapping':'WITHHELD',
  },
  'violations':v,
  'policy':'Exact native GCN arithmetic and gate predicate only. Renderer inputs and native symbolic intermediates remain semantically unnamed without primary evidence.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'equation':out['exact_terminal_equation'],'negative_proof':out['negative_proof'],'violations':v},indent=2))
 return 0 if not v else 2

if __name__=='__main__':raise SystemExit(main())
