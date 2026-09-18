#!/usr/bin/env python3
"""Promote fixed-field Crota composition-FX material references from retail bytes.

Input is the exact-tag probe over source-owned Crota ultra-spawn composition
children.  The proof is deliberately structural:

  * every observed 80801C40 record is exactly 0x24 bytes and carries one
    80801AD7 Material FileHash at +0x10;
  * every observed 80801BD9 record is exactly 0xB0 bytes and carries one
    80801AD7 Material FileHash at +0x90;
  * 80801B7B siblings are retained as a separate structured frontier and do not
    contribute a material merely because other aligned tags are present.

This proves composition visual-FX material ownership for these exact records.
It does not identify the official Bungie names of the outer classes, does not
promote these materials as Crota body materials, and does not infer particle,
beam, decal, render-pass, or gameplay-effect semantics.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path

MATERIAL="80801AD7"
C40="80801C40"
BD9="80801BD9"
B7B="80801B7B"
EXPECTED_COUNTS={C40:11,BD9:2,B7B:3}
EXPECTED_SIZE={C40:0x24,BD9:0xB0,B7B:0x48}
MATERIAL_OFF={C40:0x10,BD9:0x90}

def norm(x): return str(x).upper().removeprefix("0X").zfill(8)

def main()->int:
 ap=argparse.ArgumentParser()
 ap.add_argument("--probe",type=Path,required=True)
 ap.add_argument("-o","--output",type=Path,required=True)
 a=ap.parse_args()
 src=json.loads(a.probe.read_text())
 v=[]
 if src.get("schema")!="d1_remote_exact_tag_probe/v1":v.append(f"probe_schema:{src.get('schema')}")
 if src.get("status")!="D1_REMOTE_EXACT_TAG_PROBE_COMPLETE":v.append(f"probe_status:{src.get('status')}")
 if src.get("violation_count")!=0 or src.get("violations"):v.append("probe_has_violations")

 rows=[x for x in src.get("entries",[]) if norm((x.get("entry") or {}).get("reference")) in EXPECTED_COUNTS]
 counts=Counter(norm(x["entry"]["reference"]) for x in rows)
 if dict(counts)!=EXPECTED_COUNTS:v.append(f"class_counts:{dict(counts)!r}")

 carriers=[];materials=[];siblings=[]
 for row in rows:
  h=norm(row["tag_hash"]);cl=norm(row["entry"]["reference"]);size=int(row.get("payload_size",-1))
  if size!=EXPECTED_SIZE[cl]:v.append(f"{h}:{cl}:size:{size}")
  aligned={int(x["offset"]):x for x in row.get("aligned_resolved_tags",[])}
  base={"tag_hash":h,"class":cl,"payload_size":size,"payload_sha256":row.get("payload_sha256")}
  if cl in MATERIAL_OFF:
   off=MATERIAL_OFF[cl];x=aligned.get(off)
   if x is None:
    v.append(f"{h}:{cl}:missing_material_field_0x{off:X}")
    continue
   target=norm(x.get("tag_hash"));ref=norm((x.get("entry") or {}).get("reference"))
   if ref!=MATERIAL:v.append(f"{h}:{cl}:field_0x{off:X}_ref:{ref}")
   cr={**base,"material_field_offset":off,"material_field_offset_hex":f"0x{off:X}",
       "material":target,"material_reference":ref,
       "evidence_class":"FIXED_FIELD_STRUCTURED_MATERIAL_REFERENCE"}
   carriers.append(cr);materials.append(target)
  else:
   # B7B is intentionally retained as a sibling/frontier only.
   siblings.append({**base,"aligned_resolved_tags":[
    {"offset":int(x["offset"]),"tag_hash":norm(x["tag_hash"]),
     "reference":norm((x.get("entry") or {}).get("reference"))}
    for x in row.get("aligned_resolved_tags",[])
   ]})

 if len(carriers)!=13:v.append(f"material_carrier_count:{len(carriers)}")
 if len(set(materials))!=13:v.append(f"unique_material_count:{len(set(materials))}")
 expected=sorted([
  "8108EA09","8108EA0A","8108EA0B","8108EA0D","8108EA0E","8108EA0F",
  "8108EA10","8108EA11","8108EA12","8108EA13","8108EA14","8108EA16"
 ])
 # 8108EA0A occurs in two distinct C40 carriers, so there are 13 carrier edges
 # but 12 unique material identities in this exact nested-tag probe.
 if len(carriers)==13 and len(set(materials))!=12:
  v.append(f"expected_12_unique_materials_from_13_edges_got:{len(set(materials))}")
 if sorted(set(materials))!=expected:
  v.append(f"material_identity_set:{sorted(set(materials))!r}")

 exact=not v
 out={
  "schema":"d1_crota_fx_material_carrier_proof/v1",
  "status":"D1_CROTA_COMPOSITION_FX_MATERIAL_CARRIERS_EXACT" if exact else "D1_CROTA_COMPOSITION_FX_MATERIAL_CARRIERS_PARTIAL",
  "source_probe":str(a.probe),
  "class_counts":dict(sorted(counts.items())),
  "fixed_layouts":{
   C40:{"record_size":0x24,"material_offset":0x10,"material_reference":MATERIAL,"record_count":counts.get(C40,0)},
   BD9:{"record_size":0xB0,"material_offset":0x90,"material_reference":MATERIAL,"record_count":counts.get(BD9,0)},
   B7B:{"record_size":0x48,"material_offset":None,"record_count":counts.get(B7B,0),
        "status":"STRUCTURED_SIBLING_NO_MATERIAL_FIELD_PROMOTED"},
  },
  "material_edge_count":len(carriers),
  "unique_material_count":len(set(materials)),
  "materials":sorted(set(materials)),
  "material_edges":carriers,
  "structured_siblings":siblings,
  "gates":{
   "composition_visual_fx_material_ownership_closed":exact,
   "outer_class_official_names_closed":False,
   "particle_or_decal_semantic_closed":False,
   "crota_body_material_ownership_closed":False,
  },
  "violations":v,
  "policy":"Only invariant fixed-field 80801AD7 FileHashes in the exact typed Crota composition child records are promoted. Outer class names, VFX subtype semantics, and Crota body ownership remain withheld."
 }
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+"\n")
 print(json.dumps({k:out[k] for k in ("status","class_counts","material_edge_count","unique_material_count","materials","gates","violations")},indent=2))
 return 0 if exact else 2

if __name__=="__main__":raise SystemExit(main())
