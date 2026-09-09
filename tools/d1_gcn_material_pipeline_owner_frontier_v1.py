#!/usr/bin/env python3
"""Exact structural material graphics-pipeline ownership frontier for Destiny 1 PS4.

This corrects the earlier assumption that the material dword at +0x28 universally names a
VertexShader header. The field is kept as a neutral serialized pre-raster slot. Exact
OrbShdr stage is authoritative: frozen 32:9 corpus headers resolve to VertexShader/DomainShader,
while the separately source-closed 32:11 wrapper family resolves to LocalShader. Remaining
fallback/special references stay opaque rather than being coerced into shader stages.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
from pathlib import Path

OWNER_SCHEMA = "d1_gcn_material_shader_owner_frontier/v1"
OWNER_FAILED_STATUS = "D1_GCN_MATERIAL_SHADER_OWNER_FRONTIER_WITH_VIOLATIONS"
SHADER_SCHEMA = "d1_remote_ps4_shader_corpus_extract/v3"
SHADER_STATUS = "D1_REMOTE_PS4_SHADER_CORPUS_EXACT_PS_VS_DS"
PROBE_SCHEMA = "d1_gcn_material_shader_reference_probe_merged/v1"
PROBE_STATUS = "D1_GCN_MATERIAL_SHADER_REFERENCE_PROBE_MERGED_EXACT"
SCHEMA = "d1_gcn_material_pipeline_owner_frontier/v1"
STATUS = "D1_GCN_MATERIAL_PIPELINE_OWNER_FRONTIER_EXACT_STRUCTURAL"
NULLS = {"00000000", "FFFFFFFF"}
ABSENT_RE = re.compile(r"^shader_header_absent:([0-9A-F]{8}):(VS|PS):([0-9A-F]{8})$")


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def shader_header_index(src: dict) -> dict[str, dict]:
    if src.get("schema") != SHADER_SCHEMA or src.get("status") != SHADER_STATUS:
        raise ValueError(f"shader corpus identity mismatch:{src.get('schema')}:{src.get('status')}")
    if src.get("violations"):
        raise ValueError(f"shader corpus has {len(src['violations'])} violations")
    out: dict[str, dict] = {}
    for p in src.get("unique_gcn_programs") or []:
        sha = str(p["gcn_sha256"]).lower()
        stages = list(p.get("stages") or [])
        if len(stages) != 1:
            raise ValueError(f"exact GCN program has non-single stage:{sha}:{stages}")
        stage = stages[0]
        refs = sorted(str(x).upper() for x in (p.get("native_program_references") or []))
        for h in p.get("headers") or []:
            tag = norm(h["header"])
            hs = h.get("stage")
            rec = {"header": tag, "stage": stage, "gcn_sha256": sha, "native_program_references": refs}
            if hs != stage:
                raise ValueError(f"header/program stage mismatch:{tag}:{hs}:{stage}")
            old = out.get(tag)
            if old is not None and old != rec:
                raise ValueError(f"shader header maps ambiguously:{tag}:{old}:{rec}")
            out[tag] = rec
    if len(out) != 37_892:
        raise ValueError(f"shader header denominator:{len(out)}!=37892")
    return out


def exact_local_shader(row: dict) -> bool:
    te = row.get("target_entry") or {}
    re = row.get("reference_target_entry") or {}
    orb = row.get("reference_target_orbshdr_shape") or {}
    bi = orb.get("binary_info") or {}
    return (
        te.get("type") == 32
        and te.get("subtype") == 11
        and re.get("type") == 1
        and re.get("subtype") == 11
        and orb.get("code_bounds_valid") is True
        and bi.get("stage") == "LocalShader"
        and bi.get("stage_value") == 3
        and bool(orb.get("code_sha256"))
    )


def resolve_slot(tag: str, headers: dict[str, dict], probes: dict[str, dict]) -> dict:
    h = norm(tag)
    if h in NULLS:
        return {"reference": h, "resolution": "NULL", "orb_stage": None}
    direct = headers.get(h)
    if direct is not None:
        return {
            "reference": h,
            "resolution": "EXACT_SHADER_CORPUS_HEADER",
            "orb_stage": direct["stage"],
            "gcn_sha256": direct["gcn_sha256"],
            "native_program_references": direct["native_program_references"],
        }
    probe = probes.get(h)
    if probe is None:
        return {"reference": h, "resolution": "UNRESOLVED_REFERENCE", "orb_stage": None}
    te = probe.get("target_entry") or {}
    base = {
        "reference": h,
        "entry_class": f"{te.get('type')}:{te.get('subtype')}",
        "target_payload_sha256": (probe.get("target_payload") or {}).get("sha256"),
        "orb_stage": None,
    }
    if exact_local_shader(probe):
        re = probe["reference_target_entry"]
        orb = probe["reference_target_orbshdr_shape"]
        bi = orb["binary_info"]
        return {
            **base,
            "resolution": "EXACT_LOCALSHADER_WRAPPER",
            "orb_stage": "LocalShader",
            "orb_stage_value": 3,
            "native_program_reference": norm(te["reference"]),
            "native_entry_class": f"{re['type']}:{re['subtype']}",
            "native_payload_sha256": probe["reference_target_payload"]["sha256"],
            "gcn_sha256": orb["code_sha256"],
            "code_length_bytes": orb["code_length_bytes"],
            "num_input_usage_slots": bi["num_input_usage_slots"],
        }
    return {
        **base,
        "resolution": "EXACT_OPAQUE_SPECIAL_REFERENCE",
        "file_entry_reference": te.get("reference"),
        "reference_resolution": (probe.get("reference_resolution") or {}).get("kind"),
        "structural_shape": probe.get("structural_shape"),
    }


def build(owner_path: Path, shader_path: Path, probe_path: Path) -> dict:
    owner = json.loads(owner_path.read_text())
    shader = json.loads(shader_path.read_text())
    probe = json.loads(probe_path.read_text())
    violations: list[str] = []

    if owner.get("schema") != OWNER_SCHEMA or owner.get("status") != OWNER_FAILED_STATUS:
        violations.append(f"owner_identity:{owner.get('schema')}:{owner.get('status')}")
    owner_cov = owner.get("coverage") or {}
    if owner_cov.get("current_material_entry_count") != 230_706:
        violations.append(f"owner_material_denominator:{owner_cov.get('current_material_entry_count')}!=230706")
    if len(owner.get("materials") or []) != 230_706:
        violations.append(f"owner_material_rows:{len(owner.get('materials') or [])}!=230706")
    if probe.get("schema") != PROBE_SCHEMA or probe.get("status") != PROBE_STATUS or probe.get("violations"):
        violations.append(f"probe_not_exact:{probe.get('schema')}:{probe.get('status')}:{len(probe.get('violations') or [])}")

    try:
        headers = shader_header_index(shader)
    except Exception as ex:
        raise SystemExit(f"shader prerequisite failed:{type(ex).__name__}:{ex}")
    probes = {norm(r["target"]): r for r in (probe.get("targets") or [])}
    if len(probes) != 196:
        violations.append(f"probe_target_denominator:{len(probes)}!=196")

    absent = collections.Counter()
    other_owner_violations = []
    for raw in owner.get("violations") or []:
        m = ABSENT_RE.match(str(raw))
        if m is None:
            other_owner_violations.append(str(raw))
            continue
        _, role, target = norm(m.group(1)), m.group(2), norm(m.group(3))
        absent[(target, role)] += 1
    if other_owner_violations:
        violations.append(f"owner_has_non_absent_violations:{len(other_owner_violations)}")
    expected_absent = collections.Counter()
    for target, row in probes.items():
        for role, count in (row.get("material_reference_roles") or {}).items():
            expected_absent[(target, role)] += int(count)
    if absent != expected_absent:
        violations.append("owner_absent_denominator_differs_from_exact_probe")
    if sum(absent.values()) != 3987:
        violations.append(f"owner_absent_occurrences:{sum(absent.values())}!=3987")

    slot28_counts = collections.Counter()
    slot2a8_counts = collections.Counter()
    pair_counts = collections.Counter()
    slot28_stage_counts = collections.Counter()
    slot2a8_stage_counts = collections.Counter()
    direct_pair_members: dict[tuple[str, str], list[str]] = collections.defaultdict(list)
    local_pair_members: dict[tuple[str, str], list[str]] = collections.defaultdict(list)
    local_gcn = set()
    rows = []

    for material in owner.get("materials") or []:
        tag = norm(material["material"])
        r28 = resolve_slot(material["vertex_shader_header"], headers, probes)
        r2a8 = resolve_slot(material["pixel_shader_header"], headers, probes)
        slot28_counts[r28["resolution"]] += 1
        slot2a8_counts[r2a8["resolution"]] += 1
        if r28.get("orb_stage"):
            slot28_stage_counts[r28["orb_stage"]] += 1
        if r2a8.get("orb_stage"):
            slot2a8_stage_counts[r2a8["orb_stage"]] += 1
        pair_counts[(r28["resolution"], r2a8["resolution"])] += 1

        if r28["resolution"] == "EXACT_SHADER_CORPUS_HEADER" and r28["orb_stage"] != "VS":
            violations.append(f"slot28_unexpected_corpus_stage:{tag}:{r28['reference']}:{r28['orb_stage']}")
        if r2a8["resolution"] == "EXACT_SHADER_CORPUS_HEADER" and r2a8["orb_stage"] != "PS":
            violations.append(f"slot2a8_unexpected_corpus_stage:{tag}:{r2a8['reference']}:{r2a8['orb_stage']}")
        if r28["resolution"] == "UNRESOLVED_REFERENCE":
            violations.append(f"slot28_unresolved:{tag}:{r28['reference']}")
        if r2a8["resolution"] == "UNRESOLVED_REFERENCE":
            violations.append(f"slot2a8_unresolved:{tag}:{r2a8['reference']}")

        if r28["resolution"] == "EXACT_LOCALSHADER_WRAPPER":
            local_gcn.add(r28["gcn_sha256"])
        if r28["resolution"] == "EXACT_SHADER_CORPUS_HEADER" and r2a8["resolution"] == "EXACT_SHADER_CORPUS_HEADER":
            direct_pair_members[(r28["reference"], r2a8["reference"])].append(tag)
        if r28["resolution"] == "EXACT_LOCALSHADER_WRAPPER" and r2a8["resolution"] == "EXACT_SHADER_CORPUS_HEADER":
            local_pair_members[(r28["reference"], r2a8["reference"])].append(tag)

        rows.append({
            "material": tag,
            "package_id": material.get("package_id"),
            "logical_view": material.get("logical_view"),
            "entry_index": material.get("entry_index"),
            "payload_sha256": material.get("payload_sha256"),
            "serialized_slot_0x28": r28,
            "serialized_slot_0x2a8": r2a8,
        })

    pair_counts_json = {f"{a}+{b}": n for (a, b), n in sorted(pair_counts.items())}
    special_materials = sum(
        1 for r in rows
        if r["serialized_slot_0x28"]["resolution"] == "EXACT_OPAQUE_SPECIAL_REFERENCE"
        or r["serialized_slot_0x2a8"]["resolution"] == "EXACT_OPAQUE_SPECIAL_REFERENCE"
    )
    coverage = {
        "material_count": len(rows),
        "shader_corpus_header_count": len(headers),
        "slot_0x28_resolution_counts": dict(sorted(slot28_counts.items())),
        "slot_0x2a8_resolution_counts": dict(sorted(slot2a8_counts.items())),
        "slot_0x28_orb_stage_counts": dict(sorted(slot28_stage_counts.items())),
        "slot_0x2a8_orb_stage_counts": dict(sorted(slot2a8_stage_counts.items())),
        "slot_resolution_pair_counts": pair_counts_json,
        "direct_vertex_plus_pixel_material_count": sum(len(v) for v in direct_pair_members.values()),
        "localshader_plus_pixel_material_count": sum(len(v) for v in local_pair_members.values()),
        "unique_direct_vertex_pixel_header_pair_count": len(direct_pair_members),
        "unique_localshader_pixel_header_pair_count": len(local_pair_members),
        "unique_localshader_wrapper_count": len({r["serialized_slot_0x28"]["reference"] for r in rows if r["serialized_slot_0x28"]["resolution"] == "EXACT_LOCALSHADER_WRAPPER"}),
        "unique_localshader_gcn_program_count": len(local_gcn),
        "materials_with_opaque_special_reference": special_materials,
        "opaque_special_reference_occurrence_count": slot28_counts["EXACT_OPAQUE_SPECIAL_REFERENCE"] + slot2a8_counts["EXACT_OPAQUE_SPECIAL_REFERENCE"],
        "param_index_to_attr_index_promotions": 0,
        "localshader_to_hullshader_promotions": 0,
        "domainshader_to_pixel_directness_promotions": 0,
        "shader_expression_semantic_promotions": 0,
    }

    expected = {
        "slot28": {"EXACT_LOCALSHADER_WRAPPER": 3967, "EXACT_OPAQUE_SPECIAL_REFERENCE": 8, "EXACT_SHADER_CORPUS_HEADER": 226731},
        "slot2a8": {"EXACT_OPAQUE_SPECIAL_REFERENCE": 12, "EXACT_SHADER_CORPUS_HEADER": 227981, "NULL": 2713},
        "stage28": {"LocalShader": 3967, "VS": 226731},
        "stage2a8": {"PS": 227981},
    }
    if coverage["slot_0x28_resolution_counts"] != expected["slot28"]:
        violations.append(f"slot28_accounting:{coverage['slot_0x28_resolution_counts']}")
    if coverage["slot_0x2a8_resolution_counts"] != expected["slot2a8"]:
        violations.append(f"slot2a8_accounting:{coverage['slot_0x2a8_resolution_counts']}")
    if coverage["slot_0x28_orb_stage_counts"] != expected["stage28"]:
        violations.append(f"slot28_stage_accounting:{coverage['slot_0x28_orb_stage_counts']}")
    if coverage["slot_0x2a8_orb_stage_counts"] != expected["stage2a8"]:
        violations.append(f"slot2a8_stage_accounting:{coverage['slot_0x2a8_orb_stage_counts']}")
    if coverage["unique_localshader_wrapper_count"] != 177:
        violations.append(f"local_wrapper_count:{coverage['unique_localshader_wrapper_count']}!=177")
    if coverage["unique_localshader_gcn_program_count"] != 65:
        violations.append(f"local_gcn_count:{coverage['unique_localshader_gcn_program_count']}!=65")
    if coverage["materials_with_opaque_special_reference"] != 13:
        violations.append(f"special_material_count:{coverage['materials_with_opaque_special_reference']}!=13")
    if coverage["opaque_special_reference_occurrence_count"] != 20:
        violations.append(f"special_occurrences:{coverage['opaque_special_reference_occurrence_count']}!=20")

    direct_pairs = [
        {"slot_0x28_header": a, "slot_0x2a8_header": b, "material_count": len(m), "materials": sorted(m)}
        for (a, b), m in sorted(direct_pair_members.items())
    ]
    local_pairs = [
        {"localshader_wrapper": a, "slot_0x2a8_header": b, "material_count": len(m), "materials": sorted(m)}
        for (a, b), m in sorted(local_pair_members.items())
    ]

    return {
        "schema": SCHEMA,
        "status": STATUS if not violations else "D1_GCN_MATERIAL_PIPELINE_OWNER_FRONTIER_WITH_VIOLATIONS",
        "coverage": coverage,
        "materials": rows,
        "direct_vertex_pixel_pairs": direct_pairs,
        "localshader_pixel_pairs": local_pairs,
        "violations": violations,
        "semantic_boundary": {
            "material_offset_0x28": "EXACT_SERIALIZED_PRE_RASTER_REFERENCE",
            "material_offset_0x2a8": "EXACT_SERIALIZED_PIXEL_PIPELINE_REFERENCE",
            "orbshdr_stage_identity": "AUTHORITATIVE_WHEN_SOURCE_CLOSED",
            "type32_subtype11_localshader": "GLOBAL_EXACT_FOR_MATERIAL_REFERENCED_POPULATION",
            "localshader_as_vertexshader": "FORBIDDEN",
            "opaque_special_reference_stage": "WITHHELD",
            "local_hull_domain_pipeline_ownership": "NEXT_TESSELLATION_GATE",
            "direct_vs_to_ps_owner_relation": "EXACT_MATERIAL_SCOPED_RELATION_NOT_YET_RASTER_DIRECTNESS",
            "param_index_to_attr_index_provenance": "WITHHELD_UNTIL_RASTER_STAGE_DIRECTNESS",
            "varying_semantic_names": "WITHHELD",
            "shader_expression_semantics": "WITHHELD"
        },
        "policy": (
            "The +0x28/+0x2A8 material fields are preserved as serialized pipeline references, not stage names. "
            "Exact OrbShdr stage is promoted only from the frozen shader corpus or from the exact merged 32:11 "
            "LocalShader wrapper proof. Remaining fallback/special references remain opaque. No LocalShader is "
            "relabelled as VertexShader and no PARAM->ATTR edge is promoted here."
        )
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--owner", type=Path, required=True)
    ap.add_argument("--shader-corpus", type=Path, required=True)
    ap.add_argument("--reference-probe", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()
    out = build(a.owner, a.shader_corpus, a.reference_probe)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": out["status"], "coverage": out["coverage"], "violations": out["violations"][:50]}, indent=2, sort_keys=True))
    return 0 if not out["violations"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
