#!/usr/bin/env python3
"""Comparative exact-signature cross-check for the D1 Xur permutation frontier.

This does NOT promote Marathon/MIDA behavior as Destiny 1 runtime authority.
It compares an independently published later-engine ModelPermutation algorithm
against the already source-closed D1 static graph and source-decoded Xur config.

Pinned comparative source:
  DeltaDesigns/MIDA commit 0a5adc9a31951bd1b244ab9792e20e496f598a7b
  Tiger/Schema/Entity/EntityModelParent.cs

Relevant comparative behavior:
  * switch records contribute key/value pairs;
  * descriptor switch-record references are reduced to a sorted key/value set;
  * the live configuration is sorted by key;
  * exact pair-set equality maps to a permutation index.

D1 authority remains the retail bytes.  The output reports convergence/divergence
with the existing D1 list-A subset/max-specificity candidate without opening any
live-selection gate.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

MIDA_COMMIT="0a5adc9a31951bd1b244ab9792e20e496f598a7b"
MIDA_PATH="Tiger/Schema/Entity/EntityModelParent.cs"
TARGETS={"E6":"80C885E6","E7":"80C885E7","E8":"80C885E8"}

def norm(x): return str(x).upper().removeprefix("0X").zfill(8)

def flatten(desc_list):
    out=[]
    for r in desc_list.get("switch_records",[]):
        pairs=r.get("pairs",[])
        for p in pairs:
            out.append((norm(p[0]),norm(p[1])))
    return out

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--static-graph",type=Path,required=True)
    ap.add_argument("--placement-config",type=Path,required=True)
    ap.add_argument("--candidate",type=Path,required=True)
    ap.add_argument("-o","--output",type=Path,required=True)
    a=ap.parse_args()

    g=json.loads(a.static_graph.read_text())
    p=json.loads(a.placement_config.read_text())
    c=json.loads(a.candidate.read_text())
    v=[]
    if g.get("status")!="D1_XUR_MODEL_PARENT_PERMUTATION_STATIC_REFERENCE_GRAPH_EXACT":v.append("static_graph_not_exact")
    if p.get("status")!="D1_XUR_PLACEMENT_CONFIGURATION_SOURCE_DECODED":v.append("placement_config_not_exact")
    if c.get("status")!="D1_XUR_CANDIDATE_PERMUTATION_EVALUATION_UNIQUE":v.append("candidate_not_unique")
    if g.get("violations") or p.get("violations") or c.get("violations"):v.append("upstream_violations")

    model_config={tuple(x) for x in c.get("model_switch_configuration_pairs",[])}
    desc={int(x["descriptor_index"]):x for x in g.get("descriptors",[])}
    by_vi={}
    for m in g.get("variant_members",[]):
        by_vi.setdefault(int(m["variant_shader_index"]),[]).append(m)
    candidate_by_vi={int(x["variant_shader_index"]):x for x in c.get("evaluations",[])}

    rows=[]
    exact_unique=exact_none=exact_ambig=converged=0
    for vi,members in sorted(by_vi.items()):
        exact=[]
        signatures=[]
        for m in sorted(members,key=lambda x:int(x["member_index"])):
            d=desc[int(m["descriptor_index"])]
            all_pairs=flatten(d["list_a"])
            sig=tuple(sorted(set(all_pairs)))
            first_pairs=[]
            for sr in d["list_a"].get("switch_records",[]):
                pp=sr.get("pairs",[])
                if pp:
                    first_pairs.append((norm(pp[0][0]),norm(pp[0][1])))
            first_sig=tuple(sorted(set(first_pairs)))
            signatures.append({
                "member_index":int(m["member_index"]),
                "material_tag_hash":norm(m["material_tag_hash"]),
                "descriptor_index":int(m["descriptor_index"]),
                "d1_all_pair_signature":[list(x) for x in sig],
                "mida_first_pair_signature":[list(x) for x in first_sig],
            })
            # Exact equality is the only comparative match tested here.
            if set(first_sig)==model_config:
                exact.append(signatures[-1])
        if len(exact)==1: exact_unique+=1
        elif len(exact)==0: exact_none+=1
        else: exact_ambig+=1
        ce=candidate_by_vi.get(vi) or {}
        cw=ce.get("candidate_members") or []
        current_material=norm(cw[0]["material_tag_hash"]) if len(cw)==1 else None
        exact_material=exact[0]["material_tag_hash"] if len(exact)==1 else None
        same=(current_material is not None and exact_material==current_material)
        if same: converged+=1
        rows.append({
            "variant_shader_index":vi,
            "member_count":len(members),
            "current_d1_candidate_material":current_material,
            "comparative_exact_signature_match_count":len(exact),
            "comparative_exact_signature_material":exact_material,
            "converges_with_current_candidate":same,
            "comparative_matches":exact,
            "signatures":signatures,
        })

    target_rows={}
    for label,tag in TARGETS.items():
        hit=[]
        for r in rows:
            members=[x for x in r["signatures"] if x["material_tag_hash"]==tag]
            if members:
                hit.append({
                    "variant_shader_index":r["variant_shader_index"],
                    "target_material":tag,
                    "current_d1_candidate_material":r["current_d1_candidate_material"],
                    "comparative_exact_signature_material":r["comparative_exact_signature_material"],
                    "converges":r["converges_with_current_candidate"],
                })
        target_rows[label]=hit

    out={
        "schema":"d1_xur_mida_permutation_crosscheck/v1",
        "status":"D1_XUR_COMPARATIVE_PERMUTATION_CROSSCHECK_COMPLETE" if not v else "D1_XUR_COMPARATIVE_PERMUTATION_CROSSCHECK_VIOLATIONS",
        "comparative_source":{"repository":"DeltaDesigns/MIDA","commit":MIDA_COMMIT,"path":MIDA_PATH},
        "d1_model_config":[list(x) for x in sorted(model_config)],
        "variant_group_count":len(rows),
        "comparative_exact_signature_unique_groups":exact_unique,
        "comparative_exact_signature_no_match_groups":exact_none,
        "comparative_exact_signature_ambiguous_groups":exact_ambig,
        "converged_with_d1_subset_max_specificity_groups":converged,
        "all_groups_converge":bool(rows) and converged==len(rows),
        "rows":rows,
        "target_consequences":target_rows,
        "gates":{
            "D1_retail_descriptor_evaluator_source_closed":False,
            "E6_80C885E6_live_selection_proven":False,
            "E7_80C885E7_live_selection_proven":False,
            "E8_80C885E8_live_selection_proven":False,
        },
        "violations":v,
        "policy":"Comparative MIDA behavior is evidence about engine-family architecture only. Exact D1 retail consumer/evaluator execution remains required before any live material selection is promoted."
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps({k:out[k] for k in (
        "status","d1_model_config","variant_group_count",
        "comparative_exact_signature_unique_groups",
        "comparative_exact_signature_no_match_groups",
        "comparative_exact_signature_ambiguous_groups",
        "converged_with_d1_subset_max_specificity_groups","all_groups_converge",
        "target_consequences","gates","violations"
    )},indent=2))
    return 0 if not v else 2

if __name__=="__main__":
    raise SystemExit(main())
