#!/usr/bin/env python3
"""Fail-closed terminal MRT0 factorization for Tower light PS 80AAE1BE.

Exact native arithmetic only:
    Q = clamp(q_in * API0[32] + API0[33])
    L = clamp(l_a*l_b + l_c)
    MRT0.rgb = API0[52:54] * Q^2 * API0[56] * L * t2.y
    MRT0.a = 0

The q/l inputs are native symbolic intermediates; renderer-resource semantics are withheld.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

SHADER='80AAE1BE';NATIVE='80AAE1BF'
NATIVE_SHA='964c7f9fc04bc9d9656bf5cb43e6f4daf0ca512a8a4a71ae05ea6c42dfee32ba'
GCN_SHA='a9ef5d7d65e3cb51c88594d328ad2b7718c59e55df0ae94ce85d61c04fa25218'
GCN_BYTES=688;EXPECTED_INSTANCES=37;EXPECTED_MATERIALS=14;EXPECTED_TERMINAL='0000000002A4'
ANCHORS=[
 '/*0000000001d4: f09c0300 00020c0c*/ image_sample_lz v[12:13], v[12:15], s[8:15], s[0:3] dmask:3',
 '/*0000000001dc: c2400520         */ s_buffer_load_dwordx2 s[0:1], s[4:7], 0x20',
 '/*0000000001e4: c2840534         */ s_buffer_load_dwordx4 s[8:11], s[4:7], 0x34',
 '/*0000000001f0: c2010538         */ s_buffer_load_dword s2, s[4:7], 0x38',
 '/*000000000200: c201853d         */ s_buffer_load_dword s3, s[4:7], 0x3d',
 '/*00000000021c: d2820804 04100109*/ v_mad_f32       v4, v9, s0, v4 clamp',
 '/*000000000224: d2820801 04060105*/ v_mad_f32       v1, v5, v0, v1 clamp',
 '/*000000000230: 10040904         */ v_mul_f32       v2, v4, v4',
 '/*000000000240: 10060408         */ v_mul_f32       v3, s8, v2',
 '/*000000000244: 10080409         */ v_mul_f32       v4, s9, v2',
 '/*000000000248: 1004040a         */ v_mul_f32       v2, s10, v2',
 '/*00000000024c: 10021b01         */ v_mul_f32       v1, v1, v13',
 '/*00000000025c: 10060602         */ v_mul_f32       v3, s2, v3',
 '/*000000000260: 10080802         */ v_mul_f32       v4, s2, v4',
 '/*000000000264: 10040402         */ v_mul_f32       v2, s2, v2',
 '/*000000000268: 10060701         */ v_mul_f32       v3, v1, v3',
 '/*00000000026c: 10080901         */ v_mul_f32       v4, v1, v4',
 '/*000000000270: 10020501         */ v_mul_f32       v1, v1, v2',
 '/*000000000280: 7e0c0280         */ v_mov_b32       v6, 0',
 '/*00000000029c: 5e000903         */ v_cvt_pkrtz_f16_f32 v0, v3, v4',
 '/*0000000002a0: 5e020d01         */ v_cvt_pkrtz_f16_f32 v1, v1, v6',
 '/*0000000002a4: f8001c0f 00000100*/ exp             mrt0, v0, v0, v1, v1 done compr vm',
]
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
  exp=[('000000000040','image_load_mip',[1],'x'),('000000000048','image_sample',[0],'xyzw'),('0000000001D4','image_sample_lz',[2],'xy')]
  if got!=exp:v.append(f'image instruction scope drift {got!r}')
 cr=next((x for x in c.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if c.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or not cr:v.append('cbuffer usage not exact/present')
 else:
  by={x.get('address'):x for x in cr.get('loads',[])}
  expected={'0000000001DC':(0,[32,33],[0,1]),'0000000001E4':(0,[52,53,54,55],[8,9,10,11]),'0000000001F0':(0,[56],[2]),'000000000200':(0,[61],[3])}
  for addr,(api,dw,dst) in expected.items():
   q=by.get(addr)
   if not q or q.get('api_slot')!=api or q.get('dword_indices')!=dw or q.get('destination')!=dst:v.append(f'{addr}: cbuffer provenance drift {q}')
 tr=next((x for x in t.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if t.get('status')!='D1_GCN_TERMINAL_MRT0_DEPENDENCY_CENSUS_EXACT' or not tr:v.append('terminal MRT0 slice not exact/present')
 else:
  if tr.get('terminal_mrt0_export_address')!=EXPECTED_TERMINAL or not tr.get('terminal_mrt0_compressed'):v.append('terminal export identity drift')
  if tr.get('terminal_mrt0_operands')!=['v0','v0','v1','v1']:v.append('terminal operands drift')
  family={(0,x,'000000000048') for x in 'xyz'}|{(1,'x','000000000040'),(2,'y','0000000001D4')}
  for ch,colordw in [('R',52),('G',53),('B',54)]:
   q=tr['channels'][ch]['value_slice'];tex={(int(x['texture_index']),x['channel'],x['sample_address']) for x in q.get('texture_sample_channels',[])}
   if tex!=family:v.append(f'{ch}: terminal texture leaf drift {sorted(tex)}')
   cb={str(k):set(z) for k,z in q.get('cbuffer_dwords',{}).items()}
   if set(cb)-{'0'}:v.append(f'{ch}: unexpected non-API0 MRT0 cbuffer leaves {cb}')
   required={32,33,colordw,56}
   if not required.issubset(cb.get('0',set())):v.append(f'{ch}: terminal coefficient leaves missing {sorted(required-cb.get("0",set()))}')
   if 55 in cb.get('0',set()) or 61 in cb.get('0',set()):v.append(f'{ch}: non-MRT0 coefficient leaked into MRT0 {cb}')
  aq=tr['channels']['A']['value_slice']
  if aq.get('literals')!=['0'] or aq.get('texture_sample_channels') or aq.get('cbuffer_dwords') or aq.get('unknown_registers'):v.append(f'alpha is not exact zero-only {aq}')
  union=tr.get('mrt0_value_union') or {};alltex={(int(x['texture_index']),x['channel']) for x in union.get('texture_sample_channels',[])}
  if (0,'w') in alltex or (2,'x') in alltex:v.append(f'dead sampled channel reached MRT0 unexpectedly {sorted(alltex)}')
  if '12' in (union.get('cbuffer_dwords') or {}):v.append('API12 unexpectedly reaches MRT0')
 missing=[x for x in ANCHORS if x not in asm]
 if missing:v.append(f'missing exact native anchors {missing}')
 out={'schema':'d1_tower_light_80aae1be_mrt0_factorization/v1','status':'D1_TOWER_LIGHT_80AAE1BE_MRT0_FACTORIZATION_EXACT' if not v else 'D1_TOWER_LIGHT_80AAE1BE_MRT0_FACTORIZATION_PARTIAL','shader':SHADER,'native_shader':NATIVE,'gcn_sha256':GCN_SHA,'instance_count':EXPECTED_INSTANCES,'unique_material_count':len(mats),
 'exact_tail_symbols':{'Q':'v4 after 0x21C = clamp(q_in*API0[32]+API0[33])','L':'v1 after 0x224 = clamp(l_a*l_b+l_c)','C':'API0[52:54].rgb','S':'API0[56]','T':'t2.y'},
 'exact_terminal_equation':{'mrt0_r':'API0[52] * Q^2 * API0[56] * L * t2.y','mrt0_g':'API0[53] * Q^2 * API0[56] * L * t2.y','mrt0_b':'API0[54] * Q^2 * API0[56] * L * t2.y','mrt0_a':'0','vector_form':'MRT0.rgb = API0[52:55].rgb * Q^2 * API0[56] * L * t2.y'},
 'negative_proof':{'t0_alpha_reaches_mrt0':False,'t2_x_reaches_mrt0':False,'api0_dword55_reaches_mrt0':False,'api0_dword61_reaches_mrt0':False,'api12_reaches_mrt0':False},
 'semantic_boundary':{'terminal_arithmetic':'EXACT_NATIVE_GCN','serialized_ps_texture_bindings':'NONE_FOR_14_FAMILY_MATERIALS','renderer_t0_t1_t2_human_semantics':'WITHHELD','symbols_Q_L_human_semantics':'WITHHELD','portable_light_model_mapping':'WITHHELD'},'violations':v,'policy':'Exact native GCN arithmetic only; renderer inputs and native symbolic intermediates remain semantically unnamed without primary evidence.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'equation':out['exact_terminal_equation'],'negative_proof':out['negative_proof'],'violations':v},indent=2));return 0 if not v else 2
if __name__=='__main__':raise SystemExit(main())
