#!/usr/bin/env python3
"""Compatibility/hardening driver for the game-wide D1 GCN structural census.

The structural algorithm remains ``d1_gcn_shader_corpus_structural_census.py``.
This driver makes three deliberately narrow corrections for the v2 corpus pass:

1. accept the exact ``d1_remote_ps4_shader_corpus_extract/v2`` recovery report
   without weakening any v1 structural acceptance rule;
2. classify VCC before the generic ``v*`` register rule in normalized reporting;
3. record that CLRX ``encoding_hex`` is a textual instruction representation used
   for instruction width/address accounting and form census, not a byte-stream
   oracle that may be concatenated to reproduce the raw GCN SHA-256.

Raw program identity continues to come only from the OrbShdr-bounded ``*.bin``
files emitted by the exact corpus extractor.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import d1_gcn_shader_corpus_structural_census as core

V2_SCHEMA = "d1_remote_ps4_shader_corpus_extract/v2"
V1_SCHEMA = "d1_remote_ps4_shader_corpus_extract/v1"


def fixed_reg_kind(r: str) -> str:
    # VCC names begin with 'v', so these special registers must be classified
    # before the generic VGPR rule. This affects normalized census reporting only;
    # the underlying Structural IR defs/uses remain untouched.
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


def main() -> int:
    extract_i, extract_s = arg_value("--extract-report")
    _, output_s = arg_value("-o", "--output")
    extract_path = Path(extract_s)
    output_path = Path(output_s)
    src = json.loads(extract_path.read_text())
    schema = src.get("schema")
    if schema not in (V1_SCHEMA, V2_SCHEMA):
        raise SystemExit(f"unsupported extract report: {schema!r}")

    # Keep the existing structural implementation unchanged. Its input schema
    # check is adapted through a deterministic compatibility copy only.
    compat_path = extract_path
    remove_compat = False
    if schema == V2_SCHEMA:
        compat_path = extract_path.with_name(extract_path.stem + ".STRUCTURAL_V1_COMPAT.json")
        compat = dict(src)
        compat["schema"] = V1_SCHEMA
        compat["compatibility_source_schema"] = V2_SCHEMA
        compat["compatibility_policy"] = (
            "Schema adaptation changes only the top-level version marker; the fields "
            "consumed by the structural census retain their exact v2 values."
        )
        compat_path.write_text(json.dumps(compat, indent=2) + "\n")
        sys.argv[extract_i] = str(compat_path)
        remove_compat = True

    core.reg_kind = fixed_reg_kind
    try:
        rc = core.main()
    finally:
        sys.argv[extract_i] = extract_s

    if output_path.is_file():
        out = json.loads(output_path.read_text())
        out["source_extract_report"] = str(extract_path)
        out["source_extract_schema"] = schema
        out["driver"] = {
            "schema": "d1_gcn_shader_corpus_structural_census_driver/v2",
            "vcc_normalized_register_classification_fixed": True,
            "structural_algorithm": "d1_gcn_shader_corpus_structural_census.py",
        }
        out["encoding_representation_boundary"] = {
            "raw_gcn_program_identity": "OrbShdr-bounded extractor .bin bytes and SHA-256",
            "clrx_encoding_hex_role": (
                "textual per-instruction representation used for width/address accounting "
                "and normalized form census"
            ),
            "clrx_encoding_hex_concatenation_is_raw_byte_oracle": False,
            "reason": (
                "808EE505 exact recovery proves the raw 2200-byte GCN SHA-256 is "
                "7cbed0ae8ff82a15a9945c136cb8e58188c78cc0fd7c45ee8d3778959cbca352; "
                "naive concatenation of CLRX encoding_hex yields a different digest."
            ),
        }
        out["policy"] = str(out.get("policy") or "") + (
            " CLRX encoding_hex is not promoted as raw native byte order; exact raw "
            "program identity always comes from the extractor's OrbShdr-bounded .bin."
        )
        output_path.write_text(json.dumps(out, indent=2) + "\n")

    if remove_compat:
        try:
            compat_path.unlink()
        except FileNotFoundError:
            pass
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
