#!/usr/bin/env python3
"""Replay an exact candidate D1 GCN corpus through the universal structural decoder.

This gate is stage-neutral. Candidate provenance/stage labels select exact binaries only;
they never alter GFX7 decoding. Every candidate is disassembled with caller-pinned CLRX,
lifted by d1_gcn_cfg_ir_v2.py unchanged, parse-accounted byte-for-byte, and compared to
a frozen structural census. Exact encoding values and whole-program CFG tuples may be new
instances; new opcodes, normalized instruction forms, widths, classification rules, or
malformed CFG are fail-closed architectural frontier evidence.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import d1_gcn_shader_corpus_structural_census as core
import d1_gcn_shader_corpus_structural_census_v3 as v3
import d1_gcn_cfg_ir_v2 as structural

MANIFEST_SCHEMA = "d1_gcn_structural_candidate_manifest/v1"
MANIFEST_STATUS = "D1_GCN_STRUCTURAL_CANDIDATE_MANIFEST_EXACT"
BASELINE_SCHEMA = "d1_gcn_shader_corpus_structural_census/v1"
BASELINE_STATUS = "D1_GCN_SHADER_CORPUS_STRUCTURAL_CENSUS_COMPLETE"
IR_STATUS = "D1_GCN_STRUCTURAL_IR_COMPLETE"
ACCOUNTING_STATUS = "D1_GCN_STRUCTURAL_PARSE_ACCOUNTING_EXACT"
SCHEMA = "d1_gcn_structural_candidate_compare/v1"
STATUS = "D1_GCN_STRUCTURAL_CANDIDATE_ARCHITECTURE_REPLAY_EXACT"

# Match the proven V3 global census register-class normalization exactly.
core.reg_kind = v3.fixed_reg_kind


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def baseline_form_key(row: dict) -> tuple:
    return (
        str(row["opcode"]),
        int(row["encoding_width_bytes"]),
        tuple(str(x) for x in row.get("operand_syntax") or []),
        tuple(str(x) for x in row.get("def_kinds") or []),
        tuple(str(x) for x in row.get("use_kinds") or []),
        bool(row.get("has_branch_target")),
        str(row["classification_rule"]),
    )


def cfg_signature(ir: dict) -> tuple:
    cf = ir.get("control_flow") or {}
    return (
        int(ir.get("basic_block_count", 0)),
        int(ir.get("cfg_edge_count", 0)),
        len(cf.get("back_edges") or []),
        int(cf.get("conditional_branch_count", 0)),
        int(cf.get("unconditional_branch_count", 0)),
        bool(cf.get("divergent_exec_present")),
    )


def baseline_cfg_key(row: dict) -> tuple:
    return (
        int(row["basic_blocks"]), int(row["edges"]), int(row["back_edge_count"]),
        int(row["conditional_branch_count"]), int(row["unconditional_branch_count"]),
        bool(row["divergent_exec_present"]),
    )


def validate_cfg(ir: dict) -> list[str]:
    violations: list[str] = []
    ins = ir.get("instructions") or []
    blocks = ir.get("basic_blocks") or []
    if [b.get("id") for b in blocks] != list(range(len(blocks))):
        violations.append("cfg_block_ids_noncontiguous")
    if len(blocks) != int(ir.get("basic_block_count", -1)):
        violations.append("cfg_basic_block_count_mismatch")
    valid = set(range(len(blocks)))
    edge_count = 0
    for b in blocks:
        bid = int(b.get("id", -1))
        s, e = int(b.get("start_instruction", -1)), int(b.get("end_instruction", -1))
        if s < 0 or e < s or e >= len(ins):
            violations.append(f"cfg_block_instruction_range:{bid}:{s}:{e}")
        succ = list(b.get("successors") or [])
        pred = list(b.get("predecessors") or [])
        edge_count += len(succ)
        if any(x not in valid for x in succ):
            violations.append(f"cfg_invalid_successor:{bid}:{succ}")
        if any(x not in valid for x in pred):
            violations.append(f"cfg_invalid_predecessor:{bid}:{pred}")
    if edge_count != int(ir.get("cfg_edge_count", -1)):
        violations.append(f"cfg_edge_count:{edge_count}!={ir.get('cfg_edge_count')}")
    for b in blocks:
        bid = int(b["id"])
        for dst in b.get("successors") or []:
            if bid not in (blocks[dst].get("predecessors") or []):
                violations.append(f"cfg_predecessor_asymmetry:{bid}->{dst}")
    labels = {label for x in ins for label in (x.get("labels") or [])}
    for x in ins:
        op = str(x.get("opcode", ""))
        if op in structural.UNCOND or op.startswith(structural.COND_PREFIX):
            target = x.get("branch_target_label")
            if not target:
                violations.append(f"cfg_branch_without_target:{x.get('index')}:{op}")
            elif target not in labels:
                violations.append(f"cfg_unresolved_branch_target:{x.get('index')}:{op}:{target}")
    return violations


def validate_accounting(ir: dict, code_bytes: int) -> list[str]:
    violations: list[str] = []
    ins = ir.get("instructions") or []
    pa = ir.get("parse_accounting") or {}
    if ir.get("status") != IR_STATUS:
        violations.append(f"structural_ir_status:{ir.get('status')!r}")
    if pa.get("status") != ACCOUNTING_STATUS:
        violations.append(f"parse_accounting_status:{pa.get('status')!r}")
    expected = {
        "native_instruction_line_count": len(ins),
        "ir_instruction_count": len(ins),
        "encoded_byte_count": code_bytes,
        "unaccounted_native_instruction_line_count": 0,
        "duplicate_ir_instruction_count": 0,
    }
    for key, want in expected.items():
        if pa.get(key) != want:
            violations.append(f"parse_accounting_{key}:{pa.get(key)!r}!={want!r}")
    if int(ir.get("instruction_count", -1)) != len(ins):
        violations.append("instruction_count_mismatch")
    if [x.get("index") for x in ins] != list(range(len(ins))):
        violations.append("instruction_indices_noncontiguous")
    end = 0
    for i, x in enumerate(ins):
        addr = int(x.get("address", -1)); size = int(x.get("byte_size", -1))
        enc = str(x.get("encoding_hex", ""))
        if addr != end:
            violations.append(f"instruction_address_gap:{i}:{addr}!={end}")
        if size not in (4, 8) or len(enc) != size * 2:
            violations.append(f"instruction_encoding_size:{i}:{size}:{len(enc)//2}")
        end = addr + size
    if end != code_bytes:
        violations.append(f"instruction_bytes:{end}!={code_bytes}")
    return violations


def self_test() -> None:
    row = {
        "opcode":"s_branch", "encoding_width_bytes":4, "operand_syntax":["LABEL"],
        "def_kinds":[], "use_kinds":[], "has_branch_target":True,
        "classification_rule":"NO_DESTINATION",
    }
    assert baseline_form_key(row) == (
        "s_branch",4,("LABEL",),(),(),True,"NO_DESTINATION"
    )
    assert core.reg_kind("vcc") == "VCC"
    assert core.reg_kind("v7") == "VGPR"
    print("D1_GCN_STRUCTURAL_CANDIDATE_COMPARE_V1_SELF_TEST_OK")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path)
    ap.add_argument("--program-dir", type=Path)
    ap.add_argument("--baseline-census", type=Path)
    ap.add_argument("--clrx", type=Path)
    ap.add_argument("--work-dir", type=Path)
    ap.add_argument("-o", "--output", type=Path)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        self_test(); return 0
    for name in ("manifest","program_dir","baseline_census","clrx","work_dir","output"):
        if getattr(a, name) is None:
            ap.error(f"--{name.replace('_','-')} is required")

    manifest = json.loads(a.manifest.read_text())
    if manifest.get("schema") != MANIFEST_SCHEMA or manifest.get("status") != MANIFEST_STATUS or manifest.get("violations"):
        raise SystemExit("zero-violation exact candidate manifest required")
    baseline = json.loads(a.baseline_census.read_text())
    if baseline.get("schema") != BASELINE_SCHEMA or baseline.get("status") != BASELINE_STATUS or baseline.get("violations"):
        raise SystemExit("zero-violation complete baseline structural census required")

    bc = baseline.get("census") or {}
    baseline_ops = {str(x["opcode"]) for x in bc.get("opcodes") or []}
    baseline_widths = {int(x["bytes"]) for x in bc.get("encoding_widths") or []}
    baseline_rules = {str(x["rule"]) for x in bc.get("classification_rules") or []}
    baseline_forms = {baseline_form_key(x) for x in bc.get("structural_forms") or []}
    baseline_exact_enc = {str(x["encoding_hex"]).lower() for x in bc.get("exact_encodings") or []}
    baseline_cfg = {baseline_cfg_key(x) for x in bc.get("cfg_forms") or []}
    if len(baseline_ops) != int(bc.get("opcode_count", -1)) or len(baseline_forms) != int(bc.get("structural_form_count", -1)):
        raise SystemExit("baseline structural census internal count mismatch")

    disasm_dir=a.work_dir/"disasm"; ir_dir=a.work_dir/"ir"; stderr_dir=a.work_dir/"stderr"
    for p in (disasm_dir, ir_dir, stderr_dir): p.mkdir(parents=True, exist_ok=True)

    violations: list[str] = []
    rows=[]; all_ops=collections.Counter(); all_forms=collections.Counter(); all_widths=collections.Counter(); all_rules=collections.Counter(); all_enc=collections.Counter(); all_cfg=collections.Counter()
    total_bytes=0; total_ins=0; exact=0
    programs=manifest.get("programs") or []
    seen=set()
    for p in programs:
        sha=str(p.get("gcn_sha256","")).lower(); code_bytes=int(p.get("gcn_bytes",0)); rep=str(p.get("representative","")).upper().removeprefix("0X").zfill(8)
        rec={"gcn_sha256":sha,"gcn_bytes":code_bytes,"representative":rep,"stages":p.get("stages") or [],"provenance":p.get("provenance"),"violations":[]}
        if sha in seen: rec["violations"].append("duplicate_candidate_gcn_sha256")
        seen.add(sha)
        rel=str(p.get("binary_file") or f"{sha}.bin")
        bin_path=a.program_dir/rel
        if not bin_path.is_file(): rec["violations"].append(f"program_binary_missing:{rel}")
        else:
            got=sha256_file(bin_path)
            if got != sha: rec["violations"].append(f"program_sha256:{got}!={sha}")
            if bin_path.stat().st_size != code_bytes: rec["violations"].append(f"program_size:{bin_path.stat().st_size}!={code_bytes}")
        if rec["violations"]:
            violations.extend(f"{sha}:{x}" for x in rec["violations"]); rows.append(rec); continue

        dis=disasm_dir/f"{sha}.s"; err=stderr_dir/f"{sha}.stderr"; irp=ir_dir/f"{sha}.json"
        proc=subprocess.run([str(a.clrx),"--raw","--gpuType=GFX700","--hexcode",str(bin_path)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        dis.write_text(proc.stdout); err.write_text(proc.stderr)
        rec["clrx"]={"returncode":proc.returncode,"stderr_bytes":len(proc.stderr.encode()),"contains_s_endpgm":"s_endpgm" in proc.stdout}
        if proc.returncode != 0: rec["violations"].append(f"clrx_returncode:{proc.returncode}")
        if proc.stderr: rec["violations"].append("clrx_stderr_nonempty")
        if "s_endpgm" not in proc.stdout: rec["violations"].append("clrx_missing_s_endpgm")
        if not rec["violations"]:
            q=subprocess.run([sys.executable,str(HERE/"d1_gcn_cfg_ir_v2.py"),"--disasm",str(dis),"--shader",rep,"-o",str(irp)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            rec["structural_ir"]={"returncode":q.returncode,"stdout":q.stdout[-2000:],"stderr":q.stderr[-2000:]}
            if q.returncode != 0 or not irp.is_file(): rec["violations"].append(f"structural_ir_returncode:{q.returncode}")
        if not rec["violations"]:
            ir=json.loads(irp.read_text())
            rec["violations"].extend(validate_accounting(ir,code_bytes)); rec["violations"].extend(validate_cfg(ir))
            ins=ir.get("instructions") or []
            ops=collections.Counter(str(x["opcode"]) for x in ins)
            forms=collections.Counter(core.form_key(x) for x in ins)
            widths=collections.Counter(len(str(x["encoding_hex"]))//2 for x in ins)
            rules=collections.Counter(core.classification_rule(x) for x in ins)
            encs=collections.Counter(str(x["encoding_hex"]).lower() for x in ins)
            cfg=cfg_signature(ir)
            unsupported_ops=sorted(set(ops)-baseline_ops); unsupported_forms=sorted(set(forms)-baseline_forms,key=str); unsupported_widths=sorted(set(widths)-baseline_widths); unsupported_rules=sorted(set(rules)-baseline_rules)
            rec["architectural_frontier"]={
                "unsupported_opcodes":unsupported_ops,
                "unsupported_structural_forms":[core.form_payload(x) for x in unsupported_forms],
                "unsupported_encoding_widths":unsupported_widths,
                "unsupported_classification_rules":unsupported_rules,
                "novel_exact_encoding_count":len(set(encs)-baseline_exact_enc),
                "cfg_signature":{"basic_blocks":cfg[0],"edges":cfg[1],"back_edge_count":cfg[2],"conditional_branch_count":cfg[3],"unconditional_branch_count":cfg[4],"divergent_exec_present":cfg[5]},
                "cfg_signature_novel_combination":cfg not in baseline_cfg,
                "cfg_signature_novel_combination_is_violation":False,
            }
            for name, vals in (("unsupported_opcodes",unsupported_ops),("unsupported_structural_forms",unsupported_forms),("unsupported_encoding_widths",unsupported_widths),("unsupported_classification_rules",unsupported_rules)):
                if vals: rec["violations"].append(f"{name}:{len(vals)}")
            if not rec["violations"]:
                exact += 1; total_bytes += code_bytes; total_ins += len(ins); all_ops.update(ops); all_forms.update(forms); all_widths.update(widths); all_rules.update(rules); all_enc.update(encs); all_cfg[cfg]+=1
        if rec["violations"]: violations.extend(f"{sha}:{x}" for x in rec["violations"])
        rows.append(rec)

    unsupported_ops=sorted(set(all_ops)-baseline_ops); unsupported_forms=sorted(set(all_forms)-baseline_forms,key=str); unsupported_widths=sorted(set(all_widths)-baseline_widths); unsupported_rules=sorted(set(all_rules)-baseline_rules)
    novel_cfg=sorted(set(all_cfg)-baseline_cfg)
    out={
        "schema":SCHEMA,
        "status":STATUS if not violations and exact==len(programs) else "D1_GCN_STRUCTURAL_CANDIDATE_ARCHITECTURE_REPLAY_WITH_VIOLATIONS",
        "inputs":{"manifest":str(a.manifest),"baseline_census":str(a.baseline_census),"baseline_status":baseline.get("status"),"baseline_unique_gcn_programs":(baseline.get("coverage") or {}).get("unique_exact_gcn_program_total")},
        "coverage":{"planned_unique_gcn_programs":len(programs),"exact_parse_accounted_unique_gcn_programs":exact,"instruction_count":total_ins,"encoded_bytes":total_bytes,"opcode_count":len(all_ops),"structural_form_count":len(all_forms)},
        "architecture_comparison":{"baseline_opcode_count":len(baseline_ops),"baseline_structural_form_count":len(baseline_forms),"unsupported_opcode_count":len(unsupported_ops),"unsupported_opcodes":unsupported_ops,"unsupported_structural_form_count":len(unsupported_forms),"unsupported_structural_forms":[core.form_payload(x) for x in unsupported_forms],"unsupported_encoding_widths":unsupported_widths,"unsupported_classification_rules":unsupported_rules,"candidate_exact_encoding_count":len(all_enc),"novel_exact_encoding_count":len(set(all_enc)-baseline_exact_enc),"novel_exact_encodings_are_architecture_violation":False,"candidate_cfg_signature_count":len(all_cfg),"novel_cfg_signature_combination_count":len(novel_cfg),"novel_cfg_signature_combinations":[{"basic_blocks":x[0],"edges":x[1],"back_edge_count":x[2],"conditional_branch_count":x[3],"unconditional_branch_count":x[4],"divergent_exec_present":x[5]} for x in novel_cfg],"novel_cfg_signature_combinations_are_architecture_violation":False},
        "programs":rows,"violations":violations,
        "semantic_boundary":{"candidate_stage_labels_affect_gfx7_decode":False,"exact_encoding_value_novelty":"EVIDENCE_ONLY","whole_program_cfg_tuple_novelty":"EVIDENCE_ONLY","new_normalized_instruction_form":"FAIL_CLOSED","shader_expression_semantics":"NOT_PROMOTED"},
        "policy":"The candidate uses the unchanged universal GFX7 Structural IR producer. Exact register/immediate encodings and aggregate CFG size/topology tuples may be new instances. Any new opcode, normalized operand/def-use/branch form, encoding width, classification rule, malformed CFG, or parse-accounting loss fails closed and is not semantically promoted.",
    }
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2)+"\n")
    print("STATUS",out["status"],"PROGRAMS",f"{exact}/{len(programs)}","INSTRUCTIONS",total_ins,"BYTES",total_bytes,"UNSUPPORTED_OPCODES",len(unsupported_ops),"UNSUPPORTED_FORMS",len(unsupported_forms),"NOVEL_CFG_COMBINATIONS",len(novel_cfg),"VIOLATIONS",len(violations))
    for v in violations[:200]: print("VIOLATION",v)
    return 0 if out["status"]==STATUS else 2


if __name__ == "__main__":
    raise SystemExit(main())
