#!/usr/bin/env python3
"""Inventory renderer-oriented strings and candidate RIP-relative xrefs in a D1 PS4 ELF.

This is a discovery pass over the exact executable bytes. It does not assign
function semantics. The output is intentionally loss-preserving and namespaced by
full executable SHA-256 so later Ghidra/decompiler evidence can promote only
source-closed relationships.

The default profile is deliberately broad enough to find renderer orchestration,
material/shader setup, draw submission, deferred lighting, sky/fog and post
processing diagnostics without relying on Tower-specific addresses.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

from d1_elf_rip_string_xrefs import probe as rip_probe
from d1_executable_probe import printable_ascii_strings


CATEGORY_PATTERNS: dict[str, tuple[str, ...]] = {
    "frame_graph": (
        r"render(?:er|ing)?",
        r"graphics:",
        r"frame(?:buffer)?",
        r"back[_ -]?buffer",
        r"swap[_ -]?chain",
        r"present",
        r"render[_ -]?target",
        r"mrt\d*",
        r"gbuffer",
        r"g[-_ ]?buffer",
        r"resolve",
        r"generate_gbuffer",
        r"final_combine_output_surface",
        r"quarter_res_transp_surface",
        r"screen area fullscreen textures",
    ),
    "shader_material": (
        r"shader",
        r"vertex[_ -]?shader",
        r"pixel[_ -]?shader",
        r"material",
        r"technique",
        r"texture",
        r"sampler",
        r"constant[_ -]?buffer",
        r"resource[_ -]?table",
        r"descriptor",
    ),
    "fixed_function": (
        r"blend",
        r"depth",
        r"stencil",
        r"raster",
        r"cull",
        r"viewport",
        r"scissor",
        r"color[_ -]?write",
        r"depth_stencil",
        r"depth_prepass",
        r"minmax_depth",
        r"min_max_depth",
    ),
    "draw_submit": (
        r"draw",
        r"dispatch",
        r"submit",
        r"command[_ -]?buffer",
        r"command[_ -]?list",
        r"gpu",
        r"fence",
        r"render_submit",
    ),
    "lighting": (
        r"lighting",
        r"light[_ -]?probe",
        r"light[_ -]?shaft",
        r"shadow",
        r"reflection",
        r"irradiance",
        r"ambient[_ -]?occlusion",
        r"deferred[_ -]?lights",
        r"chunked[_ -]?lights",
        r"mask[_ -]?sun[_ -]?light",
        r"autoexposure",
        r"hdr",
    ),
    "environment": (
        r"sky",
        r"fog",
        r"atmosphere",
        r"cloud",
        r"weather",
        r"water_reflection",
    ),
    "post": (
        r"post[-_ ]?process(?:ing)?",
        r"postprocess",
        r"bloom",
        r"tonemap(?:ping)?",
        r"color[_ -]?grade",
        r"taa",
        r"fxaa",
        r"dof",
        r"depth[_ -]?of[_ -]?field",
        r"motion[_ -]?blur",
    ),
}

COMPILED_PATTERNS = {
    category: tuple(re.compile(pattern, re.IGNORECASE) for pattern in patterns)
    for category, patterns in CATEGORY_PATTERNS.items()
}


def classify(text: str) -> list[str]:
    lower = text.lower()
    # Renderer discovery must not confuse unrelated networking/physics queues,
    # QoS probes or transport "deferred" diagnostics with graphics evidence.
    if lower.startswith((
        "networking:",
        "demonware ",
        "bd",
        "physics:",
        "audio:",
    )):
        return []
    return [
        category
        for category, patterns in COMPILED_PATTERNS.items()
        if any(pattern.search(text) for pattern in patterns)
    ]


def analyze(
    executable: Path,
    *,
    min_length: int = 5,
    max_length: int = 192,
    limit_per_category: int = 256,
) -> dict:
    raw = executable.read_bytes()
    strings = printable_ascii_strings(raw, min_length=min_length)

    candidates: dict[str, dict] = {}
    category_counts = defaultdict(int)
    for row in strings:
        text = row["text"]
        if len(text) > max_length:
            continue
        categories = classify(text)
        if not categories:
            continue
        if all(category_counts[category] >= limit_per_category for category in categories):
            continue
        selected = []
        for category in categories:
            if category_counts[category] >= limit_per_category:
                continue
            category_counts[category] += 1
            selected.append(category)
        if not selected:
            continue
        item = candidates.setdefault(
            text,
            {
                "text": text,
                "occurrences": [],
                "categories": set(),
            },
        )
        item["categories"].update(selected)
        item["occurrences"].append(
            {
                "file_offset": row["file_offset"],
                "length": row["length"],
            }
        )

    terms = sorted(candidates)
    xrefs = rip_probe(executable, terms) if terms else {
        "schema": "d1_elf_rip_string_xrefs/v1",
        "terms": {},
    }

    rows = []
    xref_count = 0
    referenced_string_count = 0
    for text in terms:
        xref_rows = xrefs.get("terms", {}).get(text, [])
        candidate_xrefs = [
            xref
            for occurrence in xref_rows
            for xref in occurrence.get("candidate_lea_xrefs", [])
        ]
        if candidate_xrefs:
            referenced_string_count += 1
            xref_count += len(candidate_xrefs)
        rows.append(
            {
                "text": text,
                "categories": sorted(candidates[text]["categories"]),
                "printable_occurrences": candidates[text]["occurrences"],
                "rip_occurrences": xref_rows,
                "candidate_lea_xrefs": candidate_xrefs,
                "candidate_lea_xref_count": len(candidate_xrefs),
                "status": (
                    "BYTE_PATTERN_XREF_CANDIDATE_REQUIRES_DISASSEMBLY"
                    if candidate_xrefs
                    else "STRING_PRESENT_NO_RIP_LEA_CANDIDATE"
                ),
            }
        )

    rows.sort(
        key=lambda row: (
            -row["candidate_lea_xref_count"],
            -len(row["categories"]),
            row["text"].lower(),
        )
    )

    return {
        "schema": "d1_executable_renderer_strings/v1",
        "executable_sha256": hashlib.sha256(raw).hexdigest(),
        "file_size": len(raw),
        "profile": {
            "categories": {
                key: list(value) for key, value in CATEGORY_PATTERNS.items()
            },
            "min_length": min_length,
            "max_length": max_length,
            "limit_per_category": limit_per_category,
            "policy": (
                "String/category matches are discovery anchors only. RIP-relative "
                "byte-pattern xrefs require disassembly validation before any "
                "function or renderer semantic is promoted."
            ),
        },
        "counts": {
            "printable_strings_scanned": len(strings),
            "selected_unique_strings": len(rows),
            "selected_strings_with_candidate_xrefs": referenced_string_count,
            "candidate_lea_xrefs": xref_count,
            "selected_by_category": dict(sorted(category_counts.items())),
        },
        "strings": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("executable", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument("--min-length", type=int, default=5)
    parser.add_argument("--max-length", type=int, default=192)
    parser.add_argument("--limit-per-category", type=int, default=256)
    args = parser.parse_args()

    report = analyze(
        args.executable,
        min_length=args.min_length,
        max_length=args.max_length,
        limit_per_category=args.limit_per_category,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "D1_EXECUTABLE_RENDERER_STRING_FRONTIER",
                "sha256": report["executable_sha256"],
                **report["counts"],
                "output": str(args.output),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
