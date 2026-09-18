#!/usr/bin/env python3
"""Cross-reference the exact frozen LocalShader/API10 membership against checked-in text.

This is a repository-availability audit, not semantic proof. It never promotes
runtime writer/allocation/engine meaning. Its purpose is to identify exact GCN
members for which checked-in source, notes, evidence, or tests already contain
the frozen SHA-256 identity.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

SKIP_DIRS={".git",".venv","node_modules","target","dist","build","__pycache__"}
TEXT_SUFFIXES={".py",".json",".md",".yml",".yaml",".txt",".toml",".rs",".cs",".cpp",".c",".h",".hpp",".js",".ts"}

def iter_text(root:Path):
    for p in root.rglob("*"):
        if not p.is_file(): continue
        if any(part in SKIP_DIRS for part in p.parts): continue
        if p.suffix.lower() not in TEXT_SUFFIXES: continue
        try: yield p,p.read_text(errors="replace")
        except Exception: continue

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",type=Path,default=Path("."))
    ap.add_argument("--census",type=Path,required=True)
    ap.add_argument("-o","--out",type=Path,required=True)
    a=ap.parse_args()
    d=json.loads(a.census.read_text())
    if d.get("schema")!="d1_gcn_localshader_api10_access_family_census/v2": raise SystemExit("bad census schema")
    if d.get("status")!="D1_GCN_LOCALSHADER_API10_ACCESS_FAMILY_CENSUS_EXACT" or d.get("violations"): raise SystemExit("census not exact")
    programs=d.get("programs",[])
    if len(programs)!=39 or len({x.get("gcn_sha256") for x in programs})!=39: raise SystemExit("membership denominator")
    by={x["gcn_sha256"]:{**x,"paths":[]} for x in programs}
    census_rel=str(a.census)
    for p,text in iter_text(a.root):
        rel=str(p)
        if rel==census_rel or rel.endswith("/"+census_rel): continue
        for h,row in by.items():
            if h in text: row["paths"].append(rel)
    rows=[]
    for h in sorted(by):
        r=by[h]
        rows.append({
          "gcn_sha256":h,
          "descriptor_window":r["descriptor_window"],
          "tbuffer_instruction_count":r["tbuffer_instruction_count"],
          "wrapper_count":r["wrapper_count"],
          "checked_in_reference_count":len(r["paths"]),
          "checked_in_paths":sorted(set(r["paths"])),
        })
    found=[r for r in rows if r["checked_in_reference_count"]]
    out={
      "schema":"d1_api10_membership_repo_crossref/v1",
      "status":"D1_API10_MEMBERSHIP_REPO_CROSSREF_EXACT",
      "membership_program_count":39,
      "programs_with_checked_in_references":len(found),
      "programs_without_checked_in_references":39-len(found),
      "programs":rows,
      "evidence_class":"REPOSITORY_AVAILABILITY_AUDIT_NOT_RETAIL_SEMANTIC_PROOF",
      "semantic_boundary":{"runtime_writer":"WITHHELD","backing_allocation":"WITHHELD","engine_semantic":"WITHHELD"},
      "policy":"A textual reference is only a lead to inspect. It does not classify the program or establish runtime ownership/semantics."
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps({k:out[k] for k in ["status","membership_program_count","programs_with_checked_in_references","programs_without_checked_in_references","semantic_boundary"]},indent=2))
    return 0
if __name__=="__main__": raise SystemExit(main())
