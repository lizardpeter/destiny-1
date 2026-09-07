#!/usr/bin/env python3
"""Close exact D1 activity actor -> animation-control ownership from retained closure bytes.

Input is an exact entity dependency closure plus ``d1_activity_actor_animation_seed/v1``.
The seed has already proved that each admitted SEntity source-owns exactly one resource
of each calibrated animation owner class pair:

    808020BF -> 808029D2 : control FileHash at +0x110
    80802B92 -> 808020BB : control FileHash at +0x448

This tool requires the retained exact EntityResource node to contain one resolved
FileHash at that fixed byte offset and requires the target entry class to be 80802C0E.
The two independently owned resources are preserved separately. Agreement is reported
and, when they agree, the actor receives one exact control identity.

No package adjacency, general aligned-hash scanning, state-name heuristic, animation
compatibility, or model similarity participates. Only the calibrated fixed owner fields
are promoted from the retained payload evidence.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

CONTROL_REF = "80802C0E"
OWNER_EDGES = {
    ("808020BF", "808029D2"): 0x110,
    ("80802B92", "808020BB"): 0x448,
}


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--entity-closure", type=Path, required=True)
    ap.add_argument("--actor-seed", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    closure = json.loads(a.entity_closure.read_text(encoding="utf-8"))
    seed = json.loads(a.actor_seed.read_text(encoding="utf-8"))
    violations: list[str] = []
    frontiers: list[str] = []

    if closure.get("schema") != "d1_remote_entity_dependency_closure/v1":
        violations.append(f"unexpected_closure_schema:{closure.get('schema')!r}")
    if closure.get("status") != "D1_ENTITY_DEPENDENCY_CLOSURE_COMPLETE":
        violations.append("entity_closure_not_complete")
    if closure.get("violations"):
        violations.append("entity_closure_contains_violations")
    if closure.get("truncated"):
        violations.append("entity_closure_truncated")
    if seed.get("schema") != "d1_activity_actor_animation_seed/v1":
        violations.append(f"unexpected_seed_schema:{seed.get('schema')!r}")
    if seed.get("status") != "D1_ACTIVITY_ACTOR_ANIMATION_SEED_COMPLETE":
        violations.append("actor_seed_not_complete")
    if seed.get("violations"):
        violations.append("actor_seed_contains_violations")

    nodes = {norm(n.get("tag_hash")): n for n in closure.get("nodes", []) if n.get("tag_hash")}
    rows = []
    control_to_entities: dict[str, list[str]] = defaultdict(list)
    edge_count = 0

    for actor in seed.get("candidates", []):
        entity = norm(actor.get("entity"))
        row = {
            "entity": entity,
            "owner_edges": [],
            "control_hashes": [],
            "owner_pair_controls_agree": False,
            "violations": [],
            "frontiers": [],
        }
        pair_rows = actor.get("animation_owner_resources", [])
        pair_map = {
            tuple(norm(x) for x in r.get("pair", [])): [norm(x) for x in r.get("resource_hashes", [])]
            for r in pair_rows
        }
        observed = []
        for pair, expected_offset in OWNER_EDGES.items():
            rhs = pair_map.get(pair, [])
            if len(rhs) != 1:
                row["violations"].append(
                    f"owner_pair_{pair[0]}_{pair[1]}_resource_count={len(rhs)}"
                )
                continue
            resource_hash = rhs[0]
            node = nodes.get(resource_hash)
            edge = {
                "owner_resource": resource_hash,
                "owner_pair": list(pair),
                "fixed_control_offset": expected_offset,
                "fixed_control_offset_hex": f"0x{expected_offset:X}",
                "evidence_class": "TYPED_EXACT_FIXED_OFFSET_OWNER_EDGE",
            }
            if node is None:
                edge["violation"] = "owner_resource_not_retained_in_closure"
                row["violations"].append(f"{resource_hash}:owner_resource_not_retained_in_closure")
                row["owner_edges"].append(edge)
                continue
            if node.get("kind") != "entity_resource" or not str(node.get("path_class", "")).startswith("TYPED_EXACT"):
                edge["violation"] = "owner_resource_not_exact_entity_resource_path"
                row["violations"].append(f"{resource_hash}:owner_resource_not_exact_entity_resource_path")
                row["owner_edges"].append(edge)
                continue
            actual_pair = (norm(node.get("unk10_class")), norm(node.get("unk18_class")))
            edge["retained_owner_pair"] = list(actual_pair)
            if actual_pair != pair:
                edge["violation"] = f"retained_owner_pair_mismatch:{actual_pair}"
                row["violations"].append(f"{resource_hash}:retained_owner_pair_mismatch:{actual_pair}")
                row["owner_edges"].append(edge)
                continue

            fixed = [
                x for x in node.get("aligned_resolved_tags", [])
                if int(x.get("offset", -1)) == expected_offset
            ]
            edge["fixed_offset_candidate_count"] = len(fixed)
            if len(fixed) != 1:
                edge["violation"] = f"fixed_offset_candidate_count={len(fixed)}"
                row["violations"].append(
                    f"{resource_hash}:fixed_offset_0x{expected_offset:X}_candidate_count={len(fixed)}"
                )
                row["owner_edges"].append(edge)
                continue
            hit = fixed[0]
            control = norm(hit.get("tag_hash"))
            target_ref = norm((hit.get("entry") or {}).get("reference", "FFFFFFFF"))
            edge.update(
                {
                    "control": control,
                    "control_reference": target_ref,
                    "target_package_id": hit.get("package_id"),
                    "target_entry": hit.get("entry"),
                }
            )
            if target_ref != CONTROL_REF:
                edge["violation"] = f"fixed_owner_edge_target_class_{target_ref}_not_{CONTROL_REF}"
                row["violations"].append(
                    f"{resource_hash}:fixed_owner_edge_target_class_{target_ref}_not_{CONTROL_REF}"
                )
            else:
                observed.append(control)
                edge_count += 1
            row["owner_edges"].append(edge)

        row["control_hashes"] = sorted(set(observed))
        row["owner_pair_controls_agree"] = (
            len(row["owner_edges"]) == len(OWNER_EDGES)
            and len(observed) == len(OWNER_EDGES)
            and len(set(observed)) == 1
        )
        if not row["violations"] and not row["owner_pair_controls_agree"]:
            row["frontiers"].append(
                f"independent owner controls differ:{sorted(set(observed))}"
            )
        if row["owner_pair_controls_agree"]:
            row["exact_control"] = observed[0]
            control_to_entities[observed[0]].append(entity)
        row["status"] = (
            "SOURCE_CLOSED"
            if not row["violations"] and not row["frontiers"] and row["owner_pair_controls_agree"]
            else "PRESERVED_WITH_FRONTIER" if not row["violations"]
            else "VIOLATION"
        )
        violations.extend(f"{entity}:{x}" for x in row["violations"])
        frontiers.extend(f"{entity}:{x}" for x in row["frontiers"])
        rows.append(row)

    statuses = Counter(x["status"] for x in rows)
    controls = sorted(control_to_entities)
    out = {
        "schema": "d1_activity_actor_animation_control_plan/v1",
        "status": (
            "D1_ACTIVITY_ACTOR_ANIMATION_CONTROL_PLAN_COMPLETE"
            if not violations and not frontiers
            else "D1_ACTIVITY_ACTOR_ANIMATION_CONTROL_PLAN_PARTIAL"
        ),
        "source_entity_closure": str(a.entity_closure),
        "source_actor_seed": str(a.actor_seed),
        "actor_count": len(rows),
        "source_closed_actor_count": statuses["SOURCE_CLOSED"],
        "frontier_actor_count": statuses["PRESERVED_WITH_FRONTIER"],
        "violation_actor_count": statuses["VIOLATION"],
        "fixed_owner_edge_count": edge_count,
        "owner_agreement_count": sum(bool(x["owner_pair_controls_agree"]) for x in rows),
        "unique_control_count": len(controls),
        "control_hashes": controls,
        "control_to_entities": {h: sorted(control_to_entities[h]) for h in controls},
        "actors": rows,
        "frontier_count": len(frontiers),
        "frontiers": frontiers,
        "violation_count": len(violations),
        "violations": violations,
        "policy": (
            "Actor control ownership is promoted only through the two independently calibrated fixed-offset fields "
            "inside exact source-owned EntityResources of the required class pairs. Each target must resolve to class "
            "80802C0E. Generic aligned-hash occurrence is not ownership evidence. Agreement of the two owner resources "
            "is recorded independently; disagreement remains a frontier rather than being collapsed."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(
        "STATUS", out["status"],
        "ACTORS", out["actor_count"],
        "SOURCE_CLOSED", out["source_closed_actor_count"],
        "OWNER_EDGES", out["fixed_owner_edge_count"],
        "AGREE", out["owner_agreement_count"],
        "CONTROLS", out["unique_control_count"],
        "FRONTIERS", out["frontier_count"],
        "VIOLATIONS", out["violation_count"],
    )
    return 0 if out["status"] == "D1_ACTIVITY_ACTOR_ANIMATION_CONTROL_PLAN_COMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
