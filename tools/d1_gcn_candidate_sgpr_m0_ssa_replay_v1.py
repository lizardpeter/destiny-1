#!/usr/bin/env python3
"""Replay exact source-closed candidate programs through universal physical SGPR/M0 SSA."""
from __future__ import annotations
import argparse, collections, json, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent; sys.path.insert(0,str(HERE))
import d1_gcn_sgpr_ssa_v1 as scalar

STRUCT_SCHEMA='d1_gcn_source_closed_structural_promotion/v1'; STRUCT_STATUS='D1_GCN_SOURCE_CLOSED_STRUCTURAL_PROMOTION_EXACT'
RAW_SCHEMA='d1_gcn_structural_candidate_compare/v1'; SSA_STATUS='D1_GCN_SGPR_SSA_EXACT'
SCHEMA='d1_gcn_candidate_sgpr_m0_ssa_replay/v1'; STATUS='D1_GCN_CANDIDATE_SGPR_M0_SSA_REPLAY_EXACT'

def main()->int:
 ap=argparse.ArgumentParser(); ap.add_argument('--structural-source-closure',type=Path,required=True); ap.add_argument('--raw-replay',type=Path,required=True); ap.add_argument('--ir-dir',type=Path,required=True); ap.add_argument('--ssa-dir',type=Path); ap.add_argument('-o','--output',type=Path,required=True); a=ap.parse_args()
 sc=json.loads(a.structural_source_closure.read_text()); raw=json.loads(a.raw_replay.read_text())
 if sc.get('schema')!=STRUCT_SCHEMA or sc.get('status')!=STRUCT_STATUS or sc.get('violations'): raise SystemExit('exact structural source closure required')
 if raw.get('schema')!=RAW_SCHEMA: raise SystemExit('supported raw candidate replay required')
 sr={str(x.get('gcn_sha256','')).lower():x for x in sc.get('programs') or []}; rr={str(x.get('gcn_sha256','')).lower():x for x in raw.get('programs') or []}; planned=int((sc.get('coverage') or {}).get('architecture_admitted_unique_gcn_programs',-1))
 violations=[]
 if len(sr)!=planned: violations.append(f'structural_roster:{len(sr)}!={planned}')
 if set(sr)!=set(rr): violations.append('raw_structural_sha_roster_mismatch')
 if a.ssa_dir: a.ssa_dir.mkdir(parents=True,exist_ok=True)
 totals=collections.Counter(); stages=collections.Counter(); defops=collections.Counter(); defentries=collections.Counter(); useops=collections.Counter(); useentries=collections.Counter(); m0ops=collections.Counter(); rows=[]; exact=0; maxsgpr=-1
 for sha in sorted(sr):
  rraw=rr[sha]; st=sorted({str(x).upper() for x in (rraw.get('stages') or [])}); [stages.update([x]) for x in st]
  rec={'gcn_sha256':sha,'stages':st,'violations':[]}; ip=a.ir_dir/f'{sha}.json'
  if not ip.is_file(): rec['violations'].append('structural_ir_missing')
  else:
   try: ir=json.loads(ip.read_text()); d=scalar.analyze(ir)
   except Exception as e: rec['violations'].append(f'scalar_analyze:{type(e).__name__}:{e}'); d=None
   if d is not None:
    if d.get('status')!=SSA_STATUS or d.get('violations'): rec['violations'].append(f'scalar_status:{d.get("status")!r}:{(d.get("violations") or [])[:5]}')
    c=d.get('coverage') or {}
    if int(c.get('shader_expression_semantic_promotions',-1))!=0: rec['violations'].append(f'semantic_promotions:{c.get("shader_expression_semantic_promotions")}')
    if a.ssa_dir: (a.ssa_dir/f'{sha}.json').write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
    if not rec['violations']:
     exact+=1; totals['instructions']+=int(d.get('instruction_count',0)); totals['blocks']+=int(d.get('basic_block_count',0)); totals['edges']+=int(d.get('concrete_cfg_edge_count',0)); totals['nodes']+=len(d.get('nodes') or {})
     for k in ('tracked_scalar_register_count','entry_node_count','cfg_phi_node_count','unresolved_control_entry_block_count','unresolved_control_entry_scalar_node_count','non_scalar_source_leaf_count','sgpr_def_instruction_count','sgpr_def_entry_count','sgpr_use_instruction_count','sgpr_use_entry_count','whole_scalar_write_entry_count','whole_scalar_rmw_write_entry_count','exec_gated_mask_half_write_entry_count','scalar_result_component_node_count','implicit_rmw_use_entry_count','implicit_m0_use_instruction_count','shader_expression_semantic_promotions'): totals[k]+=int(c.get(k,0))
     m0defs=sum(1 for q in (d.get('instructions') or []) for w in (q.get('scalar_writes') or []) if w.get('register')=='m0'); totals['m0_def_instruction_count']+=m0defs
     maxsgpr=max(maxsgpr,int(c.get('max_tracked_sgpr_index',-1))); defops.update(c.get('sgpr_def_opcode_counts') or {}); defentries.update(c.get('sgpr_def_entry_opcode_counts') or {}); useops.update(c.get('sgpr_use_opcode_counts') or {}); useentries.update(c.get('sgpr_use_entry_opcode_counts') or {}); m0ops.update(c.get('implicit_m0_use_opcode_counts') or {})
     rec.update({'tracked_scalar_register_count':c.get('tracked_scalar_register_count'),'max_tracked_sgpr_index':c.get('max_tracked_sgpr_index'),'node_count':len(d.get('nodes') or {}),'sgpr_def_entry_count':c.get('sgpr_def_entry_count'),'sgpr_use_entry_count':c.get('sgpr_use_entry_count'),'implicit_m0_use_instruction_count':c.get('implicit_m0_use_instruction_count')})
  if rec['violations']: violations.extend(f'{sha}:{x}' for x in rec['violations'])
  rows.append(rec)
 if totals['instructions']!=int((sc.get('coverage') or {}).get('instruction_count',-1)): violations.append('instruction_reconciliation_mismatch')
 if exact!=planned: violations.append(f'exact_programs:{exact}!={planned}')
 if totals['whole_scalar_write_entry_count']+totals['exec_gated_mask_half_write_entry_count']!=totals['sgpr_def_entry_count']: violations.append('write_partition_mismatch')
 if totals['scalar_result_component_node_count']!=totals['sgpr_def_entry_count']: violations.append('result_component_mismatch')
 if totals['shader_expression_semantic_promotions']!=0: violations.append('semantic_promotions_nonzero')
 coverage={'planned_unique_gcn_programs':planned,'exact_sgpr_m0_ssa_unique_gcn_programs':exact,'stage_program_counts':dict(sorted(stages.items())),'exact_instructions_replayed':totals['instructions'],'effect_aware_basic_block_count':totals['blocks'],'concrete_cfg_edge_count':totals['edges'],'scalar_ssa_node_count':totals['nodes'],'tracked_scalar_register_instances':totals['tracked_scalar_register_count'],'max_sgpr_index':maxsgpr,'program_entry_scalar_node_count':totals['entry_node_count'],'scalar_cfg_phi_node_count':totals['cfg_phi_node_count'],'unresolved_control_entry_block_count':totals['unresolved_control_entry_block_count'],'unresolved_control_entry_scalar_node_count':totals['unresolved_control_entry_scalar_node_count'],'non_scalar_source_leaf_count':totals['non_scalar_source_leaf_count'],'sgpr_def_instruction_count':totals['sgpr_def_instruction_count'],'sgpr_def_entry_count':totals['sgpr_def_entry_count'],'sgpr_use_instruction_count':totals['sgpr_use_instruction_count'],'sgpr_use_entry_count':totals['sgpr_use_entry_count'],'whole_scalar_write_entry_count':totals['whole_scalar_write_entry_count'],'whole_scalar_rmw_write_entry_count':totals['whole_scalar_rmw_write_entry_count'],'exec_gated_mask_half_write_entry_count':totals['exec_gated_mask_half_write_entry_count'],'scalar_result_component_node_count':totals['scalar_result_component_node_count'],'implicit_rmw_use_entry_count':totals['implicit_rmw_use_entry_count'],'m0_def_instruction_count':totals['m0_def_instruction_count'],'implicit_m0_use_instruction_count':totals['implicit_m0_use_instruction_count'],'sgpr_def_opcode_counts':dict(sorted(defops.items())),'sgpr_def_entry_opcode_counts':dict(sorted(defentries.items())),'sgpr_use_opcode_counts':dict(sorted(useops.items())),'sgpr_use_entry_opcode_counts':dict(sorted(useentries.items())),'implicit_m0_use_opcode_counts':dict(sorted(m0ops.items())),'shader_expression_semantic_promotions':totals['shader_expression_semantic_promotions']}
 out={'schema':SCHEMA,'status':STATUS if not violations else 'D1_GCN_CANDIDATE_SGPR_M0_SSA_REPLAY_WITH_VIOLATIONS','sources':{'structural_source_closure':str(a.structural_source_closure),'raw_replay':str(a.raw_replay),'ir_dir':str(a.ir_dir)},'coverage':coverage,'programs':rows,'violations':violations,'semantic_boundary':{'candidate_stage_affects_scalar_analyzer':False,'physical_sgpr_m0_ssa':'EXACT' if not violations else 'NOT_PROMOTED','implicit_m0_provenance':'EXACT' if not violations else 'NOT_PROMOTED','scalar_rmw_identity':'EXACT' if not violations else 'NOT_PROMOTED','opcode_result_value_semantics':'NEXT_GATE' if not violations else 'WITHHELD','shader_expression_semantics':'WITHHELD','shader_expression_semantic_promotions':0},'policy':'Every source-closed candidate program is replayed through the unchanged physical SGPR/M0 SSA analyzer. Its source-backed generic M0 classifier, not stage labels, determines implicit LDS/interpolation/relative-register dependencies. Scalar result expressions remain withheld.'}
 a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print('STATUS',out['status'],'PROGRAMS',f'{exact}/{planned}','INSTRUCTIONS',totals['instructions'],'NODES',totals['nodes'],'SGPR_DEFS',totals['sgpr_def_entry_count'],'M0_USES',totals['implicit_m0_use_instruction_count'],'VIOLATIONS',len(violations)); [print('VIOLATION',x) for x in violations[:100]]; return 0 if out['status']==STATUS else 2
if __name__=='__main__': raise SystemExit(main())
