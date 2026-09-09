#!/usr/bin/env python3
"""Exact retail PS4 Material -> VS/PS shader-owner frontier for Destiny 1.

This gate consumes the same current-entry SQLite denominator and universal package-member
catalog used by the exact global shader census.  It enumerates every current PS4 material
entry by its serialized class reference (80801AD7), fetches and parses the exact material
payload, and joins each non-null vertex/pixel shader FileHash to the frozen exact shader
corpus by shader-header identity.

Only ownership is promoted here.  PARAM->ATTR linkage, varying semantic names, material
roles and shader-expression meaning remain withheld for later gates.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import sqlite3
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
            rec = {
                "header": tag,
                "stage": stage,
                "gcn_sha256": sha,
                "native_program_references": refs,
            }
            if hs != stage:
                raise ValueError(f"header/program stage mismatch:{tag}:{hs}:{stage}")
            old = out.get(tag)
            if old is not None and old != rec:
                raise ValueError(f"shader header maps ambiguously:{tag}:{old}:{rec}")
            out[tag] = rec
    return out


def material_rows(db_path: Path) -> tuple[list[dict], dict]:
    db = sqlite3.connect(str(db_path))
    db.row_factory = sqlite3.Row
    try:
        meta = {r["key"]: r["value"] for r in db.execute("SELECT key,value FROM meta ORDER BY key")}
        rows = [dict(r) for r in db.execute(
            """SELECT package_name,package_id,package_generation,package_patch_id,
                      entry_index,tag_hash,reference,type,subtype,file_size,
                      starting_block,starting_block_offset
                 FROM current_entries
                WHERE UPPER(reference)=?
                ORDER BY tag_hash""",
            (PS4_MATERIAL_CLASS,),
        )]
    finally:
        db.close()
    return rows, meta


def join_shader(header: str, expected_stage: str, headers: dict[str, dict], violations: list[str], material: str) -> dict:
    h = norm(header)
    if h in NULLS:
        return {"header": h, "null": True, "stage": expected_stage}
    rec = headers.get(h)
    if rec is None:
        violations.append(f"shader_header_absent:{material}:{expected_stage}:{h}")
        return {"header": h, "null": False, "stage": expected_stage, "resolved": False}
    if rec["stage"] != expected_stage:
        violations.append(f"shader_stage_mismatch:{material}:{h}:{rec['stage']}!={expected_stage}")
    return {**rec, "null": False, "resolved": rec["stage"] == expected_stage}


def build(sqlite_path: Path, catalog_paths: list[Path], base_url: str, part_count: int,
          runtime: Path, shader_corpus_path: Path) -> dict:
    violations: list[str] = []
    src = json.loads(shader_corpus_path.read_text())
    try:
        headers = shader_header_index(src)
    except Exception as ex:
        raise SystemExit(f"shader corpus prerequisite failed:{type(ex).__name__}:{ex}")

    rows, dbmeta = material_rows(sqlite_path)
    if not rows:
        violations.append("zero_current_ps4_material_rows")
    tags = [norm(r["tag_hash"]) for r in rows]
    if len(set(tags)) != len(tags):
        dup = [x for x, n in collections.Counter(tags).items() if n > 1]
        violations.append(f"duplicate_current_material_tags:{dup[:20]}")

    catalogs = load_catalogs(catalog_paths)
    arc = SplitHttpTar(
        [f"{base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1, part_count + 1)],
        retries=6, timeout=90,
    )
    corpus = RemoteCorpus(arc, catalogs, runtime)

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

    for n, row in enumerate(rows, 1):
        tag = norm(row["tag_hash"])
        package_id = str(row["package_id"]).upper().zfill(4)
        if norm(row["reference"]) != PS4_MATERIAL_CLASS:
            violations.append(f"material_class_query_drift:{tag}:{row['reference']}")
            continue
        try:
            meta = corpus.entry_meta(tag)
        except Exception as ex:
            meta = None
            violations.append(f"material_entry_meta_exception:{tag}:{type(ex).__name__}:{ex}")
        if meta is None:
            violations.append(f"material_entry_meta_missing:{tag}")
            continue
        if norm(meta.get("tag_hash")) != tag:
            violations.append(f"material_tag_identity:{tag}:{meta.get('tag_hash')}")
        if norm(meta.get("reference")) != PS4_MATERIAL_CLASS:
            violations.append(f"material_remote_class:{tag}:{meta.get('reference')}")
        if int(meta.get("index", -1)) != int(row["entry_index"]):
            violations.append(f"material_entry_index:{tag}:{meta.get('index')}!={row['entry_index']}")
        if int(meta.get("file_size", -1)) != int(row["file_size"]):
            violations.append(f"material_file_size:{tag}:{meta.get('file_size')}!={row['file_size']}")

        payload, logical_view = corpus.payload(tag)
        if payload is None:
            violations.append(f"material_payload_missing:{tag}")
            continue
        try:
            mat = parse_material(payload, "PS4")
        except Exception as ex:
            violations.append(f"material_parse:{tag}:{type(ex).__name__}:{ex}")
            continue

        vs = join_shader(mat["vertex_shader"], "VS", headers, violations, tag)
        ps = join_shader(mat["pixel_shader"], "PS", headers, violations, tag)
        vsh, psh = norm(mat["vertex_shader"]), norm(mat["pixel_shader"])
        pattern = ("NULL" if vsh in NULLS else "VS") + "+" + ("NULL" if psh in NULLS else "PS")
        null_patterns[pattern] += 1
        if vsh not in NULLS:
            vs_headers[vsh] += 1
            if vs.get("gcn_sha256"):
                vs_gcn[vs["gcn_sha256"]] += 1
        if psh not in NULLS:
            ps_headers[psh] += 1
            if ps.get("gcn_sha256"):
                ps_gcn[ps["gcn_sha256"]] += 1
        if vsh not in NULLS and psh not in NULLS and vs.get("resolved") and ps.get("resolved"):
            key = (vsh, psh)
            pair_members[key].append(tag)
            pair_packages[key].add(package_id)

        logical_views[str(logical_view)] += 1
        package_counts[package_id] += 1
        materials.append({
            "material": tag,
            "package_id": package_id,
            "package_name": row["package_name"],
            "package_generation": int(row["package_generation"]),
            "package_patch_id": int(row["package_patch_id"]),
            "entry_index": int(row["entry_index"]),
            "file_size": int(row["file_size"]),
            "payload_sha256": sha256_bytes(payload),
            "logical_view": logical_view,
            "material_declared_file_size": int(mat["declared_file_size"]),
            "material_actual_file_size": int(mat["actual_file_size"]),
            "vertex_shader": vs,
            "pixel_shader": ps,
            "owner_pattern": pattern,
        })
        if n % 1000 == 0 or n == len(rows):
            print(f"MATERIALS {n}/{len(rows)} violations={len(violations)}", flush=True)

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

    coverage = {
        "current_material_entry_count": len(rows),
        "material_payload_recovered_count": len(materials),
        "material_parse_success_count": len(materials),
        "material_owner_pattern_counts": dict(sorted(null_patterns.items())),
        "resolved_nonnull_vs_material_count": sum(1 for x in materials if not x["vertex_shader"].get("null") and x["vertex_shader"].get("resolved")),
        "resolved_nonnull_ps_material_count": sum(1 for x in materials if not x["pixel_shader"].get("null") and x["pixel_shader"].get("resolved")),
        "unique_vertex_shader_header_count": len(vs_headers),
        "unique_pixel_shader_header_count": len(ps_headers),
        "unique_vertex_gcn_program_count": len(vs_gcn),
        "unique_pixel_gcn_program_count": len(ps_gcn),
        "resolved_vs_ps_owner_pair_count": len(pairs),
        "materials_with_resolved_vs_ps_owner_pair": sum(len(x["materials"]) for x in pairs),
        "material_package_count": len(package_counts),
        "logical_view_count": len(logical_views),
        "shader_corpus_header_count": len(headers),
        "material_header_vs_ps_pair_promotions": sum(len(x["materials"]) for x in pairs),
        "param_index_to_attr_index_promotions": 0,
        "shader_expression_semantic_promotions": 0,
    }
    if len(materials) != len(rows):
        violations.append(f"material_accounting:{len(materials)}!={len(rows)}")

    return {
        "schema": SCHEMA,
        "status": STATUS if not violations else "D1_GCN_MATERIAL_SHADER_OWNER_FRONTIER_WITH_VIOLATIONS",
        "source": {
            "everything_sqlite_meta": dbmeta,
            "material_class": PS4_MATERIAL_CLASS,
            "shader_corpus_schema": src.get("schema"),
            "shader_corpus_status": src.get("status"),
            "base_url": base_url,
            "catalog_paths": [str(x) for x in catalog_paths],
        },
        "coverage": coverage,
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
    ap.add_argument("--sqlite", type=Path, required=True)
    ap.add_argument("--member-catalog", type=Path, action="append", required=True)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--part-count", type=int, default=10)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--shader-corpus", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()
    out = build(a.sqlite, a.member_catalog, a.base_url, a.part_count, a.runtime, a.shader_corpus)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": out["status"], "coverage": out["coverage"], "violations": out["violations"][:50]}, indent=2, sort_keys=True))
    return 0 if not out["violations"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
