#!/usr/bin/env python3
"""Promote path-sensitive persistent-export kill control from D1 GCN structural IR.

V2 fixes a weakness in the original linear scan: a branch immediately after a
persistent mask update may bypass the first EXEC-mask application. Export relations
are therefore derived separately for the nonempty fallthrough and the empty-mask
branch path. Native EXP.vm is preserved and no claim is made that EXEC affects an
export when vm is false.
"""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

REGPAIR_RE = re.compile(r"^s\[(\d+):(\d+)\]$")


def block_for(ir, i):
    for b in ir["basic_blocks"]:
        if b["start_instruction"] <= i <= b["end_instruction"]:
            return b
    raise KeyError(i)


def prev_def(ir, reg, before, lo=0):
    for i in range(before - 1, lo - 1, -1):
        if reg in ir["instructions"][i].get("defs", []):
            return ir["instructions"][i]
    return None


def flatten_cb(stage):
    out = []
    for r in stage["stage"]["ps_cbuffers"]["items"]:
        out.extend(float(x) for x in r["value"])
    return out


def exp_vm(x):
    return bool(re.search(r"(?:^|\s)vm(?:\s|$)", x.get("assembly", "")))


def path_exec_relation(ins, start, end, mask):
    """Classify the last exact EXEC provenance before export on one linear path."""
    relation = "PRE_PATH_EXEC_UNCHANGED"
    write_instruction = None
    mask_apply_instruction = None
    for x in ins[start:end]:
        op = x["opcode"]
        a = x["operands"]
        if op == "s_and_b64" and len(a) >= 3 and a[0] == "exec" and a[1] == "exec" and a[2] == mask:
            relation = "DIRECT_AND_MASK"
            write_instruction = x["index"]
            mask_apply_instruction = x["index"]
        elif op == "s_mov_b64" and len(a) >= 2 and a[0] == "exec" and a[1] == mask:
            relation = "DIRECT_MOV_MASK"
            write_instruction = x["index"]
            mask_apply_instruction = x["index"]
        elif op == "s_wqm_b64" and len(a) >= 2 and a[0] == "exec" and a[1] == "exec":
            if mask_apply_instruction is not None:
                relation = "WQM_OF_MASKED_EXEC"
            else:
                relation = "WQM_OF_PREVIOUS_EXEC"
            write_instruction = x["index"]
        elif "exec" in x.get("defs", []):
            relation = "OTHER_EXEC_WRITE"
            write_instruction = x["index"]
            mask_apply_instruction = None
    return {
        "exec_relation": relation,
        "exec_write_instruction": write_instruction,
        "originating_mask_apply_instruction": mask_apply_instruction,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ir", type=Path, required=True)
    ap.add_argument("--stage", type=Path, required=True)
    ap.add_argument("--control-semantics", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    ir = json.load(open(a.ir))
    sd = json.load(open(a.stage))
    cs = json.load(open(a.control_semantics))
    violations = []
    contracts = []
    try:
        assert ir["status"] == "D1_GCN_STRUCTURAL_IR_COMPLETE"
        assert int(ir.get("schema_version", 0)) >= 3
        assert sd["status"] == "D1_CORPUS_MATERIAL_STAGE_EXACT" and len(sd["materials"]) == 1
        assert cs["status"] == "D1_GCN_CONTROL_SEMANTICS_SOURCE_PROVEN" and not cs["violations"]
        sem = cs["semantics"]
        assert sem["s_andn2_b64"]["equation"] == "D = S0 & ~S1"
        assert sem["s_andn2_b64"]["scc"] == "D != 0"
        assert sem["s_cbranch_scc0"]["equation"] == "branch iff SCC == 0"
        assert sem["v_subrev_f32"]["equation"] == "D = S1 - S0"

        stage = sd["materials"][0]
        assert stage["stage"]["pixel_shader"] == ir["shader"]
        cb = flatten_cb(stage)
        ins = ir["instructions"]
        label_to_index = {lab: x["index"] for x in ins for lab in x.get("labels", [])}

        inits = {}
        for x in ins:
            if x["opcode"] == "s_mov_b64" and len(x["operands"]) >= 2 and x["operands"][1] == "exec" and REGPAIR_RE.match(x["operands"][0]):
                inits[x["operands"][0]] = x["index"]

        for k in ins:
            if k["opcode"] != "s_andn2_b64" or len(k["operands"]) < 3:
                continue
            mask = k["operands"][0]
            if mask not in inits or k["operands"][1] != mask or k["operands"][2] not in ("vcc", "vcc_lo", "vcc_hi"):
                continue
            assert "scc" in k.get("defs", []), k

            # Canonical empty-mask early-out branch must consume the SCC produced by
            # this exact mask update. This is source/def-use proof, not adjacency alone.
            assert k["index"] + 1 < len(ins)
            branch = ins[k["index"] + 1]
            assert branch["opcode"] == "s_cbranch_scc0" and "scc" in branch.get("uses", []), branch
            b = block_for(ir, k["index"])
            scc_def = prev_def(ir, "scc", branch["index"], b["start_instruction"])
            assert scc_def and scc_def["index"] == k["index"], (scc_def, k)
            target_label = branch.get("branch_target_label")
            assert target_label in label_to_index, branch
            target = label_to_index[target_label]
            fallthrough = branch["index"] + 1

            # Recover threshold/sample predicate exactly.
            cmp = prev_def(ir, "vcc", k["index"], b["start_instruction"])
            assert cmp and cmp["opcode"] == "v_cmp_gt_f32" and len(cmp["operands"]) == 3
            assert cmp["operands"][0] == "vcc" and cmp["operands"][1] == "0"
            valreg = cmp["operands"][2]
            sub = prev_def(ir, valreg, cmp["index"], b["start_instruction"])
            assert sub and sub["opcode"] == "v_subrev_f32" and sub["operands"][0] == valreg and len(sub["operands"]) == 3
            threshold_reg, sample_reg = sub["operands"][1], sub["operands"][2]
            assert sample_reg == valreg and threshold_reg.startswith("s")
            sample = prev_def(ir, sample_reg, sub["index"], b["start_instruction"])
            assert sample and "image" in sample
            tex = sample["image"]["textures"]
            assert len(tex) == 1
            load = prev_def(ir, threshold_reg, sub["index"], b["start_instruction"])
            assert load and load["opcode"] == "s_buffer_load_dword" and load["operands"][0] == threshold_reg
            off = int(load["operands"][2], 0)
            assert 0 <= off < len(cb)
            threshold = cb[off]

            # Find native MRT exports at or after the branch target and classify the
            # EXEC path independently for branch-taken and fallthrough routes.
            export_paths = []
            directly_mask_governed = []
            for x in ins[target:]:
                if x["opcode"] != "exp" or not x["operands"] or not x["operands"][0].startswith("mrt"):
                    continue
                ei = x["index"]
                nonempty = path_exec_relation(ins, fallthrough, ei, mask)
                empty = path_exec_relation(ins, target, ei, mask)
                vm = exp_vm(x)
                row = {
                    "instruction": ei,
                    "target": x["operands"][0],
                    "vm": vm,
                    "nonempty_mask_path": nonempty,
                    "empty_mask_branch_path": empty,
                }
                if vm and nonempty["exec_relation"] in ("DIRECT_AND_MASK", "DIRECT_MOV_MASK") and empty["exec_relation"] in ("DIRECT_AND_MASK", "DIRECT_MOV_MASK"):
                    row["kill_mask_binding"] = "DIRECT_VALID_MASK_ON_ALL_PATHS"
                    directly_mask_governed.append({
                        "instruction": ei,
                        "target": x["operands"][0],
                        "vm": True,
                        "binding": "DIRECT_VALID_MASK_ON_ALL_PATHS",
                    })
                elif vm:
                    row["kill_mask_binding"] = "PATH_DEPENDENT_VALID_EXEC_MASK"
                else:
                    row["kill_mask_binding"] = "VM_FALSE_EXEC_EFFECT_WITHHELD"
                export_paths.append(row)

            assert export_paths, "no MRT exports after kill branch"
            assert directly_mask_governed, "no directly valid-mask-governed MRT export"

            contracts.append({
                "mask_register": mask,
                "mask_initialized_instruction": inits[mask],
                "kill_instruction": k["index"],
                "predicate": {
                    "sample_instruction": sample["index"],
                    "texture_indices": tex,
                    "dmask_channels": sample["image"].get("dmask_channels"),
                    "threshold_load_instruction": load["index"],
                    "constant_scalar_index": off,
                    "threshold": threshold,
                    "arithmetic_instruction": sub["index"],
                    "arithmetic": "threshold - sample",
                    "compare_instruction": cmp["index"],
                    "compare": "0 > (threshold - sample)",
                    "equivalent": "sample > threshold",
                },
                "mask_update": "persistent_export_mask &= ~predicate",
                "discard_when": "sample > threshold",
                "survive_when": "sample <= threshold",
                "empty_mask_branch": {
                    "instruction": branch["index"],
                    "source_scc_instruction": k["index"],
                    "condition": "updated persistent_export_mask == 0",
                    "target_label": target_label,
                    "target_instruction": target,
                    "fallthrough_instruction": fallthrough,
                },
                "export_path_relations": export_paths,
                "directly_mask_governed_exports": directly_mask_governed,
                "proof": (
                    "The sampled scalar and exact material threshold form threshold-sample; "
                    "the compare feeds VCC, s_andn2 removes matching lanes from the persistent "
                    "mask and source-proven SCC reports whether that updated mask is nonzero. "
                    "The following SCC0 branch is therefore an exact empty-mask branch. MRT "
                    "EXEC provenance is evaluated separately on branch-taken and fallthrough "
                    "paths, and EXP.vm is preserved before claiming direct mask governance."
                ),
            })

        assert contracts, "no path-sensitive export kill contract found"
    except Exception as exc:
        violations.append(repr(exc))

    out = {
        "schema_version": 2,
        "status": "D1_GCN_EXPORT_KILL_MASK_PATH_SENSITIVE_COMPLETE" if contracts and not violations else "D1_GCN_EXPORT_KILL_MASK_PATH_SENSITIVE_PARTIAL",
        "shader": ir.get("shader"),
        "material": sd.get("materials", [{}])[0].get("material") if sd.get("materials") else None,
        "contracts": contracts,
        "violations": violations,
        "policy": (
            "Promotion requires source-proven SCC semantics, exact structural def-use, exact "
            "branch target, exact sample/cbuffer predicate provenance, and path-sensitive EXEC "
            "tracking. EXP.vm is preserved; vm=false exports are not claimed to be directly "
            "governed by the persistent kill mask."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({
        "status": out["status"],
        "contract_count": len(contracts),
        "directly_mask_governed_exports": [
            q for c in contracts for q in c.get("directly_mask_governed_exports", [])
        ],
        "violations": violations,
    }, indent=2))
    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
