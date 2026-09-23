#!/usr/bin/env python3
"""Aggregate fail-closed terminal-behavior closure for all Tower common shaders.

Evidence levels are intentionally distinct:
A) flattened terminal equation:
   - CFG-safe exact rows from d1_tower_common_symbolic_coverage/v1;
   - dedicated family-specific CFG equation proofs.
B) exact native CFG program + exact terminal reduction:
   - 8093E501, whose real iterative loop is preserved as a program.

The union must exactly equal the 65-family / 99-visible-material common corpus.
No human material-role or portable renderer equivalence is implied.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def load(p):return json.loads(p.read_text())

def main():
 ap=argparse.ArgumentParser()
 for n in ('manifest','symbolic-coverage','alpha-cfg','be9-bea-cfg','ps-80c997a7','ps-80ca0bfa','ps-80ca1427','ps-8093e501','out'):
  ap.add_argument('--'+n,type=Path,required=True)
 a=ap.parse_args();v=[]
 m=load(a.manifest);sy=load(a.symbolic_coverage);alpha=load(a.alpha_cfg);pair=load(a.be9_bea_cfg);p997=load(a.ps_80c997a7);pbfa=load(a.ps_80ca0bfa);p1427=load(a.ps_80ca1427);p501=load(a.ps_8093e501)
 if m.get('status')!='D1_WORLD_VISIBLE_MATERIAL_TEXTURE_EXPORT' or m.get('material_decode_errors') or m.get('texture_errors'):v.append('manifest not exact')
 if sy.get('status')!='D1_TOWER_COMMON_SYMBOLIC_COVERAGE_EXACT' or sy.get('violations'):v.append('symbolic coverage not exact')
 expected_status=[
  (alpha,'D1_TOWER_COMMON_ALPHA_BRANCH_CFG_PROOF_EXACT'),
  (pair,'D1_TOWER_COMMON_80CA0BE9_80CA0BEA_CFG_PROOF_EXACT'),
  (p997,'D1_TOWER_COMMON_PS_80C997A7_CFG_PROOF_EXACT'),
  (pbfa,'D1_TOWER_COMMON_PS_80CA0BFA_CFG_PROOF_EXACT'),
  (p1427,'D1_TOWER_COMMON_PS_80CA1427_CFG_PROOF_EXACT'),
  (p501,'D1_TOWER_COMMON_PS_8093E501_CFG_PROGRAM_PROOF_EXACT'),
 ]
 for d,s in expected_status:
  if d.get('status')!=s or d.get('violations'):v.append(f'{s}: source proof not exact')

 freq={norm(k):int(x) for k,x in (m.get('pixel_shader_frequency') or {}).items()}
 if len(freq)!=65 or sum(freq.values())!=99:v.append(f'corpus size drift families={len(freq)} visible={sum(freq.values())}')

 flat={}
 def add_flat(sh,kind,source):
  sh=norm(sh)
  if sh in flat:v.append(f'duplicate flattened closure {sh}: {flat[sh]["source"]} vs {source}')
  flat[sh]={'shader':sh,'visible_material_count':freq.get(sh),'closure_kind':kind,'source':source}

 for r in sy.get('exact_rows',[]):
  add_flat(r['shader'],'CFG_SAFE_STRAIGHTLINE_SYMBOLIC_EQUATION','TOWER_COMMON65_SYMBOLIC_COVERAGE')
 for r in alpha.get('rows',[]):add_flat(r['shader'],'DEDICATED_CFG_EQUATION','ALPHA_BRANCH_CFG_PROOF')
 for r in pair.get('rows',[]):add_flat(r['shader'],'DEDICATED_CFG_EQUATION','80CA0BE9_80CA0BEA_CFG_PROOF')
 add_flat(p997.get('shader'),'DEDICATED_CFG_EQUATION','80C997A7_CFG_PROOF')
 add_flat(pbfa.get('shader'),'DEDICATED_CFG_EQUATION','80CA0BFA_CFG_PROOF')
 add_flat(p1427.get('shader'),'DEDICATED_CFG_EQUATION','80CA1427_CFG_PROOF')

 prog_sh=norm(p501.get('shader'))
 if prog_sh in flat:v.append(f'program closure {prog_sh} overlaps flattened closure')
 program={prog_sh:{'shader':prog_sh,'visible_material_count':freq.get(prog_sh),'closure_kind':'EXACT_NATIVE_CFG_PROGRAM_PLUS_TERMINAL_REDUCTION','source':'8093E501_CFG_PROGRAM_PROOF'}}

 closed=set(flat)|set(program);expected=set(freq)
 missing=sorted(expected-closed);extra=sorted(closed-expected)
 if missing:v.append(f'unclosed common shader families {missing}')
 if extra:v.append(f'closure rows outside common corpus {extra}')
 flat_weight=sum(freq.get(x,0) for x in flat);program_weight=sum(freq.get(x,0) for x in program)
 if len(flat)!=64:v.append(f'flattened family count {len(flat)} != 64')
 if flat_weight!=98:v.append(f'flattened visible-material weight {flat_weight} != 98')
 if len(program)!=1 or program_weight!=1:v.append(f'program closure count/weight {len(program)}/{program_weight} != 1/1')

 out={'schema':'d1_tower_common_terminal_closure/v1',
      'status':'D1_TOWER_COMMON_TERMINAL_BEHAVIOR_CLOSED' if not v and closed==expected else 'D1_TOWER_COMMON_TERMINAL_BEHAVIOR_PARTIAL',
      'total_shader_family_count':len(freq),'total_visible_material_count':sum(freq.values()),
      'flattened_terminal_equation_family_count':len(flat),'flattened_terminal_equation_visible_material_count':flat_weight,
      'exact_cfg_program_family_count':len(program),'exact_cfg_program_visible_material_count':program_weight,
      'terminal_behavior_closed_family_count':len(closed),'terminal_behavior_closed_visible_material_count':sum(freq.get(x,0) for x in closed),
      'flattened_terminal_equation_fraction':len(flat)/len(freq) if freq else None,
      'terminal_behavior_closed_fraction':len(closed)/len(freq) if freq else None,
      'flattened_rows':[flat[x] for x in sorted(flat,key=lambda h:(-freq[h],h))],
      'program_rows':[program[x] for x in sorted(program)],
      'missing_families':missing,'violations':v,
      'semantic_boundary':{
       '64_flattened_equations':'EXACT_TERMINAL_OPERATION_STRUCTURE',
       '8093E501':'EXACT_NATIVE_CFG_PROGRAM_PLUS_EXACT_TERMINAL_REDUCTION_NOT_FLATTENED',
       'resource_and_cbuffer_identity':'EXACT',
       'runtime_global_producers_and_live_values':'WITHHELD_WHERE_NOT_SOURCE_CLOSED',
       'human_material_roles':'SEPARATE_EVIDENCE_LAYER',
       'portable_renderer_equivalence':'NOT_IMPLIED'},
      'policy':'All 65 common families have exact terminal behavior closure, but only 64 are flattened equations. 8093E501 remains an exact replayable native CFG program because flattening its iterative loop would weaken evidence.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'flattened_families':len(flat),'flattened_visible':flat_weight,'program_families':len(program),'program_visible':program_weight,'closed_families':len(closed),'closed_visible':out['terminal_behavior_closed_visible_material_count'],'missing':missing,'violations':v},indent=2))
 return 0 if out['status']=='D1_TOWER_COMMON_TERMINAL_BEHAVIOR_CLOSED' else 2
if __name__=='__main__':raise SystemExit(main())
