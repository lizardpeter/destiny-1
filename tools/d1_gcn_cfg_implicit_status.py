#!/usr/bin/env python3
"""Augment structural D1 GCN IR with source-proven implicit status destinations.

The structural parser intentionally derives most defs/uses from textual operands. Some
GCN scalar instructions also write status registers that are not printed as operands.
This adapter adds only implicit status destinations whose behavior has already been
source-proven by the pinned control-semantics contract. It does not infer new shader
intent or ordinary VGPR SSA.
"""
from __future__ import annotations
import argparse, copy, json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ir", type=Path, required=True)
    ap.add_argument("--control-semantics", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    ir = json.load(open(a.ir))
    cs = json.load(open(a.control_semantics))
    violations = []
    out = {}
    try:
        assert ir.get("status") == "D1_GCN_STRUCTURAL_IR_COMPLETE"
        assert int(ir.get("schema_version", 0)) >= 2
        assert cs.get("status") == "D1_GCN_CONTROL_SEMANTICS_SOURCE_PROVEN"
        assert not cs.get("violations")
        semantics = cs["semantics"]

        # Only operations whose pinned source contract explicitly states SCC behavior
        # are eligible. This is deliberately narrower than the full GCN ISA.
        exact_scc_ops = {
            op for op, q in semantics.items()
            if isinstance(q, dict) and "scc" in q
        }
        required = {"s_and_b64", "s_andn2_b64", "s_and_saveexec_b64"}
        assert required.issubset(exact_scc_ops), (required, exact_scc_ops)

        out = copy.deepcopy(ir)
        implicit = []
        for x in out["instructions"]:
            op = x["opcode"]
            if op not in exact_scc_ops:
                continue
            before = list(x.get("defs", []))
            if "scc" not in before:
                x["defs"] = before + ["scc"]
                x["implicit_defs"] = sorted(set(x.get("implicit_defs", []) + ["scc"]))
                implicit.append({
                    "instruction": int(x["index"]),
                    "opcode": op,
                    "implicit_defs": ["scc"],
                    "source_semantic": semantics[op],
                })

        out["schema_version"] = max(3, int(out.get("schema_version", 0)))
        out["implicit_status_destinations"] = implicit
        out.setdefault("semantic_boundary", {})[
            "register_def_use_classification"
        ] = "STRUCTURAL_WITH_SOURCE_PROVEN_IMPLICIT_STATUS_DESTINATIONS"
        out["semantic_boundary"]["implicit_status_scope"] = sorted(exact_scc_ops)
        out["policy"] = (
            "Textual structural IR is preserved. Implicit SCC destinations are added "
            "only for operations whose SCC behavior is explicitly present in the pinned "
            "source-semantics contract. Divergent VGPR SSA remains withheld."
        )

        # Target regression: the export-kill mask update must now be the exact SCC
        # producer consumed by the following SCC0 branch.
        if out.get("shader") == "808EE505" and len(out.get("instructions", [])) > 338:
            k = out["instructions"][337]
            b = out["instructions"][338]
            assert k["opcode"] == "s_andn2_b64" and "scc" in k["defs"], k
            assert b["opcode"] == "s_cbranch_scc0" and "scc" in b["uses"], b
    except Exception as exc:
        violations.append(repr(exc))

    if violations:
        result = {
            "schema_version": 1,
            "status": "D1_GCN_STRUCTURAL_IR_IMPLICIT_STATUS_PARTIAL",
            "violations": violations,
        }
        rc = 2
    else:
        result = out
        result["status"] = "D1_GCN_STRUCTURAL_IR_COMPLETE"
        result["implicit_status_violations"] = []
        rc = 0

    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({
        "status": result.get("status"),
        "schema_version": result.get("schema_version"),
        "implicit_status_destination_count": len(result.get("implicit_status_destinations", [])),
        "violations": violations,
    }, indent=2))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
