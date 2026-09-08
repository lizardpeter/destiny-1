#!/usr/bin/env python3
"""Close D1 world SEntity dependencies through the verified archive-wide package index.

This is the indexed counterpart to ``d1_expand_world_entity_dependencies.py``.
Each pass runs the source-pinned ``d1_world_entity_dependency_census.py`` over the
currently recovered corpus. Any unresolved dependency TagHash is converted to its
physical package family only with the source-validated universal D1 FileHash decoder.
Those exact families are recovered through ``d1_recover_indexed_package_families.py``
and the census repeats until no serialized dependency remains unresolved.

No package filename, activity name, visual resemblance, historical actor list, or
untyped byte scan creates a dependency. Package filenames are used only by the
index recovery primitive after a serialized FileHash has already selected a package
ID.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from d1_filehash import package_hex

NULLS = {"00000000", "FFFFFFFF"}
COMPLETE = "D1_WORLD_ENTITY_DEPENDENCY_CENSUS_COMPLETE"


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def pkgid_from_name(name: str) -> str | None:
    import re
    m = re.search(r"_([0-9A-Fa-f]{4})_[0-9]+\.pkg$", Path(name).name)
    return m.group(1).lower() if m else None


def snapshots(roots: list[Path]) -> list[Path]:
    by_name: dict[str, Path] = {}
    for root in roots:
        if not root.exists():
            continue
        for p in root.glob("*.pkg"):
            if p.is_file():
                by_name[p.name] = p.resolve()
    return [by_name[k] for k in sorted(by_name)]


def present_package_ids(roots: list[Path]) -> set[str]:
    return {x for x in (pkgid_from_name(p.name) for p in snapshots(roots)) if x}


def run_census(runtime: Path, placements: Path, roots: list[Path], out: Path, stdout: Path) -> tuple[int, dict]:
    cmd = [sys.executable, str(HERE / "d1_world_entity_dependency_census.py")]
    for p in snapshots(roots):
        cmd += ["--snapshot", str(p)]
    cmd += ["--runtime", str(runtime), "--placements", str(placements), "--out", str(out)]
    cp = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout.write_text(cp.stdout, encoding="utf-8")
    if not out.exists():
        raise RuntimeError(f"entity dependency census emitted no report rc={cp.returncode}; see {stdout}")
    if cp.returncode not in (0, 2):
        raise RuntimeError(f"entity dependency census failed rc={cp.returncode}; see {stdout}")
    return cp.returncode, json.loads(out.read_text(encoding="utf-8"))


def recover(index: Path, package_list: Path, ids: list[str], out_dir: Path, report: Path, stdout: Path) -> dict:
    cmd = [
        sys.executable,
        str(HERE / "d1_recover_indexed_package_families.py"),
        "--index", str(index),
        "--package-list", str(package_list),
    ]
    for pid in ids:
        cmd += ["--package-id", pid]
    cmd += ["--out-dir", str(out_dir), "--report", str(report)]
    cp = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout.write_text(cp.stdout, encoding="utf-8")
    if cp.returncode != 0:
        raise RuntimeError(f"indexed entity dependency recovery failed rc={cp.returncode}; see {stdout}")
    d = json.loads(report.read_text(encoding="utf-8"))
    if d.get("status") != "D1_INDEXED_PACKAGE_FAMILY_RECOVERY_COMPLETE":
        raise RuntimeError(f"unexpected indexed recovery status: {d.get('status')!r}")
    return d


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot-dir", type=Path, action="append", required=True)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--placements", type=Path, required=True)
    ap.add_argument("--index", type=Path, required=True)
    ap.add_argument("--package-list", type=Path, required=True)
    ap.add_argument("--expansion-dir", type=Path, required=True)
    ap.add_argument("--work-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--max-passes", type=int, default=12)
    a = ap.parse_args()

    a.expansion_dir.mkdir(parents=True, exist_ok=True)
    a.work_dir.mkdir(parents=True, exist_ok=True)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.report.parent.mkdir(parents=True, exist_ok=True)

    roots = [p.resolve() for p in a.snapshot_dir] + [a.expansion_dir.resolve()]
    initial_ids = sorted(present_package_ids(roots))
    recovered_ids: set[str] = set()
    passes: list[dict] = []
    final: dict | None = None
    stop_reason: str | None = None

    for n in range(a.max_passes):
        census_path = a.work_dir / f"entity_dependency_pass_{n:02d}.json"
        rc, dep = run_census(
            a.runtime.resolve(), a.placements.resolve(), roots,
            census_path, a.work_dir / f"entity_dependency_pass_{n:02d}.stdout.txt"
        )
        final = dep
        unresolved = sorted({
            norm(x) for x in dep.get("unresolved_dependency_hashes", [])
            if norm(x) not in NULLS
        })
        unresolved_ids = sorted({package_hex(h).lower() for h in unresolved})
        present = present_package_ids(roots)
        new_ids = sorted(set(unresolved_ids) - present)
        row = {
            "pass": n,
            "census_returncode": rc,
            "census_status": dep.get("status"),
            "snapshot_count": len(snapshots(roots)),
            "present_package_ids": sorted(present),
            "placed_unique_entity_count": dep.get("placed_unique_entity_count"),
            "parsed_entity_count": dep.get("parsed_entity_count"),
            "unique_entity_resource_hash_count": dep.get("unique_entity_resource_hash_count"),
            "unique_embedded_model_count": dep.get("unique_embedded_model_count"),
            "articulated_candidate_count": dep.get("articulated_candidate_count"),
            "unresolved_dependency_hash_count": len(unresolved),
            "unresolved_dependency_hashes": unresolved,
            "unresolved_package_ids_universal": unresolved_ids,
            "new_package_ids": new_ids,
            "census": str(census_path),
        }
        passes.append(row)

        if dep.get("status") == COMPLETE and not unresolved:
            stop_reason = "closed_zero_unresolved_entity_dependencies"
            break
        if not unresolved:
            stop_reason = "partial_census_without_unresolved_hashes"
            break
        if not new_ids:
            stop_reason = "unresolved_dependencies_but_no_new_package_ids"
            break

        rec_report = a.work_dir / f"recovery_{n:02d}.json"
        rec = recover(
            a.index.resolve(), a.package_list.resolve(), new_ids,
            a.expansion_dir.resolve(), rec_report,
            a.work_dir / f"recovery_{n:02d}.stdout.txt"
        )
        row["recovery_status"] = rec.get("status")
        row["recovered_member_count"] = rec.get("member_count")
        row["recovered_package_ids"] = rec.get("requested_package_ids")
        recovered_ids.update(new_ids)
    else:
        stop_reason = "max_passes_reached"

    if final is None:
        raise RuntimeError("no entity dependency census pass executed")

    a.out.write_text(json.dumps(final, indent=2) + "\n", encoding="utf-8")
    closed = final.get("status") == COMPLETE and not final.get("unresolved_dependency_hashes")
    final_ids = sorted(present_package_ids(roots))
    report = {
        "schema_version": 1,
        "status": (
            "D1_INDEXED_WORLD_ENTITY_DEPENDENCY_EXPANSION_CLOSED"
            if closed else "D1_INDEXED_WORLD_ENTITY_DEPENDENCY_EXPANSION_PARTIAL"
        ),
        "stop_reason": stop_reason,
        "initial_package_ids": initial_ids,
        "initial_package_family_count": len(initial_ids),
        "final_package_ids": final_ids,
        "final_package_family_count": len(final_ids),
        "recovered_package_ids": sorted(recovered_ids),
        "recovered_package_family_count": len(recovered_ids),
        "passes": passes,
        "final_dependency_status": final.get("status"),
        "final_unresolved_dependency_hashes": final.get("unresolved_dependency_hashes", []),
        "final_unresolved_dependency_package_ids_reported_by_legacy_census": final.get("unresolved_dependency_package_ids", {}),
        "final_unresolved_dependency_package_ids_universal": sorted({
            package_hex(norm(x)).lower()
            for x in final.get("unresolved_dependency_hashes", [])
            if norm(x) not in NULLS
        }),
        "policy": (
            "Expansion starts from source-owned SEntity placement hashes and follows only serialized dependencies emitted "
            "by d1_world_entity_dependency_census.py. Every unresolved dependency package ID is recomputed with the "
            "source-validated universal D1 FileHash decoder before indexed family recovery. The legacy census package-id "
            "summary is retained for diagnostics only and never controls recovery."
        ),
    }
    a.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "stop_reason": stop_reason,
        "passes": len(passes),
        "initial_package_family_count": len(initial_ids),
        "final_package_family_count": len(final_ids),
        "recovered_package_ids": report["recovered_package_ids"],
        "final_dependency_status": report["final_dependency_status"],
        "placed_unique_entity_count": final.get("placed_unique_entity_count"),
        "parsed_entity_count": final.get("parsed_entity_count"),
        "articulated_candidate_count": final.get("articulated_candidate_count"),
        "unique_embedded_model_count": final.get("unique_embedded_model_count"),
        "final_unresolved_dependency_package_ids_universal": report["final_unresolved_dependency_package_ids_universal"],
    }, indent=2))
    return 0 if closed else 2


if __name__ == "__main__":
    raise SystemExit(main())
