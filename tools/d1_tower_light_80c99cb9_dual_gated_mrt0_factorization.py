#!/usr/bin/env python3
"""Fail-closed dual-gated terminal MRT0 factorization for singleton Tower light PS 80C99CB9."""
from __future__ import annotations
import argparse,json
from pathlib import Path

SHADER='80C99CB9';NATIVE='80C99F16'
NATIVE_SHA='4f169f2f1f2c3fe2bea50886b0d608c208b6696a4d7fcd0ad7c252d643ee2e5a'
GCN_SHA='495d7b3485d9f212fcb05b0aee736debf8fd1034dd79f806617c72b17d413cb2'
GCN_BYTES=1128;EXPECTED_TERMINAL='00000000045C'
DEAD_API0=[47,51,55,79,95,101]

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def main():
 ap=argparse.ArgumentParser()
 for n in ('material-manifest','shader-report','image-usage','cbuffer-usage','terminal-mrt0','disasm','out'):ap.add_argument('--'+n,type=Path,required=True)
 a=ap.parse_args();v=[]
 m=json.loads(a.material_manifest.read_text());s=json.loads(a.shader_report.read_text());i=json.loads(a.image_usage.read_text());c=json.loads(a.cbuffer_usage.read_text());t=json.loads(a.terminal_mrt0.read_text());asm=a.disasm.read_text(errors='replace')
 if m.get('status')!='D1_WORLD_LIGHT_MATERIAL_MANIFEST_COMPLETE':v.append('material manifest not exact')
 mats=(m.get('pixel_shader_materials') or {}).get(SHADER,[])
 if int((m.get('pixel_shader_frequency') or {}).get(SHADER,-1))!=1 or len(mats)!=1:v.append('frequency/material count drift')
 if any(int((m.get('materials') or {}).get(x,{}).get('ps_texture_count',-1))!=0 for x in mats):v.append('serialized PS texture binding unexpectedly present')

 sr=next((x for x in s.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if s.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or not sr:v.append('shader report not exact/present')
 else:
  for k,z in {'native_shader':NATIVE,'native_sha256':NATIVE_SHA,'gcn_sha256':GCN_SHA,'gcn_bytes':GCN_BYTES}.items():
   if sr.get(k)!=z:v.append(f'{k} drift')

 ir=next((x for x in i.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 expimg=[('000000000040','image_load_mip',[1],'x'),('000000000048','image_sample',[0],'xyzw'),('000000000294','image_sample_lz',[2],'xy'),('0000000002A4','image_sample_lz',[3],'x')]
 got=[] if not ir else [(x['address'],x['opcode'],[q['texture_index'] for q in x.get('resources',[])],x['dmask_channels']) for x in ir.get('instructions',[])]
 if i.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT' or got!=expimg:v.append(f'image provenance drift {got}')

 cr=next((x for x in c.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 expected={'000000000200':(0,[40],[0]),'0000000002AC':(0,[76,77,78,79],[12,13,14,15]),'0000000002B0':(0,[56,57],[2,3]),'0000000002B4':(0,[104,105,106,107],[16,17,18,19]),'0000000002B8':(0,[108,109,110,111],[20,21,22,23]),'0000000002BC':(0,[88,89],[24,25]),'0000000002C0':(0,[52,53,54,55],[28,29,30,31]),'0000000002C8':(0,[92,93,94,95],[32,33,34,35]),'0000000002CC':(0,[48,49,50,51],[36,37,38,39]),'0000000002DC':(0,[96],[1]),'0000000002E0':(0,[101],[4])}
 if c.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or not cr:v.append('cbuffer usage not exact/present')
 else:
  by={x['address']:x for x in cr.get('loads',[])}
  for addr,(api,dw,dst) in expected.items():
   q=by.get(addr)
   if not q or q.get('api_slot')!=api or q.get('dword_indices')!=dw or q.get('destination')!=dst:v.append(f'{addr}: cbuffer drift {q}')

 tr=next((x for x in t.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if t.get('status')!='D1_GCN_TERMINAL_MRT0_DEPENDENCY_CENSUS_EXACT' or not tr:v.append('terminal slice not exact/present')
 else:
  if tr.get('terminal_mrt0_export_address')!=EXPECTED_TERMINAL or tr.get('terminal_mrt0_operands')!=['v1','v1','v0','v0'] or not tr.get('terminal_mrt0_compressed'):v.append('terminal export drift')
  fam={(0,x,'000000000048') for x in 'xyz'}|{(1,'x','000000000040'),(2,'y','000000000294')}
  expcb={'R':[12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,40,44,45,46,48,52,56,57,76,77,78,88,89,92,96,104,105,106,107],
         'G':[12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,40,44,45,46,49,53,56,57,76,77,78,88,89,93,96,104,105,106,107],
         'B':[12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,40,44,45,46,50,54,56,57,76,77,78,88,89,94,96,104,105,106,107]}
  for ch in 'RGB':
   q=tr['channels'][ch]['value_slice'];tex={(int(x['texture_index']),x['channel'],x['sample_address']) for x in q.get('texture_sample_channels',[])}
   if tex!=fam:v.append(f'{ch}: texture leaf drift {sorted(tex)}')
   if q.get('cbuffer_dwords')!={'0':expcb[ch]}:v.append(f'{ch}: cbuffer leaf drift {q.get("cbuffer_dwords")}')
   if q.get('unknown_registers')!=['v2','v3']:v.append(f'{ch}: native input frontier drift {q.get("unknown_registers")}')
  aq=tr['channels']['A']['value_slice']
  if aq.get('literals')!=['0'] or aq.get('texture_sample_channels') or aq.get('cbuffer_dwords') or aq.get('unknown_registers'):v.append('alpha drift')
  union=tr.get('mrt0_value_union') or {};api0=set((union.get('cbuffer_dwords') or {}).get('0',[]));alltex={(int(x['texture_index']),x['channel']) for x in union.get('texture_sample_channels',[])}
  if (0,'w') in alltex or (2,'x') in alltex or any(x[0]==3 for x in alltex):v.append('dead sampled channel reaches MRT0')
  for d in DEAD_API0:
   if d in api0:v.append(f'API0[{d}] reaches MRT0')
  if '12' in (union.get('cbuffer_dwords') or {}):v.append('API12 reaches MRT0')

 anchors=[
  '/*000000000328: d2820802 040a0f05*/ v_mad_f32       v2, v5, v7, v2 clamp',
  '/*000000000348: d282080b 042c0500*/ v_mad_f32       v11, v0, s2, v11 clamp',
  '/*000000000358: 10000b02         */ v_mul_f32       v0, v2, v5',
  '/*000000000360: 10042702         */ v_mul_f32       v2, v2, v19',
  '/*000000000370: d2820806 24183109*/ v_mad_f32       v6, -v9, s24, v6 clamp',
  '/*000000000378: d2060808 0001e108*/ v_add_f32       v8, v8, 0.5 clamp',
  '/*000000000388: 100e170b         */ v_mul_f32       v7, v11, v11',
  '/*000000000394: 10002500         */ v_mul_f32       v0, v0, v18',
  '/*000000000398: 3e080420         */ v_mac_f32       v4, s32, v2',
  '/*00000000039c: 3e0a0421         */ v_mac_f32       v5, s33, v2',
  '/*0000000003a0: 3e140422         */ v_mac_f32       v10, s34, v2',
  '/*0000000003a4: 10041108         */ v_mul_f32       v2, v8, v8',
  '/*0000000003b4: 100c0f06         */ v_mul_f32       v6, v6, v7',
  '/*0000000003b8: 060e1813         */ v_add_f32       v7, s19, v12',
  '/*0000000003bc: 06060617         */ v_add_f32       v3, s23, v3',
  '/*0000000003c0: 3e080424         */ v_mac_f32       v4, s36, v2',
  '/*0000000003c4: 3e0a0425         */ v_mac_f32       v5, s37, v2',
  '/*0000000003c8: 3e140426         */ v_mac_f32       v10, s38, v2',
  '/*0000000003d8: 10000c01         */ v_mul_f32       v0, s1, v6',
  '/*0000000003e0: d0060000 00010103*/ v_cmp_le_f32    s[0:1], v3, 0',
  '/*0000000003e8: 7c0c0e80         */ v_cmp_ge_f32    vcc, 0, v7',
  '/*000000000404: 88ea6a00         */ s_or_b64        vcc, s[0:1], vcc',
  '/*000000000408: d2000000 01a90100*/ v_cndmask_b32   v0, v0, 0, vcc',
  '/*000000000410: d2000002 01a90104*/ v_cndmask_b32   v2, v4, 0, vcc',
  '/*000000000418: d2000003 01a90103*/ v_cndmask_b32   v3, v3, 0, vcc',
  '/*00000000045c: f8001c0f 00000001*/ exp             mrt0, v1, v1, v0, v0 done compr vm',
 ]
 miss=[x for x in anchors if x not in asm]
 if miss:v.append(f'missing anchors {miss}')

 out={'schema':'d1_tower_light_80c99cb9_dual_gated_mrt0_factorization/v1',
      'status':'D1_TOWER_LIGHT_80C99CB9_DUAL_GATED_MRT0_FACTORIZATION_EXACT' if not v else 'D1_TOWER_LIGHT_80C99CB9_DUAL_GATED_MRT0_FACTORIZATION_PARTIAL',
      'shader':SHADER,'instance_count':1,'unique_material_count':len(mats),
      'exact_tail_symbols':{
       'Q':'clamp(q_in*API0[56]+API0[57])','R':'clamp(-r_in*API0[88]+API0[89])',
       'B':'exact native clamped branch squared at 0x3A4','P':'exact native clamped/reciprocal scalar before multiplication by t2.y','T':'t2.y',
       'G0':'API0[104]*g00 + API0[105]*g01 + API0[106]*g02 + API0[107]',
       'G1':'API0[108]*g10 + API0[109]*g11 + API0[110]*g12 + API0[111]',
      },
      'exact_terminal_equation':{
       'vector_pre_scale':'V.rgb = API0[52:54].rgb + API0[92:94].rgb*(P*t2.y) + API0[48:50].rgb*B',
       'scalar_scale':'K = API0[96] * Q^2 * R','gate':'G0 > 0 AND G1 > 0',
       'mrt0_rgb':'V.rgb*K iff both gates are positive, else (0,0,0)','mrt0_a':'0',
       'vector_form':'MRT0.rgb = [API0[52:54] + API0[92:94]*(P*t2.y) + API0[48:50]*B] * API0[96] * Q^2 * R iff G0 > 0 and G1 > 0, else 0',
      },
      'predicate_proof':{'first_compare':'G1 <= 0','second_compare':'G0 <= 0','combine':'OR','kept_when':'G0 > 0 AND G1 > 0'},
      'native_input_frontier':['v2','v3'],'renderer_texture_value_frontier':['t0.rgb','t1.x','t2.y'],
      'negative_proof':{'t0_alpha_reaches_mrt0':False,'t2_x_reaches_mrt0':False,'t3_reaches_mrt0':False,**{f'api0_dword{d}_reaches_mrt0':False for d in DEAD_API0},'api12_reaches_mrt0':False},
      'mrt1_boundary':'SHADER_WRITES_MRT1_BUT_THIS PROOF REDUCES MRT0 ONLY',
      'semantic_boundary':{'terminal_arithmetic_and_dual_gate':'EXACT_NATIVE_GCN','renderer_resource_human_semantics':'WITHHELD','gate_human_semantics':'WITHHELD','mrt1_semantics':'WITHHELD','portable_light_model_mapping':'WITHHELD'},
      'violations':v}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'equation':out['exact_terminal_equation'],'predicate':out['predicate_proof'],'violations':v},indent=2))
 return 0 if not v else 2

if __name__=='__main__':raise SystemExit(main())
