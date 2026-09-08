#!/usr/bin/env python3
from __future__ import annotations
import argparse,collections,copy,json
from pathlib import Path
TARGETS={'v_mul_f32','v_mov_b32','v_mac_f32','v_mul_legacy_f32','v_mad_f32','v_mac_legacy_f32','v_rcp_f32','v_rsq_clamp_f32'}

def contiguous(v):
 v=sorted(set(v));o=[]
 if not v:return o
 a=b=v[0]
 for x in v[1:]:
  if x==b+1:b=x
  else:o.append((a,b));a=b=x
 o.append((a,b));return o

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--program',type=Path,required=True);ap.add_argument('--ir',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args()
 bad=[];res={}
 try:
  base=json.load(open(a.program));ir=json.load(open(a.ir));p=base['program'];c=p['coverage']
  assert base['status']=='D1_GCN_RENDERER_PROGRAM_IR_EXACT_PARTIAL' and not base['violations']
  assert c['primary_resolution_counts']=={'CONTROL_EXACT':18,'EXPRESSION_EXACT':161,'INPUT_PROVENANCE_EXACT':70,'RECURRENCE_EXACT':36,'STRUCTURAL_ONLY':171};assert c['exact_nonstructural_instruction_count']==285
  assert ir['status']=='D1_GCN_STRUCTURAL_IR_COMPLETE' and ir['instruction_count']==456
  sem={}
  def walk(x):
   if isinstance(x,dict):
    ss=x.get('source_semantics')
    if isinstance(ss,dict):
     for k,v in ss.items():sem.setdefault(k,v)
    for v in x.values():walk(v)
   elif isinstance(x,list):
    for v in x:walk(v)
  walk(p)
  for op in TARGETS:
   assert op in sem and sem[op].get('equation') and sem[op].get('source_revision') and sem[op].get('source_file_sha256'),(op,sem.get(op))
  out=copy.deepcopy(base);oprog=out['program'];rows=oprog['instruction_resolution'];ins=ir['instructions'];prom=[];contracts=[]
  for i,r in enumerate(rows):
   if r['primary_resolution']!='STRUCTURAL_ONLY' or r['opcode'] not in TARGETS:continue
   s=sem[r['opcode']];x=ins[i]
   contracts.append({'instruction':i,'address':x['address_hex'],'opcode':r['opcode'],'assembly':x['assembly'].split('*/',1)[-1].strip(),'operands':x['operands'],'equation':s['equation'],'operation':s.get('operation'),'source_revision':s['source_revision'],'source_file_sha256':s['source_file_sha256'],'modifiers_preserved_in_exact_assembly':True})
   r['primary_resolution']='EXPRESSION_EXACT';r['evidence_tags']=sorted(set(r.get('evidence_tags',[])+['SOURCE_OPCODE_SEMANTICS_EXACT','EXACT_STRUCTURAL_OPERANDS_AND_MODIFIERS']));prom.append(i)
  assert len(prom)==93,(len(prom),prom)
  oprog['source_alu_instruction_contracts']=contracts
  counts=collections.Counter(r['primary_resolution'] for r in rows);struct={i for i,r in enumerate(rows) if r['primary_resolution']=='STRUCTURAL_ONLY'};spans=[]
  for lo,hi in contiguous(struct):
   rr=ins[lo:hi+1];ops=collections.Counter(x['opcode'] for x in rr);spans.append({'start_instruction':lo,'end_instruction':hi,'instruction_count':hi-lo+1,'opcode_histogram':dict(sorted(ops.items())),'image_instructions':[x['index'] for x in rr if x['opcode'].startswith('image_')],'branch_instructions':[x['index'] for x in rr if x['opcode'].startswith('s_cbranch') or x['opcode']=='s_branch'],'exec_write_instructions':[x['index'] for x in rr if 'exec' in x.get('defs',[])],'boundary':'STRUCTURAL_ONLY_NO_VALUE_EXPRESSION_PROMOTION'})
  oc=oprog['coverage'];oc['primary_resolution_counts']=dict(sorted(counts.items()));oc['exact_nonstructural_instruction_count']=456-counts['STRUCTURAL_ONLY'];oc['structural_only_instruction_count']=counts['STRUCTURAL_ONLY'];oc['structural_only_spans']=spans;oc['source_alu_semantics_promoted_instructions']=prom;oc['source_alu_semantics_promoted_instruction_count']=len(prom)
  exp={'CONTROL_EXACT':18,'EXPRESSION_EXACT':254,'INPUT_PROVENANCE_EXACT':70,'RECURRENCE_EXACT':36,'STRUCTURAL_ONLY':78};assert oc['primary_resolution_counts']==exp;assert oc['exact_nonstructural_instruction_count']==378
  out['schema_version']=max(7,int(out.get('schema_version',0)));out.setdefault('semantic_boundary',{})['source_backed_scalar_vgpr_alu']='EXACT_SYMBOLIC_FOR_LISTED_93_INSTRUCTIONS';out['semantic_boundary']['live_input_values_for_source_alu']='NOT_NUMERICALLY_CAPTURED'
  res=out
 except Exception as e:bad=[repr(e)];res={'schema_version':1,'status':'D1_GCN_RENDERER_SOURCE_ALU_SEMANTICS_PARTIAL','violations':bad}
 a.output.write_text(json.dumps(res,indent=2)+'\n');print(json.dumps({'status':res.get('status'),'coverage':res.get('program',{}).get('coverage',{}).get('primary_resolution_counts'),'exact':res.get('program',{}).get('coverage',{}).get('exact_nonstructural_instruction_count'),'violations':bad},indent=2));return 0 if not bad else 2
if __name__=='__main__':raise SystemExit(main())
