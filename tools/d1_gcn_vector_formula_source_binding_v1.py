#!/usr/bin/env python3
"""Bind D1 GFX7 vector-formula source slots to the existing VGPR and SGPR SSA identities.

The preceding formula/lane layer already proves each formula result is the existing active-lane
VGPR result and each physical destination is the existing write node.  This layer closes the
other side of the operation: every explicit formula source is attached to its exact architectural
state at that instruction.  VGPR and literal sources are verified in place; SGPR sources replace
the temporary instruction-local NON_VGPR leaf with an explicit cross-graph reference to the
already exact physical SGPR/M0 SSA.  No second register graph is created.

This is still architectural value provenance, not shader/material interpretation.  Scalar-memory
values remain opaque in the scalar value overlay, and resource/LDS/interpolation boundaries are
unchanged.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
from collections import Counter
from pathlib import Path

import d1_gcn_vector_formula_lane_binding_v1 as formula
import d1_gcn_vector_formula_semantics_v1 as sem
import d1_gcn_sgpr_ssa_v1 as scalar_ssa

INPUT_STATUS = "D1_GCN_STRUCTURAL_IR_COMPLETE"
FORMULA_STATUS = "D1_GCN_VECTOR_FORMULA_LANE_BINDING_EXACT"
SCALAR_STATUS = "D1_GCN_SGPR_SSA_EXACT"
SCHEMA = "d1_gcn_vector_formula_source_binding/v1"
STATUS = "D1_GCN_VECTOR_FORMULA_SOURCE_BINDING_EXACT"
VREG_RE = re.compile(r"^v(\d+)$")
SREG_RE = re.compile(r"^s(\d+)$")


def _find_scalar_use(row: dict, reg: str) -> list[str]:
    vals = sorted({
        u.get("value") for u in (row.get("scalar_uses") or [])
        if u.get("register") == reg and u.get("value") is not None
    })
    return vals


def _bridge(nodes: dict[str, dict], *, idx: int, slot: int, op: str, reg: str,
            scalar_node: str, scalar_kind: str) -> str:
    nid = f"formula:i{idx}:src{slot}:scalar_state"
    n = {
        "id": nid,
        "kind": "EXACT_SCALAR_SSA_STATE_REFERENCE",
        "inputs": [],
        "instruction": idx,
        "opcode": op,
        "exactness": "GLOBAL_SCALAR_SSA_IDENTITY_EXACT",
        "detail": {
            "register": reg,
            "external_graph": "d1_gcn_sgpr_ssa/v1",
            "external_node": scalar_node,
            "external_ref": f"scalar:{scalar_node}",
            "external_node_kind": scalar_kind,
        },
    }
    old = nodes.get(nid)
    if old is not None and old != n:
        raise ValueError(f"scalar bridge identity collision:{nid}")
    nodes[nid] = n
    return nid


def analyze(v2: dict) -> dict:
    if v2.get("status") != INPUT_STATUS:
        raise ValueError(f"input status {v2.get('status')!r}")

    out = formula.analyze(v2)
    if out.get("status") != FORMULA_STATUS or out.get("violations"):
        raise ValueError(
            f"formula/lane prerequisite not exact:{out.get('status')}:{(out.get('violations') or [])[:3]}"
        )
    scalar = scalar_ssa.analyze(v2)
    if scalar.get("status") != SCALAR_STATUS or scalar.get("violations"):
        raise ValueError(
            f"scalar SSA prerequisite not exact:{scalar.get('status')}:{(scalar.get('violations') or [])[:3]}"
        )

    ins = v2.get("instructions") or []
    vrows = out.get("instructions") or []
    srows = scalar.get("instructions") or []
    nodes = out.get("nodes") or {}
    snodes = scalar.get("nodes") or {}
    if not (len(ins) == len(vrows) == len(srows)):
        raise ValueError("formula/scalar instruction roster mismatch")

    violations: list[str] = []
    counts = Counter()
    scalar_state_kinds = Counter()
    opcode_source_slots = Counter()
    seen_raw: set[str] = set()
    source_bindings: list[dict] = []

    for idx, x in enumerate(ins):
        if x.get("index") != idx:
            violations.append(f"instruction_index:{idx}:{x.get('index')}")
            continue
        op = x.get("opcode")
        if op not in sem.PENDING:
            continue
        ent = sem.FORMULAS[op]
        operands = x.get("operands") or []
        nsrc = ent["explicit_source_count"]
        if len(operands) != 1 + nsrc:
            violations.append(f"operand_count:{idx}:{op}:{len(operands)}!={1+nsrc}")
            continue
        counts["formula_instruction_count"] += 1
        counts["expected_source_slot_count"] += nsrc
        opcode_source_slots[op] += nsrc

        for slot, token in enumerate(operands[1:]):
            try:
                parsed = formula._parse_source_token(token)
            except Exception as e:
                violations.append(f"source_parse:{idx}:src{slot}:{type(e).__name__}:{e}")
                continue
            atom = parsed["atom"]
            raw_id = f"formula:i{idx}:src{slot}:raw"
            raw = nodes.get(raw_id)
            if raw is None:
                violations.append(f"missing_formula_raw_source:{idx}:src{slot}:{atom}")
                continue
            if raw_id in seen_raw:
                violations.append(f"duplicate_formula_raw_source:{raw_id}")
                continue
            seen_raw.add(raw_id)
            if raw.get("kind") != "ARCHITECTURAL_SOURCE_OPERAND_SLOT":
                violations.append(f"raw_kind:{raw_id}:{raw.get('kind')}")
            if raw.get("instruction") != idx or raw.get("opcode") != op:
                violations.append(f"raw_metadata:{raw_id}:{raw.get('instruction')}:{raw.get('opcode')}")
            d = raw.get("detail") or {}
            if d.get("slot") != slot or d.get("atom") != atom or d.get("token") != parsed["token"]:
                violations.append(f"raw_detail:{raw_id}:{d!r}")
            rin = raw.get("inputs") or []
            if len(rin) != 1:
                violations.append(f"raw_input_arity:{raw_id}:{rin!r}")
                continue

            binding = {
                "instruction": idx,
                "opcode": op,
                "slot": slot,
                "token": parsed["token"],
                "atom": atom,
                "raw_node": raw_id,
            }

            if VREG_RE.fullmatch(atom):
                vals = sorted({
                    u.get("value") for u in (vrows[idx].get("vgpr_uses") or [])
                    if u.get("register") == atom and u.get("value") is not None
                })
                if len(vals) != 1:
                    violations.append(f"vgpr_state_resolution:{idx}:src{slot}:{atom}:{vals}")
                    continue
                expected = vals[0]
                if expected not in nodes:
                    violations.append(f"vgpr_state_missing:{idx}:src{slot}:{atom}:{expected}")
                    continue
                if rin[0] != expected:
                    violations.append(f"vgpr_raw_edge:{idx}:src{slot}:{rin[0]}!={expected}")
                    continue
                binding.update({"kind": "VGPR_STATE", "state_node": expected})
                counts["vgpr_source_slot_count"] += 1
                counts["exact_source_slot_count"] += 1

            elif SREG_RE.fullmatch(atom):
                vals = _find_scalar_use(srows[idx], atom)
                if len(vals) != 1:
                    violations.append(f"sgpr_state_resolution:{idx}:src{slot}:{atom}:{vals}")
                    continue
                sref = vals[0]
                sn = snodes.get(sref)
                if sn is None:
                    violations.append(f"sgpr_state_missing:{idx}:src{slot}:{atom}:{sref}")
                    continue
                old_ref = rin[0]
                old_node = nodes.get(old_ref)
                if not old_node or old_node.get("kind") != "NON_VGPR_SOURCE_AT_INSTRUCTION":
                    violations.append(f"sgpr_expected_placeholder:{idx}:src{slot}:{atom}:{old_ref}:{old_node}")
                    continue
                if old_node.get("instruction") != idx or old_node.get("detail") != atom:
                    violations.append(f"sgpr_placeholder_identity:{idx}:src{slot}:{atom}:{old_node}")
                    continue
                bridge = _bridge(
                    nodes, idx=idx, slot=slot, op=op, reg=atom,
                    scalar_node=sref, scalar_kind=sn.get("kind", "UNKNOWN"),
                )
                raw["inputs"] = [bridge]
                binding.update({
                    "kind": "SGPR_STATE",
                    "state_node": sref,
                    "bridge_node": bridge,
                    "replaced_instruction_local_placeholder": old_ref,
                    "scalar_state_kind": sn.get("kind"),
                })
                counts["sgpr_source_slot_count"] += 1
                counts["sgpr_placeholder_replacement_count"] += 1
                counts["exact_source_slot_count"] += 1
                scalar_state_kinds[sn.get("kind", "UNKNOWN")] += 1

            elif formula._is_literal(atom):
                lit = rin[0]
                ln = nodes.get(lit)
                if not ln or ln.get("kind") != "ISA_LITERAL_32":
                    violations.append(f"literal_source_identity:{idx}:src{slot}:{atom}:{lit}:{ln}")
                    continue
                if (ln.get("detail") or {}).get("token") != atom:
                    violations.append(f"literal_token:{idx}:src{slot}:{atom}:{ln.get('detail')}")
                    continue
                binding.update({"kind": "ISA_LITERAL_32", "state_node": lit})
                counts["literal_source_slot_count"] += 1
                counts["exact_source_slot_count"] += 1

            else:
                violations.append(f"unregistered_source_domain:{idx}:src{slot}:{atom!r}")
                continue

            source_bindings.append(binding)

    if counts["exact_source_slot_count"] != counts["expected_source_slot_count"]:
        violations.append(
            f"global_source_accounting:{counts['exact_source_slot_count']}!={counts['expected_source_slot_count']}"
        )
    if len(seen_raw) != counts["expected_source_slot_count"]:
        violations.append(f"raw_node_accounting:{len(seen_raw)}!={counts['expected_source_slot_count']}")
    if len(source_bindings) != counts["expected_source_slot_count"]:
        violations.append(f"binding_accounting:{len(source_bindings)}!={counts['expected_source_slot_count']}")

    # Formula source slots may no longer depend on the temporary SGPR leaf abstraction.
    leaked = []
    for b in source_bindings:
        raw = nodes[b["raw_node"]]
        for ref in raw.get("inputs") or []:
            n = nodes.get(ref)
            if n and n.get("kind") == "NON_VGPR_SOURCE_AT_INSTRUCTION":
                leaked.append((b["raw_node"], ref))
    if leaked:
        violations.extend(f"formula_source_placeholder_leak:{a}->{b}" for a, b in leaked[:50])

    counts["formula_source_placeholder_leak_count"] = len(leaked)
    coverage = {
        "formula_instruction_count": counts["formula_instruction_count"],
        "expected_source_slot_count": counts["expected_source_slot_count"],
        "exact_source_slot_count": counts["exact_source_slot_count"],
        "vgpr_source_slot_count": counts["vgpr_source_slot_count"],
        "sgpr_source_slot_count": counts["sgpr_source_slot_count"],
        "literal_source_slot_count": counts["literal_source_slot_count"],
        "sgpr_placeholder_replacement_count": counts["sgpr_placeholder_replacement_count"],
        "formula_source_placeholder_leak_count": counts["formula_source_placeholder_leak_count"],
        "scalar_state_kind_counts": dict(sorted(scalar_state_kinds.items())),
        "opcode_source_slot_counts": dict(sorted(opcode_source_slots.items())),
        "integrated_vector_node_count": len(nodes),
        "scalar_ssa_node_count": scalar.get("node_count", len(snodes)),
        "shader_expression_semantic_promotions": 0,
    }

    out["schema"] = SCHEMA
    out["status"] = STATUS if not violations else "D1_GCN_VECTOR_FORMULA_SOURCE_BINDING_WITH_VIOLATIONS"
    out["formula_lane_binding_prerequisite"] = {
        "schema": formula.SCHEMA,
        "status": FORMULA_STATUS,
    }
    out["scalar_ssa_prerequisite"] = {
        "schema": scalar.get("schema"),
        "status": scalar.get("status"),
        "node_count": scalar.get("node_count"),
        "coverage": copy.deepcopy(scalar.get("coverage") or {}),
    }
    out["source_binding_coverage"] = coverage
    out["formula_source_bindings"] = source_bindings
    out["violations"] = violations
    out["semantic_boundary"] = {
        "formula_result_to_lane_candidate_binding": "GLOBAL_EXACT_PREREQUISITE",
        "formula_result_to_physical_write_binding": "GLOBAL_EXACT_PREREQUISITE",
        "vgpr_formula_source_state_identity": "EXACT" if not violations else "WITHHELD",
        "sgpr_formula_source_state_identity": "EXACT_CROSS_GRAPH_REFERENCE" if not violations else "WITHHELD",
        "literal_formula_source_identity": "EXACT" if not violations else "WITHHELD",
        "scalar_architectural_value_overlay": "EXISTING_DOWNSTREAM_OF_SCALAR_SSA",
        "scalar_memory_values": "OPAQUE_RESOURCE_ADDRESS_WITHHELD",
        "resource_lds_interpolation_values": "UNCHANGED_OPAQUE_BOUNDARIES",
        "floating_numeric_replay": "WITHHELD_MODE_AND_OPCODE_SPECIFIC_HARDWARE_BEHAVIOR",
        "vop3_clamp_numeric_range": "WITHHELD_AMD_REV1_3_INTERNAL_SOURCE_CONFLICT",
        "shader_expression_semantics": "WITHHELD",
        "material_semantics": "WITHHELD",
        "shader_expression_semantic_promotions": 0,
    }
    out["policy"] = (
        "Every source slot of every source-closed vector formula is attached to the exact architectural register "
        "state or encoded literal at that instruction. VGPR identities remain the existing lane SSA; SGPR identities "
        "are explicit references into the existing physical scalar SSA and replace only the old instruction-local "
        "placeholder leaves. No shader expression, resource value, texture role, or material meaning is inferred."
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
    print(json.dumps({
        "status": out["status"],
        "coverage": out["source_binding_coverage"],
        "violations": out["violations"][:50],
    }, indent=2, sort_keys=True))
    return 0 if not out["violations"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
