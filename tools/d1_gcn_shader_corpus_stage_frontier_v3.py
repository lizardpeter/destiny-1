#!/usr/bin/env python3
"""Build the exact PS/VS/DS GFX7 structural stage frontier for Destiny 1.

Unlike the historical PS/VS frontier, this implementation treats DomainShader as a
first-class stage. It consumes only a complete parse-accounted structural census and
compares exact opcode and normalized operand/def-use forms by OrbShdr-derived stage.
The result is prioritization evidence, not semantic promotion.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import tempfile
from pathlib import Path

import d1_gcn_cfg_ir_v2 as structural
import d1_gcn_shader_corpus_structural_census as census_lib
from d1_gcn_shader_corpus_structural_census_v3 import fixed_reg_kind

CENSUS_SCHEMA = "d1_gcn_shader_corpus_structural_census/v1"
IR_STATUS = "D1_GCN_STRUCTURAL_IR_COMPLETE"
ACCOUNTING_GATE_SCHEMA = "d1_gcn_structural_parse_accounting_gate/v1"
ACCOUNTING_GATE_STATUS = "D1_GCN_STRUCTURAL_PARSE_ACCOUNTING_CORPUS_EXACT"
OUTPUT_STATUS = "D1_GCN_SHADER_CORPUS_STAGE_FRONTIER_PS_VS_DS_EXACT"
STAGES = ("PS", "VS", "DS")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")


def _stage() -> dict:
    return {
        "programs": set(),
        "code_bytes": 0,
        "instructions": 0,
        "opcodes": collections.Counter(),
        "forms": collections.Counter(),
        "opcode_programs": collections.defaultdict(set),
        "form_programs": collections.defaultdict(set),
    }


def _stage_payload(d: dict) -> dict:
    return {
        "unique_program_count": len(d["programs"]),
        "exact_code_bytes": int(d["code_bytes"]),
        "instruction_count": int(d["instructions"]),
        "opcode_count": len(d["opcodes"]),
        "structural_form_count": len(d["forms"]),
        "opcodes": [
            {
                "opcode": op,
                "instruction_count": int(d["opcodes"][op]),
                "program_count": len(d["opcode_programs"][op]),
            }
            for op in sorted(d["opcodes"])
        ],
    }


def _form_row(key: tuple, ds: dict[str, dict]) -> dict:
    row = census_lib.form_payload(key)
    row["stages"] = [s for s in STAGES if key in ds[s]["forms"]]
    row["stage_instruction_counts"] = {
        s: int(ds[s]["forms"].get(key, 0)) for s in STAGES if key in ds[s]["forms"]
    }
    row["stage_program_counts"] = {
        s: len(ds[s]["form_programs"].get(key, set())) for s in STAGES if key in ds[s]["forms"]
    }
    return row


def build(census_path: Path, ir_dir: Path, accounting_gate: Path | None = None) -> dict:
    census_lib.reg_kind = fixed_reg_kind
    src = json.loads(census_path.read_text())
    violations: list[str] = []
    if src.get("schema") != CENSUS_SCHEMA:
        raise ValueError(f"unsupported census schema: {src.get('schema')!r}")
    if src.get("status") != "D1_GCN_SHADER_CORPUS_STRUCTURAL_CENSUS_COMPLETE":
        violations.append(f"census_status:{src.get('status')!r}")
    if src.get("violations"):
        violations.append(f"census_violations:{len(src['violations'])}")

    data = {s: _stage() for s in STAGES}
    exact_programs = 0
    all_shas: set[str] = set()
    multi_stage_shas: set[str] = set()

    for rec in src.get("programs") or []:
        sha = str(rec.get("gcn_sha256", "")).lower()
        nbytes = int(rec.get("gcn_bytes", 0))
        stages = sorted({str(x).upper() for x in (rec.get("stages") or [])})
        rv = []
        if not SHA_RE.fullmatch(sha):
            rv.append("invalid_sha")
        if nbytes <= 0:
            rv.append(f"invalid_bytes:{nbytes}")
        if not stages or any(s not in STAGES for s in stages):
            rv.append(f"invalid_stages:{stages}")
        if rec.get("violations"):
            rv.append(f"census_program_violations:{len(rec['violations'])}")

        p = ir_dir / f"{sha}.json"
        ir = None
        if not p.is_file():
            rv.append("ir_missing")
        else:
            try:
                ir = json.loads(p.read_text())
            except Exception as exc:
                rv.append(f"ir_json:{type(exc).__name__}:{exc}")
        if ir is not None:
            if ir.get("status") != IR_STATUS:
                rv.append(f"ir_status:{ir.get('status')!r}")
            ins = ir.get("instructions") or []
            pa = ir.get("parse_accounting") or {}
            if pa.get("status") != structural.PARSE_ACCOUNTING_STATUS:
                rv.append(f"parse_accounting_status:{pa.get('status')!r}")
            checks = {
                "native_instruction_line_count": len(ins),
                "ir_instruction_count": len(ins),
                "encoded_byte_count": nbytes,
                "unaccounted_native_instruction_line_count": 0,
                "duplicate_ir_instruction_count": 0,
            }
            for k, expected in checks.items():
                if pa.get(k) != expected:
                    rv.append(f"parse_accounting_{k}:{pa.get(k)!r}!={expected!r}")
            if int(ir.get("instruction_count", -1)) != len(ins):
                rv.append("instruction_count_mismatch")

        if rv:
            violations.extend(f"{sha}:{x}" for x in rv)
            continue
        assert ir is not None
        exact_programs += 1
        all_shas.add(sha)
        if len(stages) > 1:
            multi_stage_shas.add(sha)
        rows = ir["instructions"]
        for stage in stages:
            d = data[stage]
            d["programs"].add(sha)
            d["code_bytes"] += nbytes
            d["instructions"] += len(rows)
            for ins in rows:
                op = str(ins["opcode"])
                key = census_lib.form_key(ins)
                d["opcodes"][op] += 1
                d["forms"][key] += 1
                d["opcode_programs"][op].add(sha)
                d["form_programs"][key].add(sha)

    planned = len(src.get("programs") or [])
    if exact_programs != planned:
        violations.append(f"exact_program_count:{exact_programs}!={planned}")
    for stage in STAGES:
        if not data[stage]["programs"]:
            violations.append(f"stage_absent:{stage}")

    gate_summary = None
    if accounting_gate is not None:
        gate = json.loads(accounting_gate.read_text())
        if gate.get("schema") != ACCOUNTING_GATE_SCHEMA:
            raise ValueError(f"unsupported accounting gate: {gate.get('schema')!r}")
        if gate.get("status") != ACCOUNTING_GATE_STATUS or gate.get("violations"):
            violations.append(f"accounting_gate_not_exact:{gate.get('status')!r}")
        cov = gate.get("coverage") or {}
        exact_counts = cov.get("stage_exact_unique_program_counts") or {}
        for stage in STAGES:
            actual = len(data[stage]["programs"])
            expected = int(exact_counts.get(stage, -1))
            if actual != expected:
                violations.append(f"gate_stage_count:{stage}:{expected}!={actual}")
        if int(cov.get("exact_parse_accounted_unique_gcn_programs", -1)) != exact_programs:
            violations.append("gate_program_count_mismatch")
        gate_summary = {
            "status": gate.get("status"),
            "stage_exact_unique_program_counts": exact_counts,
            "exact_parse_accounted_unique_gcn_programs": cov.get("exact_parse_accounted_unique_gcn_programs"),
        }

    op_sets = {s: set(data[s]["opcodes"]) for s in STAGES}
    form_sets = {s: set(data[s]["forms"]) for s in STAGES}
    union_ops = set().union(*op_sets.values())
    union_forms = set().union(*form_sets.values())
    all_common_ops = set.intersection(*(op_sets[s] for s in STAGES))
    all_common_forms = set.intersection(*(form_sets[s] for s in STAGES))

    opcode_membership = []
    for op in sorted(union_ops):
        stages = [s for s in STAGES if op in op_sets[s]]
        opcode_membership.append({
            "opcode": op,
            "stages": stages,
            "stage_instruction_counts": {s: int(data[s]["opcodes"][op]) for s in stages},
            "stage_program_counts": {s: len(data[s]["opcode_programs"][op]) for s in stages},
        })

    pairwise = {}
    for a, b in (("PS", "VS"), ("PS", "DS"), ("VS", "DS")):
        pairwise[f"{a}_{b}"] = {
            "common_opcode_count": len(op_sets[a] & op_sets[b]),
            "a_only_opcode_count": len(op_sets[a] - op_sets[b]),
            "b_only_opcode_count": len(op_sets[b] - op_sets[a]),
            "common_structural_form_count": len(form_sets[a] & form_sets[b]),
        }

    baseline = src.get("baseline") or {}
    baseline_sha = str(baseline.get("gcn_sha256") or "").lower()
    baseline_ops: set[str] = set()
    baseline_forms: set[tuple] = set()
    bp = ir_dir / f"{baseline_sha}.json"
    if not baseline_sha or not bp.is_file():
        violations.append(f"baseline_ir_missing:{baseline.get('header')}:{baseline_sha}")
    else:
        bir = json.loads(bp.read_text())
        baseline_ops = {str(x["opcode"]) for x in (bir.get("instructions") or [])}
        baseline_forms = {census_lib.form_key(x) for x in (bir.get("instructions") or [])}

    queue = []
    for op in sorted(union_ops - baseline_ops):
        stages = [s for s in STAGES if op in op_sets[s]]
        queue.append({
            "opcode": op,
            "stages": stages,
            "instruction_count": sum(int(data[s]["opcodes"][op]) for s in stages),
            "stage_program_memberships": sum(len(data[s]["opcode_programs"][op]) for s in stages),
            "program_counts": {s: len(data[s]["opcode_programs"][op]) for s in stages},
        })
    queue.sort(key=lambda x: (-x["stage_program_memberships"], -x["instruction_count"], x["opcode"]))

    stage_exclusive_forms = {}
    for stage in STAGES:
        other = set().union(*(form_sets[s] for s in STAGES if s != stage))
        keys = form_sets[stage] - other
        stage_exclusive_forms[stage] = {
            "count": len(keys),
            "forms": [_form_row(k, data) for k in sorted(keys, key=str)],
        }

    return {
        "schema": "d1_gcn_shader_corpus_stage_frontier/v3",
        "status": OUTPUT_STATUS if not violations else "D1_GCN_SHADER_CORPUS_STAGE_FRONTIER_PS_VS_DS_WITH_VIOLATIONS",
        "source_census": str(census_path),
        "source_accounting_gate": None if accounting_gate is None else str(accounting_gate),
        "accounting_gate_summary": gate_summary,
        "coverage": {
            "planned_unique_gcn_programs": planned,
            "exact_unique_gcn_programs": exact_programs,
            "stage_unique_program_counts": {s: len(data[s]["programs"]) for s in STAGES},
            "multi_stage_exact_code_sha_count": len(multi_stage_shas),
        },
        "baseline": {
            "header": baseline.get("header"),
            "gcn_sha256": baseline_sha or None,
            "opcode_count": len(baseline_ops),
            "structural_form_count": len(baseline_forms),
        },
        "stages": {s: _stage_payload(data[s]) for s in STAGES},
        "cross_stage": {
            "all_three_common_opcodes": sorted(all_common_ops),
            "all_three_common_opcode_count": len(all_common_ops),
            "all_three_common_structural_form_count": len(all_common_forms),
            "stage_exclusive_opcodes": {
                s: sorted(op_sets[s] - set().union(*(op_sets[x] for x in STAGES if x != s)))
                for s in STAGES
            },
            "stage_exclusive_structural_forms": stage_exclusive_forms,
            "pairwise": pairwise,
            "opcode_stage_membership": opcode_membership,
        },
        "frontier_vs_808ee505_baseline": {
            "novel_opcode_count": len(union_ops - baseline_ops),
            "novel_structural_form_count": len(union_forms - baseline_forms),
            "opcode_promotion_queue": queue,
        },
        "violations": violations,
        "policy": (
            "PS, VS and DS membership comes only from the exact V3 OrbShdr-derived corpus. "
            "Every counted program must carry exact Structural IR native-line accounting. "
            "Stage-exclusive/common opcode and form evidence remains structural; semantic "
            "instruction and shader-expression promotion is a separate source-backed gate."
        ),
    }


def self_test() -> None:
    census_lib.reg_kind = fixed_reg_kind
    with tempfile.TemporaryDirectory() as td:
        root = Path(td); ir_dir = root / "ir"; ir_dir.mkdir()
        shas = {"PS": "1"*64, "VS": "2"*64, "DS": "3"*64}
        ops = {"PS": "image_sample", "VS": "exp", "DS": "v_interp_mov_f32"}
        programs = []
        for n, stage in enumerate(STAGES):
            rows = [
                {"index":0,"address":0,"address_hex":"000000000000","encoding_hex":"01000000","byte_size":4,"opcode":ops[stage],"operands":["v0"],"defs":["v0"],"uses":[],"branch_target_label":None},
                {"index":1,"address":4,"address_hex":"000000000004","encoding_hex":"02000000","byte_size":4,"opcode":"s_endpgm","operands":[],"defs":[],"uses":[],"branch_target_label":None},
            ]
            ir={"status":IR_STATUS,"instruction_count":2,"parse_accounting":{"status":structural.PARSE_ACCOUNTING_STATUS,"native_instruction_line_count":2,"ir_instruction_count":2,"encoded_byte_count":8,"unaccounted_native_instruction_line_count":0,"duplicate_ir_instruction_count":0},"instructions":rows}
            (ir_dir/f"{shas[stage]}.json").write_text(json.dumps(ir))
            programs.append({"gcn_sha256":shas[stage],"gcn_bytes":8,"stages":[stage],"headers":[{"stage":stage,"header":f"8000000{n+1}"}],"violations":[]})
        census={"schema":CENSUS_SCHEMA,"status":"D1_GCN_SHADER_CORPUS_STRUCTURAL_CENSUS_COMPLETE","violations":[],"baseline":{"header":"80000001","gcn_sha256":shas["PS"]},"programs":programs}
        cp=root/"census.json"; cp.write_text(json.dumps(census))
        out=build(cp,ir_dir)
        assert out["status"]==OUTPUT_STATUS,out["violations"]
        assert out["coverage"]["stage_unique_program_counts"]=={"PS":1,"VS":1,"DS":1}
        assert out["cross_stage"]["all_three_common_opcodes"]==["s_endpgm"]
        assert out["cross_stage"]["stage_exclusive_opcodes"]["DS"]==["v_interp_mov_f32"]
        assert {x["opcode"] for x in out["frontier_vs_808ee505_baseline"]["opcode_promotion_queue"]}=={"exp","v_interp_mov_f32"}
    print("D1_GCN_SHADER_CORPUS_STAGE_FRONTIER_V3_SELF_TEST_OK")


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--census",type=Path)
    ap.add_argument("--ir-dir",type=Path)
    ap.add_argument("--accounting-gate",type=Path)
    ap.add_argument("-o","--output",type=Path)
    ap.add_argument("--self-test",action="store_true")
    a=ap.parse_args()
    if a.self_test:
        self_test(); return 0
    if a.census is None or a.ir_dir is None or a.output is None:
        ap.error("--census, --ir-dir and --output required unless --self-test")
    out=build(a.census,a.ir_dir,a.accounting_gate)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2)+"\n")
    print("STATUS",out["status"],"PROGRAMS",out["coverage"],"NOVEL_OPS",out["frontier_vs_808ee505_baseline"]["novel_opcode_count"],"VIOLATIONS",len(out["violations"]))
    for v in out["violations"][:200]: print("VIOLATION",v)
    return 0 if out["status"]==OUTPUT_STATUS else 2


if __name__=="__main__":
    raise SystemExit(main())
