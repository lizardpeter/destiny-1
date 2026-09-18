#!/usr/bin/env python3
"""Fail-closed API10 runtime-capture validator with exact census membership.

v1 accepted a self-asserted membership_proof string.  That is insufficient to
prove that a captured GCN belongs to the frozen 39-program census.  v2 requires
a separately supplied, hash-pinned census reconstruction containing the exact
39 program identities and refuses to promote captures until that input exists.
"""
import argparse, hashlib, json
from pathlib import Path

CENSUS_SHA256="7305071b52d427a7cc78da79fe795ca490fcf9edc05c06fbf1cc1c02ab9bfce8"
WINDOWS={"s[12:15]","s[8:11]"}
COUNTS={3,6,8,12}


def die(msg):
    raise SystemExit("API10_RUNTIME_CAPTURE_INVALID: "+msg)


def load_exact_membership(path: Path):
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=CENSUS_SHA256:
        die("membership census sha256 does not match frozen producer output")
    d=json.loads(raw)
    programs=d.get("programs")
    if not isinstance(programs,list) or len(programs)!=39:
        die("membership census must expose exact 39-program list")
    out={}
    for i,p in enumerate(programs):
        if not isinstance(p,dict): die(f"membership program {i}")
        h=p.get("gcn_sha256","")
        if len(h)!=64 or any(c not in "0123456789abcdef" for c in h):
            die(f"membership program {i} gcn_sha256")
        if h in out: die(f"membership duplicate program {h}")
        w=p.get("descriptor_window")
        n=p.get("tbuffer_instruction_count")
        if w not in WINDOWS or n not in COUNTS:
            die(f"membership program {i} access family")
        out[h]=(w,n)
    hist={n:sum(1 for _,pn in out.values() if pn==n) for n in COUNTS}
    if hist!={3:1,6:1,8:17,12:20}:
        die(f"membership instruction histogram {hist}")
    if {w for w,_ in out.values()}!=WINDOWS:
        die("membership descriptor-window coverage")
    return out


def backing_digest(s,i):
    try: b=bytes.fromhex(s)
    except ValueError: die(f"sample {i} backing_bytes_hex")
    return hashlib.sha256(b).hexdigest(),len(b)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("capture",type=Path)
    ap.add_argument("--membership-census",type=Path,required=True,
                    help="exact frozen producer output; SHA-256 is pinned")
    a=ap.parse_args()
    members=load_exact_membership(a.membership_census)
    d=json.loads(a.capture.read_text())
    if d.get("schema")!="d1_ps4_api10_runtime_capture/v1": die("schema")
    if d.get("engine_semantic") not in (None,"WITHHELD"): die("engine semantic must remain WITHHELD")
    if d.get("universal_record_schema") not in (None,"WITHHELD"): die("universal record schema must remain WITHHELD")
    samples=d.get("samples")
    if not isinstance(samples,list) or not samples: die("samples")
    seen=set(); seen_counts=set(); seen_windows=set()
    for i,s in enumerate(samples):
        p=s.get("gcn_sha256","")
        if p not in members: die(f"sample {i} is not in frozen 39-program census")
        if p in seen: die(f"sample {i} duplicate program")
        seen.add(p)
        expected_window,expected_count=members[p]
        w=s.get("descriptor_window"); n=s.get("tbuffer_instruction_count")
        if w!=expected_window: die(f"sample {i} descriptor_window disagrees with census")
        if n!=expected_count: die(f"sample {i} tbuffer count disagrees with census")
        seen_windows.add(w); seen_counts.add(n)
        if not s.get("consumer_record_structure") or s.get("consumer_record_structure")=="UNIVERSAL_API10":
            die(f"sample {i} consumer record structure")
        dw=s.get("descriptor_dwords")
        if not isinstance(dw,list) or len(dw)!=4 or any(not isinstance(x,int) or x<0 or x>0xffffffff for x in dw):
            die(f"sample {i} descriptor dwords")
        writer=s.get("writer",{})
        if writer.get("evidence_class")!="PRIMARY_RUNTIME" or not writer.get("raw_bytes_sha256") or not writer.get("capture_locator"):
            die(f"sample {i} writer provenance")
        backing=s.get("backing",{})
        if backing.get("evidence_class")!="PRIMARY_RUNTIME" or not backing.get("bytes_hex"):
            die(f"sample {i} backing")
        h,nbytes=backing_digest(backing["bytes_hex"],i)
        if h!=backing.get("sha256"): die(f"sample {i} backing sha256")
        if nbytes!=backing.get("length"): die(f"sample {i} backing length")
        if backing.get("descriptor_range_relation")!="PROVEN": die(f"sample {i} descriptor/backing relation")
    complete=seen_counts==COUNTS and seen_windows==WINDOWS
    print(json.dumps({
        "status":"D1_PS4_API10_PRIMARY_RUNTIME_CAPTURE_VALID" if complete else "D1_PS4_API10_PRIMARY_RUNTIME_CAPTURE_PARTIAL_VALID",
        "sample_count":len(samples),
        "membership":"EXACT_FROZEN_39_PROGRAM_CENSUS_SHA256_PINNED",
        "coverage":{"instruction_counts":sorted(seen_counts),"descriptor_windows":sorted(seen_windows)},
        "runtime_writer":"EVIDENCED_PER_SAMPLE","backing_allocation":"EVIDENCED_PER_SAMPLE",
        "universal_record_schema":"WITHHELD","engine_semantic":"WITHHELD"},indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
