#!/usr/bin/env python3
"""Resolve exact D1 PS4 pixel-material constant vectors for selected materials.

D1 ROI materials can store pixel-stage b0 vectors in two forms:
  * external PS Vector4 container at Material +0x32C (PS4 subtype 32:7), or
  * inline DynamicArray<Vec4> at Material +0x300 when the external hash is null.

This tool preserves both paths independently, including raw u32 words and source
provenance. It does not assign shader-semantic names to vector slots.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import d1_tower_map_schema_validate_v5 as v5
from d1_entity_model_probe import rel_array
from d1_material_decode import parse_material
from d1_world_material_constant_export import decode_vec4s, export_container

MAT_CLASS = "80801AD7"
NULLS = {"FFFFFFFF", "00000000"}


def norm(h: object) -> str:
    return str(h).upper().removeprefix("0X").zfill(8)


def inline_ps_vectors(material_bytes: bytes) -> dict:
    o = 0x300
    if len(material_bytes) < o + 16:
        return {"error": f"material too small for inline PS DynamicArray header: {len(material_bytes):#x}"}
    count, abs_off, elem_size = rel_array(material_bytes, o, 16)
    rel = struct.unpack_from("<q", material_bytes, o + 8)[0]
    end = abs_off + count * elem_size
    row = {
        "header_offset": o,
        "count": count,
        "element_size": elem_size,
        "relative_pointer": rel,
        "absolute_offset": abs_off,
        "payload_bytes": count * elem_size,
        "header_hex": material_bytes[o : o + 16].hex(),
    }
    if abs_off < 0 or end < abs_off or end > len(material_bytes):
        row["error"] = (
            f"inline PS vec4 array out of bounds: off={abs_off:#x}, "
            f"count={count}, elem={elem_size:#x}, end={end:#x}, len={len(material_bytes):#x}"
        )
        return row
    payload = material_bytes[abs_off:end]
    row["payload_hex"] = payload.hex()
    row["vectors"] = decode_vec4s(payload)
    return row


def resolve_material(c, material_hash: str) -> dict:
    mh = norm(material_hash)
    meta = c.entry_meta(mh)
    b, src = c.payload(mh)
    row = {"material": mh, "meta": meta, "source": src}
    if meta is None:
        row["error"] = "material metadata unavailable"
        return row
    if norm(meta.get("reference", "")) != MAT_CLASS:
        row["error"] = f"unexpected material class {norm(meta.get('reference', ''))}; expected {MAT_CLASS}"
        return row
    if b is None:
        row["error"] = "material payload unavailable"
        return row

    try:
        p = parse_material(b, "PS4")
    except Exception as ex:
        row["error"] = f"parse_material failed: {ex!r}"
        return row

    psc = norm(p["ps_vector4_container"])
    inline = inline_ps_vectors(b)
    external = None
    if psc not in NULLS:
        external = export_container(c, psc)

    inline_count = int(inline.get("count", 0)) if not inline.get("error") else None
    external_ok = bool(external is not None and not external.get("error"))
    if psc not in NULLS and inline_count == 0:
        mode = "external"
    elif psc in NULLS and inline_count and inline_count > 0:
        mode = "inline"
    elif psc in NULLS and inline_count == 0:
        mode = "none"
    else:
        mode = "mixed_or_unexpected"

    row.update(
        {
            "actual_file_size": len(b),
            "pixel_shader": norm(p["pixel_shader"]),
            "vertex_shader": norm(p["vertex_shader"]),
            "ps_texture_tags": p["ps_textures"]["items"],
            "ps_vector4_container": psc,
            "storage_mode": mode,
            "inline": inline,
            "external": external,
            "external_resolved": external_ok,
            "material_constant_window_2f0_340_hex": b[0x2F0 : min(len(b), 0x340)].hex(),
        }
    )
    if inline.get("error"):
        row["error"] = inline["error"]
    elif psc not in NULLS and external is not None and external.get("error"):
        row["error"] = f"external constant container unresolved: {external['error']}"
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", type=Path, action="append", required=True)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--tag-hash", action="append", required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    c = v5.v3.base.Corpus([p.resolve() for p in a.snapshot], a.runtime.resolve())
    materials = {norm(h): resolve_material(c, h) for h in a.tag_hash}
    errors = [h for h, r in materials.items() if r.get("error")]
    modes: dict[str, int] = {}
    for r in materials.values():
        m = r.get("storage_mode", "error")
        modes[m] = modes.get(m, 0) + 1

    out = {
        "schema_version": 1,
        "status": "D1_PS_MATERIAL_CONSTANTS_EXACT" if not errors else "D1_PS_MATERIAL_CONSTANTS_PARTIAL",
        "selected_material_count": len(materials),
        "storage_mode_counts": modes,
        "error_count": len(errors),
        "error_materials": errors,
        "materials": materials,
        "policy": (
            "Exact PS4 Material +0x300 inline DynamicArray<Vec4> and +0x32C external subtype-32:7 "
            "resolution. Raw vectors are preserved; shader-semantic roles are not inferred here."
        ),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in ("status", "selected_material_count", "storage_mode_counts", "error_count")}, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
