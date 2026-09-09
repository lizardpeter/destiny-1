#!/usr/bin/env python3
"""Lift exact D1 GCN Structural IR v2 into source-backed architectural-effect IR v3.

V3 is an additive adapter. It never reparses native text and never changes v2's
address/encoding/order/accounting facts. It adds source-closed architectural defs,
uses and effect metadata from d1_gcn_arch_effects_v1, plus a CFG view that recognizes
source-closed indirect PC swaps without guessing their runtime target.
"""
from __future__ import annotations

import argparse
import copy
import json
from collections import Counter
from pathlib import Path

import d1_gcn_arch_effects_v1 as arch

INPUT_STATUS = "D1_GCN_STRUCTURAL_IR_COMPLETE"
INPUT_PARSE_STATUS = "D1_GCN_STRUCTURAL_PARSE_ACCOUNTING_EXACT"
OUTPUT_SCHEMA = "d1_gcn_effect_ir/v3"
OUTPUT_STATUS = "D1_GCN_EFFECT_IR_V3_ARCHITECTURAL_EFFECTS_APPLIED"
COND_PREFIX = "s_cbranch_"
UNCOND = {"s_branch"}
TERMINAL = {"s_endpgm"}
IMMUTABLE_INST_FIELDS = (
    "index", "address", "address_hex", "encoding_words", "encoding_hex", "byte_size",
    "source_line", "labels", "opcode", "operands", "defs", "uses", "branch_target_label", "assembly",
)


def _closed_effect(inst: dict) -> dict | None:
    return arch.REGISTRY.get(str(inst.get("opcode", "")))


def _upgrade_instruction(inst: dict) -> dict:
    out = copy.deepcopy(inst)
    ann = arch.annotate_instruction(inst)
    out["architectural_status"] = ann["architectural_status"]
    out["shader_expression_status"] = ann["shader_expression_status"]
    out["architectural_defs"] = ann["architectural_defs"]
    out["architectural_uses"] = ann["architectural_uses"]
    if ann["architectural_status"] == "SOURCE_CLOSED":
        e = ann["effects"]
        out["architectural_effects"] = {
            k: copy.deepcopy(e[k]) for k in (
                "family", "execution_scope", "exec_behavior", "destination_write_scope",
                "memory_effect", "control_flow", "reads_old_destination", "operation", "source", "notes",
            )
        }
    return out


def _is_indirect_transfer(inst: dict) -> bool:
    e = _closed_effect(inst)
    return bool(e and e.get("control_flow") == "INDIRECT_PC_SWAP")


def _blocks_v3(ins: list[dict]) -> tuple[list[dict], list[dict]]:
    if not ins:
        return [], []
    label_to_index = {label: x["index"] for x in ins for label in x.get("labels") or []}
    starts = {0}
    for x in ins:
        op = x["opcode"]
        if x.get("labels"):
            starts.add(x["index"])
        is_terminator = op in UNCOND or op.startswith(COND_PREFIX) or op in TERMINAL or _is_indirect_transfer(x)
        if is_terminator and x["index"] + 1 < len(ins):
            starts.add(x["index"] + 1)
        target = x.get("branch_target_label")
        if target in label_to_index:
            starts.add(label_to_index[target])
    ss = sorted(starts)
    bb = []
    i2b = {}
    for bi, s in enumerate(ss):
        e = ss[bi + 1] - 1 if bi + 1 < len(ss) else len(ins) - 1
        b = {
            "id": bi,
            "start_instruction": s,
            "end_instruction": e,
            "start_address": ins[s]["address_hex"],
            "labels": list(ins[s].get("labels") or []),
            "successors": [],
            "predecessors": [],
            "indirect_successor": None,
        }
        bb.append(b)
        for i in range(s, e + 1):
            i2b[i] = bi
    for b in bb:
        x = ins[b["end_instruction"]]
        op = x["opcode"]
        succ = []
        if _is_indirect_transfer(x):
            operands = x.get("operands") or []
            b["indirect_successor"] = {
                "kind": "INDIRECT_PC_SWAP",
                "instruction": x["index"],
                "address": x["address_hex"],
                "source_operand": operands[1] if len(operands) >= 2 else None,
                "concrete_target": None,
                "fallthrough_edge_emitted": False,
            }
        else:
            target = x.get("branch_target_label")
            if target and target in label_to_index:
                succ.append(i2b[label_to_index[target]])
            if op.startswith(COND_PREFIX):
                if x["index"] + 1 < len(ins):
                    succ.append(i2b[x["index"] + 1])
            elif op not in UNCOND and op not in TERMINAL:
                if x["index"] + 1 < len(ins):
                    succ.append(i2b[x["index"] + 1])
        b["successors"] = list(dict.fromkeys(succ))
    for b in bb:
        for s in b["successors"]:
            bb[s]["predecessors"].append(b["id"])
    back = []
    for b in bb:
        for s in b["successors"]:
            if bb[s]["start_instruction"] <= b["start_instruction"]:
                back.append({"from_block": b["id"], "to_block": s})
    return bb, back


def assert_v2_preserved(v2: dict, v3: dict) -> None:
    if v2.get("status") != INPUT_STATUS:
        raise ValueError(f"input status is not exact structural IR: {v2.get('status')!r}")
    pa = v2.get("parse_accounting") or {}
    if pa.get("status") != INPUT_PARSE_STATUS:
        raise ValueError(f"input parse accounting is not exact: {pa.get('status')!r}")
    if v3["parse_accounting"] != v2["parse_accounting"]:
        raise ValueError("parse_accounting changed during v3 lift")
    if len(v2.get("instructions") or []) != len(v3.get("instructions") or []):
        raise ValueError("instruction count changed during v3 lift")
    for old, new in zip(v2["instructions"], v3["instructions"]):
        for k in IMMUTABLE_INST_FIELDS:
            if new.get(k) != old.get(k):
                raise ValueError(f"native structural field changed at instruction {old.get('index')}: {k}")


def upgrade(v2: dict) -> dict:
    if v2.get("status") != INPUT_STATUS:
        raise ValueError(f"input status is not {INPUT_STATUS}: {v2.get('status')!r}")
    if (v2.get("parse_accounting") or {}).get("status") != INPUT_PARSE_STATUS:
        raise ValueError("input lacks exact structural parse accounting")
    instructions = [_upgrade_instruction(x) for x in (v2.get("instructions") or [])]
    blocks, back_edges = _blocks_v3(instructions)
    source_closed = [x for x in instructions if x["architectural_status"] == "SOURCE_CLOSED"]
    defs_differ = [x for x in source_closed if x["architectural_defs"] != x.get("defs", [])]
    uses_differ = [x for x in source_closed if x["architectural_uses"] != x.get("uses", [])]
    indirect = [x for x in source_closed if x.get("architectural_effects", {}).get("control_flow") == "INDIRECT_PC_SWAP"]
    partial = [x for x in source_closed if x.get("architectural_effects", {}).get("destination_write_scope") != "FULL_DESTINATION"]
    old_blocks = v2.get("basic_blocks") or []
    old_edges = int(v2.get("cfg_edge_count", sum(len(x.get("successors") or []) for x in old_blocks)))
    concrete_edges_v3 = sum(len(x["successors"]) for x in blocks)
    out = {
        "schema": OUTPUT_SCHEMA,
        "status": OUTPUT_STATUS,
        "shader": v2.get("shader"),
        "source_structural_schema_version": v2.get("schema_version"),
        "source_structural_status": v2.get("status"),
        "parse_accounting": copy.deepcopy(v2["parse_accounting"]),
        "instruction_count": len(instructions),
        "source_closed_instruction_count": len(source_closed),
        "source_closed_opcode_counts": dict(sorted(Counter(x["opcode"] for x in source_closed).items())),
        "architectural_defs_differ_instruction_count": len(defs_differ),
        "architectural_uses_differ_instruction_count": len(uses_differ),
        "partial_destination_write_instruction_count": len(partial),
        "indirect_pc_swap_instruction_count": len(indirect),
        "basic_block_count": len(blocks),
        "cfg_edge_count": concrete_edges_v3,
        "cfg_delta_vs_structural_v2": {
            "basic_block_count_v2": len(old_blocks),
            "basic_block_count_v3": len(blocks),
            "basic_block_delta": len(blocks) - len(old_blocks),
            "concrete_cfg_edge_count_v2": old_edges,
            "concrete_cfg_edge_count_v3": concrete_edges_v3,
            "concrete_cfg_edge_delta": concrete_edges_v3 - old_edges,
            "indirect_pc_swap_site_count": len(indirect),
            "indirect_targets_resolved": 0,
        },
        "control_flow": {
            "back_edges": back_edges,
            "indirect_pc_swap_sites": [
                {"instruction": x["index"], "address": x["address_hex"], "operands": x.get("operands") or []}
                for x in indirect
            ],
        },
        "instructions": instructions,
        "basic_blocks": blocks,
        "semantic_boundary": {
            "native_parse_accounting": INPUT_PARSE_STATUS,
            "architectural_effects": "SOURCE_CLOSED_TRANCHE_APPLIED",
            "shader_expression_semantics": "UNPROVEN",
            "exec_mask_symbolic_dataflow": "NOT_YET_PROMOTED",
            "indirect_pc_target_resolution": "WITHHELD",
            "shader_expression_semantic_promotions": 0,
        },
        "policy": (
            "V3 is additive over exact structural v2. Native instruction identity/order/address/encoding and parse "
            "accounting are immutable. Architectural effects are admitted only from the source-closed GFX7 registry. "
            "Indirect PC swaps terminate the local concrete block and expose an unresolved indirect successor; no "
            "target or fallthrough is invented. High-level shader expression semantics remain withheld."
        ),
    }
    assert_v2_preserved(v2, out)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--structural-ir", required=True, type=Path)
    ap.add_argument("-o", "--output", required=True, type=Path)
    a = ap.parse_args()
    v2 = json.loads(a.structural_ir.read_text())
    out = upgrade(v2)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": out["status"], "shader": out["shader"], "instruction_count": out["instruction_count"],
        "source_closed_instruction_count": out["source_closed_instruction_count"],
        "cfg_delta_vs_structural_v2": out["cfg_delta_vs_structural_v2"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
