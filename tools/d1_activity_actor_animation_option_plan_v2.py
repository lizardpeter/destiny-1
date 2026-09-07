#!/usr/bin/env python3
"""Normalize D1 activity actor animation options with v3-compatible evidence.

This additive adapter preserves ``d1_activity_actor_animation_option_plan.py`` as the
historical v1 normalizer. It accepts either historical animation-options/v2 or the
source-closed animation-options/v3 report, then delegates the actor/control/state
normalization to v1. Actor->control identity still comes from the independent fixed-
field control plan; v3 does not replace that ownership proof.

For v3 input the adapter additionally requires the v3 report itself to be complete
and violation/frontier free, and carries the explicit-null selector / exact-empty
control audit counts into the generic activity plan.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

V2_SCHEMA = "d1_remote_spawned_actor_animation_options/v2"
V3_SCHEMA = "d1_remote_spawned_actor_animation_options/v3"
V3_COMPLETE = "D1_ACTIVITY_ACTOR_ANIMATION_OPTIONS_COMPLETE"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--control-plan", type=Path, required=True)
    ap.add_argument("--animation-options", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    src = json.loads(a.animation_options.read_text(encoding="utf-8"))
    upstream_schema = src.get("schema")
    if upstream_schema not in {V2_SCHEMA, V3_SCHEMA}:
        raise SystemExit(f"unsupported animation-options schema {upstream_schema!r}")
    if upstream_schema == V3_SCHEMA:
        if src.get("status") != V3_COMPLETE:
            raise SystemExit(f"v3 animation options are not complete: {src.get('status')!r}")
        if src.get("violation_count") or src.get("frontier_count"):
            raise SystemExit("v3 animation options contain violations/frontiers")

    # v1 checks the historical schema string but otherwise consumes the same preserved
    # fields. Give it a temporary compatibility copy rather than weakening v1.
    compatibility = dict(src)
    compatibility["schema"] = V2_SCHEMA
    with tempfile.TemporaryDirectory() as td:
        compat_path = Path(td) / "animation_options_v2_compat.json"
        compat_path.write_text(json.dumps(compatibility) + "\n", encoding="utf-8")

        import d1_activity_actor_animation_option_plan as v1

        old_argv = sys.argv[:]
        try:
            sys.argv = [
                old_argv[0],
                "--control-plan", str(a.control_plan),
                "--animation-options", str(compat_path),
                "-o", str(a.output),
            ]
            try:
                rc = v1.main()
            except SystemExit as ex:
                rc = int(ex.code or 0)
        finally:
            sys.argv = old_argv

    if not a.output.exists():
        raise FileNotFoundError(a.output)
    out = json.loads(a.output.read_text(encoding="utf-8"))
    out["schema"] = "d1_activity_actor_animation_option_plan/v2"
    out["upstream_animation_options_schema"] = upstream_schema
    out["source_animation_options"] = str(a.animation_options)
    out["implicit_null_selector_count"] = int(src.get("implicit_null_selector_count", 0))
    out["implicit_null_selector_controls"] = list(src.get("implicit_null_selector_controls", []))
    out["exact_empty_control_target_count"] = int(src.get("exact_empty_control_target_count", 0))
    out["v2_policy"] = (
        "Actor->control ownership remains independently fixed-field proven. For "
        "animation-options/v3 input, selector implicit-null tails remain explicit "
        "audit metadata and never become clip hashes; exact empty controls remain "
        "valid empty option sets; every non-empty selected clip must already have "
        "passed native decode/control-limit/retarget/local conversion upstream."
    )
    a.output.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

    print(
        "STATUS", out.get("status"),
        "ACTORS", out.get("actor_count"),
        "SOURCE_CLOSED", out.get("source_closed_actor_count"),
        "CONTROLS", out.get("unique_control_count"),
        "SELECTED_CLIPS", out.get("unique_selector_selected_clip_count"),
        "IMPLICIT_NULL", out.get("implicit_null_selector_count"),
        "EMPTY_TARGETS", out.get("exact_empty_control_target_count"),
        "VIOLATIONS", out.get("violation_count"),
        "FRONTIERS", out.get("frontier_count"),
    )
    return int(rc)


if __name__ == "__main__":
    raise SystemExit(main())
