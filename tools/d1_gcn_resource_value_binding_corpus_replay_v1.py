#!/usr/bin/env python3
"""Replay exact IMAGE/BUFFER/DS architectural state binding across the D1 shader corpus."""
from __future__ import annotations
import argparse,collections,json,multiprocessing as mp,os
from pathlib import Path
import d1_gcn_resource_value_binding_v1 as binding

CENSUS_STATUS="D1_GCN_SHADER_CORPUS_STRUCTURAL_CENSUS_COMPLETE"
BINDING_STATUS="D1_GCN_RESOURCE_VALUE_BINDING_EXACT"
SCHEMA="d1_gcn_resource_value_binding_corpus_replay/v1"
STATUS="D1_GCN_RESOURCE_VALUE_BINDING_CORPUS_EXACT"
EXPECTED_PROGRAMS=26464
EXPECTED_INSTRUCTIONS=4896165
EXPECTED_STAGE={"DS":20,"PS":18375,"VS":8069}
EXPECTED_OPCODE_I={
 "buffer_load_dword":40,"ds_read2_b32":401,"ds_read_b32":89,"ds_swizzle_b32":9556,
 "image_gather4_lz":6,"image_gather4_lz_o":2,"image_get_lod":2953,"image_get_resinfo":48,
 "image_load_mip":6623,"image_sample":98786,"image_sample_d":150,"image_sample_l":2953,
 "image_sample_lz":3941,"image_sample_lz_o":4,"tbuffer_load_format_xyz":4,"tbuffer_load_format_xyzw":10085,
}
EXPECTED_OPCODE_C={
 "buffer_load_dword":40,"ds_read2_b32":802,"ds_read_b32":89,"ds_swizzle_b32":9556,
 "image_gather4_lz":24,"image_gather4_lz_o":8,"image_get_lod":2953,"image_get_resinfo":96,
 "image_load_mip":8446,"image_sample":230402,"image_sample_d":153,"image_sample_l":11268,
 "image_sample_lz":5078,"image_sample_lz_o":4,"tbuffer_load_format_xyz":12,"tbuffer_load_format_xyzw":40340,
}
EXPECTED_RESOURCE_INSTRUCTIONS=135641
EXPECTED_RESOURCE_COMPONENTS=309271
EXPECTED_IMAGE_I=115466
EXPECTED_IMAGE_C=258432
EXPECTED_BUFFER_I=10129
EXPECTED_BUFFER_C=40392
EXPECTED_DS_I=10046
EXPECTED_DS_C=10447
EXPECTED_VGPR_SOURCE_COMPONENT_REFS=482039
EXPECTED_RESOURCE_DESCRIPTOR_COMPONENT_REFS=964244
EXPECTED_SAMPLER_DESCRIPTOR_COMPONENT_REFS=435180
EXPECTED_SCALAR_SOURCE_COMPONENT_REFS=1399464
EXPECTED_BUFFER_SCALAR_OFFSET_REFS=40
EXPECTED_DS_M0_REFS=490


def worker(path: str) -> dict:
 p=Path(path);sha=p.stem.lower()
 try:
  d=binding.analyze(json.loads(p.read_text()));c=d.get("coverage") or {}
  return {"sha":sha,"ok":d.get("status")==BINDING_STATUS and not d.get("violations"),"status":d.get("status"),
          "violations":(d.get("violations") or [])[:8],"instructions":d.get("instruction_count",0),"coverage":c}
 except Exception as e:return {"sha":sha,"ok":False,"exception":f"{type(e).__name__}:{e}"}


def replay(ir_dir: Path,census_path: Path,workers: int) -> dict:
 v=[];census=json.loads(census_path.read_text())
 if census.get("status")!=CENSUS_STATUS:v.append(f"census_status:{census.get('status')!r}")
 stages={p["gcn_sha256"]:(p.get("stages") or []) for p in census.get("programs") or []}
 if len(stages)!=EXPECTED_PROGRAMS:v.append(f"stage_map:{len(stages)}!={EXPECTED_PROGRAMS}")
 paths=sorted(ir_dir.glob("*.json"))
 if len(paths)!=EXPECTED_PROGRAMS:v.append(f"ir_file_count:{len(paths)}!={EXPECTED_PROGRAMS}")
 totals=collections.Counter();op_i=collections.Counter();op_c=collections.Counter();stage=collections.Counter();rows=[]
 pool=None;it=map(worker,map(str,paths))
 if workers>1:
  pool=mp.Pool(workers);it=pool.imap_unordered(worker,map(str,paths),chunksize=4)
 try:
  for r in it:
   sha=r["sha"];st=stages.get(sha)
   if not st or len(st)!=1:v.append(f"stage:{sha}:{st}");continue
   stage[st[0]]+=1
   if not r.get("ok"):
    v.append(f"analyze:{sha}:{r.get('exception') or (r.get('status'),r.get('violations'))}");continue
   c=r["coverage"];totals["instructions"]+=r["instructions"]
   for k in (
    "resource_instruction_count","resource_result_component_count","image_instruction_count","image_result_component_count",
    "buffer_instruction_count","buffer_result_component_count","ds_instruction_count","ds_result_component_count",
    "vgpr_source_state_component_reference_count","scalar_source_state_component_reference_count",
    "resource_descriptor_sgpr_component_reference_count","sampler_descriptor_sgpr_component_reference_count",
    "buffer_scalar_offset_state_reference_count","ds_m0_state_reference_count","shader_expression_semantic_promotions",
   ):totals[k]+=c.get(k,0)
   op_i.update(c.get("opcode_instruction_counts") or {});op_c.update(c.get("opcode_result_component_counts") or {})
   rows.append({"gcn_sha256":sha,"stage":st[0],"resource_instruction_count":c.get("resource_instruction_count",0),
                "resource_result_component_count":c.get("resource_result_component_count",0)})
 finally:
  if pool:pool.close();pool.join()
 rows.sort(key=lambda x:x["gcn_sha256"])
 checks=[
  ("programs",len(rows),EXPECTED_PROGRAMS),("stage_counts",dict(sorted(stage.items())),EXPECTED_STAGE),
  ("instructions",totals["instructions"],EXPECTED_INSTRUCTIONS),
  ("resource_instruction_count",totals["resource_instruction_count"],EXPECTED_RESOURCE_INSTRUCTIONS),
  ("resource_result_component_count",totals["resource_result_component_count"],EXPECTED_RESOURCE_COMPONENTS),
  ("image_instruction_count",totals["image_instruction_count"],EXPECTED_IMAGE_I),
  ("image_result_component_count",totals["image_result_component_count"],EXPECTED_IMAGE_C),
  ("buffer_instruction_count",totals["buffer_instruction_count"],EXPECTED_BUFFER_I),
  ("buffer_result_component_count",totals["buffer_result_component_count"],EXPECTED_BUFFER_C),
  ("ds_instruction_count",totals["ds_instruction_count"],EXPECTED_DS_I),
  ("ds_result_component_count",totals["ds_result_component_count"],EXPECTED_DS_C),
  ("vgpr_source_state_component_reference_count",totals["vgpr_source_state_component_reference_count"],EXPECTED_VGPR_SOURCE_COMPONENT_REFS),
  ("resource_descriptor_sgpr_component_reference_count",totals["resource_descriptor_sgpr_component_reference_count"],EXPECTED_RESOURCE_DESCRIPTOR_COMPONENT_REFS),
  ("sampler_descriptor_sgpr_component_reference_count",totals["sampler_descriptor_sgpr_component_reference_count"],EXPECTED_SAMPLER_DESCRIPTOR_COMPONENT_REFS),
  ("scalar_source_state_component_reference_count",totals["scalar_source_state_component_reference_count"],EXPECTED_SCALAR_SOURCE_COMPONENT_REFS),
  ("buffer_scalar_offset_state_reference_count",totals["buffer_scalar_offset_state_reference_count"],EXPECTED_BUFFER_SCALAR_OFFSET_REFS),
  ("ds_m0_state_reference_count",totals["ds_m0_state_reference_count"],EXPECTED_DS_M0_REFS),
  ("opcode_instruction_counts",dict(sorted(op_i.items())),EXPECTED_OPCODE_I),
  ("opcode_result_component_counts",dict(sorted(op_c.items())),EXPECTED_OPCODE_C),
  ("shader_expression_semantic_promotions",totals["shader_expression_semantic_promotions"],0),
 ]
 for name,got,want in checks:
  if got!=want:v.append(f"{name}:{got}!={want}")
 closed=2994369+425370+totals["resource_result_component_count"]
 coverage={
  "exact_programs_replayed":len(rows),"stage_program_counts":dict(sorted(stage.items())),"exact_instructions_replayed":totals["instructions"],
  **{k:totals[k] for k in sorted(totals) if k!="instructions"},
  "opcode_instruction_counts":dict(sorted(op_i.items())),"opcode_result_component_counts":dict(sorted(op_c.items())),
  "architectural_result_components_formula_interpolation_resource":closed,
  "total_vgpr_result_components":3864039,
  "architectural_result_surface_percent":100.0*closed/3864039,
  "remaining_machine_special_result_components":3864039-closed,
 }
 return {"schema":SCHEMA,"status":STATUS if not v else "D1_GCN_RESOURCE_VALUE_BINDING_CORPUS_WITH_VIOLATIONS",
         "coverage":coverage,"programs":rows,"violations":v,
         "semantic_boundary":{
          "image_buffer_ds_operation_identity":"GLOBAL_SOURCE_CLOSED" if not v else "NOT_PROMOTED",
          "resource_result_lane_binding":"GLOBAL_EXACT" if not v else "NOT_PROMOTED",
          "resource_operand_register_state":"GLOBAL_EXACT" if not v else "NOT_PROMOTED",
          "descriptor_contents":"OPAQUE_STATE_VALUES","runtime_resource_table_assignment":"NEXT_GATE" if not v else "WITHHELD",
          "material_texture_sampler_constant_binding":"NEXT_GATE" if not v else "WITHHELD",
          "shader_expression_semantics":"WITHHELD","material_semantics":"WITHHELD","shader_expression_semantic_promotions":0},
         "policy":"The entire observed IMAGE/BUFFER/DS result surface is reconciled to exact existing register/M0 and lane-write identities. Runtime descriptor contents and D1 material/resource assignments remain withheld until independently proven."}


def main() -> int:
 p=argparse.ArgumentParser();p.add_argument("--ir-dir",type=Path,required=True);p.add_argument("--census",type=Path,required=True);p.add_argument("--workers",type=int,default=max(1,min(4,os.cpu_count() or 1)));p.add_argument("-o","--output",type=Path,required=True);a=p.parse_args()
 d=replay(a.ir_dir,a.census,max(1,a.workers));a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":d["status"],"coverage":d["coverage"],"violations":d["violations"][:50]},indent=2,sort_keys=True));return 0 if not d["violations"] else 2
if __name__=="__main__":raise SystemExit(main())
