#!/usr/bin/env python3
"""Classify exact material shader references omitted from the frozen D1 shader corpus.

This is a diagnostic boundary, not a promotion step.  It consumes the fail-closed
material->shader owner report, extracts only ``shader_header_absent`` references,
then resolves those exact FileHashes through the frozen universal package-member
catalog.  Package entry metadata and payload shapes are reported verbatim.

The probe deliberately does not infer shader stage from the referring material.
OrbShdr parsing is used only as a structural payload-shape test.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import multiprocessing as mp
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_investment_arrangement_probe import filehash_pkg_index
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_split_tar_extract import SplitHttpTar
from d1_ps4_shader_binary_probe import find_footer, parse_binary_info, parse_usage

NULLS = {"00000000", "FFFFFFFF"}
_WORKER_CORPUS: RemoteCorpus | None = None
ABSENT_RE = re.compile(
    r"^shader_header_absent:([0-9A-Fa-f]{8}):(VS|PS):([0-9A-Fa-f]{8})$"
)


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def digest(payload: bytes | None) -> dict:
    return {
        "bytes": None if payload is None else len(payload),
        "sha256": None if payload is None else hashlib.sha256(payload).hexdigest(),
    }


def orbshdr_shape(payload: bytes | None) -> dict:
    out = {
        "footer_found": False,
        "binary_info_parsed": False,
        "usage_parsed": False,
        "code_bounds_valid": False,
    }
    if payload is None:
        return out
    try:
        footer, checks = find_footer(payload)
        out["locator_checks"] = checks
        out["footer"] = footer
        if footer is None:
            return out
        out["footer_found"] = True
        info = parse_binary_info(payload, footer)
        out["binary_info"] = info
        out["binary_info_parsed"] = True
        usage = parse_usage(payload, footer, info)
        out["usage"] = usage
        out["usage_parsed"] = True
        n = int(info["code_length_bytes"])
        out["code_length_bytes"] = n
        out["code_bounds_valid"] = 0 < n <= footer <= len(payload)
        if out["code_bounds_valid"]:
            out["code_sha256"] = hashlib.sha256(payload[:n]).hexdigest()
    except Exception as ex:
        out["parse_error"] = repr(ex)
    return out


def exact_entry(c: RemoteCorpus, tag: str) -> tuple[dict, bytes]:
    pkg, idx = filehash_pkg_index(int(tag, 16))
    v = c.view(pkg)
    if int(v.h["pkg_id"]) != pkg:
        raise RuntimeError(
            f"{tag}: logical package header {int(v.h['pkg_id']):04X} != FileHash package {pkg:04X}"
        )
    if idx >= len(v.entries):
        raise RuntimeError(f"{tag}: entry index {idx} outside {len(v.entries)}")
    e = v.entries[idx]
    if norm(e["tag_hash"]) != tag:
        raise RuntimeError(f"{tag}: logical entry mismatch {e['tag_hash']}")
    payload = v.entry(idx)
    if len(payload) != int(e["file_size"]):
        raise RuntimeError(
            f"{tag}: payload length {len(payload)} != declared {int(e['file_size'])}"
        )
    meta = {
        "package_id": f"{pkg:04X}",
        "entry_index": idx,
        "logical_view": v.view.name,
        "package_patch_id": int(v.view.patch_id),
        "reference": norm(e["reference"]),
        "type": int(e["type"]),
        "subtype": int(e["subtype"]),
        "file_size": int(e["file_size"]),
        "starting_block": int(e["starting_block"]),
        "starting_block_offset": int(e["starting_block_offset"]),
        "entry_b": int(e["entry_b"]),
    }
    return meta, payload



def _worker_init(catalog_paths: list[str], base_url: str, part_count: int, runtime: str) -> None:
    global _WORKER_CORPUS
    catalogs = load_catalogs([Path(x) for x in catalog_paths])
    base = base_url.rstrip("/")
    arc = SplitHttpTar(
        [f"{base}/packages.tar.{i:03d}" for i in range(1, part_count + 1)],
        retries=6,
        timeout=90,
    )
    _WORKER_CORPUS = RemoteCorpus(arc, catalogs, Path(runtime))


def _probe_target(job: tuple[str, dict]) -> dict:
    if _WORKER_CORPUS is None:
        raise RuntimeError("worker corpus is not initialized")
    c = _WORKER_CORPUS
    target, src = job
    row = {
        "target": target,
        "occurrence_count": src["occurrence_count"],
        "material_reference_roles": dict(sorted(src["material_reference_roles"].items())),
        "example_materials": src["example_materials"],
        "violations": [],
    }
    try:
        meta, payload = exact_entry(c, target)
        row["target_entry"] = meta
        row["target_payload"] = {
            **digest(payload),
            "prefix_hex_64": payload[:64].hex().upper(),
        }
        row["target_orbshdr_shape"] = orbshdr_shape(payload)

        ref = meta["reference"]
        if ref not in NULLS:
            try:
                rmeta, rpayload = exact_entry(c, ref)
                row["reference_target_entry"] = rmeta
                row["reference_target_payload"] = {
                    **digest(rpayload),
                    "prefix_hex_64": rpayload[:64].hex().upper(),
                }
                row["reference_target_orbshdr_shape"] = orbshdr_shape(rpayload)
            except Exception as ex:
                row["violations"].append("reference_target:" + repr(ex))

        target_orb = row.get("target_orbshdr_shape", {})
        ref_orb = row.get("reference_target_orbshdr_shape", {})
        if (meta["type"], meta["subtype"]) == (32, 8):
            if ref_orb.get("code_bounds_valid"):
                shape = "TYPE32_SUBTYPE8_REFERENCES_VALID_ORBSHDR"
            else:
                shape = "TYPE32_SUBTYPE8_WITHOUT_VALID_REFERENCED_ORBSHDR"
        elif target_orb.get("code_bounds_valid"):
            shape = "NON_32_8_DIRECT_VALID_ORBSHDR"
        elif ref_orb.get("code_bounds_valid"):
            shape = "NON_32_8_REFERENCES_VALID_ORBSHDR"
        else:
            shape = "NON_32_8_NO_VALID_ORBSHDR_PROVEN"
        row["structural_shape"] = shape
    except Exception as ex:
        row["violations"].append("target_entry:" + repr(ex))
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("owner_report", type=Path)
    ap.add_argument("--member-catalog", type=Path, action="append", required=True)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--part-count", type=int, default=10)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    owner = json.loads(a.owner_report.read_text())
    if owner.get("schema") != "d1_gcn_material_shader_owner_frontier/v1":
        raise RuntimeError(f"unexpected owner schema {owner.get('schema')!r}")

    references: dict[str, dict] = {}
    malformed_owner_violations = []
    non_absent_owner_violations = []
    absent_occurrences = 0
    for violation in owner.get("violations", []):
        m = ABSENT_RE.match(str(violation))
        if not m:
            non_absent_owner_violations.append(str(violation))
            continue
        material, stage, target = (norm(m.group(1)), m.group(2), norm(m.group(3)))
        absent_occurrences += 1
        rec = references.setdefault(
            target,
            {
                "target": target,
                "occurrence_count": 0,
                "material_reference_roles": collections.Counter(),
                "example_materials": [],
            },
        )
        rec["occurrence_count"] += 1
        rec["material_reference_roles"][stage] += 1
        if len(rec["example_materials"]) < 16:
            rec["example_materials"].append(
                {"material": material, "serialized_stage_slot": stage}
            )

    if non_absent_owner_violations:
        malformed_owner_violations.append(
            f"owner_report_contains_non_absent_violations:{len(non_absent_owner_violations)}"
        )

    jobs = [(target, references[target]) for target in sorted(references)]
    workers = max(1, int(a.workers))
    initargs = (
        [str(x) for x in a.member_catalog],
        a.base_url,
        a.part_count,
        str(a.runtime),
    )
    rows = []
    if workers == 1:
        _worker_init(*initargs)
        iterator = map(_probe_target, jobs)
        pool = None
    else:
        pool = mp.Pool(
            processes=workers,
            initializer=_worker_init,
            initargs=initargs,
        )
        iterator = pool.imap_unordered(_probe_target, jobs, chunksize=1)
    try:
        for n, row in enumerate(iterator, 1):
            rows.append(row)
            if n % 25 == 0 or n == len(jobs):
                print(f"PROBED {n}/{len(jobs)}", flush=True)
    finally:
        if pool is not None:
            pool.close()
            pool.join()

    rows.sort(key=lambda r: r["target"])
    hard_violations = list(malformed_owner_violations)
    entry_class_counts = collections.Counter()
    reference_entry_class_counts = collections.Counter()
    structural_shape_counts = collections.Counter()
    package_counts = collections.Counter()
    for row in rows:
        meta = row.get("target_entry")
        if meta:
            entry_class_counts[f"{meta['type']}:{meta['subtype']}"] += 1
            package_counts[meta["package_id"]] += 1
        rmeta = row.get("reference_target_entry")
        if rmeta:
            reference_entry_class_counts[f"{rmeta['type']}:{rmeta['subtype']}"] += 1
        shape = row.get("structural_shape")
        if shape:
            structural_shape_counts[shape] += 1
        if row["violations"]:
            hard_violations.extend(
                f"{row['target']}:{x}" for x in row["violations"]
            )

    coverage = {
        "owner_violation_count": len(owner.get("violations", [])),
        "shader_header_absent_occurrence_count": absent_occurrences,
        "unique_missing_reference_count": len(references),
        "target_resolved_count": sum("target_entry" in r for r in rows),
        "target_payload_recovered_count": sum(
            (r.get("target_payload") or {}).get("sha256") is not None for r in rows
        ),
        "target_entry_class_counts": dict(sorted(entry_class_counts.items())),
        "reference_target_entry_class_counts": dict(sorted(reference_entry_class_counts.items())),
        "structural_shape_counts": dict(sorted(structural_shape_counts.items())),
        "target_package_counts": dict(sorted(package_counts.items())),
        "serialized_stage_slot_occurrences": dict(
            sorted(
                collections.Counter(
                    stage
                    for r in rows
                    for stage, count in r["material_reference_roles"].items()
                    for _ in range(count)
                ).items()
            )
        ),
        "shader_stage_promotions": 0,
        "shader_expression_semantic_promotions": 0,
        "worker_count": workers,
    }

    out = {
        "schema": "d1_gcn_material_shader_reference_probe/v1",
        "status": (
            "D1_GCN_MATERIAL_SHADER_REFERENCE_PROBE_EXACT"
            if not hard_violations
            else "D1_GCN_MATERIAL_SHADER_REFERENCE_PROBE_WITH_VIOLATIONS"
        ),
        "coverage": coverage,
        "targets": rows,
        "non_absent_owner_violations": non_absent_owner_violations,
        "violations": hard_violations,
        "policy": (
            "This diagnostic classifies only exact nonzero material shader references rejected by the "
            "frozen shader-header denominator. Package type/subtype/reference and payload hashes are retail "
            "facts. VS/PS labels are retained only as serialized material-slot provenance and are never "
            "promoted into target shader stage. OrbShdr parsing is a structural payload-shape test only. "
            "No missing reference is admitted into the shader corpus by this probe."
        ),
        "next_gate": (
            "Change the shader-corpus admission rule or material owner resolver only after the exact "
            "target entry-class and payload/reference structure establishes a generic source-closed rule."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(
        "STATUS", out["status"],
        "OCCURRENCES", absent_occurrences,
        "UNIQUE_TARGETS", len(rows),
        "ENTRY_CLASSES", dict(entry_class_counts),
        "SHAPES", dict(structural_shape_counts),
        "VIOLATIONS", len(hard_violations),
    )
    return 0 if not hard_violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
