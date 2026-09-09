#!/usr/bin/env python3
"""Recover the exact current D1 PS4 PS/VS corpus with package-scoped parallelism.

This is the scalable successor to ``d1_remote_ps4_shader_corpus_extract.py``.
It preserves the same proof boundary while changing only execution strategy:

* the exact metadata plan supplies the complete logical-header/native-reference
  denominator even when a later payload fails;
* required logical package views are constructed serially because Oodle3 loader
  initialization temporarily changes process cwd;
* distinct package families are then processed concurrently;
* each package retains its decompressed block cache only for that package task and
  clears it when complete, bounding peak memory rather than retaining the union of
  every touched 0x40000-byte Tiger block;
* header bytes and native payloads are joined only by the plan's exact serialized
  FileEntry.Reference after recovery;
* OrbShdr framing remains fail-closed and byte-level GCN deduplication remains
  SHA-256 exact.

No shader semantics are inferred here.
"""
from __future__ import annotations

import argparse
import collections
import concurrent.futures
import hashlib
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_investment_arrangement_probe import filehash_pkg_index
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_split_tar_extract import SplitHttpTar
from d1_ps4_shader_binary_probe import find_footer, parse_binary_info, parse_usage
from d1_ps4_vertex_shader_header import parse_header as parse_vertex_header

NULLS = {"00000000", "FFFFFFFF"}
EXPECTED = {
    "PS": {"header": (32, 8), "native": (1, 8), "orb_stage": "PixelShader"},
    "VS": {"header": (32, 9), "native": (1, 9), "orb_stage": "VertexShader"},
}


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def package_of(tag: str) -> int:
    return filehash_pkg_index(int(norm(tag), 16))[0]


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def digest(b: bytes) -> dict:
    return {"bytes": len(b), "sha256": sha256(b)}


def u32(b: bytes, off: int = 0) -> int:
    if off < 0 or off + 4 > len(b):
        raise ValueError((off, len(b)))
    return struct.unpack_from("<I", b, off)[0]


def recover_package(
    pkg: int,
    view: RemoteLogicalPackage,
    header_specs: list[dict],
    native_refs: list[str],
    ref_users: dict[str, list[dict]],
) -> dict:
    """Recover all requested shader resources from one already-created package view."""
    out = {
        "package_id": f"{pkg:04X}",
        "logical_view": view.view.name,
        "headers": {},
        "natives": {},
        "violations": [],
    }
    by = {norm(e["tag_hash"]): e for e in view.entries}
    try:
        for spec in sorted(header_specs, key=lambda x: x["header"]):
            stage = spec["stage"]
            tag = spec["header"]
            planned_ref = spec["native_program_reference"]
            row = {
                "stage": stage,
                "header": tag,
                "planned_native_program_reference": planned_ref,
                "package_id": f"{pkg:04X}",
                "logical_view": view.view.name,
                "violations": [],
            }
            e = by.get(tag)
            if e is None:
                row["violations"].append("header_entry_unavailable")
                out["headers"][tag] = {"row": row, "payload": None}
                continue
            row["retail_header_meta"] = e
            want = EXPECTED[stage]["header"]
            if (int(e.get("type", -1)), int(e.get("subtype", -1))) != want:
                row["violations"].append(
                    f"header_type_subtype:{e.get('type')}:{e.get('subtype')}!={want[0]}:{want[1]}"
                )
            retail_ref = norm(e.get("reference", "FFFFFFFF"))
            row["retail_native_program_reference"] = retail_ref
            if retail_ref != planned_ref:
                row["violations"].append(f"reference_mismatch:{planned_ref}!={retail_ref}")
            try:
                hb = view.entry(int(e["index"]))
            except Exception as ex:
                hb = None
                row["violations"].append(f"header_payload:{type(ex).__name__}:{ex}")
            if hb is not None:
                row["header_payload"] = digest(hb)
                if len(hb) != int(e.get("file_size", -1)):
                    row["violations"].append(
                        f"header_size:{len(hb)}!={e.get('file_size')}"
                    )
            out["headers"][tag] = {"row": row, "payload": hb}

        for ref in sorted(native_refs):
            users = ref_users[ref]
            stages = sorted({x["stage"] for x in users})
            row = {
                "native_program_reference": ref,
                "package_id": f"{pkg:04X}",
                "logical_view": view.view.name,
                "header_count": len(users),
                "headers": [
                    {"stage": x["stage"], "header": x["header"]}
                    for x in sorted(users, key=lambda x: (x["stage"], x["header"]))
                ],
                "stages": stages,
                "violations": [],
            }
            if len(stages) != 1:
                row["violations"].append(
                    "native_reference_shared_across_shader_stages:" + ",".join(stages)
                )
            e = by.get(ref)
            if e is None:
                row["violations"].append("native_entry_unavailable")
                out["natives"][ref] = {"row": row, "payload": None, "code": None}
                continue
            row["retail_native_meta"] = e
            if len(stages) == 1:
                want_native = EXPECTED[stages[0]]["native"]
                if (int(e.get("type", -1)), int(e.get("subtype", -1))) != want_native:
                    row["violations"].append(
                        f"native_type_subtype:{e.get('type')}:{e.get('subtype')}!="
                        f"{want_native[0]}:{want_native[1]}"
                    )
            try:
                pb = view.entry(int(e["index"]))
            except Exception as ex:
                pb = None
                row["violations"].append(f"native_payload:{type(ex).__name__}:{ex}")
            code = None
            if pb is not None:
                row["native_payload"] = digest(pb)
                if len(pb) != int(e.get("file_size", -1)):
                    row["violations"].append(
                        f"native_size:{len(pb)}!={e.get('file_size')}"
                    )
                footer, locator = find_footer(pb)
                row["orbshdr_locator"] = locator
                if footer is None:
                    row["violations"].append("orbshdr_footer_unresolved")
                elif not locator.get("formula_magic_matches"):
                    row["violations"].append("orbshdr_nonformula_footer_form")
                else:
                    try:
                        info = parse_binary_info(pb, footer)
                        row["binary_info"] = info
                        row["usage"] = parse_usage(pb, footer, info)
                        if len(stages) == 1 and info["stage"] != EXPECTED[stages[0]]["orb_stage"]:
                            row["violations"].append(
                                f"orbshdr_stage:{info['stage']}!={EXPECTED[stages[0]]['orb_stage']}"
                            )
                        n = int(info["code_length_bytes"])
                        if n <= 0 or n > footer or n > len(pb):
                            row["violations"].append(
                                f"invalid_code_length:{n}:footer={footer}:payload={len(pb)}"
                            )
                        else:
                            code = pb[:n]
                            row["gcn_code"] = digest(code)
                    except Exception as ex:
                        row["violations"].append(
                            f"orbshdr_parse:{type(ex).__name__}:{ex}"
                        )
            out["natives"][ref] = {"row": row, "payload": pb, "code": code}
    finally:
        # Package-scoped cache lifetime is the main memory-bound improvement over v1.
        view.block_cache.clear()
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", type=Path, required=True)
    ap.add_argument("--member-catalog", type=Path, action="append", required=True)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--part-count", type=int, default=10)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    a = ap.parse_args()
    if a.workers < 1 or a.workers > 32:
        raise SystemExit("--workers must be in 1..32")

    plan = json.loads(a.plan.read_text())
    if plan.get("schema") != "d1_shader_corpus_plan/v1":
        raise SystemExit(f"unsupported plan schema: {plan.get('schema')!r}")
    if plan.get("status") != "D1_SHADER_CORPUS_PLAN_COMPLETE" or plan.get("violations"):
        raise SystemExit("exact violation-free shader corpus plan required")

    headers = plan.get("headers") or []
    violations: list[str] = []
    header_specs: list[dict] = []
    ref_users: dict[str, list[dict]] = collections.defaultdict(list)
    by_pkg_headers: dict[int, list[dict]] = collections.defaultdict(list)
    by_pkg_refs: dict[int, set[str]] = collections.defaultdict(set)

    for p in headers:
        stage = str(p.get("stage"))
        if stage not in EXPECTED:
            violations.append(f"{p.get('header')}:unsupported_stage:{stage}")
            continue
        tag = norm(p.get("header"))
        ref = norm(p.get("native_program_reference"))
        spec = {
            "stage": stage,
            "header": tag,
            "native_program_reference": ref,
        }
        if ref in NULLS:
            violations.append(f"{stage}:{tag}:null_native_program_reference:{ref}")
        hpkg = package_of(tag)
        planned_hpkg = str(p.get("header_package_id") or "").upper().zfill(4)
        if planned_hpkg and planned_hpkg != f"{hpkg:04X}":
            violations.append(
                f"{stage}:{tag}:header_package:{planned_hpkg}!={hpkg:04X}"
            )
        header_specs.append(spec)
        by_pkg_headers[hpkg].append(spec)
        ref_users[ref].append({"stage": stage, "header": tag})

    # The denominator is built from the complete plan, never from successful payload recovery.
    for ref, users in ref_users.items():
        if ref in NULLS:
            continue
        rpkg = package_of(ref)
        by_pkg_refs[rpkg].add(ref)
        stages = {x["stage"] for x in users}
        if len(stages) != 1:
            violations.append(
                f"{ref}:native_reference_shared_across_shader_stages:{','.join(sorted(stages))}"
            )

    planned_unique_refs = len([x for x in ref_users if x not in NULLS])
    expected_plan_refs = int(
        (plan.get("native_reference_population") or {}).get(
            "unique_native_program_reference_count", planned_unique_refs
        )
    )
    if expected_plan_refs != planned_unique_refs:
        violations.append(
            f"plan_native_reference_denominator:{planned_unique_refs}!={expected_plan_refs}"
        )

    catalogs = load_catalogs(a.member_catalog)
    needed_pkgs = sorted(set(by_pkg_headers) | set(by_pkg_refs))
    missing_pkgs = [f"{p:04X}" for p in needed_pkgs if p not in catalogs]
    if missing_pkgs:
        violations.append(f"member_catalog_missing_packages:{missing_pkgs[:40]}")
    if violations:
        # Metadata/corpus identity problems are not recoverable payload diagnostics.
        raise SystemExit("; ".join(violations[:50]))

    base = a.base_url.rstrip("/")
    arc = SplitHttpTar(
        [f"{base}/packages.tar.{i:03d}" for i in range(1, a.part_count + 1)],
        retries=6,
        timeout=90,
    )

    # Oodle3 initialization changes cwd temporarily; construct views serially.
    views: dict[int, RemoteLogicalPackage] = {}
    init_errors = []
    for n, pkg in enumerate(needed_pkgs, 1):
        try:
            views[pkg] = RemoteLogicalPackage(arc, catalogs[pkg], a.runtime)
        except Exception as ex:
            init_errors.append(f"{pkg:04X}:{type(ex).__name__}:{ex}")
        if n % 25 == 0 or n == len(needed_pkgs):
            print(f"VIEWS {n}/{len(needed_pkgs)} ERRORS {len(init_errors)}", flush=True)
    if init_errors:
        raise SystemExit("package view initialization failed: " + "; ".join(init_errors[:30]))

    a.out_dir.mkdir(parents=True, exist_ok=True)
    headers_dir = a.out_dir / "headers"
    programs_dir = a.out_dir / "programs"
    headers_dir.mkdir(parents=True, exist_ok=True)
    programs_dir.mkdir(parents=True, exist_ok=True)

    recovered_headers: dict[str, dict] = {}
    header_payloads: dict[str, bytes] = {}
    recovered_natives: dict[str, dict] = {}
    native_payloads: dict[str, bytes] = {}
    native_codes: dict[str, bytes] = {}
    package_rows = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
        futures = {
            pool.submit(
                recover_package,
                pkg,
                views[pkg],
                list(by_pkg_headers.get(pkg, [])),
                sorted(by_pkg_refs.get(pkg, set())),
                ref_users,
            ): pkg
            for pkg in needed_pkgs
        }
        for done, fut in enumerate(concurrent.futures.as_completed(futures), 1):
            pkg = futures[fut]
            try:
                r = fut.result()
            except Exception as ex:
                violations.append(f"package_worker:{pkg:04X}:{type(ex).__name__}:{ex}")
                r = {
                    "package_id": f"{pkg:04X}",
                    "logical_view": views[pkg].view.name,
                    "headers": {},
                    "natives": {},
                    "violations": [f"worker:{type(ex).__name__}:{ex}"],
                }
            package_rows.append({
                "package_id": r["package_id"],
                "logical_view": r.get("logical_view"),
                "planned_header_count": len(by_pkg_headers.get(pkg, [])),
                "planned_native_reference_count": len(by_pkg_refs.get(pkg, set())),
                "recovered_header_count": len(r.get("headers") or {}),
                "recovered_native_reference_count": len(r.get("natives") or {}),
                "violations": r.get("violations") or [],
            })
            for tag, x in (r.get("headers") or {}).items():
                recovered_headers[tag] = x["row"]
                if x.get("payload") is not None:
                    header_payloads[tag] = x["payload"]
            for ref, x in (r.get("natives") or {}).items():
                recovered_natives[ref] = x["row"]
                if x.get("payload") is not None:
                    native_payloads[ref] = x["payload"]
                if x.get("code") is not None:
                    native_codes[ref] = x["code"]
            print(
                f"PACKAGES {done}/{len(futures)} HEADERS {len(recovered_headers)}/{len(header_specs)} "
                f"NATIVES {len(recovered_natives)}/{planned_unique_refs}",
                flush=True,
            )

    # Restore deterministic plan order and preserve rows for every planned identity.
    header_rows = []
    header_index = {}
    for spec in header_specs:
        tag = spec["header"]
        row = recovered_headers.get(tag)
        if row is None:
            row = {
                "stage": spec["stage"],
                "header": tag,
                "planned_native_program_reference": spec["native_program_reference"],
                "violations": ["package_recovery_row_missing"],
            }
        hb = header_payloads.get(tag)
        if hb is not None:
            path = headers_dir / f"{spec['stage']}_{tag}.bin"
            path.write_bytes(hb)
            row["header_file"] = str(path)
        header_index[tag] = len(header_rows)
        header_rows.append(row)

    native_rows = []
    by_code_sha: dict[str, dict] = {}
    for ref in sorted(x for x in ref_users if x not in NULLS):
        users = ref_users[ref]
        row = recovered_natives.get(ref)
        if row is None:
            row = {
                "native_program_reference": ref,
                "header_count": len(users),
                "headers": sorted(users, key=lambda x: (x["stage"], x["header"])),
                "stages": sorted({x["stage"] for x in users}),
                "violations": ["package_recovery_row_missing"],
            }
        row.setdefault("violations", [])
        pb = native_payloads.get(ref)
        code = native_codes.get(ref)

        # Join exact recovered header bytes to the exact serialized native reference.
        if pb is not None and row.get("binary_info") is not None:
            info = row["binary_info"]
            for user in users:
                stage = user["stage"]
                htag = user["header"]
                hb = header_payloads.get(htag)
                if hb is None:
                    row["violations"].append(f"{htag}:header_payload_unavailable_for_native_join")
                    continue
                if stage == "PS":
                    if len(hb) < 4:
                        row["violations"].append(f"{htag}:ps_header_too_short:{len(hb)}")
                    else:
                        packed = u32(hb)
                        embedded = packed & 0x00FFFFFF
                        usage_count = (packed >> 24) & 0xFF
                        if embedded != len(pb):
                            row["violations"].append(
                                f"{htag}:ps_embedded_size:{embedded}!={len(pb)}"
                            )
                        if usage_count != int(info["num_input_usage_slots"]):
                            row["violations"].append(
                                f"{htag}:ps_usage_count:{usage_count}!={info['num_input_usage_slots']}"
                            )
                else:
                    try:
                        vh = parse_vertex_header(hb, pb)
                        header_rows[header_index[htag]]["vertex_header"] = vh
                        checks = vh.get("checks") or {}
                        native_checks = vh.get("native_checks") or {}
                        if not checks.get("wrapper_shader_size_matches_gnmx_shader_size"):
                            row["violations"].append(f"{htag}:vs_wrapper_shader_size_mismatch")
                        for key in (
                            "resolved",
                            "stage_is_vertex_shader",
                            "gnmx_shader_size_matches_orbshdr_end",
                            "usage_count_matches_orbshdr",
                        ):
                            if not native_checks.get(key):
                                row["violations"].append(f"{htag}:vs_native_check:{key}")
                    except Exception as ex:
                        row["violations"].append(
                            f"{htag}:vs_header_parse:{type(ex).__name__}:{ex}"
                        )

        if code is not None:
            code_sha = sha256(code)
            code_len = len(code)
            if row.get("gcn_code") != {"bytes": code_len, "sha256": code_sha}:
                row["violations"].append("gcn_digest_recheck_mismatch")
            path = programs_dir / f"{code_sha}.bin"
            if path.exists() and path.read_bytes() != code:
                row["violations"].append(f"code_sha256_collision:{code_sha}")
            else:
                path.write_bytes(code)
                row["gcn_program_file"] = str(path)
            q = by_code_sha.setdefault(code_sha, {
                "gcn_sha256": code_sha,
                "gcn_bytes": code_len,
                "native_program_references": [],
                "headers": [],
                "stages": set(),
            })
            if int(q["gcn_bytes"]) != code_len:
                row["violations"].append(f"code_length_disagreement_for_sha:{code_sha}")
            q["native_program_references"].append(ref)
            q["headers"].extend(
                {"stage": x["stage"], "header": x["header"]} for x in users
            )
            q["stages"].update(x["stage"] for x in users)

        if row["violations"]:
            violations.extend(f"{ref}:{x}" for x in row["violations"])
        native_rows.append(row)

    for row in header_rows:
        if row.get("violations"):
            violations.extend(
                f"{row.get('stage')}:{row.get('header')}:{x}" for x in row["violations"]
            )

    program_rows = []
    for code_sha, q in sorted(by_code_sha.items()):
        q["native_program_references"] = sorted(set(q["native_program_references"]))
        q["headers"] = sorted(q["headers"], key=lambda x: (x["stage"], x["header"]))
        q["stages"] = sorted(q["stages"])
        q["native_reference_count"] = len(q["native_program_references"])
        q["header_count"] = len(q["headers"])
        program_rows.append(q)

    stage_program_sets: dict[str, set[str]] = collections.defaultdict(set)
    for p in program_rows:
        for stage in p["stages"]:
            stage_program_sets[stage].add(p["gcn_sha256"])

    plan_stage_counts = dict(
        sorted((plan.get("header_population") or {}).get("stage_counts", {}).items())
    )
    if sum(int(x) for x in plan_stage_counts.values()) != len(header_specs):
        violations.append("plan_stage_counts_do_not_sum_to_header_denominator")

    out = {
        "schema": "d1_remote_ps4_shader_corpus_extract/v2",
        "status": (
            "D1_REMOTE_PS4_SHADER_CORPUS_EXACT"
            if not violations
            else "D1_REMOTE_PS4_SHADER_CORPUS_WITH_VIOLATIONS"
        ),
        "source_plan": str(a.plan),
        "recovery_strategy": {
            "name": "package_scoped_parallel_sparse_recovery",
            "workers": a.workers,
            "package_view_initialization": "serial",
            "package_payload_recovery": "parallel_across_distinct_package_views",
            "block_cache_lifetime": "one_package_task",
            "native_reference_denominator_source": "complete_exact_metadata_plan"
        },
        "header_population": {
            "total": len(header_specs),
            "stage_counts": plan_stage_counts,
            "payload_recovered_count": len(header_payloads),
            "payload_unrecovered_count": len(header_specs) - len(header_payloads),
        },
        "native_reference_population": {
            "planned_unique": planned_unique_refs,
            "recovered_rows": len(recovered_natives),
            "payload_recovered_count": len(native_payloads),
            "gcn_code_recovered_count": len(native_codes),
            "violation_rows": sum(bool(x.get("violations")) for x in native_rows),
            "unrecovered_native_references": sorted(
                set(ref_users) - NULLS - set(native_payloads)
            ),
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
        "package_recovery": sorted(package_rows, key=lambda x: x["package_id"]),
        "headers": header_rows,
        "native_programs": native_rows,
        "unique_gcn_programs": program_rows,
        "violations": violations,
        "policy": (
            "The complete current 32:8/32:9 metadata plan fixes the denominator before payload I/O. "
            "Every resource is recovered from its exact FileHash package/index, every compressed "
            "Tiger block retains stored SHA-1 and Oodle length validation, native type/subtype must "
            "match 1:8/1:9 by stage, only formula-resolved OrbShdr metadata bounds executable GCN, "
            "and exact GCN bytes are deduplicated only by SHA-256. Parallelism changes scheduling only."
        ),
    }

    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(out, indent=2) + "\n")
    print(
        "STATUS", out["status"],
        "HEADERS", f"{len(header_payloads)}/{len(header_specs)}",
        "NATIVE_PAYLOADS", f"{len(native_payloads)}/{planned_unique_refs}",
        "GCN_REFS", f"{len(native_codes)}/{planned_unique_refs}",
        "UNIQUE_GCN", len(program_rows),
        "VIOLATIONS", len(violations),
    )
    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
