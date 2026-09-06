#!/usr/bin/env python3
"""Census exact D1 Guardian stage-part dye selectors for proven model selections.

This probe joins a previously byte-proven Guardian visual-context report to the
serialized SEntityModel stage-part records.  It deliberately uses the same
index-range grouping key as d1_entity_model_export.py so each output row maps to
one exported GLB primitive name:

    <MODEL>_mesh<MESH>_range<INDEX_OFFSET>_<INDEX_COUNT>

For every grouped range it preserves every candidate part and requires a single
GearDyeChangeColorIndex before declaring the range dye-resolved.  The semantic
mapping is delegated to d1_dye_stage_part_semantics.py, which records Bungie's
D1 renderer convention separately from the raw byte.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_dye_stage_part_semantics import decode_gear_dye_change_color_index
from d1_entity_model_probe import D1_ENTITY_MODEL_CLASS, parse_model
from d1_investment_arrangement_probe import filehash_pkg_index
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_split_tar_extract import SplitHttpTar


def norm_hash(value: str) -> str:
    value = str(value).upper().removeprefix("0X").zfill(8)
    int(value, 16)
    return value


def fetch_exact_model(tag: str, views: dict[int, RemoteLogicalPackage]) -> tuple[dict, bytes]:
    h = int(tag, 16)
    pkg, idx = filehash_pkg_index(h)
    view = views.get(pkg)
    if view is None:
        raise KeyError(f"{tag}: package {pkg:04X} absent from verified catalogs")
    if idx >= len(view.entries):
        raise IndexError(f"{tag}: file index {idx} outside package {pkg:04X}")
    entry = view.entries[idx]
    if entry["tag_hash"].upper() != tag:
        raise ValueError(f"{tag}: logical entry mismatch {entry['tag_hash']}")
    if entry["reference"].upper() != D1_ENTITY_MODEL_CLASS:
        raise ValueError(f"{tag}: reference {entry['reference']} is not D1 SEntityModel {D1_ENTITY_MODEL_CLASS}")
    return entry, view.entry(idx)


def candidate_summary(part_index: int, p: dict) -> dict:
    return {
        "part_index": part_index,
        "material": p["material"],
        "variant_shader_index": p["variant_shader_index"],
        "primitive_type": p["primitive_type"],
        "index_offset": p["index_offset"],
        "index_count": p["index_count"],
        "external_identifier": p["external_identifier"],
        "flags_d1": p["flags_d1"],
        "gear_dye_change_color_index": p["gear_dye_change_color_index"],
        "lod": p["lod"],
        "lod_run": p["lod_run"],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--visual-context", type=Path, required=True)
    ap.add_argument("--member-catalog", type=Path, action="append", required=True)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--part-count", type=int, default=10)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--expected-body-role", choices=("masculine", "feminine"))
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    visual = json.loads(a.visual_context.read_text())
    if a.expected_body_role and visual.get("body_role") != a.expected_body_role:
        raise ValueError(f"expected body role {a.expected_body_role}, got {visual.get('body_role')!r}")
    selected = []
    seen = set()
    for row in visual.get("models", []):
        tag = norm_hash(row.get("tag_hash") or "")
        if tag in seen:
            raise ValueError(f"duplicate selected model {tag}")
        seen.add(tag)
        selected.append({
            "tag_hash": tag,
            "entity_resource_hash": row.get("entity_resource_hash"),
            "examples": row.get("examples") or [],
        })
    if not selected:
        raise SystemExit("visual-context report selected no models")

    catalogs = load_catalogs(a.member_catalog)
    missing = sorted({filehash_pkg_index(int(x["tag_hash"], 16))[0] for x in selected} - set(catalogs))
    if missing:
        raise SystemExit("missing verified package catalogs: " + ", ".join(f"{x:04X}" for x in missing))

    base = a.base_url.rstrip("/")
    arc = SplitHttpTar([f"{base}/packages.tar.{i:03d}" for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    views = {pkg: RemoteLogicalPackage(arc, fam, a.runtime) for pkg, fam in sorted(catalogs.items())}

    models = []
    all_groups = []
    conflicts = []
    selector_counts = collections.Counter()
    semantic_counts = collections.Counter()

    for sel in selected:
        tag = sel["tag_hash"]
        entry, payload = fetch_exact_model(tag, views)
        model = parse_model(payload, "PS4")
        mrow = {
            **sel,
            "source_package_id": f"{filehash_pkg_index(int(tag, 16))[0]:04X}",
            "source_file_index": filehash_pkg_index(int(tag, 16))[1],
            "entry_reference": entry["reference"].upper(),
            "mesh_count": model["mesh_count"],
            "meshes": [],
        }
        for mi, mesh in enumerate(model["meshes"]):
            grouped: dict[tuple[int, int, int], list[tuple[int, dict]]] = {}
            for pi, part in enumerate(mesh["parts"]):
                key = (part["index_offset"], part["index_count"], part["primitive_type"])
                grouped.setdefault(key, []).append((pi, part))

            grows = []
            for key, candidates in grouped.items():
                off, count, primitive = key
                dye_values = sorted({p["gear_dye_change_color_index"] for _, p in candidates})
                materials = sorted({p["material"] for _, p in candidates})
                lods = sorted({p["lod"] for _, p in candidates})
                name = f"{tag}_mesh{mi}_range{off}_{count}"
                row = {
                    "name": name,
                    "model_tag": tag,
                    "mesh_index": mi,
                    "index_offset": off,
                    "index_count": count,
                    "primitive_type": primitive,
                    "candidate_count": len(candidates),
                    "candidate_materials": materials,
                    "candidate_lods": lods,
                    "candidate_dye_change_color_indices": dye_values,
                    "candidates": [candidate_summary(pi, p) for pi, p in candidates],
                    "resolved": len(dye_values) == 1,
                }
                if len(dye_values) == 1:
                    raw = dye_values[0]
                    semantic = decode_gear_dye_change_color_index(raw)
                    row["gear_dye_change_color_index"] = raw
                    row["dye_semantics"] = semantic
                    selector_counts[raw] += 1
                    semantic_counts[(semantic.get("armor_channel_name"), semantic["color_role"])] += 1
                else:
                    row["error"] = "same exported index range has conflicting serialized dye selectors"
                    conflicts.append(row)
                grows.append(row)
                all_groups.append(row)

            mrow["meshes"].append({
                "mesh_index": mi,
                "part_count": mesh["part_count"],
                "unique_range_count": len(grows),
                "groups": grows,
            })
        mrow["unique_range_count"] = sum(x["unique_range_count"] for x in mrow["meshes"])
        models.append(mrow)

    report = {
        "schema": "d1_guardian_stage_part_dye_census/v1",
        "body_role": visual.get("body_role"),
        "model_count": len(models),
        "unique_range_count": len(all_groups),
        "resolved_range_count": sum(bool(x["resolved"]) for x in all_groups),
        "conflict_count": len(conflicts),
        "selector_distribution": {str(k): v for k, v in sorted(selector_counts.items())},
        "semantic_distribution": {
            f"{channel or 'none'}:{role}": count
            for (channel, role), count in sorted(semantic_counts.items(), key=lambda x: str(x[0]))
        },
        "models": models,
        "conflicts": conflicts,
        "policy": (
            "Raw GearDyeChangeColorIndex is read directly from each D1 SEntityModel stage-part byte at +0x1E. "
            "Parts are grouped with the exact index_offset/index_count/primitive_type key used by the exporter. "
            "A range receives semantic dye metadata only when every serialized candidate for that range agrees."
        ),
        "semantic_source": (
            "Bungie archived web renderer Spasm.RenderablePart: changeColorIndex 0/1 -> gear dye slot 0 primary/secondary; "
            "2/3 -> slot 1 primary/secondary; 4/5 -> slot 2 primary/secondary; 6/7 -> slot 3 investment decal."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + "\n")

    print("MODELS", report["model_count"], "RANGES", report["unique_range_count"],
          "RESOLVED", report["resolved_range_count"], "CONFLICTS", report["conflict_count"])
    print("SELECTORS", report["selector_distribution"])
    print("SEMANTICS", report["semantic_distribution"])
    for m in models:
        name = (m.get("examples") or [{}])[0].get("name")
        print("MODEL", name, m["tag_hash"], "ranges", m["unique_range_count"])
    for c in conflicts:
        print("CONFLICT", c["name"], c["candidate_dye_change_color_indices"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
