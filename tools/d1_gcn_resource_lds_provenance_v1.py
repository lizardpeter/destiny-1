#!/usr/bin/env python3
"""Source-closed symbolic resource/LDS provenance over existing D1 GCN IR/SSA artifacts.

This layer deliberately does not parse GCN or reconstruct SSA. It joins the generic
structural IR, integrated vector value-binding graph, and scalar/M0 SSA by exact
program/instruction identity. Concrete resource identities and concrete LDS addresses
remain unresolved until their external ABI/memory inputs are proven.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence

SCHEMA = "d1_gcn_resource_lds_provenance/v1"
STATUS_EXACT = "D1_GCN_RESOURCE_LDS_PROVENANCE_EXACT_SYMBOLIC"
STATUS_BAD = "D1_GCN_RESOURCE_LDS_PROVENANCE_WITH_VIOLATIONS"
TARGETS = {"tbuffer_load_format_xyzw", "ds_write2_b32"}
PARSE_EXACT = "D1_GCN_STRUCTURAL_PARSE_ACCOUNTING_EXACT"
BIND_EXACT = "D1_GCN_VECTOR_SPECIAL_VALUE_BINDING_EXACT"
SCALAR_EXACT = "D1_GCN_SGPR_SSA_EXACT"

RE_VGPR = re.compile(r"^v(\d+)$")
RE_SGPR = re.compile(r"^s(\d+)$")
RE_RANGE = re.compile(r"^s\[(\d+):(\d+)\]$")
RE_OFFSET0 = re.compile(r"(?:^|\s)offset0:(\d+)(?:\s|$)")
RE_OFFSET1 = re.compile(r"(?:^|\s)offset1:(\d+)(?:\s|$)")
RE_GDS = re.compile(r"(?:^|\s)gds(?:\s|$)")


class GateError(RuntimeError):
    pass


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        obj = json.load(f)
    if not isinstance(obj, dict):
        raise GateError(f"{path}: top-level JSON must be an object")
    return obj


def node_values(bound: Mapping[str, Any]) -> List[Dict[str, Any]]:
    nodes = bound.get("nodes")
    vals: Iterable[Any]
    if isinstance(nodes, dict):
        vals = nodes.values()
    elif isinstance(nodes, list):
        vals = nodes
    else:
        raise GateError("binding nodes must be an object or array")
    return [x for x in vals if isinstance(x, dict)]


def expand_sgpr_range(token: str) -> List[str]:
    m = RE_RANGE.fullmatch(token)
    if not m:
        raise GateError(f"expected SGPR range, got {token!r}")
    lo, hi = int(m.group(1)), int(m.group(2))
    if hi < lo:
        raise GateError(f"descending SGPR range {token!r}")
    return [f"s{i}" for i in range(lo, hi + 1)]


def instruction_identity(ir_ins: Mapping[str, Any], bound_ins: Mapping[str, Any], scalar_ins: Mapping[str, Any]) -> None:
    expected = (ir_ins.get("index"), ir_ins.get("address_hex"), ir_ins.get("opcode"))
    got_b = (bound_ins.get("instruction"), bound_ins.get("address"), bound_ins.get("opcode"))
    got_s = (scalar_ins.get("instruction"), scalar_ins.get("address"), scalar_ins.get("opcode"))
    if expected != got_b:
        raise GateError(f"binding instruction identity mismatch: expected={expected!r} got={got_b!r}")
    if expected != got_s:
        raise GateError(f"scalar instruction identity mismatch: expected={expected!r} got={got_s!r}")


def vgpr_use_map(bound_ins: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for u in bound_ins.get("vgpr_uses", []):
        if not isinstance(u, dict):
            raise GateError("vgpr_uses entry is not an object")
        reg, val = u.get("register"), u.get("value")
        if not isinstance(reg, str) or not RE_VGPR.fullmatch(reg) or not isinstance(val, str) or not val:
            raise GateError(f"malformed VGPR use {u!r}")
        prior = out.get(reg)
        if prior is not None and prior != u:
            raise GateError(f"conflicting current values for {reg}")
        out[reg] = dict(u)
    return out


def require_unique(nodes: Sequence[Mapping[str, Any]], pred, what: str) -> Dict[str, Any]:
    got = [dict(n) for n in nodes if pred(n)]
    if len(got) != 1:
        raise GateError(f"expected exactly one {what}, found {len(got)}")
    return got[0]


def tbuffer_record(program_sha: str, shader: Any, ir_ins: Mapping[str, Any], bound_ins: Mapping[str, Any], nodes: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    idx = int(ir_ins["index"])
    inodes = [n for n in nodes if n.get("instruction") == idx]
    op = require_unique(
        inodes,
        lambda n: n.get("kind") == "GFX7_TYPED_BUFFER_LOAD_XYZW" and n.get("opcode") == "tbuffer_load_format_xyzw",
        "GFX7 typed-buffer operation node",
    )
    if op.get("id") != f"special:i{idx}:operation":
        raise GateError(f"unexpected typed-buffer operation node id {op.get('id')!r}")
    detail = op.get("detail")
    if not isinstance(detail, dict):
        raise GateError("typed-buffer operation detail is missing")

    operands = ir_ins.get("operands")
    if not isinstance(operands, list) or len(operands) < 4:
        raise GateError("typed-buffer structural operand vector is malformed")
    dest, vaddr, srsrc = operands[0], operands[1], operands[2]
    if detail.get("vaddr_register") != vaddr or detail.get("srsrc_register_range") != srsrc:
        raise GateError("typed-buffer semantic detail disagrees with structural operand identities")

    regs = expand_sgpr_range(srsrc)
    if len(regs) != 4:
        raise GateError(f"typed-buffer SRSRC must contain exactly four SGPRs, got {regs!r}")

    uses = vgpr_use_map(bound_ins)
    if vaddr not in uses:
        raise GateError(f"typed-buffer VADDR {vaddr} missing exact current VGPR value")
    vaddr_use = uses[vaddr]
    if vaddr_use["value"] not in op.get("inputs", []):
        raise GateError("typed-buffer operation node does not consume current VADDR value")

    srefs = [n for n in inodes if n.get("kind") == "EXACT_SCALAR_SSA_STATE_REFERENCE" and isinstance(n.get("detail"), dict)]
    desc_refs: List[Dict[str, Any]] = []
    for reg in regs:
        n = require_unique(
            srefs,
            lambda x, reg=reg: x["detail"].get("role") == "srsrc" and x["detail"].get("register") == reg,
            f"SRSRC scalar SSA reference for {reg}",
        )
        if n.get("id") not in op.get("inputs", []):
            raise GateError(f"typed-buffer operation node does not consume SRSRC node {n.get('id')!r}")
        d = n["detail"]
        for k in ("external_graph", "external_node", "external_ref"):
            if not isinstance(d.get(k), str) or not d[k]:
                raise GateError(f"SRSRC {reg} missing exact scalar provenance field {k}")
        desc_refs.append({
            "register": reg,
            "node": n["id"],
            "external_graph": d["external_graph"],
            "external_node": d["external_node"],
            "external_node_kind": d.get("external_node_kind"),
            "external_ref": d["external_ref"],
            "exactness": n.get("exactness"),
        })

    soff_token = detail.get("soffset_token")
    if not isinstance(soff_token, str) or not soff_token:
        raise GateError("typed-buffer SOFFSET token missing")
    soff: Dict[str, Any]
    if RE_SGPR.fullmatch(soff_token):
        n = require_unique(
            srefs,
            lambda x: x["detail"].get("role") == "soffset" and x["detail"].get("register") == soff_token,
            f"SOFFSET scalar SSA reference for {soff_token}",
        )
        if n.get("id") not in op.get("inputs", []):
            raise GateError("typed-buffer operation node does not consume SOFFSET SSA reference")
        d = n["detail"]
        soff = {
            "kind": "SCALAR_SSA_REFERENCE", "token": soff_token, "node": n.get("id"),
            "external_node": d.get("external_node"), "external_ref": d.get("external_ref"),
            "exactness": n.get("exactness"),
        }
    else:
        slot = require_unique(
            inodes,
            lambda n: n.get("kind") == "ARCHITECTURAL_SOURCE_OPERAND_SLOT" and isinstance(n.get("detail"), dict)
            and n["detail"].get("role") == "soffset" and n["detail"].get("token") == soff_token,
            f"SOFFSET raw source slot for {soff_token}",
        )
        if slot.get("id") not in op.get("inputs", []):
            raise GateError("typed-buffer operation node does not consume SOFFSET raw source slot")
        lit = require_unique(
            inodes,
            lambda n: n.get("kind") == "ISA_LITERAL_32" and isinstance(n.get("detail"), dict)
            and n["detail"].get("role") == "soffset" and n["detail"].get("token") == soff_token,
            f"SOFFSET literal for {soff_token}",
        )
        if lit.get("id") not in slot.get("inputs", []):
            raise GateError("SOFFSET raw source slot does not consume exact literal node")
        soff = {
            "kind": "ENCODED_LITERAL_32", "token": soff_token, "u32_bits": lit["detail"].get("u32_bits"),
            "raw_source_node": slot.get("id"), "literal_node": lit.get("id"), "exactness": lit.get("exactness"),
        }

    comps = sorted(
        [n for n in inodes if n.get("kind") == "GFX7_TYPED_BUFFER_RESULT_COMPONENT_OPAQUE" and n.get("opcode") == "tbuffer_load_format_xyzw"],
        key=lambda n: (n.get("detail") or {}).get("component", -1),
    )
    if len(comps) != 4 or [(n.get("detail") or {}).get("component") for n in comps] != [0, 1, 2, 3]:
        raise GateError("typed-buffer result component identity coverage is not exactly xyzw")
    for n in comps:
        if n.get("inputs") != [op["id"]]:
            raise GateError(f"typed-buffer component {n.get('id')!r} not sourced solely by operation node")

    return {
        "program_sha256": program_sha, "shader": shader, "instruction": idx, "address": ir_ins.get("address_hex"),
        "opcode": "tbuffer_load_format_xyzw", "kind": "GFX7_TYPED_BUFFER_RESOURCE_PROVENANCE",
        "exactness": "ARCHITECTURAL_OPERAND_AND_SSA_PROVENANCE_EXACT_CONCRETE_RESOURCE_UNRESOLVED",
        "destination": dest,
        "vaddr": {"register": vaddr, "current_value": vaddr_use["value"]},
        "resource_descriptor": {
            "register_range": srsrc, "components": desc_refs, "status": "UNRESOLVED_CONCRETE_RESOURCE",
            "reason_code": "DESCRIPTOR_BINARY_AND_D1_RESOURCE_TABLE_MAPPING_NOT_YET_PROVEN",
        },
        "soffset": soff,
        "addressing": {
            "offset12": detail.get("offset12"), "idxen": bool(detail.get("idxen")), "offen": bool(detail.get("offen")),
            "addr64": bool(detail.get("addr64")), "glc": bool(detail.get("glc")), "slc": bool(detail.get("slc")),
        },
        "format": {"dfmt": detail.get("dfmt"), "nfmt": detail.get("nfmt"), "component_count": detail.get("component_count")},
        "result_component_nodes": [n["id"] for n in comps],
        "memory_value_status": detail.get("memory_value_status"),
    }


def parse_ds_role_register(token: str, role: str) -> str:
    atom = token.split()[0]
    if not RE_VGPR.fullmatch(atom):
        raise GateError(f"DS {role} is not one exact VGPR token: {token!r}")
    return atom


def ds_record(program_sha: str, shader: Any, ir_ins: Mapping[str, Any], bound_ins: Mapping[str, Any], scalar_ins: Mapping[str, Any]) -> Dict[str, Any]:
    idx = int(ir_ins["index"])
    operands = ir_ins.get("operands")
    if not isinstance(operands, list) or len(operands) < 3:
        raise GateError("ds_write2_b32 structural operand vector is malformed")
    addr = parse_ds_role_register(operands[0], "ADDR")
    data0 = parse_ds_role_register(operands[1], "DATA0")
    data1 = parse_ds_role_register(operands[2], "DATA1")
    joined = " ".join(str(x) for x in operands)
    if RE_GDS.search(joined):
        raise GateError("ds_write2_b32 GDS semantics are intentionally not admitted by LDS provenance v1")

    m0 = scalar_ins.get("implicit_m0_use")
    if not isinstance(m0, dict):
        raise GateError("ds_write2_b32 missing exact implicit M0 SSA use")
    if m0.get("register") != "m0" or m0.get("kind") != "ARCHITECTURAL_IMPLICIT_M0" or m0.get("category") != "LDS_DS_M0_BOUNDS":
        raise GateError(f"ds_write2_b32 implicit M0 classification mismatch: {m0!r}")
    if not isinstance(m0.get("value"), str) or not m0["value"]:
        raise GateError("ds_write2_b32 M0 SSA value identity missing")

    uses = vgpr_use_map(bound_ins)
    role_values: Dict[str, Dict[str, str]] = {}
    for role, reg in (("addr", addr), ("data0", data0), ("data1", data1)):
        u = uses.get(reg)
        if u is None:
            raise GateError(f"ds_write2_b32 {role} register {reg} missing current VGPR value")
        role_values[role] = {"register": reg, "current_value": u["value"]}

    m0o, m1o = RE_OFFSET0.search(joined), RE_OFFSET1.search(joined)
    off0 = int(m0o.group(1)) if m0o else 0
    off1 = int(m1o.group(1)) if m1o else 0
    if not (0 <= off0 <= 255 and 0 <= off1 <= 255):
        raise GateError(f"ds_write2_b32 offset outside unsigned 8-bit field: {(off0, off1)!r}")

    return {
        "program_sha256": program_sha, "shader": shader, "instruction": idx, "address": ir_ins.get("address_hex"),
        "opcode": "ds_write2_b32", "kind": "GFX7_DS_WRITE2_B32_LDS_PROVENANCE",
        "exactness": "ARCHITECTURAL_OPERAND_AND_SSA_PROVENANCE_EXACT_CONCRETE_LDS_ADDRESS_UNRESOLVED",
        "memory_space": "LDS", "gds": False,
        "addr": role_values["addr"], "data0": role_values["data0"], "data1": role_values["data1"],
        "offsets": {
            "offset0_encoded_u8": off0, "offset1_encoded_u8": off1,
            "offset0_effective_bytes": off0 * 4, "offset1_effective_bytes": off1 * 4,
            "scale_bytes_per_encoded_unit": 4,
        },
        "implicit_m0": {
            "register": "m0", "current_value": m0["value"], "kind": m0["kind"], "category": m0["category"],
            "architectural_role": "LDS_BYTE_SIZE_CLAMP_BOUND",
        },
        "stores": [
            {"address_expression": "VGPR[ADDR] + offset0*4", "data_role": "DATA0", "width_bits": 32},
            {"address_expression": "VGPR[ADDR] + offset1*4", "data_role": "DATA1", "width_bits": 32},
        ],
        "concrete_address_status": "UNRESOLVED_EXTERNAL_LANE_AND_LDS_ALLOCATION_STATE",
    }


def verify_program_triplet(stem: str, ir: Mapping[str, Any], bound: Mapping[str, Any], scalar: Mapping[str, Any]) -> None:
    if ir.get("status") != "D1_GCN_STRUCTURAL_IR_COMPLETE":
        raise GateError(f"{stem}: structural IR status is not complete")
    if (ir.get("parse_accounting") or {}).get("status") != PARSE_EXACT:
        raise GateError(f"{stem}: structural parse accounting is not exact")
    if bound.get("status") != BIND_EXACT:
        raise GateError(f"{stem}: vector binding status is not exact")
    if (bound.get("parse_accounting") or {}).get("status") != PARSE_EXACT:
        raise GateError(f"{stem}: vector binding parse accounting is not exact")
    if scalar.get("status") != SCALAR_EXACT:
        raise GateError(f"{stem}: scalar SSA status is not exact")
    if (scalar.get("parse_accounting") or {}).get("status") != PARSE_EXACT:
        raise GateError(f"{stem}: scalar SSA parse accounting is not exact")
    shaders = (ir.get("shader"), bound.get("shader"), scalar.get("shader"))
    if len(set(shaders)) != 1:
        raise GateError(f"{stem}: shader identity mismatch {shaders!r}")
    ii, bi, si = ir.get("instructions"), bound.get("instructions"), scalar.get("instructions")
    if not all(isinstance(x, list) for x in (ii, bi, si)):
        raise GateError(f"{stem}: one or more instruction vectors missing")
    if not (len(ii) == len(bi) == len(si)):
        raise GateError(f"{stem}: instruction count mismatch {(len(ii), len(bi), len(si))!r}")
    for i in range(len(ii)):
        instruction_identity(ii[i], bi[i], si[i])


def parse_expect(items: Sequence[str]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for item in items:
        if "=" not in item:
            raise GateError(f"--expect-opcode needs OPCODE=COUNT, got {item!r}")
        op, raw = item.split("=", 1)
        if not op or op in out:
            raise GateError(f"invalid or duplicate expected opcode {op!r}")
        try:
            n = int(raw)
        except ValueError as e:
            raise GateError(f"invalid expected count {raw!r}") from e
        if n < 0:
            raise GateError("expected count must be non-negative")
        out[op] = n
    return out


def stems(dirpath: Path) -> Dict[str, Path]:
    if not dirpath.is_dir():
        raise GateError(f"missing directory {dirpath}")
    out = {p.stem: p for p in sorted(dirpath.glob("*.json"))}
    if not out:
        raise GateError(f"no JSON inputs in {dirpath}")
    return out


def analyze_corpus(ir_dir: Path, binding_dir: Path, scalar_dir: Path, expected: Mapping[str, int]) -> Dict[str, Any]:
    irs, bounds, scalars = stems(ir_dir), stems(binding_dir), stems(scalar_dir)
    sets = (set(irs), set(bounds), set(scalars))
    violations: List[Dict[str, Any]] = []
    if not (sets[0] == sets[1] == sets[2]):
        violations.append({
            "code": "PROGRAM_SET_MISMATCH", "ir_only": sorted(sets[0] - sets[1] - sets[2]),
            "binding_only": sorted(sets[1] - sets[0] - sets[2]), "scalar_only": sorted(sets[2] - sets[0] - sets[1]),
            "counts": [len(x) for x in sets],
        })
    common = sorted(set.intersection(*sets))
    records: List[Dict[str, Any]] = []
    target_counts: Counter[str] = Counter()
    accounted: Counter[str] = Counter()
    unresolved: Counter[str] = Counter()
    reason_counts: Counter[str] = Counter()
    structural_total = 0
    exact_programs = 0
    program_rows: List[Dict[str, Any]] = []

    for stem in common:
        pviols: List[Dict[str, Any]] = []
        try:
            ir, bound, scalar = load_json(irs[stem]), load_json(bounds[stem]), load_json(scalars[stem])
            verify_program_triplet(stem, ir, bound, scalar)
            structural_total += len(ir["instructions"])
            nodes = node_values(bound)
            pc, pa = Counter(), Counter()
            for i, ir_ins in enumerate(ir["instructions"]):
                op = ir_ins.get("opcode")
                if op not in TARGETS:
                    continue
                target_counts[op] += 1
                pc[op] += 1
                try:
                    if op == "tbuffer_load_format_xyzw":
                        rec = tbuffer_record(stem, ir.get("shader"), ir_ins, bound["instructions"][i], nodes)
                        unresolved["UNRESOLVED_CONCRETE_RESOURCE"] += 1
                        reason_counts[rec["resource_descriptor"]["reason_code"]] += 1
                    else:
                        rec = ds_record(stem, ir.get("shader"), ir_ins, bound["instructions"][i], scalar["instructions"][i])
                        unresolved["UNRESOLVED_EXTERNAL_LANE_AND_LDS_ALLOCATION_STATE"] += 1
                        reason_counts[rec["concrete_address_status"]] += 1
                    records.append(rec)
                    accounted[op] += 1
                    pa[op] += 1
                except GateError as e:
                    pviols.append({"code": "TARGET_PROVENANCE_FAILURE", "instruction": i, "opcode": op, "detail": str(e)})
            if not pviols:
                exact_programs += 1
            program_rows.append({
                "program_sha256": stem, "shader": ir.get("shader"), "structural_instruction_count": len(ir["instructions"]),
                "target_counts": dict(sorted(pc.items())), "accounted_counts": dict(sorted(pa.items())),
                "status": STATUS_EXACT if not pviols else STATUS_BAD, "violations": pviols,
            })
        except (GateError, KeyError, TypeError, ValueError) as e:
            pviols.append({"code": "PROGRAM_JOIN_FAILURE", "detail": str(e)})
            program_rows.append({"program_sha256": stem, "status": STATUS_BAD, "violations": pviols})
        violations.extend({"program_sha256": stem, **v} for v in pviols)

    for op, n in expected.items():
        actual = target_counts.get(op, 0)
        if actual != n:
            violations.append({"code": "EXPECTED_OPCODE_COUNT_MISMATCH", "opcode": op, "expected": n, "actual": actual})
    for op in TARGETS:
        if target_counts[op] != accounted[op]:
            violations.append({"code": "TARGET_ACCOUNTING_MISMATCH", "opcode": op, "target": target_counts[op], "accounted": accounted[op]})

    status = STATUS_EXACT if not violations else STATUS_BAD
    return {
        "schema": SCHEMA, "status": status,
        "semantic_boundary": {
            "claim": "Exact program/instruction/operand and current SSA-value provenance for admitted GFX7 typed-buffer and LDS-write operations; external resource identities, descriptor contents, lane values, LDS allocation/base, and backing memory remain unresolved unless separately proven.",
            "no_stage_inference": True, "no_concrete_resource_guessing": True,
            "no_concrete_memory_address_guessing": True, "gds_admitted": False,
        },
        "sources": {
            "amd_gcn3_isa": {
                "document_id": "70645", "revision": "1.1", "release_date": "2016-08-01",
                "ds_write2_b32": "DS[ADDR+offset0*4]=D0; DS[ADDR+offset1*4]=D1",
                "m0_lds_role": "All LDS operations require initialized M0; M0 supplies LDS byte-size clamp state.",
            },
            "llvm_gfx7_syntax": "ds_write2_b32 vaddr, vdata0, vdata1 offset0 offset1 gds",
        },
        "coverage": {
            "input_program_count": len(common), "exact_symbolic_program_count": exact_programs,
            "structural_instruction_count": structural_total, "target_instruction_count": sum(target_counts.values()),
            "target_counts": dict(sorted(target_counts.items())), "accounted_counts": dict(sorted(accounted.items())),
            "exact_symbolic_provenance_instruction_count": sum(accounted.values()),
            "unresolved_downstream_counts": dict(sorted(unresolved.items())),
            "unresolved_reason_counts": dict(sorted(reason_counts.items())),
            "expected_opcode_counts": dict(sorted(expected.items())), "violation_count": len(violations),
        },
        "programs": program_rows, "records": records, "violations": violations,
    }


def _self_test() -> None:
    assert expand_sgpr_range("s[8:11]") == ["s8", "s9", "s10", "s11"]
    try:
        expand_sgpr_range("s[11:8]")
        raise AssertionError("descending SGPR range admitted")
    except GateError:
        pass

    ir = {"index": 7, "address_hex": "000000000038", "opcode": "ds_write2_b32", "operands": ["v1", "v11", "v11 offset0:6 offset1:7"]}
    b = {"instruction": 7, "address": "000000000038", "opcode": "ds_write2_b32", "vgpr_uses": [{"register": "v1", "value": "input:v1"}, {"register": "v11", "value": "write:i6:v11"}]}
    s = {"instruction": 7, "address": "000000000038", "opcode": "ds_write2_b32", "implicit_m0_use": {"register": "m0", "value": "write:i2:m0", "kind": "ARCHITECTURAL_IMPLICIT_M0", "category": "LDS_DS_M0_BOUNDS"}}
    instruction_identity(ir, b, s)
    r = ds_record("0" * 64, "S", ir, b, s)
    assert r["data0"]["current_value"] == r["data1"]["current_value"] == "write:i6:v11"
    assert r["offsets"]["offset0_effective_bytes"] == 24 and r["offsets"]["offset1_effective_bytes"] == 28

    ir0 = dict(ir); ir0["operands"] = ["v1", "v2", "v3 offset1:1"]
    b0 = dict(b); b0["vgpr_uses"] = [{"register": "v1", "value": "a"}, {"register": "v2", "value": "b"}, {"register": "v3", "value": "c"}]
    r0 = ds_record("0" * 64, "S", ir0, b0, s)
    assert r0["offsets"]["offset0_encoded_u8"] == 0 and r0["offsets"]["offset1_encoded_u8"] == 1

    bad = dict(ir); bad["operands"] = ["v1", "v2", "v3 gds"]
    try:
        ds_record("0" * 64, "S", bad, b0, s)
        raise AssertionError("GDS form admitted")
    except GateError:
        pass
    try:
        ds_record("0" * 64, "S", ir0, b0, {**s, "implicit_m0_use": None})
        raise AssertionError("missing M0 admitted")
    except GateError:
        pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ir-dir", type=Path)
    ap.add_argument("--binding-dir", type=Path)
    ap.add_argument("--scalar-dir", type=Path)
    ap.add_argument("--output", type=Path)
    ap.add_argument("--expect-opcode", action="append", default=[])
    ap.add_argument("--self-test", action="store_true")
    ns = ap.parse_args()
    try:
        _self_test()
        if ns.self_test and not ns.ir_dir:
            print("SELF_TEST_OK")
            return 0
        if not all((ns.ir_dir, ns.binding_dir, ns.scalar_dir, ns.output)):
            raise GateError("--ir-dir, --binding-dir, --scalar-dir, and --output are required for corpus analysis")
        expected = parse_expect(ns.expect_opcode)
        report = analyze_corpus(ns.ir_dir, ns.binding_dir, ns.scalar_dir, expected)
        ns.output.parent.mkdir(parents=True, exist_ok=True)
        ns.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"status": report["status"], "coverage": report["coverage"]}, indent=2, sort_keys=True))
        return 0 if report["status"] == STATUS_EXACT else 1
    except (GateError, OSError, json.JSONDecodeError) as e:
        print(f"ERROR: {e}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
