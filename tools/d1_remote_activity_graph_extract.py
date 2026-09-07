#!/usr/bin/env python3
"""Run the reusable source-exact D1 activity graph extraction pipeline.

Given one named SUnkActivity_ROI/80800616 activity root, this orchestrates the
existing independently validated tools:

  activity root
    -> exact Activity placements / S6E / F603 ownership
    -> activity-wide F603 EntityResource class census
    -> every S6E stage container
    -> many-to-many stage/resource matrix
    -> source-owned D912 scripted-entity census

The output is an activity graph manifest plus the full component reports. It is
intentionally independent of Crota, raids, strikes, patrols, or any other gameplay
category. Category labels are metadata; serialized ownership drives extraction.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NULLS = {"00000000", "FFFFFFFF"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd: list[str], stdout_path: Path | None = None) -> None:
    print("RUN", " ".join(cmd), flush=True)
    if stdout_path is None:
        cp = subprocess.run(cmd, check=False)
    else:
        stdout_path.parent.mkdir(parents=True, exist_ok=True)
        with stdout_path.open("w", encoding="utf-8") as f:
            cp = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, check=False, text=True)
    if cp.returncode != 0:
        tail = ""
        if stdout_path is not None and stdout_path.exists():
            lines = stdout_path.read_text(encoding="utf-8", errors="replace").splitlines()
            tail = "\n".join(lines[-30:])
        raise RuntimeError(
            f"command failed rc={cp.returncode}: {' '.join(cmd)}"
            + (f"\n--- output tail ---\n{tail}" if tail else "")
        )


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--activity-hash", required=True)
    ap.add_argument("--activity-name", required=True)
    ap.add_argument("--activity-class", default="80800616")
    ap.add_argument("--member-catalog", action="append", type=Path, required=True)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--part-count", type=int, default=10)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    a = ap.parse_args()

    ah = str(a.activity_hash).upper().removeprefix("0X").zfill(8)
    ac = str(a.activity_class).upper().removeprefix("0X").zfill(8)
    out = a.output_dir
    out.mkdir(parents=True, exist_ok=True)
    stages = out / "stages"
    stages.mkdir(parents=True, exist_ok=True)
    logs = out / "logs"
    logs.mkdir(parents=True, exist_ok=True)

    common = []
    for p in a.member_catalog:
        common += ["--member-catalog", str(p)]
    common += [
        "--base-url", a.base_url,
        "--part-count", str(a.part_count),
        "--runtime", str(a.runtime),
    ]

    placements_path = out / "activity_placements.json"
    run(
        [
            sys.executable,
            str(HERE / "d1_remote_activity_placements.py"),
            "--activity-hash", ah,
            "--activity-name", a.activity_name,
            "--activity-class", ac,
            *common,
            "-o", str(placements_path),
        ],
        logs / "placements.txt",
    )
    placements = load(placements_path)
    if placements.get("schema") != "d1_remote_activity_placements/v1" or placements.get("violations"):
        raise RuntimeError("activity placements did not close exactly")

    f603_path = out / "activity_f603_resources.json"
    run(
        [
            sys.executable,
            str(HERE / "d1_remote_activity_f603_resource_census.py"),
            "--placements", str(placements_path),
            *common,
            "-o", str(f603_path),
        ],
        logs / "f603.txt",
    )
    f603 = load(f603_path)
    if f603.get("schema") != "d1_remote_activity_f603_resource_census/v1" or f603.get("violations"):
        raise RuntimeError("activity F603 census did not close exactly")

    s6es = [
        str(x).upper().removeprefix("0X").zfill(8)
        for x in placements.get("unique_s6e_resources", [])
        if str(x).upper().removeprefix("0X").zfill(8) not in NULLS
    ]
    s6es = list(dict.fromkeys(s6es))
    for h in s6es:
        run(
            [
                sys.executable,
                str(HERE / "d1_remote_s6e_stage_probe.py"),
                "--s6e", h,
                *common,
                "-o", str(stages / f"{h}.json"),
            ],
            logs / f"stage_{h}.txt",
        )

    matrix_path = out / "activity_stage_resource_matrix.json"
    run(
        [
            sys.executable,
            str(HERE / "d1_activity_stage_resource_matrix.py"),
            "--placements", str(placements_path),
            "--f603-census", str(f603_path),
            "--stage-dir", str(stages),
            "--label", a.activity_name,
            "-o", str(matrix_path),
        ],
        logs / "matrix.txt",
    )
    matrix = load(matrix_path)
    if matrix.get("status") != "D1_ACTIVITY_STAGE_RESOURCE_MATRIX_EXACT":
        raise RuntimeError("activity stage matrix did not close exactly")

    scripted_path = out / "activity_scripted_entities.json"
    run(
        [
            sys.executable,
            str(HERE / "d1_remote_activity_scripted_entity_census.py"),
            "--activity-hash", ah,
            "--activity-name", a.activity_name,
            "--activity-class", ac,
            *common,
            "-o", str(scripted_path),
        ],
        logs / "scripted_entities.txt",
    )
    scripted = load(scripted_path)
    if scripted.get("violations"):
        raise RuntimeError("activity scripted-entity census did not close exactly")

    components = {
        "placements": placements_path.name,
        "f603_resources": f603_path.name,
        "stage_resource_matrix": matrix_path.name,
        "scripted_entities": scripted_path.name,
        "stage_dir": stages.name,
    }
    hashes = {
        key: sha256(out / value)
        for key, value in components.items()
        if key != "stage_dir"
    }
    stage_hashes = {
        p.name: sha256(p) for p in sorted(stages.glob("*.json"))
    }
    manifest = {
        "schema": "d1_remote_activity_graph_extract/v1",
        "status": "D1_REMOTE_ACTIVITY_GRAPH_EXACT",
        "activity": {
            "tag_hash": ah,
            "name": a.activity_name,
            "class_hash": ac,
        },
        "counts": {
            "runtime_placements": placements.get("runtime_placement_count"),
            "unique_root_entities": len(placements.get("unique_entity_hashes", [])),
            "unique_s6e_resources": len(s6es),
            "unique_f603_resources": matrix.get("unique_f603_count"),
            "f603_stage_occurrences": matrix.get("f603_occurrence_count"),
            "shared_f603_resources": matrix.get("shared_f603_count"),
            "stages": matrix.get("stage_count"),
            "scripted_owner_f603": scripted.get("scripted_owner_f603_count"),
            "scripted_tables": scripted.get("unique_scripted_table_count"),
            "scripted_records": scripted.get("scripted_record_count"),
            "scripted_locations": scripted.get("scripted_location_count"),
        },
        "entity_resource_role_counts": f603.get("role_counts"),
        "entity_resource_class_pair_counts": f603.get("class_pair_counts"),
        "components": components,
        "component_sha256": hashes,
        "stage_sha256": stage_hashes,
        "policy": (
            "This manifest is assembled only after every component extractor returns an "
            "exact/no-violation result. Activity classification does not alter parsing. "
            "Shared F603 resources remain many-to-many stage edges. Unknown EntityResource "
            "pairs remain unresolved rather than receiving activity-specific semantics."
        ),
    }
    manifest_path = out / "activity_graph_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("STATUS", manifest["status"], "ACTIVITY", ah, "COUNTS", manifest["counts"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
