#!/usr/bin/env python3
"""Fail-closed terminal MRT0 factorization for Tower light PS 80CA0ED3.

This proof promotes exact native arithmetic only. Renderer-resource meanings and
upstream symbolic VGPR meanings remain withheld when source evidence does not name them.

Current exact terminal factorization:
    Q = clamp(q_in * API0[56] + API0[57])
    H = clamp(-h_in * API0[88] + API0[89])
    L = clamp(l_a * l_b + l_c)
    U = clamp(u_in + 0.5)
    A = L * t2.y
    V.rgb = API0[52:54] + API0[92:94] * A + API0[48:50] * U^2
    MRT0.rgb = V.rgb * API0[96] * H * Q^2
    MRT0.a = 0

The q/h/l/u inputs remain exact native symbolic intermediates, not guessed human
light parameters.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

SHADER='80CA0ED3'
NATIVE='80CA0EDE'
NATIVE_SHA='626be17ec595e0498f5f3b5812c281ec64047be068f2477df7f5e0b9f02d04f1'
GCN_SHA='0eca19dfb3719477022311361e4217ee4262c362feeb76bbf39e21f45580328a'
GCN_BYTES=1024
EXPECTED_INSTANCES=60
EXPECTED_MATERIALS=53
EXPECTED_TERMINAL='0000000003F4'

ANCHORS=[
 '/*000000000294: f09c0300 00a31113*/ image_sample_lz v[17:18], v[19:22], s[12:19], s[20:23] dmask:3',
 '/*0000000002a4: f09c0100 01060113*/ image_sample_lz v1, v[19:22], s[24:31], s[32:35]',
 '/*0000000002ac: c286054c         */ s_buffer_load_dwordx4 s[12:15], s[4:7], 0x4c',
 '/*0000000002b0: c2410538         */ s_buffer_load_dwordx2 s[2:3], s[4:7], 0x38',
 '/*0000000002b4: c2480558         */ s_buffer_load_dwordx2 s[16:17], s[4:7], 0x58',
 '/*0000000002b8: c28a0534         */ s_buffer_load_dwordx4 s[20:23], s[4:7], 0x34',
 '/*0000000002c0: c28c055c         */ s_buffer_load_dwordx4 s[24:27], s[4:7], 0x5c',
 '/*0000000002c4: c28e0530         */ s_buffer_load_dwordx4 s[28:31], s[4:7], 0x30',
 '/*0000000002d4: c2008560         */ s_buffer_load_dword s1, s[4:7], 0x60',
 '/*0000000002d8: c2020565         */ s_buffer_load_dword s4, s[4:7], 0x65',
 '/*000000000318: d2820802 040a0f05*/ v_mad_f32       v2, v5, v7, v2 clamp',
 '/*000000000320: 7e065503         */ v_rcp_f32       v3, v3',
 '/*000000000338: d2820809 04240500*/ v_mad_f32       v9, v0, s2, v9 clamp',
 '/*000000000348: 10042502         */ v_mul_f32       v2, v2, v18',
 '/*000000000358: d2820805 24142104*/ v_mad_f32       v5, -v4, s16, v5 clamp',
 '/*000000000360: d2060804 0001e106*/ v_add_f32       v4, v6, 0.5 clamp',
 '/*000000000370: 100c1309         */ v_mul_f32       v6, v9, v9',
 '/*000000000378: 3e060418         */ v_mac_f32       v3, s24, v2',
 '/*00000000037c: 3e100419         */ v_mac_f32       v8, s25, v2',
 '/*000000000380: 3e14041a         */ v_mac_f32       v10, s26, v2',
 '/*000000000384: 10040904         */ v_mul_f32       v2, v4, v4',
 '/*000000000394: 100a0d05         */ v_mul_f32       v5, v5, v6',
 '/*000000000398: 3e06041c         */ v_mac_f32       v3, s28, v2',
 '/*00000000039c: 3e10041d         */ v_mac_f32       v8, s29, v2',
 '/*0000000003a0: 3e14041e         */ v_mac_f32       v10, s30, v2',
 '/*0000000003b0: 10000a01         */ v_mul_f32       v0, s1, v5',
 '/*0000000003b8: 10060103         */ v_mul_f32       v3, v3, v0',
 '/*0000000003bc: 100a0108         */ v_mul_f32       v5, v8, v0',
 '/*0000000003c0: 1000010a         */ v_mul_f32       v0, v10, v0',
 '/*0000000003d0: 7e040280         */ v_mov_b32       v2, 0',
 '/*0000000003ec: 5e020b03         */ v_cvt_pkrtz_f16_f32 v1, v3, v5',
 '/*0000000003f0: 5e000500         */ v_cvt_pkrtz_f16_f32 v0, v0, v2',
 '/*0000000003f4: f8001c0f 00000001*/ exp             mrt0, v1, v1, v0, v0 done compr vm',
]

def norm(x): return str(x).upper().removeprefix('0X').zfill(8)

def main()->int:
 ap=argparse.ArgumentParser()
 for n in ('material-manifest','shader-report','image-usage','cbuffer-usage','terminal-mrt0','disasm','out'):
  ap.add_argument('--'+n,type=Path,required=True)
 a=ap.parse_args();v=[]
 m=json.loads(a.material_manifest.read_text());s=json.loads(a.shader_report.read_text())
 i=json.loads(a.image_usage.read_text());c=json.loads(a.cbuffer_usage.read_text())
 t=json.loads(a.terminal_mrt0.read_text());asm=a.disasm.read_text(errors='replace')

 if m.get('status')!='D1_WORLD_LIGHT_MATERIAL_MANIFEST_COMPLETE': v.append('material manifest not exact')
 if int((m.get('pixel_shader_frequency') or {}).get(SHADER,-1))!=EXPECTED_INSTANCES: v.append('instance count drift')
 mats=(m.get('pixel_shader_materials') or {}).get(SHADER,[])
 if len(mats)!=EXPECTED_MATERIALS: v.append(f'unique material count drift {len(mats)} != {EXPECTED_MATERIALS}')
 if any(int((m.get('materials') or {}).get(x,{}).get('ps_texture_count',-1))!=0 for x in mats):
  v.append('serialized PS texture binding unexpectedly present')

 sr=next((x for x in s.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if s.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or not sr: v.append('shader report not exact/present')
 else:
  for k,z in {'native_shader':NATIVE,'native_sha256':NATIVE_SHA,'gcn_sha256':GCN_SHA,'gcn_bytes':GCN_BYTES}.items():
   if sr.get(k)!=z: v.append(f'{k} drift {sr.get(k)!r} != {z!r}')

 ir=next((x for x in i.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if i.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT' or not ir: v.append('image usage not exact/present')
 else:
  got=[(x['address'],x['opcode'],[q['texture_index'] for q in x.get('resources',[])],x['dmask_channels']) for x in ir.get('instructions',[])]
  exp=[
   ('000000000040','image_load_mip',[1],'x'),
   ('000000000048','image_sample',[0],'xyzw'),
   ('000000000294','image_sample_lz',[2],'xy'),
   ('0000000002A4','image_sample_lz',[3],'x'),
  ]
  if got!=exp: v.append(f'image instruction scope drift {got!r}')

 cr=next((x for x in c.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if c.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or not cr: v.append('cbuffer usage not exact/present')
 else:
  by={x.get('address'):x for x in cr.get('loads',[])}
  expected={
   '000000000200':(0,[40],[0]),
   '0000000002AC':(0,[76,77,78,79],[12,13,14,15]),
   '0000000002B0':(0,[56,57],[2,3]),
   '0000000002B4':(0,[88,89],[16,17]),
   '0000000002B8':(0,[52,53,54,55],[20,21,22,23]),
   '0000000002C0':(0,[92,93,94,95],[24,25,26,27]),
   '0000000002C4':(0,[48,49,50,51],[28,29,30,31]),
   '0000000002D4':(0,[96],[1]),
   '0000000002D8':(0,[101],[4]),
  }
  for addr,(api,dw,dst) in expected.items():
   q=by.get(addr)
   if not q or q.get('api_slot')!=api or q.get('dword_indices')!=dw or q.get('destination')!=dst:
    v.append(f'{addr}: cbuffer provenance drift {q}')

 tr=next((x for x in t.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if t.get('status')!='D1_GCN_TERMINAL_MRT0_DEPENDENCY_CENSUS_EXACT' or not tr: v.append('terminal MRT0 slice not exact/present')
 else:
  if tr.get('terminal_mrt0_export_address')!=EXPECTED_TERMINAL or not tr.get('terminal_mrt0_compressed'): v.append('terminal export identity drift')
  if tr.get('terminal_mrt0_operands')!=['v1','v1','v0','v0']: v.append('terminal operands drift')
  family={(0,x,'000000000048') for x in 'xyz'}|{(1,'x','000000000040'),(2,'y','000000000294')}
  for ch,base,blend,quad in [('R',52,92,48),('G',53,93,49),('B',54,94,50)]:
   q=tr['channels'][ch]['value_slice']
   tex={(int(x['texture_index']),x['channel'],x['sample_address']) for x in q.get('texture_sample_channels',[])}
   if tex!=family: v.append(f'{ch}: terminal texture leaf drift {sorted(tex)}')
   cb={str(k):set(z) for k,z in q.get('cbuffer_dwords',{}).items()}
   if set(cb)-{'0'}: v.append(f'{ch}: unexpected non-API0 MRT0 cbuffer leaves {cb}')
   required={base,blend,quad,56,57,76,77,78,88,89,96}
   if not required.issubset(cb.get('0',set())): v.append(f'{ch}: terminal coefficient leaves missing {sorted(required-cb.get("0",set()))}')
   if 101 in cb.get('0',set()): v.append(f'{ch}: MRT1-only API0[101] leaked into MRT0')
  aq=tr['channels']['A']['value_slice']
  if aq.get('literals')!=['0'] or aq.get('texture_sample_channels') or aq.get('cbuffer_dwords') or aq.get('unknown_registers'):
   v.append(f'alpha is not exact zero-only {aq}')
  union=tr.get('mrt0_value_union') or {}
  alltex={(int(x['texture_index']),x['channel']) for x in union.get('texture_sample_channels',[])}
  if (0,'w') in alltex or (2,'x') in alltex or any(ti==3 for ti,_ in alltex):
   v.append(f'dead sampled channel/resource reached MRT0 unexpectedly {sorted(alltex)}')
  if '12' in (union.get('cbuffer_dwords') or {}): v.append('API12 unexpectedly reaches MRT0')
  if 101 in set((union.get('cbuffer_dwords') or {}).get('0',[])): v.append('API0[101] unexpectedly reaches MRT0')

 missing=[x for x in ANCHORS if x not in asm]
 if missing: v.append(f'missing exact native anchors {missing}')

 out={
  'schema':'d1_tower_light_80ca0ed3_mrt0_factorization/v1',
  'status':'D1_TOWER_LIGHT_80CA0ED3_MRT0_FACTORIZATION_EXACT' if not v else 'D1_TOWER_LIGHT_80CA0ED3_MRT0_FACTORIZATION_PARTIAL',
  'shader':SHADER,'native_shader':NATIVE,'gcn_sha256':GCN_SHA,
  'instance_count':EXPECTED_INSTANCES,'unique_material_count':len(mats),
  'renderer_input_leaf_scope':{
   't0':'xyz reach MRT0; alpha does not',
   't1':'x reaches MRT0',
   't2':'y reaches MRT0; x does not',
   't3':'sampled by the shader but does not reach MRT0',
  },
  'exact_tail_symbols':{
   'Q':'v9 after 0x338 = clamp(q_in * API0[56] + API0[57])',
   'H':'v5 after 0x358 = clamp(-h_in * API0[88] + API0[89])',
   'L':'v2 after 0x318 = clamp(l_a*l_b + l_c)',
   'U':'v4 after 0x360 = clamp(u_in + 0.5)',
   'A':'v2 after 0x348 = L * t2.y',
   'C0':'API0[52:54].rgb',
   'C1':'API0[92:94].rgb',
   'C2':'API0[48:50].rgb',
   'S':'API0[96]',
  },
  'exact_terminal_equation':{
   'vector_pre_scale':'V.rgb = API0[52:54].rgb + API0[92:94].rgb*(L*t2.y) + API0[48:50].rgb*U^2',
   'scalar_scale':'K = API0[96] * H * Q^2',
   'mrt0_rgb':'MRT0.rgb = V.rgb * K',
   'mrt0_a':'0',
   'vector_form':'MRT0.rgb = (API0[52:54].rgb + API0[92:94].rgb*(L*t2.y) + API0[48:50].rgb*U^2) * API0[96] * H * Q^2',
  },
  'negative_proof':{
   't0_alpha_reaches_mrt0':False,
   't2_x_reaches_mrt0':False,
   't3_reaches_mrt0':False,
   'api0_dword101_reaches_mrt0':False,
   'api12_reaches_mrt0':False,
  },
  'semantic_boundary':{
   'terminal_arithmetic':'EXACT_NATIVE_GCN',
   'serialized_ps_texture_bindings':'NONE_FOR_53_FAMILY_MATERIALS',
   'renderer_t0_t1_t2_t3_human_semantics':'WITHHELD',
   'symbols_Q_H_L_U_human_semantics':'WITHHELD',
   'portable_light_model_mapping':'WITHHELD',
  },
  'violations':v,
  'policy':'The terminal factorization is exact native GCN arithmetic. Renderer-resource identities and upstream symbolic terms are intentionally not renamed without primary evidence.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'equation':out['exact_terminal_equation'],'negative_proof':out['negative_proof'],'violations':v},indent=2))
 return 0 if not v else 2

if __name__=='__main__': raise SystemExit(main())
