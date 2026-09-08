#!/usr/bin/env python3
"""Promote the source-proven final ordinary GCN core of 808EE505, fail closed."""
from __future__ import annotations
import argparse,collections,copy,json
from pathlib import Path
TARGETS={'s_mov_b32','s_mov_b64','s_wqm_b64','s_waitcnt','s_cbranch_execz','s_endpgm','v_sub_f32','v_subrev_f32','v_sqrt_f32','v_rsq_f32','v_cvt_i32_f32','v_cvt_f32_i32','v_add_i32','v_cmp_lg_i32','v_cndmask_b32','v_madmk_f32'}
CONTROL={'s_wqm_b64','s_waitcnt','s_cbranch_execz','s_endpgm'}
EXPECTED_REMAIN=[63,64,65,66,74,75,76,77,212,213]

def contiguous(v):
 v=sorted(set(v));o=[]
 if not v:return o
 a=b=v[0]
 for x in v[1:]:
  if x==b+1:b=x
  else:o.append((a,b));a=b=x
 o.append((a,b));return o

def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument('--program',type=Path,required=True);ap.add_argument('--ir',type=Path,required=True);ap.add_argument('--source-proof',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args();viol=[];result={}
 try:
  base=json.load(open(a.program));ir=json.load(open(a.ir));sp=json.load(open(a.source_proof));p=base['program'];c=p['coverage']
  assert base['status']=='D1_GCN_RENDERER_PROGRAM_IR_EXACT_PARTIAL' and not base['violations']
  assert p['material']=='80D777B6' and p['pixel_shader']=='808EE505' and p['instruction_count']==456
  assert c['primary_resolution_counts']=={'CONTROL_EXACT':18,'EXPRESSION_EXACT':254,'INPUT_PROVENANCE_EXACT':70,'RECURRENCE_EXACT':36,'STRUCTURAL_ONLY':78},c
  assert c['exact_nonstructural_instruction_count']==378
  assert ir['status']=='D1_GCN_STRUCTURAL_IR_COMPLETE' and ir['shader']=='808EE505' and ir['instruction_count']==456
  assert sp['status']=='D1_GCN_REMAINING_CORE_SOURCE_SEMANTICS_EXACT' and sp['shader']=='808EE505' and not sp['violations']
  sem=sp['opcode_semantics'];assert set(sem)==TARGETS
  out=copy.deepcopy(base);op=out['program'];rows=op['instruction_resolution'];ins=ir['instructions'];prom=[];contracts=[];control=[];expr=[]
  for i,r in enumerate(rows):
   if r['primary_resolution']!='STRUCTURAL_ONLY' or r['opcode'] not in TARGETS:continue
   x=ins[i];s=sem[r['opcode']];asm=x['assembly'].split('*/',1)[-1].strip();dest=(x.get('operands') or [''])[0]
   tier='CONTROL_EXACT' if r['opcode'] in CONTROL or (r['opcode']=='s_mov_b64' and dest=='exec') else 'EXPRESSION_EXACT'
   r['primary_resolution']=tier;r['evidence_tags']=sorted(set(r.get('evidence_tags',[])+['REMAINING_CORE_SOURCE_OPCODE_SEMANTICS_EXACT','EXACT_STRUCTURAL_OPERANDS_AND_MODIFIERS']))
   prom.append(i);(control if tier=='CONTROL_EXACT' else expr).append(i)
   contracts.append({'instruction':i,'address':x['address_hex'],'opcode':r['opcode'],'assembly':asm,'operands':x.get('operands',[]),'primary_resolution':tier,'equation':s['equation'],'source_key':s['source_key'],'source_revision':s['source_revision'],'source_file_sha256':s['source_file_sha256']})
  assert len(prom)==68,(len(prom),prom);assert len(control)==29,(len(control),control);assert len(expr)==39,(len(expr),expr)
  remaining=[i for i,r in enumerate(rows) if r['primary_resolution']=='STRUCTURAL_ONLY'];assert remaining==EXPECTED_REMAIN,remaining
  assert collections.Counter(rows[i]['opcode'] for i in remaining)=={'ds_swizzle_b32':8,'image_sample':2}
  op['remaining_core_source_semantic_contracts']=contracts
  counts=collections.Counter(r['primary_resolution'] for r in rows);struct=set(remaining);spans=[]
  for lo,hi in contiguous(struct):
   rr=ins[lo:hi+1];ops=collections.Counter(x['opcode'] for x in rr);spans.append({'start_instruction':lo,'end_instruction':hi,'instruction_count':hi-lo+1,'opcode_histogram':dict(sorted(ops.items())),'image_instructions':[x['index'] for x in rr if x['opcode'].startswith('image_')],'branch_instructions':[x['index'] for x in rr if x['opcode'].startswith('s_cbranch') or x['opcode']=='s_branch'],'exec_write_instructions':[x['index'] for x in rr if 'exec' in x.get('defs',[])],'boundary':'STRUCTURAL_ONLY_DS_SWIZZLE_OR_IMAGE_SAMPLE'})
  oc=op['coverage'];oc['primary_resolution_counts']=dict(sorted(counts.items()));oc['exact_nonstructural_instruction_count']=456-counts['STRUCTURAL_ONLY'];oc['structural_only_instruction_count']=counts['STRUCTURAL_ONLY'];oc['structural_only_spans']=spans;oc['remaining_core_source_semantics_promoted_instructions']=prom;oc['remaining_core_source_semantics_promoted_instruction_count']=68;oc['remaining_core_control_promoted_instructions']=control;oc['remaining_core_expression_promoted_instructions']=expr
  expected={'CONTROL_EXACT':47,'EXPRESSION_EXACT':293,'INPUT_PROVENANCE_EXACT':70,'RECURRENCE_EXACT':36,'STRUCTURAL_ONLY':10};assert oc['primary_resolution_counts']==expected,oc;assert oc['exact_nonstructural_instruction_count']==446
  out['schema_version']=max(8,int(out.get('schema_version',0)));out.setdefault('semantic_boundary',{})['remaining_core_source_semantics']='EXACT_SYMBOLIC_68_INSTRUCTIONS';out['semantic_boundary']['remaining_structural_frontier']='8_DS_SWIZZLE_PLUS_2_IMAGE_SAMPLE';result=out;result['violations']=[]
 except Exception as e:
  viol=[repr(e)];result={'schema_version':1,'status':'D1_GCN_RENDERER_REMAINING_CORE_SEMANTICS_PARTIAL','violations':viol}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result.get('status'),'coverage':result.get('program',{}).get('coverage',{}).get('primary_resolution_counts'),'exact_nonstructural':result.get('program',{}).get('coverage',{}).get('exact_nonstructural_instruction_count'),'violations':viol},indent=2));return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
