#!/usr/bin/env python3
"""Bind LocalShader typed-buffer results to exact API10 resource-read identities.

This refines the earlier opaque TBUFFER result boundary only after the exact descriptor
usage gate has proven that every descriptor is untouched program-entry ImmConstBuffer
API slot 10 state. Runtime buffer contents and engine-level meaning remain opaque.
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

SCHEMA = "d1_gcn_localshader_tbuffer_value_binding/v1"
STATUS = "D1_GCN_LOCALSHADER_TBUFFER_VALUE_BINDING_EXACT"
USAGE_STATUS = "D1_GCN_LOCALSHADER_TBUFFER_USAGE_BINDING_EXACT"
SPECIAL_STATUS = "D1_GCN_VECTOR_SPECIAL_VALUE_BINDING_EXACT"
EXPECTED_PROGRAMS = 65
EXPECTED_TBUFFER_PROGRAMS = 39
EXPECTED_TBUFFER_INSTRUCTIONS = 385
EXPECTED_COMPONENTS = 1540
EXPECTED_WINDOWS = {"s[12:15]": 260, "s[8:11]": 125}
EXPECTED_HIST = {3: 1, 6: 1, 8: 17, 12: 20}


def build(usage_path: Path, bound_dir: Path) -> dict:
    usage = json.loads(usage_path.read_text())
    violations: list[str] = []
    if usage.get("status") != USAGE_STATUS or usage.get("violations"):
        raise ValueError(
            f"usage prerequisite:{usage.get('status')}:{usage.get('violations')}"
        )
    urows = {
        (r["gcn_sha256"].lower(), int(r["instruction"])): r
        for r in usage["bindings"]
    }
    if len(urows) != EXPECTED_TBUFFER_INSTRUCTIONS:
        violations.append(
            f"usage_binding_count:{len(urows)}!={EXPECTED_TBUFFER_INSTRUCTIONS}"
        )

    paths = sorted(bound_dir.glob("*.json"))
    if len(paths) != EXPECTED_PROGRAMS:
        violations.append(f"bound_program_count:{len(paths)}!={EXPECTED_PROGRAMS}")

    bindings: list[dict] = []
    program_rows: list[dict] = []
    windows = collections.Counter()
    hist = collections.Counter()
    component_count = 0
    tprograms = 0
    vaddr_kind = collections.Counter()
    resource_key = collections.Counter()
    all_special_tbuffers = 0

    for p in paths:
        sha = p.stem.lower()
        d = json.loads(p.read_text())
        if d.get("status") != SPECIAL_STATUS or d.get("violations"):
            violations.append(
                f"special_status:{sha}:{d.get('status')}:"
                f"{(d.get('violations') or [])[:3]}"
            )
            continue
        nodes = d.get("nodes") or {}
        specials = [
            x
            for x in (d.get("special_value_bindings") or [])
            if x.get("opcode") == "tbuffer_load_format_xyzw"
        ]
        all_special_tbuffers += len(specials)
        local: list[dict] = []

        for s in specials:
            idx = int(s["instruction"])
            key = (sha, idx)
            u = urows.get(key)
            if u is None:
                violations.append(f"missing_usage_binding:{sha}:{idx}")
                continue
            slot = u.get("usage_slot") or {}
            if (
                slot.get("usage_name") != "ImmConstBuffer"
                or int(slot.get("api_slot", -1)) != 10
            ):
                violations.append(f"usage_identity:{sha}:{idx}:{slot}")
                continue
            if u.get("reaching_state") != "PROGRAM_ENTRY_USER_DATA":
                violations.append(
                    f"usage_reaching_state:{sha}:{idx}:{u.get('reaching_state')}"
                )
                continue

            opid = f"special:i{idx}:operation"
            op = nodes.get(opid)
            if not op or op.get("kind") != "GFX7_TYPED_BUFFER_LOAD_XYZW":
                violations.append(f"missing_special_operation:{sha}:{idx}:{op}")
                continue
            det = op.get("detail") or {}
            expected = {
                "addr64": False,
                "component_count": 4,
                "dfmt": "32_32_32_32",
                "glc": False,
                "idxen": True,
                "nfmt": "float",
                "offen": False,
                "offset12": 0,
                "slc": False,
                "soffset_token": "0",
                "srsrc_register_range": u["descriptor_window"],
            }
            for k, v in expected.items():
                if det.get(k) != v:
                    violations.append(
                        f"operation_control:{sha}:{idx}:{k}:{det.get(k)!r}!={v!r}"
                    )

            inputs = op.get("inputs") or []
            if len(inputs) != 6:
                violations.append(
                    f"operation_input_count:{sha}:{idx}:{len(inputs)}"
                )
                continue
            vaddr = inputs[0]
            vn = nodes.get(vaddr)
            if vn is None:
                violations.append(f"vaddr_node_missing:{sha}:{idx}:{vaddr}")
                continue
            if not (
                vaddr.startswith("write:")
                or vaddr.startswith("external:")
                or vaddr.startswith("phi:")
            ):
                violations.append(f"vaddr_identity_shape:{sha}:{idx}:{vaddr}")
            vaddr_kind[vn.get("kind", "UNKNOWN")] += 1

            comps = []
            for c in range(4):
                cid = f"special:i{idx}:component:{c}"
                cn = nodes.get(cid)
                if not cn or cn.get("kind") != "GFX7_TYPED_BUFFER_RESULT_COMPONENT_OPAQUE":
                    violations.append(f"component_node:{sha}:{idx}:{c}:{cn}")
                    continue
                if (cn.get("inputs") or []) != [opid]:
                    violations.append(
                        f"component_edge:{sha}:{idx}:{c}:{cn.get('inputs')}"
                    )
                comps.append(
                    {
                        "component": c,
                        "existing_special_node": cid,
                        "resource_value_node": f"api10_tbuffer:{sha}:i{idx}:c{c}",
                        "value_expression": (
                            f"ImmConstBuffer[api=10][index={vaddr}]."
                            f"{('x', 'y', 'z', 'w')[c]}"
                        ),
                    }
                )
                component_count += 1

            windows[u["descriptor_window"]] += 1
            resource_key["ImmConstBuffer:10"] += 1
            rec = {
                "gcn_sha256": sha,
                "instruction": idx,
                "address": s.get("address"),
                "resource_identity": {
                    "usage_name": "ImmConstBuffer",
                    "api_slot": 10,
                    "descriptor_window": u["descriptor_window"],
                    "reaching_state": "PROGRAM_ENTRY_USER_DATA",
                },
                "addressing": {
                    "idxen": True,
                    "offen": False,
                    "addr64": False,
                    "offset12": 0,
                    "soffset_u32": 0,
                    "vaddr_state_node": vaddr,
                },
                "format": {
                    "dfmt": "32_32_32_32",
                    "nfmt": "float",
                    "result_components": 4,
                },
                "operation": "GFX7_TYPED_BUFFER_READ_XYZW_FROM_BOUND_IMM_CONST_BUFFER",
                "components": comps,
                "numeric_value_status": "RUNTIME_BUFFER_CONTENT_OPAQUE",
            }
            bindings.append(rec)
            local.append(rec)

        if local:
            tprograms += 1
            hist[len(local)] += 1
            program_rows.append(
                {
                    "gcn_sha256": sha,
                    "tbuffer_instruction_count": len(local),
                    "descriptor_window": local[0]["resource_identity"]["descriptor_window"],
                }
            )

    bkeys = set(urows)
    gotkeys = {(r["gcn_sha256"], r["instruction"]) for r in bindings}
    if gotkeys != bkeys:
        violations.append(
            f"binding_roster_delta:missing={len(bkeys-gotkeys)}:extra={len(gotkeys-bkeys)}"
        )
    if all_special_tbuffers != EXPECTED_TBUFFER_INSTRUCTIONS:
        violations.append(
            f"special_tbuffer_count:{all_special_tbuffers}!={EXPECTED_TBUFFER_INSTRUCTIONS}"
        )
    if len(bindings) != EXPECTED_TBUFFER_INSTRUCTIONS:
        violations.append(
            f"binding_count:{len(bindings)}!={EXPECTED_TBUFFER_INSTRUCTIONS}"
        )
    if component_count != EXPECTED_COMPONENTS:
        violations.append(f"component_count:{component_count}!={EXPECTED_COMPONENTS}")
    if tprograms != EXPECTED_TBUFFER_PROGRAMS:
        violations.append(
            f"tbuffer_programs:{tprograms}!={EXPECTED_TBUFFER_PROGRAMS}"
        )
    if dict(windows) != EXPECTED_WINDOWS:
        violations.append(f"windows:{dict(windows)}!={EXPECTED_WINDOWS}")
    if dict(hist) != EXPECTED_HIST:
        violations.append(f"hist:{dict(hist)}!={EXPECTED_HIST}")

    coverage = {
        "exact_bound_program_count": len(paths),
        "tbuffer_program_count": tprograms,
        "tbuffer_instruction_count": len(bindings),
        "tbuffer_result_component_count": component_count,
        "resource_identity_counts": dict(resource_key),
        "descriptor_window_counts": dict(sorted(windows.items())),
        "per_program_instruction_histogram": {
            str(k): v for k, v in sorted(hist.items())
        },
        "vaddr_reaching_node_kind_counts": dict(sorted(vaddr_kind.items())),
        "resource_read_expression_component_count": component_count,
        "runtime_buffer_content_promotions": 0,
        "shader_expression_semantic_promotions": 0,
    }
    return {
        "schema": SCHEMA,
        "status": (
            STATUS
            if not violations
            else "D1_GCN_LOCALSHADER_TBUFFER_VALUE_BINDING_WITH_VIOLATIONS"
        ),
        "coverage": coverage,
        "programs": program_rows,
        "bindings": bindings,
        "violations": violations,
        "semantic_boundary": {
            "tbuffer_resource_identity": "EXACT_IMM_CONST_BUFFER_API_SLOT_10",
            "tbuffer_descriptor_state": "EXACT_PROGRAM_ENTRY_USER_DATA",
            "tbuffer_vaddr_state": "EXACT_EXISTING_LANE_SSA_REFERENCE",
            "tbuffer_architectural_read_expression": "EXACT_GFX7_TYPED_FLOAT4_READ_IDENTITY",
            "tbuffer_runtime_buffer_contents": "OPAQUE",
            "api_slot_10_runtime_binding_owner": "NEXT_GATE",
            "semantic_record_name": "WITHHELD",
            "shader_expression_semantics": "WITHHELD",
            "shader_expression_semantic_promotions": 0,
        },
        "policy": (
            "Promote only the architectural resource-read expression: exact ImmConstBuffer "
            "API slot 10 descriptor identity, exact reaching VGPR index state, exact "
            "idxen/offen/offset/format controls, and exact XYZW result-component identity. "
            "Runtime buffer contents, engine owner, transform/bone/material names, and "
            "shader-level meaning remain withheld."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--usage-binding", type=Path, required=True)
    ap.add_argument("--bound-dir", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()
    d = build(a.usage_binding, a.bound_dir)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(d, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "status": d["status"],
                "coverage": d["coverage"],
                "violations": d["violations"][:30],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if not d["violations"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
