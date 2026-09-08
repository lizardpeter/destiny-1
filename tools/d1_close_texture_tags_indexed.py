#!/usr/bin/env python3
"""Recursively close arbitrary D1 Texture TagHashes through the archive index.

Unlike the material-driven world texture closer, this starts from an explicit set
of Texture TagHashes (for example STerrain mesh-group dyemaps). It derives only
serialized FileHash package IDs, recovers those exact package families from the
current global archive index, runs the exact texture exporter, and follows any
serialized unresolved backing FileHash edges until every texture decodes or the
closure stops making progress.

No filename, destination, material-slot or texture-role inference participates.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from d1_filehash import package_hex

HERE = Path(__file__).resolve().parent
NULLS = {"00000000", "FFFFFFFF"}


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def run(cmd: list[str], stdout_path: Path | None = None) -> int:
    if stdout_path is None:
        return subprocess.run(cmd, check=False).returncode
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    with stdout_path.open("w", encoding="utf-8") as f:
        return subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, text=True, check=False).returncode


def recover(index: Path, plist: Path, outdir: Path, ids: list[str], report: Path, stdout: Path) -> None:
    if not ids:
        return
    cmd = [
        sys.executable, str(HERE / "d1_recover_indexed_package_families.py"),
        "--index", str(index), "--package-list", str(plist),
        "--out-dir", str(outdir), "--report", str(report),
    ]
    for p in ids:
        cmd += ["--package-id", p]
    rc = run(cmd, stdout)
    if rc != 0:
        raise SystemExit(f"indexed package recovery failed rc={rc}; see {stdout}")


def export(snapshot_dirs: list[Path], runtime: Path, tags: list[str], outdir: Path, stdout: Path) -> tuple[int, dict]:
    files = sorted({p.resolve() for d in snapshot_dirs for p in d.glob("*.pkg") if p.is_file()})
    if not files:
        raise SystemExit("no package snapshots available")
    if outdir.exists():
        shutil.rmtree(outdir)
    cmd = [sys.executable, str(HERE / "d1_texture_tag_export.py")]
    for p in files:
        cmd += ["--snapshot", str(p)]
    cmd += ["--runtime", str(runtime)]
    for h in tags:
        cmd += ["--texture", h]
    cmd += ["--out", str(outdir)]
    rc = run(cmd, stdout)
    rp = outdir / "texture_tag_export.json"
    if not rp.exists():
        raise SystemExit(f"texture export emitted no report; rc={rc}; see {stdout}")
    return rc, json.loads(rp.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot-dir", type=Path, action="append", required=True)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--texture", action="append", default=[])
    ap.add_argument("--texture-list-json", type=Path)
    ap.add_argument("--texture-list-key", default="effective_selected_dyemaps")
    ap.add_argument("--index", type=Path, required=True)
    ap.add_argument("--package-list", type=Path, required=True)
    ap.add_argument("--expansion-dir", type=Path, required=True)
    ap.add_argument("--work-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--max-passes", type=int, default=6)
    a = ap.parse_args()

    tags = {norm(x) for x in a.texture if norm(x) not in NULLS}
    if a.texture_list_json:
        d = json.loads(a.texture_list_json.read_text(encoding="utf-8"))
        vals = d.get(a.texture_list_key)
        if not isinstance(vals, list):
            raise SystemExit(f"{a.texture_list_json}: key {a.texture_list_key!r} is not a list")
        tags.update(norm(x) for x in vals if norm(x) not in NULLS)
    tags = sorted(tags)
    if not tags:
        raise SystemExit("no direct texture tags supplied")

    a.expansion_dir.mkdir(parents=True, exist_ok=True)
    a.work_dir.mkdir(parents=True, exist_ok=True)
    source_dirs = [d.resolve() for d in a.snapshot_dir] + [a.expansion_dir.resolve()]
    initial_ids = sorted({package_hex(h).lower() for h in tags})
    recovered: list[str] = []
    known = {p.stem for p in a.expansion_dir.glob("*.pkg")}

    # Exact texture-header owner package families are source-derived from the tags.
    recover(a.index, a.package_list, a.expansion_dir, initial_ids,
            a.work_dir / "recovery_initial.json", a.work_dir / "recovery_initial.stdout.txt")
    recovered.extend(initial_ids)

    passes = []
    final = None
    stop_reason = None
    seen_missing_sets: set[tuple[str, ...]] = set()
    for n in range(1, a.max_passes + 1):
        pass_out = a.work_dir / f"export_{n:02d}"
        rc, doc = export(source_dirs, a.runtime, tags, pass_out, a.work_dir / f"export_{n:02d}.stdout.txt")
        failed = doc.get("failed_textures") or {}
        missing_ids = sorted({
            str(pid).lower()
            for row in failed.values()
            for pid in (row.get("missing_dependency_package_ids") or [])
            if pid
        })
        passes.append({
            "pass": n, "return_code": rc, "status": doc.get("status"),
            "resolved": doc.get("resolved"), "failed": doc.get("failed"),
            "missing_package_ids": missing_ids,
        })
        final = doc
        if doc.get("status") == "D1_TEXTURE_TAG_EXPORT_COMPLETE" and not failed:
            stop_reason = "closed_all_direct_texture_tags"
            # Preserve final exact exports at the requested stable path.
            if a.out.exists():
                shutil.rmtree(a.out)
            shutil.copytree(pass_out, a.out)
            break
        key = tuple(missing_ids)
        if not missing_ids:
            stop_reason = "failed_without_recoverable_serialized_dependency"
            break
        if key in seen_missing_sets:
            stop_reason = "repeated_missing_dependency_set"
            break
        seen_missing_sets.add(key)
        recover(a.index, a.package_list, a.expansion_dir, missing_ids,
                a.work_dir / f"recovery_{n:02d}.json", a.work_dir / f"recovery_{n:02d}.stdout.txt")
        recovered.extend(x for x in missing_ids if x not in recovered)

    complete = bool(final and final.get("status") == "D1_TEXTURE_TAG_EXPORT_COMPLETE" and int(final.get("failed", -1)) == 0)
    report = {
        "schema_version": 1,
        "status": "D1_INDEXED_DIRECT_TEXTURE_TAG_CLOSURE_COMPLETE" if complete else "D1_INDEXED_DIRECT_TEXTURE_TAG_CLOSURE_PARTIAL",
        "stop_reason": stop_reason,
        "requested_texture_count": len(tags),
        "requested_textures": tags,
        "initial_header_package_ids": initial_ids,
        "recovered_package_ids": recovered,
        "passes": passes,
        "final_export_status": None if final is None else final.get("status"),
        "final_resolved": None if final is None else final.get("resolved"),
        "final_failed": None if final is None else final.get("failed"),
        "final_failed_textures": None if final is None else final.get("failed_textures"),
        "policy": "Package recovery is driven only by the explicit Texture TagHashes and exact serialized unresolved backing FileHash edges emitted by d1_texture_tag_export.py. No filename, material slot, destination or texture-role inference is used."
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in (
        "status", "stop_reason", "requested_texture_count", "initial_header_package_ids",
        "recovered_package_ids", "passes", "final_export_status", "final_resolved", "final_failed"
    )}, indent=2))
    return 0 if complete else 2


if __name__ == "__main__":
    raise SystemExit(main())
