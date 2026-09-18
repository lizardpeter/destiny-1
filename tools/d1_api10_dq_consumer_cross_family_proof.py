#!/usr/bin/env python3
"""Cross-proof API10 consumer role across 1-, 2-, and 4-influence Xur VS GCN.

No engine-facing name is assigned. The one-influence family independently shows
the same consecutive API10 float4 record pair feeding dual-quaternion transform
math, extending the consumer-role proof beyond the weighted families.
"""
import argparse,json
from pathlib import Path

EXPECTED={
 "one":{"gcn":"a5ad940fbf21746563f6585b889ac91b4220c94a3559e768028c894454bcdc12","materials":31,
        "equation":"entry = 2 * uint(0.1 + 32767.0*v7); q = api10[entry]; d = api10[entry+1]"},
 "two":{"gcn":"b045462d7896e5c5012e8587076f6c669455b35009c197cd1c50d4e7529a1ab6","materials":3,
        "equation":"q0=api10[2*index0]; d0=api10[2*index0+1]; q1=api10[2*index1]; d1=api10[2*index1+1]"},
 "four":{"gcn":"24392dbd8f217a832456372a8d9c24d3ef365ab5a0b8bcd362882ca845052964","materials":14,
         "equation":"qi=api10[2*index_i]; di=api10[2*index_i+1]"}
}
def main():
 ap=argparse.ArgumentParser()
 for k in EXPECTED:ap.add_argument("--"+k,type=Path,required=True)
 ap.add_argument("-o","--out",type=Path,required=True);a=ap.parse_args();viol=[];rows={}
 for k,e in EXPECTED.items():
  t=getattr(a,k).read_text()
  if e["gcn"] not in t:viol.append(k+":gcn")
  if "('ImmConstBuffer',10,8)" not in t:viol.append(k+":usage")
  if "s[8:11]" not in t or "tbuffer_load_format_xyzw" not in t:viol.append(k+":descriptor_load")
  if e["equation"] not in t:viol.append(k+":pair_equation")
  if f"'scope_material_count':{e['materials']}" not in t and f"'scope_material_count':len(MEMBERS)" not in t:viol.append(k+":denominator")
  rows[k]={"gcn_sha256":e["gcn"],"material_count":e["materials"],"pair_equation":e["equation"]}
 out={"schema":"d1_api10_dq_consumer_cross_family/v1","status":"D1_API10_DQ_CONSUMER_CROSS_FAMILY_EXACT" if not viol else "D1_API10_DQ_CONSUMER_CROSS_FAMILY_VIOLATIONS",
      "families":rows,"material_occurrences":48,"influence_counts":[1,2,4],
      "proven_common_role":{"usage":"ImmConstBuffer API10 at user-data start SGPR 8","descriptor_window":"s[8:11]","record_width_bytes":16,
      "record_pair":"consecutive float4 records selected as real quaternion q and dual record d","consumer":"native dual-quaternion transform/skinning arithmetic"},
      "limits":{"all_39_api10_programs_have_dq_role":False,"runtime_writer":"WITHHELD","backing_allocation":"WITHHELD","engine_buffer_name":"WITHHELD","engine_semantic":"WITHHELD"},
      "violations":viol,"policy":"Common instruction-level data role is exact only for these three GCN families. Material occurrences overlap the Xur scoped material corpus and are not the global API10 denominator."}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+"\n");print(json.dumps(out,indent=2));return 0 if not viol else 2
if __name__=="__main__":raise SystemExit(main())
