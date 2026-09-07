#!/usr/bin/env python3
"""Close exact visual dependencies for source-owned D1 activity EntityModels remotely.

Input is ``d1_activity_entity_model_plan/v1``. For every exact EntityModel this tool
parses the retail model payload and closes these source-serialized dependencies:

  EntityModel
    -> vertices1 / vertices2 / old_weights / indices reference-file FileHashes
    -> each reference-file entry's exact backing FileHash payload
    -> inline material FileHashes (variant_shader_index == -1)

External material variants are preserved as unresolved variant records instead of
being guessed. They require an owning EntityResource/shader-variant schema before
material identity can be promoted.

All payloads are resolved through the verified universal package-member catalog and
banked Tiger FileHash routing. No package-name or visual heuristic participates.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_entity_model_probe import D1_ENTITY_MODEL_CLASS, parse_model
from d1_filehash import package_hex
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_split_tar_extract import SplitHttpTar

MATERIAL = "80801AD7"
NULLS = {"00000000", "FFFFFFFF"}
BUFFER_FIELDS = ("vertices1", "vertices2", "old_weights", "indices")


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def meta(c: RemoteCorpus, h: str) -> dict | None:
    m = c.entry_meta(h)
    if m is None:
        return None
    return {
        "tag_hash": norm(m.get("tag_hash", h)),
        "index": m.get("index"),
        "type": m.get("type"),
        "subtype": m.get("subtype"),
        "reference": norm(m.get("reference")),
        "file_size": m.get("file_size"),
        "package_id": package_hex(h),
    }


def payload_digest(b: bytes | None) -> dict:
    return {
        "bytes": None if b is None else len(b),
        "sha256": None if b is None else hashlib.sha256(b).hexdigest(),
    }


def model_hashes(plan: dict) -> list[str]:
    vals = plan.get("model_hashes")
    if vals is None:
        vals = [x.get("model") for x in plan.get("models", [])]
    return sorted({norm(x) for x in vals if x and norm(x) not in NULLS})


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-plan", type=Path, required=True)
    ap.add_argument("--member-catalog", type=Path, action="append", required=True)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--part-count", type=int, default=10)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    plan = json.loads(a.model_plan.read_text(encoding="utf-8"))
    violations: list[str] = []
    if plan.get("schema") != "d1_activity_entity_model_plan/v1":
        violations.append(f"unexpected_model_plan_schema:{plan.get('schema')!r}")
    if plan.get("status") != "D1_ACTIVITY_ENTITY_MODEL_PLAN_COMPLETE":
        violations.append("model_plan_not_complete")
    if plan.get("violations"):
        violations.append("model_plan_contains_violations")
    models = model_hashes(plan)
    if not models:
        violations.append("model_plan_contains_no_models")

    catalogs = load_catalogs(a.member_catalog)
    base = a.base_url.rstrip("/")
    arc = SplitHttpTar(
        [f"{base}/packages.tar.{i:03d}" for i in range(1, a.part_count + 1)],
        retries=6,
        timeout=90,
    )
    c = RemoteCorpus(arc, catalogs, a.runtime)

    rows = []
    edges = []
    buffer_headers: set[str] = set()
    backing_hashes: set[str] = set()
    inline_materials: set[str] = set()
    external_variants = []

    for h in models:
        row = {
            "model": h,
            "package_id": package_hex(h),
            "meta": meta(c, h),
            "meshes": [],
            "violations": [],
        }
        b, src = c.payload(h)
        row["payload_source"] = src
        row["payload"] = payload_digest(b)
        if row["meta"] is None or row["meta"]["reference"] != D1_ENTITY_MODEL_CLASS or b is None:
            row["violations"].append("entity_model_unavailable_or_class_mismatch")
        else:
            try:
                parsed = parse_model(b, "PS4")
            except Exception as ex:
                row["violations"].append("parse_model:" + repr(ex))
            else:
                row["mesh_count"] = parsed["mesh_count"]
                for mi, mesh in enumerate(parsed["meshes"]):
                    mout = {
                        "mesh_index": mi,
                        "model_scale": mesh.get("model_scale"),
                        "model_translation": mesh.get("model_translation"),
                        "texcoord_scale": mesh.get("texcoord_scale"),
                        "texcoord_translation": mesh.get("texcoord_translation"),
                        "buffer_headers": [],
                        "parts": [],
                    }
                    for field in BUFFER_FIELDS:
                        bh = norm(mesh.get(field))
                        if bh in NULLS:
                            continue
                        bm = meta(c, bh)
                        bb, bsrc = c.payload(bh)
                        bout = {
                            "field": field,
                            "header": bh,
                            "package_id": package_hex(bh),
                            "meta": bm,
                            "payload_source": bsrc,
                            "header_payload": payload_digest(bb),
                            "backing": None,
                        }
                        buffer_headers.add(bh)
                        edges.append({
                            "subject": h,
                            "predicate": "ENTITY_MODEL_BUFFER_HEADER",
                            "object": bh,
                            "evidence_class": "TYPED_EXACT",
                            "attrs": {"mesh_index": mi, "field": field},
                        })
                        if bm is None:
                            row["violations"].append(f"mesh[{mi}].{field}:buffer_header_missing")
                        else:
                            backing = norm(bm.get("reference"))
                            if backing in NULLS:
                                row["violations"].append(f"mesh[{mi}].{field}:null_backing_reference")
                            else:
                                backing_hashes.add(backing)
                                pb, psrc = c.payload(backing)
                                pm = meta(c, backing)
                                bout["backing"] = {
                                    "hash": backing,
                                    "package_id": package_hex(backing),
                                    "meta": pm,
                                    "payload_source": psrc,
                                    "payload": payload_digest(pb),
                                }
                                edges.append({
                                    "subject": bh,
                                    "predicate": "REFERENCE_FILE_BACKING_PAYLOAD",
                                    "object": backing,
                                    "evidence_class": "TYPED_EXACT",
                                    "attrs": {"model": h, "mesh_index": mi, "field": field},
                                })
                                if pb is None:
                                    row["violations"].append(f"mesh[{mi}].{field}:backing_payload_missing:{backing}")
                        mout["buffer_headers"].append(bout)

                    for pi, part in enumerate(mesh.get("parts", [])):
                        variant = int(part.get("variant_shader_index", -1))
                        mh = norm(part.get("material"))
                        pout = {
                            "part_index": pi,
                            "lod": part.get("lod"),
                            "variant_shader_index": variant,
                            "external_identifier": part.get("external_identifier"),
                            "material": mh,
                            "material_resolution": None,
                        }
                        if variant == -1:
                            if mh not in NULLS:
                                inline_materials.add(mh)
                                mm = meta(c, mh)
                                mb, msrc = c.payload(mh)
                                pout["material_resolution"] = {
                                    "status": "inline_exact",
                                    "package_id": package_hex(mh),
                                    "meta": mm,
                                    "payload_source": msrc,
                                    "payload": payload_digest(mb),
                                }
                                edges.append({
                                    "subject": h,
                                    "predicate": "ENTITY_MODEL_INLINE_MATERIAL",
                                    "object": mh,
                                    "evidence_class": "TYPED_EXACT",
                                    "attrs": {"mesh_index": mi, "part_index": pi, "lod": part.get("lod")},
                                })
                                if mm is None or mm["reference"] != MATERIAL or mb is None:
                                    row["violations"].append(f"mesh[{mi}].part[{pi}]:inline_material_missing_or_class_mismatch:{mh}")
                        else:
                            rec = {
                                "model": h,
                                "mesh_index": mi,
                                "part_index": pi,
                                "variant_shader_index": variant,
                                "external_identifier": part.get("external_identifier"),
                                "serialized_material_field": mh,
                                "lod": part.get("lod"),
                                "status": "REQUIRES_OWNING_VARIANT_SCHEMA",
                            }
                            external_variants.append(rec)
                            pout["material_resolution"] = {
                                "status": "external_variant_not_promoted",
                                "reason": "variant_shader_index != -1; model-local material field is not sufficient ownership proof",
                            }
                        mout["parts"].append(pout)
                    row["meshes"].append(mout)

        if row["violations"]:
            violations.extend(f"{h}:{x}" for x in row["violations"])
        rows.append(row)

    out = {
        "schema": "d1_remote_activity_model_visual_dependency_closure/v1",
        "status": "D1_REMOTE_ACTIVITY_MODEL_VISUAL_DEPENDENCY_CLOSURE_COMPLETE" if not violations else "D1_REMOTE_ACTIVITY_MODEL_VISUAL_DEPENDENCY_CLOSURE_WITH_VIOLATIONS",
        "source_model_plan": str(a.model_plan),
        "model_count": len(models),
        "models": models,
        "buffer_header_count": len(buffer_headers),
        "buffer_headers": sorted(buffer_headers),
        "backing_payload_count": len(backing_hashes),
        "backing_payload_hashes": sorted(backing_hashes),
        "inline_material_count": len(inline_materials),
        "inline_materials": sorted(inline_materials),
        "external_variant_part_count": len(external_variants),
        "external_variant_parts": external_variants,
        "rows": rows,
        "typed_edges": edges,
        "typed_edge_count": len(edges),
        "violations": violations,
        "policy": (
            "Buffer headers, backing payloads and inline materials are admitted only from source-parsed EntityModel "
            "fields. old_weights is retained for skinned models. External variant materials are not guessed from "
            "the model-local material field and remain unresolved until their owning variant schema is closed. "
            "All FileHashes are resolved against the verified universal package catalog using banked D1 Tiger routing."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(
        "STATUS", out["status"],
        "MODELS", out["model_count"],
        "BUFFER_HEADERS", out["buffer_header_count"],
        "BACKINGS", out["backing_payload_count"],
        "INLINE_MATERIALS", out["inline_material_count"],
        "EXTERNAL_VARIANT_PARTS", out["external_variant_part_count"],
        "VIOLATIONS", len(violations),
    )
    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
