#!/usr/bin/env python3
"""Fail closed against cross-stage/API-number semantic leakage.

API numbers are ABI identities, not engine semantic names.  This guard joins two
independent exact checkpoints: the native semantic registry (which contains
instruction-proven VS transform-palette users of api10) and the LocalShader
api10 entry-layout census (whose runtime owner is explicitly withheld).

It intentionally does NOT assign a meaning to LocalShader api10.  Its purpose is
to make that non-transferability machine-checkable before portable Blender or
Rust/Vulkan binding code consumes these reports.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

STATUS='D1_API_SLOT_SEMANTIC_SCOPE_GUARD_EXACT'

def main()->int:
 ap=argparse.ArgumentParser(); ap.add_argument('--registry',type=Path,required=True); ap.add_argument('--local',type=Path,required=True); ap.add_argument('-o','--out',type=Path,required=True); a=ap.parse_args()
 reg=json.loads(a.registry.read_text()); loc=json.loads(a.local.read_text()); v=[]
 if reg.get('status')!='D1_NATIVE_SHADER_SEMANTIC_REGISTRY_V1_EXACT': v.append('semantic_registry_not_exact')
 if loc.get('status')!='D1_GCN_LOCALSHADER_API10_ENTRY_LAYOUT_CENSUS_EXACT': v.append('localshader_api10_census_not_exact')
 cov=loc.get('coverage',{})
 expected={'api10_program_count':39,'api10_wrapper_count':56,'api10_material_occurrence_count':3386,'api10_usage_layout_count':2,'api10_direct_immconstbuffer_program_count':39,'ptr_const_buffer_table_program_count':0,'ptr_resource_table_program_count':0,'ptr_extended_user_data_program_count':26}
 for k,x in expected.items():
  if cov.get(k)!=x: v.append(f'local_{k}:{cov.get(k)!r}')
 sem=loc.get('semantic_boundary',{})
 if sem.get('api10_delivery')!='EXACT_DIRECT_IMMCONSTBUFFER_PROGRAM_ENTRY_USER_DATA': v.append('local_api10_delivery_not_exact_direct')
 if sem.get('runtime_writer')!='WITHHELD' or sem.get('backing_memory_semantics')!='WITHHELD': v.append('local_semantic_boundary_was_promoted')
 # Require at least one independently proven VS semantic whose dataflow names
 # api10 as a transform palette.  Scope stays bound to that GCN/stage entry.
 vs=[]
 for e in reg.get('entries',[]):
  if e.get('stage')=='vs' and 'dual_quaternion' in str(e.get('semantic_class','')):
   vs.append({'gcn_sha256':e.get('gcn_sha256'),'shader_headers':e.get('shader_headers',[]),'semantic_class':e.get('semantic_class'),'source_proof_status':e.get('source_proof_status')})
 if not vs: v.append('no_exact_vs_dual_quaternion_registry_entry')
 for e in vs:
  if not e['gcn_sha256'] or not str(e['source_proof_status']).endswith('_EXACT'): v.append(f'vs_entry_not_exact:{e}')
 out={'schema':'d1_api_slot_semantic_scope_guard/v1','status':STATUS if not v else 'D1_API_SLOT_SEMANTIC_SCOPE_GUARD_WITH_VIOLATIONS','api_slot':10,'independent_scopes':{'vertex_shader_instruction_proven':vs,'localshader_entry_binding':{'program_count':cov.get('api10_program_count'),'wrapper_count':cov.get('api10_wrapper_count'),'material_occurrence_count':cov.get('api10_material_occurrence_count'),'delivery':sem.get('api10_delivery'),'runtime_writer':'WITHHELD','backing_memory_semantics':'WITHHELD'}},'portable_binding_rule':'Key resource semantics by exact program/stage/usage provenance; never by API slot number alone. VS api10 transform-palette semantics are not transferable to LocalShader api10.','violations':v}
 a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps({'status':out['status'],'vs_semantic_entries':len(vs),'violations':v},indent=2)); return 0 if not v else 2
if __name__=='__main__': raise SystemExit(main())
