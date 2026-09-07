#!/usr/bin/env python3
"""Derive source-owned D1 animation-capable actor seeds from an activity closure.

This is the safe bridge between the generic activity dependency graph and the
already-validated spawned-actor animation options pipeline.

An SEntity is admitted only when its exact source-parsed Resource[] contains:
- exactly one entity_skeleton Resource;
- exactly one runtime-rig EntityResource pair 808008B2 -> 8080099B;
- exactly one owner Resource for 808020BF -> 808029D2;
- exactly one owner Resource for 80802B92 -> 808020BB.

Those owner-pair resources are the two calibrated D1 structures whose fixed fields
select 80802C0E animation controls in the downstream byte parser. This seed tool does
not read those control fields and does not promote any aligned/literal FileHash edge.
It only proves that an exact activity SEntity owns the required source structures.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

NULLS = {"00000000", "FFFFFFFF"}
RUNTIME_RIG_PAIR = ("808008B2", "8080099B")
OWNER_PAIRS = (
    ("808020BF", "808029D2"),
    ("80802B92", "808020BB"),
)


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def pair_of(resource_row: dict) -> tuple[str, str]:
    er = resource_row.get("entity_resource") or {}
    return (
        norm(er.get("unk10_class", "FFFFFFFF")),
        norm(er.get("unk18_class", "FFFFFFFF")),
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--entity-closure", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    src = json.loads(a.entity_closure.read_text(encoding="utf-8"))
    violations: list[str] = []
    if src.get("schema") != "d1_remote_entity_dependency_closure/v1":
        violations.append(f"unexpected_schema:{src.get('schema')!r}")
    if src.get("status") != "D1_ENTITY_DEPENDENCY_CLOSURE_COMPLETE":
        violations.append("entity_closure_not_complete")
    if src.get("violations"):
        violations.append("entity_closure_contains_violations")
    if src.get("truncated"):
        violations.append("entity_closure_truncated")

    candidates = []
    excluded = []
    signature_counts = Counter()
    exact_sentity_count = 0

    for node in src.get("nodes", []):
        if node.get("kind") != "s_entity":
            continue
        if not str(node.get("path_class", "")).startswith("TYPED_EXACT"):
            continue
        exact_sentity_count += 1
        entity = norm(node.get("tag_hash"))
        resources = [
            r for r in node.get("resources", [])
            if norm(r.get("resource_hash", "FFFFFFFF")) not in NULLS
            and r.get("resolution_status") == "resolved_exact"
        ]
        skeletons = [
            norm(r["resource_hash"])
            for r in resources
            if (r.get("entity_resource") or {}).get("semantic_role") == "entity_skeleton"
        ]
        rigs = [norm(r["resource_hash"]) for r in resources if pair_of(r) == RUNTIME_RIG_PAIR]
        owners = {
            pair: [norm(r["resource_hash"]) for r in resources if pair_of(r) == pair]
            for pair in OWNER_PAIRS
        }
        sig = (
            len(skeletons),
            len(rigs),
            len(owners[OWNER_PAIRS[0]]),
            len(owners[OWNER_PAIRS[1]]),
        )
        signature_counts[str(sig)] += 1

        reasons = []
        if len(skeletons) != 1:
            reasons.append(f"skeleton_count={len(skeletons)}")
        if len(rigs) != 1:
            reasons.append(f"runtime_rig_count={len(rigs)}")
        for pair in OWNER_PAIRS:
            if len(owners[pair]) != 1:
                reasons.append(f"owner_pair_{pair[0]}_{pair[1]}_count={len(owners[pair])}")

        evidence = {
            "entity": entity,
            "entity_depth": node.get("depth"),
            "entity_path_class": node.get("path_class"),
            "skeleton_resources": skeletons,
            "runtime_rig_resources": rigs,
            "animation_owner_resources": [
                {
                    "pair": list(pair),
                    "resource_hashes": owners[pair],
                }
                for pair in OWNER_PAIRS
            ],
            "articulated": bool(node.get("articulated")),
        }
        if reasons:
            evidence["exclusion_reasons"] = reasons
            excluded.append(evidence)
        else:
            evidence["status"] = "SOURCE_STRUCTURE_COMPLETE"
            candidates.append(evidence)

    entity_hashes = [x["entity"] for x in candidates]
    out = {
        "schema": "d1_activity_actor_animation_seed/v1",
        "status": "D1_ACTIVITY_ACTOR_ANIMATION_SEED_COMPLETE" if not violations else "D1_ACTIVITY_ACTOR_ANIMATION_SEED_WITH_VIOLATIONS",
        "source_entity_closure": str(a.entity_closure),
        "exact_sentity_count": exact_sentity_count,
        "animation_capable_entity_count": len(candidates),
        "excluded_exact_sentity_count": len(excluded),
        "resource_signature_counts": dict(signature_counts),
        "entity_hashes": entity_hashes,
        "candidates": candidates,
        "excluded": excluded,
        "violations": violations,
        "policy": (
            "Admission uses only exact source-parsed SEntity Resource[] ownership. The runtime-rig and two calibrated "
            "animation-owner class pairs must each occur exactly as required. No aligned FileHash occurrence, package "
            "adjacency, developer name, model similarity, or animation compatibility creates actor ownership. The "
            "downstream animation parser must independently reopen the owner resources and prove their fixed-offset "
            "80802C0E control edges before any clip is selected."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(
        "STATUS", out["status"],
        "EXACT_SENTITY", exact_sentity_count,
        "ANIMATION_CAPABLE", len(candidates),
        "EXCLUDED", len(excluded),
        "VIOLATIONS", len(violations),
    )
    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
