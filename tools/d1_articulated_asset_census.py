#!/usr/bin/env python3
"""Asset-first wrapper for the D1 articulated-resource census.

The original discovery implementation lives in ``d1_character_family_census``.
That filename predates an important semantic correction: a package-local model +
skeleton + runtime rig + clips proves an *articulated asset*, not a gameplay
character/combatant. Small animated mechanisms, environmental machinery, props,
and other non-character objects can have exactly that structure.

This wrapper is now the canonical interface. It preserves the byte-level graph
census while deliberately downgrading semantic labels until a separate gameplay
ownership/entity edge proves character or combatant identity.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import d1_character_family_census as legacy

_CLASS_MAP = {
    "animated_articulated_entity_candidate": "animated_articulated_asset_candidate",
    "rigged_articulated_entity_candidate": "rigged_articulated_asset_candidate",
}
_LEGACY_SPECIAL_KIND = "observed_0767_combatant_component"
_CANONICAL_SPECIAL_KIND = "observed_0767_special_component"
_LEGACY_SPECIAL_FACT = "observed_0767_combatant_components"
_CANONICAL_SPECIAL_FACT = "observed_0767_special_components"


def _reframe_classification(row: dict) -> dict:
    out = dict(row)
    out["classification"] = _CLASS_MAP.get(out.get("classification"), out.get("classification"))
    counts = dict(out.get("evidence_counts", {}))
    if _LEGACY_SPECIAL_FACT in counts:
        counts[_CANONICAL_SPECIAL_FACT] = counts.pop(_LEGACY_SPECIAL_FACT)
    out["evidence_counts"] = counts
    # Keep the legacy semantic-proof field for downstream compatibility, but
    # make the stronger asset-first rule explicit in a new canonical field.
    out["character_or_combatant_semantic_proven"] = False
    out["gameplay_identity_proven"] = False
    return out


def _reframe_facts(facts: dict) -> dict:
    out = dict(facts)
    if _LEGACY_SPECIAL_FACT in out:
        out[_CANONICAL_SPECIAL_FACT] = out.pop(_LEGACY_SPECIAL_FACT)
    return out


def classify_component(facts: dict) -> dict:
    # Accept either the canonical or legacy spelling when used as a library.
    legacy_facts = dict(facts)
    if _CANONICAL_SPECIAL_FACT in legacy_facts and _LEGACY_SPECIAL_FACT not in legacy_facts:
        legacy_facts[_LEGACY_SPECIAL_FACT] = legacy_facts[_CANONICAL_SPECIAL_FACT]
    return _reframe_classification(legacy.classify_component(legacy_facts))


def connected_components(nodes: set[str], graph: dict[str, set[str]]) -> list[list[str]]:
    return legacy.connected_components(nodes, graph)


def analyze_family(pkg: Path, runtime: Path, *, include_all_components: bool = False) -> dict:
    report = legacy.analyze_family(pkg, runtime, include_all_components=include_all_components)
    report = dict(report)
    report["schema"] = "d1_articulated_asset_census/v1"

    roles = {}
    for tag, row in report.get("roles", {}).items():
        q = dict(row)
        if q.get("kind") == _LEGACY_SPECIAL_KIND:
            q["kind"] = _CANONICAL_SPECIAL_KIND
        roles[tag] = q
    report["roles"] = roles

    kind_counts = dict(report.get("kind_counts", {}))
    if _LEGACY_SPECIAL_KIND in kind_counts:
        kind_counts[_CANONICAL_SPECIAL_KIND] = kind_counts.pop(_LEGACY_SPECIAL_KIND)
    report["kind_counts"] = kind_counts

    for key in ("components", "candidates"):
        rows = []
        for item in report.get(key, []):
            q = dict(item)
            q["classification"] = _reframe_classification(q["classification"])
            q["facts"] = _reframe_facts(q.get("facts", {}))
            rows.append(q)
        report[key] = rows

    report["policy"] = (
        "This census proves articulated-resource structure only. Model + skeleton + runtime rig + animation "
        "is classified as an articulated ASSET candidate, not a character/combatant. Package names, race/architecture "
        "families, adjacency, bone counts, and animation presence do not establish gameplay identity. The legacy "
        "0767 class pair formerly nicknamed 'combatant' is exposed only as observed_0767_special_component until its "
        "actual semantic role is independently proven. Promotion to a character/combatant requires an exact gameplay/"
        "entity ownership edge or equivalent runtime evidence."
    )
    return report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pkg", type=Path, nargs="+")
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--include-all-components", action="store_true")
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args()

    reports = [
        analyze_family(p, args.runtime, include_all_components=args.include_all_components)
        for p in args.pkg
    ]
    out = {
        "schema": "d1_articulated_asset_census_set/v1",
        "family_count": len(reports),
        "candidate_count": sum(x["candidate_count"] for x in reports),
        "families": reports,
        "policy": (
            "Candidate means articulated asset only. No candidate is a character/combatant until separately proven."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "family_count": out["family_count"],
        "candidate_count": out["candidate_count"],
        "packages": [
            {"package": x["package"], "candidate_count": x["candidate_count"], "kind_counts": x["kind_counts"]}
            for x in reports
        ],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
