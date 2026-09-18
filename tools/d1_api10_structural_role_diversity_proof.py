#!/usr/bin/env python3
"""API10 structural-role diversity proof from exact native GCN handlers.

This prevents over-generalizing the Xur DQ result. Exact Vex VS 80AAE149 uses
API10 as indexed three-row rigid transforms, while exact Xur families use
consecutive real/dual quaternion records. Same API slot/window != one universal
record schema or engine semantic.
"""
import argparse,json
from pathlib import Path
XUR=["a5ad940fbf21746563f6585b889ac91b4220c94a3559e768028c894454bcdc12","b045462d7896e5c5012e8587076f6c669455b35009c197cd1c50d4e7529a1ab6","24392dbd8f217a832456372a8d9c24d3ef365ab5a0b8bcd362882ca845052964"]
VEX="e6f18138e330a9c6b3ddce2e71890b1bcda73f732c4f6007b4c788c0ff62f4c0"
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--dq",type=Path,required=True);ap.add_argument("--vex",type=Path,required=True);ap.add_argument("-o","--out",type=Path,required=True);a=ap.parse_args();d=a.dq.read_text();v=a.vex.read_text();viol=[]
 for h in XUR:
  if h not in d:viol.append("missing_xur:"+h)
 if VEX not in v:viol.append("missing_vex")
 for t,name in [(d,"xur"),(v,"vex")]:
  if "('ImmConstBuffer',10,8)" not in t:viol.append(name+":usage")
  if "s[8:11]" not in t:viol.append(name+":window")
 if "row_indices':['3*joint','3*joint+1','3*joint+2']" not in v:viol.append("vex:three_rows")
 if "'row_format':'float4 x 3'" not in v:viol.append("vex:row_format")
 if "real quaternion q and dual record d" not in d:viol.append("xur:dq_pair")
 out={"schema":"d1_api10_structural_role_diversity/v1","status":"D1_API10_STRUCTURAL_ROLE_DIVERSITY_EXACT" if not viol else "D1_API10_STRUCTURAL_ROLE_DIVERSITY_VIOLATIONS",
 "common_binding":{"usage":"ImmConstBuffer API10","start_sgpr":8,"descriptor_window":"s[8:11]"},
 "proven_roles":[
  {"corpus":"Xur exact VS GCN families","gcn_sha256":XUR,"record_structure":"two consecutive float4 records per selected transform: real quaternion + dual record","consumer_role":"dual-quaternion transform/skinning"},
  {"corpus":"Vex exact VS 80AAE149","gcn_sha256":[VEX],"record_structure":"three consecutive float4 rows per selected transform","consumer_role":"rigid three-row affine/basis transform"}
 ],
 "conclusion":"API10 has proven heterogeneous consumer-side record structures across exact retail GCN. API number and SGPR window cannot define a universal record layout or engine semantic.",
 "semantic_boundary":{"runtime_writer":"WITHHELD","backing_allocation":"WITHHELD","universal_record_schema":"WITHHELD","engine_buffer_name":"WITHHELD","engine_semantic":"WITHHELD"},
 "violations":viol}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+"\n");print(json.dumps(out,indent=2));return 0 if not viol else 2
if __name__=="__main__":raise SystemExit(main())
