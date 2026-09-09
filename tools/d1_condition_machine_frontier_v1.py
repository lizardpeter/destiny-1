#!/usr/bin/env python3
"""Fail-closed exact condition-mask/SCC census for the D1 structural IR corpus."""
from __future__ import annotations
import argparse, collections, hashlib, json, re
from pathlib import Path
import d1_condition_machine_semantics_v1 as sem

SCHEMA='d1_gcn_condition_machine_frontier/v1'
STATUS='D1_GCN_CONDITION_MACHINE_FRONTIER_EXACT'
EXPECTED_PROGRAMS=26464
EXPECTED_INSTRUCTIONS=4896165
EXPECTED={
 'compare_instruction_count':115023,
 'compare_vcc_destination_count':101601,
 'compare_sgpr_pair_destination_count':13422,
 'carry_instruction_count':11521,
 'carry_vcc_destination_count':11521,
 'carry_sgpr_pair_destination_count':0,
 'cndmask_instruction_count':114066,
 'cndmask_vcc_predicate_count':110902,
 'cndmask_sgpr_pair_predicate_count':3164,
 'scc_producer_instruction_count':55835,
 'scc_branch_consumer_count':1840,
 'vcc_branch_consumer_count':300,
 'vcc_half_write_count':26464,
 'structural_explicit_scc_def_count':0,
}
PAIR_RE=re.compile(r'^s\[(\d+):(\d+)\]$')

def pair_key(x):
 m=PAIR_RE.fullmatch(x or '')
 if not m:return None
 a,b=map(int,m.groups())
 return x if b==a+1 else None

def sha256_file(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()

def build(ir_dir:Path):
 violations=[];paths=sorted(ir_dir.glob('*.json'))
 if len(paths)!=EXPECTED_PROGRAMS:violations.append(f'ir_file_count:{len(paths)}!={EXPECTED_PROGRAMS}')
 c=collections.Counter();cmp_ops=collections.Counter();scc_ops=collections.Counter();scalar_mask=collections.Counter()
 cmp_dests=collections.Counter();carry_dests=collections.Counter();cnd_preds=collections.Counter();examples={}
 total_ins=0;program_rows=[]
 def ex(key,sha,x):
  if key not in examples:examples[key]={'gcn_sha256':sha,'instruction':x['index'],'address':x['address_hex'],'opcode':x['opcode'],'operands':x.get('operands') or []}
 for p in paths:
  sha=p.stem.lower();d=json.loads(p.read_text());ins=d.get('instructions') or []
  total_ins+=len(ins);pt=collections.Counter()
  if d.get('status')!='D1_GCN_STRUCTURAL_IR_COMPLETE':violations.append(f'ir_status:{sha}:{d.get("status")!r}')
  if (d.get('parse_accounting') or {}).get('status')!='D1_GCN_STRUCTURAL_PARSE_ACCOUNTING_EXACT':violations.append(f'parse_status:{sha}')
  for x in ins:
   op=x['opcode'];a=x.get('operands') or []
   if op.startswith('v_cmp'):
    if op not in sem.COMPARES:violations.append(f'unregistered_compare:{sha}:{x["index"]}:{op}')
    if len(a)<3:violations.append(f'compare_operands:{sha}:{x["index"]}:{a!r}');continue
    dst=a[0];cmp_ops[op]+=1;c['compare_instruction_count']+=1;cmp_dests[dst]+=1;pt['compare']+=1;ex(('cmp',dst),sha,x)
    if dst=='vcc':c['compare_vcc_destination_count']+=1
    elif pair_key(dst):c['compare_sgpr_pair_destination_count']+=1
    else:violations.append(f'compare_bad_destination:{sha}:{x["index"]}:{dst}')
   if op in sem.CARRY:
    if len(a)<4:violations.append(f'carry_operands:{sha}:{x["index"]}:{a!r}');continue
    dst=a[1];carry_dests[dst]+=1;c['carry_instruction_count']+=1;pt['carry']+=1;ex(('carry',dst),sha,x)
    if dst=='vcc':c['carry_vcc_destination_count']+=1
    elif pair_key(dst):c['carry_sgpr_pair_destination_count']+=1
    else:violations.append(f'carry_bad_destination:{sha}:{x["index"]}:{dst}')
   if op=='v_cndmask_b32':
    if len(a)<4:violations.append(f'cndmask_operands:{sha}:{x["index"]}:{a!r}');continue
    pred=a[3];cnd_preds[pred]+=1;c['cndmask_instruction_count']+=1;pt['cndmask']+=1;ex(('cnd',pred),sha,x)
    if pred=='vcc':c['cndmask_vcc_predicate_count']+=1
    elif pair_key(pred):c['cndmask_sgpr_pair_predicate_count']+=1
    else:violations.append(f'cndmask_bad_predicate:{sha}:{x["index"]}:{pred}')
   if op in sem.SCC_PRODUCERS:scc_ops[op]+=1;c['scc_producer_instruction_count']+=1;pt['scc_producer']+=1
   if op=='s_cbranch_scc0':c['scc_branch_consumer_count']+=1;pt['scc_branch']+=1
   if op in {'s_cbranch_vccz','s_cbranch_vccnz'}:c['vcc_branch_consumer_count']+=1;pt['vcc_branch']+=1
   if op in sem.SCALAR_MASK:scalar_mask[op]+=1;c['scalar_mask_transform_instruction_count']+=1
   if op=='s_mov_b32' and a and a[0] in ('vcc_lo','vcc_hi'):
    c['vcc_half_write_count']+=1;pt['vcc_half_write']+=1
    if a[0]!='vcc_hi':violations.append(f'unexpected_vcc_half:{sha}:{x["index"]}:{a[0]}')
   if 'scc' in (x.get('defs') or []):c['structural_explicit_scc_def_count']+=1
   if op.startswith('s_cbranch_scc') and op not in sem.CONSUMERS:violations.append(f'unregistered_scc_branch:{sha}:{x["index"]}:{op}')
   if op.startswith('s_cbranch_vcc') and op not in sem.CONSUMERS:violations.append(f'unregistered_vcc_branch:{sha}:{x["index"]}:{op}')
  program_rows.append({'gcn_sha256':sha,'instruction_count':len(ins),'condition_counts':dict(sorted(pt.items()))})
 if total_ins!=EXPECTED_INSTRUCTIONS:violations.append(f'instruction_count:{total_ins}!={EXPECTED_INSTRUCTIONS}')
 for k,w in EXPECTED.items():
  if c[k]!=w:violations.append(f'{k}:{c[k]}!={w}')
 # Materialize expected zero-valued counters in the durable coverage ledger.
 # Counter lookups above already proved their exact value; omitting a zero key from
 # JSON makes downstream fail-closed consumers unable to distinguish proved-zero
 # from missing/unmeasured.
 for k in EXPECTED:
  c.setdefault(k,0)
 if dict(cmp_ops)!=dict(collections.Counter({op:0 for op in []})+cmp_ops):pass
 if set(cmp_ops)!=set(sem.COMPARES):violations.append(f'compare_opcode_set:{sorted(cmp_ops)}')
 if set(scc_ops)!=set(sem.SCC_PRODUCERS):violations.append(f'scc_opcode_set:{sorted(scc_ops)}')
 if set(cnd_preds)-({'vcc'}|{k for k in cnd_preds if pair_key(k)}):violations.append('cndmask_nonmask_predicate_present')
 return {
  'schema':SCHEMA,'status':STATUS if not violations else 'D1_GCN_CONDITION_MACHINE_FRONTIER_WITH_VIOLATIONS',
  'sources':{'ir_dir':str(ir_dir),'semantics_status':sem.STATUS},
  'coverage':{'exact_program_count':len(paths),'exact_instruction_count':total_ins,**dict(sorted(c.items())),
              'compare_opcode_counts':dict(sorted(cmp_ops.items())),'scc_producer_opcode_counts':dict(sorted(scc_ops.items())),
              'scalar_mask_opcode_counts':dict(sorted(scalar_mask.items())),
              'compare_destination_counts':dict(sorted(cmp_dests.items())),'carry_destination_counts':dict(sorted(carry_dests.items())),
              'cndmask_predicate_counts':dict(sorted(cnd_preds.items())),'shader_expression_semantic_promotions':0},
  'examples':[{'role':k[0],'mask':k[1],**v} for k,v in sorted(examples.items())],
  'programs':program_rows,'violations':violations,
  'semantic_boundary':{'condition_mask_machine_semantics':'SOURCE_CLOSED','scc_machine_semantics':'SOURCE_CLOSED','condition_symbolic_dataflow':'NEXT_GATE','lane_aware_vgpr_ssa':'WITHHELD','shader_expression_semantics':'WITHHELD','shader_expression_semantic_promotions':0},
  'policy':'Every compare/carry mask producer, CNDMASK predicate, VCC/SCC branch consumer and source-closed SCC producer in the exact corpus is admitted explicitly. Arbitrary SGPR-pair condition masks are first-class; VCC is not assumed to be the only predicate mask.'
 }

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--ir-dir',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args();out=build(a.ir_dir);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':out['status'],'coverage':out['coverage'],'violation_count':len(out['violations'])},indent=2));return 0 if not out['violations'] else 2
if __name__=='__main__':raise SystemExit(main())
