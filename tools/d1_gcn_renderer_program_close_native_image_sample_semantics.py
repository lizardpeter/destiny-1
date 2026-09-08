#!/usr/bin/env python3
"""Close the final two 808EE505 IMAGE_SAMPLE instructions as exact native-symbolic operations.

This deliberately does NOT guess a portable texture dimension. GCN IMAGE_SAMPLE consumes
its live T# resource descriptor, S# sampler descriptor, VADDR vector and implicit pixel
sampling state. Those native inputs are already exact for the target instructions. A
concrete portable dimension remains a resource-adapter concern, not an opcode-semantic
unknown.
"""
from __future__ import annotations
import argparse, collections, copy, hashlib, json
from pathlib import Path

TARGET=[212,213]
GEM5_REV='f5c5a6e390f55dd5984977815bf9d0bd05da6945'

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()

def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument('--program',type=Path,required=True);ap.add_argument('--ir',type=Path,required=True);ap.add_argument('--gem5-mimg',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args();viol=[];result={}
 try:
  base=json.load(open(a.program));ir=json.load(open(a.ir));p=base['program'];c=p['coverage']
  assert base['status']=='D1_GCN_RENDERER_PROGRAM_IR_EXACT_PARTIAL' and not base['violations']
  assert p['material']=='80D777B6' and p['pixel_shader']=='808EE505' and p['instruction_count']==456
  assert c['primary_resolution_counts']=={'CONTROL_EXACT':47,'EXPRESSION_EXACT':301,'INPUT_PROVENANCE_EXACT':70,'RECURRENCE_EXACT':36,'STRUCTURAL_ONLY':2},c
  assert c['exact_nonstructural_instruction_count']==454
  assert ir['status']=='D1_GCN_STRUCTURAL_IR_COMPLETE' and ir['shader']=='808EE505' and ir['instruction_count']==456
  rows=p['instruction_resolution'];ins=ir['instructions']
  rem=[i for i,r in enumerate(rows) if r['primary_resolution']=='STRUCTURAL_ONLY'];assert rem==TARGET,rem
  assert [rows[i]['opcode'] for i in TARGET]==['image_sample','image_sample']

  src=a.gem5_mimg.read_text(errors='strict');digest=sha(a.gem5_mimg)
  assert 'Inst_MIMG__IMAGE_SAMPLE::Inst_MIMG__IMAGE_SAMPLE(InFmt_MIMG *iFmt)' in src
  assert ': Inst_MIMG(iFmt, "image_sample")' in src
  assert '// sample texture map.' in src

  # Existing renderer semantics already use SAMPLE nodes as native symbolic texture
  # operations without fabricating a concrete portable dimension. Preserve that exact
  # abstraction for the two final samples, but require their live descriptor provenance.
  sample_nodes=[]
  for reg in p.get('exact_simple_region_expressions',[]):
   for n in reg.get('nodes',[]):
    if n.get('op')=='SAMPLE': sample_nodes.append(n)
  assert len(sample_nodes)>=8 and all('texture_indices' in n and 'sampler_indices' in n and 'coordinate_operand' in n for n in sample_nodes)

  live={int(x['instruction']):x for x in p['descriptor_live_provenance']['image_live_bindings']}
  tb={int(x['texture_index']):x['texture_taghash'] for x in p['texture_bindings']}
  expected={212:{'texture_index':4,'texture':'808EE500','sampler_index':5,'channels':'xy','resource_producer':196,'sampler_origin':'EXTENDED_USER_DATA_LOAD'},213:{'texture_index':0,'texture':'808EE4FE','sampler_index':1,'channels':'xyzw','resource_producer':198,'sampler_origin':'ENTRY_RESIDENT'}}

  out=copy.deepcopy(base);op=out['program'];orows=op['instruction_resolution'];contracts=[]
  for i in TARGET:
   x=ins[i];lv=live[i];ex=expected[i]
   assert lv['opcode']=='image_sample' and lv['crosscheck']=='MATCHES_D1_GCN_IMAGE_RESOURCE_USAGE_EXACT'
   assert lv['texture_index']==ex['texture_index'] and tb[lv['texture_index']]==ex['texture']
   assert lv['sampler_index']==ex['sampler_index'] and lv['dmask_channels']==ex['channels']
   assert lv['resource_descriptor']['producer_instruction']==ex['resource_producer']
   assert lv['resource_descriptor']['origin_kind']=='RESOURCE_TABLE_LOAD'
   assert lv['sampler_descriptor']['origin_kind']==ex['sampler_origin']
   assert x['image']['textures']==[ex['texture_index']] and x['image']['samplers']==[ex['sampler_index']]
   assert x['image']['dmask_channels']==ex['channels']
   r=orows[i];r['primary_resolution']='EXPRESSION_EXACT';r['evidence_tags']=sorted(set(r.get('evidence_tags',[])+['NATIVE_IMAGE_SAMPLE_SEMANTICS_SOURCE_EXACT','DESCRIPTOR_LIVE_PROVENANCE_EXACT','NATIVE_DESCRIPTOR_PARAMETRIC_SAMPLE_EXACT']))
   contracts.append({'instruction':i,'address':x['address_hex'],'assembly':x['assembly'].split('*/',1)[-1].strip(),'operation':'NATIVE_IMAGE_SAMPLE','texture_index':ex['texture_index'],'texture_taghash':ex['texture'],'sampler_index':ex['sampler_index'],'dmask_channels':ex['channels'],'coordinate_operand':x['operands'][1],'resource_descriptor':lv['resource_descriptor'],'sampler_descriptor':lv['sampler_descriptor'],'expression':'D[dmask] = GCN_IMAGE_SAMPLE(T#, S#, VADDR, implicit_pixel_sampling_state)[dmask]','resource_dimension':'CONSUMED_FROM_NATIVE_RESOURCE_DESCRIPTOR_NOT_GUESSED','source_revision':GEM5_REV,'source_file_sha256':digest,'source_literal':'// sample texture map.'})

  op['final_native_image_sample_contracts']=contracts
  counts=collections.Counter(r['primary_resolution'] for r in orows);oc=op['coverage']
  oc['primary_resolution_counts']=dict(sorted(counts.items()));oc['exact_nonstructural_instruction_count']=456-counts['STRUCTURAL_ONLY'];oc['structural_only_instruction_count']=counts['STRUCTURAL_ONLY'];oc['structural_only_spans']=[];oc['final_native_image_sample_promoted_instructions']=TARGET;oc['final_native_image_sample_promoted_instruction_count']=2
  expected_counts={'CONTROL_EXACT':47,'EXPRESSION_EXACT':303,'INPUT_PROVENANCE_EXACT':70,'RECURRENCE_EXACT':36}
  assert oc['primary_resolution_counts']==expected_counts,oc
  assert oc['exact_nonstructural_instruction_count']==456 and oc['structural_only_instruction_count']==0
  assert all(r['primary_resolution']!='STRUCTURAL_ONLY' for r in orows)
  out['schema_version']=max(10,int(out.get('schema_version',0)))
  out['status']='D1_GCN_RENDERER_PROGRAM_IR_NATIVE_SEMANTICS_EXACT'
  sb=out.setdefault('semantic_boundary',{});sb['native_instruction_semantics']='EXACT_456_OF_456';sb['final_image_samples']='EXACT_NATIVE_DESCRIPTOR_PARAMETRIC';sb['portable_resource_dimension_for_808EE500_808EE4FE']='SEPARATE_RESOURCE_ADAPTER_FRONTIER'
  result=out;result['violations']=[]
 except Exception as e:
  viol=[repr(e)];result={'schema_version':1,'status':'D1_GCN_RENDERER_FINAL_IMAGE_SAMPLE_SEMANTICS_PARTIAL','violations':viol}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result.get('status'),'coverage':result.get('program',{}).get('coverage',{}).get('primary_resolution_counts'),'exact_nonstructural':result.get('program',{}).get('coverage',{}).get('exact_nonstructural_instruction_count'),'violations':viol},indent=2));return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
