#!/usr/bin/env python3
"""Exact symbolic closure for the final four Tower sky shader families.

These families exercise the extended GFX700 symbolic subset: reverse subtract,
sqrt, exp2, floating compare predicates, and conditional select. Each is accepted
only by pinned retail identity, source material binding scope, exact terminal export
address, and operation-preserving terminal expression hashes.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

CFG={
'80B9EA17':(1,'80B9EA32','305c6e95011e259a04f6d99d5a73546585755927f97a1a92a35a3c88d9e2b4ac','0bd884d3b32785e2c0634defcccd2513f387477f97fa900381f3ca9163f8631c',580,'000000000238',[0,1],
 {'R':'085c5c089e0c57bb0f6249e08ce954c5df421073d4fa895704d62fa6f0e880cf','G':'0dc49a67cfc930b76747a49e82650f15f1c1b031c8ea78c2e2f8809319dc8da2','B':'ca66554657121a3ea34ad6e7bcf690f4440475e83d7b0ae0a12953e1d28e459e','A':'c6074f67a27b8f4ca7c991336f8185c2adad782e3b0f68bac0403f1849de03cd'}),
'80B9EA1A':(1,'80B9EA35','76cd8431d7926d93adab941d979eeac42535d6e7faba41488835a6c9d41eef40','55a3964c486edae4a745a5c95dc70f153e3ca18a9283b0272261825870067ad4',592,'000000000244',[0,1],
 {'R':'2e852bf059bd9d783361f3956500793c2cf948675ef5b057a202524577a9409d','G':'6ec723f05a062123f78261baafeb648830487d42487fe501e6a5e88c878c02da','B':'ff64024a2f45c217312ea88527ef2ae1a922e2900ed0864a972a5c3ea0449966','A':'c6074f67a27b8f4ca7c991336f8185c2adad782e3b0f68bac0403f1849de03cd'}),
'80B9EA23':(1,'80B9EA3C','c96b97bc7cc16a2ffc1469336c66673cdc58470379ef94fc0c2ca2a9ca8731fa','53b6463b4d0c71da0ec80c5d39b4536a1a0cca36cea591dfff580eb7ae2fe6b8',972,'0000000003C0',[0,1,2,3,4],
 {'R':'cf6a17811f8b8fb42b598f88576f945ae39ba522fcec572caaf1e980093d3f2f','G':'49afe5781341a06ad96460a9a4e3c18bed8e7ad9f2a0a75fc0151df797063f18','B':'eac3115c5523b296518d29605526fca725788080bbf04c68dffcf7bfc843e402','A':'b5063e1ae70b517392a92fd97dca2b733e144370024e801b8cb710dc98072802'}),
'80B9EA25':(1,'80B9EA3E','eb880a21da5d5bca6655556616596647816110aec4c42de7d109de922ee0b7a9','39aab1a693fcbefd64a29ea7d320eda5e878e5ee856c83b118730b05c628c324',1108,'000000000448',[0,1,2,3,4,5,6],
 {'R':'ea42acbb79ce08fc42fb5510ff5e2e7dd4bb13b4f15624492dd5b2e6a04f37d8','G':'3845d323fee8d5f86ead488400915c9baf61e43afcec3580cad1f6e6e980a3c3','B':'e4cbc81e2f62957f1f6b5ec33a9dfa8463144579ba4cc021695f3be8cf8d41ac','A':'aebc1ab0aaff428f10a768162efd18b1ab88944f0e28f4bc62c96d6bf6f899ab'}),
}

def main():
 ap=argparse.ArgumentParser()
 for n in ('material-manifest','shader-report','symbolic','out'):ap.add_argument('--'+n,type=Path,required=True)
 a=ap.parse_args()
 m=json.loads(a.material_manifest.read_text());sr=json.loads(a.shader_report.read_text());sy=json.loads(a.symbolic.read_text())
 v=[];rows=[]
 if m.get('status')!='D1_WORLD_VISIBLE_MATERIAL_TEXTURE_EXPORT' or m.get('material_decode_errors') or m.get('texture_errors'):v.append('manifest not exact')
 if sr.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or sr.get('error_count'):v.append('shader report not exact')
 if sy.get('status')!='D1_GCN_TERMINAL_SYMBOLIC_REDUCER_EXACT' or sy.get('violations'):v.append('symbolic reducer input not exact')
 sby={norm(x['shader']):x for x in sr.get('shaders',[])};yby={norm(x['shader']):x for x in sy.get('shaders',[])}
 freq={norm(k):int(x) for k,x in (m.get('pixel_shader_frequency') or {}).items()};mats=m.get('materials') or {}
 for sh,cfg in CFG.items():
  freq0,native,nsha,gsha,gbytes,terminal,bindings,exprsha=cfg;errs=[]
  if freq.get(sh)!=freq0:errs.append(f'frequency {freq.get(sh)} != {freq0}')
  mm=[x for x in mats.values() if norm(x.get('pixel_shader'))==sh]
  if len(mm)!=freq0:errs.append(f'material row count {len(mm)} != {freq0}')
  for x in mm:
   inds=sorted(int(q['texture_index']) for q in (x.get('bindings') or []) if q.get('stage')=='ps')
   if inds!=bindings:errs.append(f"material {x.get('material')} binding indices {inds} != {bindings}")
  s=sby.get(sh)
  if not s:errs.append('shader row missing')
  else:
   for k,z in [('native_shader',native),('native_sha256',nsha),('gcn_sha256',gsha),('gcn_bytes',gbytes)]:
    if s.get(k)!=z:errs.append(f'{k} drift {s.get(k)!r} != {z!r}')
  y=yby.get(sh)
  if not y:errs.append('symbolic row missing')
  else:
   if y.get('terminal_mrt0_export_address')!=terminal:errs.append('terminal address drift')
   if not y.get('exact_terminal_expression'):errs.append('terminal expression not exact')
   if y.get('terminal_expression_sha256')!=exprsha:errs.append(f"expression SHA drift {y.get('terminal_expression_sha256')}")
   if y.get('unsupported_operations'):errs.append(f"unsupported operations {y['unsupported_operations']}")
   if any(y.get('terminal_unresolved_markers',{}).values()):errs.append(f"unresolved markers {y['terminal_unresolved_markers']}")
  rows.append({'shader':sh,'visible_material_count':freq0,'gcn_sha256':gsha,
               'terminal_expression_sha256':exprsha,
               'exact_terminal_equation':None if not y else y.get('terminal_expressions'),'violations':errs})
  v.extend(f'{sh}: {e}' for e in errs)
 out={
  'schema':'d1_tower_sky_final_symbolic_proof/v1',
  'status':'D1_TOWER_SKY_FINAL_SYMBOLIC_PROOF_EXACT' if len(rows)==4 and not v else 'D1_TOWER_SKY_FINAL_SYMBOLIC_PROOF_PARTIAL',
  'shader_family_count':len(rows),'visible_material_count':sum(x['visible_material_count'] for x in rows),
  'visible_material_fraction':sum(x['visible_material_count'] for x in rows)/74,
  'rows':rows,'violations':v,
  'semantic_boundary':{
   'terminal_expression':'EXACT_NATIVE_OPERATION_ORDER',
   'predicate_select_shape':'EXACT_NATIVE_GCN',
   'exp_operation':'EXACT_GCN_EXP2_SHAPE',
   'human_sky_semantics':'WITHHELD',
   'runtime_producer_identity':'WITHHELD',
  },
  'policy':'Final tail closure uses only audited GFX700 operation semantics and pinned terminal expression hashes. Human sky meanings remain withheld.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'families':len(rows),'materials':out['visible_material_count'],
                   'rows':[{'shader':x['shader'],'sha':x['terminal_expression_sha256'],'violations':x['violations']} for x in rows],
                   'violations':v},indent=2))
 return 0 if out['status']=='D1_TOWER_SKY_FINAL_SYMBOLIC_PROOF_EXACT' else 2
if __name__=='__main__':raise SystemExit(main())
