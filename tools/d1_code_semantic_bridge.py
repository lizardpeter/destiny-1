#!/usr/bin/env python3
"""Promote selected executable-function semantic bridges into D1 knowledge records.

The bulk code graph remains JSONL/graph-database data. This tool promotes only
meaningful reviewed function->resource/semantic relationships into the durable,
Git-friendly d1_knowledge_record/v1 layer.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

STATUSES = {
    "PROVEN",
    "STRONGLY_SUPPORTED",
    "CANDIDATE",
    "UNRESOLVED",
    "REJECTED",
    "TARGET",
}

BRIDGE_PREDICATES = {
    "PARSES_TIGER_STRUCTURE",
    "RESOLVES_TAG_HASH",
    "CONSUMES_RESOURCE_CLASS",
    "DECODES_TEXTURE",
    "DECODES_ANIMATION",
    "SELECTS_MATERIAL",
    "BINDS_SHADER_RESOURCE",
    "EVALUATES_SHADER_PROGRAM",
    "LOADS_WORLD_GRAPH",
    "OWNS_RUNTIME_BEHAVIOR_FOR",
    "IMPLEMENTS_SEMANTIC_ASSET_BEHAVIOR",
    "INVOKES_DECOMPRESSION",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    doc = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict):
        raise ValueError(f"{path}: expected JSON object")
    return doc


def read_nodes(path: Path) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{line_no}: expected object")
        node_id = row.get("id")
        if not isinstance(node_id, str) or not node_id:
            raise ValueError(f"{path}:{line_no}: missing node id")
        if node_id in out:
            raise ValueError(f"{path}:{line_no}: duplicate node id {node_id}")
        out[node_id] = row
    return out


def function_knowledge_node(node: dict[str, Any]) -> dict[str, Any]:
    if node.get("kind") != "function":
        raise ValueError(f"bridge source {node.get('id')!r} is not a function node")
    attrs = node.get("attrs")
    if not isinstance(attrs, dict):
        raise ValueError(f"function node {node.get('id')!r} has no attrs")

    keep = {
        "executable_sha256",
        "entry",
        "image_offset",
        "body_ranges",
        "instruction_count",
        "instruction_byte_count",
        "instruction_bytes_sha256",
        "mnemonic_sequence_sha256",
        "name",
        "namespace",
        "source",
        "calling_convention",
        "prototype",
        "is_thunk",
        "is_external",
        "title_id",
        "app_version",
    }
    promoted = {key: attrs.get(key) for key in sorted(keep) if key in attrs}
    return {
        "id": node["id"],
        "kind": "function",
        "status": "PROVEN",
        "label": attrs.get("name") or node["id"],
        "attrs": promoted,
    }


def build_record(
    graph_dir: Path,
    bridge_spec_path: Path,
    bridge_spec: dict[str, Any],
) -> dict[str, Any]:
    if bridge_spec.get("schema") != "d1_code_semantic_bridge/v1":
        raise ValueError("bridge spec schema must be d1_code_semantic_bridge/v1")

    manifest_path = graph_dir / "manifest.json"
    nodes_path = graph_dir / "nodes.jsonl"
    manifest = read_json(manifest_path)
    if manifest.get("schema") != "d1_normalized_code_graph/v1":
        raise ValueError("normalized graph manifest schema mismatch")
    nodes = read_nodes(nodes_path)

    record_id = bridge_spec.get("record_id")
    title = bridge_spec.get("title")
    updated_utc = bridge_spec.get("updated_utc")
    if not all(isinstance(value, str) and value for value in (record_id, title, updated_utc)):
        raise ValueError("bridge spec requires non-empty record_id, title and updated_utc")

    bridge_rows = bridge_spec.get("bridges")
    if not isinstance(bridge_rows, list) or not bridge_rows:
        raise ValueError("bridge spec requires a non-empty bridges array")

    local_nodes: dict[str, dict[str, Any]] = {}
    external_nodes: dict[tuple[str, str | None], dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []
    assertions: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = [
        {
            "id": "source:code_graph_manifest",
            "kind": "normalized_code_graph",
            "locator": str(manifest_path),
            "sha256": sha256_file(manifest_path),
            "details": {
                "executable_sha256": manifest.get("executable_sha256"),
                "title_id": manifest.get("title_id"),
                "app_version": manifest.get("app_version"),
            },
        },
        {
            "id": "source:code_graph_nodes",
            "kind": "normalized_code_graph_nodes",
            "locator": str(nodes_path),
            "sha256": sha256_file(nodes_path),
            "details": {},
        },
        {
            "id": "source:bridge_spec",
            "kind": "reviewed_semantic_bridge_spec",
            "locator": str(bridge_spec_path),
            "sha256": sha256_file(bridge_spec_path),
            "details": {},
        },
    ]

    extra_sources = bridge_spec.get("sources", [])
    if not isinstance(extra_sources, list):
        raise ValueError("bridge spec sources must be an array")
    used_source_ids = {row["id"] for row in sources}
    for row in extra_sources:
        if not isinstance(row, dict):
            raise ValueError("bridge spec source rows must be objects")
        source_id = row.get("id")
        if not isinstance(source_id, str) or not source_id:
            raise ValueError("bridge spec sources require non-empty id")
        if source_id in used_source_ids:
            raise ValueError(f"duplicate source id {source_id}")
        used_source_ids.add(source_id)
        sources.append(row)

    for index, bridge in enumerate(bridge_rows):
        if not isinstance(bridge, dict):
            raise ValueError(f"bridges[{index}] must be an object")

        function_id = bridge.get("function_id")
        target_id = bridge.get("target_node_id")
        target_record_id = bridge.get("target_record_id")
        predicate = bridge.get("predicate")
        status = bridge.get("status")
        claim = bridge.get("claim")
        source_ids = bridge.get("source_ids", ["source:code_graph_nodes", "source:bridge_spec"])

        if function_id not in nodes:
            raise ValueError(f"bridges[{index}]: unknown function_id {function_id!r}")
        if not isinstance(target_id, str) or not target_id:
            raise ValueError(f"bridges[{index}]: target_node_id must be non-empty")
        if target_record_id is not None and (
            not isinstance(target_record_id, str) or not target_record_id
        ):
            raise ValueError(f"bridges[{index}]: target_record_id must be non-empty or null")
        if predicate not in BRIDGE_PREDICATES:
            raise ValueError(f"bridges[{index}]: unsupported bridge predicate {predicate!r}")
        if status not in STATUSES:
            raise ValueError(f"bridges[{index}]: invalid status {status!r}")
        if not isinstance(claim, str) or not claim:
            raise ValueError(f"bridges[{index}]: claim must be non-empty")
        if not isinstance(source_ids, list) or not source_ids:
            raise ValueError(f"bridges[{index}]: source_ids must be non-empty array")
        unknown_sources = [source_id for source_id in source_ids if source_id not in used_source_ids]
        if unknown_sources:
            raise ValueError(f"bridges[{index}]: unknown source_ids {unknown_sources}")

        fn_node = function_knowledge_node(nodes[function_id])
        previous = local_nodes.get(function_id)
        if previous is not None and previous["attrs"] != fn_node["attrs"]:
            raise ValueError(f"function {function_id} promoted with conflicting attrs")
        local_nodes[function_id] = fn_node

        ext_key = (target_id, target_record_id)
        external_nodes[ext_key] = {
            "id": target_id,
            "record_id": target_record_id,
            "note": bridge.get("target_note"),
        }

        assertion_id = f"assert:bridge:{index:04d}"
        edge_id = f"edge:bridge:{index:04d}"
        assertions.append(
            {
                "id": assertion_id,
                "status": status,
                "claim": claim,
                "source_ids": source_ids,
                "details": {
                    "function_id": function_id,
                    "target_node_id": target_id,
                    "predicate": predicate,
                    "evidence": bridge.get("evidence", {}),
                },
            }
        )
        edges.append(
            {
                "id": edge_id,
                "subject": function_id,
                "predicate": predicate,
                "object": target_id,
                "status": status,
                "assertion_ids": [assertion_id],
                "attrs": bridge.get("edge_attrs", {}),
            }
        )

    return {
        "schema": "d1_knowledge_record/v1",
        "record_id": record_id,
        "title": title,
        "updated_utc": updated_utc,
        "scope": {
            "game": "Destiny 1",
            "platform": "PS4",
            "title_id": manifest.get("title_id"),
            "app_version": manifest.get("app_version"),
            "executable_sha256": manifest.get("executable_sha256"),
            "kind": "code_semantic_bridge",
        },
        "nodes": sorted(local_nodes.values(), key=lambda row: row["id"]),
        "external_nodes": sorted(
            external_nodes.values(),
            key=lambda row: (row["id"], row.get("record_id") or ""),
        ),
        "edges": edges,
        "assertions": assertions,
        "sources": sources,
        "rejections": [],
        "frontiers": bridge_spec.get("frontiers", []),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("graph_dir", type=Path)
    parser.add_argument("bridge_spec", type=Path)
    parser.add_argument("-o", "--out", type=Path, required=True)
    args = parser.parse_args()

    spec = read_json(args.bridge_spec)
    record = build_record(args.graph_dir, args.bridge_spec, spec)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
