#!/usr/bin/env python3
"""Export a Destiny 1 ROI baked-static map chunk only after binary validation passes.

This deliberately gates every export on a previously generated
`d1_tower_map_schema_validate.py` report entry with `ok: true`.

The current output is a geometry/provenance proof scene, not yet a final visual map:
- static placement/index relationships come only from the validated retail bytes;
- raw D1 0x40 instance matrices are transposed before use, matching the source-derived
  convention independently validated by exact backing size/index bounds;
- mesh buffer FileHashes/index ranges come from validated D1 static table records;
- material hashes are preserved as material identities, but texture/material semantic
  reconstruction is intentionally deferred;
- no map/world ownership is inferred from successful mesh decoding.

A sidecar JSON records every source table, static record, material hash, instance range,
buffer source and emitted node.
"""
from __future__ import annotations

import argparse
import json
import math
import struct
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from d1_tower_map_schema_validate import Corpus
from d1_entity_model_export import (
    decode_indices,
    hdr_stride,
    index_is32,
    primitive_faces,
)


def norm_hash(s: str) -> str:
    return s.upper().removeprefix("0X").zfill(8)


def snorm16_xyz(raw: np.ndarray) -> np.ndarray:
    x = raw.astype(np.float32) / 32767.0
    return np.maximum(x, -1.0)


def decode_static_positions(data: bytes, stride: int) -> np.ndarray:
    """Decode only the proven/observed D1 position prefix.

    D1 ROI buffer-0 layouts store xyz in the first 3 signed 16-bit components for
    the common packed strides; 0x30 is the known float physics-style layout.
    Other semantics in the record remain untouched.
    """
    if stride <= 0 or len(data) % stride:
        raise ValueError(f"vertex backing size {len(data)} not divisible by stride {stride:#x}")
    n = len(data) // stride
    if stride == 0x30:
        raw = np.frombuffer(data, dtype="<f4").reshape(n, stride // 4)
        pos = raw[:, :3].astype(np.float32)
    elif stride in (0x08, 0x0C, 0x10, 0x1C, 0x20):
        raw = np.frombuffer(data, dtype="<i2").reshape(n, stride // 2)
        pos = snorm16_xyz(raw[:, :3])
    else:
        raise ValueError(f"unsupported D1 static position stride {stride:#x}")
    if not np.isfinite(pos).all():
        raise ValueError("non-finite static positions")
    return pos


def payload_with_meta(c: Corpus, h: str):
    h = norm_hash(h)
    b, src = c.payload(h)
    if b is None or src is None:
        raise KeyError(f"payload unavailable for {h}")
    meta = c.entry_meta(h)
    if not meta:
        raise KeyError(f"metadata unavailable for {h}")
    return b, src, meta


def read_reference_file(c: Corpus, header_hash: str):
    """Return reference-file header bytes + backing bytes with exact provenance."""
    hh = norm_hash(header_hash)
    header, hsrc, hmeta = payload_with_meta(c, hh)
    backing_hash = norm_hash(hmeta["reference"])
    backing, bsrc, bmeta = payload_with_meta(c, backing_hash)
    return {
        "header_hash": hh,
        "header": header,
        "header_source": hsrc,
        "header_meta": hmeta,
        "backing_hash": backing_hash,
        "backing": backing,
        "backing_source": bsrc,
        "backing_meta": bmeta,
    }


def matrix_records(data: bytes, count: int) -> list[np.ndarray]:
    expected = count * 0x40
    if len(data) != expected:
        raise ValueError(f"transform backing {len(data)} != {count}*0x40 ({expected})")
    vals = np.frombuffer(data, dtype="<f4").reshape(count, 4, 4)
    if not np.isfinite(vals).all():
        raise ValueError("non-finite instance matrix")
    # Shipped rows are transposed before decomposition/use by the source-derived ROI
    # implementation. Keep the full matrix rather than decomposing/recomposing it.
    return [m.T.astype(np.float64) for m in vals]


def select_validated_map(report: dict, static_map_hash: str) -> dict:
    h = norm_hash(static_map_hash)
    rows = [x for x in report.get("static_map_data", []) if norm_hash(x.get("hash", "0")) == h]
    if not rows:
        raise KeyError(f"{h} absent from validation report")
    good = [x for x in rows if x.get("ok")]
    if not good:
        raise ValueError(f"{h} exists but did not pass the binary validator")
    if len(good) != 1:
        raise ValueError(f"{h} has {len(good)} passing validation rows; expected one canonical row")
    row = good[0]
    if not row.get("d1_validation", {}).get("ok"):
        raise ValueError(f"{h} parent passed unexpectedly without a passing D1 child")
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", type=Path, action="append", required=True)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--validation-json", type=Path, required=True)
    ap.add_argument("--static-map-data", required=True,
                    help="validated 808008B4 TagHash, e.g. 80CA0B70")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--json", type=Path)
    ap.add_argument("--max-nodes", type=int, default=200000)
    args = ap.parse_args()

    validation = json.loads(args.validation_json.read_text())
    selected = select_validated_map(validation, args.static_map_data)
    d1 = selected["d1_validation"]

    c = Corpus([p.resolve() for p in args.snapshot], args.runtime.resolve())
    transform_hash = norm_hash(d1["instance_transforms"])
    transform_bytes, transform_src, transform_meta = payload_with_meta(c, transform_hash)
    transforms = matrix_records(transform_bytes, int(d1["instance_count"]))

    # Cache whole reference buffers and decoded geometry ranges. Geometry is keyed by
    # the exact serialized static record + material identity; nodes may then instance it.
    ref_cache = {}
    geometry_cache = {}
    scene = trimesh.Scene()
    emitted_nodes = []
    failures = []
    table_reports = []

    def ref_file(h):
        h = norm_hash(h)
        if h not in ref_cache:
            ref_cache[h] = read_reference_file(c, h)
        return ref_cache[h]

    node_total = 0
    for table_i, table in enumerate(d1["static_tables"]):
        if not table.get("ok"):
            raise ValueError(f"validated parent contains failing static table {table.get('hash')}")
        trep = {"table_hash": table["hash"], "table_index": table_i, "emitted_groups": []}
        meshes = table["mesh_entries"]
        materials = table["material_hashes"]

        for info in table["info_entries"]:
            if not info.get("all_indices_in_bounds"):
                raise ValueError(f"validated table contains out-of-bounds info {table['hash']}:{info['index']}")
            mesh = meshes[int(info["static_index"])]
            material_hash = norm_hash(materials[int(info["material_index"])])
            instance_count = int(info["instance_count"])
            transform_index = int(info["transform_index"])
            if instance_count < 0 or transform_index < 0 or transform_index + instance_count > len(transforms):
                raise ValueError("instance range escaped validated transform bounds")

            key = (
                norm_hash(mesh["vertices0"]), norm_hash(mesh["vertices1"]), norm_hash(mesh["indices"]),
                int(mesh["index_offset"]), int(mesh["index_count"]), int(mesh["primitive_type"]),
                material_hash,
            )
            if key not in geometry_cache:
                try:
                    v0 = ref_file(mesh["vertices0"])
                    # v1 is still resolved and provenance-checked even though this first
                    # proof scene does not yet consume its normals/UVs.
                    v1 = ref_file(mesh["vertices1"])
                    ib = ref_file(mesh["indices"])
                    stride0 = hdr_stride(v0["header"])
                    stride1 = hdr_stride(v1["header"])
                    is32 = index_is32(ib["header"])
                    pos = decode_static_positions(v0["backing"], stride0)
                    indices = decode_indices(ib["backing"], is32)
                    off = int(mesh["index_offset"]); cnt = int(mesh["index_count"])
                    if off < 0 or cnt < 0 or off + cnt > len(indices):
                        raise ValueError(f"serialized index range {off}+{cnt} > {len(indices)}")
                    faces_global = primitive_faces(indices[off:off+cnt], int(mesh["primitive_type"]), is32)
                    if len(faces_global) == 0:
                        raise ValueError("serialized mesh range produced zero triangles")
                    if faces_global.min() < 0 or faces_global.max() >= len(pos):
                        raise ValueError(f"index range [{faces_global.min()},{faces_global.max()}] outside {len(pos)} vertices")
                    used, inv = np.unique(faces_global.reshape(-1), return_inverse=True)
                    faces = inv.reshape((-1, 3))
                    verts = pos[used]
                    mat = trimesh.visual.material.PBRMaterial(name=f"TigerMaterial_{material_hash}")
                    visual = trimesh.visual.TextureVisuals(material=mat)
                    tm = trimesh.Trimesh(vertices=verts, faces=faces, visual=visual,
                                         process=False, validate=False)
                    geom_name = (
                        f"static_{key[0]}_{key[2]}_o{key[3]}_n{key[4]}_p{key[5]}_m{material_hash}"
                    )
                    tm.metadata = {
                        "evidence": "validated D1 baked-static record",
                        "vertices0": key[0], "vertices1": key[1], "indices": key[2],
                        "index_offset": key[3], "index_count": key[4],
                        "primitive_type": key[5], "material_hash": material_hash,
                        "detail_level": int(mesh["detail_level"]),
                        "source_vertex_indices": used.tolist(),
                    }
                    scene.add_geometry(tm, geom_name=geom_name, node_name=None)
                    geometry_cache[key] = {
                        "geom_name": geom_name,
                        "triangle_count": int(len(faces)),
                        "vertex_count": int(len(verts)),
                        "source_vertex_count": int(len(pos)),
                        "stride0": int(stride0), "stride1": int(stride1),
                        "index_width_bits": 32 if is32 else 16,
                        "buffers": {
                            "vertices0": {k: v0[k] for k in ("header_hash","header_source","header_meta","backing_hash","backing_source","backing_meta")},
                            "vertices1": {k: v1[k] for k in ("header_hash","header_source","header_meta","backing_hash","backing_source","backing_meta")},
                            "indices": {k: ib[k] for k in ("header_hash","header_source","header_meta","backing_hash","backing_source","backing_meta")},
                        },
                    }
                except Exception as ex:
                    failures.append({
                        "table_hash": table["hash"], "info_index": info["index"],
                        "static_index": info["static_index"], "material_hash": material_hash,
                        "mesh": mesh, "error": repr(ex),
                    })
                    continue

            g = geometry_cache[key]
            group_nodes = []
            for local_i in range(instance_count):
                ti = transform_index + local_i
                node_total += 1
                if node_total > args.max_nodes:
                    raise ValueError(f"node count exceeded --max-nodes {args.max_nodes}")
                node_name = f"{table['hash']}_info{info['index']}_xform{ti}"
                scene.graph.update(frame_to=node_name, matrix=transforms[ti], geometry=g["geom_name"])
                group_nodes.append(node_name)
                emitted_nodes.append({
                    "node": node_name, "table_hash": table["hash"], "info_index": info["index"],
                    "static_index": info["static_index"], "material_index": info["material_index"],
                    "material_hash": material_hash, "transform_index": ti,
                    "geometry": g["geom_name"], "detail_level": int(mesh["detail_level"]),
                })
            trep["emitted_groups"].append({
                "info_index": info["index"], "static_index": info["static_index"],
                "material_index": info["material_index"], "material_hash": material_hash,
                "transform_index": transform_index, "instance_count": instance_count,
                "geometry": g["geom_name"], "nodes": group_nodes,
            })
        table_reports.append(trep)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    scene.export(args.out)
    out_json = args.json or args.out.with_suffix(".json")
    report = {
        "evidence_status": "BINARY_VALIDATED_STATIC_ASSEMBLY_PROOF",
        "scope_warning": "This is one validator-passing Tower static-map resource, not yet the complete Tower.",
        "static_map_data": norm_hash(args.static_map_data),
        "d1_static_map_data": d1["hash"],
        "validation_source": str(args.validation_json),
        "instance_count": int(d1["instance_count"]),
        "instance_transforms": transform_hash,
        "instance_transform_source": transform_src,
        "instance_transform_meta": transform_meta,
        "static_table_hashes": d1["static_table_hashes"],
        "geometry_variant_count": len(geometry_cache),
        "node_instance_count": len(emitted_nodes),
        "buffer_reference_file_count": len(ref_cache),
        "decode_failure_count": len(failures),
        "decode_failures": failures,
        "geometry": list(geometry_cache.values()),
        "tables": table_reports,
        "nodes": emitted_nodes,
        "scene_bounds": scene.bounds.tolist() if scene.bounds is not None else None,
        "output_glb": str(args.out),
        "policy": {
            "placement": "only validator-passing StaticInfo -> TransformIndex/InstanceCount ranges are emitted",
            "materials": "exact material hashes preserved; texture/shader semantics not inferred here",
            "lod": "no visual LOD/depth-pass filtering is applied in this proof export",
            "coordinate_system": "raw Tiger packed positions + transposed shipped instance matrices; no cosmetic axis conversion",
        },
    }
    out_json.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in (
        "evidence_status","static_map_data","d1_static_map_data","instance_count",
        "geometry_variant_count","node_instance_count","buffer_reference_file_count",
        "decode_failure_count","scene_bounds","output_glb")}, indent=2))
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
