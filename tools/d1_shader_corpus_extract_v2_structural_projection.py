#!/usr/bin/env python3
"""Project an exact D1 PS4 shader-corpus V2 recovery report to the V1 structural input contract.

The V2 extractor changes recovery scheduling, not shader identity or GCN bytes. The
existing structural census predates V2 and accepts the V1 report schema. This adapter
allows a fully exact, violation-free V2 raw-corpus checkpoint to be reused without
re-downloading tens of thousands of retail resources.

Projection is fail-closed: every planned header and native reference must have been
recovered, every native reference must have exact OrbShdr-bounded GCN code, all row
violations must be empty, and population counts must agree before the schema is
projected. No field used by the structural census is synthesized from names or guesses.
"""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

V2_SCHEMA = "d1_remote_ps4_shader_corpus_extract/v2"
V1_SCHEMA = "d1_remote_ps4_shader_corpus_extract/v1"
EXACT_STATUS = "D1_REMOTE_PS4_SHADER_CORPUS_EXACT"
PROJECTION_STATUS = "D1_SHADER_CORPUS_V2_STRUCTURAL_PROJECTION_EXACT"


def project(src: dict) -> tuple[dict, dict]:
    violations: list[str] = []
    if src.get("schema") != V2_SCHEMA:
        raise ValueError(f"unsupported source schema: {src.get('schema')!r}")
    if src.get("status") != EXACT_STATUS:
        violations.append(f"source_status:{src.get('status')!r}")
    if src.get("violations"):
        violations.append(f"source_violations:{len(src['violations'])}")

    hp = src.get("header_population") or {}
    nr = src.get("native_reference_population") or {}
    gp = src.get("gcn_program_population") or {}
    headers = src.get("headers") or []
    natives = src.get("native_programs") or []
    programs = src.get("unique_gcn_programs") or []

    htotal = int(hp.get("total", -1))
    hrecovered = int(hp.get("payload_recovered_count", -1))
    planned_refs = int(nr.get("planned_unique", -1))
    recovered_rows = int(nr.get("recovered_rows", -1))
    payload_refs = int(nr.get("payload_recovered_count", -1))
    gcn_refs = int(nr.get("gcn_code_recovered_count", -1))
    unique_gcn = int(gp.get("unique_exact_code_sha256_count", -1))

    checks = {
        "header_rows": (len(headers), htotal),
        "header_payload_recovery": (hrecovered, htotal),
        "native_rows": (len(natives), planned_refs),
        "native_recovered_rows": (recovered_rows, planned_refs),
        "native_payload_recovery": (payload_refs, planned_refs),
        "native_gcn_recovery": (gcn_refs, planned_refs),
        "unique_gcn_rows": (len(programs), unique_gcn),
    }
    for name, (actual, expected) in checks.items():
        if actual != expected:
            violations.append(f"{name}:{actual}!={expected}")

    if int(hp.get("payload_unrecovered_count", -1)) != 0:
        violations.append(
            f"header_payload_unrecovered:{hp.get('payload_unrecovered_count')!r}"
        )
    if nr.get("unrecovered_native_references"):
        violations.append(
            f"unrecovered_native_references:{len(nr['unrecovered_native_references'])}"
        )

    seen_headers: set[tuple[str, str]] = set()
    for i, row in enumerate(headers):
        if row.get("violations"):
            violations.append(f"header_row_{i}_violations:{len(row['violations'])}")
        stage = str(row.get("stage", "")).upper()
        tag = str(row.get("header", "")).upper()
        if stage not in ("PS", "VS") or not tag:
            violations.append(f"header_row_{i}_identity:{stage}:{tag}")
            continue
        key = (stage, tag)
        if key in seen_headers:
            violations.append(f"duplicate_header_row:{stage}:{tag}")
        seen_headers.add(key)

    seen_refs: set[str] = set()
    for i, row in enumerate(natives):
        if row.get("violations"):
            violations.append(f"native_row_{i}_violations:{len(row['violations'])}")
        ref = str(row.get("native_program_reference", "")).upper()
        if not ref:
            violations.append(f"native_row_{i}_missing_reference")
        elif ref in seen_refs:
            violations.append(f"duplicate_native_reference:{ref}")
        else:
            seen_refs.add(ref)
        code = row.get("gcn_code") or {}
        if int(code.get("bytes", 0)) <= 0 or len(str(code.get("sha256", ""))) != 64:
            violations.append(f"native_row_{i}_missing_exact_gcn:{ref}")

    seen_sha: set[str] = set()
    for i, row in enumerate(programs):
        sha = str(row.get("gcn_sha256", "")).lower()
        stages = sorted({str(x).upper() for x in (row.get("stages") or [])})
        if len(sha) != 64:
            violations.append(f"program_row_{i}_invalid_sha:{sha!r}")
        elif sha in seen_sha:
            violations.append(f"duplicate_unique_gcn_sha:{sha}")
        else:
            seen_sha.add(sha)
        if int(row.get("gcn_bytes", 0)) <= 0:
            violations.append(f"program_row_{i}_invalid_bytes:{row.get('gcn_bytes')!r}")
        if not stages or any(x not in ("PS", "VS") for x in stages):
            violations.append(f"program_row_{i}_invalid_stages:{stages}")
        if not row.get("native_program_references"):
            violations.append(f"program_row_{i}_no_native_references")
        if not row.get("headers"):
            violations.append(f"program_row_{i}_no_headers")

    projected = dict(src)
    projected["schema"] = V1_SCHEMA
    projected["projection"] = {
        "status": PROJECTION_STATUS if not violations else "D1_SHADER_CORPUS_V2_STRUCTURAL_PROJECTION_WITH_VIOLATIONS",
        "source_schema": V2_SCHEMA,
        "target_contract": V1_SCHEMA,
        "policy": (
            "This projection changes only the report schema accepted by the existing "
            "structural census. Header/native/program identity, exact GCN SHA-256, byte "
            "lengths, stage membership, provenance rows and violations are retained from V2."
        ),
    }
    projected["projection_violations"] = violations

    report = {
        "schema": "d1_shader_corpus_extract_v2_structural_projection/v1",
        "status": PROJECTION_STATUS if not violations else "D1_SHADER_CORPUS_V2_STRUCTURAL_PROJECTION_WITH_VIOLATIONS",
        "source_schema": V2_SCHEMA,
        "target_contract": V1_SCHEMA,
        "coverage": {
            "headers": htotal,
            "header_payloads_recovered": hrecovered,
            "planned_unique_native_references": planned_refs,
            "native_payloads_recovered": payload_refs,
            "native_references_with_gcn": gcn_refs,
            "unique_exact_gcn_programs": unique_gcn,
        },
        "violations": violations,
    }
    return projected, report


def self_test() -> None:
    sha = "a" * 64
    src = {
        "schema": V2_SCHEMA,
        "status": EXACT_STATUS,
        "violations": [],
        "header_population": {
            "total": 1,
            "stage_counts": {"PS": 1},
            "payload_recovered_count": 1,
            "payload_unrecovered_count": 0,
        },
        "native_reference_population": {
            "planned_unique": 1,
            "recovered_rows": 1,
            "payload_recovered_count": 1,
            "gcn_code_recovered_count": 1,
            "violation_rows": 0,
            "unrecovered_native_references": [],
        },
        "gcn_program_population": {
            "unique_exact_code_sha256_count": 1,
            "stage_unique_counts": {"PS": 1},
            "shared_by_multiple_native_references": 0,
            "shared_by_multiple_headers": 0,
        },
        "headers": [{"stage": "PS", "header": "808EE505", "violations": []}],
        "native_programs": [{
            "native_program_reference": "808EE508",
            "gcn_code": {"bytes": 8, "sha256": sha},
            "violations": [],
        }],
        "unique_gcn_programs": [{
            "gcn_sha256": sha,
            "gcn_bytes": 8,
            "native_program_references": ["808EE508"],
            "headers": [{"stage": "PS", "header": "808EE505"}],
            "stages": ["PS"],
        }],
    }
    projected, report = project(src)
    assert report["status"] == PROJECTION_STATUS, report
    assert projected["schema"] == V1_SCHEMA
    assert projected["unique_gcn_programs"] == src["unique_gcn_programs"]
    bad = json.loads(json.dumps(src))
    bad["native_reference_population"]["gcn_code_recovered_count"] = 0
    _, bad_report = project(bad)
    assert bad_report["status"] != PROJECTION_STATUS
    assert bad_report["violations"]
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "projected.json"
        p.write_text(json.dumps(projected))
        assert json.loads(p.read_text())["schema"] == V1_SCHEMA
    print("D1_SHADER_CORPUS_V2_STRUCTURAL_PROJECTION_SELF_TEST_OK")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("source", type=Path, nargs="?")
    ap.add_argument("-o", "--output", type=Path)
    ap.add_argument("--report", type=Path)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        self_test()
        return 0
    if a.source is None or a.output is None or a.report is None:
        ap.error("source, --output and --report are required unless --self-test is used")
    src = json.loads(a.source.read_text())
    projected, report = project(src)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(projected, indent=2) + "\n")
    a.report.write_text(json.dumps(report, indent=2) + "\n")
    print("STATUS", report["status"], "COVERAGE", json.dumps(report["coverage"], sort_keys=True), "VIOLATIONS", len(report["violations"]))
    for v in report["violations"][:100]:
        print("VIOLATION", v)
    return 0 if report["status"] == PROJECTION_STATUS else 2


if __name__ == "__main__":
    raise SystemExit(main())
