#!/usr/bin/env python3
"""Census articulated D1 character/combatant graph clusters in a package family.

This is a discovery tool, not an ownership guesser. It combines only structures
already byte-validated elsewhere in this repository:

* standard EntityResource model parents and their embedded s_entity_model hash;
* D1 skeleton EntityResources and decoded bone counts;
* observed runtime-rig class pair 808008B2 -> 8080099B;
* observed composition class pair 8080079A -> 80800610;
* s_animation_clip, 0x8080222A animation-bundle wrappers, and 0x80802C0E
  post/action controls;
* exact 4-byte-aligned FileHash/TagHash values that resolve to entries in the
  same logical package family.

Connected components containing model + skeleton + runtime-rig + animation-side
evidence are promoted only to *character/combatant candidates*. Package naming
or adjacency alone never promotes a cluster, and this tool does not claim a
specific gameplay archetype or animation semantic.
"""
from __future__ import annotations

import argparse
import collections
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_entry_extract import EntryReader
from d1_entity_model_probe import D1_ENTITY_MODEL_CLASS
from d1_entity_resource_probe import ENTITY_RESOURCE_CLASS, parse_resource
from d1_skeleton_probe import parse_skeleton_resource

ANIMATION_CLIP_CLASS = "808005A1"
ANIMATION_WRAPPER_CLASS = "8080222A"
POST_ANIMATION_CONTROL_CLASS = "80802C0E"
CONTEXT_TABLE_CLASS = "80800368"
RUNTIME_RIG_DISCRIMINATOR = "808008B2"
RUNTIME_RIG_INFO = "8080099B"
COMPOSITION_DISCRIMINATOR = "8080079A"
COMPOSITION_INFO = "80800610"
# Observed in the proven 0767 Vex combatant cluster. Keep the name scoped to
# that observation rather than asserting a universal Bungie semantic name.
OBSERVED_0767_COMBATANT_DISCRIMINATOR = "80802465"
OBSERVED_0767_COMBATANT_INFO = "80802955"


def aligned_local_refs(payload: bytes, local_hashes: set[int]) -> dict[str, list[int]]:
    """Return aligned dword references that exactly resolve inside this family."""
    out: dict[str, list[int]] = collections.defaultdict(list)
    end = len(payload) - (len(payload) % 4)
    for off in range(0, end, 4):
        value = struct.unpack_from("<I", payload, off)[0]
        if value in local_hashes:
            out[f"{value:08X}"].append(off)
    return dict(out)


def classify_component(facts: dict) -> dict:
    model_count = len(facts.get("model_parents", []))
    skeleton_count = len(facts.get("skeletons", []))
    runtime_rig_count = len(facts.get("runtime_rigs", []))
    clip_count = len(facts.get("animation_clips", []))
    wrapper_count = len(facts.get("animation_wrappers", []))
    control_count = len(facts.get("post_animation_controls", []))
    composition_count = len(facts.get("compositions", []))
    observed_combatant_count = len(facts.get("observed_0767_combatant_components", []))

    has_model = model_count > 0
    has_skeleton = skeleton_count > 0
    has_rig = runtime_rig_count > 0
    has_animation_side = clip_count > 0 or wrapper_count > 0 or control_count > 0

    if has_model and has_skeleton and has_rig and has_animation_side:
        classification = "animated_articulated_entity_candidate"
    elif has_model and has_skeleton and has_rig:
        classification = "rigged_articulated_entity_candidate"
    elif has_model and has_skeleton:
        classification = "model_skeleton_cluster"
    elif has_model and has_animation_side:
        classification = "model_animation_cluster_unresolved"
    else:
        classification = "unresolved_component"

    score = 0
    score += 30 if has_model else 0
    score += 25 if has_skeleton else 0
    score += 25 if has_rig else 0
    score += 20 if has_animation_side else 0
    score += 5 if composition_count else 0
    score += 5 if observed_combatant_count else 0

    return {
        "classification": classification,
        "candidate": classification in {
            "animated_articulated_entity_candidate",
            "rigged_articulated_entity_candidate",
        },
        "character_or_combatant_semantic_proven": False,
        "score": score,
        "evidence_counts": {
            "model_parents": model_count,
            "skeletons": skeleton_count,
            "runtime_rigs": runtime_rig_count,
            "animation_clips": clip_count,
            "animation_wrappers": wrapper_count,
            "post_animation_controls": control_count,
            "compositions": composition_count,
            "observed_0767_combatant_components": observed_combatant_count,
        },
    }


def connected_components(nodes: set[str], graph: dict[str, set[str]]) -> list[list[str]]:
    components = []
    unseen = set(nodes)
    while unseen:
        start = min(unseen)
        stack = [start]
        unseen.remove(start)
        comp = []
        while stack:
            cur = stack.pop()
            comp.append(cur)
            for nxt in sorted(graph.get(cur, ())):
                if nxt in unseen:
                    unseen.remove(nxt)
                    stack.append(nxt)
        components.append(sorted(comp))
    return components


def analyze_family(pkg: Path, runtime: Path, *, include_all_components: bool = False) -> dict:
    r = EntryReader(pkg, runtime)
    entries = {e["tag_hash"].upper(): e for e in r.entries}
    local_ints = {int(h, 16) for h in entries}

    roles: dict[str, dict] = {}
    structured_payloads: dict[str, bytes] = {}
    errors = []

    for h, e in entries.items():
        role = {
            "tag_hash": h,
            "entry_index": e["index"],
            "reference": e["reference"].upper(),
            "type": e["type"],
            "subtype": e["subtype"],
            "size": e["file_size"],
            "available": r.available(e["index"]),
        }
        ref = role["reference"]
        if ref == D1_ENTITY_MODEL_CLASS:
            role["kind"] = "s_entity_model"
        elif ref == ANIMATION_CLIP_CLASS:
            role["kind"] = "s_animation_clip"
        elif ref == ANIMATION_WRAPPER_CLASS:
            role["kind"] = "animation_wrapper"
        elif ref == POST_ANIMATION_CONTROL_CLASS:
            role["kind"] = "post_animation_control"
        elif ref == CONTEXT_TABLE_CLASS:
            role["kind"] = "context_table"

        if e["type"] == 16 and e["subtype"] == 0 and role["available"]:
            try:
                b = r.entry(e["index"])
                structured_payloads[h] = b
            except Exception as ex:
                errors.append({"tag_hash": h, "phase": "read", "error": repr(ex)})
                roles[h] = role
                continue

            if ref == ENTITY_RESOURCE_CLASS:
                try:
                    parsed = parse_resource(b, r.h["platform"])
                    role["entity_resource"] = {
                        "semantic_role": parsed.get("semantic_role"),
                        "unk10_class": parsed.get("unk10", {}).get("class_hash"),
                        "unk18_class": parsed.get("unk18", {}).get("class_hash"),
                        "embedded_model_tag_hash": parsed.get("embedded_model_tag_hash"),
                    }
                    sem = parsed.get("semantic_role")
                    u10 = parsed.get("unk10", {}).get("class_hash")
                    u18 = parsed.get("unk18", {}).get("class_hash")
                    if sem == "entity_model" and parsed.get("embedded_model_tag_hash"):
                        role["kind"] = "model_parent"
                        role["embedded_model_tag_hash"] = parsed["embedded_model_tag_hash"].upper()
                    elif sem == "entity_skeleton":
                        role["kind"] = "skeleton"
                        try:
                            sk = parse_skeleton_resource(b)
                            info = sk["skeleton_info"]
                            role["bone_count"] = info["node_hierarchy"]["count"]
                            role["bone_hashes"] = [x["node_hash"] for x in info.get("bones", [])]
                        except Exception as ex:
                            errors.append({"tag_hash": h, "phase": "parse_skeleton", "error": repr(ex)})
                    elif u10 == RUNTIME_RIG_DISCRIMINATOR and u18 == RUNTIME_RIG_INFO:
                        role["kind"] = "runtime_rig"
                    elif u10 == COMPOSITION_DISCRIMINATOR and u18 == COMPOSITION_INFO:
                        role["kind"] = "composition"
                    elif (
                        u10 == OBSERVED_0767_COMBATANT_DISCRIMINATOR
                        and u18 == OBSERVED_0767_COMBATANT_INFO
                    ):
                        role["kind"] = "observed_0767_combatant_component"
                    else:
                        role.setdefault("kind", "entity_resource_other")
                except Exception as ex:
                    errors.append({"tag_hash": h, "phase": "parse_entity_resource", "error": repr(ex)})

        roles[h] = role

    graph: dict[str, set[str]] = collections.defaultdict(set)
    edges = []

    def add_edge(src: str, dst: str, kind: str, offsets: list[int] | None = None):
        if src == dst or dst not in entries:
            return
        graph[src].add(dst)
        graph[dst].add(src)
        edge = {"source": src, "target": dst, "kind": kind}
        if offsets is not None:
            edge["offsets"] = offsets
        edges.append(edge)

    for h, role in roles.items():
        model_hash = role.get("embedded_model_tag_hash")
        if model_hash:
            add_edge(h, model_hash, "standard_model_parent_embedded_model")

    for src, b in structured_payloads.items():
        for dst, offsets in aligned_local_refs(b, local_ints).items():
            add_edge(src, dst, "aligned_exact_local_taghash", offsets)

    interesting_nodes = {
        h
        for h, row in roles.items()
        if row.get("kind") in {
            "model_parent",
            "s_entity_model",
            "skeleton",
            "runtime_rig",
            "composition",
            "observed_0767_combatant_component",
            "s_animation_clip",
            "animation_wrapper",
            "post_animation_control",
            "context_table",
        }
    }
    # Keep bridge nodes that connect interesting structures, but discard wholly
    # unrelated package islands from the expensive component report.
    expanded = set(interesting_nodes)
    for h in list(interesting_nodes):
        expanded.update(graph.get(h, ()))

    components = []
    for comp in connected_components(expanded, graph):
        comp_set = set(comp)
        facts = {
            "model_parents": sorted(h for h in comp if roles[h].get("kind") == "model_parent"),
            "models": sorted(h for h in comp if roles[h].get("kind") == "s_entity_model"),
            "skeletons": sorted(h for h in comp if roles[h].get("kind") == "skeleton"),
            "runtime_rigs": sorted(h for h in comp if roles[h].get("kind") == "runtime_rig"),
            "compositions": sorted(h for h in comp if roles[h].get("kind") == "composition"),
            "observed_0767_combatant_components": sorted(
                h for h in comp if roles[h].get("kind") == "observed_0767_combatant_component"
            ),
            "animation_clips": sorted(h for h in comp if roles[h].get("kind") == "s_animation_clip"),
            "animation_wrappers": sorted(h for h in comp if roles[h].get("kind") == "animation_wrapper"),
            "post_animation_controls": sorted(
                h for h in comp if roles[h].get("kind") == "post_animation_control"
            ),
            "context_tables": sorted(h for h in comp if roles[h].get("kind") == "context_table"),
        }
        cls = classify_component(facts)
        if not include_all_components and cls["classification"] == "unresolved_component":
            continue
        components.append({
            "nodes": comp,
            "facts": facts,
            "classification": cls,
            "bone_counts": sorted(
                {roles[h].get("bone_count") for h in facts["skeletons"] if roles[h].get("bone_count") is not None}
            ),
            "edge_count": sum(1 for e in edges if e["source"] in comp_set and e["target"] in comp_set),
        })

    components.sort(
        key=lambda x: (
            -x["classification"]["score"],
            -len(x["nodes"]),
            x["nodes"][0] if x["nodes"] else "",
        )
    )
    candidates = [x for x in components if x["classification"]["candidate"]]

    kind_counts = collections.Counter(row.get("kind", "unclassified") for row in roles.values())
    return {
        "schema": "d1_character_family_census/v1",
        "package": str(r.pkg),
        "platform": r.h["platform"],
        "package_id": r.h["pkg_id"],
        "package_patch_id": r.h["patch_id"],
        "entry_count": len(r.entries),
        "kind_counts": dict(kind_counts),
        "candidate_count": len(candidates),
        "candidates": candidates,
        "components": components,
        "roles": roles,
        "edges": edges,
        "errors": errors,
        "policy": (
            "Character/combatant labels are candidates only. Promotion requires an exact graph component containing "
            "a standard model parent, decoded skeleton, observed runtime-rig class pair, and animation-side evidence. "
            "Package filename, entry adjacency, and matching counts are not ownership evidence."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pkg", type=Path, nargs="+")
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--include-all-components", action="store_true")
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args()

    reports = [
        analyze_family(p, args.runtime, include_all_components=args.include_all_components)
        for p in args.pkg
    ]
    out = {
        "schema": "d1_character_family_census_set/v1",
        "family_count": len(reports),
        "candidate_count": sum(x["candidate_count"] for x in reports),
        "families": reports,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "family_count": out["family_count"],
        "candidate_count": out["candidate_count"],
        "packages": [
            {"package": x["package"], "candidate_count": x["candidate_count"], "kind_counts": x["kind_counts"]}
            for x in reports
        ],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
