#!/usr/bin/env python3
"""Prove that PS 8087670E's target material-local TFX does not source API15/t4.

The two remaining Tower materials (808766B2/808766B6) use an identical complete
24-byte PS TFX stream. It contains only six D1 opcode-0x49 one-byte records paired
with PopTemp slots 33..38. No PushExternInput* opcode occurs.

This is an exclusion proof only. D1 opcode 0x49 remains semantically UNKNOWN:
Charm labels it Unk49 and source lineage does not justify renaming it. Therefore
this tool does not claim what values are stored into temps 33..38. It proves only
that the material-local TFX stream itself performs no extern read, including no
source-pinned ExternIndex 87/GearDye read.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

MATERIALS = ("808766B2", "808766B6")
SHADER = "8087670E"
EXPECTED_TFX = bytes.fromhex("490047214901472249024723490347244904472549054726")
EXPECTED_OPS = [
    ("Unk49", 0), ("PopTemp", 33),
    ("Unk49", 1), ("PopTemp", 34),
    ("Unk49", 2), ("PopTemp", 35),
    ("Unk49", 3), ("PopTemp", 36),
    ("Unk49", 4), ("PopTemp", 37),
    ("Unk49", 5), ("PopTemp", 38),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--material-state", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    d = json.loads(a.material_state.read_text())
    v: list[str] = []
    if d.get("status") != "D1_MATERIAL_STAGE_STATE_EXACT" or d.get("violations"):
        v.append("material_state_not_exact")
    if int(d.get("resolved_material_count", -1)) != 85:
        v.append(f"resolved_material_count:{d.get('resolved_material_count')}")
    if d.get("tfx_extern_histogram") != {"Frame": 82}:
        v.append(f"whole_scope_extern_histogram:{d.get('tfx_extern_histogram')!r}")

    rows = []
    for mh in MATERIALS:
        m = (d.get("materials") or {}).get(mh)
        if not m:
            v.append(f"{mh}:material_missing")
            continue
        ps = m.get("ps") or {}
        if ps.get("shader") != SHADER:
            v.append(f"{mh}:shader:{ps.get('shader')}")
        raw_hex = ((ps.get("tfx_bytecode") or {}).get("bytes_hex") or "")
        try:
            raw = bytes.fromhex(raw_hex)
        except ValueError:
            raw = b""
            v.append(f"{mh}:invalid_tfx_hex")
        if raw != EXPECTED_TFX:
            v.append(f"{mh}:tfx_bytes_drift:{raw_hex}")
        dis = ps.get("tfx_disassembly") or {}
        if dis.get("complete") is not True or dis.get("unknown_opcodes"):
            v.append(f"{mh}:tfx_disassembly_not_complete")
        ops = []
        extern_ops = []
        for op in dis.get("ops") or []:
            name = op.get("name")
            if name == "Unk49":
                arg = (op.get("operand_bytes") or [None])[0]
            elif name == "PopTemp":
                arg = op.get("slot_or_element")
            else:
                arg = None
            ops.append((name, arg))
            if "extern_name" in op or str(name).startswith("PushExternInput"):
                extern_ops.append(op)
        if ops != EXPECTED_OPS:
            v.append(f"{mh}:op_sequence_drift:{ops!r}")
        if extern_ops:
            v.append(f"{mh}:unexpected_extern_ops:{extern_ops!r}")
        rows.append({
            "material": mh,
            "pixel_shader": ps.get("shader"),
            "tfx_bytes": len(raw),
            "tfx_sha256": hashlib.sha256(raw).hexdigest(),
            "tfx_hex": raw.hex().upper(),
            "ops": [{"name": n, "operand": x} for n, x in ops],
            "extern_read_count": len(extern_ops),
        })

    exact = not v
    out = {
        "schema": "d1_ps_8087670e_tfx_extern_exclusion/v1",
        "status": "D1_PS_8087670E_MATERIAL_TFX_EXTERN_EXCLUSION_EXACT" if exact else "D1_PS_8087670E_MATERIAL_TFX_EXTERN_EXCLUSION_VIOLATIONS",
        "pixel_shader": SHADER,
        "scope_materials": list(MATERIALS),
        "whole_three_npc_material_denominator": 85,
        "whole_three_npc_tfx_extern_histogram": d.get("tfx_extern_histogram"),
        "target_materials": rows,
        "target_tfx_identical": exact and len({x["tfx_sha256"] for x in rows}) == 1,
        "target_tfx_extern_read_count": sum(x["extern_read_count"] for x in rows),
        "excluded_material_local_producers": [
            "TFX PushExternInputFloat/Vec4/Mat4/U64/U32/U64Unknown",
            "TFX ExternIndex 87 (GearDye)",
        ] if exact else [],
        "remaining_runtime_frontier": {
            "api15_c0_w_source": "NON_MATERIAL_TFX_RUNTIME_PRODUCER_REQUIRED" if exact else "UNRESOLVED",
            "t4_resource_source": "NON_MATERIAL_RESOURCE_TABLE_PRODUCER_REQUIRED" if exact else "UNRESOLVED",
        },
        "opcode_49": {
            "name": "Unk49",
            "operand_width_bytes": 1,
            "semantic": "WITHHELD",
            "reason": "Pinned D1 Charm source labels opcode 0x49 Unk49; adjacency/pattern is not semantic proof.",
        },
        "violations": v,
        "policy": (
            "A complete absence of extern-read opcodes excludes material-local TFX extern injection for the two target "
            "materials. It does not reveal the meaning of Unk49, API15 c0.w, or the runtime/default t4 binding."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0 if exact else 2


if __name__ == "__main__":
    raise SystemExit(main())
