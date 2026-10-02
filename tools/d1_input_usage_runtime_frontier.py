#!/usr/bin/env python3
"""Find the exact D1 runtime interpreter for Sony InputUsageSlot records.

The PS4 shader ABI uses adjacent InputUsageSlot kinds:
  0x12 SubPtrFetchShader
  0x13 PtrResourceTable
  0x14 PtrInternalResourceTable
  0x15 PtrSamplerTable
  0x16 PtrConstBufferTable
  0x17 PtrVertexBufferTable
  0x18 PtrStreamOutBufferTable
  0x19 PtrRwResourceTable

A generic shader setup/bind routine has to branch on these values.  This probe
scans exact Ghidra function ranges in the owner-provided D1 eboot, retaining
functions that reference several of the adjacent enum values and ranking those
inside/near the existing renderer call frontier.

This is discovery evidence only.  Enum-shaped immediates are not assigned a
semantic role until surrounding data flow proves that the compared value is an
InputUsageSlot usage type.
"""
from __future__ import annotations

import argparse
import bisect
import gzip
import json
from collections import defaultdict, deque
from pathlib import Path

from capstone import Cs, CS_ARCH_X86, CS_MODE_64
from capstone.x86 import X86_OP_IMM

from d1_executable_probe import parse_elf64_header, parse_elf64_program_headers

USAGE_NAMES = {
    0x0D: "ImmLdsEsGsSize",
    0x12: "SubPtrFetchShader",
    0x13: "PtrResourceTable",
    0x14: "PtrInternalResourceTable",
    0x15: "PtrSamplerTable",
    0x16: "PtrConstBufferTable",
    0x17: "PtrVertexBufferTable",
    0x18: "PtrStreamOutBufferTable",
    0x19: "PtrRwResourceTable",
}
CORE = {0x12,0x13,0x14,0x15,0x16,0x17,0x18,0x19}


def load_json(path: Path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as fh:
        return json.load(fh)


def v2f(va: int, segments: list[dict]) -> int | None:
    for seg in segments:
        base = int(seg["virtual_address"], 16)
        size = int(seg["file_size"])
        if base <= va < base + size:
            return int(seg["absolute_file_offset"]) + va - base
    return None


def graph_indexes(graph: dict):
    by_entry = {}
    callers = defaultdict(set)
    callees = defaultdict(set)
    for fn in graph.get("functions", []):
        e = int(fn["entry"], 16)
        by_entry[e] = fn
    for row in graph.get("calls", []):
        a = int(row["caller"], 16)
        b = int(row["callee"], 16)
        callers[b].add(a)
        callees[a].add(b)
    return by_entry, callers, callees


def renderer_entries(frontier: dict) -> set[int]:
    # The broad renderer frontier also contains high-scoring D1 hash-literal
    # and assertion neighborhoods that are useful for discovery but are not
    # renderer ownership evidence. For proximity here, seed only functions with
    # direct renderer string xrefs (frame graph / draw submit / lighting/etc.).
    out = set()
    for row in frontier.get("candidates", []):
        offset = row.get("image_offset")
        if not isinstance(offset, int):
            continue
        if any(
            evidence.get("kind") == "renderer_string_xref"
            for evidence in row.get("evidence", [])
        ):
            out.add(int(offset))
    return out


def renderer_distance(entry: int, seeds: set[int], callers, callees, max_depth=3):
    if entry in seeds:
        return 0
    q = deque([(entry,0)])
    seen={entry}
    while q:
        cur,d=q.popleft()
        if d>=max_depth:
            continue
        for n in callers.get(cur,set()) | callees.get(cur,set()):
            if n in seen:
                continue
            if n in seeds:
                return d+1
            seen.add(n)
            q.append((n,d+1))
    return None


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("executable",type=Path)
    ap.add_argument("--codegraph",type=Path,required=True)
    ap.add_argument("--renderer-frontier",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--top",type=int,default=160)
    args=ap.parse_args()

    raw=args.executable.read_bytes()
    h=parse_elf64_header(raw)
    if not h or not h.get("supported"):
        raise SystemExit("supported ELF64 required")
    segments=parse_elf64_program_headers(raw,h)
    graph=load_json(args.codegraph)
    frontier=load_json(args.renderer_frontier)
    by_entry,callers,callees=graph_indexes(graph)
    seeds=renderer_entries(frontier)

    md=Cs(CS_ARCH_X86,CS_MODE_64); md.detail=True
    rows=[]
    for entry,fn in by_entry.items():
        hits=[]
        values=set()
        cmp_values=set()
        for body in fn.get("body_ranges",[]):
            lo=int(body["min"],16); hi=int(body["max"],16)+1
            off=v2f(lo,segments)
            if off is None: continue
            blob=raw[off:off+(hi-lo)]
            for insn in md.disasm(blob,lo):
                vals=[]
                for op in insn.operands:
                    if op.type==X86_OP_IMM:
                        v=int(op.imm) & 0xFFFFFFFFFFFFFFFF
                        if v in USAGE_NAMES:
                            vals.append(v)
                if not vals:
                    continue
                values.update(vals)
                if insn.mnemonic in ("cmp","test","sub","and"):
                    cmp_values.update(vals)
                hits.append({
                    "address":insn.address,
                    "address_hex":hex(insn.address),
                    "mnemonic":insn.mnemonic,
                    "op_str":insn.op_str,
                    "usage_values":[{"value":v,"hex":hex(v),"name":USAGE_NAMES[v]} for v in vals],
                })
        core=values & CORE
        # Keep PtrResourceTable plus at least two adjacent ABI values, or a
        # broad switch with four adjacent ABI values even if 0x13 is compiled
        # into a jump-table bound check rather than a literal case.
        if not ((0x13 in core and len(core)>=3) or len(core)>=4):
            continue
        dist=renderer_distance(entry,seeds,callers,callees,3)
        score=0
        score += 120 if 0x13 in core else 0
        score += 35*len(core)
        score += 20*len(cmp_values & CORE)
        if dist is not None:
            score += {0:180,1:100,2:50,3:20}[dist]
        # Short/medium routines are more plausible enum dispatchers than giant
        # generated registration initializers.
        ic=int(fn.get("instruction_count") or 0)
        if 8 <= ic <= 800: score += 40
        elif ic > 5000: score -= 80
        rows.append({
            "entry":entry,
            "entry_hex":hex(entry),
            "name":fn.get("name"),
            "prototype":fn.get("prototype"),
            "instruction_count":ic,
            "instruction_bytes_sha256":fn.get("instruction_bytes_sha256"),
            "usage_values":[{"value":v,"hex":hex(v),"name":USAGE_NAMES[v]} for v in sorted(values)],
            "comparison_usage_values":[{"value":v,"hex":hex(v),"name":USAGE_NAMES[v]} for v in sorted(cmp_values)],
            "renderer_distance":dist,
            "score":score,
            "caller_entries":[hex(x) for x in sorted(callers.get(entry,set()))],
            "called_function_entries":fn.get("called_function_entries",[]),
            "hits":hits,
        })

    rows.sort(key=lambda r:(-r["score"],r["instruction_count"],r["entry"]))
    rows=rows[:max(1,args.top)]

    # Preserve full disassembly for selected functions to expose switch/jump
    # table setup and pointer writes without another pass.
    for row in rows:
        fn=by_entry[row["entry"]]
        full=[]
        for body in fn.get("body_ranges",[]):
            lo=int(body["min"],16); hi=int(body["max"],16)+1
            off=v2f(lo,segments)
            if off is None: continue
            for insn in md.disasm(raw[off:off+(hi-lo)],lo):
                full.append({"address_hex":hex(insn.address),"mnemonic":insn.mnemonic,"op_str":insn.op_str})
        row["instructions"]=full

    out={
        "schema":"d1_input_usage_runtime_frontier/v1",
        "status":"D1_INPUT_USAGE_RUNTIME_FRONTIER",
        "proof_policy":"Enum-shaped immediates are discovery evidence only; semantics require surrounding InputUsageSlot data flow.",
        "usage_names":{hex(k):v for k,v in USAGE_NAMES.items()},
        "candidate_count":len(rows),
        "candidates":rows,
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":out["status"],
        "candidate_count":len(rows),
        "top":[
            {
                "entry":r["entry_hex"],
                "score":r["score"],
                "instruction_count":r["instruction_count"],
                "renderer_distance":r["renderer_distance"],
                "usage":[x["name"] for x in r["usage_values"]],
                "cmp_usage":[x["name"] for x in r["comparison_usage_values"]],
            } for r in rows[:40]
        ]
    },indent=2))


if __name__=="__main__":
    main()
