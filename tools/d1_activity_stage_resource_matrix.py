#!/usr/bin/env python3
"""Build a loss-preserving D1 activity stage/resource matrix.

Inputs are outputs of existing source-validated extractors:
  * d1_remote_activity_placements/v1
  * d1_remote_raid_f603_scripted_owner_census/v1 (legacy name; this is an
    activity-wide F603/EntityResource classifier)
  * one or more d1_remote_s6e_stage_probe/v2 JSON files

A single F603 may be serialized in more than one S6E stage/container. This tool
therefore distinguishes unique resources from serialized stage occurrences and
preserves the resulting many-to-many graph. It never assigns semantic identity
from stage concentration or developer-name proximity.
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

NULLS = {"00000000", "FFFFFFFF"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--placements", type=Path, required=True)
    ap.add_argument("--f603-census", type=Path, required=True)
    ap.add_argument("--stage-dir", type=Path, required=True)
    ap.add_argument("--label")
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    placements = load(a.placements)
    f603 = load(a.f603_census)
    if placements.get("schema") != "d1_remote_activity_placements/v1":
        raise SystemExit(f"unexpected placements schema {placements.get('schema')!r}")
    if placements.get("violations"):
        raise SystemExit(f"placements has violations: {placements['violations'][:10]}")
    if f603.get("violations"):
        raise SystemExit(f"F603 census has violations: {f603['violations'][:10]}")

    fby = {r["f603"]: r for r in f603.get("rows", [])}
    expected = {
        x for x in placements.get("unique_f603_entity_resources", []) if x not in NULLS
    }
    if set(fby) != expected:
        missing = sorted(expected - set(fby))[:20]
        extra = sorted(set(fby) - expected)[:20]
        raise SystemExit(f"F603 census set mismatch missing={missing} extra={extra}")

    stage_paths = sorted(a.stage_dir.glob("*.json"))
    if not stage_paths:
        raise SystemExit(f"no stage JSON files under {a.stage_dir}")

    occurrences = []
    containers = []
    pair_occ = collections.defaultdict(list)
    pair_unique = collections.defaultdict(set)
    pair_devs = collections.defaultdict(set)
    resource_occ = collections.defaultdict(list)

    for path in stage_paths:
        p = load(path)
        if p.get("schema") != "d1_remote_s6e_stage_probe/v2":
            raise SystemExit(f"{path}: unexpected stage schema {p.get('schema')!r}")
        if p.get("violations"):
            raise SystemExit(f"{path}: stage probe violations: {p['violations'][:10]}")
        s6e = p["s6e"]
        stages = []
        for s in p.get("stages", []):
            pair_counts = collections.Counter()
            unique_pair_sets = collections.defaultdict(set)
            roles = collections.Counter()
            devs = []
            rows = []
            for x in s.get("f603s", []):
                fh = x["f603"]["hash"]
                if fh in NULLS:
                    continue
                if fh not in fby:
                    raise SystemExit(
                        f"{s6e} stage {s['stage_index']}: F603 {fh} absent from activity census"
                    )
                r = fby[fh]
                pair = (
                    f"{r.get('unk10_class') or 'NONE'}->"
                    f"{r.get('unk18_class') or 'NONE'}"
                )
                role = r.get("semantic_role", "unknown")
                cp = x.get("activity_collapse") or {}
                dev = (cp.get("dev_name") or {}).get("value")
                occ = {
                    "s6e": s6e,
                    "stage_index": s["stage_index"],
                    "f603": fh,
                    "entity_resource": r.get("entity_resource_hash"),
                    "pair": pair,
                    "semantic_role": role,
                    "dev_name": dev,
                    "scripted_entity_table": r.get("scripted_entity_table_hash"),
                }
                occurrences.append(occ)
                resource_occ[fh].append(occ)
                pair_occ[pair].append(occ)
                pair_unique[pair].add(fh)
                if dev:
                    devs.append(dev)
                    pair_devs[pair].add(dev)
                pair_counts[pair] += 1
                unique_pair_sets[pair].add(fh)
                roles[role] += 1
                rows.append(
                    {
                        k: occ[k]
                        for k in (
                            "f603",
                            "entity_resource",
                            "pair",
                            "semantic_role",
                            "dev_name",
                            "scripted_entity_table",
                        )
                    }
                )
            stages.append(
                {
                    "stage_index": s["stage_index"],
                    "map_data_table": s["map_data_table"]["hash"],
                    "f603_occurrence_count": len(rows),
                    "unique_f603_count": len({r["f603"] for r in rows}),
                    "pair_occurrence_counts": dict(pair_counts),
                    "pair_unique_counts": {
                        k: len(v) for k, v in sorted(unique_pair_sets.items())
                    },
                    "role_occurrence_counts": dict(roles),
                    "dev_names": devs,
                    "resources": rows,
                }
            )
        containers.append({"s6e": s6e, "stage_count": len(stages), "stages": stages})

    seen_unique = set(resource_occ)
    if seen_unique != expected:
        missing = sorted(expected - seen_unique)[:20]
        extra = sorted(seen_unique - expected)[:20]
        raise SystemExit(f"stage coverage mismatch missing={missing} extra={extra}")

    shared = []
    for fh, occs in sorted(resource_occ.items()):
        if len(occs) <= 1:
            continue
        shared.append(
            {
                "f603": fh,
                "occurrence_count": len(occs),
                "pair": occs[0]["pair"],
                "stage_locations": [
                    {"s6e": o["s6e"], "stage_index": o["stage_index"]} for o in occs
                ],
            }
        )

    pair_summary = []
    all_pairs = sorted(pair_unique, key=lambda p: (-len(pair_unique[p]), p))
    for pair in all_pairs:
        occs = pair_occ[pair]
        unique = pair_unique[pair]
        stage_keys = sorted({(o["s6e"], o["stage_index"]) for o in occs})
        pair_summary.append(
            {
                "pair": pair,
                "unique_f603_count": len(unique),
                "occurrence_count": len(occs),
                "shared_occurrence_excess": len(occs) - len(unique),
                "s6e_containers": sorted({o["s6e"] for o in occs}),
                "stage_keys": [
                    {"s6e": x, "stage_index": y} for x, y in stage_keys
                ],
                "stage_count": len(stage_keys),
                "dev_names": sorted(pair_devs[pair]),
                "f603_hashes": sorted(unique),
            }
        )

    report = {
        "schema": "d1_activity_stage_resource_matrix/v1",
        "status": "D1_ACTIVITY_STAGE_RESOURCE_MATRIX_EXACT",
        "label": a.label,
        "activity": placements.get("activity"),
        "s6e_container_count": len(containers),
        "stage_count": sum(x["stage_count"] for x in containers),
        "unique_f603_count": len(expected),
        "f603_occurrence_count": len(occurrences),
        "shared_f603_count": len(shared),
        "shared_occurrence_excess": len(occurrences) - len(expected),
        "containers": containers,
        "class_pair_summary": pair_summary,
        "shared_resources": shared,
        "policy": (
            "Every S6E/stage/F603 edge is source-layout-derived. A resource may be "
            "referenced by multiple stages; unique resource identity and serialized "
            "occurrences are therefore reported separately. EntityResource class pairs "
            "come from the exact activity-owned F603 census. Dev names are retained only "
            "when supplied by the source-validated Activity collapse path. Stage "
            "concentration is structural evidence, not identity."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        "STATUS",
        report["status"],
        "ACTIVITY",
        (report.get("activity") or {}).get("tag_hash"),
        "S6E",
        report["s6e_container_count"],
        "STAGES",
        report["stage_count"],
        "UNIQUE_F603",
        report["unique_f603_count"],
        "OCCURRENCES",
        report["f603_occurrence_count"],
        "SHARED",
        report["shared_f603_count"],
        "EXCESS",
        report["shared_occurrence_excess"],
    )
    for r in pair_summary:
        print(
            "PAIR",
            r["pair"],
            "UNIQUE",
            r["unique_f603_count"],
            "OCC",
            r["occurrence_count"],
            "STAGES",
            r["stage_count"],
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
