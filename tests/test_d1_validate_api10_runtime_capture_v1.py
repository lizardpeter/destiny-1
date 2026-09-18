#!/usr/bin/env python3
import hashlib,json,subprocess,sys,tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
VALIDATOR=ROOT/"tools/d1_validate_api10_runtime_capture_v1.py"

def run(doc):
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/"capture.json"; p.write_text(json.dumps(doc))
        return subprocess.run([sys.executable,str(VALIDATOR),str(p)],text=True,capture_output=True)

raw=b"\x00\x01\x02\x03"
sample={
 "gcn_sha256":"0"*64,
 "membership_proof":"SOURCE_CLOSED_39_MEMBER_SET",\n "consumer_record_structure":"CAPTURE_SPECIFIC_WITHHELD_NAME",
 "descriptor_window":"s[12:15]",
 "tbuffer_instruction_count":8,
 "descriptor_dwords":[0,1,2,3],
 "writer":{"evidence_class":"PRIMARY_RUNTIME","raw_bytes_sha256":"1"*64,"capture_locator":"fixture-only"},
 "backing":{"evidence_class":"PRIMARY_RUNTIME","bytes_hex":raw.hex(),"sha256":hashlib.sha256(raw).hexdigest(),"length":len(raw),"descriptor_range_relation":"PROVEN"}
}
base={"schema":"d1_ps4_api10_runtime_capture/v1","engine_semantic":"WITHHELD","universal_record_schema":"WITHHELD","samples":[sample]}

r=run(base)
assert r.returncode==0 and "PARTIAL_VALID" in r.stdout,(r.stdout,r.stderr)

bad=json.loads(json.dumps(base)); bad["engine_semantic"]="guessed_name"
r=run(bad)
assert r.returncode!=0 and "engine semantic must remain WITHHELD" in (r.stdout+r.stderr),(r.stdout,r.stderr)

bad=json.loads(json.dumps(base)); bad["universal_record_schema"]="DQ_PAIR"\nr=run(bad)\nassert r.returncode!=0 and "universal record schema must remain WITHHELD" in (r.stdout+r.stderr),(r.stdout,r.stderr)\n\nbad=json.loads(json.dumps(base)); bad["samples"][0]["consumer_record_structure"]="UNIVERSAL_API10"\nr=run(bad)\nassert r.returncode!=0 and "consumer record structure" in (r.stdout+r.stderr),(r.stdout,r.stderr)\n\nbad=json.loads(json.dumps(base)); bad["samples"][0]["descriptor_dwords"]=[0,1,2]
r=run(bad)
assert r.returncode!=0 and "descriptor dwords" in (r.stdout+r.stderr),(r.stdout,r.stderr)

bad=json.loads(json.dumps(base)); bad["samples"][0]["backing"]["sha256"]="f"*64
r=run(bad)
assert r.returncode!=0 and "backing sha256" in (r.stdout+r.stderr),(r.stdout,r.stderr)

print("API10_RUNTIME_CAPTURE_VALIDATOR_SELFTEST_GREEN")
