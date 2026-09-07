#!/usr/bin/env python3
"""Run the D1 spawned-actor animation engine with source-closed retail adapters.

v3 deliberately wraps the historical v2 engine instead of editing it in place. It
adds three independently proven semantics:

1. 80802C0E selectors may use the retail final-clip + implicit-null-tail form closed
   by the Wrath 45-control / 2,297-selector census.
2. The pinned Tiger parser's NumPy codec offsets are promoted to Python integers
   before slice arithmetic, preventing int16 host overflow on valid large codec-1
   uncompressed spans.
3. An exact control with zero states, zero bank clips and zero selected clips is a
   source-closed empty option set. No retarget executions are required for it.

No non-empty failure, ownership mismatch, rig mismatch or unknown selector form is
suppressed. The v2 JSON is normalized only after the wrapped engine has written it.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))


def _early_args():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--parser-root", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    return ap.parse_known_args()[0]


def _is_exact_empty_target(t: dict) -> bool:
    return (
        int(t.get("selector_state_count", -1)) == 0
        and int(t.get("animation_list_count", -1)) == 0
        and int(t.get("selector_selected_unique_clip_count", -1)) == 0
        and int(t.get("retarget_failure_count", -1)) == 0
        and int(t.get("retarget_success_count", -1)) == 0
        and not t.get("clips")
    )


def _target_key(t: dict) -> tuple[str, str, str]:
    return (
        str(t.get("skeleton", "")).upper(),
        str(t.get("runtime_rig", "")).upper(),
        str(t.get("control", "")).upper(),
    )


def _normalize(output: Path) -> dict:
    d = json.loads(output.read_text(encoding="utf-8"))
    if d.get("schema") != "d1_remote_spawned_actor_animation_options/v2":
        raise ValueError(f"unexpected wrapped schema {d.get('schema')!r}")

    source_status = d.get("status")
    empty_keys: set[tuple[str, str, str]] = set()
    for t in d.get("targets", []):
        if _is_exact_empty_target(t):
            t["all_selector_selected_clips_retarget_success"] = True
            t["source_closed_empty_control"] = True
            empty_keys.add(_target_key(t))

    for row in d.get("entities", []):
        target_rows = row.get("target_validations", []) or []
        empty_controls = set()
        for t in target_rows:
            key = _target_key(t)
            if key in empty_keys:
                t["all_selector_selected_clips_retarget_success"] = True
                t["source_closed_empty_control"] = True
                empty_controls.add(key[2])

        if empty_controls:
            expected = {
                f"{control}: selector-selected native retarget failures 0/0"
                for control in empty_controls
            }
            row["violations"] = [
                v for v in row.get("violations", []) if str(v) not in expected
            ]
            row["source_closed_empty_controls"] = sorted(empty_controls)

        row["all_selector_selected_clips_retarget_success"] = (
            bool(target_rows)
            and all(
                bool(t.get("all_selector_selected_clips_retarget_success"))
                for t in target_rows
            )
        )
        controls = row.get("control_hashes", []) or []
        if (
            not row.get("violations")
            and not row.get("frontiers")
            and controls
            and row["all_selector_selected_clips_retarget_success"]
        ):
            row["status"] = "source_closed"
        elif not row.get("violations"):
            row["status"] = "preserved_with_frontier"
        else:
            row["status"] = "violation"

    violations = []
    frontiers = []
    for row in d.get("entities", []):
        entity = row.get("entity")
        violations.extend(
            {"entity": entity, "error": str(x)} for x in row.get("violations", [])
        )
        frontiers.extend(
            {"entity": entity, "frontier": str(x)} for x in row.get("frontiers", [])
        )

    statuses = [x.get("status") for x in d.get("entities", [])]
    d["source_closed_entity_count"] = statuses.count("source_closed")
    d["preserved_with_frontier_entity_count"] = statuses.count(
        "preserved_with_frontier"
    )
    d["violation_entity_count"] = statuses.count("violation")
    d["violations"] = violations
    d["violation_count"] = len(violations)
    d["frontiers"] = frontiers
    d["frontier_count"] = len(frontiers)
    d["closed_target_count"] = sum(
        bool(t.get("all_selector_selected_clips_retarget_success"))
        for t in d.get("targets", [])
    )
    d["exact_empty_control_target_count"] = len(empty_keys)

    implicit_null_count = 0
    implicit_null_controls = set()
    for control, ci in (d.get("controls") or {}).items():
        for st in (ci.get("state_table") or {}).get("records", []):
            if st.get("selection_kind") == "range_with_implicit_null_tail":
                implicit_null_count += int(st.get("implicit_null_count", 1))
                implicit_null_controls.add(str(control).upper())
    d["implicit_null_selector_count"] = implicit_null_count
    d["implicit_null_selector_controls"] = sorted(implicit_null_controls)

    d["source_v2_status"] = source_status
    d["schema"] = "d1_remote_spawned_actor_animation_options/v3"
    clean = (
        d.get("entity_count") == d.get("source_closed_entity_count")
        and d.get("violation_count") == 0
        and d.get("frontier_count") == 0
        and d.get("retarget_pair_failure_count") == 0
        and d.get("closed_target_count") == d.get("target_count")
    )
    d["status"] = (
        "D1_ACTIVITY_ACTOR_ANIMATION_OPTIONS_COMPLETE"
        if clean
        else "D1_ACTIVITY_ACTOR_ANIMATION_OPTIONS_PARTIAL"
    )
    d["v3_policy"] = (
        "v3 preserves v2 ownership and native retarget requirements. Selector "
        "one-past ranges are accepted only for the source-proven final-clip plus "
        "serialized-zero implicit-null form. The null is never promoted to a clip. "
        "Tiger Tag_Array_NP offsets are converted to Python int before slice "
        "arithmetic to prevent host int16 overflow; codec equations and bytes are "
        "unchanged. Exact 0-state/0-bank/0-selected controls are source-closed empty "
        "option sets. No non-empty failure is normalized away."
    )
    output.write_text(json.dumps(d, indent=2) + "\n", encoding="utf-8")
    return d


def main() -> int:
    a = _early_args()
    parser_root = a.parser_root.resolve()
    sys.path.insert(0, str(parser_root))

    from d1_tiger_animation_safe_offsets import install_safe_tag_array_offsets

    install_safe_tag_array_offsets()

    # Patch the module attribute before importing the historical engine because v2
    # imports decode_control by value from this module.
    import d1_animation_control_state_map as selector_module
    from d1_animation_control_state_map_v2 import decode_control as decode_control_v2

    selector_module.decode_control = decode_control_v2

    import d1_remote_spawned_actor_animation_options_v2 as engine

    try:
        rc = engine.main()
    except SystemExit as ex:
        rc = int(ex.code or 0)
    if rc not in (0, 2):
        return int(rc)
    if not a.output.exists():
        raise FileNotFoundError(a.output)

    d = _normalize(a.output)
    print(
        "STATUS", d["status"],
        "ENTITIES", d.get("entity_count"),
        "SOURCE_CLOSED", d.get("source_closed_entity_count"),
        "CONTROLS", d.get("unique_control_count"),
        "IMPLICIT_NULL_SELECTORS", d.get("implicit_null_selector_count"),
        "EMPTY_TARGETS", d.get("exact_empty_control_target_count"),
        "RETARGET_PAIRS", d.get("retarget_pair_execution_count"),
        "RETARGET_FAILURES", d.get("retarget_pair_failure_count"),
        "VIOLATIONS", d.get("violation_count"),
        "FRONTIERS", d.get("frontier_count"),
    )
    return 0 if d["status"] == "D1_ACTIVITY_ACTOR_ANIMATION_OPTIONS_COMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
