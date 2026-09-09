#!/usr/bin/env python3
"""Merge complementary exact D1 material-shader reference probes fail-closed.

Remote package recovery can fail transiently at the HTTP transport layer. This tool does
not relax any structural gate: it combines two or more probes of the same frozen 196-target
denominator, accepts recovered facts only when every overlapping observation is identical,
and requires every target/reference candidate to be source-closed by at least one input.
"""
from __future__ import annotations

import argparse
import collections
import copy
import hashlib
import json
from pathlib import Path

INPUT_SCHEMA = "d1_gcn_material_shader_reference_probe/v1"
SCHEMA = "d1_gcn_material_shader_reference_probe_merged/v1"
STATUS = "D1_GCN_MATERIAL_SHADER_REFERENCE_PROBE_MERGED_EXACT"
STATIC_KEYS = ("target", "occurrence_count", "material_reference_roles", "example_materials")
EXACT_TARGET_KEYS = ("target_entry", "target_payload", "target_orbshdr_shape")
EXACT_REFERENCE_KEYS = (
    "reference_target_entry",
    "reference_target_payload",
    "reference_target_orbshdr_shape",
)
TERMINAL_REFERENCE_KINDS = {
    "CURRENT_FILEHASH_TARGET_RESOLVED",
    "NULL_REFERENCE",
    "NO_CURRENT_PACKAGE_TARGET",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def one_exact(values: list[object], label: str, violations: list[str]) -> object | None:
    if not values:
        return None
    first = values[0]
    for other in values[1:]:
        if other != first:
            violations.append(f"conflicting_observations:{label}")
            return None
    return copy.deepcopy(first)


def classify_shape(row: dict) -> str:
    meta = row.get("target_entry") or {}
    target_orb = row.get("target_orbshdr_shape") or {}
    ref_orb = row.get("reference_target_orbshdr_shape") or {}
    typ = (meta.get("type"), meta.get("subtype"))
    if typ == (32, 8):
        if ref_orb.get("code_bounds_valid"):
            return "TYPE32_SUBTYPE8_REFERENCES_VALID_ORBSHDR"
        return "TYPE32_SUBTYPE8_WITHOUT_VALID_REFERENCED_ORBSHDR"
    if target_orb.get("code_bounds_valid"):
        return "NON_32_8_DIRECT_VALID_ORBSHDR"
    if ref_orb.get("code_bounds_valid"):
        return "NON_32_8_REFERENCES_VALID_ORBSHDR"
    return "NON_32_8_NO_VALID_ORBSHDR_PROVEN"


def build(paths: list[Path]) -> dict:
    if len(paths) < 2:
        raise ValueError("at least two complementary probe reports are required")
    probes = [json.loads(p.read_text()) for p in paths]
    violations: list[str] = []
    input_meta = []
    by_input: list[dict[str, dict]] = []

    for path, probe in zip(paths, probes):
        if probe.get("schema") != INPUT_SCHEMA:
            violations.append(f"input_schema:{path}:{probe.get('schema')}")
        cov = probe.get("coverage") or {}
        if cov.get("owner_violation_count") != 3987:
            violations.append(f"input_owner_denominator:{path}:{cov.get('owner_violation_count')}!=3987")
        if cov.get("shader_header_absent_occurrence_count") != 3987:
            violations.append(
                f"input_occurrence_denominator:{path}:{cov.get('shader_header_absent_occurrence_count')}!=3987"
            )
        if cov.get("unique_missing_reference_count") != 196:
            violations.append(f"input_target_denominator:{path}:{cov.get('unique_missing_reference_count')}!=196")
        rows = probe.get("targets") or []
        if len(rows) != 196:
            violations.append(f"input_target_rows:{path}:{len(rows)}!=196")
        idx = {str(r.get("target")): r for r in rows}
        if len(idx) != len(rows):
            violations.append(f"input_duplicate_targets:{path}:{len(rows)-len(idx)}")
        by_input.append(idx)
        input_meta.append(
            {
                "path": str(path),
                "sha256": sha256_file(path),
                "status": probe.get("status"),
                "input_violation_count": len(probe.get("violations") or []),
                "target_resolved_count": cov.get("target_resolved_count"),
                "reference_resolution_counts": cov.get("reference_resolution_counts") or {},
            }
        )

    target_sets = [set(x) for x in by_input]
    target_union = set().union(*target_sets)
    if any(s != target_sets[0] for s in target_sets[1:]):
        violations.append(
            "input_target_sets_differ:" + ":".join(str(len(s)) for s in target_sets)
        )
    if len(target_union) != 196:
        violations.append(f"merged_target_denominator:{len(target_union)}!=196")

    rows: list[dict] = []
    for target in sorted(target_union):
        observations = [idx[target] for idx in by_input if target in idx]
        row: dict = {}
        row_violations: list[str] = []
        for key in STATIC_KEYS:
            v = one_exact([o.get(key) for o in observations], f"{target}:{key}", row_violations)
            if v is not None:
                row[key] = v

        for key in EXACT_TARGET_KEYS:
            vals = [o.get(key) for o in observations if o.get(key) is not None]
            v = one_exact(vals, f"{target}:{key}", row_violations)
            if v is not None:
                row[key] = v
        if "target_entry" not in row or "target_payload" not in row:
            row_violations.append(f"{target}:target_not_recovered_by_any_input")

        for key in EXACT_REFERENCE_KEYS:
            vals = [o.get(key) for o in observations if o.get(key) is not None]
            v = one_exact(vals, f"{target}:{key}", row_violations)
            if v is not None:
                row[key] = v

        resolutions = [o.get("reference_resolution") for o in observations if o.get("reference_resolution")]
        terminal = [r for r in resolutions if r.get("kind") in TERMINAL_REFERENCE_KINDS]
        candidate = [r for r in resolutions if r.get("kind") == "CURRENT_FILEHASH_CANDIDATE"]
        chosen = one_exact(terminal, f"{target}:terminal_reference_resolution", row_violations)
        if chosen is None and not terminal:
            chosen = one_exact(candidate, f"{target}:candidate_reference_resolution", row_violations)
        if chosen is not None:
            row["reference_resolution"] = chosen
        if (row.get("reference_resolution") or {}).get("kind") == "CURRENT_FILEHASH_CANDIDATE":
            row_violations.append(f"{target}:reference_target_not_recovered_by_any_input")
        if (row.get("reference_resolution") or {}).get("kind") == "CURRENT_FILEHASH_TARGET_RESOLVED":
            if "reference_target_entry" not in row or "reference_target_payload" not in row:
                row_violations.append(f"{target}:resolved_reference_missing_exact_payload")

        if "target_entry" in row:
            row["structural_shape"] = classify_shape(row)
        row["source_probe_observations"] = [
            {
                "input_index": i,
                "target_recovered": o.get("target_entry") is not None,
                "reference_resolution_kind": (o.get("reference_resolution") or {}).get("kind"),
                "input_row_violations": list(o.get("violations") or []),
            }
            for i, o in enumerate(observations)
        ]
        row["violations"] = row_violations
        violations.extend(row_violations)
        rows.append(row)

    entry_class_counts = collections.Counter()
    reference_class_counts = collections.Counter()
    shape_counts = collections.Counter()
    reference_resolution_counts = collections.Counter()
    stage_slot_counts = collections.Counter()
    orb_stage_target_counts = collections.Counter()
    orb_stage_occurrence_counts = collections.Counter()
    local_wrapper_targets = 0
    local_wrapper_occurrences = 0

    for row in rows:
        meta = row.get("target_entry") or {}
        if "type" in meta and "subtype" in meta:
            entry_class_counts[f"{meta['type']}:{meta['subtype']}"] += 1
        rmeta = row.get("reference_target_entry") or {}
        if "type" in rmeta and "subtype" in rmeta:
            reference_class_counts[f"{rmeta['type']}:{rmeta['subtype']}"] += 1
        if row.get("structural_shape"):
            shape_counts[row["structural_shape"]] += 1
        kind = (row.get("reference_resolution") or {}).get("kind")
        if kind:
            reference_resolution_counts[kind] += 1
        for stage, count in (row.get("material_reference_roles") or {}).items():
            stage_slot_counts[stage] += int(count)
        bi = (row.get("reference_target_orbshdr_shape") or {}).get("binary_info") or {}
        orb_stage = bi.get("stage")
        if orb_stage:
            orb_stage_target_counts[orb_stage] += 1
            orb_stage_occurrence_counts[orb_stage] += int(row.get("occurrence_count", 0))
        if (
            meta.get("type") == 32
            and meta.get("subtype") == 11
            and rmeta.get("type") == 1
            and rmeta.get("subtype") == 11
            and bi.get("stage") == "LocalShader"
            and (row.get("reference_target_orbshdr_shape") or {}).get("code_bounds_valid") is True
        ):
            local_wrapper_targets += 1
            local_wrapper_occurrences += int(row.get("occurrence_count", 0))

    coverage = {
        "input_probe_count": len(paths),
        "owner_violation_count": 3987,
        "shader_header_absent_occurrence_count": sum(stage_slot_counts.values()),
        "unique_missing_reference_count": len(rows),
        "target_resolved_count": sum("target_entry" in r for r in rows),
        "target_payload_recovered_count": sum("target_payload" in r for r in rows),
        "target_entry_class_counts": dict(sorted(entry_class_counts.items())),
        "reference_target_entry_class_counts": dict(sorted(reference_class_counts.items())),
        "reference_resolution_counts": dict(sorted(reference_resolution_counts.items())),
        "structural_shape_counts": dict(sorted(shape_counts.items())),
        "serialized_stage_slot_occurrences": dict(sorted(stage_slot_counts.items())),
        "referenced_orb_stage_target_counts": dict(sorted(orb_stage_target_counts.items())),
        "referenced_orb_stage_occurrence_counts": dict(sorted(orb_stage_occurrence_counts.items())),
        "type32_subtype11_localshader_target_count": local_wrapper_targets,
        "type32_subtype11_localshader_occurrence_count": local_wrapper_occurrences,
        "shader_stage_promotions": 0,
        "shader_expression_semantic_promotions": 0,
    }
    if coverage["shader_header_absent_occurrence_count"] != 3987:
        violations.append(f"merged_occurrence_accounting:{coverage['shader_header_absent_occurrence_count']}!=3987")
    if coverage["target_resolved_count"] != 196:
        violations.append(f"merged_target_recovery:{coverage['target_resolved_count']}!=196")
    if coverage["target_payload_recovered_count"] != 196:
        violations.append(f"merged_payload_recovery:{coverage['target_payload_recovered_count']}!=196")

    return {
        "schema": SCHEMA,
        "status": STATUS if not violations else "D1_GCN_MATERIAL_SHADER_REFERENCE_PROBE_MERGED_WITH_VIOLATIONS",
        "source_probes": input_meta,
        "coverage": coverage,
        "targets": rows,
        "violations": violations,
        "semantic_boundary": {
            "material_slot_labels": "SERIALIZED_PROVENANCE_ONLY",
            "type32_subtype11_to_localshader": "STRUCTURAL_EXACT" if not violations else "NOT_PROMOTED",
            "localshader_as_vertexshader": "FORBIDDEN",
            "direct_raster_stage_ownership": "WITHHELD",
            "param_index_to_attr_index_provenance": "WITHHELD",
            "varying_semantic_names": "WITHHELD",
            "shader_expression_semantics": "WITHHELD",
        },
        "policy": (
            "Transport failures are not treated as missing data. A fact is admitted only if at least one "
            "probe recovered it exactly and every overlapping successful observation agrees. The merge "
            "does not convert material VS/PS slot labels into shader-stage semantics. A 32:11 wrapper is "
            "classified as LocalShader only when its exact 1:11 referenced payload parses as OrbShdr "
            "LocalShader with valid code bounds."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("probe", type=Path, nargs="+")
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()
    out = build(a.probe)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": out["status"], "coverage": out["coverage"], "violations": out["violations"][:50]}, indent=2, sort_keys=True))
    return 0 if not out["violations"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
