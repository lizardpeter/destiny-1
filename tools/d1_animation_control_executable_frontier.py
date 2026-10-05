#!/usr/bin/env python3
"""Find exact CUSA00219 01.33 executable frontiers for D1 animation controls.

The primary target is serialized class 0x80802C0E. The probe does not assume a
class registry schema. It finds exact class-hash bytes, inspects nearby mapped
words for executable pointers, disassembles those code candidates, and scans
all executable segments for:
  * direct immediates equal to the target class hashes;
  * RIP-relative references near a target-hash occurrence;
  * direct calls to code pointers recovered beside those occurrences.

Candidate code is ranked by accesses shaped like the known serialized
80802C0E fields (+0x08/+0x10 animation list, +0x14 scalar, +0x18 selection,
+0x68/+0x70 selector table). Those offsets are discovery signals only; a match
does not prove that the instruction's base register points at an animation
control.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from collections import defaultdict
from pathlib import Path

from capstone import Cs, CS_ARCH_X86, CS_MODE_64
from capstone.x86 import X86_OP_IMM, X86_OP_MEM, X86_REG_RIP

from d1_executable_probe import parse_elf64_header, parse_elf64_program_headers

TARGET_CLASSES = {
    0x80802C0E: "animation_control",
    0x808005A1: "animation_clip",
    0x8080222A: "animation_wrapper",
}
CONTROL_FIELD_OFFSETS = {
    0x08: "animation_count",
    0x10: "animation_array_relptr",
    0x14: "selector_scalar",
    0x18: "packed_selection",
    0x68: "selector_count",
    0x70: "selector_array_relptr",
}
NEAR_CLASS_RADIUS = 0x100
POINTER_WINDOW = 0x100


def file_to_va(offset: int, segments: list[dict]) -> int | None:
    for segment in segments:
        base = int(segment["absolute_file_offset"])
        size = int(segment["file_size"])
        if base <= offset < base + size:
            return int(segment["virtual_address"], 16) + offset - base
    return None


def va_to_file(va: int, segments: list[dict]) -> int | None:
    for segment in segments:
        base_va = int(segment["virtual_address"], 16)
        size = int(segment["file_size"])
        if base_va <= va < base_va + size:
            return int(segment["absolute_file_offset"]) + va - base_va
    return None


def segment_for_file(offset: int, segments: list[dict]) -> dict | None:
    for segment in segments:
        base = int(segment["absolute_file_offset"])
        size = int(segment["file_size"])
        if base <= offset < base + size:
            return segment
    return None


def executable_va(va: int, segments: list[dict]) -> bool:
    for segment in segments:
        if not segment.get("executable"):
            continue
        base = int(segment["virtual_address"], 16)
        size = int(segment["file_size"])
        if base <= va < base + size:
            return True
    return False


def find_hash_occurrences(raw: bytes, segments: list[dict]) -> list[dict]:
    rows = []
    for value, label in TARGET_CLASSES.items():
        needle = struct.pack("<I", value)
        cursor = 0
        while True:
            pos = raw.find(needle, cursor)
            if pos < 0:
                break
            cursor = pos + 1
            segment = segment_for_file(pos, segments)
            va = file_to_va(pos, segments)
            rows.append({
                "class_hash": value,
                "class_hash_hex": f"{value:08X}",
                "label": label,
                "file_offset": pos,
                "virtual_address": va,
                "virtual_address_hex": hex(va) if va is not None else None,
                "segment_index": segment.get("index") if segment else None,
                "segment_type": segment.get("type_name") if segment else None,
                "segment_executable": bool(segment and segment.get("executable")),
                "segment_writable": bool(segment and segment.get("writable")),
            })
    rows.sort(key=lambda x: (x["class_hash"], x["file_offset"]))
    return rows


def nearby_code_pointers(raw: bytes, segments: list[dict], occurrences: list[dict]) -> list[dict]:
    by_pointer: dict[int, dict] = {}
    for occ in occurrences:
        center = occ["file_offset"]
        start = max(0, center - POINTER_WINDOW)
        end = min(len(raw), center + POINTER_WINDOW + 4)

        # 64-bit mapped pointers.
        for pos in range((start + 7) & ~7, max((start + 7) & ~7, end - 7), 8):
            value = struct.unpack_from("<Q", raw, pos)[0]
            if not executable_va(value, segments):
                continue
            row = by_pointer.setdefault(value, {
                "code_va": value,
                "code_va_hex": hex(value),
                "sources": [],
            })
            row["sources"].append({
                "kind": "u64_executable_pointer_near_class",
                "pointer_file_offset": pos,
                "pointer_va": file_to_va(pos, segments),
                "relative_to_class_bytes": pos - center,
                "class_hash_hex": occ["class_hash_hex"],
                "class_label": occ["label"],
                "class_occurrence_va": occ["virtual_address"],
            })

        # Some retail tables retain 32-bit image-relative/low-VA code pointers.
        for pos in range((start + 3) & ~3, max((start + 3) & ~3, end - 3), 4):
            value = struct.unpack_from("<I", raw, pos)[0]
            if not executable_va(value, segments):
                continue
            row = by_pointer.setdefault(value, {
                "code_va": value,
                "code_va_hex": hex(value),
                "sources": [],
            })
            row["sources"].append({
                "kind": "u32_executable_pointer_near_class",
                "pointer_file_offset": pos,
                "pointer_va": file_to_va(pos, segments),
                "relative_to_class_bytes": pos - center,
                "class_hash_hex": occ["class_hash_hex"],
                "class_label": occ["label"],
                "class_occurrence_va": occ["virtual_address"],
            })
    return sorted(by_pointer.values(), key=lambda x: x["code_va"])


def disassemble_candidate(
    raw: bytes,
    segments: list[dict],
    code_va: int,
    *,
    size: int = 0x600,
    max_instructions: int = 320,
) -> dict:
    file_offset = va_to_file(code_va, segments)
    if file_offset is None:
        return {"code_va": code_va, "status": "UNMAPPED", "instructions": []}
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    md.detail = True
    data = raw[file_offset:min(len(raw), file_offset + size)]
    rows = []
    field_hits = []
    class_immediates = []
    calls = []
    jumps = []
    score = 0
    for insn in md.disasm(data, code_va):
        ops = []
        for op in insn.operands:
            if op.type == X86_OP_IMM:
                value = int(op.imm) & 0xFFFFFFFFFFFFFFFF
                ops.append({"type": "imm", "value": value, "hex": hex(value)})
                if value in TARGET_CLASSES:
                    class_immediates.append({
                        "instruction_va": int(insn.address),
                        "class_hash_hex": f"{value:08X}",
                        "label": TARGET_CLASSES[value],
                    })
                    score += 12 if value == 0x80802C0E else 4
            elif op.type == X86_OP_MEM:
                disp = int(op.mem.disp)
                item = {
                    "type": "mem",
                    "base": int(op.mem.base),
                    "index": int(op.mem.index),
                    "scale": int(op.mem.scale),
                    "disp": disp,
                }
                if disp in CONTROL_FIELD_OFFSETS:
                    field_hits.append({
                        "instruction_va": int(insn.address),
                        "instruction_va_hex": hex(int(insn.address)),
                        "field_offset": disp,
                        "field_offset_hex": hex(disp),
                        "field_name": CONTROL_FIELD_OFFSETS[disp],
                        "mnemonic": insn.mnemonic,
                        "op_str": insn.op_str,
                    })
                    score += 5 if disp in (0x14, 0x18) else 2
                if op.mem.base == X86_REG_RIP:
                    item["rip_target"] = int(insn.address + insn.size + disp)
                ops.append(item)
            else:
                ops.append({"type": int(op.type)})
        if insn.mnemonic == "call" and insn.operands and insn.operands[0].type == X86_OP_IMM:
            calls.append({
                "instruction_va": int(insn.address),
                "target_va": int(insn.operands[0].imm) & 0xFFFFFFFFFFFFFFFF,
            })
        if insn.mnemonic.startswith("j") and insn.operands and insn.operands[0].type == X86_OP_IMM:
            jumps.append({
                "instruction_va": int(insn.address),
                "target_va": int(insn.operands[0].imm) & 0xFFFFFFFFFFFFFFFF,
                "mnemonic": insn.mnemonic,
            })
        rows.append({
            "address": int(insn.address),
            "address_hex": hex(int(insn.address)),
            "mnemonic": insn.mnemonic,
            "op_str": insn.op_str,
            "size": int(insn.size),
            "operands": ops,
        })
        if len(rows) >= max_instructions:
            break
        if insn.mnemonic == "ret" and len(rows) >= 8:
            break
    return {
        "code_va": code_va,
        "code_va_hex": hex(code_va),
        "status": "DISASSEMBLED" if rows else "NO_INSTRUCTIONS",
        "score": score,
        "instruction_count": len(rows),
        "field_hits": field_hits,
        "class_immediates": class_immediates,
        "direct_calls": calls,
        "direct_jumps": jumps,
        "instructions": rows,
    }



def scan_structural_control_fields(
    raw: bytes,
    segments: list[dict],
    *,
    radius: int = 0x180,
    top: int = 240,
) -> dict:
    """Rank code neighborhoods that structurally resemble 80802C0E consumers.

    This is intentionally hash-independent. The strongest signal is one base
    register used for selector-record +0x14 (float duration) and +0x18 (packed
    selection) accesses in one tight neighborhood. Control-header +0x68/+0x70
    and animation-list +0x08/+0x10 accesses add supporting weight.
    """
    import bisect

    md = Cs(CS_ARCH_X86, CS_MODE_64)
    md.detail = True
    md.skipdata = True

    hits = []
    decoded = 0
    for segment in segments:
        if not segment.get("executable") or int(segment.get("file_size", 0)) <= 0:
            continue
        file_offset = int(segment["absolute_file_offset"])
        size = int(segment["file_size"])
        va = int(segment["virtual_address"], 16)
        data = raw[file_offset:file_offset + size]
        for insn in md.disasm(data, va):
            if insn.id == 0:
                continue
            decoded += 1
            for operand_index, op in enumerate(insn.operands):
                if op.type != X86_OP_MEM:
                    continue
                disp = int(op.mem.disp)
                if disp not in CONTROL_FIELD_OFFSETS:
                    continue
                base_name = md.reg_name(op.mem.base) if op.mem.base else ""
                index_name = md.reg_name(op.mem.index) if op.mem.index else ""
                hits.append({
                    "address": int(insn.address),
                    "address_hex": hex(int(insn.address)),
                    "mnemonic": insn.mnemonic,
                    "op_str": insn.op_str,
                    "operand_index": operand_index,
                    "field_offset": disp,
                    "field_offset_hex": hex(disp),
                    "field_name": CONTROL_FIELD_OFFSETS[disp],
                    "base_register": base_name,
                    "index_register": index_name,
                    "scale": int(op.mem.scale),
                })

    hits.sort(key=lambda row: row["address"])
    addresses = [row["address"] for row in hits]
    candidates = {}
    float_mnemonics = {
        "movss", "movaps", "movups", "comiss", "ucomiss", "addss", "subss",
        "mulss", "divss", "minss", "maxss", "cvtss2sd", "cvttss2si",
    }

    for anchor_hit in hits:
        if anchor_hit["field_offset"] != 0x14:
            continue
        center = anchor_hit["address"]
        lo = bisect.bisect_left(addresses, center - radius)
        hi = bisect.bisect_right(addresses, center + radius)
        nearby = hits[lo:hi]
        base = anchor_hit["base_register"]

        same_base = [
            row for row in nearby
            if base and row["base_register"] == base
        ]
        same_offsets = {row["field_offset"] for row in same_base}
        all_offsets = {row["field_offset"] for row in nearby}

        score = 0
        reasons = []
        if 0x18 in same_offsets:
            score += 40
            reasons.append("same-base +0x14/+0x18 selector-record pair")
        if anchor_hit["mnemonic"] in float_mnemonics:
            score += 18
            reasons.append("+0x14 consumed by scalar/float-shaped instruction")
        if {0x68, 0x70}.issubset(all_offsets):
            score += 18
            reasons.append("nearby +0x68/+0x70 selector-table header pair")
        elif 0x68 in all_offsets or 0x70 in all_offsets:
            score += 7
            reasons.append("nearby selector-table header field")
        if {0x08, 0x10}.issubset(all_offsets):
            score += 10
            reasons.append("nearby +0x08/+0x10 animation-list header pair")
        elif 0x08 in all_offsets or 0x10 in all_offsets:
            score += 4
            reasons.append("nearby animation-list header field")
        score += min(len(all_offsets), len(CONTROL_FIELD_OFFSETS)) * 2

        # Reward +0x18 immediately adjacent in code even if compiler register
        # allocation changed the base register between the two accesses.
        nearest_18 = min(
            (abs(row["address"] - center) for row in nearby if row["field_offset"] == 0x18),
            default=None,
        )
        if nearest_18 is not None:
            if nearest_18 <= 0x20:
                score += 20
                reasons.append("+0x18 access within 0x20 bytes")
            elif nearest_18 <= 0x60:
                score += 10
                reasons.append("+0x18 access within 0x60 bytes")

        # Deduplicate multiple +0x14 instructions from the same tight code
        # neighborhood while retaining the strongest representative.
        bucket = center >> 7
        row = {
            "anchor_va": center,
            "anchor_va_hex": hex(center),
            "score": score,
            "reasons": reasons,
            "anchor": anchor_hit,
            "same_base_offsets": sorted(same_offsets),
            "all_nearby_offsets": sorted(all_offsets),
            "nearest_18_distance": nearest_18,
            "nearby_field_hits": nearby[:120],
        }
        previous = candidates.get(bucket)
        if previous is None or (row["score"], -row["anchor_va"]) > (
            previous["score"], -previous["anchor_va"]
        ):
            candidates[bucket] = row

    ranked = sorted(
        candidates.values(),
        key=lambda row: (-row["score"], row["anchor_va"]),
    )[:top]

    return {
        "decoded_instruction_count": decoded,
        "field_access_hit_count": len(hits),
        "duration_field_access_count": sum(row["field_offset"] == 0x14 for row in hits),
        "selection_field_access_count": sum(row["field_offset"] == 0x18 for row in hits),
        "candidate_count": len(candidates),
        "ranked_candidates": ranked,
        "policy": (
            "These are hash-independent structural candidates. Matching raw "
            "displacements is not type proof. Promotion requires a candidate "
            "to converge with call/data flow, exact object provenance, or "
            "decompiler evidence."
        ),
    }


def scan_executable_xrefs(
    raw: bytes,
    segments: list[dict],
    occurrences: list[dict],
    pointer_targets: set[int],
) -> dict:
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    md.detail = True
    md.skipdata = True

    occurrence_vas = [
        (int(row["virtual_address"]), row)
        for row in occurrences
        if row["virtual_address"] is not None
    ]
    class_immediate_hits = []
    near_class_rip_hits = []
    calls: dict[int, list[dict]] = defaultdict(list)
    decoded = 0

    for segment in segments:
        if not segment.get("executable") or int(segment.get("file_size", 0)) <= 0:
            continue
        file_offset = int(segment["absolute_file_offset"])
        size = int(segment["file_size"])
        va = int(segment["virtual_address"], 16)
        data = raw[file_offset:file_offset + size]
        for insn in md.disasm(data, va):
            if insn.id == 0:
                continue
            decoded += 1
            for op in insn.operands:
                if op.type == X86_OP_IMM:
                    value = int(op.imm) & 0xFFFFFFFFFFFFFFFF
                    if value in TARGET_CLASSES:
                        class_immediate_hits.append({
                            "instruction_va": int(insn.address),
                            "instruction_va_hex": hex(int(insn.address)),
                            "class_hash_hex": f"{value:08X}",
                            "label": TARGET_CLASSES[value],
                            "mnemonic": insn.mnemonic,
                            "op_str": insn.op_str,
                        })
                elif op.type == X86_OP_MEM and op.mem.base == X86_REG_RIP:
                    target = int(insn.address + insn.size + int(op.mem.disp))
                    for occ_va, occ in occurrence_vas:
                        delta = target - occ_va
                        if abs(delta) <= NEAR_CLASS_RADIUS:
                            near_class_rip_hits.append({
                                "instruction_va": int(insn.address),
                                "instruction_va_hex": hex(int(insn.address)),
                                "rip_target_va": target,
                                "rip_target_va_hex": hex(target),
                                "relative_to_class": delta,
                                "class_hash_hex": occ["class_hash_hex"],
                                "class_label": occ["label"],
                                "class_occurrence_va": occ_va,
                                "mnemonic": insn.mnemonic,
                                "op_str": insn.op_str,
                            })
            if insn.mnemonic == "call" and insn.operands and insn.operands[0].type == X86_OP_IMM:
                target = int(insn.operands[0].imm) & 0xFFFFFFFFFFFFFFFF
                if target in pointer_targets:
                    calls[target].append({
                        "callsite_va": int(insn.address),
                        "callsite_va_hex": hex(int(insn.address)),
                    })

    return {
        "decoded_instruction_count": decoded,
        "class_immediate_hits": class_immediate_hits,
        "near_class_rip_hits": near_class_rip_hits,
        "direct_calls_to_nearby_code_pointers": [
            {
                "target_va": target,
                "target_va_hex": hex(target),
                "xref_count": len(rows),
                "xrefs": sorted(rows, key=lambda x: x["callsite_va"]),
            }
            for target, rows in sorted(calls.items())
        ],
    }


def analyze(executable: Path) -> dict:
    raw = executable.read_bytes()
    header = parse_elf64_header(raw)
    if header is None or not header.get("supported"):
        raise ValueError("expected supported ELF64 executable")
    segments = parse_elf64_program_headers(raw, header)
    occurrences = find_hash_occurrences(raw, segments)
    nearby = nearby_code_pointers(raw, segments, occurrences)
    pointer_targets = {row["code_va"] for row in nearby}
    xrefs = scan_executable_xrefs(raw, segments, occurrences, pointer_targets)
    structural = scan_structural_control_fields(raw, segments)

    decoded = []
    for row in nearby:
        window = disassemble_candidate(raw, segments, row["code_va"])
        window["sources"] = row["sources"]
        # A nearby pointer is useful discovery evidence itself. Prioritize
        # pointers near the actual animation-control class over sibling classes.
        source_score = sum(
            8 if source["class_hash_hex"] == "80802C0E" else 2
            for source in row["sources"]
        )
        window["score"] += source_score
        decoded.append(window)

    # Include bounded neighborhoods around exact code-side class immediates and
    # RIP xrefs even when no descriptor-adjacent code pointer was recovered.
    extra_starts = {
        max(0, hit["instruction_va"] - 0x80)
        for hit in xrefs["class_immediate_hits"]
        if hit["class_hash_hex"] == "80802C0E"
    }
    extra_starts.update(
        max(0, hit["instruction_va"] - 0x80)
        for hit in xrefs["near_class_rip_hits"]
        if hit["class_hash_hex"] == "80802C0E"
    )
    existing = {row["code_va"] for row in decoded}
    for start in sorted(extra_starts - existing):
        window = disassemble_candidate(raw, segments, start, size=0x300, max_instructions=180)
        window["sources"] = [{"kind": "bounded_context_around_animation_control_xref"}]
        window["score"] += 10
        decoded.append(window)

    decoded.sort(key=lambda row: (-row["score"], row["code_va"]))
    control_occurrences = [x for x in occurrences if x["class_hash"] == 0x80802C0E]
    return {
        "schema": "d1_animation_control_executable_frontier/v1",
        "executable_sha256": hashlib.sha256(raw).hexdigest(),
        "file_size": len(raw),
        "target_classes": [
            {"hash": value, "hash_hex": f"{value:08X}", "label": label}
            for value, label in TARGET_CLASSES.items()
        ],
        "known_serialized_control_offsets": {
            hex(offset): name for offset, name in CONTROL_FIELD_OFFSETS.items()
        },
        "counts": {
            "class_hash_occurrence_count": len(occurrences),
            "animation_control_occurrence_count": len(control_occurrences),
            "nearby_executable_pointer_count": len(nearby),
            "code_side_class_immediate_count": len(xrefs["class_immediate_hits"]),
            "code_side_near_class_rip_count": len(xrefs["near_class_rip_hits"]),
            "ranked_code_candidate_count": len(decoded),
            "structural_field_access_hit_count": structural["field_access_hit_count"],
            "structural_duration_field_access_count": structural["duration_field_access_count"],
            "structural_selection_field_access_count": structural["selection_field_access_count"],
            "structural_candidate_count": structural["candidate_count"],
        },
        "class_hash_occurrences": occurrences,
        "executable_xrefs": xrefs,
        "structural_control_field_frontier": structural,
        "ranked_code_candidates": decoded,
        "policy": (
            "This is exact-build discovery evidence for CUSA00219 01.33. "
            "A class-hash occurrence, nearby executable pointer, RIP reference, "
            "matching displacement, or call edge does not by itself prove the "
            "80802C0E playback consumer. Semantic promotion requires converging "
            "control/data flow or decompiler evidence."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("executable", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args()
    report = analyze(args.executable)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "D1_ANIMATION_CONTROL_EXECUTABLE_FRONTIER",
        **report["counts"],
        "top_candidates": [
            {
                "code_va": row["code_va_hex"],
                "score": row["score"],
                "field_hits": len(row["field_hits"]),
                "calls": len(row["direct_calls"]),
            }
            for row in report["ranked_code_candidates"][:20]
        ],
        "top_structural_candidates": [
            {
                "anchor_va": row["anchor_va_hex"],
                "score": row["score"],
                "reasons": row["reasons"],
                "same_base_offsets": [hex(x) for x in row["same_base_offsets"]],
                "all_nearby_offsets": [hex(x) for x in row["all_nearby_offsets"]],
            }
            for row in report["structural_control_field_frontier"]["ranked_candidates"][:40]
        ],
        "output": str(args.output),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
