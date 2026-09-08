#!/usr/bin/env python3
"""Join exact D1 GCN proof layers into one structured renderer-program IR.

This is deliberately not a decompiler-completion claim. Every native instruction is
assigned a resolution tier and may carry multiple evidence tags. Exact expression
DAGs, exact loop recurrences, exact terminal packed-MRT roots, exact EXEC/kill control,
exact input provenance, and exact exports are preserved separately. The complement is
emitted as contiguous STRUCTURAL_ONLY spans so consumers cannot silently treat an
unlifted value path as solved.
"""
from __future__ import annotations
import argparse, collections, json
from pathlib import Path


def norm(x):
    return str(x).upper().removeprefix("0X").zfill(8)


def rng(a, b):
    return set(range(int(a), int(b) + 1))


def contiguous(values):
    vals = sorted(set(values))
    if not vals:
        return []
    out = []
    a = b = vals[0]
    for x in vals[1:]:
        if x == b + 1:
            b = x
        else:
            out.append((a, b))
            a = b = x
    out.append((a, b))
    return out


def load_exprs(paths):
    out = {}
    for p in paths:
        d = json.load(open(p))
        if d.get("status") != "D1_GCN_SIMPLE_REGION_EXPRESSION_DAG_EXACT" or d.get("violations"):
            raise ValueError(f"{p}: exact simple-region expression DAG required")
        e = d["expression"]
        rid = int(e["region_id"])
        if rid in out:
            raise ValueError(f"duplicate region expression {rid}")
        out[rid] = d
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", type=Path, required=True)
    ap.add_argument("--ir", type=Path, required=True)
    ap.add_argument("--exec-regions", type=Path, required=True)
    ap.add_argument("--kill-mask", type=Path, required=True)
    ap.add_argument("--cbuffer-provenance", type=Path, required=True)
    ap.add_argument("--mimg", type=Path, required=True)
    ap.add_argument("--loop-recurrence", type=Path, required=True)
    ap.add_argument("--region-expr", type=Path, action="append", default=[])
    ap.add_argument("--terminal-mrt-expr", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    sd = json.load(open(a.stage))
    ir = json.load(open(a.ir))
    er = json.load(open(a.exec_regions))
    km = json.load(open(a.kill_mask))
    cb = json.load(open(a.cbuffer_provenance))
    mi = json.load(open(a.mimg))
    lr = json.load(open(a.loop_recurrence))
    terminal = json.load(open(a.terminal_mrt_expr)) if a.terminal_mrt_expr else None
    violations = []
    program = {}

    try:
        assert sd["status"] == "D1_CORPUS_MATERIAL_STAGE_EXACT" and len(sd["materials"]) == 1
        assert ir["status"] == "D1_GCN_STRUCTURAL_IR_COMPLETE" and int(ir.get("schema_version", 0)) >= 2
        assert er["status"] == "D1_GCN_EXEC_REGION_IR_COMPLETE" and not er["violations"]
        assert km["status"] == "D1_GCN_EXPORT_KILL_MASK_CONTRACT_COMPLETE" and not km["violations"]
        assert cb["status"] == "D1_GCN_CBUFFER_PROVENANCE_EXACT" and not cb["violations"]
        assert mi["status"] == "D1_GCN_MIMG_ADDRESS_PROVENANCE_EXACT" and not mi["violations"]
        assert lr["status"] == "D1_GCN_LOOP_RECURRENCE_EXACT" and not lr["violations"]
        exprs = load_exprs(a.region_expr)

        m = sd["materials"][0]
        st = m["stage"]
        material = norm(m["material"])
        shader = norm(st["pixel_shader"])
        assert shader == norm(ir["shader"]) == norm(er["shader"]) == norm(km["shader"]) == norm(cb["shader"]) == norm(mi["shader"]) == norm(lr["shader"])
        assert material == norm(km["material"]) == norm(cb["material"])
        for d in exprs.values():
            assert norm(d["expression"]["shader"]) == shader
        terminal_payload = None
        if terminal is not None:
            assert terminal.get("status") == "D1_GCN_TERMINAL_MRT_PACKED_EXPRESSION_EXACT" and not terminal.get("violations")
            terminal_payload = terminal["expression"]
            assert norm(terminal_payload["shader"]) == shader
            assert norm(terminal_payload["material"]) == material
            assert terminal_payload["semantic_boundary"]["compressed_export_rgba_channel_unpacking"] == "WITHHELD_NOT_SOURCE_CLOSED"

        ins = ir["instructions"]
        n = int(ir["instruction_count"])
        assert n == len(ins) and [x["index"] for x in ins] == list(range(n))

        regions = {int(r["region_id"]): r for r in er["regions"]}
        assert set(exprs).issubset(regions)
        for rid in exprs:
            assert regions[rid]["promotion"] == "EXACT_SIMPLE_LANE_MERGE"

        evidence = {i: set() for i in range(n)}
        expression_exact = set()
        recurrence_exact = set()
        control_exact = set()
        input_exact = set()
        export_exact = set()

        # Exact simple-region expression arms. Predicate and EXEC plumbing stay in
        # CONTROL_EXACT so arithmetic and control proof tiers remain distinct.
        expr_payloads = []
        for rid, d in sorted(exprs.items()):
            e = d["expression"]
            r = regions[rid]
            arm = rng(*e["then_range"]) | rng(*e["else_range"])
            expression_exact |= arm
            for i in arm:
                evidence[i].add(f"REGION_{rid}_EXPRESSION_DAG")
            ctl = {int(e["predicate"]["instruction"]), int(r["saveexec_instruction"]), int(r["restore_instruction"])}
            if r.get("complement_switch_instruction") is not None:
                ctl.add(int(r["complement_switch_instruction"]))
            control_exact |= ctl
            for i in ctl:
                evidence[i].add(f"REGION_{rid}_EXEC_CONTROL")
            expr_payloads.append({
                "region_id": rid,
                "predicate": e["predicate"],
                "then_range": e["then_range"],
                "else_range": e["else_range"],
                "node_count": e["node_count"],
                "sample_count": e["sample_count"],
                "sample_node_ids": e["sample_node_ids"],
                "lane_merge_roots": e["lane_merge_roots"],
                "promoted_factor_roots": e["promoted_factor_roots"],
                "nodes": e["nodes"],
                "source_semantics": e["source_semantics"],
            })

        # Exact loop and post-loop recurrence. If a nested simple expression DAG
        # overlaps the refinement, EXPRESSION_EXACT wins as the primary tier but
        # both evidence tags are retained.
        recurrence_payloads = []
        for q in lr["recurrences"]:
            rr = rng(q["loop_start_instruction"], q["loop_end_instruction"])
            pr = q.get("post_loop_refinement", {}).get("instruction_range")
            if pr:
                rr |= rng(*pr)
            recurrence_exact |= rr
            for i in rr:
                evidence[i].add("EXACT_LOOP_RECURRENCE")
            recurrence_payloads.append(q)

        # All canonical EXEC-region skeleton points are exact structural control,
        # even where the enclosed VGPR dataflow is not yet lifted.
        structured_regions = []
        loop_ranges = [(q["loop_start_instruction"], q["post_loop_refinement"]["instruction_range"][1]) for q in lr["recurrences"]]
        for rid, r in sorted(regions.items()):
            ctl = {int(r["saveexec_instruction"]), int(r["restore_instruction"]), int(r["predicate"]["instruction"])}
            if r.get("complement_switch_instruction") is not None:
                ctl.add(int(r["complement_switch_instruction"]))
            control_exact |= ctl
            for i in ctl:
                evidence[i].add(f"REGION_{rid}_STRUCTURED_EXEC")
            a0, b0 = int(r["saveexec_instruction"]), int(r["restore_instruction"])
            if rid in exprs:
                resolution = "EXPRESSION_EXACT"
                reason = "simple EXEC region has an exact expression DAG"
            elif any(a0 >= a and b0 <= b for a, b in loop_ranges):
                resolution = "ABSORBED_BY_EXACT_RECURRENCE"
                reason = "region control/value recurrence is explicitly represented by exact loop IR"
            else:
                resolution = "STRUCTURAL_PARTIAL"
                reason = "control skeleton is exact but complete enclosed VGPR value dataflow is not yet lifted"
            structured_regions.append({**r, "program_resolution": resolution, "program_resolution_reason": reason})

        # Exact cbuffer source provenance is an input/data-binding tier, not a
        # claim that downstream arithmetic has been expression-lifted.
        cbuffer_rows = []
        for q in cb["loads"]:
            i = int(q["instruction"])
            input_exact.add(i)
            evidence[i].add(q["resolution"])
            cbuffer_rows.append(q)

        mimg_rows = []
        for q in mi["rows"]:
            i = int(q["instruction"])
            input_exact.add(i)
            evidence[i].add("DIMENSION_AWARE_MIMG_ADDRESS")
            mimg_rows.append(q)

        # Exact persistent export-kill contract, retaining all instruction links.
        kills = []
        for q in km["contracts"]:
            kset = {
                int(q["mask_initialized_instruction"]),
                int(q["kill_instruction"]),
                int(q["first_exec_consume_instruction"]),
                int(q["predicate"]["compare_instruction"]),
                int(q["predicate"]["threshold_load_instruction"]),
                int(q["predicate"]["sample_instruction"]),
            }
            for ex in q["governed_exports"]:
                kset |= {
                    int(ex["instruction"]),
                    int(ex["exec_write_instruction"]),
                    int(ex["originating_mask_apply_instruction"]),
                }
            control_exact |= kset
            for i in kset:
                evidence[i].add("PERSISTENT_EXPORT_KILL")
            kills.append(q)

        exports = ir.get("exports", [])
        for q in exports:
            i = int(q["instruction"])
            export_exact.add(i)
            evidence[i].add("NATIVE_MRT_EXPORT")

        # Exact terminal packed-MRT value path. Only explicitly listed value/export
        # instructions are promoted; waits and EXEC restore remain in their proper
        # structural/control tiers. This proof may overlap native export/control tags.
        if terminal_payload is not None:
            tids = {int(i) for i in terminal_payload["value_instruction_indices"]}
            assert tids == {437,438,439,440,441,442,443,445,446,447,448,449,452,453,454}
            assert all(0 <= i < n for i in tids)
            expression_exact |= tids
            for i in tids:
                evidence[i].add("TERMINAL_MRT_PACKED_EXPRESSION_DAG")
            assert {int(x["instruction"]) for x in terminal_payload["exports"]} == {449,454}

        # Primary resolution is intentionally conservative. Higher-level exact
        # evidence overrides lower tiers only for reporting; all tags are retained.
        primary = {}
        for i in range(n):
            if i in expression_exact:
                primary[i] = "EXPRESSION_EXACT"
            elif i in recurrence_exact:
                primary[i] = "RECURRENCE_EXACT"
            elif i in control_exact:
                primary[i] = "CONTROL_EXACT"
            elif i in export_exact:
                primary[i] = "EXPORT_EXACT"
            elif i in input_exact:
                primary[i] = "INPUT_PROVENANCE_EXACT"
            else:
                primary[i] = "STRUCTURAL_ONLY"

        structural_only = {i for i, v in primary.items() if v == "STRUCTURAL_ONLY"}
        structural_spans = []
        for lo, hi in contiguous(structural_only):
            rows = ins[lo:hi + 1]
            ops = collections.Counter(x["opcode"] for x in rows)
            structural_spans.append({
                "start_instruction": lo,
                "end_instruction": hi,
                "instruction_count": hi - lo + 1,
                "opcode_histogram": dict(sorted(ops.items())),
                "image_instructions": [x["index"] for x in rows if "image" in x],
                "branch_instructions": [x["index"] for x in rows if x["opcode"].startswith("s_cbranch") or x["opcode"] == "s_branch"],
                "exec_write_instructions": [x["index"] for x in rows if "exec" in x.get("defs", [])],
                "boundary": "STRUCTURAL_ONLY_NO_VALUE_EXPRESSION_PROMOTION",
            })

        counts = collections.Counter(primary.values())
        exact_nonstructural = n - counts["STRUCTURAL_ONLY"]
        instruction_rows = [
            {
                "instruction": i,
                "address": ins[i]["address_hex"],
                "opcode": ins[i]["opcode"],
                "primary_resolution": primary[i],
                "evidence_tags": sorted(evidence[i]),
            }
            for i in range(n)
        ]

        tex = {int(x["texture_index"]): norm(x["texture"]) for x in st["ps_textures"]["items"]}
        sam = {int(x["index"]): norm(x["first_dword_hex"]) for x in st["ps_samplers"]["items"]}
        image_use = collections.Counter()
        for x in ins:
            if "image" in x:
                for ti in x["image"].get("textures", []):
                    image_use[int(ti)] += 1

        program = {
            "material": material,
            "vertex_shader": norm(st["vertex_shader"]),
            "pixel_shader": shader,
            "material_state4_hex": st["material_state4_hex"],
            "material_state4_u8": st["material_state4_u8"],
            "unk20": st["unk20"],
            "instruction_count": n,
            "cfg": {
                "basic_block_count": ir["basic_block_count"],
                "edge_count": ir["cfg_edge_count"],
                "back_edges": ir["control_flow"]["back_edges"],
            },
            "interpolator_inputs": ir.get("interpolator_inputs", []),
            "texture_bindings": [
                {"texture_index": i, "texture_taghash": tex[i], "native_image_instruction_count": image_use[i]}
                for i in sorted(tex)
            ],
            "sampler_bindings": [
                {"sampler_index": i, "sampler_first_dword_hex": sam[i]}
                for i in sorted(sam)
            ],
            "cbuffer_provenance": {
                "load_count": cb["load_count"],
                "material_b0_load_count": cb["material_b0_load_count"],
                "loads": cbuffer_rows,
            },
            "dimension_aware_mimg": mimg_rows,
            "structured_exec_regions": structured_regions,
            "exact_loop_recurrences": recurrence_payloads,
            "exact_simple_region_expressions": expr_payloads,
            "terminal_mrt_expression": terminal_payload,
            "persistent_export_kills": kills,
            "native_exports": exports,
            "multi_destination_overrides": ir.get("multi_destination_overrides", []),
            "coverage": {
                "primary_resolution_counts": dict(sorted(counts.items())),
                "exact_nonstructural_instruction_count": exact_nonstructural,
                "exact_nonstructural_fraction": exact_nonstructural / n,
                "structural_only_instruction_count": counts["STRUCTURAL_ONLY"],
                "structural_only_fraction": counts["STRUCTURAL_ONLY"] / n,
                "structural_only_spans": structural_spans,
                "definition": (
                    "Coverage counts instruction resolution tiers, not visual accuracy. "
                    "EXPRESSION_EXACT/RECURRENCE_EXACT are value-level; CONTROL/INPUT/EXPORT exact "
                    "tiers prove narrower facts. STRUCTURAL_ONLY means opcode/CFG/def-use are known "
                    "but no higher-level value contract is promoted."
                ),
            },
            "instruction_resolution": instruction_rows,
        }

        # Required anchor facts for the exact target. These are invariant checks,
        # not semantic guesses.
        assert n == 456
        assert sorted(tex) == [0, 1, 2, 3, 4, 5]
        assert len(lr["recurrences"]) == 1
        assert {q["instruction"] for q in exports} == {449, 454}
        assert kills
        assert counts["STRUCTURAL_ONLY"] > 0, "full shader must not be claimed solved by this join"
    except Exception as exc:
        violations.append(repr(exc))

    out = {
        "schema_version": 2,
        "status": (
            "D1_GCN_RENDERER_PROGRAM_IR_EXACT_PARTIAL"
            if program and not violations
            else "D1_GCN_RENDERER_PROGRAM_IR_FAILED"
        ),
        "program": program,
        "violations": violations,
        "semantic_boundary": {
            "native_structure": "EXACT",
            "material_and_resource_provenance": "EXACT_WHERE_LISTED",
            "promoted_simple_region_expressions": "EXACT",
            "promoted_loop_recurrence": "EXACT",
            "terminal_packed_mrt_expressions": "EXACT" if terminal_payload is not None else "NOT_ATTACHED",
            "compressed_export_rgba_channel_unpacking": "WITHHELD_NOT_SOURCE_CLOSED" if terminal_payload is not None else "NOT_ATTACHED",
            "persistent_export_kill": "EXACT",
            "mrt_export_sites": "EXACT",
            "full_mrt_value_expression_tree": "INCOMPLETE",
            "remaining_straight_line_value_dataflow": "NEXT_GATE",
            "visual_texture_role_names": "WITHHELD_UNLESS_SEPARATELY_SOURCE_PROVEN",
            "consumer_policy": (
                "Blender and Rust/WGSL consumers must preserve resolution tiers and native packed export roots. "
                "STRUCTURAL_ONLY spans and compressed channel ordering cannot be silently replaced by guessed semantics."
            ),
        },
        "policy": (
            "This program IR is a lossless join of independently exact proof layers plus explicit "
            "unresolved spans. It is not a claim that every pixel-shader instruction has been decompiled."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n")
    summary = {
        "status": out["status"],
        "shader": program.get("pixel_shader") if program else None,
        "material": program.get("material") if program else None,
        "coverage": program.get("coverage", {}).get("primary_resolution_counts") if program else None,
        "structural_only_spans": len(program.get("coverage", {}).get("structural_only_spans", [])) if program else None,
        "terminal_mrt_attached": terminal_payload is not None,
        "violations": violations,
    }
    print(json.dumps(summary, indent=2))
    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
