#!/usr/bin/env python3
"""Fail closed against cross-stage/API-number semantic leakage."""
from __future__ import annotations
import argparse,json
from pathlib import Path
STATUS='D1_API_SLOT_SEMANTIC_SCOPE_GUARD_EXACT'
EXPECTED_VS={
 'a5ad940fbf21746563f6585b889ac91b4220c94a3559e768028c894454bcdc12':'D1_XUR_VS_A5AD940F_DATAFLOW_SEMANTICS_EXACT',
 'b045462d7896e5c5012e8587076f6c669455b35009c197cd1c50d4e7529a1ab6':'D1_XUR_VS_80876960_TWO_INFLUENCE_DQ_EXACT',
 '24392dbd8f217a832456372a8d9c24d3ef365ab5a0b8bcd362882ca845052964':'D1_XUR_VS_8087695B_FOUR_INFLUENCE_DQ_EXACT',
}
def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument('--registry',type=Path,required=True);ap.add_argument('--local',type=Path,required=True);ap.add_argument('-o','--out',type=Path,required=True);a=ap.parse_args();reg=json.loads(a.registry.read_text());loc=json.loads(a.local.read_text());v=[]
 if reg.get('status')!='D1_NATIVE_SHADER_SEMANTIC_REGISTRY_V1_EXACT':v.append('semantic_registry_not_exact')
 if loc.get('status')!='D1_GCN_LOCALSHADER_API10_ENTRY_LAYOUT_CENSUS_EXACT':v.append('localshader_api10_census_not_exact')
 cov=loc.get('coverage',{}); expected={'api10_program_count':39,'api10_wrapper_count':56,'api10_material_occurrence_count':3386,'api10_usage_layout_count':2,'api10_direct_immconstbuffer_program_count':39,'ptr_const_buffer_table_program_count':0,'ptr_resource_table_program_count':0,'ptr_extended_user_data_program_count':26}
 for k,x in expected.items():
  if cov.get(k)!=x:v.append(f'local_{k}:{cov.get(k)!r}')
 sem=loc.get('semantic_boundary',{})
 if sem.get('api10_delivery')!='EXACT_DIRECT_IMMCONSTBUFFER_PROGRAM_ENTRY_USER_DATA':v.append('local_api10_delivery_not_exact_direct')
 if sem.get('runtime_writer')!='WITHHELD' or sem.get('backing_memory_semantics')!='WITHHELD':v.append('local_semantic_boundary_was_promoted')
 by={e.get('gcn_sha256'):e for e in reg.get('entries',[])};vs=[]
 for sha,status in EXPECTED_VS.items():
  e=by.get(sha)
  if not e:v.append(f'missing_exact_vs:{sha}');continue
  if e.get('stage')!='vs':v.append(f'wrong_stage:{sha}:{e.get("stage")}')
  if e.get('source_proof_status')!=status:v.append(f'wrong_proof_status:{sha}:{e.get("source_proof_status")}')
  if 'dual_quaternion' not in str(e.get('semantic_class','')):v.append(f'wrong_semantic_class:{sha}:{e.get("semantic_class")}')
  vs.append({'gcn_sha256':sha,'shader_headers':e.get('shader_headers',[]),'semantic_class':e.get('semantic_class'),'source_proof_status':e.get('source_proof_status')})
 if len(vs)!=3:v.append(f'vs_exact_count:{len(vs)}')
 out={'schema':'d1_api_slot_semantic_scope_guard/v1','status':STATUS if not v else 'D1_API_SLOT_SEMANTIC_SCOPE_GUARD_WITH_VIOLATIONS','api_slot':10,'independent_scopes':{'vertex_shader_instruction_proven':vs,'localshader_entry_binding':{'program_count':cov.get('api10_program_count'),'wrapper_count':cov.get('api10_wrapper_count'),'material_occurrence_count':cov.get('api10_material_occurrence_count'),'delivery':sem.get('api10_delivery'),'runtime_writer':'WITHHELD','backing_memory_semantics':'WITHHELD'}},'portable_binding_rule':'Key resource semantics by exact program/stage/usage provenance; never by API slot number alone. The three exact VS api10 dual-quaternion transform-palette proofs are scoped to their VS GCN identities and are not transferable to LocalShader api10.','next_primary_evidence':'Capture or retail-runtime command evidence connecting one of the 56 LocalShader wrappers to the four descriptor dwords written at its direct API10 user-SGPR window, then trace that descriptor to its backing allocation.','violations':v}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':out['status'],'vs_exact_count':len(vs),'local_program_count':cov.get('api10_program_count'),'violations':v},indent=2));return 0 if not v else 2
if __name__=='__main__':raise SystemExit(main())
