#!/usr/bin/env python3
"""Export every exact D1 visual world EntityModel/owning-parent pair.

Geometry decoding is delegated to the established articulated-model decoder, but
selection is deliberately different from the specialized articulated stage-0 path.
Pinned Charm EntityModel.Load(MostDetailed) considers highest-detail LOD categories
across the complete part array. GetPartsOfDetailLevel renumbers those selected parts
densely before GenerateParts uses StagePartOffsets to assign GroupIndex. For a
portable Blender-facing world preview we therefore build the same source-complete
highest-detail visual union already validated by the Crota-body adapter:

* inspect every source part and retain Charm highest-detail LODs {0,1,2,3,10};
* assign GroupIndex from the selected-part ordinal exactly as Charm does;
* resolve each Material through the exact owning EntityResource;
* group exact duplicate geometry ranges by (mesh,index_offset,index_count,primitive);
* emit the first source-ordered candidate once, while preserving every later render
  variant, material, group and source part index losslessly in the report.

StagePartOffsets is a fixed 30-short D1 field. Boundaries may extend beyond the count
of selected or serialized parts; Charm populates a dictionary across those intervals
and only queries the compact selected ordinals that actually exist. We preserve that
behavior rather than clamping or rejecting unused high boundaries.

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


def _group_map(offsets: list[int]) -> tuple[list[int], list[dict], dict[int, int]]:
    """Reproduce pinned Charm GenerateParts StagePartOffsets dictionary exactly.

    D1 StagePartOffsets is a fixed 30-short field. Charm sorts its unique values and
    writes partGroups[j]=group for every integer in each half-open interval, with no
    comparison to Parts.Count. GenerateParts later looks up only the dense selected
    ordinals produced by GetPartsOfDetailLevel.
    """
    bounds = sorted(set(int(x) for x in offsets))
    if len(bounds) < 2:
        raise ValueError("StagePartOffsets has fewer than two unique boundaries")
    intervals = []
    out: dict[int, int] = {}
    for gi in range(len(bounds) - 1):
        start, end = bounds[gi], bounds[gi + 1]
        if end < start:
            raise ValueError(f"non-monotonic StagePartOffsets interval [{start},{end})")
        intervals.append({"group_index": gi, "start": start, "end": end})
        for selected_ordinal in range(start, end):
            out[selected_ordinal] = gi
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
        if len(offsets) != 30:
            raise ValueError(f"mesh {mi}: D1 StagePartOffsets count {len(offsets)} != 30")
        bounds, intervals, group_for_selected = _group_map(offsets)

        grouped: dict[tuple[int, int, int], list[dict]] = defaultdict(list)
        explicit_null_parts = []
        highest_parts = []
        selected_ordinals = []
        selected_ordinal = 0
        for pi, p in enumerate(mesh["parts"]):
            lod = int(p["lod"])
            if lod not in HIGHEST_LODS:
                continue
            ordinal = selected_ordinal
            selected_ordinal += 1
            highest_parts.append(pi)
            selected_ordinals.append({'source_part_index': pi, 'selected_ordinal': ordinal})
            if ordinal not in group_for_selected:
                # This is the actual source-equivalent failure: Charm would throw a
                # KeyNotFoundException at partGroups[i] for this selected ordinal.
                raise ValueError(
                    f"mesh {mi} source part {pi}: selected ordinal {ordinal} has no StagePartOffsets GroupIndex"
                )
            group_index = group_for_selected[ordinal]
            bp = bparts.get(pi)
            if bp is None:
                raise ValueError(f"mesh {mi} part {pi}: missing exact material binding")
            sm = bp.get("selected_material") or {}
            mh = norm(sm.get("hash", "FFFFFFFF"))
            if mh in NULLS or bp.get("selection_status") == "EXPLICIT_NULL_MATERIAL":
                # Charm increments the dense selected ordinal before GenerateParts
                # rejects null material, so null parts still consume an ordinal.
                explicit_null_parts.append({'source_part_index': pi, 'selected_ordinal': ordinal, 'group_index': group_index})
                continue
            if not sm.get("class_matches"):
                raise ValueError(f"mesh {mi} part {pi}: selected non-null material unresolved {mh}")
            key = (int(p["index_offset"]), int(p["index_count"]), int(p["primitive_type"]))
            grouped[key].append({
                "part_index": pi,
                "selected_ordinal": ordinal,
                "group_index": group_index,
                "lod": lod,
                "material": mh,
                "gear_dye_change_color_index": int(p["gear_dye_change_color_index"]),
                "variant_shader_index": int(p["variant_shader_index"]),
                "flags_d1": int(p["flags_d1"]),
                "selection": bp.get("selection"),
            })

        duplicate_variant_count = 0
        for (off, count, prim), rows in sorted(
            grouped.items(), key=lambda kv: min(x["selected_ordinal"] for x in kv[1])
        ):
            rows = sorted(rows, key=lambda x: x["selected_ordinal"])
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
                "selected_ordinal": chosen["selected_ordinal"],
                "group_index": chosen["group_index"],
                "visual_union_source_first_part": chosen["part_index"],
                "duplicate_render_variants": rows[1:],
                "all_candidate_part_indices": [x["part_index"] for x in rows],
                "all_candidate_selected_ordinals": [x["selected_ordinal"] for x in rows],
                "all_candidate_group_indices": [x["group_index"] for x in rows],
                "all_candidate_materials": [x["material"] for x in rows],
                "all_candidate_lods": [x["lod"] for x in rows],
            })

        mesh_summaries.append({
            "mesh_index": mi,
            "serialized_part_count": len(mesh["parts"]),
            "stage_part_offsets": offsets,
            "stage_bounds_unique_sorted": bounds,
            "stage_intervals": intervals,
            "highest_detail_selected_count": selected_ordinal,
            "highest_detail_source_part_indices": highest_parts,
            "selected_ordinal_map": selected_ordinals,
            "explicit_null_highest_parts": explicit_null_parts,
            "unique_highest_detail_range_count": len(grouped),
            "duplicate_highest_detail_render_variant_count": duplicate_variant_count,
            "selected_range_count": len(grouped),
            "group_index_semantics": "Charm dense GetPartsOfDetailLevel selected ordinal -> GenerateParts partGroups[selected_ordinal]",
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
                rep["schema_version"] = 4
                rep["status"] = "D1_WORLD_VISUAL_MODEL_PAIR_EXPORT_COMPLETE"
                rep["parent_resource"] = parent
                rep["pair_id"] = pair_id
                rep["visual_union_range_count"] = legacy_count
                rep["selection_mode"] = "CHARM_MOST_DETAILED_DENSE_SELECTED_ORDINAL_GROUPS_PORTABLE_VISUAL_UNION"
                rep["glb"] = str(dst_glb)
                rep["glb_bytes"] = dst_glb.stat().st_size
                rep["selection_policy"] = (
                    "Pinned Charm D1 GetPartsOfDetailLevel(MostDetailed) selects LOD categories then densely renumbers "
                    "the selected parts. GenerateParts assigns GroupIndex by looking up that compact ordinal in the "
                    "dictionary generated from all fixed StagePartOffsets boundaries. Exact duplicate geometry ranges "
                    "are emitted once using their first selected-ordinal candidate for the portable Blender visual union; "
                    "all later material/group variants remain serialized in duplicate_render_variants. Owning "
                    "EntityResource identity is part of the export key."
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
        "schema_version": 3,
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
            "Only exact model-parent pairs from the completed visual entity plan are exported. Charm's D1 "
            "MostDetailed selected-part compaction and subsequent StagePartOffsets GroupIndex lookup are reproduced "
            "exactly. Duplicate render variants of an identical geometry range remain in evidence rather than being "
            "drawn simultaneously. Pair identity prevents external material maps from being cross-wired."
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
