#!/usr/bin/env python3
"""Accept a D1 shader corpus plan only against an immutable metadata checkpoint.

This gate keeps the game-wide PS4 shader denominator separate from later native-byte,
disassembly, structural-IR, and semantic claims.  It validates the exact current
32:8 -> Reference -> 1:8 and 32:9 -> Reference -> 1:9 graph, fan-out, package-family
counts, and native-entry size bounds recorded in d1_ps4_shader_header_corpus_r1.json.
"""
from __future__ import annotations

import argparse
import collections
import json
import statistics
from pathlib import Path


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("plan", type=Path)
    ap.add_argument("evidence", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    p = json.loads(a.plan.read_text())
    e = json.loads(a.evidence.read_text())
    violations: list[str] = []
    if p.get("schema") != "d1_shader_corpus_plan/v1":
        violations.append(f"plan_schema:{p.get('schema')!r}")
    if p.get("status") != "D1_SHADER_CORPUS_PLAN_COMPLETE" or p.get("violations"):
        violations.append("plan_not_complete_and_violation_free")
    if e.get("schema") != "d1_ps4_shader_header_corpus_evidence/v1":
        violations.append(f"evidence_schema:{e.get('schema')!r}")
    if e.get("status") != "D1_PS4_SHADER_HEADER_CORPUS_EXACT":
        violations.append(f"evidence_status:{e.get('status')!r}")

    psha = str((p.get("source") or {}).get("packages_txt_sha256") or "").lower()
    esha = str((e.get("source") or {}).get("packages_txt_sha256") or "").lower()
    if psha != esha:
        violations.append(f"packages_txt_sha256:{psha}!={esha}")

    headers = p.get("headers") or []
    by_stage = collections.defaultdict(list)
    refs_by_stage = collections.defaultdict(collections.Counter)
    header_pkgs = collections.defaultdict(set)
    native_pkgs = collections.defaultdict(set)
    native_sizes = collections.defaultdict(dict)
    target_edges = collections.Counter()
    target_missing = collections.Counter()
    cross = collections.defaultdict(set)

    expected = {"PS": (32, 8, 1, 8), "VS": (32, 9, 1, 9)}
    for row in headers:
        stage = str(row.get("stage"))
        if stage not in expected:
            violations.append(f"unsupported_stage:{stage}")
            continue
        ht, hs, nt, ns = expected[stage]
        tag = norm(row.get("header"))
        ref = norm(row.get("native_program_reference"))
        by_stage[stage].append(tag)
        refs_by_stage[stage][ref] += 1
        cross[ref].add(stage)
        header_pkgs[stage].add(str(row.get("header_package_id")).upper().zfill(4))
        if (int(row.get("header_type", -1)), int(row.get("header_subtype", -1))) != (ht, hs):
            violations.append(f"{stage}:{tag}:header_type_subtype")
        m = row.get("native_program_meta")
        if not isinstance(m, dict) or "type" not in m:
            target_missing[stage] += 1
            violations.append(f"{stage}:{tag}:native_program_meta_unresolved:{ref}")
            continue
        typ = int(m["type"]); sub = int(m["subtype"])
        target_edges[(stage, typ, sub)] += 1
        if (typ, sub) != (nt, ns):
            violations.append(f"{stage}:{tag}:native_target:{ref}:{typ}:{sub}!={nt}:{ns}")
        native_pkgs[stage].add(str(m.get("package_id")).upper().zfill(4))
        size = int(m.get("file_size", -1))
        if ref in native_sizes[stage] and native_sizes[stage][ref] != size:
            violations.append(f"{stage}:{ref}:native_size_disagreement")
        native_sizes[stage][ref] = size

    all_refs = set(refs_by_stage["PS"]) | set(refs_by_stage["VS"])
    cross_stage = sorted(ref for ref, stages in cross.items() if len(stages) > 1)
    if cross_stage:
        violations.append(f"cross_stage_native_references:{cross_stage[:20]}")

    observed = {
        "header_population": {
            "total": len(headers),
            "distinct_header_tag_hashes": len({h for rows in by_stage.values() for h in rows}),
            "package_families_with_any_ps_or_vs_header": len(set().union(*header_pkgs.values())),
            "pixel_shader": {
                "header_count": len(by_stage["PS"]),
                "distinct_header_tag_hashes": len(set(by_stage["PS"])),
                "distinct_native_program_references": len(refs_by_stage["PS"]),
                "header_package_families": len(header_pkgs["PS"]),
            },
            "vertex_shader": {
                "header_count": len(by_stage["VS"]),
                "distinct_header_tag_hashes": len(set(by_stage["VS"])),
                "distinct_native_program_references": len(refs_by_stage["VS"]),
                "header_package_families": len(header_pkgs["VS"]),
            },
        },
        "native_reference_population": {
            "distinct_native_program_references": len(all_refs),
            "cross_stage_shared_reference_count": len(cross_stage),
            "references_used_by_multiple_logical_headers": sum(
                n > 1 for c in refs_by_stage.values() for n in c.values()
            ),
            "maximum_headers_per_native_reference": max(
                [0] + [n for c in refs_by_stage.values() for n in c.values()]
            ),
        },
    }

    for stage, key in (("PS", "pixel_shader"), ("VS", "vertex_shader")):
        c = refs_by_stage[stage]
        vals = list(native_sizes[stage].values())
        exp_stage = e["native_reference_population"][key]
        obs_stage = {
            "distinct_native_program_references": len(c),
            "references_used_by_multiple_logical_headers": sum(n > 1 for n in c.values()),
            "maximum_headers_per_native_reference": max([0] + list(c.values())),
            "native_target_type": expected[stage][2],
            "native_target_subtype": expected[stage][3],
            "native_target_edge_count": target_edges[(stage, expected[stage][2], expected[stage][3])],
            "unexpected_native_target_edge_count": sum(
                n for (s, typ, sub), n in target_edges.items()
                if s == stage and (typ, sub) != expected[stage][2:]
            ) + target_missing[stage],
            "native_target_package_families": len(native_pkgs[stage]),
            "native_payload_file_size_bytes": {
                "minimum": min(vals) if vals else None,
                "median_across_distinct_references": statistics.median(vals) if vals else None,
                "maximum": max(vals) if vals else None,
            },
        }
        observed["native_reference_population"][key] = obs_stage
        for k, v in obs_stage.items():
            if exp_stage.get(k) != v:
                violations.append(f"{stage}:{k}:{v!r}!={exp_stage.get(k)!r}")

    for k, v in observed["header_population"].items():
        if isinstance(v, dict):
            for kk, vv in v.items():
                if e["header_population"][k].get(kk) != vv:
                    violations.append(f"header_population:{k}:{kk}:{vv!r}!={e['header_population'][k].get(kk)!r}")
        elif e["header_population"].get(k) != v:
            violations.append(f"header_population:{k}:{v!r}!={e['header_population'].get(k)!r}")
    for k in ("distinct_native_program_references", "cross_stage_shared_reference_count",
              "references_used_by_multiple_logical_headers", "maximum_headers_per_native_reference"):
        v = observed["native_reference_population"][k]
        if e["native_reference_population"].get(k) != v:
            violations.append(f"native_reference_population:{k}:{v!r}!={e['native_reference_population'].get(k)!r}")

    out = {
        "schema": "d1_shader_corpus_metadata_accept/v1",
        "status": "D1_SHADER_CORPUS_METADATA_ACCEPTED" if not violations else "D1_SHADER_CORPUS_METADATA_REJECTED",
        "source_plan": str(a.plan),
        "source_evidence": str(a.evidence),
        "packages_txt_sha256": psha,
        "observed": observed,
        "violations": violations,
        "policy": "Acceptance requires exact agreement with the immutable current-retail metadata checkpoint. This gate proves only shader-header/native-reference graph facts; native bytes, OrbShdr, GCN structural IR, and semantics remain separate gates."
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n")
    print("STATUS", out["status"], "HEADERS", len(headers), "REFS", len(all_refs), "VIOLATIONS", len(violations))
    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
