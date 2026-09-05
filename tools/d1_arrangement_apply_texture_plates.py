#!/usr/bin/env python3
"""Apply byte-proven D1 per-model texture plates to an arrangement GLB.

This is the generic form of the presentation layer first proven on Gjallarhorn
arrangement 1229.  It does not contain a weapon/model list.  The mapping is read
from the supplied plate report and matched to geometry nodes by the `d1Model`
provenance emitted by the geometry exporter.

Required normalized plate ownership per model:

    model_tag
    header_tag
    plate_tags: {albedo, normal, gstack}

Accepted report shapes:

1. `models` array, each row already containing the fields above.
2. `plates` array with model_tag, header_tag, role, plate_tag rows.

Albedo and normal are connected to portable core glTF PBR.  GStack is embedded
and preserved as provenance but is not guessed into metallic/roughness channels.
Gear-dye semantics/colors are likewise not synthesized.
"""
from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path

from pygltflib import (
    GLTF2, Image, Texture, Sampler, Material, PbrMetallicRoughness,
    TextureInfo, NormalMaterialTexture,
)

LINEAR = 9729
LINEAR_MIPMAP_LINEAR = 9987
CLAMP_TO_EDGE = 33071
ROLES = ("albedo", "normal", "gstack")


def data_uri(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def normalize_plate_rows(report: dict) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    if "models" in report:
        for src in report["models"]:
            model = src["model_tag"].upper()
            header = src["header_tag"].upper()
            tags = {k.lower(): v.upper() for k, v in src.get("plate_tags", {}).items()}
            if set(tags) != set(ROLES):
                raise RuntimeError(f"{model}: incomplete plate_tags {tags}")
            rec = {"model_tag": model, "header_tag": header, "plate_tags": tags}
            if model in rows and rows[model] != rec:
                raise RuntimeError(f"duplicate conflicting model plate mapping {model}")
            rows[model] = rec
        if not rows:
            raise RuntimeError("models plate report is empty")
        return rows

    if "plates" not in report:
        raise RuntimeError("plate report has neither models nor plates schema")
    for p in report["plates"]:
        if "model_tag" not in p:
            raise RuntimeError("generic plates schema requires model_tag on every plate row")
        model = p["model_tag"].upper()
        header = p["header_tag"].upper()
        role = p["role"].lower()
        tag = p["plate_tag"].upper()
        if role not in ROLES:
            raise RuntimeError(f"unexpected plate role {role!r}")
        rec = rows.setdefault(model, {"model_tag": model, "header_tag": header, "plate_tags": {}})
        if rec["header_tag"] != header:
            raise RuntimeError(f"{model}: conflicting plate headers {rec['header_tag']} vs {header}")
        old = rec["plate_tags"].get(role)
        if old is not None and old != tag:
            raise RuntimeError(f"{model}: conflicting {role} plates {old} vs {tag}")
        rec["plate_tags"][role] = tag
    for model, rec in rows.items():
        if set(rec["plate_tags"]) != set(ROLES):
            raise RuntimeError(f"{model}: incomplete plate roles {rec['plate_tags']}")
    if not rows:
        raise RuntimeError("plates report is empty")
    return rows


def find_plate_path(plate_dir: Path, model: str, row: dict, role: str) -> Path:
    header = row["header_tag"]
    tag = row["plate_tags"][role]
    candidates = [
        plate_dir / f"{header}_{role}_plate.png",
        plate_dir / f"{tag}.png",
        plate_dir / f"{model}_{header}_{role}_plate.png",
    ]
    found = [p for p in candidates if p.is_file()]
    if len(found) != 1:
        raise FileNotFoundError(
            f"{model}/{role}: expected exactly one plate image among {[str(x) for x in candidates]}, found {[str(x) for x in found]}"
        )
    return found[0]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input_glb", type=Path)
    ap.add_argument("--plate-dir", type=Path, required=True)
    ap.add_argument("--plate-report", type=Path, required=True)
    ap.add_argument("--arrangement-index", type=int)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    a = ap.parse_args()

    gltf = GLTF2().load_binary(str(a.input_glb))
    plate_report = json.loads(a.plate_report.read_text())
    rows = normalize_plate_rows(plate_report)

    mesh_owner: dict[int, str] = {}
    for node in gltf.nodes:
        if node.mesh is None:
            continue
        extras = node.extras or {}
        model = extras.get("d1Model")
        if not model:
            raise RuntimeError(f"mesh node {node.name!r} lacks d1Model provenance")
        model = str(model).upper()
        if model not in rows:
            raise RuntimeError(f"mesh node {node.name!r} references model {model} absent from plate report")
        mi = int(node.mesh)
        old = mesh_owner.get(mi)
        if old is not None and old != model:
            raise RuntimeError(f"mesh {mi} is shared across conflicting d1Model owners {old}/{model}")
        mesh_owner[mi] = model
    if not mesh_owner:
        raise RuntimeError("input GLB contains no d1Model-owned meshes")
    used_models = set(mesh_owner.values())
    extra_models = set(rows) - used_models
    if extra_models:
        raise RuntimeError(f"plate report contains models not represented by GLB geometry: {sorted(extra_models)}")

    gltf.samplers.append(Sampler(
        magFilter=LINEAR,
        minFilter=LINEAR_MIPMAP_LINEAR,
        wrapS=CLAMP_TO_EDGE,
        wrapT=CLAMP_TO_EDGE,
    ))
    sampler_index = len(gltf.samplers) - 1

    plate_assets = {}
    for model in sorted(used_models):
        row = rows[model]
        header = row["header_tag"]
        role_assets = {}
        for role in ROLES:
            path = find_plate_path(a.plate_dir, model, row, role)
            ii = len(gltf.images)
            gltf.images.append(Image(
                name=f"{model}_{header}_{role}",
                uri=data_uri(path),
                extras={
                    "d1Model": model,
                    "d1TexturePlateHeader": header,
                    "d1TexturePlateRole": role,
                    "d1TexturePlateTag": row["plate_tags"][role],
                    "nativeInterpretation": role if role in ("albedo", "normal") else "GStack preserved; portable semantics unresolved",
                },
            ))
            if role in ("albedo", "normal"):
                ti = len(gltf.textures)
                gltf.textures.append(Texture(name=f"{model}_{role}", source=ii, sampler=sampler_index))
            else:
                ti = None
            role_assets[role] = {"image": ii, "texture": ti, "path": str(path), "tag": row["plate_tags"][role]}
        plate_assets[model] = role_assets

    old_materials = list(gltf.materials)
    material_map = {}
    material_rows = []
    new_materials = []
    for mesh_index, mesh in enumerate(gltf.meshes):
        if mesh_index not in mesh_owner:
            raise RuntimeError(f"mesh {mesh_index} has no d1Model-owning node")
        model = mesh_owner[mesh_index]
        row = rows[model]
        header = row["header_tag"]
        for prim in mesh.primitives:
            if prim.material is None:
                raise RuntimeError(f"mesh {mesh_index} primitive lacks native material provenance")
            old_index = int(prim.material)
            key = (model, old_index)
            new_index = material_map.get(key)
            if new_index is None:
                old = old_materials[old_index]
                native_extras = dict(old.extras or {})
                native_hash = native_extras.get("d1DisplayMaterial")
                native_candidates = native_extras.get("nativeMaterialCandidates", [])
                extras = {
                    **native_extras,
                    "d1Model": model,
                    "d1TexturePlateHeader": header,
                    "d1AlbedoPlate": row["plate_tags"]["albedo"],
                    "d1NormalPlate": row["plate_tags"]["normal"],
                    "d1GStackPlate": row["plate_tags"]["gstack"],
                    "d1GStackImageIndex": plate_assets[model]["gstack"]["image"],
                    "portablePolicy": "exact model plate albedo+normal; GStack preserved but not mapped to glTF metallic/roughness; gear dyes not synthesized",
                }
                mat = Material(
                    name=f"D1_{model}_{native_hash or old_index}_PLATE_PBR",
                    pbrMetallicRoughness=PbrMetallicRoughness(
                        baseColorTexture=TextureInfo(index=plate_assets[model]["albedo"]["texture"]),
                        metallicFactor=0.0,
                        roughnessFactor=0.65,
                    ),
                    normalTexture=NormalMaterialTexture(index=plate_assets[model]["normal"]["texture"]),
                    doubleSided=old.doubleSided,
                    extras=extras,
                )
                new_index = len(new_materials)
                new_materials.append(mat)
                material_map[key] = new_index
                material_rows.append({
                    "model_tag": model,
                    "old_material_index": old_index,
                    "new_material_index": new_index,
                    "native_material_hash": native_hash,
                    "native_material_candidates": native_candidates,
                    "plate_header": header,
                    "albedo_plate": row["plate_tags"]["albedo"],
                    "normal_plate": row["plate_tags"]["normal"],
                    "gstack_plate": row["plate_tags"]["gstack"],
                })
            prim.material = new_index

    gltf.materials = new_materials
    extras = gltf.extras or {}
    extras["d1PortableTexturePlateLayer"] = {
        "arrangementIndex": a.arrangement_index,
        "modelPlateHeaders": {m: rows[m]["header_tag"] for m in sorted(rows)},
        "geometryChanged": False,
        "albedoAndNormalConnected": True,
        "gstackEmbeddedButNotInterpreted": True,
        "gearDyesApplied": False,
    }
    gltf.extras = extras
    gltf.asset.generator = "destiny-1 generic exact arrangement texture-plate portable layer"

    a.out.parent.mkdir(parents=True, exist_ok=True)
    gltf.save_binary(str(a.out))
    check = GLTF2().load_binary(str(a.out))
    if len(check.meshes) != len(gltf.meshes):
        raise RuntimeError("mesh count changed during texture application")

    report = {
        "input_glb": str(a.input_glb),
        "output_glb": str(a.out),
        "output_bytes": a.out.stat().st_size,
        "arrangement_index": a.arrangement_index,
        "model_count": len(used_models),
        "mesh_count": len(check.meshes),
        "material_count": len(check.materials),
        "image_count": len(check.images),
        "texture_count": len(check.textures),
        "plate_assets": plate_assets,
        "materials": material_rows,
        "policy": {
            "geometry": "unchanged exact input arrangement geometry",
            "albedo_normal": "byte-proven per-model texture plates connected to core glTF",
            "gstack": "embedded/proven but not interpreted as glTF PBR channels",
            "dyes": "not applied; final native dye semantics/colors remain separate work",
        },
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k not in ("plate_assets", "materials")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
