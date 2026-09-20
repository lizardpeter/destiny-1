#!/usr/bin/env python3
"""Fail-closed gated terminal MRT0 factorization for Tower light PS 80C998E6.

Exact native arithmetic only:
    Q = clamp(q_in * API0[40] + API0[41])
    H = clamp(-h_in * API0[72] + API0[73])
    L = clamp(l_a*l_b + l_c)
    BASE.rgb = API0[76:78] * Q^2 * H * API0[80] * L * t2.y
    G = API0[88]*g0 + API0[89]*g1 + API0[90]*g2 + API0[91]
    MRT0.rgb = BASE.rgb if G > 0 else 0
    MRT0.a = 0

The q/h/l/g inputs remain exact native symbolic intermediates.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

SHADER='80C998E6';NATIVE='80C99911'
NATIVE_SHA='9823b1eb0a0d7c47a3a378aa1039c95bfddeeac4576387da00e50cde9af24bf6'
GCN_SHA='f31e2ba8683e1e823cc7185c2e4ea3d4dfedaa7ed42dab444a5d4ab3ae87b6a5'
GCN_BYTES=896;EXPECTED_INSTANCES=37;EXPECTED_MATERIALS=37;EXPECTED_TERMINAL='000000000374'
ANCHORS=[
 '/*000000000234: f09c0300 00021010*/ image_sample_lz v[16:17], v[16:19], s[8:15], s[0:3] dmask:3',
 '/*00000000023c: c280053c         */ s_buffer_load_dwordx4 s[0:3], s[4:7], 0x3c',
 '/*000000000240: c2440528         */ s_buffer_load_dwordx2 s[8:9], s[4:7], 0x28',
 '/*000000000244: c2450548         */ s_buffer_load_dwordx2 s[10:11], s[4:7], 0x48',
 '/*000000000248: c2860558         */ s_buffer_load_dwordx4 s[12:15], s[4:7], 0x58',
 '/*000000000254: c288054c         */ s_buffer_load_dwordx4 s[16:19], s[4:7], 0x4c',
 '/*000000000268: c2010550         */ s_buffer_load_dword s2, s[4:7], 0x50',
 '/*000000000280: c2008555         */ s_buffer_load_dword s1, s[4:7], 0x55',
 '/*000000000298: d2820801 04041100*/ v_mad_f32       v1, v0, s8, v1 clamp',
 '/*0000000002a0: d2820802 040a0f05*/ v_mad_f32       v2, v5, v7, v2 clamp',
 '/*0000000002ac: d2820808 2420150b*/ v_mad_f32       v8, -v11, s10, v8 clamp',
 '/*0000000002b4: 10020301         */ v_mul_f32       v1, v1, v1',
 '/*0000000002c0: 10020308         */ v_mul_f32       v1, v8, v1',
 '/*0000000002d0: 10080210         */ v_mul_f32       v4, s16, v1',
 '/*0000000002d4: 100a0211         */ v_mul_f32       v5, s17, v1',
 '/*0000000002d8: 10020212         */ v_mul_f32       v1, s18, v1',
 '/*0000000002e0: 10042302         */ v_mul_f32       v2, v2, v17',
 '/*0000000002f4: 10080802         */ v_mul_f32       v4, s2, v4',
 '/*0000000002f8: 100a0a02         */ v_mul_f32       v5, s2, v5',
 '/*0000000002fc: 10020202         */ v_mul_f32       v1, s2, v1',
 '/*000000000300: 0606060f         */ v_add_f32       v3, s15, v3',
 '/*000000000304: 10080902         */ v_mul_f32       v4, v2, v4',
 '/*000000000308: 100a0b02         */ v_mul_f32       v5, v2, v5',
 '/*00000000030c: 10020302         */ v_mul_f32       v1, v2, v1',
 '/*00000000031c: 7c0c0680         */ v_cmp_ge_f32    vcc, 0, v3',
 '/*000000000320: d2000001 01a90101*/ v_cndmask_b32   v1, v1, 0, vcc',
 '/*000000000328: d2000003 01a90105*/ v_cndmask_b32   v3, v5, 0, vcc',
 '/*000000000330: d2000004 01a90104*/ v_cndmask_b32   v4, v4, 0, vcc',
 '/*000000000350: 7e0c0280         */ v_mov_b32       v6, 0',
 '/*00000000036c: 5e000704         */ v_cvt_pkrtz_f16_f32 v0, v4, v3',
 '/*000000000370: 5e020d01         */ v_cvt_pkrtz_f16_f32 v1, v1, v6',
 '/*000000000374: f8001c0f 00000100*/ exp             mrt0, v0, v0, v1, v1 done compr vm',
]
EXPECTED_CB={
 'R':[12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,40,41,60,61,62,72,73,76,80,88,89,90,91],
 'G':[12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,40,41,60,61,62,72,73,77,80,88,89,90,91],
 'B':[12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,40,41,60,61,62,72,73,78,80,88,89,90,91],
}
def norm(x):return str(x).upper().removeprefix('0X').zfill(8)
def main()->int:
 ap=argparse.ArgumentParser()
 for n in ('material-manifest','shader-report','image-usage','cbuffer-usage','terminal-mrt0','disasm','out'):ap.add_argument('--'+n,type=Path,required=True)
 a=ap.parse_args();v=[];m=json.loads(a.material_manifest.read_text());s=json.loads(a.shader_report.read_text());i=json.loads(a.image_usage.read_text());c=json.loads(a.cbuffer_usage.read_text());t=json.loads(a.terminal_mrt0.read_text());asm=a.disasm.read_text(errors='replace')
 if m.get('status')!='D1_WORLD_LIGHT_MATERIAL_MANIFEST_COMPLETE':v.append('material manifest not exact')
 if int((m.get('pixel_shader_frequency') or {}).get(SHADER,-1))!=EXPECTED_INSTANCES:v.append('instance count drift')
 mats=(m.get('pixel_shader_materials') or {}).get(SHADER,[])
 if len(mats)!=EXPECTED_MATERIALS:v.append(f'unique material count drift {len(mats)} != {EXPECTED_MATERIALS}')
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
  exp=[('000000000040','image_load_mip',[1],'x'),('000000000048','image_sample',[0],'xyzw'),('000000000234','image_sample_lz',[2],'xy')]
  if got!=exp:v.append(f'image instruction scope drift {got!r}')
 cr=next((x for x in c.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if c.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or not cr:v.append('cbuffer usage not exact/present')
 else:
  by={x.get('address'):x for x in cr.get('loads',[])}
  expected={
   '00000000023C':(0,[60,61,62,63],[0,1,2,3]),'000000000240':(0,[40,41],[8,9]),
   '000000000244':(0,[72,73],[10,11]),'000000000248':(0,[88,89,90,91],[12,13,14,15]),
   '000000000254':(0,[76,77,78,79],[16,17,18,19]),'000000000268':(0,[80],[2]),
   '000000000280':(0,[85],[1]),
  }
  for addr,(api,dw,dst) in expected.items():
   q=by.get(addr)
   if not q or q.get('api_slot')!=api or q.get('dword_indices')!=dw or q.get('destination')!=dst:v.append(f'{addr}: cbuffer provenance drift {q}')
 tr=next((x for x in t.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if t.get('status')!='D1_GCN_TERMINAL_MRT0_DEPENDENCY_CENSUS_EXACT' or not tr:v.append('terminal MRT0 slice not exact/present')
 else:
  if tr.get('terminal_mrt0_export_address')!=EXPECTED_TERMINAL or not tr.get('terminal_mrt0_compressed'):v.append('terminal export identity drift')
  if tr.get('terminal_mrt0_operands')!=['v0','v0','v1','v1']:v.append('terminal operands drift')
  family={(0,x,'000000000048') for x in 'xyz'}|{(1,'x','000000000040'),(2,'y','000000000234')}
  for ch in 'RGB':
   q=tr['channels'][ch]['value_slice'];tex={(int(x['texture_index']),x['channel'],x['sample_address']) for x in q.get('texture_sample_channels',[])}
   if tex!=family:v.append(f'{ch}: terminal texture leaf drift {sorted(tex)}')
   cb=q.get('cbuffer_dwords') or {}
   if cb!={'0':EXPECTED_CB[ch]}:v.append(f'{ch}: exact cbuffer leaf set drift {cb!r}')
  aq=tr['channels']['A']['value_slice']
  if aq.get('literals')!=['0'] or aq.get('texture_sample_channels') or aq.get('cbuffer_dwords') or aq.get('unknown_registers'):v.append(f'alpha is not exact zero-only {aq}')
  union=tr.get('mrt0_value_union') or {};alltex={(int(x['texture_index']),x['channel']) for x in union.get('texture_sample_channels',[])}
  if (0,'w') in alltex or (2,'x') in alltex:v.append(f'dead sampled channel reached MRT0 unexpectedly {sorted(alltex)}')
  if '12' in (union.get('cbuffer_dwords') or {}):v.append('API12 unexpectedly reaches MRT0')
  api0=set((union.get('cbuffer_dwords') or {}).get('0',[]))
  if 79 in api0 or 85 in api0:v.append(f'MRT1-only coefficient reached MRT0 {sorted(api0)}')
 missing=[x for x in ANCHORS if x not in asm]
 if missing:v.append(f'missing exact native anchors {missing}')
 out={'schema':'d1_tower_light_80c998e6_gated_mrt0_factorization/v1','status':'D1_TOWER_LIGHT_80C998E6_GATED_MRT0_FACTORIZATION_EXACT' if not v else 'D1_TOWER_LIGHT_80C998E6_GATED_MRT0_FACTORIZATION_PARTIAL','shader':SHADER,'native_shader':NATIVE,'gcn_sha256':GCN_SHA,'instance_count':EXPECTED_INSTANCES,'unique_material_count':len(mats),
 'exact_tail_symbols':{'Q':'v1 after 0x298 = clamp(q_in*API0[40]+API0[41])','L':'v2 after 0x2A0 = clamp(l_a*l_b+l_c)','H':'v8 after 0x2AC = clamp(-h_in*API0[72]+API0[73])','C':'API0[76:78].rgb','S':'API0[80]','T':'t2.y','G':'API0[88]*g0 + API0[89]*g1 + API0[90]*g2 + API0[91]'},
 'exact_terminal_equation':{'base_rgb':'API0[76:79].rgb * Q^2 * H * API0[80] * L * t2.y','gate':'G > 0','mrt0_rgb':'BASE.rgb if G > 0 else (0,0,0)','mrt0_a':'0'},
 'predicate_proof':{'compare':'v_cmp_ge_f32 vcc, 0, G','false_when':'G <= 0','kept_when':'G > 0'},
 'negative_proof':{'t0_alpha_reaches_mrt0':False,'t2_x_reaches_mrt0':False,'api0_dword79_reaches_mrt0':False,'api0_dword85_reaches_mrt0':False,'api12_reaches_mrt0':False},
 'semantic_boundary':{'terminal_arithmetic':'EXACT_NATIVE_GCN','serialized_ps_texture_bindings':'NONE_FOR_37_FAMILY_MATERIALS','renderer_t0_t1_t2_human_semantics':'WITHHELD','symbols_Q_H_L_G_human_semantics':'WITHHELD','portable_light_model_mapping':'WITHHELD'},'violations':v,'policy':'Exact native GCN arithmetic and gate predicate only; renderer inputs and native symbolic intermediates remain semantically unnamed without primary evidence.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'equation':out['exact_terminal_equation'],'negative_proof':out['negative_proof'],'violations':v},indent=2));return 0 if not v else 2
if __name__=='__main__':raise SystemExit(main())
