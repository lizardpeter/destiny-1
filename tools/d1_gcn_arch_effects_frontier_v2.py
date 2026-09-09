#!/usr/bin/env python3
"""Prove all 67 exact baseline-novel D1 GCN opcodes have source-closed GFX7 architectural effects."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import d1_gcn_arch_effects_v2 as arch

INPUT_SCHEMA='d1_gcn_opcode_structural_evidence_frontier/v1'
INPUT_STATUS='D1_GCN_OPCODE_STRUCTURAL_EVIDENCE_FRONTIER_EXACT'
OUTPUT_SCHEMA='d1_gcn_arch_effects_frontier/v2'
OUTPUT_STATUS='D1_GCN_ARCH_EFFECTS_ALL_67_FRONTIER_OPCODES_SOURCE_CLOSED_EXACT'
EXPECTED_OPCODE_COUNT=67
EXPECTED_OCCURRENCES=261733
EXPECTED_PROGRAMS=20199
EXPECTED_STAGE_PROGRAMS={'PS':12111,'VS':8068,'DS':20}


def sha256_file(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()


def build(path,expected_sha256=None):
 violations=[]; got=sha256_file(path)
 if expected_sha256 and got!=expected_sha256.lower():violations.append(f'input_sha256:{got}!={expected_sha256.lower()}')
 d=json.loads(path.read_text())
 if d.get('schema')!=INPUT_SCHEMA:violations.append(f"schema:{d.get('schema')!r}")
 if d.get('status')!=INPUT_STATUS:violations.append(f"status:{d.get('status')!r}")
 if d.get('violations'):violations.append(f"input_violations:{len(d['violations'])}")
 violations.extend('registry:'+x for x in arch.validate_registry())
 novel={x['opcode']:x for x in d.get('novel_opcodes') or []}
 if set(novel)!=set(arch.REGISTRY):
  violations.append(f"registry_frontier_set_mismatch:missing={sorted(set(novel)-set(arch.REGISTRY))}:extra={sorted(set(arch.REGISTRY)-set(novel))}")
 programs=set(); stages={'PS':set(),'VS':set(),'DS':set()}; occurrences=0; rows=[]; correction_totals={}
 prov=d.get('program_provenance') or {}
 for op in sorted(arch.REGISTRY,key=lambda x:(-int(novel.get(x,{}).get('instruction_count',0)),x)):
  src=novel.get(op)
  if not src:continue
  occurrences+=int(src['instruction_count']); programs.update(src.get('program_sha256') or [])
  for sha in src.get('program_sha256') or []:
   p=prov.get(sha)
   if not p:violations.append(f'missing_provenance:{op}:{sha}');continue
   st=p.get('stage')
   if st not in stages:violations.append(f'bad_stage:{op}:{sha}:{st!r}');continue
   stages[st].add(sha)
  e=arch.REGISTRY[op]; classes=set(); examples=[]
  for inst in src.get('examples') or []:
   ann=arch.annotate_instruction(inst); sd=list(inst.get('defs') or []); su=list(inst.get('uses') or [])
   if ann['architectural_defs']!=sd:classes.add('ARCHITECTURAL_DEFS_DIFFER')
   if ann['architectural_uses']!=su:classes.add('ARCHITECTURAL_USES_DIFFER')
   if e['control_flow']!='NONE':classes.add('ARCHITECTURAL_CONTROL_FLOW_EFFECT')
   if e['destination_write_scope']!='FULL_DESTINATION':classes.add('NONTRIVIAL_DESTINATION_WRITE_SCOPE')
   if e['memory_effect']!='NONE':classes.add('ARCHITECTURAL_MEMORY_EFFECT')
   if e['reads_old_destination']:classes.add('READ_MODIFY_WRITE_DESTINATION')
   examples.append({'gcn_sha256':inst.get('gcn_sha256'),'stage':inst.get('stage'),'address':inst.get('address'),'source_line':inst.get('source_line'),'encoding_hex':inst.get('encoding_hex'),'operands':inst.get('operands') or [],'structural_defs':sd,'structural_uses':su,'architectural_defs':ann['architectural_defs'],'architectural_uses':ann['architectural_uses']})
  for c in classes:correction_totals[c]=correction_totals.get(c,0)+1
  rows.append({'opcode':op,'instruction_count':int(src['instruction_count']),'program_count':int(src['program_count']),'stages':src.get('stages') or [],'architectural_status':e['architectural_status'],'shader_expression_status':e['shader_expression_status'],'family':e['family'],'execution_scope':e['execution_scope'],'exec_behavior':e['exec_behavior'],'memory_effect':e['memory_effect'],'control_flow':e['control_flow'],'destination_write_scope':e['destination_write_scope'],'implicit_reads':e['implicit_reads'],'implicit_writes':e['implicit_writes'],'reads_old_destination':e['reads_old_destination'],'operation':e['operation'],'source':e['source'],'structural_correction_classes':sorted(classes),'examples':examples})
 stage_counts={k:len(v) for k,v in stages.items()}
 if len(rows)!=EXPECTED_OPCODE_COUNT:violations.append(f'opcode_count:{len(rows)}!={EXPECTED_OPCODE_COUNT}')
 if occurrences!=EXPECTED_OCCURRENCES:violations.append(f'occurrences:{occurrences}!={EXPECTED_OCCURRENCES}')
 if len(programs)!=EXPECTED_PROGRAMS:violations.append(f'programs:{len(programs)}!={EXPECTED_PROGRAMS}')
 if stage_counts!=EXPECTED_STAGE_PROGRAMS:violations.append(f'stages:{stage_counts!r}!={EXPECTED_STAGE_PROGRAMS!r}')
 if any(x['shader_expression_status']!='UNPROVEN' for x in rows):violations.append('semantic_promotion_detected')
 hazards={
  's_addk_i32':{'ARCHITECTURAL_DEFS_DIFFER','ARCHITECTURAL_USES_DIFFER','READ_MODIFY_WRITE_DESTINATION'},
  's_lshl_b32':{'ARCHITECTURAL_DEFS_DIFFER'},'s_and_b32':{'ARCHITECTURAL_DEFS_DIFFER'},
  's_nand_b64':{'ARCHITECTURAL_DEFS_DIFFER'},'s_xor_b64':{'ARCHITECTURAL_DEFS_DIFFER'},
  'v_interp_mov_f32':{'ARCHITECTURAL_USES_DIFFER'},'v_movrels_b32':{'ARCHITECTURAL_USES_DIFFER'},
 }
 by={x['opcode']:set(x['structural_correction_classes']) for x in rows}
 for op,want in hazards.items():
  miss=want-by.get(op,set())
  if miss:violations.append(f'hazard_missing:{op}:{sorted(miss)}')
 return {'schema':OUTPUT_SCHEMA,'status':OUTPUT_STATUS if not violations else 'D1_GCN_ARCH_EFFECTS_FRONTIER_V2_WITH_VIOLATIONS','input':{'path':str(path),'sha256':got},'architectural_source':arch.AMD_SEA_ISLANDS,'coverage':{'exact_novel_opcode_count':len(novel),'exact_novel_opcode_instruction_occurrences':int((d.get('coverage') or {}).get('novel_opcode_instruction_occurrences',-1)),'source_closed_opcode_count':len(rows),'source_closed_opcode_instruction_occurrences':occurrences,'source_closed_novel_occurrence_ratio':occurrences/EXPECTED_OCCURRENCES,'source_closed_unique_programs':len(programs),'source_closed_stage_programs':stage_counts,'remaining_architecturally_unclosed_opcode_count':len(novel)-len(rows),'remaining_architecturally_unclosed_occurrences':EXPECTED_OCCURRENCES-occurrences,'shader_expression_semantic_promotions':0},'structural_correction_summary':dict(sorted(correction_totals.items())),'source_closed_opcodes':rows,'remaining_unclosed_opcodes':[],'violations':violations,'policy':'Every exact 808EE505-baseline-novel opcode has source-closed GFX7 architectural effects. This is machine-level closure only; shader-expression, resource-role, material and game semantics remain UNPROVEN.'}


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--evidence',type=Path,required=True);ap.add_argument('--expected-sha256');ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args();out=build(a.evidence,a.expected_sha256);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':out['status'],'coverage':out['coverage'],'structural_correction_summary':out['structural_correction_summary'],'violation_count':len(out['violations'])},indent=2));[print('VIOLATION',x) for x in out['violations'][:100]];return 0 if not out['violations'] else 2
if __name__=='__main__':raise SystemExit(main())
