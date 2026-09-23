#!/usr/bin/env python3
"""Fail-closed gated terminal MRT0 factorization for Tower light PS 80C99CBE."""
from __future__ import annotations
import argparse,json
from pathlib import Path
SHADER='80C99CBE';NATIVE='80C99F1B'
NATIVE_SHA='7cf07cc5801930757f394d7198718f2511bb293b65b278eebc53d3418345b7e1'
GCN_SHA='09a2d0a43f620cffb62517417b7a0d7ab051e66e16de917bcb5698a404ce5973'
GCN_BYTES=916;EXPECTED_INSTANCES=2;EXPECTED_MATERIALS=2;EXPECTED_TERMINAL='000000000388'
ANCHORS=[
 '/*000000000234: f09c0300 00021010*/ image_sample_lz v[16:17], v[16:19], s[8:15], s[0:3] dmask:3',
 '/*00000000023c: c2800540         */ s_buffer_load_dwordx4 s[0:3], s[4:7], 0x40',
 '/*000000000240: c244052c         */ s_buffer_load_dwordx2 s[8:9], s[4:7], 0x2c',
 '/*000000000244: c245054c         */ s_buffer_load_dwordx2 s[10:11], s[4:7], 0x4c',
 '/*000000000248: c286055c         */ s_buffer_load_dwordx4 s[12:15], s[4:7], 0x5c',
 '/*000000000254: c2880528         */ s_buffer_load_dwordx4 s[16:19], s[4:7], 0x28',
 '/*000000000258: c28a0550         */ s_buffer_load_dwordx4 s[20:23], s[4:7], 0x50',
 '/*00000000026c: c2010554         */ s_buffer_load_dword s2, s[4:7], 0x54',
 '/*000000000284: c2008559         */ s_buffer_load_dword s1, s[4:7], 0x59',
 '/*00000000029c: d2820801 04041100*/ v_mad_f32       v1, v0, s8, v1 clamp',
 '/*0000000002a4: d2820802 040a0f05*/ v_mad_f32       v2, v5, v7, v2 clamp',
 '/*0000000002b0: d2820808 2420150b*/ v_mad_f32       v8, -v11, s10, v8 clamp',
 '/*0000000002b8: 10020301         */ v_mul_f32       v1, v1, v1',
 '/*0000000002c4: 10020308         */ v_mul_f32       v1, v8, v1',
 '/*0000000002d0: 10042302         */ v_mul_f32       v2, v2, v17',
 '/*0000000002d8: 7e080210         */ v_mov_b32       v4, s16',
 '/*0000000002dc: 7e0a0211         */ v_mov_b32       v5, s17',
 '/*0000000002e0: 7e0c0212         */ v_mov_b32       v6, s18',
 '/*0000000002e4: 100e0214         */ v_mul_f32       v7, s20, v1',
 '/*0000000002e8: 10100215         */ v_mul_f32       v8, s21, v1',
 '/*0000000002ec: 10120216         */ v_mul_f32       v9, s22, v1',
 '/*0000000002f4: 3e080414         */ v_mac_f32       v4, s20, v2',
 '/*0000000002f8: 3e0a0415         */ v_mac_f32       v5, s21, v2',
 '/*0000000002fc: 3e0c0416         */ v_mac_f32       v6, s22, v2',
 '/*000000000310: 10020202         */ v_mul_f32       v1, s2, v1',
 '/*000000000314: 0606060f         */ v_add_f32       v3, s15, v3',
 '/*000000000318: 10080304         */ v_mul_f32       v4, v4, v1',
 '/*00000000031c: 100a0305         */ v_mul_f32       v5, v5, v1',
 '/*000000000320: 10020306         */ v_mul_f32       v1, v6, v1',
 '/*000000000330: 7c0c0680         */ v_cmp_ge_f32    vcc, 0, v3',
 '/*000000000334: d2000001 01a90101*/ v_cndmask_b32   v1, v1, 0, vcc',
 '/*00000000033c: d2000003 01a90105*/ v_cndmask_b32   v3, v5, 0, vcc',
 '/*000000000344: d2000004 01a90104*/ v_cndmask_b32   v4, v4, 0, vcc',
 '/*000000000380: 5e000704         */ v_cvt_pkrtz_f16_f32 v0, v4, v3',
 '/*000000000384: 5e020d01         */ v_cvt_pkrtz_f16_f32 v1, v1, v6',
 '/*000000000388: f8001c0f 00000100*/ exp             mrt0, v0, v0, v1, v1 done compr vm',
]
def norm(x):return str(x).upper().removeprefix('0X').zfill(8)
def main()->int:
 ap=argparse.ArgumentParser()
 for n in ('material-manifest','shader-report','image-usage','cbuffer-usage','terminal-mrt0','disasm','out'):ap.add_argument('--'+n,type=Path,required=True)
 a=ap.parse_args();v=[];m=json.loads(a.material_manifest.read_text());s=json.loads(a.shader_report.read_text());i=json.loads(a.image_usage.read_text());c=json.loads(a.cbuffer_usage.read_text());t=json.loads(a.terminal_mrt0.read_text());asm=a.disasm.read_text(errors='replace')
 if m.get('status')!='D1_WORLD_LIGHT_MATERIAL_MANIFEST_COMPLETE':v.append('material manifest not exact')
 if int((m.get('pixel_shader_frequency') or {}).get(SHADER,-1))!=EXPECTED_INSTANCES:v.append('instance count drift')
 mats=(m.get('pixel_shader_materials') or {}).get(SHADER,[])
 if len(mats)!=EXPECTED_MATERIALS:v.append('material count drift')
 if any(int((m.get('materials') or {}).get(x,{}).get('ps_texture_count',-1))!=0 for x in mats):v.append('serialized PS texture binding unexpectedly present')
 sr=next((x for x in s.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if s.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or not sr:v.append('shader report not exact/present')
 else:
  for k,z in {'native_shader':NATIVE,'native_sha256':NATIVE_SHA,'gcn_sha256':GCN_SHA,'gcn_bytes':GCN_BYTES}.items():
   if sr.get(k)!=z:v.append(f'{k} drift')
 ir=next((x for x in i.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if i.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT' or not ir:v.append('image usage not exact/present')
 else:
  got=[(x['address'],x['opcode'],[q['texture_index'] for q in x.get('resources',[])],x['dmask_channels']) for x in ir.get('instructions',[])]
  exp=[('000000000040','image_load_mip',[1],'x'),('000000000048','image_sample',[0],'xyzw'),('000000000234','image_sample_lz',[2],'xy')]
  if got!=exp:v.append(f'image scope drift {got!r}')
 cr=next((x for x in c.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if c.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or not cr:v.append('cbuffer usage not exact/present')
 else:
  by={x.get('address'):x for x in cr.get('loads',[])}
  expected={'00000000023C':(0,[64,65,66,67],[0,1,2,3]),'000000000240':(0,[44,45],[8,9]),'000000000244':(0,[76,77],[10,11]),'000000000248':(0,[92,93,94,95],[12,13,14,15]),'000000000254':(0,[40,41,42,43],[16,17,18,19]),'000000000258':(0,[80,81,82,83],[20,21,22,23]),'00000000026C':(0,[84],[2]),'000000000284':(0,[89],[1])}
  for addr,(api,dw,dst) in expected.items():
   q=by.get(addr)
   if not q or q.get('api_slot')!=api or q.get('dword_indices')!=dw or q.get('destination')!=dst:v.append(f'{addr}: cbuffer drift {q}')
 tr=next((x for x in t.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if t.get('status')!='D1_GCN_TERMINAL_MRT0_DEPENDENCY_CENSUS_EXACT' or not tr:v.append('terminal MRT0 slice not exact/present')
 else:
  if tr.get('terminal_mrt0_export_address')!=EXPECTED_TERMINAL or tr.get('terminal_mrt0_operands')!=['v0','v0','v1','v1']:v.append('terminal export drift')
  texreq={(0,x,'000000000048') for x in 'xyz'}|{(1,'x','000000000040'),(2,'y','000000000234')}
  for ch,base,mod in [('R',40,80),('G',41,81),('B',42,82)]:
   q=tr['channels'][ch]['value_slice'];tex={(int(x['texture_index']),x['channel'],x['sample_address']) for x in q.get('texture_sample_channels',[])}
   if tex!=texreq:v.append(f'{ch}: texture leaf drift {sorted(tex)}')
   cbq={str(k):set(z) for k,z in (q.get('cbuffer_dwords') or {}).items()};req={base,mod,44,45,76,77,84,92,93,94,95}
   if set(cbq)-{'0'} or not req.issubset(cbq.get('0',set())):v.append(f'{ch}: cbuffer leaf drift {cbq}')
  aq=tr['channels']['A']['value_slice']
  if aq.get('literals')!=['0'] or aq.get('texture_sample_channels') or aq.get('cbuffer_dwords') or aq.get('unknown_registers'):v.append('alpha drift')
  union=tr.get('mrt0_value_union') or {};alltex={(int(x['texture_index']),x['channel']) for x in union.get('texture_sample_channels',[])}
  if (0,'w') in alltex or (2,'x') in alltex:v.append('dead sampled channel reaches MRT0')
  api0=set((union.get('cbuffer_dwords') or {}).get('0',[]))
  for dead in (43,83,89):
   if dead in api0:v.append(f'API0[{dead}] reaches MRT0')
  if '12' in (union.get('cbuffer_dwords') or {}):v.append('API12 reaches MRT0')
 missing=[x for x in ANCHORS if x not in asm]
 if missing:v.append(f'missing native anchors {missing}')
 out={'schema':'d1_tower_light_80c99cbe_gated_mrt0_factorization/v1','status':'D1_TOWER_LIGHT_80C99CBE_GATED_MRT0_FACTORIZATION_EXACT' if not v else 'D1_TOWER_LIGHT_80C99CBE_GATED_MRT0_FACTORIZATION_PARTIAL','shader':SHADER,'native_shader':NATIVE,'gcn_sha256':GCN_SHA,'instance_count':EXPECTED_INSTANCES,'unique_material_count':len(mats),
 'exact_tail_symbols':{'Q':'clamp(q_in*API0[44]+API0[45])','H':'clamp(-h_in*API0[76]+API0[77])','L':'exact native clamped scalar','B':'API0[40:42].rgb','M':'API0[80:82].rgb','S':'API0[84]','T':'t2.y','G':'API0[92]*g0+API0[93]*g1+API0[94]*g2+API0[95]'},
 'exact_terminal_equation':{'vector_pre_scale':'V.rgb = API0[40:42].rgb + API0[80:82].rgb*(L*t2.y)','scalar_scale':'K = API0[84] * Q^2 * H','gate':'G > 0','mrt0_rgb':'V.rgb * K if G > 0 else (0,0,0)','mrt0_a':'0','vector_form':'MRT0.rgb = (API0[40:42].rgb + API0[80:82].rgb*(L*t2.y)) * API0[84] * Q^2 * H when G > 0, else 0'},
 'predicate_proof':{'compare':'v_cmp_ge_f32 vcc, 0, G','false_when':'G <= 0','kept_when':'G > 0'},
 'negative_proof':{'t0_alpha_reaches_mrt0':False,'t2_x_reaches_mrt0':False,'api0_dword43_reaches_mrt0':False,'api0_dword83_reaches_mrt0':False,'api0_dword89_reaches_mrt0':False,'api12_reaches_mrt0':False},
 'semantic_boundary':{'terminal_arithmetic':'EXACT_NATIVE_GCN','gate_predicate':'EXACT_NATIVE_GCN','serialized_ps_texture_bindings':'NONE_FOR_2_FAMILY_MATERIALS','renderer_resource_human_semantics':'WITHHELD'},'violations':v}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'equation':out['exact_terminal_equation'],'violations':v},indent=2));return 0 if not v else 2
if __name__=='__main__':raise SystemExit(main())
