#!/usr/bin/env python3
"""Recompute and fail-close the exact API10 program→wrapper→material index."""
from __future__ import annotations
import argparse,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path

CENSUS_SHA="7305071b52d427a7cc78da79fe795ca490fcf9edc05c06fbf1cc1c02ab9bfce8"
USAGE_SHA="6c6c07d03ed06d8b53693326cbabd9fde7c7a2f7b0c41e02939e700cf4f21127"
MATERIAL_SHA="23415246337abdbb1543447e0123fa809027e3b9e94d5efee12a1476e7a2a113"

def die(s): raise SystemExit("API10_PROGRAM_WRAPPER_MATERIAL_INDEX_INVALID: "+s)
def sha256(p:Path):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--census",type=Path,required=True)
 ap.add_argument("--index",type=Path,required=True)
 ap.add_argument("--usage",type=Path)
 ap.add_argument("--material",type=Path)
 a=ap.parse_args()
 if sha256(a.census)!=CENSUS_SHA:die("census byte hash")
 c=json.loads(a.census.read_text()); ix=json.loads(a.index.read_text())
 if c.get("status")!="D1_GCN_LOCALSHADER_API10_ACCESS_FAMILY_CENSUS_EXACT" or c.get("violations"):die("census status")
 if ix.get("status")!="D1_API10_PROGRAM_WRAPPER_MATERIAL_INDEX_EXACT":die("index status")
 rows=ix.get("programs",[])
 if len(rows)!=39 or len({x["gcn_sha256"] for x in rows})!=39:die("program denominator")
 if sum(x["wrapper_count"] for x in rows)!=56:die("wrapper denominator")
 if sum(x["material_occurrence_count"] for x in rows)!=3386:die("material denominator")
 cm={x["gcn_sha256"]:x for x in c["programs"]}
 im={x["gcn_sha256"]:x for x in rows}
 if set(cm)!=set(im):die("membership identities")
 for h,x in im.items():
  z=cm[h]
  for k in ["descriptor_window","tbuffer_instruction_count","wrapper_count"]:
   if x[k]!=z[k]:die(f"census row drift {h} {k}")
 if ix.get("coverage",{}).get("serialized_material_stage_slot_counts")!={"VS":3386}:die("serialized slot count")
 b=ix.get("semantic_boundary",{})
 for k in ["localshader_hardware_stage","tessellation_pipeline_ownership","runtime_api10_binding_owner","descriptor_dwords","backing_allocation","engine_semantic"]:
  if b.get(k)!="WITHHELD":die("semantic boundary "+k)
 if b.get("serialized_material_stage_slot")!="PROVENANCE_ONLY_NOT_HARDWARE_STAGE":die("stage-slot boundary")
 if bool(a.usage)!=bool(a.material):die("usage and material must be supplied together")
 if a.usage:
  if sha256(a.usage)!=USAGE_SHA:die("usage hash")
  if sha256(a.material)!=MATERIAL_SHA:die("material hash")
  u=json.loads(a.usage.read_text()); m=json.loads(a.material.read_text())
  if u.get("status")!="D1_GCN_LOCALSHADER_TBUFFER_USAGE_BINDING_EXACT" or u.get("violations"):die("usage status")
  if m.get("status")!="D1_GCN_LOCALSHADER_API10_MATERIAL_CHAIN_EXACT" or m.get("violations"):die("material status")
  up={x["gcn_sha256"]:x for x in u["programs"]}
  mats=defaultdict(list)
  for x in m["bindings"]:mats[x["gcn_sha256"]].append(x)
  if set(up)!=set(im) or set(mats)!=set(im):die("producer membership")
  pair_u={(h,w) for h,p in up.items() for w in p["wrappers"]}
  pair_m={(x["gcn_sha256"],x["localshader_wrapper"]) for x in m["bindings"]}
  if pair_u!=pair_m or len(pair_u)!=56:die("program-wrapper exact join")
  if len({x["material"] for x in m["bindings"]})!=3386:die("material uniqueness")
  if len({x["material_logical_view"] for x in m["bindings"]})!=77:die("package denominator")
  if Counter(x["serialized_material_stage_slot"] for x in m["bindings"])!=Counter({"VS":3386}):die("serialized material slot")
  for h,x in im.items():
   rs=mats[h]; p=up[h]
   if sorted(x["wrappers"])!=sorted(p["wrappers"]):die("wrapper list "+h)
   if x["material_occurrence_count"]!=len(rs):die("material count "+h)
   if x["package_count"]!=len({r["material_logical_view"] for r in rs}):die("package count "+h)
   if x["serialized_material_stage_slots"]!=sorted({r["serialized_material_stage_slot"] for r in rs}):die("slot labels "+h)
 print(json.dumps({"status":"D1_API10_PROGRAM_WRAPPER_MATERIAL_INDEX_VERIFIED","program_count":39,"wrapper_count":56,"material_occurrence_count":3386,"package_count":77,"producer_bytes_verified":bool(a.usage)},indent=2))
if __name__=="__main__":main()
