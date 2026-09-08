#!/usr/bin/env python3
"""Reconstruct the exact 808EE505 persistent export-mask predicate, v2.

V1 had a sign/orientation error in its prose because it described v_subrev_f32
as threshold-sample. This validator derives the predicate mechanically from
the structural operands plus independently source-proven VOP2/VOPC/SOP
semantics and material/image provenance.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

def load(p:Path): return json.loads(p.read_text())

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--ir",type=Path,required=True)
    ap.add_argument("--cbuffer",type=Path,required=True)
    ap.add_argument("--control-semantics",type=Path,required=True)
    ap.add_argument("--vopc-semantics",type=Path,required=True)
    ap.add_argument("-o","--output",type=Path,required=True)
    a=ap.parse_args()
    violations=[]; contract={}
    try:
        ir=load(a.ir); cb=load(a.cbuffer); ctl=load(a.control_semantics); vc=load(a.vopc_semantics)
        if ir.get("status")!="D1_GCN_STRUCTURAL_IR_COMPLETE" or ir.get("shader")!="808EE505":
            raise ValueError("structural IR is not exact 808EE505")
        if cb.get("status")!="D1_GCN_CBUFFER_PROVENANCE_EXACT" or cb.get("violations"):
            raise ValueError("cbuffer provenance not exact")
        if ctl.get("status")!="D1_GCN_CONTROL_SEMANTICS_SOURCE_PROVEN" or ctl.get("violations"):
            raise ValueError("control semantics not source-proven")
        if vc.get("status")!="D1_GCN_VOPC_SEMANTICS_SOURCE_PROVEN" or vc.get("violations"):
            raise ValueError("VOPC semantics not source-proven")
        ins=ir["instructions"]
        expected={
            332:("image_sample",["v16","v[16:19]","s[4:11]","s[16:19]"]),
            333:("s_buffer_load_dword",["s0","s[20:23]","0x1c"]),
            334:("s_waitcnt",["vmcnt(0) & lgkmcnt(0)"]),
            335:("v_subrev_f32",["v16","s0","v16"]),
            336:("v_cmp_gt_f32",["vcc","0","v16"]),
            337:("s_andn2_b64",["s[48:49]","s[48:49]","vcc"]),
            338:("s_cbranch_scc0",[".L2140_0"]),
            339:("s_and_b64",["exec","exec","s[48:49]"]),
            340:("s_wqm_b64",["exec","exec"]),
        }
        for i,(op,oper) in expected.items():
            x=ins[i]
            if x["opcode"]!=op or x["operands"]!=oper:
                raise ValueError(f"instruction {i} mismatch: {x['opcode']} {x['operands']}")
        img=ins[332].get("image") or {}
        if img.get("textures")!=[2] or img.get("dmask_channels")!="x":
            raise ValueError(f"332 image provenance mismatch: {img}")
        rows=[r for r in cb["loads"] if r.get("instruction")==333]
        if len(rows)!=1 or rows[0].get("resolution")!="EXACT_MATERIAL_PS_B0":
            raise ValueError(f"333 threshold provenance mismatch: {rows}")
        vals=rows[0].get("material_values") or []
        if len(vals)!=1 or vals[0].get("value")!=0.5 or rows[0].get("offset_dwords")!=28:
            raise ValueError(f"333 exact threshold mismatch: {rows[0]}")
        if ctl["semantics"]["v_subrev_f32"]["equation"]!="D = S1 - S0":
            raise ValueError("v_subrev semantics mismatch")
        if vc["semantics"]["v_cmp_gt_f32"]["equation"]!="D = (S0 > S1)":
            raise ValueError("v_cmp_gt semantics mismatch")
        if ctl["semantics"]["s_andn2_b64"]["equation"]!="D = S0 & ~S1" or ctl["semantics"]["s_andn2_b64"]["scc"]!="D != 0":
            raise ValueError("s_andn2/SCC semantics mismatch")
        if ctl["semantics"]["s_cbranch_scc0"]["equation"]!="branch iff SCC == 0":
            raise ValueError("s_cbranch_scc0 semantics mismatch")
        if ctl["semantics"]["s_and_b64"]["equation"]!="D = S0 & S1":
            raise ValueError("s_and_b64 semantics mismatch")
        if ins[338].get("branch_target_label")!=".L2140_0":
            raise ValueError("338 target label mismatch")
        targets=[x["index"] for x in ins if ".L2140_0" in (x.get("labels") or [])]
        if targets!=[443]:
            raise ValueError(f"338 target resolution mismatch: {targets}")
        if ins[338].get("uses")!=["scc"]:
            raise ValueError(f"338 SCC use mismatch: {ins[338].get('uses')}")
        contract={
            "material":"80D777B6","shader":"808EE505","texture_index":2,
            "sample_instruction":332,"threshold_load_instruction":333,
            "threshold_material_b0_scalar_index":28,"threshold":0.5,
            "subtract_instruction":335,
            "subtract_equation":"delta = sample - threshold",
            "compare_instruction":336,
            "compare_equation":"predicate = (0 > delta)",
            "predicate_equivalent":"sample < threshold",
            "mask_update_instruction":337,
            "mask_update_equation":"persistent_export_mask &= ~predicate",
            "branch_instruction":338,
            "branch_equation":"branch iff persistent_export_mask_after == 0",
            "branch_target_instruction":443,
            "first_exec_apply_instruction":339,
            "wqm_instruction":340,
            "discard_when":"sample < threshold",
            "survive_when":"sample >= threshold",
            "exact_threshold_rule":"discard t2.x < 0.5; survive t2.x >= 0.5",
            "v1_correction":{
                "supersedes_status":"D1_GCN_EXPORT_KILL_MASK_CONTRACT_COMPLETE",
                "error":"V1 prose treated v_subrev_f32 as threshold-sample. Exact operands plus D=S1-S0 prove sample-threshold.",
                "old_discard_rule":"sample > threshold",
                "old_survive_rule":"sample <= threshold"
            },
            "instruction_indices":[332,333,335,336,337,338,339,340],
            "semantic_role":"SOURCE_EXACT_MASK_CONTROL; HUMAN_VISUAL_ROLE_WITHHELD"
        }
    except Exception as exc:
        violations.append(repr(exc))
    out={
        "schema_version":2,
        "status":"D1_GCN_808EE505_EXPORT_KILL_MASK_V2_EXACT" if contract and not violations else "D1_GCN_808EE505_EXPORT_KILL_MASK_V2_PARTIAL",
        "contract":contract,"violations":violations,
        "policy":"The inequality is derived mechanically from exact instruction operands and independently pinned ISA semantics. No appearance, texture filename, or visual-role guess is used."
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2))
    return 0 if not violations else 2
if __name__=="__main__":
    raise SystemExit(main())
