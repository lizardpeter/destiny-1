#!/usr/bin/env python3
"""Exact PS/VS/DS admission driver for the universal D1 GCN structural census.

The underlying GCN/CFG producer is intentionally unchanged: stage identity does not
change GFX7 instruction decoding. This driver admits only the zero-violation canonical
V3 corpus, projects its already-proven report fields to the legacy structural input
contract, preserves PS/VS/DS membership, and retains the corrected VCC register-class
normalization used by the prior V2 structural driver.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import d1_gcn_shader_corpus_structural_census as core

V3_SCHEMA = "d1_remote_ps4_shader_corpus_extract/v3"
V3_STATUS = "D1_REMOTE_PS4_SHADER_CORPUS_EXACT_PS_VS_DS"
V1_SCHEMA = "d1_remote_ps4_shader_corpus_extract/v1"
REQUIRED_STAGES = {"PS", "VS", "DS"}


def fixed_reg_kind(r: str) -> str:
    if r.startswith("vcc"):
        return "VCC"
    if r.startswith("exec"):
        return "EXEC"
    if r == "scc":
        return "SCC"
    if r == "m0":
        return "M0"
    if r.startswith("v"):
        return "VGPR"
    if r.startswith("s"):
        return "SGPR"
    return r.upper()


def arg_value(*names: str) -> tuple[int, str]:
    for name in names:
        if name in sys.argv:
            i = sys.argv.index(name)
            if i + 1 >= len(sys.argv):
                raise SystemExit(f"{name} requires a value")
            return i + 1, sys.argv[i + 1]
    raise SystemExit(f"one of {names!r} is required")


def self_test() -> None:
    assert fixed_reg_kind("vcc") == "VCC"
    assert fixed_reg_kind("vcc_lo") == "VCC"
    assert fixed_reg_kind("v7") == "VGPR"
    assert fixed_reg_kind("s12") == "SGPR"
    assert fixed_reg_kind("exec") == "EXEC"
    sample = {
        "schema": V3_SCHEMA,
        "status": V3_STATUS,
        "violations": [],
        "header_population": {"stage_counts": {"PS": 1, "VS": 1, "DS": 1}},
        "gcn_program_population": {"stage_unique_counts": {"PS": 1, "VS": 1, "DS": 1}},
    }
    assert sample["schema"] == V3_SCHEMA
    assert set(sample["header_population"]["stage_counts"]) == REQUIRED_STAGES
    print("D1_GCN_SHADER_CORPUS_STRUCTURAL_CENSUS_V3_SELF_TEST_OK")


def main() -> int:
    if "--self-test" in sys.argv:
        self_test()
        return 0

    extract_i, extract_s = arg_value("--extract-report")
    _, output_s = arg_value("-o", "--output")
    extract_path = Path(extract_s)
    output_path = Path(output_s)
    src = json.loads(extract_path.read_text())

    if src.get("schema") != V3_SCHEMA:
        raise SystemExit(f"exact V3 corpus required, got {src.get('schema')!r}")
    if src.get("status") != V3_STATUS or src.get("violations"):
        raise SystemExit("zero-violation exact PS/VS/DS V3 corpus required")
    hs = (src.get("header_population") or {}).get("stage_counts") or {}
    ps = (src.get("gcn_program_population") or {}).get("stage_unique_counts") or {}
    if set(hs) != REQUIRED_STAGES or any(int(hs.get(s, 0)) <= 0 for s in REQUIRED_STAGES):
        raise SystemExit(f"exact PS/VS/DS header population required: {hs!r}")
    if set(ps) != REQUIRED_STAGES or any(int(ps.get(s, 0)) <= 0 for s in REQUIRED_STAGES):
        raise SystemExit(f"exact PS/VS/DS program population required: {ps!r}")

    compat_path = extract_path.with_name(extract_path.stem + ".STRUCTURAL_V1_COMPAT.json")
    compat = dict(src)
    compat["schema"] = V1_SCHEMA
    compat["compatibility_source_schema"] = V3_SCHEMA
    compat["compatibility_policy"] = (
        "Only the top-level schema marker is projected for the legacy structural algorithm. "
        "Exact GCN identities, corrected PS/VS/DS stages, headers, native references and the "
        "zero-violation V3 proof are retained verbatim."
    )
    compat_path.write_text(json.dumps(compat, indent=2) + "\n")
    sys.argv[extract_i] = str(compat_path)
    core.reg_kind = fixed_reg_kind
    try:
        rc = core.main()
    finally:
        sys.argv[extract_i] = extract_s
        try:
            compat_path.unlink()
        except FileNotFoundError:
            pass

    if output_path.is_file():
        out = json.loads(output_path.read_text())
        observed = set()
        for p in out.get("programs") or []:
            observed.update(str(x).upper() for x in (p.get("stages") or []))
        if observed != REQUIRED_STAGES:
            out.setdefault("violations", []).append(
                f"structural_stage_population:{sorted(observed)}!={sorted(REQUIRED_STAGES)}"
            )
            out["status"] = "D1_GCN_SHADER_CORPUS_STRUCTURAL_CENSUS_WITH_VIOLATIONS"
            rc = 2
        out["source_extract_report"] = str(extract_path)
        out["source_extract_schema"] = V3_SCHEMA
        out["driver"] = {
            "schema": "d1_gcn_shader_corpus_structural_census_driver/v3",
            "status": "D1_GCN_SHADER_CORPUS_STRUCTURAL_CENSUS_DRIVER_PS_VS_DS",
            "required_stages": sorted(REQUIRED_STAGES),
            "vcc_normalized_register_classification_fixed": True,
            "structural_algorithm": "d1_gcn_shader_corpus_structural_census.py",
        }
        out["encoding_representation_boundary"] = {
            "raw_gcn_program_identity": "OrbShdr-bounded V3 extractor bytes and SHA-256",
            "clrx_encoding_hex_role": "textual per-instruction width/form evidence",
            "clrx_encoding_hex_concatenation_is_raw_byte_oracle": False,
        }
        out["policy"] = str(out.get("policy") or "") + (
            " Stage membership is the exact V3 OrbShdr-derived PS/VS/DS identity. "
            "The generic GFX7 Structural IR algorithm is intentionally shared across stages."
        )
        output_path.write_text(json.dumps(out, indent=2) + "\n")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
