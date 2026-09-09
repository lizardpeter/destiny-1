#!/usr/bin/env python3
"""Exact retail PS4 Material -> VS/PS shader-owner frontier for Destiny 1.

The universal package-member catalog used by the global shader corpus is the sole package
universe. Each current logical package view is opened exactly once per worker, its complete
entry table is counted, every PS4 Material (reference 80801AD7) is selected directly from
that table, and its exact payload is parsed for the serialized VS/PS FileHashes.

The global entry/material counts are pinned to the already-green everything-index metadata
boundary. Only material ownership is promoted here; PARAM->ATTR linkage, varying names,
tessellation ownership and shader-expression meaning remain withheld.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import multiprocessing as mp
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from d1_material_decode import PS4_MATERIAL_CLASS, parse_material
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_split_tar_extract import SplitHttpTar

SCHEMA = "d1_gcn_material_shader_owner_frontier/v1"
STATUS = "D1_GCN_MATERIAL_SHADER_OWNER_FRONTIER_EXACT"
EXTRACT_SCHEMA = "d1_remote_ps4_shader_corpus_extract/v3"
EXTRACT_STATUS = "D1_REMOTE_PS4_SHADER_CORPUS_EXACT_PS_VS_DS"
NULLS = {"00000000", "FFFFFFFF"}
EXPECTED_PACKAGE_FAMILIES = 337
EXPECTED_CURRENT_ENTRY_COUNT = 1_437_333
EXPECTED_CURRENT_MATERIAL_COUNT = 230_706
DENOMINATOR_EVIDENCE_ARTIFACT_ID = 10086369300
DENOMINATOR_EVERYTHING_REPORT_SHA256 = "3d7f6ebd978147fc6a920a780a58e34102c826b250c55452e27f84099b9ab56e"
_WORKER_CORPUS = None


def norm(x: object) -> str:
    return str(x).upper().removeprefix("0X").zfill(8)


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def shader_header_index(src: dict) -> dict[str, dict]:
    if src.get("schema") != EXTRACT_SCHEMA or src.get("status") != EXTRACT_STATUS:
        raise ValueError(f"shader corpus identity mismatch:{src.get('schema')}:{src.get('status')}")
    if src.get("violations"):
        raise ValueError(f"shader corpus has {len(src['violations'])} violations")
    out: dict[str, dict] = {}
    for p in src.get("unique_gcn_programs") or []:
        sha = str(p["gcn_sha256"]).lower()
        stages = list(p.get("stages") or [])
        if len(stages) != 1:
            raise ValueError(f"exact GCN program has non-single stage:{sha}:{stages}")
        stage = stages[0]
        refs = sorted(str(x).upper() for x in (p.get("native_program_references") or []))
        for h in p.get("headers") or []:
            tag = norm(h["header"])
            hs = h.get("stage")
            rec = {"header": tag, "stage": stage, "gcn_sha256": sha, "native_program_references": refs}
            if hs != stage:
                raise ValueError(f"header/program stage mismatch:{tag}:{hs}:{stage}")
            old = out.get(tag)
            if old is not None and old != rec:
                raise ValueError(f"shader header maps ambiguously:{tag}:{old}:{rec}")
            out[tag] = rec
    if len(out) != 37_892:
        raise ValueError(f"shader header denominator:{len(out)}!=37892")
    return out


def _worker_init(catalog_paths: list[str], base_url: str, part_count: int, runtime: str) -> None:
    global _WORKER_CORPUS
    catalogs = load_catalogs([Path(x) for x in catalog_paths])
    arc = SplitHttpTar(
        [f"{base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1, part_count + 1)],
        retries=6, timeout=90,
    )
    _WORKER_CORPUS = RemoteCorpus(arc, catalogs, Path(runtime))


def _recover_package(package_id: str) -> dict:
    assert _WORKER_CORPUS is not None
    pkg = int(package_id, 16)
    errors = []
    recovered = []
    try:
        view = _WORKER_CORPUS.view(pkg)
    except Exception as ex:
        return {
            "package_id": package_id, "logical_view": None, "entry_count": 0,
            "material_count": 0, "recovered": [],
            "errors": [f"package_view:{package_id}:{type(ex).__name__}:{ex}"],
        }
    if int(view.h["pkg_id"]) != pkg:
        errors.append(f"package_identity:{package_id}:{int(view.h['pkg_id']):04X}")
    materials = [e for e in view.entries if norm(e.get("reference")) == PS4_MATERIAL_CLASS]
    for e in materials:
        tag = norm(e["tag_hash"])
        idx = int(e["index"])
        try:
            payload = view.entry(idx)
        except Exception as ex:
            errors.append(f"material_payload:{tag}:{type(ex).__name__}:{ex}")
            continue
        try:
            mat = parse_material(payload, "PS4")
        except Exception as ex:
            errors.append(f"material_parse:{tag}:{type(ex).__name__}:{ex}")
            continue
        recovered.append({
            "material": tag,
            "package_id": package_id,
            "logical_view": view.view.name,
            "package_patch_id": int(view.view.patch_id),
            "entry_index": idx,
            "file_size": int(e["file_size"]),
            "payload_sha256": sha256_bytes(payload),
            "material_declared_file_size": int(mat["declared_file_size"]),
            "material_actual_file_size": int(mat["actual_file_size"]),
            "vertex_shader_header": norm(mat["vertex_shader"]),
            "pixel_shader_header": norm(mat["pixel_shader"]),
        })
    return {
        "package_id": package_id,
        "logical_view": view.view.name,
        "entry_count": len(view.entries),
        "material_count": len(materials),
        "recovered": recovered,
        "errors": errors,
    }


def join_shader(header: str, expected_stage: str, headers: dict[str, dict], violations: list[str], material: str) -> dict | None:
    h = norm(header)
    if h in NULLS:
        return None
    rec = headers.get(h)
    if rec is None:
        violations.append(f"shader_header_absent:{material}:{expected_stage}:{h}")
        return None
    if rec["stage"] != expected_stage:
        violations.append(f"shader_stage_mismatch:{material}:{h}:{rec['stage']}!={expected_stage}")
        return None
    return rec


def build(catalog_paths: list[Path], base_url: str, part_count: int, runtime: Path,
          shader_corpus_path: Path, workers: int) -> dict:
    violations: list[str] = []
    src = json.loads(shader_corpus_path.read_text())
    try:
        headers = shader_header_index(src)
    except Exception as ex:
        raise SystemExit(f"shader corpus prerequisite failed:{type(ex).__name__}:{ex}")

    catalogs = load_catalogs(catalog_paths)
    package_ids = [f"{pkg:04X}" for pkg in sorted(catalogs)]
    if len(package_ids) != EXPECTED_PACKAGE_FAMILIES:
        violations.append(f"package_family_denominator:{len(package_ids)}!={EXPECTED_PACKAGE_FAMILIES}")

    recovered = []
    package_recovery = []
    initargs = ([str(x) for x in catalog_paths], base_url, part_count, str(runtime))
    if workers <= 1:
        _worker_init(*initargs)
        iterator = map(_recover_package, package_ids)
        pool = None
    else:
        pool = mp.Pool(processes=workers, initializer=_worker_init, initargs=initargs)
        iterator = pool.imap_unordered(_recover_package, package_ids, chunksize=1)
    total_entries = 0
    total_materials = 0
    try:
        done = 0
        for result in iterator:
            done += 1
            total_entries += int(result["entry_count"])
            total_materials += int(result["material_count"])
            violations.extend(result["errors"])
            recovered.extend(result["recovered"])
            package_recovery.append({
                "package_id": result["package_id"],
                "logical_view": result["logical_view"],
                "entry_count": result["entry_count"],
                "material_count": result["material_count"],
                "recovered_material_count": len(result["recovered"]),
                "error_count": len(result["errors"]),
            })
            if done % 20 == 0 or done == len(package_ids):
                print(
                    f"PACKAGES {done}/{len(package_ids)} ENTRIES {total_entries} "
                    f"MATERIALS {total_materials} RECOVERED {len(recovered)} violations={len(violations)}",
                    flush=True,
                )
    finally:
        if pool is not None:
            pool.close()
            pool.join()

    recovered.sort(key=lambda x: x["material"])
    package_recovery.sort(key=lambda x: x["package_id"])
    if total_entries != EXPECTED_CURRENT_ENTRY_COUNT:
        violations.append(f"current_entry_denominator:{total_entries}!={EXPECTED_CURRENT_ENTRY_COUNT}")
    if total_materials != EXPECTED_CURRENT_MATERIAL_COUNT:
        violations.append(f"material_denominator:{total_materials}!={EXPECTED_CURRENT_MATERIAL_COUNT}")
    if len(recovered) != total_materials:
        violations.append(f"material_accounting:{len(recovered)}!={total_materials}")
    tags = [x["material"] for x in recovered]
    if len(set(tags)) != len(tags):
        dup = [x for x, n in collections.Counter(tags).items() if n > 1]
        violations.append(f"duplicate_current_material_tags:{dup[:20]}")

    materials = []
    pair_members: dict[tuple[str, str], list[str]] = collections.defaultdict(list)
    pair_packages: dict[tuple[str, str], set[str]] = collections.defaultdict(set)
    null_patterns = collections.Counter()
    vs_headers = collections.Counter()
    ps_headers = collections.Counter()
    vs_gcn = collections.Counter()
    ps_gcn = collections.Counter()
    logical_views = collections.Counter()
    package_counts = collections.Counter()
    declared_actual_equal = 0

    for row in recovered:
        tag = row["material"]
        vsh, psh = row["vertex_shader_header"], row["pixel_shader_header"]
        vs = join_shader(vsh, "VS", headers, violations, tag)
        ps = join_shader(psh, "PS", headers, violations, tag)
        pattern = ("NULL" if vsh in NULLS else "VS") + "+" + ("NULL" if psh in NULLS else "PS")
        null_patterns[pattern] += 1
        if vs is not None:
            vs_headers[vsh] += 1
            vs_gcn[vs["gcn_sha256"]] += 1
        if ps is not None:
            ps_headers[psh] += 1
            ps_gcn[ps["gcn_sha256"]] += 1
        if vsh not in NULLS and psh not in NULLS and vs is not None and ps is not None:
            key = (vsh, psh)
            pair_members[key].append(tag)
            pair_packages[key].add(row["package_id"])
        logical_views[str(row["logical_view"])] += 1
        package_counts[row["package_id"]] += 1
        declared_actual_equal += int(row["material_declared_file_size"] == row["material_actual_file_size"])
        materials.append({**row, "owner_pattern": pattern})

    pairs = []
    for (vs, ps), members in sorted(pair_members.items()):
        pairs.append({
            "vertex_shader_header": vs,
            "pixel_shader_header": ps,
            "vertex_gcn_sha256": headers[vs]["gcn_sha256"],
            "pixel_gcn_sha256": headers[ps]["gcn_sha256"],
            "material_count": len(members),
            "materials": sorted(members),
            "package_ids": sorted(pair_packages[(vs, ps)]),
        })

    pair_materials = sum(len(x["materials"]) for x in pairs)
    coverage = {
        "package_family_count": len(package_ids),
        "current_entry_count": total_entries,
        "current_material_entry_count": total_materials,
        "material_package_count": sum(1 for x in package_recovery if x["material_count"]),
        "material_payload_recovered_count": len(recovered),
        "material_parse_success_count": len(recovered),
        "material_declared_size_equals_actual_count": declared_actual_equal,
        "material_owner_pattern_counts": dict(sorted(null_patterns.items())),
        "resolved_nonnull_vs_material_count": sum(vs_headers.values()),
        "resolved_nonnull_ps_material_count": sum(ps_headers.values()),
        "unique_vertex_shader_header_count": len(vs_headers),
        "unique_pixel_shader_header_count": len(ps_headers),
        "unique_vertex_gcn_program_count": len(vs_gcn),
        "unique_pixel_gcn_program_count": len(ps_gcn),
        "resolved_vs_ps_owner_pair_count": len(pairs),
        "materials_with_resolved_vs_ps_owner_pair": pair_materials,
        "logical_view_count": len(logical_views),
        "shader_corpus_header_count": len(headers),
        "material_header_vs_ps_pair_promotions": pair_materials,
        "param_index_to_attr_index_promotions": 0,
        "shader_expression_semantic_promotions": 0,
    }

    return {
        "schema": SCHEMA,
        "status": STATUS if not violations else "D1_GCN_MATERIAL_SHADER_OWNER_FRONTIER_WITH_VIOLATIONS",
        "source": {
            "material_class": PS4_MATERIAL_CLASS,
            "expected_package_family_count": EXPECTED_PACKAGE_FAMILIES,
            "expected_current_entry_count": EXPECTED_CURRENT_ENTRY_COUNT,
            "expected_current_material_count": EXPECTED_CURRENT_MATERIAL_COUNT,
            "denominator_evidence_artifact_id": DENOMINATOR_EVIDENCE_ARTIFACT_ID,
            "denominator_everything_report_sha256": DENOMINATOR_EVERYTHING_REPORT_SHA256,
            "shader_corpus_schema": src.get("schema"),
            "shader_corpus_status": src.get("status"),
            "base_url": base_url,
            "catalog_paths": [str(x) for x in catalog_paths],
            "worker_count": workers,
            "enumeration_strategy": "single current RemoteLogicalPackage entry-table pass per package family",
        },
        "coverage": coverage,
        "package_recovery": package_recovery,
        "material_owner_pattern_counts": dict(sorted(null_patterns.items())),
        "material_package_counts": dict(sorted(package_counts.items())),
        "logical_view_counts": dict(sorted(logical_views.items())),
        "vertex_shader_header_material_counts": dict(sorted(vs_headers.items())),
        "pixel_shader_header_material_counts": dict(sorted(ps_headers.items())),
        "owner_pairs": pairs,
        "materials": materials,
        "violations": violations,
        "semantic_boundary": {
            "material_to_vertex_shader_header": "GLOBAL_EXACT" if not violations else "NOT_PROMOTED",
            "material_to_pixel_shader_header": "GLOBAL_EXACT" if not violations else "NOT_PROMOTED",
            "shader_header_to_exact_gcn_program": "GLOBAL_EXACT_PREREQUISITE",
            "material_backed_vs_ps_owner_relation": "GLOBAL_EXACT" if not violations else "NOT_PROMOTED",
            "param_index_to_attr_index_provenance": "NEXT_GATE" if not violations else "WITHHELD",
            "domain_shader_pipeline_ownership": "WITHHELD_SEPARATE_TESSELLATION_GATE",
            "varying_semantic_names": "WITHHELD",
            "shader_expression_semantics": "WITHHELD",
            "shader_expression_semantic_promotions": 0,
        },
        "policy": (
            "VS/PS ownership is promoted only when both shader FileHashes are serialized in the same exact retail "
            "PS4 Material payload and each non-null header resolves uniquely to the frozen exact shader corpus at the "
            "correct stage. Package proximity, slot compatibility, naming and visual similarity are never pairing evidence."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--member-catalog", type=Path, action="append", required=True)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--part-count", type=int, default=10)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--shader-corpus", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=max(1, min(6, os.cpu_count() or 1)))
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()
    out = build(a.member_catalog, a.base_url, a.part_count, a.runtime, a.shader_corpus, max(1, a.workers))
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": out["status"], "coverage": out["coverage"], "violations": out["violations"][:50]}, indent=2, sort_keys=True))
    return 0 if not out["violations"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
