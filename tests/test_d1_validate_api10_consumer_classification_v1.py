#!/usr/bin/env python3
import json,subprocess,sys,tempfile
from pathlib import Path
V=Path(__file__).resolve().parents[1]/"tools/d1_validate_api10_consumer_classification_v1.py"
WITH=["runtime_writer","backing_allocation","universal_record_schema","engine_buffer_name","engine_semantic"]

base={"schema":"d1_api10_consumer_classification/v1","programs":[{"gcn_sha256":"a"*64,"evidence_class":"EXACT_NATIVE_GCN","descriptor_window":"s[8:11]","consumer_record_structure":"capture-specific float4 records","consumer_math_role":"instruction-proven transform arithmetic","runtime_writer":"WITHHELD","backing_allocation":"WITHHELD","universal_record_schema":"WITHHELD","engine_buffer_name":"WITHHELD","engine_semantic":"WITHHELD"}],"semantic_boundary":{k:"WITHHELD" for k in WITH}}

def run(d,census=None):
 with tempfile.TemporaryDirectory() as td:
  p=Path(td)/"x.json";p.write_text(json.dumps(d))
  cmd=[sys.executable,str(V),str(p)]
  if census is not None:
   c=Path(td)/"census.json";c.write_text(json.dumps(census));cmd+=["--localshader-census",str(c)]
  return subprocess.run(cmd,capture_output=True,text=True)

r=run(base);assert r.returncode==0,(r.stdout,r.stderr)
for key,val in [("engine_semantic","bone_buffer"),("runtime_writer","guessed_writer"),("universal_record_schema","DQ_PAIR")]:
 d=json.loads(json.dumps(base));d["programs"][0][key]=val;r=run(d);assert r.returncode!=0 and "promoted" in r.stderr+r.stdout,(key,r.stdout,r.stderr)
d=json.loads(json.dumps(base));d["programs"][0]["consumer_record_structure"]="UNIVERSAL_API10";r=run(d);assert r.returncode!=0 and "universal schema" in r.stderr+r.stdout

# Cross-stage population relationship must be proven against the exact-style
# LocalShader census, not asserted from a denominator alone.
cross=json.loads(json.dumps(base))
cross["status"]="SOURCE_CLOSED_CROSS_STAGE_REFERENCE_ONLY"
cross["programs"][0]["source_hardware_stage"]="VertexShader"
cross["coverage"]={"classified_cross_stage_programs":1,"localshader_api10_program_denominator":39,"localshader_membership_overlap":0,"localshader_programs_classified_by_this_manifest":0,"classification_complete_for_localshader":False}
cross["population_relation"]={"exact_sha256_overlap_count":0,"conclusion":"DISJOINT_GCN_POPULATIONS"}
census={"schema":"d1_gcn_localshader_api10_access_family_census/v2","status":"D1_GCN_LOCALSHADER_API10_ACCESS_FAMILY_CENSUS_EXACT","violations":[],"programs":[{"gcn_sha256":f"{i:064x}"} for i in range(1,40)]}
r=run(cross,census);assert r.returncode==0,(r.stdout,r.stderr)
r=run(cross);assert r.returncode!=0 and "requires LocalShader census" in r.stderr+r.stdout
bad=json.loads(json.dumps(census));bad["programs"][0]["gcn_sha256"]="a"*64
r=run(cross,bad);assert r.returncode!=0 and "LocalShader overlap" in r.stderr+r.stdout
print("API10_CONSUMER_CLASSIFIER_SELFTEST_GREEN")
