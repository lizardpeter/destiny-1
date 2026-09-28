#!/usr/bin/env python3
"""Recover exact executable data-table references to D1 renderer labels.

Some retail renderer/pass names are present in eboot.bin but have no direct
RIP-relative LEA from code. This probe searches mapped ELF bytes for exact
32/64-bit virtual-address references and signed rel32 references to selected
renderer labels, then groups nearby references into candidate metadata tables.

Every result is exact-build evidence only. A pointer hit does not by itself prove
table schema or execution order.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from collections import defaultdict
from pathlib import Path

from d1_executable_probe import (
    parse_elf64_header,
    parse_elf64_program_headers,
    printable_ascii_strings,
)


FIXED_FUNCTION_DATA_WINDOWS = (
    ("pipeline_state_tables", 0x15D16C0, 0xE00),
    ("depth_stencil_selector_remaps", 0x18DEC70, 0x400),
    ("depth_stencil_aux_table_pointer", 0x1A1F4C0, 0x20),
)

DEFAULT_LABELS = (
    "generate_gbuffer",
    "lighting apply",
    "light probe apply",
    "light_shaft_occlusion",
    "depth_prepass",
    "postprocess_transparent_stencil",
    "mask_sun_light",
    "depth_3d",
    "depth_ui",
    "deferred_lights_renderer",
    "chunked_lights_renderer",
    "gbuffer_albedo",
    "gbuffer_normals",
    "gbuffer_normals_16bit",
    "autoexposure",
    "final_combine_output_surface",
    "render_submit_lights_view_job",
)


def file_to_virtual(offset: int, segments: list[dict]) -> int | None:
    for segment in segments:
        base = int(segment["absolute_file_offset"])
        size = int(segment["file_size"])
        if base <= offset < base + size:
            return int(segment["virtual_address"], 16) + offset - base
    return None


def segment_for_file(offset: int, segments: list[dict]) -> dict | None:
    for segment in segments:
        base = int(segment["absolute_file_offset"])
        size = int(segment["file_size"])
        if base <= offset < base + size:
            return segment
    return None


def virtual_to_file(virtual_address: int, segments: list[dict]) -> int | None:
    for segment in segments:
        base_va = int(segment["virtual_address"], 16)
        size = int(segment["file_size"])
        if base_va <= virtual_address < base_va + size:
            return int(segment["absolute_file_offset"]) + virtual_address - base_va
    return None


def dump_exact_data_window(
    raw: bytes,
    segments: list[dict],
    name: str,
    virtual_address: int,
    size: int,
) -> dict:
    file_offset = virtual_to_file(virtual_address, segments)
    if file_offset is None:
        return {
            "name": name,
            "virtual_address": virtual_address,
            "virtual_address_hex": hex(virtual_address),
            "size": size,
            "status": "UNMAPPED_VIRTUAL_ADDRESS",
        }
    end = file_offset + size
    if end > len(raw):
        return {
            "name": name,
            "virtual_address": virtual_address,
            "virtual_address_hex": hex(virtual_address),
            "file_offset": file_offset,
            "size": size,
            "status": "WINDOW_EXCEEDS_FILE",
        }
    payload = raw[file_offset:end]
    return {
        "name": name,
        "virtual_address": virtual_address,
        "virtual_address_hex": hex(virtual_address),
        "file_offset": file_offset,
        "size": size,
        "sha256": hashlib.sha256(payload).hexdigest(),
        "hex": payload.hex(),
        "status": "EXACT_BUILD_DATA_WINDOW",
    }


def find_labels(raw: bytes, segments: list[dict], labels: tuple[str, ...]) -> dict[str, list[dict]]:
    wanted = set(labels)
    out = defaultdict(list)
    for row in printable_ascii_strings(raw, min_length=4):
        text = row["text"]
        if text not in wanted:
            continue
        va = file_to_virtual(row["file_offset"], segments)
        if va is None:
            continue
        out[text].append({
            "file_offset": row["file_offset"],
            "virtual_address": va,
            "length": row["length"],
        })
    return dict(out)


def mapped_ranges(segments: list[dict]) -> list[tuple[int, int, dict]]:
    out = []
    for segment in segments:
        size = int(segment["file_size"])
        if size <= 0:
            continue
        start = int(segment["absolute_file_offset"])
        out.append((start, start + size, segment))
    return out


def scan(
    executable: Path,
    labels: tuple[str, ...],
    *,
    cluster_distance: int = 0x200,
) -> dict:
    raw = executable.read_bytes()
    header = parse_elf64_header(raw)
    if header is None or not header.get("supported"):
        raise ValueError("expected supported ELF64 executable")
    segments = parse_elf64_program_headers(raw, header)
    label_rows = find_labels(raw, segments, labels)

    targets = defaultdict(list)
    for label, rows in label_rows.items():
        for row in rows:
            targets[row["virtual_address"]].append(label)

    hits = []
    ranges = mapped_ranges(segments)
    for start, end, segment in ranges:
        # Aligned absolute pointer forms.
        for file_offset in range((start + 7) & ~7, end - 7, 8):
            value = struct.unpack_from("<Q", raw, file_offset)[0]
            if value in targets:
                ref_va = file_to_virtual(file_offset, segments)
                for label in targets[value]:
                    hits.append({
                        "label": label,
                        "kind": "u64_absolute_va",
                        "reference_file_offset": file_offset,
                        "reference_virtual_address": ref_va,
                        "target_virtual_address": value,
                        "segment_index": segment["index"],
                        "segment_executable": segment["executable"],
                        "segment_writable": segment["writable"],
                    })

        # 32-bit absolute and rel32 forms. Restrict to 4-byte alignment for data
        # table discovery; code RIP xrefs are handled by the separate scanner.
        for file_offset in range((start + 3) & ~3, end - 3, 4):
            raw_u32 = struct.unpack_from("<I", raw, file_offset)[0]
            ref_va = file_to_virtual(file_offset, segments)
            if raw_u32 in targets:
                for label in targets[raw_u32]:
                    hits.append({
                        "label": label,
                        "kind": "u32_absolute_va",
                        "reference_file_offset": file_offset,
                        "reference_virtual_address": ref_va,
                        "target_virtual_address": raw_u32,
                        "segment_index": segment["index"],
                        "segment_executable": segment["executable"],
                        "segment_writable": segment["writable"],
                    })
            if ref_va is not None:
                rel = struct.unpack_from("<i", raw, file_offset)[0]
                rel_target = ref_va + 4 + rel
                if rel_target in targets:
                    for label in targets[rel_target]:
                        hits.append({
                            "label": label,
                            "kind": "aligned_rel32",
                            "reference_file_offset": file_offset,
                            "reference_virtual_address": ref_va,
                            "target_virtual_address": rel_target,
                            "segment_index": segment["index"],
                            "segment_executable": segment["executable"],
                            "segment_writable": segment["writable"],
                        })

    hits.sort(key=lambda row: (row["reference_file_offset"], row["label"], row["kind"]))

    clusters = []
    if hits:
        current = [hits[0]]
        for hit in hits[1:]:
            if hit["reference_file_offset"] - current[-1]["reference_file_offset"] <= cluster_distance:
                current.append(hit)
            else:
                clusters.append(current)
                current = [hit]
        clusters.append(current)

    cluster_rows = []
    for index, cluster in enumerate(clusters):
        labels_here = sorted({row["label"] for row in cluster})
        cluster_rows.append({
            "cluster_index": index,
            "reference_file_offset_min": min(row["reference_file_offset"] for row in cluster),
            "reference_file_offset_max": max(row["reference_file_offset"] for row in cluster),
            "reference_virtual_address_min": min(
                row["reference_virtual_address"] for row in cluster
                if row["reference_virtual_address"] is not None
            ),
            "reference_virtual_address_max": max(
                row["reference_virtual_address"] for row in cluster
                if row["reference_virtual_address"] is not None
            ),
            "labels": labels_here,
            "unique_label_count": len(labels_here),
            "hit_count": len(cluster),
            "hits": cluster,
            "segment_type_names": sorted({
                next(
                    (
                        segment["type_name"]
                        for segment in segments
                        if segment["index"] == row["segment_index"]
                    ),
                    "UNKNOWN",
                )
                for row in cluster
            }),
            "status": (
                "SCE_DYNLIBDATA_POINTER_CLUSTER_NOT_RUNTIME_RENDER_TABLE"
                if all(
                    next(
                        (
                            segment["type"]
                            for segment in segments
                            if segment["index"] == row["segment_index"]
                        ),
                        None,
                    ) == 0x61000000
                    for row in cluster
                )
                else (
                    "MULTI_LABEL_RENDER_METADATA_TABLE_CANDIDATE"
                    if len(labels_here) >= 2
                    else "SINGLE_LABEL_POINTER_CANDIDATE"
                )
            ),
        })

    fixed_function_data_windows = [
        dump_exact_data_window(raw, segments, name, virtual_address, size)
        for name, virtual_address, size in FIXED_FUNCTION_DATA_WINDOWS
    ]

    per_label = {}
    for label in labels:
        rows = [row for row in hits if row["label"] == label]
        per_label[label] = {
            "string_occurrences": label_rows.get(label, []),
            "pointer_hit_count": len(rows),
            "pointer_hits": rows,
        }

    return {
        "schema": "d1_executable_renderer_label_tables/v1",
        "executable_sha256": hashlib.sha256(raw).hexdigest(),
        "file_size": len(raw),
        "labels": per_label,
        "counts": {
            "requested_label_count": len(labels),
            "present_label_count": sum(bool(v["string_occurrences"]) for v in per_label.values()),
            "pointer_hit_count": len(hits),
            "cluster_count": len(cluster_rows),
            "multi_label_cluster_count": sum(
                row["unique_label_count"] >= 2 for row in cluster_rows
            ),
        },
        "clusters": cluster_rows,
        "fixed_function_data_windows": fixed_function_data_windows,
        "policy": (
            "Exact pointer/rel32 matches and physical clustering are discovery "
            "evidence. PT_SCE_DYNLIBDATA hits are loader/dynamic-link metadata "
            "and are explicitly not promoted as Bungie runtime render tables. "
            "Table schema, ownership, pass order and runtime semantics require "
            "mapped runtime data plus disassembly/decompiler proof."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("executable", type=Path)
    parser.add_argument("--label", action="append", dest="labels")
    parser.add_argument("--cluster-distance", type=lambda x: int(x, 0), default=0x200)
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args()
    labels = tuple(args.labels) if args.labels else DEFAULT_LABELS
    report = scan(
        args.executable,
        labels,
        cluster_distance=args.cluster_distance,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "D1_EXECUTABLE_RENDERER_LABEL_TABLE_FRONTIER",
        **report["counts"],
        "output": str(args.output),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
