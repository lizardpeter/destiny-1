#!/usr/bin/env python3
"""Bind source-backed GFX7 vector formulas into the existing Destiny 1 lane-aware VGPR SSA.

This is an architectural-value integration layer, not a shader-expression decompiler.  It keeps
`result:i<instruction>:<vgpr>` as the active-lane result identity and
`write:i<instruction>:<vgpr>` as the already-proven physical VGPR state after EXEC masking.
Formula nodes are inserted behind the existing result identity.  The physical write graph is not
recreated or renumbered.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
from collections import Counter
from pathlib import Path

import d1_gcn_vgpr_lane_ssa_v1 as lane
import d1_gcn_vector_formula_semantics_v1 as sem
import d1_gcn_vector_bit_exact_eval_v1 as bit_eval

INPUT_STATUS = "D1_GCN_STRUCTURAL_IR_COMPLETE"
LANE_STATUS = "D1_GCN_VGPR_LANE_SSA_EXACT"
SCHEMA = "d1_gcn_vector_formula_lane_binding/v1"
STATUS = "D1_GCN_VECTOR_FORMULA_LANE_BINDING_EXACT"
VREG_RE = re.compile(r"^v(\d+)$")
SREG_RE = re.compile(r"^s(\d+)$")
OMOD_RE = re.compile(r"(?:^|\s)(mul|div):([^\s]+)")


def _is_literal(atom: str) -> bool:
    try:
        bit_eval.literal_u32(atom)
        return True
    except Exception:
        return False


def _parse_source_token(token: str) -> dict:
    """Preserve exact CLRX spelling while exposing only source-closed modifier structure."""
    exact = token.strip()
    clamp = bool(re.search(r"(?:^|\s)clamp(?:$|\s)", exact))
    omods = OMOD_RE.findall(exact)
    if len(omods) > 1:
        raise ValueError(f"multiple output modifiers in source token {token!r}")
    core = re.sub(r"(?:^|\s)clamp(?:$|\s)", " ", exact).strip()
    core = OMOD_RE.sub("", core).strip()
    # Signed inline constants (for example -1.0 and -0.5) are encoded source values,
    # not VOP3 NEG modifier syntax. Only a leading minus on a non-literal source is NEG.
    if _is_literal(core):
        neg = False
        abs_on = False
    else:
        neg = core.startswith("-")
        if neg:
            core = core[1:].strip()
        abs_on = core.startswith("abs(") and core.endswith(")")
        if abs_on:
            core = core[4:-1].strip()
    if not core:
        raise ValueError(f"empty source atom after modifiers: {token!r}")
    omod = None
    if omods:
        action, amount = omods[0]
        if (action, amount) not in {("mul", "2"), ("mul", "4"), ("div", "2")}:
            raise ValueError(f"unsupported OMOD spelling {action}:{amount} in {token!r}")
        omod = {("mul", "2"): "MUL_2", ("mul", "4"): "MUL_4", ("div", "2"): "DIV_2"}[(action, amount)]
    return {"token": exact, "atom": core, "abs": abs_on, "neg": neg, "omod": omod, "clamp": clamp}


def _add(nodes: dict[str, dict], node_id: str, kind: str, *, inputs=(), instruction=None,
         opcode=None, exactness="SOURCE_CLOSED", detail=None) -> str:
    n = {"id": node_id, "kind": kind, "inputs": list(inputs), "exactness": exactness}
    if instruction is not None:
        n["instruction"] = instruction
    if opcode is not None:
        n["opcode"] = opcode
    if detail is not None:
        n["detail"] = copy.deepcopy(detail)
    old = nodes.get(node_id)
    if old is not None and old != n:
        raise ValueError(f"formula node identity collision:{node_id}")
    nodes[node_id] = n
    return node_id


def _resolve_atom(atom: str, idx: int, row: dict, original_inputs: list[str], nodes: dict[str, dict],
                  slot: int, violations: list[str]) -> str | None:
    if VREG_RE.fullmatch(atom):
        vals = {u.get("value") for u in (row.get("vgpr_uses") or []) if u.get("register") == atom}
        vals.discard(None)
        if len(vals) != 1:
            violations.append(f"vgpr_source_resolution:{idx}:src{slot}:{atom}:{sorted(vals)}")
            return None
        ref = next(iter(vals))
        if ref not in nodes:
            violations.append(f"vgpr_source_missing_node:{idx}:src{slot}:{atom}:{ref}")
            return None
        return ref
    if SREG_RE.fullmatch(atom):
        refs = []
        for ref in original_inputs:
            n = nodes.get(ref)
            if n and n.get("kind") == "NON_VGPR_SOURCE_AT_INSTRUCTION" and n.get("instruction") == idx and n.get("detail") == atom:
                refs.append(ref)
        refs = sorted(set(refs))
        if len(refs) != 1:
            violations.append(f"sgpr_source_resolution:{idx}:src{slot}:{atom}:{refs}")
            return None
        return refs[0]
    if _is_literal(atom):
        return _add(
            nodes, f"formula:i{idx}:src{slot}:literal", "ISA_LITERAL_32",
            instruction=idx, exactness="ENCODED_LITERAL_VALUE_EXACT",
            detail={"token": atom, "u32_bits": bit_eval.literal_u32(atom)},
        )
    violations.append(f"unregistered_formula_source_atom:{idx}:src{slot}:{atom!r}")
    return None


def analyze(v2: dict) -> dict:
    if v2.get("status") != INPUT_STATUS:
        raise ValueError(f"input status {v2.get('status')!r}")
    registry_problems = sem.validate()
    evaluator_problems = bit_eval.validate()
    if registry_problems or evaluator_problems:
        raise ValueError(f"formula prerequisites invalid:{registry_problems[:3]}:{evaluator_problems[:3]}")

    base = lane.analyze(v2)
    if base.get("status") != LANE_STATUS or base.get("violations"):
        raise ValueError(f"lane SSA prerequisite not exact:{base.get('status')}:{(base.get('violations') or [])[:3]}")

    # lane.analyze() returns a fresh per-program graph. Mutate it in place to avoid duplicating
    # millions of SSA nodes during the corpus replay while preserving every existing identity.
    lane_prereq = {
        "schema": base.get("schema"), "status": base.get("status"),
        "node_count": base.get("node_count"), "coverage": copy.deepcopy(base.get("coverage") or {}),
    }
    lane_coverage = copy.deepcopy(base.get("coverage") or {})
    out = base
    nodes = out.get("nodes") or {}
    rows = out.get("instructions") or []
    ins = v2.get("instructions") or []
    violations: list[str] = []
    counts = Counter()
    opcode_instruction_counts = Counter()
    opcode_component_counts = Counter()
    bindings: list[dict] = []
    bound_result_ids: set[str] = set()
    bound_write_ids: set[str] = set()
    mode_instructions: set[int] = set()
    modifier_instr = {k: set() for k in ("ABS", "NEG", "OMOD", "CLAMP")}
    any_modifier_instr: set[int] = set()

    for idx, x in enumerate(ins):
        if x.get("index") != idx:
            violations.append(f"instruction_index:{idx}:{x.get('index')}")
            continue
        op = x.get("opcode")
        if op not in sem.PENDING:
            continue
        ent = sem.FORMULAS[op]
        vd = [r for r in (x.get("defs") or []) if VREG_RE.fullmatch(r or "")]
        if len(vd) != ent["result_components"]:
            violations.append(f"result_width:{idx}:{op}:{len(vd)}!={ent['result_components']}")
            continue
        row = rows[idx]
        writes = row.get("vgpr_writes") or []
        if len(writes) != len(vd):
            violations.append(f"lane_write_width:{idx}:{op}:{len(writes)}!={len(vd)}")
            continue
        operands = x.get("operands") or []
        nsrc = ent["explicit_source_count"]
        if len(operands) != 1 + nsrc:
            violations.append(f"operand_count:{idx}:{op}:{len(operands)}!={1+nsrc}:{operands!r}")
            continue

        # Prove the durable no-second-register-graph binding before creating formula nodes.
        destination_records = []
        for component, reg in enumerate(vd):
            wr = writes[component]
            expected_result = f"result:i{idx}:{reg}"
            expected_write = f"write:i{idx}:{reg}"
            if wr.get("register") != reg:
                violations.append(f"lane_write_register:{idx}:c{component}:{wr.get('register')}!={reg}")
            if wr.get("result") != expected_result:
                violations.append(f"lane_result_identity:{idx}:c{component}:{wr.get('result')}!={expected_result}")
            if wr.get("new") != expected_write:
                violations.append(f"lane_write_identity:{idx}:c{component}:{wr.get('new')}!={expected_write}")
            result_node = nodes.get(expected_result)
            write_node = nodes.get(expected_write)
            if result_node is None or write_node is None:
                violations.append(f"lane_binding_missing_node:{idx}:c{component}:{expected_result}:{expected_write}")
                continue
            if result_node.get("kind") != "OPAQUE_INSTRUCTION_RESULT_COMPONENT":
                violations.append(f"lane_result_kind:{idx}:c{component}:{result_node.get('kind')}")
            if result_node.get("instruction") != idx or result_node.get("opcode") != op or result_node.get("key") != reg:
                violations.append(f"lane_result_metadata:{idx}:c{component}:{result_node}")
            if (result_node.get("detail") or {}).get("destination_component") != component:
                violations.append(f"lane_result_component:{idx}:{reg}:{(result_node.get('detail') or {}).get('destination_component')}!={component}")
            win = write_node.get("inputs") or []
            if win.count(expected_result) != 1:
                violations.append(f"write_result_edge_count:{idx}:{reg}:{win.count(expected_result)}")
            if len(win) < 2 or win[1] != expected_result:
                violations.append(f"write_result_edge_position:{idx}:{reg}:{win}")
            if expected_result in bound_result_ids:
                violations.append(f"duplicate_result_binding:{expected_result}")
            if expected_write in bound_write_ids:
                violations.append(f"duplicate_write_binding:{expected_write}")
            bound_result_ids.add(expected_result)
            bound_write_ids.add(expected_write)
            destination_records.append((component, reg, wr, expected_result, expected_write, copy.deepcopy(result_node.get("inputs") or [])))
        if len(destination_records) != len(vd):
            continue
        original_inputs = destination_records[0][5]

        parsed_sources = []
        source_value_nodes = []
        source_resolved_refs = []
        for slot, token in enumerate(operands[1:]):
            try:
                parsed = _parse_source_token(token)
            except Exception as e:
                violations.append(f"source_modifier_parse:{idx}:src{slot}:{type(e).__name__}:{e}")
                continue
            ref = _resolve_atom(parsed["atom"], idx, row, original_inputs, nodes, slot, violations)
            if ref is None:
                continue
            raw = _add(
                nodes, f"formula:i{idx}:src{slot}:raw", "ARCHITECTURAL_SOURCE_OPERAND_SLOT",
                inputs=[ref], instruction=idx, opcode=op, exactness="SOURCE_IDENTITY_EXACT",
                detail={"slot": slot, "token": parsed["token"], "atom": parsed["atom"]},
            )
            cur = raw
            if parsed["abs"]:
                cur = _add(
                    nodes, f"formula:i{idx}:src{slot}:abs", "GFX7_VOP3_INPUT_ABS",
                    inputs=[cur], instruction=idx, opcode=op, exactness="SOURCE_CLOSED_ABS_BEFORE_NEG",
                    detail={"slot": slot},
                )
                modifier_instr["ABS"].add(idx)
                any_modifier_instr.add(idx)
            if parsed["neg"]:
                cur = _add(
                    nodes, f"formula:i{idx}:src{slot}:neg", "GFX7_VOP3_INPUT_NEG",
                    inputs=[cur], instruction=idx, opcode=op, exactness="SOURCE_CLOSED_NEG_AFTER_ABS",
                    detail={"slot": slot},
                )
                modifier_instr["NEG"].add(idx)
                any_modifier_instr.add(idx)
            parsed_sources.append(parsed)
            source_value_nodes.append(cur)
            source_resolved_refs.append(ref)
        if len(source_value_nodes) != nsrc:
            violations.append(f"source_binding_count:{idx}:{op}:{len(source_value_nodes)}!={nsrc}")
            continue

        omods = {p["omod"] for p in parsed_sources if p["omod"] is not None}
        clamps = any(p["clamp"] for p in parsed_sources)
        if len(omods) > 1:
            violations.append(f"multiple_instruction_omod:{idx}:{op}:{sorted(omods)}")
            continue
        omod = next(iter(omods)) if omods else None
        if omod:
            modifier_instr["OMOD"].add(idx)
            any_modifier_instr.add(idx)
        if clamps:
            modifier_instr["CLAMP"].add(idx)
            any_modifier_instr.add(idx)

        op_inputs = list(source_value_nodes)
        old_dest_nodes = []
        if ent["old_destination_is_input"]:
            for component, reg, wr, _, _, _ in destination_records:
                old = wr.get("old")
                if old not in nodes:
                    violations.append(f"old_dest_missing_lane_state:{idx}:{reg}:{old}")
                    continue
                old_ref = _add(
                    nodes, f"formula:i{idx}:old_dest:c{component}", "OLD_DESTINATION_ARITHMETIC_INPUT",
                    inputs=[old], instruction=idx, opcode=op, exactness="LANE_SSA_STATE_IDENTITY_EXACT",
                    detail={
                        "component": component, "register": reg,
                        "role": "ARITHMETIC_INPUT_INDEPENDENT_OF_INACTIVE_LANE_PRESERVATION",
                    },
                )
                old_dest_nodes.append(old_ref)
                counts["old_destination_arithmetic_input_component_count"] += 1
            if len(old_dest_nodes) != len(destination_records):
                violations.append(f"old_dest_binding_count:{idx}:{op}:{len(old_dest_nodes)}!={len(destination_records)}")
                continue
            op_inputs.extend(old_dest_nodes)
            counts["old_destination_arithmetic_input_instruction_count"] += 1

        # Every old opaque result input must be claimed by explicit formula state or OLD_D.
        # Literals are new encoded-value nodes and therefore are intentionally absent here.
        original_ref_union = {ref for _, _, _, _, _, inputs in destination_records for ref in inputs}
        claimed_raw_refs = {ref for ref in source_resolved_refs if ref in original_ref_union}
        if ent["old_destination_is_input"]:
            claimed_raw_refs.update(wr.get("old") for _, _, wr, _, _, _ in destination_records)
        for component, reg, _, _, _, original_result_inputs in destination_records:
            original_ref_set = set(original_result_inputs)
            if claimed_raw_refs != original_ref_set:
                violations.append(
                    f"formula_raw_input_accounting:{idx}:c{component}:{reg}:"
                    f"claimed={sorted(claimed_raw_refs)}:original={sorted(original_ref_set)}"
                )
        counts["formula_raw_input_accounting_instruction_count"] += 1

        mode_ref = None
        if ent["fp_state_policy"] != "NOT_APPLICABLE":
            mode_ref = _add(
                nodes, f"formula:i{idx}:mode", "GFX7_MODE_SNAPSHOT",
                instruction=idx, opcode=op,
                exactness="ARCHITECTURAL_STATE_IDENTITY_SOURCE_CLOSED_VALUE_UNRESOLVED",
                detail={"policy": ent["fp_state_policy"], "source": copy.deepcopy(sem.FP_MODE)},
            )
            op_inputs.append(mode_ref)
            mode_instructions.add(idx)

        executable = op in sem.BIT_EXACT_REPLAY_READY
        operation = _add(
            nodes, f"formula:i{idx}:op",
            "GFX7_BIT_EXACT_EXECUTABLE_OPERATION" if executable else "GFX7_SYMBOLIC_ARCHITECTURAL_OPERATION",
            inputs=op_inputs, instruction=idx, opcode=op,
            exactness="SOURCE_CLOSED_BIT_EXACT_EXECUTABLE" if executable else "SOURCE_CLOSED_SYMBOLIC_NUMERIC_REPLAY_WITHHELD",
            detail={
                "formula": ent["formula"], "semantic_kind": ent["semantic_kind"],
                "result_kind": ent["result_kind"], "result_components": ent["result_components"],
                "explicit_source_count": ent["explicit_source_count"],
                "old_destination_is_input": ent["old_destination_is_input"],
                "special_rules": copy.deepcopy(ent["special_rules"]),
                "numeric_replay_status": ent["numeric_replay_status"],
                "fp_state_policy": ent["fp_state_policy"],
                "source": copy.deepcopy(ent["source"]),
                "evaluator": ({"module": "d1_gcn_vector_bit_exact_eval_v1", "entrypoint": "evaluate"} if executable else None),
            },
        )

        for component, reg, wr, result_id, write_id, original_result_inputs in destination_records:
            component_node = _add(
                nodes, f"formula:i{idx}:component:c{component}", "GFX7_OPERATION_RESULT_COMPONENT",
                inputs=[operation], instruction=idx, opcode=op, exactness="ARCHITECTURAL_COMPONENT_IDENTITY_EXACT",
                detail={"component": component, "register": reg, "result_kind": ent["result_kind"]},
            )
            final = component_node
            if omod:
                final = _add(
                    nodes, f"formula:i{idx}:component:c{component}:omod", "GFX7_VOP3_OUTPUT_MODIFIER",
                    inputs=[final], instruction=idx, opcode=op, exactness="SOURCE_CLOSED_OMOD_BEFORE_CLAMP",
                    detail={"omod": omod, "ordering": "BASE_OPERATION_THEN_OMOD_THEN_CLAMP"},
                )
            if clamps:
                final = _add(
                    nodes, f"formula:i{idx}:component:c{component}:clamp", "GFX7_VOP3_CLAMP_BOUNDARY",
                    inputs=[final], instruction=idx, opcode=op,
                    exactness="WITHHELD_AMD_REV1_3_INTERNAL_SOURCE_CONFLICT",
                    detail=copy.deepcopy(sem.VOP3_MODIFIERS["clamp"]),
                )

            result_node = nodes[result_id]
            result_node["kind"] = "ARCHITECTURAL_BIT_EXACT_RESULT_COMPONENT" if executable else "ARCHITECTURAL_SYMBOLIC_RESULT_COMPONENT"
            result_node["inputs"] = [final]
            result_node["exactness"] = (
                "SOURCE_CLOSED_BIT_EXACT_EXECUTABLE" if executable
                else ("SOURCE_CLOSED_SYMBOLIC_CLAMP_WITHHELD" if clamps else "SOURCE_CLOSED_SYMBOLIC_NUMERIC_REPLAY_WITHHELD")
            )
            result_node["detail"] = {
                "destination_component": component,
                "formula_binding": {
                    "operation_node": operation,
                    "final_value_node": final,
                    "physical_write_node": write_id,
                    "source_operand_tokens": [p["token"] for p in parsed_sources],
                    "source_value_nodes": list(source_value_nodes),
                    "old_destination_arithmetic_inputs": list(old_dest_nodes),
                    "mode_snapshot": mode_ref,
                    "omod": omod,
                    "clamp": clamps,
                    "numeric_replay": "BIT_EXACT_EXECUTABLE" if executable else "SYMBOLIC_ARCHITECTURAL_OPERATION",
                    "lane_ssa_original_source_inputs": original_result_inputs,
                },
            }
            bindings.append({
                "instruction": idx, "opcode": op, "component": component, "register": reg,
                "result_node": result_id, "write_node": write_id, "formula_value_node": final,
                "bit_exact_executable": executable,
            })
            counts["formula_result_component_binding_count"] += 1
            counts["physical_write_binding_count"] += 1
            if executable:
                counts["bit_exact_result_component_count"] += 1
            else:
                counts["symbolic_result_component_count"] += 1
            opcode_component_counts[op] += 1

        counts["formula_instruction_count"] += 1
        if executable:
            counts["bit_exact_instruction_count"] += 1
        else:
            counts["symbolic_instruction_count"] += 1
        opcode_instruction_counts[op] += 1

    for nid, n in nodes.items():
        for src in n.get("inputs") or []:
            if src not in nodes:
                violations.append(f"missing_node_reference:{nid}->{src}")
    if counts["formula_result_component_binding_count"] != len(bound_result_ids):
        violations.append(f"result_binding_uniqueness:{counts['formula_result_component_binding_count']}!={len(bound_result_ids)}")
    if counts["physical_write_binding_count"] != len(bound_write_ids):
        violations.append(f"write_binding_uniqueness:{counts['physical_write_binding_count']}!={len(bound_write_ids)}")

    total_lane_results = lane_coverage.get("vgpr_result_component_node_count", 0)
    counts["opaque_nonformula_result_component_count"] = total_lane_results - counts["formula_result_component_binding_count"]
    counts["mode_snapshot_instruction_count"] = len(mode_instructions)
    for name, ids in modifier_instr.items():
        counts[f"{name.lower()}_modifier_instruction_count"] = len(ids)
    counts["modifier_touched_instruction_count"] = len(any_modifier_instr)
    counts["formula_operation_node_count"] = counts["formula_instruction_count"]
    counts["shader_expression_semantic_promotions"] = 0

    out["schema"] = SCHEMA
    out["status"] = STATUS if not violations else "D1_GCN_VECTOR_FORMULA_LANE_BINDING_WITH_VIOLATIONS"
    out["lane_ssa_prerequisite"] = lane_prereq
    out["node_count"] = len(nodes)
    out["coverage"] = {
        **lane_coverage,
        **dict(sorted(counts.items())),
        "formula_opcode_count": len(opcode_instruction_counts),
        "formula_opcode_instruction_counts": dict(sorted(opcode_instruction_counts.items())),
        "formula_opcode_component_counts": dict(sorted(opcode_component_counts.items())),
    }
    out["formula_bindings"] = bindings
    out["violations"] = violations
    out["semantic_boundary"] = {
        "physical_vgpr_lane_ssa": "REUSED_WITH_IDENTITIES_UNCHANGED",
        "formula_result_to_lane_candidate_binding": "EXACT" if not violations else "NOT_PROMOTED",
        "formula_result_to_physical_write_binding": "EXACT" if not violations else "NOT_PROMOTED",
        "integer_bit_exact_operations": "EXECUTABLE_ARCHITECTURAL_NODES" if not violations else "NOT_PROMOTED",
        "floating_and_special_operations": "SOURCE_CLOSED_SYMBOLIC_WITH_MODE_STATE_RETAINED",
        "vop3_abs_neg_order": "SOURCE_CLOSED_EXPLICIT_NODES",
        "vop3_omod_order": "SOURCE_CLOSED_EXPLICIT_NODE_BEFORE_CLAMP",
        "vop3_clamp_numeric_range": "WITHHELD_AMD_REV1_3_INTERNAL_SOURCE_CONFLICT",
        "resource_lds_interpolation_values": "UNCHANGED_OPAQUE_NONFORMULA_RESULT_NODES",
        "shader_expression_semantics": "WITHHELD",
        "material_semantics": "WITHHELD",
        "shader_expression_semantic_promotions": 0,
    }
    out["policy"] = (
        "The frozen GFX7 base formulas are attached to the existing lane-aware VGPR result identities. "
        "Physical write identities and EXEC/inactive-lane merge semantics are unchanged. Integer/bit operations "
        "use an executable bit-pattern evaluator; floating/special operations remain architectural symbolic nodes "
        "with MODE retained. MAC old-destination arithmetic input is represented separately from the physical "
        "write's inactive-lane preservation input. CLAMP remains numerically unresolved."
    )
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--structural-ir", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()
    d = analyze(json.loads(a.structural_ir.read_text()))
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(d, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": d["status"], "coverage": d["coverage"], "violations": d["violations"][:20]}, indent=2, sort_keys=True))
    return 0 if not d["violations"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
