#!/usr/bin/env python3
"""Cross-source proof for D1 PS4 constant-buffer API scope names.

Pinned D1 TFX source (Charm) explicitly declares TfxScope as "Based on CBuffer
index" and maps:
  12 -> View
  13 -> Frame

Exact retail Vex PS 816CE0A8 independently exposes ImmConstBuffer API12/API13 and
instruction-level consumption for both. This proves the source-level CBuffer
scope names can be attached to those API indices without guessing from arithmetic.

This proof intentionally does NOT claim:
  * the runtime writer/producer object;
  * descriptor backing allocation/address/bytes;
  * live values;
  * field-level names inside View/Frame;
  * any name for API15, because TfxScope has no index 15.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

CHARM_COMMIT = "50d36ee1f9ecadad7522504c20b1f3f9c97e30af"
CHARM_BLOB = "7311688c71ab3a9e9d6eacd5393d07254688bace"
EXPECTED_SCOPE = {
    1: "Instance",
    2: "Transparent",
    3: "Unk3",
    8: "Unk8",
    9: "Decal",
    12: "View",
    13: "Frame",
}


def parse_tfx_scope(text: str) -> dict[int, str]:
    m = re.search(r"public\s+enum\s+TfxScope\s*:\s*byte\s*\{(.*?)\}", text, re.S)
    if not m:
        raise ValueError("TfxScope enum not found")
    out = {}
    for name, value in re.findall(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(\d+)\s*,?", m.group(1), re.M):
        out[int(value)] = name
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--charm-externs", type=Path, required=True)
    ap.add_argument("--vex-proof", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    v: list[str] = []
    source = a.charm_externs.read_text(encoding="utf-8-sig")
    if "//Based on CBuffer index" not in source:
        v.append("source_cbuffer_index_comment_missing")
    try:
        mapping = parse_tfx_scope(source)
    except Exception as ex:
        mapping = {}
        v.append(f"tfx_scope_parse:{ex!r}")
    if mapping != EXPECTED_SCOPE:
        v.append(f"tfx_scope_mapping_drift:{mapping!r}")

    vex = json.loads(a.vex_proof.read_text())
    if vex.get("status") != "D1_VEX_09A_NATIVE_STATE_CLOSURE_REPRODUCED":
        v.append("vex_native_state_not_exact")
    exact = vex.get("exact_findings") or {}
    cbs = exact.get("extended_user_data_constant_buffers") or []
    by_api = {int(x["api_slot"]): x for x in cbs}
    if set(by_api) != {0, 12, 13}:
        v.append(f"vex_cb_api_set:{sorted(by_api)}")
    if by_api.get(12, {}).get("start_register") != 32 or by_api.get(12, {}).get("spill_dword_offset") != 16:
        v.append("api12_binding_drift")
    if by_api.get(13, {}).get("start_register") != 36 or by_api.get(13, {}).get("spill_dword_offset") != 20:
        v.append("api13_binding_drift")
    if exact.get("api12_view_origin_delta") != "float3(api12[28]-attr4.x, api12[29]-attr4.y, api12[30]-attr4.z)":
        v.append("api12_dataflow_drift")
    if exact.get("api13_global_rgb_factor") != "api13[6] * api13[7]":
        v.append("api13_dataflow_drift")
    withheld = vex.get("withheld") or {}
    for k in ("api12_engine_producer", "api12_live_values", "api13_engine_producer", "api13_live_values"):
        if withheld.get(k) is not True:
            v.append(f"vex_unexpected_promotion:{k}")

    exact_ok = not v
    out = {
        "schema": "d1_ps4_cbuffer_scope_name_proof/v1",
        "status": "D1_PS4_CBUFFER_SCOPE_NAMES_CROSS_SOURCE_EXACT" if exact_ok else "D1_PS4_CBUFFER_SCOPE_NAMES_VIOLATIONS",
        "source": {
            "repository": "MontagueM/Charm",
            "commit": CHARM_COMMIT,
            "blob_sha1": CHARM_BLOB,
            "path": "Tiger/Schema/Shaders/TFX Bytecode/Externs.cs",
            "source_declaration": "TfxScope : byte // Based on CBuffer index",
            "mapping": {str(k): name for k, name in sorted(mapping.items())},
        },
        "promoted_scope_names": {
            "api12": {
                "source_name": "View",
                "cbuffer_index": 12,
                "retail_binding": by_api.get(12),
                "retail_consumption": "dwords 28..30 feed the attr4-relative normalized view-vector path",
                "name_status": "SOURCE_CORRELATED_EXACT",
                "runtime_writer": "WITHHELD",
                "backing_allocation": "WITHHELD",
                "live_values": "WITHHELD",
                "field_names": "WITHHELD",
            },
            "api13": {
                "source_name": "Frame",
                "cbuffer_index": 13,
                "retail_binding": by_api.get(13),
                "retail_consumption": "dwords 6 and 7 are independent multiplicative ancestors of final RGB",
                "name_status": "SOURCE_CORRELATED_EXACT",
                "runtime_writer": "WITHHELD",
                "backing_allocation": "WITHHELD",
                "live_values": "WITHHELD",
                "field_names": "WITHHELD",
            },
        } if exact_ok else {},
        "api15": {
            "present_in_source_tfx_scope_enum": 15 in mapping,
            "source_name": mapping.get(15),
            "name_status": "WITHHELD_NO_TFXSCOPE_INDEX_15",
        },
        "gates": {
            "api12_source_scope_name_closed": exact_ok,
            "api13_source_scope_name_closed": exact_ok,
            "api12_runtime_writer_closed": False,
            "api13_runtime_writer_closed": False,
            "api12_live_values_closed": False,
            "api13_live_values_closed": False,
            "api15_source_scope_name_closed": False,
        },
        "violations": v,
        "policy": (
            "The pinned source explicitly maps CBuffer indices to TfxScope names. Retail OrbShdr/API indices independently "
            "match those indices. This promotes only the source-level scope labels View/Frame for API12/API13. It does not "
            "promote producer identity, descriptor backing memory, live values, or individual field names."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0 if exact_ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
