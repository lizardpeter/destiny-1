#!/usr/bin/env python3
"""Fail-closed audit of what the checked-in repository can classify for API10.

This intentionally distinguishes source-closed membership (39 exact GCN) from
checked-in semantic handlers. Searchability is not evidence of absence from
retail; it is an availability gate for the next offline/source-closed step.
"""
import argparse,json,re
from pathlib import Path
SHA=re.compile(r"\b[0-9a-f]{64}\b")
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--root",type=Path,default=Path("."));ap.add_argument("--classification",type=Path,required=True);ap.add_argument("-o","--out",type=Path,required=True);a=ap.parse_args()
 c=json.loads(a.classification.read_text());known={x["gcn_sha256"] for x in c["programs"]}
 hits={}
 for p in sorted((a.root/"tools").glob("*.py")):
  t=p.read_text(errors="replace")
  if "ImmConstBuffer" not in t or "10" not in t:continue
  hs=sorted(set(SHA.findall(t)))
  for h in hs:hits.setdefault(h,[]).append(str(p))
 classifiable=sorted(known & set(hits));extra=sorted(set(hits)-known)
 out={"schema":"d1_api10_checked_in_semantic_source_audit/v1","status":"D1_API10_CHECKED_IN_SEMANTIC_SOURCE_AUDIT_EXACT",
 "classified_manifest_programs":len(known),"classified_programs_with_checked_in_handlers":len(classifiable),
 "classified_gcn_sha256":classifiable,"additional_checked_in_candidate_sha256":extra,
 "global_source_closed_api10_program_denominator":39,
 "finding":"Checked-in semantic handlers expose the currently classified API10 programs, but do not provide the remaining source-closed 39-member disassemblies as repository files.",
 "next_evidence_required":"Recover/reconstruct the frozen 39-program membership/disassembly producer output, or obtain primary runtime capture. Do not infer roles for unmaterialized members.",
 "evidence_class":"REPOSITORY_AVAILABILITY_AUDIT_NOT_RETAIL_SEMANTIC_PROOF"}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+"\n");print(json.dumps(out,indent=2))
if __name__=="__main__":main()
