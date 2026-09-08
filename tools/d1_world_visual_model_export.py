#!/usr/bin/env python3
"""Export every exact D1 visual world EntityModel/owning-parent pair.

Geometry decoding is delegated to the established articulated-model decoder, but
selection is deliberately different from the specialized articulated stage-0 path.
Pinned Charm EntityModel.Load(MostDetailed) considers highest-detail LOD categories
across the complete part array; StagePartOffsets only assign GroupIndex. For a
portable Blender-facing world preview we therefore build the same source-complete
highest-detail *visual union* already validated by the Crota-body adapter:

* inspect every source part in every StagePartOffsets group;
* retain only Charm highest-detail LOD categories {0,1,2,3,10};
* resolve each Material through the exact owning EntityResource;
* group exact duplicate geometry ranges by (mesh,index_offset,index_count,primitive);
* emit the first source-ordered candidate once, while preserving every later render
  variant, material, group and part index losslessly in the report.

This prevents duplicate render variants from being drawn on top of one another in a
portable GLB without pretending the alternatives do not exist. It also avoids the
incorrect old assumption that StagePartOffsets[0:1] is universally the visible group.
Specialized Guardian/Crota articulated adapters may still impose independently proven
stage selection; this generic map-entity exporter does not change them.

Identity remains keyed by ``(EntityModel, owning EntityResource)`` so the same model
may safely appear under distinct external material maps in another Activity.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import d1_tower_map_schema_validate_v5 as v5
import d1_world_articulated_model_export as articulated

PLAN_STATUS = "D1_WORLD_VISUAL_ENTITY_PLAN_COMPLETE"
BIND_STATUS = "D1_WORLD_ENTITY_MODEL_MATERIAL_BINDINGS_COMPLETE"
HIGHEST_LODS = articulated.HIGHEST_LODS
NULLS = articulated.NULLS


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def exact_pairs(plan: dict) -> list[tuple[str, str]]:
    declared = plan.get("unique_model_parent_pairs") or []
    pairs = []
    for row in declared:
        m = norm(row.get("model"))
        p = norm(row.get("parent_resource"))
        pairs.append((m, p))
    out = sorted(set(pairs))
    if len(out) != int(plan.get("unique_model_parent_pair_count", -1)):
        raise ValueError("visual plan model-parent pair count mismatch")
    return out


def binding_pairs(doc: dict) -> dict[tuple[str, str], dict]:
    if doc.get("status") != BIND_STATUS:
        raise ValueError(f"material bindings are not complete: {doc.get('status')!r}")
    out = {}
    for row in doc.get("bindings", []):
        key = (norm(row.get("model")), norm(row.get("parent_resource")))
        if key in out:
            raise ValueError(f"duplicate material binding pair {key}")
        if not row.get("validation_ok"):
            raise ValueError(f"material binding pair is not valid {key}")
        out[key] = row
    return out


def _group_map(offsets: list[int], part_count: int) -> tuple[list[int], list[dict], dict[int, int]]:
    """Reproduce pinned Charm EntityModel.GenerateParts GroupIndex construction."""
    bounds = sorted(set(int(x) for x in offsets))
    intervals = []
    out: dict[int, int] = {}
    for gi in range(max(0, len(bounds) - 1)):
        start, end = bounds[gi], bounds[gi + 1]
        if start < 0 or end < start or end > part_count:
            raise ValueError(f"invalid StagePartOffsets interval [{start},{end})/{part_count}")
        intervals.append({"group_index": gi, "start": start, "end": end})
        for pi in range(start, end):
            out[pi] = gi
    return bounds, intervals, out


def visual_union_ranges(model: dict, binding: dict) -> tuple[list[dict], list[dict]]:
    """Build the source-complete Charm-highest-detail portable visual union.

    This has the same return shape as articulated.selected_ranges so its proven
    geometry decoder can be reused without changing the specialized stage-0 path.
    """
    selected = []
    mesh_summaries = []
    bmeshes = {int(x["mesh_index"]): x for x in binding.get("meshes", [])}
    for mi, mesh in enumerate(model["meshes"]):
        bm = bmeshes.get(mi)
        if bm is None:
            raise ValueError(f"mesh {mi}: no material binding")
        bparts = {int(x["part_index"]): x for x in bm.get("parts", [])}
        offsets = [int(x) for x in (mesh.get("stage_part_offsets_source_derived") or [])]
        if len(offsets) < 2:
            raise ValueError(f"mesh {mi}: missing D1 StagePartOffsets boundaries")
        bounds, intervals, group_for_part = _group_map(offsets, len(mesh["parts"]))

        grouped: dict[tuple[int, int, int], list[dict]] = defaultdict(list)
        explicit_null_parts = []
        highest_parts = []
        for pi, p in enumerate(mesh["parts"]):
            lod = int(p["lod"])
            if lod not in HIGHEST_LODS:
                continue
            highest_parts.append(pi)
            if pi not in group_for_part:
                # Charm GenerateParts indexes partGroups[i] for every selected part;
                # absence is therefore malformed rather than an invitation to guess.
                raise ValueError(f"mesh {mi} part {pi}: highest-detail part has no StagePartOffsets GroupIndex")
            bp = bparts.get(pi)
            if bp is None:
                raise ValueError(f"mesh {mi} part {pi}: missing exact material binding")
            sm = bp.get("selected_material") or {}
            mh = norm(sm.get("hash", "FFFFFFFF"))
            if mh in NULLS or bp.get("selection_status") == "EXPLICIT_NULL_MATERIAL":
                # Pinned ROI EntityModel.GenerateParts skips a null Material.
                explicit_null_parts.append(pi)
                continue
            if not sm.get("class_matches"):
                raise ValueError(f"mesh {mi} part {pi}: selected non-null material unresolved {mh}")
            key = (int(p["index_offset"]), int(p["index_count"]), int(p["primitive_type"]))
            grouped[key].append({
                "part_index": pi,
                "group_index": group_for_part[pi],
                "lod": lod,
                "material": mh,
                "gear_dye_change_color_index": int(p["gear_dye_change_color_index"]),
                "variant_shader_index": int(p["variant_shader_index"]),
                "flags_d1": int(p["flags_d1"]),
                "selection": bp.get("selection"),
            })

        duplicate_variant_count = 0
        for (off, count, prim), rows in sorted(
            grouped.items(), key=lambda kv: min(x["part_index"] for x in kv[1])
        ):
            rows = sorted(rows, key=lambda x: x["part_index"])
            chosen = rows[0]
            duplicate_variant_count += max(0, len(rows) - 1)
            selected.append({
                "mesh_index": mi,
                "index_offset": off,
                "index_count": count,
                "primitive_type": prim,
                "material": chosen["material"],
                "part_indices": [chosen["part_index"]],
                "lod_values": [chosen["lod"]],
                "dye_indices": [chosen["gear_dye_change_color_index"]],
                "parts": [chosen],
                "group_index": chosen["group_index"],
                "visual_union_source_first_part": chosen["part_index"],
                "duplicate_render_variants": rows[1:],
                "all_candidate_part_indices": [x["part_index"] for x in rows],
                "all_candidate_group_indices": [x["group_index"] for x in rows],
                "all_candidate_materials": [x["material"] for x in rows],
                "all_candidate_lods": [x["lod"] for x in rows],
            })

        mesh_summaries.append({
            "mesh_index": mi,
            "part_count": len(mesh["parts"]),
            "stage_part_offsets": offsets,
            "stage_bounds_unique_sorted": bounds,
            "stage_intervals": intervals,
            "highest_detail_part_count": len(highest_parts),
            "highest_detail_part_indices": highest_parts,
            "explicit_null_highest_part_indices": explicit_null_parts,
            "unique_highest_detail_range_count": len(grouped),
            "duplicate_highest_detail_render_variant_count": duplicate_variant_count,
            "selected_range_count": len(grouped),
        })
    return selected, mesh_summaries


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", type=Path, action="append", required=True)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--visual-plan", type=Path, required=True)
    ap.add_argument("--material-bindings", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    a = ap.parse_args()

    plan = json.loads(a.visual_plan.read_text(encoding="utf-8"))
    if plan.get("status") != PLAN_STATUS or plan.get("violations"):
        raise SystemExit(f"visual plan is not complete: {plan.get('status')!r}")
    pairs = exact_pairs(plan)
    bindings = binding_pairs(json.loads(a.material_bindings.read_text(encoding="utf-8")))
    missing = sorted(set(pairs) - set(bindings))
    extra = sorted(set(bindings) - set(pairs))
    if missing:
        raise SystemExit("missing exact pair bindings: " + repr(missing))

    corpus = v5.v3.base.Corpus([p.resolve() for p in a.snapshot], a.runtime.resolve())
    a.out_dir.mkdir(parents=True, exist_ok=True)
    work = a.out_dir / ".pair_work"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)

    # export_one performs geometry decoding and reads selected_ranges as a module
    # global at call time. Rebind it only inside this dedicated process so the
    # specialized articulated CLI/default remains unchanged in every other workflow.
    original_selector = articulated.selected_ranges
    articulated.selected_ranges = visual_union_ranges
    rows = []
    errors = []
    try:
        for model, parent in pairs:
            pair_id = f"{model}__{parent}"
            pair_work = work / pair_id
            try:
                rep = articulated.export_one(corpus, model, bindings[(model, parent)], pair_work)
                src_glb = pair_work / f"{model}.glb"
                src_json = pair_work / f"{model}.json"
                dst_glb = a.out_dir / f"{pair_id}.glb"
                dst_json = a.out_dir / f"{pair_id}.json"
                shutil.move(str(src_glb), str(dst_glb))
                legacy_count = rep.pop("stage0_selected_range_count", rep.get("geometry_count", 0))
                rep["schema_version"] = 3
                rep["status"] = "D1_WORLD_VISUAL_MODEL_PAIR_EXPORT_COMPLETE"
                rep["parent_resource"] = parent
                rep["pair_id"] = pair_id
                rep["visual_union_range_count"] = legacy_count
                rep["selection_mode"] = "CHARM_MOST_DETAILED_ALL_GROUPS_PORTABLE_VISUAL_UNION"
                rep["glb"] = str(dst_glb)
                rep["glb_bytes"] = dst_glb.stat().st_size
                rep["selection_policy"] = (
                    "Pinned Charm D1 EntityModel.Load(MostDetailed) highest LOD categories are considered across every "
                    "StagePartOffsets GroupIndex. Exact duplicate geometry ranges are emitted once using their first "
                    "source-ordered candidate for the portable Blender visual union; all later material/group variants "
                    "remain losslessly serialized in duplicate_render_variants. Owning EntityResource identity is part "
                    "of the export key. No model, parent, LOD category, material or geometry range is inferred."
                )
                dst_json.write_text(json.dumps(rep, indent=2) + "\n", encoding="utf-8")
                if src_json.exists():
                    src_json.unlink()
                rows.append(rep)
            except Exception as ex:
                errors.append({"model": model, "parent_resource": parent, "error": repr(ex)})
    finally:
        articulated.selected_ranges = original_selector

    if work.exists():
        shutil.rmtree(work)
    active = sorted({h for row in rows for h in row.get("active_materials", [])})
    out = {
        "schema_version": 2,
        "status": (
            "D1_WORLD_VISUAL_MODEL_PAIR_SET_COMPLETE"
            if not errors and len(rows) == len(pairs)
            else "D1_WORLD_VISUAL_MODEL_PAIR_SET_PARTIAL"
        ),
        "source_visual_plan": str(a.visual_plan),
        "source_material_bindings": str(a.material_bindings),
        "requested_pair_count": len(pairs),
        "exported_pair_count": len(rows),
        "unique_model_count": len({m for m, _p in pairs}),
        "unique_parent_resource_count": len({p for _m, p in pairs}),
        "geometry_count": sum(int(r.get("geometry_count", 0)) for r in rows),
        "triangle_count": sum(int(r.get("triangle_count", 0)) for r in rows),
        "active_material_count": len(active),
        "active_materials": active,
        "duplicate_render_variant_count": sum(
            len(rng.get("duplicate_render_variants", []))
            for row in rows for rng in row.get("ranges", [])
        ),
        "pairs": rows,
        "unplaced_extra_binding_pairs": [list(x) for x in extra],
        "errors": errors,
        "policy": (
            "Only exact model-parent pairs from the completed visual entity plan are exported. The portable visual set "
            "uses the source-complete Charm-highest-detail union across every GroupIndex, while duplicate render variants "
            "of an identical geometry range are preserved in reports instead of drawn simultaneously. Pair identity "
            "prevents external material maps from being cross-wired when models are reused."
        ),
    }
    a.summary.parent.mkdir(parents=True, exist_ok=True)
    a.summary.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in (
        "status","requested_pair_count","exported_pair_count","unique_model_count",
        "unique_parent_resource_count","geometry_count","triangle_count","active_material_count",
        "duplicate_render_variant_count","errors"
    )}, indent=2))
    return 0 if out["status"] == "D1_WORLD_VISUAL_MODEL_PAIR_SET_COMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
