#!/usr/bin/env python3
"""Promote CFG-aware GCN persistent export-kill contracts.

Version 1 proved the image-sample -> threshold -> compare -> persistent-mask update
chain, but followed EXEC linearly after the mask update. This v2 pass additionally
requires source-proven SCC/branch semantics and the exact CFG successors, so exports
are described per path. In particular, a zero-mask branch that bypasses an EXEC-mask
application cannot be silently described as though every later export used that mask.

The pass remains intentionally narrow and destination-neutral. It proves native
control/dataflow only; render-target meaning and visual material intent are withheld.
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ir", type=Path, required=True)
    ap.add_argument("--stage", type=Path, required=True)
    ap.add_argument("--control-semantics", type=Path, required=True)
    ap.add_argument("--cfg-semantics", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    ir = json.load(open(a.ir))
    sd = json.load(open(a.stage))
    cs = json.load(open(a.control_semantics))
    xs = json.load(open(a.cfg_semantics))
    violations = []
    contracts = []

    try:
        assert ir["status"] == "D1_GCN_STRUCTURAL_IR_COMPLETE"
        assert int(ir.get("schema_version", 0)) >= 2
        assert sd["status"] == "D1_CORPUS_MATERIAL_STAGE_EXACT" and len(sd["materials"]) == 1
        assert cs["status"] == "D1_GCN_CONTROL_SEMANTICS_SOURCE_PROVEN" and not cs["violations"]
        assert xs["status"] == "D1_GCN_EXPORT_KILL_CFG_SEMANTICS_SOURCE_PROVEN" and not xs["violations"]

        csem = cs["semantics"]
        xsem = xs["semantics"]
        assert csem["s_andn2_b64"]["equation"] == "D = S0 & ~S1"
        assert csem["s_andn2_b64"]["scc"] == "D != 0"
        assert csem["s_and_b64"]["equation"] == "D = S0 & S1"
        assert csem["s_cbranch_scc0"]["equation"] == "branch iff SCC == 0"
        assert csem["v_subrev_f32"]["equation"] == "D = S1 - S0"
        assert xsem["v_cmp_gt_f32"]["equation"] == "VCC[lane] = (S0 > S1) for active lanes"
        assert xsem["s_mov_b64"]["equation"] == "D = S0"
        assert xsem["s_wqm_b64"]["equation"] == "D = wholeQuadMode(S0)"

        stage = sd["materials"][0]
        assert stage["stage"]["pixel_shader"] == ir["shader"]
        cb = flatten_cb(stage)
        ins = ir["instructions"]
        labels = {lab: x["index"] for x in ins for lab in x.get("labels", [])}

        inits = {}
        for x in ins:
            if (
                x["opcode"] == "s_mov_b64"
                and len(x["operands"]) >= 2
                and x["operands"][1] == "exec"
                and REGPAIR_RE.match(x["operands"][0])
            ):
                inits[x["operands"][0]] = x["index"]

        for k in ins:
            if k["opcode"] != "s_andn2_b64" or len(k["operands"]) < 3:
                continue
            mask = k["operands"][0]
            if (
                mask not in inits
                or k["operands"][1] != mask
                or k["operands"][2] not in ("vcc", "vcc_lo", "vcc_hi")
            ):
                continue

            b = block_for(ir, k["index"])
            lo = b["start_instruction"]

            cmpi = prev_def(ir, "vcc", k["index"], lo)
            assert (
                cmpi
                and cmpi["opcode"] == "v_cmp_gt_f32"
                and len(cmpi["operands"]) == 3
                and cmpi["operands"][0] == "vcc"
                and cmpi["operands"][1] == "0"
            ), cmpi
            valreg = cmpi["operands"][2]
            assert valreg.startswith("v")

            sub = prev_def(ir, valreg, cmpi["index"], lo)
            assert (
                sub
                and sub["opcode"] == "v_subrev_f32"
                and len(sub["operands"]) == 3
                and sub["operands"][0] == valreg
            ), sub
            threshold_reg = sub["operands"][1]
            sample_reg = sub["operands"][2]
            assert sample_reg == valreg and threshold_reg.startswith("s")

            sample = prev_def(ir, sample_reg, sub["index"], lo)
            assert sample and "image" in sample, sample
            tex = sample["image"]["textures"]
            assert len(tex) == 1, tex

            load = prev_def(ir, threshold_reg, sub["index"], lo)
            assert load and load["opcode"] == "s_buffer_load_dword", load
            assert load["operands"][0] == threshold_reg and len(load["operands"]) >= 3
            off = int(load["operands"][2], 0)
            assert 0 <= off < len(cb), (off, len(cb))
            threshold = cb[off]

            branch_idx = k["index"] + 1
            assert branch_idx < len(ins)
            branch = ins[branch_idx]
            assert branch["opcode"] == "s_cbranch_scc0", branch
            assert "scc" in branch.get("uses", []), branch
            assert branch["branch_target_label"] in labels, branch
            assert b["end_instruction"] == branch_idx, (b, branch)

            target_idx = labels[branch["branch_target_label"]]
            fallthrough_idx = branch_idx + 1
            succ_starts = {
                ir["basic_blocks"][bid]["start_instruction"]
                for bid in b["successors"]
            }
            assert succ_starts == {target_idx, fallthrough_idx}, (
                succ_starts,
                target_idx,
                fallthrough_idx,
            )
            assert target_idx > fallthrough_idx

            pre_exec = prev_def(ir, "exec", branch_idx, 0)
            assert (
                pre_exec
                and pre_exec["opcode"] == "s_mov_b64"
                and pre_exec["operands"][0] == "exec"
            ), pre_exec

            applyi = ins[fallthrough_idx]
            assert applyi["opcode"] == "s_and_b64"
            assert applyi["operands"] == ["exec", "exec", mask], applyi
            wqm = ins[fallthrough_idx + 1]
            assert wqm["opcode"] == "s_wqm_b64"
            assert wqm["operands"] == ["exec", "exec"], wqm

            between_exec_writes = [
                x["index"]
                for x in ins[wqm["index"] + 1 : target_idx]
                if "exec" in x.get("defs", [])
            ]
            assert not between_exec_writes, between_exec_writes

            mrt1 = None
            for x in ins[target_idx:]:
                if "exec" in x.get("defs", []):
                    break
                if (
                    x["opcode"] == "exp"
                    and x["operands"]
                    and x["operands"][0].startswith("mrt")
                ):
                    mrt1 = x
                    break
            assert mrt1 and mrt1["operands"][0] == "mrt1", mrt1

            restore = None
            mrt0 = None
            for x in ins[mrt1["index"] + 1 :]:
                if (
                    restore is None
                    and x["opcode"] == "s_mov_b64"
                    and x["operands"] == ["exec", mask]
                ):
                    restore = x
                if (
                    x["opcode"] == "exp"
                    and x["operands"]
                    and x["operands"][0] == "mrt0"
                ):
                    mrt0 = x
                    break
            assert restore and mrt0 and restore["index"] < mrt0["index"]
            assert not [
                x["index"]
                for x in ins[restore["index"] + 1 : mrt0["index"]]
                if "exec" in x.get("defs", [])
            ]

            contracts.append(
                {
                    "mask_register": mask,
                    "mask_initialized_instruction": inits[mask],
                    "predicate": {
                        "sample_instruction": sample["index"],
                        "texture_indices": tex,
                        "dmask_channels": sample["image"].get("dmask_channels"),
                        "threshold_load_instruction": load["index"],
                        "constant_scalar_index": off,
                        "threshold": threshold,
                        "difference_instruction": sub["index"],
                        "compare_instruction": cmpi["index"],
                        "difference": "threshold - sample",
                        "compare": "0 > (threshold - sample)",
                        "equivalent": "sample > threshold",
                    },
                    "kill_instruction": k["index"],
                    "mask_update": "persistent_export_mask &= ~predicate",
                    "branch": {
                        "instruction": branch_idx,
                        "condition": "updated_persistent_export_mask == 0",
                        "source_condition": (
                            "SCC == 0 after s_andn2_b64; "
                            "SCC = (updated mask != 0)"
                        ),
                        "target_label": branch["branch_target_label"],
                        "target_instruction": target_idx,
                        "fallthrough_instruction": fallthrough_idx,
                        "bypassed_instruction_range": [
                            fallthrough_idx,
                            target_idx - 1,
                        ],
                        "prebranch_exec_writer_instruction": pre_exec["index"],
                        "prebranch_exec_writer": pre_exec["assembly"],
                    },
                    "mrt1_paths": [
                        {
                            "path": "updated_mask_nonzero_fallthrough",
                            "mask_apply_instruction": applyi["index"],
                            "wqm_instruction": wqm["index"],
                            "export_instruction": mrt1["index"],
                            "exec_relation": "WQM_OF_EXEC_INTERSECT_PERSISTENT_MASK",
                        },
                        {
                            "path": "updated_mask_zero_branch",
                            "branch_instruction": branch_idx,
                            "export_instruction": mrt1["index"],
                            "exec_relation": "PREBRANCH_EXEC_PRESERVED",
                            "prebranch_exec_writer_instruction": pre_exec["index"],
                            "visual_or_buffer_semantics": "WITHHELD",
                        },
                    ],
                    "mrt0": {
                        "export_instruction": mrt0["index"],
                        "mask_restore_instruction": restore["index"],
                        "exec_relation": "DIRECT_PERSISTENT_MASK_ON_ALL_CFG_PATHS",
                    },
                    "discard_when": "sample > threshold",
                    "survive_when": "sample <= threshold",
                    "semantic_boundary": {
                        "mrt1_zero_mask_export_meaning": "WITHHELD",
                        "mrt1_visual_role": "WITHHELD",
                        "mrt0_visual_role": "WITHHELD",
                    },
                }
            )

        assert contracts, "no CFG-aware persistent export-kill contract found"
    except Exception as exc:
        violations.append(repr(exc))

    out = {
        "schema_version": 2,
        "status": (
            "D1_GCN_EXPORT_KILL_CFG_CONTRACT_COMPLETE"
            if contracts and not violations
            else "D1_GCN_EXPORT_KILL_CFG_CONTRACT_PARTIAL"
        ),
        "shader": ir.get("shader"),
        "material": (
            sd.get("materials", [{}])[0].get("material")
            if sd.get("materials")
            else None
        ),
        "contracts": contracts,
        "violations": violations,
        "source_semantics": {
            "control_status": cs.get("status"),
            "cfg_supplement_status": xs.get("status"),
        },
        "policy": (
            "Promotion requires an exact image/constant/predicate chain, "
            "source-proven SCC and branch semantics, exact CFG successors, and "
            "path-specific EXEC provenance through MRT exports. Render-target "
            "meaning and visual intent are withheld."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
