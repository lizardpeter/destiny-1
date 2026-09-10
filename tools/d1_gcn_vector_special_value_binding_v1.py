#!/usr/bin/env python3
"""Bind source-backed non-formula GFX7 vector values into the existing D1 VGPR lane SSA.

The 50-opcode formula/source layer remains authoritative for ordinary VALU results.  This
additive layer closes three special result families without rebuilding register state:
V_ADD_I32, V_CNDMASK_B32, and TBUFFER_LOAD_FORMAT_XYZW.  Existing `result:iN:vX` and
`write:iN:vX` identities are retained.  Condition masks and scalar resource registers are
referenced from their existing graphs.  Typed-buffer data remains opaque until resource
descriptor and backing-memory provenance are closed.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
from collections import Counter
from pathlib import Path

import d1_gcn_vector_special_value_semantics_v1 as sem
import d1_gcn_vector_formula_source_binding_v1 as formula_source
import d1_gcn_vector_formula_lane_binding_v1 as formula_lane
import d1_gcn_vector_bit_exact_eval_v1 as bit_eval
import d1_condition_symbolic_dataflow_v1 as condition_df
import d1_gcn_sgpr_ssa_v1 as scalar_ssa

INPUT_STATUS = "D1_GCN_STRUCTURAL_IR_COMPLETE"
FORMULA_SOURCE_STATUS = "D1_GCN_VECTOR_FORMULA_SOURCE_BINDING_EXACT"
CONDITION_STATUS = "D1_GCN_CONDITION_SYMBOLIC_DATAFLOW_EXACT"
SCALAR_STATUS = "D1_GCN_SGPR_SSA_EXACT"
SCHEMA = "d1_gcn_vector_special_value_binding/v1"
STATUS = "D1_GCN_VECTOR_SPECIAL_VALUE_BINDING_EXACT"
VREG_RE = re.compile(r"^v(\d+)$")
SREG_RE = re.compile(r"^s(\d+)$")
SRANGE_RE = re.compile(r"^s\[(\d+):(\d+)\]$")


def _add(nodes: dict[str, dict], nid: str, kind: str, *, inputs=(), instruction=None,
         opcode=None, exactness="SOURCE_CLOSED", detail=None) -> str:
    n = {"id": nid, "kind": kind, "inputs": list(inputs), "exactness": exactness}
    if instruction is not None:
        n["instruction"] = instruction
    if opcode is not None:
        n["opcode"] = opcode
    if detail is not None:
        n["detail"] = copy.deepcopy(detail)
    old = nodes.get(nid)
    if old is not None and old != n:
        raise ValueError(f"special value node identity collision:{nid}")
    nodes[nid] = n
    return nid


def _vgpr_state(row: dict, nodes: dict[str, dict], idx: int, reg: str, violations: list[str]) -> str | None:
    vals = sorted({u.get("value") for u in (row.get("vgpr_uses") or [])
                   if u.get("register") == reg and u.get("value") is not None})
    if len(vals) != 1:
        violations.append(f"vgpr_state_resolution:{idx}:{reg}:{vals}")
        return None
    ref = vals[0]
    if ref not in nodes:
        violations.append(f"vgpr_state_missing:{idx}:{reg}:{ref}")
        return None
    return ref


def _scalar_state(srow: dict, snodes: dict[str, dict], idx: int, reg: str, violations: list[str]) -> tuple[str, str] | None:
    vals = sorted({u.get("value") for u in (srow.get("scalar_uses") or [])
                   if u.get("register") == reg and u.get("value") is not None})
    if len(vals) != 1:
        violations.append(f"scalar_state_resolution:{idx}:{reg}:{vals}")
        return None
    ref = vals[0]
    node = snodes.get(ref)
    if node is None:
        violations.append(f"scalar_state_missing:{idx}:{reg}:{ref}")
        return None
    return ref, node.get("kind", "UNKNOWN")


def _scalar_bridge(nodes: dict[str, dict], srow: dict, snodes: dict[str, dict], *, idx: int,
                   op: str, reg: str, role: str, ordinal: int, violations: list[str]) -> str | None:
    got = _scalar_state(srow, snodes, idx, reg, violations)
    if got is None:
        return None
    ref, kind = got
    return _add(
        nodes, f"special:i{idx}:{role}:s{ordinal}", "EXACT_SCALAR_SSA_STATE_REFERENCE",
        instruction=idx, opcode=op, exactness="GLOBAL_SCALAR_SSA_IDENTITY_EXACT",
        detail={
            "register": reg,
            "role": role,
            "external_graph": "d1_gcn_sgpr_ssa/v1",
            "external_node": ref,
            "external_ref": f"scalar:{ref}",
            "external_node_kind": kind,
        },
    )


def _condition_bridge(nodes: dict[str, dict], cnodes: dict[str, dict], *, idx: int, op: str,
                      ref: str, role: str, key: str | None, violations: list[str]) -> str | None:
    if ref not in cnodes:
        violations.append(f"condition_state_missing:{idx}:{op}:{role}:{ref}")
        return None
    return _add(
        nodes, f"special:i{idx}:{role}", "EXACT_CONDITION_MASK_STATE_REFERENCE",
        instruction=idx, opcode=op, exactness="GLOBAL_CONDITION_MASK_IDENTITY_EXACT",
        detail={
            "role": role,
            "mask_key": key,
            "external_graph": "d1_gcn_condition_symbolic_dataflow/v1",
            "external_node": ref,
            "external_ref": f"condition:{ref}",
            "external_node_kind": cnodes[ref].get("kind"),
        },
    )


def _literal(nodes: dict[str, dict], idx: int, op: str, role: str, token: str, violations: list[str]) -> str | None:
    try:
        bits = bit_eval.literal_u32(token)
    except Exception as e:
        violations.append(f"literal_parse:{idx}:{op}:{role}:{token!r}:{type(e).__name__}:{e}")
        return None
    return _add(
        nodes, f"special:i{idx}:{role}:literal", "ISA_LITERAL_32",
        instruction=idx, opcode=op, exactness="ENCODED_LITERAL_VALUE_EXACT",
        detail={"token": token, "u32_bits": bits, "role": role},
    )


def _value_source(nodes: dict[str, dict], row: dict, srow: dict, snodes: dict[str, dict], *,
                  idx: int, op: str, token: str, role: str, ordinal: int,
                  allow_source_modifiers: bool, violations: list[str]) -> str | None:
    try:
        parsed = formula_lane._parse_source_token(token)
    except Exception as e:
        violations.append(f"source_parse:{idx}:{op}:{role}:{type(e).__name__}:{e}")
        return None
    if parsed.get("omod") or parsed.get("clamp"):
        violations.append(f"source_has_output_modifier:{idx}:{op}:{role}:{token!r}")
        return None
    if (parsed.get("abs") or parsed.get("neg")) and not allow_source_modifiers:
        violations.append(f"unexpected_source_modifier:{idx}:{op}:{role}:{token!r}")
        return None
    atom = parsed["atom"]
    if VREG_RE.fullmatch(atom):
        ref = _vgpr_state(row, nodes, idx, atom, violations)
    elif SREG_RE.fullmatch(atom):
        ref = _scalar_bridge(nodes, srow, snodes, idx=idx, op=op, reg=atom,
                             role=role, ordinal=ordinal, violations=violations)
    elif formula_lane._is_literal(atom):
        ref = _literal(nodes, idx, op, role, atom, violations)
    else:
        violations.append(f"unregistered_value_source:{idx}:{op}:{role}:{atom!r}")
        return None
    if ref is None:
        return None
    raw = _add(
        nodes, f"special:i{idx}:{role}:raw", "ARCHITECTURAL_SOURCE_OPERAND_SLOT",
        inputs=[ref], instruction=idx, opcode=op, exactness="SOURCE_IDENTITY_EXACT",
        detail={"role": role, "token": parsed["token"], "atom": atom},
    )
    cur = raw
    if parsed.get("abs"):
        cur = _add(
            nodes, f"special:i{idx}:{role}:abs", "GFX7_VOP3_INPUT_ABS",
            inputs=[cur], instruction=idx, opcode=op,
            exactness="SOURCE_CLOSED_MODIFIER_STRUCTURE_NUMERIC_B32_INTERPRETATION_SYMBOLIC",
            detail={"role": role},
        )
    if parsed.get("neg"):
        cur = _add(
            nodes, f"special:i{idx}:{role}:neg", "GFX7_VOP3_INPUT_NEG",
            inputs=[cur], instruction=idx, opcode=op,
            exactness="SOURCE_CLOSED_MODIFIER_STRUCTURE_NUMERIC_B32_INTERPRETATION_SYMBOLIC",
            detail={"role": role},
        )
    return cur


def _check_result_identity(nodes: dict[str, dict], row: dict, *, idx: int, op: str,
                           regs: list[str], violations: list[str]) -> list[tuple[str, str, dict]]:
    writes = row.get("vgpr_writes") or []
    if len(writes) != len(regs):
        violations.append(f"lane_write_width:{idx}:{op}:{len(writes)}!={len(regs)}")
        return []
    out = []
    for component, reg in enumerate(regs):
        wr = writes[component]
        rid = f"result:i{idx}:{reg}"
        wid = f"write:i{idx}:{reg}"
        rn, wn = nodes.get(rid), nodes.get(wid)
        if wr.get("register") != reg or wr.get("result") != rid or wr.get("new") != wid:
            violations.append(f"lane_identity:{idx}:{op}:c{component}:{wr!r}:{rid}:{wid}")
            continue
        if rn is None or wn is None:
            violations.append(f"lane_node_missing:{idx}:{op}:c{component}:{rid}:{wid}")
            continue
        if rn.get("kind") != "OPAQUE_INSTRUCTION_RESULT_COMPONENT":
            violations.append(f"expected_opaque_nonformula_result:{idx}:{op}:c{component}:{rn.get('kind')}")
            continue
        if rn.get("instruction") != idx or rn.get("opcode") != op or rn.get("key") != reg:
            violations.append(f"result_metadata:{idx}:{op}:c{component}:{rn!r}")
            continue
        if (rn.get("detail") or {}).get("destination_component") != component:
            violations.append(f"result_component:{idx}:{op}:{reg}:{rn.get('detail')!r}")
            continue
        win = wn.get("inputs") or []
        if len(win) < 2 or win[1] != rid or win.count(rid) != 1:
            violations.append(f"physical_write_edge:{idx}:{op}:{reg}:{win!r}")
            continue
        out.append((rid, wid, wr))
    return out


def _parse_tbuffer_tail(operands: list[str], idx: int, violations: list[str]) -> dict | None:
    if len(operands) < 5:
        violations.append(f"tbuffer_operand_count:{idx}:{operands!r}")
        return None
    tail = ",".join(operands[3:]).strip()
    marker = " format:["
    if marker not in tail or not tail.endswith("]"):
        violations.append(f"tbuffer_tail_form:{idx}:{tail!r}")
        return None
    prefix, fmt = tail.split(marker, 1)
    fmt = fmt[:-1]
    if "," not in fmt:
        violations.append(f"tbuffer_format_form:{idx}:{fmt!r}")
        return None
    dfmt, nfmt = [x.strip() for x in fmt.split(",", 1)]
    toks = prefix.split()
    if not toks:
        violations.append(f"tbuffer_missing_soffset:{idx}:{tail!r}")
        return None
    soffset = toks[0]
    flags = toks[1:]
    allowed_plain = {"idxen", "offen", "addr64", "glc", "slc"}
    unknown = [x for x in flags if x not in allowed_plain and not x.startswith("offset:")]
    if unknown:
        violations.append(f"tbuffer_unknown_flags:{idx}:{unknown}:{tail!r}")
        return None
    offsets = [x for x in flags if x.startswith("offset:")]
    if len(offsets) > 1:
        violations.append(f"tbuffer_multiple_offsets:{idx}:{offsets}")
        return None
    offset12 = 0
    if offsets:
        try:
            offset12 = int(offsets[0].split(":", 1)[1], 0)
        except Exception:
            violations.append(f"tbuffer_bad_offset:{idx}:{offsets[0]!r}")
            return None
    return {
        "tail": tail,
        "soffset_token": soffset,
        "idxen": "idxen" in flags,
        "offen": "offen" in flags,
        "addr64": "addr64" in flags,
        "glc": "glc" in flags,
        "slc": "slc" in flags,
        "offset12": offset12,
        "dfmt": dfmt,
        "nfmt": nfmt,
    }


def analyze(v2: dict) -> dict:
    if v2.get("status") != INPUT_STATUS:
        raise ValueError(f"input status {v2.get('status')!r}")
    bad = sem.validate()
    if bad:
        raise ValueError(f"special semantics invalid:{bad}")

    out = formula_source.analyze(v2)
    if out.get("status") != FORMULA_SOURCE_STATUS or out.get("violations"):
        raise ValueError(f"formula source prerequisite not exact:{out.get('status')}:{(out.get('violations') or [])[:3]}")
    condition = condition_df.analyze(v2)
    if condition.get("status") != CONDITION_STATUS or condition.get("violations"):
        raise ValueError(f"condition prerequisite not exact:{condition.get('status')}:{(condition.get('violations') or [])[:3]}")
    scalar = scalar_ssa.analyze(v2)
    if scalar.get("status") != SCALAR_STATUS or scalar.get("violations"):
        raise ValueError(f"scalar prerequisite not exact:{scalar.get('status')}:{(scalar.get('violations') or [])[:3]}")

    ins = v2.get("instructions") or []
    rows = out.get("instructions") or []
    crows = condition.get("instructions") or []
    srows = scalar.get("instructions") or []
    nodes = out.get("nodes") or {}
    cnodes = condition.get("nodes") or {}
    snodes = scalar.get("nodes") or {}
    if not (len(ins) == len(rows) == len(crows) == len(srows)):
        raise ValueError("special-value prerequisite instruction roster mismatch")

    violations: list[str] = []
    counts = Counter()
    opcounts = Counter()
    component_counts = Counter()
    bindings = []

    for idx, x in enumerate(ins):
        if x.get("index") != idx:
            violations.append(f"instruction_index:{idx}:{x.get('index')}")
            continue
        op = x.get("opcode")
        if op not in sem.SEMANTICS:
            continue
        regs = [r for r in (x.get("defs") or []) if VREG_RE.fullmatch(r or "")]
        expected_width = sem.behavior(op)["result_components"]
        if len(regs) != expected_width:
            violations.append(f"result_width:{idx}:{op}:{len(regs)}!={expected_width}")
            continue
        dests = _check_result_identity(nodes, rows[idx], idx=idx, op=op, regs=regs, violations=violations)
        if len(dests) != expected_width:
            continue
        operands = x.get("operands") or []

        if op == "v_add_i32":
            if len(operands) != 4 or operands[1] not in {"vcc"} and not SRANGE_RE.fullmatch(operands[1] or ""):
                violations.append(f"v_add_i32_operands:{idx}:{operands!r}")
                continue
            s0 = _value_source(nodes, rows[idx], srows[idx], snodes, idx=idx, op=op,
                               token=operands[2], role="src0", ordinal=0,
                               allow_source_modifiers=False, violations=violations)
            s1 = _value_source(nodes, rows[idx], srows[idx], snodes, idx=idx, op=op,
                               token=operands[3], role="src1", ordinal=1,
                               allow_source_modifiers=False, violations=violations)
            md = crows[idx].get("mask_definition")
            if not md or md.get("kind") != "EXEC_GATED_CARRY_MASK_MERGE":
                violations.append(f"v_add_i32_carry_state:{idx}:{md!r}")
                continue
            carry_ref = _condition_bridge(nodes, cnodes, idx=idx, op=op, ref=md.get("node"),
                                          role="carry_mask_out", key=md.get("key"), violations=violations)
            if s0 is None or s1 is None or carry_ref is None:
                continue
            operation = _add(
                nodes, f"special:i{idx}:operation", "GFX7_V_ADD_I32_LOW32_UNSIGNED_SUM",
                inputs=[s0, s1], instruction=idx, opcode=op,
                exactness="SOURCE_CLOSED_BIT_EXACT_OPERATION",
                detail={"formula": sem.behavior(op)["value_formula"], "carry_mask_reference": carry_ref},
            )
            rid, wid, _ = dests[0]
            rn = nodes[rid]
            rn["kind"] = "ARCHITECTURAL_BIT_EXACT_RESULT_COMPONENT"
            rn["inputs"] = [operation]
            rn["exactness"] = "SOURCE_CLOSED_BIT_EXACT_OPERATION"
            rn["detail"] = {
                "destination_component": 0,
                "special_value_binding": {"operation_node": operation, "physical_write_node": wid,
                                           "carry_mask_reference_node": carry_ref},
            }
            counts["v_add_i32_instruction_count"] += 1
            counts["computational_result_component_count"] += 1
            counts["carry_mask_alias_count"] += 1

        elif op == "v_cndmask_b32":
            if len(operands) != 4:
                violations.append(f"v_cndmask_operands:{idx}:{operands!r}")
                continue
            s0 = _value_source(nodes, rows[idx], srows[idx], snodes, idx=idx, op=op,
                               token=operands[1], role="src0", ordinal=0,
                               allow_source_modifiers=True, violations=violations)
            s1 = _value_source(nodes, rows[idx], srows[idx], snodes, idx=idx, op=op,
                               token=operands[2], role="src1", ordinal=1,
                               allow_source_modifiers=True, violations=violations)
            mu = crows[idx].get("mask_use")
            if not mu or mu.get("kind") != "VECTOR_SELECT_BY_MASK":
                violations.append(f"v_cndmask_predicate_state:{idx}:{mu!r}")
                continue
            pred = _condition_bridge(nodes, cnodes, idx=idx, op=op, ref=mu.get("node"),
                                     role="predicate_mask_in", key=mu.get("key"), violations=violations)
            if s0 is None or s1 is None or pred is None:
                continue
            operation = _add(
                nodes, f"special:i{idx}:operation", "GFX7_V_CNDMASK_B32_LANE_SELECT",
                inputs=[s0, s1, pred], instruction=idx, opcode=op,
                exactness="SOURCE_CLOSED_SELECT_WITH_ENCODED_SOURCE_MODIFIERS_RETAINED",
                detail={"formula": sem.behavior(op)["value_formula"], "predicate_mask_reference": pred},
            )
            rid, wid, _ = dests[0]
            rn = nodes[rid]
            rn["kind"] = "ARCHITECTURAL_SYMBOLIC_RESULT_COMPONENT"
            rn["inputs"] = [operation]
            rn["exactness"] = "SOURCE_CLOSED_SELECT_WITH_ENCODED_SOURCE_MODIFIERS_RETAINED"
            rn["detail"] = {
                "destination_component": 0,
                "special_value_binding": {"operation_node": operation, "physical_write_node": wid,
                                           "predicate_mask_reference_node": pred},
            }
            counts["v_cndmask_b32_instruction_count"] += 1
            counts["computational_result_component_count"] += 1
            counts["predicate_mask_alias_count"] += 1

        elif op == "tbuffer_load_format_xyzw":
            if len(operands) < 5 or not VREG_RE.fullmatch(operands[1] or ""):
                violations.append(f"tbuffer_operands:{idx}:{operands!r}")
                continue
            rm = SRANGE_RE.fullmatch(operands[2] or "")
            if not rm:
                violations.append(f"tbuffer_srsrc_form:{idx}:{operands[2] if len(operands)>2 else None!r}")
                continue
            ra, rb = map(int, rm.groups())
            if rb != ra + 3:
                violations.append(f"tbuffer_srsrc_width:{idx}:{operands[2]!r}")
                continue
            tail = _parse_tbuffer_tail(operands, idx, violations)
            if tail is None:
                continue
            vaddr = _vgpr_state(rows[idx], nodes, idx, operands[1], violations)
            resource_refs = []
            for ordinal, rno in enumerate(range(ra, rb + 1)):
                ref = _scalar_bridge(nodes, srows[idx], snodes, idx=idx, op=op, reg=f"s{rno}",
                                     role="srsrc", ordinal=ordinal, violations=violations)
                if ref is not None:
                    resource_refs.append(ref)
            soff = _value_source(nodes, rows[idx], srows[idx], snodes, idx=idx, op=op,
                                 token=tail["soffset_token"], role="soffset", ordinal=0,
                                 allow_source_modifiers=False, violations=violations)
            if vaddr is None or len(resource_refs) != 4 or soff is None:
                continue
            load = _add(
                nodes, f"special:i{idx}:operation", "GFX7_TYPED_BUFFER_LOAD_XYZW",
                inputs=[vaddr, *resource_refs, soff], instruction=idx, opcode=op,
                exactness="ADDRESS_RESOURCE_FORMAT_INPUT_IDENTITIES_EXACT_RESULT_CONTENT_OPAQUE",
                detail={
                    "vaddr_register": operands[1], "srsrc_register_range": operands[2],
                    "soffset_token": tail["soffset_token"], "idxen": tail["idxen"],
                    "offen": tail["offen"], "addr64": tail["addr64"], "glc": tail["glc"],
                    "slc": tail["slc"], "offset12": tail["offset12"], "dfmt": tail["dfmt"],
                    "nfmt": tail["nfmt"], "component_count": 4,
                    "memory_value_status": "OPAQUE_UNTIL_DESCRIPTOR_AND_BACKING_MEMORY_PROVEN",
                },
            )
            for component, (rid, wid, _) in enumerate(dests):
                value = _add(
                    nodes, f"special:i{idx}:component:{component}", "GFX7_TYPED_BUFFER_RESULT_COMPONENT_OPAQUE",
                    inputs=[load], instruction=idx, opcode=op,
                    exactness="TYPED_RESULT_COMPONENT_IDENTITY_EXACT_MEMORY_CONTENT_OPAQUE",
                    detail={"component": component, "dfmt": tail["dfmt"], "nfmt": tail["nfmt"]},
                )
                rn = nodes[rid]
                rn["kind"] = "ARCHITECTURAL_RESOURCE_RESULT_COMPONENT_OPAQUE"
                rn["inputs"] = [value]
                rn["exactness"] = "TYPED_RESULT_COMPONENT_IDENTITY_EXACT_MEMORY_CONTENT_OPAQUE"
                rn["detail"] = {
                    "destination_component": component,
                    "special_value_binding": {"operation_node": load, "component_node": value,
                                               "physical_write_node": wid},
                }
            counts["tbuffer_load_format_xyzw_instruction_count"] += 1
            counts["resource_opaque_result_component_count"] += 4

        opcounts[op] += 1
        component_counts[op] += len(regs)
        bindings.append({
            "instruction": idx, "address": x.get("address_hex"), "opcode": op,
            "result_registers": regs, "result_component_count": len(regs),
            "category": sem.behavior(op)["category"],
        })

    counts["special_instruction_count"] = sum(opcounts.values())
    counts["special_result_component_count"] = sum(component_counts.values())
    counts["computational_instruction_count"] = (
        counts["v_add_i32_instruction_count"] + counts["v_cndmask_b32_instruction_count"]
    )
    counts["resource_opaque_instruction_count"] = counts["tbuffer_load_format_xyzw_instruction_count"]
    counts["shader_expression_semantic_promotions"] = 0

    for b in bindings:
        for reg in b["result_registers"]:
            rid = f"result:i{b['instruction']}:{reg}"
            if nodes.get(rid, {}).get("kind") == "OPAQUE_INSTRUCTION_RESULT_COMPONENT":
                violations.append(f"unpromoted_special_result:{rid}:{b['opcode']}")

    coverage = {
        **dict(sorted(counts.items())),
        "opcode_instruction_counts": dict(sorted(opcounts.items())),
        "opcode_result_component_counts": dict(sorted(component_counts.items())),
        "integrated_vector_node_count": len(nodes),
        "condition_graph_node_count": len(cnodes),
        "scalar_ssa_node_count": scalar.get("node_count", len(snodes)),
    }
    out["schema"] = SCHEMA
    out["status"] = STATUS if not violations else "D1_GCN_VECTOR_SPECIAL_VALUE_BINDING_WITH_VIOLATIONS"
    out["special_value_semantics"] = sem.document()
    out["condition_prerequisite"] = {"schema": condition.get("schema"), "status": condition.get("status")}
    out["scalar_prerequisite"] = {"schema": scalar.get("schema"), "status": scalar.get("status")}
    out["special_value_coverage"] = coverage
    out["special_value_bindings"] = bindings
    out["violations"] = violations
    out["semantic_boundary"] = {
        "formula_result_and_source_binding": "EXACT_PREREQUISITE",
        "v_add_i32_low32_value": "SOURCE_CLOSED_BIT_EXACT",
        "v_add_i32_carry_mask": "EXACT_CROSS_GRAPH_REFERENCE",
        "v_cndmask_b32_predicate": "EXACT_CROSS_GRAPH_REFERENCE",
        "v_cndmask_b32_source_modifier_structure": "SOURCE_CLOSED_SYMBOLIC",
        "typed_buffer_address_resource_format_input_identity": "EXACT",
        "typed_buffer_fetched_memory_contents": "OPAQUE_RESOURCE_DESCRIPTOR_BACKING_MEMORY_WITHHELD",
        "shader_expression_semantics": "WITHHELD",
        "material_semantics": "WITHHELD",
        "shader_expression_semantic_promotions": 0,
    }
    out["policy"] = (
        "Special non-formula vector values are attached to the existing lane result/write identities. "
        "Carry and predicate state are references into the existing condition graph; scalar resource registers "
        "are references into the existing SGPR SSA. Typed-buffer addressing/format fields are preserved exactly, "
        "but resource descriptor contents and backing memory are not inferred."
    )
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--structural-ir", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()
    out = analyze(json.loads(a.structural_ir.read_text()))
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": out["status"], "coverage": out["special_value_coverage"],
                      "violations": out["violations"][:50]}, indent=2, sort_keys=True))
    return 0 if not out["violations"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
