#!/usr/bin/env python3
"""Fail-closed validator for Destiny 1 LocalShader API10 runtime captures.

A capture is useful only when it is bound to an exact program present in the frozen
source census. Family labels supplied by a capture are never trusted as authority.
No engine semantic is inferred here.
"""
import argparse, json, re, sys
from pathlib import Path

EXPECTED_FAMILIES={(3,"s[8:11]"),(6,"s[8:11]"),(8,"s[12:15]"),(8,"s[8:11]"),(12,"s[12:15]"),(12,"s[8:11]")}
EXPECTED_COVERAGE={"program_count":39,"wrapper_count":56,"material_occurrence_count":3386}
HEX64=re.compile(r"^[0-9a-fA-F]{64}$")

def die(msg): raise SystemExit("FAIL: "+msg)
def load(path):
    with open(path,"r",encoding="utf-8") as f:return json.load(f)
def canon_program_id(v): return str(v).strip().lower()
def exact_sha256(v): return isinstance(v,str) and HEX64.fullmatch(v) is not None

def require_primary_evidence(ev,label="primary evidence"):
    """Require durable identity for a primary evidence byte stream.

    A source label alone is not provenance.  The byte stream must carry an exact
    SHA-256 so later runs can prove they are validating the same evidence.
    """
    if not isinstance(ev,dict):die(f"{label} must be an object")
    if not isinstance(ev.get("source"),str) or not ev["source"].strip():die(f"{label} requires non-empty source")
    if not exact_sha256(ev.get("sha256")):die(f"{label} sha256 must be 64 hex digits")

def require_semantic_provenance(ev,i):
    """Semantic promotion needs independently hash-addressed writer + backing evidence."""
    for key in ("writer_trace","backing_bytes"):
        item=ev.get(key)
        require_primary_evidence(item,f"capture[{i}] {key}")
    # The two evidence objects must remain distinct provenance records.  This
    # prevents one opaque blob from being relabeled as both required proof legs.
    w,b=ev["writer_trace"],ev["backing_bytes"]
    if w["source"]==b["source"] and w["sha256"].lower()==b["sha256"].lower():
        die(f"capture[{i}] writer_trace and backing_bytes must be distinct evidence records")

def build_program_index(frozen):
    """Build exact program membership from the source-closed census."""
    rows=frozen.get("programs")
    if rows is None:return None
    if not isinstance(rows,list):die("frozen programs must be a list")
    idx={}
    for i,r in enumerate(rows):
        raw_pid=r.get("gcn_sha256",r.get("program_id"))
        if raw_pid is None:die(f"frozen programs[{i}] missing gcn_sha256")
        for k in ("tbuffer_instruction_count","descriptor_window"):
            if k not in r:die(f"frozen programs[{i}] missing {k}")
        pid=canon_program_id(raw_pid)
        if not HEX64.fullmatch(pid):die(f"frozen programs[{i}] identity is not an exact SHA-256")
        fam=(int(r["tbuffer_instruction_count"]),r["descriptor_window"])
        if fam not in EXPECTED_FAMILIES:die(f"frozen program {pid} has unknown family {fam}")
        if pid in idx:die(f"duplicate frozen program identity {pid}")
        idx[pid]=fam
    if len(idx)!=EXPECTED_COVERAGE["program_count"]:die(f"frozen program table drift: {len(idx)} != 39")
    return idx

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--frozen",required=True);ap.add_argument("--captures",required=True);ap.add_argument("--out");ap.add_argument("--allow-test-fixtures",action="store_true",help="permit TEST_FIXTURE_NOT_PRIMARY_EVIDENCE rows; never use for primary capture validation");a=ap.parse_args()
    frozen=load(a.frozen);captures=load(a.captures)
    if frozen.get("status")!="D1_GCN_LOCALSHADER_API10_ACCESS_FAMILY_CENSUS_EXACT":die("frozen census status is not exact")
    cov=frozen.get("coverage",{})
    for k,v in EXPECTED_COVERAGE.items():
        if cov.get(k)!=v:die(f"frozen {k} drift: {cov.get(k)!r} != {v}")
    fam={(int(x["tbuffer_instruction_count"]),x["descriptor_window"]) for x in frozen.get("families",[])}
    if fam!=EXPECTED_FAMILIES:die(f"frozen family drift: {sorted(fam)}")
    program_index=build_program_index(frozen)
    rows=captures.get("captures")
    if not isinstance(rows,list):die("captures must be a list")
    seen=set()
    for i,r in enumerate(rows):
        for key in ("program_id","descriptor_window","tbuffer_instruction_count","descriptor_dwords","evidence"):
            if key not in r:die(f"capture[{i}] missing {key}")
        pid=canon_program_id(r["program_id"]); claimed=(int(r["tbuffer_instruction_count"]),r["descriptor_window"])
        ev=r["evidence"]
        if not isinstance(ev,dict) or not ev.get("source") or not ev.get("sha256"):die(f"capture[{i}] requires source and sha256 evidence provenance")
        fixture=ev.get("source")=="TEST_FIXTURE_NOT_PRIMARY_EVIDENCE"
        if fixture:
            if not a.allow_test_fixtures:die(f"capture[{i}] test fixture rejected without explicit --allow-test-fixtures")
            family=claimed
        else:
            require_primary_evidence(ev,f"capture[{i}] primary evidence")
            if program_index is None:die("primary capture rejected: frozen evidence lacks exact program membership table")
            if pid not in program_index:die(f"capture[{i}] program_id {pid} is not in frozen exact census")
            family=program_index[pid]
            if claimed!=family:die(f"capture[{i}] family claim {claimed} disagrees with frozen program family {family}")
        if family not in EXPECTED_FAMILIES:die(f"capture[{i}] unknown family {family}")
        d=r["descriptor_dwords"]
        if not(isinstance(d,list) and len(d)==4 and all(isinstance(x,int) and not isinstance(x,bool) and 0<=x<=0xffffffff for x in d)):die(f"capture[{i}] descriptor_dwords must be four exact u32 values")
        if r.get("engine_semantic") not in (None,"WITHHELD"):
            if fixture:die(f"capture[{i}] test fixture may not assert engine semantic")
            require_semantic_provenance(ev,i)
        seen.add(family)
    missing=sorted(EXPECTED_FAMILIES-seen)
    result={"schema":"d1_localshader_api10_capture_gate/v1","status":"D1_LOCALSHADER_API10_CAPTURE_COVERAGE_EXACT" if not missing else "D1_LOCALSHADER_API10_CAPTURE_COVERAGE_INCOMPLETE","validated_capture_count":len(rows),"covered_families":[{"tbuffer_instruction_count":x,"descriptor_window":w} for x,w in sorted(seen)],"missing_families":[{"tbuffer_instruction_count":x,"descriptor_window":w} for x,w in missing],"primary_capture_membership_gate":"EXACT_GCN_SHA256_TABLE_REQUIRED","semantic_boundary":{"runtime_writer":"WITHHELD_UNLESS_HASHED_PRIMARY_TRACE","backing_allocation":"WITHHELD_UNLESS_HASHED_PRIMARY_BYTES","engine_semantic":"WITHHELD_UNLESS_BOTH_DISTINCT"}}
    if a.out:Path(a.out).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2));return 2 if missing else 0
if __name__=="__main__":sys.exit(main())
