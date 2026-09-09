#!/usr/bin/env python3
"""Promote a complete D1 PS4 shader-corpus V2 diagnostic into exact PS/VS/DS form.

The first complete current-retail V2 recovery reached every planned header/native
reference but intentionally failed closed on two assumptions that the complete corpus
then disproved:

1. the low 24 bits of a D1 32:8 pixel header were compared with the enclosing Tiger
   native-resource length; the exact field instead equals the embedded Orbis shader
   binary end (formula OrbShdr offset + sizeof(ShaderBinaryInfo), i.e. +28 bytes);
2. every 32:9 -> 1:9 pair was called VertexShader from subtype; exact OrbShdr type
   proves that family contains both VertexShader and DomainShader. Public GNM source
   proves DS_VS uses the same GnmVsShader serialized structure as VS_VS.

This tool is not a permissive repair pass. It accepts only a *complete* raw V2 recovery,
re-hashes every retained header and GCN program, revalidates every serialized join and
stage-specific header invariant, and requires every original violation to be one of the
now-explained obsolete checks. Any other discrepancy remains fatal.
"""
from __future__ import annotations

import argparse
import collections
import copy
import hashlib
import json
import re
import struct
import tempfile
from pathlib import Path

from d1_ps4_vs_ds_shader_header import parse_header as parse_vs_ds_header

RAW_SCHEMA = "d1_remote_ps4_shader_corpus_extract/v2"
OUT_SCHEMA = "d1_remote_ps4_shader_corpus_extract/v3"
OUT_STATUS = "D1_REMOTE_PS4_SHADER_CORPUS_EXACT_PS_VS_DS"
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
STAGE_MAP = {"PixelShader": "PS", "VertexShader": "VS", "DomainShader": "DS"}
FAMILY = {
    "PS": {"header": (32, 8), "native": (1, 8)},
    "VSD": {"header": (32, 9), "native": (1, 9)},
}


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def u32(b: bytes, off: int = 0) -> int:
    if off < 0 or off + 4 > len(b):
        raise ValueError((off, len(b)))
    return struct.unpack_from("<I", b, off)[0]


def _legacy_violation_allowed(v: str, actual_stage: str) -> bool:
    if ":ps_embedded_size:" in v:
        return actual_stage == "PixelShader"
    if v.endswith("orbshdr_stage:DomainShader!=VertexShader"):
        return actual_stage == "DomainShader"
    if v.endswith(":vs_wrapper_shader_size_mismatch"):
        return actual_stage == "DomainShader"
    if v.endswith(":vs_native_check:stage_is_vertex_shader"):
        return actual_stage == "DomainShader"
    return False


def reclassify(src: dict, header_dir: Path, program_dir: Path) -> dict:
    violations: list[str] = []
    if src.get("schema") != RAW_SCHEMA:
        raise ValueError(f"unsupported raw schema: {src.get('schema')!r}")

    hp = src.get("header_population") or {}
    nr = src.get("native_reference_population") or {}
    gp = src.get("gcn_program_population") or {}
    headers = src.get("headers") or []
    natives = src.get("native_programs") or []

    htotal = int(hp.get("total", -1))
    planned_refs = int(nr.get("planned_unique", -1))
    completeness = {
        "header_rows": (len(headers), htotal),
        "header_payloads": (int(hp.get("payload_recovered_count", -1)), htotal),
        "native_rows": (len(natives), planned_refs),
        "native_recovered_rows": (int(nr.get("recovered_rows", -1)), planned_refs),
        "native_payloads": (int(nr.get("payload_recovered_count", -1)), planned_refs),
        "native_gcn": (int(nr.get("gcn_code_recovered_count", -1)), planned_refs),
        "unique_gcn_rows": (
            len(src.get("unique_gcn_programs") or []),
            int(gp.get("unique_exact_code_sha256_count", -1)),
        ),
    }
    for name, (actual, expected) in completeness.items():
        if actual != expected:
            violations.append(f"incomplete:{name}:{actual}!={expected}")
    if int(hp.get("payload_unrecovered_count", -1)) != 0:
        violations.append(f"header_payload_unrecovered:{hp.get('payload_unrecovered_count')!r}")
    if nr.get("unrecovered_native_references"):
        violations.append(
            f"unrecovered_native_references:{len(nr['unrecovered_native_references'])}"
        )

    header_by_tag: dict[str, dict] = {}
    for i, h in enumerate(headers):
        tag = norm(h.get("header"))
        if tag in header_by_tag:
            violations.append(f"duplicate_header:{tag}")
        header_by_tag[tag] = h
        if h.get("violations"):
            violations.append(f"header_row_violations:{tag}:{len(h['violations'])}")

    canonical_headers: dict[str, dict] = {}
    canonical_natives: list[dict] = []
    stage_header_counts = collections.Counter()
    stage_native_counts = collections.Counter()
    explained_legacy: list[str] = []
    exact_join_count = 0

    for raw in natives:
        ref = norm(raw.get("native_program_reference"))
        bi = raw.get("binary_info") or {}
        actual_orb = str(bi.get("stage", ""))
        canonical_stage = STAGE_MAP.get(actual_orb)
        old_stages = sorted({str(x).upper() for x in (raw.get("stages") or [])})
        old_family = None
        if old_stages == ["PS"]:
            old_family = "PS"
        elif old_stages == ["VS"]:
            old_family = "VSD"
        else:
            violations.append(f"{ref}:raw_family_stages:{old_stages}")

        if canonical_stage is None:
            violations.append(f"{ref}:unsupported_orb_stage:{actual_orb!r}")
        elif old_family == "PS" and canonical_stage != "PS":
            violations.append(f"{ref}:32_8_stage:{actual_orb}")
        elif old_family == "VSD" and canonical_stage not in ("VS", "DS"):
            violations.append(f"{ref}:32_9_stage:{actual_orb}")

        meta = raw.get("retail_native_meta") or {}
        if old_family in FAMILY:
            want = FAMILY[old_family]["native"]
            got = (int(meta.get("type", -1)), int(meta.get("subtype", -1)))
            if got != want:
                violations.append(f"{ref}:native_type_subtype:{got}!={want}")

        loc = raw.get("orbshdr_locator") or {}
        footer = loc.get("formula_footer_offset")
        if not loc.get("formula_magic_matches") or not isinstance(footer, int):
            violations.append(f"{ref}:formula_orbshdr_not_exact")
        if int(bi.get("offset", -1)) != footer:
            violations.append(f"{ref}:binary_info_offset:{bi.get('offset')!r}!={footer!r}")
        embedded_shader_end = footer + 28 if isinstance(footer, int) else None
        payload_bytes = int((raw.get("native_payload") or {}).get("bytes", -1))
        if embedded_shader_end is not None and embedded_shader_end > payload_bytes:
            violations.append(
                f"{ref}:embedded_shader_end:{embedded_shader_end}>{payload_bytes}"
            )

        code = raw.get("gcn_code") or {}
        code_sha = str(code.get("sha256", "")).lower()
        code_bytes = int(code.get("bytes", -1))
        if not SHA_RE.fullmatch(code_sha) or code_bytes <= 0:
            violations.append(f"{ref}:invalid_gcn_identity:{code_bytes}:{code_sha!r}")
        else:
            pp = program_dir / f"{code_sha}.bin"
            if not pp.is_file():
                violations.append(f"{ref}:gcn_program_missing:{code_sha}")
            else:
                if pp.stat().st_size != code_bytes:
                    violations.append(
                        f"{ref}:gcn_program_size:{pp.stat().st_size}!={code_bytes}"
                    )
                got_sha = sha256_file(pp)
                if got_sha != code_sha:
                    violations.append(f"{ref}:gcn_program_sha:{got_sha}!={code_sha}")

        raw_legacy = [f"{ref}:{v}" for v in (raw.get("violations") or [])]
        for full in raw_legacy:
            if not _legacy_violation_allowed(full, actual_orb):
                violations.append(f"unexplained_legacy_violation:{full}")
            else:
                explained_legacy.append(full)

        canonical_uses = []
        users = raw.get("headers") or []
        if int(raw.get("header_count", -1)) != len(users):
            violations.append(f"{ref}:header_count:{raw.get('header_count')!r}!={len(users)}")
        for user in users:
            htag = norm(user.get("header"))
            h = header_by_tag.get(htag)
            if h is None:
                violations.append(f"{ref}:{htag}:header_row_missing")
                continue
            if norm(h.get("planned_native_program_reference")) != ref:
                violations.append(f"{ref}:{htag}:planned_reference_mismatch")
            if norm(h.get("retail_native_program_reference")) != ref:
                violations.append(f"{ref}:{htag}:retail_reference_mismatch")

            hmeta = h.get("retail_header_meta") or {}
            if old_family in FAMILY:
                want_h = FAMILY[old_family]["header"]
                got_h = (int(hmeta.get("type", -1)), int(hmeta.get("subtype", -1)))
                if got_h != want_h:
                    violations.append(f"{ref}:{htag}:header_type_subtype:{got_h}!={want_h}")

            old_stage = str(user.get("stage", "")).upper()
            hfile = header_dir / f"{old_stage}_{htag}.bin"
            if not hfile.is_file():
                violations.append(f"{ref}:{htag}:header_file_missing:{hfile.name}")
                continue
            hb = hfile.read_bytes()
            hd = h.get("header_payload") or {}
            if len(hb) != int(hd.get("bytes", -1)):
                violations.append(
                    f"{ref}:{htag}:header_bytes:{len(hb)}!={hd.get('bytes')!r}"
                )
            hsha = sha256_bytes(hb)
            if hsha != str(hd.get("sha256", "")).lower():
                violations.append(
                    f"{ref}:{htag}:header_sha:{hsha}!={hd.get('sha256')!r}"
                )

            decoded = None
            if canonical_stage == "PS":
                if len(hb) < 4:
                    violations.append(f"{ref}:{htag}:ps_header_short:{len(hb)}")
                else:
                    packed = u32(hb, 0)
                    declared = packed & 0x00FFFFFF
                    usage_count = (packed >> 24) & 0xFF
                    if declared != embedded_shader_end:
                        violations.append(
                            f"{ref}:{htag}:ps_embedded_shader_end:{declared}!={embedded_shader_end}"
                        )
                    if usage_count != int(bi.get("num_input_usage_slots", -1)):
                        violations.append(
                            f"{ref}:{htag}:ps_usage_count:{usage_count}!={bi.get('num_input_usage_slots')!r}"
                        )
                    decoded = {
                        "schema": "d1_ps4_pixel_shader_header_exact/v1",
                        "packed_word": f"{packed:08X}",
                        "embedded_shader_binary_size": declared,
                        "num_input_usage_slots": usage_count,
                        "checks": {
                            "embedded_size_matches_orbshdr_end": declared == embedded_shader_end,
                            "usage_count_matches_orbshdr": usage_count == int(bi.get("num_input_usage_slots", -1)),
                        },
                    }
            elif canonical_stage in ("VS", "DS"):
                orb_name = "VertexShader" if canonical_stage == "VS" else "DomainShader"
                try:
                    decoded = parse_vs_ds_header(hb, expected_stage=orb_name)
                    g = decoded["gnm_vs_shader"]
                    sc = decoded.get("stage_wrapper_check") or {}
                    if int(g["shader_size"]) != embedded_shader_end:
                        violations.append(
                            f"{ref}:{htag}:gnm_shader_size:{g['shader_size']}!={embedded_shader_end}"
                        )
                    if int(g["num_input_usage_slots"]) != int(bi.get("num_input_usage_slots", -1)):
                        violations.append(
                            f"{ref}:{htag}:gnm_usage_count:{g['num_input_usage_slots']}!={bi.get('num_input_usage_slots')!r}"
                        )
                    if not sc.get("exact"):
                        violations.append(f"{ref}:{htag}:d1_stage_wrapper_invariant")
                    if not decoded["checks"]["tables_in_bounds"]:
                        violations.append(f"{ref}:{htag}:gnm_tables_out_of_bounds")
                except Exception as exc:
                    violations.append(
                        f"{ref}:{htag}:vs_ds_header_parse:{type(exc).__name__}:{exc}"
                    )

            canonical_headers[htag] = {
                **copy.deepcopy(h),
                "stage": canonical_stage,
                "orb_stage": actual_orb,
                "family_stage_from_metadata": old_stage,
                "canonical_header_file": str(hfile),
                "decoded_stage_header": decoded,
                "violations": [],
            }
            canonical_uses.append({"stage": canonical_stage, "header": htag})
            if canonical_stage is not None:
                stage_header_counts[canonical_stage] += 1
            exact_join_count += 1

        nr_out = copy.deepcopy(raw)
        nr_out["family_stages_from_metadata"] = old_stages
        nr_out["stages"] = [] if canonical_stage is None else [canonical_stage]
        nr_out["orb_stage"] = actual_orb
        nr_out["headers"] = sorted(canonical_uses, key=lambda x: (x["stage"] or "", x["header"]))
        nr_out["legacy_v2_violations_explained"] = raw.get("violations") or []
        nr_out["violations"] = []
        canonical_natives.append(nr_out)
        if canonical_stage is not None:
            stage_native_counts[canonical_stage] += 1

    # Every top-level V2 violation must be exactly the prefixed union of row violations.
    source_violations = list(src.get("violations") or [])
    expected_source_violations = []
    for raw in natives:
        ref = norm(raw.get("native_program_reference"))
        expected_source_violations.extend(f"{ref}:{v}" for v in (raw.get("violations") or []))
    if source_violations != expected_source_violations:
        violations.append("raw_top_level_violation_ledger_mismatch")
    if collections.Counter(explained_legacy) != collections.Counter(source_violations):
        violations.append(
            f"legacy_violation_accounting:{len(explained_legacy)}!={len(source_violations)}"
        )

    # Rebuild exact GCN groups from corrected native/header stage identities.
    groups: dict[str, dict] = {}
    for n in canonical_natives:
        code = n.get("gcn_code") or {}
        sha = str(code.get("sha256", "")).lower()
        if not SHA_RE.fullmatch(sha):
            continue
        q = groups.setdefault(sha, {
            "gcn_sha256": sha,
            "gcn_bytes": int(code.get("bytes", -1)),
            "native_program_references": [],
            "headers": [],
            "stages": set(),
        })
        if q["gcn_bytes"] != int(code.get("bytes", -1)):
            violations.append(f"{sha}:gcn_length_disagreement")
        q["native_program_references"].append(n["native_program_reference"])
        q["headers"].extend(n.get("headers") or [])
        q["stages"].update(n.get("stages") or [])

    programs = []
    stage_programs: dict[str, set[str]] = collections.defaultdict(set)
    for sha, q in sorted(groups.items()):
        q["native_program_references"] = sorted(set(q["native_program_references"]))
        q["headers"] = sorted(q["headers"], key=lambda x: (x["stage"], x["header"]))
        q["stages"] = sorted(q["stages"])
        q["native_reference_count"] = len(q["native_program_references"])
        q["header_count"] = len(q["headers"])
        q["violations"] = []
        programs.append(q)
        for stage in q["stages"]:
            stage_programs[stage].add(sha)

    if len(programs) != int(gp.get("unique_exact_code_sha256_count", -1)):
        violations.append(
            f"unique_gcn_population:{len(programs)}!={gp.get('unique_exact_code_sha256_count')!r}"
        )
    if len(canonical_headers) != htotal:
        violations.append(f"canonical_header_population:{len(canonical_headers)}!={htotal}")
    if exact_join_count != htotal:
        violations.append(f"exact_join_count:{exact_join_count}!={htotal}")

    out = {
        "schema": OUT_SCHEMA,
        "status": OUT_STATUS if not violations else "D1_REMOTE_PS4_SHADER_CORPUS_V3_WITH_VIOLATIONS",
        "source_raw_schema": RAW_SCHEMA,
        "source_raw_status": src.get("status"),
        "source_plan": src.get("source_plan"),
        "reclassification": {
            "status": "D1_SHADER_CORPUS_FORMAT_RECLASSIFICATION_EXACT" if not violations else "WITH_VIOLATIONS",
            "pixel_header_embedded_size_boundary": "OrbShdr_formula_footer_offset_plus_28",
            "type_32_9_native_1_9_family": ["VertexShader", "DomainShader"],
            "domain_serialized_gnm_structure": "GnmVsShader / DS_VS",
            "legacy_v2_violation_count": len(source_violations),
            "legacy_v2_violations_exactly_explained": len(explained_legacy),
        },
        "header_population": {
            "total": htotal,
            "stage_counts": dict(sorted(stage_header_counts.items())),
            "payload_recovered_count": int(hp.get("payload_recovered_count", -1)),
            "payload_unrecovered_count": int(hp.get("payload_unrecovered_count", -1)),
        },
        "native_reference_population": {
            "planned_unique": planned_refs,
            "recovered_rows": int(nr.get("recovered_rows", -1)),
            "payload_recovered_count": int(nr.get("payload_recovered_count", -1)),
            "gcn_code_recovered_count": int(nr.get("gcn_code_recovered_count", -1)),
            "stage_counts": dict(sorted(stage_native_counts.items())),
            "violation_rows": 0 if not violations else None,
            "unrecovered_native_references": list(nr.get("unrecovered_native_references") or []),
        },
        "gcn_program_population": {
            "unique_exact_code_sha256_count": len(programs),
            "stage_unique_counts": {
                k: len(v) for k, v in sorted(stage_programs.items())
            },
            "shared_by_multiple_native_references": sum(
                int(x["native_reference_count"] > 1) for x in programs
            ),
            "shared_by_multiple_headers": sum(int(x["header_count"] > 1) for x in programs),
            "shared_by_multiple_stages": sum(int(len(x["stages"]) > 1) for x in programs),
        },
        "headers": [canonical_headers[k] for k in sorted(canonical_headers)],
        "native_programs": sorted(canonical_natives, key=lambda x: x["native_program_reference"]),
        "unique_gcn_programs": programs,
        "violations": violations,
        "proof": {
            "raw_recovery_complete": all(a == b for a, b in completeness.values()),
            "header_and_program_artifact_hashes_rechecked": True,
            "all_original_violations_accounted": collections.Counter(explained_legacy) == collections.Counter(source_violations),
            "pixel_embedded_size_rule": "all 32:8 headers must equal exact OrbShdr end, not enclosing Tiger resource length",
            "stage_identity_rule": "32:8 requires PixelShader; 32:9 accepts only exact OrbShdr VertexShader or DomainShader",
            "vs_ds_layout_rule": "both VS_VS and DS_VS require exact GnmVsShader common/table layout; D1 outer wrapper invariant remains stage-specific",
        },
        "policy": (
            "No original diagnostic is discarded by category alone. Promotion requires complete raw recovery, exact retained-file hashes, exact serialized references, exact OrbShdr framing, stage-family closure, stage-specific D1 header invariants, and one-for-one accounting of every legacy V2 violation."
        ),
    }
    return out


def self_test() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        hd = root / "headers"; pd = root / "programs"
        hd.mkdir(); pd.mkdir()
        # Minimal PS example: embedded shader end 0x40, enclosing resource 0x80.
        hb = struct.pack("<I", (2 << 24) | 0x40) + b"\x00" * 12
        hsha = sha256_bytes(hb)
        (hd / "PS_80000001.bin").write_bytes(hb)
        code = b"\x00" * 16
        csha = sha256_bytes(code)
        (pd / f"{csha}.bin").write_bytes(code)
        native = {
            "native_program_reference": "80000002", "header_count": 1,
            "headers": [{"stage": "PS", "header": "80000001"}], "stages": ["PS"],
            "violations": ["80000001:ps_embedded_size:64!=128"],
            "retail_native_meta": {"type": 1, "subtype": 8},
            "native_payload": {"bytes": 128, "sha256": "0" * 64},
            "orbshdr_locator": {"formula_footer_offset": 36, "formula_magic_matches": True},
            "binary_info": {"offset": 36, "stage": "PixelShader", "num_input_usage_slots": 2},
            "gcn_code": {"bytes": 16, "sha256": csha},
        }
        header = {
            "stage": "PS", "header": "80000001",
            "planned_native_program_reference": "80000002",
            "retail_native_program_reference": "80000002", "violations": [],
            "retail_header_meta": {"type": 32, "subtype": 8},
            "header_payload": {"bytes": len(hb), "sha256": hsha},
        }
        topv = ["80000002:80000001:ps_embedded_size:64!=128"]
        src = {
            "schema": RAW_SCHEMA, "status": "D1_REMOTE_PS4_SHADER_CORPUS_WITH_VIOLATIONS",
            "source_plan": "plan.json", "violations": topv,
            "header_population": {"total": 1, "payload_recovered_count": 1, "payload_unrecovered_count": 0},
            "native_reference_population": {"planned_unique": 1, "recovered_rows": 1, "payload_recovered_count": 1, "gcn_code_recovered_count": 1, "unrecovered_native_references": []},
            "gcn_program_population": {"unique_exact_code_sha256_count": 1},
            "headers": [header], "native_programs": [native], "unique_gcn_programs": [],
        }
        out = reclassify(src, hd, pd)
        assert out["status"] == OUT_STATUS, out["violations"]
        assert out["header_population"]["stage_counts"] == {"PS": 1}
        assert out["reclassification"]["legacy_v2_violations_exactly_explained"] == 1
        bad = copy.deepcopy(src)
        bad["native_programs"][0]["violations"].append("mystery_violation")
        bad["violations"].append("80000002:mystery_violation")
        out_bad = reclassify(bad, hd, pd)
        assert out_bad["status"] != OUT_STATUS
        assert any("unexplained_legacy_violation" in x for x in out_bad["violations"])
    print("D1_SHADER_CORPUS_V2_FORMAT_RECLASSIFY_SELF_TEST_OK")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("source", type=Path, nargs="?")
    ap.add_argument("--header-dir", type=Path)
    ap.add_argument("--program-dir", type=Path)
    ap.add_argument("-o", "--output", type=Path)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        self_test()
        return 0
    if a.source is None or a.header_dir is None or a.program_dir is None or a.output is None:
        ap.error("source, --header-dir, --program-dir and --output are required unless --self-test is used")
    out = reclassify(json.loads(a.source.read_text()), a.header_dir, a.program_dir)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n")
    print(
        "STATUS", out["status"],
        "HEADERS", out["header_population"],
        "NATIVES", out["native_reference_population"],
        "GCN", out["gcn_program_population"],
        "LEGACY_EXPLAINED", out["reclassification"]["legacy_v2_violations_exactly_explained"],
        "VIOLATIONS", len(out["violations"]),
    )
    for v in out["violations"][:200]:
        print("VIOLATION", v)
    return 0 if out["status"] == OUT_STATUS else 2


if __name__ == "__main__":
    raise SystemExit(main())
