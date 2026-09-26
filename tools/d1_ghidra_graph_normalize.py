#!/usr/bin/env python3
"""Normalize a D1 Ghidra export into graph-native JSONL node/edge streams.

The output is designed to be easy to ingest into FalkorDB or another graph
backend while remaining diffable and deterministic on disk.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def read_report(path: Path) -> dict[str, Any]:
    doc = json.loads(path.read_text(encoding="utf-8"))
    if doc.get("schema") != "d1_ghidra_code_graph/v1":
        raise ValueError(f"unsupported code graph schema {doc.get('schema')!r}")
    program = doc.get("program")
    if not isinstance(program, dict):
        raise ValueError("missing program object")
    sha = program.get("executable_sha256")
    if not isinstance(sha, str) or len(sha) != 64:
        raise ValueError("Ghidra export must contain a 64-character executable_sha256")
    return doc


def stable_external_id(exe_sha: str, library: str | None, name: str) -> str:
    key = f"{library or ''}\0{name}".encode("utf-8")
    digest = hashlib.sha256(key).hexdigest()[:20]
    return f"external:{exe_sha[:16]}:{digest}"


def stable_library_id(exe_sha: str, name: str) -> str:
    digest = hashlib.sha256(name.encode("utf-8")).hexdigest()[:20]
    return f"library:{exe_sha[:16]}:{digest}"


def function_id(exe_sha: str, offset: int | None, entry: str) -> str:
    if offset is not None:
        return f"function:{exe_sha[:16]}:{offset & ((1 << 64) - 1):016x}"
    digest = hashlib.sha256(entry.encode("utf-8")).hexdigest()[:20]
    return f"function:{exe_sha[:16]}:addr_{digest}"


def string_id(exe_sha: str, offset: int | None, address: str) -> str:
    if offset is not None:
        return f"string:{exe_sha[:16]}:{offset & ((1 << 64) - 1):016x}"
    digest = hashlib.sha256(address.encode("utf-8")).hexdigest()[:20]
    return f"string:{exe_sha[:16]}:addr_{digest}"


def d1_hash_literal_id(exe_sha: str, value: int) -> str:
    return f"d1hash:{exe_sha[:16]}:{value & 0xFFFFFFFF:08x}"


def normalize(doc: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    program = doc["program"]
    exe_sha = program["executable_sha256"].lower()
    title_id = program.get("title_id")
    app_version = program.get("app_version")
    executable_id = f"executable:{title_id or 'unknown'}:{app_version or 'unknown'}:{exe_sha[:16]}"

    nodes: list[dict[str, Any]] = [
        {
            "id": executable_id,
            "kind": "executable_build",
            "attrs": {
                "sha256": exe_sha,
                "title_id": title_id,
                "app_version": app_version,
                "image_base": program.get("image_base"),
                "language_id": program.get("language_id"),
                "compiler_spec": program.get("compiler_spec"),
                "executable_format": program.get("executable_format"),
            },
        }
    ]
    edges: list[dict[str, Any]] = []

    internal_by_entry: dict[str, str] = {}
    literal_nodes: dict[int, str] = {}
    for fn in doc.get("functions", []):
        if not isinstance(fn, dict):
            continue
        node_id = function_id(exe_sha, fn.get("image_offset"), str(fn.get("entry")))
        internal_by_entry[str(fn.get("entry"))] = node_id
        function_attrs = {key: value for key, value in fn.items() if key != "d1_hash_literals"}
        function_attrs.update(
            {
                "executable_sha256": exe_sha,
                "title_id": title_id,
                "app_version": app_version,
            }
        )
        nodes.append(
            {
                "id": node_id,
                "kind": "function",
                "attrs": function_attrs,
            }
        )
        edges.append(
            {
                "subject": executable_id,
                "predicate": "HAS_FUNCTION",
                "object": node_id,
                "attrs": {},
            }
        )
        for literal in fn.get("d1_hash_literals", []):
            if not isinstance(literal, dict):
                continue
            value = literal.get("value_u32")
            if not isinstance(value, int) or not (0x80800000 <= value <= 0x827FFFFF):
                continue
            literal_node = literal_nodes.setdefault(
                value, d1_hash_literal_id(exe_sha, value)
            )
            edges.append(
                {
                    "subject": node_id,
                    "predicate": "REFERENCES_D1_HASH_LITERAL",
                    "object": literal_node,
                    "attrs": {
                        "instruction": literal.get("instruction"),
                        "instruction_image_offset": literal.get("instruction_image_offset"),
                        "operand_index": literal.get("operand_index"),
                        "bit_length": literal.get("bit_length"),
                    },
                }
            )

    for value, literal_node in sorted(literal_nodes.items()):
        nodes.append(
            {
                "id": literal_node,
                "kind": "d1_hash_literal",
                "attrs": {
                    "executable_sha256": exe_sha,
                    "value_u32": value,
                    "value_hex": f"0x{value:08X}",
                },
            }
        )
        edges.append(
            {
                "subject": executable_id,
                "predicate": "HAS_D1_HASH_LITERAL",
                "object": literal_node,
                "attrs": {},
            }
        )

    library_nodes: dict[str, str] = {}
    for lib in doc.get("external_libraries", []):
        if not isinstance(lib, dict):
            continue
        name = str(lib.get("name"))
        node_id = stable_library_id(exe_sha, name)
        library_nodes[name] = node_id
        nodes.append(
            {
                "id": node_id,
                "kind": "external_library",
                "attrs": {**lib, "executable_sha256": exe_sha},
            }
        )
        edges.append(
            {
                "subject": executable_id,
                "predicate": "IMPORTS_LIBRARY",
                "object": node_id,
                "attrs": {},
            }
        )

    external_by_entry: dict[str, str] = {}
    for ext in doc.get("external_functions", []):
        if not isinstance(ext, dict):
            continue
        name = str(ext.get("name"))
        library = ext.get("library")
        node_id = stable_external_id(exe_sha, library, name)
        external_by_entry[str(ext.get("entry"))] = node_id
        nodes.append(
            {
                "id": node_id,
                "kind": "external_function",
                "attrs": {**ext, "executable_sha256": exe_sha},
            }
        )
        edges.append(
            {
                "subject": executable_id,
                "predicate": "IMPORTS_FUNCTION",
                "object": node_id,
                "attrs": {},
            }
        )
        if isinstance(library, str) and library in library_nodes:
            edges.append(
                {
                    "subject": node_id,
                    "predicate": "BELONGS_TO_LIBRARY",
                    "object": library_nodes[library],
                    "attrs": {},
                }
            )

    for call in doc.get("calls", []):
        if not isinstance(call, dict):
            continue
        caller = internal_by_entry.get(str(call.get("caller")))
        target_entry = str(call.get("callee"))
        callee = internal_by_entry.get(target_entry) or external_by_entry.get(target_entry)
        if caller is None or callee is None:
            continue
        edges.append(
            {
                "subject": caller,
                "predicate": "CALLS",
                "object": callee,
                "attrs": {},
            }
        )

    for item in doc.get("strings", []):
        if not isinstance(item, dict):
            continue
        node_id = string_id(exe_sha, item.get("image_offset"), str(item.get("address")))
        string_attrs = {k: v for k, v in item.items() if k != "xrefs"}
        string_attrs["executable_sha256"] = exe_sha
        nodes.append({"id": node_id, "kind": "defined_string", "attrs": string_attrs})
        edges.append(
            {
                "subject": executable_id,
                "predicate": "HAS_DEFINED_STRING",
                "object": node_id,
                "attrs": {},
            }
        )
        for xref in item.get("xrefs", []):
            if not isinstance(xref, dict):
                continue
            owner = internal_by_entry.get(str(xref.get("function_entry")))
            if owner is None:
                continue
            edges.append(
                {
                    "subject": owner,
                    "predicate": "REFERENCES_STRING",
                    "object": node_id,
                    "attrs": {
                        "from": xref.get("from"),
                        "from_image_offset": xref.get("from_image_offset"),
                        "reference_type": xref.get("reference_type"),
                    },
                }
            )

    nodes.sort(key=lambda n: n["id"])
    edges.sort(
        key=lambda e: (
            e["subject"],
            e["predicate"],
            e["object"],
            json.dumps(e.get("attrs", {}), sort_keys=True),
        )
    )

    manifest = {
        "schema": "d1_normalized_code_graph/v1",
        "executable_id": executable_id,
        "executable_sha256": exe_sha,
        "title_id": title_id,
        "app_version": app_version,
        "source_schema": doc.get("schema"),
        "counts": {
            "nodes": len(nodes),
            "edges": len(edges),
            "functions": sum(1 for n in nodes if n["kind"] == "function"),
            "external_functions": sum(1 for n in nodes if n["kind"] == "external_function"),
            "external_libraries": sum(1 for n in nodes if n["kind"] == "external_library"),
            "defined_strings": sum(1 for n in nodes if n["kind"] == "defined_string"),
            "d1_hash_literals": sum(1 for n in nodes if n["kind"] == "d1_hash_literal"),
            "call_edges": sum(1 for e in edges if e["predicate"] == "CALLS"),
            "string_xref_edges": sum(1 for e in edges if e["predicate"] == "REFERENCES_STRING"),
            "hash_literal_xref_edges": sum(
                1 for e in edges if e["predicate"] == "REFERENCES_D1_HASH_LITERAL"
            ),
        },
    }
    return manifest, nodes, edges


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for row in rows:
            fh.write(json.dumps(row, sort_keys=True, ensure_ascii=False))
            fh.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ghidra_export", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    doc = read_report(args.ghidra_export)
    manifest, nodes, edges = normalize(doc)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_jsonl(args.out_dir / "nodes.jsonl", nodes)
    write_jsonl(args.out_dir / "edges.jsonl", edges)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
