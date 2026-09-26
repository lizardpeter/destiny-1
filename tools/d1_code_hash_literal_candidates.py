#!/usr/bin/env python3
"""Find executable functions that reference known D1 class/hash literals.

A literal equality is discovery evidence only. This tool never promotes a
function to a parser/owner automatically; it emits candidate sites for review
and later semantic-bridge promotion.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    doc = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict):
        raise ValueError(f"{path}: expected object")
    return doc


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    out = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{line_no}: expected object")
        out.append(row)
    return out


def parse_u32(text: str) -> int:
    value = int(text, 0) if text.lower().startswith("0x") else int(text, 16)
    if value < 0 or value > 0xFFFFFFFF:
        raise ValueError(f"not a u32: {text}")
    return value


def load_registry(path: Path | None) -> dict[int, dict[str, Any]]:
    if path is None:
        return {}
    doc = read_json(path)
    if doc.get("schema") != "d1_export_class_registry/v1":
        raise ValueError(f"{path}: unsupported registry schema {doc.get('schema')!r}")
    out = {}
    for key, value in doc.get("reference_classes", {}).items():
        out[int(key, 16)] = value if isinstance(value, dict) else {}
    return out


def analyze(
    graph_dir: Path,
    registry: dict[int, dict[str, Any]],
    explicit_values: list[int],
) -> dict[str, Any]:
    manifest = read_json(graph_dir / "manifest.json")
    if manifest.get("schema") != "d1_normalized_code_graph/v1":
        raise ValueError("normalized code graph manifest schema mismatch")
    nodes = read_jsonl(graph_dir / "nodes.jsonl")
    edges = read_jsonl(graph_dir / "edges.jsonl")

    nodes_by_id = {
        row["id"]: row
        for row in nodes
        if isinstance(row.get("id"), str)
    }
    literal_by_value = {
        row.get("attrs", {}).get("value_u32"): row
        for row in nodes
        if row.get("kind") == "d1_hash_literal"
        and isinstance(row.get("attrs"), dict)
        and isinstance(row["attrs"].get("value_u32"), int)
    }

    xrefs_by_literal: dict[str, list[dict[str, Any]]] = {}
    for edge in edges:
        if edge.get("predicate") != "REFERENCES_D1_HASH_LITERAL":
            continue
        obj = edge.get("object")
        if isinstance(obj, str):
            xrefs_by_literal.setdefault(obj, []).append(edge)

    requested = sorted(set(registry) | set(explicit_values))
    rows = []
    for value in requested:
        literal = literal_by_value.get(value)
        registry_row = registry.get(value, {})
        item = {
            "value_u32": value,
            "value_hex": f"{value:08X}",
            "registry_label": registry_row.get("label"),
            "registry_semantic_status": registry_row.get("semantic_status"),
            "registry_export_route": registry_row.get("export_route"),
            "literal_present": literal is not None,
            "status": "LITERAL_MATCH_ONLY" if literal is not None else "NOT_OBSERVED",
            "occurrence_count": 0,
            "function_count": 0,
            "functions": [],
        }
        if literal is not None:
            xrefs = xrefs_by_literal.get(literal["id"], [])
            grouped: dict[str, list[dict[str, Any]]] = {}
            for edge in xrefs:
                function_id = edge.get("subject")
                if isinstance(function_id, str):
                    grouped.setdefault(function_id, []).append(edge.get("attrs", {}))

            for function_id, occurrences in sorted(grouped.items()):
                function = nodes_by_id.get(function_id)
                attrs = function.get("attrs", {}) if function else {}
                item["functions"].append(
                    {
                        "function_id": function_id,
                        "name": attrs.get("name"),
                        "image_offset": attrs.get("image_offset"),
                        "entry": attrs.get("entry"),
                        "instruction_count": attrs.get("instruction_count"),
                        "instruction_bytes_sha256": attrs.get(
                            "instruction_bytes_sha256"
                        ),
                        "mnemonic_sequence_sha256": attrs.get(
                            "mnemonic_sequence_sha256"
                        ),
                        "occurrences": sorted(
                            occurrences,
                            key=lambda row: (
                                row.get("instruction_image_offset")
                                if isinstance(row.get("instruction_image_offset"), int)
                                else 1 << 65,
                                row.get("operand_index")
                                if isinstance(row.get("operand_index"), int)
                                else 1 << 31,
                            ),
                        ),
                    }
                )
            item["occurrence_count"] = sum(
                len(row["occurrences"]) for row in item["functions"]
            )
            item["function_count"] = len(item["functions"])
        rows.append(item)

    return {
        "schema": "d1_code_hash_literal_candidates/v1",
        "status": "D1_CODE_HASH_LITERAL_CANDIDATES_COMPLETE",
        "executable_sha256": manifest.get("executable_sha256"),
        "title_id": manifest.get("title_id"),
        "app_version": manifest.get("app_version"),
        "policy": (
            "Exact instruction literal equality only. A matching class/TagHash "
            "value identifies candidate code sites and never proves parser, "
            "ownership, resource role or semantic function identity by itself."
        ),
        "requested_value_count": len(rows),
        "observed_value_count": sum(1 for row in rows if row["literal_present"]),
        "observed_occurrence_count": sum(row["occurrence_count"] for row in rows),
        "observed_function_count": len(
            {
                fn["function_id"]
                for row in rows
                for fn in row["functions"]
            }
        ),
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("graph_dir", type=Path)
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path("evidence/d1_export_class_registry.json"),
    )
    parser.add_argument(
        "--value",
        action="append",
        default=[],
        type=parse_u32,
        help="additional 32-bit candidate in hex, e.g. 80801AD7 or 0x80801AD7",
    )
    parser.add_argument("-o", "--out", type=Path)
    args = parser.parse_args()

    registry = load_registry(args.registry) if args.registry else {}
    result = analyze(args.graph_dir, registry, args.value)
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
