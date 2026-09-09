#!/usr/bin/env python3
"""Build path-aware symbolic EXEC provenance over exact D1 GCN structural IR.

The analysis is deliberately narrower than a shader decompiler. It gives every
instruction an exact wave-mask provenance node, closes all source-backed EXEC
mutations/branches, tracks saved EXEC masks through relevant SGPR pairs, preserves
opaque mask producers as explicit boundaries, and retains both sides of conditional
branches. It never guesses branch feasibility, indirect PC targets, or shader meaning.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
from collections import Counter
from pathlib import Path

import d1_gcn_exec_mask_semantics_v1 as sem

INPUT_STATUS = "D1_GCN_STRUCTURAL_IR_COMPLETE"
INPUT_PARSE_STATUS = "D1_GCN_STRUCTURAL_PARSE_ACCOUNTING_EXACT"
OUTPUT_SCHEMA = "d1_gcn_exec_symbolic_dataflow/v1"
OUTPUT_STATUS = "D1_GCN_EXEC_SYMBOLIC_DATAFLOW_EXACT"
PAIR_RE = re.compile(r"^s\[(\d+):(\d+)\]$")
COND_PREFIX = "s_cbranch_"
UNCOND = {"s_branch"}
TERMINAL = {"s_endpgm"}
INDIRECT = {"s_swappc_b64"}
EXACT_MASK_OPS = {
    "s_mov_b64", "s_wqm_b64", "s_and_b64", "s_andn2_b64", "s_and_saveexec_b64",
    "v_cmpx_eq_i32", "v_cmpx_lt_u32",
}
EXEC_BRANCHES = {"s_cbranch_execz", "s_cbranch_execnz"}


def pair_range(text: str):
    m = PAIR_RE.fullmatch(text)
    if not m:
        return None
    a, b = int(m.group(1)), int(m.group(2))
    if b != a + 1:
        return None
    return (a, b)


def pair_key(text: str):
    r = pair_range(text)
    return None if r is None else f"s[{r[0]}:{r[1]}]"


def overlap_pair_defs(pair: str, defs: list[str]) -> bool:
    r = pair_range(pair)
    if not r:
        return False
    want = {f"s{r[0]}", f"s{r[1]}"}
    return bool(want & set(defs or []))


def _is_explicit_exec_touch(inst: dict) -> bool:
    return "exec" in (inst.get("defs") or []) or "exec" in (inst.get("uses") or [])


def _is_cmpx(inst: dict) -> bool:
    return str(inst.get("opcode", "")) in {"v_cmpx_eq_i32", "v_cmpx_lt_u32"}


def _build_cfg(ins: list[dict]):
    if not ins:
        return [], {}, []
    label_to_index = {lab: x["index"] for x in ins for lab in (x.get("labels") or [])}
    starts = {0}
    for x in ins:
        i = x["index"]; op = x["opcode"]
        if x.get("labels"):
            starts.add(i)
        if op in UNCOND or op.startswith(COND_PREFIX) or op in TERMINAL or op in INDIRECT:
            if i + 1 < len(ins): starts.add(i + 1)
        t = x.get("branch_target_label")
        if t in label_to_index: starts.add(label_to_index[t])
    ss = sorted(starts); blocks=[]; i2b={}
    for bi,s in enumerate(ss):
        e = ss[bi+1]-1 if bi+1 < len(ss) else len(ins)-1
        b={"id":bi,"start_instruction":s,"end_instruction":e,"successors":[],"predecessors":[],"indirect_successor":None}
        blocks.append(b)
        for i in range(s,e+1): i2b[i]=bi
    for b in blocks:
        x=ins[b["end_instruction"]]; op=x["opcode"]; succ=[]
        if op in INDIRECT:
            ops=x.get("operands") or []
            b["indirect_successor"]={
                "kind":"INDIRECT_PC_SWAP","instruction":x["index"],"address":x["address_hex"],
                "source_operand":ops[1] if len(ops)>=2 else (ops[0] if ops else None),
                "concrete_target":None,"fallthrough_edge_emitted":False,
            }
        else:
            t=x.get("branch_target_label")
            if t in label_to_index: succ.append(i2b[label_to_index[t]])
            if op.startswith(COND_PREFIX):
                if x["index"]+1 < len(ins): succ.append(i2b[x["index"]+1])
            elif op not in UNCOND and op not in TERMINAL:
                if x["index"]+1 < len(ins): succ.append(i2b[x["index"]+1])
        b["successors"]=list(dict.fromkeys(succ))
    for b in blocks:
        for s in b["successors"]: blocks[s]["predecessors"].append(b["id"])
    back=[]
    for b in blocks:
        for s in b["successors"]:
            if blocks[s]["start_instruction"] <= b["start_instruction"]:
                back.append({"from_block":b["id"],"to_block":s})
    return blocks,i2b,back


def _relevant_pairs(ins: list[dict]) -> list[str]:
    tracked=set()
    # Seed with any pair directly participating in explicit EXEC mechanics or CMPX.
    for x in ins:
        if _is_explicit_exec_touch(x) or _is_cmpx(x):
            for a in x.get("operands") or []:
                k=pair_key(a)
                if k: tracked.add(k)
    # Backward-close exact scalar mask computations that define a tracked pair.
    changed=True
    while changed:
        changed=False
        for x in reversed(ins):
            op=x["opcode"]; a=x.get("operands") or []
            if op not in {"s_mov_b64","s_wqm_b64","s_and_b64","s_andn2_b64","s_and_saveexec_b64"} or not a:
                continue
            d=pair_key(a[0])
            if d and d in tracked:
                for src in a[1:]:
                    k=pair_key(src)
                    if k and k not in tracked:
                        tracked.add(k); changed=True
    return sorted(tracked, key=lambda s: pair_range(s))


class Graph:
    def __init__(self): self.nodes={}
    def add(self,node_id,kind,*,key=None,inputs=(),instruction=None,opcode=None,operands=None,exactness="SOURCE_CLOSED",detail=None):
        n={"id":node_id,"kind":kind,"inputs":list(inputs),"exactness":exactness}
        if key is not None:n["key"]=key
        if instruction is not None:n["instruction"]=instruction
        if opcode is not None:n["opcode"]=opcode
        if operands is not None:n["operands"]=copy.deepcopy(operands)
        if detail is not None:n["detail"]=detail
        old=self.nodes.get(node_id)
        if old is not None and old != n: raise ValueError(f"node identity collision {node_id}: {old!r} != {n!r}")
        self.nodes[node_id]=n
        return node_id


def analyze(v2: dict) -> dict:
    violations=[]
    if v2.get("status") != INPUT_STATUS: raise ValueError(f"input status {v2.get('status')!r}")
    if (v2.get("parse_accounting") or {}).get("status") != INPUT_PARSE_STATUS: raise ValueError("input parse accounting not exact")
    ins=v2.get("instructions") or []
    blocks,i2b,back=_build_cfg(ins)
    tracked_pairs=_relevant_pairs(ins)
    keys=["exec","vcc","scc",*tracked_pairs]
    g=Graph()
    for k in keys: g.add(f"entry:{k}","PROGRAM_ENTRY",key=k,exactness="SYMBOLIC_INPUT")

    # Fixed identity for every block-entry state. Non-entry blocks use PHI-like nodes even
    # with one predecessor so loops and later predecessor updates never expand expressions.
    entry_ids={}
    for b in blocks:
        entry_ids[b["id"]]={}
        for k in keys:
            if b["id"]==0:
                entry_ids[b["id"]][k]=f"entry:{k}"
            elif b["predecessors"]:
                nid=f"phi:b{b['id']}:{k}"
                entry_ids[b["id"]][k]=nid
                g.add(nid,"CFG_PHI",key=k,inputs=(),exactness="CFG_EXACT")
            else:
                nid=f"external:b{b['id']}:{k}"
                entry_ids[b["id"]][k]=nid
                g.add(nid,"UNRESOLVED_CONTROL_ENTRY",key=k,exactness="CONTROL_TARGET_UNRESOLVED")

    instruction_rows=[None]*len(ins)
    block_exit={}
    exact_exec_op_counts=Counter()
    branch_predicate_count=0
    exec_write_count=0
    opaque_pair_write_count=0
    opaque_vcc_write_count=0
    opaque_scc_write_count=0

    def op_value(state, operand, idx):
        if operand == "exec": return state["exec"]
        if operand == "vcc": return state["vcc"]
        if operand == "scc": return state["scc"]
        k=pair_key(operand)
        if k and k in state: return state[k]
        # Literals, single SGPRs, VGPRs and descriptors remain named leaf inputs.
        nid=f"leaf:i{idx}:{operand}"
        return g.add(nid,"OPERAND_VALUE",detail=operand,exactness="VALUE_UNINTERPRETED")

    def set_pair_from_unknown(state, pair, x):
        nonlocal opaque_pair_write_count
        nid=f"i{x['index']}:{pair}"
        g.add(nid,"OPAQUE_PAIR_DEF",key=pair,instruction=x["index"],opcode=x["opcode"],operands=x.get("operands") or [],exactness="PROVEN_DEF_OPAQUE_VALUE")
        state[pair]=nid; opaque_pair_write_count+=1

    for b in blocks:
        state=dict(entry_ids[b["id"]])
        for ii in range(b["start_instruction"],b["end_instruction"]+1):
            x=ins[ii]; idx=x["index"]; op=x["opcode"]; a=x.get("operands") or []
            if idx != ii: violations.append(f"instruction_index_mismatch:{ii}:{idx}")
            exec_in=state["exec"]
            row={"instruction":idx,"address":x["address_hex"],"opcode":op,"exec_in":exec_in,"exec_out":None,"exec_transition":None,"branch_predicate":None}

            if op in {"s_mov_b64","s_wqm_b64","s_and_b64","s_andn2_b64"} and a:
                dst=a[0]
                dk=dst if dst in ("exec","vcc") else pair_key(dst)
                if dk in state:
                    srcs=[op_value(state,z,idx) for z in a[1:]]
                    kind={"s_mov_b64":"MASK_MOVE","s_wqm_b64":"WQM","s_and_b64":"MASK_AND","s_andn2_b64":"MASK_AND_NOT_SECOND"}[op]
                    nid=f"i{idx}:{dk}"
                    g.add(nid,kind,key=dk,inputs=srcs,instruction=idx,opcode=op,operands=a)
                    state[dk]=nid
                    if dk=="exec": exec_write_count+=1; row["exec_transition"]={"kind":kind,"result":nid,"inputs":srcs}
                    if op != "s_mov_b64":
                        sn=f"i{idx}:scc";g.add(sn,"NONZERO_RESULT",key="scc",inputs=(nid,),instruction=idx,opcode=op);state["scc"]=sn
                    exact_exec_op_counts[op]+=1 if (_is_explicit_exec_touch(x)) else 0
            elif op == "s_and_saveexec_b64" and a:
                dst=pair_key(a[0]); src=op_value(state,a[1],idx) if len(a)>1 else g.add(f"leaf:i{idx}:missing_src","OPERAND_VALUE",detail="MISSING",exactness="INVALID")
                if not dst or dst not in state:
                    violations.append(f"saveexec_untracked_destination:{idx}:{a[0] if a else None}")
                else:
                    saved=f"i{idx}:{dst}";g.add(saved,"SAVE_OLD_EXEC",key=dst,inputs=(exec_in,),instruction=idx,opcode=op,operands=a);state[dst]=saved
                    en=f"i{idx}:exec";g.add(en,"MASK_AND",key="exec",inputs=(src,exec_in),instruction=idx,opcode=op,operands=a);state["exec"]=en
                    sn=f"i{idx}:scc";g.add(sn,"NONZERO_RESULT",key="scc",inputs=(en,),instruction=idx,opcode=op);state["scc"]=sn
                    exec_write_count+=1; exact_exec_op_counts[op]+=1
                    row["exec_transition"]={"kind":"SAVEEXEC_AND","result":en,"inputs":[src,exec_in],"saved_old_exec":saved}
            elif op in {"v_cmpx_eq_i32","v_cmpx_lt_u32"}:
                if len(a)<3:
                    violations.append(f"cmpx_operands:{idx}:{a!r}")
                else:
                    dst=pair_key(a[0]) or (a[0] if a[0] in ("vcc",) else None)
                    src0=op_value(state,a[1],idx);src1=op_value(state,a[2],idx)
                    nid=f"i{idx}:cmpx_mask"
                    g.add(nid,"CMPX_ACTIVE_MASK",inputs=(exec_in,src0,src1),instruction=idx,opcode=op,operands=a,detail=sem.REGISTRY[op]["result"])
                    state["exec"]=nid
                    if dst in state: state[dst]=nid
                    else: violations.append(f"cmpx_untracked_destination:{idx}:{a[0]}")
                    exec_write_count+=1;exact_exec_op_counts[op]+=1
                    row["exec_transition"]={"kind":"CMPX_ACTIVE_MASK","result":nid,"inputs":[exec_in,src0,src1],"compare_destination":dst}
            elif op in EXEC_BRANCHES:
                pred=f"pred:i{idx}"
                kind="EXEC_EQ_ZERO" if op=="s_cbranch_execz" else "EXEC_NE_ZERO"
                g.add(pred,kind,inputs=(state["exec"],),instruction=idx,opcode=op,operands=a)
                row["branch_predicate"]={"node":pred,"kind":kind,"exec":state["exec"],"target":x.get("branch_target_label")}
                branch_predicate_count+=1; exact_exec_op_counts[op]+=1

            # Structural/opaque writers that were not consumed by an exact rule above.
            handled_pair_dest = False
            if a:
                dpk=pair_key(a[0])
                if dpk in tracked_pairs and op in EXACT_MASK_OPS:
                    handled_pair_dest=True
            if op not in EXACT_MASK_OPS:
                for p in tracked_pairs:
                    if overlap_pair_defs(p,x.get("defs") or []):
                        set_pair_from_unknown(state,p,x)
                if "vcc" in (x.get("defs") or []):
                    nid=f"i{idx}:vcc";g.add(nid,"OPAQUE_VCC_DEF",key="vcc",inputs=(exec_in,),instruction=idx,opcode=op,operands=a,exactness="PROVEN_DEF_OPAQUE_VALUE");state["vcc"]=nid;opaque_vcc_write_count+=1
                if "scc" in (x.get("defs") or []):
                    nid=f"i{idx}:scc";g.add(nid,"OPAQUE_SCC_DEF",key="scc",instruction=idx,opcode=op,operands=a,exactness="PROVEN_DEF_OPAQUE_VALUE");state["scc"]=nid;opaque_scc_write_count+=1
                if "exec" in (x.get("defs") or []):
                    violations.append(f"unknown_exec_writer:{idx}:{op}")
            # Any explicit EXEC touch must belong to the exact machine registry.
            if _is_explicit_exec_touch(x) and op not in sem.REGISTRY:
                violations.append(f"explicit_exec_touch_not_in_registry:{idx}:{op}")
            row["exec_out"]=state["exec"]
            instruction_rows[ii]=row
        block_exit[b["id"]]=dict(state)

    # Now populate fixed PHI inputs from predecessor exits.
    for b in blocks:
        if b["id"]==0 or not b["predecessors"]: continue
        for k in keys:
            nid=entry_ids[b["id"]][k]
            inputs=[block_exit[p][k] for p in b["predecessors"]]
            n=g.nodes[nid]; n["inputs"]=inputs

    # Node graph integrity.
    for nid,n in g.nodes.items():
        for src in n.get("inputs") or []:
            if src not in g.nodes:
                violations.append(f"missing_node_reference:{nid}->{src}")
    for r in instruction_rows:
        if r is None: violations.append("missing_instruction_row")
        elif r["exec_in"] not in g.nodes or r["exec_out"] not in g.nodes:
            violations.append(f"instruction_exec_node_missing:{r['instruction']}")

    exec_transitions=sum(1 for r in instruction_rows if r and r["exec_transition"])
    explicit_exec_touches=sum(1 for x in ins if _is_explicit_exec_touch(x))
    cmpx_count=sum(1 for x in ins if _is_cmpx(x))
    orphan_blocks=sum(1 for b in blocks if b["id"]!=0 and not b["predecessors"])
    phi_nodes=sum(1 for n in g.nodes.values() if n["kind"]=="CFG_PHI")
    return {
        "schema":OUTPUT_SCHEMA,
        "status":OUTPUT_STATUS if not violations else "D1_GCN_EXEC_SYMBOLIC_DATAFLOW_WITH_VIOLATIONS",
        "shader":v2.get("shader"),
        "parse_accounting":copy.deepcopy(v2["parse_accounting"]),
        "instruction_count":len(ins),
        "basic_block_count":len(blocks),
        "concrete_cfg_edge_count":sum(len(b["successors"]) for b in blocks),
        "back_edges":back,
        "tracked_mask_keys":keys,
        "tracked_sgpr_pairs":tracked_pairs,
        "node_count":len(g.nodes),
        "phi_node_count":phi_nodes,
        "unresolved_control_entry_block_count":orphan_blocks,
        "explicit_structural_exec_touch_count":explicit_exec_touches,
        "implicit_cmpx_exec_touch_count":cmpx_count,
        "exec_transition_count":exec_transitions,
        "exec_branch_predicate_count":branch_predicate_count,
        "exec_write_count":exec_write_count,
        "opaque_pair_write_count":opaque_pair_write_count,
        "opaque_vcc_write_count":opaque_vcc_write_count,
        "opaque_scc_write_count":opaque_scc_write_count,
        "exact_machine_exec_opcode_counts":dict(sorted(exact_exec_op_counts.items())),
        "instructions":instruction_rows,
        "blocks":[{
            "id":b["id"],"start_instruction":b["start_instruction"],"end_instruction":b["end_instruction"],
            "predecessors":b["predecessors"],"successors":b["successors"],"indirect_successor":b["indirect_successor"],
            "exec_in":entry_ids[b["id"]]["exec"],"exec_out":block_exit[b["id"]]["exec"],
        } for b in blocks],
        "nodes":g.nodes,
        "violations":violations,
        "semantic_boundary":{
            "exec_machine_semantics":"SOURCE_CLOSED",
            "cfg_path_merge":"EXACT_WITH_UNRESOLVED_INDIRECT_TARGETS",
            "mask_carrier_unknown_values":"EXPLICIT_OPAQUE_NODES",
            "branch_feasibility":"WITHHELD",
            "lane_aware_vgpr_ssa":"NEXT_GATE",
            "shader_expression_semantics":"WITHHELD",
            "shader_expression_semantic_promotions":0,
        },
        "policy":(
            "Every instruction receives symbolic EXEC-in/EXEC-out provenance over the effect-aware concrete CFG. Exact "
            "Sea Islands mask operations are represented algebraically; unknown mask-producing values remain explicit opaque "
            "nodes. Conditional branch feasibility and indirect targets are not guessed, so high-level shader semantics remain withheld."
        ),
    }


def main():
    ap=argparse.ArgumentParser();ap.add_argument("--structural-ir",type=Path,required=True);ap.add_argument("-o","--output",type=Path,required=True);a=ap.parse_args()
    out=analyze(json.loads(a.structural_ir.read_text()))
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:out[k] for k in ("status","shader","instruction_count","basic_block_count","node_count","exec_transition_count","exec_branch_predicate_count")}|{"violation_count":len(out["violations"])},indent=2))
    for x in out["violations"][:100]:print("VIOLATION",x)
    return 0 if not out["violations"] else 2

if __name__=="__main__": raise SystemExit(main())
