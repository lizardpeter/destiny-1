#!/usr/bin/env python3
"""Fail-closed cross-proof for API10's instruction-level data role.

This does NOT name the engine buffer. It mechanically intersects two independently
closed native GCN proofs: Xur's 2-influence and 4-influence VS families. Both
declare ImmConstBuffer API10 at the same user-data start and both use its
descriptor for indexed float4 loads in consecutive real/dual record pairs.
"""
import argparse,json,re
from pathlib import Path

EXPECTED={
 "two":{"gcn":"b045462d7896e5c5012e8587076f6c669455b35009c197cd1c50d4e7529a1ab6","members":3,"loads":2},
 "four":{"gcn":"24392dbd8f217a832456372a8d9c24d3ef365ab5a0b8bcd362882ca845052964","members":14,"loads":4},
}

def inspect(path,key):
    t=path.read_text()
    e=EXPECTED[key]; v=[]
    if e["gcn"] not in t:v.append(f"{key}:gcn")
    if "('ImmConstBuffer',10,8)" not in t:v.append(f"{key}:api10_usage")
    loads=re.findall(r"tbuffer_load_format_xyzw[^\n']*s\[8:11\][^\n']*idxen format:\[32_32_32_32,float\]",t)
    if len(set(loads))<e["loads"]:v.append(f"{key}:indexed_load_count:{len(set(loads))}")
    if key=="two":
        for q in ("q0=api10[2*index0]","d0=api10[2*index0+1]","q1=api10[2*index1]","d1=api10[2*index1+1]"):
            if q not in t:v.append("two:pair_equation")
    else:
        if "qi=api10[2*index_i]; di=api10[2*index_i+1]" not in t:v.append("four:pair_equation")
    marker=f"'scope_material_count':{e['members']}"
    if marker not in t:v.append(f"{key}:member_denominator")
    return {"gcn_sha256":e["gcn"],"material_count":e["members"],"minimum_distinct_indexed_api10_load_anchors":e["loads"]},v

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--two",type=Path,required=True);ap.add_argument("--four",type=Path,required=True);ap.add_argument("-o","--out",type=Path,required=True);a=ap.parse_args()
    r2,v2=inspect(a.two,"two");r4,v4=inspect(a.four,"four");v=v2+v4
    out={
      "schema":"d1_api10_cross_gcn_data_role/v1",
      "status":"D1_API10_CROSS_GCN_DATA_ROLE_EXACT" if not v else "D1_API10_CROSS_GCN_DATA_ROLE_VIOLATIONS",
      "proof_families":{"two_influence":r2,"four_influence":r4},
      "combined_material_occurrences_in_these_proofs":17,
      "source_closed_role":{
        "usage_record":"ImmConstBuffer API10, user-data start SGPR 8",
        "descriptor_window":"s[8:11]",
        "record_shape":"indexed 16-byte float4 records",
        "pair_structure":"each proven influence selects records 2*index and 2*index+1",
        "consumer_math_role":"real+dual quaternion records used by native dual-quaternion skinning dataflow"
      },
      "semantic_boundary":{"runtime_writer":"WITHHELD","backing_allocation":"WITHHELD","engine_buffer_name":"WITHHELD","engine_semantic":"WITHHELD"},
      "violations":v,
      "policy":"Instruction-level consumer role is proven for these exact GCN families. It does not identify API10's runtime writer, allocation, engine-facing buffer name, or establish that every API10 consumer has this role."
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+"\n");print(json.dumps(out,indent=2));return 0 if not v else 2
if __name__=="__main__":raise SystemExit(main())
