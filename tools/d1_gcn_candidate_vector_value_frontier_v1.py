#!/usr/bin/env python3
"""Classify exact candidate VGPR-result instructions through the frozen universal value registry."""
from __future__ import annotations
import argparse, collections, json, re, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent; sys.path.insert(0,str(HERE))
import d1_gcn_vector_value_semantics_v1 as sem
import d1_gcn_vgpr_machine_semantics_v1 as machine
import d1_condition_machine_semantics_v1 as condition
import d1_gcn_shader_corpus_structural_census as census
from d1_gcn_shader_corpus_structural_census_v3 import fixed_reg_kind
VREG=re.compile(r'^v(\d+)$'); SCHEMA='d1_gcn_candidate_vector_value_frontier/v1'; STATUS='D1_GCN_CANDIDATE_VECTOR_VALUE_FRONTIER_EXACT'
def is_vgpr(r): return bool(VREG.fullmatch(r or ''))
def main()->int:
 ap=argparse.ArgumentParser(); ap.add_argument('--structural-source-closure',type=Path,required=True); ap.add_argument('--lane-ssa-report',type=Path,required=True); ap.add_argument('--ir-dir',type=Path,required=True); ap.add_argument('-o','--output',type=Path,required=True); a=ap.parse_args()
 sc=json.loads(a.structural_source_closure.read_text()); lr=json.loads(a.lane_ssa_report.read_text()); violations=[]; unresolved=[]
 if sc.get('status')!='D1_GCN_SOURCE_CLOSED_STRUCTURAL_PROMOTION_EXACT' or sc.get('violations'): violations.append('structural_source_closure_not_exact')
 if lr.get('status')!='D1_GCN_CANDIDATE_VGPR_LANE_SSA_REPLAY_EXACT' or lr.get('violations'): violations.append('lane_ssa_not_exact')
 violations += ['registry:'+x for x in sem.validate()]; expected={str(x.get('gcn_sha256','')).lower() for x in sc.get('programs') or []}; paths={p.stem.lower():p for p in a.ir_dir.glob('*.json')}
 if set(paths)!=expected: violations.append(f'ir_roster_mismatch:{len(paths)}!={len(expected)}')
 op=collections.Counter(); entries=collections.Counter(); cats=collections.Counter(); catentries=collections.Counter(); catprogs=collections.defaultdict(set); operand=collections.defaultdict(collections.Counter); kinds=collections.defaultdict(collections.Counter); widths=collections.defaultdict(collections.Counter); wb=collections.Counter(); roles=collections.Counter(); examples={}; total=0
 for sha in sorted(expected):
  p=paths.get(sha)
  if not p: continue
  d=json.loads(p.read_text()); ins=d.get('instructions') or []; total+=len(ins)
  for x in ins:
   vd=[r for r in (x.get('defs') or []) if is_vgpr(r)]
   if not vd: continue
   opc=x['opcode']; op[opc]+=1; entries[opc]+=len(vd); widths[opc][len(vd)]+=1
   if opc not in sem.OBSERVED or opc not in machine.VGPR_DEF_OPCODES:
    unresolved.append({'gcn_sha256':sha,'instruction':x['index'],'opcode':opc,'problem':'UNREGISTERED_VGPR_DEF_OPCODE'}); continue
   cat=sem.behavior(opc)['category']; cats[cat]+=1; catentries[cat]+=len(vd); catprogs[cat].add(sha); wb[machine.behavior(opc)['write_behavior']]+=1
   sig=tuple(census.normalized_operand(z) for z in (x.get('operands') or [])); k=tuple(fixed_reg_kind(z) for z in (x.get('uses') or [])); operand[opc][sig]+=1; kinds[opc][k]+=1
   rr=[]
   if opc in condition.CARRY: rr.append('CONDITION_CARRY_MASK_OUTPUT')
   if opc=='v_cndmask_b32': rr.append('CONDITION_MASK_INPUT')
   if opc=='v_movrels_b32': rr.append('M0_INDEXED_DYNAMIC_VGPR_SOURCE')
   if opc=='v_writelane_b32': rr.extend(['EXEC_BYPASS','SINGLE_LANE_DESTINATION_MUTATION'])
   if cat in {'IMAGE_RESOURCE_VALUE_OPAQUE','BUFFER_RESOURCE_VALUE_OPAQUE'}: rr.append('RESOURCE_VALUE_BOUNDARY')
   if cat=='DS_LDS_VALUE_OPAQUE': rr.append('LDS_DS_VALUE_BOUNDARY')
   if cat=='INTERPOLATION_VALUE_OPAQUE': rr.append('INTERPOLATION_VALUE_BOUNDARY')
   if not rr: rr=['NO_ADDITIONAL_MACHINE_ROLE_PROMOTED']
   roles.update(rr); key=(opc,sig,k,len(vd),tuple(rr)); examples.setdefault(key,{'gcn_sha256':sha,'instruction':x['index'],'address':x['address_hex'],'opcode':opc,'normalized_operands':list(sig),'use_kinds':list(k),'vgpr_result_component_count':len(vd),'category':cat,'write_behavior':machine.behavior(opc)['write_behavior'],'machine_roles':rr})
 if unresolved: violations.extend(f"unresolved:{x['gcn_sha256']}:{x['instruction']}:{x['opcode']}" for x in unresolved[:50])
 lc=lr.get('coverage') or {}
 if total!=lc.get('exact_instructions_replayed'): violations.append(f'instructions:{total}!={lc.get("exact_instructions_replayed")}')
 if sum(op.values())!=lc.get('vgpr_def_instruction_count'): violations.append(f'vgpr_defs:{sum(op.values())}!={lc.get("vgpr_def_instruction_count")}')
 if sum(entries.values())!=lc.get('vgpr_def_entry_count'): violations.append(f'vgpr_def_entries:{sum(entries.values())}!={lc.get("vgpr_def_entry_count")}')
 if not set(op)<=sem.OBSERVED: violations.append('candidate_opcode_surface_outside_registry')
 def forms(src): return {o:[{'signature':list(s) if isinstance(s,tuple) else s,'count':n} for s,n in sorted(c.items(),key=lambda kv:str(kv[0]))] for o,c in sorted(src.items())}
 cov={'exact_program_count':len(expected),'exact_instruction_count':total,'vgpr_def_instruction_count':sum(op.values()),'vgpr_def_entry_count':sum(entries.values()),'vgpr_def_opcode_count':len(op),'opcode_instruction_counts':dict(sorted(op.items())),'opcode_def_entry_counts':dict(sorted(entries.items())),'category_instruction_counts':dict(sorted(cats.items())),'category_def_entry_counts':dict(sorted(catentries.items())),'category_program_counts':{k:len(v) for k,v in sorted(catprogs.items())},'operand_form_count':sum(len(v) for v in operand.values()),'use_kind_form_count':sum(len(v) for v in kinds.values()),'def_width_form_count':sum(len(v) for v in widths.values()),'write_behavior_instruction_counts':dict(sorted(wb.items())),'machine_role_instruction_counts':dict(sorted(roles.items())),'candidate_vgpr_opcode_surface_is_registry_subset':set(op)<=sem.OBSERVED,'shader_expression_semantic_promotions':0}
 out={'schema':SCHEMA,'status':STATUS if not violations else 'D1_GCN_CANDIDATE_VECTOR_VALUE_FRONTIER_WITH_VIOLATIONS','source_registry':sem.document(),'coverage':cov,'operand_forms_by_opcode':forms(operand),'structural_use_kinds_by_opcode':forms(kinds),'vgpr_result_widths_by_opcode':{o:[{'component_count':w,'instruction_count':n} for w,n in sorted(c.items())] for o,c in sorted(widths.items())},'examples':[v for _,v in sorted(examples.items(),key=lambda kv:str(kv[0]))],'unresolved':unresolved,'violations':violations,'semantic_boundary':{'lane_aware_vgpr_ssa':'EXACT_PREREQUISITE','candidate_vgpr_opcode_surface':'SOURCE_CLOSED_REGISTRY_SUBSET' if not violations else 'WITHHELD','resource_lds_interpolation_values':'EXPLICIT_OPAQUE_BOUNDARIES','per_opcode_valu_formula_semantics':'NEXT_GATE' if not violations else 'WITHHELD','shader_expression_semantic_promotions':0},'policy':'Candidate VGPR definitions use the exact same conservative universal value registry as the global corpus. Missing global opcodes are allowed; any candidate opcode outside the registry fails closed. No stage-specific value semantics are introduced.'}
 a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print('STATUS',out['status'],'PROGRAMS',len(expected),'INSTRUCTIONS',total,'VGPR_DEFS',sum(op.values()),'OPCODES',len(op),'FORMULA_PENDING',cats['VALU_FORMULA_PENDING'],'VIOLATIONS',len(violations)); return 0 if not violations else 2
if __name__=='__main__': raise SystemExit(main())
