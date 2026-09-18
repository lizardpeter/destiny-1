#!/usr/bin/env python3
"""Fail-closed verifier for the exact API10 OrbShdr usage-layout bifurcation."""
from __future__ import annotations
import argparse,hashlib,json
from collections import Counter
from pathlib import Path

USAGE_SHA="6c6c07d03ed06d8b53693326cbabd9fde7c7a2f7b0c41e02939e700cf4f21127"
EXPECTED={
 "s[12:15]":{
   "program_count":26,"wrapper_count":40,"material_occurrence_count":819,
   "tbuffer_total":260,"hist":{8:13,12:13},
   "signature":((18,0,0),(23,0,2),(27,1,6),(2,0,8),(2,10,12),(2,11,16)),
 },
 "s[8:11]":{
   "program_count":13,"wrapper_count":16,"material_occurrence_count":2567,
   "tbuffer_total":125,"hist":{3:1,6:1,8:4,12:7},
   "signature":((18,0,0),(23,0,2),(2,10,8),(2,11,12)),
 }
}

def die(s): raise SystemExit("API10_USAGE_LAYOUT_BIFURCATION_INVALID: "+s)
def sha256(p:Path):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--census",type=Path,required=True)
 ap.add_argument("--index",type=Path,required=True)
 ap.add_argument("--evidence",type=Path,required=True)
 ap.add_argument("--usage",type=Path)
 a=ap.parse_args()
 census=json.loads(a.census.read_text()); idx=json.loads(a.index.read_text()); ev=json.loads(a.evidence.read_text())
 if census.get("status")!="D1_GCN_LOCALSHADER_API10_ACCESS_FAMILY_CENSUS_EXACT":die("census status")
 if idx.get("status")!="D1_API10_PROGRAM_WRAPPER_MATERIAL_INDEX_EXACT":die("index status")
 if ev.get("status")!="D1_API10_USAGE_LAYOUT_BIFURCATION_EXACT":die("evidence status")
 if len(census.get("programs",[]))!=39 or len(idx.get("programs",[]))!=39:die("program denominator")
 by_idx={x["gcn_sha256"]:x for x in idx["programs"]}
 by_c={x["gcn_sha256"]:x for x in census["programs"]}
 if set(by_idx)!=set(by_c):die("membership identity mismatch")
 for win,e in EXPECTED.items():
  rows=[x for x in idx["programs"] if x["descriptor_window"]==win]
  if len(rows)!=e["program_count"]:die(win+" program count")
  if sum(x["wrapper_count"] for x in rows)!=e["wrapper_count"]:die(win+" wrapper count")
  if sum(x["material_occurrence_count"] for x in rows)!=e["material_occurrence_count"]:die(win+" material count")
  if sum(x["tbuffer_instruction_count"] for x in rows)!=e["tbuffer_total"]:die(win+" tbuffer total")
  if Counter(x["tbuffer_instruction_count"] for x in rows)!=Counter(e["hist"]):die(win+" histogram")
  for x in rows:
   c=by_c[x["gcn_sha256"]]
   if c["descriptor_window"]!=x["descriptor_window"] or c["tbuffer_instruction_count"]!=x["tbuffer_instruction_count"] or c["wrapper_count"]!=x["wrapper_count"]:die("census/index row drift")
 if a.usage:
  if sha256(a.usage)!=USAGE_SHA:die("usage artifact hash")
  u=json.loads(a.usage.read_text())
  if u.get("status")!="D1_GCN_LOCALSHADER_TBUFFER_USAGE_BINDING_EXACT" or u.get("violations"):die("usage status")
  up={x["gcn_sha256"]:x for x in u["programs"]}
  if set(up)!=set(by_idx):die("usage membership")
  for h,row in up.items():
   win=row["descriptor_window"]; sig=tuple(tuple(x[:3]) for x in row["usage_signature"])
   if sig!=EXPECTED[win]["signature"]:die("usage signature "+h)
   if sorted(row["wrappers"])!=sorted(by_idx[h]["wrappers"]):die("wrapper set "+h)
   if row["tbuffer_instruction_count"]!=by_idx[h]["tbuffer_instruction_count"]:die("tbuffer count "+h)
 b=ev.get("semantic_boundary",{})
 for k in ["api10_runtime_binding_owner","api0_semantic_relationship_to_api10","api11_engine_semantic","ptr_extended_user_data_engine_semantic","hardware_stage_ownership","tessellation_pipeline_ownership"]:
  if b.get(k)!="WITHHELD":die("semantic boundary "+k)
 print(json.dumps({"status":"D1_API10_USAGE_LAYOUT_BIFURCATION_VERIFIED","program_count":39,"wrapper_count":56,"material_occurrence_count":3386,"usage_bytes_verified":bool(a.usage)},indent=2))

if __name__=="__main__":main()
