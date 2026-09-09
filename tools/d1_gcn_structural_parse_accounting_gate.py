#!/usr/bin/env python3
"""Fail-closed corpus gate for D1 GCN Structural IR native-line accounting.

This is deliberately narrower than semantic shader promotion.  It consumes the
structural-census checkpoint plus each emitted Structural IR JSON and requires every
program admitted as structurally complete to carry the producer's exact native-line
accounting proof.  The gate also makes a caller-selected mixed-stage reference set
explicit, so a game-wide run cannot accidentally become single-stage while still
reporting aggregate coverage.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

ACCOUNTING_STATUS = "D1_GCN_STRUCTURAL_PARSE_ACCOUNTING_EXACT"
IR_STATUS = "D1_GCN_STRUCTURAL_IR_COMPLETE"
GATE_STATUS = "D1_GCN_STRUCTURAL_PARSE_ACCOUNTING_CORPUS_EXACT"


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def parse_required(value: str) -> tuple[str, str | None]:
    header, sep, stage = value.partition(":")
    header = norm(header)
    stage = stage.upper() if sep and stage else None
    if stage not in (None, "PS", "VS"):
        raise argparse.ArgumentTypeError(
            f"required header stage must be PS or VS, got {stage!r}"
        )
    return header, stage


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--census", type=Path, required=True)
    ap.add_argument("--ir-dir", type=Path, required=True)
    ap.add_argument(
        "--required-header",
        action="append",
        default=[],
        type=parse_required,
        metavar="HEADER[:PS|VS]",
    )
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    census = json.loads(a.census.read_text())
    if census.get("schema") != "d1_gcn_shader_corpus_structural_census/v1":
        raise SystemExit(f"unsupported census schema: {census.get('schema')!r}")

    programs = census.get("programs") or []
    violations: list[str] = []
    program_rows: list[dict] = []
    stage_planned = Counter()
    stage_exact = Counter()
    total_native_lines = 0
    total_ir_instructions = 0
    total_encoded_bytes = 0
    exact_programs = 0
    exact_headers: dict[str, set[str]] = {}

    for rec in programs:
        code_sha = str(rec.get("gcn_sha256", "")).lower()
        code_bytes = int(rec.get("gcn_bytes", 0))
        stages = sorted({str(x).upper() for x in (rec.get("stages") or [])})
        for stage in stages:
            stage_planned[stage] += 1

        row = {
            "gcn_sha256": code_sha,
            "gcn_bytes": code_bytes,
            "stages": stages,
            "headers": rec.get("headers") or [],
            "violations": [],
        }
        ir_path = a.ir_dir / f"{code_sha}.json"
        if not ir_path.is_file():
            row["violations"].append("structural_ir_missing")
        else:
            try:
                ir = json.loads(ir_path.read_text())
            except Exception as exc:
                row["violations"].append(
                    f"structural_ir_json:{type(exc).__name__}:{exc}"
                )
                ir = None
            if ir is not None:
                if ir.get("status") != IR_STATUS:
                    row["violations"].append(
                        f"structural_ir_status:{ir.get('status')!r}"
                    )
                ins = ir.get("instructions") or []
                pa = ir.get("parse_accounting") or {}
                if pa.get("status") != ACCOUNTING_STATUS:
                    row["violations"].append(
                        f"parse_accounting_status:{pa.get('status')!r}"
                    )
                checks = {
                    "native_instruction_line_count": len(ins),
                    "ir_instruction_count": len(ins),
                    "encoded_byte_count": code_bytes,
                    "unaccounted_native_instruction_line_count": 0,
                    "duplicate_ir_instruction_count": 0,
                }
                for key, expected in checks.items():
                    actual = pa.get(key)
                    if actual != expected:
                        row["violations"].append(
                            f"parse_accounting_{key}:{actual!r}!={expected!r}"
                        )
                if int(ir.get("instruction_count", -1)) != len(ins):
                    row["violations"].append(
                        f"instruction_count:{ir.get('instruction_count')!r}!={len(ins)}"
                    )
                if ins:
                    first = int(ins[0]["address"])
                    last = ins[-1]
                    last_end = int(last["address"]) + int(last["byte_size"])
                    if first != 0:
                        row["violations"].append(f"first_address:{first}!=0")
                    if last_end != code_bytes:
                        row["violations"].append(
                            f"last_instruction_end:{last_end}!={code_bytes}"
                        )
                elif code_bytes:
                    row["violations"].append("nonempty_program_has_no_instructions")

                row["parse_accounting"] = pa
                row["instruction_count"] = len(ins)

        if row["violations"]:
            violations.extend(f"{code_sha}:{v}" for v in row["violations"])
        else:
            exact_programs += 1
            pa = row["parse_accounting"]
            total_native_lines += int(pa["native_instruction_line_count"])
            total_ir_instructions += int(pa["ir_instruction_count"])
            total_encoded_bytes += int(pa["encoded_byte_count"])
            for stage in stages:
                stage_exact[stage] += 1
            for h in row["headers"]:
                if not h.get("header"):
                    continue
                header = norm(h["header"])
                exact_headers.setdefault(header, set()).add(
                    str(h.get("stage", "")).upper()
                )
        program_rows.append(row)

    required_rows = []
    for header, expected_stage in a.required_header:
        actual_stages = sorted(x for x in exact_headers.get(header, set()) if x)
        ok = header in exact_headers and (
            expected_stage is None or expected_stage in actual_stages
        )
        required_rows.append({
            "header": header,
            "expected_stage": expected_stage,
            "exact_structural_parse_accounting": ok,
            "observed_stages": actual_stages,
        })
        if not ok:
            violations.append(
                f"required_header_not_exact:{header}:expected_stage={expected_stage}:"
                f"observed_stages={actual_stages}"
            )

    for stage in ("PS", "VS"):
        if stage_planned[stage] <= 0:
            violations.append(f"stage_absent_from_planned_corpus:{stage}")
        if stage_exact[stage] != stage_planned[stage]:
            violations.append(
                f"stage_not_fully_accounted:{stage}:"
                f"{stage_exact[stage]}/{stage_planned[stage]}"
            )

    if total_native_lines != total_ir_instructions:
        violations.append(
            f"aggregate_native_ir_count_mismatch:"
            f"{total_native_lines}!={total_ir_instructions}"
        )

    planned_programs = len(programs)
    census_complete = (
        census.get("status") == "D1_GCN_SHADER_CORPUS_STRUCTURAL_CENSUS_COMPLETE"
    )
    if not census_complete:
        violations.append(f"census_not_complete:{census.get('status')!r}")
    if exact_programs != planned_programs:
        violations.append(
            f"exact_program_count:{exact_programs}!={planned_programs}"
        )

    out = {
        "schema": "d1_gcn_structural_parse_accounting_gate/v1",
        "status": GATE_STATUS if not violations else "D1_GCN_STRUCTURAL_PARSE_ACCOUNTING_CORPUS_WITH_VIOLATIONS",
        "source_census": str(a.census),
        "producer_contract": {
            "structural_ir_status": IR_STATUS,
            "parse_accounting_status": ACCOUNTING_STATUS,
            "required_per_program_fields": [
                "native_instruction_line_count",
                "ir_instruction_count",
                "encoded_byte_count",
                "unaccounted_native_instruction_line_count",
                "duplicate_ir_instruction_count",
            ],
        },
        "coverage": {
            "planned_unique_gcn_programs": planned_programs,
            "exact_parse_accounted_unique_gcn_programs": exact_programs,
            "stage_planned_unique_program_counts": dict(sorted(stage_planned.items())),
            "stage_exact_unique_program_counts": dict(sorted(stage_exact.items())),
            "native_instruction_lines": total_native_lines,
            "ir_instructions": total_ir_instructions,
            "encoded_bytes": total_encoded_bytes,
        },
        "required_mixed_stage_reference_headers": required_rows,
        "programs": program_rows,
        "violations": violations,
        "policy": (
            "Every exact OrbShdr-bounded GCN program must be represented by a Structural IR "
            "whose independent source ledger proves every address-bearing CLRX native line "
            "entered IR exactly once, in order, with exact address, encoding words and byte "
            "size. PS and VS are both mandatory. This gate proves structural parse accounting "
            "only and does not promote shader semantics."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n")
    print(
        "STATUS", out["status"],
        "PROGRAMS", f"{exact_programs}/{planned_programs}",
        "PS", f"{stage_exact['PS']}/{stage_planned['PS']}",
        "VS", f"{stage_exact['VS']}/{stage_planned['VS']}",
        "INSTRUCTIONS", total_ir_instructions,
        "BYTES", total_encoded_bytes,
        "REQUIRED", f"{sum(x['exact_structural_parse_accounting'] for x in required_rows)}/{len(required_rows)}",
        "VIOLATIONS", len(violations),
    )
    for violation in violations[:200]:
        print("VIOLATION", violation)
    return 0 if out["status"] == GATE_STATUS else 2


if __name__ == "__main__":
    raise SystemExit(main())
