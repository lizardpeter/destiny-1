#!/usr/bin/env python3
"""Census raw D1 PS4 material header state without assigning semantics.

This tool intentionally treats the compact ROI material header at +0x08..+0x27
as opaque state.  It inventories exact shipped bytes and correlates them only with
other serialized structures (shader identities and constant-storage form).  It does
not label any bit as blend, cull, depth, alpha-test, or pass state.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import d1_tower_map_schema_validate_v5 as v5
from d1_material_decode import parse_material

MAT_CLASS = "80801AD7"
NULLS = {"FFFFFFFF", "00000000"}
TARGET_PS = "809DCD66"
PEER_PS = "80CA0BE9"


def norm(x: object) -> str:
    return str(x).upper().removeprefix("0X").zfill(8)


def header_state(b: bytes) -> dict:
    if len(b) < 0x28:
        raise ValueError(f"material too short for state header: {len(b):#x}")
    window = b[0x08:0x28]
    dwords = [struct.unpack_from("<I", b, o)[0] for o in range(0x08, 0x28, 4)]
    return {
        "window_offset": "0x08",
        "window_end_exclusive": "0x28",
        "window_hex": window.hex().upper(),
        "dwords": {f"0x{o:02X}": f"{v:08X}" for o, v in zip(range(0x08, 0x28, 4), dwords)},
        "unk08": f"{dwords[0]:08X}",
        "unk0c": f"{dwords[1]:08X}",
        "unk10": f"{dwords[2]:08X}",
        "unk20_u16": struct.unpack_from("<H", b, 0x20)[0],
        "unk20_hex": f"{struct.unpack_from('<H', b, 0x20)[0]:04X}",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", type=Path, action="append", required=True)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    c = v5.v3.base.Corpus([p.resolve() for p in a.snapshot], a.runtime.resolve())
    hashes = sorted(
        h for h, occ in c.occ.items()
        if any(norm(x[3].get("reference", "")) == MAT_CLASS for x in occ)
    )

    rows = []
    violations = []
    for h in hashes:
        meta = c.entry_meta(h)
        b, src = c.payload(h)
        if b is None:
            violations.append({"material": h, "error": "payload_unavailable"})
            continue
        try:
            p = parse_material(b, "PS4")
            st = header_state(b)
        except Exception as ex:
            violations.append({"material": h, "error": repr(ex)})
            continue
        psc = norm(p["ps_vector4_container"])
        rows.append({
            "material": h,
            "source": src,
            "meta": meta,
            "state": st,
            "vertex_shader": norm(p["vertex_shader"]),
            "pixel_shader": norm(p["pixel_shader"]),
            "ps_vector4_container": psc,
            "ps_external_vector_present": psc not in NULLS,
            "ps_texture_count": int(p["ps_textures"]["count"]),
            "ps_tfx_bytes": int(p["ps_tfx_bytecode"]["count"]),
        })

    by_window = Counter(r["state"]["window_hex"] for r in rows)
    by_unk0c = Counter(r["state"]["unk0c"] for r in rows)
    by_unk20 = Counter(r["state"]["unk20_hex"] for r in rows)
    by_ps = Counter(r["pixel_shader"] for r in rows)
    relation = Counter(
        (r["state"]["unk0c"], "external" if r["ps_external_vector_present"] else "inline_only")
        for r in rows
    )

    ps_groups: dict[str, dict] = {}
    grouped = defaultdict(list)
    for r in rows:
        grouped[r["pixel_shader"]].append(r)
    for ps, grp in sorted(grouped.items()):
        ps_groups[ps] = {
            "material_count": len(grp),
            "state_window_histogram": dict(Counter(x["state"]["window_hex"] for x in grp)),
            "unk0c_histogram": dict(Counter(x["state"]["unk0c"] for x in grp)),
            "unk20_histogram": dict(Counter(x["state"]["unk20_hex"] for x in grp)),
            "external_vector_histogram": dict(Counter("external" if x["ps_external_vector_present"] else "inline_only" for x in grp)),
        }

    target = [r for r in rows if r["pixel_shader"] == TARGET_PS]
    peer = [r for r in rows if r["pixel_shader"] == PEER_PS]
    target_relation = Counter(
        (r["state"]["unk0c"], "external" if r["ps_external_vector_present"] else "inline_only")
        for r in target
    )

    out = {
        "schema_version": 1,
        "status": "D1_PS4_MATERIAL_STATE_CENSUS_COMPLETE" if not violations else "D1_PS4_MATERIAL_STATE_CENSUS_PARTIAL",
        "material_class": MAT_CLASS,
        "material_count": len(rows),
        "candidate_hash_count": len(hashes),
        "violations": violations,
        "histograms": {
            "state_window": dict(by_window),
            "unk0c": dict(by_unk0c),
            "unk20": dict(by_unk20),
            "pixel_shader": dict(by_ps),
            "unk0c_x_ps_constant_storage": {f"{a}|{b}": n for (a, b), n in sorted(relation.items())},
        },
        "pixel_shader_groups": ps_groups,
        "target_809DCD66": {
            "material_count": len(target),
            "unk0c_histogram": dict(Counter(r["state"]["unk0c"] for r in target)),
            "unk20_histogram": dict(Counter(r["state"]["unk20_hex"] for r in target)),
            "state_window_histogram": dict(Counter(r["state"]["window_hex"] for r in target)),
            "unk0c_x_ps_constant_storage": {f"{a}|{b}": n for (a, b), n in sorted(target_relation.items())},
            "materials": target,
        },
        "peer_80CA0BE9": {
            "material_count": len(peer),
            "materials": peer,
        },
        "materials": rows,
        "policy": (
            "Raw PS4 ROI material-header bytes only. Correlations with shader identity and PS constant-storage form "
            "are reported mechanically; no render-state semantic is assigned to any header field or bit."
        ),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({
        "status": out["status"],
        "material_count": out["material_count"],
        "state_window_count": len(by_window),
        "unk0c_histogram": out["histograms"]["unk0c"],
        "unk20_histogram": out["histograms"]["unk20"],
        "target_809DCD66": {k: out["target_809DCD66"][k] for k in ("material_count", "unk0c_histogram", "unk20_histogram", "unk0c_x_ps_constant_storage")},
        "peer_80CA0BE9_material_count": len(peer),
        "violations": violations,
    }, indent=2))
    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
