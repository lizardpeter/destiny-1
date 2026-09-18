#!/usr/bin/env python3
"""Prove API10 material→LocalShader package-topology from frozen exact bindings.

This is an identity/routing proof only. It demonstrates whether the material
package is the same Tiger package as the referenced LocalShader wrapper and
whether wrapper/native-program FileHashes resolve to the same package. It does
not assign semantic ownership to either package.
"""
from __future__ import annotations
import argparse,hashlib,json
from collections import Counter
from pathlib import Path
from d1_filehash import decode

MATERIAL_SHA="23415246337abdbb1543447e0123fa809027e3b9e94d5efee12a1476e7a2a113"

def sha256(p:Path):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()

def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument("material_chain",type=Path);ap.add_argument("-o","--out",type=Path,required=True);a=ap.parse_args()
 if sha256(a.material_chain)!=MATERIAL_SHA:raise SystemExit("material-chain byte hash drift")
 d=json.loads(a.material_chain.read_text())
 if d.get("status")!="D1_GCN_LOCALSHADER_API10_MATERIAL_CHAIN_EXACT" or d.get("violations"):raise SystemExit("material-chain not exact")
 rows=d.get("bindings",[])
 if len(rows)!=3386:raise SystemExit("material denominator")
 relation=Counter();by_window={};by_tbuffer={};wrapper_pkgs=Counter();pair_counts=Counter();mismatch=[]
 for r in rows:
  wp,_=decode(r["localshader_wrapper"]);np,_=decode(r["native_program_reference"]);mp=int(r["material_package_id"],16)
  if wp!=np:mismatch.append({"material":r["material"],"wrapper":r["localshader_wrapper"],"native":r["native_program_reference"],"wrapper_package":f"{wp:04X}","native_package":f"{np:04X}"})
  rel="SAME_PACKAGE" if mp==wp else "CROSS_PACKAGE"
  relation[rel]+=1;wrapper_pkgs[wp]+=1;pair_counts[(mp,wp)]+=1
  by_window.setdefault(r["descriptor_window"],Counter())[rel]+=1
  by_tbuffer.setdefault(str(r["tbuffer_instruction_count"]),Counter())[rel]+=1
 if mismatch:raise SystemExit(f"wrapper/native package mismatch count {len(mismatch)}")
 out={
  "schema":"d1_api10_material_wrapper_package_topology/v1",
  "status":"D1_API10_MATERIAL_WRAPPER_PACKAGE_TOPOLOGY_EXACT",
  "provenance":{"material_chain_artifact_id":10529319011,"material_chain_json_sha256":MATERIAL_SHA},
  "coverage":{
    "material_occurrence_count":len(rows),
    "same_package_occurrences":relation["SAME_PACKAGE"],
    "cross_package_occurrences":relation["CROSS_PACKAGE"],
    "unique_material_to_wrapper_package_pairs":len(pair_counts),
    "unique_wrapper_package_count":len(wrapper_pkgs),
    "wrapper_native_program_package_mismatch_count":0
  },
  "wrapper_package_ids":[f"{x:04X}" for x in sorted(wrapper_pkgs)],
  "descriptor_window_relation_counts":{k:dict(sorted(v.items())) for k,v in sorted(by_window.items())},
  "tbuffer_family_relation_counts":{k:dict(sorted(v.items())) for k,v in sorted(by_tbuffer.items(),key=lambda kv:int(kv[0]))},
  "recovery_rule":"Resolve LocalShader wrapper and native-program bytes from their FileHash-derived logical package family; material physical/logical package co-location is not a valid recovery assumption.",
  "semantic_boundary":{
    "filehash_package_routing":"EXACT",
    "wrapper_native_same_package":"EXACT",
    "material_package_semantic_ownership":"WITHHELD",
    "wrapper_package_semantic_ownership":"WITHHELD",
    "runtime_binding_owner":"WITHHELD",
    "engine_semantic":"WITHHELD"
  }
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+"\n")
 print(json.dumps(out,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
