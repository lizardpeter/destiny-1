#!/usr/bin/env python3
"""Resolve exact D1 PS4 ROI pixel-material vector structures.

Retail Tower evidence plus the pinned ROI material schema closes the pixel-stage
layout used here:

  +0x2D0  PS TFX bytecode DynamicArray<u8>
  +0x2E0  PS TFX private constants DynamicArray<Vec4>
  +0x2F0  PS sampler DynamicArray<16-byte tag records>
  +0x300  PS CBuffers DynamicArray<Vec4>
  +0x32C  optional external PS Vector4 container

For the 24 visible 809DCD66 materials, +0x300 is always seven Vec4s.  Ten also
have +0x32C subtype-32:7 payloads that are byte-identical mirrors of those seven
vectors; fourteen have no external mirror.  The +0x2E0 count independently tracks
the highest constant referenced by each TFX program.

Raw u32 words and source provenance remain canonical.  This module does not infer
shader-semantic meanings for individual vector elements or material state words
beyond structures closed by retail/schema evidence.
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
from d1_material_decode import parse_material
from d1_world_material_constant_export import decode_vec4s, export_container

MAT_CLASS = "80801AD7"
NULLS = {"FFFFFFFF", "00000000"}


def norm(h: object) -> str:
    return str(h).upper().removeprefix("0X").zfill(8)


def array_probe(material_bytes: bytes, o: int, elem_size: int = 16) -> dict:
    row = {"header_offset": o, "element_size_candidate": elem_size}
    if o < 0 or o + 16 > len(material_bytes):
        row["error"] = "header out of bounds"
        return row
    count = struct.unpack_from("<I", material_bytes, o)[0]
    reserved = struct.unpack_from("<I", material_bytes, o + 4)[0]
    rel = struct.unpack_from("<q", material_bytes, o + 8)[0]
    # Charm DynamicArray<T>: RelativePointer is based at pointer field o+8 and
    # carries the engine's +0x10 extra offset.
    abs_off = (o + 8) + rel + 0x10
    end = abs_off + count * elem_size
    row.update(
        {
            "count": count,
            "reserved_u32": reserved,
            "relative_pointer": rel,
            "absolute_offset": abs_off,
            "candidate_end": end,
            "header_hex": material_bytes[o : o + 16].hex(),
            "candidate_in_bounds": bool(0 <= abs_off <= end <= len(material_bytes)),
        }
    )
    if row["candidate_in_bounds"] and count <= 256:
        payload = material_bytes[abs_off:end]
        row["candidate_payload_hex"] = payload.hex()
        if elem_size == 16:
            try:
                row["candidate_vectors"] = decode_vec4s(payload)
            except Exception as ex:
                row["candidate_decode_error"] = repr(ex)
    return row


def vec4_array(material_bytes: bytes, o: int) -> dict:
    p = array_probe(material_bytes, o, 16)
    if p.get("error"):
        return p
    if not p.get("candidate_in_bounds"):
        p["error"] = (
            f"vec4 array out of bounds: off={p.get('absolute_offset'):#x}, "
            f"count={p.get('count')}, end={p.get('candidate_end'):#x}, len={len(material_bytes):#x}"
        )
        return p
    p["vectors"] = p.pop("candidate_vectors", [])
    p["payload_hex"] = p.pop("candidate_payload_hex", "")
    p["payload_bytes"] = int(p.get("count", 0)) * 16
    return p


def _external_payload_hex(external: dict | None) -> str | None:
    if not external or external.get("error"):
        return None
    return "".join(
        "".join(struct.pack("<I", int(x, 16)).hex() for x in v["u32_hex"])
        for v in external.get("vectors", [])
    )


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

    ps_tfx_constants = vec4_array(b, 0x2E0)
    ps_cbuffers = vec4_array(b, 0x300)
    psc = norm(p["ps_vector4_container"])
    external = export_container(c, psc) if psc not in NULLS else None
    external_ok = bool(external is not None and not external.get("error"))

    cb_hex = ps_cbuffers.get("payload_hex") if not ps_cbuffers.get("error") else None
    ext_hex = _external_payload_hex(external)
    mirror_equal = None if external is None or cb_hex is None or ext_hex is None else (cb_hex == ext_hex)

    if external is None:
        relation = "ps_cbuffers_only"
    elif external_ok and mirror_equal:
        relation = "ps_cbuffers_plus_external_identical"
    elif external_ok:
        relation = "ps_cbuffers_plus_external_different"
    else:
        relation = "ps_cbuffers_plus_external_unresolved"

    probe_offsets = list(range(0x2D0, 0x330, 8))
    probes = {f"{o:03X}": array_probe(b, o, 16) for o in probe_offsets}

    row.update(
        {
            "actual_file_size": len(b),
            "material_state_raw": {
                "unk08_hex": p["unk08"],
                "unk0c_hex": p["unk0c"],
                "unk10_hex": p["unk10"],
                "unk20_u16": p["unk20"],
                "unk20_hex": p["unk20_hex"],
            },
            "pixel_shader": norm(p["pixel_shader"]),
            "vertex_shader": norm(p["vertex_shader"]),
            "ps_texture_tags": p["ps_textures"]["items"],
            "ps_tfx_bytecode": p["ps_tfx_bytecode"],
            "ps_tfx_constants": ps_tfx_constants,
            "ps_cbuffers": ps_cbuffers,
            # Compatibility alias for reports emitted before the offset closure.
            "array_300": ps_cbuffers,
            "ps_vector4_container": psc,
            "external": external,
            "external_resolved": external_ok,
            "ps_cbuffers_external_byte_identical": mirror_equal,
            "array_300_external_byte_identical": mirror_equal,
            "vector_storage_relation": relation,
            "dynamic_array_candidate_scan": probes,
            "material_ps_control_window_2d0_340_hex": b[0x2D0 : min(len(b), 0x340)].hex(),
        }
    )
    if ps_tfx_constants.get("error"):
        row["error"] = f"PS TFX constants: {ps_tfx_constants['error']}"
    elif ps_cbuffers.get("error"):
        row["error"] = f"PS CBuffers: {ps_cbuffers['error']}"
    elif external is not None and not external_ok:
        row["error"] = f"external constant container unresolved: {external.get('error')}"
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
    relations: dict[str, int] = {}
    for r in materials.values():
        k = r.get("vector_storage_relation", "error")
        relations[k] = relations.get(k, 0) + 1

    out = {
        "schema_version": 4,
        "status": "D1_PS_MATERIAL_VECTOR_LAYOUT_EXACT" if not errors else "D1_PS_MATERIAL_VECTOR_LAYOUT_PARTIAL",
        "selected_material_count": len(materials),
        "vector_storage_relation_counts": relations,
        "error_count": len(errors),
        "error_materials": errors,
        "materials": materials,
        "closed_offsets": {
            "material_unk20": "0x20:u16",
            "ps_tfx_bytecode": "0x2D0",
            "ps_tfx_constants": "0x2E0",
            "ps_samplers": "0x2F0",
            "ps_cbuffers": "0x300",
            "ps_vector4_container": "0x32C",
        },
        "policy": (
            "Exact PS4 ROI material structures: raw state words are preserved without semantic naming; "
            "+0x2E0 PS TFX constants and +0x300 PS CBuffers are decoded independently; +0x32C subtype-32:7 "
            "is resolved and byte-compared to PS CBuffers. Raw values and provenance remain canonical."
        ),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in ("status", "selected_material_count", "vector_storage_relation_counts", "error_count", "closed_offsets")}, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
