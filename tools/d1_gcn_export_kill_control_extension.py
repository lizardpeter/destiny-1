#!/usr/bin/env python3
"""Extend an exact persistent-export-kill contract with omitted value/branch links.

The v1 export-kill detector proves the canonical sample -> threshold -> compare ->
persistent-mask update -> MRT relationship, but intentionally serializes only the
major endpoints. This pass closes two renderer-useful links without using adjacency
as evidence:

* the exact v_subrev_f32 value instruction that constructs threshold - sample;
* an SCC branch whose unique reaching SCC writer in the same CFG basic block is the
  source-proven persistent-mask update, including independent SIMM16 target decoding.

No shader intent, texture-name semantics, or visual appearance is inferred.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def block_for(ir, instruction):
    hits = [b for b in ir["basic_blocks"] if int(b["start_instruction"]) <= instruction <= int(b["end_instruction"])]
    if len(hits) != 1:
        raise ValueError(f"instruction {instruction}: expected one basic block, got {len(hits)}")
    return hits[0]


def prev_def(ir, reg, before, lo):
    for i in range(before - 1, lo - 1, -1):
        if reg in ir["instructions"][i].get("defs", []):
            return ir["instructions"][i]
    return None


def source_scc_writer(ins, semantics):
    # Structural IR already marks explicit SCC destinations such as s_cmp*. The
    # source-semantics contract supplements scalar ALU opcodes whose implicit SCC
    # destination is not represented by CLRX operand syntax.
    if "scc" in ins.get("defs", []):
        return True
    q = semantics.get(ins["opcode"])
    return isinstance(q, dict) and "scc" in q


def signext16(x):
    x &= 0xFFFF
    return x - 0x10000 if x & 0x8000 else x


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ir", type=Path, required=True)
    ap.add_argument("--kill-mask", type=Path, required=True)
    ap.add_argument("--control-semantics", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    ir = json.load(open(a.ir))
    km = json.load(open(a.kill_mask))
    cs = json.load(open(a.control_semantics))
    violations = []
    extensions = []

    try:
        assert ir["status"] == "D1_GCN_STRUCTURAL_IR_COMPLETE" and int(ir.get("schema_version", 0)) >= 2
        assert km["status"] == "D1_GCN_EXPORT_KILL_MASK_CONTRACT_COMPLETE" and not km.get("violations")
        assert cs["status"] == "D1_GCN_CONTROL_SEMANTICS_SOURCE_PROVEN" and not cs.get("violations")
        assert str(ir["shader"]).upper() == str(km["shader"]).upper()
        sem = cs["semantics"]
        for required in ("v_subrev_f32", "s_andn2_b64", "s_cbranch_scc0"):
            assert required in sem, required
        assert sem["v_subrev_f32"]["equation"] == "D = S1 - S0"
        assert sem["s_andn2_b64"]["equation"] == "D = S0 & ~S1"
        assert sem["s_andn2_b64"]["scc"] == "D != 0"
        assert sem["s_cbranch_scc0"]["equation"] == "branch iff SCC == 0"

        ins = ir["instructions"]
        label_to_instruction = {
            label: x["index"]
            for x in ins
            for label in x.get("labels", [])
        }

        for q in km["contracts"]:
            cmp_i = int(q["predicate"]["compare_instruction"])
            kill_i = int(q["kill_instruction"])
            cmp = ins[cmp_i]
            kill = ins[kill_i]
            b = block_for(ir, kill_i)
            lo, hi = int(b["start_instruction"]), int(b["end_instruction"])
            assert lo <= cmp_i < kill_i <= hi

            # Reconstruct the exact predicate-value instruction using register
            # def-use, exactly as the v1 kill detector did, and serialize it.
            assert cmp["opcode"] == "v_cmp_gt_f32" and len(cmp["operands"]) == 3
            assert cmp["operands"][0] == "vcc" and cmp["operands"][1] == "0"
            value_reg = cmp["operands"][2]
            sub = prev_def(ir, value_reg, cmp_i, lo)
            assert sub and sub["opcode"] == "v_subrev_f32", sub
            assert len(sub["operands"]) == 3 and sub["operands"][0] == value_reg
            threshold_reg, sample_reg = sub["operands"][1], sub["operands"][2]
            assert sample_reg == value_reg
            threshold_load_i = int(q["predicate"]["threshold_load_instruction"])
            sample_i = int(q["predicate"]["sample_instruction"])
            threshold_load = ins[threshold_load_i]
            sample = ins[sample_i]
            assert threshold_reg in threshold_load.get("defs", []), (threshold_reg, threshold_load)
            assert sample_reg in sample.get("defs", []), (sample_reg, sample)
            assert sample_i < sub["index"] < cmp_i < kill_i

            # Find an SCC-consuming branch in the same CFG block. Its reaching SCC
            # writer is derived from structural SCC defs plus only source-proven
            # implicit SCC writers. No instruction-order adjacency assumption is used.
            branches = [
                x for x in ins[kill_i + 1:hi + 1]
                if x["opcode"].startswith("s_cbranch_scc") and "scc" in x.get("uses", [])
            ]
            assert len(branches) == 1, branches
            br = branches[0]
            writers = []
            for i in range(br["index"] - 1, lo - 1, -1):
                if source_scc_writer(ins[i], sem):
                    writers.append(ins[i])
                    break
            assert len(writers) == 1
            writer = writers[0]
            assert writer["index"] == kill_i, (writer, kill)
            assert writer["opcode"] == "s_andn2_b64"
            assert br["opcode"] == "s_cbranch_scc0"

            # Prove the branch target twice: CLRX structural label/CFG and the
            # instruction's encoded SOPP SIMM16 using the source-proven PC equation.
            target_label = br.get("branch_target_label")
            assert target_label in label_to_instruction, (target_label, label_to_instruction)
            target_i = int(label_to_instruction[target_label])
            target = ins[target_i]
            word = int(br["encoding_hex"], 16)
            simm16_raw = word & 0xFFFF
            simm16 = signext16(simm16_raw)
            encoded_target_address = int(br["address"]) + 4 + simm16 * 4
            assert encoded_target_address == int(target["address"]), (
                hex(encoded_target_address), target["address_hex"])

            target_block = block_for(ir, target_i)
            fallthrough_i = br["index"] + 1
            fallthrough_block = block_for(ir, fallthrough_i)
            successors = set(int(x) for x in b.get("successors", []))
            assert int(target_block["id"]) in successors
            assert int(fallthrough_block["id"]) in successors

            extensions.append({
                "mask_register": q["mask_register"],
                "kill_instruction": kill_i,
                "predicate_value": {
                    "instruction": int(sub["index"]),
                    "opcode": sub["opcode"],
                    "destination": value_reg,
                    "threshold_register": threshold_reg,
                    "sample_register": sample_reg,
                    "equation": "threshold - sample",
                    "source_semantics": sem["v_subrev_f32"],
                    "sample_instruction": sample_i,
                    "threshold_load_instruction": threshold_load_i,
                    "threshold": q["predicate"]["threshold"],
                },
                "scc_branch": {
                    "instruction": int(br["index"]),
                    "opcode": br["opcode"],
                    "scc_writer_instruction": int(writer["index"]),
                    "scc_writer_opcode": writer["opcode"],
                    "scc_writer_equation": sem["s_andn2_b64"],
                    "branch_equation": sem["s_cbranch_scc0"],
                    "exact_condition": "updated_persistent_export_mask == 0",
                    "target_label": target_label,
                    "target_instruction": target_i,
                    "target_address_hex": target["address_hex"],
                    "fallthrough_instruction": fallthrough_i,
                    "encoded_word_hex": br["encoding_hex"],
                    "encoded_simm16_raw": simm16_raw,
                    "encoded_simm16_signed": simm16,
                    "encoded_target_address_hex": f"{encoded_target_address:012X}",
                    "cfg_block": int(b["id"]),
                    "target_block": int(target_block["id"]),
                    "fallthrough_block": int(fallthrough_block["id"]),
                },
                "proof": (
                    "Predicate-value provenance is reconstructed by register def-use inside the exact CFG block. "
                    "The SCC branch has a unique reaching SCC writer under the source-proven SCC-writer vocabulary; "
                    "its target independently agrees between structural CFG/label resolution and encoded SOPP SIMM16 arithmetic."
                ),
            })
        assert extensions, "no persistent-export-kill extensions found"
    except Exception as exc:
        violations.append(repr(exc))

    out = {
        "schema_version": 1,
        "status": (
            "D1_GCN_EXPORT_KILL_CONTROL_EXTENSION_EXACT"
            if extensions and not violations
            else "D1_GCN_EXPORT_KILL_CONTROL_EXTENSION_PARTIAL"
        ),
        "shader": ir.get("shader"),
        "material": km.get("material"),
        "extensions": extensions,
        "violations": violations,
        "semantic_boundary": {
            "predicate_value_instruction": "EXACT",
            "scc_reaching_definition": "EXACT_WITH_SOURCE_PROVEN_WRITER_VOCABULARY",
            "branch_target": "EXACT_CFG_AND_ENCODED_SIMM16_AGREE",
            "visual_role": "WITHHELD",
        },
        "policy": (
            "Only links already structurally connected to an exact persistent-export-kill contract are extended. "
            "SCC writers must be explicit structural defs or carry source-proven SCC semantics; branch targets must "
            "agree between CFG/label resolution and native SIMM16 decoding."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
