#!/usr/bin/env python3
"""Exact gated terminal MRT0 factorization for Tower light PS 80CA0451.

Promoted native arithmetic:
    Q = clamp(P * API0[32] + API0[33])
    H = clamp(-R * API0[56] + API0[57])
    L = clamp(A * B + C)
    G = API0[73]*U0 + API0[72]*U1 + API0[74]*U2 + API0[75]
    BASE.rgb = API0[60:63].rgb * Q^2 * H * API0[64] * L * t2.y
    MRT0.rgb = BASE.rgb when G > 0, otherwise 0
    MRT0.a = 0

P/R/A/B/C/U0/U1/U2 remain native symbolic intermediates. The compare/cndmask
predicate is part of terminal provenance and must not be discarded.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

SHADER='80CA0451';NATIVE='80CA0482'
NATIVE_SHA='80cb0ee0589c356f87f56f982957bc3b0ceaeda756682135d5101081a4c52ea4'
GCN_SHA='e82e0a465a88a9120a8e38377e3bd42b7503c8e64034ada4fcf4fa743d28fbdb'
GCN_BYTES=800;EXPECTED_INSTANCES=46;EXPECTED_MATERIALS=46;EXPECTED_TERMINAL='000000000314'

ANCHORS=[
 '/*0000000001d4: f09c0300 00021010*/ image_sample_lz v[16:17], v[16:19], s[8:15], s[0:3] dmask:3',
 '/*0000000001e0: c2440520         */ s_buffer_load_dwordx2 s[8:9], s[4:7], 0x20',
 '/*0000000001e4: c2450538         */ s_buffer_load_dwordx2 s[10:11], s[4:7], 0x38',
 '/*0000000001e8: c2860548         */ s_buffer_load_dwordx4 s[12:15], s[4:7], 0x48',
 '/*0000000001f4: c288053c         */ s_buffer_load_dwordx4 s[16:19], s[4:7], 0x3c',
 '/*000000000208: c2010540         */ s_buffer_load_dword s2, s[4:7], 0x40',
 '/*000000000220: c2008545         */ s_buffer_load_dword s1, s[4:7], 0x45',
 '/*000000000224: d282080b 042c1109*/ v_mad_f32       v11, v9, s8, v11 clamp',
 '/*000000000240: 100c170b         */ v_mul_f32       v6, v11, v11',
 '/*000000000244: d2820807 241c150d*/ v_mad_f32       v7, -v13, s10, v7 clamp',
 '/*00000000024c: d2820801 04060105*/ v_mad_f32       v1, v5, v0, v1 clamp',
 '/*000000000258: 1006060d         */ v_mul_f32       v3, s13, v3',
 '/*000000000260: 10080f06         */ v_mul_f32       v4, v6, v7',
 '/*000000000264: 3e06180c         */ v_mac_f32       v3, s12, v12',
 '/*000000000270: 100a0810         */ v_mul_f32       v5, s16, v4',
 '/*000000000274: 100c0811         */ v_mul_f32       v6, s17, v4',
 '/*000000000278: 10080812         */ v_mul_f32       v4, s18, v4',
 '/*00000000027c: 3e06040e         */ v_mac_f32       v3, s14, v2',
 '/*000000000280: 10022301         */ v_mul_f32       v1, v1, v17',
 '/*000000000294: 100a0a02         */ v_mul_f32       v5, s2, v5',
 '/*000000000298: 100c0c02         */ v_mul_f32       v6, s2, v6',
 '/*00000000029c: 10080802         */ v_mul_f32       v4, s2, v4',
 '/*0000000002a0: 0606060f         */ v_add_f32       v3, s15, v3',
 '/*0000000002a4: 100a0b01         */ v_mul_f32       v5, v1, v5',
 '/*0000000002a8: 100c0d01         */ v_mul_f32       v6, v1, v6',
 '/*0000000002ac: 10020901         */ v_mul_f32       v1, v1, v4',
 '/*0000000002bc: 7c0c0680         */ v_cmp_ge_f32    vcc, 0, v3',
 '/*0000000002c0: d2000001 01a90101*/ v_cndmask_b32   v1, v1, 0, vcc',
 '/*0000000002c8: d2000003 01a90106*/ v_cndmask_b32   v3, v6, 0, vcc',
 '/*0000000002d0: d2000005 01a90105*/ v_cndmask_b32   v5, v5, 0, vcc',
 '/*00000000030c: 5e000705         */ v_cvt_pkrtz_f16_f32 v0, v5, v3',
 '/*000000000310: 5e020d01         */ v_cvt_pkrtz_f16_f32 v1, v1, v6',
 '/*000000000314: f8001c0f 00000100*/ exp             mrt0, v0, v0, v1, v1 done compr vm',
]

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def main():
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
 if len(mats)!=EXPECTED_MATERIALS:v.append(f'material count drift {len(mats)}')
 if any(int((m.get('materials') or {}).get(x,{}).get('ps_texture_count',-1))!=0 for x in mats):v.append('serialized PS texture binding unexpectedly present')

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
   '0000000001E0':(0,[32,33],[8,9]),'0000000001E4':(0,[56,57],[10,11]),
   '0000000001E8':(0,[72,73,74,75],[12,13,14,15]),
   '0000000001F4':(0,[60,61,62,63],[16,17,18,19]),
   '000000000208':(0,[64],[2]),'000000000220':(0,[69],[1]),
  }
  for addr,(api,dw,dst) in expected.items():
   q=by.get(addr)
   if not q or q.get('api_slot')!=api or q.get('dword_indices')!=dw or q.get('destination')!=dst:v.append(f'{addr}: cbuffer provenance drift {q}')

 tr=next((x for x in t.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if t.get('status')!='D1_GCN_TERMINAL_MRT0_DEPENDENCY_CENSUS_EXACT' or not tr:v.append('terminal MRT0 slice not exact/present')
 else:
  if tr.get('terminal_mrt0_export_address')!=EXPECTED_TERMINAL or not tr.get('terminal_mrt0_compressed'):v.append('terminal export identity drift')
  if tr.get('terminal_mrt0_operands')!=['v0','v0','v1','v1']:v.append('terminal operands drift')
  family={(0,x,'000000000048') for x in 'xyz'}|{(1,'x','000000000040'),(2,'y','0000000001D4')}
  for ch,colordw in [('R',60),('G',61),('B',62)]:
   q=tr['channels'][ch]['value_slice']
   tex={(int(x['texture_index']),x['channel'],x['sample_address']) for x in q.get('texture_sample_channels',[])}
   if tex!=family:v.append(f'{ch}: terminal texture leaf drift {sorted(tex)}')
   cb={str(k):set(z) for k,z in q.get('cbuffer_dwords',{}).items()}
   required={32,33,56,57,60,61,62,64,72,73,74,75,colordw}
   if not required.issubset(cb.get('0',set())):v.append(f'{ch}: gate/tail coefficient leaves missing {sorted(required-cb.get("0",set()))}')
   if 63 in cb.get('0',set()) or 69 in cb.get('0',set()):v.append(f'{ch}: MRT1-only coefficient leaked into MRT0 {cb}')
   ops={(x.get('address'),x.get('mnemonic')) for x in q.get('native_ops',[])}
   if ('0000000002BC','v_cmp_ge_f32') not in ops or not any(mn=='v_cndmask_b32' for _,mn in ops):v.append(f'{ch}: predicate ops missing from terminal provenance')
  aq=tr['channels']['A']['value_slice']
  if aq.get('literals')!=['0'] or aq.get('texture_sample_channels') or aq.get('cbuffer_dwords'):v.append(f'alpha is not zero-only {aq}')

 missing=[x for x in ANCHORS if x not in asm]
 if missing:v.append(f'missing native anchors {missing}')

 out={
  'schema':'d1_tower_light_80ca0451_gated_mrt0_factorization/v1',
  'status':'D1_TOWER_LIGHT_80CA0451_GATED_MRT0_FACTORIZATION_EXACT' if not v else 'D1_TOWER_LIGHT_80CA0451_GATED_MRT0_FACTORIZATION_PARTIAL',
  'shader':SHADER,'native_shader':NATIVE,'gcn_sha256':GCN_SHA,'instance_count':EXPECTED_INSTANCES,'unique_material_count':len(mats),
  'exact_tail_symbols':{
   'Q':'clamp(P*API0[32]+API0[33])','H':'clamp(-R*API0[56]+API0[57])','L':'clamp(A*B+C)',
   'G':'API0[73]*U0 + API0[72]*U1 + API0[74]*U2 + API0[75]',
   'C':'API0[60:63].rgb','S':'API0[64]','T':'t2.y',
  },
  'exact_terminal_equation':{
   'base_rgb':'API0[60:63].rgb * Q^2 * H * API0[64] * L * t2.y',
   'gate':'G > 0',
   'mrt0_rgb':'BASE.rgb if G > 0 else (0,0,0)',
   'mrt0_a':'0',
  },
  'predicate_proof':{
   'compare':'v_cmp_ge_f32 vcc, 0, G',
   'cndmask_effect':'when 0 >= G, RGB lanes select literal zero; otherwise they retain BASE',
  },
  'semantic_boundary':{
   'terminal_arithmetic_and_gate':'EXACT_NATIVE_GCN','serialized_ps_texture_bindings':'NONE_FOR_46_FAMILY_MATERIALS',
   'renderer_t0_t1_t2_human_semantics':'WITHHELD','gate_U0_U1_U2_human_semantics':'WITHHELD','portable_light_model_mapping':'WITHHELD',
  },
  'violations':v,
  'policy':'The conditional terminal equation is exact. The native gate variables and renderer resource meanings remain unnamed until primary evidence identifies them.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'equation':out['exact_terminal_equation'],'predicate':out['predicate_proof'],'violations':v},indent=2))
 return 0 if not v else 2
if __name__=='__main__':raise SystemExit(main())
