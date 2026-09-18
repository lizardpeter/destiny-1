#!/usr/bin/env python3
"""Fail-closed validator for exact API10 consumer-role classifications.

A classification may describe instruction-level consumer structure only.
Runtime writer, backing allocation, universal record schema, engine buffer name,
and engine semantic remain forbidden. Cross-stage reference manifests must also
prove their population relationship to the exact LocalShader census.
"""
import argparse,json,re
from pathlib import Path
HEX64=re.compile(r"^[0-9a-f]{64}$")
WITHHELD={"runtime_writer","backing_allocation","universal_record_schema","engine_buffer_name","engine_semantic"}
WINDOWS={"s[8:11]","s[12:15]"}

def die(s): raise SystemExit("API10_CONSUMER_CLASS_INVALID: "+s)
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("classification",type=Path)
 ap.add_argument("--localshader-census",type=Path)
 a=ap.parse_args()
 d=json.loads(a.classification.read_text())
 if d.get("schema")!="d1_api10_consumer_classification/v1":die("schema")
 rows=d.get("programs")
 if not isinstance(rows,list) or not rows:die("programs")
 seen=set()
 for i,r in enumerate(rows):
  h=r.get("gcn_sha256","")
  if not HEX64.match(h) or h in seen:die(f"program {i} identity")
  seen.add(h)
  if r.get("evidence_class") not in {"EXACT_NATIVE_GCN","PRIMARY_RETAIL_RUNTIME"}:die(f"program {i} evidence class")
  if r.get("descriptor_window") not in WINDOWS:die(f"program {i} descriptor window")
  if not r.get("consumer_record_structure") or not r.get("consumer_math_role"):die(f"program {i} role")
  if r.get("consumer_record_structure")=="UNIVERSAL_API10":die(f"program {i} universal schema")
  for k in WITHHELD:
   if r.get(k,"WITHHELD")!="WITHHELD":die(f"program {i} promoted {k}")
 b=d.get("semantic_boundary",{})
 for k in WITHHELD:
  if b.get(k)!="WITHHELD":die("semantic boundary "+k)

 overlap=None
 if d.get("status")=="SOURCE_CLOSED_CROSS_STAGE_REFERENCE_ONLY":
  if not a.localshader_census:die("cross-stage manifest requires LocalShader census")
  c=json.loads(a.localshader_census.read_text())
  if c.get("schema")!="d1_gcn_localshader_api10_access_family_census/v2" or c.get("status")!="D1_GCN_LOCALSHADER_API10_ACCESS_FAMILY_CENSUS_EXACT" or c.get("violations"):die("LocalShader census")
  local={x.get("gcn_sha256") for x in c.get("programs",[])}
  if len(local)!=39:die("LocalShader denominator")
  overlap=len(seen & local)
  cov=d.get("coverage",{})
  if cov.get("classified_cross_stage_programs")!=len(rows):die("cross-stage classified count")
  if cov.get("localshader_api10_program_denominator")!=39:die("LocalShader coverage denominator")
  if cov.get("localshader_membership_overlap")!=overlap:die("LocalShader overlap")
  if cov.get("localshader_programs_classified_by_this_manifest")!=overlap:die("LocalShader classified count")
  if cov.get("classification_complete_for_localshader") is not False:die("LocalShader completion gate")
  rel=d.get("population_relation",{})
  if rel.get("exact_sha256_overlap_count")!=overlap:die("population relation overlap")
  expected="DISJOINT_GCN_POPULATIONS" if overlap==0 else "OVERLAPPING_GCN_POPULATIONS"
  if rel.get("conclusion")!=expected:die("population relation conclusion")
  if any(r.get("source_hardware_stage")!="VertexShader" for r in rows):die("cross-stage source hardware stage")

 print(json.dumps({"status":"D1_API10_CONSUMER_CLASSIFICATION_VALID","program_count":len(rows),"localshader_membership_overlap":overlap,"gcn_sha256":sorted(seen),"semantic_boundary":{k:"WITHHELD" for k in sorted(WITHHELD)}},indent=2))
if __name__=="__main__":main()
