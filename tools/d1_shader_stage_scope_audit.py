#!/usr/bin/env python3
"""Audit the current D1 PS4 archive for shader-stage scope beyond proven PS/VS classes.

The current universal shader census deliberately starts from two byte/source-proven
logical header/native payload pairs:

  * type/subtype 32:8 -> 1:8 : PixelShader
  * type/subtype 32:9 -> 1:9 : VertexShader

This tool prevents that useful PS/VS census from being mislabeled as the complete
Destiny shader universe. It consumes the exact archive-wide metadata summary and the
exact PS/VS corpus plan, enumerates every current 32:* and 1:* subtype population, and
reports all non-proven subtype classes as an explicit scope frontier.

It does not infer that an adjacent subtype is a shader stage. Additional stage names
must be promoted only after serialized header/reference structure and native OrbShdr
stage bytes prove the relationship.
"""
from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path

SUMMARY_SCHEMA = "d1_remote_everything_index/v1"
PLAN_SCHEMA = "d1_shader_corpus_plan/v1"
STATUS = "D1_SHADER_STAGE_SCOPE_AUDIT_EXACT"
PAIR = {
    "PS": {"header_type_subtype": "32:8", "native_type_subtype": "1:8", "orb_stage": "PixelShader"},
    "VS": {"header_type_subtype": "32:9", "native_type_subtype": "1:9", "orb_stage": "VertexShader"},
}
TYPE_KEY_RE = re.compile(r"^(\d+):(\d+)$")


def _typed_counts(summary: dict, major: int) -> dict[str, int]:
    out: dict[str, int] = {}
    for key, value in (summary.get("current_type_subtype_counts") or {}).items():
        m = TYPE_KEY_RE.fullmatch(str(key))
        if not m:
            raise ValueError(f"malformed type/subtype count key: {key!r}")
        if int(m.group(1)) == major:
            out[str(key)] = int(value)
    return dict(sorted(out.items(), key=lambda kv: int(kv[0].split(':')[1])))


def build(summary: dict, plan: dict) -> dict:
    violations: list[str] = []
    if summary.get("schema") != SUMMARY_SCHEMA:
        violations.append(f"summary_schema:{summary.get('schema')!r}")
    if summary.get("status") != "D1_REMOTE_EVERYTHING_INDEX_COMPLETE":
        violations.append(f"summary_status:{summary.get('status')!r}")
    if summary.get("violations"):
        violations.append(f"summary_violations:{len(summary['violations'])}")
    if plan.get("schema") != PLAN_SCHEMA:
        violations.append(f"plan_schema:{plan.get('schema')!r}")
    if plan.get("status") != "D1_SHADER_CORPUS_PLAN_COMPLETE":
        violations.append(f"plan_status:{plan.get('status')!r}")
    if plan.get("violations"):
        violations.append(f"plan_violations:{len(plan['violations'])}")

    type32 = _typed_counts(summary, 32)
    type1 = _typed_counts(summary, 1)
    plan_stages = (plan.get("header_population") or {}).get("stage_counts") or {}

    proven = []
    for stage in ("PS", "VS"):
        spec = PAIR[stage]
        hk = spec["header_type_subtype"]
        nk = spec["native_type_subtype"]
        hcount = int(type32.get(hk, 0))
        ncount = int(type1.get(nk, 0))
        pcount = int(plan_stages.get(stage, 0))
        if hcount <= 0:
            violations.append(f"proven_header_class_absent:{stage}:{hk}")
        if ncount <= 0:
            violations.append(f"proven_native_class_absent:{stage}:{nk}")
        if pcount != hcount:
            violations.append(f"plan_header_count:{stage}:{pcount}!={hcount}")
        proven.append({
            "stage": stage,
            **spec,
            "current_header_entry_count": hcount,
            "current_native_entry_count": ncount,
            "planned_header_count": pcount,
        })

    proven_header_keys = {x["header_type_subtype"] for x in PAIR.values()}
    proven_native_keys = {x["native_type_subtype"] for x in PAIR.values()}
    unresolved32 = [
        {"type_subtype": k, "current_entry_count": v}
        for k, v in type32.items() if k not in proven_header_keys
    ]
    unresolved1 = [
        {"type_subtype": k, "current_entry_count": v}
        for k, v in type1.items() if k not in proven_native_keys
    ]

    plan_total = int((plan.get("header_population") or {}).get("total", -1))
    proven_header_total = sum(int(x["current_header_entry_count"]) for x in proven)
    if plan_total != proven_header_total:
        violations.append(f"plan_total:{plan_total}!={proven_header_total}")

    return {
        "schema": "d1_shader_stage_scope_audit/v1",
        "status": STATUS if not violations else "D1_SHADER_STAGE_SCOPE_AUDIT_WITH_VIOLATIONS",
        "coverage": {
            "current_archive_entry_count": int(summary.get("current_entry_count", -1)),
            "proven_ps_vs_header_count": proven_header_total,
            "ps_vs_plan_header_count": plan_total,
            "type32_entry_count": sum(type32.values()),
            "type1_entry_count": sum(type1.values()),
            "type32_subtype_count": len(type32),
            "type1_subtype_count": len(type1),
            "unresolved_type32_subtype_count": len(unresolved32),
            "unresolved_type1_subtype_count": len(unresolved1),
        },
        "proven_shader_stage_pairs": proven,
        "current_type32_subtypes": [
            {"type_subtype": k, "current_entry_count": v,
             "scope": "PROVEN_SHADER_HEADER" if k in proven_header_keys else "UNRESOLVED_CLASS"}
            for k, v in type32.items()
        ],
        "current_type1_subtypes": [
            {"type_subtype": k, "current_entry_count": v,
             "scope": "PROVEN_SHADER_NATIVE" if k in proven_native_keys else "UNRESOLVED_CLASS"}
            for k, v in type1.items()
        ],
        "additional_stage_or_class_frontier": {
            "type32_unresolved": unresolved32,
            "type1_unresolved": unresolved1,
            "semantic_stage_count": None,
            "reason": (
                "Type/subtype adjacency alone does not prove shader-stage identity. "
                "Each candidate requires exact serialized header/reference and native OrbShdr-stage proof."
            ),
        },
        "scope_statement": (
            "The current 37,892-header census is exact for the proven PS/VS classes only. "
            "It may be called game-wide PS/VS coverage, but not complete all-stage shader coverage "
            "until every remaining relevant archive class is either source/byte-proven as another "
            "shader stage and added, or proven non-shader."
        ),
        "violations": violations,
    }


def self_test() -> None:
    summary = {
        "schema": SUMMARY_SCHEMA,
        "status": "D1_REMOTE_EVERYTHING_INDEX_COMPLETE",
        "violations": [],
        "current_entry_count": 100,
        "current_type_subtype_counts": {
            "1:8": 9, "1:9": 6, "1:10": 2,
            "32:1": 20, "32:8": 10, "32:9": 7, "32:10": 3,
        },
    }
    plan = {
        "schema": PLAN_SCHEMA,
        "status": "D1_SHADER_CORPUS_PLAN_COMPLETE",
        "violations": [],
        "header_population": {"total": 17, "stage_counts": {"PS": 10, "VS": 7}},
    }
    out = build(summary, plan)
    assert out["status"] == STATUS, out["violations"]
    assert out["coverage"]["proven_ps_vs_header_count"] == 17
    assert out["additional_stage_or_class_frontier"]["type32_unresolved"] == [
        {"type_subtype": "32:1", "current_entry_count": 20},
        {"type_subtype": "32:10", "current_entry_count": 3},
    ]
    assert {x["type_subtype"] for x in out["additional_stage_or_class_frontier"]["type1_unresolved"]} == {"1:10"}

    bad_plan = json.loads(json.dumps(plan))
    bad_plan["header_population"]["stage_counts"]["PS"] = 9
    bad = build(summary, bad_plan)
    assert bad["status"] != STATUS
    assert any(x.startswith("plan_header_count:PS") for x in bad["violations"])
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "audit.json"
        p.write_text(json.dumps(out))
        assert json.loads(p.read_text())["status"] == STATUS
    print("D1_SHADER_STAGE_SCOPE_AUDIT_SELF_TEST_OK")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", type=Path)
    ap.add_argument("--plan", type=Path)
    ap.add_argument("-o", "--output", type=Path)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        self_test()
        return 0
    if a.summary is None or a.plan is None or a.output is None:
        ap.error("--summary, --plan and --output are required unless --self-test is used")
    out = build(json.loads(a.summary.read_text()), json.loads(a.plan.read_text()))
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n")
    print(
        "STATUS", out["status"],
        "PSVS_HEADERS", out["coverage"]["proven_ps_vs_header_count"],
        "TYPE32_SUBTYPES", out["coverage"]["type32_subtype_count"],
        "TYPE1_SUBTYPES", out["coverage"]["type1_subtype_count"],
        "UNRESOLVED32", out["coverage"]["unresolved_type32_subtype_count"],
        "UNRESOLVED1", out["coverage"]["unresolved_type1_subtype_count"],
        "VIOLATIONS", len(out["violations"]),
    )
    print("TYPE32_FRONTIER", json.dumps(out["additional_stage_or_class_frontier"]["type32_unresolved"], sort_keys=True))
    print("TYPE1_FRONTIER", json.dumps(out["additional_stage_or_class_frontier"]["type1_unresolved"], sort_keys=True))
    return 0 if out["status"] == STATUS else 2


if __name__ == "__main__":
    raise SystemExit(main())
