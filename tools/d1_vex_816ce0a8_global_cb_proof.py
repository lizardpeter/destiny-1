#!/usr/bin/env python3
"""Fail-closed global constant-buffer provenance proof for D1 PS4 PS 816CE0A8.

Consumes the exact retail shader extraction report and CLRX/GFX700 disassembly.
It proves only structural/API-indexed facts:
  * spilled ImmConstBuffer API0/API12/API13 descriptor provenance;
  * API12 dwords 28..30 feed the attr4-relative normalized view vector;
  * API0 dword 8 scales the centered first texture sample before UV displacement;
  * API13 dwords 6 and 7 are independent multiplicative ancestors of all RGB
    lanes immediately before MRT0 packing.

No engine-facing name, runtime producer, live value, address, or opacity meaning
is assigned to API12/API13.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

SHADER = "816CE0A8"
NATIVE = "816CE0AE"
GCN_SHA256 = "8e0e11cd37896f14873d86215ddec89dd5be34d457e33f6b734b7c3fd0e126fd"
CODE_BYTES = 516
INLINE_USER_SGPR_DWORDS = 16
EXPECTED_USAGE = [
    ("PtrExtendedUserData", 1, 2),
    ("ImmResource", 0, 4),
    ("ImmSampler", 1, 12),
    ("ImmResource", 1, 16),
    ("ImmSampler", 2, 24),
    ("ImmConstBuffer", 0, 28),
    ("ImmConstBuffer", 12, 32),
    ("ImmConstBuffer", 13, 36),
]

ANCHORS = [
    "s_load_dwordx4 s[4:7], s[2:3], 0x10",
    "s_buffer_load_dwordx4 s[4:7], s[4:7], 0x1c",
    "v_sub_f32 v5, s6, v5",
    "v_sub_f32 v6, s5, v6",
    "v_sub_f32 v7, s4, v7",
    "s_load_dwordx4 s[4:7], s[2:3], 0xc",
    "s_buffer_load_dword s0, s[4:7], 0x8",
    "v_add_f32 v1, -0.5, v4",
    "v_mul_f32 v1, s0, v1",
    "s_load_dwordx4 s[0:3], s[2:3], 0x14",
    "s_buffer_load_dwordx2 s[0:1], s[0:3], 0x6",
    "v_mul_f32 v1, s1, v1",
    "v_mul_f32 v4, s1, v4",
    "v_mul_f32 v2, s1, v2",
    "v_mul_f32 v1, s0, v1",
    "v_mul_f32 v4, s0, v4",
    "v_mul_f32 v2, s0, v2",
    "v_mov_b32 v3, 0",
    "v_cvt_pkrtz_f16_f32 v1, v1, v2",
    "v_cvt_pkrtz_f16_f32 v0, v0, v3",
    "exp mrt0, v1, v1, v0, v0 done compr vm",
]


def normalize_asm(line: str) -> str:
    line = re.sub(r"/\*.*?\*/", "", line)
    return re.sub(r"\s+", " ", line.strip())


def code_bytes_from_clrx(text: str) -> bytes:
    rows = []
    for line in text.splitlines():
        m = re.match(r"/\*([0-9A-Fa-f]{12}):\s*([0-9A-Fa-f ]+)\*/", line.strip())
        if not m:
            continue
        addr = int(m.group(1), 16)
        raw = b"".join(bytes.fromhex(w)[::-1] for w in m.group(2).split())
        rows.append((addr, raw))
    if not rows:
        raise ValueError("no CLRX hexcode rows")
    rows.sort()
    out = bytearray()
    if rows[0][0] != 0:
        raise ValueError(f"first GCN address {rows[0][0]:#x} != 0")
    for addr, raw in rows:
        if addr != len(out):
            raise ValueError(f"non-contiguous GCN at {addr:#x}, expected {len(out):#x}")
        out.extend(raw)
    return bytes(out)


def ordered_anchors(text: str, violations: list[str]) -> list[str]:
    lines = [normalize_asm(x) for x in text.splitlines()]
    lines = [x for x in lines if x]
    cursor = 0
    found = []
    for anchor in ANCHORS:
        hit = None
        for i in range(cursor, len(lines)):
            if lines[i] == anchor:
                hit = i
                break
        if hit is None:
            violations.append(f"missing_or_out_of_order_anchor:{anchor}")
            continue
        found.append(lines[hit])
        cursor = hit + 1
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--extract-report", type=Path, required=True)
    ap.add_argument("--disassembly", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    extract = json.loads(a.extract_report.read_text())
    asm_text = a.disassembly.read_text(errors="replace")
    violations: list[str] = []

    if extract.get("status") != "D1_REMOTE_PS4_SHADER_EXTRACT_COMPLETE" or extract.get("violations"):
        violations.append("extract_report_not_exact")
    rows = extract.get("shaders") or []
    if len(rows) != 1:
        violations.append(f"shader_row_count:{len(rows)}")
        row = {}
    else:
        row = rows[0]
    if row.get("shader") != SHADER:
        violations.append(f"shader_identity:{row.get('shader')}")
    if row.get("native_payload_hash") != NATIVE:
        violations.append(f"native_identity:{row.get('native_payload_hash')}")
    if (row.get("code") or {}).get("bytes") != CODE_BYTES:
        violations.append(f"code_bytes:{(row.get('code') or {}).get('bytes')}")
    if (row.get("code") or {}).get("sha256") != GCN_SHA256:
        violations.append(f"extract_gcn_sha256:{(row.get('code') or {}).get('sha256')}")

    usage = [
        (x.get("usage_name"), int(x.get("api_slot")), int(x.get("start_register")))
        for x in ((row.get("usage") or {}).get("slots") or [])
    ]
    if usage != EXPECTED_USAGE:
        violations.append(f"usage_layout_drift:{usage!r}")

    try:
        code = code_bytes_from_clrx(asm_text)
        sha = hashlib.sha256(code).hexdigest()
    except Exception as ex:
        code = b""
        sha = None
        violations.append(f"clrx_code_reconstruction:{ex!r}")
    if len(code) != CODE_BYTES:
        violations.append(f"clrx_code_bytes:{len(code)}")
    if sha != GCN_SHA256:
        violations.append(f"clrx_gcn_sha256:{sha}")

    cb_usage = {api: start for name, api, start in usage if name == "ImmConstBuffer"}
    expected_cb_starts = {0: 28, 12: 32, 13: 36}
    if cb_usage != expected_cb_starts:
        violations.append(f"constant_buffer_start_registers:{cb_usage!r}")
    spill = {api: start - INLINE_USER_SGPR_DWORDS for api, start in cb_usage.items()}
    if spill != {0: 0x0C, 12: 0x10, 13: 0x14}:
        violations.append(f"extended_user_data_spill_offsets:{spill!r}")

    found = ordered_anchors(asm_text, violations)

    out = {
        "schema_version": 1,
        "status": "D1_VEX_816CE0A8_GLOBAL_CB_DATAFLOW_EXACT" if not violations else "D1_VEX_816CE0A8_GLOBAL_CB_DATAFLOW_PARTIAL",
        "shader": SHADER,
        "native_shader": NATIVE,
        "gcn_bytes": len(code),
        "gcn_sha256": sha,
        "orbshdr_usage": [
            {"usage_name": n, "api_slot": api, "start_register": start}
            for n, api, start in usage
        ],
        "extended_user_data": {
            "pointer_registers": "s[2:3]",
            "inline_user_sgpr_dword_count": INLINE_USER_SGPR_DWORDS,
            "spill_rule": "extended_user_data_dword_offset = start_register - 16",
            "constant_buffers": [
                {"api_slot": api, "start_register": expected_cb_starts[api], "extended_user_data_dword_offset": spill.get(api)}
                for api in (0, 12, 13)
            ],
        },
        "api12_provenance": {
            "descriptor_spill_offset_dwords": 0x10,
            "descriptor_loaded_into": "s[4:7]",
            "buffer_load": "dwords 28..31 -> s[4:7]",
            "proven_consumed_components": {
                "api12[28]": "subtracted from attr4.x",
                "api12[29]": "subtracted from attr4.y",
                "api12[30]": "subtracted from attr4.z",
            },
            "proven_arithmetic_role": "forms the attr4-relative xyz vector that is normalized before the view-dependent UV displacement path",
            "engine_producer": None,
            "live_values": None,
        },
        "api0_local_crosscheck": {
            "descriptor_spill_offset_dwords": 0x0C,
            "descriptor_loaded_into": "s[4:7]",
            "dword8_destination": "s0",
            "proven_arithmetic": "(first texture scalar - 0.5) * api0[8] feeds the view-dependent UV displacement",
        },
        "api13_provenance": {
            "descriptor_spill_offset_dwords": 0x14,
            "descriptor_loaded_into": "s[0:3]",
            "buffer_load": "dwords 6..7 -> s0,s1",
            "rgb_dataflow": [
                "RGB working lanes are each multiplied by api13[7] (s1)",
                "the same three lanes are then each multiplied by api13[6] (s0)",
                "both scalars are therefore independent multiplicative ancestors of final MRT0 RGB",
            ],
            "output_alpha": "exact zero is packed separately; api13[6:7] are not opacity inputs in this shader",
            "engine_producer": None,
            "live_values": None,
        },
        "proven_equations": {
            "global_rgb_factor": "api13[6] * api13[7]",
            "view_origin_delta": "float3(api12[28]-attr4.x, api12[29]-attr4.y, api12[30]-attr4.z)",
            "centered_height_scale": "(t0_scalar - 0.5) * api0[8]",
        },
        "anchors": found,
        "gates": {
            "api0_descriptor_binding_closed": not violations,
            "api12_descriptor_binding_closed": not violations,
            "api12_consumed_dword_indices_closed": not violations,
            "api13_descriptor_binding_closed": not violations,
            "api13_consumed_dword_indices_closed": not violations,
            "api13_rgb_multiplicative_dataflow_closed": not violations,
            "api12_engine_producer_closed": False,
            "api13_engine_producer_closed": False,
            "api12_live_values_closed": False,
            "api13_live_values_closed": False,
        },
        "violations": violations,
        "policy": (
            "Exact retail OrbShdr usage + exact CLRX/GFX700 instruction provenance only. "
            "API12/API13 remain source-level slot names; no Bungie engine field name, producer, live value, address, exposure/brightness semantic, or opacity semantic is inferred."
        ),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
