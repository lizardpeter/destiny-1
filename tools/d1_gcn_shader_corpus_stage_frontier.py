#!/usr/bin/env python3
"""Build an exact PS-versus-VS frontier from the game-wide D1 GCN Structural IR corpus.

This is deliberately a post-processing layer. It does not recover packages, disassemble
new bytes, or promote instruction semantics. It consumes the exact structural census and
the per-program Structural IR files emitted by that census, then preserves stage
membership while counting opcodes and normalized structural forms.

A GCN program whose exact code bytes are used by both stages is counted once in each
stage population and once in the unique all-stage population. This is intentional and
is reported explicitly. The output is a prioritization frontier for later source-backed
semantic work, not a claim that novel forms are semantically understood.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import tempfile
from pathlib import Path

import d1_gcn_shader_corpus_structural_census as census_lib
import d1_gcn_cfg_ir_v2 as structural

CENSUS_SCHEMA = "d1_gcn_shader_corpus_structural_census/v1"
GATE_SCHEMA = "d1_gcn_structural_parse_accounting_gate/v1"
IR_STATUS = "D1_GCN_STRUCTURAL_IR_COMPLETE"
OUTPUT_STATUS = "D1_GCN_SHADER_CORPUS_STAGE_FRONTIER_EXACT"
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
STAGES = ("PS", "VS")


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def _new_stage() -> dict:
    return {
        "program_shas": set(),
        "code_bytes": 0,
        "instruction_count": 0,
        "opcodes": collections.Counter(),
        "forms": collections.Counter(),
        "widths": collections.Counter(),
        "rules": collections.Counter(),
        "opcode_programs": collections.defaultdict(set),
        "form_programs": collections.defaultdict(set),
    }


def _stage_payload(stage: dict) -> dict:
    opcode_rows = []
    for op in sorted(stage["opcodes"]):
        opcode_rows.append({
            "opcode": op,
            "instruction_count": int(stage["opcodes"][op]),
            "program_count": len(stage["opcode_programs"][op]),
        })
    form_rows = []
    for key in sorted(stage["forms"], key=str):
        row = census_lib.form_payload(key)
        row["instruction_count"] = int(stage["forms"][key])
        row["program_count"] = len(stage["form_programs"][key])
        form_rows.append(row)
    return {
        "unique_program_count": len(stage["program_shas"]),
        "exact_code_bytes": int(stage["code_bytes"]),
        "instruction_count": int(stage["instruction_count"]),
        "opcode_count": len(stage["opcodes"]),
        "structural_form_count": len(stage["forms"]),
        "encoding_widths": [
            {"bytes": int(width), "instruction_count": int(stage["widths"][width])}
            for width in sorted(stage["widths"])
        ],
        "classification_rules": [
            {"rule": rule, "instruction_count": int(stage["rules"][rule])}
            for rule in sorted(stage["rules"])
        ],
        "opcodes": opcode_rows,
        "structural_forms": form_rows,
    }


def _form_rows(keys: set[tuple], ps: dict, vs: dict) -> list[dict]:
    rows = []
    for key in sorted(keys, key=str):
        row = census_lib.form_payload(key)
        row.update({
            "ps_instruction_count": int(ps["forms"].get(key, 0)),
            "vs_instruction_count": int(vs["forms"].get(key, 0)),
            "ps_program_count": len(ps["form_programs"].get(key, set())),
            "vs_program_count": len(vs["form_programs"].get(key, set())),
        })
        rows.append(row)
    return rows


def build(census_path: Path, ir_dir: Path, accounting_gate: Path | None = None) -> dict:
    src = json.loads(census_path.read_text())
    violations: list[str] = []
    if src.get("schema") != CENSUS_SCHEMA:
        raise ValueError(f"unsupported census schema: {src.get('schema')!r}")
    if src.get("status") != "D1_GCN_SHADER_CORPUS_STRUCTURAL_CENSUS_COMPLETE":
        violations.append(f"census_not_complete:{src.get('status')!r}")
    if src.get("violations"):
        violations.append(f"source_census_violations:{len(src['violations'])}")

    programs = src.get("programs") or []
    stage_data = {s: _new_stage() for s in STAGES}
    all_program_shas: set[str] = set()
    shared_program_shas: set[str] = set()
    header_owner: dict[tuple[str, str], str] = {}
    exact_programs = 0

    for rec in programs:
        code_sha = str(rec.get("gcn_sha256", "")).lower()
        code_bytes = int(rec.get("gcn_bytes", 0))
        stages = sorted({str(x).upper() for x in (rec.get("stages") or [])})
        row_prefix = code_sha or "<missing-sha>"
        row_violations = []
        if not SHA_RE.fullmatch(code_sha):
            row_violations.append("invalid_gcn_sha256")
        if code_bytes <= 0:
            row_violations.append(f"invalid_gcn_bytes:{code_bytes}")
        if not stages or any(x not in STAGES for x in stages):
            row_violations.append(f"invalid_stages:{stages}")
        if rec.get("violations"):
            row_violations.append(f"census_program_violations:{len(rec['violations'])}")

        ir = None
        ir_path = ir_dir / f"{code_sha}.json"
        if not ir_path.is_file():
            row_violations.append("structural_ir_missing")
        else:
            try:
                ir = json.loads(ir_path.read_text())
            except Exception as exc:
                row_violations.append(f"structural_ir_json:{type(exc).__name__}:{exc}")
        if ir is not None:
            if ir.get("status") != IR_STATUS:
                row_violations.append(f"structural_ir_status:{ir.get('status')!r}")
            pa = ir.get("parse_accounting") or {}
            if pa.get("status") != structural.PARSE_ACCOUNTING_STATUS:
                row_violations.append(f"parse_accounting_status:{pa.get('status')!r}")
            ins = ir.get("instructions") or []
            if int(ir.get("instruction_count", -1)) != len(ins):
                row_violations.append("instruction_count_mismatch")
            if int(pa.get("native_instruction_line_count", -1)) != len(ins):
                row_violations.append("native_line_count_mismatch")
            if int(pa.get("ir_instruction_count", -1)) != len(ins):
                row_violations.append("ir_line_count_mismatch")
            if int(pa.get("encoded_byte_count", -1)) != code_bytes:
                row_violations.append(
                    f"encoded_byte_count:{pa.get('encoded_byte_count')!r}!={code_bytes}"
                )
            if int(pa.get("unaccounted_native_instruction_line_count", -1)) != 0:
                row_violations.append("unaccounted_native_instruction_lines")
            if int(pa.get("duplicate_ir_instruction_count", -1)) != 0:
                row_violations.append("duplicate_ir_instructions")

        for h in rec.get("headers") or []:
            header = norm(h.get("header"))
            stage = str(h.get("stage", "")).upper()
            if stage not in stages:
                row_violations.append(f"header_stage_not_in_program:{header}:{stage}:{stages}")
                continue
            key = (stage, header)
            old = header_owner.get(key)
            if old is not None and old != code_sha:
                row_violations.append(f"header_maps_to_multiple_code_sha:{stage}:{header}:{old}:{code_sha}")
            else:
                header_owner[key] = code_sha

        if row_violations:
            violations.extend(f"{row_prefix}:{x}" for x in row_violations)
            continue

        exact_programs += 1
        all_program_shas.add(code_sha)
        if set(stages) == set(STAGES):
            shared_program_shas.add(code_sha)
        assert ir is not None
        ins = ir["instructions"]
        for stage_name in stages:
            d = stage_data[stage_name]
            if code_sha in d["program_shas"]:
                violations.append(f"duplicate_program_stage_membership:{code_sha}:{stage_name}")
                continue
            d["program_shas"].add(code_sha)
            d["code_bytes"] += code_bytes
            d["instruction_count"] += len(ins)
            for x in ins:
                op = str(x["opcode"])
                key = census_lib.form_key(x)
                width = len(str(x["encoding_hex"])) // 2
                rule = census_lib.classification_rule(x)
                d["opcodes"][op] += 1
                d["forms"][key] += 1
                d["widths"][width] += 1
                d["rules"][rule] += 1
                d["opcode_programs"][op].add(code_sha)
                d["form_programs"][key].add(code_sha)

    planned_programs = len(programs)
    if exact_programs != planned_programs:
        violations.append(f"exact_program_count:{exact_programs}!={planned_programs}")

    gate_summary = None
    if accounting_gate is not None:
        gate = json.loads(accounting_gate.read_text())
        if gate.get("schema") != GATE_SCHEMA:
            raise ValueError(f"unsupported accounting gate schema: {gate.get('schema')!r}")
        if gate.get("status") != "D1_GCN_STRUCTURAL_PARSE_ACCOUNTING_CORPUS_EXACT":
            violations.append(f"accounting_gate_not_exact:{gate.get('status')!r}")
        if gate.get("violations"):
            violations.append(f"accounting_gate_violations:{len(gate['violations'])}")
        gcov = gate.get("coverage") or {}
        gate_stage = gcov.get("stage_exact_unique_program_counts") or {}
        for stage_name in STAGES:
            expected = int(gate_stage.get(stage_name, -1))
            actual = len(stage_data[stage_name]["program_shas"])
            if expected != actual:
                violations.append(f"accounting_gate_stage_count:{stage_name}:{expected}!={actual}")
        if int(gcov.get("exact_parse_accounted_unique_gcn_programs", -1)) != exact_programs:
            violations.append(
                "accounting_gate_program_count:"
                f"{gcov.get('exact_parse_accounted_unique_gcn_programs')!r}!={exact_programs}"
            )
        gate_summary = {
            "status": gate.get("status"),
            "exact_parse_accounted_unique_gcn_programs": gcov.get(
                "exact_parse_accounted_unique_gcn_programs"
            ),
            "stage_exact_unique_program_counts": gate_stage,
        }

    ps = stage_data["PS"]
    vs = stage_data["VS"]
    ps_ops, vs_ops = set(ps["opcodes"]), set(vs["opcodes"])
    ps_forms, vs_forms = set(ps["forms"]), set(vs["forms"])

    baseline = src.get("baseline") or {}
    baseline_sha = str(baseline.get("gcn_sha256") or "").lower()
    baseline_ir = None
    if baseline_sha:
        p = ir_dir / f"{baseline_sha}.json"
        if p.is_file():
            baseline_ir = json.loads(p.read_text())
    if baseline_ir is None:
        violations.append(f"baseline_ir_missing:{baseline.get('header')}:{baseline_sha}")
        baseline_ops: set[str] = set()
        baseline_forms: set[tuple] = set()
    else:
        baseline_ops = {str(x["opcode"]) for x in baseline_ir.get("instructions") or []}
        baseline_forms = {census_lib.form_key(x) for x in baseline_ir.get("instructions") or []}

    promotion_queue = []
    for op in sorted((ps_ops | vs_ops) - baseline_ops):
        stages = [s for s in STAGES if op in stage_data[s]["opcodes"]]
        promotion_queue.append({
            "opcode": op,
            "stages": stages,
            "instruction_count": sum(int(stage_data[s]["opcodes"].get(op, 0)) for s in STAGES),
            "unique_stage_program_memberships": sum(
                len(stage_data[s]["opcode_programs"].get(op, set())) for s in STAGES
            ),
            "ps_program_count": len(ps["opcode_programs"].get(op, set())),
            "vs_program_count": len(vs["opcode_programs"].get(op, set())),
        })
    promotion_queue.sort(
        key=lambda x: (-x["unique_stage_program_memberships"], -x["instruction_count"], x["opcode"])
    )

    out = {
        "schema": "d1_gcn_shader_corpus_stage_frontier/v1",
        "status": OUTPUT_STATUS if not violations else "D1_GCN_SHADER_CORPUS_STAGE_FRONTIER_WITH_VIOLATIONS",
        "source_census": str(census_path),
        "source_accounting_gate": None if accounting_gate is None else str(accounting_gate),
        "accounting_gate_summary": gate_summary,
        "coverage": {
            "planned_unique_gcn_programs": planned_programs,
            "exact_unique_gcn_programs": exact_programs,
            "ps_unique_programs": len(ps["program_shas"]),
            "vs_unique_programs": len(vs["program_shas"]),
            "exact_code_sha_shared_by_ps_and_vs": len(shared_program_shas),
            "header_stage_mappings": len(header_owner),
        },
        "baseline": {
            "header": baseline.get("header"),
            "gcn_sha256": baseline_sha or None,
            "opcode_count": len(baseline_ops),
            "structural_form_count": len(baseline_forms),
        },
        "stages": {s: _stage_payload(stage_data[s]) for s in STAGES},
        "cross_stage": {
            "common_opcodes": sorted(ps_ops & vs_ops),
            "ps_only_opcodes": sorted(ps_ops - vs_ops),
            "vs_only_opcodes": sorted(vs_ops - ps_ops),
            "common_structural_form_count": len(ps_forms & vs_forms),
            "ps_only_structural_form_count": len(ps_forms - vs_forms),
            "vs_only_structural_form_count": len(vs_forms - ps_forms),
            "ps_only_structural_forms": _form_rows(ps_forms - vs_forms, ps, vs),
            "vs_only_structural_forms": _form_rows(vs_forms - ps_forms, ps, vs),
        },
        "frontier_vs_808ee505_baseline": {
            "novel_opcode_count": len((ps_ops | vs_ops) - baseline_ops),
            "novel_structural_form_count": len((ps_forms | vs_forms) - baseline_forms),
            "opcode_promotion_queue": promotion_queue,
        },
        "violations": violations,
        "policy": (
            "Stage membership comes only from the exact recovered corpus. Every counted "
            "program must already carry exact native-line Structural IR parse accounting. "
            "Stage-exclusive/common opcode and operand-form facts are structural evidence only; "
            "semantic promotion remains a separate source-backed gate."
        ),
    }
    return out


def self_test() -> None:
    def ins(index: int, address: int, opcode: str, operands: list[str], defs: list[str], uses: list[str]) -> dict:
        return {
            "index": index,
            "address": address,
            "address_hex": f"{address:012X}",
            "encoding_words": [f"{index + 1:08x}"],
            "encoding_hex": f"{index + 1:08x}",
            "byte_size": 4,
            "source_line": index + 1,
            "labels": [],
            "opcode": opcode,
            "operands": operands,
            "defs": defs,
            "uses": uses,
            "branch_target_label": None,
            "assembly": opcode + (" " + ", ".join(operands) if operands else ""),
        }

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        ir_dir = root / "ir"
        ir_dir.mkdir()
        ps_sha = "1" * 64
        vs_sha = "2" * 64
        ps_ins = [ins(0, 0, "image_sample", ["v0", "v1"], ["v0"], ["v1"]), ins(1, 4, "s_endpgm", [], [], [])]
        vs_ins = [ins(0, 0, "exp", ["param0", "v0"], [], ["v0"]), ins(1, 4, "s_endpgm", [], [], [])]
        for sha, shader, rows in ((ps_sha, "808EE505", ps_ins), (vs_sha, "8087695B", vs_ins)):
            ir = {
                "schema_version": 2,
                "status": IR_STATUS,
                "shader": shader,
                "parse_accounting": {
                    "status": structural.PARSE_ACCOUNTING_STATUS,
                    "native_instruction_line_count": len(rows),
                    "ir_instruction_count": len(rows),
                    "encoded_byte_count": 8,
                    "unaccounted_native_instruction_line_count": 0,
                    "duplicate_ir_instruction_count": 0,
                },
                "instruction_count": len(rows),
                "instructions": rows,
            }
            (ir_dir / f"{sha}.json").write_text(json.dumps(ir))
        census = {
            "schema": CENSUS_SCHEMA,
            "status": "D1_GCN_SHADER_CORPUS_STRUCTURAL_CENSUS_COMPLETE",
            "violations": [],
            "baseline": {"header": "808EE505", "gcn_sha256": ps_sha},
            "programs": [
                {"gcn_sha256": ps_sha, "gcn_bytes": 8, "stages": ["PS"], "headers": [{"stage": "PS", "header": "808EE505"}], "violations": []},
                {"gcn_sha256": vs_sha, "gcn_bytes": 8, "stages": ["VS"], "headers": [{"stage": "VS", "header": "8087695B"}], "violations": []},
            ],
        }
        cp = root / "census.json"
        cp.write_text(json.dumps(census))
        out = build(cp, ir_dir)
        assert out["status"] == OUTPUT_STATUS, out["violations"]
        assert out["coverage"]["exact_unique_gcn_programs"] == 2
        assert out["stages"]["PS"]["instruction_count"] == 2
        assert out["stages"]["VS"]["instruction_count"] == 2
        assert out["cross_stage"]["common_opcodes"] == ["s_endpgm"]
        assert out["cross_stage"]["ps_only_opcodes"] == ["image_sample"]
        assert out["cross_stage"]["vs_only_opcodes"] == ["exp"]
        assert out["frontier_vs_808ee505_baseline"]["opcode_promotion_queue"][0]["opcode"] == "exp"
    print("D1_GCN_SHADER_CORPUS_STAGE_FRONTIER_SELF_TEST_OK")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--census", type=Path)
    ap.add_argument("--ir-dir", type=Path)
    ap.add_argument("--accounting-gate", type=Path)
    ap.add_argument("-o", "--output", type=Path)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        self_test()
        return 0
    if a.census is None or a.ir_dir is None or a.output is None:
        ap.error("--census, --ir-dir and --output are required unless --self-test is used")
    out = build(a.census, a.ir_dir, a.accounting_gate)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n")
    print(
        "STATUS", out["status"],
        "PROGRAMS", f"{out['coverage']['exact_unique_gcn_programs']}/{out['coverage']['planned_unique_gcn_programs']}",
        "PS", out["coverage"]["ps_unique_programs"],
        "VS", out["coverage"]["vs_unique_programs"],
        "SHARED", out["coverage"]["exact_code_sha_shared_by_ps_and_vs"],
        "PS_ONLY_OPS", len(out["cross_stage"]["ps_only_opcodes"]),
        "VS_ONLY_OPS", len(out["cross_stage"]["vs_only_opcodes"]),
        "NOVEL_OPS", out["frontier_vs_808ee505_baseline"]["novel_opcode_count"],
        "VIOLATIONS", len(out["violations"]),
    )
    for v in out["violations"][:200]:
        print("VIOLATION", v)
    return 0 if out["status"] == OUTPUT_STATUS else 2


if __name__ == "__main__":
    raise SystemExit(main())
