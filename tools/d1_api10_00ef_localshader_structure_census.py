#!/usr/bin/env python3
"""Build an exact structural census of the 00EF API10 LocalShader corpus.

The census is deliberately non-semantic. It records exact GCN-visible API10
indexed-load topology, M0 writes, scalar-buffer load signatures, LDS write slots,
and per-record byte stride. It does not name the LDS record, API10/API11 data,
runtime owners, or tessellation pipeline roles.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from collections import Counter,defaultdict
from pathlib import Path

CENSUS_SHA="cec4e79ac0f42d152c87632688097df1176330b98864d2b014cec863b0e593ff"

def sha(p:Path)->str:
 return hashlib.sha256(p.read_bytes()).hexdigest()

def die(s): raise SystemExit("API10_00EF_STRUCTURE_CENSUS_INVALID: "+s)

def ds_slots(text:str):
 slots=set();lines=[]
 for line in text.splitlines():
  if "ds_write2_b32" not in line:continue
  lines.append(line.strip())
  m0=re.search(r"offset0:(\d+)",line);m1=re.search(r"offset1:(\d+)",line)
  slots.add(int(m0.group(1)) if m0 else 0)
  slots.add(int(m1.group(1)) if m1 else 1)
 return sorted(slots),lines

def main()->int:
 ap=argparse.ArgumentParser()
 ap.add_argument("--retail-census",type=Path,required=True)
 ap.add_argument("--disasm-dir",type=Path,required=True)
 ap.add_argument("-o","--out",type=Path,required=True)
 a=ap.parse_args()
 if sha(a.retail_census)!=CENSUS_SHA:die("retail census hash")
 src=json.loads(a.retail_census.read_text())
 if src.get("status")!="D1_API10_00EF_LOCALSHADER_RETAIL_CENSUS_EXACT":die("retail census status")
 if len(src.get("programs",[]))!=11:die("program denominator")

 rows=[];clusters=defaultdict(list)
 for r in sorted(src["programs"],key=lambda x:x["wrapper"]):
  p=a.disasm_dir/f'{r["wrapper"]}.s'
  if not p.is_file():die("missing disassembly "+r["wrapper"])
  if sha(p)!=r["disassembly_sha256"]:die("disassembly hash "+r["wrapper"])
  text=p.read_text()

  loads=[]
  for line in text.splitlines():
   if "tbuffer_load_format_xyzw" not in line:continue
   m=re.search(r"tbuffer_load_format_xyzw\s+([^,]+),\s*([^,]+),\s*(s\[\d+:\d+\])",line)
   if not m:die("unparsed TBUFFER "+r["wrapper"])
   loads.append({"result":m.group(1).strip(),"index":m.group(2).strip(),"descriptor_window":m.group(3)})
  if len(loads)!=r["tbuffer_instruction_count"]:die("TBUFFER count "+r["wrapper"])
  if any(x["descriptor_window"]!=r["descriptor_window"] for x in loads):die("TBUFFER window "+r["wrapper"])

  slots,ds=ds_slots(text)
  m0=[x.strip() for x in text.splitlines() if re.search(r"\bm0\b",x)]
  if m0!=[next((x.strip() for x in text.splitlines() if "s_mov_b32       m0, 0x10000" in x),"")]:
   die("unexpected M0 writes "+r["wrapper"])
  if not m0[0]:die("missing M0 write "+r["wrapper"])

  stride=None;stride_reg=None
  for line in text.splitlines():
   m=re.search(r"s_movk_i32\s+(s\d+),\s*0x(50|60)\b",line)
   if not m:continue
   reg=m.group(1);value=int(m.group(2),16)
   if re.search(rf"v_mul_lo_i32\s+v1,\s*v1,\s*{re.escape(reg)}\b",text):
    if stride is not None and stride!=value:die("ambiguous stride "+r["wrapper"])
    stride=value;stride_reg=reg
  if stride not in (80,96):die("LDS stride unresolved "+r["wrapper"])

  expected_slots=(list(range(15))+[16,17,18]) if stride==80 else (list(range(19))+[20,21,22])
  expected_unwritten=[15,19] if stride==80 else [19,23]
  if slots!=expected_slots:die(f'LDS slot set {r["wrapper"]}: {slots}')

  sb=[]
  for line in text.splitlines():
   if "s_buffer_load_" not in line:continue
   m=re.search(r"(s_buffer_load_\w+)\s+([^,]+),\s*(s\[\d+:\d+\]),\s*(0x[0-9a-f]+)",line)
   if m:sb.append({"opcode":m.group(1),"destination":m.group(2).strip(),"descriptor":m.group(3),"offset":m.group(4)})

  row={
   "wrapper":r["wrapper"],"native_program_reference":r["native_program_reference"],"gcn_sha256":r["gcn_sha256"],
   "descriptor_window":r["descriptor_window"],"tbuffer_instruction_count":r["tbuffer_instruction_count"],
   "tbuffer_result_sequence":[x["result"] for x in loads],
   "tbuffer_index_vgpr_sequence":[x["index"] for x in loads],
   "m0_write":"s_mov_b32 m0, 0x10000",
   "lds_record_stride_bytes":stride,"lds_stride_scalar_register":stride_reg,
   "lds_write_instruction_count":len(ds),"lds_written_dword_slots":slots,"lds_unwritten_dword_slots_within_record":expected_unwritten,
   "scalar_buffer_loads":sb,
  }
  sig=(row["descriptor_window"],row["tbuffer_instruction_count"],tuple(row["tbuffer_index_vgpr_sequence"]),stride,tuple(slots),
       tuple((x["opcode"],x["descriptor"],x["offset"]) for x in sb))
  clusters[sig].append(r["wrapper"])
  rows.append(row)

 cluster_rows=[]
 for i,(sig,wrappers) in enumerate(sorted(clusters.items(),key=lambda kv:(kv[0][0],kv[0][1],kv[1])),1):
  exemplar=next(x for x in rows if x["wrapper"]==wrappers[0])
  cluster_rows.append({
   "cluster_id":f"S{i:02d}","wrappers":sorted(wrappers),"program_count":len(wrappers),
   "descriptor_window":exemplar["descriptor_window"],"tbuffer_instruction_count":exemplar["tbuffer_instruction_count"],
   "tbuffer_index_vgpr_sequence":exemplar["tbuffer_index_vgpr_sequence"],
   "lds_record_stride_bytes":exemplar["lds_record_stride_bytes"],
   "lds_written_dword_slots":exemplar["lds_written_dword_slots"],
   "scalar_buffer_load_signature":[{"opcode":x["opcode"],"descriptor":x["descriptor"],"offset":x["offset"]} for x in exemplar["scalar_buffer_loads"]],
  })

 out={
  "schema":"d1_api10_00ef_localshader_structure_census/v1",
  "status":"D1_API10_00EF_LOCALSHADER_STRUCTURE_CENSUS_EXACT",
  "source":{"run_id":35388976901,"artifact_id":10565230330,"artifact_digest":"sha256:2196267519aca512a35f43073bbe1ab9cb19b22ad8f5379296e877d844fd400c","retail_census_sha256":CENSUS_SHA},
  "coverage":{"program_count":len(rows),"structural_cluster_count":len(cluster_rows),
    "descriptor_window_histogram":dict(sorted(Counter(x["descriptor_window"] for x in rows).items())),
    "tbuffer_instruction_histogram":{str(k):v for k,v in sorted(Counter(x["tbuffer_instruction_count"] for x in rows).items())},
    "lds_record_stride_histogram":{str(k):v for k,v in sorted(Counter(x["lds_record_stride_bytes"] for x in rows).items())},
    "m0_0x10000_program_count":sum(x["m0_write"]=="s_mov_b32 m0, 0x10000" for x in rows)},
  "programs":rows,"structural_clusters":cluster_rows,
  "cross_dimension_findings":{
    "80_byte_and_96_byte_records_both_exist":set(x["lds_record_stride_bytes"] for x in rows)=={80,96},
    "s8_11_contains_both_record_strides":{x["lds_record_stride_bytes"] for x in rows if x["descriptor_window"]=="s[8:11]"}=={80,96},
    "s12_15_contains_both_record_strides":{x["lds_record_stride_bytes"] for x in rows if x["descriptor_window"]=="s[12:15]"}=={80,96},
    "eight_tbuffer_contains_both_record_strides":{x["lds_record_stride_bytes"] for x in rows if x["tbuffer_instruction_count"]==8}=={80,96},
    "twelve_tbuffer_contains_both_record_strides":{x["lds_record_stride_bytes"] for x in rows if x["tbuffer_instruction_count"]==12}=={80,96}
  },
  "semantic_boundary":{"m0_numeric_write":"EXACT","lds_record_stride_and_written_slots":"EXACT","api10_indexed_load_structure":"EXACT",
    "m0_engine_meaning":"WITHHELD","lds_record_engine_name":"WITHHELD","hardware_tessellation_ownership":"WITHHELD",
    "runtime_writer":"WITHHELD","descriptor_dwords":"WITHHELD","backing_allocation":"WITHHELD","engine_semantic":"WITHHELD"},
  "policy":"Exact structural dimensions are intentionally kept independent. Descriptor window or TBUFFER count must not be used to infer LDS record shape, hardware pipeline ownership, runtime writer, or engine semantic."
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+"\n")
 print(json.dumps({"status":out["status"],"coverage":out["coverage"],"cross_dimension_findings":out["cross_dimension_findings"],"semantic_boundary":out["semantic_boundary"]},indent=2))
 return 0

if __name__=="__main__":raise SystemExit(main())
