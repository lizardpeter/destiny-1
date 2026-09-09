#!/usr/bin/env python3
"""Revalidate the full D1 PS4 shader corpus against corrected wrapper semantics.

This consumes the immutable global shader-extraction JSON plus its exact-binary
tar. It does not recover packages and it does not weaken parsing. Instead it
rechecks the two wrapper assumptions that caused the legacy diagnostic artifact
to fail:

* Pixel wrapper dword 0 low16 is the embedded OrbShdr extent, not necessarily
  the complete package-entry size.
* Type/subtype 32:9 is a shader wrapper family, not universally a VertexShader
  declaration. The resolved native OrbShdr stage is authoritative.

All exact header/code hashes are re-read from the tar and all legacy violations
must be explained by one of those two corrected structural rules. Unknown
stages, unknown violations, or any accounting/hash/size mismatch fail closed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import tarfile
from collections import Counter
from pathlib import Path
from typing import Any

SCHEMA_IN = "d1_remote_ps4_shader_corpus_extract/v2"
SCHEMA_OUT = "d1_shader_corpus_format_revalidation/v1"
STATUS = "D1_SHADER_CORPUS_FORMAT_REVALIDATED"

PS_VIOLATION_RE = re.compile(
    r"^(?P<program>[0-9A-F]{8}):(?P<header>[0-9A-F]{8}):"
    r"ps_embedded_size:(?P<embedded>\d+)!=(?P<payload>\d+)$"
)
ORB_STAGE_RE = re.compile(
    r"^(?P<program>[0-9A-F]{8}):orbshdr_stage:DomainShader!=VertexShader$"
)
VS_SIZE_RE = re.compile(
    r"^(?P<program>[0-9A-F]{8}):(?P<header>[0-9A-F]{8}):"
    r"vs_wrapper_shader_size_mismatch$"
)
VS_STAGE_RE = re.compile(
    r"^(?P<program>[0-9A-F]{8}):(?P<header>[0-9A-F]{8}):"
    r"vs_native_check:stage_is_vertex_shader$"
)


def die(message: str) -> "NoReturn":
    raise SystemExit(f"ERROR: {message}")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_u32(data: bytes, off: int) -> int:
    if off < 0 or off + 4 > len(data):
        die(f"u32 read out of bounds: off={off} size={len(data)}")
    return struct.unpack_from("<I", data, off)[0]


def canonical_json(obj: Any) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode()


def member_bytes(
    tf: tarfile.TarFile, members: dict[str, tarfile.TarInfo], name: str
) -> bytes:
    member = members.get(name)
    if member is None:
        die(f"missing exact-binary member: {name}")
    if not member.isfile():
        die(f"exact-binary member is not a file: {name}")
    f = tf.extractfile(member)
    if f is None:
        die(f"could not read exact-binary member: {name}")
    return f.read()


def classify_legacy_violation(v: str) -> str:
    if PS_VIOLATION_RE.fullmatch(v):
        return "pixel_embedded_extent_vs_entry_size"
    if ORB_STAGE_RE.fullmatch(v):
        return "subtype9_native_domain_stage"
    if VS_SIZE_RE.fullmatch(v):
        return "subtype9_vertex_size_assumption"
    if VS_STAGE_RE.fullmatch(v):
        return "subtype9_vertex_stage_assumption"
    die(f"unrecognized legacy violation: {v}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--extract", required=True, type=Path)
    ap.add_argument("--binaries", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    extract_path = args.extract.resolve()
    binaries_path = args.binaries.resolve()
    if not extract_path.is_file():
        die(f"missing extract JSON: {extract_path}")
    if not binaries_path.is_file():
        die(f"missing exact-binaries tar: {binaries_path}")

    doc = json.loads(extract_path.read_text(encoding="utf-8"))
    if doc.get("schema") != SCHEMA_IN:
        die(f"unexpected input schema: {doc.get('schema')!r}")
    headers = doc.get("headers")
    native_programs = doc.get("native_programs")
    violations = doc.get("violations")
    if not isinstance(headers, list) or not isinstance(native_programs, list) or not isinstance(violations, list):
        die("extract JSON lacks headers/native_programs/violations arrays")

    headers_by_tag: dict[str, dict[str, Any]] = {}
    for h in headers:
        tag = h.get("header")
        if not isinstance(tag, str) or not re.fullmatch(r"[0-9A-F]{8}", tag):
            die(f"invalid header tag: {tag!r}")
        if tag in headers_by_tag:
            die(f"duplicate header row: {tag}")
        headers_by_tag[tag] = h

    native_by_ref: dict[str, dict[str, Any]] = {}
    for n in native_programs:
        ref = n.get("native_program_reference")
        if not isinstance(ref, str) or not re.fullmatch(r"[0-9A-F]{8}", ref):
            die(f"invalid native-program reference: {ref!r}")
        if ref in native_by_ref:
            die(f"duplicate native-program row: {ref}")
        native_by_ref[ref] = n

    legacy_classes = Counter(classify_legacy_violation(v) for v in violations)

    header_stage_counts: Counter[str] = Counter()
    native_stage_counts: Counter[str] = Counter()
    pixel_trailing_bytes: Counter[int] = Counter()
    vertex_trailing_bytes: Counter[int] = Counter()
    domain_trailing_bytes: Counter[int] = Counter()
    exact_code_shas: set[str] = set()
    exact_code_sha_stages: dict[str, set[str]] = {}
    ref_count = 0

    with tarfile.open(binaries_path, "r") as tf:
        members = {m.name: m for m in tf.getmembers()}
        code_verified: set[str] = set()
        for n in native_programs:
            ref = n["native_program_reference"]
            binfo = n.get("binary_info")
            payload = n.get("native_payload")
            gcn = n.get("gcn_code")
            gcn_file = n.get("gcn_program_file")
            refs = n.get("headers")
            if not isinstance(binfo, dict) or not isinstance(payload, dict) or not isinstance(gcn, dict):
                die(f"{ref}: incomplete native metadata")
            if not isinstance(refs, list) or not refs:
                die(f"{ref}: no header references")

            native_stage = binfo.get("stage")
            if native_stage not in {"PixelShader", "VertexShader", "DomainShader"}:
                die(f"{ref}: unrecognized native OrbShdr stage {native_stage!r}")
            native_stage_counts[native_stage] += 1

            orb_offset = binfo.get("offset")
            if not isinstance(orb_offset, int) or orb_offset < 0:
                die(f"{ref}: invalid OrbShdr offset")
            orb_end = orb_offset + 28
            payload_bytes = payload.get("bytes")
            if not isinstance(payload_bytes, int) or payload_bytes < orb_end:
                die(f"{ref}: package-entry size precedes OrbShdr end")
            trailing = payload_bytes - orb_end

            code_sha = gcn.get("sha256")
            code_bytes = gcn.get("bytes")
            if not isinstance(code_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", code_sha):
                die(f"{ref}: invalid GCN SHA")
            if not isinstance(code_bytes, int) or code_bytes <= 0:
                die(f"{ref}: invalid GCN byte count")
            if not isinstance(gcn_file, str):
                die(f"{ref}: missing GCN program file")
            if code_sha not in code_verified:
                raw_code = member_bytes(tf, members, gcn_file)
                if len(raw_code) != code_bytes:
                    die(f"{ref}: GCN byte-count mismatch")
                if sha256(raw_code) != code_sha:
                    die(f"{ref}: GCN SHA mismatch")
                code_verified.add(code_sha)
            if binfo.get("code_length_bytes") != code_bytes:
                die(f"{ref}: OrbShdr code length != exact GCN byte count")
            exact_code_shas.add(code_sha)
            exact_code_sha_stages.setdefault(code_sha, set()).add(native_stage)

            for href in refs:
                stage_alias = href.get("stage")
                tag = href.get("header")
                if stage_alias not in {"PS", "VS"} or tag not in headers_by_tag:
                    die(f"{ref}: malformed header reference {href!r}")
                h = headers_by_tag[tag]
                if h.get("retail_native_program_reference") != ref:
                    die(f"{ref}/{tag}: retail native reference disagreement")
                hfile = h.get("header_file")
                hpayload = h.get("header_payload")
                if not isinstance(hfile, str) or not isinstance(hpayload, dict):
                    die(f"{ref}/{tag}: missing exact header metadata")
                raw_header = member_bytes(tf, members, hfile)
                if len(raw_header) != hpayload.get("bytes"):
                    die(f"{ref}/{tag}: header byte-count mismatch")
                if sha256(raw_header) != hpayload.get("sha256"):
                    die(f"{ref}/{tag}: header SHA mismatch")
                ref_count += 1
                header_stage_counts[stage_alias] += 1

                if stage_alias == "PS":
                    if native_stage != "PixelShader":
                        die(f"{ref}/{tag}: PS wrapper resolved to {native_stage}")
                    embedded_extent = read_u32(raw_header, 0x00) & 0xFFFF
                    if embedded_extent != orb_end:
                        die(f"{ref}/{tag}: PS embedded extent {embedded_extent} != OrbShdr end {orb_end}")
                    pixel_trailing_bytes[trailing] += 1
                else:
                    if len(raw_header) < 0x18:
                        die(f"{ref}/{tag}: subtype-9 wrapper shorter than 0x18")
                    common_extent = read_u32(raw_header, 0x14) & 0xFFFF
                    if common_extent != orb_end:
                        die(f"{ref}/{tag}: subtype-9 common extent {common_extent} != OrbShdr end {orb_end}")
                    if native_stage == "VertexShader":
                        duplicated_extent = read_u32(raw_header, 0x04)
                        if duplicated_extent != orb_end:
                            die(f"{ref}/{tag}: vertex duplicated extent {duplicated_extent} != OrbShdr end {orb_end}")
                        vertex_trailing_bytes[trailing] += 1
                    elif native_stage == "DomainShader":
                        if read_u32(raw_header, 0x00) != 0 or read_u32(raw_header, 0x04) != 0:
                            die(f"{ref}/{tag}: DomainShader subtype-9 prefix is not zero/zero")
                        if trailing != 0:
                            die(f"{ref}/{tag}: DomainShader has unexpected {trailing} trailing bytes")
                        domain_trailing_bytes[trailing] += 1
                    else:
                        die(f"{ref}/{tag}: subtype-9 wrapper resolved to unsupported {native_stage}")

    if ref_count != len(headers):
        die(f"reference accounting mismatch: {ref_count} != {len(headers)}")

    expected_legacy = {
        "pixel_embedded_extent_vs_entry_size": sum(
            count for size, count in pixel_trailing_bytes.items() if size != 0
        ),
        "subtype9_native_domain_stage": native_stage_counts["DomainShader"],
        "subtype9_vertex_size_assumption": native_stage_counts["DomainShader"],
        "subtype9_vertex_stage_assumption": native_stage_counts["DomainShader"],
    }
    if dict(legacy_classes) != expected_legacy:
        die(f"legacy-violation accounting mismatch: observed={dict(legacy_classes)} expected={expected_legacy}")

    cross_stage_code_shas = {
        code_sha: sorted(stages)
        for code_sha, stages in exact_code_sha_stages.items()
        if len(stages) != 1
    }
    if cross_stage_code_shas:
        die(f"exact GCN binary SHA appears under multiple native stages: {cross_stage_code_shas}")

    vertex_reference_count = sum(
        1
        for n in native_programs
        for h in n["headers"]
        if h["stage"] == "VS" and n["binary_info"]["stage"] == "VertexShader"
    )

    out = {
        "schema": SCHEMA_OUT,
        "status": STATUS,
        "inputs": {
            "extract_json_sha256": sha256(extract_path.read_bytes()),
            "exact_binaries_tar_sha256": sha256(binaries_path.read_bytes()),
        },
        "accounting": {
            "header_reference_count": ref_count,
            "native_program_count": len(native_programs),
            "unique_exact_gcn_sha256_count": len(exact_code_shas),
            "legacy_violation_count": len(violations),
            "legacy_violation_classes": dict(sorted(legacy_classes.items())),
            "all_legacy_violations_structurally_resolved": True,
        },
        "native_stage_counts": dict(sorted(native_stage_counts.items())),
        "wrapper_reference_counts": dict(sorted(header_stage_counts.items())),
        "corrected_rules": {
            "pixel_wrapper": {
                "embedded_extent_field": "u32@0x00 & 0xFFFF",
                "required_relation": "embedded_extent == OrbShdr_offset + 28",
                "references_validated": header_stage_counts["PS"],
                "package_entry_trailing_bytes_distribution": {
                    str(k): v for k, v in sorted(pixel_trailing_bytes.items())
                },
            },
            "subtype9_wrapper": {
                "common_extent_field": "u32@0x14 & 0xFFFF",
                "required_relation": "common_extent == OrbShdr_offset + 28",
                "references_validated": header_stage_counts["VS"],
                "stage_authority": "native OrbShdr stage",
                "vertex_shader": {
                    "reference_count": vertex_reference_count,
                    "additional_relation": "u32@0x04 == OrbShdr_offset + 28",
                    "package_entry_trailing_bytes_distribution": {
                        str(k): v for k, v in sorted(vertex_trailing_bytes.items())
                    },
                },
                "domain_shader": {
                    "reference_count": sum(domain_trailing_bytes.values()),
                    "additional_relations": [
                        "u32@0x00 == 0",
                        "u32@0x04 == 0",
                        "package_entry_size == OrbShdr_offset + 28",
                    ],
                    "package_entry_trailing_bytes_distribution": {
                        str(k): v for k, v in sorted(domain_trailing_bytes.items())
                    },
                },
            },
        },
        "semantic_boundary": {
            "closed": [
                "legacy PS embedded-size comparison was against wrong extent",
                "type/subtype 32:9 is not universally VertexShader",
                "native OrbShdr stage discriminates VertexShader vs DomainShader",
            ],
            "not_claimed": [
                "semantic meaning of bytes trailing the embedded OrbShdr extent",
                "portable material intent",
                "game-wide GCN instruction semantic closure",
            ],
        },
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(canonical_json(out))
    print(json.dumps(out["accounting"], indent=2))
    print(json.dumps(out["native_stage_counts"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
