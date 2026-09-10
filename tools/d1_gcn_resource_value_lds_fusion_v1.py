#!/usr/bin/env python3
"""Fuse exact D1 GCN resource/LDS provenance with separately proven resource identities.

This is an evidence-join gate, not a GCN decoder. It preserves the generic provenance
records exactly and enriches only resource reads whose external ABI identity was proven
by a separate report. Runtime buffer contents, concrete LDS addresses, and engine-level
semantic ownership remain outside this layer.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

SCHEMA = "d1_gcn_resource_value_lds_fusion/v1"
STATUS_EXACT = "D1_GCN_RESOURCE_VALUE_LDS_FUSION_EXACT"
STATUS_BAD = "D1_GCN_RESOURCE_VALUE_LDS_FUSION_WITH_VIOLATIONS"
PROVENANCE_STATUS = "D1_GCN_RESOURCE_LDS_PROVENANCE_EXACT_SYMBOLIC"
VALUE_STATUS = "D1_GCN_LOCALSHADER_TBUFFER_VALUE_BINDING_EXACT"
EXPECTED_PROGRAMS = 65
EXPECTED_RESOURCE_READS = 385
EXPECTED_COMPONENTS = 1540
EXPECTED_LDS_WRITES = 641
EXPECTED_TARGETS = 1026

RE_WRITE_VGPR = re.compile(r"^write:i(\d+):v(\d+)$")
RE_SGPR_RANGE = re.compile(r"^s\[(\d+):(\d+)\]$")


class GateError(RuntimeError):
    pass


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        obj = json.load(f)
    if not isinstance(obj, dict):
        raise GateError(f"{path}: top-level JSON must be an object")
    return obj


def require(cond: bool, message: str) -> None:
    if not cond:
        raise GateError(message)


def as_int(v: Any, what: str) -> int:
    if isinstance(v, bool):
        raise GateError(f"{what}: boolean is not an integer")
    if isinstance(v, int):
        return v
    if isinstance(v, str):
        s = v.strip().lower()
        try:
            return int(s, 16) if s.startswith("0x") else int(s, 10)
        except ValueError as e:
            raise GateError(f"{what}: invalid integer {v!r}") from e
    raise GateError(f"{what}: invalid integer type {type(v).__name__}")


def exact_key(program: Any, instruction: Any) -> Tuple[str, int]:
    require(isinstance(program, str) and len(program) == 64, f"invalid program SHA {program!r}")
    return program, as_int(instruction, "instruction")


def unique_map(rows: Iterable[Mapping[str, Any]], program_field: str, what: str) -> Dict[Tuple[str, int], Dict[str, Any]]:
    out: Dict[Tuple[str, int], Dict[str, Any]] = {}
    for row in rows:
        require(isinstance(row, Mapping), f"{what}: row is not an object")
        k = exact_key(row.get(program_field), row.get("instruction"))
        if k in out:
            raise GateError(f"{what}: duplicate exact row key {k!r}")
        out[k] = dict(row)
    return out


def descriptor_registers(token: Any) -> List[str]:
    require(isinstance(token, str), f"descriptor range is not a string: {token!r}")
    m = RE_SGPR_RANGE.fullmatch(token)
    require(m is not None, f"invalid descriptor SGPR range {token!r}")
    lo, hi = int(m.group(1)), int(m.group(2))
    require(hi >= lo and hi - lo == 3, f"descriptor range is not exactly four SGPRs: {token!r}")
    return [f"s{i}" for i in range(lo, hi + 1)]


def require_exact_descriptor_provenance(resource: Mapping[str, Any], descriptor_window: str) -> None:
    desc = resource.get("resource_descriptor")
    require(isinstance(desc, Mapping), "resource provenance is missing resource_descriptor")
    require(desc.get("register_range") == descriptor_window,
            f"descriptor range mismatch: provenance={desc.get('register_range')!r} value={descriptor_window!r}")
    regs = descriptor_registers(descriptor_window)
    comps = desc.get("components")
    require(isinstance(comps, list) and len(comps) == 4, "descriptor provenance must contain four SGPR components")
    got_regs: List[str] = []
    for c in comps:
        require(isinstance(c, Mapping), "descriptor component provenance is not an object")
        reg = c.get("register")
        got_regs.append(reg)
        for field in ("node", "external_graph", "external_node", "external_ref", "exactness"):
            require(isinstance(c.get(field), str) and bool(c[field]), f"descriptor {reg}: missing exact {field}")
    require(got_regs == regs, f"descriptor component order mismatch: expected={regs!r} got={got_regs!r}")
    require(desc.get("status") == "UNRESOLVED_CONCRETE_RESOURCE",
            f"generic provenance unexpectedly claims concrete resource: {desc.get('status')!r}")


def compare_resource(resource: Mapping[str, Any], binding: Mapping[str, Any]) -> None:
    require(resource.get("opcode") == "tbuffer_load_format_xyzw", f"unexpected resource opcode {resource.get('opcode')!r}")
    require(resource.get("kind") == "GFX7_TYPED_BUFFER_RESOURCE_PROVENANCE", f"unexpected resource kind {resource.get('kind')!r}")
    require(binding.get("operation") == "GFX7_TYPED_BUFFER_READ_XYZW_FROM_BOUND_IMM_CONST_BUFFER",
            f"unexpected value-binding operation {binding.get('operation')!r}")
    require(resource.get("address") == binding.get("address"),
            f"instruction address mismatch: provenance={resource.get('address')!r} value={binding.get('address')!r}")

    rid = binding.get("resource_identity")
    require(isinstance(rid, Mapping), "value binding is missing resource_identity")
    require(rid.get("usage_name") == "ImmConstBuffer" and as_int(rid.get("api_slot"), "api_slot") == 10,
            f"unexpected resource identity {rid!r}")
    require(rid.get("reaching_state") == "PROGRAM_ENTRY_USER_DATA", f"unexpected descriptor reaching state {rid.get('reaching_state')!r}")
    descriptor_window = rid.get("descriptor_window")
    require(isinstance(descriptor_window, str), "resource identity descriptor_window missing")
    require_exact_descriptor_provenance(resource, descriptor_window)

    pa = resource.get("addressing")
    ba = binding.get("addressing")
    require(isinstance(pa, Mapping) and isinstance(ba, Mapping), "resource addressing record missing")
    for field in ("addr64", "idxen", "offen", "offset12"):
        require(pa.get(field) == ba.get(field), f"addressing {field} mismatch: provenance={pa.get(field)!r} value={ba.get(field)!r}")
    require(ba.get("idxen") is True and ba.get("offen") is False and ba.get("addr64") is False,
            f"API10 value binding admitted an unexpected addressing form: {dict(ba)!r}")

    vaddr = resource.get("vaddr")
    require(isinstance(vaddr, Mapping), "resource VADDR provenance missing")
    state_node = ba.get("vaddr_state_node")
    require(isinstance(state_node, str), "value binding VADDR state node missing")
    m = RE_WRITE_VGPR.fullmatch(state_node)
    require(m is not None, f"value binding VADDR state is not an exact in-program VGPR write: {state_node!r}")
    require(vaddr.get("register") == f"v{m.group(2)}", f"VADDR register mismatch: provenance={vaddr.get('register')!r} state={state_node!r}")
    require(vaddr.get("current_value") == state_node,
            f"VADDR current SSA value mismatch: provenance={vaddr.get('current_value')!r} value={state_node!r}")

    soff = resource.get("soffset")
    require(isinstance(soff, Mapping), "resource SOFFSET provenance missing")
    require(as_int(ba.get("soffset_u32"), "value-binding soffset_u32") == 0, "value-binding SOFFSET is not exact zero")
    require(soff.get("kind") == "ENCODED_LITERAL_32", f"provenance SOFFSET is not an encoded literal: {soff!r}")
    require(as_int(soff.get("u32_bits"), "provenance SOFFSET u32_bits") == 0, f"provenance SOFFSET is not exact zero: {soff!r}")

    pf = resource.get("format")
    bf = binding.get("format")
    require(isinstance(pf, Mapping) and isinstance(bf, Mapping), "resource format record missing")
    require(pf.get("dfmt") == bf.get("dfmt"), f"DFMT mismatch: provenance={pf.get('dfmt')!r} value={bf.get('dfmt')!r}")
    require(pf.get("nfmt") == bf.get("nfmt"), f"NFMT mismatch: provenance={pf.get('nfmt')!r} value={bf.get('nfmt')!r}")
    require(as_int(pf.get("component_count"), "provenance component_count") == as_int(bf.get("result_components"), "value result_components"),
            "resource component-count mismatch")
    require(as_int(bf.get("result_components"), "value result_components") == 4, "typed-buffer result is not exactly XYZW")

    nodes = resource.get("result_component_nodes")
    comps = binding.get("components")
    require(isinstance(nodes, list) and len(nodes) == 4, "provenance result component nodes are not exactly XYZW")
    require(isinstance(comps, list) and len(comps) == 4, "value components are not exactly XYZW")
    ordered = sorted(comps, key=lambda c: c.get("component", -1) if isinstance(c, Mapping) else -1)
    require([c.get("component") for c in ordered if isinstance(c, Mapping)] == [0, 1, 2, 3], "value component numbering is not exactly 0..3")
    require([c.get("existing_special_node") for c in ordered] == nodes,
            f"result-node identity mismatch: provenance={nodes!r} value={[c.get('existing_special_node') for c in ordered]!r}")
    for c in ordered:
        require(isinstance(c.get("resource_value_node"), str) and bool(c["resource_value_node"]), "resource value node identity missing")
        require(isinstance(c.get("value_expression"), str) and c["value_expression"].startswith("ImmConstBuffer[api=10][index="),
                f"unexpected resource value expression {c.get('value_expression')!r}")

    require(binding.get("numeric_value_status") == "RUNTIME_BUFFER_CONTENT_OPAQUE",
            f"value binding unexpectedly claims runtime numeric contents: {binding.get('numeric_value_status')!r}")


def analyze(provenance: Mapping[str, Any], values: Mapping[str, Any]) -> Dict[str, Any]:
    violations: List[Dict[str, Any]] = []
    require(provenance.get("status") == PROVENANCE_STATUS, f"provenance status mismatch: {provenance.get('status')!r}")
    require(values.get("status") == VALUE_STATUS, f"resource-value status mismatch: {values.get('status')!r}")
    require(not provenance.get("violations"), "generic provenance report contains violations")
    require(not values.get("violations"), "resource-value report contains violations")

    records = provenance.get("records")
    bindings = values.get("bindings")
    require(isinstance(records, list), "generic provenance records missing")
    require(isinstance(bindings, list), "resource-value bindings missing")
    resources = [r for r in records if isinstance(r, Mapping) and r.get("opcode") == "tbuffer_load_format_xyzw"]
    lds = [r for r in records if isinstance(r, Mapping) and r.get("opcode") == "ds_write2_b32"]
    require(len(resources) == EXPECTED_RESOURCE_READS, f"resource read denominator changed: {len(resources)} != {EXPECTED_RESOURCE_READS}")
    require(len(lds) == EXPECTED_LDS_WRITES, f"LDS write denominator changed: {len(lds)} != {EXPECTED_LDS_WRITES}")
    require(len(records) == EXPECTED_TARGETS, f"target operation denominator changed: {len(records)} != {EXPECTED_TARGETS}")
    require(len(bindings) == EXPECTED_RESOURCE_READS, f"resource-value binding denominator changed: {len(bindings)} != {EXPECTED_RESOURCE_READS}")

    rm = unique_map(resources, "program_sha256", "generic resource provenance")
    bm = unique_map(bindings, "gcn_sha256", "resource-value binding")
    require(set(rm) == set(bm), f"resource/value key sets differ: provenance_only={sorted(set(rm)-set(bm))!r} value_only={sorted(set(bm)-set(rm))!r}")

    fused_records: List[Dict[str, Any]] = []
    component_total = 0
    resource_programs = set()
    all_programs = set()
    for row in records:
        require(isinstance(row, Mapping), "generic provenance record is not an object")
        program = row.get("program_sha256")
        require(isinstance(program, str) and len(program) == 64, f"invalid record program SHA {program!r}")
        all_programs.add(program)
        out = copy.deepcopy(dict(row))
        if row.get("opcode") == "tbuffer_load_format_xyzw":
            k = exact_key(program, row.get("instruction"))
            binding = bm[k]
            try:
                compare_resource(row, binding)
            except GateError as e:
                violations.append({"program_sha256": program, "instruction": row.get("instruction"), "code": "RESOURCE_FUSION_MISMATCH", "detail": str(e)})
            comps = binding.get("components") if isinstance(binding.get("components"), list) else []
            component_total += len(comps)
            resource_programs.add(program)
            out["resource_value_binding"] = {
                "operation": binding.get("operation"),
                "resource_identity": copy.deepcopy(binding.get("resource_identity")),
                "numeric_value_status": binding.get("numeric_value_status"),
                "components": copy.deepcopy(comps),
            }
        fused_records.append(out)

    require(component_total == EXPECTED_COMPONENTS, f"resource component denominator changed: {component_total} != {EXPECTED_COMPONENTS}")
    programs = provenance.get("programs")
    require(isinstance(programs, list), "generic provenance program rows missing")
    exact_program_shas = {p.get("program_sha256") for p in programs if isinstance(p, Mapping) and p.get("status") == PROVENANCE_STATUS}
    require(len(exact_program_shas) == EXPECTED_PROGRAMS, f"exact program denominator changed: {len(exact_program_shas)} != {EXPECTED_PROGRAMS}")
    require(all_programs <= exact_program_shas, "one or more target records do not belong to exact generic-provenance programs")

    # LDS is intentionally not enriched. Prove byte-for-byte object identity at the JSON object layer.
    input_lds = [copy.deepcopy(dict(r)) for r in lds]
    output_lds = [copy.deepcopy(r) for r in fused_records if r.get("opcode") == "ds_write2_b32"]
    require(output_lds == input_lds, "LDS records changed during resource-value fusion")

    if violations:
        status = STATUS_BAD
    else:
        status = STATUS_EXACT
    return {
        "schema": SCHEMA,
        "status": status,
        "semantic_boundary": {
            "claim": "Exact generic GFX7 resource/LDS provenance plus separately proven D1 API resource identity for admitted typed-buffer reads. Runtime buffer contents, concrete LDS addresses, engine ownership, and higher shader meaning are not promoted.",
            "resource_identity": "EXACT_D1_USAGE_BINDING_API10_IMMCONSTBUFFER",
            "resource_numeric_contents": "OPAQUE_NOT_EVALUATED",
            "lds_records": "PRESERVED_UNCHANGED_FROM_GENERIC_PROVENANCE",
            "lds_runtime_addresses": "NOT_EVALUATED",
            "engine_resource_ownership": "NOT_YET_PROVEN",
            "higher_shader_expression_semantics": "NOT_PROMOTED",
            "no_stage_slot_semantic_transfer": True,
            "no_runtime_value_fabrication": True,
            "no_concrete_memory_address_guessing": True,
        },
        "coverage": {
            "exact_bound_program_count": len(exact_program_shas),
            "resource_read_count": len(resources),
            "resource_program_count": len(resource_programs),
            "resource_result_component_count": component_total,
            "resource_value_bound_read_count": len(bm) if not violations else 0,
            "resource_value_bound_component_count": component_total if not violations else 0,
            "lds_write_count": len(input_lds),
            "target_operation_count": len(records),
            "proven_target_operation_count": len(records) if not violations else 0,
            "runtime_buffer_content_promotions": 0,
            "lds_runtime_address_promotions": 0,
            "engine_semantic_promotions": 0,
            "violation_count": len(violations),
        },
        "programs": copy.deepcopy(programs),
        "records": fused_records,
        "violations": violations,
    }


def _self_test() -> None:
    sha = "a" * 64
    desc = []
    for i in range(8, 12):
        desc.append({"register": f"s{i}", "node": f"scalarref:s{i}", "external_graph": "g", "external_node": f"entry:s{i}", "external_node_kind": "PROGRAM_ENTRY", "external_ref": f"g#entry:s{i}", "exactness": "EXACT"})
    res = {
        "program_sha256": sha, "instruction": 2, "address": "000000000010", "opcode": "tbuffer_load_format_xyzw",
        "kind": "GFX7_TYPED_BUFFER_RESOURCE_PROVENANCE", "destination": "v[0:3]",
        "vaddr": {"register": "v0", "current_value": "write:i1:v0"},
        "resource_descriptor": {"register_range": "s[8:11]", "components": desc, "status": "UNRESOLVED_CONCRETE_RESOURCE", "reason_code": "X"},
        "soffset": {"kind": "ENCODED_LITERAL_32", "token": "0", "u32_bits": 0, "raw_source_node": "raw", "literal_node": "lit", "exactness": "EXACT"},
        "addressing": {"offset12": 0, "idxen": True, "offen": False, "addr64": False, "glc": False, "slc": False},
        "format": {"dfmt": "32_32_32_32", "nfmt": "float", "component_count": 4},
        "result_component_nodes": [f"special:i2:component:{i}" for i in range(4)], "memory_value_status": "OPAQUE",
    }
    val = {
        "gcn_sha256": sha, "instruction": 2, "address": "000000000010",
        "operation": "GFX7_TYPED_BUFFER_READ_XYZW_FROM_BOUND_IMM_CONST_BUFFER",
        "addressing": {"addr64": False, "idxen": True, "offen": False, "offset12": 0, "soffset_u32": 0, "vaddr_state_node": "write:i1:v0"},
        "format": {"dfmt": "32_32_32_32", "nfmt": "float", "result_components": 4},
        "resource_identity": {"usage_name": "ImmConstBuffer", "api_slot": 10, "descriptor_window": "s[8:11]", "reaching_state": "PROGRAM_ENTRY_USER_DATA"},
        "numeric_value_status": "RUNTIME_BUFFER_CONTENT_OPAQUE",
        "components": [{"component": i, "existing_special_node": f"special:i2:component:{i}", "resource_value_node": f"rv{i}", "value_expression": f"ImmConstBuffer[api=10][index=write:i1:v0].{'xyzw'[i]}"} for i in range(4)],
    }
    compare_resource(res, val)
    bad = copy.deepcopy(val); bad["addressing"]["offset12"] = 4
    try:
        compare_resource(res, bad)
        raise AssertionError("mismatched resource addressing was admitted")
    except GateError:
        pass


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provenance-report", type=Path, required=True)
    ap.add_argument("--resource-value-report", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        _self_test()
    report = analyze(load_json(args.provenance_report), load_json(args.resource_value_report))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "coverage": report["coverage"]}, sort_keys=True))
    if report["status"] != STATUS_EXACT:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
