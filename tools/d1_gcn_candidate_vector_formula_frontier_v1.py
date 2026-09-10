#!/usr/bin/env python3
"""Validate candidate VALU formulas using the frozen source-backed 50-opcode registry."""
from __future__ import annotations
import argparse, collections, json, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent; sys.path.insert(0,str(HERE))
import d1_gcn_vector_formula_semantics_v1 as sem
SCHEMA='d1_gcn_candidate_vector_formula_frontier/v1'; STATUS='D1_GCN_CANDIDATE_VECTOR_BASE_FORMULA_FRONTIER_EXACT'; SOURCE='d1_gcn_candidate_vector_value_frontier/v1'; SOURCE_STATUS='D1_GCN_CANDIDATE_VECTOR_VALUE_FRONTIER_EXACT'
def has_neg(s): return any(x.startswith('-') or ' -' in x for x in s)
def has_abs(s): return any('abs(' in x for x in s)
def has_clamp(s): return any('clamp' in x for x in s)
def has_omod(s): return any('mul:' in x or 'div:' in x for x in s)
def main()->int:
 ap=argparse.ArgumentParser(); ap.add_argument('--vector-frontier',type=Path,required=True); ap.add_argument('-o','--output',type=Path,required=True); a=ap.parse_args(); src=json.loads(a.vector_frontier.read_text()); violations=[]; unresolved=[]
 if src.get('schema')!=SOURCE or src.get('status')!=SOURCE_STATUS or src.get('violations'): violations.append('candidate_vector_frontier_not_exact')
 violations += ['registry:'+x for x in sem.validate()]
 cov=src.get('coverage') or {}; op_counts=cov.get('opcode_instruction_counts') or {}; widths=src.get('vgpr_result_widths_by_opcode') or {}; forms=src.get('operand_forms_by_opcode') or {}
 candidate_pending={op for op in op_counts if op in sem.PENDING}; outside={op for op in op_counts if op not in sem.PENDING and ((src.get('source_registry') or {}).get('opcode_behaviors') or {}).get(op,{}).get('category')=='VALU_FORMULA_PENDING'}
 if outside: violations.append(f'formula_registry_missing:{sorted(outside)}')
 fi=fc=0; bit_i=bit_c=0; mods=collections.Counter(); anymod=0; opmods=collections.defaultdict(collections.Counter); formcounts={}; classes=collections.Counter(); classinst=collections.Counter()
 for op in sorted(candidate_pending):
  ent=sem.FORMULAS.get(op)
  if ent is None: violations.append(f'formula_missing:{op}'); continue
  n=int(op_counts.get(op,0)); fi+=n; w=int(ent['result_components']); fc+=w*n; classes[ent['semantic_kind']]+=1; classinst[ent['semantic_kind']]+=n
  if op in sem.BIT_EXACT_REPLAY_READY: bit_i+=n; bit_c+=w*n
  gotw=widths.get(op)
  if gotw!=[{'component_count':w,'instruction_count':n}]: violations.append(f'result_width:{op}:{gotw}!={w}x{n}')
  rows=forms.get(op) or []; total=0; expected_arity=1+int(ent['explicit_source_count'])
  if not rows: violations.append(f'operand_forms_missing:{op}')
  for r in rows:
   sig=r.get('signature') or []; c=int(r.get('count',0)); total+=c
   if c<=0: violations.append(f'bad_form_count:{op}:{c}')
   if len(sig)!=expected_arity: violations.append(f'operand_arity:{op}:{sig}:{len(sig)}!={expected_arity}')
   flags={'NEG':has_neg(sig),'ABS':has_abs(sig),'CLAMP':has_clamp(sig),'OMOD':has_omod(sig)}
   if any(flags.values()): anymod+=c
   for k,on in flags.items():
    if on: mods[k]+=c; opmods[op][k]+=c
   if op in sem.BIT_EXACT_REPLAY_READY and any(flags.values()): unresolved.append({'opcode':op,'signature':sig,'count':c,'problem':'BIT_EXACT_READY_OPCODE_HAS_FP_MODIFIER'})
  formcounts[op]=len(rows)
  if total!=n: violations.append(f'operand_form_total:{op}:{total}!={n}')
 if unresolved: violations.extend(f"unresolved:{x['opcode']}:{x['problem']}" for x in unresolved[:50])
 out={'schema':SCHEMA,'status':STATUS if not violations else 'D1_GCN_CANDIDATE_VECTOR_BASE_FORMULA_FRONTIER_WITH_VIOLATIONS','source_vector_frontier':{'schema':src.get('schema'),'status':src.get('status')},'formula_registry':sem.document(),'coverage':{'exact_program_count':cov.get('exact_program_count'),'exact_instruction_count':cov.get('exact_instruction_count'),'candidate_formula_opcode_count':len(candidate_pending),'formula_instruction_count':fi,'formula_result_component_count':fc,'bit_exact_replay_ready_opcode_count':len(candidate_pending & sem.BIT_EXACT_REPLAY_READY),'bit_exact_replay_ready_instruction_count':bit_i,'bit_exact_replay_ready_result_component_count':bit_c,'floating_or_special_symbolic_opcode_count':len(candidate_pending-sem.BIT_EXACT_REPLAY_READY),'floating_or_special_symbolic_instruction_count':fi-bit_i,'operand_form_count':sum(formcounts.values()),'modifier_touched_instruction_count':anymod,'neg_modifier_instruction_count':mods['NEG'],'abs_modifier_instruction_count':mods['ABS'],'omod_modifier_instruction_count':mods['OMOD'],'clamp_modifier_instruction_count':mods['CLAMP'],'clamp_numeric_semantics_withheld_instruction_count':mods['CLAMP'],'semantic_kind_opcode_counts':dict(sorted(classes.items())),'semantic_kind_instruction_counts':dict(sorted(classinst.items())),'shader_expression_semantic_promotions':0},'candidate_formula_opcodes':sorted(candidate_pending),'modifier_instruction_counts_by_opcode':{op:dict(sorted(c.items())) for op,c in sorted(opmods.items())},'operand_form_counts_by_opcode':dict(sorted(formcounts.items())),'unresolved':unresolved,'violations':violations,'semantic_boundary':{'candidate_formula_opcode_surface':'SOURCE_CLOSED_50_OPCODE_REGISTRY_SUBSET' if not violations else 'WITHHELD','integer_bit_exact_subset':'READY_FOR_LANE_SSA_VALUE_NODE_REPLAY','floating_special_values':'SOURCE_CLOSED_SYMBOLIC_MODE_RETAINED','vop3_abs_neg_omod_order':'SOURCE_CLOSED','vop3_clamp_numeric_range':'WITHHELD_AMD_REV1_3_INTERNAL_SOURCE_CONFLICT','resource_lds_interpolation_values':'UNCHANGED_OPAQUE_BOUNDARIES','shader_expression_semantic_promotions':0},'policy':'Only formula opcodes present in this candidate are required, but every one must belong to the existing 50-opcode source-backed formula registry with exact result width and operand arity. Missing global opcodes are not errors; any candidate formula outside the registry fails closed. FP MODE and CLAMP uncertainty remain preserved.'}
 a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print('STATUS',out['status'],'FORMULA_OPCODES',len(candidate_pending),'FORMULA_INSTRUCTIONS',fi,'RESULT_COMPONENTS',fc,'BIT_EXACT',bit_i,'SYMBOLIC',fi-bit_i,'VIOLATIONS',len(violations)); return 0 if not violations else 2
if __name__=='__main__': raise SystemExit(main())
