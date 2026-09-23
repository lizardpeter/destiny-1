#!/usr/bin/env python3
"""Exact CFG-aware closure for three D1 Tower common alpha-branch pixel shaders.

These three retail programs share one structural boundary that the generic
straight-line symbolic reducer intentionally refuses to cross:
- sample authored t0.rgba;
- select lanes where 0 < t0.a with EXEC;
- write complementary per-lane values;
- merge EXEC;
- consume exact API0[5].

The proof is deliberately family-specific and pins retail identities, material
bindings, cbuffer provenance, terminal export addresses, and critical native GCN
control-flow/arithmetic anchors. Equations preserve select/rcp/clamp operation
shape rather than assuming normalized texture ranges or simplifying A*rcp(A).

No human material/pass meaning is inferred.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

CFG={
'80C991D5':{
 'material':'80C98E79','texture':'80BB60D6','native_shader':'80A3D3AE',
 'native_sha256':'9b8b88caeb4ef7f964823ba167e2d35322e4cf238eb4f9fc14175db023d9471c',
 'gcn_sha256':'fb604def41c1f79ebee55fda5e47db83fc957c99fc5f9835a71e4bc0e178b305',
 'gcn_bytes':232,'terminal':'0000000000DC',
 'anchors':[
  'v_cmp_lt_f32    vcc, 0, v3',
  's_and_saveexec_b64 s[0:1], vcc',
  'v_add_f32       v4, -v3, 1.0 clamp',
  's_cbranch_execz .L96_0',
  'v_rcp_f32       v5, v3',
  'v_mul_f32       v3, v3, v5',
  'v_sub_f32       v5, 1.0, v4',
  's_andn2_b64     exec, s[0:1], exec',
  'v_mov_b32       v5, 0',
  's_mov_b64       exec, s[0:1]',
  's_buffer_load_dword s0, s[0:3], 0x5',
  'v_max_f32       v4, s0, s0 clamp',
  'v_mul_f32       v0, v5, v4',
  'v_madak_f32     v1, v0, v1, 0x3f800000',
  'v_madak_f32     v2, v0, v2, 0x3f800000',
  'v_madak_f32     v0, v0, v3, 0x3f800000',
  'exp             mrt0, v1, v1, v0, v0 done compr vm',
 ],
 'equation':{
  'P':'gt(t0.a,0)',
  'N':'select(P,mul(t0.a,rcp(t0.a)),0)',
  'coverage':'select(P,sub(1,clamp(sub(1,t0.a))),0)',
  'K':'clamp(API0[5])',
  'branch_rgb':'select(P,mul(t0.rgb,N),(0,0,0))',
  'MRT0.rgb':'mad(mul(coverage,K),sub(branch_rgb,1),1)',
  'MRT0.a':'0',
 },
 'export_lane_gate':'original incoming EXEC restored before MRT0; no additional post-merge numeric gate',
},
'8093EA57':{
 'material':'8093EA4A','texture':'80AA9D4D','native_shader':'80AA9D64',
 'native_sha256':'6b6c1ecdbf81370d5e702a611deefec6cf2f96795e9bfc761b065a780aad5635',
 'gcn_sha256':'c846c4182497fb5f7e98226964f91045e2c8fab244141c380845800968fdbf51',
 'gcn_bytes':212,'terminal':'0000000000C8',
 'anchors':[
  'v_cmp_lt_f32    vcc, 0, v3',
  's_and_saveexec_b64 s[0:1], vcc',
  'v_add_f32       v4, -v3, 1.0 clamp',
  's_cbranch_execz .L100_0',
  'v_rcp_f32       v5, v3',
  'v_mul_f32       v3, v3, v5',
  'v_sub_f32       v5, 1.0, v4',
  's_andn2_b64     exec, s[0:1], exec',
  'v_mov_b32       v5, 0',
  's_mov_b64       exec, s[0:1]',
  's_buffer_load_dword s0, s[0:3], 0x5',
  'v_max_f32       v4, s0, s0 clamp',
  'v_madak_f32     v0, v4, v5, 0xbf000000',
  'v_cmp_gt_f32    vcc, 0, v0',
  's_andn2_b64     s[18:19], s[18:19], vcc',
  'exp             mrt0, v1, v1, v0, v0 done compr vm',
 ],
 'equation':{
  'P':'gt(t0.a,0)',
  'N':'select(P,mul(t0.a,rcp(t0.a)),0)',
  'coverage':'select(P,sub(1,clamp(sub(1,t0.a))),0)',
  'K':'clamp(API0[5])',
  'MRT0.rgb':'select(P,mul(t0.rgb,N),(0,0,0))',
  'MRT0.a':'0',
  'post_merge_gate_value':'mad(K,coverage,-0.5)',
 },
 'export_lane_gate':'incoming_EXEC AND NOT(gt(0,post_merge_gate_value))',
},
'80CA12E0':{
 'material':'80CA12CF','texture':'80CA0D09','native_shader':'80AAF492',
 'native_sha256':'a9f3e160b79bbc3ffa288a34b58eb4311a1de509649b81da936c319ee1c0d119',
 'gcn_sha256':'005a8c90623b7f391bef50e714bbf21a864bd90dc05583de6cfedf0b34467abc',
 'gcn_bytes':196,'terminal':'0000000000B8',
 'anchors':[
  'v_cmp_lt_f32    vcc, 0, v3',
  's_and_saveexec_b64 s[0:1], vcc',
  'v_add_f32       v5, -v3, 1.0 clamp',
  'v_mul_f32       v0, v0, v3',
  'v_mul_f32       v6, v1, v3',
  'v_mul_f32       v3, v2, v3',
  's_andn2_b64     exec, s[0:1], exec',
  'v_mov_b32       v5, 1.0',
  'v_mov_b32       v0, 0',
  's_mov_b64       exec, s[0:1]',
  's_buffer_load_dword s0, s[0:3], 0x5',
  'v_max_f32       v4, s0, s0 clamp',
  'v_mul_f32       v1, v0, v4',
  'v_mul_f32       v2, v6, v4',
  'v_mul_f32       v3, v3, v4',
  'v_add_f32       v0, -1.0, v5',
  'v_madak_f32     v0, v4, v0, 0x3f800000',
  'exp             mrt0, v1, v1, v0, v0 done compr vm',
 ],
 'equation':{
  'P':'gt(t0.a,0)',
  'K':'clamp(API0[5])',
  'selected_alpha_helper':'select(P,clamp(sub(1,t0.a)),1)',
  'MRT0.rgb':'select(P,mul(mul(t0.rgb,t0.a),K),(0,0,0))',
  'MRT0.a':'mad(K,sub(selected_alpha_helper,1),1)',
 },
 'export_lane_gate':'original incoming EXEC restored before MRT0; no additional post-merge numeric gate',
},
}

def main():
 ap=argparse.ArgumentParser()
 for n in ('manifest','shader-report','image-usage','cbuffer-usage','disasm-dir','out'):
  ap.add_argument('--'+n,type=Path,required=True)
 a=ap.parse_args()
 m=json.loads(a.manifest.read_text());sr=json.loads(a.shader_report.read_text())
 iu=json.loads(a.image_usage.read_text());cb=json.loads(a.cbuffer_usage.read_text())
 violations=[];rows=[]
 if m.get('status')!='D1_WORLD_VISIBLE_MATERIAL_TEXTURE_EXPORT' or m.get('material_decode_errors') or m.get('texture_errors'):violations.append('manifest not exact')
 if sr.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or sr.get('error_count'):violations.append('shader report not exact')
 if iu.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':violations.append('image usage not exact')
 if cb.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or cb.get('missing_usage'):violations.append('cbuffer usage not exact')
 sby={norm(x['shader']):x for x in sr.get('shaders',[])};iby={norm(x['shader']):x for x in iu.get('shaders',[])};cby={norm(x['shader']):x for x in cb.get('shaders',[])}
 mats=m.get('materials') or {};freq={norm(k):int(v) for k,v in (m.get('pixel_shader_frequency') or {}).items()}
 for sh,cfg in CFG.items():
  errs=[];s=sby.get(sh);i=iby.get(sh);c=cby.get(sh)
  if freq.get(sh)!=1:errs.append(f"visible material frequency {freq.get(sh)} != 1")
  mm=[(norm(k),v) for k,v in mats.items() if norm(v.get('pixel_shader'))==sh]
  if len(mm)!=1:errs.append(f'material row count {len(mm)} != 1')
  else:
   mh,mr=mm[0]
   if mh!=cfg['material']:errs.append(f'material {mh} != {cfg["material"]}')
   binds=[x for x in (mr.get('bindings') or []) if x.get('stage')=='ps']
   got=[(int(x['texture_index']),norm(x['texture'])) for x in binds]
   if got!=[(0,cfg['texture'])]:errs.append(f'PS binding {got} != t0:{cfg["texture"]}')
   if (mr.get('tfx') or {}).get('ps',{}).get('bytes_hex')!='49004721':errs.append('PS TFX assignment prefix drift')
  if not s:errs.append('shader extract row missing')
  else:
   for k,want in [('native_shader',cfg['native_shader']),('native_sha256',cfg['native_sha256']),('gcn_sha256',cfg['gcn_sha256']),('gcn_bytes',cfg['gcn_bytes'])]:
    if s.get(k)!=want:errs.append(f'{k} {s.get(k)!r} != {want!r}')
  if not i:errs.append('image usage row missing')
  else:
   if i.get('used_texture_indices')!=[0]:errs.append(f"used t# {i.get('used_texture_indices')} != [0]")
   ins=i.get('instructions') or []
   if len(ins)!=1 or ins[0].get('dmask_channels')!='xyzw':errs.append(f'image sample shape drift {ins}')
  if not c:errs.append('cbuffer row missing')
  else:
   if (c.get('api_slot_read_dwords') or {}).get('0')!=[5]:errs.append(f"API0 reads {(c.get('api_slot_read_dwords') or {}).get('0')} != [5]")
   if c.get('unresolved_load_count')!=0:errs.append('unresolved cbuffer load present')
  p=a.disasm_dir/f'PS_{sh}.s'
  if not p.exists():p=a.disasm_dir/f'PS_{sh}_GFX700.s'
  if not p.exists():errs.append('disassembly missing');txt=''
  else:txt=p.read_text(errors='replace')
  missing=[x for x in cfg['anchors'] if x not in txt]
  if missing:errs.append(f'missing exact control/dataflow anchors {missing}')
  rows.append({
   'shader':sh,'visible_material_count':1,'material':cfg['material'],'texture_t0':cfg['texture'],
   'native_shader':cfg['native_shader'],'gcn_sha256':cfg['gcn_sha256'],'gcn_bytes':cfg['gcn_bytes'],
   'terminal_mrt0_export_address':cfg['terminal'],
   'exact_cfg_equation':cfg['equation'],'exact_export_lane_gate':cfg['export_lane_gate'],
   'violations':errs,
  })
  violations.extend(f'{sh}: {x}' for x in errs)
 out={
  'schema':'d1_tower_common_alpha_branch_cfg_proof/v1',
  'status':'D1_TOWER_COMMON_ALPHA_BRANCH_CFG_PROOF_EXACT' if len(rows)==3 and not violations else 'D1_TOWER_COMMON_ALPHA_BRANCH_CFG_PROOF_PARTIAL',
  'shader_family_count':len(rows),'visible_material_count':sum(x['visible_material_count'] for x in rows),
  'rows':rows,'violations':violations,
  'semantic_boundary':{
   'branch_predicate':'EXACT_NATIVE_GCN',
   'exec_lane_partition_and_merge':'EXACT_NATIVE_GCN_STRUCTURE',
   'terminal_equation':'EXACT_OPERATION_PRESERVING_CFG_REDUCTION',
   'API0_5_identity':'EXACT_CBUFFER_SLOT_AND_DWORD_SEMANTIC_WITHHELD',
   'texture_identity':'EXACT_SERIALIZED_MATERIAL_BINDING',
   'pass_or_blend_semantics':'WITHHELD',
   'portable_renderer_equivalence':'NOT_IMPLIED',
  },
  'policy':'Equations preserve the alpha predicate, EXEC complementary lane writes, rcp/clamp operation shape, and any final export-lane gate. API0[5] and t0 are exact identities but are not assigned human meanings.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'rows':rows,'violations':violations},indent=2))
 return 0 if out['status']=='D1_TOWER_COMMON_ALPHA_BRANCH_CFG_PROOF_EXACT' else 2
if __name__=='__main__':raise SystemExit(main())
