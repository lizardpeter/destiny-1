#!/usr/bin/env python3
"""Fail-closed verifier for the exact API10 wrapper→native-program map."""
from __future__ import annotations
import argparse,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
MATERIAL_SHA="23415246337abdbb1543447e0123fa809027e3b9e94d5efee12a1476e7a2a113"

def die(s): raise SystemExit("API10_WRAPPER_NATIVE_MAP_INVALID: "+s)
def sha256(p:Path):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--map",type=Path,required=True)
 ap.add_argument("--index",type=Path,required=True)
 ap.add_argument("--material",type=Path)
 a=ap.parse_args()
 mp=json.loads(a.map.read_text()); idx=json.loads(a.index.read_text())
 if mp.get("status")!="D1_API10_WRAPPER_NATIVE_PROGRAM_MAP_EXACT":die("map status")
 if idx.get("status")!="D1_API10_PROGRAM_WRAPPER_MATERIAL_INDEX_EXACT":die("index status")
 bs=mp.get("bindings",[])
 if len(bs)!=56:die("binding denominator")
 if len({x["localshader_wrapper"] for x in bs})!=56:die("wrapper uniqueness")
 if len({x["native_program_reference"] for x in bs})!=56:die("native reference uniqueness")
 if len({x["gcn_sha256"] for x in bs})!=39:die("gcn denominator")
 hist=Counter()
 by_g=defaultdict(list)
 for x in bs:
  by_g[x["gcn_sha256"]].append(x)
 for rows in by_g.values():hist[len(rows)]+=1
 if dict(sorted(hist.items()))!={1:30,2:1,3:8}:die("gcn native-reference histogram")
 ix={x["gcn_sha256"]:x for x in idx["programs"]}
 if set(by_g)!=set(ix):die("index membership mismatch")
 for h,rows in by_g.items():
  if sorted(x["localshader_wrapper"] for x in rows)!=sorted(ix[h]["wrappers"]):die("wrapper set "+h)
  if any(x["descriptor_window"]!=ix[h]["descriptor_window"] or x["tbuffer_instruction_count"]!=ix[h]["tbuffer_instruction_count"] for x in rows):die("program metadata "+h)
 if a.material:
  if sha256(a.material)!=MATERIAL_SHA:die("material artifact hash")
  m=json.loads(a.material.read_text())
  if m.get("status")!="D1_GCN_LOCALSHADER_API10_MATERIAL_CHAIN_EXACT" or m.get("violations"):die("material status")
  src={}
  for r in m["bindings"]:
   k=r["localshader_wrapper"]
   v=(r["native_program_reference"],r["gcn_sha256"],r["descriptor_window"],r["tbuffer_instruction_count"])
   if k in src and src[k]!=v:die("material wrapper drift "+k)
   src[k]=v
  got={x["localshader_wrapper"]:(x["native_program_reference"],x["gcn_sha256"],x["descriptor_window"],x["tbuffer_instruction_count"]) for x in bs}
  if src!=got:die("material/map exact mismatch")
 b=mp.get("semantic_boundary",{})
 for k in ["wrapper_hardware_stage","tessellation_pipeline_ownership","runtime_api10_binding_owner","engine_semantic"]:
  if b.get(k)!="WITHHELD":die("semantic boundary "+k)
 print(json.dumps({"status":"D1_API10_WRAPPER_NATIVE_PROGRAM_MAP_VERIFIED","wrapper_count":56,"native_program_reference_count":56,"gcn_program_count":39,"material_bytes_verified":bool(a.material)},indent=2))
if __name__=="__main__":main()
