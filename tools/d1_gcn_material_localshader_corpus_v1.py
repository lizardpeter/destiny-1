#!/usr/bin/env python3
"""Recover the exact material-referenced Destiny 1 PS4 LocalShader corpus.

Input is the frozen complementary reference merge. Only wrappers already proven as
32:11 -> 1:11 OrbShdr LocalShader are admitted. Full retail wrapper/native payloads are
re-read, byte hashes are checked against the frozen proof, exact GCN code is recovered,
and identical code blobs are deduplicated without losing wrapper/native/material provenance.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import multiprocessing as mp
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from d1_gcn_material_shader_reference_probe_v1 import exact_entry, orbshdr_shape
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_split_tar_extract import SplitHttpTar

INPUT_SCHEMA = "d1_gcn_material_shader_reference_probe_merged/v1"
INPUT_STATUS = "D1_GCN_MATERIAL_SHADER_REFERENCE_PROBE_MERGED_EXACT"
SHADER_SCHEMA = "d1_remote_ps4_shader_corpus_extract/v3"
SHADER_STATUS = "D1_REMOTE_PS4_SHADER_CORPUS_EXACT_PS_VS_DS"
SCHEMA = "d1_gcn_material_localshader_corpus/v1"
STATUS = "D1_GCN_MATERIAL_LOCALSHADER_CORPUS_EXACT"
_WORKER_CORPUS: RemoteCorpus | None = None


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def is_exact_local(row: dict) -> bool:
    te = row.get("target_entry") or {}
    re = row.get("reference_target_entry") or {}
    orb = row.get("reference_target_orbshdr_shape") or {}
    bi = orb.get("binary_info") or {}
    return (
        te.get("type") == 32
        and te.get("subtype") == 11
        and re.get("type") == 1
        and re.get("subtype") == 11
        and orb.get("code_bounds_valid") is True
        and bi.get("stage") == "LocalShader"
        and bi.get("stage_value") == 3
        and bool(orb.get("code_sha256"))
    )


def _worker_init(catalog_paths: list[str], base_url: str, part_count: int, runtime: str) -> None:
    global _WORKER_CORPUS
    catalogs = load_catalogs([Path(x) for x in catalog_paths])
    base = base_url.rstrip("/")
    arc = SplitHttpTar(
        [f"{base}/packages.tar.{i:03d}" for i in range(1, part_count + 1)],
        retries=8,
        timeout=120,
    )
    _WORKER_CORPUS = RemoteCorpus(arc, catalogs, Path(runtime))


def retry_exact_entry(c: RemoteCorpus, tag: str, attempts: int = 4) -> tuple[dict, bytes]:
    last = None
    for attempt in range(1, attempts + 1):
        try:
            return exact_entry(c, tag)
        except TimeoutError as ex:
            last = ex
            print(f"TIMEOUT_RETRY {tag} {attempt}/{attempts}", flush=True)
    raise TimeoutError(f"{tag}: exhausted {attempts} exact-entry retries: {last}")


def _recover(source: dict) -> dict:
    if _WORKER_CORPUS is None:
        raise RuntimeError("worker corpus not initialized")
    c = _WORKER_CORPUS
    wrapper = str(source["target"]).upper()
    native = str(source["target_entry"]["reference"]).upper()
    out = {"wrapper": wrapper, "native_program_reference": native, "violations": []}
    try:
        wmeta, wpayload = retry_exact_entry(c, wrapper)
        nmeta, npayload = retry_exact_entry(c, native)
        if wmeta != source["target_entry"]:
            out["violations"].append("wrapper_entry_metadata_changed")
        if nmeta != source["reference_target_entry"]:
            out["violations"].append("native_entry_metadata_changed")
        if sha256_bytes(wpayload) != source["target_payload"]["sha256"]:
            out["violations"].append("wrapper_payload_sha256_changed")
        if sha256_bytes(npayload) != source["reference_target_payload"]["sha256"]:
            out["violations"].append("native_payload_sha256_changed")
        shape = orbshdr_shape(npayload)
        if shape != source["reference_target_orbshdr_shape"]:
            out["violations"].append("native_orbshdr_shape_changed")
        bi = shape.get("binary_info") or {}
        if not shape.get("code_bounds_valid") or bi.get("stage") != "LocalShader" or bi.get("stage_value") != 3:
            out["violations"].append(f"native_stage_not_localshader:{bi.get('stage')}:{bi.get('stage_value')}")
        code_len = int(shape.get("code_length_bytes") or 0)
        code = npayload[:code_len]
        code_sha = sha256_bytes(code)
        if code_sha != source["reference_target_orbshdr_shape"]["code_sha256"]:
            out["violations"].append("gcn_sha256_changed")
        out.update({
            "wrapper_entry": wmeta,
            "wrapper_payload_sha256": sha256_bytes(wpayload),
            "wrapper_payload": wpayload,
            "native_entry": nmeta,
            "native_payload_sha256": sha256_bytes(npayload),
            "native_payload": npayload,
            "orbshdr": shape,
            "gcn_sha256": code_sha,
            "gcn_bytes": len(code),
            "gcn_code": code,
            "material_occurrence_count": int(source["occurrence_count"]),
            "material_reference_roles": source["material_reference_roles"],
        })
    except Exception as ex:
        out["violations"].append(f"recovery:{type(ex).__name__}:{ex}")
    return out


def existing_gcn_set(path: Path | None) -> set[str]:
    if path is None:
        return set()
    d = json.loads(path.read_text())
    if d.get("schema") != SHADER_SCHEMA or d.get("status") != SHADER_STATUS or d.get("violations"):
        raise ValueError(f"existing shader corpus not exact:{d.get('schema')}:{d.get('status')}")
    if len(d.get("unique_gcn_programs") or []) != 26464:
        raise ValueError("existing shader corpus denominator changed")
    return {str(x["gcn_sha256"]).lower() for x in d["unique_gcn_programs"]}


def build(reference_path: Path, shader_path: Path | None, catalog_paths: list[Path], base_url: str,
          part_count: int, runtime: Path, workers: int, binary_dir: Path) -> dict:
    src = json.loads(reference_path.read_text())
    if src.get("schema") != INPUT_SCHEMA or src.get("status") != INPUT_STATUS or src.get("violations"):
        raise ValueError(f"reference merge not exact:{src.get('schema')}:{src.get('status')}")
    selected = [r for r in (src.get("targets") or []) if is_exact_local(r)]
    if len(selected) != 177 or sum(int(r["occurrence_count"]) for r in selected) != 3967:
        raise ValueError(f"LocalShader denominator changed:{len(selected)}:{sum(int(r['occurrence_count']) for r in selected)}")

    initargs = ([str(x) for x in catalog_paths], base_url, part_count, str(runtime))
    worker_count = max(1, int(workers))
    if worker_count == 1:
        _worker_init(*initargs)
        iterator = map(_recover, selected)
        pool = None
    else:
        pool = mp.Pool(processes=worker_count, initializer=_worker_init, initargs=initargs)
        iterator = pool.imap_unordered(_recover, selected, chunksize=1)
    recovered = []
    try:
        for n, row in enumerate(iterator, 1):
            recovered.append(row)
            if n % 20 == 0 or n == len(selected):
                print(f"LOCALSHADER_RECOVERED {n}/{len(selected)}", flush=True)
    finally:
        if pool is not None:
            pool.close(); pool.join()
    recovered.sort(key=lambda x: x["wrapper"])

    violations = [f"{r['wrapper']}:{v}" for r in recovered for v in r["violations"]]
    code_by_sha: dict[str, bytes] = {}
    program_members: dict[str, list[dict]] = collections.defaultdict(list)
    native_refs = set()
    material_occurrences = 0
    usage_counts = collections.Counter()
    for row in recovered:
        if row["violations"]:
            continue
        sha = row["gcn_sha256"]
        code = row["gcn_code"]
        old = code_by_sha.get(sha)
        if old is not None and old != code:
            violations.append(f"gcn_sha_collision:{sha}")
        else:
            code_by_sha[sha] = code
        native_refs.add(row["native_program_reference"])
        material_occurrences += row["material_occurrence_count"]
        usage_counts[int(row["orbshdr"]["binary_info"]["num_input_usage_slots"])] += 1
        program_members[sha].append({
            "wrapper": row["wrapper"],
            "native_program_reference": row["native_program_reference"],
            "material_occurrence_count": row["material_occurrence_count"],
        })

    existing = existing_gcn_set(shader_path)
    overlap = sorted(existing.intersection(code_by_sha))
    if overlap:
        violations.append(f"localshader_gcn_overlaps_existing_stage_corpus:{len(overlap)}")

    binary_dir.mkdir(parents=True, exist_ok=True)
    (binary_dir / "headers").mkdir(exist_ok=True)
    (binary_dir / "native").mkdir(exist_ok=True)
    (binary_dir / "gcn").mkdir(exist_ok=True)
    headers = []
    for row in recovered:
        if row["violations"]:
            continue
        wrapper_path = f"headers/LS_{row['wrapper']}.bin"
        native_path = f"native/LS_{row['native_program_reference']}.bin"
        (binary_dir / wrapper_path).write_bytes(row["wrapper_payload"])
        (binary_dir / native_path).write_bytes(row["native_payload"])
        headers.append({
            "stage": "LS",
            "orb_stage": "LocalShader",
            "wrapper": row["wrapper"],
            "native_program_reference": row["native_program_reference"],
            "package_id": row["wrapper_entry"]["package_id"],
            "logical_view": row["wrapper_entry"]["logical_view"],
            "wrapper_entry": row["wrapper_entry"],
            "native_entry": row["native_entry"],
            "wrapper_payload_sha256": row["wrapper_payload_sha256"],
            "native_payload_sha256": row["native_payload_sha256"],
            "gcn_sha256": row["gcn_sha256"],
            "gcn_bytes": row["gcn_bytes"],
            "material_occurrence_count": row["material_occurrence_count"],
            "wrapper_file": wrapper_path,
            "native_file": native_path,
        })
    programs = []
    for sha in sorted(code_by_sha):
        code = code_by_sha[sha]
        path = f"gcn/{sha}.bin"
        (binary_dir / path).write_bytes(code)
        members = sorted(program_members[sha], key=lambda x: (x["wrapper"], x["native_program_reference"]))
        programs.append({
            "gcn_sha256": sha,
            "gcn_bytes": len(code),
            "stage": "LS",
            "orb_stage": "LocalShader",
            "wrapper_count": len(members),
            "native_reference_count": len({x["native_program_reference"] for x in members}),
            "material_occurrence_count": sum(x["material_occurrence_count"] for x in members),
            "members": members,
            "gcn_file": path,
        })

    coverage = {
        "localshader_wrapper_count": len(headers),
        "localshader_native_reference_count": len(native_refs),
        "unique_localshader_gcn_program_count": len(programs),
        "material_occurrence_count": material_occurrences,
        "input_usage_slot_count_histogram": {str(k): v for k, v in sorted(usage_counts.items())},
        "existing_ps_vs_ds_unique_gcn_program_count": len(existing) if shader_path else None,
        "localshader_gcn_overlap_with_existing_ps_vs_ds": len(overlap),
        "combined_known_unique_gcn_program_count": len(existing) + len(programs) if shader_path else None,
        "combined_known_shader_wrapper_count": 37892 + len(headers) if shader_path else None,
        "shader_expression_semantic_promotions": 0,
    }
    if len(headers) != 177: violations.append(f"wrapper_accounting:{len(headers)}!=177")
    if len(native_refs) != 177: violations.append(f"native_reference_accounting:{len(native_refs)}!=177")
    if len(programs) != 65: violations.append(f"unique_gcn_accounting:{len(programs)}!=65")
    if material_occurrences != 3967: violations.append(f"material_occurrence_accounting:{material_occurrences}!=3967")

    return {
        "schema": SCHEMA,
        "status": STATUS if not violations else "D1_GCN_MATERIAL_LOCALSHADER_CORPUS_WITH_VIOLATIONS",
        "coverage": coverage,
        "headers": headers,
        "unique_gcn_programs": programs,
        "violations": violations,
        "semantic_boundary": {
            "wrapper_stage": "GLOBAL_EXACT_FOR_MATERIAL_REFERENCED_32_11_POPULATION",
            "gcn_code_identity": "EXACT",
            "localshader_as_vertexshader": "FORBIDDEN",
            "localshader_to_hullshader_ownership": "WITHHELD",
            "domainshader_pipeline_ownership": "WITHHELD",
            "shader_expression_semantics": "WITHHELD",
        },
        "policy": "Only exact 32:11 -> 1:11 OrbShdr LocalShader wrappers from the frozen material-reference proof are admitted. Every re-read wrapper/native payload must hash-identically to that proof. GCN binaries are deduplicated only by exact SHA-256 while all wrapper/native/material provenance is retained.",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reference-probe", type=Path, required=True)
    ap.add_argument("--existing-shader-corpus", type=Path)
    ap.add_argument("--member-catalog", type=Path, action="append", required=True)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--part-count", type=int, default=10)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--binary-dir", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()
    out = build(a.reference_probe, a.existing_shader_corpus, a.member_catalog, a.base_url,
                a.part_count, a.runtime, a.workers, a.binary_dir)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": out["status"], "coverage": out["coverage"], "violations": out["violations"][:50]}, indent=2, sort_keys=True))
    return 0 if not out["violations"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
