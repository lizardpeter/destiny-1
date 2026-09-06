#!/usr/bin/env python3
"""Resolve and structurally probe D1 PS4 pixel-material vector data.

The ROI Material PS region contains several independent structures: TFX bytecode,
samplers, TFX-expression data, GPU constant-buffer data, and an optional external
PS Vector4 container at +0x32C.  Earlier tooling incorrectly treated +0x300 and
+0x32C as mutually exclusive storage modes.  Retail 809DCD66 materials prove that
both can coexist and that the external 32:7 payload may be a byte-identical mirror.

This tool therefore preserves raw structure first.  It decodes the known +0x300
DynamicArray<Vec4>, resolves +0x32C when present, compares both payloads exactly,
and emits bounded DynamicArray probes across the surrounding PS control region.
No semantic name is assigned to an unresolved array solely from its offset.
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


def array_probe(material_bytes: bytes, o: int, elem_size: int = 16) -> dict:
    row = {"header_offset": o, "element_size_candidate": elem_size}
    if o < 0 or o + 16 > len(material_bytes):
        row["error"] = "header out of bounds"
        return row
    count = struct.unpack_from("<I", material_bytes, o)[0]
    reserved = struct.unpack_from("<I", material_bytes, o + 4)[0]
    rel = struct.unpack_from("<q", material_bytes, o + 8)[0]
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
    a300 = vec4_array(b, 0x300)
    external = export_container(c, psc) if psc not in NULLS else None
    external_ok = bool(external is not None and not external.get("error"))

    a300_hex = a300.get("payload_hex") if not a300.get("error") else None
    external_hex = None
    if external_ok:
        external_hex = "".join(
            "".join(struct.pack("<I", int(x, 16)).hex() for x in v["u32_hex"])
            for v in external.get("vectors", [])
        )
    mirror_equal = None if external is None or a300_hex is None or not external_ok else (a300_hex == external_hex)

    if external is None:
        relation = "array_300_only"
    elif external_ok and mirror_equal:
        relation = "array_300_plus_external_identical"
    elif external_ok:
        relation = "array_300_plus_external_different"
    else:
        relation = "array_300_plus_external_unresolved"

    # Keep the complete region plus a deliberately redundant 8-byte-step scan.
    # The scan is forensic: only explicitly parsed structures receive semantic names.
    probe_offsets = list(range(0x2D0, 0x330, 8))
    probes = {f"{o:03X}": array_probe(b, o, 16) for o in probe_offsets}

    row.update(
        {
            "actual_file_size": len(b),
            "pixel_shader": norm(p["pixel_shader"]),
            "vertex_shader": norm(p["vertex_shader"]),
            "ps_texture_tags": p["ps_textures"]["items"],
            "ps_tfx_bytecode": p["ps_tfx_bytecode"],
            "ps_vector4_container": psc,
            "array_300": a300,
            "external": external,
            "external_resolved": external_ok,
            "array_300_external_byte_identical": mirror_equal,
            "vector_storage_relation": relation,
            "dynamic_array_candidate_scan": probes,
            "material_ps_control_window_2d0_340_hex": b[0x2D0 : min(len(b), 0x340)].hex(),
        }
    )
    if a300.get("error"):
        row["error"] = a300["error"]
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
        "schema_version": 2,
        "status": "D1_PS_MATERIAL_VECTOR_PROBE_EXACT" if not errors else "D1_PS_MATERIAL_VECTOR_PROBE_PARTIAL",
        "selected_material_count": len(materials),
        "vector_storage_relation_counts": relations,
        "error_count": len(errors),
        "error_materials": errors,
        "materials": materials,
        "policy": (
            "Raw PS4 ROI material-vector structure. +0x300 is decoded structurally as DynamicArray<Vec4>; "
            "+0x32C external subtype-32:7 is resolved independently and byte-compared. Surrounding array scans "
            "are forensic candidates only until retail/schema dataflow closes their semantic role."
        ),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in ("status", "selected_material_count", "vector_storage_relation_counts", "error_count")}, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
