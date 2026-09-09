#!/usr/bin/env python3
"""Build an exact evidence frontier for D1 GCN forms absent from 808EE505.

This report is deliberately structural-only. It joins the exact OrbShdr-derived
PS/VS/DS corpus, the complete Structural IR census, the stage frontier and every
per-code-SHA IR record. Novel opcodes/forms are mapped back to exact package/native
program/header/stage provenance, but no instruction semantics are promoted here.
"""
from __future__ import annotations

import argparse
import collections
import gc
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import d1_gcn_cfg_ir_v2 as structural
import d1_gcn_shader_corpus_structural_census as census_lib
from d1_gcn_shader_corpus_structural_census_v3 import fixed_reg_kind

EXACT_SCHEMA = "d1_remote_ps4_shader_corpus_extract/v3"
EXACT_STATUS = "D1_REMOTE_PS4_SHADER_CORPUS_EXACT_PS_VS_DS"
CENSUS_SCHEMA = "d1_gcn_shader_corpus_structural_census/v1"
CENSUS_STATUS = "D1_GCN_SHADER_CORPUS_STRUCTURAL_CENSUS_COMPLETE"
FRONTIER_SCHEMA = "d1_gcn_shader_corpus_stage_frontier/v3"
FRONTIER_STATUS = "D1_GCN_SHADER_CORPUS_STAGE_FRONTIER_PS_VS_DS_EXACT"
OUTPUT_SCHEMA = "d1_gcn_opcode_structural_evidence_frontier/v1"
OUTPUT_STATUS = "D1_GCN_OPCODE_STRUCTURAL_EVIDENCE_FRONTIER_EXACT"
IR_STATUS = "D1_GCN_STRUCTURAL_IR_COMPLETE"
STAGES = ("PS", "VS", "DS")
EXPECTED_STAGE_PROGRAMS = {"PS": 18375, "VS": 8069, "DS": 20}
EXPECTED_HEADER_STAGES = {"PS": 25405, "VS": 12408, "DS": 79}
EXPECTED_NATIVE_STAGE_ROWS = {"PS": 24771, "VS": 12329, "DS": 79}
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
TAG_RE = re.compile(r"^[0-9A-F]{8}$")
PKG_RE = re.compile(r"^[0-9A-F]{4}$")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def canonical(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def form_id(payload: dict) -> str:
    return hashlib.sha256(canonical(payload).encode()).hexdigest()


def stage_counter() -> dict[str, int]:
    return {s: 0 for s in STAGES}


def require_sha(path: Path, expected: str | None, violations: list[str], label: str) -> str:
    got = sha256_file(path)
    if expected and got != expected.lower():
        violations.append(f"{label}_sha256:{got}!={expected.lower()}")
    return got


def _form_from_census_row(row: dict) -> dict:
    return {
        "opcode": row["opcode"],
        "encoding_width_bytes": int(row["encoding_width_bytes"]),
        "operand_syntax": list(row.get("operand_syntax") or []),
        "def_kinds": list(row.get("def_kinds") or []),
        "use_kinds": list(row.get("use_kinds") or []),
        "has_branch_target": bool(row.get("has_branch_target")),
        "classification_rule": row["classification_rule"],
    }


def _instruction_example(row: dict, sha: str, stage: str) -> dict:
    return {
        "gcn_sha256": sha,
        "stage": stage,
        "index": int(row["index"]),
        "address": row.get("address_hex"),
        "encoding_hex": str(row.get("encoding_hex", "")).lower(),
        "byte_size": int(row.get("byte_size", len(str(row.get("encoding_hex", ""))) // 2)),
        "opcode": row["opcode"],
        "operands": list(row.get("operands") or []),
        "defs": list(row.get("defs") or []),
        "uses": list(row.get("uses") or []),
        "branch_target_label": row.get("branch_target_label"),
        "source_line": row.get("source_line"),
    }


def build(
    exact_path: Path,
    census_path: Path,
    frontier_path: Path,
    ir_dir: Path,
    expected_exact_sha: str | None = None,
    expected_census_sha: str | None = None,
    expected_frontier_sha: str | None = None,
) -> dict:
    census_lib.reg_kind = fixed_reg_kind
    violations: list[str] = []
    source_hashes = {
        "exact_corpus_sha256": require_sha(exact_path, expected_exact_sha, violations, "exact_corpus"),
        "structural_census_sha256": require_sha(census_path, expected_census_sha, violations, "structural_census"),
        "stage_frontier_sha256": require_sha(frontier_path, expected_frontier_sha, violations, "stage_frontier"),
    }

    # Retain only exact provenance from the large source corpus, then release it.
    exact = json.loads(exact_path.read_text())
    if exact.get("schema") != EXACT_SCHEMA:
        violations.append(f"exact_schema:{exact.get('schema')!r}")
    if exact.get("status") != EXACT_STATUS:
        violations.append(f"exact_status:{exact.get('status')!r}")
    if exact.get("violations"):
        violations.append(f"exact_violations:{len(exact['violations'])}")
    hp = exact.get("header_population") or {}
    np = exact.get("native_reference_population") or {}
    gp = exact.get("gcn_program_population") or {}
    if hp.get("stage_counts") != EXPECTED_HEADER_STAGES:
        violations.append(f"exact_header_stage_counts:{hp.get('stage_counts')!r}")
    if np.get("stage_counts") != EXPECTED_NATIVE_STAGE_ROWS:
        violations.append(f"exact_native_stage_counts:{np.get('stage_counts')!r}")
    if gp.get("stage_unique_counts") != EXPECTED_STAGE_PROGRAMS:
        violations.append(f"exact_program_stage_counts:{gp.get('stage_unique_counts')!r}")
    if int(gp.get("unique_exact_code_sha256_count", -1)) != 26464:
        violations.append("exact_unique_program_count_mismatch")
    if int(gp.get("shared_by_multiple_stages", -1)) != 0:
        violations.append(f"exact_cross_stage_sha_count:{gp.get('shared_by_multiple_stages')!r}")

    native_by_ref: dict[str, dict] = {}
    for row in exact.get("native_programs") or []:
        ref = str(row.get("native_program_reference", "")).upper()
        pkg = str(row.get("package_id", "")).upper()
        stages = sorted({str(x).upper() for x in (row.get("stages") or [])})
        gcn = row.get("gcn_code") or {}
        gsha = str(gcn.get("sha256", "")).lower()
        if not TAG_RE.fullmatch(ref):
            violations.append(f"native_ref_invalid:{ref!r}")
            continue
        if ref in native_by_ref:
            violations.append(f"native_ref_duplicate:{ref}")
            continue
        if not PKG_RE.fullmatch(pkg):
            violations.append(f"native_package_invalid:{ref}:{pkg!r}")
        if len(stages) != 1 or stages[0] not in STAGES:
            violations.append(f"native_stage_invalid:{ref}:{stages!r}")
        if not SHA_RE.fullmatch(gsha):
            violations.append(f"native_gcn_sha_invalid:{ref}:{gsha!r}")
        native_by_ref[ref] = {
            "native_program_reference": ref,
            "package_id": pkg,
            "logical_view": row.get("logical_view"),
            "stage": stages[0] if len(stages) == 1 else None,
            "headers": sorted(
                [{"stage": str(h.get("stage", "")).upper(), "header": str(h.get("header", "")).upper()}
                 for h in (row.get("headers") or [])],
                key=lambda x: (x["stage"], x["header"]),
            ),
            "gcn_sha256": gsha,
            "gcn_bytes": int(gcn.get("bytes", 0)),
            "native_payload_sha256": (row.get("native_payload") or {}).get("sha256"),
            "orb_stage": row.get("orb_stage"),
        }
    if len(native_by_ref) != int(np.get("planned_unique", -1)):
        violations.append(f"native_ref_map_count:{len(native_by_ref)}!={np.get('planned_unique')}")
    del exact
    gc.collect()

    census = json.loads(census_path.read_text())
    if census.get("schema") != CENSUS_SCHEMA:
        violations.append(f"census_schema:{census.get('schema')!r}")
    if census.get("status") != CENSUS_STATUS:
        violations.append(f"census_status:{census.get('status')!r}")
    if census.get("violations"):
        violations.append(f"census_violations:{len(census['violations'])}")
    programs = census.get("programs") or []
    if len(programs) != 26464:
        violations.append(f"census_program_count:{len(programs)}!=26464")
    baseline = census.get("baseline") or {}
    baseline_sha = str(baseline.get("gcn_sha256", "")).lower()
    if str(baseline.get("header", "")).upper() != "808EE505" or not SHA_RE.fullmatch(baseline_sha):
        violations.append(f"baseline_identity:{baseline!r}")

    census_summary = census.get("census") or {}
    census_op_rows = census_summary.get("opcodes") or []
    census_form_rows = census_summary.get("structural_forms") or []
    novel_op_rows = [x for x in census_op_rows if x.get("novel_vs_baseline")]
    novel_form_rows = [x for x in census_form_rows if x.get("novel_vs_baseline")]
    novel_ops = {str(x["opcode"]) for x in novel_op_rows}
    if len(novel_ops) != 67:
        violations.append(f"novel_opcode_count:{len(novel_ops)}!=67")
    if len(novel_form_rows) != 532:
        violations.append(f"novel_form_count:{len(novel_form_rows)}!=532")

    novel_form_by_canonical: dict[str, dict] = {}
    for row in novel_form_rows:
        payload = _form_from_census_row(row)
        key = canonical(payload)
        fid = form_id(payload)
        if key in novel_form_by_canonical:
            violations.append(f"novel_form_duplicate:{fid}")
        novel_form_by_canonical[key] = {
            "structural_form_key_sha256": fid,
            **payload,
            "census_instruction_count": int(row["count"]),
            "baseline_instruction_count": int(row.get("baseline_count", 0)),
            "instruction_count": 0,
            "program_sha256": set(),
            "stage_instruction_counts": stage_counter(),
            "stage_program_sha256": {s: set() for s in STAGES},
            "examples": [],
        }

    frontier = json.loads(frontier_path.read_text())
    if frontier.get("schema") != FRONTIER_SCHEMA:
        violations.append(f"frontier_schema:{frontier.get('schema')!r}")
    if frontier.get("status") != FRONTIER_STATUS:
        violations.append(f"frontier_status:{frontier.get('status')!r}")
    if frontier.get("violations"):
        violations.append(f"frontier_violations:{len(frontier['violations'])}")
    fcov = frontier.get("coverage") or {}
    if fcov.get("stage_unique_program_counts") != EXPECTED_STAGE_PROGRAMS:
        violations.append(f"frontier_stage_counts:{fcov.get('stage_unique_program_counts')!r}")
    if int(fcov.get("exact_unique_gcn_programs", -1)) != 26464:
        violations.append("frontier_program_count_mismatch")
    if int(fcov.get("multi_stage_exact_code_sha_count", -1)) != 0:
        violations.append("frontier_cross_stage_sha_nonzero")
    ff = frontier.get("frontier_vs_808ee505_baseline") or {}
    if int(ff.get("novel_opcode_count", -1)) != 67:
        violations.append(f"frontier_novel_opcodes:{ff.get('novel_opcode_count')!r}")
    if int(ff.get("novel_structural_form_count", -1)) != 532:
        violations.append(f"frontier_novel_forms:{ff.get('novel_structural_form_count')!r}")
    queue_by_op = {str(x["opcode"]): x for x in (ff.get("opcode_promotion_queue") or [])}
    if set(queue_by_op) != novel_ops:
        violations.append("frontier_novel_opcode_set_disagrees_with_census")

    opcode_ev = {
        op: {
            "opcode": op,
            "semantic_status": "UNPROVEN",
            "instruction_count": 0,
            "program_sha256": set(),
            "stage_instruction_counts": stage_counter(),
            "stage_program_sha256": {s: set() for s in STAGES},
            "structural_form_key_sha256": set(),
            "encoding_width_bytes": set(),
            "examples": [],
        }
        for op in sorted(novel_ops)
    }

    program_provenance: dict[str, dict] = {}
    seen_shas: set[str] = set()
    observed_ops = collections.Counter()
    observed_forms = collections.Counter()
    exact_instruction_count = 0
    exact_stage_program_counts = stage_counter()

    for rec in programs:
        sha = str(rec.get("gcn_sha256", "")).lower()
        stages = sorted({str(x).upper() for x in (rec.get("stages") or [])})
        nbytes = int(rec.get("gcn_bytes", 0))
        if not SHA_RE.fullmatch(sha):
            violations.append(f"program_sha_invalid:{sha!r}")
            continue
        if sha in seen_shas:
            violations.append(f"program_sha_duplicate:{sha}")
            continue
        seen_shas.add(sha)
        if len(stages) != 1 or stages[0] not in STAGES:
            violations.append(f"program_stage_invalid:{sha}:{stages!r}")
            continue
        stage = stages[0]
        exact_stage_program_counts[stage] += 1
        if rec.get("violations"):
            violations.append(f"program_census_violations:{sha}:{len(rec['violations'])}")
        if not (rec.get("byte_coverage") or {}).get("exact_full_coverage"):
            violations.append(f"program_byte_coverage_not_exact:{sha}")

        p = ir_dir / f"{sha}.json"
        if not p.is_file():
            violations.append(f"ir_missing:{sha}")
            continue
        ir = json.loads(p.read_text())
        rows = ir.get("instructions") or []
        pa = ir.get("parse_accounting") or {}
        if ir.get("status") != IR_STATUS:
            violations.append(f"ir_status:{sha}:{ir.get('status')!r}")
        if pa.get("status") != structural.PARSE_ACCOUNTING_STATUS:
            violations.append(f"parse_status:{sha}:{pa.get('status')!r}")
        checks = {
            "native_instruction_line_count": len(rows),
            "ir_instruction_count": len(rows),
            "encoded_byte_count": nbytes,
            "unaccounted_native_instruction_line_count": 0,
            "duplicate_ir_instruction_count": 0,
        }
        for k, want in checks.items():
            if pa.get(k) != want:
                violations.append(f"parse_accounting:{sha}:{k}:{pa.get(k)!r}!={want!r}")
        if int(ir.get("instruction_count", -1)) != len(rows):
            violations.append(f"ir_instruction_count:{sha}:{ir.get('instruction_count')}!={len(rows)}")
        if int(rec.get("instruction_count", -1)) != len(rows):
            violations.append(f"census_instruction_count:{sha}:{rec.get('instruction_count')}!={len(rows)}")

        native_refs = sorted({str(x).upper() for x in (rec.get("native_program_references") or [])})
        native_rows = []
        for ref in native_refs:
            nrow = native_by_ref.get(ref)
            if nrow is None:
                violations.append(f"provenance_native_ref_missing:{sha}:{ref}")
                continue
            if nrow["gcn_sha256"] != sha:
                violations.append(f"provenance_gcn_sha:{ref}:{nrow['gcn_sha256']}!={sha}")
            if nrow["stage"] != stage:
                violations.append(f"provenance_stage:{ref}:{nrow['stage']}!={stage}")
            native_rows.append({k: v for k, v in nrow.items() if k not in ("gcn_sha256", "gcn_bytes")})
        census_headers = sorted(
            [{"stage": str(h.get("stage", "")).upper(), "header": str(h.get("header", "")).upper()}
             for h in (rec.get("headers") or [])],
            key=lambda x: (x["stage"], x["header"]),
        )
        from_native_headers = sorted({(h["stage"], h["header"]) for n in native_rows for h in n["headers"]})
        census_header_pairs = sorted({(h["stage"], h["header"]) for h in census_headers})
        if from_native_headers != census_header_pairs:
            violations.append(f"provenance_header_set:{sha}:native={from_native_headers!r}:census={census_header_pairs!r}")

        touched = False
        exact_instruction_count += len(rows)
        for row in rows:
            op = str(row["opcode"])
            observed_ops[op] += 1
            payload = census_lib.form_payload(census_lib.form_key(row))
            pkey = canonical(payload)
            observed_forms[pkey] += 1
            form_ev = novel_form_by_canonical.get(pkey)
            if form_ev is not None:
                touched = True
                form_ev["instruction_count"] += 1
                form_ev["program_sha256"].add(sha)
                form_ev["stage_instruction_counts"][stage] += 1
                form_ev["stage_program_sha256"][stage].add(sha)
                if len(form_ev["examples"]) < 3:
                    form_ev["examples"].append(_instruction_example(row, sha, stage))
            if op in opcode_ev:
                touched = True
                oe = opcode_ev[op]
                oe["instruction_count"] += 1
                oe["program_sha256"].add(sha)
                oe["stage_instruction_counts"][stage] += 1
                oe["stage_program_sha256"][stage].add(sha)
                oe["structural_form_key_sha256"].add(form_id(payload))
                oe["encoding_width_bytes"].add(int(payload["encoding_width_bytes"]))
                if len(oe["examples"]) < 3:
                    oe["examples"].append(_instruction_example(row, sha, stage))
        if touched:
            program_provenance[sha] = {
                "gcn_sha256": sha,
                "gcn_bytes": nbytes,
                "stage": stage,
                "headers": census_headers,
                "native_program_references": native_rows,
            }

    if len(seen_shas) != 26464:
        violations.append(f"observed_program_shas:{len(seen_shas)}!=26464")
    if exact_stage_program_counts != EXPECTED_STAGE_PROGRAMS:
        violations.append(f"observed_stage_program_counts:{exact_stage_program_counts!r}")
    if exact_instruction_count != int(census_summary.get("instruction_count", -1)):
        violations.append(f"observed_instruction_count:{exact_instruction_count}!={census_summary.get('instruction_count')}")

    want_ops = {str(x["opcode"]): int(x["count"]) for x in census_op_rows}
    if dict(observed_ops) != want_ops:
        violations.append("recomputed_opcode_histogram_disagrees_with_census")
    want_forms = {canonical(_form_from_census_row(x)): int(x["count"]) for x in census_form_rows}
    if dict(observed_forms) != want_forms:
        violations.append("recomputed_structural_form_histogram_disagrees_with_census")

    opcode_rows = []
    for op in sorted(opcode_ev, key=lambda x: (-opcode_ev[x]["instruction_count"], x)):
        e = opcode_ev[op]
        census_count = int(next(x["count"] for x in novel_op_rows if x["opcode"] == op))
        q = queue_by_op[op]
        if e["instruction_count"] != census_count:
            violations.append(f"opcode_count:{op}:{e['instruction_count']}!={census_count}")
        actual_stage_program_counts = {s: len(e["stage_program_sha256"][s]) for s in STAGES if e["stage_program_sha256"][s]}
        if actual_stage_program_counts != q.get("program_counts"):
            violations.append(f"opcode_stage_program_counts:{op}:{actual_stage_program_counts!r}!={q.get('program_counts')!r}")
        opcode_rows.append({
            "opcode": op,
            "semantic_status": "UNPROVEN",
            "instruction_count": e["instruction_count"],
            "program_count": len(e["program_sha256"]),
            "stages": [s for s in STAGES if e["stage_program_sha256"][s]],
            "stage_instruction_counts": {s: e["stage_instruction_counts"][s] for s in STAGES if e["stage_instruction_counts"][s]},
            "stage_program_counts": actual_stage_program_counts,
            "encoding_width_bytes": sorted(e["encoding_width_bytes"]),
            "structural_form_key_sha256": sorted(e["structural_form_key_sha256"]),
            "program_sha256": sorted(e["program_sha256"]),
            "examples": e["examples"],
        })

    form_rows = []
    for key in sorted(novel_form_by_canonical):
        e = novel_form_by_canonical[key]
        if e["instruction_count"] != e["census_instruction_count"]:
            violations.append(f"form_count:{e['structural_form_key_sha256']}:{e['instruction_count']}!={e['census_instruction_count']}")
        form_rows.append({
            "structural_form_key_sha256": e["structural_form_key_sha256"],
            "semantic_status": "UNPROVEN",
            **{k: e[k] for k in ("opcode", "encoding_width_bytes", "operand_syntax", "def_kinds", "use_kinds", "has_branch_target", "classification_rule")},
            "instruction_count": e["instruction_count"],
            "program_count": len(e["program_sha256"]),
            "stages": [s for s in STAGES if e["stage_program_sha256"][s]],
            "stage_instruction_counts": {s: e["stage_instruction_counts"][s] for s in STAGES if e["stage_instruction_counts"][s]},
            "stage_program_counts": {s: len(e["stage_program_sha256"][s]) for s in STAGES if e["stage_program_sha256"][s]},
            "program_sha256": sorted(e["program_sha256"]),
            "examples": e["examples"],
        })
    form_rows.sort(key=lambda x: (-x["program_count"], -x["instruction_count"], x["structural_form_key_sha256"]))

    touched_stages = stage_counter()
    for p in program_provenance.values():
        touched_stages[p["stage"]] += 1

    return {
        "schema": OUTPUT_SCHEMA,
        "status": OUTPUT_STATUS if not violations else "D1_GCN_OPCODE_STRUCTURAL_EVIDENCE_FRONTIER_WITH_VIOLATIONS",
        "sources": {
            "exact_corpus": str(exact_path),
            "structural_census": str(census_path),
            "stage_frontier": str(frontier_path),
            "ir_dir": str(ir_dir),
            **source_hashes,
        },
        "baseline": {
            "header": "808EE505",
            "gcn_sha256": baseline_sha,
            "opcode_count": int(frontier.get("baseline", {}).get("opcode_count", -1)),
            "structural_form_count": int(frontier.get("baseline", {}).get("structural_form_count", -1)),
        },
        "coverage": {
            "exact_unique_gcn_programs": len(seen_shas),
            "stage_unique_program_counts": exact_stage_program_counts,
            "exact_instruction_count": exact_instruction_count,
            "global_opcode_count": len(observed_ops),
            "global_structural_form_count": len(observed_forms),
            "novel_opcode_count": len(opcode_rows),
            "novel_structural_form_count": len(form_rows),
            "novel_opcode_instruction_occurrences": sum(x["instruction_count"] for x in opcode_rows),
            "novel_form_instruction_occurrences": sum(x["instruction_count"] for x in form_rows),
            "frontier_touching_unique_programs": len(program_provenance),
            "frontier_touching_stage_program_counts": touched_stages,
            "exact_native_program_reference_count": len(native_by_ref),
            "semantic_promotions": 0,
        },
        "novel_opcodes": opcode_rows,
        "novel_structural_forms": form_rows,
        "program_provenance": {k: program_provenance[k] for k in sorted(program_provenance)},
        "violations": violations,
        "policy": (
            "This artifact proves only exact structural occurrence and provenance. A novel opcode or "
            "normalized structural form is not semantically supported merely because CLRX disassembles it, "
            "because it is frequent, or because it appears in multiple stages. semantic_promotions remains "
            "zero. Instruction semantics require a separate source-backed promotion gate before canonical D1 "
            "shader IR, Rust, or Blender backends may rely on them. structural_form_key_sha256 is a report-local "
            "SHA-256 of the exact canonical normalized form payload used by the existing census algorithm."
        ),
    }


def self_test() -> None:
    p = {
        "opcode": "v_add_f32", "encoding_width_bytes": 8, "operand_syntax": ["v#", "v#", "v#"],
        "def_kinds": ["VGPR"], "use_kinds": ["VGPR", "VGPR"], "has_branch_target": False,
        "classification_rule": "GENERIC_FIRST_OPERAND_DESTINATION",
    }
    assert form_id(p) == form_id(dict(reversed(list(p.items()))))
    assert len(form_id(p)) == 64
    assert stage_counter() == {"PS": 0, "VS": 0, "DS": 0}
    print("D1_GCN_OPCODE_STRUCTURAL_EVIDENCE_FRONTIER_V1_SELF_TEST_OK")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exact-corpus", type=Path)
    ap.add_argument("--census", type=Path)
    ap.add_argument("--frontier", type=Path)
    ap.add_argument("--ir-dir", type=Path)
    ap.add_argument("--expected-exact-sha256")
    ap.add_argument("--expected-census-sha256")
    ap.add_argument("--expected-frontier-sha256")
    ap.add_argument("-o", "--output", type=Path)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        self_test()
        return 0
    for name in ("exact_corpus", "census", "frontier", "ir_dir", "output"):
        if getattr(a, name) is None:
            ap.error(f"--{name.replace('_','-')} is required unless --self-test")
    out = build(
        a.exact_corpus, a.census, a.frontier, a.ir_dir,
        a.expected_exact_sha256, a.expected_census_sha256, a.expected_frontier_sha256,
    )
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"status": out["status"], "coverage": out["coverage"], "violation_count": len(out["violations"])}, indent=2))
    if out["violations"]:
        for x in out["violations"][:100]:
            print("VIOLATION", x)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
