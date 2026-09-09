#!/usr/bin/env python3
"""Bind exact D1 GFX7 IMAGE/BUFFER/DS operations to existing architectural state identities.

The output is an architectural resource-value overlay, not a material decompiler.  Every resource
operation is attached to the already-proven physical VGPR/SGPR/M0 states and to the existing
active-lane result/write identities.  Descriptor *contents*, runtime resource-table selection,
texture payload meaning and LDS contents remain explicitly opaque until later provenance gates.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

import d1_gcn_vgpr_lane_ssa_v1 as lane
import d1_gcn_sgpr_ssa_v1 as scalar
import d1_gcn_resource_value_semantics_v1 as sem

INPUT_STATUS="D1_GCN_STRUCTURAL_IR_COMPLETE"
LANE_STATUS="D1_GCN_VGPR_LANE_SSA_EXACT"
SCALAR_STATUS="D1_GCN_SGPR_SSA_EXACT"
SCHEMA="d1_gcn_resource_value_binding/v1"
STATUS="D1_GCN_RESOURCE_VALUE_BINDING_EXACT"
VREG_RE=re.compile(r"^v(\d+)$")
SREG_RE=re.compile(r"^s(\d+)$")
VRANGE_RE=re.compile(r"v\[(\d+):(\d+)\]")
SRANGE_RE=re.compile(r"s\[(\d+):(\d+)\]")


def _expand(tok: str, kind: str) -> list[str]:
    rr=VRANGE_RE if kind=="v" else SRANGE_RE
    m=rr.search(tok or "")
    if m:
        a,b=map(int,m.groups())
        if b<a: return []
        return [f"{kind}{i}" for i in range(a,b+1)]
    r=VREG_RE if kind=="v" else SREG_RE
    # tokens may carry modifiers after a single register
    m=re.search(rf"\b{kind}(\d+)\b",tok or "")
    return [f"{kind}{m.group(1)}"] if m else []


def _resolve(row: dict, field: str, regs: list[str]) -> list[str] | None:
    out=[]
    entries=row.get(field) or []
    for reg in regs:
        vals=sorted({u.get("value") for u in entries if u.get("register")==reg and u.get("value")})
        if len(vals)!=1: return None
        out.append(vals[0])
    return out


def _controls(x: dict) -> dict:
    asm=x.get("assembly") or ""
    joined=" ".join(x.get("operands") or [])
    text=asm+" "+joined
    dmask=re.search(r"\bdmask:(\d+)\b",text)
    fmt=re.search(r"\bformat:\[([^\]]+)\]",text)
    offsets={}
    for k in ("offset","offset0","offset1"):
        m=re.search(rf"\b{k}:(\d+)\b",text)
        if m: offsets[k]=int(m.group(1))
    return {
        "dmask":int(dmask.group(1)) if dmask else None,
        "unorm":bool(re.search(r"\bunorm\b",text)),
        "idxen":bool(re.search(r"\bidxen\b",text)),
        "format":fmt.group(1) if fmt else None,
        "offsets":offsets,
    }


def analyze(v2: dict) -> dict:
    if v2.get("status")!=INPUT_STATUS: raise ValueError(f"input status {v2.get('status')!r}")
    bad=sem.validate()
    if bad: raise ValueError(f"resource registry invalid:{bad}")
    ins=v2.get("instructions") or []
    targets=[x for x in ins if x.get("opcode") in sem.OPS]
    if not targets:
        return {
            "schema":SCHEMA,"status":STATUS,"shader":v2.get("shader"),"instruction_count":len(ins),
            "coverage":{"resource_instruction_count":0,"resource_result_component_count":0,
                        "image_instruction_count":0,"buffer_instruction_count":0,"ds_instruction_count":0,
                        "shader_expression_semantic_promotions":0},
            "nodes":{},"bindings":[],"violations":[],
            "semantic_boundary":{"architectural_resource_operation_identity":"NOT_PRESENT_IN_PROGRAM",
                                 "runtime_resource_assignment":"WITHHELD","material_semantics":"WITHHELD",
                                 "shader_expression_semantic_promotions":0},
        }

    vg=lane.analyze(v2); sg=scalar.analyze(v2)
    if vg.get("status")!=LANE_STATUS or vg.get("violations"):
        raise ValueError(f"lane prerequisite:{vg.get('status')}:{(vg.get('violations') or [])[:3]}")
    if sg.get("status")!=SCALAR_STATUS or sg.get("violations"):
        raise ValueError(f"scalar prerequisite:{sg.get('status')}:{(sg.get('violations') or [])[:3]}")
    vrows=vg.get("instructions") or []; srows=sg.get("instructions") or []
    vnodes=vg.get("nodes") or {}; snodes=sg.get("nodes") or {}
    if len(vrows)!=len(ins) or len(srows)!=len(ins): raise ValueError("instruction roster mismatch")

    nodes={};bindings=[];violations=[];counts=Counter();op_i=Counter();op_c=Counter()
    bound_results=set();bound_writes=set()

    def add(nid,kind,*,inputs=(),idx=None,op=None,exactness="SOURCE_CLOSED",detail=None):
        n={"id":nid,"kind":kind,"inputs":list(inputs),"exactness":exactness}
        if idx is not None:n["instruction"]=idx
        if op is not None:n["opcode"]=op
        if detail is not None:n["detail"]=detail
        old=nodes.get(nid)
        if old is not None and old!=n: raise ValueError(f"resource overlay collision:{nid}")
        nodes[nid]=n;return nid

    def vgref(idx,op,role,regs,row):
        vals=_resolve(row,"vgpr_uses",regs)
        if vals is None or any(v not in vnodes for v in vals):
            violations.append(f"vgpr_state:{idx}:{op}:{role}:{regs}:{vals}");return None
        counts["vgpr_source_state_component_reference_count"]+=len(regs)
        return add(f"resource:i{idx}:{role}","EXACT_VGPR_STATE_VECTOR_REFERENCE",idx=idx,op=op,
                   exactness="GLOBAL_VGPR_LANE_SSA_IDENTITY_EXACT",
                   detail={"role":role,"registers":regs,"external_graph":"d1_gcn_vgpr_lane_ssa/v1",
                           "external_nodes":vals,"external_refs":[f"vgpr:{v}" for v in vals]})

    def sgref(idx,op,role,regs,row,expected_width=None):
        if expected_width is not None and len(regs)!=expected_width:
            violations.append(f"scalar_width:{idx}:{op}:{role}:{len(regs)}!={expected_width}:{regs}");return None
        vals=_resolve(row,"scalar_uses",regs)
        if vals is None or any(v not in snodes for v in vals):
            violations.append(f"scalar_state:{idx}:{op}:{role}:{regs}:{vals}");return None
        counts["scalar_source_state_component_reference_count"]+=len(regs)
        if role=="resource_descriptor": counts["resource_descriptor_sgpr_component_reference_count"]+=len(regs)
        if role=="sampler_descriptor": counts["sampler_descriptor_sgpr_component_reference_count"]+=len(regs)
        return add(f"resource:i{idx}:{role}","EXACT_SCALAR_SSA_VECTOR_REFERENCE",idx=idx,op=op,
                   exactness="GLOBAL_SCALAR_SSA_IDENTITY_EXACT",
                   detail={"role":role,"registers":regs,"external_graph":"d1_gcn_sgpr_ssa/v1",
                           "external_nodes":vals,"external_refs":[f"scalar:{v}" for v in vals]})

    for idx,x in enumerate(ins):
        op=x.get("opcode")
        if op not in sem.OPS: continue
        if x.get("index")!=idx:
            violations.append(f"instruction_index:{idx}:{x.get('index')}");continue
        operands=x.get("operands") or []; vd=[r for r in (x.get("defs") or []) if VREG_RE.fullmatch(r or "")]
        if not vd:
            violations.append(f"missing_vgpr_dest:{idx}:{op}");continue
        vr=vrows[idx];sr=srows[idx];writes=vr.get("vgpr_writes") or []
        if len(writes)!=len(vd):
            violations.append(f"write_width:{idx}:{op}:{len(writes)}!={len(vd)}");continue

        dest_records=[]
        for c,reg in enumerate(vd):
            wr=writes[c]; result=f"result:i{idx}:{reg}"; write=f"write:i{idx}:{reg}"
            rn=vnodes.get(result);wn=vnodes.get(write)
            if wr.get("register")!=reg or wr.get("result")!=result or wr.get("new")!=write or rn is None or wn is None:
                violations.append(f"lane_identity:{idx}:{op}:c{c}:{reg}:{wr}");continue
            if wr.get("kind")!="EXEC_GATED_LANE_WRITE" or wn.get("kind")!="EXEC_GATED_LANE_WRITE":
                violations.append(f"write_kind:{idx}:{op}:{reg}:{wr.get('kind')}:{wn.get('kind')}")
            win=wn.get("inputs") or []
            if len(win)<2 or win[1]!=result or win.count(result)!=1:
                violations.append(f"write_result_edge:{idx}:{op}:{reg}:{win}")
            if result in bound_results or write in bound_writes:
                violations.append(f"duplicate_lane_binding:{idx}:{op}:{reg}")
            bound_results.add(result);bound_writes.add(write)
            dest_records.append((c,reg,result,write))
        if len(dest_records)!=len(vd): continue

        beh=sem.behavior(op); domain=beh["domain"]; op_inputs=[]; controls=_controls(x)
        detail={"domain":domain,"operands":operands,"assembly":x.get("assembly"),"encoded_controls":controls,
                "result_value_status":beh["result_value_status"]}

        if op in sem.IMAGE_OPS:
            if len(operands)!=(4 if op in sem.IMAGE_WITH_SAMPLER else 3):
                violations.append(f"image_operand_count:{idx}:{op}:{len(operands)}:{operands}");continue
            vregs=_expand(operands[1],"v"); rregs=_expand(operands[2],"s")
            if len(vregs)!=4:
                violations.append(f"image_vaddr_width:{idx}:{op}:{vregs}:{operands[1]!r}");continue
            a=vgref(idx,op,"vaddr",vregs,vr); r=sgref(idx,op,"resource_descriptor",rregs,sr,8)
            if a is None or r is None: continue
            op_inputs=[a,r]
            if op in sem.IMAGE_WITH_SAMPLER:
                sregs=_expand(operands[3],"s"); s=sgref(idx,op,"sampler_descriptor",sregs,sr,4)
                if s is None: continue
                op_inputs.append(s)
            counts["image_instruction_count"]+=1
            counts["image_result_component_count"]+=len(vd)

        elif op in sem.BUFFER_OPS:
            if len(operands)<4:
                violations.append(f"buffer_operand_count:{idx}:{op}:{operands}");continue
            vregs=_expand(operands[1],"v"); rregs=_expand(operands[2],"s")
            if len(vregs)!=1:
                violations.append(f"buffer_vaddr_width:{idx}:{op}:{vregs}");continue
            a=vgref(idx,op,"vaddr_or_index",vregs,vr); r=sgref(idx,op,"resource_descriptor",rregs,sr,4)
            if a is None or r is None: continue
            op_inputs=[a,r]
            # BUFFER_LOAD_DWORD has an explicit scalar offset register in the exact observed forms.
            if op=="buffer_load_dword":
                offregs=_expand(operands[3],"s")
                if len(offregs)!=1:
                    violations.append(f"buffer_scalar_offset_shape:{idx}:{operands[3]!r}:{offregs}");continue
                so=sgref(idx,op,"scalar_offset",offregs,sr,1)
                if so is None: continue
                op_inputs.append(so); counts["buffer_scalar_offset_state_reference_count"]+=1
            counts["buffer_instruction_count"]+=1
            counts["buffer_result_component_count"]+=len(vd)

        elif op in sem.DS_OPS:
            if len(operands)!=2:
                violations.append(f"ds_operand_count:{idx}:{op}:{operands}");continue
            vregs=_expand(operands[1],"v")
            if len(vregs)!=1:
                violations.append(f"ds_vsrc_width:{idx}:{op}:{vregs}");continue
            a=vgref(idx,op,"address_or_data",vregs,vr)
            if a is None: continue
            op_inputs=[a]
            if op in sem.DS_MEMORY_OPS:
                m0=sr.get("implicit_m0_use")
                if not m0 or m0.get("register")!="m0" or m0.get("category")!="LDS_DS_M0_BOUNDS":
                    violations.append(f"ds_m0_identity:{idx}:{op}:{m0}");continue
                mv=m0.get("value")
                if mv not in snodes:
                    violations.append(f"ds_m0_state_missing:{idx}:{op}:{mv}");continue
                mr=add(f"resource:i{idx}:m0","EXACT_SCALAR_M0_STATE_REFERENCE",idx=idx,op=op,
                       exactness="GLOBAL_SCALAR_SSA_IDENTITY_EXACT",
                       detail={"role":"LDS_SIZE_CLAMP","external_graph":"d1_gcn_sgpr_ssa/v1",
                               "external_node":mv,"external_ref":f"scalar:{mv}"})
                op_inputs.append(mr);counts["ds_m0_state_reference_count"]+=1
            else:
                if sr.get("implicit_m0_use") is not None:
                    violations.append(f"ds_swizzle_unexpected_m0:{idx}:{sr.get('implicit_m0_use')}");continue
            counts["ds_instruction_count"]+=1
            counts["ds_result_component_count"]+=len(vd)
        else:
            raise AssertionError(op)

        opnode=add(f"resource:i{idx}:operation","GFX7_ARCHITECTURAL_RESOURCE_OPERATION",inputs=op_inputs,idx=idx,op=op,
                   exactness="SOURCE_CLOSED_OPERATION_IDENTITY_VALUE_CONTENT_OPAQUE",detail=detail)
        for c,reg,result,write in dest_records:
            comp=add(f"resource:i{idx}:component{c}","GFX7_RESOURCE_OPERATION_RESULT_COMPONENT",inputs=[opnode],idx=idx,op=op,
                     exactness="ARCHITECTURAL_RESULT_IDENTITY_EXACT_VALUE_CONTENT_OPAQUE",
                     detail={"component":c,"destination":reg,"lane_result":result,"physical_write":write})
            bindings.append({"instruction":idx,"opcode":op,"component":c,"destination":reg,
                             "operation_component":comp,"lane_result":result,"physical_write":write,"domain":domain})
        counts["resource_instruction_count"]+=1; counts["resource_result_component_count"]+=len(vd)
        op_i[op]+=1;op_c[op]+=len(vd)

    if counts["resource_result_component_count"]!=len(bindings):
        violations.append(f"binding_accounting:{len(bindings)}!={counts['resource_result_component_count']}")
    if len(bound_results)!=counts["resource_result_component_count"]:
        violations.append(f"result_identity_accounting:{len(bound_results)}!={counts['resource_result_component_count']}")
    if len(bound_writes)!=counts["resource_result_component_count"]:
        violations.append(f"write_identity_accounting:{len(bound_writes)}!={counts['resource_result_component_count']}")

    coverage={
        **dict(sorted(counts.items())),
        "opcode_instruction_counts":dict(sorted(op_i.items())),
        "opcode_result_component_counts":dict(sorted(op_c.items())),
        "overlay_node_count":len(nodes),
        "shader_expression_semantic_promotions":0,
    }
    return {
        "schema":SCHEMA,"status":STATUS if not violations else "D1_GCN_RESOURCE_VALUE_BINDING_WITH_VIOLATIONS",
        "shader":v2.get("shader"),"instruction_count":len(ins),"coverage":coverage,"nodes":nodes,
        "bindings":bindings,"violations":violations,
        "semantic_boundary":{
            "resource_result_to_existing_lane_ssa":"GLOBAL_EXACT" if not violations else "WITHHELD",
            "resource_operand_vgpr_state":"EXACT" if not violations else "WITHHELD",
            "resource_descriptor_sgpr_state":"EXACT_CROSS_GRAPH" if not violations else "WITHHELD",
            "sampler_descriptor_sgpr_state":"EXACT_CROSS_GRAPH" if not violations else "WITHHELD",
            "lds_m0_state":"EXACT_CROSS_GRAPH" if not violations else "WITHHELD",
            "descriptor_contents":"OPAQUE_STATE_VALUES",
            "runtime_resource_table_assignment":"NEXT_GATE" if not violations else "WITHHELD",
            "image_buffer_lds_contents":"WITHHELD",
            "texture_role_semantics":"WITHHELD",
            "material_semantics":"WITHHELD",
            "shader_expression_semantic_promotions":0,
        },
        "policy":"Every observed IMAGE/BUFFER/DS result is bound to its existing active-lane result and physical write, and every architectural register operand is reconciled to exact VGPR/SGPR/M0 state. Descriptor contents and D1 runtime/material resource assignment are not inferred.",
    }


def main() -> int:
    p=argparse.ArgumentParser();p.add_argument("--structural-ir",type=Path,required=True);p.add_argument("-o","--output",type=Path,required=True);a=p.parse_args()
    d=analyze(json.loads(a.structural_ir.read_text()));a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":d["status"],"coverage":d["coverage"],"violations":d["violations"][:50]},indent=2,sort_keys=True));return 0 if not d["violations"] else 2

if __name__=="__main__": raise SystemExit(main())
