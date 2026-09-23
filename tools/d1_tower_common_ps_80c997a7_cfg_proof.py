#!/usr/bin/env python3
"""Exact CFG-aware MRT0 proof for Tower common shader 80C997A7.

The shader has a large MRT1 path, but its terminal MRT0 can be isolated exactly.
Three serialized scalar samples are multiplied into one positive-test control:
  S = t1.y * t2.x
For S>0, t0.x contributes to a grayscale RGB output and alpha becomes clamp(1-S).
For the complementary lanes, RGB is zero and alpha is one. API0[25] supplies the
final exact scalar multiplier. MRT1 arithmetic is explicitly outside this proof.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

SH='80C997A7';MAT='80C9964B';TEX='80CA0AD6'
NATIVE='80C997AA'
NSHA='78272e25440963d76c46479f5c4d3fdd3554801aa150fc962dcde7757c010b20'
GSHA='33fd4ec94f2585635391402ba126c1c6302dbd32f3052995a6be6e6e6b08548b'
GBYTES=484;TERMINAL='0000000001D8'
API0=[0,1,2,3,4,5,6,7,8,9,10,11,16,25]
ANCHORS=[
 'image_sample    v4, v[4:7], s[4:11], s[12:15]',
 'image_sample    v5, v[5:8], s[28:35], s[36:39] dmask:2',
 'image_sample    v2, v[6:9], s[40:47], s[0:3]',
 'v_mul_f32       v3, v5, v2',
 'v_cmp_lt_f32    vcc, 0, v3',
 's_and_saveexec_b64 s[0:1], vcc',
 'v_mad_f32       v2, -v5, v2, 1.0 clamp',
 's_buffer_load_dword s2, s[16:19], 0x10',
 'v_mul_f32       v5, v4, v3',
 'v_sub_f32       v3, 1.0, v2',
 's_andn2_b64     exec, s[0:1], exec',
 'v_mov_b32       v2, 1.0',
 'v_mov_b32       v3, 0',
 'v_mov_b32       v5, 0',
 's_mov_b64       exec, s[0:1]',
 's_buffer_load_dword s0, s[16:19], 0x19',
 'v_max_f32       v7, s0, s0 clamp',
 'v_mul_f32       v5, v5, v7',
 'v_cvt_pkrtz_f16_f32 v0, v5, v5',
 'v_cvt_pkrtz_f16_f32 v1, v5, v2',
 'exp             mrt0, v0, v0, v1, v1 done compr vm',
]

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def main():
 ap=argparse.ArgumentParser()
 for n in ('manifest','shader-report','image-usage','cbuffer-usage','disasm','out'):
  ap.add_argument('--'+n,type=Path,required=True)
 a=ap.parse_args()
 m=json.loads(a.manifest.read_text());sr=json.loads(a.shader_report.read_text())
 iu=json.loads(a.image_usage.read_text());cb=json.loads(a.cbuffer_usage.read_text())
 v=[]
 if m.get('status')!='D1_WORLD_VISIBLE_MATERIAL_TEXTURE_EXPORT' or m.get('material_decode_errors') or m.get('texture_errors'):v.append('manifest not exact')
 if sr.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or sr.get('error_count'):v.append('shader report not exact')
 if iu.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':v.append('image usage not exact')
 if cb.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or cb.get('missing_usage'):v.append('cbuffer usage not exact')
 s=next((x for x in sr.get('shaders',[]) if norm(x.get('shader'))==SH),None)
 i=next((x for x in iu.get('shaders',[]) if norm(x.get('shader'))==SH),None)
 c=next((x for x in cb.get('shaders',[]) if norm(x.get('shader'))==SH),None)
 freq={norm(k):int(x) for k,x in (m.get('pixel_shader_frequency') or {}).items()}
 if freq.get(SH)!=1:v.append(f'frequency {freq.get(SH)} != 1')
 mm=[(norm(k),x) for k,x in (m.get('materials') or {}).items() if norm(x.get('pixel_shader'))==SH]
 if len(mm)!=1:v.append(f'material count {len(mm)} != 1')
 else:
  mh,mr=mm[0]
  if mh!=MAT:v.append(f'material {mh} != {MAT}')
  binds=[(int(x['texture_index']),norm(x['texture'])) for x in (mr.get('bindings') or []) if x.get('stage')=='ps']
  if binds!=[(0,TEX),(1,TEX),(2,TEX)]:v.append(f'bindings {binds} drift')
 if not s:v.append('shader row missing')
 else:
  for k,w in [('native_shader',NATIVE),('native_sha256',NSHA),('gcn_sha256',GSHA),('gcn_bytes',GBYTES)]:
   if s.get(k)!=w:v.append(f'{k} drift {s.get(k)!r} != {w!r}')
 if not i:v.append('image usage missing')
 else:
  got=[(int(x['resources'][0]['texture_index']),x['dmask_channels']) for x in i.get('instructions',[])]
  if got!=[(0,'x'),(1,'y'),(2,'x')]:v.append(f'image scalar lanes {got} drift')
 if not c:v.append('cbuffer usage missing')
 else:
  if (c.get('api_slot_read_dwords') or {}).get('0')!=API0:v.append(f"API0 reads {(c.get('api_slot_read_dwords') or {}).get('0')} != {API0}")
  if c.get('unresolved_load_count')!=0:v.append('unresolved cbuffer load')
 txt=a.disasm.read_text(errors='replace') if a.disasm.exists() else ''
 miss=[x for x in ANCHORS if x not in txt]
 if miss:v.append(f'missing native anchors {miss}')
 eq={
  'S':'mul(t1.y,t2.x)',
  'P':'gt(S,0)',
  'K':'clamp(API0[25])',
  'positive_rgb':'mul(mul(t0.x,S),K)',
  'MRT0.rgb':'select(P,(positive_rgb,positive_rgb,positive_rgb),(0,0,0))',
  'MRT0.a':'select(P,clamp(sub(1,S)),1)',
 }
 out={'schema':'d1_tower_common_ps_80c997a7_cfg_proof/v1',
      'status':'D1_TOWER_COMMON_PS_80C997A7_CFG_PROOF_EXACT' if not v else 'D1_TOWER_COMMON_PS_80C997A7_CFG_PROOF_PARTIAL',
      'shader':SH,'material':MAT,'visible_material_count':1,'texture_bindings':{'t0':TEX,'t1':TEX,'t2':TEX},
      'native_shader':NATIVE,'gcn_sha256':GSHA,'terminal_mrt0_export_address':TERMINAL,
      'exact_cfg_equation':eq,'violations':v,
      'semantic_boundary':{
       'MRT0_equation':'EXACT_OPERATION_PRESERVING_CFG_REDUCTION',
       'MRT1_equation':'OUTSIDE_THIS_PROOF',
       'texture_scalar_lanes':'EXACT_NATIVE_IMAGE_USAGE',
       'API0_25_identity':'EXACT_SLOT_DWORD_HUMAN_MEANING_WITHHELD',
       'human_material_semantics':'WITHHELD'},
      'policy':'Only MRT0 is promoted. The distinct MRT1 path is not used to assign a material role here.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(out,indent=2))
 return 0 if out['status'].endswith('_EXACT') else 2
if __name__=='__main__':raise SystemExit(main())
