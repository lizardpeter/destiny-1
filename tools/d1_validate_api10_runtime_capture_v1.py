#!/usr/bin/env python3
"""Fail-closed validator for API10 primary runtime captures.

A capture is evidence only when it ties an exact source-closed program identity
to the consuming stage/window, four raw descriptor dwords, primary writer
provenance, and exact backing bytes. Engine semantic is intentionally outside
this validator.
"""
import argparse, hashlib, json
from pathlib import Path

WINDOWS={"s[12:15]","s[8:11]"}
COUNTS={3,6,8,12}

def die(msg):
    raise SystemExit("API10_RUNTIME_CAPTURE_INVALID: "+msg)

def sha256_bytes_hex(s):
    try: b=bytes.fromhex(s)
    except ValueError: die("backing_bytes_hex")
    return hashlib.sha256(b).hexdigest(),len(b)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("capture",type=Path)
    a=ap.parse_args()
    d=json.loads(a.capture.read_text())
    if d.get("schema")!="d1_ps4_api10_runtime_capture/v1": die("schema")
    if d.get("engine_semantic") not in (None,"WITHHELD"): die("engine semantic must remain WITHHELD")\n    if d.get("universal_record_schema") not in (None,"WITHHELD"): die("universal record schema must remain WITHHELD")
    samples=d.get("samples")
    if not isinstance(samples,list) or not samples: die("samples")
    seen_counts=set(); seen_windows=set(); seen_programs=set()
    for i,s in enumerate(samples):
        p=s.get("gcn_sha256","")
        if len(p)!=64 or any(c not in "0123456789abcdef" for c in p): die(f"sample {i} gcn_sha256")
        if p in seen_programs: die(f"sample {i} duplicate program")
        seen_programs.add(p)
        if s.get("membership_proof")!="SOURCE_CLOSED_39_MEMBER_SET": die(f"sample {i} membership")\n        if not s.get("consumer_record_structure") or s.get("consumer_record_structure")=="UNIVERSAL_API10": die(f"sample {i} consumer record structure")
        w=s.get("descriptor_window")
        if w not in WINDOWS: die(f"sample {i} descriptor_window")
        seen_windows.add(w)
        n=s.get("tbuffer_instruction_count")
        if n not in COUNTS: die(f"sample {i} tbuffer count")
        seen_counts.add(n)
        dw=s.get("descriptor_dwords")
        if not isinstance(dw,list) or len(dw)!=4 or any(not isinstance(x,int) or x<0 or x>0xffffffff for x in dw): die(f"sample {i} descriptor dwords")
        writer=s.get("writer",{})
        if writer.get("evidence_class")!="PRIMARY_RUNTIME" or not writer.get("raw_bytes_sha256") or not writer.get("capture_locator"): die(f"sample {i} writer provenance")
        backing=s.get("backing",{})
        if backing.get("evidence_class")!="PRIMARY_RUNTIME" or not backing.get("bytes_hex"): die(f"sample {i} backing")
        h,nbytes=sha256_bytes_hex(backing["bytes_hex"])
        if h!=backing.get("sha256"): die(f"sample {i} backing sha256")
        if nbytes!=backing.get("length"): die(f"sample {i} backing length")
        if backing.get("descriptor_range_relation")!="PROVEN": die(f"sample {i} descriptor/backing relation")
    coverage={"instruction_counts":sorted(seen_counts),"descriptor_windows":sorted(seen_windows)}
    complete=seen_counts==COUNTS and seen_windows==WINDOWS
    print(json.dumps({"status":"D1_PS4_API10_PRIMARY_RUNTIME_CAPTURE_VALID" if complete else "D1_PS4_API10_PRIMARY_RUNTIME_CAPTURE_PARTIAL_VALID","sample_count":len(samples),"coverage":coverage,"runtime_writer":"EVIDENCED_PER_SAMPLE","backing_allocation":"EVIDENCED_PER_SAMPLE","universal_record_schema":"WITHHELD","engine_semantic":"WITHHELD"},indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
