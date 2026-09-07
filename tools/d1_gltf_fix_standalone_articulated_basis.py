#!/usr/bin/env python3
"""Repair basis composition for a standalone D1 articulated glTF export.

The pinned tiger-animation-parser converts native Tiger/D1 vectors internally as

    parser = [raw_y, raw_z, raw_x]

for its Three.js-oriented animation path.  D1 model geometry, however, is authored
in native Z-up model space.  Combining parser-space joints/animations with unchanged
native mesh vertices creates a glTF whose bind algebra can still be self-consistent
while the visible armature is physically on a different axis from the mesh.

For a standalone actor this adapter performs two explicit, source-constrained steps:

1. Undo the parser-only basis on the selected skin domain (joint local TRS,
   inverseBindMatrices, and all animation outputs targeting those joints).
2. Wrap the complete standalone scene in the already-established native D1 Z-up ->
   glTF Y-up world adapter, [x,y,z] -> [x,z,-y].

Mesh vertex/index/UV/joint-weight bytes, materials, textures, images, animation times,
clip identity, topology, and source texture resources are not changed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.spatial.transform import Rotation

from d1_gltf_layer_merge import read_glb, write_glb
from d1_gltf_skin_bind_identity_probe import accessor, node_local

# parser p = P @ raw, where p=[raw_y, raw_z, raw_x]
P = np.array(
    [[0.0, 1.0, 0.0, 0.0],
     [0.0, 0.0, 1.0, 0.0],
     [1.0, 0.0, 0.0, 0.0],
     [0.0, 0.0, 0.0, 1.0]],
    dtype=np.float64,
)
PI = P.T

# Native D1/Tiger Z-up -> glTF Y-up, row-major mathematical form.
Q = np.array(
    [[1.0, 0.0, 0.0, 0.0],
     [0.0, 0.0, 1.0, 0.0],
     [0.0, -1.0, 0.0, 0.0],
     [0.0, 0.0, 0.0, 1.0]],
    dtype=np.float64,
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def decompose_trs(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    t = matrix[:3, 3].copy()
    a = matrix[:3, :3].copy()
    s = np.linalg.norm(a, axis=0)
    if np.any(s < 1e-12):
        raise ValueError("zero scale during basis conversion")
    r = a / s
    if np.linalg.det(r) < 0:
        k = int(np.argmax(np.abs(s)))
        s[k] *= -1.0
        r[:, k] *= -1.0
    q = Rotation.from_matrix(r).as_quat()
    return t, q, s


def set_accessor(doc: dict, blob: bytearray, ai: int, data: np.ndarray) -> None:
    a = doc["accessors"][ai]
    bv = doc["bufferViews"][a["bufferView"]]
    if int(a["componentType"]) != 5126:
        raise ValueError(f"accessor {ai}: expected FLOAT output")
    n = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}[a["type"]]
    x = np.asarray(data, dtype="<f4")
    if a["type"] == "MAT4":
        flat = np.stack([m.reshape(16, order="F") for m in x], axis=0)
    else:
        flat = x.reshape((int(a["count"]), n))
    expected = (int(a["count"]), n)
    if flat.shape != expected:
        raise ValueError(f"accessor {ai}: shape {flat.shape} != {expected}")
    base = int(bv.get("byteOffset", 0)) + int(a.get("byteOffset", 0))
    stride = int(bv.get("byteStride", 4 * n))
    row_bytes = 4 * n
    if stride == row_bytes:
        raw = flat.tobytes(order="C")
        blob[base:base + len(raw)] = raw
    else:
        for i, row in enumerate(flat):
            raw = row.astype("<f4", copy=False).tobytes()
            blob[base + i * stride:base + i * stride + row_bytes] = raw


def transform_joint_node(node: dict) -> None:
    native = PI @ node_local(node) @ P
    t, q, s = decompose_trs(native)
    node.pop("matrix", None)
    node["translation"] = [float(x) for x in t]
    node["rotation"] = [float(x) for x in q]
    node["scale"] = [float(x) for x in s]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input_glb", type=Path)
    ap.add_argument("--model", required=True, help="D1 model tag hash, e.g. 80C88CEF")
    ap.add_argument("--expect-skeleton", help="Optional exact skeleton tag hash")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()

    model = args.model.upper()
    expected_skeleton = args.expect_skeleton.upper() if args.expect_skeleton else None
    doc, source_bin = read_glb(args.input_glb)
    if (doc.get("asset", {}).get("extras", {}) or {}).get("d1_standalone_articulated_basis_fix"):
        raise ValueError("input is already marked as standalone articulated basis-fixed")
    blob = bytearray(source_bin)
    nodes = doc.get("nodes", [])
    skins = doc.get("skins", [])

    selected: list[tuple[int, dict]] = []
    for si, skin in enumerate(skins):
        root = int(skin["skeleton"])
        extras = nodes[root].get("extras") or {}
        if str(extras.get("d1Model", "")).upper() == model:
            selected.append((si, skin))
    if len(selected) != 1:
        raise ValueError(f"expected exactly one standalone skin for {model}, found {len(selected)}")

    skin_index, skin = selected[0]
    skeleton_root = int(skin["skeleton"])
    root_extras = nodes[skeleton_root].get("extras") or {}
    skeleton_tag = str(root_extras.get("d1Skeleton", "")).upper()
    if expected_skeleton and skeleton_tag != expected_skeleton:
        raise ValueError(f"skeleton drift: {skeleton_tag} != {expected_skeleton}")

    joint_nodes = [int(x) for x in skin["joints"]]
    joint_set = set(joint_nodes)
    if len(joint_set) != len(joint_nodes):
        raise ValueError("duplicate joint node in skin palette")

    # Standalone guard: every skinned mesh node must use this one selected skin.
    skinned_mesh_nodes = [
        i for i, n in enumerate(nodes)
        if n.get("mesh") is not None and n.get("skin") is not None
    ]
    wrong_skin = [i for i in skinned_mesh_nodes if int(nodes[i]["skin"]) != skin_index]
    if wrong_skin:
        raise ValueError(f"standalone input contains other skinned domains: {wrong_skin[:16]}")
    if not skinned_mesh_nodes:
        raise ValueError("no skinned mesh nodes")

    for ji in joint_nodes:
        transform_joint_node(nodes[ji])

    ibm_ai = int(skin["inverseBindMatrices"])
    ibm = accessor(doc, source_bin, ibm_ai).astype(np.float64)
    if ibm.shape != (len(joint_nodes), 4, 4):
        raise ValueError(f"IBM shape {ibm.shape} does not match {len(joint_nodes)} joints")
    native_ibm = np.stack([PI @ m @ P for m in ibm], axis=0)
    set_accessor(doc, blob, ibm_ai, native_ibm)

    transformed: set[tuple[int, str]] = set()
    channel_count = 0
    total_channel_count = 0
    animation_rows = []
    p3 = P[:3, :3]
    pi3 = PI[:3, :3]
    for animation_index, anim in enumerate(doc.get("animations", [])):
        targeted = 0
        for ch in anim.get("channels", []):
            total_channel_count += 1
            node = int(ch["target"]["node"])
            if node not in joint_set:
                continue
            path = ch["target"]["path"]
            if path not in ("translation", "rotation", "scale"):
                raise ValueError(f"unsupported articulated path {path}")
            sampler = anim["samplers"][int(ch["sampler"])]
            ai = int(sampler["output"])
            key = (ai, path)
            if key not in transformed:
                values = accessor(doc, bytes(blob), ai).astype(np.float64)
                if path in ("translation", "scale"):
                    new_values = values[:, [2, 0, 1]]
                else:
                    rotations = Rotation.from_quat(values).as_matrix()
                    native_rotations = np.einsum("ij,njk,kl->nil", pi3, rotations, p3)
                    new_values = Rotation.from_matrix(native_rotations).as_quat()
                set_accessor(doc, blob, ai, new_values)
                transformed.add(key)
            targeted += 1
            channel_count += 1
        if targeted:
            anim.setdefault("extras", {})["d1BasisDomainModel"] = model
            anim["extras"]["d1ParserBasisUndone"] = True
            animation_rows.append({
                "animation_index": animation_index,
                "name": anim.get("name"),
                "targeted_channel_count": targeted,
            })

    # This is deliberately a standalone adapter. Mixed animation domains should fail
    # rather than silently rotating only one actor in a compound scene.
    if channel_count != total_channel_count:
        raise ValueError(
            f"standalone animation-domain mismatch: targeted {channel_count} of {total_channel_count} channels"
        )

    scene_index = int(doc.get("scene", 0))
    scene = doc["scenes"][scene_index]
    old_roots = [int(x) for x in scene.get("nodes", [])]
    if not old_roots:
        raise ValueError("scene has no root nodes")

    # A quaternion avoids any ambiguity about the column-major JSON encoding of MAT4.
    root_index = len(nodes)
    half = math.sqrt(0.5)
    nodes.append({
        "name": f"D1_{model}_NATIVE_ZUP_TO_GLTF_YUP",
        "rotation": [-half, 0.0, 0.0, half],
        "children": old_roots,
        "extras": {
            "d1BasisAdapter": "native D1 Z-up -> glTF Y-up",
            "d1RowMajorMatrix": Q.tolist(),
            "d1VectorMapping": "[x,y,z] -> [x,z,-y]",
        },
    })
    scene["nodes"] = [root_index]

    fix_extras = {
        "schema": "d1_standalone_articulated_basis_fix/v1",
        "model": model,
        "skeleton": skeleton_tag,
        "skin_index": skin_index,
        "joint_count": len(joint_nodes),
        "skinned_mesh_node_count": len(skinned_mesh_nodes),
        "animation_count": len(animation_rows),
        "animation_channel_count": channel_count,
        "animation_output_accessor_count": len(transformed),
        "inverse_bind_accessor": ibm_ai,
        "parser_basis_undone": "[x,y,z] -> [y,z,x]",
        "native_to_gltf_world_adapter": "[x,y,z] -> [x,z,-y]",
        "world_adapter_root_node": root_index,
        "source_bin_byte_length": len(source_bin),
        "protected_domains": [
            "mesh vertex/index/UV/JOINTS_0/WEIGHTS_0 bytes",
            "materials/textures/images",
            "animation time accessors and clip identity",
        ],
    }
    doc.setdefault("asset", {"version": "2.0"}).setdefault("extras", {})[
        "d1_standalone_articulated_basis_fix"
    ] = fix_extras

    args.out.parent.mkdir(parents=True, exist_ok=True)
    write_glb(args.out, doc, bytes(blob))
    check_doc, check_bin = read_glb(args.out)
    if len(check_bin) != len(source_bin):
        raise ValueError("BIN byte length changed")
    if len(check_doc.get("nodes", [])) != len(nodes):
        raise ValueError("node count changed after round trip")

    report = {
        "schema_version": 1,
        "status": "D1_STANDALONE_ARTICULATED_PARSER_AND_GLTF_BASIS_FIXED",
        "input": str(args.input_glb),
        "input_sha256": sha256_file(args.input_glb),
        "output": str(args.out),
        "output_sha256": sha256_file(args.out),
        "output_bytes": args.out.stat().st_size,
        "model": model,
        "skeleton": skeleton_tag,
        "skin_index": skin_index,
        "joint_count": len(joint_nodes),
        "skinned_mesh_node_count": len(skinned_mesh_nodes),
        "animation_count": len(animation_rows),
        "animation_channel_count": channel_count,
        "animation_output_accessor_count": len(transformed),
        "inverse_bind_accessor": ibm_ai,
        "old_scene_roots": old_roots,
        "new_scene_root": root_index,
        "source_bin_bytes": len(source_bin),
        "output_bin_bytes": len(check_bin),
        "bin_byte_length_unchanged": len(check_bin) == len(source_bin),
        "animation_rows": animation_rows,
        "policy": (
            "Undo only tiger-animation-parser's internal [x,y,z]->[y,z,x] articulated basis, "
            "then wrap the standalone native-Z-up actor in the established D1->glTF Y-up adapter. "
            "Mesh/material/texture/weight/topology/action identity is not reinterpreted."
        ),
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        k: report[k]
        for k in (
            "status", "output_sha256", "output_bytes", "joint_count",
            "skinned_mesh_node_count", "animation_count", "animation_channel_count",
            "animation_output_accessor_count", "bin_byte_length_unchanged",
        )
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
