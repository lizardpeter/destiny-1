#!/usr/bin/env python3
"""Build the exact current-retail D1 PS4 shader-header/native-reference census plan.

This is metadata-only.  It consumes the archive-wide current Tiger entry index and
enumerates every current type 32/subtype 8 PixelShader header and type 32/subtype 9
VertexShader header.  FileEntry.Reference is preserved as the only native-program
edge.  No package names, adjacency, material names, or shader semantics are used to
discover programs.

The output is intentionally a plan, not a shader-coverage claim.  Native payload
bytes, OrbShdr framing, disassembly, and structural IR are separate later gates.
"""
from __future__ import annotations

import argparse
import collections
import json
import sqlite3
from pathlib import Path

NULLS = {"00000000", "FFFFFFFF"}
STAGES = {(32, 8): "PS", (32, 9): "VS"}


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("sqlite", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    db = sqlite3.connect(a.sqlite)
    db.row_factory = sqlite3.Row
    violations: list[str] = []
    try:
        meta = {str(k): str(v) for k, v in db.execute("select key,value from meta")}
        if meta.get("schema") != "d1_remote_everything_index/v1":
            violations.append(f"index_schema:{meta.get('schema')!r}")

        rows = list(db.execute(
            """select occurrence_id,package_name,package_id,package_generation,
                      package_patch_id,entry_index,tag_hash,reference,type,subtype,
                      entry_b,file_size
               from current_entries
               where type=32 and subtype in (8,9)
               order by subtype,tag_hash"""
        ))
        by_tag: dict[str, list[sqlite3.Row]] = collections.defaultdict(list)
        for r in db.execute(
            """select occurrence_id,package_name,package_id,package_generation,
                      package_patch_id,entry_index,tag_hash,reference,type,subtype,
                      entry_b,file_size
               from current_entries
               order by tag_hash"""
        ):
            by_tag[norm(r["tag_hash"])].append(r)

        tag_counts = collections.Counter(norm(r["tag_hash"]) for r in rows)
        dup_headers = sorted(k for k, n in tag_counts.items() if n != 1)
        if dup_headers:
            violations.append(f"nonunique_current_shader_headers:{dup_headers[:20]}")

        headers = []
        refs: dict[str, dict] = {}
        stage_counts = collections.Counter()
        for r in rows:
            typ = (int(r["type"]), int(r["subtype"]))
            stage = STAGES[typ]
            stage_counts[stage] += 1
            tag = norm(r["tag_hash"])
            ref = norm(r["reference"])
            rec = {
                "stage": stage,
                "header": tag,
                "header_occurrence_id": int(r["occurrence_id"]),
                "header_package_name": str(r["package_name"]),
                "header_package_id": str(r["package_id"]).upper().zfill(4),
                "header_package_generation": int(r["package_generation"]),
                "header_package_patch_id": int(r["package_patch_id"]),
                "header_entry_index": int(r["entry_index"]),
                "header_type": int(r["type"]),
                "header_subtype": int(r["subtype"]),
                "header_entry_b": norm(r["entry_b"]),
                "header_file_size": int(r["file_size"]),
                "native_program_reference": ref,
            }
            if ref in NULLS:
                rec["native_program_meta"] = None
                violations.append(f"{stage}:{tag}:null_native_program_reference:{ref}")
            else:
                targets = by_tag.get(ref, [])
                if len(targets) != 1:
                    rec["native_program_meta"] = {
                        "current_occurrence_count": len(targets),
                    }
                    violations.append(
                        f"{stage}:{tag}:native_program_current_occurrence_count:{ref}:{len(targets)}"
                    )
                else:
                    t = targets[0]
                    rec["native_program_meta"] = {
                        "occurrence_id": int(t["occurrence_id"]),
                        "package_name": str(t["package_name"]),
                        "package_id": str(t["package_id"]).upper().zfill(4),
                        "package_generation": int(t["package_generation"]),
                        "package_patch_id": int(t["package_patch_id"]),
                        "entry_index": int(t["entry_index"]),
                        "tag_hash": norm(t["tag_hash"]),
                        "reference": norm(t["reference"]),
                        "type": int(t["type"]),
                        "subtype": int(t["subtype"]),
                        "entry_b": norm(t["entry_b"]),
                        "file_size": int(t["file_size"]),
                    }
                q = refs.setdefault(ref, {"native_program_reference": ref, "headers": []})
                q["headers"].append({"stage": stage, "header": tag})
            headers.append(rec)

        for q in refs.values():
            q["headers"].sort(key=lambda x: (x["stage"], x["header"]))
            q["header_count"] = len(q["headers"])
            q["stage_counts"] = dict(sorted(collections.Counter(
                x["stage"] for x in q["headers"]
            ).items()))

        if not stage_counts["PS"]:
            violations.append("no_current_32_8_pixel_shader_headers")
        if not stage_counts["VS"]:
            violations.append("no_current_32_9_vertex_shader_headers")

        out = {
            "schema": "d1_shader_corpus_plan/v1",
            "status": (
                "D1_SHADER_CORPUS_PLAN_COMPLETE"
                if not violations
                else "D1_SHADER_CORPUS_PLAN_WITH_VIOLATIONS"
            ),
            "source": {
                "sqlite": str(a.sqlite),
                "index_schema": meta.get("schema"),
                "packages_txt_sha256": meta.get("packages_txt_sha256"),
                "index_mode": meta.get("index_mode"),
            },
            "header_population": {
                "total": len(headers),
                "stage_counts": dict(sorted(stage_counts.items())),
                "unique_header_tag_count": len(tag_counts),
            },
            "native_reference_population": {
                "unique_native_program_reference_count": len(refs),
                "shared_native_reference_count": sum(
                    1 for q in refs.values() if q["header_count"] > 1
                ),
                "max_headers_per_native_reference": max(
                    (q["header_count"] for q in refs.values()), default=0
                ),
            },
            "headers": headers,
            "native_references": [refs[k] for k in sorted(refs)],
            "violations": violations,
            "policy": (
                "Current PS/VS population is selected only by exact Tiger type/subtype "
                "32:8 and 32:9. Native programs are reached only through each header's "
                "FileEntry.Reference. This layer makes no payload, disassembly, opcode, "
                "semantic, or shader-coverage claim."
            ),
        }
    finally:
        db.close()

    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n")
    print(
        "STATUS", out["status"],
        "HEADERS", out["header_population"]["total"],
        "PS", out["header_population"]["stage_counts"].get("PS", 0),
        "VS", out["header_population"]["stage_counts"].get("VS", 0),
        "UNIQUE_NATIVE_REFS", out["native_reference_population"]["unique_native_program_reference_count"],
        "VIOLATIONS", len(out["violations"]),
    )
    return 0 if not out["violations"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
