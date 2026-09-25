#!/usr/bin/env python3
"""Static analysis helper for the exact Destiny Oodle 3 reference DLL.

This tool records compatibility evidence (PE layout, exports/imports and a
conservative direct-call/basic-block map) without copying the DLL into the repo.
It intentionally does not emit a decompiler-style source reconstruction.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import Counter, deque
from pathlib import Path

import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_64, CS_GRP_CALL, CS_GRP_JUMP, CS_GRP_RET
from capstone.x86_const import X86_OP_IMM, X86_OP_MEM, X86_REG_RIP

EXPECTED_SHA256 = "682c0aad216fae443e0f9561876cfabfddaeffcd48e5990613ad2cf47c49fa62"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def entropy(data: bytes) -> float:
    if not data:
        return 0.0
    hist = [0] * 256
    for b in data:
        hist[b] += 1
    n = len(data)
    return -sum((c / n) * math.log2(c / n) for c in hist if c)


def sec_name(sec) -> str:
    return sec.Name.rstrip(b"\0").decode("ascii", "replace")


def direct_target(ins):
    try:
        if ins.operands and ins.operands[0].type == X86_OP_IMM:
            return int(ins.operands[0].imm)
    except Exception:
        pass
    return None


def walk_function(md: Cs, image: bytes, text_va: int, text_end: int, start: int,
                  max_instructions: int = 12000) -> dict:
    q = deque([start])
    seen_blocks = set()
    seen_ins = set()
    calls = set()
    edges = []
    rows = []
    truncated = False

    while q and len(seen_ins) < max_instructions:
        block = q.popleft()
        if block in seen_blocks or not (text_va <= block < text_end):
            continue
        seen_blocks.add(block)
        pc = block

        while text_va <= pc < text_end and len(seen_ins) < max_instructions:
            if pc in seen_ins:
                break
            off = pc - text_va
            chunk = image[off:off + 15]
            decoded = list(md.disasm(chunk, pc, count=1))
            if not decoded:
                break
            ins = decoded[0]
            seen_ins.add(pc)
            imm_values = []
            rip_targets = []
            try:
                imm_values = [
                    int(op.imm) for op in ins.operands if op.type == X86_OP_IMM
                ]
                rip_targets = [
                    int(ins.address + ins.size + op.mem.disp)
                    for op in ins.operands
                    if op.type == X86_OP_MEM and op.mem.base == X86_REG_RIP
                ]
            except Exception:
                pass
            rows.append({
                "address": pc,
                "size": ins.size,
                "mnemonic": ins.mnemonic,
                "op_str": ins.op_str,
                "bytes": ins.bytes.hex(),
                "immediates": imm_values,
                "rip_targets": rip_targets,
            })
            nxt = pc + ins.size

            if ins.group(CS_GRP_RET):
                break

            if ins.group(CS_GRP_CALL):
                target = direct_target(ins)
                if target is not None and text_va <= target < text_end:
                    calls.add(target)
                    edges.append({"kind": "call", "from": pc, "to": target})
                pc = nxt
                continue

            if ins.group(CS_GRP_JUMP):
                target = direct_target(ins)
                unconditional = ins.mnemonic in ("jmp", "ljmp")
                if target is not None and text_va <= target < text_end:
                    edges.append({"kind": "jump", "from": pc, "to": target})
                    q.append(target)
                if not unconditional:
                    edges.append({"kind": "fallthrough", "from": pc, "to": nxt})
                    q.append(nxt)
                break

            pc = nxt

    if len(seen_ins) >= max_instructions:
        truncated = True

    rows.sort(key=lambda x: x["address"])
    mnemonic_counts = Counter(row["mnemonic"] for row in rows)
    small_immediates = Counter()
    compare_immediates = Counter()
    mask_immediates = Counter()
    for row in rows:
        for imm in row["immediates"]:
            if -0x10000 <= imm <= 0x10000:
                small_immediates[imm] += 1
            if row["mnemonic"] in ("cmp", "test") and -0x100000 <= imm <= 0x100000:
                compare_immediates[imm] += 1
            if row["mnemonic"] in ("and", "or", "xor", "test") and -0x100000 <= imm <= 0x100000:
                mask_immediates[imm] += 1

    body = b"".join(bytes.fromhex(row["bytes"]) for row in rows)
    return {
        "start": start,
        "instruction_count": len(rows),
        "block_count": len(seen_blocks),
        "direct_calls": sorted(calls),
        "edges": edges,
        "truncated": truncated,
        "semantic_signature": {
            "body_sha256": sha256(body),
            "mnemonic_histogram": dict(sorted(mnemonic_counts.items())),
            "small_immediates": {str(k): v for k, v in sorted(small_immediates.items())},
            "compare_immediates": {str(k): v for k, v in sorted(compare_immediates.items())},
            "mask_immediates": {str(k): v for k, v in sorted(mask_immediates.items())},
        },
        "instructions": rows,
    }


def interesting_strings(blob: bytes) -> list[dict]:
    out = []
    ascii_re = re.compile(rb"[\x20-\x7e]{4,}")
    keys = ("oodle", "lz", "huff", "decode", "compress", "entropy", "literal",
            "match", "offset", "window", "crc", "corrupt", "fuzz")
    for m in ascii_re.finditer(blob):
        s = m.group().decode("ascii", "replace")
        low = s.lower()
        if any(k in low for k in keys):
            out.append({"offset": m.start(), "encoding": "ascii", "text": s[:300]})
    return out[:2000]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("dll", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--asm-output", type=Path)
    ap.add_argument("--max-functions", type=int, default=256)
    args = ap.parse_args()

    data = args.dll.read_bytes()
    digest = sha256(data)
    if digest != EXPECTED_SHA256:
        raise SystemExit(f"unexpected DLL SHA-256: {digest}")

    pe = pefile.PE(data=data, fast_load=False)
    image_base = int(pe.OPTIONAL_HEADER.ImageBase)

    sections = []
    text = None
    for s in pe.sections:
        name = sec_name(s)
        raw = s.get_data()
        row = {
            "name": name,
            "virtual_address": int(s.VirtualAddress),
            "virtual_size": int(s.Misc_VirtualSize),
            "raw_offset": int(s.PointerToRawData),
            "raw_size": int(s.SizeOfRawData),
            "sha256": sha256(raw),
            "entropy": entropy(raw),
            "characteristics": int(s.Characteristics),
        }
        sections.append(row)
        if name == ".text":
            text = (s, raw)

    if text is None:
        raise SystemExit("missing .text")

    exports = []
    export_by_name = {}
    if hasattr(pe, "DIRECTORY_ENTRY_EXPORT"):
        for sym in pe.DIRECTORY_ENTRY_EXPORT.symbols:
            name = sym.name.decode("ascii", "replace") if sym.name else None
            rva = int(sym.address)
            row = {
                "name": name,
                "ordinal": int(sym.ordinal),
                "rva": rva,
                "va": image_base + rva,
                "forwarder": sym.forwarder.decode("ascii", "replace") if sym.forwarder else None,
            }
            exports.append(row)
            if name:
                export_by_name[name] = row

    imports = []
    if hasattr(pe, "DIRECTORY_ENTRY_IMPORT"):
        for desc in pe.DIRECTORY_ENTRY_IMPORT:
            dll = desc.dll.decode("ascii", "replace")
            names = []
            for imp in desc.imports:
                names.append({
                    "name": imp.name.decode("ascii", "replace") if imp.name else None,
                    "ordinal": int(imp.ordinal) if imp.ordinal is not None else None,
                    "iat_va": int(imp.address),
                })
            imports.append({"dll": dll, "symbols": names})

    target = export_by_name.get("OodleLZ_Decompress")
    if not target:
        raise SystemExit("OodleLZ_Decompress export not found")

    text_sec, text_bytes = text
    text_va = image_base + int(text_sec.VirtualAddress)
    text_end = text_va + len(text_bytes)

    md = Cs(CS_ARCH_X86, CS_MODE_64)
    md.detail = True

    queue = deque([target["va"]])
    funcs = {}
    while queue and len(funcs) < args.max_functions:
        fva = queue.popleft()
        if fva in funcs or not (text_va <= fva < text_end):
            continue
        f = walk_function(md, text_bytes, text_va, text_end, fva)
        funcs[fva] = f
        for callee in f["direct_calls"]:
            if callee not in funcs:
                queue.append(callee)

    def ascii_at_va(va: int):
        rva = va - image_base
        if rva < 0:
            return None
        try:
            off = pe.get_offset_from_rva(rva)
        except Exception:
            return None
        if off < 0 or off >= len(data):
            return None
        end = off
        while end < len(data) and end - off < 500 and data[end] != 0:
            b = data[end]
            if b < 0x20 or b > 0x7e:
                return None
            end += 1
        if end - off < 4:
            return None
        return data[off:end].decode("ascii", "replace")

    string_xrefs = []
    for fva, fn in funcs.items():
        for row in fn["instructions"]:
            for target_va in row.get("rip_targets", []):
                s = ascii_at_va(target_va)
                if s:
                    string_xrefs.append({
                        "function_rva": fva - image_base,
                        "instruction_rva": row["address"] - image_base,
                        "target_rva": target_va - image_base,
                        "text": s,
                    })

    runtime_functions = []
    if hasattr(pe, "DIRECTORY_ENTRY_EXCEPTION"):
        for ent in pe.DIRECTORY_ENTRY_EXCEPTION:
            begin = int(ent.struct.BeginAddress)
            end = int(ent.struct.EndAddress)
            runtime_functions.append((begin, end))
        runtime_functions.sort()

    def containing_runtime_function(rva: int):
        # x64 .pdata ranges are non-overlapping and sorted by BeginAddress.
        lo, hi = 0, len(runtime_functions)
        while lo < hi:
            mid = (lo + hi) // 2
            if runtime_functions[mid][0] <= rva:
                lo = mid + 1
            else:
                hi = mid
        if lo == 0:
            return None
        begin, end = runtime_functions[lo - 1]
        return begin if begin <= rva < end else None

    whole_text_string_xrefs = []
    md_all = Cs(CS_ARCH_X86, CS_MODE_64)
    md_all.detail = True
    md_all.skipdata = True
    for ins in md_all.disasm(text_bytes, text_va):
        if ins.id == 0:
            continue
        try:
            targets = [
                int(ins.address + ins.size + op.mem.disp)
                for op in ins.operands
                if op.type == X86_OP_MEM and op.mem.base == X86_REG_RIP
            ]
        except Exception:
            continue
        for target_va in targets:
            s = ascii_at_va(target_va)
            if not s:
                continue
            irva = int(ins.address - image_base)
            whole_text_string_xrefs.append({
                "function_rva": containing_runtime_function(irva),
                "instruction_rva": irva,
                "target_rva": target_va - image_base,
                "text": s,
            })

    def summarize_codec_dispatch(fn):
        codec_ids = {0, 1, 2, 3, 4, 5, 6, 7, 10, 11}
        rows = fn["instructions"]
        by_addr = {row["address"]: row for row in rows}

        def codec_cmp(row):
            return (
                row["mnemonic"] == "cmp"
                and any(imm in codec_ids for imm in row.get("immediates", []))
            )

        def path_calls(start, budget=96):
            pending = [start]
            seen = set()
            calls = []
            while pending and len(seen) < budget:
                pc = pending.pop()
                while pc in by_addr and pc not in seen and len(seen) < budget:
                    row = by_addr[pc]
                    seen.add(pc)
                    if codec_cmp(row) and pc != start:
                        break
                    m = row["mnemonic"]
                    imms = row.get("immediates", [])
                    nxt = pc + row["size"]
                    if m == "call" and imms:
                        target = imms[0]
                        if text_va <= target < text_end and target not in calls:
                            calls.append(target)
                        pc = nxt
                        continue
                    if m.startswith("ret"):
                        break
                    if m == "jmp":
                        if imms and imms[0] in by_addr:
                            pc = imms[0]
                            continue
                        break
                    if m.startswith("j") and m != "jmp":
                        if imms and imms[0] in by_addr:
                            pending.append(imms[0])
                        pc = nxt
                        continue
                    pc = nxt
            return calls[:16]

        sites = []
        for row in rows:
            if not codec_cmp(row):
                continue
            codec_values = [imm for imm in row["immediates"] if imm in codec_ids]
            nxt_addr = row["address"] + row["size"]
            jcc = by_addr.get(nxt_addr)
            item = {
                "cmp_rva": row["address"] - image_base,
                "codec_values": codec_values,
                "next_mnemonic": jcc["mnemonic"] if jcc else None,
                "taken_rva": None,
                "fallthrough_rva": None,
                "taken_call_rvas": [],
                "fallthrough_call_rvas": [],
            }
            if jcc and jcc["mnemonic"].startswith("j") and jcc["mnemonic"] != "jmp":
                targets = jcc.get("immediates", [])
                if targets and text_va <= targets[0] < text_end:
                    item["taken_rva"] = targets[0] - image_base
                    item["taken_call_rvas"] = [
                        x - image_base for x in path_calls(targets[0])
                    ]
                fall = jcc["address"] + jcc["size"]
                if fall in by_addr:
                    item["fallthrough_rva"] = fall - image_base
                    item["fallthrough_call_rvas"] = [
                        x - image_base for x in path_calls(fall)
                    ]
            sites.append(item)
        return sites

    decode_some = funcs.get(export_by_name["OodleLZDecoder_DecodeSome"]["va"])
    decode_some_dispatch_sites = (
        summarize_codec_dispatch(decode_some) if decode_some is not None else []
    )

    report = {
        "schema": "d1_oodle3_static_probe_v1",
        "dll": args.dll.name,
        "size": len(data),
        "sha256": digest,
        "machine": int(pe.FILE_HEADER.Machine),
        "timestamp": int(pe.FILE_HEADER.TimeDateStamp),
        "image_base": image_base,
        "entrypoint_rva": int(pe.OPTIONAL_HEADER.AddressOfEntryPoint),
        "sections": sections,
        "imports": imports,
        "exports": sorted(exports, key=lambda x: x["ordinal"]),
        "target_export": target,
        "text": {"va": text_va, "end_va": text_end, "size": len(text_bytes)},
        "reachable_function_count": len(funcs),
        "reachable_functions": [
            {
                **{k: v for k, v in funcs[a].items() if k != "instructions"},
                "rva": a - image_base,
                "export_name": next(
                    (e["name"] for e in exports if e["va"] == a and e["name"]),
                    None,
                ),
                "direct_call_rvas": [x - image_base for x in funcs[a]["direct_calls"]],
            }
            for a in sorted(funcs)
        ],
        "interesting_strings": interesting_strings(data),
        "string_xrefs": string_xrefs,
        "whole_text_string_xrefs": whole_text_string_xrefs,
        "runtime_function_count": len(runtime_functions),
        "decode_some_dispatch_sites": decode_some_dispatch_sites,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    asm_path = args.asm_output or args.output.with_suffix(".asm.txt")
    with asm_path.open("w", encoding="utf-8") as f:
        for va in sorted(funcs):
            fn = funcs[va]
            f.write(f"\n; function {va:#x} blocks={fn['block_count']} ins={fn['instruction_count']}\n")
            for row in fn["instructions"]:
                f.write(f"{row['address']:016x}  {row['bytes']:<30} {row['mnemonic']:<8} {row['op_str']}\n")

    print(json.dumps({
        "sha256": digest,
        "decompress": target,
        "exports": len(exports),
        "imports": sum(len(x["symbols"]) for x in imports),
        "reachable_functions": len(funcs),
        "json": str(args.output),
        "asm": str(asm_path),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
