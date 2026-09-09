#!/usr/bin/env python3
"""Exact anonymous GFX7 stage-interface frontier for Destiny 1 PS4 shaders.

This gate closes only the architectural shape of vertex/domain parameter exports and
pixel interpolation attribute imports.  It deliberately does NOT pair unrelated shader
programs by package, slot count, naming, or proximity.  A later material-backed gate must
supply the exact retail VS/PS owner relation before any PARAM->ATTR provenance is promoted.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
from pathlib import Path

SCHEMA = "d1_gcn_stage_interface_frontier/v1"
STATUS = "D1_GCN_STAGE_INTERFACE_FRONTIER_EXACT"
EXTRACT_SCHEMA = "d1_remote_ps4_shader_corpus_extract/v3"
EXTRACT_STATUS = "D1_REMOTE_PS4_SHADER_CORPUS_EXACT_PS_VS_DS"
CENSUS_STATUS = "D1_GCN_SHADER_CORPUS_STRUCTURAL_CENSUS_COMPLETE"
EXPECTED_PROGRAMS = 26464
EXPECTED_STAGE = {"DS": 20, "PS": 18375, "VS": 8069}
EXPECTED_HEADERS = {"DS": 79, "PS": 25405, "VS": 12408}
EXPECTED_INSTRUCTIONS = 4896165
EXPECTED_INTERP_INSTRUCTIONS = 425370
EXPECTED_INTERP_PROGRAMS = 17868
EXPECTED_PARAM_EXPORTS = {"DS": 68, "VS": 37907}
EXPECTED_PARAM_EXPORT_PROGRAMS = {"DS": 20, "VS": 8069}
CHAN_BITS = {"x": 1, "y": 2, "z": 4, "w": 8}
ATTR_RE = re.compile(r"^attr(\d+)\.([xyzw])$")
PARAM_RE = re.compile(r"^param(\d+)$")

AMD = {
    "vendor": "Advanced Micro Devices, Inc.",
    "title": "Sea Islands Series Instruction Set Architecture",
    "document_id": "70653",
    "revision": "1.3",
    "release_date": "2013-12-01",
    "architecture": "GCN 2 / GFX7 / Sea Islands",
    "official_url": "https://www.amd.com/content/dam/amd/en/documents/radeon-tech-docs/instruction-set-architectures/sea-islands-instruction-set-architecture_0.pdf",
}


def source(locator: str, pdf_pages: str) -> dict:
    return {**AMD, "locator": locator, "pdf_pages": pdf_pages}


def mask_channels(mask: int) -> str:
    return "".join(ch for ch in "xyzw" if mask & CHAN_BITS[ch])


def compatible(imports: dict[int, int], exports: dict[int, int]) -> bool:
    return all((exports.get(slot, 0) & mask) == mask for slot, mask in imports.items())


def provenance(src: dict) -> tuple[dict, dict]:
    native_by_ref = {n["native_program_reference"]: n for n in src["native_programs"]}
    by_sha = {}
    header_to_sha = {}
    for p in src["unique_gcn_programs"]:
        sha = p["gcn_sha256"].lower()
        refs = p["native_program_references"]
        packages = sorted({native_by_ref[r]["package_id"] for r in refs})
        logical = sorted({native_by_ref[r]["logical_view"] for r in refs})
        headers = sorted((h["stage"], h["header"]) for h in p["headers"])
        by_sha[sha] = {
            "stage": p["stages"][0],
            "native_program_references": refs,
            "headers": [{"stage": s, "header": h} for s, h in headers],
            "package_ids": packages,
            "logical_views": logical,
        }
        for stage, h in headers:
            old = header_to_sha.setdefault(h, {"stage": stage, "gcn_sha256": sha})
            if old != {"stage": stage, "gcn_sha256": sha}:
                raise ValueError(f"header maps to multiple exact programs:{h}:{old}:{sha}")
    return by_sha, header_to_sha


def build(ir_dir: Path, census_path: Path, extract_path: Path) -> dict:
    violations = []
    src = json.loads(extract_path.read_text())
    census = json.loads(census_path.read_text())
    if src.get("schema") != EXTRACT_SCHEMA or src.get("status") != EXTRACT_STATUS:
        violations.append(f"extract_identity:{src.get('schema')}:{src.get('status')}")
    if src.get("violations"):
        violations.append(f"extract_violations:{len(src['violations'])}")
    if census.get("status") != CENSUS_STATUS or census.get("violations"):
        violations.append(f"census_not_exact:{census.get('status')}:{len(census.get('violations') or [])}")

    prov, header_to_sha = provenance(src)
    stages = {p["gcn_sha256"].lower(): p["stages"][0] for p in census["programs"]}
    paths = sorted(ir_dir.glob("*.json"))
    if len(paths) != EXPECTED_PROGRAMS:
        violations.append(f"ir_file_count:{len(paths)}!={EXPECTED_PROGRAMS}")
    if len(stages) != EXPECTED_PROGRAMS or set(stages) != set(prov):
        violations.append("program_roster_mismatch")

    stage_counts = collections.Counter(stages.values())
    import_programs = {}
    export_programs = {}
    import_signature_counts = collections.Counter()
    export_signature_counts = collections.Counter()
    attr_instruction_counts = collections.Counter()
    channel_instruction_counts = collections.Counter()
    param_export_slot_counts = collections.defaultdict(collections.Counter)
    param_export_en_counts = collections.defaultdict(collections.Counter)
    exp_target_counts = collections.defaultdict(collections.Counter)
    interp_opcode_counts = collections.Counter()
    total_instructions = 0
    param_done_count = param_compr_count = 0
    malformed_interp = malformed_param = 0

    for p in paths:
        sha = p.stem.lower()
        d = json.loads(p.read_text())
        if d.get("status") != "D1_GCN_STRUCTURAL_IR_COMPLETE":
            violations.append(f"ir_status:{sha}:{d.get('status')}")
            continue
        if (d.get("parse_accounting") or {}).get("status") != "D1_GCN_STRUCTURAL_PARSE_ACCOUNTING_EXACT":
            violations.append(f"parse_accounting:{sha}")
            continue
        st = stages.get(sha)
        if prov.get(sha, {}).get("stage") != st:
            violations.append(f"stage_provenance:{sha}:{st}:{prov.get(sha,{}).get('stage')}")
            continue
        ins = d.get("instructions") or []
        total_instructions += len(ins)

        imports = collections.defaultdict(int)
        interp_count = 0
        exports = {}
        export_rows = []
        for x in ins:
            op = x["opcode"]
            if op in {"v_interp_p1_f32", "v_interp_p2_f32", "v_interp_mov_f32"}:
                interp_count += 1
                interp_opcode_counts[op] += 1
                ops = x.get("operands") or []
                if not ops:
                    malformed_interp += 1
                    violations.append(f"interp_no_operands:{sha}:{x['index']}")
                    continue
                m = ATTR_RE.fullmatch(ops[-1])
                if not m:
                    malformed_interp += 1
                    violations.append(f"interp_attr_form:{sha}:{x['index']}:{ops!r}")
                    continue
                slot, ch = int(m.group(1)), m.group(2)
                if st != "PS":
                    violations.append(f"interp_non_ps:{sha}:{st}:{x['index']}")
                imports[slot] |= CHAN_BITS[ch]
                attr_instruction_counts[slot] += 1
                channel_instruction_counts[ch] += 1

            if op == "exp":
                ops = x.get("operands") or []
                target_name = ops[0] if ops else ""
                exp_target_counts[st][target_name] += 1
                m = PARAM_RE.fullmatch(target_name)
                if not m:
                    continue
                if st not in {"VS", "DS"}:
                    violations.append(f"param_export_bad_stage:{sha}:{st}:{x['index']}")
                    continue
                if len(x.get("encoding_words") or []) != 2:
                    malformed_param += 1
                    violations.append(f"param_export_encoding_width:{sha}:{x['index']}")
                    continue
                word0 = int(x["encoding_words"][0], 16)
                en = word0 & 0xF
                target = (word0 >> 4) & 0x3F
                compr = (word0 >> 10) & 1
                done = (word0 >> 11) & 1
                vm = (word0 >> 12) & 1
                slot = int(m.group(1))
                if target != 32 + slot:
                    violations.append(f"param_target_encoding:{sha}:{x['index']}:{target}!={32+slot}")
                if slot in exports:
                    violations.append(f"duplicate_param_export_slot:{sha}:{slot}")
                exports[slot] = en
                param_export_slot_counts[st][slot] += 1
                param_export_en_counts[st][en] += 1
                param_compr_count += compr
                param_done_count += done
                export_rows.append({
                    "instruction": x["index"], "address": x["address_hex"],
                    "slot": slot, "enabled_mask": en, "enabled_channels": mask_channels(en),
                    "compressed": bool(compr), "done": bool(done), "valid_mask": bool(vm),
                })

        if st == "PS":
            isig = tuple(sorted(imports.items()))
            import_signature_counts[isig] += 1
            import_programs[sha] = {
                **prov[sha],
                "interpolation_instruction_count": interp_count,
                "imports": [
                    {"attribute": k, "channel_mask": v, "channels": mask_channels(v)}
                    for k, v in sorted(imports.items())
                ],
            }
        elif st in {"VS", "DS"}:
            esig = tuple(sorted(exports.items()))
            export_signature_counts[(st, esig)] += 1
            export_programs[sha] = {
                **prov[sha],
                "parameter_exports": [
                    {"parameter": k, "channel_mask": v, "channels": mask_channels(v)}
                    for k, v in sorted(exports.items())
                ],
                "export_instructions": export_rows,
            }

    if total_instructions != EXPECTED_INSTRUCTIONS:
        violations.append(f"instruction_count:{total_instructions}!={EXPECTED_INSTRUCTIONS}")
    if dict(sorted(stage_counts.items())) != EXPECTED_STAGE:
        violations.append(f"stage_counts:{dict(stage_counts)}!={EXPECTED_STAGE}")
    hp = src.get("header_population", {}).get("stage_counts") or {}
    if hp != EXPECTED_HEADERS:
        violations.append(f"header_stage_counts:{hp}!={EXPECTED_HEADERS}")

    interp_total = sum(interp_opcode_counts.values())
    interp_program_count = sum(1 for r in import_programs.values() if r["interpolation_instruction_count"])
    if interp_total != EXPECTED_INTERP_INSTRUCTIONS:
        violations.append(f"interp_instruction_count:{interp_total}!={EXPECTED_INTERP_INSTRUCTIONS}")
    if interp_program_count != EXPECTED_INTERP_PROGRAMS:
        violations.append(f"interp_program_count:{interp_program_count}!={EXPECTED_INTERP_PROGRAMS}")
    got_param = {s: sum(param_export_slot_counts[s].values()) for s in ("DS", "VS")}
    if got_param != EXPECTED_PARAM_EXPORTS:
        violations.append(f"param_export_count:{got_param}!={EXPECTED_PARAM_EXPORTS}")
    got_param_programs = {
        s: sum(1 for r in export_programs.values() if r["stage"] == s and r["parameter_exports"])
        for s in ("DS", "VS")
    }
    if got_param_programs != EXPECTED_PARAM_EXPORT_PROGRAMS:
        violations.append(f"param_export_programs:{got_param_programs}!={EXPECTED_PARAM_EXPORT_PROGRAMS}")
    if param_done_count != 0 or param_compr_count != 0:
        violations.append(f"unexpected_param_modifiers:done={param_done_count}:compr={param_compr_count}")
    if malformed_interp or malformed_param:
        violations.append(f"malformed_forms:interp={malformed_interp}:param={malformed_param}")
    expected_en = {"DS": {15: 68}, "VS": {15: 37907}}
    got_en = {s: dict(sorted(param_export_en_counts[s].items())) for s in ("DS", "VS")}
    if got_en != expected_en:
        violations.append(f"param_enable_surface:{got_en}!={expected_en}")

    vs_exports = [
        {x["parameter"]: x["channel_mask"] for x in r["parameter_exports"]}
        for r in export_programs.values() if r["stage"] == "VS"
    ]
    ds_exports = [
        {x["parameter"]: x["channel_mask"] for x in r["parameter_exports"]}
        for r in export_programs.values() if r["stage"] == "DS"
    ]
    ps_with_imports = 0
    globally_vs_compatible = globally_any_compatible = 0
    for r in import_programs.values():
        im = {x["attribute"]: x["channel_mask"] for x in r["imports"]}
        if not im:
            continue
        ps_with_imports += 1
        has_vs = any(compatible(im, ex) for ex in vs_exports)
        has_any = has_vs or any(compatible(im, ex) for ex in ds_exports)
        globally_vs_compatible += int(has_vs)
        globally_any_compatible += int(has_any)
    if globally_any_compatible != ps_with_imports:
        violations.append(f"global_signature_coverage:{globally_any_compatible}!={ps_with_imports}")

    def sig_rows_import(counter):
        return [
            {
                "imports": [{"attribute": k, "channel_mask": v, "channels": mask_channels(v)} for k, v in sig],
                "program_count": n,
            }
            for sig, n in sorted(counter.items(), key=lambda kv: (len(kv[0]), kv[0]))
        ]

    def sig_rows_export(counter):
        return [
            {
                "stage": st,
                "exports": [{"parameter": k, "channel_mask": v, "channels": mask_channels(v)} for k, v in sig],
                "program_count": n,
            }
            for (st, sig), n in sorted(counter.items(), key=lambda kv: (kv[0][0], len(kv[0][1]), kv[0][1]))
        ]

    coverage = {
        "exact_program_count": len(paths),
        "stage_program_counts": dict(sorted(stage_counts.items())),
        "exact_header_count": len(header_to_sha),
        "header_stage_counts": hp,
        "exact_instruction_count": total_instructions,
        "pixel_program_count": len(import_programs),
        "pixel_programs_with_interpolation": ps_with_imports,
        "pixel_programs_without_interpolation": len(import_programs) - ps_with_imports,
        "interpolation_instruction_count": interp_total,
        "interpolation_opcode_counts": dict(sorted(interp_opcode_counts.items())),
        "attribute_instruction_counts": {str(k): v for k, v in sorted(attr_instruction_counts.items())},
        "channel_instruction_counts": dict(sorted(channel_instruction_counts.items())),
        "unique_pixel_import_signatures": len(import_signature_counts),
        "parameter_export_instruction_counts": got_param,
        "parameter_export_program_counts": got_param_programs,
        "parameter_export_enable_mask_counts": {s: {str(k): v for k, v in sorted(param_export_en_counts[s].items())} for s in ("DS", "VS")},
        "parameter_export_compressed_count": param_compr_count,
        "parameter_export_done_count": param_done_count,
        "unique_parameter_export_signatures": {
            s: len({sig for (stage, sig), n in export_signature_counts.items() if stage == s}) for s in ("DS", "VS")
        },
        "pixel_import_signatures_with_global_vs_compatible_shape": globally_vs_compatible,
        "pixel_import_signatures_with_global_any_producer_compatible_shape": globally_any_compatible,
        "material_backed_shader_pair_promotions": 0,
        "shader_expression_semantic_promotions": 0,
    }
    return {
        "schema": SCHEMA,
        "status": STATUS if not violations else "D1_GCN_STAGE_INTERFACE_FRONTIER_WITH_VIOLATIONS",
        "source": {
            "export_semantics": source("Chapter 11 EXP encoding and operations: TARGET Param0..31, EN, COMPR, DONE", "11-1..11-3"),
            "interpolation_semantics": source("10.3.2 parameter reads; 12.12 VINTRP ATTR/ATTRCHAN", "10-4..10-5, 12-140"),
        },
        "coverage": coverage,
        "pixel_import_signatures": sig_rows_import(import_signature_counts),
        "parameter_export_signatures": sig_rows_export(export_signature_counts),
        "program_interfaces": {
            "pixel_imports": import_programs,
            "parameter_exports": export_programs,
        },
        "header_to_exact_program": header_to_sha,
        "violations": violations,
        "semantic_boundary": {
            "exp_parameter_target_and_enable_identity": "GLOBAL_EXACT",
            "vintrp_attribute_channel_identity": "GLOBAL_EXACT",
            "anonymous_interface_shape_compatibility": "GLOBAL_EXACT_DIAGNOSTIC_ONLY",
            "param_index_to_attr_index_provenance": "WITHHELD_UNTIL_RETAIL_PIPELINE_OWNER_JOIN",
            "material_header_vs_ps_pair_relation": "AUTHORITATIVE_NEXT_JOIN_SOURCE",
            "domain_shader_pipeline_ownership": "WITHHELD_SEPARATE_TESSELLATION_GATE",
            "varying_semantic_names": "WITHHELD",
            "shader_expression_semantics": "WITHHELD",
            "material_backed_shader_pair_promotions": 0,
            "shader_expression_semantic_promotions": 0,
        },
        "policy": (
            "EXP parameter exports and VINTRP attribute/channel imports are decoded exactly and retained as anonymous slot/channel interfaces. "
            "Global shape compatibility is diagnostic only and never pairs shaders. Exact VS->PS provenance must come from a retail owner such as "
            "the PS4 material header carrying both shader header references. No UV/color/normal/material role is inferred."
        ),
    }


def self_test() -> None:
    assert mask_channels(0xF) == "xyzw"
    assert mask_channels(0x5) == "xz"
    assert compatible({0: 3, 2: 4}, {0: 15, 1: 15, 2: 15})
    assert not compatible({2: 8}, {0: 15, 1: 15})
    # EXP PARAM0 example: EN=f, TARGET=32, COMPR=0, DONE=0.
    w = int("f800020f", 16)
    assert (w & 0xF) == 15
    assert ((w >> 4) & 0x3F) == 32
    assert ((w >> 10) & 1) == 0
    assert ((w >> 11) & 1) == 0
    print("D1_GCN_STAGE_INTERFACE_FRONTIER_SELF_TEST_OK")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ir-dir", type=Path)
    ap.add_argument("--census", type=Path)
    ap.add_argument("--extract-report", type=Path)
    ap.add_argument("-o", "--output", type=Path)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        self_test(); return 0
    if not all((a.ir_dir, a.census, a.extract_report, a.output)):
        ap.error("--ir-dir, --census, --extract-report and --output are required")
    out = build(a.ir_dir, a.census, a.extract_report)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": out["status"], "coverage": out["coverage"], "violations": out["violations"][:50]}, indent=2, sort_keys=True))
    return 0 if not out["violations"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
