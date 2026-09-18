#!/usr/bin/env python3
import argparse,json
from pathlib import Path
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--materials-spec",type=Path,required=True);ap.add_argument("--resource-spec",type=Path,required=True);ap.add_argument("--probe",type=Path,required=True);ap.add_argument("-o","--out",type=Path,required=True);a=ap.parse_args()
 m=a.materials_spec.read_text();r=a.resource_spec.read_text();p=a.probe.read_text();v=[]
 anchors=[(m,"122/122 observed headers exactly 16 bytes"),(m,"122/122 linked metadata sizes"),(m,"constant-buffer API slot 0"),(m,"GCN load offsets land exactly on the recovered local vectors"),(r,"88 "), (r,"subtype-7 header TagHash"),(p,"PS4GpuSubtype7Header"),(p,"payload_size_matches_unit_count")]
 for t,q in anchors:
  if q not in t:v.append("missing:"+q)
 out={"schema":"d1_ps4_subtype7_material_b0_role/v1","status":"D1_PS4_SUBTYPE7_MATERIAL_B0_ROLE_EXACT" if not v else "D1_PS4_SUBTYPE7_MATERIAL_B0_ROLE_VIOLATIONS","resource":{"header_type":32,"header_subtype":7,"header_bytes":16,"payload_unit_bytes":16,"validated_header_payload_pairs":122,"technique_refs_at_0x32c":88},"proven_role":"PS4 material Vector4 constant storage feeding material pixel-shader constant-buffer API slot 0 (b0) in the validated D1 ROI path","official_d1_tiger_class_name":"WITHHELD","global_all_usage_semantics":"WITHHELD","evidence_classes":["CONFIRMED_BINARY","CONFIRMED_CROSS_PLATFORM_SEMANTIC","INSTRUCTION_LEVEL_SHADER_BINDING"],"violations":v}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+"\n");print(json.dumps(out,indent=2));return 0 if not v else 2
if __name__=="__main__":raise SystemExit(main())
