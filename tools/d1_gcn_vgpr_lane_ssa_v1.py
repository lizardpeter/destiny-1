#!/usr/bin/env python3
"""Lane-aware physical-VGPR SSA over exact Destiny 1 GFX7 structural IR.

This layer closes register state identity, not shader-expression meaning. Each ordinary
VGPR destination is represented as an EXEC-gated lane merge between the old physical
register state and an opaque instruction-result component. V_WRITELANE_B32 instead
updates exactly one literal-selected lane without consulting EXEC. V_MOVRELS_B32 keeps
its M0-indexed source as an explicit dynamic-read boundary rather than pretending the
encoded base VGPR is the actual source.

Scalar/condition operands remain instruction-local symbolic leaves. Their own def-site
SSA is intentionally a later value-provenance layer; this file does not invent it.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
from collections import Counter
from pathlib import Path

import d1_gcn_exec_symbolic_dataflow_v1 as exec_sym
import d1_gcn_vgpr_machine_semantics_v1 as machine

INPUT_STATUS = "D1_GCN_STRUCTURAL_IR_COMPLETE"
INPUT_PARSE_STATUS = "D1_GCN_STRUCTURAL_PARSE_ACCOUNTING_EXACT"
EXEC_STATUS = "D1_GCN_EXEC_SYMBOLIC_DATAFLOW_EXACT"
OUTPUT_SCHEMA = "d1_gcn_vgpr_lane_ssa/v1"
OUTPUT_STATUS = "D1_GCN_VGPR_LANE_SSA_EXACT"
VREG_RE = re.compile(r"^v(\d+)$")
SREG_RE = re.compile(r"^s(\d+)$")


def is_vgpr(x: str) -> bool:
    return bool(VREG_RE.fullmatch(x or ""))


def vkey(x: str) -> tuple[int, str]:
    m = VREG_RE.fullmatch(x)
    return (int(m.group(1)), x) if m else (1 << 30, x)


class Graph:
    def __init__(self):
        self.nodes: dict[str, dict] = {}

    def add(
        self,
        node_id: str,
        kind: str,
        *,
        key: str | None = None,
        inputs=(),
        instruction: int | None = None,
        opcode: str | None = None,
        operands=None,
        exactness: str = "SOURCE_CLOSED",
        detail=None,
    ) -> str:
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


def _tracked_vgprs(ins: list[dict]) -> list[str]:
    regs = {
        r
        for x in ins
        for r in [*(x.get("defs") or []), *(x.get("uses") or [])]
        if is_vgpr(r)
    }
    return sorted(regs, key=vkey)


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

    tracked = _tracked_vgprs(ins)
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
    opcode_write_counts = Counter()
    opcode_write_entry_counts = Counter()

    def exec_ref(idx: int) -> str:
        er = exrows[idx]
        return g.add(
            f"exec_ref:i{idx}:in",
            "EXEC_CHECKPOINT_REFERENCE",
            instruction=idx,
            exactness="GLOBAL_EXEC_EXACT",
            detail=er["exec_in"],
        )

    def non_vgpr_leaf(idx: int, ordinal: int, value: str) -> str:
        return g.add(
            f"leaf:i{idx}:src{ordinal}",
            "NON_VGPR_SOURCE_AT_INSTRUCTION",
            instruction=idx,
            exactness="VALUE_UNINTERPRETED_AT_USE",
            detail=value,
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
            vd = [r for r in defs if is_vgpr(r)]
            vu = [r for r in uses if is_vgpr(r)]
            non_vu = [r for r in uses if not is_vgpr(r)]
            before = dict(state)

            row = {
                "instruction": idx,
                "address": x["address_hex"],
                "opcode": op,
                "vgpr_uses": [{"register": r, "value": before[r]} for r in vu],
                "vgpr_writes": [],
                "exec_in_reference": exrows[idx]["exec_in"],
            }

            for r in vu:
                if r not in before:
                    violations.append(f"untracked_vgpr_use:{idx}:{r}")

            if vd:
                if op not in machine.VGPR_DEF_OPCODES:
                    violations.append(f"unregistered_vgpr_def_opcode:{idx}:{op}")
                else:
                    beh = machine.behavior(op)
                    source_nodes = [before[r] for r in vu if r in before]
                    scalar_nodes = [non_vgpr_leaf(idx, j, r) for j, r in enumerate(non_vu)]

                    if op == "v_movrels_b32":
                        if len(vd) != 1 or len(vu) != 1:
                            violations.append(f"movrels_shape:{idx}:{vd!r}:{vu!r}:{operands!r}")
                        dynamic = g.add(
                            f"dynamic_read:i{idx}",
                            "DYNAMIC_VGPR_READ",
                            instruction=idx,
                            opcode=op,
                            operands=operands,
                            exactness="SOURCE_CLOSED_IDENTITY_OPAQUE_VALUE",
                            detail={
                                "identity": "VGPR[encoded_source + M0]",
                                "encoded_source": operands[1] if len(operands) > 1 else None,
                                "structural_base_vgpr": vu[0] if vu else None,
                                "m0_indexed": True,
                            },
                        )
                        source_nodes = [dynamic, *scalar_nodes]
                        counts["dynamic_vgpr_read_boundary_count"] += 1
                    else:
                        source_nodes = [*source_nodes, *scalar_nodes]

                    if beh["write_behavior"] == "SINGLE_LANE_UNMASKED":
                        if op != "v_writelane_b32" or len(vd) != 1 or len(operands) < 3:
                            violations.append(f"single_lane_shape:{idx}:{op}:{vd!r}:{operands!r}")
                        lane = None
                        if len(operands) >= 3:
                            try:
                                lane = int(operands[2], 0)
                            except Exception:
                                violations.append(f"single_lane_nonliteral:{idx}:{operands[2]!r}")
                        reg = vd[0]
                        old = before[reg]
                        value = g.add(
                            f"result:i{idx}:{reg}",
                            "OPAQUE_INSTRUCTION_RESULT_COMPONENT",
                            key=reg,
                            inputs=source_nodes,
                            instruction=idx,
                            opcode=op,
                            operands=operands,
                            exactness="VALUE_SEMANTICS_WITHHELD",
                            detail={"destination_component": 0},
                        )
                        write = g.add(
                            f"write:i{idx}:{reg}",
                            "SINGLE_LANE_WRITE",
                            key=reg,
                            inputs=(old, value),
                            instruction=idx,
                            opcode=op,
                            operands=operands,
                            exactness="SOURCE_CLOSED_LANE_MUTATION",
                            detail={
                                "lane": lane,
                                "exec_dependency": "IGNORES_EXEC",
                                "preserve": "ALL_OTHER_LANES",
                            },
                        )
                        state[reg] = write
                        row["vgpr_writes"].append({
                            "register": reg,
                            "old": old,
                            "result": value,
                            "new": write,
                            "kind": "SINGLE_LANE_WRITE",
                            "lane": lane,
                            "exec": None,
                        })
                        counts["single_lane_write_node_count"] += 1
                        counts["vgpr_result_component_node_count"] += 1
                        opcode_write_counts[op] += 1
                        opcode_write_entry_counts[op] += 1
                    elif beh["write_behavior"] == "EXEC_MASKED_WHOLE_LANE_DEST":
                        e = exec_ref(idx)
                        for component, reg in enumerate(vd):
                            old = before[reg]
                            value = g.add(
                                f"result:i{idx}:{reg}",
                                "OPAQUE_INSTRUCTION_RESULT_COMPONENT",
                                key=reg,
                                inputs=source_nodes,
                                instruction=idx,
                                opcode=op,
                                operands=operands,
                                exactness=(
                                    "DYNAMIC_SOURCE_IDENTITY_ONLY"
                                    if op == "v_movrels_b32"
                                    else "VALUE_SEMANTICS_WITHHELD"
                                ),
                                detail={"destination_component": component},
                            )
                            write = g.add(
                                f"write:i{idx}:{reg}",
                                "EXEC_GATED_LANE_WRITE",
                                key=reg,
                                inputs=(old, value, e),
                                instruction=idx,
                                opcode=op,
                                operands=operands,
                                exactness="SOURCE_CLOSED_LANE_MUTATION",
                                detail={
                                    "active_lanes": "RESULT_COMPONENT",
                                    "inactive_lanes": "PRESERVE_OLD",
                                    "exec_dependency": "EXEC_IN",
                                    "destination_component": component,
                                },
                            )
                            state[reg] = write
                            row["vgpr_writes"].append({
                                "register": reg,
                                "old": old,
                                "result": value,
                                "new": write,
                                "kind": "EXEC_GATED_LANE_WRITE",
                                "exec": exrows[idx]["exec_in"],
                                "destination_component": component,
                            })
                            counts["exec_gated_write_node_count"] += 1
                            counts["vgpr_result_component_node_count"] += 1
                            opcode_write_entry_counts[op] += 1
                        opcode_write_counts[op] += 1
                    else:
                        violations.append(f"unknown_write_behavior:{idx}:{op}:{beh['write_behavior']}")

                counts["vgpr_def_instruction_count"] += 1
                counts["vgpr_def_entry_count"] += len(vd)
            if vu:
                counts["vgpr_use_instruction_count"] += 1
                counts["vgpr_use_entry_count"] += len(vu)

            rows[ii] = row
        block_exit[b["id"]] = dict(state)

    # Fixed PHI identities permit exact loop/backedge wiring without expression expansion.
    for b in blocks:
        if b["id"] == 0 or not b["predecessors"]:
            continue
        for reg in tracked:
            nid = entry[b["id"]][reg]
            g.nodes[nid]["inputs"] = [block_exit[p][reg] for p in b["predecessors"]]

    # Integrity: every graph edge resolves, every structural definition gets one write
    # node per expanded physical destination, and every instruction receives a row.
    for nid, n in g.nodes.items():
        for src in n.get("inputs") or []:
            if src not in g.nodes:
                violations.append(f"missing_node_reference:{nid}->{src}")
    for i, r in enumerate(rows):
        if r is None:
            violations.append(f"missing_instruction_row:{i}")
            continue
        x = ins[i]
        vd = [z for z in (x.get("defs") or []) if is_vgpr(z)]
        if len(r["vgpr_writes"]) != len(vd):
            violations.append(f"write_accounting:{i}:{len(r['vgpr_writes'])}!={len(vd)}")

    phi_count = sum(1 for n in g.nodes.values() if n["kind"] == "CFG_PHI")
    orphan_count = sum(1 for b in blocks if b["id"] != 0 and not b["predecessors"])
    entry_node_count = sum(1 for n in g.nodes.values() if n["kind"] == "PROGRAM_ENTRY")
    unresolved_nodes = sum(1 for n in g.nodes.values() if n["kind"] == "UNRESOLVED_CONTROL_ENTRY")
    scalar_leaf_count = sum(1 for n in g.nodes.values() if n["kind"] == "NON_VGPR_SOURCE_AT_INSTRUCTION")
    exact_write_count = counts["exec_gated_write_node_count"] + counts["single_lane_write_node_count"]
    if exact_write_count != counts["vgpr_def_entry_count"]:
        violations.append(f"global_write_accounting:{exact_write_count}!={counts['vgpr_def_entry_count']}")

    coverage = {
        "tracked_vgpr_count": len(tracked),
        "max_tracked_vgpr_index": max((int(r[1:]) for r in tracked), default=-1),
        "entry_node_count": entry_node_count,
        "cfg_phi_node_count": phi_count,
        "unresolved_control_entry_block_count": orphan_count,
        "unresolved_control_entry_vgpr_node_count": unresolved_nodes,
        "non_vgpr_source_leaf_count": scalar_leaf_count,
        **dict(sorted(counts.items())),
        "opcode_write_instruction_counts": dict(sorted(opcode_write_counts.items())),
        "opcode_write_entry_counts": dict(sorted(opcode_write_entry_counts.items())),
        "shader_expression_semantic_promotions": 0,
    }

    return {
        "schema": OUTPUT_SCHEMA,
        "status": OUTPUT_STATUS if not violations else "D1_GCN_VGPR_LANE_SSA_WITH_VIOLATIONS",
        "shader": v2.get("shader"),
        "parse_accounting": copy.deepcopy(v2["parse_accounting"]),
        "instruction_count": len(ins),
        "basic_block_count": len(blocks),
        "concrete_cfg_edge_count": sum(len(b["successors"]) for b in blocks),
        "tracked_vgprs": tracked,
        "node_count": len(g.nodes),
        "coverage": coverage,
        "instructions": rows,
        "blocks": [
            {
                "id": b["id"],
                "start_instruction": b["start_instruction"],
                "end_instruction": b["end_instruction"],
                "predecessors": b["predecessors"],
                "successors": b["successors"],
                "indirect_successor": b["indirect_successor"],
                "vgpr_entry": entry[b["id"]],
                "vgpr_exit": block_exit[b["id"]],
            }
            for b in blocks
        ],
        "nodes": g.nodes,
        "violations": violations,
        "semantic_boundary": {
            "exec_mask_symbolic_dataflow": "GLOBAL_EXACT_PREREQUISITE",
            "vgpr_lane_mutation_machine_semantics": "SOURCE_CLOSED",
            "physical_vgpr_cfg_ssa": "EXACT",
            "inactive_lane_preservation": "EXACT",
            "v_writelane_exec_exception": "EXACT",
            "v_movrels_dynamic_source_identity": "EXACT_OPAQUE_VALUE_BOUNDARY",
            "ordinary_sgpr_value_ssa": "NOT_YET_LINKED",
            "opcode_result_value_semantics": "WITHHELD",
            "shader_expression_semantics": "WITHHELD",
            "shader_expression_semantic_promotions": 0,
        },
        "policy": (
            "Physical VGPR state is represented as path-aware per-register lane SSA. Ordinary vector destinations merge "
            "an opaque instruction-result component under exact EXEC-in, preserving inactive lanes; V_WRITELANE_B32 "
            "preserves every non-selected lane while ignoring EXEC. Dynamic V_MOVRELS source identity and all scalar/value "
            "semantics remain explicit boundaries. No shader expression or material meaning is inferred."
        ),
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
        "shader": out["shader"],
        "instruction_count": out["instruction_count"],
        "basic_block_count": out["basic_block_count"],
        "node_count": out["node_count"],
        "coverage": out["coverage"],
        "violation_count": len(out["violations"]),
    }, indent=2, sort_keys=True))
    for v in out["violations"][:100]:
        print("VIOLATION", v)
    return 0 if not out["violations"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
