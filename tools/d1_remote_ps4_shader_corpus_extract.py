#!/usr/bin/env python3
"""Recover and byte-deduplicate every planned current-retail D1 PS4 PS/VS program.

Input is an exact ``d1_shader_corpus_plan/v1``.  Every shader header is re-resolved
against the verified universal member catalog, then its FileEntry.Reference native
payload is fetched through RemoteCorpus.  OrbShdr bounds the machine code.  Programs
are deduplicated twice: first by native FileHash reference and then by exact GCN code
SHA-256.

This layer deliberately stops before instruction interpretation.  Unexpected header
or OrbShdr forms are violations, not guessed compatibility cases.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_split_tar_extract import SplitHttpTar
from d1_ps4_shader_binary_probe import find_footer, parse_binary_info, parse_usage
from d1_ps4_vertex_shader_header import parse_header as parse_vertex_header

NULLS = {"00000000", "FFFFFFFF"}
EXPECTED = {"PS": (32, 8, "PixelShader"), "VS": (32, 9, "VertexShader")}


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def digest(b: bytes) -> dict:
    return {"bytes": len(b), "sha256": sha256(b)}


def u32(b: bytes, off: int = 0) -> int:
    if off < 0 or off + 4 > len(b):
        raise ValueError((off, len(b)))
    return struct.unpack_from("<I", b, off)[0]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", type=Path, required=True)
    ap.add_argument("--member-catalog", type=Path, action="append", required=True)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--part-count", type=int, default=10)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    a = ap.parse_args()

    plan = json.loads(a.plan.read_text())
    if plan.get("schema") != "d1_shader_corpus_plan/v1":
        raise SystemExit(f"unsupported plan schema: {plan.get('schema')!r}")
    if plan.get("status") != "D1_SHADER_CORPUS_PLAN_COMPLETE" or plan.get("violations"):
        raise SystemExit("exact violation-free shader corpus plan required")

    catalogs = load_catalogs(a.member_catalog)
    base = a.base_url.rstrip("/")
    arc = SplitHttpTar(
        [f"{base}/packages.tar.{i:03d}" for i in range(1, a.part_count + 1)],
        retries=6, timeout=90,
    )
    corpus = RemoteCorpus(arc, catalogs, a.runtime)

    headers_dir = a.out_dir / "headers"
    programs_dir = a.out_dir / "programs"
    headers_dir.mkdir(parents=True, exist_ok=True)
    programs_dir.mkdir(parents=True, exist_ok=True)

    violations: list[str] = []
    header_rows: list[dict] = []
    ref_users: dict[str, list[dict]] = collections.defaultdict(list)

    # Re-resolve every planned header from the retail corpus before trusting the
    # plan's FileEntry.Reference. This catches stale/mismatched index/catalog data.
    for p in plan["headers"]:
        stage = str(p["stage"])
        if stage not in EXPECTED:
            violations.append(f"{p.get('header')}:unsupported_stage:{stage}")
            continue
        want_type, want_subtype, _ = EXPECTED[stage]
        tag = norm(p["header"])
        planned_ref = norm(p["native_program_reference"])
        row = {"stage": stage, "header": tag, "planned_native_program_reference": planned_ref}

        hm = corpus.entry_meta(tag)
        row["retail_header_meta"] = hm
        if hm is None:
            row["violation"] = "header_meta_unavailable"
            violations.append(f"{stage}:{tag}:header_meta_unavailable")
            header_rows.append(row)
            continue
        if (int(hm.get("type", -1)), int(hm.get("subtype", -1))) != (want_type, want_subtype):
            violations.append(
                f"{stage}:{tag}:header_type_subtype:"
                f"{hm.get('type')}:{hm.get('subtype')}!={want_type}:{want_subtype}"
            )
        retail_ref = norm(hm.get("reference", "FFFFFFFF"))
        row["retail_native_program_reference"] = retail_ref
        if retail_ref != planned_ref:
            violations.append(f"{stage}:{tag}:reference_mismatch:{planned_ref}!={retail_ref}")
        if retail_ref in NULLS:
            violations.append(f"{stage}:{tag}:null_native_program_reference:{retail_ref}")

        hb, hsrc = corpus.payload(tag)
        row["header_source"] = hsrc
        if hb is None:
            violations.append(f"{stage}:{tag}:header_payload_unavailable")
            header_rows.append(row)
            continue
        row["header_payload"] = digest(hb)
        row["header_file"] = str(headers_dir / f"{stage}_{tag}.bin")
        (headers_dir / f"{stage}_{tag}.bin").write_bytes(hb)

        if len(hb) != int(hm.get("file_size", -1)):
            violations.append(f"{stage}:{tag}:header_size:{len(hb)}!={hm.get('file_size')}")

        ref_users[retail_ref].append({
            "stage": stage,
            "header": tag,
            "header_bytes": hb,
            "row_index": len(header_rows),
        })
        header_rows.append(row)

    native_rows: list[dict] = []
    by_code_sha: dict[str, dict] = {}

    for ref in sorted(ref_users):
        users = ref_users[ref]
        nrow = {
            "native_program_reference": ref,
            "header_count": len(users),
            "headers": [{"stage": x["stage"], "header": x["header"]} for x in users],
            "stages": sorted({x["stage"] for x in users}),
            "violations": [],
        }
        if ref in NULLS:
            nrow["violations"].append("null_reference")
            native_rows.append(nrow)
            continue

        pm = corpus.entry_meta(ref)
        nrow["retail_native_meta"] = pm
        pb, psrc = corpus.payload(ref)
        nrow["native_source"] = psrc
        if pm is None:
            nrow["violations"].append("native_meta_unavailable")
        if pb is None:
            nrow["violations"].append("native_payload_unavailable")
            native_rows.append(nrow)
            violations.extend(f"{ref}:{x}" for x in nrow["violations"])
            continue
        nrow["native_payload"] = digest(pb)
        if pm is not None and len(pb) != int(pm.get("file_size", -1)):
            nrow["violations"].append(f"native_size:{len(pb)}!={pm.get('file_size')}")

        footer, locator = find_footer(pb)
        nrow["orbshdr_locator"] = locator
        # A non-formula fallback is a newly observed binary form, not silent compatibility.
        if footer is None:
            nrow["violations"].append("orbshdr_footer_unresolved")
        elif not locator.get("formula_magic_matches"):
            nrow["violations"].append("orbshdr_nonformula_footer_form")
        else:
            try:
                info = parse_binary_info(pb, footer)
                nrow["binary_info"] = info
                nrow["usage"] = parse_usage(pb, footer, info)
                expected_stages = {EXPECTED[x["stage"]][2] for x in users}
                if len(expected_stages) != 1:
                    nrow["violations"].append(
                        "native_reference_shared_across_shader_stages:" + ",".join(sorted(expected_stages))
                    )
                elif info["stage"] not in expected_stages:
                    nrow["violations"].append(
                        f"orbshdr_stage:{info['stage']}!={next(iter(expected_stages))}"
                    )
                code_len = int(info["code_length_bytes"])
                if code_len <= 0 or code_len > footer or code_len > len(pb):
                    nrow["violations"].append(
                        f"invalid_code_length:{code_len}:footer={footer}:payload={len(pb)}"
                    )
                else:
                    code = pb[:code_len]
                    code_sha = sha256(code)
                    nrow["gcn_code"] = {"bytes": code_len, "sha256": code_sha}
                    nrow["gcn_program_file"] = str(programs_dir / f"{code_sha}.bin")
                    path = programs_dir / f"{code_sha}.bin"
                    if path.exists() and path.read_bytes() != code:
                        nrow["violations"].append(f"code_sha256_collision:{code_sha}")
                    else:
                        path.write_bytes(code)

                    q = by_code_sha.setdefault(code_sha, {
                        "gcn_sha256": code_sha,
                        "gcn_bytes": code_len,
                        "native_program_references": [],
                        "headers": [],
                        "stages": set(),
                    })
                    if int(q["gcn_bytes"]) != code_len:
                        nrow["violations"].append(f"code_length_disagreement_for_sha:{code_sha}")
                    q["native_program_references"].append(ref)
                    q["headers"].extend({"stage": x["stage"], "header": x["header"]} for x in users)
                    q["stages"].update(x["stage"] for x in users)

                    # Header-form checks remain stage-specific but do not infer source semantics.
                    for x in users:
                        htag = x["header"]
                        hb = x["header_bytes"]
                        if x["stage"] == "PS":
                            if len(hb) < 4:
                                nrow["violations"].append(f"{htag}:ps_header_too_short:{len(hb)}")
                            else:
                                packed = u32(hb)
                                embedded = packed & 0x00FFFFFF
                                usage_count = (packed >> 24) & 0xFF
                                if embedded != len(pb):
                                    nrow["violations"].append(
                                        f"{htag}:ps_embedded_size:{embedded}!={len(pb)}"
                                    )
                                if usage_count != int(info["num_input_usage_slots"]):
                                    nrow["violations"].append(
                                        f"{htag}:ps_usage_count:{usage_count}!="
                                        f"{info['num_input_usage_slots']}"
                                    )
                        else:
                            try:
                                vh = parse_vertex_header(hb, pb)
                                header_rows[x["row_index"]]["vertex_header"] = vh
                                checks = vh.get("checks") or {}
                                native_checks = vh.get("native_checks") or {}
                                if not checks.get("wrapper_shader_size_matches_gnmx_shader_size"):
                                    nrow["violations"].append(
                                        f"{htag}:vs_wrapper_shader_size_mismatch"
                                    )
                                for key in (
                                    "resolved",
                                    "stage_is_vertex_shader",
                                    "gnmx_shader_size_matches_orbshdr_end",
                                    "usage_count_matches_orbshdr",
                                ):
                                    if not native_checks.get(key):
                                        nrow["violations"].append(f"{htag}:vs_native_check:{key}")
                            except Exception as ex:
                                nrow["violations"].append(
                                    f"{htag}:vs_header_parse:{type(ex).__name__}:{ex}"
                                )
            except Exception as ex:
                nrow["violations"].append(
                    f"orbshdr_parse:{type(ex).__name__}:{ex}"
                )

        if nrow["violations"]:
            violations.extend(f"{ref}:{x}" for x in nrow["violations"])
        native_rows.append(nrow)

    program_rows = []
    for code_sha, q in sorted(by_code_sha.items()):
        q["native_program_references"] = sorted(set(q["native_program_references"]))
        q["headers"] = sorted(
            q["headers"], key=lambda x: (x["stage"], x["header"])
        )
        q["stages"] = sorted(q["stages"])
        q["native_reference_count"] = len(q["native_program_references"])
        q["header_count"] = len(q["headers"])
        program_rows.append(q)

    stage_header_counts = collections.Counter(x["stage"] for x in header_rows)
    stage_program_sets: dict[str, set[str]] = collections.defaultdict(set)
    for p in program_rows:
        for stage in p["stages"]:
            stage_program_sets[stage].add(p["gcn_sha256"])

    out = {
        "schema": "d1_remote_ps4_shader_corpus_extract/v1",
        "status": (
            "D1_REMOTE_PS4_SHADER_CORPUS_EXACT"
            if not violations
            else "D1_REMOTE_PS4_SHADER_CORPUS_WITH_VIOLATIONS"
        ),
        "source_plan": str(a.plan),
        "header_population": {
            "total": len(header_rows),
            "stage_counts": dict(sorted(stage_header_counts.items())),
        },
        "native_reference_population": {
            "planned_unique": len(ref_users),
            "recovered_rows": len(native_rows),
            "violation_rows": sum(bool(x["violations"]) for x in native_rows),
        },
        "gcn_program_population": {
            "unique_exact_code_sha256_count": len(program_rows),
            "stage_unique_counts": {
                k: len(v) for k, v in sorted(stage_program_sets.items())
            },
            "shared_by_multiple_native_references": sum(
                int(x["native_reference_count"] > 1) for x in program_rows
            ),
            "shared_by_multiple_headers": sum(
                int(x["header_count"] > 1) for x in program_rows
            ),
        },
        "headers": header_rows,
        "native_programs": native_rows,
        "unique_gcn_programs": program_rows,
        "violations": violations,
        "policy": (
            "Every current 32:8/32:9 header is re-resolved from exact retail bytes. "
            "Only FileEntry.Reference selects native payloads; only formula-resolved "
            "OrbShdr metadata bounds GCN code. Native references and exact GCN bytes "
            "are separately deduplicated. Unexpected binary/header forms remain violations."
        ),
    }

    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(out, indent=2) + "\n")
    print(
        "STATUS", out["status"],
        "HEADERS", out["header_population"]["total"],
        "NATIVE_REFS", out["native_reference_population"]["planned_unique"],
        "UNIQUE_GCN", out["gcn_program_population"]["unique_exact_code_sha256_count"],
        "VIOLATIONS", len(violations),
    )
    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
