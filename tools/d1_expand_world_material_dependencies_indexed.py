#!/usr/bin/env python3
"""Close D1 articulated-world material dependencies through the archive-wide index.

The exact owning-parent material resolver may emit selected external Material
FileHashes that are outside the already recovered SEntity/model corpus. This driver
reruns that resolver, derives package families only from those unresolved selected
Material TagHashes using the source-validated universal D1 FileHash decoder, recovers
the exact current families through ``d1_recover_indexed_package_families.py``, and
repeats until all bindings close.

No package adjacency, filename semantics, material resemblance, or historical map
material list participates in selection.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from d1_filehash import package_hex

NULLS = {"00000000", "FFFFFFFF"}
COMPLETE = "D1_WORLD_ENTITY_MODEL_MATERIAL_BINDINGS_COMPLETE"


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


def present_ids(roots: list[Path]) -> set[str]:
    return {x for x in (pkgid_from_name(p.name) for p in snapshots(roots)) if x}


def unresolved_selected_material_hashes(doc: dict) -> list[str]:
    out = set()
    for binding in doc.get("bindings", []):
        for mesh in binding.get("meshes", []):
            for part in mesh.get("parts", []):
                selected = part.get("selected_material") or {}
                h = norm(selected.get("hash", "FFFFFFFF"))
                if h in NULLS or selected.get("class_matches"):
                    continue
                out.add(h)
    return sorted(out)


def run_bindings(runtime: Path, plan: Path, roots: list[Path], out: Path, stdout: Path) -> tuple[int, dict]:
    cmd = [sys.executable, str(HERE / "d1_world_entity_model_material_bindings.py")]
    for p in snapshots(roots):
        cmd += ["--snapshot", str(p)]
    cmd += ["--runtime", str(runtime), "--articulated-plan", str(plan), "--out", str(out)]
    cp = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout.write_text(cp.stdout, encoding="utf-8")
    if not out.exists():
        raise RuntimeError(f"material resolver emitted no report rc={cp.returncode}; see {stdout}")
    if cp.returncode not in (0, 2):
        raise RuntimeError(f"material resolver failed rc={cp.returncode}; see {stdout}")
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
        raise RuntimeError(f"indexed material recovery failed rc={cp.returncode}; see {stdout}")
    d = json.loads(report.read_text(encoding="utf-8"))
    if d.get("status") != "D1_INDEXED_PACKAGE_FAMILY_RECOVERY_COMPLETE":
        raise RuntimeError(f"unexpected indexed recovery status {d.get('status')!r}")
    return d


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot-dir", type=Path, action="append", required=True)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--articulated-plan", type=Path, required=True)
    ap.add_argument("--index", type=Path, required=True)
    ap.add_argument("--package-list", type=Path, required=True)
    ap.add_argument("--expansion-dir", type=Path, required=True)
    ap.add_argument("--work-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--max-passes", type=int, default=10)
    a = ap.parse_args()

    a.expansion_dir.mkdir(parents=True, exist_ok=True)
    a.work_dir.mkdir(parents=True, exist_ok=True)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.report.parent.mkdir(parents=True, exist_ok=True)
    roots = [p.resolve() for p in a.snapshot_dir] + [a.expansion_dir.resolve()]
    initial_ids = sorted(present_ids(roots))
    recovered_ids: set[str] = set()
    passes = []
    final = None
    stop_reason = None

    for n in range(a.max_passes):
        out_path = a.work_dir / f"material_bindings_pass_{n:02d}.json"
        rc, doc = run_bindings(
            a.runtime.resolve(), a.articulated_plan.resolve(), roots,
            out_path, a.work_dir / f"material_bindings_pass_{n:02d}.stdout.txt"
        )
        final = doc
        unresolved = unresolved_selected_material_hashes(doc)
        unresolved_ids = sorted({package_hex(h).lower() for h in unresolved})
        present = present_ids(roots)
        new_ids = sorted(set(unresolved_ids) - present)
        row = {
            "pass": n,
            "resolver_returncode": rc,
            "status": doc.get("status"),
            "snapshot_count": len(snapshots(roots)),
            "present_package_ids": sorted(present),
            "model_parent_pair_count": doc.get("model_parent_pair_count"),
            "validated_pair_count": doc.get("validated_pair_count"),
            "unique_selected_material_count": doc.get("unique_selected_material_count"),
            "unresolved_selected_material_hash_count": len(unresolved),
            "unresolved_selected_material_hashes": unresolved,
            "unresolved_package_ids_universal": unresolved_ids,
            "new_package_ids": new_ids,
            "material_bindings": str(out_path),
        }
        passes.append(row)

        if doc.get("status") == COMPLETE:
            stop_reason = "closed_material_bindings_complete"
            break
        if not unresolved:
            stop_reason = "partial_without_unresolved_selected_material_hashes"
            break
        if not new_ids:
            stop_reason = "unresolved_materials_but_no_new_package_ids"
            break

        rec = recover(
            a.index.resolve(), a.package_list.resolve(), new_ids,
            a.expansion_dir.resolve(), a.work_dir / f"recovery_{n:02d}.json",
            a.work_dir / f"recovery_{n:02d}.stdout.txt"
        )
        row["recovery_status"] = rec.get("status")
        row["recovered_member_count"] = rec.get("member_count")
        row["recovered_package_ids"] = rec.get("requested_package_ids")
        recovered_ids.update(new_ids)
    else:
        stop_reason = "max_passes_reached"

    if final is None:
        raise RuntimeError("no material binding pass executed")

    a.out.write_text(json.dumps(final, indent=2) + "\n", encoding="utf-8")
    closed = final.get("status") == COMPLETE
    final_ids = sorted(present_ids(roots))
    report = {
        "schema_version": 1,
        "status": (
            "D1_INDEXED_WORLD_MATERIAL_DEPENDENCY_EXPANSION_CLOSED"
            if closed else "D1_INDEXED_WORLD_MATERIAL_DEPENDENCY_EXPANSION_PARTIAL"
        ),
        "stop_reason": stop_reason,
        "initial_package_ids": initial_ids,
        "initial_package_family_count": len(initial_ids),
        "final_package_ids": final_ids,
        "final_package_family_count": len(final_ids),
        "recovered_package_ids": sorted(recovered_ids),
        "recovered_package_family_count": len(recovered_ids),
        "passes": passes,
        "final_material_binding_status": final.get("status"),
        "final_violations": final.get("violations", []),
        "policy": (
            "Expansion is driven only by unresolved selected external Material FileHashes emitted by the exact owning-parent "
            "resolver. Package IDs are recomputed with the source-validated universal D1 FileHash decoder and recovered "
            "through the archive-wide package index. No split-TAR scan or destination-specific material family list is used."
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
        "final_material_binding_status": report["final_material_binding_status"],
        "unique_selected_material_count": final.get("unique_selected_material_count"),
        "final_violations": report["final_violations"],
    }, indent=2))
    return 0 if closed else 2


if __name__ == "__main__":
    raise SystemExit(main())
