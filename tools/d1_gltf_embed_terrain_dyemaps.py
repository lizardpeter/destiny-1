#!/usr/bin/env python3
"""Embed exact STerrain dyemap textures and per-part bindings into a terrain GLB.

Input geometry already contains source-selected terrain parts and ordinary material
texture resources.  This adapter adds the independent STerrain.MeshGroups dyemap
resources produced by ``d1_texture_tag_export.py`` and annotates each exact terrain
part node with:
  * source and effective dyemap TagHash;
  * embedded glTF texture index for the effective dyemap;
  * GroupIndex and Charm's generated GroupIndex%4 selector RGBA;
  * exact terrain/material/part provenance.

The selector is metadata, not COLOR_0, because generic glTF PBR would otherwise
multiply base color by a D1 shader-control value.  No dyemap channel semantics or
blending equation is invented here.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
from pathlib import Path

from PIL import Image

from d1_gltf_layer_merge import read_glb, write_glb


def hbytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def hfile(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def append_blob(doc: dict, bindata: bytes, payload: bytes, name: str) -> tuple[int, bytes]:
    aligned = (len(bindata) + 3) & ~3
    if aligned != len(bindata):
        bindata += b"\0" * (aligned - len(bindata))
    off = len(bindata)
    idx = len(doc.setdefault("bufferViews", []))
    doc["bufferViews"].append({"buffer": 0, "byteOffset": off, "byteLength": len(payload), "name": name})
    return idx, bindata + payload


def verify_png(data: bytes) -> tuple[int, int]:
    with Image.open(io.BytesIO(data)) as im:
        im.verify()
    with Image.open(io.BytesIO(data)) as im:
        return int(im.width), int(im.height)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-glb", type=Path, required=True)
    ap.add_argument("--terrain-scene", type=Path, required=True)
    ap.add_argument("--dyemap-export-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    a = ap.parse_args()

    scene = json.loads(a.terrain_scene.read_text(encoding="utf-8"))
    if scene.get("status") != "D1_WORLD_TERRAIN_SCENE_COMPLETE":
        raise SystemExit("terrain scene is not complete")
    tex_report_path = a.dyemap_export_dir / "texture_tag_export.json"
    direct = json.loads(tex_report_path.read_text(encoding="utf-8"))
    if direct.get("status") != "D1_TEXTURE_TAG_EXPORT_COMPLETE" or int(direct.get("failed", -1)) != 0:
        raise SystemExit("direct dyemap texture export is not complete")

    expected = sorted(str(x).upper() for x in scene.get("effective_selected_dyemaps", []))
    actual = sorted(str(x).upper() for x in (direct.get("textures") or {}))
    if actual != expected:
        raise SystemExit(f"dyemap tag set mismatch export={len(actual)} scene={len(expected)}")

    src, srcbin = read_glb(a.input_glb)
    doc = copy.deepcopy(src)
    bindata = srcbin
    base_counts = {k: len(src.get(k, [])) for k in ("bufferViews", "images", "textures", "materials", "meshes", "nodes", "accessors")}
    texroot = a.dyemap_export_dir / "textures"
    tag_to_index = {}
    rows = []
    for tag in expected:
        rec = direct["textures"][tag]
        png_name = rec.get("png")
        if not png_name:
            raise SystemExit(f"{tag}: terrain dyemap is not an exported 2D PNG")
        p = texroot / png_name
        if not p.exists():
            raise SystemExit(f"{tag}: missing exported PNG {p}")
        raw = p.read_bytes()
        w, h = verify_png(raw)
        bvi, bindata = append_blob(doc, bindata, raw, f"D1_TERRAIN_DYEMAP_{tag}_PNG")
        ii = len(doc.setdefault("images", []))
        doc["images"].append({
            "name": f"D1_TERRAIN_DYEMAP_{tag}",
            "mimeType": "image/png",
            "bufferView": bvi,
            "extras": {
                "d1_taghash": tag,
                "d1_terrain_dyemap_resource": True,
                "d1_header_info": rec.get("header_info"),
                "d1_backing_hash": rec.get("backing_hash"),
                "d1_format_name": rec.get("format_name"),
                "d1_native_colorspace_hint": rec.get("native_colorspace_hint"),
                "d1_png_sha256": hbytes(raw),
            },
        })
        ti = len(doc.setdefault("textures", []))
        doc["textures"].append({
            "name": f"D1_TERRAIN_DYEMAP_{tag}",
            "source": ii,
            "extras": {"d1_taghash": tag, "d1_terrain_dyemap_resource": True},
        })
        tag_to_index[tag] = ti
        rows.append({
            "tag": tag, "texture_index": ti, "image_index": ii, "buffer_view": bvi,
            "png": png_name, "png_bytes": len(raw), "png_sha256": hbytes(raw),
            "width": w, "height": h, "format_name": rec.get("format_name"),
            "backing_hash": rec.get("backing_hash"),
        })

    nodes = doc.get("nodes", [])
    by_name = {}
    for i, n in enumerate(nodes):
        name = str(n.get("name") or "")
        if name:
            if name in by_name:
                raise SystemExit(f"duplicate GLB node name {name}")
            by_name[name] = i

    bound_nodes = 0
    material_to_dyes: dict[str, set[str]] = {}
    for part in scene.get("parts", []):
        nn = str(part["node"])
        ni = by_name.get(nn)
        if ni is None:
            raise SystemExit(f"terrain part node absent from GLB: {nn}")
        dy = str(part.get("effective_dyemap") or "").upper()
        if dy not in tag_to_index:
            raise SystemExit(f"{nn}: effective dyemap {dy!r} not embedded")
        ex = nodes[ni].setdefault("extras", {})
        ex.update({
            "d1Terrain": str(part["terrain"]).upper(),
            "d1TerrainPartIndex": int(part["part_index"]),
            "d1TerrainGroupIndex": int(part["group_index"]),
            "d1TerrainMaterial": str(part["material"]).upper(),
            "d1TerrainSourceDyemap": str(part["source_dyemap"]).upper(),
            "d1TerrainEffectiveDyemap": dy,
            "d1TerrainDyemapTextureIndex": int(tag_to_index[dy]),
            "d1TerrainDyemapControlRGBA": [float(x) for x in part["dyemap_control_rgba"]],
            "d1TerrainIndexOffset": int(part["index_offset"]),
            "d1TerrainIndexCount": int(part["index_count"]),
        })
        material_to_dyes.setdefault(str(part["material"]).upper(), set()).add(dy)
        bound_nodes += 1

    if bound_nodes != int(scene.get("selected_main_geom0_part_count", -1)):
        raise SystemExit(f"terrain node binding coverage {bound_nodes} != {scene.get('selected_main_geom0_part_count')}")

    # Material-level union is supplemental; the authoritative selection remains per part node.
    import re
    mat_re = re.compile(r"(?:TigerMaterial_|D1_)([0-9A-Fa-f]{8})")
    seen_materials = set()
    for m in doc.get("materials", []):
        mm = mat_re.search(str(m.get("name") or ""))
        if not mm:
            continue
        mh = mm.group(1).upper()
        if mh not in material_to_dyes:
            continue
        seen_materials.add(mh)
        m.setdefault("extras", {})["d1TerrainEffectiveDyemapTagSet"] = sorted(material_to_dyes[mh])
        m["extras"]["d1TerrainDyemapSemantics"] = "NATIVE_STERRAIN_RESOURCE_PRESERVED_PORTABLE_BLEND_UNASSIGNED"
    missing_materials = sorted(set(material_to_dyes) - seen_materials)
    if missing_materials:
        raise SystemExit("terrain materials absent from GLB: " + ",".join(missing_materials))

    doc.setdefault("asset", {"version": "2.0"}).setdefault("extras", {})["d1TerrainDyemapCorpus"] = {
        "exactDyemapTagCount": len(tag_to_index),
        "boundTerrainPartNodeCount": bound_nodes,
        "policy": "All effective STerrain dyemap resources are embedded by exact TagHash. Per-part GroupIndex%4 control is metadata, not COLOR_0. No portable dyemap blend equation is inferred.",
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    write_glb(a.out, doc, bindata)
    chk, chkbin = read_glb(a.out)
    if chkbin[:len(srcbin)] != srcbin:
        raise SystemExit("input BIN is not exact output prefix")
    for k in ("accessors", "meshes"):
        if chk.get(k, []) != src.get(k, []):
            raise SystemExit(f"input {k} changed")
    final_counts = {k: len(chk.get(k, [])) for k in base_counts}
    if final_counts["images"] != base_counts["images"] + len(tag_to_index):
        raise SystemExit("dyemap image count mismatch")
    if final_counts["textures"] != base_counts["textures"] + len(tag_to_index):
        raise SystemExit("dyemap texture count mismatch")
    report = {
        "schema_version": 1,
        "status": "D1_GLTF_TERRAIN_DYEMAPS_EMBEDDED",
        "input_glb": str(a.input_glb),
        "input_sha256": hfile(a.input_glb),
        "output_glb": str(a.out),
        "output_bytes": a.out.stat().st_size,
        "output_sha256": hfile(a.out),
        "exact_dyemap_count": len(tag_to_index),
        "bound_terrain_part_node_count": bound_nodes,
        "terrain_material_count": len(material_to_dyes),
        "base_counts": base_counts,
        "final_counts": final_counts,
        "dyemaps": rows,
        "policy": "Every exact effective STerrain dyemap is a named embedded glTF resource and every terrain part node stores the exact source/effective TagHash, glTF texture index, group index and generated selector. Portable shader blending remains intentionally unassigned.",
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in (
        "status", "exact_dyemap_count", "bound_terrain_part_node_count", "terrain_material_count",
        "base_counts", "final_counts", "output_bytes", "output_sha256"
    )}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
