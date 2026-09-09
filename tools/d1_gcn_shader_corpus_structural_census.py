#!/usr/bin/env python3
"""Run the exact recovered D1 PS4 shader corpus through generic Structural IR.

This is the first game-wide *structural* coverage gate.  It is intentionally not a
semantic shader-solved percentage.  For each exact unique GCN code SHA-256 recovered
by ``d1_remote_ps4_shader_corpus_extract.py`` it:

  1. disassembles with a caller-pinned CLRX ``clrxdisasm`` in raw GFX700 mode;
  2. invokes the existing ``d1_gcn_cfg_ir_v2.py`` producer unchanged;
  3. proves instruction-address/encoding widths cover the exact OrbShdr-bounded code;
  4. censuses opcodes, exact encodings, encoding widths, structural operand forms,
     CFG/control-flow forms, and the producer's def/use classification rule;
  5. compares those facts to an exact baseline header (default 808EE505).

"Structural form" below is explicitly a normalized CLRX operand/def-use syntax form.
It is not promoted as an AMD ISA encoding-family name.  Unknown/new forms remain
machine-readable evidence for later source-correlated decoder work.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import d1_gcn_cfg_ir_v2 as structural

REG_RANGE_RE = re.compile(r"\b([vs])\[\d+:\d+\]")
REG_RE = re.compile(r"\b([vs])\d+\b")
ATTR_RE = re.compile(r"\battr\d+(\.[xyzw])?\b")
PARAM_RE = re.compile(r"\bparam\d+\b")
LABEL_RE = re.compile(r"\.L\w+")
HEX_RE = re.compile(r"(?<![A-Za-z0-9_])[-+]?0x[0-9A-Fa-f]+(?![A-Za-z0-9_])")
FLOAT_RE = re.compile(r"(?<![A-Za-z0-9_])[-+]?(?:\d+\.\d*|\.\d+)(?:[eE][-+]?\d+)?(?![A-Za-z0-9_])")
INT_RE = re.compile(r"(?<![A-Za-z0-9_])[-+]?\d+(?![A-Za-z0-9_])")


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(1 << 20)
            if not b:
                return h.hexdigest()
            h.update(b)


def normalized_operand(text: str) -> str:
    s = text
    s = REG_RANGE_RE.sub(lambda m: f"{m.group(1)}[#: #]".replace(" ", ""), s)
    s = REG_RE.sub(lambda m: f"{m.group(1)}#", s)
    s = ATTR_RE.sub(lambda m: "attr#" + (m.group(1) or ""), s)
    s = PARAM_RE.sub("param#", s)
    s = LABEL_RE.sub("LABEL", s)
    s = HEX_RE.sub("IMM_HEX", s)
    s = FLOAT_RE.sub("IMM_FLOAT", s)
    s = INT_RE.sub("IMM_INT", s)
    return s


def reg_kind(r: str) -> str:
    if r.startswith("v"):
        return "VGPR"
    if r.startswith("s") and r != "scc":
        return "SGPR"
    if r.startswith("vcc"):
        return "VCC"
    if r.startswith("exec"):
        return "EXEC"
    if r == "scc":
        return "SCC"
    if r == "m0":
        return "M0"
    return r.upper()


def classification_rule(row: dict) -> str:
    op = row["opcode"]
    a = row.get("operands") or []
    if not a:
        return "NO_OPERANDS"
    no_dest = (
        op in structural.TERMINAL
        or op in structural.UNCOND
        or op.startswith(structural.COND_PREFIX)
        or any(op.startswith(x) for x in structural.NO_DEST)
    )
    if no_dest:
        return "NO_DESTINATION"
    if op.startswith("s_cmp"):
        return "SCC_IMPLICIT_DESTINATION"
    if op in structural.VCC_SECOND_DEST and len(a) >= 2 and a[1].startswith("vcc"):
        if op in structural.VCC_CARRY_IN:
            return "EXPLICIT_VALUE_PLUS_VCC_DESTINATION_WITH_CARRY_CLASS"
        return "EXPLICIT_VALUE_PLUS_VCC_DESTINATION"
    if op.startswith(structural.RMW):
        return "GENERIC_FIRST_DESTINATION_READ_MODIFY_WRITE"
    return "GENERIC_FIRST_OPERAND_DESTINATION"


def form_key(row: dict) -> tuple:
    enc = str(row["encoding_hex"])
    return (
        row["opcode"],
        len(enc) // 2,
        tuple(normalized_operand(x) for x in (row.get("operands") or [])),
        tuple(reg_kind(x) for x in (row.get("defs") or [])),
        tuple(reg_kind(x) for x in (row.get("uses") or [])),
        bool(row.get("branch_target_label")),
        classification_rule(row),
    )


def form_payload(key: tuple) -> dict:
    op, width, operands, defs, uses, branch, rule = key
    return {
        "opcode": op,
        "encoding_width_bytes": width,
        "operand_syntax": list(operands),
        "def_kinds": list(defs),
        "use_kinds": list(uses),
        "has_branch_target": branch,
        "classification_rule": rule,
    }


def counter_rows(counter: collections.Counter, baseline: collections.Counter | None = None,
                 payload=lambda x: x) -> list[dict]:
    baseline = baseline or collections.Counter()
    rows = []
    for k in sorted(counter, key=lambda x: str(x)):
        v = payload(k)
        rec = dict(v) if isinstance(v, dict) else {"value": v}
        rec["count"] = int(counter[k])
        rec["baseline_count"] = int(baseline.get(k, 0))
        rec["novel_vs_baseline"] = k not in baseline
        rows.append(rec)
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--extract-report", type=Path, required=True)
    ap.add_argument("--program-dir", type=Path, required=True)
    ap.add_argument("--clrx", type=Path, required=True)
    ap.add_argument("--baseline-header", default="808EE505")
    ap.add_argument("--work-dir", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    src = json.loads(a.extract_report.read_text())
    if src.get("schema") != "d1_remote_ps4_shader_corpus_extract/v1":
        raise SystemExit(f"unsupported extract report: {src.get('schema')!r}")

    a.work_dir.mkdir(parents=True, exist_ok=True)
    disasm_dir = a.work_dir / "disasm"
    ir_dir = a.work_dir / "ir"
    stderr_dir = a.work_dir / "stderr"
    for p in (disasm_dir, ir_dir, stderr_dir):
        p.mkdir(parents=True, exist_ok=True)

    violations = list(src.get("violations") or [])
    programs = src.get("unique_gcn_programs") or []
    program_results: list[dict] = []
    ir_by_sha: dict[str, dict] = {}

    opcode_all = collections.Counter()
    encoding_all = collections.Counter()
    width_all = collections.Counter()
    forms_all = collections.Counter()
    rules_all = collections.Counter()
    cfg_forms_all = collections.Counter()

    for p in programs:
        code_sha = str(p["gcn_sha256"]).lower()
        code_bytes = int(p["gcn_bytes"])
        bin_path = a.program_dir / f"{code_sha}.bin"
        rec = {
            "gcn_sha256": code_sha,
            "gcn_bytes": code_bytes,
            "headers": p.get("headers") or [],
            "stages": p.get("stages") or [],
            "native_program_references": p.get("native_program_references") or [],
            "violations": [],
        }
        if not bin_path.is_file():
            rec["violations"].append("program_binary_missing")
            program_results.append(rec)
            violations.append(f"{code_sha}:program_binary_missing")
            continue
        got_sha = sha256_file(bin_path)
        if got_sha != code_sha:
            rec["violations"].append(f"program_sha256:{got_sha}!={code_sha}")
        if bin_path.stat().st_size != code_bytes:
            rec["violations"].append(
                f"program_size:{bin_path.stat().st_size}!={code_bytes}"
            )

        disasm_path = disasm_dir / f"{code_sha}.s"
        stderr_path = stderr_dir / f"{code_sha}.stderr"
        proc = subprocess.run(
            [str(a.clrx), "--raw", "--gpuType=GFX700", "--hexcode", str(bin_path)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        disasm_path.write_text(proc.stdout)
        stderr_path.write_text(proc.stderr)
        rec["clrx"] = {
            "returncode": proc.returncode,
            "stdout_file": str(disasm_path),
            "stderr_file": str(stderr_path),
            "stderr_bytes": len(proc.stderr.encode()),
            "contains_s_endpgm": "s_endpgm" in proc.stdout,
        }
        if proc.returncode != 0:
            rec["violations"].append(f"clrx_returncode:{proc.returncode}")
        if proc.stderr:
            rec["violations"].append("clrx_stderr_nonempty")
        if "s_endpgm" not in proc.stdout:
            rec["violations"].append("clrx_missing_s_endpgm")
        if rec["violations"]:
            violations.extend(f"{code_sha}:{x}" for x in rec["violations"])
            program_results.append(rec)
            continue

        representative = sorted(
            (x for x in rec["headers"] if x.get("header")),
            key=lambda x: (x.get("stage", ""), x["header"]),
        )[0]["header"]
        ir_path = ir_dir / f"{code_sha}.json"
        ir_proc = subprocess.run(
            [
                sys.executable, str(HERE / "d1_gcn_cfg_ir_v2.py"),
                "--disasm", str(disasm_path),
                "--shader", representative,
                "-o", str(ir_path),
            ],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        rec["structural_ir"] = {
            "representative_header": representative,
            "returncode": ir_proc.returncode,
            "file": str(ir_path),
            "stdout": ir_proc.stdout[-4000:],
            "stderr": ir_proc.stderr[-4000:],
        }
        if ir_proc.returncode != 0 or not ir_path.is_file():
            rec["violations"].append(f"structural_ir_returncode:{ir_proc.returncode}")
            violations.extend(f"{code_sha}:{x}" for x in rec["violations"])
            program_results.append(rec)
            continue

        ir = json.loads(ir_path.read_text())
        if ir.get("status") != "D1_GCN_STRUCTURAL_IR_COMPLETE":
            rec["violations"].append(f"structural_ir_status:{ir.get('status')}")
        ins = ir.get("instructions") or []
        if int(ir.get("instruction_count", -1)) != len(ins):
            rec["violations"].append("instruction_count_mismatch")
        if [x.get("index") for x in ins] != list(range(len(ins))):
            rec["violations"].append("instruction_indices_noncontiguous")

        byte_spans = []
        for i, row in enumerate(ins):
            enc = str(row.get("encoding_hex", ""))
            if not enc or len(enc) % 2 or any(c not in "0123456789abcdefABCDEF" for c in enc):
                rec["violations"].append(f"instruction_{i}:invalid_encoding_hex")
                continue
            addr = int(row["address"])
            width = len(enc) // 2
            byte_spans.append((addr, addr + width))
        if byte_spans:
            if byte_spans[0][0] != 0:
                rec["violations"].append(f"first_instruction_address:{byte_spans[0][0]}!=0")
            gaps = []
            for i in range(1, len(byte_spans)):
                if byte_spans[i][0] != byte_spans[i - 1][1]:
                    gaps.append({
                        "previous_end": byte_spans[i - 1][1],
                        "next_start": byte_spans[i][0],
                    })
            if gaps:
                rec["violations"].append(f"instruction_byte_gaps:{gaps[:10]}")
            represented_end = byte_spans[-1][1]
        else:
            represented_end = 0
            rec["violations"].append("no_structural_instructions")
        rec["byte_coverage"] = {
            "orbshdr_gcn_bytes": code_bytes,
            "represented_end": represented_end,
            "exact_full_coverage": represented_end == code_bytes and not any(
                "instruction_byte_gaps" in x for x in rec["violations"]
            ),
        }
        if represented_end != code_bytes:
            rec["violations"].append(
                f"instruction_bytes:{represented_end}!={code_bytes}"
            )

        op = collections.Counter(x["opcode"] for x in ins)
        encs = collections.Counter(str(x["encoding_hex"]).lower() for x in ins)
        widths = collections.Counter(len(str(x["encoding_hex"])) // 2 for x in ins)
        forms = collections.Counter(form_key(x) for x in ins)
        rules = collections.Counter(classification_rule(x) for x in ins)
        cfg_form = (
            int(ir.get("basic_block_count", 0)),
            int(ir.get("cfg_edge_count", 0)),
            len((ir.get("control_flow") or {}).get("back_edges") or []),
            int((ir.get("control_flow") or {}).get("conditional_branch_count", 0)),
            int((ir.get("control_flow") or {}).get("unconditional_branch_count", 0)),
            bool((ir.get("control_flow") or {}).get("divergent_exec_present")),
        )
        opcode_all.update(op)
        encoding_all.update(encs)
        width_all.update(widths)
        forms_all.update(forms)
        rules_all.update(rules)
        cfg_forms_all[cfg_form] += 1
        rec["instruction_count"] = len(ins)
        rec["opcode_count"] = len(op)
        rec["structural_form_count"] = len(forms)
        rec["classification_rule_counts"] = dict(sorted(rules.items()))
        rec["cfg_form"] = {
            "basic_blocks": cfg_form[0],
            "edges": cfg_form[1],
            "back_edge_count": cfg_form[2],
            "conditional_branch_count": cfg_form[3],
            "unconditional_branch_count": cfg_form[4],
            "divergent_exec_present": cfg_form[5],
        }
        if rec["violations"]:
            violations.extend(f"{code_sha}:{x}" for x in rec["violations"])
        else:
            ir_by_sha[code_sha] = ir
        program_results.append(rec)

    # Locate baseline by exact logical header -> exact code SHA.
    baseline_header = norm(a.baseline_header)
    baseline_sha = None
    for p in programs:
        if any(norm(x.get("header")) == baseline_header for x in p.get("headers") or []):
            baseline_sha = str(p["gcn_sha256"]).lower()
            break
    baseline_ir = ir_by_sha.get(baseline_sha) if baseline_sha else None
    baseline_violation = None
    if baseline_sha is None:
        baseline_violation = f"baseline_header_not_in_exact_corpus:{baseline_header}"
    elif baseline_ir is None:
        baseline_violation = f"baseline_structural_ir_not_complete:{baseline_header}:{baseline_sha}"
    if baseline_violation:
        violations.append(baseline_violation)

    base_op = collections.Counter()
    base_enc = collections.Counter()
    base_width = collections.Counter()
    base_forms = collections.Counter()
    base_rules = collections.Counter()
    if baseline_ir:
        for x in baseline_ir["instructions"]:
            base_op[x["opcode"]] += 1
            base_enc[str(x["encoding_hex"]).lower()] += 1
            base_width[len(str(x["encoding_hex"])) // 2] += 1
            base_forms[form_key(x)] += 1
            base_rules[classification_rule(x)] += 1

    # Annotate each complete program with its frontier relative to 808EE505.
    for rec in program_results:
        ir = ir_by_sha.get(rec["gcn_sha256"])
        if not ir or not baseline_ir:
            continue
        op = collections.Counter(x["opcode"] for x in ir["instructions"])
        forms = collections.Counter(form_key(x) for x in ir["instructions"])
        encs = collections.Counter(str(x["encoding_hex"]).lower() for x in ir["instructions"])
        rec["frontier_vs_baseline"] = {
            "novel_opcodes": sorted(set(op) - set(base_op)),
            "novel_structural_form_count": len(set(forms) - set(base_forms)),
            "novel_exact_encoding_count": len(set(encs) - set(base_enc)),
            "novel_generic_fallback_opcodes": sorted({
                x["opcode"] for x in ir["instructions"]
                if x["opcode"] not in base_op
                and classification_rule(x).startswith("GENERIC_FIRST_")
            }),
        }

    exact_programs = len(ir_by_sha)
    planned_programs = len(programs)
    complete_headers = {
        norm(x.get("header"))
        for p in programs if str(p["gcn_sha256"]).lower() in ir_by_sha
        for x in p.get("headers") or []
        if x.get("header")
    }
    exact_headers = sum(
        1 for h in src.get("headers") or []
        if h.get("header") and norm(h["header"]) in complete_headers
    )
    header_total = int((src.get("header_population") or {}).get("total", len(src.get("headers") or [])))
    exact_code_bytes = sum(
        int(p["gcn_bytes"]) for p in programs if str(p["gcn_sha256"]).lower() in ir_by_sha
    )
    total_code_bytes = sum(int(p["gcn_bytes"]) for p in programs)

    cfg_rows = []
    for key in sorted(cfg_forms_all):
        cfg_rows.append({
            "basic_blocks": key[0],
            "edges": key[1],
            "back_edge_count": key[2],
            "conditional_branch_count": key[3],
            "unconditional_branch_count": key[4],
            "divergent_exec_present": key[5],
            "program_count": cfg_forms_all[key],
        })

    out = {
        "schema": "d1_gcn_shader_corpus_structural_census/v1",
        "status": (
            "D1_GCN_SHADER_CORPUS_STRUCTURAL_CENSUS_COMPLETE"
            if not violations and exact_programs == planned_programs
            else "D1_GCN_SHADER_CORPUS_STRUCTURAL_CENSUS_WITH_VIOLATIONS"
        ),
        "source_extract_report": str(a.extract_report),
        "baseline": {
            "header": baseline_header,
            "gcn_sha256": baseline_sha,
            "structural_ir_complete": baseline_ir is not None,
            "instruction_count": None if baseline_ir is None else baseline_ir["instruction_count"],
        },
        "coverage": {
            "header_population_total": header_total,
            "headers_mapped_to_structurally_complete_program": exact_headers,
            "header_structural_coverage_fraction": (
                0.0 if not header_total else exact_headers / header_total
            ),
            "unique_exact_gcn_program_total": planned_programs,
            "structurally_complete_unique_gcn_programs": exact_programs,
            "unique_program_structural_coverage_fraction": (
                0.0 if not planned_programs else exact_programs / planned_programs
            ),
            "exact_gcn_code_bytes_total": total_code_bytes,
            "structurally_represented_exact_gcn_code_bytes": exact_code_bytes,
            "code_byte_structural_coverage_fraction": (
                0.0 if not total_code_bytes else exact_code_bytes / total_code_bytes
            ),
            "semantic_shader_solved_percentage": None,
            "semantic_percentage_withheld_reason": (
                "This checkpoint measures exact structural decoding only. Semantic "
                "promotion remains a separate proof gate."
            ),
        },
        "census": {
            "opcode_count": len(opcode_all),
            "instruction_count": sum(opcode_all.values()),
            "exact_encoding_count": len(encoding_all),
            "structural_form_count": len(forms_all),
            "encoding_widths": counter_rows(width_all, base_width, lambda x: {"bytes": x}),
            "classification_rules": counter_rows(rules_all, base_rules, lambda x: {"rule": x}),
            "opcodes": counter_rows(opcode_all, base_op, lambda x: {"opcode": x}),
            "exact_encodings": counter_rows(
                encoding_all, base_enc, lambda x: {
                    "encoding_hex": x, "encoding_width_bytes": len(x) // 2
                }
            ),
            "structural_forms": counter_rows(forms_all, base_forms, form_payload),
            "cfg_forms": cfg_rows,
            "novel_vs_baseline": {
                "opcode_count": len(set(opcode_all) - set(base_op)),
                "opcodes": sorted(set(opcode_all) - set(base_op)),
                "exact_encoding_count": len(set(encoding_all) - set(base_enc)),
                "structural_form_count": len(set(forms_all) - set(base_forms)),
                "encoding_widths": sorted(set(width_all) - set(base_width)),
                "classification_rules": sorted(set(rules_all) - set(base_rules)),
                "generic_fallback_opcodes": sorted({
                    x["opcode"]
                    for ir in ir_by_sha.values()
                    for x in ir["instructions"]
                    if x["opcode"] not in base_op
                    and classification_rule(x).startswith("GENERIC_FIRST_")
                }),
            },
        },
        "programs": program_results,
        "violations": violations,
        "policy": (
            "Coverage is exact only when OrbShdr-bounded GCN bytes are byte-for-byte "
            "accounted for by contiguous CLRX instruction encodings and the generic "
            "Structural IR producer returns D1_GCN_STRUCTURAL_IR_COMPLETE. Novelty is "
            "reported against the exact logical baseline header. Structural operand "
            "forms are normalized syntax facts, not invented AMD ISA family names."
        ),
    }

    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n")
    print(
        "STATUS", out["status"],
        "HEADERS", f"{exact_headers}/{header_total}",
        "PROGRAMS", f"{exact_programs}/{planned_programs}",
        "BYTES", f"{exact_code_bytes}/{total_code_bytes}",
        "OPCODES", len(opcode_all),
        "NOVEL_OPCODES", len(set(opcode_all) - set(base_op)),
        "FORMS", len(forms_all),
        "NOVEL_FORMS", len(set(forms_all) - set(base_forms)),
        "VIOLATIONS", len(violations),
    )
    return 0 if out["status"] == "D1_GCN_SHADER_CORPUS_STRUCTURAL_CENSUS_COMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
