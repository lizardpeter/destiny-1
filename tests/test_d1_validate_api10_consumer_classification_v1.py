#!/usr/bin/env python3
import json,subprocess,sys,tempfile
from pathlib import Path
V=Path(__file__).resolve().parents[1]/"tools/d1_validate_api10_consumer_classification_v1.py"
base={"schema":"d1_api10_consumer_classification/v1","programs":[{"gcn_sha256":"a"*64,"evidence_class":"EXACT_NATIVE_GCN","descriptor_window":"s[8:11]","consumer_record_structure":"capture-specific float4 records","consumer_math_role":"instruction-proven transform arithmetic","runtime_writer":"WITHHELD","backing_allocation":"WITHHELD","universal_record_schema":"WITHHELD","engine_buffer_name":"WITHHELD","engine_semantic":"WITHHELD"}],"semantic_boundary":{k:"WITHHELD" for k in ["runtime_writer","backing_allocation","universal_record_schema","engine_buffer_name","engine_semantic"]}}
def run(d):
 with tempfile.TemporaryDirectory() as td:
  p=Path(td)/"x.json";p.write_text(json.dumps(d))
  return subprocess.run([sys.executable,str(V),str(p)],capture_output=True,text=True)
r=run(base);assert r.returncode==0,(r.stdout,r.stderr)
for key,val in [("engine_semantic","bone_buffer"),("runtime_writer","guessed_writer"),("universal_record_schema","DQ_PAIR")]:
 d=json.loads(json.dumps(base));d["programs"][0][key]=val;r=run(d);assert r.returncode!=0 and "promoted" in r.stderr+r.stdout,(key,r.stdout,r.stderr)
d=json.loads(json.dumps(base));d["programs"][0]["consumer_record_structure"]="UNIVERSAL_API10";r=run(d);assert r.returncode!=0 and "universal schema" in r.stderr+r.stdout
print("API10_CONSUMER_CLASSIFIER_SELFTEST_GREEN")
