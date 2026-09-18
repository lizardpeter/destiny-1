#!/usr/bin/env python3
"""Fail-closed validator for future Destiny 1 LocalShader API10 runtime captures.

This tool intentionally proves no engine semantic.  It validates that a capture corpus
covers the frozen source-closed access families before runtime-writer conclusions are
allowed to generalize across the retail LocalShader population.
"""
import argparse, json, sys
from pathlib import Path

EXPECTED_FAMILIES = {
    (3, "s[8:11]"),
    (6, "s[8:11]"),
    (8, "s[12:15]"),
    (8, "s[8:11]"),
    (12, "s[12:15]"),
    (12, "s[8:11]"),
}
EXPECTED_COVERAGE = {"program_count":39, "wrapper_count":56, "material_occurrence_count":3386}


def die(msg):
    raise SystemExit("FAIL: " + msg)


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--frozen", required=True)
    ap.add_argument("--captures", required=True)
    ap.add_argument("--out")
    a=ap.parse_args()
    frozen=load(a.frozen); captures=load(a.captures)
    if frozen.get("status") != "D1_GCN_LOCALSHADER_API10_ACCESS_FAMILY_CENSUS_EXACT":
        die("frozen census status is not exact")
    cov=frozen.get("coverage",{})
    for k,v in EXPECTED_COVERAGE.items():
        if cov.get(k) != v: die(f"frozen {k} drift: {cov.get(k)!r} != {v}")
    fam={(int(x["tbuffer_instruction_count"]), x["descriptor_window"]) for x in frozen.get("families",[])}
    if fam != EXPECTED_FAMILIES: die(f"frozen family drift: {sorted(fam)}")
    rows=captures.get("captures")
    if not isinstance(rows,list): die("captures must be a list")
    seen=set(); validated=[]
    for i,r in enumerate(rows):
        for key in ("program_id","descriptor_window","tbuffer_instruction_count","descriptor_dwords","evidence"):
            if key not in r: die(f"capture[{i}] missing {key}")
        family=(int(r["tbuffer_instruction_count"]),r["descriptor_window"])
        if family not in EXPECTED_FAMILIES: die(f"capture[{i}] unknown family {family}")
        d=r["descriptor_dwords"]
        if not (isinstance(d,list) and len(d)==4 and all(isinstance(x,int) and 0<=x<=0xffffffff for x in d)):
            die(f"capture[{i}] descriptor_dwords must be four exact u32 values")
        ev=r["evidence"]
        if not isinstance(ev,dict) or not ev.get("source") or not ev.get("sha256"):
            die(f"capture[{i}] requires source and sha256 evidence provenance")
        # Runtime semantics may only be asserted with an explicit writer trace and backing-byte provenance.
        if r.get("engine_semantic") not in (None,"WITHHELD"):
            if not ev.get("writer_trace") or not ev.get("backing_bytes"):
                die(f"capture[{i}] semantic asserted without writer_trace + backing_bytes")
        seen.add(family); validated.append(r["program_id"])
    missing=sorted(EXPECTED_FAMILIES-seen)
    result={
      "schema":"d1_localshader_api10_capture_gate/v1",
      "status":"D1_LOCALSHADER_API10_CAPTURE_COVERAGE_EXACT" if not missing else "D1_LOCALSHADER_API10_CAPTURE_COVERAGE_INCOMPLETE",
      "validated_capture_count":len(rows),
      "covered_families":[{"tbuffer_instruction_count":x,"descriptor_window":w} for x,w in sorted(seen)],
      "missing_families":[{"tbuffer_instruction_count":x,"descriptor_window":w} for x,w in missing],
      "semantic_boundary":{"runtime_writer":"WITHHELD_UNLESS_PRIMARY_TRACE","backing_allocation":"WITHHELD_UNLESS_PRIMARY_BYTES","engine_semantic":"WITHHELD_UNLESS_BOTH"}
    }
    if a.out: Path(a.out).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))
    if missing: return 2
    return 0
if __name__=="__main__": sys.exit(main())
