#!/usr/bin/env python3
"""Corrected driver for the exact PS/VS structural frontier.

The v1 postprocessor is retained as the algorithmic implementation. This driver applies
the same register-kind normalization contract as the v2 structural census before any
form keys are built, so VCC/EXEC special registers cannot be folded into generic VGPR/
SGPR classes in stage-exclusive/common form statistics.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import d1_gcn_shader_corpus_stage_frontier as core
import d1_gcn_shader_corpus_structural_census_v2 as census_v2

DRIVER_STATUS = "D1_GCN_SHADER_CORPUS_STAGE_FRONTIER_DRIVER_V2"


def arg_value(*names: str) -> str | None:
    for name in names:
        if name in sys.argv:
            i = sys.argv.index(name)
            if i + 1 >= len(sys.argv):
                raise SystemExit(f"{name} requires a value")
            return sys.argv[i + 1]
    return None


def assert_register_contract() -> dict[str, str]:
    expected = {
        "v0": "VGPR",
        "vcc": "VCC",
        "vcc_lo": "VCC",
        "vcc_hi": "VCC",
        "s0": "SGPR",
        "scc": "SCC",
        "exec": "EXEC",
        "exec_lo": "EXEC",
        "exec_hi": "EXEC",
        "m0": "M0",
    }
    got = {k: census_v2.fixed_reg_kind(k) for k in expected}
    if got != expected:
        raise SystemExit(f"register-kind normalization contract failed: {got!r}")
    return got


def main() -> int:
    contract = assert_register_contract()
    # form_key() in the v1 frontier resolves census_lib.reg_kind dynamically.
    core.census_lib.reg_kind = census_v2.fixed_reg_kind

    self_test = "--self-test" in sys.argv
    output_s = arg_value("-o", "--output")
    rc = core.main()

    if self_test:
        # Explicitly prove the bug class that the v1 synthetic fixture did not cover.
        row = {
            "opcode": "v_add_i32",
            "encoding_hex": "0000000000000000",
            "operands": ["v0", "vcc", "v1", "v2"],
            "defs": ["v0", "vcc"],
            "uses": ["v1", "v2"],
            "branch_target_label": None,
        }
        key = core.census_lib.form_key(row)
        if key[3] != ("VGPR", "VCC"):
            raise SystemExit(f"VCC destination normalized incorrectly: {key!r}")
        print(DRIVER_STATUS, json.dumps(contract, sort_keys=True))
        return rc

    if output_s:
        output = Path(output_s)
        if not output.is_file():
            raise SystemExit(f"stage frontier did not create {output}")
        data = json.loads(output.read_text())
        data["driver"] = {
            "status": DRIVER_STATUS,
            "structural_form_register_kind_source": (
                "d1_gcn_shader_corpus_structural_census_v2.fixed_reg_kind"
            ),
            "vcc_precedence_over_generic_vgpr_prefix": True,
            "exec_precedence_over_generic_sgpr_prefix": True,
        }
        data["policy"] = (
            str(data.get("policy") or "")
            + " Stage structural-form normalization uses the same corrected V2 special-register "
              "classification as the global census."
        ).strip()
        output.write_text(json.dumps(data, indent=2) + "\n")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
