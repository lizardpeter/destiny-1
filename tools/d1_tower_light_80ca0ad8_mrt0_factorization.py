#!/usr/bin/env python3
"""Fail-closed terminal MRT0 factorization for Tower light PS 80CA0AD8.

Exact native arithmetic only:
    Q = clamp(q_in * API0[44] + API0[45])
    L = clamp(l_a*l_b + l_c)
    V.rgb = API0[40:42] + API0[80:82] * (L * t2.y)
    MRT0.rgb = V.rgb * API0[84] * Q^2
    MRT0.a = 0

Native symbolic q/l inputs remain unnamed.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

SHADER='80CA0AD8';NATIVE='80CA0AD9'
NATIVE_SHA='9ad61190dfbb97cc693564ae7706a99f8c1c6648fe1f284eac0d73992164ff47'
GCN_SHA='773dae01691cbf8cc070c62645a4a614491aab777c2fbf9bcb85b44d4f189f5f'
GCN_BYTES=804;EXPECTED_INSTANCES=40;EXPECTED_MATERIALS=32;EXPECTED_TERMINAL='000000000318'

ANCHORS=[
 '/*000000000234: f09c0300 00020f0f*/ image_sample_lz v[15:16], v[15:18], s[8:15], s[0:3] dmask:3',
 '/*00000000023c: c240052c         */ s_buffer_load_dwordx2 s[0:1], s[4:7], 0x2c',
 '/*000000000244: c2840528         */ s_buffer_load_dwordx4 s[8:11], s[4:7], 0x28',
 '/*000000000248: c2860550         */ s_buffer_load_dwordx4 s[12:15], s[4:7], 0x50',
 '/*000000000254: c2010554         */ s_buffer_load_dword s2, s[4:7], 0x54',
 '/*000000000264: c2018559         */ s_buffer_load_dword s3, s[4:7], 0x59',
 '/*000000000280: d2820802 040a0305*/ v_mad_f32       v2, v5, v1, v2 clamp',
 '/*00000000028c: d2820804 04100100*/ v_mad_f32       v4, v0, s0, v4 clamp',
 '/*000000000298: 10020904         */ v_mul_f32       v1, v4, v4',
 '/*0000000002a0: 10042102         */ v_mul_f32       v2, v2, v16',
 '/*0000000002a8: 7e060208         */ v_mov_b32       v3, s8',
 '/*0000000002ac: 7e080209         */ v_mov_b32       v4, s9',
 '/*0000000002b0: 7e0a020a         */ v_mov_b32       v5, s10',
 '/*0000000002b4: 100c020c         */ v_mul_f32       v6, s12, v1',
 '/*0000000002b8: 100e020d         */ v_mul_f32       v7, s13, v1',
 '/*0000000002bc: 1010020e         */ v_mul_f32       v8, s14, v1',
 '/*0000000002c0: 3e06040c         */ v_mac_f32       v3, s12, v2',
 '/*0000000002c4: 3e08040d         */ v_mac_f32       v4, s13, v2',
 '/*0000000002c8: 3e0a040e         */ v_mac_f32       v5, s14, v2',
 '/*0000000002d8: 10020202         */ v_mul_f32       v1, s2, v1',
 '/*0000000002dc: 10060303         */ v_mul_f32       v3, v3, v1',
 '/*0000000002e0: 10080304         */ v_mul_f32       v4, v4, v1',
 '/*0000000002e4: 10020305         */ v_mul_f32       v1, v5, v1',
 '/*0000000002f4: 7e0c0280         */ v_mov_b32       v6, 0',
 '/*000000000310: 5e000903         */ v_cvt_pkrtz_f16_f32 v0, v3, v4',
 '/*000000000314: 5e020d01         */ v_cvt_pkrtz_f16_f32 v1, v1, v6',
 '/*000000000318: f8001c0f 00000100*/ exp             mrt0, v0, v0, v1, v1 done compr vm',
]

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def main()->int:
 ap=argparse.ArgumentParser()
 for n in ('material-manifest','shader-report','image-usage','cbuffer-usage','terminal-mrt0','disasm','out'):ap.add_argument('--'+n,type=Path,required=True)
 a=ap.parse_args();v=[]
 m=json.loads(a.material_manifest.read_text());s=json.loads(a.shader_report.read_text());i=json.loads(a.image_usage.read_text())
 c=json.loads(a.cbuffer_usage.read_text());t=json.loads(a.terminal_mrt0.read_text());asm=a.disasm.read_text(errors='replace')
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
   '00000000023C':(0,[44,45],[0,1]),'000000000244':(0,[40,41,42,43],[8,9,10,11]),
   '000000000248':(0,[80,81,82,83],[12,13,14,15]),'000000000254':(0,[84],[2]),
   '000000000264':(0,[89],[3]),
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
  for ch,base,mod in [('R',40,80),('G',41,81),('B',42,82)]:
   q=tr['channels'][ch]['value_slice'];tex={(int(x['texture_index']),x['channel'],x['sample_address']) for x in q.get('texture_sample_channels',[])}
   if tex!=family:v.append(f'{ch}: terminal texture leaf drift {sorted(tex)}')
   cb={str(k):set(z) for k,z in q.get('cbuffer_dwords',{}).items()}
   if set(cb)-{'0'}:v.append(f'{ch}: unexpected non-API0 MRT0 cbuffer leaves {cb}')
   required={base,mod,44,45,84}
   if not required.issubset(cb.get('0',set())):v.append(f'{ch}: terminal coefficient leaves missing {sorted(required-cb.get("0",set()))}')
   if 43 in cb.get('0',set()) or 83 in cb.get('0',set()) or 89 in cb.get('0',set()):v.append(f'{ch}: non-MRT0 coefficient leaked into MRT0 {cb}')
  aq=tr['channels']['A']['value_slice']
  if aq.get('literals')!=['0'] or aq.get('texture_sample_channels') or aq.get('cbuffer_dwords') or aq.get('unknown_registers'):v.append(f'alpha is not exact zero-only {aq}')
  union=tr.get('mrt0_value_union') or {};alltex={(int(x['texture_index']),x['channel']) for x in union.get('texture_sample_channels',[])}
  if (0,'w') in alltex or (2,'x') in alltex:v.append(f'dead sampled channel reached MRT0 unexpectedly {sorted(alltex)}')
  if '12' in (union.get('cbuffer_dwords') or {}):v.append('API12 unexpectedly reaches MRT0')
 missing=[x for x in ANCHORS if x not in asm]
 if missing:v.append(f'missing exact native anchors {missing}')
 out={
  'schema':'d1_tower_light_80ca0ad8_mrt0_factorization/v1','status':'D1_TOWER_LIGHT_80CA0AD8_MRT0_FACTORIZATION_EXACT' if not v else 'D1_TOWER_LIGHT_80CA0AD8_MRT0_FACTORIZATION_PARTIAL',
  'shader':SHADER,'native_shader':NATIVE,'gcn_sha256':GCN_SHA,'instance_count':EXPECTED_INSTANCES,'unique_material_count':len(mats),
  'exact_tail_symbols':{'Q':'v4 after 0x28C = clamp(q_in*API0[44]+API0[45])','L':'v2 after 0x280 = clamp(l_a*l_b+l_c)','B':'API0[40:42].rgb','M':'API0[80:82].rgb','S':'API0[84]','T':'t2.y'},
  'exact_terminal_equation':{
   'vector_pre_scale':'V.rgb = API0[40:42].rgb + API0[80:82].rgb*(L*t2.y)',
   'scalar_scale':'K = API0[84] * Q^2','mrt0_rgb':'MRT0.rgb = V.rgb * K','mrt0_a':'0',
   'vector_form':'MRT0.rgb = (API0[40:42].rgb + API0[80:82].rgb*(L*t2.y)) * API0[84] * Q^2',
  },
  'negative_proof':{'t0_alpha_reaches_mrt0':False,'t2_x_reaches_mrt0':False,'api0_dword43_reaches_mrt0':False,'api0_dword83_reaches_mrt0':False,'api0_dword89_reaches_mrt0':False,'api12_reaches_mrt0':False},
  'semantic_boundary':{'terminal_arithmetic':'EXACT_NATIVE_GCN','serialized_ps_texture_bindings':'NONE_FOR_32_FAMILY_MATERIALS','renderer_t0_t1_t2_human_semantics':'WITHHELD','symbols_Q_L_human_semantics':'WITHHELD','portable_light_model_mapping':'WITHHELD'},
  'violations':v,'policy':'Exact native GCN arithmetic only; renderer inputs and native symbolic intermediates remain semantically unnamed without primary evidence.'
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'equation':out['exact_terminal_equation'],'negative_proof':out['negative_proof'],'violations':v},indent=2));return 0 if not v else 2
if __name__=='__main__':raise SystemExit(main())
