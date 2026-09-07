#!/usr/bin/env python3
"""Classify every SF603 EntityResource reachable from one exact D1 activity.

Input is d1_remote_activity_placements/v1. For every serialized SF603/808003F6,
follow the source-pinned +0x0C EntityResource FileHash, parse that 80800861 with the
shared EntityResource parser, and preserve its exact ResourcePointer class pair.
Known roles such as normal SMap placement and scripted-entity-table ownership are
reported by the shared parser; unresolved pairs remain unresolved rather than being
named from activity-specific developer strings.

This is the activity-generic successor to d1_remote_raid_f603_scripted_owner_census.py.
"""
from __future__ import annotations

import argparse
import collections
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_entity_resource_probe import ENTITY_RESOURCE_CLASS, parse_resource
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus, norm
from d1_split_tar_extract import SplitHttpTar

F603 = "808003F6"
D912 = "808012D9"
NULLS = {"00000000", "FFFFFFFF"}


def u32(b: bytes, o: int) -> int:
    return struct.unpack_from("<I", b, o)[0]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--placements", type=Path, required=True)
    ap.add_argument("--member-catalog", type=Path, action="append", required=True)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--part-count", type=int, default=10)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    src = json.loads(a.placements.read_text(encoding="utf-8"))
    if src.get("schema") != "d1_remote_activity_placements/v1":
        raise SystemExit(f"unexpected placements schema {src.get('schema')!r}")
    if src.get("violations"):
        raise SystemExit(f"placements contain violations: {src['violations'][:10]}")
    f603s = [
        norm(x)
        for x in src.get("unique_f603_entity_resources", [])
        if norm(x) not in NULLS
    ]
    f603s = list(dict.fromkeys(f603s))

    catalogs = load_catalogs(a.member_catalog)
    base = a.base_url.rstrip("/")
    arc = SplitHttpTar(
        [f"{base}/packages.tar.{i:03d}" for i in range(1, a.part_count + 1)],
        retries=6,
        timeout=90,
    )
    c = RemoteCorpus(arc, catalogs, a.runtime)

    rows = []
    violations = []
    role_counts = collections.Counter()
    pair_counts = collections.Counter()
    table_counts = collections.Counter()

    for fh in f603s:
        row = {"f603": fh, "violations": []}
        fm = c.entry_meta(fh)
        row["f603_reference"] = None if fm is None else norm(fm.get("reference"))
        fb, fsrc = c.payload(fh)
        row["f603_payload_source"] = fsrc
        if fm is None or row["f603_reference"] != F603 or fb is None:
            row["violations"].append("f603_missing_or_wrong_class")
            rows.append(row)
            violations.extend(f"{fh}:{x}" for x in row["violations"])
            continue
        if len(fb) < 0x10:
            row["violations"].append("f603_shorter_than_0x10")
            rows.append(row)
            violations.extend(f"{fh}:{x}" for x in row["violations"])
            continue

        erh = f"{u32(fb, 0x0C):08X}"
        row["entity_resource_hash"] = erh
        em = c.entry_meta(erh)
        row["entity_resource_reference"] = (
            None if em is None else norm(em.get("reference"))
        )
        eb, esrc = c.payload(erh)
        row["entity_resource_payload_source"] = esrc
        if erh in NULLS:
            row["entity_resource_null"] = True
            role_counts["null"] += 1
            rows.append(row)
            continue
        if (
            em is None
            or row["entity_resource_reference"] != ENTITY_RESOURCE_CLASS
            or eb is None
        ):
            row["violations"].append("entity_resource_missing_or_wrong_class")
            rows.append(row)
            violations.extend(f"{fh}:{x}" for x in row["violations"])
            continue
        try:
            parsed = parse_resource(eb, "PS4")
        except Exception as ex:
            row["violations"].append(
                f"entity_resource_parse_error:{type(ex).__name__}:{ex}"
            )
            rows.append(row)
            violations.extend(f"{fh}:{x}" for x in row["violations"])
            continue

        role = parsed.get("semantic_role", "other_or_unknown")
        row["semantic_role"] = role
        row["unk10_class"] = (parsed.get("unk10") or {}).get("class_hash")
        row["unk18_class"] = (parsed.get("unk18") or {}).get("class_hash")
        role_counts[role] += 1
        pair_counts[(row["unk10_class"], row["unk18_class"])] += 1

        # Preserve parser-proven typed targets generically.
        for key in (
            "embedded_model_tag_hash",
            "entity_name_string_hash",
            "entity_name_tag_hash",
            "scripted_entity_table_tag_hash",
            "dialogue_entity_tag_hash",
        ):
            if parsed.get(key) is not None:
                row[key] = parsed.get(key)

        if role == "scripted_entity_table_owner":
            th = parsed.get("scripted_entity_table_tag_hash")
            row["scripted_entity_table_hash"] = th
            tm = None if not th else c.entry_meta(th)
            row["scripted_entity_table_reference"] = (
                None if tm is None else norm(tm.get("reference"))
            )
            row["scripted_entity_table_class_matches"] = bool(
                tm and row["scripted_entity_table_reference"] == D912
            )
            if not th or not row["scripted_entity_table_class_matches"]:
                row["violations"].append("scripted_table_missing_or_wrong_class")
            else:
                table_counts[th] += 1

        rows.append(row)
        violations.extend(f"{fh}:{x}" for x in row["violations"])

    report = {
        "schema": "d1_remote_activity_f603_resource_census/v1",
        "status": (
            "D1_REMOTE_ACTIVITY_F603_RESOURCE_CENSUS_EXACT"
            if not violations
            else "D1_REMOTE_ACTIVITY_F603_RESOURCE_CENSUS_PARTIAL"
        ),
        "activity": src.get("activity"),
        "input_f603_count": len(f603s),
        "role_counts": dict(role_counts),
        "class_pair_counts": {
            f"{x or 'NONE'}->{y or 'NONE'}": n
            for (x, y), n in sorted(pair_counts.items(), key=lambda z: str(z[0]))
        },
        "scripted_owner_count": sum(
            1 for r in rows if r.get("semantic_role") == "scripted_entity_table_owner"
        ),
        "scripted_table_hashes": sorted(table_counts),
        "scripted_table_owner_counts": dict(sorted(table_counts.items())),
        "rows": rows,
        "violations": violations,
        "policy": (
            "Every F603->EntityResource edge comes from source-pinned activity layout. "
            "EntityResource class pairs and parser-proven typed targets are retained exactly. "
            "Unknown class pairs remain unknown; no activity-specific name, proximity or "
            "appearance is promoted to semantic identity."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        "STATUS", report["status"],
        "ACTIVITY", (report.get("activity") or {}).get("tag_hash"),
        "F603", len(f603s),
        "ROLES", dict(role_counts),
        "PAIRS", len(pair_counts),
        "SCRIPTED_OWNERS", report["scripted_owner_count"],
        "VIOLATIONS", len(violations),
    )
    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
