#!/usr/bin/env python3
"""Normalize source-closed D1 actor animation options into a generic activity plan.

Inputs:
- ``d1_activity_actor_animation_control_plan/v1``: exact actor -> 80802C0E ownership
  proven independently through the two calibrated fixed owner fields;
- ``d1_remote_spawned_actor_animation_options/v2``: decoded state tables and native
  D1 retarget validation against the exact actor skeleton/runtime rig.

The output contains only clips actually selected by decoded selector records. Unused
animation-list bank entries remain audit metadata and are never promoted to runtime
options. Every state survives; no idle/default/startup state is selected or invented.

This adapter also removes historical Tower-specific status naming from the reusable
activity pipeline without weakening any upstream evidence requirement.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

NULLS = {"00000000", "FFFFFFFF"}


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--control-plan", type=Path, required=True)
    ap.add_argument("--animation-options", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    controls = json.loads(a.control_plan.read_text(encoding="utf-8"))
    options = json.loads(a.animation_options.read_text(encoding="utf-8"))
    violations: list[str] = []
    frontiers: list[str] = []

    if controls.get("schema") != "d1_activity_actor_animation_control_plan/v1":
        violations.append(f"unexpected_control_plan_schema:{controls.get('schema')!r}")
    if controls.get("status") != "D1_ACTIVITY_ACTOR_ANIMATION_CONTROL_PLAN_COMPLETE":
        violations.append("control_plan_not_complete")
    if controls.get("violations") or controls.get("frontiers"):
        violations.append("control_plan_contains_frontier_or_violation")

    if options.get("schema") != "d1_remote_spawned_actor_animation_options/v2":
        violations.append(f"unexpected_animation_options_schema:{options.get('schema')!r}")

    control_actor = {
        norm(r.get("entity")): norm(r.get("exact_control"))
        for r in controls.get("actors", [])
        if r.get("entity") and r.get("exact_control")
    }
    option_actor = {
        norm(r.get("entity")): r
        for r in options.get("entities", [])
        if r.get("entity")
    }
    if set(control_actor) != set(option_actor):
        missing = sorted(set(control_actor) - set(option_actor))
        extra = sorted(set(option_actor) - set(control_actor))
        violations.append(f"actor_domain_mismatch:missing={missing}:extra={extra}")

    rows = []
    state_hash_counts = Counter()
    state_name_counts = Counter()
    selected_clip_counts = Counter()
    family_key_entities: dict[tuple[str, str, str], list[str]] = defaultdict(list)

    controls_by_hash = {norm(h): v for h, v in (options.get("controls") or {}).items()}
    targets = {
        (norm(x.get("skeleton")), norm(x.get("runtime_rig")), norm(x.get("control"))): x
        for x in options.get("targets", [])
    }

    for entity in sorted(control_actor):
        expected_control = control_actor[entity]
        src = option_actor.get(entity) or {}
        row = {
            "entity": entity,
            "control": expected_control,
            "skeleton_resources": [norm(x) for x in src.get("skeleton_resources", [])],
            "runtime_rig_resources": [norm(x) for x in src.get("runtime_rig_resources", [])],
            "states": [],
            "selected_clip_hashes": [],
            "unused_animation_list_clip_hashes": [
                norm(x) for x in src.get("unused_animation_list_clip_hashes", [])
            ],
            "violations": [],
            "frontiers": [],
        }
        observed_controls = sorted({norm(x) for x in src.get("control_hashes", [])})
        if observed_controls != [expected_control]:
            row["violations"].append(
                f"animation_options_control_mismatch:{observed_controls}!={[expected_control]}"
            )
        if src.get("status") == "violation" or src.get("violations"):
            row["violations"].append(
                f"upstream_animation_option_violation:{src.get('violations', [])}"
            )
        if src.get("frontiers"):
            row["frontiers"].extend(str(x) for x in src.get("frontiers", []))

        if len(row["skeleton_resources"]) != 1:
            row["frontiers"].append(
                f"expected_one_skeleton:{row['skeleton_resources']}"
            )
        if len(row["runtime_rig_resources"]) != 1:
            row["frontiers"].append(
                f"expected_one_runtime_rig:{row['runtime_rig_resources']}"
            )

        ci = controls_by_hash.get(expected_control)
        if ci is None:
            row["violations"].append("control_decode_missing")
        else:
            selected = set()
            for si, st in enumerate(ci.get("state_table", {}).get("records", [])):
                state_hash = norm(st.get("state_hash", st.get("state_string_hash", "FFFFFFFF")))
                chosen = [
                    norm(x.get("tag_hash"))
                    for x in st.get("selected_animations", [])
                    if x.get("tag_hash") and norm(x.get("tag_hash")) not in NULLS
                ]
                srow = {
                    "state_index": si,
                    "state_hash": state_hash,
                    "state_name": st.get("state_name"),
                    "selection_count": st.get("selection_count"),
                    "selection_start": st.get("selection_start"),
                    "packed_selection": st.get("packed_selection"),
                    "selected_clip_hashes": chosen,
                }
                row["states"].append(srow)
                if state_hash not in NULLS:
                    state_hash_counts[state_hash] += 1
                if st.get("state_name"):
                    state_name_counts[str(st["state_name"])] += 1
                for h in chosen:
                    selected.add(h)
                    selected_clip_counts[h] += 1
            row["selected_clip_hashes"] = sorted(selected)

        if len(row["skeleton_resources"]) == 1 and len(row["runtime_rig_resources"]) == 1:
            key = (
                row["skeleton_resources"][0],
                row["runtime_rig_resources"][0],
                expected_control,
            )
            target = targets.get(key)
            row["target_validation"] = target
            if target is None:
                row["violations"].append("native_retarget_target_validation_missing")
            elif not target.get("all_selector_selected_clips_retarget_success"):
                row["violations"].append(
                    f"native_retarget_failures:{target.get('retarget_failure_count')}"
                )
            else:
                family_key_entities[key].append(entity)

        row["status"] = (
            "SOURCE_CLOSED"
            if not row["violations"] and not row["frontiers"]
            else "PRESERVED_WITH_FRONTIER" if not row["violations"]
            else "VIOLATION"
        )
        violations.extend(f"{entity}:{x}" for x in row["violations"])
        frontiers.extend(f"{entity}:{x}" for x in row["frontiers"])
        rows.append(row)

    families = []
    for i, (key, entities) in enumerate(sorted(family_key_entities.items()), 1):
        sk, rig, control = key
        families.append(
            {
                "family_id": f"ACTIVITY_ANIM_FAMILY_{i:03d}",
                "skeleton": sk,
                "runtime_rig": rig,
                "control": control,
                "entity_count": len(entities),
                "entities": sorted(entities),
            }
        )

    statuses = Counter(x["status"] for x in rows)
    selected_unique = sorted(selected_clip_counts)
    bank_unique = sorted({
        norm(x)
        for r in options.get("entities", [])
        for x in r.get("animation_list_clip_hashes", [])
        if norm(x) not in NULLS
    })
    out = {
        "schema": "d1_activity_actor_animation_option_plan/v1",
        "status": (
            "D1_ACTIVITY_ACTOR_ANIMATION_OPTION_PLAN_COMPLETE"
            if not violations and not frontiers
            else "D1_ACTIVITY_ACTOR_ANIMATION_OPTION_PLAN_PARTIAL"
        ),
        "source_control_plan": str(a.control_plan),
        "source_animation_options": str(a.animation_options),
        "actor_count": len(rows),
        "source_closed_actor_count": statuses["SOURCE_CLOSED"],
        "frontier_actor_count": statuses["PRESERVED_WITH_FRONTIER"],
        "violation_actor_count": statuses["VIOLATION"],
        "family_count": len(families),
        "families": families,
        "unique_control_count": len(set(control_actor.values())),
        "unique_state_hash_count": len(state_hash_counts),
        "state_hash_reference_counts": dict(sorted(state_hash_counts.items())),
        "known_state_name_reference_counts": dict(sorted(state_name_counts.items())),
        "unique_selector_selected_clip_count": len(selected_unique),
        "selector_selected_clip_hashes": selected_unique,
        "selector_selected_clip_reference_counts": dict(sorted(selected_clip_counts.items())),
        "unique_animation_list_bank_clip_count": len(bank_unique),
        "animation_list_bank_clip_hashes": bank_unique,
        "unused_bank_clip_count": len(set(bank_unique) - set(selected_unique)),
        "native_retarget_pair_execution_count": int(options.get("retarget_pair_execution_count", 0)),
        "native_retarget_pair_success_count": int(options.get("retarget_pair_success_count", 0)),
        "native_retarget_pair_failure_count": int(options.get("retarget_pair_failure_count", 0)),
        "actors": rows,
        "frontier_count": len(frontiers),
        "frontiers": frontiers,
        "violation_count": len(violations),
        "violations": violations,
        "policy": (
            "Actor->control identity comes from the independent fixed-field control plan. Runtime animation options "
            "are only clips selected by decoded 80802C0E state records. Unselected animation-list bank clips remain "
            "audit data and are not promoted. Each selector-selected option must pass the pinned native D1 decode, "
            "control-limit, rig-retarget and local-space conversion against the actor's exact skeleton/runtime rig. "
            "No state is chosen as idle/default/startup and no unknown state hash is assigned a name."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(
        "STATUS", out["status"],
        "ACTORS", out["actor_count"],
        "SOURCE_CLOSED", out["source_closed_actor_count"],
        "FAMILIES", out["family_count"],
        "CONTROLS", out["unique_control_count"],
        "STATES", out["unique_state_hash_count"],
        "SELECTED_CLIPS", out["unique_selector_selected_clip_count"],
        "BANK_CLIPS", out["unique_animation_list_bank_clip_count"],
        "RETARGET_FAILURES", out["native_retarget_pair_failure_count"],
        "FRONTIERS", out["frontier_count"],
        "VIOLATIONS", out["violation_count"],
    )
    return 0 if out["status"] == "D1_ACTIVITY_ACTOR_ANIMATION_OPTION_PLAN_COMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
