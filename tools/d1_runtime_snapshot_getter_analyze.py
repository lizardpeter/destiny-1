#!/usr/bin/env python3
"""Classify exact D1 runtime-snapshot getter functions from derived code windows.

Inputs are the exact-build outputs of:
  d1_executable_call_xrefs.py
  d1_executable_code_windows.py

The classifier is deliberately structural. It recognizes only small common getter
shapes such as returning a RIP-relative address or loading a RIP-relative pointer.
It does not assign renderer semantics or field names.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def xref_map(doc: dict) -> dict[int, dict]:
    return {int(row["target_va"]): row for row in doc.get("targets", [])}


def first_return_window(doc: dict) -> dict[int, dict]:
    return {int(row["start_va"]): row for row in doc.get("windows", [])}


def rip_targets(insn: dict) -> list[int]:
    out = []
    for op in insn.get("operands", []):
        if op.get("type") == "mem" and "rip_target" in op:
            out.append(int(op["rip_target"]))
    return out


def classify(window: dict) -> dict:
    ins = window.get("instructions", [])
    body = [x for x in ins if x.get("mnemonic") not in {"nop", "endbr64"}]
    # Keep only the first basic straight-line getter-sized prefix.
    prefix = []
    for row in body[:16]:
        prefix.append(row)
        if row.get("mnemonic", "").startswith("ret"):
            break

    result = {
        "instruction_count_to_first_ret": len(prefix),
        "first_instructions": [
            f"{x.get('address_hex')} {x.get('mnemonic')} {x.get('op_str')}"
            for x in prefix
        ],
        "shape": "other",
        "returned_storage_target": None,
        "returned_storage_target_hex": None,
    }

    # Typical singleton getter:
    #   lea rax,[rip+disp]
    #   ret
    # or:
    #   mov rax,qword ptr [rip+disp]
    #   ret
    for row in prefix:
        mnemonic = row.get("mnemonic", "")
        op_str = row.get("op_str", "")
        targets = rip_targets(row)
        if not targets:
            continue
        if mnemonic == "lea" and op_str.startswith("rax,"):
            result["shape"] = "returns_rip_relative_address"
            result["returned_storage_target"] = targets[0]
            result["returned_storage_target_hex"] = hex(targets[0])
            break
        if mnemonic == "mov" and op_str.startswith("rax,"):
            result["shape"] = "loads_rip_relative_pointer"
            result["returned_storage_target"] = targets[0]
            result["returned_storage_target_hex"] = hex(targets[0])
            break

    if result["shape"] == "other":
        calls = [
            int(edge["target_va"])
            for edge in window.get("direct_calls", [])
        ]
        if calls:
            result["direct_call_targets"] = [hex(x) for x in calls]

    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--xrefs", type=Path, required=True)
    ap.add_argument("--windows", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    xdoc = load(a.xrefs)
    wdoc = load(a.windows)
    if xdoc.get("executable_sha256") != wdoc.get("executable_sha256"):
        raise ValueError("xref/window executable SHA mismatch")

    xrefs = xref_map(xdoc)
    windows = first_return_window(wdoc)
    targets = sorted(set(xrefs) | set(windows))
    rows = []
    for target in targets:
        xr = xrefs.get(target, {})
        win = windows.get(target)
        analysis = classify(win) if win else {
            "shape": "window_missing",
            "returned_storage_target": None,
            "returned_storage_target_hex": None,
        }
        rows.append({
            "target_va": target,
            "target_va_hex": hex(target),
            "direct_call_xref_count": int(xr.get("direct_call_xref_count", 0)),
            "callsites": [
                x.get("callsite_va_hex")
                for x in xr.get("xrefs", [])
            ],
            **analysis,
        })

    storage_groups = {}
    for row in rows:
        key = row.get("returned_storage_target_hex")
        if key is None:
            continue
        storage_groups.setdefault(key, []).append(row["target_va_hex"])

    report = {
        "schema": "d1_runtime_snapshot_getter_analysis/v1",
        "status": "EXACT_BUILD_STRUCTURAL_GETTER_CLASSIFICATION",
        "executable_sha256": xdoc.get("executable_sha256"),
        "targets": rows,
        "returned_storage_groups": storage_groups,
        "policy": (
            "Getter shapes, direct-call xrefs and RIP-relative targets are exact "
            "build evidence. A returned storage address is not assigned Frame, "
            "DeferredLight or any other renderer semantic without independent "
            "consumer/producer dataflow."
        ),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "status": report["status"],
        "targets": [
            {
                "target": x["target_va_hex"],
                "xrefs": x["direct_call_xref_count"],
                "shape": x["shape"],
                "storage": x.get("returned_storage_target_hex"),
            }
            for x in rows
        ],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
