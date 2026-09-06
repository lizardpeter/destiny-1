#!/usr/bin/env python3
"""Resolve only the source-proven D1 Guardian EntityResource render parent.

This intentionally does not inspect model vertex/index streams.  It exists for
material resolution paths that need the owning EntityResource's standard D1
model parent (TexturePlatesROI, ExternalMaterialsMap, ExternalMaterials) but
must not fail because an unrelated cross-package geometry stream is absent from
the current package catalog.

Input is a source-proven Guardian selection report with arrangements and
resolved_body_assignments.  For each selected body assignment we follow exactly:

    s_entity selection -> EntityResource resource_hash -> standard D1 model
    parent -> embedded model TagHash + external material structures

The probe fails closed on missing catalogs, wrong EntityResource class, parent
layout errors, embedded-model mismatches, duplicates, or any unresolved row.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_investment_arrangement_probe import filehash_pkg_index
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_render_owner_probe import ENTITY_RESOURCE_CLASS, parse_parent_resource
from d1_split_tar_extract import SplitHttpTar


def norm_hash(v: str) -> str:
    h = str(v).upper().removeprefix("0X").zfill(8)
    if len(h) != 8:
        raise ValueError(v)
    int(h, 16)
    return h


def pkg_id(tag: str) -> int:
    return filehash_pkg_index(int(norm_hash(tag), 16))[0]


def selected_from_report(report: dict, body_role: str) -> list[dict]:
    rows: list[dict] = []
    seen: set[tuple[str, str]] = set()
    arrangements = report.get("arrangements")
    if not isinstance(arrangements, list):
        raise ValueError("selection report lacks arrangements[]")

    for arrangement in arrangements:
        assignments = arrangement.get("resolved_body_assignments") or []
        for assignment in assignments:
            if assignment.get("body_role") != body_role:
                continue
            entity = assignment.get("entity_resolution") or {}
            entity_hash = norm_hash(entity.get("entity_hash"))
            for resource in entity.get("resources") or []:
                embedded = resource.get("embedded_model") or {}
                if not embedded.get("resolved"):
                    continue
                model_tag = norm_hash(embedded.get("tag_hash"))
                resource_tag = norm_hash(resource.get("resource_hash"))
                key = (model_tag, resource_tag)
                if key in seen:
                    continue
                seen.add(key)
                rows.append({
                    "tag_hash": model_tag,
                    "entity_hash": entity_hash,
                    "entity_resource_hash": resource_tag,
                    "body_role": body_role,
                    "arrangement_index": arrangement.get("arrangement_index"),
                    "className": arrangement.get("className"),
                    "examples": arrangement.get("examples") or [],
                })
    return rows


def fetch_exact(tag: str, views: dict[int, RemoteLogicalPackage]) -> tuple[dict, bytes]:
    pkg, idx = filehash_pkg_index(int(tag, 16))
    view = views.get(pkg)
    if view is None:
        raise KeyError(f"{tag}: package {pkg:04X} absent from selected catalogs")
    if idx < 0 or idx >= len(view.entries):
        raise IndexError(f"{tag}: index {idx} outside package {pkg:04X}")
    entry = view.entries[idx]
    actual = str(entry.get("tag_hash") or "").upper()
    if actual != tag:
        raise ValueError(f"{tag}: logical entry mismatch {actual}")
    return entry, view.entry(idx)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--body-role", choices=("masculine", "feminine"), required=True)
    ap.add_argument("--member-catalog", type=Path, action="append", required=True)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--part-count", type=int, default=10)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    source = json.loads(a.report.read_text())
    selected = selected_from_report(source, a.body_role)
    if not selected:
        raise SystemExit("no source-proven models selected from report")

    # Ambiguous ownership is not acceptable for this material resolver.  A model
    # may appear only once in the body selection unless the exact same tuple was
    # already deduplicated above.
    model_counts: dict[str, int] = {}
    for row in selected:
        model_counts[row["tag_hash"]] = model_counts.get(row["tag_hash"], 0) + 1
    ambiguous = sorted(k for k, v in model_counts.items() if v != 1)
    if ambiguous:
        raise SystemExit("ambiguous model ownership: " + ", ".join(ambiguous))

    catalogs = load_catalogs(a.member_catalog)
    needed_packages = sorted({pkg_id(x["entity_resource_hash"]) for x in selected})
    missing = [p for p in needed_packages if p not in catalogs]
    if missing:
        raise SystemExit("missing EntityResource package catalogs: " + ", ".join(f"{p:04X}" for p in missing))

    base = a.base_url.rstrip("/")
    archive = SplitHttpTar(
        [f"{base}/packages.tar.{i:03d}" for i in range(1, a.part_count + 1)],
        retries=6,
        timeout=90,
    )
    views = {
        pkg: RemoteLogicalPackage(archive, catalogs[pkg], a.runtime)
        for pkg in needed_packages
    }

    models = []
    errors = []
    for sel in selected:
        rec = dict(sel)
        model_tag = sel["tag_hash"]
        resource_tag = sel["entity_resource_hash"]
        try:
            entry, payload = fetch_exact(resource_tag, views)
            reference = str(entry.get("reference") or "").upper()
            rec["entity_resource_reference"] = reference
            if reference != ENTITY_RESOURCE_CLASS:
                raise ValueError(
                    f"{resource_tag}: expected EntityResource class {ENTITY_RESOURCE_CLASS}, got {reference}"
                )
            parent = parse_parent_resource(payload)
            if parent is None:
                raise ValueError(f"{resource_tag}: standard D1 model parent not present")
            if parent.get("error"):
                raise ValueError(f"{resource_tag}: parent parse error {parent['error']}")
            if parent.get("embedded_model_tag_hash") != model_tag:
                raise ValueError(
                    f"{resource_tag}: parent embeds {parent.get('embedded_model_tag_hash')}, expected {model_tag}"
                )
            if (parent.get("external_materials_map") or {}).get("error"):
                raise ValueError(f"{resource_tag}: external material map parse failed")
            if (parent.get("external_materials") or {}).get("error"):
                raise ValueError(f"{resource_tag}: external material bank parse failed")
            rec["render_parent"] = parent
        except Exception as ex:
            rec["error"] = repr(ex)
            errors.append({
                "tag_hash": model_tag,
                "entity_resource_hash": resource_tag,
                "error": repr(ex),
            })
        models.append(rec)

    report = {
        "schema": "d1_guardian_render_parent_context/v1",
        "body_role": a.body_role,
        "model_count": len(models),
        "needed_package_ids": [f"{p:04X}" for p in needed_packages],
        "models": models,
        "errors": errors,
        "policy": (
            "Source-proven model ownership is followed only through the selected s_entity EntityResource. "
            "This probe intentionally does not inspect geometry streams. Standard D1 model-parent, embedded-model, "
            "ExternalMaterialsMap, and ExternalMaterials validation fail closed."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + "\n")

    print("MODELS", report["model_count"], "PACKAGES", report["needed_package_ids"], "ERRORS", len(errors))
    for rec in models:
        parent = rec.get("render_parent") or {}
        print(
            "MODEL", rec["tag_hash"], "RESOURCE", rec["entity_resource_hash"],
            "EXTERNAL_MAP", parent.get("external_materials_map_entries"),
            "EXTERNAL_MATERIALS", parent.get("external_material_tag_hashes"),
        )
    if errors:
        raise SystemExit(f"{len(errors)} render-parent resolution error(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
