#!/usr/bin/env python3
"""Recover exact D1 PS4 terrain renderer runtime ownership from the retail eboot.

This probe joins:
  * authored terrain renderer labels in the exact executable,
  * mapped absolute/relative label-pointer tables,
  * x86-64 RIP-relative code references into those table neighborhoods,
  * the existing exact-build Ghidra function/call graph.

It is deliberately conservative. A nearby immediate 14/0xE0/0x1C0 is reported as
an observation only; it is not promoted as the terrain T14 producer without a
closed dataflow from the STerrain dyemap to the shader resource table.
"""
from __future__ import annotations

import argparse
import bisect
import gzip
import hashlib
import json
import struct
from pathlib import Path

from capstone import Cs, CS_ARCH_X86, CS_MODE_64
from capstone.x86 import X86_OP_IMM, X86_OP_MEM, X86_REG_RIP

from d1_executable_probe import parse_elf64_header, parse_elf64_program_headers
from d1_executable_renderer_label_tables import scan as scan_label_tables

LABELS = (
    "terrain_feature_renderer",
    "editor_terrain_tile_renderer",
    "?chunked_terrain",
    "static_objects_renderer",
    "dynamic_objects_renderer",
    "chunked_instance_renderer",
    "rigid_objects_renderer",
    "skinned_objects_renderer",
    "speedtree feature renderer",
)

INTERESTING_IMMEDIATES = {0xE, 0xE0, 0x1C0, 14, 224, 448}

# Sony/Orbis dynamic table tags.  DT_SCE_* table addresses are file offsets
# relative to PT_SCE_DYNLIBDATA, not runtime virtual addresses.
DT_NULL = 0
DT_SCE_JMPREL = 0x61000029
DT_SCE_PLTRELSZ = 0x6100002D
DT_SCE_RELA = 0x6100002F
DT_SCE_RELASZ = 0x61000031
DT_SCE_RELAENT = 0x61000033
DT_SCE_STRTAB = 0x61000035
DT_SCE_STRSZ = 0x61000037
DT_SCE_SYMTAB = 0x61000039
DT_SCE_SYMENT = 0x6100003B
DT_SCE_SYMTABSZ = 0x6100003F

STT_NAMES = {
    0: "NOTYPE",
    1: "OBJECT",
    2: "FUNC",
    3: "SECTION",
    4: "FILE",
}
STB_NAMES = {0: "LOCAL", 1: "GLOBAL", 2: "WEAK"}


def _segment(segments: list[dict], p_type: int) -> dict | None:
    return next((row for row in segments if int(row["type"]) == p_type), None)


def _cstr(table: bytes, offset: int) -> str:
    if offset < 0 or offset >= len(table):
        return ""
    end = table.find(b"\0", offset)
    if end < 0:
        end = len(table)
    return table[offset:end].decode("utf-8", errors="replace")


def parse_orbis_dynlib(
    raw: bytes,
    segments: list[dict],
    interesting_addends: set[int] | None = None,
) -> dict:
    """Parse the exact Orbis dynsym/rela metadata without treating it as runtime data."""
    dynamic = _segment(segments, 2)  # PT_DYNAMIC
    dynlib = _segment(segments, 0x61000000)  # PT_SCE_DYNLIBDATA
    if dynamic is None or dynlib is None:
        return {
            "status": "MISSING_DYNAMIC_OR_DYNLIBDATA",
            "dynamic_present": dynamic is not None,
            "dynlib_present": dynlib is not None,
        }

    doff = int(dynamic["absolute_file_offset"])
    dsize = int(dynamic["file_size"])
    dend = min(len(raw), doff + dsize)
    tags: dict[int, list[int]] = {}
    entries = []
    for off in range(doff, dend - 15, 16):
        tag, value = struct.unpack_from("<QQ", raw, off)
        entries.append({"file_offset": off, "tag": tag, "tag_hex": hex(tag), "value": value, "value_hex": hex(value)})
        tags.setdefault(tag, []).append(value)
        if tag == DT_NULL:
            break

    def one(tag: int, default: int = 0) -> int:
        rows = tags.get(tag, [])
        return int(rows[-1]) if rows else default

    liboff = int(dynlib["absolute_file_offset"])
    libsize = int(dynlib["file_size"])

    str_rel = one(DT_SCE_STRTAB)
    str_size = one(DT_SCE_STRSZ)
    sym_rel = one(DT_SCE_SYMTAB)
    sym_size = one(DT_SCE_SYMTABSZ)
    sym_ent = one(DT_SCE_SYMENT, 0x18) or 0x18

    def dyn_slice(relative: int, size: int, label: str) -> bytes:
        if relative < 0 or size < 0 or relative + size > libsize:
            raise ValueError(
                f"{label} relative span 0x{relative:X}+0x{size:X} exceeds PT_SCE_DYNLIBDATA 0x{libsize:X}"
            )
        start = liboff + relative
        end = start + size
        if end > len(raw):
            raise ValueError(f"{label} file span exceeds executable")
        return raw[start:end]

    strtab = dyn_slice(str_rel, str_size, "DT_SCE_STRTAB") if str_size else b""
    symtab = dyn_slice(sym_rel, sym_size, "DT_SCE_SYMTAB") if sym_size else b""
    if sym_ent < 0x18:
        raise ValueError(f"DT_SCE_SYMENT 0x{sym_ent:X} is smaller than ELF64 symbol size")
    if sym_size % sym_ent:
        raise ValueError(f"DT_SCE_SYMTABSZ 0x{sym_size:X} not divisible by entry 0x{sym_ent:X}")

    symbols = []
    for index in range(sym_size // sym_ent):
        off = index * sym_ent
        st_name = struct.unpack_from("<I", symtab, off)[0]
        st_info = symtab[off + 4]
        st_other = symtab[off + 5]
        st_shndx = struct.unpack_from("<H", symtab, off + 6)[0]
        st_value = struct.unpack_from("<Q", symtab, off + 8)[0]
        st_size = struct.unpack_from("<Q", symtab, off + 0x10)[0]
        symbols.append({
            "index": index,
            "name_offset": st_name,
            "name": _cstr(strtab, st_name),
            "info": st_info,
            "bind": st_info >> 4,
            "bind_name": STB_NAMES.get(st_info >> 4, f"BIND_{st_info >> 4}"),
            "type": st_info & 0xF,
            "type_name": STT_NAMES.get(st_info & 0xF, f"TYPE_{st_info & 0xF}"),
            "other": st_other,
            "shndx": st_shndx,
            "value": st_value,
            "value_hex": hex(st_value),
            "size": st_size,
        })

    def parse_rela(rel_tag: int, size_tag: int, name: str) -> list[dict]:
        rel = one(rel_tag)
        size = one(size_tag)
        if not rel or not size:
            return []
        payload = dyn_slice(rel, size, name)
        ent = one(DT_SCE_RELAENT, 0x18) or 0x18
        if ent < 0x18 or size % ent:
            raise ValueError(f"{name} size/entry mismatch: 0x{size:X}/0x{ent:X}")
        out = []
        for index in range(size // ent):
            off = index * ent
            r_offset, r_info, r_addend = struct.unpack_from("<QQq", payload, off)
            sym_index = r_info >> 32
            r_type = r_info & 0xFFFFFFFF
            symbol = symbols[sym_index] if sym_index < len(symbols) else None
            out.append({
                "index": index,
                "offset": r_offset,
                "offset_hex": hex(r_offset),
                "info": r_info,
                "type": r_type,
                "symbol_index": sym_index,
                "symbol_name": symbol["name"] if symbol else None,
                "addend": r_addend,
                "addend_hex": hex(r_addend & 0xFFFFFFFFFFFFFFFF),
            })
        return out

    relas = parse_rela(DT_SCE_RELA, DT_SCE_RELASZ, "DT_SCE_RELA")
    jmprels = parse_rela(DT_SCE_JMPREL, DT_SCE_PLTRELSZ, "DT_SCE_JMPREL")
    terrain_symbols = [
        row for row in symbols
        if "terrain" in row["name"].lower()
        or row["name"] in LABELS
    ]
    terrain_indices = {row["index"] for row in terrain_symbols}
    terrain_relocations = [
        {**row, "table": table_name}
        for table_name, rows in (("rela", relas), ("jmprel", jmprels))
        for row in rows
        if row["symbol_index"] in terrain_indices
    ]
    interesting_addends = interesting_addends or set()
    addend_relocations = [
        {**row, "table": table_name}
        for table_name, rows in (("rela", relas), ("jmprel", jmprels))
        for row in rows
        if (row["addend"] & 0xFFFFFFFFFFFFFFFF) in interesting_addends
    ]

    # A terrain renderer-name relocation can be one field of a compact runtime
    # registration record. Preserve adjacent relocation entries so other pointer
    # fields in the same record can be identified without assuming the schema.
    addend_relocation_neighborhoods = []
    for anchor in addend_relocations:
        rows = relas if anchor["table"] == "rela" else jmprels
        lo = max(0, int(anchor["index"]) - 4)
        hi = min(len(rows), int(anchor["index"]) + 5)
        addend_relocation_neighborhoods.append({
            "anchor": anchor,
            "neighbors": [
                {
                    **row,
                    "table": anchor["table"],
                    "index_delta": int(row["index"]) - int(anchor["index"]),
                    "runtime_offset_delta": int(row["offset"]) - int(anchor["offset"]),
                }
                for row in rows[lo:hi]
            ],
        })

    return {
        "status": "ORBIS_DYNLIB_PARSED",
        "dynamic_segment": dynamic,
        "dynlib_segment": dynlib,
        "dynamic_entries": entries,
        "table_layout": {
            "strtab_relative": str_rel,
            "strtab_size": str_size,
            "symtab_relative": sym_rel,
            "symtab_size": sym_size,
            "symbol_entry_size": sym_ent,
            "symbol_count": len(symbols),
            "rela_count": len(relas),
            "jmprel_count": len(jmprels),
        },
        "terrain_symbols": terrain_symbols,
        "terrain_relocations": terrain_relocations,
        "interesting_addend_relocations": addend_relocations,
        "interesting_addend_relocation_neighborhoods": addend_relocation_neighborhoods,
        "proof_boundary": (
            "PT_SCE_DYNLIBDATA is loader metadata. Symbol values and relocations identify "
            "code/data ownership or import slots, but the metadata bytes themselves are not "
            "promoted as Bungie runtime renderer tables."
        ),
    }



def v2f(va: int, segments: list[dict]) -> int | None:
    for seg in segments:
        base = int(seg["virtual_address"], 16)
        size = int(seg["file_size"])
        if base <= va < base + size:
            return int(seg["absolute_file_offset"]) + va - base
    return None


def load_graph(path: Path) -> dict:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as fh:
        return json.load(fh)


def build_function_index(graph: dict):
    ranges = []
    by_entry = {}
    for fn in graph.get("functions", []):
        entry = int(fn["entry"], 16)
        by_entry[entry] = fn
        for row in fn.get("body_ranges", []):
            ranges.append((int(row["min"], 16), int(row["max"], 16) + 1, entry))
    ranges.sort()
    starts = [r[0] for r in ranges]
    return ranges, starts, by_entry


def owner_of(addr: int, ranges, starts, by_entry):
    i = bisect.bisect_right(starts, addr) - 1
    for j in range(max(0, i - 2), min(len(ranges), i + 3)):
        lo, hi, entry = ranges[j]
        if lo <= addr < hi:
            return by_entry.get(entry)
    return None


def function_callers(graph: dict) -> dict[int, list[int]]:
    callers: dict[int, list[int]] = {}
    for fn in graph.get("functions", []):
        src = int(fn["entry"], 16)
        for dst_s in fn.get("called_function_entries", []):
            dst = int(dst_s, 16)
            callers.setdefault(dst, []).append(src)
    return callers


def string_va_index(graph: dict) -> dict[int, str]:
    out = {}
    for row in graph.get("strings", []):
        try:
            out[int(row["address"], 16)] = row.get("text", "")
        except Exception:
            pass
    return out


def function_entry_index(graph: dict) -> dict[int, str]:
    return {int(row["entry"], 16): row["name"] for row in graph.get("functions", [])}


def data_window(raw: bytes, segments: list[dict], center_va: int, *,
                radius: int, function_entries: dict[int, str],
                string_vas: dict[int, str]) -> dict:
    start_va = max(0, center_va - radius)
    end_va = center_va + radius
    start_file = v2f(start_va, segments)
    end_file = v2f(end_va - 1, segments)
    if start_file is None or end_file is None:
        return {"center_va": center_va, "status": "UNMAPPED"}
    end_file += 1
    payload = raw[start_file:end_file]
    qwords = []
    for off in range(0, len(payload) - 7, 8):
        va = start_va + off
        value = struct.unpack_from("<Q", payload, off)[0]
        kind = None
        name = None
        if value in function_entries:
            kind = "exact_function_pointer"
            name = function_entries[value]
        elif value in string_vas:
            kind = "exact_string_pointer"
            name = string_vas[value]
        elif v2f(value, segments) is not None:
            kind = "mapped_pointer"
        if kind:
            qwords.append({
                "slot_va": va,
                "slot_va_hex": hex(va),
                "value": value,
                "value_hex": hex(value),
                "kind": kind,
                "name": name,
            })
    return {
        "center_va": center_va,
        "center_va_hex": hex(center_va),
        "start_va": start_va,
        "start_va_hex": hex(start_va),
        "end_va": end_va,
        "end_va_hex": hex(end_va),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "pointer_qwords": qwords,
        "hex": payload.hex(),
        "status": "EXACT_WINDOW",
    }


def executable_segments(segments: list[dict]) -> list[dict]:
    return [s for s in segments if s.get("executable") and int(s.get("file_size", 0)) > 0]


def scan_code_references(raw: bytes, segments: list[dict], target_vas: list[int],
                         ranges, starts, by_entry, *, radius: int) -> list[dict]:
    if not target_vas:
        return []
    lo_target = min(target_vas) - radius
    hi_target = max(target_vas) + radius
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    md.detail = True
    hits = []
    seen = set()
    for seg in executable_segments(segments):
        foff = int(seg["absolute_file_offset"])
        size = int(seg["file_size"])
        va0 = int(seg["virtual_address"], 16)
        blob = raw[foff:foff + size]
        for insn in md.disasm(blob, va0):
            refs = []
            for op in insn.operands:
                if op.type == X86_OP_MEM and op.mem.base == X86_REG_RIP:
                    target = insn.address + insn.size + op.mem.disp
                    if lo_target <= target <= hi_target:
                        refs.append(("rip_mem", target))
                elif op.type == X86_OP_IMM:
                    target = int(op.imm) & 0xFFFFFFFFFFFFFFFF
                    if lo_target <= target <= hi_target:
                        refs.append(("imm", target))
            for kind, target in refs:
                nearest = min(target_vas, key=lambda x: abs(x - target))
                if abs(nearest - target) > radius:
                    continue
                key = (insn.address, target, kind)
                if key in seen:
                    continue
                seen.add(key)
                owner = owner_of(insn.address, ranges, starts, by_entry)
                hits.append({
                    "instruction_va": insn.address,
                    "instruction_va_hex": hex(insn.address),
                    "mnemonic": insn.mnemonic,
                    "op_str": insn.op_str,
                    "reference_kind": kind,
                    "target_va": target,
                    "target_va_hex": hex(target),
                    "nearest_table_va": nearest,
                    "nearest_table_va_hex": hex(nearest),
                    "delta": target - nearest,
                    "function_entry": int(owner["entry"], 16) if owner else None,
                    "function_entry_hex": hex(int(owner["entry"], 16)) if owner else None,
                    "function_name": owner.get("name") if owner else None,
                })
    return hits


def disassemble_function(raw: bytes, segments: list[dict], fn: dict) -> list[dict]:
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    md.detail = True
    out = []
    for body in fn.get("body_ranges", []):
        lo = int(body["min"], 16)
        hi = int(body["max"], 16) + 1
        foff = v2f(lo, segments)
        if foff is None:
            continue
        blob = raw[foff:foff + (hi - lo)]
        for insn in md.disasm(blob, lo):
            imms = []
            mem_disps = []
            for op in insn.operands:
                if op.type == X86_OP_IMM:
                    imms.append(int(op.imm))
                elif op.type == X86_OP_MEM:
                    mem_disps.append(int(op.mem.disp))
            interesting = [
                value for value in imms + mem_disps
                if abs(value) in INTERESTING_IMMEDIATES
            ]
            out.append({
                "address": insn.address,
                "address_hex": hex(insn.address),
                "mnemonic": insn.mnemonic,
                "op_str": insn.op_str,
                "interesting_slot_like_values": interesting,
            })
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("executable", type=Path)
    ap.add_argument("--codegraph", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--table-radius", type=lambda x: int(x, 0), default=0x180)
    ap.add_argument("--xref-radius", type=lambda x: int(x, 0), default=0x200)
    args = ap.parse_args()

    raw = args.executable.read_bytes()
    header = parse_elf64_header(raw)
    if not header or not header.get("supported"):
        raise SystemExit("expected supported ELF64 eboot")
    segments = parse_elf64_program_headers(raw, header)
    graph = load_graph(args.codegraph)
    ranges, starts, by_entry = build_function_index(graph)
    callers = function_callers(graph)
    strings = string_va_index(graph)
    fentries = function_entry_index(graph)

    table_report = scan_label_tables(args.executable, LABELS, cluster_distance=0x400)
    terrain_hits = []
    target_vas = []
    for label in ("terrain_feature_renderer", "editor_terrain_tile_renderer", "?chunked_terrain"):
        row = table_report["labels"].get(label, {})
        for hit in row.get("pointer_hits", []):
            va = hit.get("reference_virtual_address")
            if va is not None:
                target_vas.append(int(va))
                terrain_hits.append(hit)

    terrain_label_targets = {
        int(hit["target_virtual_address"]) for hit in terrain_hits
    }
    dynlib = parse_orbis_dynlib(raw, segments, terrain_label_targets)
    terrain_loader_relocations = dynlib.get("interesting_addend_relocations", [])

    windows = [
        data_window(
            raw, segments, va, radius=args.table_radius,
            function_entries=fentries, string_vas=strings,
        )
        for va in sorted(set(target_vas))
    ]

    code_refs = scan_code_references(
        raw, segments, sorted(set(target_vas)), ranges, starts, by_entry,
        radius=args.xref_radius,
    )
    candidate_entries = {
        row["function_entry"] for row in code_refs if row["function_entry"] is not None
    }
    dynsym_owners = []
    for symbol in dynlib.get("terrain_symbols", []):
        value = int(symbol.get("value", 0))
        if not value:
            continue
        owner = by_entry.get(value) or owner_of(value, ranges, starts, by_entry)
        dynsym_owners.append({
            "symbol": symbol,
            "owner_entry": int(owner["entry"], 16) if owner else None,
            "owner_name": owner.get("name") if owner else None,
        })
        if owner is not None:
            candidate_entries.add(int(owner["entry"], 16))

    relocation_consumers = []
    relocation_targets = sorted({
        int(row["offset"])
        for row in (
            dynlib.get("terrain_relocations", [])
            + terrain_loader_relocations
        )
        if int(row.get("offset", 0))
    })
    if relocation_targets:
        # The relocation destination is often one field inside a renderer
        # registration record. Search a bounded neighborhood so code that
        # references the record base rather than the name field is retained.
        rel_refs = scan_code_references(
            raw, segments, relocation_targets, ranges, starts, by_entry, radius=0x400,
        )
        relocation_consumers = rel_refs
        for row in rel_refs:
            if row["function_entry"] is not None:
                candidate_entries.add(row["function_entry"])
    candidate_entries = sorted(candidate_entries)

    loader_relocation_owners = []
    for row in terrain_loader_relocations:
        destination = int(row["offset"])
        owner = owner_of(destination, ranges, starts, by_entry)
        loader_relocation_owners.append({
            "label_target_addend": row["addend"],
            "label_target_addend_hex": row["addend_hex"],
            "relocation_table": row["table"],
            "relocation_index": row["index"],
            "relocation_type": row["type"],
            "relocation_symbol_index": row["symbol_index"],
            "relocation_symbol_name": row["symbol_name"],
            "runtime_destination": destination,
            "runtime_destination_hex": row["offset_hex"],
            "destination_function_owner": int(owner["entry"], 16) if owner else None,
            "destination_function_name": owner.get("name") if owner else None,
        })

    terrain_registration_relocation_groups = []
    for group in dynlib.get("interesting_addend_relocation_neighborhoods", []):
        anchor = group["anchor"]
        resolved = []
        for row in group["neighbors"]:
            addend = int(row["addend"]) & 0xFFFFFFFFFFFFFFFF
            function = by_entry.get(addend) or owner_of(addend, ranges, starts, by_entry)
            resolved.append({
                **row,
                "addend_function_owner": int(function["entry"], 16) if function else None,
                "addend_function_name": function.get("name") if function else None,
                "addend_is_exact_function_entry": addend in by_entry,
                "addend_is_mapped_file_address": v2f(addend, segments) is not None,
            })
            if function is not None:
                candidate_entries.add(int(function["entry"], 16))
        terrain_registration_relocation_groups.append({
            "anchor": anchor,
            "neighbors": resolved,
        })

    relocation_destination_windows = [
        data_window(
            raw, segments, int(row["offset"]), radius=args.table_radius,
            function_entries=fentries, string_vas=strings,
        )
        for row in terrain_loader_relocations
        if int(row.get("offset", 0))
    ]

    functions = []
    for entry in candidate_entries:
        fn = by_entry[entry]
        instructions = disassemble_function(raw, segments, fn)
        functions.append({
            "entry": entry,
            "entry_hex": hex(entry),
            "name": fn.get("name"),
            "prototype": fn.get("prototype"),
            "instruction_bytes_sha256": fn.get("instruction_bytes_sha256"),
            "mnemonic_sequence_sha256": fn.get("mnemonic_sequence_sha256"),
            "called_function_entries": fn.get("called_function_entries", []),
            "caller_entries": [hex(x) for x in sorted(callers.get(entry, []))],
            "slot_like_instruction_count": sum(
                bool(i["interesting_slot_like_values"]) for i in instructions
            ),
            "slot_like_instructions": [
                i for i in instructions if i["interesting_slot_like_values"]
            ],
            "instructions": instructions,
        })

    report = {
        "schema": "d1_executable_terrain_runtime_probe/v1",
        "status": "D1_TERRAIN_RUNTIME_PRODUCER_FRONTIER",
        "executable_sha256": hashlib.sha256(raw).hexdigest(),
        "codegraph_program": graph.get("program"),
        "labels": list(LABELS),
        "terrain_pointer_hits": terrain_hits,
        "terrain_pointer_hit_count": len(terrain_hits),
        "terrain_data_windows": windows,
        "code_references_to_terrain_table_neighborhoods": code_refs,
        "orbis_dynlib": dynlib,
        "dynsym_owners": dynsym_owners,
        "terrain_loader_relocations": terrain_loader_relocations,
        "terrain_loader_relocation_owners": loader_relocation_owners,
        "terrain_registration_relocation_groups": terrain_registration_relocation_groups,
        "terrain_relocation_destination_windows": relocation_destination_windows,
        "terrain_relocation_consumers": relocation_consumers,
        "candidate_function_count": len(functions),
        "candidate_functions": functions,
        "t14_proof_boundary": (
            "This report discovers exact executable owners around terrain renderer "
            "metadata. Constants 14/0xE0/0x1C0 are observations only. T14 is not "
            "promoted as STerrain dyemap until a concrete producer path is traced "
            "from the terrain resource/dyemap value into the pixel resource table."
        ),
        "label_table_policy": table_report.get("policy"),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": report["status"],
        "terrain_pointer_hit_count": len(terrain_hits),
        "code_reference_count": len(code_refs),
        "candidate_function_count": len(functions),
        "terrain_dynsym_count": len(dynlib.get("terrain_symbols", [])),
        "terrain_relocation_count": len(dynlib.get("terrain_relocations", [])),
        "terrain_label_addend_relocation_count": len(terrain_loader_relocations),
        "terrain_loader_relocations": [
            {
                "index": row["index"],
                "type": row["type"],
                "offset": row["offset_hex"],
                "addend": row["addend_hex"],
                "symbol_index": row["symbol_index"],
                "symbol_name": row["symbol_name"],
            }
            for row in terrain_loader_relocations
        ],
        "terrain_registration_groups": [
            {
                "anchor_offset": group["anchor"]["offset_hex"],
                "anchor_addend": group["anchor"]["addend_hex"],
                "neighbors": [
                    {
                        "index": row["index"],
                        "index_delta": row["index_delta"],
                        "offset": row["offset_hex"],
                        "offset_delta": row["runtime_offset_delta"],
                        "type": row["type"],
                        "addend": row["addend_hex"],
                        "function": (
                            hex(row["addend_function_owner"])
                            if row["addend_function_owner"] is not None
                            else None
                        ),
                        "exact_function": row["addend_is_exact_function_entry"],
                    }
                    for row in group["neighbors"]
                ],
            }
            for group in terrain_registration_relocation_groups
        ],
        "dynsym_owners": [
            {
                "symbol": row["symbol"]["name"],
                "type": row["symbol"]["type_name"],
                "value": row["symbol"]["value_hex"],
                "size": row["symbol"]["size"],
                "owner": hex(row["owner_entry"]) if row["owner_entry"] is not None else None,
            }
            for row in dynsym_owners
        ],
        "candidates": [
            {
                "entry": f["entry_hex"],
                "slot_like_instruction_count": f["slot_like_instruction_count"],
                "calls": len(f["called_function_entries"]),
                "callers": len(f["caller_entries"]),
            }
            for f in functions[:32]
        ],
        "output": str(args.out),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
