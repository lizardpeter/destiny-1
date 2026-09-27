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
        r"\brender(?:er|ing)?\b",
        r"\bgraphics\b",
        r"\bframe(?:buffer)?\b",
        r"\bback\s*buffer\b",
        r"\bswap\s*chain\b",
        r"\bpresent\b",
        r"\brender\s*target\b",
        r"\bmrt\d*\b",
        r"\bgbuffer\b",
        r"\bg[-_ ]?buffer\b",
        r"\bresolve\b",
    ),
    "shader_material": (
        r"\bshader\b",
        r"\bvertex\s*shader\b",
        r"\bpixel\s*shader\b",
        r"\bmaterial\b",
        r"\btechnique\b",
        r"\btexture\b",
        r"\bsampler\b",
        r"\bconstant\s*buffer\b",
        r"\bresource\s*table\b",
        r"\bdescriptor\b",
    ),
    "fixed_function": (
        r"\bblend\b",
        r"\bdepth\b",
        r"\bstencil\b",
        r"\braster\b",
        r"\bcull\b",
        r"\bviewport\b",
        r"\bscissor\b",
        r"\bcolor\s*write\b",
    ),
    "draw_submit": (
        r"\bdraw\b",
        r"\bdispatch\b",
        r"\bsubmit\b",
        r"\bcommand\s*buffer\b",
        r"\bcommand\s*list\b",
        r"\bgpu\b",
        r"\bqueue\b",
        r"\bfence\b",
    ),
    "lighting": (
        r"\blight(?:ing)?\b",
        r"\bshadow\b",
        r"\breflection\b",
        r"\bprobe\b",
        r"\birradiance\b",
        r"\bambient\b",
        r"\bdeferred\b",
        r"\bexposure\b",
        r"\bhdr\b",
    ),
    "environment": (
        r"\bsky\b",
        r"\bfog\b",
        r"\batmosphere\b",
        r"\bcloud\b",
        r"\bweather\b",
    ),
    "post": (
        r"\bpost[-_ ]?process(?:ing)?\b",
        r"\bbloom\b",
        r"\btonemap(?:ping)?\b",
        r"\bcolor\s*grade\b",
        r"\btaa\b",
        r"\bfxaa\b",
        r"\bdof\b",
        r"\bdepth\s*of\s*field\b",
        r"\bmotion\s*blur\b",
    ),
}

COMPILED_PATTERNS = {
    category: tuple(re.compile(pattern, re.IGNORECASE) for pattern in patterns)
    for category, patterns in CATEGORY_PATTERNS.items()
}


def classify(text: str) -> list[str]:
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
