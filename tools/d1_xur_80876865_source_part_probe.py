#!/usr/bin/env python3
"""Exact source-part neighborhood probe for the two Xur 80876865 ranges.

Re-decodes retail D1 model 80C88CEF and owning model-parent 80C88CE2 from the
remote corpus.  It reports mesh-5 source parts 88..101, with the exact source
part record, parent-aware base binding, and corpus-calibrated external-material
winner under the source-typed Xur configuration 26170C92=4AC210DE.

This is intentionally diagnostic: it does not promote the calibrated selector to
the retail consumer algorithm.
"""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_split_tar_extract import SplitHttpTar
from d1_entity_model_probe import parse_model
import d1_world_entity_model_material_bindings as base
from d1_remote_tower_descriptor_selection_calibration import parse_graph
from d1_xur_corpus_calibrated_material_bindings import winner,norm

MODEL="80C88CEF";PARENT="80C88CE2";MESH=5
TARGET_PARTS={93,96}
CONFIG={("26170C92","4AC210DE")}

def compact_bp(bp):
    keys=[
      "part_index","inline_material","variant_shader_index","selection",
      "selected_external_material_index","selected_material","selection_status",
      "external_map_entry","renderable","null_material_source_rule","violations"
    ]
    return {k:bp.get(k) for k in keys if k in bp}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--member-catalog",type=Path,action="append",required=True)
    ap.add_argument("--base-url",required=True)
    ap.add_argument("--part-count",type=int,default=10)
    ap.add_argument("--runtime",type=Path,required=True)
    ap.add_argument("-o","--output",type=Path,required=True)
    a=ap.parse_args();viol=[]
    cats=load_catalogs(a.member_catalog)
    arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90)
    c=RemoteCorpus(arc,cats,a.runtime)

    meta=c.entry_meta(MODEL);payload,src=c.payload(MODEL)
    if meta is None or payload is None: raise SystemExit("model unavailable")
    model=parse_model(payload,"PS4")
    if len(model.get("meshes") or [])<=MESH: raise SystemExit("mesh 5 absent")
    mesh=model["meshes"][MESH]
    offsets=[int(x) for x in mesh.get("stage_part_offsets_source_derived") or []]
    binding=base.bind_model(c,MODEL,PARENT)
    if binding.get("violations"):viol.extend("binding:"+x for x in binding["violations"])
    bm=next((x for x in binding.get("meshes",[]) if int(x["mesh_index"])==MESH),None)
    if bm is None: raise SystemExit("binding mesh5 absent")
    bparts={int(x["part_index"]):x for x in bm.get("parts",[])}
    graph=parse_graph(c,PARENT)
    groups={int(g["variant_shader_index"]):g for g in graph["groups"]}

    rows=[]
    for pi in range(88,min(102,len(mesh.get("parts") or []))):
        p=dict(mesh["parts"][pi])
        bp=bparts.get(pi) or {}
        vi=int(p.get("variant_shader_index",-1))
        cal=None
        if vi!=-1:
            g=groups.get(vi)
            if g is None:
                viol.append(f"part{pi}:group{vi}:missing")
            else:
                try:
                    spec,win,ev=winner(g,CONFIG)
                    cal={
                      "winner_material":norm(win["material_tag_hash"]),
                      "winner_member_index":int(win["member_index"]),
                      "winner_descriptor_index":int(win["descriptor_index"]),
                      "winner_specificity":int(spec),
                      "group_member_count":len(g["members"]),
                      "candidate_evidence":ev,
                    }
                except Exception as ex: viol.append(f"part{pi}:winner:{ex!r}")
        rows.append({
          "part_index":pi,
          "is_target_part":pi in TARGET_PARTS,
          "source_part":p,
          "base_parent_binding":compact_bp(bp),
          "calibrated_selection":cal,
        })

    targets=[x for x in rows if x["is_target_part"]]
    if [x["part_index"] for x in targets]!=[93,96]:viol.append("target parts absent")
    for x in targets:
        p=x["source_part"];cal=x["calibrated_selection"]
        if int(p.get("index_offset",-1)) not in (61638,61864):viol.append(f"part{x['part_index']}:unexpected offset")
        if int(p.get("gear_dye_change_color_index",-999))!=0:viol.append(f"part{x['part_index']}:dye not zero")
        if int(p.get("lod",-1))!=1:viol.append(f"part{x['part_index']}:lod not 1")
        bp=x["base_parent_binding"]
        if int(p.get("variant_shader_index",-999))!=-1:viol.append(f"part{x['part_index']}:not inline variant")
        if norm(p.get("material","FFFFFFFF"))!="80876865":viol.append(f"part{x['part_index']}:inline material drift")
        if bp.get("selection")!="inline_material":viol.append(f"part{x['part_index']}:binding not inline")
        if norm((bp.get("selected_material") or {}).get("hash","FFFFFFFF"))!="80876865":viol.append(f"part{x['part_index']}:bound material drift")
        if cal is not None:viol.append(f"part{x['part_index']}:unexpected external calibrated selection")

    out={
      "schema_version":1,
      "status":"D1_XUR_80876865_SOURCE_PART_NEIGHBORHOOD_EXACT" if not viol else "D1_XUR_80876865_SOURCE_PART_NEIGHBORHOOD_VIOLATIONS",
      "model":MODEL,"model_parent":PARENT,"model_source":src,
      "model_payload_sha256":hashlib.sha256(payload).hexdigest(),
      "mesh_index":MESH,"mesh_part_count":len(mesh.get("parts") or []),
      "stage_part_offsets_source_derived":offsets,
      "configuration_pairs":[list(x) for x in sorted(CONFIG)],
      "target_parts":[93,96],"rows":rows,
      "graph_summary":{
        "resource_hash":graph.get("resource_hash"),"descriptor_count":graph.get("descriptor_count"),
        "group_count":graph.get("group_count"),"material_count":graph.get("material_count"),
        "switch_record_count":graph.get("switch_record_count"),
      },
      "proof":{
        "source_model_redecoded":True,
        "owning_parent_binding_redecoded":not binding.get("violations"),
        "target_parts_are_source_inline_80876865":not viol and all(
          int(x["source_part"].get("variant_shader_index",-999))==-1
          and norm(x["source_part"].get("material","FFFFFFFF"))=="80876865"
          and x["base_parent_binding"].get("selection")=="inline_material"
          and norm((x["base_parent_binding"].get("selected_material") or {}).get("hash","FFFFFFFF"))=="80876865"
          and x["calibrated_selection"] is None
          for x in targets
        ),
        "external_material_selector_not_in_path_for_target_parts":not viol and all(int(x["source_part"].get("variant_shader_index",-999))==-1 for x in targets),
        "D1_retail_consumer_execution_path_proven":False,
      },
      "violations":viol,
      "policy":"Exact source part/binding bytes are re-decoded. Parts 93/96 are direct inline-material parts (variant_shader_index=-1), so their 80876865 binding does not pass through the external-material selector. Neighbor external variants remain diagnostic only."
    }
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps({
      "status":out["status"],"stage0":offsets[:2],
      "targets":[{
        "part_index":x["part_index"],
        "source_part":x["source_part"],
        "base_parent_binding":x["base_parent_binding"],
        "calibrated_selection":None if x["calibrated_selection"] is None else {k:v for k,v in x["calibrated_selection"].items() if k!="candidate_evidence"}
      } for x in targets],
      "neighbor_summary":[{
        "part":x["part_index"],
        "off":x["source_part"].get("index_offset"),"count":x["source_part"].get("index_count"),
        "lod":x["source_part"].get("lod"),"dye":x["source_part"].get("gear_dye_change_color_index"),
        "vi":x["source_part"].get("variant_shader_index"),"flags":x["source_part"].get("flags_d1"),
        "winner":None if x["calibrated_selection"] is None else x["calibrated_selection"]["winner_material"]
      } for x in rows],
      "violations":viol
    },indent=2))
    return 0 if not viol else 2

if __name__=="__main__":raise SystemExit(main())
