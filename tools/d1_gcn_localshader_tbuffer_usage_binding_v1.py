#!/usr/bin/env python3
"""Bind exact D1 LocalShader TBUFFER descriptors to OrbShdr input-usage slots.

This is a resource-identity frontier, not a buffer-content decoder.  A typed-buffer
instruction is promoted only when its four-SGPR descriptor window is still the untouched
program-entry user-data state and the exact native OrbShdr InputUsageSlot table identifies
that same start register as ImmConstBuffer API slot 10.  Register numbers alone are never
interpreted as resource slots.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
from pathlib import Path

from d1_ps4_shader_binary_probe import find_footer, parse_binary_info, parse_usage

SCHEMA = "d1_gcn_localshader_tbuffer_usage_binding/v1"
STATUS = "D1_GCN_LOCALSHADER_TBUFFER_USAGE_BINDING_EXACT"
CORPUS_SCHEMA = "d1_gcn_material_localshader_corpus/v1"
CORPUS_STATUS = "D1_GCN_MATERIAL_LOCALSHADER_CORPUS_EXACT"
IR_STATUS = "D1_GCN_STRUCTURAL_IR_COMPLETE"
ACCOUNT_STATUS = "D1_GCN_STRUCTURAL_PARSE_ACCOUNTING_EXACT"

EXPECTED_PROGRAMS = 65
EXPECTED_WRAPPERS = 177
EXPECTED_INSTRUCTIONS = 10858
EXPECTED_TBUFFER_PROGRAMS = 39
EXPECTED_TBUFFER_WRAPPERS = 56
EXPECTED_TBUFFER_MATERIAL_OCCURRENCES = 3386
EXPECTED_TBUFFER_INSTRUCTIONS = 385
EXPECTED_TBUFFER_COMPONENTS = 1540
EXPECTED_DESCRIPTOR_WINDOWS = {"s[12:15]": 260, "s[8:11]": 125}
EXPECTED_DESCRIPTOR_PROGRAM_WINDOWS = {"s[12:15]": 26, "s[8:11]": 13}
EXPECTED_PER_PROGRAM_HIST = {3: 1, 6: 1, 8: 17, 12: 20}

PAIR_RE = re.compile(r"^s\[(\d+):(\d+)\]$")
SREG_RE = re.compile(r"^s(\d+)$")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def pair_regs(text: str) -> list[str]:
    m = PAIR_RE.fullmatch(text or "")
    if not m:
        return []
    a, b = map(int, m.groups())
    return [f"s{i}" for i in range(a, b + 1)]


def usage_signature(slots: list[dict]) -> tuple:
    return tuple(
        (int(x["usage_type"]), int(x["api_slot"]), int(x["start_register"]), x["raw_hex"])
        for x in slots
    )


def build(corpus_path: Path, binary_root: Path, ir_dir: Path) -> dict:
    violations: list[str] = []
    src = json.loads(corpus_path.read_text())
    if (
        src.get("schema") != CORPUS_SCHEMA
        or src.get("status") != CORPUS_STATUS
        or src.get("violations")
    ):
        raise ValueError(
            f"LocalShader corpus not exact:{src.get('schema')}:{src.get('status')}:"
            f"{len(src.get('violations') or [])}"
        )

    headers = src.get("headers") or []
    programs = src.get("unique_gcn_programs") or []
    if len(headers) != EXPECTED_WRAPPERS:
        violations.append(f"wrapper_count:{len(headers)}!={EXPECTED_WRAPPERS}")
    if len(programs) != EXPECTED_PROGRAMS:
        violations.append(f"program_count:{len(programs)}!={EXPECTED_PROGRAMS}")

    program_roster = {str(x["gcn_sha256"]).lower() for x in programs}
    by_sha: dict[str, list[dict]] = collections.defaultdict(list)
    signature_by_sha: dict[str, set[tuple]] = collections.defaultdict(set)
    slots_by_sha: dict[str, list[dict]] = {}
    all_layouts = collections.Counter()

    for h in headers:
        sha = str(h["gcn_sha256"]).lower()
        p = binary_root / h["native_file"]
        if not p.is_file():
            violations.append(f"missing_native:{h['native_program_reference']}:{p}")
            continue
        b = p.read_bytes()
        if sha256_bytes(b) != h["native_payload_sha256"]:
            violations.append(f"native_sha:{h['native_program_reference']}")

        footer, _checks = find_footer(b)
        if footer is None:
            violations.append(f"orb_footer:{h['native_program_reference']}")
            continue
        info = parse_binary_info(b, footer)
        if info.get("stage") != "LocalShader" or info.get("stage_value") != 3:
            violations.append(
                f"orb_stage:{h['native_program_reference']}:"
                f"{info.get('stage')}:{info.get('stage_value')}"
            )
        n = int(info.get("code_length_bytes") or 0)
        if n <= 0 or n > footer or sha256_bytes(b[:n]) != sha:
            violations.append(f"gcn_identity:{h['native_program_reference']}:{sha}")

        usage = parse_usage(b, footer, info)
        slots = usage.get("slots") or []
        sig = usage_signature(slots)
        by_sha[sha].append(h)
        signature_by_sha[sha].add(sig)
        slots_by_sha[sha] = slots
        all_layouts[sig] += 1

    for sha, sigs in signature_by_sha.items():
        if len(sigs) != 1:
            violations.append(f"usage_layout_not_invariant:{sha}:{len(sigs)}")
    if set(by_sha) != program_roster:
        violations.append(f"wrapper_program_roster:{len(by_sha)}:{len(program_roster)}")

    paths = sorted(ir_dir.glob("*.json"))
    ir_roster = {p.stem.lower() for p in paths}
    if len(paths) != EXPECTED_PROGRAMS or ir_roster != program_roster:
        violations.append(
            f"ir_roster:{len(paths)}:{len(ir_roster)}:{len(program_roster)}"
        )

    tbuf_rows: list[dict] = []
    descriptor_windows = collections.Counter()
    descriptor_program_windows = collections.Counter()
    api_slots = collections.Counter()
    usage_names = collections.Counter()
    per_program_hist = collections.Counter()
    total_ins = 0
    tbuf_programs: set[str] = set()
    descriptor_mutated_count = 0
    tbuf_component_count = 0

    for p in paths:
        sha = p.stem.lower()
        d = json.loads(p.read_text())
        if d.get("status") != IR_STATUS:
            violations.append(f"ir_status:{sha}:{d.get('status')}")
            continue
        pa = d.get("parse_accounting") or {}
        if pa.get("status") != ACCOUNT_STATUS:
            violations.append(f"parse_accounting:{sha}:{pa.get('status')}")
            continue

        ins = d.get("instructions") or []
        total_ins += len(ins)
        prior_scalar_defs: dict[str, list[int]] = collections.defaultdict(list)
        local: list[dict] = []
        windows: set[str] = set()
        slots = slots_by_sha.get(sha) or []

        for x in ins:
            if x.get("opcode") == "tbuffer_load_format_xyzw":
                ops = x.get("operands") or []
                defs = x.get("defs") or []
                if len(ops) < 3:
                    violations.append(
                        f"tbuffer_operands:{sha}:{x.get('index')}:{ops!r}"
                    )
                    continue
                window = ops[2]
                regs = pair_regs(window)
                if len(regs) != 4:
                    violations.append(
                        f"tbuffer_descriptor_width:{sha}:{x.get('index')}:{window}"
                    )
                    continue
                if len(defs) != 4 or any(not str(v).startswith("v") for v in defs):
                    violations.append(
                        f"tbuffer_result_width:{sha}:{x.get('index')}:{defs!r}"
                    )

                start_reg = int(regs[0][1:])
                matching = [s for s in slots if int(s["start_register"]) == start_reg]
                exact = [
                    s
                    for s in matching
                    if int(s["usage_type"]) == 2
                    and s.get("usage_name") == "ImmConstBuffer"
                    and int(s["api_slot"]) == 10
                ]
                if len(exact) != 1:
                    violations.append(
                        f"tbuffer_usage_slot:{sha}:{x.get('index')}:{window}:{matching!r}"
                    )
                    slot = None
                else:
                    slot = exact[0]

                mutated = {
                    r: list(prior_scalar_defs.get(r) or [])
                    for r in regs
                    if prior_scalar_defs.get(r)
                }
                if mutated:
                    descriptor_mutated_count += 1
                    violations.append(
                        f"tbuffer_descriptor_not_entry_state:{sha}:{x.get('index')}:"
                        f"{window}:{mutated!r}"
                    )

                descriptor_windows[window] += 1
                windows.add(window)
                api_slots[10 if slot else -1] += 1
                usage_names[slot["usage_name"] if slot else "UNRESOLVED"] += 1
                tbuf_component_count += len(defs)
                local.append(
                    {
                        "instruction": x.get("index"),
                        "address": x.get("address_hex"),
                        "descriptor_window": window,
                        "descriptor_registers": regs,
                        "reaching_state": (
                            "PROGRAM_ENTRY_USER_DATA" if not mutated else "MUTATED"
                        ),
                        "usage_slot": (
                            None
                            if slot is None
                            else {
                                k: slot[k]
                                for k in (
                                    "index",
                                    "usage_type",
                                    "usage_name",
                                    "api_slot",
                                    "start_register",
                                    "raw_hex",
                                )
                            }
                        ),
                    }
                )

            for r in x.get("defs") or []:
                if SREG_RE.fullmatch(str(r)):
                    prior_scalar_defs[r].append(x.get("index"))

        if local:
            tbuf_programs.add(sha)
            per_program_hist[len(local)] += 1
            for w in windows:
                descriptor_program_windows[w] += 1
            tbuf_rows.extend({"gcn_sha256": sha, **r} for r in local)

    if total_ins != EXPECTED_INSTRUCTIONS:
        violations.append(f"instruction_count:{total_ins}!={EXPECTED_INSTRUCTIONS}")
    if len(tbuf_programs) != EXPECTED_TBUFFER_PROGRAMS:
        violations.append(
            f"tbuffer_program_count:{len(tbuf_programs)}!={EXPECTED_TBUFFER_PROGRAMS}"
        )
    if len(tbuf_rows) != EXPECTED_TBUFFER_INSTRUCTIONS:
        violations.append(
            f"tbuffer_instruction_count:{len(tbuf_rows)}!={EXPECTED_TBUFFER_INSTRUCTIONS}"
        )
    if tbuf_component_count != EXPECTED_TBUFFER_COMPONENTS:
        violations.append(
            f"tbuffer_component_count:{tbuf_component_count}!={EXPECTED_TBUFFER_COMPONENTS}"
        )
    if dict(descriptor_windows) != EXPECTED_DESCRIPTOR_WINDOWS:
        violations.append(
            f"descriptor_windows:{dict(descriptor_windows)}!={EXPECTED_DESCRIPTOR_WINDOWS}"
        )
    if dict(descriptor_program_windows) != EXPECTED_DESCRIPTOR_PROGRAM_WINDOWS:
        violations.append(
            "descriptor_program_windows:"
            f"{dict(descriptor_program_windows)}!={EXPECTED_DESCRIPTOR_PROGRAM_WINDOWS}"
        )
    if dict(per_program_hist) != EXPECTED_PER_PROGRAM_HIST:
        violations.append(
            f"per_program_hist:{dict(per_program_hist)}!={EXPECTED_PER_PROGRAM_HIST}"
        )

    t_headers = [
        h for h in headers if str(h["gcn_sha256"]).lower() in tbuf_programs
    ]
    t_materials = sum(int(h["material_occurrence_count"]) for h in t_headers)
    if len(t_headers) != EXPECTED_TBUFFER_WRAPPERS:
        violations.append(
            f"tbuffer_wrapper_count:{len(t_headers)}!={EXPECTED_TBUFFER_WRAPPERS}"
        )
    if t_materials != EXPECTED_TBUFFER_MATERIAL_OCCURRENCES:
        violations.append(
            "tbuffer_material_occurrences:"
            f"{t_materials}!={EXPECTED_TBUFFER_MATERIAL_OCCURRENCES}"
        )
    if api_slots != {10: EXPECTED_TBUFFER_INSTRUCTIONS}:
        violations.append(f"api_slots:{dict(api_slots)}")
    if usage_names != {"ImmConstBuffer": EXPECTED_TBUFFER_INSTRUCTIONS}:
        violations.append(f"usage_names:{dict(usage_names)}")

    program_rows = []
    for sha in sorted(tbuf_programs):
        hs = by_sha[sha]
        rows = [r for r in tbuf_rows if r["gcn_sha256"] == sha]
        window = rows[0]["descriptor_window"] if rows else None
        if any(r["descriptor_window"] != window for r in rows):
            violations.append(f"multi_descriptor_window_program:{sha}")
        program_rows.append(
            {
                "gcn_sha256": sha,
                "tbuffer_instruction_count": len(rows),
                "descriptor_window": window,
                "wrapper_count": len(hs),
                "wrappers": sorted(h["wrapper"] for h in hs),
                "material_occurrence_count": sum(
                    int(h["material_occurrence_count"]) for h in hs
                ),
                "usage_signature": [
                    list(x) for x in next(iter(signature_by_sha[sha]))
                ],
            }
        )

    coverage = {
        "exact_localshader_program_count": len(program_roster),
        "exact_localshader_wrapper_count": len(headers),
        "exact_instruction_count": total_ins,
        "unique_usage_layout_count": len(all_layouts),
        "tbuffer_program_count": len(tbuf_programs),
        "tbuffer_wrapper_count": len(t_headers),
        "tbuffer_material_occurrence_count": t_materials,
        "tbuffer_instruction_count": len(tbuf_rows),
        "tbuffer_result_component_count": tbuf_component_count,
        "tbuffer_descriptor_usage_type_counts": dict(sorted(usage_names.items())),
        "tbuffer_descriptor_api_slot_counts": {
            str(k): v for k, v in sorted(api_slots.items())
        },
        "tbuffer_descriptor_window_counts": dict(sorted(descriptor_windows.items())),
        "tbuffer_descriptor_program_window_counts": dict(
            sorted(descriptor_program_windows.items())
        ),
        "tbuffer_per_program_instruction_histogram": {
            str(k): v for k, v in sorted(per_program_hist.items())
        },
        "direct_unmutated_program_entry_descriptor_count": (
            len(tbuf_rows) - descriptor_mutated_count
        ),
        "mutated_descriptor_count": descriptor_mutated_count,
        "shader_expression_semantic_promotions": 0,
        "tessellation_pipeline_ownership_promotions": 0,
    }
    return {
        "schema": SCHEMA,
        "status": (
            STATUS
            if not violations
            else "D1_GCN_LOCALSHADER_TBUFFER_USAGE_BINDING_WITH_VIOLATIONS"
        ),
        "coverage": coverage,
        "programs": program_rows,
        "bindings": tbuf_rows,
        "violations": violations,
        "semantic_boundary": {
            "tbuffer_descriptor_input_usage": (
                "EXACT_IMM_CONST_BUFFER_API_SLOT_10"
                if not violations
                else "NOT_PROMOTED"
            ),
            "tbuffer_descriptor_reaching_state": (
                "EXACT_UNMUTATED_PROGRAM_ENTRY_USER_DATA"
                if not violations
                else "NOT_PROMOTED"
            ),
            "tbuffer_result_width": "EXACT_4X32",
            "tbuffer_fetched_contents": (
                "OPAQUE_CONSTANT_BUFFER_BACKING_MEMORY_WITHHELD"
            ),
            "api_slot_10_runtime_binding_owner": "NEXT_GATE",
            "localshader_to_hullshader_ownership": "WITHHELD",
            "domainshader_pipeline_ownership": "WITHHELD",
            "shader_expression_semantics": "WITHHELD",
            "shader_expression_semantic_promotions": 0,
        },
        "policy": (
            "Every LocalShader TBUFFER_LOAD_FORMAT_XYZW descriptor is admitted only "
            "when the exact OrbShdr InputUsageSlot table identifies the reaching, "
            "unmodified program-entry SGPR window as ImmConstBuffer API slot 10. "
            "Register number alone is never treated as a resource slot. Buffer contents, "
            "runtime API-slot ownership, tessellation topology, material roles and "
            "shader-expression meaning remain withheld."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--localshader-corpus", type=Path, required=True)
    ap.add_argument("--binary-root", type=Path, required=True)
    ap.add_argument("--ir-dir", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()
    out = build(a.localshader_corpus, a.binary_root, a.ir_dir)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "status": out["status"],
                "coverage": out["coverage"],
                "violations": out["violations"][:40],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if not out["violations"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
