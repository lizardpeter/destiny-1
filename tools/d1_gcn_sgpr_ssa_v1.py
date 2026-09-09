#!/usr/bin/env python3
"""Path-aware physical SGPR/M0 SSA for the exact Destiny 1 GFX7 structural IR.

This layer closes scalar register state identity, not scalar expression meaning. Ordinary
whole-register destinations become new definitions; S_ADDK_I32 explicitly reads the old
destination; vector compares targeting SGPR pairs preserve inactive EXEC lane bits; and
architectural implicit M0 consumers are linked to the current M0 definition even though
CLRX structural def/use text omits those dependencies.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
from collections import Counter
from pathlib import Path

import d1_gcn_exec_symbolic_dataflow_v1 as exec_sym
import d1_gcn_m0_implicit_frontier_v1 as m0_frontier
import d1_gcn_sgpr_machine_semantics_v1 as machine

INPUT_STATUS = "D1_GCN_STRUCTURAL_IR_COMPLETE"
INPUT_PARSE_STATUS = "D1_GCN_STRUCTURAL_PARSE_ACCOUNTING_EXACT"
EXEC_STATUS = "D1_GCN_EXEC_SYMBOLIC_DATAFLOW_EXACT"
OUTPUT_SCHEMA = "d1_gcn_sgpr_ssa/v1"
OUTPUT_STATUS = "D1_GCN_SGPR_SSA_EXACT"
SREG_RE = re.compile(r"^s(\d+)$")
PAIR_RE = re.compile(r"^s\[(\d+):(\d+)\]$")


def is_scalar_reg(x: str) -> bool:
    return bool(SREG_RE.fullmatch(x or "")) or x == "m0"


def skey(x: str) -> tuple[int, str]:
    if x == "m0":
        return (1 << 29, x)
    m = SREG_RE.fullmatch(x or "")
    return (int(m.group(1)), x) if m else (1 << 30, x)


def tracked_scalars(ins: list[dict]) -> list[str]:
    regs = {
        r
        for x in ins
        for r in [*(x.get("defs") or []), *(x.get("uses") or [])]
        if is_scalar_reg(r)
    }
    regs.add("m0")
    return sorted(regs, key=skey)


class Graph:
    def __init__(self):
        self.nodes: dict[str, dict] = {}

    def add(self, node_id: str, kind: str, *, key=None, inputs=(), instruction=None,
            opcode=None, operands=None, exactness="SOURCE_CLOSED", detail=None) -> str:
        n = {"id": node_id, "kind": kind, "inputs": list(inputs), "exactness": exactness}
        if key is not None:
            n["key"] = key
        if instruction is not None:
            n["instruction"] = instruction
        if opcode is not None:
            n["opcode"] = opcode
        if operands is not None:
            n["operands"] = copy.deepcopy(operands)
        if detail is not None:
            n["detail"] = copy.deepcopy(detail)
        old = self.nodes.get(node_id)
        if old is not None and old != n:
            raise ValueError(f"node identity collision {node_id}: {old!r} != {n!r}")
        self.nodes[node_id] = n
        return node_id


def analyze(v2: dict) -> dict:
    violations: list[str] = []
    if v2.get("status") != INPUT_STATUS:
        raise ValueError(f"input status {v2.get('status')!r}")
    if (v2.get("parse_accounting") or {}).get("status") != INPUT_PARSE_STATUS:
        raise ValueError("input parse accounting not exact")

    ex = exec_sym.analyze(v2)
    if ex.get("status") != EXEC_STATUS or ex.get("violations"):
        raise ValueError(f"EXEC prerequisite not exact: {ex.get('status')}: {ex.get('violations', [])[:3]}")

    ins = v2.get("instructions") or []
    exrows = ex.get("instructions") or []
    blocks = ex.get("blocks") or []
    if len(exrows) != len(ins):
        raise ValueError("EXEC instruction roster mismatch")

    tracked = tracked_scalars(ins)
    g = Graph()
    for reg in tracked:
        g.add(f"entry:{reg}", "PROGRAM_ENTRY", key=reg, exactness="SYMBOLIC_INPUT")

    entry: dict[int, dict[str, str]] = {}
    for b in blocks:
        bid = b["id"]
        entry[bid] = {}
        for reg in tracked:
            if bid == 0:
                entry[bid][reg] = f"entry:{reg}"
            elif b["predecessors"]:
                nid = f"phi:b{bid}:{reg}"
                entry[bid][reg] = nid
                g.add(nid, "CFG_PHI", key=reg, exactness="CFG_EXACT")
            else:
                nid = f"external:b{bid}:{reg}"
                entry[bid][reg] = nid
                g.add(nid, "UNRESOLVED_CONTROL_ENTRY", key=reg, exactness="CONTROL_TARGET_UNRESOLVED")

    rows: list[dict | None] = [None] * len(ins)
    block_exit: dict[int, dict[str, str]] = {}
    counts = Counter()
    def_ops = Counter()
    def_entries = Counter()
    use_ops = Counter()
    use_entries = Counter()
    m0_use_ops = Counter()

    def exec_ref(idx: int) -> str:
        return g.add(
            f"exec_ref:i{idx}:in", "EXEC_CHECKPOINT_REFERENCE", instruction=idx,
            exactness="GLOBAL_EXEC_EXACT", detail=exrows[idx]["exec_in"]
        )

    def non_scalar_leaf(idx: int, ordinal: int, value: str) -> str:
        return g.add(
            f"leaf:i{idx}:src{ordinal}", "NON_SCALAR_SOURCE_AT_INSTRUCTION",
            instruction=idx, exactness="VALUE_UNINTERPRETED_AT_USE", detail=value
        )

    for b in blocks:
        state = dict(entry[b["id"]])
        for ii in range(b["start_instruction"], b["end_instruction"] + 1):
            x = ins[ii]
            idx = x["index"]
            if idx != ii:
                violations.append(f"instruction_index_mismatch:{ii}:{idx}")
                continue
            op = x["opcode"]
            operands = x.get("operands") or []
            defs = x.get("defs") or []
            uses = x.get("uses") or []
            sd = [r for r in defs if is_scalar_reg(r)]
            su = [r for r in uses if is_scalar_reg(r)]
            non_su = [r for r in uses if not is_scalar_reg(r)]
            before = dict(state)

            for r in su:
                if r not in before:
                    violations.append(f"untracked_scalar_use:{idx}:{r}")

            category, m0_problem = m0_frontier.classify_instruction(x)
            implicit_m0 = (
                category is not None
                and category != "DS_NON_MEMORY_NO_M0_VALUE_DEPENDENCY"
            )
            if m0_problem:
                violations.append(f"unresolved_m0_semantics:{idx}:{op}:{m0_problem}")

            row = {
                "instruction": idx,
                "address": x["address_hex"],
                "opcode": op,
                "scalar_uses": [{"register": r, "value": before[r], "kind": "STRUCTURAL_EXPLICIT"} for r in su],
                "implicit_m0_use": None,
                "implicit_rmw_uses": [],
                "scalar_writes": [],
            }
            if implicit_m0:
                row["implicit_m0_use"] = {
                    "register": "m0", "value": before["m0"], "category": category,
                    "kind": "ARCHITECTURAL_IMPLICIT_M0"
                }
                counts["implicit_m0_use_instruction_count"] += 1
                m0_use_ops[op] += 1

            if sd:
                if op not in machine.OBSERVED_SGPR_DEF_OPCODES:
                    violations.append(f"unregistered_sgpr_def_opcode:{idx}:{op}")
                else:
                    beh = machine.behavior(op)
                    source_nodes = [before[r] for r in su if r in before]
                    special_nodes = [non_scalar_leaf(idx, j, r) for j, r in enumerate(non_su)]
                    if implicit_m0:
                        source_nodes.append(before["m0"])
                    source_nodes.extend(special_nodes)

                    if beh["write_behavior"] == "EXEC_GATED_MASK_HALF_WRITE":
                        if len(sd) != 2:
                            violations.append(f"compare_sgpr_pair_shape:{idx}:{op}:{sd!r}:{operands!r}")
                        pair = operands[0] if operands else None
                        pm = PAIR_RE.fullmatch(pair or "")
                        if not pm or [f"s{i}" for i in range(int(pm.group(1)), int(pm.group(2)) + 1)] != sd:
                            violations.append(f"compare_pair_operand_mismatch:{idx}:{pair!r}:{sd!r}")
                        e = exec_ref(idx)
                        for component, reg in enumerate(sd):
                            old = before[reg]
                            result = g.add(
                                f"result:i{idx}:{reg}", "OPAQUE_COMPARE_MASK_HALF_RESULT",
                                key=reg, inputs=source_nodes, instruction=idx, opcode=op,
                                operands=operands, exactness="COMPARE_VALUE_WITHHELD",
                                detail={"pair": pair, "half": component}
                            )
                            write = g.add(
                                f"write:i{idx}:{reg}", "EXEC_GATED_MASK_HALF_WRITE",
                                key=reg, inputs=(old, result, e), instruction=idx, opcode=op,
                                operands=operands, exactness="SOURCE_CLOSED_MASK_HALF_MUTATION",
                                detail={"half": component, "inactive_exec_bits": "PRESERVE_OLD"}
                            )
                            state[reg] = write
                            row["scalar_writes"].append({
                                "register": reg, "old": old, "result": result, "new": write,
                                "kind": "EXEC_GATED_MASK_HALF_WRITE", "half": component,
                                "exec": exrows[idx]["exec_in"]
                            })
                            counts["exec_gated_mask_half_write_entry_count"] += 1
                            counts["scalar_result_component_node_count"] += 1
                            def_entries[op] += 1
                        def_ops[op] += 1
                    elif beh["write_behavior"] in {"WHOLE_SCALAR_WRITE", "WHOLE_SCALAR_RMW_WRITE"}:
                        if beh["write_behavior"] == "WHOLE_SCALAR_RMW_WRITE":
                            if len(sd) != 1:
                                violations.append(f"rmw_shape:{idx}:{op}:{sd!r}")
                            if sd:
                                source_nodes = [before[sd[0]], *source_nodes]
                                row["implicit_rmw_uses"].append({
                                    "register": sd[0], "value": before[sd[0]], "kind": "DESTINATION_READ_MODIFY_WRITE"
                                })
                                counts["implicit_rmw_use_entry_count"] += 1
                        for component, reg in enumerate(sd):
                            old = before[reg]
                            result = g.add(
                                f"result:i{idx}:{reg}", "OPAQUE_SCALAR_RESULT_COMPONENT",
                                key=reg, inputs=source_nodes, instruction=idx, opcode=op,
                                operands=operands, exactness="VALUE_SEMANTICS_WITHHELD",
                                detail={"destination_component": component}
                            )
                            write_kind = beh["write_behavior"]
                            write_inputs = (old, result) if write_kind == "WHOLE_SCALAR_RMW_WRITE" else (result,)
                            write = g.add(
                                f"write:i{idx}:{reg}", write_kind, key=reg, inputs=write_inputs,
                                instruction=idx, opcode=op, operands=operands,
                                exactness="SOURCE_CLOSED_SCALAR_REGISTER_MUTATION",
                                detail={"destination_component": component}
                            )
                            state[reg] = write
                            row["scalar_writes"].append({
                                "register": reg, "old": old, "result": result, "new": write,
                                "kind": write_kind, "destination_component": component
                            })
                            counts["whole_scalar_write_entry_count"] += 1
                            if write_kind == "WHOLE_SCALAR_RMW_WRITE":
                                counts["whole_scalar_rmw_write_entry_count"] += 1
                            counts["scalar_result_component_node_count"] += 1
                            def_entries[op] += 1
                        def_ops[op] += 1
                    else:
                        violations.append(f"unknown_scalar_write_behavior:{idx}:{op}:{beh['write_behavior']}")

                counts["sgpr_def_instruction_count"] += 1
                counts["sgpr_def_entry_count"] += len(sd)
            if su:
                counts["sgpr_use_instruction_count"] += 1
                counts["sgpr_use_entry_count"] += len(su)
                use_ops[op] += 1
                use_entries[op] += len(su)

            rows[ii] = row
        block_exit[b["id"]] = dict(state)

    for b in blocks:
        if b["id"] == 0 or not b["predecessors"]:
            continue
        for reg in tracked:
            nid = entry[b["id"]][reg]
            g.nodes[nid]["inputs"] = [block_exit[p][reg] for p in b["predecessors"]]

    for nid, n in g.nodes.items():
        for src in n.get("inputs") or []:
            if src not in g.nodes:
                violations.append(f"missing_node_reference:{nid}->{src}")
    for i, r in enumerate(rows):
        if r is None:
            violations.append(f"missing_instruction_row:{i}")
            continue
        sd = [z for z in (ins[i].get("defs") or []) if is_scalar_reg(z)]
        if len(r["scalar_writes"]) != len(sd):
            violations.append(f"write_accounting:{i}:{len(r['scalar_writes'])}!={len(sd)}")

    exact_writes = counts["whole_scalar_write_entry_count"] + counts["exec_gated_mask_half_write_entry_count"]
    if exact_writes != counts["sgpr_def_entry_count"]:
        violations.append(f"global_write_accounting:{exact_writes}!={counts['sgpr_def_entry_count']}")
    if counts["scalar_result_component_node_count"] != counts["sgpr_def_entry_count"]:
        violations.append(
            f"result_component_accounting:{counts['scalar_result_component_node_count']}!={counts['sgpr_def_entry_count']}"
        )

    phi_count = sum(1 for n in g.nodes.values() if n["kind"] == "CFG_PHI")
    orphan_blocks = sum(1 for b in blocks if b["id"] != 0 and not b["predecessors"])
    entry_nodes = sum(1 for n in g.nodes.values() if n["kind"] == "PROGRAM_ENTRY")
    unresolved_nodes = sum(1 for n in g.nodes.values() if n["kind"] == "UNRESOLVED_CONTROL_ENTRY")
    leaf_nodes = sum(1 for n in g.nodes.values() if n["kind"] == "NON_SCALAR_SOURCE_AT_INSTRUCTION")

    coverage = {
        "tracked_scalar_register_count": len(tracked),
        "max_tracked_sgpr_index": max((int(r[1:]) for r in tracked if r != "m0"), default=-1),
        "m0_tracked": "m0" in tracked,
        "entry_node_count": entry_nodes,
        "cfg_phi_node_count": phi_count,
        "unresolved_control_entry_block_count": orphan_blocks,
        "unresolved_control_entry_scalar_node_count": unresolved_nodes,
        "non_scalar_source_leaf_count": leaf_nodes,
        **dict(sorted(counts.items())),
        "sgpr_def_opcode_counts": dict(sorted(def_ops.items())),
        "sgpr_def_entry_opcode_counts": dict(sorted(def_entries.items())),
        "sgpr_use_opcode_counts": dict(sorted(use_ops.items())),
        "sgpr_use_entry_opcode_counts": dict(sorted(use_entries.items())),
        "implicit_m0_use_opcode_counts": dict(sorted(m0_use_ops.items())),
        "shader_expression_semantic_promotions": 0,
    }

    return {
        "schema": OUTPUT_SCHEMA,
        "status": OUTPUT_STATUS if not violations else "D1_GCN_SGPR_SSA_WITH_VIOLATIONS",
        "shader": v2.get("shader"),
        "parse_accounting": copy.deepcopy(v2["parse_accounting"]),
        "instruction_count": len(ins),
        "basic_block_count": len(blocks),
        "concrete_cfg_edge_count": sum(len(b["successors"]) for b in blocks),
        "tracked_scalar_registers": tracked,
        "coverage": coverage,
        "instructions": rows,
        "nodes": g.nodes,
        "violations": violations,
        "semantic_boundary": {
            "exec_symbolic_dataflow": "GLOBAL_EXACT_PREREQUISITE",
            "sgpr_m0_structural_identity": "GLOBAL_EXACT_PREREQUISITE",
            "m0_implicit_consumer_surface": "GLOBAL_EXACT_PREREQUISITE",
            "physical_sgpr_m0_ssa": "EXACT" if not violations else "NOT_PROMOTED",
            "compare_mask_inactive_bit_preservation": "EXACT" if not violations else "NOT_PROMOTED",
            "scalar_rmw_destination_identity": "EXACT" if not violations else "NOT_PROMOTED",
            "opcode_result_value_semantics": "NEXT_GATE" if not violations else "WITHHELD",
            "shader_expression_semantics": "WITHHELD",
            "shader_expression_semantic_promotions": 0,
        },
        "policy": "Physical SGPR and M0 state is SSA-renamed over the exact CFG. Compare-mask halves preserve inactive EXEC bits, S_ADDK reads its old destination, and ISA-proven implicit M0 consumers reference the current M0 node. Result values remain opaque; no arithmetic, memory, interpolation, image, material or shader expression is promoted.",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--structural-ir", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()
    out = analyze(json.loads(a.structural_ir.read_text()))
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": out["status"],
        "instruction_count": out["instruction_count"],
        "basic_block_count": out["basic_block_count"],
        "node_count": len(out["nodes"]),
        "coverage": out["coverage"],
        "violations": out["violations"][:20],
    }, indent=2, sort_keys=True))
    return 0 if not out["violations"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
