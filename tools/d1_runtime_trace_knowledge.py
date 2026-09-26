#!/usr/bin/env python3
"""Promote normalized runtime code traces into d1_knowledge_record/v1.

Input is a small, reviewable d1_runtime_code_trace/v1 JSON document. The tool
preserves dynamic stack order, build scoping, thread semantics and fixed-address
global accesses without inventing static CALLS edges or semantic function names.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

SCHEMA = "d1_runtime_code_trace/v1"
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def read_json(path: Path) -> dict[str, Any]:
    doc = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict):
        raise ValueError(f"{path}: expected JSON object")
    return doc


def source_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_str(obj: dict[str, Any], key: str, where: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{where}: {key} must be a non-empty string")
    return value


def parse_address(value: str, where: str) -> int:
    try:
        out = int(value, 0)
    except Exception as exc:
        raise ValueError(f"{where}: invalid address {value!r}") from exc
    if out < 0:
        raise ValueError(f"{where}: address must be non-negative")
    return out


def build_namespace(build: dict[str, Any]) -> str:
    sha = build.get("sha256")
    if isinstance(sha, str) and SHA256_RE.fullmatch(sha):
        return sha.lower()[:16]
    title_id = build.get("title_id")
    if isinstance(title_id, str) and title_id:
        return "reported" + re.sub(r"[^A-Za-z0-9]+", "", title_id)
    label = build.get("build_label")
    if isinstance(label, str) and label:
        digest = hashlib.sha256(label.encode("utf-8")).hexdigest()[:16]
        return "label" + digest
    raise ValueError("build requires sha256, title_id, or build_label")


def executable_node_id(build: dict[str, Any], namespace: str) -> str:
    platform = require_str(build, "platform", "build").lower().replace(" ", "")
    title_id = build.get("title_id")
    version = build.get("app_version") or build.get("build_label") or "unknown"
    if isinstance(title_id, str) and title_id:
        return f"executable:{platform}:{title_id}:{version}:{namespace}"
    return f"executable:{platform}:{version}:{namespace}"


def function_node_id(platform: str, namespace: str, address: int) -> str:
    return f"function:{platform.lower().replace(' ', '')}:{namespace}:{address:08X}"


def global_node_id(platform: str, namespace: str, address: int) -> str:
    return f"global:{platform.lower().replace(' ', '')}:{namespace}:{address:08X}"


def promote(trace_path: Path, doc: dict[str, Any]) -> dict[str, Any]:
    if doc.get("schema") != SCHEMA:
        raise ValueError(f"trace schema must be {SCHEMA!r}")

    trace_id = require_str(doc, "trace_id", "trace")
    updated_utc = require_str(doc, "updated_utc", "trace")
    build = doc.get("build")
    source = doc.get("source")
    frames = doc.get("frames")
    if not isinstance(build, dict):
        raise ValueError("trace: build must be an object")
    if not isinstance(source, dict):
        raise ValueError("trace: source must be an object")
    if not isinstance(frames, list) or not frames:
        raise ValueError("trace: frames must be a non-empty array")

    platform = require_str(build, "platform", "build")
    namespace = build_namespace(build)
    exe_id = executable_node_id(build, namespace)
    build_sha = build.get("sha256")
    if build_sha is not None and (
        not isinstance(build_sha, str) or not SHA256_RE.fullmatch(build_sha)
    ):
        raise ValueError("build.sha256 must be 64 hexadecimal characters or null")

    build_status = "PROVEN" if isinstance(build_sha, str) else "STRONGLY_SUPPORTED"
    trace_node_id = f"runtime_trace:{trace_id}"

    nodes: dict[str, dict[str, Any]] = {
        exe_id: {
            "id": exe_id,
            "kind": "executable_build",
            "status": build_status,
            "label": build.get("label") or f"{platform} {build.get('title_id') or build.get('build_label') or 'build'}",
            "attrs": {
                **build,
                "identity_basis": "exact_sha256" if build_status == "PROVEN" else "reported_runtime_build",
            },
        },
        trace_node_id: {
            "id": trace_node_id,
            "kind": "runtime_code_trace",
            "status": "STRONGLY_SUPPORTED",
            "label": doc.get("label") or trace_id,
            "attrs": {
                "thread": doc.get("thread"),
                "fault": doc.get("fault"),
                "runtime_events": doc.get("runtime_events", []),
            },
        },
    }
    edges: list[dict[str, Any]] = [
        {
            "id": "edge:build_trace",
            "subject": exe_id,
            "predicate": "HAS_RUNTIME_TRACE",
            "object": trace_node_id,
            "status": "STRONGLY_SUPPORTED",
            "assertion_ids": ["assert:trace"],
            "attrs": {},
        }
    ]

    external_nodes: list[dict[str, Any]] = []
    thread = doc.get("thread")
    if isinstance(thread, dict):
        semantic_id = thread.get("semantic_node_id")
        if isinstance(semantic_id, str) and semantic_id:
            external_nodes.append(
                {
                    "id": semantic_id,
                    "record_id": thread.get("semantic_record_id"),
                    "note": "Thread semantic supplied by reviewed runtime-trace input.",
                }
            )
            edges.append(
                {
                    "id": "edge:trace_thread",
                    "subject": trace_node_id,
                    "predicate": "OBSERVED_ON_THREAD",
                    "object": semantic_id,
                    "status": "STRONGLY_SUPPORTED",
                    "assertion_ids": ["assert:trace"],
                    "attrs": {
                        "name": thread.get("name"),
                        "handle": thread.get("handle"),
                        "is_thread_start": thread.get("is_thread_start"),
                    },
                }
            )

    seen_depths: set[int] = set()
    address_to_function: dict[int, str] = {}
    for i, frame in enumerate(frames):
        if not isinstance(frame, dict):
            raise ValueError(f"frames[{i}] must be an object")
        depth = frame.get("depth")
        if not isinstance(depth, int) or depth < 0:
            raise ValueError(f"frames[{i}].depth must be a non-negative integer")
        if depth in seen_depths:
            raise ValueError(f"duplicate runtime frame depth {depth}")
        seen_depths.add(depth)

        address_text = require_str(frame, "address", f"frames[{i}]")
        address = parse_address(address_text, f"frames[{i}]")
        fn_id = function_node_id(platform, namespace, address)
        address_to_function[address] = fn_id
        nodes.setdefault(
            fn_id,
            {
                "id": fn_id,
                "kind": "function",
                "status": "STRONGLY_SUPPORTED",
                "label": frame.get("symbol") or f"sub_{address:X}",
                "attrs": {
                    "platform": platform,
                    "runtime_address": f"0x{address:X}",
                    "symbol": frame.get("symbol"),
                    "module": frame.get("module"),
                    "generated_line": frame.get("generated_line"),
                    "exact_function_bytes_sha256": None,
                    "evidence_kind": "runtime_stack_frame",
                    "frame_attrs": frame.get("attrs", {}),
                },
            },
        )
        edges.append(
            {
                "id": f"edge:frame:{depth:04d}",
                "subject": trace_node_id,
                "predicate": "HAS_RUNTIME_STACK_FRAME",
                "object": fn_id,
                "status": "STRONGLY_SUPPORTED",
                "assertion_ids": ["assert:trace"],
                "attrs": {
                    "depth": depth,
                    "generated_line": frame.get("generated_line"),
                    "module": frame.get("module"),
                },
            }
        )

    globals_rows = doc.get("globals", [])
    if not isinstance(globals_rows, list):
        raise ValueError("trace.globals must be an array when present")
    for i, row in enumerate(globals_rows):
        if not isinstance(row, dict):
            raise ValueError(f"globals[{i}] must be an object")
        address = parse_address(require_str(row, "address", f"globals[{i}]"), f"globals[{i}]")
        fn_address = parse_address(
            require_str(row, "source_function_address", f"globals[{i}]"),
            f"globals[{i}]",
        )
        fn_id = address_to_function.get(fn_address)
        if fn_id is None:
            raise ValueError(
                f"globals[{i}] source function 0x{fn_address:X} is not a runtime frame"
            )
        access = require_str(row, "access", f"globals[{i}]").lower()
        if access not in {"read", "write"}:
            raise ValueError(f"globals[{i}].access must be read or write")
        global_id = global_node_id(platform, namespace, address)
        nodes.setdefault(
            global_id,
            {
                "id": global_id,
                "kind": "guest_global",
                "status": "STRONGLY_SUPPORTED",
                "label": f"guest global 0x{address:X}",
                "attrs": {
                    "platform": platform,
                    "address": f"0x{address:X}",
                    "semantic_role": None,
                },
            },
        )
        edges.append(
            {
                "id": f"edge:global:{i:04d}",
                "subject": fn_id,
                "predicate": "READS_GUEST_GLOBAL" if access == "read" else "WRITES_GUEST_GLOBAL",
                "object": global_id,
                "status": "STRONGLY_SUPPORTED",
                "assertion_ids": ["assert:trace"],
                "attrs": {
                    "instruction": row.get("instruction"),
                    "details": row.get("attrs", {}),
                },
            }
        )

    source_id = "source:runtime_trace"
    source_locator = require_str(source, "locator", "source")
    assertion_claim = doc.get("claim")
    if not isinstance(assertion_claim, str) or not assertion_claim:
        assertion_claim = (
            f"Runtime source {source_locator} reports {len(frames)} ordered guest/code "
            f"frames for {doc.get('label') or trace_id}; stack order is retained as "
            "runtime evidence and is not promoted to static CALLS edges."
        )

    return {
        "schema": "d1_knowledge_record/v1",
        "record_id": require_str(doc, "record_id", "trace"),
        "title": require_str(doc, "title", "trace"),
        "updated_utc": updated_utc,
        "scope": {
            "game": "Destiny 1",
            "platform": platform,
            "title_id": build.get("title_id"),
            "app_version": build.get("app_version"),
            "build_label": build.get("build_label"),
            "executable_sha256": build_sha,
            "kind": "runtime_code_trace",
        },
        "nodes": sorted(nodes.values(), key=lambda row: row["id"]),
        "external_nodes": external_nodes,
        "edges": edges,
        "assertions": [
            {
                "id": "assert:trace",
                "status": "STRONGLY_SUPPORTED",
                "claim": assertion_claim,
                "source_ids": [source_id, "source:trace_input"],
                "details": {
                    "frame_count": len(frames),
                    "dynamic_stack_not_static_calls": True,
                },
            }
        ],
        "sources": [
            {
                "id": source_id,
                "kind": source.get("kind") or "runtime_report",
                "locator": source_locator,
                "sha256": source.get("sha256"),
                "details": source.get("details", {}),
            },
            {
                "id": "source:trace_input",
                "kind": "repository_runtime_trace_input",
                "locator": str(trace_path),
                "sha256": source_sha256(trace_path),
                "details": {"schema": SCHEMA},
            },
        ],
        "rejections": [],
        "frontiers": doc.get("frontiers", []),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("trace", type=Path)
    parser.add_argument("-o", "--out", type=Path, required=True)
    args = parser.parse_args()

    doc = read_json(args.trace)
    record = promote(args.trace, doc)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
