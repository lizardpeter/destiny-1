#!/usr/bin/env python3
"""Path-aware general condition-mask + SCC SSA over exact D1 GCN structural IR.

VCC is treated as one 64-bit wave-mask carrier, not as the only predicate register.
Arbitrary SGPR pairs become typed mask carriers when compare/carry/CNDMASK or exact scalar
mask flow proves that role. Vector mask writes are merged under the exact EXEC-in mask,
so inactive lanes preserve their prior destination bits. SCC is reconstructed only from
source-closed Sea Islands instruction effects.
"""
from __future__ import annotations
import argparse, copy, json, re
from collections import Counter
from pathlib import Path
import d1_condition_machine_semantics_v1 as sem
import d1_gcn_exec_symbolic_dataflow_v1 as exec_sym

INPUT_STATUS='D1_GCN_STRUCTURAL_IR_COMPLETE'
INPUT_PARSE_STATUS='D1_GCN_STRUCTURAL_PARSE_ACCOUNTING_EXACT'
EXEC_STATUS='D1_GCN_EXEC_SYMBOLIC_DATAFLOW_EXACT'
SCHEMA='d1_gcn_condition_symbolic_dataflow/v1'
STATUS='D1_GCN_CONDITION_SYMBOLIC_DATAFLOW_EXACT'
PAIR_RE=re.compile(r'^s\[(\d+):(\d+)\]$')
SREG_RE=re.compile(r'^s(\d+)$')


def pair_key(x):
 if x=='vcc':return 'vcc'
 m=PAIR_RE.fullmatch(x or '')
 if not m:return None
 a,b=map(int,m.groups());return x if b==a+1 else None

def pair_halves(k):
 if k=='vcc':return ('vcc_lo','vcc_hi')
 m=PAIR_RE.fullmatch(k or '')
 if not m:return ()
 a,b=map(int,m.groups());return (f's{a}',f's{b}')

def half_of_operand(op, keys):
 if op in ('vcc_lo','vcc_hi'):return ('vcc',0 if op.endswith('_lo') else 1)
 m=SREG_RE.fullmatch(op or '')
 if not m:return None
 for k in keys:
  if k=='vcc':continue
  hs=pair_halves(k)
  if op in hs:return (k,hs.index(op))
 return None

def relevant_masks(ins):
 tracked={'vcc'}
 # Direct mask definitions/consumers type arbitrary SGPR pairs.
 for x in ins:
  op=x['opcode'];a=x.get('operands') or []
  if op in sem.COMPARES and a:
   k=pair_key(a[0]);
   if k:tracked.add(k)
  if op in sem.CARRY and len(a)>1:
   k=pair_key(a[1]);
   if k:tracked.add(k)
  if op=='v_cndmask_b32' and len(a)>3:
   k=pair_key(a[3]);
   if k:tracked.add(k)
  if op=='s_and_saveexec_b64' and a:
   k=pair_key(a[0]);
   if k:tracked.add(k)
 # Scalar 64-bit mask flow propagates mask typing both directions until stable.
 changed=True
 while changed:
  changed=False
  for x in ins:
   if x['opcode'] not in sem.SCALAR_MASK:continue
   a=x.get('operands') or []
   maskops=[pair_key(z) for z in a if pair_key(z)]
   if any(k in tracked for k in maskops):
    for k in maskops:
     if k and k not in tracked:tracked.add(k);changed=True
 return sorted(tracked,key=lambda k:(-1,-1) if k=='vcc' else tuple(map(int,PAIR_RE.fullmatch(k).groups())))

class Graph:
 def __init__(self):self.nodes={}
 def add(self,nid,kind,*,key=None,inputs=(),instruction=None,opcode=None,operands=None,exactness='SOURCE_CLOSED',detail=None):
  n={'id':nid,'kind':kind,'inputs':list(inputs),'exactness':exactness}
  if key is not None:n['key']=key
  if instruction is not None:n['instruction']=instruction
  if opcode is not None:n['opcode']=opcode
  if operands is not None:n['operands']=copy.deepcopy(operands)
  if detail is not None:n['detail']=detail
  old=self.nodes.get(nid)
  if old is not None and old!=n:raise ValueError(f'node identity collision {nid}')
  self.nodes[nid]=n;return nid

def analyze(v2):
 violations=[]
 if v2.get('status')!=INPUT_STATUS:raise ValueError(f'input status {v2.get("status")!r}')
 if (v2.get('parse_accounting') or {}).get('status')!=INPUT_PARSE_STATUS:raise ValueError('parse accounting not exact')
 ex=exec_sym.analyze(v2)
 if ex.get('status')!=EXEC_STATUS or ex.get('violations'):raise ValueError(f'EXEC prerequisite not exact:{ex.get("status")}:{ex.get("violations",[])[:3]}')
 ins=v2.get('instructions') or [];exrows=ex['instructions'];blocks=ex['blocks']
 if len(exrows)!=len(ins):raise ValueError('EXEC instruction roster mismatch')
 keys=relevant_masks(ins);state_keys=[*keys,'scc'];g=Graph()
 for k in state_keys:g.add(f'entry:{k}','PROGRAM_ENTRY',key=k,exactness='SYMBOLIC_INPUT')
 entry={}
 for b in blocks:
  bid=b['id'];entry[bid]={}
  for k in state_keys:
   if bid==0:entry[bid][k]=f'entry:{k}'
   elif b['predecessors']:
    nid=f'phi:b{bid}:{k}';entry[bid][k]=nid;g.add(nid,'CFG_PHI',key=k,exactness='CFG_EXACT')
   else:
    nid=f'external:b{bid}:{k}';entry[bid][k]=nid;g.add(nid,'UNRESOLVED_CONTROL_ENTRY',key=k,exactness='CONTROL_TARGET_UNRESOLVED')
 rows=[None]*len(ins);block_exit={};counts=Counter();mask_opcounts=Counter();scc_opcounts=Counter()

 def exec_ref(idx):
  r=exrows[idx];nid=f'exec_ref:i{idx}:in';return g.add(nid,'EXEC_CHECKPOINT_REFERENCE',inputs=(),instruction=idx,exactness='GLOBAL_EXEC_EXACT',detail=r['exec_in'])
 def exec_out_ref(idx):
  r=exrows[idx];nid=f'exec_ref:i{idx}:out';return g.add(nid,'EXEC_CHECKPOINT_REFERENCE',inputs=(),instruction=idx,exactness='GLOBAL_EXEC_EXACT',detail=r['exec_out'])
 def leaf(idx,val):return g.add(f'leaf:i{idx}:{val}','OPERAND_VALUE',detail=val,exactness='VALUE_UNINTERPRETED')
 def mask_value(state,idx,val):
  k=pair_key(val)
  if k and k in state:return state[k]
  if val=='exec':return exec_ref(idx)
  return leaf(idx,val)
 def scalar_result(idx,x,kind=None):
  a=x.get('operands') or [];srcs=[leaf(idx,z) for z in a[1:]]
  return g.add(f'i{idx}:scalar_result',kind or 'SCALAR_RESULT',inputs=srcs,instruction=idx,opcode=x['opcode'],operands=a,exactness='SOURCE_CLOSED_OPERATION_VALUE_SYMBOLIC',detail=x['opcode'])
 def write_half(state,idx,x,key,half,value_node,exactness='SOURCE_CLOSED'):
  old=state[key];nid=f'i{idx}:{key}'
  g.add(nid,'MASK_HALF_WRITE',key=key,inputs=(old,value_node),instruction=idx,opcode=x['opcode'],operands=x.get('operands') or [],exactness=exactness,detail={'half':half})
  state[key]=nid;counts['mask_half_write_count']+=1;return nid

 for b in blocks:
  state=dict(entry[b['id']])
  for ii in range(b['start_instruction'],b['end_instruction']+1):
   x=ins[ii];idx=x['index'];op=x['opcode'];a=x.get('operands') or [];er=exrows[idx]
   if idx!=ii:violations.append(f'instruction_index:{ii}:{idx}')
   row={'instruction':idx,'address':x['address_hex'],'opcode':op,'mask_definition':None,'mask_use':None,'scc_definition':None,'scc_use':None,'exec_in_reference':er['exec_in']}
   handled_full=set();handled_halves=set()

   if op in sem.COMPARES:
    if len(a)<3:violations.append(f'compare_operands:{idx}:{a!r}')
    else:
     dk=pair_key(a[0])
     if dk not in state:violations.append(f'compare_untracked_dest:{idx}:{a[0]}')
     else:
      e=exec_ref(idx);old=state[dk];cond=g.add(f'i{idx}:condition','VECTOR_COMPARE_CONDITION',inputs=tuple(leaf(idx,z) for z in a[1:]),instruction=idx,opcode=op,operands=a,detail=sem.COMPARES[op])
      nid=f'i{idx}:{dk}';g.add(nid,'EXEC_GATED_MASK_MERGE',key=dk,inputs=(old,cond,e),instruction=idx,opcode=op,operands=a,detail='inactive lanes preserve prior destination mask bits')
      state[dk]=nid;handled_full.add(dk);counts['compare_mask_definition_count']+=1;mask_opcounts[op]+=1
      row['mask_definition']={'key':dk,'node':nid,'kind':'EXEC_GATED_COMPARE_MASK_MERGE','old':old,'condition':cond,'exec':e}
   elif op in sem.CARRY:
    if len(a)<4:violations.append(f'carry_operands:{idx}:{a!r}')
    else:
     dk=pair_key(a[1])
     if dk not in state:violations.append(f'carry_untracked_dest:{idx}:{a[1]}')
     else:
      e=exec_ref(idx);old=state[dk];cv=g.add(f'i{idx}:carry','VECTOR_CARRY_CONDITION',inputs=tuple(leaf(idx,z) for z in a[2:]),instruction=idx,opcode=op,operands=a,detail=sem.CARRY[op])
      nid=f'i{idx}:{dk}';g.add(nid,'EXEC_GATED_MASK_MERGE',key=dk,inputs=(old,cv,e),instruction=idx,opcode=op,operands=a,detail='inactive lanes preserve prior carry-mask bits')
      state[dk]=nid;handled_full.add(dk);counts['carry_mask_definition_count']+=1;mask_opcounts[op]+=1
      row['mask_definition']={'key':dk,'node':nid,'kind':'EXEC_GATED_CARRY_MASK_MERGE','old':old,'condition':cv,'exec':e}
   elif op in sem.SCALAR_MASK and a:
    dk=pair_key(a[0])
    if dk in state:
     if op=='s_and_saveexec_b64':
      nid=f'i{idx}:{dk}';e=exec_ref(idx);g.add(nid,'SAVE_OLD_EXEC',key=dk,inputs=(e,),instruction=idx,opcode=op,operands=a);state[dk]=nid
     else:
      srcs=[mask_value(state,idx,z) for z in a[1:]];kind=sem.SCALAR_MASK[op];nid=f'i{idx}:{dk}';g.add(nid,kind,key=dk,inputs=srcs,instruction=idx,opcode=op,operands=a);state[dk]=nid
     handled_full.add(dk);counts['scalar_mask_definition_count']+=1;mask_opcounts[op]+=1
     row['mask_definition']={'key':dk,'node':state[dk],'kind':sem.SCALAR_MASK[op]}

   # Exact CNDMASK and branch consumers.
   if op=='v_cndmask_b32' and len(a)>=4:
    k=pair_key(a[3]);
    if k not in state:violations.append(f'cndmask_untracked_predicate:{idx}:{a[3]}')
    else:
     pred=state[k];row['mask_use']={'key':k,'node':pred,'kind':'VECTOR_SELECT_BY_MASK'};counts['cndmask_mask_use_count']+=1
   elif op in {'s_cbranch_vccz','s_cbranch_vccnz'}:
    pred=state['vcc'];row['mask_use']={'key':'vcc','node':pred,'kind':'MASK_EQ_ZERO_BRANCH' if op.endswith('vccz') else 'MASK_NE_ZERO_BRANCH'};counts['vcc_branch_mask_use_count']+=1

   # SCC producer semantics. Do not infer SCC from scalar opcode families.
   if op in sem.SCC_PRODUCERS:
    sk=sem.SCC_PRODUCERS[op]['kind']
    if sk=='NEW_EXEC_NONZERO':src=exec_out_ref(idx)
    elif op in sem.SCALAR_MASK and a and a[0]=='exec':src=exec_out_ref(idx)
    elif op in sem.SCALAR_MASK and row['mask_definition'] is not None:src=row['mask_definition']['node']
    else:src=scalar_result(idx,x)
    nid=f'i{idx}:scc';kind='SCC_SIGNED_OVERFLOW' if sk=='SIGNED_OVERFLOW' else 'SCC_NONZERO'
    g.add(nid,kind,key='scc',inputs=(src,),instruction=idx,opcode=op,operands=a,detail=sk);state['scc']=nid;row['scc_definition']={'node':nid,'kind':kind};counts['scc_definition_count']+=1;scc_opcounts[op]+=1
   if op=='s_cbranch_scc0':
    row['scc_use']={'node':state['scc'],'kind':'SCC_EQ_ZERO_BRANCH'};counts['scc_branch_use_count']+=1

   # Partial writes to a mask carrier invalidate/replace exactly one half while preserving the other.
   # Handle explicit vcc_lo/vcc_hi and ordinary SGPR defs that overlap a typed pair.
   defs=x.get('defs') or []
   if op=='s_mov_b32' and a:
    h=half_of_operand(a[0],keys)
    if h:
     k,half=h
     if k in state:
      val=leaf(idx,a[1]) if len(a)>1 else leaf(idx,'MISSING')
      write_half(state,idx,x,k,half,val);handled_halves.add((k,half));row['mask_definition']={'key':k,'node':state[k],'kind':'MASK_HALF_WRITE','half':half}
   for k in keys:
    if k in handled_full:continue
    hs=pair_halves(k)
    for half,hreg in enumerate(hs):
     if (k,half) in handled_halves:continue
     # v2 names vcc whole-mask writes as 'vcc'; handled source-closed full defs above.
     if hreg in defs:
      nid=f'i{idx}:{k}:opaque_half{half}';old=state[k]
      g.add(nid,'OPAQUE_MASK_HALF_DEF',key=k,inputs=(old,),instruction=idx,opcode=op,operands=a,exactness='PROVEN_DEF_OPAQUE_VALUE',detail={'half':half,'register':hreg});state[k]=nid;counts['opaque_mask_half_write_count']+=1
   # Any unhandled whole VCC definition is an explicit opaque boundary, never silently inherited.
   if 'vcc' in defs and 'vcc' not in handled_full:
    nid=f'i{idx}:vcc:opaque';g.add(nid,'OPAQUE_WHOLE_MASK_DEF',key='vcc',inputs=(state['vcc'],exec_ref(idx)),instruction=idx,opcode=op,operands=a,exactness='PROVEN_DEF_OPAQUE_VALUE');state['vcc']=nid;counts['opaque_whole_vcc_write_count']+=1
   if 'scc' in defs:violations.append(f'unexpected_structural_scc_def:{idx}:{op}')
   rows[ii]=row
  block_exit[b['id']]=dict(state)

 # Populate phi inputs after all block exits exist, preserving loops/backedges by node identity.
 for b in blocks:
  if b['id']==0 or not b['predecessors']:continue
  for k in state_keys:
   nid=entry[b['id']][k];g.nodes[nid]['inputs']=[block_exit[p][k] for p in b['predecessors']]
 # Graph integrity.
 for nid,n in list(g.nodes.items()):
  for src in n.get('inputs') or []:
   if src not in g.nodes:violations.append(f'missing_node:{nid}->{src}')
 for r in rows:
  if r is None:violations.append('missing_instruction_row')
 phi_count=sum(1 for n in g.nodes.values() if n['kind']=='CFG_PHI')
 orphan=sum(1 for b in blocks if b['id']!=0 and not b['predecessors'])
 return {
  'schema':SCHEMA,'status':STATUS if not violations else 'D1_GCN_CONDITION_SYMBOLIC_DATAFLOW_WITH_VIOLATIONS','shader':v2.get('shader'),
  'parse_accounting':copy.deepcopy(v2['parse_accounting']),'instruction_count':len(ins),'basic_block_count':len(blocks),'concrete_cfg_edge_count':sum(len(b['successors']) for b in blocks),
  'tracked_mask_keys':keys,'tracked_sgpr_pairs':[k for k in keys if k!='vcc'],'node_count':len(g.nodes),'phi_node_count':phi_count,'unresolved_control_entry_block_count':orphan,
  **dict(counts),'mask_machine_opcode_counts':dict(sorted(mask_opcounts.items())),'scc_machine_opcode_counts':dict(sorted(scc_opcounts.items())),
  'instructions':rows,'nodes':g.nodes,'violations':violations,
  'semantic_boundary':{'exec_symbolic_prerequisite':'GLOBAL_EXACT','condition_mask_symbolic_dataflow':'EXACT_FOR_SOURCE_CLOSED_MASK_SURFACE','scc_symbolic_dataflow':'EXACT_FOR_SOURCE_CLOSED_SCC_SURFACE','branch_feasibility':'WITHHELD','lane_aware_vgpr_ssa':'NEXT_GATE','shader_expression_semantics':'WITHHELD','shader_expression_semantic_promotions':0},
  'policy':'Arbitrary SGPR-pair predicates and VCC are tracked uniformly. Vector compare/carry writes merge under exact EXEC-in provenance so inactive lane bits are preserved. SCC is generated only by source-closed ISA producers. Unknown mask-half/whole writes become explicit opaque boundaries; no predicate intent or branch feasibility is invented.'
 }

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--structural-ir',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args();out=analyze(json.loads(a.structural_ir.read_text()));a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({k:out[k] for k in ('status','instruction_count','basic_block_count','node_count','phi_node_count')},indent=2));return 0 if not out['violations'] else 2
if __name__=='__main__':raise SystemExit(main())
