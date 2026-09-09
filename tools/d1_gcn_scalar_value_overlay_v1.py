#!/usr/bin/env python3
"""Bind exact D1 scalar SSA result components to source-backed architectural machine values.

This layer is deliberately below shader-expression semantics.  It reuses the already exact
EXEC, condition-mask/SCC, lane-aware VGPR, and physical SGPR/M0 SSA graphs.  Non-memory
scalar result values are bound to source-documented architectural identities; scalar-memory
loads remain explicit opaque values until descriptor/address/resource semantics are closed.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
from collections import Counter
from pathlib import Path

import d1_gcn_exec_symbolic_dataflow_v1 as exec_df
import d1_condition_symbolic_dataflow_v1 as cond_df
import d1_gcn_vgpr_lane_ssa_v1 as vgpr_df
import d1_gcn_sgpr_ssa_v1 as scalar_df
import d1_gcn_scalar_value_semantics_v1 as sem

INPUT_STATUS = "D1_GCN_STRUCTURAL_IR_COMPLETE"
EXEC_STATUS = "D1_GCN_EXEC_SYMBOLIC_DATAFLOW_EXACT"
COND_STATUS = "D1_GCN_CONDITION_SYMBOLIC_DATAFLOW_EXACT"
VGPR_STATUS = "D1_GCN_VGPR_LANE_SSA_EXACT"
SCALAR_STATUS = "D1_GCN_SGPR_SSA_EXACT"
SCHEMA = "d1_gcn_scalar_value_overlay/v1"
STATUS = "D1_GCN_SCALAR_VALUE_OVERLAY_EXACT"
PAIR_RE = re.compile(r"^s\[(\d+):(\d+)\]$")
SREG_RE = re.compile(r"^s(\d+)$")
VGPR_RE = re.compile(r"^v(\d+)$")


def pair_halves(text: str) -> list[str]:
    m = PAIR_RE.fullmatch(text or "")
    if not m:
        return []
    a, b = map(int, m.groups())
    if b != a + 1:
        return []
    return [f"s{a}", f"s{b}"]


def _find_value(rows: list[dict], reg: str) -> str | None:
    for r in rows:
        if r.get("register") == reg:
            return r.get("value")
    return None


def _scalar_operand(atom: str, scalar_row: dict, exec_row: dict) -> dict:
    """Resolve one architectural source operand without inventing shader meaning."""
    halves = pair_halves(atom)
    if halves:
        values = []
        for h in halves:
            v = _find_value(scalar_row.get("scalar_uses") or [], h)
            if v is None:
                raise ValueError(f"missing scalar pair source {atom}:{h}")
            values.append({"register": h, "node": f"scalar:{v}"})
        return {"kind": "SCALAR_PAIR_STATE", "operand": atom, "components": values}
    if SREG_RE.fullmatch(atom or "") or atom == "m0":
        v = _find_value(scalar_row.get("scalar_uses") or [], atom)
        if v is None:
            raise ValueError(f"missing scalar source {atom}")
        return {"kind": "SCALAR_STATE", "operand": atom, "node": f"scalar:{v}"}
    if atom == "exec":
        return {"kind": "EXEC_MASK", "operand": atom, "node": f"exec:{exec_row['exec_in']}"}
    if atom in {"exec_lo", "exec_hi"}:
        return {
            "kind": "EXEC_MASK_HALF", "operand": atom, "node": f"exec:{exec_row['exec_in']}",
            "half": 0 if atom.endswith("_lo") else 1,
        }
    if atom == "vcc" or atom in {"vcc_lo", "vcc_hi"}:
        return {"kind": "CONDITION_STATE_REQUIRED", "operand": atom}
    if VGPR_RE.fullmatch(atom or ""):
        return {"kind": "VGPR_STATE_REQUIRED", "operand": atom}
    return {"kind": "ISA_OPERAND_TOKEN", "operand": atom}


def _check_external_ref(ref: str, scalar: dict, ex: dict, cond: dict, vgpr: dict) -> bool:
    if ref.startswith("scalar:"):
        return ref[7:] in (scalar.get("nodes") or {})
    if ref.startswith("exec:"):
        return ref[5:] in (ex.get("nodes") or {})
    if ref.startswith("condition:"):
        return ref[10:] in (cond.get("nodes") or {})
    if ref.startswith("vgpr:"):
        return ref[5:] in (vgpr.get("nodes") or {})
    return False


def _all_external_refs(obj) -> list[str]:
    out = []
    if isinstance(obj, str) and obj.startswith(("scalar:", "exec:", "condition:", "vgpr:")):
        out.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            out.extend(_all_external_refs(v))
    elif isinstance(obj, list):
        for v in obj:
            out.extend(_all_external_refs(v))
    return out


def analyze(v2: dict) -> dict:
    violations: list[str] = []
    if v2.get("status") != INPUT_STATUS:
        raise ValueError(f"input status {v2.get('status')!r}")
    if sem.validate():
        raise ValueError(f"scalar value registry invalid: {sem.validate()}")

    ex = exec_df.analyze(v2)
    cond = cond_df.analyze(v2)
    vgpr = vgpr_df.analyze(v2)
    scalar = scalar_df.analyze(v2)
    for name, d, status in (
        ("exec", ex, EXEC_STATUS), ("condition", cond, COND_STATUS),
        ("vgpr", vgpr, VGPR_STATUS), ("scalar", scalar, SCALAR_STATUS),
    ):
        if d.get("status") != status or d.get("violations"):
            raise ValueError(f"{name} prerequisite not exact:{d.get('status')}:{(d.get('violations') or [])[:3]}")

    ins = v2.get("instructions") or []
    erows = ex.get("instructions") or []
    crows = cond.get("instructions") or []
    vrows = vgpr.get("instructions") or []
    srows = scalar.get("instructions") or []
    if not (len(ins) == len(erows) == len(crows) == len(vrows) == len(srows)):
        raise ValueError("prerequisite instruction roster mismatch")

    values: dict[str, dict] = {}
    bindings: list[dict] = []
    instruction_rows: list[dict] = []
    counts = Counter()
    opcounts = Counter()
    kindcounts = Counter()
    bound_targets = set()

    def add_value(vid: str, kind: str, *, idx: int, op: str, width: int | None,
                  inputs=None, external_ref=None, exactness="SOURCE_DOCUMENTED_ARCHITECTURAL_VALUE",
                  detail=None):
        n = {
            "id": vid, "kind": kind, "instruction": idx, "opcode": op,
            "width_bits": width, "inputs": copy.deepcopy(inputs or []), "exactness": exactness,
        }
        if external_ref is not None:
            n["external_ref"] = external_ref
        if detail is not None:
            n["detail"] = copy.deepcopy(detail)
        old = values.get(vid)
        if old is not None and old != n:
            raise ValueError(f"overlay value collision:{vid}")
        values[vid] = n
        kindcounts[kind] += 1
        return vid

    for idx, x in enumerate(ins):
        if x.get("index") != idx:
            violations.append(f"instruction_index:{idx}:{x.get('index')}")
            continue
        sr = srows[idx]
        writes = sr.get("scalar_writes") or []
        if not writes:
            continue
        op = x["opcode"]
        if op not in sem.OBSERVED:
            violations.append(f"unregistered_scalar_value_opcode:{idx}:{op}")
            continue
        beh = sem.behavior(op)
        cat = beh["category"]
        operands = x.get("operands") or []
        vid = f"i{idx}:value"
        value_kind = None

        if cat == "SCALAR_MEMORY_RESULT":
            input_refs = [
                {"kind": "SCALAR_STATE", "register": u["register"], "node": f"scalar:{u['value']}"}
                for u in (sr.get("scalar_uses") or [])
            ]
            add_value(
                vid, "OPAQUE_SCALAR_MEMORY_RESULT", idx=idx, op=op, width=len(writes) * 32,
                inputs=input_refs, exactness="MEMORY_VALUE_OPAQUE_RESOURCE_ADDRESS_WITHHELD",
                detail={"operands": operands, "memory_value_status": beh["memory_value_status"]},
            )
            value_kind = "OPAQUE_SCALAR_MEMORY_RESULT"
            counts["opaque_memory_instruction_count"] += 1
            counts["opaque_memory_component_count"] += len(writes)

        elif cat == "CONDITION_MASK_VALUE":
            md = crows[idx].get("mask_definition")
            if not md or md.get("node") not in (cond.get("nodes") or {}):
                violations.append(f"missing_condition_mask_value:{idx}:{op}:{md!r}")
                continue
            ref = f"condition:{md['node']}"
            add_value(
                vid, "CONDITION_MASK_ALIAS", idx=idx, op=op, width=64,
                external_ref=ref, inputs=[{"kind": "CONDITION_MASK", "node": ref}],
                exactness="GLOBAL_CONDITION_VALUE_EXACT",
                detail={"mask_key": md.get("key"), "mask_kind": md.get("kind")},
            )
            value_kind = "CONDITION_MASK_ALIAS"
            counts["condition_alias_instruction_count"] += 1
            counts["condition_alias_component_count"] += len(writes)

        elif cat == "CROSS_STATE_IDENTITY":
            if op == "s_and_saveexec_b64":
                ref = f"exec:{erows[idx]['exec_in']}"
                md = crows[idx].get("mask_definition")
                if not md or md.get("kind") != "SAVE_OLD_EXEC_AND_UPDATE_EXEC":
                    violations.append(f"saveexec_condition_identity:{idx}:{md!r}")
                add_value(
                    vid, "OLD_EXEC_ALIAS", idx=idx, op=op, width=64,
                    external_ref=ref, inputs=[{"kind": "EXEC_IN", "node": ref}],
                    exactness="GLOBAL_EXEC_VALUE_EXACT",
                    detail={"side_effect_exec_out": f"exec:{erows[idx]['exec_out']}"},
                )
                value_kind = "OLD_EXEC_ALIAS"
                counts["old_exec_alias_instruction_count"] += 1
            elif op == "s_swappc_b64":
                if len(writes) != 2:
                    violations.append(f"swappc_width:{idx}:{len(writes)}")
                relative = int(x.get("address") or 0) + 4
                add_value(
                    vid, "PC_PLUS_4", idx=idx, op=op, width=64,
                    inputs=[], exactness="SOURCE_DOCUMENTED_SYMBOLIC_PC_IDENTITY",
                    detail={
                        "identity": "PROGRAM_CODE_BASE_PLUS_OFFSET",
                        "program_relative_byte_offset": relative,
                        "architectural_expression": "PC_IN + 4",
                        "control_transfer_semantics": "OWNED_BY_CFG_CONTROL_LAYER",
                    },
                )
                value_kind = "PC_PLUS_4"
                counts["pc_plus_4_instruction_count"] += 1
            elif op in {"v_readlane_b32", "v_readfirstlane_b32"}:
                if len(writes) != 1 or len(operands) < 2:
                    violations.append(f"lane_read_shape:{idx}:{op}:{operands!r}:{len(writes)}")
                    continue
                src = operands[1]
                vu = _find_value(vrows[idx].get("vgpr_uses") or [], src)
                if vu is None:
                    violations.append(f"lane_read_missing_vgpr_source:{idx}:{op}:{src}")
                    continue
                vref = f"vgpr:{vu}"
                if op == "v_readlane_b32":
                    if len(operands) != 3:
                        violations.append(f"readlane_operand_count:{idx}:{operands!r}")
                        continue
                    try:
                        lane = int(operands[2], 0)
                    except Exception:
                        violations.append(f"readlane_nonliteral_lane:{idx}:{operands[2]!r}")
                        continue
                    add_value(
                        vid, "VGPR_LANE_SELECT", idx=idx, op=op, width=32,
                        inputs=[{"kind": "VGPR_STATE", "register": src, "node": vref},
                                {"kind": "LITERAL_LANE", "lane": lane}],
                        exactness="GLOBAL_VGPR_IDENTITY_AND_SOURCE_DOCUMENTED_LANE_SELECT",
                        detail={"ignores_exec": True},
                    )
                    value_kind = "VGPR_LANE_SELECT"
                    counts["vgpr_readlane_instruction_count"] += 1
                else:
                    eref = f"exec:{erows[idx]['exec_in']}"
                    add_value(
                        vid, "VGPR_FIRST_ACTIVE_LANE_SELECT", idx=idx, op=op, width=32,
                        inputs=[{"kind": "VGPR_STATE", "register": src, "node": vref},
                                {"kind": "EXEC_LANE_SELECTOR", "node": eref}],
                        exactness="GLOBAL_VGPR_EXEC_IDENTITY_AND_SOURCE_DOCUMENTED_LANE_SELECT",
                        detail={"ignores_exec_as_execution_mask": True, "exec_zero_selects_lane": 0},
                    )
                    value_kind = "VGPR_FIRST_ACTIVE_LANE_SELECT"
                    counts["vgpr_readfirstlane_instruction_count"] += 1
            else:
                violations.append(f"unhandled_cross_state:{idx}:{op}")
                continue
            counts["cross_state_instruction_count"] += 1
            counts["cross_state_component_count"] += len(writes)

        elif cat == "PURE_SCALAR_TRANSFORM":
            md = crows[idx].get("mask_definition") if beh["width_bits"] == 64 else None
            if md is not None:
                ref = f"condition:{md['node']}"
                add_value(
                    vid, "CONDITION_MASK_ALIAS", idx=idx, op=op, width=beh["width_bits"],
                    external_ref=ref, inputs=[{"kind": "CONDITION_MASK", "node": ref}],
                    exactness="GLOBAL_CONDITION_VALUE_EXACT",
                    detail={"value_kind": beh["value_kind"], "mask_key": md.get("key"), "mask_kind": md.get("kind")},
                )
                value_kind = "CONDITION_MASK_ALIAS"
                counts["pure_condition_alias_instruction_count"] += 1
            else:
                srcs = []
                if op == "s_addk_i32":
                    rmw = sr.get("implicit_rmw_uses") or []
                    if len(rmw) != 1:
                        violations.append(f"addk_rmw_source:{idx}:{rmw!r}")
                        continue
                    srcs.append({"kind": "SCALAR_RMW_OLD_DEST", "register": rmw[0]["register"],
                                 "node": f"scalar:{rmw[0]['value']}"})
                for atom in operands[1:]:
                    try:
                        resolved = _scalar_operand(atom, sr, erows[idx])
                    except ValueError as e:
                        violations.append(f"operand_resolution:{idx}:{op}:{e}")
                        resolved = None
                    if resolved is None:
                        continue
                    if resolved["kind"] in {"CONDITION_STATE_REQUIRED", "VGPR_STATE_REQUIRED"}:
                        violations.append(f"unexpected_unaliased_special_source:{idx}:{op}:{atom}:{resolved['kind']}")
                    else:
                        srcs.append(resolved)
                add_value(
                    vid, "SCALAR_ALU_OPERATION", idx=idx, op=op, width=beh["width_bits"],
                    inputs=srcs, exactness="SOURCE_DOCUMENTED_OPERATION_OVER_EXACT_MACHINE_INPUTS",
                    detail={"value_kind": beh["value_kind"], "operands": operands, "source": beh["source"]},
                )
                value_kind = "SCALAR_ALU_OPERATION"
                counts["scalar_alu_instruction_count"] += 1
            counts["pure_scalar_instruction_count"] += 1
            counts["pure_scalar_component_count"] += len(writes)

        else:
            violations.append(f"unknown_category:{idx}:{op}:{cat}")
            continue

        for component, w in enumerate(writes):
            target = w.get("result")
            if not target or target not in (scalar.get("nodes") or {}):
                violations.append(f"missing_scalar_result_node:{idx}:{op}:{target!r}")
                continue
            if target in bound_targets:
                violations.append(f"duplicate_scalar_result_binding:{target}")
                continue
            bound_targets.add(target)
            bindings.append({
                "target_scalar_result": f"scalar:{target}",
                "register": w.get("register"),
                "value": vid,
                "component": component,
                "slice_bits": [component * 32, component * 32 + 31],
                "exactness": values[vid]["exactness"],
            })
        counts["bound_instruction_count"] += 1
        counts["bound_component_count"] += len(writes)
        opcounts[op] += 1
        instruction_rows.append({
            "instruction": idx, "address": x.get("address_hex"), "opcode": op,
            "category": cat, "value": vid, "value_kind": value_kind,
            "scalar_result_components": [w.get("result") for w in writes],
        })

    expected_components = (scalar.get("coverage") or {}).get("sgpr_def_entry_count", 0)
    expected_instructions = (scalar.get("coverage") or {}).get("sgpr_def_instruction_count", 0)
    if counts["bound_component_count"] != expected_components:
        violations.append(f"component_accounting:{counts['bound_component_count']}!={expected_components}")
    if counts["bound_instruction_count"] != expected_instructions:
        violations.append(f"instruction_accounting:{counts['bound_instruction_count']}!={expected_instructions}")
    if len(bound_targets) != expected_components:
        violations.append(f"unique_binding_targets:{len(bound_targets)}!={expected_components}")

    for vid, n in values.items():
        for ref in _all_external_refs(n):
            if not _check_external_ref(ref, scalar, ex, cond, vgpr):
                violations.append(f"missing_external_reference:{vid}:{ref}")

    coverage = {
        "instruction_count": len(ins),
        "scalar_def_instruction_count": expected_instructions,
        "scalar_result_component_count": expected_components,
        "bound_instruction_count": counts["bound_instruction_count"],
        "bound_component_count": counts["bound_component_count"],
        "architectural_nonmemory_instruction_count": (
            counts["pure_scalar_instruction_count"] + counts["cross_state_instruction_count"] +
            counts["condition_alias_instruction_count"]
        ),
        "opaque_memory_instruction_count": counts["opaque_memory_instruction_count"],
        "architectural_nonmemory_component_count": (
            counts["pure_scalar_component_count"] + counts["cross_state_component_count"] +
            counts["condition_alias_component_count"]
        ),
        "opaque_memory_component_count": counts["opaque_memory_component_count"],
        **dict(sorted(counts.items())),
        "value_kind_counts": dict(sorted(kindcounts.items())),
        "opcode_binding_counts": dict(sorted(opcounts.items())),
        "shader_expression_semantic_promotions": 0,
    }
    return {
        "schema": SCHEMA,
        "status": STATUS if not violations else "D1_GCN_SCALAR_VALUE_OVERLAY_WITH_VIOLATIONS",
        "shader": v2.get("shader"),
        "instruction_count": len(ins),
        "coverage": coverage,
        "values": values,
        "bindings": bindings,
        "instructions": instruction_rows,
        "violations": violations,
        "semantic_boundary": {
            "exec_value_identity": "GLOBAL_EXACT_PREREQUISITE",
            "condition_mask_value_identity": "GLOBAL_EXACT_PREREQUISITE",
            "vgpr_lane_state_identity": "GLOBAL_EXACT_PREREQUISITE",
            "physical_sgpr_m0_ssa": "GLOBAL_EXACT_PREREQUISITE",
            "nonmemory_scalar_architectural_result_values": "EXACT" if not violations else "NOT_PROMOTED",
            "scalar_memory_result_values": "OPAQUE_RESOURCE_ADDRESS_WITHHELD",
            "expression_dag_binding": "SCALAR_RESULT_SIDE_EXACT" if not violations else "WITHHELD",
            "shader_expression_semantics": "WITHHELD",
            "shader_expression_semantic_promotions": 0,
        },
        "policy": (
            "Every physical scalar SSA result component is bound to one architectural machine value. "
            "Existing EXEC, condition-mask and lane-aware VGPR identities are reused rather than duplicated. "
            "SMEM results remain opaque; resource descriptors, addresses, shader expressions, material roles "
            "and game semantics are not inferred."
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
    print(json.dumps({"status": out["status"], "coverage": out["coverage"], "violations": out["violations"][:20]}, indent=2, sort_keys=True))
    return 0 if not out["violations"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
