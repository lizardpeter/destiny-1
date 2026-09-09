#!/usr/bin/env python3
"""Inventory the exact game-wide GFX7 EXEC-mask structural frontier.

This pass intentionally stops below symbolic EXEC dataflow. It consumes a completed
Structural IR corpus and enumerates every instruction that structurally reads, writes,
or branches on EXEC. The result is the finite opcode/form frontier that must receive
source-backed transfer semantics before divergent VGPR output lifting can be promoted.

The frontier itself can be exact even when some EXEC-touching opcode families are not
yet semantically promoted. Unsupported families are reported explicitly rather than
silently approximated.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import tempfile
from pathlib import Path

import d1_gcn_cfg_ir_v2 as structural

CENSUS_SCHEMA = "d1_gcn_shader_corpus_structural_census/v1"
IR_STATUS = "D1_GCN_STRUCTURAL_IR_COMPLETE"
OUTPUT_STATUS = "D1_GCN_EXEC_MASK_OPCODE_FRONTIER_EXACT"
SHA_RE = re.compile(r"^[0-9a-f]{64}$")

# GFX7 structural families whose EXEC behavior is directly specified by AMD's
# Southern/Sea Islands ISA. Presence here is not itself semantic dataflow closure.
SAVEEXEC_B64 = {
    "s_and_saveexec_b64",
    "s_andn2_saveexec_b64",
    "s_nand_saveexec_b64",
    "s_nor_saveexec_b64",
    "s_or_saveexec_b64",
    "s_orn2_saveexec_b64",
    "s_xnor_saveexec_b64",
    "s_xor_saveexec_b64",
}
EXEC_SCALAR_B64 = {
    "s_mov_b64",
    "s_not_b64",
    "s_and_b64",
    "s_andn2_b64",
    "s_nand_b64",
    "s_nor_b64",
    "s_or_b64",
    "s_orn2_b64",
    "s_xnor_b64",
    "s_xor_b64",
    "s_wqm_b64",
}
EXEC_BRANCH = {"s_cbranch_execz", "s_cbranch_execnz"}
KNOWN_STRUCTURAL_FAMILIES = SAVEEXEC_B64 | EXEC_SCALAR_B64 | EXEC_BRANCH


def has_exec(values: object) -> bool:
    if isinstance(values, str):
        return values == "exec" or values.startswith("exec_") or "exec" in values.lower()
    if isinstance(values, list):
        return any(has_exec(x) for x in values)
    return False


def touch_kind(ins: dict) -> str | None:
    op = str(ins.get("opcode", ""))
    defs = ins.get("defs") or []
    uses = ins.get("uses") or []
    operands = ins.get("operands") or []
    writes = has_exec(defs)
    reads = has_exec(uses)
    mentions = has_exec(operands)
    if op in EXEC_BRANCH:
        return "EXEC_BRANCH_TEST"
    if op in SAVEEXEC_B64:
        return "SAVEEXEC_MUTATION"
    if writes:
        return "EXEC_WRITE"
    if reads:
        return "EXEC_READ"
    if mentions:
        return "EXEC_OPERAND_MENTION"
    return None


def build(census_path: Path, ir_dir: Path) -> dict:
    census = json.loads(census_path.read_text())
    violations: list[str] = []
    if census.get("schema") != CENSUS_SCHEMA:
        raise ValueError(f"unsupported census schema: {census.get('schema')!r}")
    if census.get("status") != "D1_GCN_SHADER_CORPUS_STRUCTURAL_CENSUS_COMPLETE":
        violations.append(f"census_not_complete:{census.get('status')!r}")
    if census.get("violations"):
        violations.append(f"source_census_violations:{len(census['violations'])}")

    op_counts = collections.Counter()
    kind_counts = collections.Counter()
    op_programs: dict[str, set[str]] = collections.defaultdict(set)
    stage_programs: dict[str, set[str]] = collections.defaultdict(set)
    touch_programs: set[str] = set()
    rows: list[dict] = []
    exact_programs = 0
    total_instructions = 0
    total_exec_touches = 0

    for rec in census.get("programs") or []:
        sha = str(rec.get("gcn_sha256", "")).lower()
        if not SHA_RE.fullmatch(sha):
            violations.append(f"invalid_program_sha:{sha!r}")
            continue
        p = ir_dir / f"{sha}.json"
        if not p.is_file():
            violations.append(f"structural_ir_missing:{sha}")
            continue
        try:
            ir = json.loads(p.read_text())
        except Exception as exc:
            violations.append(f"structural_ir_json:{sha}:{type(exc).__name__}:{exc}")
            continue
        row_violations = []
        if ir.get("status") != IR_STATUS:
            row_violations.append(f"ir_status:{ir.get('status')!r}")
        pa = ir.get("parse_accounting") or {}
        if pa.get("status") != structural.PARSE_ACCOUNTING_STATUS:
            row_violations.append(f"parse_accounting:{pa.get('status')!r}")
        ins = ir.get("instructions") or []
        if int(ir.get("instruction_count", -1)) != len(ins):
            row_violations.append("instruction_count_mismatch")
        if int(pa.get("ir_instruction_count", -1)) != len(ins):
            row_violations.append("accounted_instruction_count_mismatch")
        if int(pa.get("unaccounted_native_instruction_line_count", -1)) != 0:
            row_violations.append("unaccounted_native_instruction_lines")
        if int(pa.get("duplicate_ir_instruction_count", -1)) != 0:
            row_violations.append("duplicate_ir_instructions")
        if rec.get("violations"):
            row_violations.append(f"census_program_violations:{len(rec['violations'])}")
        if row_violations:
            violations.extend(f"{sha}:{x}" for x in row_violations)
            continue

        exact_programs += 1
        total_instructions += len(ins)
        stages = sorted({str(x).upper() for x in (rec.get("stages") or [])})
        touches = []
        for x in ins:
            kind = touch_kind(x)
            if kind is None:
                continue
            op = str(x["opcode"])
            entry = {
                "instruction": int(x["index"]),
                "address": x["address_hex"],
                "opcode": op,
                "kind": kind,
                "operands": x.get("operands") or [],
                "defs": x.get("defs") or [],
                "uses": x.get("uses") or [],
                "known_gfx7_exec_family": op in KNOWN_STRUCTURAL_FAMILIES,
            }
            touches.append(entry)
            op_counts[op] += 1
            kind_counts[kind] += 1
            op_programs[op].add(sha)
            total_exec_touches += 1
        if touches:
            touch_programs.add(sha)
            for stage in stages:
                stage_programs[stage].add(sha)
            rows.append({
                "gcn_sha256": sha,
                "gcn_bytes": int(rec.get("gcn_bytes", 0)),
                "stages": stages,
                "headers": rec.get("headers") or [],
                "exec_touch_count": len(touches),
                "exec_touches": touches,
            })

    planned = len(census.get("programs") or [])
    if exact_programs != planned:
        violations.append(f"exact_program_count:{exact_programs}!={planned}")

    op_rows = []
    for op in sorted(op_counts):
        op_rows.append({
            "opcode": op,
            "instruction_count": int(op_counts[op]),
            "program_count": len(op_programs[op]),
            "known_gfx7_exec_family": op in KNOWN_STRUCTURAL_FAMILIES,
        })
    unknown = sorted(op for op in op_counts if op not in KNOWN_STRUCTURAL_FAMILIES)

    return {
        "schema": "d1_gcn_exec_mask_opcode_frontier/v1",
        "status": OUTPUT_STATUS if not violations else "D1_GCN_EXEC_MASK_OPCODE_FRONTIER_WITH_VIOLATIONS",
        "source_census": str(census_path),
        "coverage": {
            "planned_unique_gcn_programs": planned,
            "exact_unique_gcn_programs": exact_programs,
            "total_structural_instructions": total_instructions,
            "exec_touching_unique_programs": len(touch_programs),
            "exec_touching_instruction_count": total_exec_touches,
            "exec_touching_opcode_count": len(op_counts),
            "stage_exec_touching_unique_program_counts": {
                k: len(v) for k, v in sorted(stage_programs.items())
            },
        },
        "touch_kinds": [
            {"kind": k, "instruction_count": int(kind_counts[k])}
            for k in sorted(kind_counts)
        ],
        "opcodes": op_rows,
        "unknown_exec_touching_opcodes": unknown,
        "known_gfx7_structural_families": {
            "saveexec_b64": sorted(SAVEEXEC_B64),
            "scalar_b64_exec": sorted(EXEC_SCALAR_B64),
            "exec_branch": sorted(EXEC_BRANCH),
        },
        "programs": rows,
        "violations": violations,
        "semantic_boundary": {
            "exec_opcode_frontier": "EXACT" if not violations else "WITH_VIOLATIONS",
            "symbolic_exec_expression_dataflow": "NOT_YET_PROMOTED",
            "divergent_vgpr_ssa": "NOT_YET_PROMOTED",
            "output_expression_lifting": "WITHHELD_UNTIL_EXEC_MASK_DATAFLOW",
        },
        "source_semantics": {
            "architecture": "AMD GFX7 / Southern-Sea Islands",
            "references": [
                "AMD Southern Islands Instruction Set Architecture",
                "AMD Sea Islands Instruction Set Architecture",
                "LLVM AMDGPU GFX7 instruction syntax",
            ],
            "note": (
                "Known-family classification identifies instructions whose architectural EXEC "
                "behavior is documented. It does not claim that inter-block symbolic mask "
                "dataflow has already been solved."
            ),
        },
        "policy": (
            "Every EXEC read/write/branch is selected only from exact parse-accounted Structural "
            "IR. Unknown EXEC-touching opcode families remain explicit frontier items. No VGPR "
            "SSA or output expression is promoted from this inventory alone."
        ),
    }


def self_test() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        ir_dir = root / "ir"
        ir_dir.mkdir()
        ps_sha = "1" * 64
        vs_sha = "2" * 64

        def ins(i, op, operands, defs, uses):
            return {
                "index": i,
                "address": i * 4,
                "address_hex": f"{i*4:012X}",
                "encoding_hex": f"{i+1:08x}",
                "byte_size": 4,
                "opcode": op,
                "operands": operands,
                "defs": defs,
                "uses": uses,
            }

        ps_ins = [
            ins(0, "v_cmp_gt_f32", ["vcc", "v0", "v1"], ["vcc"], ["v0", "v1"]),
            ins(1, "s_and_saveexec_b64", ["s[0:1]", "vcc"], ["s0", "s1", "exec"], ["vcc", "exec"]),
            ins(2, "s_cbranch_execz", [".Ldone"], [], ["exec"]),
            ins(3, "s_or_b64", ["exec", "exec", "s[0:1]"], ["exec"], ["exec", "s0", "s1"]),
            ins(4, "s_endpgm", [], [], []),
        ]
        vs_ins = [ins(0, "s_endpgm", [], [], [])]
        for sha, shader, rows in ((ps_sha, "808768B7", ps_ins), (vs_sha, "8087695B", vs_ins)):
            ir = {
                "schema_version": 2,
                "status": IR_STATUS,
                "shader": shader,
                "instruction_count": len(rows),
                "parse_accounting": {
                    "status": structural.PARSE_ACCOUNTING_STATUS,
                    "native_instruction_line_count": len(rows),
                    "ir_instruction_count": len(rows),
                    "encoded_byte_count": len(rows) * 4,
                    "unaccounted_native_instruction_line_count": 0,
                    "duplicate_ir_instruction_count": 0,
                },
                "instructions": rows,
            }
            (ir_dir / f"{sha}.json").write_text(json.dumps(ir))
        census = {
            "schema": CENSUS_SCHEMA,
            "status": "D1_GCN_SHADER_CORPUS_STRUCTURAL_CENSUS_COMPLETE",
            "violations": [],
            "programs": [
                {"gcn_sha256": ps_sha, "gcn_bytes": 20, "stages": ["PS"], "headers": [{"stage": "PS", "header": "808768B7"}], "violations": []},
                {"gcn_sha256": vs_sha, "gcn_bytes": 4, "stages": ["VS"], "headers": [{"stage": "VS", "header": "8087695B"}], "violations": []},
            ],
        }
        cp = root / "census.json"
        cp.write_text(json.dumps(census))
        out = build(cp, ir_dir)
        assert out["status"] == OUTPUT_STATUS, out["violations"]
        assert out["coverage"]["exec_touching_instruction_count"] == 3
        assert out["coverage"]["exec_touching_unique_programs"] == 1
        assert [x["opcode"] for x in out["opcodes"]] == [
            "s_and_saveexec_b64", "s_cbranch_execz", "s_or_b64"
        ]
        assert not out["unknown_exec_touching_opcodes"]
        assert out["semantic_boundary"]["symbolic_exec_expression_dataflow"] == "NOT_YET_PROMOTED"
    print("D1_GCN_EXEC_MASK_OPCODE_FRONTIER_SELF_TEST_OK")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--census", type=Path)
    ap.add_argument("--ir-dir", type=Path)
    ap.add_argument("-o", "--output", type=Path)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        self_test()
        return 0
    if a.census is None or a.ir_dir is None or a.output is None:
        ap.error("--census, --ir-dir and --output are required unless --self-test is used")
    out = build(a.census, a.ir_dir)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n")
    print(
        "STATUS", out["status"],
        "PROGRAMS", f"{out['coverage']['exact_unique_gcn_programs']}/{out['coverage']['planned_unique_gcn_programs']}",
        "EXEC_PROGRAMS", out['coverage']['exec_touching_unique_programs'],
        "EXEC_INSTRUCTIONS", out['coverage']['exec_touching_instruction_count'],
        "EXEC_OPCODES", out['coverage']['exec_touching_opcode_count'],
        "UNKNOWN_OPCODES", len(out['unknown_exec_touching_opcodes']),
        "VIOLATIONS", len(out['violations']),
    )
    for op in out["unknown_exec_touching_opcodes"]:
        print("UNKNOWN_EXEC_OPCODE", op)
    for v in out["violations"][:200]:
        print("VIOLATION", v)
    return 0 if out["status"] == OUTPUT_STATUS else 2


if __name__ == "__main__":
    raise SystemExit(main())
