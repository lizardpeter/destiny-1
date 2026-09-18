#!/usr/bin/env python3
"""Exact native-GCN dataflow proof for the rare 3/6-load API10 LocalShaders.

Inputs are frozen outputs of the retail logical-package recovery workflow.
The proof promotes instruction-level arithmetic and LDS write structure only.
Runtime descriptor contents/writer, backing allocation, skeleton/bone naming,
and tessellation ownership remain withheld.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path

EXPECTED={
 "probe_sha256":"28014ea55c5a4c1204b72e50232d06f11f54ef25f63caa5d465b041bde6d3ba2",
 "retail_proof_sha256":"657b604db09e5f399a1a1748f708f0f358e0e26419b1519a682a2c5d013b9106",
 "three":{
  "wrapper":"80A08667","native":"80A08668",
  "gcn":"2611323e1fd51d609701f16bb7a6ca11da116ace11be3861659d10813154828f",
  "disasm_sha256":"3869d3c727099a9e1f910786917195b46be0d9b30261aa0e014773e803c72262"
 },
 "six":{
  "wrapper":"80A0627B","native":"80A0627C",
  "gcn":"44643993ac626aa827f90578ad0b5b6c2adc1d78e0e888a761ffb0554aeb008c",
  "disasm_sha256":"212ffbbef3fac54a4432580e1dc3a89eab6546314f50b5a5f75898bdb5ae99d9"
 }
}

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def die(s):raise SystemExit("API10_RARE_LOCALSHADER_DATAFLOW_INVALID: "+s)

def need(text:str,items:list[str],label:str):
 for x in items:
  if x not in text:die(label+" missing "+x)

def ds_slots(text:str)->list[int]:
 slots=set()
 for line in text.splitlines():
  if "ds_write2_b32" not in line:continue
  m=re.search(r"offset0:(\d+)",line);n=re.search(r"offset1:(\d+)",line)
  if m: a=int(m.group(1))
  else: a=0
  if n: b=int(n.group(1))
  else: b=1
  slots|={a,b}
 return sorted(slots)

def main()->int:
 ap=argparse.ArgumentParser()
 ap.add_argument("--probe",type=Path,required=True)
 ap.add_argument("--retail-proof",type=Path,required=True)
 ap.add_argument("--three-disasm",type=Path,required=True)
 ap.add_argument("--six-disasm",type=Path,required=True)
 ap.add_argument("-o","--out",type=Path,required=True)
 a=ap.parse_args()
 if sha(a.probe)!=EXPECTED["probe_sha256"]:die("probe hash")
 if sha(a.retail_proof)!=EXPECTED["retail_proof_sha256"]:die("retail proof hash")
 if sha(a.three_disasm)!=EXPECTED["three"]["disasm_sha256"]:die("three disassembly hash")
 if sha(a.six_disasm)!=EXPECTED["six"]["disasm_sha256"]:die("six disassembly hash")

 probe=json.loads(a.probe.read_text());rp=json.loads(a.retail_proof.read_text())
 if probe.get("status")!="D1_REMOTE_PS4_SHADER_BINARY_PROBE_EXACT" or probe.get("violations"):die("probe status")
 if rp.get("status")!="D1_API10_RARE_LOCALSHADER_RETAIL_PROOF_EXACT":die("retail proof status")
 by={x["tag_hash"]:x for x in probe["shaders"]}
 for key in ("three","six"):
  e=EXPECTED[key];r=by.get(e["wrapper"])
  if not r:die(key+" wrapper absent")
  if r["payload_reference"]!=e["native"] or r["code_sha256"]!=e["gcn"]:die(key+" identity")
  if r["binary_info"]["stage"]!="LocalShader":die(key+" OrbShdr stage")
  usage=[(x["usage_name"],x["api_slot"],x["start_register"]) for x in r["usage"]["slots"]]
  if usage!=[("SubPtrFetchShader",0,0),("PtrVertexBufferTable",0,2),("ImmConstBuffer",10,8),("ImmConstBuffer",11,12)]:die(key+" usage")

 t3=a.three_disasm.read_text();t6=a.six_disasm.read_text()
 need(t3,[
  "s_mov_b32       m0, 0x10000",
  "v_mov_b32       v0, 0x3dcccccd",
  "s_mov_b32       s4, 0x46fffe00",
  "v_mac_f32       v0, s4, v7",
  "v_cvt_u32_f32   v0, v0",
  "v_mul_lo_u32    v0, v0, 3",
  "tbuffer_load_format_xyzw v[22:25], v0, s[8:11], 0 idxen",
  "v_add_i32       v2, vcc, 1, v0",
  "tbuffer_load_format_xyzw v[26:29], v2, s[8:11], 0 idxen",
  "v_add_i32       v0, vcc, 2, v0",
  "tbuffer_load_format_xyzw v[30:33], v0, s[8:11], 0 idxen",
  "s_buffer_load_dwordx4 s[0:3], s[12:15], 0x14",
  "s_buffer_load_dwordx4 s[0:3], s[12:15], 0x18",
  "s_buffer_load_dwordx4 s[0:3], s[12:15], 0x1c",
  "s_movk_i32      s0, 0x50",
  "v_mul_lo_i32    v1, v1, s0",
  "s_endpgm"
 ],"three")
 need(t6,[
  "v_mul_lo_u32    v0, v9, 3",
  "v_mul_lo_u32    v2, v8, 3",
  "v_add_i32       v3, vcc, 1, v0",
  "v_add_i32       v7, vcc, 1, v2",
  "v_add_i32       v9, vcc, 2, v0",
  "v_add_i32       v2, vcc, 2, v2",
  "tbuffer_load_format_xyzw v[26:29], v0, s[8:11], 0 idxen",
  "tbuffer_load_format_xyzw v[30:33], v3, s[8:11], 0 idxen",
  "tbuffer_load_format_xyzw v[34:37], v0, s[8:11], 0 idxen",
  "tbuffer_load_format_xyzw v[38:41], v7, s[8:11], 0 idxen",
  "tbuffer_load_format_xyzw v[42:45], v9, s[8:11], 0 idxen",
  "tbuffer_load_format_xyzw v[46:49], v2, s[8:11], 0 idxen",
  "v_cvt_f32_u32   v0, v11",
  "v_cvt_f32_u32   v2, v10",
  "v_mul_f32       v0, 0x3b808081, v0",
  "v_mul_f32       v2, 0x3b808081, v2",
  "s_buffer_load_dwordx4 s[0:3], s[12:15], 0x1c",
  "s_buffer_load_dwordx4 s[4:7], s[12:15], 0x14",
  "s_buffer_load_dwordx4 s[8:11], s[12:15], 0x18",
  "s_mov_b32       m0, 0x10000",
  "s_movk_i32      s0, 0x50",
  "v_mul_lo_i32    v1, v1, s0",
  "s_endpgm"
 ],"six")

 loads3=[x for x in t3.splitlines() if "tbuffer_load_format_xyzw" in x]
 loads6=[x for x in t6.splitlines() if "tbuffer_load_format_xyzw" in x]
 if len(loads3)!=3 or len(loads6)!=6:die("load denominators")
 if not all("s[8:11]" in x and "idxen" in x for x in loads3+loads6):die("API10 descriptor use")
 slots3=ds_slots(t3);slots6=ds_slots(t6)
 expected_slots=list(range(15))+[16,17,18]
 if slots3!=expected_slots or slots6!=expected_slots:die(f"LDS slot contract {slots3} {slots6}")

 out={
  "schema":"d1_api10_rare_localshader_dataflow/v1",
  "status":"D1_API10_RARE_LOCALSHADER_DATAFLOW_EXACT",
  "source_artifact":{"run_id":35388270542,"artifact_id":10564682786,"artifact_digest":"sha256:cf5b8b040e4e1ea27a6548eae573f8fbdb98ed6427d3c76d4354e2f68ba98871"},
  "programs":[
   {
    "wrapper":EXPECTED["three"]["wrapper"],"native_program_reference":EXPECTED["three"]["native"],"gcn_sha256":EXPECTED["three"]["gcn"],
    "orbshdr_stage":"LocalShader","api10_descriptor_window":"s[8:11]","api11_descriptor_window":"s[12:15]","tbuffer_instruction_count":3,
    "post_fetch_index_dataflow":{
      "source_lane":"v7",
      "exact_arithmetic":"selector = uint(0x3dcccccd + 0x46fffe00 * v7); base = 3 * selector",
      "api10_record_indices":["base","base+1","base+2"],
      "loaded_float4_registers":["v[22:25]","v[26:29]","v[30:33]"]
    },
    "consumer_structure":"one selected three-float4-row affine/basis transform",
    "instruction_level_relations":[
      "api11 offset 0x14 supplies a scalar scale plus xyz bias used to pre-affine source position lanes v4/v5/v6",
      "the three API10 rows transform that pre-affined position with row w components included",
      "the same API10 row xyz components transform two source 3-vectors and their cross product is multiplied by source lane v19",
      "api11 offsets 0x18 and 0x1c participate in two-coordinate affine arithmetic and a clamped scalar dot expression"
    ],
    "m0_write":"s_mov_b32 m0, 0x10000",
    "lds_output":{"record_stride_bytes":80,"record_index_lane":"v1","written_dword_slots":expected_slots,"unwritten_dword_slots":[15,19]}
   },
   {
    "wrapper":EXPECTED["six"]["wrapper"],"native_program_reference":EXPECTED["six"]["native"],"gcn_sha256":EXPECTED["six"]["gcn"],
    "orbshdr_stage":"LocalShader","api10_descriptor_window":"s[8:11]","api11_descriptor_window":"s[12:15]","tbuffer_instruction_count":6,
    "post_fetch_index_dataflow":{
      "selector_lanes":["v9","v8"],
      "api10_record_indices":["3*v9+0","3*v9+1","3*v9+2","3*v8+0","3*v8+1","3*v8+2"],
      "loaded_float4_registers_by_selector":[["v[26:29]","v[30:33]","v[42:45]"],["v[34:37]","v[38:41]","v[46:49]"]]
    },
    "blend_coefficient_dataflow":{
      "source_lanes":["v11","v10"],
      "conversion":"v_cvt_f32_u32",
      "exact_literal_bits":"0x3b808081",
      "role":"the two converted/scaled lanes multiply corresponding components of the two selected three-row records before pairwise accumulation"
    },
    "consumer_structure":"two selected three-float4-row transforms blended component-wise before affine/basis use",
    "instruction_level_relations":[
      "the blended row xyz components transform source 3-vectors v16..v18 and v20..v22",
      "their transformed-vector cross product is multiplied by source lane v23",
      "api11 offset 0x14 supplies a scalar scale plus xyz bias used before the blended affine position transform",
      "api11 offsets 0x18 and 0x1c participate in two-coordinate affine arithmetic and a clamped scalar dot expression"
    ],
    "m0_write":"s_mov_b32 m0, 0x10000",
    "lds_output":{"record_stride_bytes":80,"record_index_lane":"v1","written_dword_slots":expected_slots,"unwritten_dword_slots":[15,19]}
   }
  ],
  "shared_localshader_output_contract":{
    "lds_record_stride_bytes":80,
    "written_dword_slots":expected_slots,
    "unwritten_dword_slots":[15,19],
    "hardware_tessellation_consumer":"WITHHELD"
  },
  "semantic_boundary":{
    "api10_runtime_writer":"WITHHELD",
    "api10_descriptor_dwords":"WITHHELD",
    "api10_backing_allocation":"WITHHELD",
    "api10_engine_semantic":"WITHHELD",
    "api11_engine_semantic":"WITHHELD",
    "m0_engine_meaning":"WITHHELD",
    "lds_record_engine_name":"WITHHELD",
    "hardware_tessellation_ownership":"WITHHELD",
    "selector_engine_name":"WITHHELD"
  },
  "policy":"Only exact OrbShdr metadata, bounded GCN identity, ordered native arithmetic, descriptor-register use, and LDS writes are promoted. Transform/basis describes mathematical consumer structure; no bone/skeleton/tessellation/runtime-owner naming is assigned."
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+"\n")
 print(json.dumps({"status":out["status"],"programs":[{"wrapper":x["wrapper"],"gcn_sha256":x["gcn_sha256"],"consumer_structure":x["consumer_structure"],"lds_output":x["lds_output"]} for x in out["programs"]],"semantic_boundary":out["semantic_boundary"]},indent=2))
 return 0

if __name__=="__main__":raise SystemExit(main())
