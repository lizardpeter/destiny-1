#!/usr/bin/env python3
"""Exact CFG-aware MRT0 proof for Tower common shader 80CA1427.

The shader samples one authored RGB texture. Its early EXEC control flow chooses:
- zero when attr1.x > 0;
- otherwise one of two exact API0 3x3 coefficient matrices selected by attr1.y > 1.

A second lane split on W=sum(t0.rgb) controls the terminal MRT0 state. API0[28:29]
form a clamped scalar used by MRT1; the MRT0 equation uses the branch-selected matrix
vector, W, and final API0[41] multiplier. The independent MRT1 path is not assigned
a semantic here.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

SH='80CA1427';MAT='80CA1402';TEX='80CA11D3';NATIVE='80CA142E'
NSHA='8aee86c88ac0072eebc0d2b0dc12a0f1c6d36a097bf8216477509d3539192cf4'
GSHA='ef72b6c993535bb461cce691ade69e4460e7e47db391afa4ede95a454e744903';GBYTES=648
API0=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,28,29,41]
ANCHORS=[
 'image_sample    v[4:6], v[2:5], s[4:11], s[12:15] dmask:7',
 'v_cmp_gt_f32    s[0:1], v3, 1.0',
 'v_cmp_lt_f32    vcc, 0, v2',
 's_buffer_load_dwordx4 s[8:11], s[4:7], 0x10',
 's_buffer_load_dwordx4 s[12:15], s[4:7], 0xc',
 's_buffer_load_dwordx4 s[16:19], s[4:7], 0x14',
 's_buffer_load_dwordx4 s[8:11], s[4:7], 0x4',
 's_buffer_load_dwordx4 s[12:15], s[4:7], 0x0',
 's_buffer_load_dwordx4 s[16:19], s[4:7], 0x8',
 'v_add_f32       v4, v4, v5',
 'v_add_f32       v4, v6, v4',
 'v_cmp_lt_f32    vcc, 0, v4',
 's_and_b64       exec, s[0:1], vcc',
 's_buffer_load_dwordx2 s[2:3], s[4:7], 0x1c',
 'v_add_f32       v5, -v4, 1.0 clamp',
 'v_mad_f32       v6, v4, s3, v6 clamp',
 'v_mul_f32       v2, v2, v4',
 'v_mul_f32       v3, v3, v4',
 'v_mul_f32       v4, v7, v4',
 'v_sub_f32       v7, 1.0, v5',
 's_buffer_load_dword s0, s[4:7], 0x29',
 'v_max_f32       v9, s0, s0 clamp',
 'v_mul_f32       v5, v5, v9',
 'v_mul_f32       v6, v6, v9',
 'v_mul_f32       v7, v7, v9',
 'v_madak_f32     v2, v9, v2, 0x3f800000',
 'exp             mrt0, v0, v0, v1, v1 done compr vm',
]

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def main():
 ap=argparse.ArgumentParser()
 for n in ('manifest','shader-report','image-usage','cbuffer-usage','disasm','out'):ap.add_argument('--'+n,type=Path,required=True)
 a=ap.parse_args();v=[]
 m=json.loads(a.manifest.read_text());sr=json.loads(a.shader_report.read_text());iu=json.loads(a.image_usage.read_text());cb=json.loads(a.cbuffer_usage.read_text())
 if m.get('status')!='D1_WORLD_VISIBLE_MATERIAL_TEXTURE_EXPORT' or m.get('material_decode_errors') or m.get('texture_errors'):v.append('manifest not exact')
 if sr.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or sr.get('error_count'):v.append('shader report not exact')
 if iu.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':v.append('image usage not exact')
 if cb.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or cb.get('missing_usage'):v.append('cbuffer usage not exact')
 s=next((x for x in sr.get('shaders',[]) if norm(x.get('shader'))==SH),None);i=next((x for x in iu.get('shaders',[]) if norm(x.get('shader'))==SH),None);c=next((x for x in cb.get('shaders',[]) if norm(x.get('shader'))==SH),None)
 freq={norm(k):int(x) for k,x in (m.get('pixel_shader_frequency') or {}).items()}
 if freq.get(SH)!=1:v.append(f'frequency {freq.get(SH)} != 1')
 mm=[(norm(k),x) for k,x in (m.get('materials') or {}).items() if norm(x.get('pixel_shader'))==SH]
 if len(mm)!=1:v.append(f'material count {len(mm)} != 1')
 else:
  mh,mr=mm[0]
  if mh!=MAT:v.append(f'material {mh} != {MAT}')
  binds=[(int(x['texture_index']),norm(x['texture'])) for x in (mr.get('bindings') or []) if x.get('stage')=='ps']
  if binds!=[(0,TEX)]:v.append(f'bindings {binds} drift')
 if not s:v.append('shader row missing')
 else:
  for k,w in [('native_shader',NATIVE),('native_sha256',NSHA),('gcn_sha256',GSHA),('gcn_bytes',GBYTES)]:
   if s.get(k)!=w:v.append(f'{k} drift {s.get(k)!r} != {w!r}')
 if not i:v.append('image usage missing')
 else:
  ins=i.get('instructions') or []
  if len(ins)!=1 or ins[0].get('dmask_channels')!='xyz' or int(ins[0]['resources'][0]['texture_index'])!=0:v.append(f'image usage drift {ins}')
 if not c:v.append('cbuffer usage missing')
 else:
  if (c.get('api_slot_read_dwords') or {}).get('0')!=API0:v.append(f"API0 reads {(c.get('api_slot_read_dwords') or {}).get('0')} != {API0}")
  if c.get('unresolved_load_count')!=0:v.append('unresolved cbuffer load')
 txt=a.disasm.read_text(errors='replace') if a.disasm.exists() else ''
 miss=[x for x in ANCHORS if x not in txt]
 if miss:v.append(f'missing native anchors {miss}')
 matrix={
  'M_lo_row_r':'(API0[0],API0[4],API0[8])','M_lo_row_g':'(API0[1],API0[5],API0[9])','M_lo_row_b':'(API0[2],API0[6],API0[10])',
  'M_hi_row_r':'(API0[12],API0[16],API0[20])','M_hi_row_g':'(API0[13],API0[17],API0[21])','M_hi_row_b':'(API0[14],API0[18],API0[22])',
  'P':'select(gt(attr1.x,0),(0,0,0),select(gt(attr1.y,1),mul_matrix(M_hi,t0.rgb),mul_matrix(M_lo,t0.rgb)))',
 }
 eq={
  'W':'add(add(t0.r,t0.g),t0.b)',
  'positive':'gt(W,0)',
  'K':'clamp(API0[41])',
  'selected_alpha_helper':'select(positive,clamp(sub(1,W)),1)',
  'MRT0.rgb':'select(positive,mul(mul(P,W),K),(0,0,0))',
  'MRT0.a':'mad(K,sub(selected_alpha_helper,1),1)',
 }
 out={'schema':'d1_tower_common_ps_80ca1427_cfg_proof/v1',
      'status':'D1_TOWER_COMMON_PS_80CA1427_CFG_PROOF_EXACT' if not v else 'D1_TOWER_COMMON_PS_80CA1427_CFG_PROOF_PARTIAL',
      'shader':SH,'material':MAT,'visible_material_count':1,'texture_t0':TEX,'native_shader':NATIVE,'gcn_sha256':GSHA,
      'exact_cfg_matrix_selector':matrix,'exact_terminal_equation':eq,'violations':v,
      'semantic_boundary':{
       'matrix_selection':'EXACT_NATIVE_GCN_STRUCTURE',
       'MRT0_equation':'EXACT_OPERATION_PRESERVING_CFG_REDUCTION',
       'API0_28_29_MRT1_helper':'EXACT_BUT_NOT_REQUIRED_FOR_MRT0_EQUATION',
       'MRT1':'OUTSIDE_THIS_PROOF',
       'human_texture_matrix_or_pass_meaning':'WITHHELD'},
      'policy':'MRT0 is closed independently of the separate MRT1 arithmetic. Matrix rows are named only by exact API0 dword positions.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
 return 0 if out['status'].endswith('_EXACT') else 2
if __name__=='__main__':raise SystemExit(main())
