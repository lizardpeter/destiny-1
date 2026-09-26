#!/usr/bin/env python3
"""Promote a D1 executable probe report into d1_knowledge_record/v1.

The generated record deliberately stores structure/provenance, not retail bytes.
Every node is scoped to the exact SHA-256 so later functions, xrefs and semantic
matches cannot silently drift across executable versions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    doc = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict):
        raise ValueError("probe report must be a JSON object")
    if doc.get("schema") not in {"d1_executable_probe/v1", "d1_executable_probe/v2"}:
        raise ValueError(f"unsupported probe schema {doc.get('schema')!r}")
    sha = doc.get("sha256")
    if not isinstance(sha, str) or len(sha) != 64:
        raise ValueError("probe report must contain a 64-character sha256")
    return doc


def source_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_identity(
    probe: dict[str, Any], title_id: str | None, app_version: str | None
) -> tuple[str, str, str]:
    known = probe.get("known_build")
    if isinstance(known, dict):
        known_title = known.get("title_id")
        known_version = known.get("app_version")
        if isinstance(known_title, str) and isinstance(known_version, str):
            return known_title, known_version, "known_build_fingerprint"

    if not title_id or not app_version:
        raise ValueError(
            "unknown executable fingerprint: provide --title-id and --app-version "
            "rather than assigning build identity by guess"
        )
    return title_id, app_version, "operator_supplied_build_identity"


def make_record(
    probe: dict[str, Any],
    probe_path: Path,
    *,
    title_id: str | None = None,
    app_version: str | None = None,
    updated_utc: str | None = None,
) -> dict[str, Any]:
    sha = probe["sha256"].lower()
    short = sha[:16]
    title_id, app_version, identity_basis = build_identity(
        probe, title_id, app_version
    )
    executable_id = f"executable:{title_id}:{app_version}:{short}"
    elf_id = f"elf_image:{title_id}:{app_version}:{short}"
    executable_status = (
        "STRONGLY_SUPPORTED"
        if identity_basis == "known_build_fingerprint"
        else "CANDIDATE"
    )

    nodes: list[dict[str, Any]] = [
        {
            "id": executable_id,
            "kind": "executable_build",
            "status": executable_status,
            "label": f"{title_id} {app_version} executable {short}",
            "attrs": {
                "sha256": sha,
                "file_size": probe.get("file_size"),
                "container": probe.get("container"),
                "identity_basis": identity_basis,
                "retail_bytes_committed": False,
            },
        }
    ]
    edges: list[dict[str, Any]] = []
    assertions: list[dict[str, Any]] = [
        {
            "id": "assert_exact_fingerprint",
            "status": "PROVEN",
            "claim": (
                f"The analyzed executable artifact has exact SHA-256 {sha} and "
                f"size {probe.get('file_size')} bytes. Build labeling remains "
                f"{executable_status} under {identity_basis}."
            ),
            "source_ids": ["src_probe_report", "src_external_executable"],
            "details": {
                "container": probe.get("container"),
                "identity_basis": identity_basis,
            },
        }
    ]

    elf_header = probe.get("elf_header")
    if isinstance(elf_header, dict):
        nodes.append(
            {
                "id": elf_id,
                "kind": "elf_image",
                "status": "PROVEN",
                "label": f"ELF image for {title_id} {app_version}",
                "attrs": elf_header,
            }
        )
        assertions.append(
            {
                "id": "assert_elf_image",
                "status": "PROVEN",
                "claim": (
                    "The executable probe located an ELF image and decoded its "
                    "ELF64 header directly from the analyzed artifact."
                ),
                "source_ids": ["src_probe_report"],
                "details": {
                    "embedded_elf_offset": probe.get("embedded_elf_offset"),
                    "machine": elf_header.get("machine_name"),
                    "entry": elf_header.get("entry"),
                },
            }
        )
        edges.append(
            {
                "id": "edge_executable_contains_elf",
                "subject": executable_id,
                "predicate": "CONTAINS_ELF_IMAGE",
                "object": elf_id,
                "status": "PROVEN",
                "assertion_ids": ["assert_elf_image"],
                "attrs": {
                    "embedded_elf_offset": probe.get("embedded_elf_offset")
                },
            }
        )

        for segment in probe.get("program_headers", []):
            if not isinstance(segment, dict):
                continue
            index = segment.get("index")
            segment_id = f"elf_segment:{title_id}:{app_version}:{short}:{index}"
            nodes.append(
                {
                    "id": segment_id,
                    "kind": "elf_program_segment",
                    "status": "PROVEN",
                    "label": (
                        f"{segment.get('type_name', 'segment')}[{index}] "
                        f"{segment.get('virtual_address', '')}"
                    ).strip(),
                    "attrs": segment,
                }
            )
            assertion_id = f"assert_segment_{index}"
            assertions.append(
                {
                    "id": assertion_id,
                    "status": "PROVEN",
                    "claim": (
                        f"ELF program segment {index} has type "
                        f"{segment.get('type_name')} at virtual address "
                        f"{segment.get('virtual_address')} with file size "
                        f"{segment.get('file_size')}."
                    ),
                    "source_ids": ["src_probe_report"],
                    "details": {
                        "executable": bool(segment.get("executable")),
                        "readable": bool(segment.get("readable")),
                        "writable": bool(segment.get("writable")),
                    },
                }
            )
            edges.append(
                {
                    "id": f"edge_elf_segment_{index}",
                    "subject": elf_id,
                    "predicate": "HAS_PROGRAM_SEGMENT",
                    "object": segment_id,
                    "status": "PROVEN",
                    "assertion_ids": [assertion_id],
                    "attrs": {},
                }
            )

    anchor = probe.get("research_anchors", {}).get(
        "graphics_heartbeat_code_offset"
    )
    frontier_nodes = [executable_id]
    if isinstance(anchor, str):
        anchor_id = f"code_anchor:{title_id}:{app_version}:graphics_heartbeat:{anchor}"
        nodes.append(
            {
                "id": anchor_id,
                "kind": "runtime_code_anchor",
                "status": "CANDIDATE",
                "label": f"Graphics Heartbeat neighborhood {anchor}",
                "attrs": {
                    "code_offset": anchor,
                    "function_identity_proven": False,
                    "build_match_required": True,
                },
            }
        )
        assertions.append(
            {
                "id": "assert_graphics_heartbeat_anchor",
                "status": "CANDIDATE",
                "claim": (
                    f"Public Destiny CUSA00219 runtime evidence identifies {anchor} "
                    "as a useful Graphics Heartbeat code neighborhood, but this "
                    "specific executable still requires local byte/xref correlation."
                ),
                "source_ids": ["src_public_runtime_anchor"],
                "details": {},
            }
        )
        edges.append(
            {
                "id": "edge_executable_candidate_anchor",
                "subject": executable_id,
                "predicate": "HAS_CANDIDATE_CODE_ANCHOR",
                "object": anchor_id,
                "status": "CANDIDATE",
                "assertion_ids": ["assert_graphics_heartbeat_anchor"],
                "attrs": {},
            }
        )
        frontier_nodes.append(anchor_id)

    stamp = updated_utc or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    record_id = f"d1_executable_{title_id.lower()}_{app_version.replace('.', '_')}_{short}"
    return {
        "schema": "d1_knowledge_record/v1",
        "record_id": record_id,
        "title": f"Destiny 1 executable intake {title_id} {app_version} {short}",
        "updated_utc": stamp,
        "scope": {
            "game": "Destiny 1",
            "platform": "PS4",
            "title_id": title_id,
            "app_version": app_version,
            "executable_sha256": sha,
        },
        "nodes": nodes,
        "edges": edges,
        "assertions": assertions,
        "sources": [
            {
                "id": "src_probe_report",
                "kind": "executable_probe_report",
                "locator": str(probe_path),
                "sha256": source_sha256(probe_path),
                "details": {
                    "schema": probe.get("schema"),
                    "tool": "tools/d1_executable_probe.py",
                },
            },
            {
                "id": "src_external_executable",
                "kind": "external_binary_fingerprint",
                "locator": f"sha256:{sha}",
                "sha256": sha,
                "details": {
                    "retail_bytes_committed": False,
                    "file_size": probe.get("file_size"),
                },
            },
            {
                "id": "src_public_runtime_anchor",
                "kind": "public_compatibility_report",
                "locator": "https://github.com/shadps4-compatibility/shadps4-game-compatibility/issues/994",
                "sha256": None,
                "details": {
                    "role": "Graphics Heartbeat runtime anchor only"
                },
            },
        ],
        "rejections": [],
        "frontiers": [
            {
                "id": "frontier_function_recovery",
                "question": (
                    "Which executable functions consume the already-reversed "
                    "Destiny Tiger, material, shader, animation and world structures?"
                ),
                "next_proof": (
                    "Disassemble this exact SHA-256 build, recover function "
                    "boundaries/xrefs/imports, and correlate constants/raw strings/"
                    "TagHash consumers to existing package evidence."
                ),
                "related_nodes": frontier_nodes,
            }
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("probe_report", type=Path)
    parser.add_argument("-o", "--out", type=Path, required=True)
    parser.add_argument("--title-id")
    parser.add_argument("--app-version")
    args = parser.parse_args()

    probe = load_json(args.probe_report)
    record = make_record(
        probe,
        args.probe_report,
        title_id=args.title_id,
        app_version=args.app_version,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
