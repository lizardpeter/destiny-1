#!/usr/bin/env python3
"""Fail-closed terminal MRT0 factorization for the dominant Tower light PS 80AAE153.

This proof intentionally stops at native symbolic intermediates where renderer-input
semantics are not source-closed. It promotes exact arithmetic only.

For the current exact GCN program:
    Q = clamp(X * API0[40] + API0[41])
    L = clamp(native_upstream_mad_at_0x27C)
    MRT0.rgb = API0[76:78] * (Q*Q) * API0[80] * L * t2.y
    MRT0.a = 0

X and L remain native symbolic intermediates. Their upstream exact leaf set includes
renderer t0.rgb, t1.x, API0 constants and two initial VGPR leaves; this tool does not
rename those leaves as depth, light cookie, world position, etc.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path

SHADER='80AAE153'
NATIVE='80AAE154'
NATIVE_SHA='3bba0b8eed861a337299729d39404ebe00d4f3acf2ada2103043597e8b943035'
GCN_SHA='64d84f04fcd6864d2fff20f43da9118f2d20e532b5801bb67b7a9832008515d4'
GCN_BYTES=784
EXPECTED_INSTANCES=195
EXPECTED_TERMINAL='000000000304'

ANCHORS=[
 '/*000000000234: f09c0300 00020f0f*/ image_sample_lz v[15:16], v[15:18], s[8:15], s[0:3] dmask:3',
 '/*00000000023c: c2400528         */ s_buffer_load_dwordx2 s[0:1], s[4:7], 0x28',
 '/*000000000244: c284054c         */ s_buffer_load_dwordx4 s[8:11], s[4:7], 0x4c',
 '/*000000000250: c2010550         */ s_buffer_load_dword s2, s[4:7], 0x50',
 '/*000000000278: 7e080201         */ v_mov_b32       v4, s1',
 '/*00000000027c: d2820802 040a0305*/ v_mad_f32       v2, v5, v1, v2 clamp',
 '/*000000000288: d2820804 04100100*/ v_mad_f32       v4, v0, s0, v4 clamp',
 '/*000000000294: 10020904         */ v_mul_f32       v1, v4, v4',
 '/*0000000002a0: 10060208         */ v_mul_f32       v3, s8, v1',
 '/*0000000002a4: 10080209         */ v_mul_f32       v4, s9, v1',
 '/*0000000002a8: 1002020a         */ v_mul_f32       v1, s10, v1',
 '/*0000000002ac: 10042102         */ v_mul_f32       v2, v2, v16',
 '/*0000000002bc: 10060602         */ v_mul_f32       v3, s2, v3',
 '/*0000000002c0: 10080802         */ v_mul_f32       v4, s2, v4',
 '/*0000000002c4: 10020202         */ v_mul_f32       v1, s2, v1',
 '/*0000000002c8: 10060702         */ v_mul_f32       v3, v2, v3',
 '/*0000000002cc: 10080902         */ v_mul_f32       v4, v2, v4',
 '/*0000000002d0: 10020302         */ v_mul_f32       v1, v2, v1',
 '/*0000000002e0: 7e0c0280         */ v_mov_b32       v6, 0',
 '/*0000000002fc: 5e000903         */ v_cvt_pkrtz_f16_f32 v0, v3, v4',
 '/*000000000300: 5e020d01         */ v_cvt_pkrtz_f16_f32 v1, v1, v6',
 '/*000000000304: f8001c0f 00000100*/ exp             mrt0, v0, v0, v1, v1 done compr vm',
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
 if int((m.get('pixel_shader_frequency') or {}).get(SHADER,-1))!=EXPECTED_INSTANCES:v.append('instance count drift')
 mats=(m.get('pixel_shader_materials') or {}).get(SHADER,[])
 if len(mats)!=112:v.append(f'unique material count drift {len(mats)} != 112')
 if any(int((m.get('materials') or {}).get(x,{}).get('ps_texture_count',-1))!=0 for x in mats):
  v.append('serialized PS texture binding unexpectedly present')

 sr=next((x for x in s.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if s.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or not sr:v.append('shader report not exact/present')
 else:
  checks={'native_shader':NATIVE,'native_sha256':NATIVE_SHA,'gcn_sha256':GCN_SHA,'gcn_bytes':GCN_BYTES}
  for k,z in checks.items():
   if sr.get(k)!=z:v.append(f'{k} drift {sr.get(k)!r} != {z!r}')

 ir=next((x for x in i.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if i.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT' or not ir:v.append('image usage not exact/present')
 else:
  got=[(x['address'],x['opcode'],[(q['texture_index']) for q in x.get('resources',[])],x['dmask_channels']) for x in ir.get('instructions',[])]
  exp=[
   ('000000000040','image_load_mip',[1],'x'),
   ('000000000048','image_sample',[0],'xyzw'),
   ('000000000234','image_sample_lz',[2],'xy'),
  ]
  if got!=exp:v.append(f'image instruction scope drift {got!r}')

 cr=next((x for x in c.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if c.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or not cr:v.append('cbuffer usage not exact/present')
 else:
  by={x.get('address'):x for x in cr.get('loads',[])}
  expected={
   '00000000023C':(0,[40,41],[0,1]),
   '000000000244':(0,[76,77,78,79],[8,9,10,11]),
   '000000000250':(0,[80],[2]),
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
  expected_channels={
   'R':('x',76),'G':('y',77),'B':('z',78)
  }
  for ch,(tex0ch,colordw) in expected_channels.items():
   q=tr['channels'][ch]['value_slice']
   tex={(int(x['texture_index']),x['channel'],x['sample_address']) for x in q.get('texture_sample_channels',[])}
   required={(0,tex0ch,'000000000048'),(1,'x','000000000040'),(2,'y','000000000234')}
   # The terminal RGB may depend on all t0 RGB channels upstream, so require the
   # family-wide exact leaf set instead of pretending channels are independent.
   family={(0,x,'000000000048') for x in 'xyz'}|{(1,'x','000000000040'),(2,'y','000000000234')}
   if tex!=family:v.append(f'{ch}: terminal texture leaf drift {sorted(tex)}')
   cb={str(k):set(z) for k,z in q.get('cbuffer_dwords',{}).items()}
   if set(cb)-{'0'}:v.append(f'{ch}: unexpected non-API0 MRT0 cbuffer leaves {cb}')
   if colordw not in cb.get('0',set()) or 80 not in cb.get('0',set()) or not {40,41}.issubset(cb.get('0',set())):
    v.append(f'{ch}: terminal coefficient leaves missing {cb}')
   if 79 in cb.get('0',set()) or 85 in cb.get('0',set()):
    v.append(f'{ch}: MRT1-only coefficient leaked into MRT0 {cb}')
  aq=tr['channels']['A']['value_slice']
  if aq.get('literals')!=['0'] or aq.get('texture_sample_channels') or aq.get('cbuffer_dwords'):
   v.append(f'alpha is not exact zero-only {aq}')
  alltex={(int(x['texture_index']),x['channel']) for ch in 'RGB' for x in tr['channels'][ch]['value_slice'].get('texture_sample_channels',[])}
  if (0,'w') in alltex or (2,'x') in alltex:v.append(f'dead sampled channel reached MRT0 unexpectedly {sorted(alltex)}')

 missing=[x for x in ANCHORS if x not in asm]
 if missing:v.append(f'missing exact native anchors {missing}')

 out={
  'schema':'d1_tower_light_80aae153_mrt0_factorization/v1',
  'status':'D1_TOWER_LIGHT_80AAE153_MRT0_FACTORIZATION_EXACT' if not v else 'D1_TOWER_LIGHT_80AAE153_MRT0_FACTORIZATION_PARTIAL',
  'shader':SHADER,'native_shader':NATIVE,'gcn_sha256':GCN_SHA,
  'instance_count':EXPECTED_INSTANCES,'unique_material_count':len(mats),
  'renderer_input_leaf_scope':{
   't0':'xyz only reach MRT0; sampled at 0x48',
   't1':'x only reaches MRT0; loaded at 0x40',
   't2':'y reaches MRT0; x does not; xy sampled at 0x234',
   'initial_vgpr_leaves':['v2','v3'],
  },
  'exact_tail_symbols':{
   'L':'v2 after 0x27C = clamp(v5*v1 + prior_v2)',
   'Q':'v4 after 0x288 = clamp(prior_v0 * API0[40] + API0[41])',
   'Q2':'v1 after 0x294 = Q*Q',
   'T':'v16 from t2.y sampled at 0x234',
   'C':'(API0[76], API0[77], API0[78])',
   'S':'API0[80]',
  },
  'exact_terminal_equation':{
   'mrt0_r':'API0[76] * Q^2 * API0[80] * L * t2.y',
   'mrt0_g':'API0[77] * Q^2 * API0[80] * L * t2.y',
   'mrt0_b':'API0[78] * Q^2 * API0[80] * L * t2.y',
   'mrt0_a':'0',
   'vector_form':'MRT0.rgb = API0[76:79].rgb * Q^2 * API0[80] * L * t2.y',
  },
  'negative_proof':{
   't0_alpha_reaches_mrt0':False,
   't2_x_reaches_mrt0':False,
   'api0_dword79_reaches_mrt0':False,
   'api0_dword85_reaches_mrt0':False,
   'api12_reaches_mrt0':False,
  },
  'violations':v,
  'semantic_boundary':{
   'terminal_arithmetic':'EXACT_NATIVE_GCN',
   'serialized_ps_texture_bindings':'NONE_FOR_112_FAMILY_MATERIALS',
   'renderer_t0_t1_t2_human_semantics':'WITHHELD',
   'symbol_L_human_semantics':'WITHHELD',
   'symbol_Q_human_semantics':'WITHHELD',
   'initial_vgpr_human_semantics':'WITHHELD',
   'portable_light_model_mapping':'WITHHELD',
  },
  'policy':'The equation is exact algebra over native symbolic leaves. It does not identify renderer t# meanings, light type, position/radius semantics, or a Blender light-model mapping.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'equation':out['exact_terminal_equation'],'negative_proof':out['negative_proof'],'violations':v},indent=2))
 return 0 if not v else 2

if __name__=='__main__':raise SystemExit(main())
