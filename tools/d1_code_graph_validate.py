#!/usr/bin/env python3
"""Validate normalized Destiny 1 executable code-graph JSONL.

This validator is intentionally dependency-free and fail-closed. It validates
identity namespace, node/edge integrity, graph counts and the executable-bound
function/string/import invariants before graph-database ingestion.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

SCHEMA = "d1_normalized_code_graph/v1"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

NODE_REQUIRED = {
    "executable_build": {
        "sha256",
        "title_id",
        "app_version",
        "image_base",
        "language_id",
        "compiler_spec",
        "executable_format",
    },
    "function": {
        "executable_sha256",
        "entry",
        "image_offset",
        "body_ranges",
        "instruction_count",
        "instruction_byte_count",
        "instruction_bytes_sha256",
        "mnemonic_sequence_sha256",
        "name",
        "source",
    },
    "external_library": {"executable_sha256", "name"},
    "external_function": {"executable_sha256", "name", "library"},
    "defined_string": {
        "executable_sha256",
        "address",
        "image_offset",
        "text",
        "data_type",
    },
    "d1_hash_literal": {
        "executable_sha256",
        "value_u32",
        "value_hex",
    },
}

EDGE_KINDS = {
    "HAS_FUNCTION": ({"executable_build"}, {"function"}),
    "IMPORTS_LIBRARY": ({"executable_build"}, {"external_library"}),
    "IMPORTS_FUNCTION": ({"executable_build"}, {"external_function"}),
    "BELONGS_TO_LIBRARY": ({"external_function"}, {"external_library"}),
    "CALLS": ({"function"}, {"function", "external_function"}),
    "HAS_DEFINED_STRING": ({"executable_build"}, {"defined_string"}),
    "REFERENCES_STRING": ({"function"}, {"defined_string"}),
    "HAS_D1_HASH_LITERAL": ({"executable_build"}, {"d1_hash_literal"}),
    "REFERENCES_D1_HASH_LITERAL": ({"function"}, {"d1_hash_literal"}),
}


def read_json(path: Path) -> dict[str, Any]:
    doc = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict):
        raise ValueError(f"{path}: expected JSON object")
    return doc


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except Exception as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_no}: expected JSON object")
            out.append(row)
    return out


def require(attrs: dict[str, Any], keys: set[str], where: str, errors: list[str]) -> None:
    missing = sorted(key for key in keys if key not in attrs)
    if missing:
        errors.append(f"{where}: missing required attrs {missing}")


def validate_graph(
    manifest: dict[str, Any],
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
) -> dict[str, Any]:
    errors: list[str] = []

    if manifest.get("schema") != SCHEMA:
        errors.append(f"manifest schema must be {SCHEMA!r}")

    exe_sha = manifest.get("executable_sha256")
    if not isinstance(exe_sha, str) or not SHA256_RE.fullmatch(exe_sha):
        errors.append("manifest executable_sha256 must be 64 lowercase hexadecimal characters")
        exe_sha = None

    executable_id = manifest.get("executable_id")
    if not isinstance(executable_id, str) or not executable_id:
        errors.append("manifest executable_id must be a non-empty string")

    node_by_id: dict[str, dict[str, Any]] = {}
    node_kind: dict[str, str] = {}
    executable_roots = 0

    for index, node in enumerate(nodes):
        where = f"nodes[{index}]"
        node_id = node.get("id")
        kind = node.get("kind")
        attrs = node.get("attrs")

        if not isinstance(node_id, str) or not node_id:
            errors.append(f"{where}: id must be a non-empty string")
            continue
        if node_id in node_by_id:
            errors.append(f"{where}: duplicate node id {node_id!r}")
            continue
        if kind not in NODE_REQUIRED:
            errors.append(f"{where}: unsupported node kind {kind!r}")
            continue
        if not isinstance(attrs, dict):
            errors.append(f"{where}: attrs must be an object")
            continue

        require(attrs, NODE_REQUIRED[kind], where, errors)
        node_by_id[node_id] = node
        node_kind[node_id] = kind

        if kind == "executable_build":
            executable_roots += 1
            if node_id != executable_id:
                errors.append(
                    f"{where}: executable root id {node_id!r} != manifest {executable_id!r}"
                )
            if exe_sha is not None and attrs.get("sha256") != exe_sha:
                errors.append(f"{where}: executable root SHA does not match manifest")
        elif exe_sha is not None and attrs.get("executable_sha256") != exe_sha:
            errors.append(
                f"{where}: node executable_sha256 does not match manifest exact build"
            )

        if kind == "d1_hash_literal":
            value = attrs.get("value_u32")
            expected_hex = attrs.get("value_hex")
            if not isinstance(value, int) or not (0x80800000 <= value <= 0x827FFFFF):
                errors.append(f"{where}: value_u32 is outside the bounded D1 hash range")
            elif expected_hex != f"0x{value:08X}":
                errors.append(f"{where}: value_hex does not match value_u32")

        if kind == "function":
            for field in ("instruction_bytes_sha256", "mnemonic_sequence_sha256"):
                value = attrs.get(field)
                if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
                    errors.append(f"{where}: {field} must be 64 lowercase hex chars")
            ranges = attrs.get("body_ranges")
            if not isinstance(ranges, list):
                errors.append(f"{where}: body_ranges must be an array")
            else:
                for range_index, body_range in enumerate(ranges):
                    if not isinstance(body_range, dict):
                        errors.append(
                            f"{where}: body_ranges[{range_index}] must be an object"
                        )
                        continue
                    lo = body_range.get("min_image_offset")
                    hi = body_range.get("max_image_offset")
                    if not isinstance(lo, int) or not isinstance(hi, int) or lo > hi:
                        errors.append(
                            f"{where}: body_ranges[{range_index}] requires integer min_image_offset <= max_image_offset"
                        )
            count = attrs.get("instruction_count")
            byte_count = attrs.get("instruction_byte_count")
            if not isinstance(count, int) or count < 0:
                errors.append(f"{where}: instruction_count must be a non-negative integer")
            if not isinstance(byte_count, int) or byte_count < 0:
                errors.append(
                    f"{where}: instruction_byte_count must be a non-negative integer"
                )

    if executable_roots != 1:
        errors.append(f"expected exactly one executable_build node, got {executable_roots}")

    seen_edges: set[tuple[str, str, str, str]] = set()
    predicate_counts: dict[str, int] = {}
    for index, edge in enumerate(edges):
        where = f"edges[{index}]"
        subject = edge.get("subject")
        predicate = edge.get("predicate")
        obj = edge.get("object")
        attrs = edge.get("attrs", {})

        if not isinstance(subject, str) or subject not in node_by_id:
            errors.append(f"{where}: unknown subject {subject!r}")
            continue
        if not isinstance(obj, str) or obj not in node_by_id:
            errors.append(f"{where}: unknown object {obj!r}")
            continue
        if predicate not in EDGE_KINDS:
            errors.append(f"{where}: unsupported predicate {predicate!r}")
            continue
        if not isinstance(attrs, dict):
            errors.append(f"{where}: attrs must be an object")
            continue

        subject_allowed, object_allowed = EDGE_KINDS[predicate]
        if node_kind[subject] not in subject_allowed:
            errors.append(
                f"{where}: {predicate} subject kind {node_kind[subject]!r} not allowed"
            )
        if node_kind[obj] not in object_allowed:
            errors.append(
                f"{where}: {predicate} object kind {node_kind[obj]!r} not allowed"
            )

        edge_identity = (
            subject,
            predicate,
            obj,
            json.dumps(attrs, sort_keys=True, separators=(",", ":")),
        )
        if edge_identity in seen_edges:
            errors.append(f"{where}: duplicate edge {subject} {predicate} {obj}")
        seen_edges.add(edge_identity)
        predicate_counts[predicate] = predicate_counts.get(predicate, 0) + 1

    actual_counts = {
        "nodes": len(nodes),
        "edges": len(edges),
        "functions": sum(1 for kind in node_kind.values() if kind == "function"),
        "external_functions": sum(
            1 for kind in node_kind.values() if kind == "external_function"
        ),
        "external_libraries": sum(
            1 for kind in node_kind.values() if kind == "external_library"
        ),
        "defined_strings": sum(
            1 for kind in node_kind.values() if kind == "defined_string"
        ),
        "d1_hash_literals": sum(
            1 for kind in node_kind.values() if kind == "d1_hash_literal"
        ),
        "call_edges": predicate_counts.get("CALLS", 0),
        "string_xref_edges": predicate_counts.get("REFERENCES_STRING", 0),
        "hash_literal_xref_edges": predicate_counts.get(
            "REFERENCES_D1_HASH_LITERAL", 0
        ),
    }

    manifest_counts = manifest.get("counts")
    if not isinstance(manifest_counts, dict):
        errors.append("manifest counts must be an object")
    else:
        for key, actual in actual_counts.items():
            if manifest_counts.get(key) != actual:
                errors.append(
                    f"manifest count {key}={manifest_counts.get(key)!r}, actual={actual}"
                )

    if errors:
        raise ValueError(
            "D1 executable code graph validation failed:\n"
            + "\n".join(f"- {error}" for error in errors)
        )

    return {
        "schema": "d1_code_graph_validation/v1",
        "status": "D1_CODE_GRAPH_VALID",
        "executable_id": executable_id,
        "executable_sha256": exe_sha,
        "counts": actual_counts,
        "predicate_counts": dict(sorted(predicate_counts.items())),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("graph_dir", type=Path)
    parser.add_argument("-o", "--out", type=Path)
    args = parser.parse_args()

    try:
        manifest = read_json(args.graph_dir / "manifest.json")
        nodes = read_jsonl(args.graph_dir / "nodes.jsonl")
        edges = read_jsonl(args.graph_dir / "edges.jsonl")
        result = validate_graph(manifest, nodes, edges)
        encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(encoded, encoding="utf-8")
        print(encoded, end="")
        return 0
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
