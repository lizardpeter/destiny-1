#!/usr/bin/env python3
"""Validate D1 terrain buffer layouts and selected index ranges before export.

This tool consumes the source-closed terrain census. It does not infer vertex
semantics. It resolves only the typed Vertices1/Vertices2/Indices1 fields, follows
their exact Tiger reference-file backing hashes, reports header layouts, and runs
Charm's exact terrain primitive selection (MainGeom0 parts over TriangleStrip
Indices1) through the project's already-proven D1 index converter.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from collections import Counter
from pathlib import Path

import numpy as np

import d1_tower_map_schema_validate_v5 as v5
import d1_tower_static_chunk_export as static
from d1_entity_model_export import decode_indices, hdr_stride, index_is32, primitive_faces

NULLS = {"00000000", "FFFFFFFF"}


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def ref_summary(c, h: str) -> dict:
    h = norm(h)
    if h in NULLS:
        raise ValueError("null terrain buffer header")
    r = static.read_reference_file(c, h)
    head = r["header"]
    if len(head) < 8:
        raise ValueError(f"{h}: reference header shorter than 8 bytes")
    stride = int(hdr_stride(head))
    data_size = struct.unpack_from("<I", head, 0)[0]
    typ = struct.unpack_from("<h", head, 6)[0]
    return {
        "header_hash": h,
        "header_bytes": len(head),
        "header_sha256": sha(head),
        "header_hex": head.hex().upper(),
        "data_size_field": int(data_size),
        "stride": stride,
        "type": int(typ),
        "backing_hash": norm(r["backing_hash"]),
        "backing_bytes": len(r["backing"]),
        "backing_sha256": sha(r["backing"]),
        "header_source": r["header_source"],
        "backing_source": r["backing_source"],
        "header_meta": r["header_meta"],
        "backing_meta": r["backing_meta"],
        "backing": r["backing"],
        "header": head,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", type=Path, action="append", required=True)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--terrain-census", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    census = json.loads(a.terrain_census.read_text(encoding="utf-8"))
    if census.get("status") != "D1_WORLD_TERRAIN_CENSUS_COMPLETE":
        raise SystemExit(f"terrain census not complete: {census.get('status')!r}")
    if census.get("violations") or census.get("missing_dependency_package_ids"):
        raise SystemExit("terrain census contains unresolved evidence")

    c = v5.v3.base.Corpus([p.resolve() for p in a.snapshot], a.runtime.resolve())
    cache = {}
    def get(h: str):
        h = norm(h)
        if h not in cache:
            cache[h] = ref_summary(c, h)
        return cache[h]

    terrains = []
    pair_hist = Counter()
    index_hist = Counter()
    selected_total = 0
    triangle_total = 0
    violations = []
    max_vertex_global = -1

    for t in census.get("terrains", []):
        th = norm(t.get("hash"))
        deps = t.get("top_level_dependencies") or {}
        v0h = norm((deps.get("vertices1") or {}).get("hash"))
        v1h = norm((deps.get("vertices2") or {}).get("hash"))
        ibh = norm((deps.get("indices1") or {}).get("hash"))
        try:
            v0 = get(v0h); v1 = get(v1h); ib = get(ibh)
            s0 = int(v0["stride"]); s1 = int(v1["stride"])
            if s0 <= 0 or s1 <= 0:
                raise ValueError(f"invalid terrain strides {s0}/{s1}")
            if v0["backing_bytes"] % s0 or v1["backing_bytes"] % s1:
                raise ValueError("terrain vertex backing is not divisible by header stride")
            n0 = v0["backing_bytes"] // s0
            n1 = v1["backing_bytes"] // s1
            if n0 != n1:
                raise ValueError(f"terrain vertex stream count mismatch {n0}!={n1}")
            is32 = bool(index_is32(ib["header"]))
            inds = decode_indices(ib["backing"], is32)
            pair_hist[f"{s0:#x}/{s1:#x}"] += 1
            index_hist["u32" if is32 else "u16"] += 1

            selected = [p for p in t.get("static_parts", []) if p.get("selected_main_geom0")]
            selected_total += len(selected)
            part_rows = []
            terrain_triangles = 0
            terrain_max = -1
            for p in selected:
                off = int(p["index_offset"]); cnt = int(p["index_count"])
                if off < 0 or cnt < 0 or off + cnt > len(inds):
                    raise ValueError(f"part {p['index']} index range {off}+{cnt}>{len(inds)}")
                faces = primitive_faces(inds[off:off+cnt], 5, is32)
                if len(faces) == 0:
                    raise ValueError(f"part {p['index']} selected MainGeom0 emitted zero strip triangles")
                lo = int(faces.min()); hi = int(faces.max())
                if lo < 0 or hi >= n0:
                    raise ValueError(f"part {p['index']} face range [{lo},{hi}] outside {n0} vertices")
                terrain_triangles += len(faces)
                terrain_max = max(terrain_max, hi)
                part_rows.append({
                    "part_index": int(p["index"]),
                    "material": norm((p.get("material") or {}).get("hash")),
                    "group_index": int(p["group_index"]),
                    "detail_level": int(p["detail_level"]),
                    "index_offset": off,
                    "index_count": cnt,
                    "triangle_count": int(len(faces)),
                    "min_vertex_index": lo,
                    "max_vertex_index": hi,
                })
            triangle_total += terrain_triangles
            max_vertex_global = max(max_vertex_global, terrain_max)
            terrains.append({
                "terrain": th,
                "vertices1": {k:v0[k] for k in ("header_hash","header_bytes","header_sha256","data_size_field","stride","type","backing_hash","backing_bytes","backing_sha256")},
                "vertices2": {k:v1[k] for k in ("header_hash","header_bytes","header_sha256","data_size_field","stride","type","backing_hash","backing_bytes","backing_sha256")},
                "indices1": {**{k:ib[k] for k in ("header_hash","header_bytes","header_sha256","data_size_field","stride","type","backing_hash","backing_bytes","backing_sha256")}, "is32":is32, "index_count":int(len(inds))},
                "vertex_count": int(n0),
                "selected_part_count": len(selected),
                "triangle_count": int(terrain_triangles),
                "max_selected_vertex_index": terrain_max,
                "selected_parts": part_rows,
            })
        except Exception as ex:
            violations.append({"terrain": th, "error": repr(ex), "vertices1": v0h, "vertices2": v1h, "indices1": ibh})

    if selected_total != int(census.get("selected_main_geom0_part_count", -1)):
        violations.append({"error": f"selected part count mismatch {selected_total}!={census.get('selected_main_geom0_part_count')}"})

    # Remove raw bytes from cache before any accidental serialization path.
    unique_headers = []
    for h, r in sorted(cache.items()):
        unique_headers.append({k:v for k,v in r.items() if k not in {"backing","header"}})

    out = {
        "schema_version": 1,
        "status": "D1_WORLD_TERRAIN_BUFFER_LAYOUT_COMPLETE" if not violations else "D1_WORLD_TERRAIN_BUFFER_LAYOUT_WITH_VIOLATIONS",
        "terrain_count": len(terrains),
        "selected_main_geom0_part_count": selected_total,
        "triangle_count": int(triangle_total),
        "max_selected_vertex_index": int(max_vertex_global),
        "stride_pair_histogram": dict(sorted(pair_hist.items())),
        "index_format_histogram": dict(sorted(index_hist.items())),
        "unique_reference_header_count": len(unique_headers),
        "reference_headers": unique_headers,
        "terrains": terrains,
        "violations": violations,
        "policy": "Only exact typed STerrain Vertices1/Vertices2/Indices1 references are followed. Backing files come only from each verified Tiger reference header's serialized reference field. MainGeom0 parts are converted as TriangleStrip using the project's proven primitive-restart logic. No vertex semantics are inferred here.",
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k:out[k] for k in ("status","terrain_count","selected_main_geom0_part_count","triangle_count","max_selected_vertex_index","stride_pair_histogram","index_format_histogram","unique_reference_header_count","violations")}, indent=2))
    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
