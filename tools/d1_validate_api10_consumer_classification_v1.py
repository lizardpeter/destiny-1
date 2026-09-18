#!/usr/bin/env python3
"""Fail-closed validator for source-closed API10 consumer-role classifications.

Classification is keyed by exact bounded native GCN SHA-256. It may describe
instruction-level consumer structure only. Runtime writer, backing allocation,
universal record schema, engine buffer name, and engine semantic are forbidden.
"""
import argparse,json,re
from pathlib import Path
HEX64=re.compile(r"^[0-9a-f]{64}$")
WITHHELD={"runtime_writer","backing_allocation","universal_record_schema","engine_buffer_name","engine_semantic"}
WINDOWS={"s[8:11]","s[12:15]"}

def die(s): raise SystemExit("API10_CONSUMER_CLASS_INVALID: "+s)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("classification",type=Path);a=ap.parse_args()
 d=json.loads(a.classification.read_text())
 if d.get("schema")!="d1_api10_consumer_classification/v1":die("schema")
 rows=d.get("programs")
 if not isinstance(rows,list) or not rows:die("programs")
 seen=set()
 for i,r in enumerate(rows):
  h=r.get("gcn_sha256","")
  if not HEX64.match(h) or h in seen:die(f"program {i} identity")
  seen.add(h)
  if r.get("evidence_class") not in {"EXACT_NATIVE_GCN","PRIMARY_RETAIL_RUNTIME"}:die(f"program {i} evidence class")
  if r.get("descriptor_window") not in WINDOWS:die(f"program {i} descriptor window")
  if not r.get("consumer_record_structure") or not r.get("consumer_math_role"):die(f"program {i} role")
  if r.get("consumer_record_structure")=="UNIVERSAL_API10":die(f"program {i} universal schema")
  for k in WITHHELD:
   if r.get(k,"WITHHELD")!="WITHHELD":die(f"program {i} promoted {k}")
 b=d.get("semantic_boundary",{})
 for k in WITHHELD:
  if b.get(k)!="WITHHELD":die("semantic boundary "+k)
 print(json.dumps({"status":"D1_API10_CONSUMER_CLASSIFICATION_VALID","program_count":len(rows),"gcn_sha256":sorted(seen),"semantic_boundary":{k:"WITHHELD" for k in sorted(WITHHELD)}},indent=2))
if __name__=="__main__":main()
