#!/usr/bin/env python3
"""Exact CFG-aware MRT0 proof for Tower common shader 80CA0BFA.

The pre-sample control flow selects one of four API0 coefficient banks from attr0.y
and attr0.x, producing a squared/clamped scalar S. The shader then samples authored
t0.rgba and expands S through API0[24:28] plus the exact API13[6]*API13[7] runtime
RGB-scale product.

MRT1/pass semantics are outside this proof. Coefficient/interpolant meanings remain
unnamed.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

SH='80CA0BFA';MATS={'80CA0BBC','80CA0BBD'};TEX='80CA0B7A'
NATIVE='80CA0C01';NSHA='6b5061263387ef8786f146f596f68db2144c12b217aeb8c634c346475292f885'
GSHA='87dc29882f05ad9560a29687e76dd090ef1d2ef0db089b986d417fc95907542e';GBYTES=380
API={'0':[8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28],'13':[6,7]}
ANCHORS=[
 'v_cmp_gt_f32    s[0:1], v6, 1.0',
 'v_cmp_lt_f32    vcc, 0, v3',
 's_buffer_load_dwordx4 s[24:27], s[16:19], 0x10',
 's_buffer_load_dwordx4 s[24:27], s[16:19], 0x14',
 's_buffer_load_dwordx4 s[24:27], s[16:19], 0x8',
 's_buffer_load_dwordx4 s[24:27], s[16:19], 0xc',
 'v_mad_f32       v4, s25, abs(v3), v4 clamp',
 'v_mul_f32       v3, v4, v4',
 'image_sample    v[4:7], v[5:8], s[4:11], s[12:15] dmask:15',
 's_buffer_load_dword s4, s[16:19], 0x1c',
 's_buffer_load_dwordx4 s[8:11], s[16:19], 0x18',
 's_buffer_load_dwordx2 s[0:1], s[0:3], 0x6',
 'v_mul_f32       v0, v3, v7',
 'v_mul_f32       v2, v3, v4',
 'v_mul_f32       v4, v3, v5',
 'v_mul_f32       v3, v3, v6',
 'exp             mrt0, v2, v2, v0, v0 done compr vm',
]

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def main():
 ap=argparse.ArgumentParser()
 for n in ('manifest','shader-report','image-usage','cbuffer-usage','disasm','out'):
  ap.add_argument('--'+n,type=Path,required=True)
 a=ap.parse_args();v=[]
 m=json.loads(a.manifest.read_text());sr=json.loads(a.shader_report.read_text());iu=json.loads(a.image_usage.read_text());cb=json.loads(a.cbuffer_usage.read_text())
 if m.get('status')!='D1_WORLD_VISIBLE_MATERIAL_TEXTURE_EXPORT' or m.get('material_decode_errors') or m.get('texture_errors'):v.append('manifest not exact')
 if sr.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or sr.get('error_count'):v.append('shader report not exact')
 if iu.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':v.append('image usage not exact')
 if cb.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or cb.get('missing_usage'):v.append('cbuffer usage not exact')
 s=next((x for x in sr.get('shaders',[]) if norm(x.get('shader'))==SH),None);i=next((x for x in iu.get('shaders',[]) if norm(x.get('shader'))==SH),None);c=next((x for x in cb.get('shaders',[]) if norm(x.get('shader'))==SH),None)
 freq={norm(k):int(x) for k,x in (m.get('pixel_shader_frequency') or {}).items()}
 if freq.get(SH)!=2:v.append(f'frequency {freq.get(SH)} != 2')
 mm=[(norm(k),x) for k,x in (m.get('materials') or {}).items() if norm(x.get('pixel_shader'))==SH]
 if {x[0] for x in mm}!=MATS:v.append(f'materials {[x[0] for x in mm]} != {sorted(MATS)}')
 for mh,mr in mm:
  binds=[(int(x['texture_index']),norm(x['texture'])) for x in (mr.get('bindings') or []) if x.get('stage')=='ps']
  if binds!=[(0,TEX)]:v.append(f'{mh}: bindings {binds} drift')
 if not s:v.append('shader row missing')
 else:
  for k,w in [('native_shader',NATIVE),('native_sha256',NSHA),('gcn_sha256',GSHA),('gcn_bytes',GBYTES)]:
   if s.get(k)!=w:v.append(f'{k} drift {s.get(k)!r} != {w!r}')
 if not i:v.append('image usage missing')
 else:
  ins=i.get('instructions') or []
  if len(ins)!=1 or ins[0].get('dmask_channels')!='xyzw' or int(ins[0]['resources'][0]['texture_index'])!=0:v.append(f'image usage drift {ins}')
 if not c:v.append('cbuffer usage missing')
 else:
  got={str(k):[int(z) for z in q] for k,q in (c.get('api_slot_read_dwords') or {}).items()}
  if got!=API:v.append(f'cbuffer reads {got} != {API}')
  if c.get('unresolved_load_count')!=0:v.append('unresolved cbuffer load')
 txt=a.disasm.read_text(errors='replace') if a.disasm.exists() else ''
 miss=[x for x in ANCHORS if x not in txt]
 if miss:v.append(f'missing native anchors {miss}')
 sel={
  'X':'attr0.x','Y':'attr0.y',
  'Q_hi_pos':'square(clamp(mad(API0[17],abs(add(API0[18],X)),API0[16])))',
  'Q_hi_else':'square(clamp(mad(API0[21],abs(add(API0[22],X)),API0[20])))',
  'Q_lo_pos':'square(clamp(mad(API0[9],abs(add(API0[10],X)),API0[8])))',
  'Q_lo_else':'square(clamp(mad(API0[13],abs(add(API0[14],X)),API0[12])))',
  'S':'select(gt(Y,1),select(gt(X,0),Q_hi_pos,Q_hi_else),select(gt(X,0),Q_lo_pos,Q_lo_else))',
 }
 eq={
  'A':'mul(S,t0.a)',
  'G':'mul(mul(API13[6],API13[7]),A)',
  'MRT0.r':'mul(mul(S,t0.r),mul(API0[24],API0[28]),G)',
  'MRT0.g':'mul(mul(S,t0.g),mul(API0[25],API0[28]),G)',
  'MRT0.b':'mul(mul(S,t0.b),mul(API0[26],API0[28]),G)',
  'MRT0.a':'A',
 }
 out={'schema':'d1_tower_common_ps_80ca0bfa_cfg_proof/v1',
      'status':'D1_TOWER_COMMON_PS_80CA0BFA_CFG_PROOF_EXACT' if not v else 'D1_TOWER_COMMON_PS_80CA0BFA_CFG_PROOF_PARTIAL',
      'shader':SH,'visible_material_count':2,'materials':sorted(MATS),'texture_t0':TEX,
      'native_shader':NATIVE,'gcn_sha256':GSHA,
      'exact_cfg_selector':sel,'exact_terminal_equation':eq,'violations':v,
      'semantic_boundary':{
       'nested_selector':'EXACT_NATIVE_GCN_STRUCTURE',
       'MRT0_equation':'EXACT_OPERATION_PRESERVING_CFG_REDUCTION',
       'MRT1':'OUTSIDE_THIS_PROOF',
       'API13_product':'EXACT_SHADER_INPUT_IDENTITY_PRODUCER_LIVE_VALUE_WITHHELD',
       'human_texture_or_pass_meaning':'WITHHELD'},
      'policy':'The exact branch-selected scalar and MRT0 arithmetic are closed without naming the coefficient banks or pass. MRT1 remains separate.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
 return 0 if out['status'].endswith('_EXACT') else 2
if __name__=='__main__':raise SystemExit(main())
