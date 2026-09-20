#!/usr/bin/env python3
"""Fail-closed terminal MRT0 factorization for Tower light PS 809DCE96.

Exact native arithmetic promoted here:
    Q = clamp(P * API0[32] + API0[33])
    H = clamp(-R * API0[56] + API0[57])
    L = clamp(A * B + C)
    MRT0.rgb = API0[60:63].rgb * Q^2 * H * API0[64] * L * t2.y
    MRT0.a = 0

P, R, A, B and C are native symbolic intermediates. Their upstream renderer-input
semantics remain withheld.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

SHADER='809DCE96'
NATIVE='809DCE97'
NATIVE_SHA='06fa34544414e55a01669615b99af5cc591f0be8b27fafd806150233829958b2'
GCN_SHA='9a5bce130475b1a9d6ec2c15581823baeb777790c29fc23b45b92b6847fb9657'
GCN_BYTES=728
EXPECTED_INSTANCES=103
EXPECTED_MATERIALS=36
EXPECTED_TERMINAL='0000000002CC'

ANCHORS=[
 '/*0000000001d4: f09c0300 00020c0c*/ image_sample_lz v[12:13], v[12:15], s[8:15], s[0:3] dmask:3',
 '/*0000000001dc: c2800534         */ s_buffer_load_dwordx4 s[0:3], s[4:7], 0x34',
 '/*0000000001e0: c2440520         */ s_buffer_load_dwordx2 s[8:9], s[4:7], 0x20',
 '/*0000000001e4: c2450538         */ s_buffer_load_dwordx2 s[10:11], s[4:7], 0x38',
 '/*0000000001f0: c286053c         */ s_buffer_load_dwordx4 s[12:15], s[4:7], 0x3c',
 '/*000000000204: c2010540         */ s_buffer_load_dword s2, s[4:7], 0x40',
 '/*00000000021c: c2008545         */ s_buffer_load_dword s1, s[4:7], 0x45',
 '/*000000000220: d2820803 040c1109*/ v_mad_f32       v3, v9, s8, v3 clamp',
 '/*00000000023c: 10060703         */ v_mul_f32       v3, v3, v3',
 '/*000000000240: d2820807 241c1508*/ v_mad_f32       v7, -v8, s10, v7 clamp',
 '/*000000000248: d2820801 04060105*/ v_mad_f32       v1, v5, v0, v1 clamp',
 '/*000000000258: 10040f03         */ v_mul_f32       v2, v3, v7',
 '/*000000000264: 1006040c         */ v_mul_f32       v3, s12, v2',
 '/*000000000268: 1008040d         */ v_mul_f32       v4, s13, v2',
 '/*00000000026c: 1004040e         */ v_mul_f32       v2, s14, v2',
 '/*000000000270: 10021b01         */ v_mul_f32       v1, v1, v13',
 '/*000000000284: 10060602         */ v_mul_f32       v3, s2, v3',
 '/*000000000288: 10080802         */ v_mul_f32       v4, s2, v4',
 '/*00000000028c: 10040402         */ v_mul_f32       v2, s2, v2',
 '/*000000000290: 10060701         */ v_mul_f32       v3, v1, v3',
 '/*000000000294: 10080901         */ v_mul_f32       v4, v1, v4',
 '/*000000000298: 10020501         */ v_mul_f32       v1, v1, v2',
 '/*0000000002a8: 7e0c0280         */ v_mov_b32       v6, 0',
 '/*0000000002c4: 5e000903         */ v_cvt_pkrtz_f16_f32 v0, v3, v4',
 '/*0000000002c8: 5e020d01         */ v_cvt_pkrtz_f16_f32 v1, v1, v6',
 '/*0000000002cc: f8001c0f 00000100*/ exp             mrt0, v0, v0, v1, v1 done compr vm',
]

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--material-manifest',type=Path,required=True)
 ap.add_argument('--shader-report',type=Path,required=True)
 ap.add_argument('--image-usage',type=Path,required=True)
 ap.add_argument('--cbuffer-usage',type=Path,required=True)
 ap.add_argument('--terminal-mrt0',type=Path,required=True)
 ap.add_argument('--disasm',type=Path,required=True)
 ap.add_argument('--out',type=Path,required=True)
 a=ap.parse_args()
 m=json.loads(a.material_manifest.read_text())
 s=json.loads(a.shader_report.read_text())
 i=json.loads(a.image_usage.read_text())
 c=json.loads(a.cbuffer_usage.read_text())
 t=json.loads(a.terminal_mrt0.read_text())
 asm=a.disasm.read_text(errors='replace')
 v=[]

 if m.get('status')!='D1_WORLD_LIGHT_MATERIAL_MANIFEST_COMPLETE':v.append('material manifest not exact')
 freq=int((m.get('pixel_shader_frequency') or {}).get(SHADER,-1))
 if freq!=EXPECTED_INSTANCES:v.append(f'instance count drift {freq} != {EXPECTED_INSTANCES}')
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
   ('0000000001D4','image_sample_lz',[2],'xy'),
  ]
  if got!=exp:v.append(f'image instruction scope drift {got!r}')

 cr=next((x for x in c.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if c.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or not cr:v.append('cbuffer usage not exact/present')
 else:
  by={x.get('address'):x for x in cr.get('loads',[])}
  expected={
   '0000000001DC':(0,[52,53,54,55],[0,1,2,3]),
   '0000000001E0':(0,[32,33],[8,9]),
   '0000000001E4':(0,[56,57],[10,11]),
   '0000000001F0':(0,[60,61,62,63],[12,13,14,15]),
   '000000000204':(0,[64],[2]),
   '00000000021C':(0,[69],[1]),
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
  family={(0,x,'000000000048') for x in 'xyz'}|{(1,'x','000000000040'),(2,'y','0000000001D4')}
  for ch,colordw in [('R',60),('G',61),('B',62)]:
   q=tr['channels'][ch]['value_slice']
   tex={(int(x['texture_index']),x['channel'],x['sample_address']) for x in q.get('texture_sample_channels',[])}
   if tex!=family:v.append(f'{ch}: terminal texture leaf drift {sorted(tex)}')
   cb={str(k):set(z) for k,z in q.get('cbuffer_dwords',{}).items()}
   if set(cb)-{'0'}:v.append(f'{ch}: unexpected non-API0 MRT0 cbuffer leaves {cb}')
   required={32,33,52,53,54,56,57,colordw,64}
   if not required.issubset(cb.get('0',set())):v.append(f'{ch}: terminal coefficient leaves missing {required-cb.get("0",set())}')
   if 63 in cb.get('0',set()) or 69 in cb.get('0',set()):
    v.append(f'{ch}: MRT1-only coefficient leaked into MRT0 {cb}')
  aq=tr['channels']['A']['value_slice']
  if aq.get('literals')!=['0'] or aq.get('texture_sample_channels') or aq.get('cbuffer_dwords'):
   v.append(f'alpha is not exact zero-only {aq}')
  alltex={(int(x['texture_index']),x['channel']) for ch in 'RGB' for x in tr['channels'][ch]['value_slice'].get('texture_sample_channels',[])}
  if (0,'w') in alltex or (2,'x') in alltex:v.append(f'dead sampled channel reached MRT0 unexpectedly {sorted(alltex)}')

 missing=[x for x in ANCHORS if x not in asm]
 if missing:v.append(f'missing exact native anchors {missing}')

 out={
  'schema':'d1_tower_light_809dce96_mrt0_factorization/v1',
  'status':'D1_TOWER_LIGHT_809DCE96_MRT0_FACTORIZATION_EXACT' if not v else 'D1_TOWER_LIGHT_809DCE96_MRT0_FACTORIZATION_PARTIAL',
  'shader':SHADER,'native_shader':NATIVE,'gcn_sha256':GCN_SHA,
  'instance_count':EXPECTED_INSTANCES,'unique_material_count':len(mats),
  'renderer_input_leaf_scope':{
   't0':'xyz only reach MRT0; sampled at 0x48',
   't1':'x only reaches MRT0; loaded at 0x40',
   't2':'y reaches MRT0; x does not; xy sampled at 0x1D4',
   'initial_vgpr_leaves':['v2','v3'],
  },
  'exact_tail_symbols':{
   'Q':'v3 after 0x220 = clamp(P * API0[32] + API0[33])',
   'H':'v7 after 0x240 = clamp(-R * API0[56] + API0[57])',
   'L':'v1 after 0x248 = clamp(A * B + C)',
   'T':'v13 = t2.y sampled at 0x1D4',
   'C':'(API0[60], API0[61], API0[62])',
   'S':'API0[64]',
  },
  'exact_terminal_equation':{
   'mrt0_r':'API0[60] * Q^2 * H * API0[64] * L * t2.y',
   'mrt0_g':'API0[61] * Q^2 * H * API0[64] * L * t2.y',
   'mrt0_b':'API0[62] * Q^2 * H * API0[64] * L * t2.y',
   'mrt0_a':'0',
   'vector_form':'MRT0.rgb = API0[60:63].rgb * Q^2 * H * API0[64] * L * t2.y',
  },
  'negative_proof':{
   't0_alpha_reaches_mrt0':False,
   't2_x_reaches_mrt0':False,
   'api0_dword63_reaches_mrt0':False,
   'api0_dword69_reaches_mrt0':False,
   'api12_reaches_mrt0':False,
  },
  'violations':v,
  'semantic_boundary':{
   'terminal_arithmetic':'EXACT_NATIVE_GCN',
   'serialized_ps_texture_bindings':f'NONE_FOR_{EXPECTED_MATERIALS}_FAMILY_MATERIALS',
   'renderer_t0_t1_t2_human_semantics':'WITHHELD',
   'symbols_P_R_A_B_C_human_semantics':'WITHHELD',
   'portable_light_model_mapping':'WITHHELD',
  },
  'policy':'The terminal equation is exact algebra over native symbolic leaves. No renderer resource, geometric variable, light type, or portable light-model meaning is inferred.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'equation':out['exact_terminal_equation'],'negative_proof':out['negative_proof'],'violations':v},indent=2))
 return 0 if not v else 2

if __name__=='__main__':raise SystemExit(main())
