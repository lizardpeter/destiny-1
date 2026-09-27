#!/usr/bin/env python3
"""Rank D1 executable functions for renderer-orchestration reverse engineering.

Inputs:
  * normalized Ghidra graph from d1_ghidra_graph_normalize.py
  * renderer-string frontier from d1_executable_renderer_strings.py

This tool is deliberately conservative. It produces a prioritized function
frontier, not semantic promotions. Evidence is retained per domain and call-graph
neighborhood so later decompilation can prove draw/material/light behavior.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict, deque
from pathlib import Path
from typing import Any


EXTERNAL_PATTERNS = (
    re.compile(r"gnm|gnmx", re.I),
    re.compile(r"videoout|graphics|gpu", re.I),
    re.compile(r"shader|texture|sampler|resource", re.I),
    re.compile(r"draw|dispatch|submit|command|queue|fence|wait", re.I),
)

DOMAIN_WEIGHTS = {
    "frame_graph": 9,
    "shader_material": 10,
    "fixed_function": 10,
    "draw_submit": 10,
    "lighting": 12,
    "environment": 7,
    "post": 7,
}
EXTERNAL_CALL_WEIGHT = 10
D1_HASH_LITERAL_WEIGHT = 2
GRAPHICS_HEARTBEAT_PROXIMITY_WEIGHT = 2


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def load_graph(graph_dir: Path) -> tuple[dict, dict[str, dict], list[dict]]:
    manifest = json.loads((graph_dir / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema") != "d1_normalized_code_graph/v1":
        raise ValueError(f"unsupported graph schema {manifest.get('schema')!r}")
    nodes = {row["id"]: row for row in load_jsonl(graph_dir / "nodes.jsonl")}
    edges = load_jsonl(graph_dir / "edges.jsonl")
    return manifest, nodes, edges


def load_renderer_strings(path: Path) -> dict[str, set[str]]:
    doc = json.loads(path.read_text(encoding="utf-8"))
    if doc.get("schema") != "d1_executable_renderer_strings/v1":
        raise ValueError(f"unsupported renderer string schema {doc.get('schema')!r}")
    return {
        row["text"]: set(row.get("categories") or [])
        for row in doc.get("strings", [])
        if row.get("candidate_lea_xref_count", 0) > 0
    }


def external_is_renderer_related(node: dict) -> bool:
    attrs = node.get("attrs") or {}
    text = " ".join(
        str(attrs.get(key) or "")
        for key in ("name", "original_imported_name", "library", "prototype")
    )
    return any(pattern.search(text) for pattern in EXTERNAL_PATTERNS)


def analyze(
    graph_dir: Path,
    renderer_strings_path: Path,
    *,
    radius: int = 2,
    top: int = 200,
    heartbeat_offset: int = 0xFAAF4,
) -> dict:
    manifest, nodes, edges = load_graph(graph_dir)
    renderer_strings = load_renderer_strings(renderer_strings_path)

    functions = {
        node_id: row
        for node_id, row in nodes.items()
        if row.get("kind") == "function"
    }
    strings = {
        node_id: row
        for node_id, row in nodes.items()
        if row.get("kind") == "defined_string"
    }
    externals = {
        node_id: row
        for node_id, row in nodes.items()
        if row.get("kind") == "external_function"
    }

    calls_out: dict[str, set[str]] = defaultdict(set)
    calls_in: dict[str, set[str]] = defaultdict(set)
    evidence: dict[str, list[dict[str, Any]]] = defaultdict(list)
    direct_score: dict[str, int] = defaultdict(int)
    domains: dict[str, set[str]] = defaultdict(set)

    for edge in edges:
        subject = edge.get("subject")
        obj = edge.get("object")
        pred = edge.get("predicate")
        if pred == "CALLS" and subject in functions:
            calls_out[subject].add(obj)
            if obj in functions:
                calls_in[obj].add(subject)
            elif obj in externals and external_is_renderer_related(externals[obj]):
                attrs = externals[obj].get("attrs") or {}
                direct_score[subject] += EXTERNAL_CALL_WEIGHT
                evidence[subject].append({
                    "kind": "renderer_external_call",
                    "target": obj,
                    "name": attrs.get("name"),
                    "library": attrs.get("library"),
                    "weight": EXTERNAL_CALL_WEIGHT,
                })
                domains[subject].add("external_gpu_api")
        elif pred == "REFERENCES_STRING" and subject in functions and obj in strings:
            text = str((strings[obj].get("attrs") or {}).get("text") or "")
            categories = renderer_strings.get(text)
            if not categories:
                continue
            weight = sum(DOMAIN_WEIGHTS.get(category, 0) for category in categories)
            direct_score[subject] += weight
            evidence[subject].append({
                "kind": "renderer_string_xref",
                "string_id": obj,
                "text": text,
                "categories": sorted(categories),
                "weight": weight,
                "xref": edge.get("attrs") or {},
            })
            domains[subject].update(categories)
        elif pred == "REFERENCES_D1_HASH_LITERAL" and subject in functions:
            direct_score[subject] += D1_HASH_LITERAL_WEIGHT
            evidence[subject].append({
                "kind": "d1_hash_literal",
                "target": obj,
                "weight": D1_HASH_LITERAL_WEIGHT,
                "xref": edge.get("attrs") or {},
            })

    # The Graphics Heartbeat offset is a relocation-stable runtime neighborhood,
    # not a renderer function identity. Give only a tiny ranking nudge when a
    # recovered function body actually contains the offset.
    for fn_id, row in functions.items():
        attrs = row.get("attrs") or {}
        for body_range in attrs.get("body_ranges") or []:
            lo = body_range.get("min_image_offset")
            hi = body_range.get("max_image_offset")
            if isinstance(lo, int) and isinstance(hi, int) and lo <= heartbeat_offset <= hi:
                direct_score[fn_id] += GRAPHICS_HEARTBEAT_PROXIMITY_WEIGHT
                evidence[fn_id].append({
                    "kind": "graphics_heartbeat_neighborhood",
                    "image_offset": heartbeat_offset,
                    "weight": GRAPHICS_HEARTBEAT_PROXIMITY_WEIGHT,
                    "status": "RUNTIME_NEIGHBORHOOD_ONLY",
                })
                domains[fn_id].add("graphics_runtime_anchor")
                break

    seed_functions = {fn for fn, score in direct_score.items() if score > 0}
    propagated: dict[str, float] = defaultdict(float)
    nearest_seed: dict[str, set[str]] = defaultdict(set)

    for seed in seed_functions:
        queue = deque([(seed, 0)])
        seen = {seed}
        while queue:
            current, distance = queue.popleft()
            if distance >= radius:
                continue
            neighbors = {
                node for node in calls_out.get(current, set()) if node in functions
            } | calls_in.get(current, set())
            for neighbor in neighbors:
                if neighbor in seen:
                    continue
                seen.add(neighbor)
                next_distance = distance + 1
                propagated[neighbor] += direct_score[seed] / (2 ** next_distance)
                nearest_seed[neighbor].add(seed)
                queue.append((neighbor, next_distance))

    candidates = []
    for fn_id, row in functions.items():
        score = float(direct_score.get(fn_id, 0)) + propagated.get(fn_id, 0.0)
        if score <= 0:
            continue
        attrs = row.get("attrs") or {}
        candidates.append({
            "function_id": fn_id,
            "entry": attrs.get("entry"),
            "image_offset": attrs.get("image_offset"),
            "name": attrs.get("name"),
            "prototype": attrs.get("prototype"),
            "instruction_count": attrs.get("instruction_count"),
            "direct_score": direct_score.get(fn_id, 0),
            "neighbor_score": round(propagated.get(fn_id, 0.0), 3),
            "score": round(score, 3),
            "domains": sorted(domains.get(fn_id, set())),
            "evidence": evidence.get(fn_id, []),
            "caller_count": len(calls_in.get(fn_id, set())),
            "callee_count": len([x for x in calls_out.get(fn_id, set()) if x in functions]),
            "renderer_external_call_count": len([
                x for x in calls_out.get(fn_id, set()) if x in externals and external_is_renderer_related(externals[x])
            ]),
            "neighbor_seed_functions": sorted(nearest_seed.get(fn_id, set())),
        })

    candidates.sort(
        key=lambda row: (
            -row["score"],
            -len(row["domains"]),
            row["image_offset"] if isinstance(row["image_offset"], int) else 2**63,
            row["function_id"],
        )
    )
    candidates = candidates[:top]

    domain_counts = defaultdict(int)
    for row in candidates:
        for domain in row["domains"]:
            domain_counts[domain] += 1

    return {
        "schema": "d1_executable_renderer_frontier/v1",
        "executable_sha256": manifest.get("executable_sha256"),
        "title_id": manifest.get("title_id"),
        "app_version": manifest.get("app_version"),
        "inputs": {
            "graph_dir": str(graph_dir),
            "renderer_strings": str(renderer_strings_path),
        },
        "policy": (
            "Scores prioritize decompilation only. String text, external-call names, "
            "D1-range immediates and call-graph proximity do not by themselves prove "
            "renderer semantics or asset ownership."
        ),
        "weights": {
            "domains": DOMAIN_WEIGHTS,
            "renderer_external_call": EXTERNAL_CALL_WEIGHT,
            "d1_hash_literal": D1_HASH_LITERAL_WEIGHT,
            "graphics_heartbeat_neighborhood": GRAPHICS_HEARTBEAT_PROXIMITY_WEIGHT,
            "neighbor_decay": "direct_seed_score / 2^call_distance",
        },
        "counts": {
            "function_count": len(functions),
            "direct_seed_function_count": len(seed_functions),
            "ranked_candidate_count": len(candidates),
            "domain_counts_in_ranked_candidates": dict(sorted(domain_counts.items())),
        },
        "candidates": candidates,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("graph_dir", type=Path)
    parser.add_argument("--renderer-strings", type=Path, required=True)
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument("--radius", type=int, default=2)
    parser.add_argument("--top", type=int, default=200)
    parser.add_argument("--graphics-heartbeat-offset", type=lambda x: int(x, 0), default=0xFAAF4)
    args = parser.parse_args()

    report = analyze(
        args.graph_dir,
        args.renderer_strings,
        radius=max(0, args.radius),
        top=max(1, args.top),
        heartbeat_offset=args.graphics_heartbeat_offset,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "D1_EXECUTABLE_RENDERER_FRONTIER",
        **report["counts"],
        "output": str(args.output),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
