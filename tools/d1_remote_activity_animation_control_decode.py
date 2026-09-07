#!/usr/bin/env python3
"""Decode exact D1 activity actor animation controls and selector-selected clips.

Consumes ``d1_activity_actor_animation_control_plan/v1`` and reopens every exact
80802C0E control from the universal retail corpus. The validated D1 selector parser
preserves the complete animation-list bank and every state record, including the
retail 0x0000FFFF empty-selection sentinel.

Only FileHashes selected by decoded state records are promoted as runtime clip
options, and every such target must resolve exactly to class 808005A1. Animation-list
entries that are never selected remain audit-only bank members. This stage establishes
control -> state -> clip identity; it does not claim target-rig compatibility, choose a
default state, or infer names for unknown state hashes.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_animation_control_state_map import decode_control
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_split_tar_extract import SplitHttpTar

CONTROL_REF = "80802C0E"
CLIP_REF = "808005A1"
NULLS = {"00000000", "FFFFFFFF"}


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def exact(c: RemoteCorpus, h: str, expected_ref: str | None = None):
    h = norm(h)
    meta = c.entry_meta(h)
    payload, src = c.payload(h)
    if meta is None or payload is None:
        raise KeyError(f"{h}: exact payload unavailable")
    got = norm(meta.get("reference", "FFFFFFFF"))
    if expected_ref is not None and got != norm(expected_ref):
        raise ValueError(f"{h}: reference {got} != {norm(expected_ref)}")
    return meta, payload, str(src)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--control-plan", type=Path, required=True)
    ap.add_argument("--member-catalog", type=Path, action="append", required=True)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--part-count", type=int, default=10)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    plan = json.loads(a.control_plan.read_text(encoding="utf-8"))
    violations: list[str] = []
    if plan.get("schema") != "d1_activity_actor_animation_control_plan/v1":
        violations.append(f"unexpected_control_plan_schema:{plan.get('schema')!r}")
    if plan.get("status") != "D1_ACTIVITY_ACTOR_ANIMATION_CONTROL_PLAN_COMPLETE":
        violations.append("control_plan_not_complete")
    if plan.get("frontiers") or plan.get("violations"):
        violations.append("control_plan_contains_frontier_or_violation")

    catalogs = load_catalogs(a.member_catalog)
    base = a.base_url.rstrip("/")
    arc = SplitHttpTar(
        [f"{base}/packages.tar.{i:03d}" for i in range(1, a.part_count + 1)],
        retries=6,
        timeout=90,
    )
    c = RemoteCorpus(arc, catalogs, a.runtime)

    controls = {}
    state_hash_counts = Counter()
    state_name_counts = Counter()
    selected_clip_counts = Counter()
    bank_clip_counts = Counter()
    selected_clip_to_controls: dict[str, set[str]] = defaultdict(set)
    selected_edge_count = 0
    empty_selector_count = 0

    for i, control in enumerate(plan.get("control_hashes", []), 1):
        ch = norm(control)
        row = {"control": ch, "violations": []}
        try:
            meta, payload, src = exact(c, ch, CONTROL_REF)
            dec = decode_control(payload, None, [])
            row.update(
                {
                    "entry_index": int(meta["index"]),
                    "size": int(meta["file_size"]),
                    "source": src,
                    "animation_list": dec["animation_list"],
                    "state_table": dec["state_table"],
                    "evidence_policy": dec["evidence_policy"],
                }
            )
            bank = []
            for item in dec["animation_list"]["items"]:
                h = norm(item["tag_hash"])
                if h not in NULLS:
                    bank.append(h)
                    bank_clip_counts[h] += 1
            selected = set()
            for st in dec["state_table"]["records"]:
                sh = norm(st.get("state_hash", "FFFFFFFF"))
                if sh not in NULLS:
                    state_hash_counts[sh] += 1
                if st.get("state_name"):
                    state_name_counts[str(st["state_name"])] += 1
                if st.get("selection_kind") == "empty_sentinel":
                    empty_selector_count += 1
                for item in st.get("selected_animations", []):
                    h = norm(item["tag_hash"])
                    if h in NULLS:
                        row["violations"].append(
                            f"state_{sh}:selected_null_clip:{h}"
                        )
                        continue
                    cm = c.entry_meta(h)
                    got = None if cm is None else norm(cm.get("reference", "FFFFFFFF"))
                    if cm is None:
                        row["violations"].append(
                            f"state_{sh}:selected_clip_{h}_missing"
                        )
                    elif got != CLIP_REF:
                        row["violations"].append(
                            f"state_{sh}:selected_clip_{h}_class_{got}_not_{CLIP_REF}"
                        )
                    else:
                        selected.add(h)
                        selected_clip_counts[h] += 1
                        selected_clip_to_controls[h].add(ch)
                        selected_edge_count += 1
            row["animation_list_clip_hashes"] = sorted(set(bank))
            row["selector_selected_clip_hashes"] = sorted(selected)
            row["unused_animation_list_clip_hashes"] = sorted(set(bank) - selected)
            row["animation_list_count"] = len(dec["animation_list"]["items"])
            row["state_count"] = len(dec["state_table"]["records"])
            row["selector_selected_unique_clip_count"] = len(selected)
            row["unused_animation_list_clip_count"] = len(set(bank) - selected)
        except Exception as ex:
            row["violations"].append(repr(ex))
        if row["violations"]:
            violations.extend(f"{ch}:{x}" for x in row["violations"])
        controls[ch] = row
        print(
            "CONTROL", i, "/", len(plan.get("control_hashes", [])), ch,
            "STATES", row.get("state_count"),
            "BANK", row.get("animation_list_count"),
            "SELECTED", row.get("selector_selected_unique_clip_count"),
            "VIOL", len(row["violations"]),
            flush=True,
        )

    actor_rows = []
    for actor in plan.get("actors", []):
        entity = norm(actor.get("entity"))
        control = norm(actor.get("exact_control"))
        ci = controls.get(control)
        row = {
            "entity": entity,
            "control": control,
            "owner_pair_controls_agree": bool(actor.get("owner_pair_controls_agree")),
            "state_count": None if ci is None else ci.get("state_count"),
            "selector_selected_clip_hashes": [] if ci is None else ci.get("selector_selected_clip_hashes", []),
            "unused_animation_list_clip_hashes": [] if ci is None else ci.get("unused_animation_list_clip_hashes", []),
        }
        actor_rows.append(row)

    unique_selected = sorted(selected_clip_counts)
    unique_bank = sorted(bank_clip_counts)
    out = {
        "schema": "d1_remote_activity_animation_control_decode/v1",
        "status": (
            "D1_REMOTE_ACTIVITY_ANIMATION_CONTROL_DECODE_COMPLETE"
            if not violations
            else "D1_REMOTE_ACTIVITY_ANIMATION_CONTROL_DECODE_WITH_VIOLATIONS"
        ),
        "source_control_plan": str(a.control_plan),
        "actor_count": len(actor_rows),
        "control_count": len(controls),
        "unique_state_hash_count": len(state_hash_counts),
        "state_hash_reference_counts": dict(sorted(state_hash_counts.items())),
        "known_state_name_reference_counts": dict(sorted(state_name_counts.items())),
        "empty_selector_count": empty_selector_count,
        "selector_selected_edge_count": selected_edge_count,
        "unique_selector_selected_clip_count": len(unique_selected),
        "selector_selected_clip_hashes": unique_selected,
        "selector_selected_clip_reference_counts": dict(sorted(selected_clip_counts.items())),
        "unique_animation_list_bank_clip_count": len(unique_bank),
        "animation_list_bank_clip_hashes": unique_bank,
        "unused_bank_clip_count": len(set(unique_bank) - set(unique_selected)),
        "selected_clip_to_controls": {
            h: sorted(selected_clip_to_controls[h]) for h in unique_selected
        },
        "controls": controls,
        "actors": actor_rows,
        "violation_count": len(violations),
        "violations": violations,
        "policy": (
            "Control identities come only from the source-closed actor animation control plan. State tables and "
            "packed selection ranges are byte-decoded from exact 80802C0E payloads. Runtime clip options are only "
            "selector-selected FileHashes whose exact retail target class is 808005A1. Unselected animation-list "
            "members remain audit-only. This stage does not choose a default state or claim target-rig compatibility."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(
        "STATUS", out["status"],
        "ACTORS", out["actor_count"],
        "CONTROLS", out["control_count"],
        "STATES", out["unique_state_hash_count"],
        "SELECTED_EDGES", out["selector_selected_edge_count"],
        "SELECTED_CLIPS", out["unique_selector_selected_clip_count"],
        "BANK_CLIPS", out["unique_animation_list_bank_clip_count"],
        "UNUSED_BANK", out["unused_bank_clip_count"],
        "VIOLATIONS", out["violation_count"],
    )
    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
