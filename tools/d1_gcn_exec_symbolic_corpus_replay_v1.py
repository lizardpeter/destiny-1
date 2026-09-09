#!/usr/bin/env python3
"""Replay exact EXEC symbolic dataflow across every D1 PS/VS/DS structural IR."""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path

import d1_gcn_exec_symbolic_dataflow_v1 as sym
import d1_gcn_exec_mask_machine_frontier_v1 as frontier

STAGE_LEDGER_STATUS="D1_GCN_EFFECT_IR_V3_GLOBAL_REPLAY_EXACT"
EXEC_STATUS="D1_GCN_EXEC_MASK_OPCODE_FRONTIER_EXACT"
OUTPUT_SCHEMA="d1_gcn_exec_symbolic_corpus_replay/v1"
OUTPUT_STATUS="D1_GCN_EXEC_SYMBOLIC_CORPUS_REPLAY_EXACT"
EXPECTED_PROGRAMS=26464
EXPECTED_INSTRUCTIONS=4896165
EXPECTED_BLOCKS=68622
EXPECTED_EDGES=51073
EXPECTED_EXPLICIT_EXEC=109678
EXPECTED_IMPLICIT_CMPX=12
EXPECTED_EXEC_TRANSITIONS=73607
EXPECTED_EXEC_BRANCHES=14828
EXPECTED_MACHINE_EXEC_OPCODES=frontier.EXPECTED_OPCODES
EXPECTED_EXEC_PROGRAMS=18521
EXPECTED_STAGE_COUNTS={"DS":20,"PS":18375,"VS":8069}
EXPECTED_EXEC_STAGE_COUNTS={"PS":17807,"VS":714}


def sha256_file(p:Path)->str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()


def _analyze_path(path_str: str):
 p=Path(path_str);sha=p.stem.lower()
 try:
  d=sym.analyze(json.loads(p.read_text()))
  return {
   "ok":not bool(d["violations"]),"sha":sha,"violations":d["violations"][:5],
   "instruction_count":d["instruction_count"],"basic_block_count":d["basic_block_count"],"edge_count":d["concrete_cfg_edge_count"],
   "explicit_exec":d["explicit_structural_exec_touch_count"],"implicit_cmpx":d["implicit_cmpx_exec_touch_count"],
   "exec_transitions":d["exec_transition_count"],"exec_branches":d["exec_branch_predicate_count"],
   "node_count":d["node_count"],"phi_count":d["phi_node_count"],"orphan_blocks":d["unresolved_control_entry_block_count"],
   "opaque_pairs":d["opaque_pair_write_count"],"opaque_vcc":d["opaque_vcc_write_count"],"opaque_scc":d["opaque_scc_write_count"],
   "opcounts":d["exact_machine_exec_opcode_counts"],"tracked_pair_count":len(d["tracked_sgpr_pairs"]),
  }
 except Exception as exc:
  return {"ok":False,"sha":sha,"exception":f"{type(exc).__name__}:{exc}"}


def replay(ir_dir:Path,stage_ledger_path:Path,exec_frontier_path:Path,workers:int=1)->dict:
 violations=[]
 ledger=json.loads(stage_ledger_path.read_text()); ex=json.loads(exec_frontier_path.read_text())
 if ledger.get('status')!=STAGE_LEDGER_STATUS:violations.append(f"stage_ledger_status:{ledger.get('status')!r}")
 if ledger.get('violations'):violations.append(f"stage_ledger_violations:{len(ledger['violations'])}")
 if ex.get('status')!=EXEC_STATUS:violations.append(f"exec_status:{ex.get('status')!r}")
 if ex.get('violations'):violations.append(f"exec_violations:{len(ex['violations'])}")
 stages={p['gcn_sha256']:[p['stage']] for p in ledger.get('programs') or []}
 if len(stages)!=EXPECTED_PROGRAMS:violations.append(f"stage_ledger_program_map:{len(stages)}!={EXPECTED_PROGRAMS}")
 explicit_programs={p['gcn_sha256'] for p in ex.get('programs') or []}
 paths=sorted(ir_dir.glob('*.json'))
 if len(paths)!=EXPECTED_PROGRAMS:violations.append(f"ir_file_count:{len(paths)}!={EXPECTED_PROGRAMS}")

 totals=collections.Counter(); opcounts=collections.Counter(); stage_counts=collections.Counter(); exec_stage_counts=collections.Counter()
 program_rows=[]; failed=0
 iterator=map(_analyze_path,(str(p) for p in paths))
 if workers>1:
  pool=mp.Pool(processes=workers)
  iterator=pool.imap_unordered(_analyze_path,(str(p) for p in paths),chunksize=16)
 try:
  for r in iterator:
   sha=r["sha"];st=stages.get(sha)
   if st is None:
    violations.append(f"missing_stage_roster:{sha}");failed+=1;continue
   if len(st)!=1:
    violations.append(f"non_single_stage_program:{sha}:{st}");failed+=1;continue
   stage=st[0];stage_counts[stage]+=1
   if not r.get("ok"):
    violations.append(f"analyze_failed:{sha}:{r.get('exception') or r.get('violations')}");failed+=1;continue
   totals.update({
    'programs':1,'instructions':r['instruction_count'],'blocks':r['basic_block_count'],'edges':r['edge_count'],
    'explicit_exec':r['explicit_exec'],'implicit_cmpx':r['implicit_cmpx'],'exec_transitions':r['exec_transitions'],'exec_branches':r['exec_branches'],
    'nodes':r['node_count'],'phis':r['phi_count'],'orphan_blocks':r['orphan_blocks'],'opaque_pairs':r['opaque_pairs'],
    'opaque_vcc':r['opaque_vcc'],'opaque_scc':r['opaque_scc'],
   })
   opcounts.update(r['opcounts'])
   is_exec=bool(r['explicit_exec'] or r['implicit_cmpx'])
   if is_exec:exec_stage_counts[stage]+=1
   if bool(r['explicit_exec']) != (sha in explicit_programs): violations.append(f"explicit_exec_program_roster_mismatch:{sha}")
   program_rows.append({
    'gcn_sha256':sha,'stage':stage,'instruction_count':r['instruction_count'],'basic_block_count':r['basic_block_count'],
    'exec_touch_count':r['explicit_exec']+r['implicit_cmpx'],'exec_transition_count':r['exec_transitions'],
    'exec_branch_predicate_count':r['exec_branches'],'tracked_sgpr_pair_count':r['tracked_pair_count'],
    'node_count':r['node_count'],'phi_node_count':r['phi_count'],'unresolved_control_entry_block_count':r['orphan_blocks'],
   })
 finally:
  if workers>1:
   pool.close();pool.join()
 program_rows.sort(key=lambda x:x['gcn_sha256'])

 checks={
  'programs':EXPECTED_PROGRAMS,'instructions':EXPECTED_INSTRUCTIONS,'blocks':EXPECTED_BLOCKS,'edges':EXPECTED_EDGES,
  'explicit_exec':EXPECTED_EXPLICIT_EXEC,'implicit_cmpx':EXPECTED_IMPLICIT_CMPX,
  'exec_transitions':EXPECTED_EXEC_TRANSITIONS,'exec_branches':EXPECTED_EXEC_BRANCHES,
 }
 for k,v in checks.items():
  if totals[k]!=v:violations.append(f"{k}:{totals[k]}!={v}")
 if dict(sorted(opcounts.items()))!=dict(sorted(EXPECTED_MACHINE_EXEC_OPCODES.items())):
  violations.append(f"machine_exec_opcode_histogram:{dict(sorted(opcounts.items()))!r}")
 if dict(sorted(stage_counts.items()))!=EXPECTED_STAGE_COUNTS:violations.append(f"stage_counts:{dict(stage_counts)!r}")
 if dict(sorted(exec_stage_counts.items()))!=EXPECTED_EXEC_STAGE_COUNTS:violations.append(f"exec_stage_counts:{dict(exec_stage_counts)!r}")
 if sum(exec_stage_counts.values())!=EXPECTED_EXEC_PROGRAMS:violations.append(f"exec_programs:{sum(exec_stage_counts.values())}!={EXPECTED_EXEC_PROGRAMS}")
 if len(program_rows)!=EXPECTED_PROGRAMS:violations.append(f"successful_programs:{len(program_rows)}!={EXPECTED_PROGRAMS}")

 return {
  'schema':OUTPUT_SCHEMA,'status':OUTPUT_STATUS if not violations else 'D1_GCN_EXEC_SYMBOLIC_CORPUS_REPLAY_WITH_VIOLATIONS',
  'sources':{
   'ir_dir':str(ir_dir),'stage_ledger':str(stage_ledger_path),'stage_ledger_sha256':sha256_file(stage_ledger_path),
   'exec_frontier':str(exec_frontier_path),'exec_frontier_sha256':sha256_file(exec_frontier_path),
  },
  'coverage':{
   'exact_programs_replayed':totals['programs'],'exact_instructions_replayed':totals['instructions'],
   'effect_aware_basic_block_count':totals['blocks'],'concrete_cfg_edge_count':totals['edges'],
   'explicit_structural_exec_instruction_count':totals['explicit_exec'],'implicit_cmpx_exec_instruction_count':totals['implicit_cmpx'],
   'exec_transition_count':totals['exec_transitions'],'exec_branch_predicate_count':totals['exec_branches'],
   'machine_exec_opcode_counts':dict(sorted(opcounts.items())),'stage_program_counts':dict(sorted(stage_counts.items())),
   'exec_touching_stage_program_counts':dict(sorted(exec_stage_counts.items())),'exec_touching_program_count':sum(exec_stage_counts.values()),
   'symbolic_node_count':totals['nodes'],'cfg_phi_node_count':totals['phis'],
   'unresolved_control_entry_block_count':totals['orphan_blocks'],'opaque_pair_write_count':totals['opaque_pairs'],
   'opaque_vcc_write_count':totals['opaque_vcc'],'opaque_scc_write_count':totals['opaque_scc'],
   'shader_expression_semantic_promotions':0,
  },
  'programs':program_rows,'violations':violations,
  'semantic_boundary':{
   'exec_machine_semantics':'SOURCE_CLOSED','symbolic_exec_provenance':'GLOBAL_EXACT',
   'branch_feasibility':'WITHHELD','indirect_pc_targets':'WITHHELD','lane_aware_vgpr_ssa':'NEXT_GATE',
   'shader_expression_semantics':'WITHHELD','shader_expression_semantic_promotions':0,
  },
  'policy':'All 26,464 exact programs are replayed through the same path-aware symbolic EXEC analysis. Exact mask transitions and branch predicates are preserved as graph nodes; opaque mask values remain explicit boundaries. No branch feasibility, indirect target, lane-value SSA, or shader meaning is invented.'
 }


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--ir-dir',type=Path,required=True);ap.add_argument('--stage-ledger',type=Path,required=True);ap.add_argument('--exec-frontier',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True);ap.add_argument('--workers',type=int,default=max(1,min(4,os.cpu_count() or 1)));a=ap.parse_args()
 out=replay(a.ir_dir,a.stage_ledger,a.exec_frontier,a.workers);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'status':out['status'],'coverage':out['coverage'],'violation_count':len(out['violations'])},indent=2))
 for x in out['violations'][:100]:print('VIOLATION',x)
 return 0 if not out['violations'] else 2
if __name__=='__main__':raise SystemExit(main())
