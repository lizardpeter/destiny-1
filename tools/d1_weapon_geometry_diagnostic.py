#!/usr/bin/env python3
"""Proof-oriented diagnostic for a D1 ROI entity weapon model.

This deliberately does not export geometry.  It records the entity/resource/model
ownership chain, exact vertex-buffer header metadata, position-stream statistics,
and connected-component bounds for the model's visible LOD ranges.  The goal is
to distinguish an incomplete model assembly from an incorrect vertex/attachment
interpretation before changing the exporter.
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from d1_entry_extract import EntryReader, decode_known
from d1_entity_model_probe import parse_model
from d1_entity_resource_probe import parse_resource


def snorm16(v: int) -> float:
    return max(-1.0, float(v) / 32767.0)


def strip_to_triangles(values: list[int]) -> list[tuple[int, int, int]]:
    out: list[tuple[int, int, int]] = []
    strip: list[int] = []
    for raw in values:
        if raw == 0xFFFF:
            strip.clear()
            continue
        strip.append(raw)
        if len(strip) < 3:
            continue
        a, b, c = strip[-3], strip[-2], strip[-1]
        if (len(strip) - 3) & 1:
            a, b = b, a
        if a != b and b != c and a != c:
            out.append((a, b, c))
    return out


def bbox(points: list[tuple[float, float, float]]) -> dict:
    if not points:
        return {"min": None, "max": None, "extent": None}
    mn = [min(p[i] for p in points) for i in range(3)]
    mx = [max(p[i] for p in points) for i in range(3)]
    return {
        "min": mn,
        "max": mx,
        "extent": [mx[i] - mn[i] for i in range(3)],
    }


class DSU:
    def __init__(self):
        self.parent: dict[int, int] = {}

    def find(self, x: int) -> int:
        self.parent.setdefault(x, x)
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def tag_entry(by_hash: dict[str, dict], tag_hash: str) -> dict:
    try:
        return by_hash[tag_hash.upper()]
    except KeyError:
        raise KeyError(f"tag {tag_hash} is not present in this package snapshot")


def entry_bytes(reader: EntryReader, by_hash: dict[str, dict], tag_hash: str) -> bytes:
    e = tag_entry(by_hash, tag_hash)
    if not reader.available(e["index"]):
        raise RuntimeError(f"tag {tag_hash} is not resident")
    return reader.entry(e["index"])


def linked(reader: EntryReader, by_hash: dict[str, dict], tag_hash: str) -> tuple[dict, bytes, dict, bytes]:
    e = tag_entry(by_hash, tag_hash)
    header = reader.entry(e["index"])
    pe = tag_entry(by_hash, e["reference"])
    payload = reader.entry(pe["index"])
    return e, header, pe, payload


def resource_literal_refs(entity_payload: bytes, resource_hashes: set[str]) -> list[dict]:
    out = []
    for h in sorted(resource_hashes):
        needle = struct.pack("<I", int(h, 16))
        pos = 0
        while True:
            p = entity_payload.find(needle, pos)
            if p < 0:
                break
            out.append({"tag_hash": h, "offset": p})
            pos = p + 1
    return sorted(out, key=lambda x: (x["offset"], x["tag_hash"]))


def mesh_diagnostic(reader: EntryReader, by_hash: dict[str, dict], mesh: dict, mesh_index: int) -> dict:
    e0, h0, p0e, p0 = linked(reader, by_hash, mesh["vertices1"])
    e1, h1, p1e, p1 = linked(reader, by_hash, mesh["vertices2"])
    eie, hi, pie, pi = linked(reader, by_hash, mesh["indices"])
    dh0 = decode_known(e0, h0, reader.h["platform"])
    dh1 = decode_known(e1, h1, reader.h["platform"])
    dhi = decode_known(eie, hi, reader.h["platform"])
    stride0 = int(dh0.get("stride", 0))
    stride1 = int(dh1.get("stride", 0))
    if stride0 <= 0 or len(p0) % stride0:
        raise RuntimeError(f"mesh {mesh_index}: invalid position payload/stride {len(p0)}/{stride0}")

    rows0 = [struct.unpack_from("<" + "h" * (stride0 // 2), p0, o)
             for o in range(0, len(p0), stride0)]
    scale = [float(x) for x in mesh["model_scale"][:3]]
    trans = [float(x) for x in mesh["model_translation"][:3]]
    positions = [tuple(snorm16(r[i]) * scale[i] + trans[i] for i in range(3)) for r in rows0]

    fourth = [r[3] for r in rows0] if stride0 >= 8 else []
    fourth_counts = collections.Counter(fourth)
    raw_xyz = [tuple(int(r[i]) for i in range(3)) for r in rows0]

    is32 = bool(dhi.get("is32bit"))
    if is32:
        idx = list(struct.unpack("<" + "I" * (len(pi) // 4), pi))
        restart = 0xFFFFFFFF
    else:
        idx = list(struct.unpack("<" + "H" * (len(pi) // 2), pi))
        restart = 0xFFFF

    # Deduplicate material variants that reuse the exact same index range.
    lod_ranges: dict[tuple[int, int, int], list[dict]] = {}
    for part in mesh["parts"]:
        if int(part["lod"]) != 1:
            continue
        k = (int(part["index_offset"]), int(part["index_count"]), int(part["primitive_type"]))
        lod_ranges.setdefault(k, []).append(part)

    triangles: list[tuple[int, int, int]] = []
    range_rows = []
    for (off, count, primitive), parts in sorted(lod_ranges.items()):
        vals = idx[off:off + count]
        if primitive == 5 and not is32:
            tris = strip_to_triangles(vals)
        elif primitive == 3:
            tris = [tuple(vals[i:i + 3]) for i in range(0, len(vals) - 2, 3)]
        else:
            # Retain evidence without inventing conversion rules.
            tris = []
        triangles.extend(tris)
        range_rows.append({
            "index_offset": off,
            "index_count": count,
            "primitive_type": primitive,
            "materials": sorted({p["material"] for p in parts}),
            "triangle_count": len(tris),
            "restart_markers": sum(1 for v in vals if v == restart),
        })

    dsu = DSU()
    tri_by_root: collections.Counter[int] = collections.Counter()
    for a, b, c in triangles:
        if max(a, b, c) >= len(positions):
            continue
        dsu.union(a, b); dsu.union(b, c)
    for a, b, c in triangles:
        if max(a, b, c) >= len(positions):
            continue
        tri_by_root[dsu.find(a)] += 1
    verts_by_root: dict[int, set[int]] = collections.defaultdict(set)
    for a, b, c in triangles:
        if max(a, b, c) >= len(positions):
            continue
        root = dsu.find(a)
        verts_by_root[root].update((a, b, c))

    components = []
    for root, verts in verts_by_root.items():
        pts = [positions[v] for v in verts]
        components.append({
            "triangle_count": int(tri_by_root[root]),
            "vertex_count": len(verts),
            "vertex_index_minmax": [min(verts), max(verts)],
            "bbox_tiger_model_space": bbox(pts),
        })
    components.sort(key=lambda x: (-x["triangle_count"], -x["vertex_count"]))

    used = sorted({v for tri in triangles for v in tri if v < len(positions)})
    return {
        "mesh_index": mesh_index,
        "model_scale": mesh["model_scale"],
        "model_translation": mesh["model_translation"],
        "texcoord_scale": mesh["texcoord_scale"],
        "texcoord_translation": mesh["texcoord_translation"],
        "position_stream": {
            "header_tag": e0["tag_hash"],
            "header": dh0,
            "payload_tag": p0e["tag_hash"],
            "payload_size": len(p0),
            "vertex_count": len(rows0),
            "raw_xyz_min": [min(r[i] for r in raw_xyz) for i in range(3)],
            "raw_xyz_max": [max(r[i] for r in raw_xyz) for i in range(3)],
            "fourth_i16_unique_count": len(fourth_counts),
            "fourth_i16_minmax": [min(fourth), max(fourth)] if fourth else None,
            "fourth_i16_most_common": [[int(k), int(v)] for k, v in fourth_counts.most_common(32)],
            "decoded_bbox_all_tiger_model_space": bbox(positions),
            "decoded_bbox_lod1_used_tiger_model_space": bbox([positions[v] for v in used]),
        },
        "secondary_stream": {
            "header_tag": e1["tag_hash"],
            "header": dh1,
            "payload_tag": p1e["tag_hash"],
            "payload_size": len(p1),
            "stride": stride1,
        },
        "index_stream": {
            "header_tag": eie["tag_hash"],
            "header": dhi,
            "payload_tag": pie["tag_hash"],
            "payload_size": len(pi),
            "index_count": len(idx),
        },
        "lod1_ranges": range_rows,
        "lod1_triangle_count_deduplicated_ranges": len(triangles),
        "lod1_used_vertex_count": len(used),
        "connected_component_count": len(components),
        "connected_components": components,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pkg", type=Path)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--entity", default="80A39E0E")
    ap.add_argument("--model", default="80A39E12")
    ap.add_argument("-o", "--output", type=Path)
    a = ap.parse_args()

    r = EntryReader(a.pkg, a.runtime)
    by = {e["tag_hash"].upper(): e for e in r.entries}
    entity_hash = a.entity.upper().removeprefix("0X")
    model_hash = a.model.upper().removeprefix("0X")

    entity_entry = tag_entry(by, entity_hash)
    entity_payload = entry_bytes(r, by, entity_hash)
    resource_entries = [e for e in r.entries if e["type"] == 16 and e["subtype"] == 0 and e["reference"].upper() == "80800861"]
    resource_hashes = {e["tag_hash"].upper() for e in resource_entries}
    literal_hits = resource_literal_refs(entity_payload, resource_hashes)
    linked_resource_hashes = sorted({x["tag_hash"] for x in literal_hits})

    resources = []
    for h in linked_resource_hashes:
        e = by[h]
        row = {"tag_hash": h, "entry_index": e["index"], "size": e["file_size"], "reference": e["reference"]}
        try:
            row.update(parse_resource(r.entry(e["index"]), r.h["platform"]))
        except Exception as ex:
            row["error"] = repr(ex)
        resources.append(row)

    me = tag_entry(by, model_hash)
    model = parse_model(r.entry(me["index"]), r.h["platform"])
    meshes = [mesh_diagnostic(r, by, m, i) for i, m in enumerate(model["meshes"])]

    report = {
        "package": str(r.pkg),
        "platform": r.h["platform"],
        "pkg_id": r.h["pkg_id"],
        "entity": {
            "tag_hash": entity_hash,
            "entry_index": entity_entry["index"],
            "reference": entity_entry["reference"],
            "size": entity_entry["file_size"],
            "entity_resource_literal_hits": literal_hits,
            "unique_entity_resources": linked_resource_hashes,
            "resources": resources,
        },
        "model": {
            "tag_hash": model_hash,
            "entry_index": me["index"],
            "reference": me["reference"],
            "size": me["file_size"],
            "mesh_count": model["mesh_count"],
            "meshes": meshes,
        },
        "interpretation_guardrails": [
            "Connected components are derived only from deduplicated LOD1 index ranges; material variants reusing one range are not duplicated.",
            "Position bbox uses the current SNORM16 XYZ * model_scale + model_translation hypothesis and is reported as a hypothesis, not proof of skin/attachment semantics.",
            "The fourth int16 is reported exactly and is not assigned a semantic by this tool.",
        ],
    }
    text = json.dumps(report, indent=2) + "\n"
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(text)
        print(f"wrote {a.output}")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
