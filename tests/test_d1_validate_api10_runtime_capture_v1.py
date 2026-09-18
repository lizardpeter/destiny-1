#!/usr/bin/env python3
import hashlib,json,struct,subprocess,sys,tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
VALIDATOR=ROOT/"tools/d1_validate_api10_runtime_capture_v1.py"

def run(doc):
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/"capture.json"; p.write_text(json.dumps(doc))
        return subprocess.run([sys.executable,str(VALIDATOR),str(p)],text=True,capture_output=True)

raw=b"\x00\x01\x02\x03"
writer_raw=b"\xc0\xde\x10\x00\x01\x02\x03\x04"
dwords=[0,1,2,3]
descriptor_raw=struct.pack("<4I",*dwords)
sample={
 "gcn_sha256":"0"*64,
 "membership_proof":"SOURCE_CLOSED_39_MEMBER_SET",
 "consumer_stage":"LOCAL_SHADER",
 "consumer_locator":"fixture-draw-0",
 "consumer_record_structure":"CAPTURE_SPECIFIC_WITHHELD_NAME",
 "descriptor_window":"s[12:15]",
 "tbuffer_instruction_count":8,
 "descriptor_dwords":dwords,
 "descriptor_bytes_hex":descriptor_raw.hex(),
 "writer":{"evidence_class":"PRIMARY_RUNTIME","raw_bytes_hex":writer_raw.hex(),"raw_bytes_sha256":hashlib.sha256(writer_raw).hexdigest(),"capture_locator":"fixture-only"},
 "backing":{"evidence_class":"PRIMARY_RUNTIME","bytes_hex":raw.hex(),"sha256":hashlib.sha256(raw).hexdigest(),"length":len(raw),"descriptor_range_relation":"PROVEN"}
}
base={"schema":"d1_ps4_api10_runtime_capture/v1","engine_semantic":"WITHHELD","universal_record_schema":"WITHHELD","samples":[sample]}

r=run(base)
assert r.returncode==0 and "PARTIAL_VALID" in r.stdout,(r.stdout,r.stderr)

def rejects(mutator,needle):
    bad=json.loads(json.dumps(base)); mutator(bad); r=run(bad)
    assert r.returncode!=0 and needle in (r.stdout+r.stderr),(r.stdout,r.stderr)

rejects(lambda d:d.__setitem__("engine_semantic","guessed_name"),"engine semantic must remain WITHHELD")
rejects(lambda d:d.__setitem__("universal_record_schema","DQ_PAIR"),"universal record schema must remain WITHHELD")
rejects(lambda d:d["samples"][0].__setitem__("consumer_record_structure","UNIVERSAL_API10"),"consumer record structure")
rejects(lambda d:d["samples"][0].pop("consumer_stage"),"consumer stage")
rejects(lambda d:d["samples"][0].__setitem__("consumer_stage","VERTEX_SHADER"),"consumer stage")
rejects(lambda d:d["samples"][0].pop("consumer_locator"),"consumer locator")
rejects(lambda d:d["samples"][0].__setitem__("descriptor_dwords",[0,1,2]),"descriptor dwords")
rejects(lambda d:d["samples"][0].__setitem__("descriptor_bytes_hex","00"*15),"descriptor raw bytes length")
rejects(lambda d:d["samples"][0].__setitem__("descriptor_bytes_hex",struct.pack("<4I",0,1,2,4).hex()),"descriptor dwords/raw bytes mismatch")
rejects(lambda d:d["samples"][0]["backing"].__setitem__("sha256","f"*64),"backing sha256")
rejects(lambda d:d["samples"][0]["backing"].__setitem__("bytes_hex",""),"backing bytes empty")
rejects(lambda d:d["samples"][0]["writer"].pop("raw_bytes_hex"),"writer raw bytes")
rejects(lambda d:d["samples"][0]["writer"].__setitem__("raw_bytes_hex","00"),"writer raw bytes sha256")
rejects(lambda d:d["samples"][0]["writer"].__setitem__("raw_bytes_sha256","not-a-sha"),"writer raw bytes sha256")

# bool is an int subclass in Python; descriptor dwords must still be literal uint32s.
rejects(lambda d:d["samples"][0].__setitem__("descriptor_dwords",[False,1,2,3]),"descriptor dwords")

print("API10_RUNTIME_CAPTURE_VALIDATOR_SELFTEST_GREEN")
