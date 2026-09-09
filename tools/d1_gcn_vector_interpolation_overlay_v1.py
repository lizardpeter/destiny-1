#!/usr/bin/env python3
"""Bind source-closed GFX7 VINTRP operations to exact D1 register/M0 state identities.

This overlay leaves the physical VGPR and SGPR graphs owned by their existing SSA layers. It
attaches symbolic VINTRP operation nodes to the already exact `result:iN:vM` active-lane result,
with explicit parameter coefficient identities, ATTR/CHAN, exact barycentric VGPR state, exact
old-destination state for P2, and exact automatic-M0 scalar state. Parameter contents and host
floating evaluation remain withheld.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

import d1_gcn_vgpr_lane_ssa_v1 as lane
import d1_gcn_sgpr_ssa_v1 as scalar
import d1_gcn_vector_interpolation_semantics_v1 as sem

INPUT_STATUS="D1_GCN_STRUCTURAL_IR_COMPLETE"
LANE_STATUS="D1_GCN_VGPR_LANE_SSA_EXACT"
SCALAR_STATUS="D1_GCN_SGPR_SSA_EXACT"
SCHEMA="d1_gcn_vector_interpolation_overlay/v1"
STATUS="D1_GCN_VECTOR_INTERPOLATION_OVERLAY_EXACT"
ATTR_RE=re.compile(r"^attr(\d+)\.([xyzw])$")
VREG_RE=re.compile(r"^v(\d+)$")


def _find_vgpr(row: dict, reg: str) -> list[str]:
    return sorted({u.get("value") for u in (row.get("vgpr_uses") or []) if u.get("register")==reg and u.get("value")})


def analyze(v2: dict) -> dict:
    if v2.get("status")!=INPUT_STATUS:
        raise ValueError(f"input status {v2.get('status')!r}")
    if sem.validate():
        raise ValueError(f"interpolation registry invalid:{sem.validate()}")
    ins=v2.get("instructions") or []
    targets=[x for x in ins if x.get("opcode") in sem.OPS]
    if not targets:
        return {
            "schema":SCHEMA,"status":STATUS,"shader":v2.get("shader"),"instruction_count":len(ins),
            "coverage":{"interpolation_instruction_count":0,"interpolation_result_component_count":0,
                        "parameter_value_identity_node_count":0,"m0_state_reference_count":0,
                        "shader_expression_semantic_promotions":0},
            "nodes":{},"bindings":[],"violations":[],
            "semantic_boundary":{"vintrp_formula_identity":"SOURCE_CLOSED","parameter_values":"NOT_PRESENT_IN_PROGRAM",
                                 "shader_expression_semantics":"WITHHELD","shader_expression_semantic_promotions":0},
        }

    vg=lane.analyze(v2); sg=scalar.analyze(v2)
    if vg.get("status")!=LANE_STATUS or vg.get("violations"):
        raise ValueError(f"lane prerequisite:{vg.get('status')}:{(vg.get('violations') or [])[:3]}")
    if sg.get("status")!=SCALAR_STATUS or sg.get("violations"):
        raise ValueError(f"scalar prerequisite:{sg.get('status')}:{(sg.get('violations') or [])[:3]}")
    vrows=vg.get("instructions") or []; srows=sg.get("instructions") or []
    vnodes=vg.get("nodes") or {}; snodes=sg.get("nodes") or {}
    if len(vrows)!=len(ins) or len(srows)!=len(ins): raise ValueError("instruction roster mismatch")

    nodes={}; bindings=[]; violations=[]; counts=Counter(); opcounts=Counter(); attrcounts=Counter(); chancounts=Counter()
    bound_results=set(); bound_writes=set()

    def add(nid,kind,*,inputs=(),idx=None,op=None,exactness="SOURCE_CLOSED",detail=None):
        n={"id":nid,"kind":kind,"inputs":list(inputs),"exactness":exactness}
        if idx is not None:n["instruction"]=idx
        if op is not None:n["opcode"]=op
        if detail is not None:n["detail"]=detail
        old=nodes.get(nid)
        if old is not None and old!=n: raise ValueError(f"overlay node collision:{nid}")
        nodes[nid]=n;return nid

    for idx,x in enumerate(ins):
        op=x.get("opcode")
        if op not in sem.OPS: continue
        if x.get("index")!=idx:
            violations.append(f"instruction_index:{idx}:{x.get('index')}");continue
        operands=x.get("operands") or []; defs=x.get("defs") or []
        vd=[r for r in defs if VREG_RE.fullmatch(r or "")]
        if len(vd)!=1:
            violations.append(f"dest_width:{idx}:{op}:{vd}");continue
        dest=vd[0]; vr=vrows[idx]; sr=srows[idx]
        writes=vr.get("vgpr_writes") or []
        if len(writes)!=1 or writes[0].get("register")!=dest:
            violations.append(f"write_shape:{idx}:{op}:{writes}");continue
        wr=writes[0]; result=f"result:i{idx}:{dest}"; write=f"write:i{idx}:{dest}"
        if wr.get("result")!=result or wr.get("new")!=write or result not in vnodes or write not in vnodes:
            violations.append(f"lane_identity:{idx}:{op}:{wr}");continue
        if result in bound_results or write in bound_writes:
            violations.append(f"duplicate_binding:{idx}:{dest}");continue
        bound_results.add(result);bound_writes.add(write)

        if len(operands)!=3:
            violations.append(f"operand_count:{idx}:{op}:{operands}");continue
        attrtok=operands[2]; am=ATTR_RE.fullmatch(attrtok or "")
        if not am:
            violations.append(f"attr_token:{idx}:{op}:{attrtok!r}");continue
        attr=int(am.group(1)); chan=am.group(2)
        if not 0<=attr<=32:
            violations.append(f"attr_range:{idx}:{attr}");continue
        attrcounts[attr]+=1;chancounts[chan]+=1

        m0=sr.get("implicit_m0_use")
        if not m0 or m0.get("register")!="m0" or m0.get("category")!="VINTRP_AUTOMATIC_M0":
            violations.append(f"m0_identity:{idx}:{op}:{m0}");continue
        m0state=m0.get("value")
        if m0state not in snodes:
            violations.append(f"m0_state_missing:{idx}:{m0state}");continue
        m0ref=add(f"interp:i{idx}:m0","EXACT_SCALAR_M0_STATE_REFERENCE",idx=idx,op=op,
                  exactness="GLOBAL_SCALAR_SSA_IDENTITY_EXACT",
                  detail={"external_graph":"d1_gcn_sgpr_ssa/v1","external_node":m0state,
                          "external_ref":f"scalar:{m0state}","role":"VINTRP_AUTOMATIC_M0"})
        counts["m0_state_reference_count"]+=1

        def param(name):
            counts["parameter_value_identity_node_count"]+=1
            return add(f"interp:i{idx}:param:{name.lower()}","GFX7_LDS_PARAMETER_VALUE",inputs=[m0ref],idx=idx,op=op,
                       exactness="PARAMETER_LOCATION_IDENTITY_EXACT_VALUE_OPAQUE",
                       detail={"coefficient":name,"attribute":attr,"channel":chan,
                               "attribute_token":attrtok,"value_status":"LDS_PARAMETER_VALUE_OPAQUE"})

        operation_inputs=[]; detail={"formula":sem.OPS[op]["formula"],"attribute":attr,"channel":chan}
        if op in {"v_interp_p1_f32","v_interp_p2_f32"}:
            src=operands[1]
            vals=_find_vgpr(vr,src)
            if len(vals)!=1 or vals[0] not in vnodes:
                violations.append(f"vsrc_identity:{idx}:{op}:{src}:{vals}");continue
            sref=add(f"interp:i{idx}:vsrc","EXACT_VGPR_STATE_REFERENCE",idx=idx,op=op,
                     exactness="GLOBAL_VGPR_LANE_SSA_IDENTITY_EXACT",
                     detail={"register":src,"external_graph":"d1_gcn_vgpr_lane_ssa/v1",
                             "external_node":vals[0],"external_ref":f"vgpr:{vals[0]}"})
            counts["vgpr_source_state_reference_count"]+=1
            if op=="v_interp_p1_f32":
                operation_inputs=[param("P10"),sref,param("P0")]
            else:
                old=wr.get("old")
                if old not in vnodes:
                    violations.append(f"old_dest_missing:{idx}:{old}");continue
                destvals=_find_vgpr(vr,dest)
                if destvals!=[old]:
                    violations.append(f"p2_old_dest_use:{idx}:{dest}:{destvals}!={[old]}");continue
                oldref=add(f"interp:i{idx}:old_dest","OLD_DESTINATION_ARITHMETIC_INPUT",idx=idx,op=op,
                           exactness="GLOBAL_VGPR_LANE_SSA_IDENTITY_EXACT",
                           detail={"register":dest,"external_graph":"d1_gcn_vgpr_lane_ssa/v1",
                                   "external_node":old,"external_ref":f"vgpr:{old}",
                                   "role":"P2_ARITHMETIC_ACCUMULATOR_NOT_EXEC_PRESERVATION"})
                counts["old_destination_arithmetic_input_count"]+=1
                operation_inputs=[param("P20"),sref,oldref]
        else:
            selector=operands[1].lower()
            if selector not in {"p0","p10","p20"}:
                violations.append(f"mov_selector:{idx}:{selector!r}");continue
            detail["selector"]=selector.upper()
            operation_inputs=[param(selector.upper())]
            counts["parameter_move_instruction_count"]+=1

        opnode=add(f"interp:i{idx}:operation","GFX7_VINTRP_ARCHITECTURAL_OPERATION",inputs=operation_inputs,idx=idx,op=op,
                   exactness="SOURCE_CLOSED_SYMBOLIC_NUMERIC_REPLAY_WITHHELD",detail=detail)
        bindings.append({"instruction":idx,"opcode":op,"result":result,"write":write,"operation":opnode,
                         "attribute":attr,"channel":chan,"m0_state":m0state})
        counts["interpolation_instruction_count"]+=1;counts["interpolation_result_component_count"]+=1
        opcounts[op]+=1

    if len(bindings)!=counts["interpolation_instruction_count"]:
        violations.append(f"binding_accounting:{len(bindings)}!={counts['interpolation_instruction_count']}")
    if len(bound_results)!=counts["interpolation_result_component_count"]:
        violations.append(f"result_accounting:{len(bound_results)}!={counts['interpolation_result_component_count']}")
    if len(bound_writes)!=counts["interpolation_result_component_count"]:
        violations.append(f"write_accounting:{len(bound_writes)}!={counts['interpolation_result_component_count']}")

    cov={
        "interpolation_instruction_count":counts["interpolation_instruction_count"],
        "interpolation_result_component_count":counts["interpolation_result_component_count"],
        "opcode_instruction_counts":dict(sorted(opcounts.items())),
        "parameter_value_identity_node_count":counts["parameter_value_identity_node_count"],
        "m0_state_reference_count":counts["m0_state_reference_count"],
        "vgpr_source_state_reference_count":counts["vgpr_source_state_reference_count"],
        "old_destination_arithmetic_input_count":counts["old_destination_arithmetic_input_count"],
        "parameter_move_instruction_count":counts["parameter_move_instruction_count"],
        "attribute_instruction_counts":{str(k):v for k,v in sorted(attrcounts.items())},
        "channel_instruction_counts":dict(sorted(chancounts.items())),
        "overlay_node_count":len(nodes),"shader_expression_semantic_promotions":0,
    }
    return {
        "schema":SCHEMA,"status":STATUS if not violations else "D1_GCN_VECTOR_INTERPOLATION_OVERLAY_WITH_VIOLATIONS",
        "shader":v2.get("shader"),"instruction_count":len(ins),"coverage":cov,"nodes":nodes,"bindings":bindings,
        "violations":violations,"source_semantics":sem.document(),
        "semantic_boundary":{
            "vintrp_formula_identity":"SOURCE_CLOSED_SYMBOLIC" if not violations else "WITHHELD",
            "vintrp_result_to_existing_lane_ssa":"EXACT" if not violations else "WITHHELD",
            "vintrp_m0_state_identity":"EXACT_CROSS_GRAPH" if not violations else "WITHHELD",
            "vintrp_attribute_channel_identity":"EXACT" if not violations else "WITHHELD",
            "parameter_contents":"LDS_PARAMETER_VALUE_OPAQUE","floating_numeric_replay":"WITHHELD",
            "vertex_to_pixel_varying_semantics":"WITHHELD","material_semantics":"WITHHELD",
            "shader_expression_semantic_promotions":0,
        },
        "policy":"VINTRP operation formulas and all encoded/register-state inputs are bound without evaluating floating arithmetic or guessing parameter contents or semantic varying names."
    }


def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument("--structural-ir",type=Path,required=True);ap.add_argument("-o","--output",type=Path,required=True);a=ap.parse_args()
    out=analyze(json.loads(a.structural_ir.read_text()));a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":out["status"],"coverage":out["coverage"],"violations":out["violations"][:50]},indent=2,sort_keys=True));return 0 if not out["violations"] else 2
if __name__=="__main__":raise SystemExit(main())
