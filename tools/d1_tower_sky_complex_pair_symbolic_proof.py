#!/usr/bin/env python3
"""Exact symbolic closure for the two highest-weight remaining Tower sky families.

PS 80B9F726 and 80B9F727 each back three visible sky materials.  Their terminal
expressions are reduced by d1_gcn_terminal_symbolic_reducer.py and pinned by
operation-preserving SHA256.

The pair shares the exact same alpha-side geometric/renderer gate: after replacing
80B9F726 API0[32]/API0[33] with 80B9F727 API0[24]/API0[25], the native-order alpha
expression strings are identical.

No human sky/pass semantic is assigned.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

CFG={
 '80B9F726':{
  'freq':3,'native':'80B9F73F','native_sha':'f769726011eafed112910ef911a6672d30c4ef5077b0a3385c38f0d65efd543d',
  'gcn_sha':'3d2051bcc2fc933266c184ec3a2d6bae6779459d41bc8281bd395af93b0b62fa','gcn_bytes':752,
  'terminal':'0000000002E4','bindings':[0,1,2,3],
  'expr_sha':{
   'R':'8589c4a031d9a73b7e9e50725f42571af551a10aa5540743257202b7357cbcf8',
   'G':'089879f032845406445d8539b4328dc35421dfc35e47f2c0fd57dad1c362598a',
   'B':'bdf62e26494c1673ec8f7d81d269cce2eeaf1ef56b9f9cc3d7cfb5e473170cfd',
   'A':'b4c6445e75412085325a965a65214c03e99ce4d4f5eda26fbd6f63b779ac702f'}},
 '80B9F727':{
  'freq':3,'native':'80B9F740','native_sha':'de1d2917987b3f1c724da39b0eb103fd391f215fef06b9389aeb75acb23b9169',
  'gcn_sha':'791725769fe0905e93dab37d3912f759904c6b861bf11ca1031841720d51eff5','gcn_bytes':404,
  'terminal':'000000000188','bindings':[0,1,2],
  'expr_sha':{
   'R':'5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9',
   'G':'5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9',
   'B':'5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9',
   'A':'424da9470ee1d3fa56f539de94274025954c6a5795d10d37e27291cb1766a8ef'}},
}

def main():
 ap=argparse.ArgumentParser()
 for n in ('material-manifest','shader-report','symbolic','out'):ap.add_argument('--'+n,type=Path,required=True)
 a=ap.parse_args()
 m=json.loads(a.material_manifest.read_text());sr=json.loads(a.shader_report.read_text());sy=json.loads(a.symbolic.read_text())
 v=[];rows=[]
 if m.get('status')!='D1_WORLD_VISIBLE_MATERIAL_TEXTURE_EXPORT' or m.get('material_decode_errors') or m.get('texture_errors'):v.append('material manifest not exact')
 if sr.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or sr.get('error_count'):v.append('shader report not exact')
 if sy.get('status')!='D1_GCN_TERMINAL_SYMBOLIC_REDUCER_EXACT' or sy.get('violations'):v.append('symbolic reducer input not exact')
 sby={norm(x['shader']):x for x in sr.get('shaders',[])};yby={norm(x['shader']):x for x in sy.get('shaders',[])}
 freq={norm(k):int(x) for k,x in (m.get('pixel_shader_frequency') or {}).items()};mats=m.get('materials') or {}
 for sh,cfg in CFG.items():
  errs=[]
  if freq.get(sh)!=cfg['freq']:errs.append(f"frequency {freq.get(sh)} != {cfg['freq']}")
  mm=[x for x in mats.values() if norm(x.get('pixel_shader'))==sh]
  if len(mm)!=cfg['freq']:errs.append(f"material row count {len(mm)} != {cfg['freq']}")
  for x in mm:
   inds=sorted(int(q['texture_index']) for q in (x.get('bindings') or []) if q.get('stage')=='ps')
   if inds!=cfg['bindings']:errs.append(f"material {x.get('material')} binding indices {inds} != {cfg['bindings']}")
  s=sby.get(sh)
  if not s:errs.append('shader report row missing')
  else:
   for k,z in [('native_shader',cfg['native']),('native_sha256',cfg['native_sha']),('gcn_sha256',cfg['gcn_sha']),('gcn_bytes',cfg['gcn_bytes'])]:
    if s.get(k)!=z:errs.append(f'{k} drift {s.get(k)!r} != {z!r}')
  y=yby.get(sh)
  if not y:errs.append('symbolic row missing')
  else:
   if not y.get('exact_terminal_expression'):errs.append('symbolic terminal expression not exact')
   if y.get('terminal_mrt0_export_address')!=cfg['terminal']:errs.append('terminal export address drift')
   if y.get('terminal_expression_sha256')!=cfg['expr_sha']:errs.append(f"symbolic expression SHA drift {y.get('terminal_expression_sha256')}")
   if y.get('unsupported_operations'):errs.append(f"unsupported ops {y['unsupported_operations']}")
   if any(y.get('terminal_unresolved_markers',{}).values()):errs.append(f"unresolved markers {y['terminal_unresolved_markers']}")
  eq=None if not y else y.get('terminal_expressions')
  rows.append({'shader':sh,'visible_material_count':cfg['freq'],'gcn_sha256':cfg['gcn_sha'],
               'terminal_expression_sha256':cfg['expr_sha'],'exact_terminal_equation':eq,'violations':errs})
  v.extend(f'{sh}: {e}' for e in errs)

 a726=(yby.get('80B9F726') or {}).get('terminal_expressions',{}).get('A')
 a727=(yby.get('80B9F727') or {}).get('terminal_expressions',{}).get('A')
 normalized=None if a726 is None else a726.replace('API0[32]','API0[24]').replace('API0[33]','API0[25]')
 shared=(normalized==a727 and a727 is not None)
 if not shared:v.append('shared alpha gate relation failed')

 factor={
  'delta':['API12[28]-attr2.x','API12[29]-attr2.y','API12[30]-attr2.z'],
  'normal':['attr0.x','attr0.y','attr0.z'],
  'plane_term':'API12[24]*delta.x + API12[25]*delta.y + API12[26]*delta.z',
  'range_term':'rcp(API9[0] + API9[1]*t10.x) - abs(plane_term)',
  'angular_term':'dot(delta*rsq_clamp(dot(delta,delta)), normal*rsq_clamp(dot(normal,normal)))',
  'shared_pre_material_gate':'range_term * angular_term',
  '80B9F726_material_gate':'clamp(API0[32] * shared_pre_material_gate + API0[33])',
  '80B9F727_material_gate':'clamp(API0[24] * shared_pre_material_gate + API0[25])',
  '80B9F726_mrt0_a':'clamp(t1.a * t2.a * 80B9F726_material_gate)',
  '80B9F727_mrt0_a':'clamp(t1.a * t2.a * 80B9F727_material_gate)',
 }
 out={
  'schema':'d1_tower_sky_complex_pair_symbolic_proof/v1',
  'status':'D1_TOWER_SKY_COMPLEX_PAIR_SYMBOLIC_PROOF_EXACT' if len(rows)==2 and not v else 'D1_TOWER_SKY_COMPLEX_PAIR_SYMBOLIC_PROOF_PARTIAL',
  'shader_family_count':len(rows),'visible_material_count':sum(x['visible_material_count'] for x in rows),
  'visible_material_fraction':sum(x['visible_material_count'] for x in rows)/74,
  'rows':rows,'shared_alpha_gate_relation_exact':shared,'shared_alpha_gate_factorization':factor,
  'violations':v,
  'semantic_boundary':{
   'terminal_expression':'EXACT_NATIVE_OPERATION_ORDER',
   'shared_alpha_gate_relation':'EXACT_STRING_IDENTITY_AFTER_API0_COEFFICIENT_REMAP',
   'factorized_readable_form':'ALGEBRAIC_SUMMARY_OF_EXACT_EXPRESSION',
   'human_sky_semantics':'WITHHELD',
   'live_API9_API12_values_and_producers':'WITHHELD',
  },
  'policy':'The raw terminal expressions are operation-preserving outputs from the exact symbolic reducer. The readable shared gate is a structural factorization only; no human role is assigned.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'shared_alpha_gate_relation_exact':shared,
                   'factorization':factor,'rows':[{'shader':x['shader'],'sha':x['terminal_expression_sha256'],'violations':x['violations']} for x in rows],
                   'violations':v},indent=2))
 return 0 if out['status']=='D1_TOWER_SKY_COMPLEX_PAIR_SYMBOLIC_PROOF_EXACT' else 2
if __name__=='__main__':raise SystemExit(main())
