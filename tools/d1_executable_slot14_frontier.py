#!/usr/bin/env python3
"""Whole-executable D1 PS4 pixel-resource slot-14 frontier.

This is a discovery probe, not semantic promotion. It scans the exact retail
x86-64 executable for instructions that use:
  * 0x1C0 = 14 * 32, the byte offset of texture resource-table slot 14 when a
    PS4 GnmTexture descriptor occupies 8 dwords / 32 bytes;
  * literal index 14 / 0xE;
  * 0xE0, retained because earlier renderer code uses 0xE0-sized records and it
    is a recurring historical candidate, but it is NOT treated as T14 proof.

Hits are joined to the exact-build Ghidra function/call graph and the ranked
renderer frontier. A function must still be traced to the STerrain dyemap value
before T14 may be named as that producer.
"""
from __future__ import annotations

import argparse
import bisect
import gzip
import json
from collections import defaultdict
from pathlib import Path

from capstone import Cs, CS_ARCH_X86, CS_MODE_64
from capstone.x86 import X86_OP_IMM, X86_OP_MEM

from d1_executable_probe import parse_elf64_header, parse_elf64_program_headers

SLOT14_INDEX=14
TEXTURE_DESCRIPTOR_BYTES=32
SLOT14_OFFSET=SLOT14_INDEX*TEXTURE_DESCRIPTOR_BYTES
SECONDARY_OFFSET=0xE0


def load_json(path: Path):
    opener=gzip.open if path.suffix=='.gz' else open
    with opener(path,'rt',encoding='utf-8') as fh:
        return json.load(fh)


def build_index(graph: dict):
    ranges=[]
    starts=[]
    by_entry={}
    for fn in graph.get('functions',[]):
        entry=int(fn['entry'],16)
        by_entry[entry]=fn
        for row in fn.get('body_ranges',[]):
            lo=int(row['min'],16); hi=int(row['max'],16)
            ranges.append((lo,hi,entry))
    ranges.sort()
    starts=[x[0] for x in ranges]
    callers=defaultdict(set)
    for edge in graph.get('calls',[]):
        callers[int(edge['callee'],16)].add(int(edge['caller'],16))
    return ranges,starts,by_entry,callers


def owner_of(addr,ranges,starts,by_entry):
    i=bisect.bisect_right(starts,addr)-1
    while i>=0 and ranges[i][0]<=addr:
        lo,hi,entry=ranges[i]
        if lo<=addr<=hi:
            return by_entry.get(entry)
        i-=1
    return None


def executable_segments(segments):
    return [s for s in segments if s.get('executable') and int(s.get('file_size',0))>0]


def v2f(va,segments):
    for seg in segments:
        base=int(seg['virtual_address'],16)
        size=int(seg['file_size'])
        if base<=va<base+size:
            return int(seg['absolute_file_offset'])+va-base
    return None


def renderer_seed_entries(frontier: dict):
    out=set()
    for row in frontier.get('candidates',[]):
        off=row.get('image_offset')
        if isinstance(off,int):
            out.add(off)
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('executable',type=Path)
    ap.add_argument('--codegraph',type=Path,required=True)
    ap.add_argument('--renderer-frontier',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--top',type=int,default=300)
    args=ap.parse_args()

    raw=args.executable.read_bytes()
    h=parse_elf64_header(raw)
    if not h or not h.get('supported'):
        raise SystemExit('supported ELF64 required')
    segments=parse_elf64_program_headers(raw,h)
    graph=load_json(args.codegraph)
    frontier=load_json(args.renderer_frontier)
    ranges,starts,by_entry,callers=build_index(graph)
    renderer_entries=renderer_seed_entries(frontier)

    md=Cs(CS_ARCH_X86,CS_MODE_64); md.detail=True
    hits=defaultdict(list)
    global_counts=defaultdict(int)

    for seg in executable_segments(segments):
        foff=int(seg['absolute_file_offset']); size=int(seg['file_size'])
        va0=int(seg['virtual_address'],16)
        blob=raw[foff:foff+size]
        for insn in md.disasm(blob,va0):
            owner=owner_of(insn.address,ranges,starts,by_entry)
            if owner is None:
                continue
            sig=[]
            mem_indices=[]
            imm_values=[]
            mem_disps=[]
            for oi,op in enumerate(insn.operands):
                if op.type==X86_OP_IMM:
                    v=int(op.imm)
                    imm_values.append(v)
                    if abs(v)==SLOT14_INDEX:
                        sig.append('literal_index_14')
                    if abs(v)==SLOT14_OFFSET:
                        sig.append('literal_offset_0x1c0')
                    if abs(v)==SECONDARY_OFFSET:
                        sig.append('literal_0xe0')
                elif op.type==X86_OP_MEM:
                    disp=int(op.mem.disp)
                    mem_disps.append(disp)
                    if abs(disp)==SLOT14_OFFSET:
                        sig.append('memory_disp_0x1c0'); mem_indices.append(oi)
                    if abs(disp)==SECONDARY_OFFSET:
                        sig.append('memory_disp_0xe0'); mem_indices.append(oi)
            if not sig:
                continue
            entry=int(owner['entry'],16)
            hit={
                'address':insn.address,
                'address_hex':hex(insn.address),
                'mnemonic':insn.mnemonic,
                'op_str':insn.op_str,
                'signals':sorted(set(sig)),
                'immediates':imm_values,
                'memory_displacements':mem_disps,
                'memory_operand_indices':mem_indices,
            }
            hits[entry].append(hit)
            for x in set(sig):
                global_counts[x]+=1

    rows=[]
    for entry,fhits in hits.items():
        fn=by_entry[entry]
        signal_counts=defaultdict(int)
        for hit in fhits:
            for x in hit['signals']: signal_counts[x]+=1
        score=(
            signal_counts['memory_disp_0x1c0']*50
            +signal_counts['literal_offset_0x1c0']*30
            +signal_counts['literal_index_14']*6
            +signal_counts['memory_disp_0xe0']*4
            +signal_counts['literal_0xe0']*2
        )
        direct_renderer=entry in renderer_entries
        callees={int(x,16) for x in fn.get('called_function_entries',[]) if int(x,16) in by_entry}
        caller_set=callers.get(entry,set())
        renderer_callees=sorted(callees & renderer_entries)
        renderer_callers=sorted(caller_set & renderer_entries)
        if direct_renderer: score+=100
        score+=25*len(renderer_callees)
        score+=25*len(renderer_callers)
        # Common exact renderer neighborhood, only a ranking nudge.
        in_renderer_band=0x7D0000<=entry<=0x8B0000
        if in_renderer_band: score+=5

        # Include a compact call neighborhood to make producer tracing easier.
        rows.append({
            'entry':entry,
            'entry_hex':hex(entry),
            'name':fn.get('name'),
            'prototype':fn.get('prototype'),
            'instruction_count':fn.get('instruction_count'),
            'instruction_bytes_sha256':fn.get('instruction_bytes_sha256'),
            'score':score,
            'signal_counts':dict(sorted(signal_counts.items())),
            'renderer_frontier_direct':direct_renderer,
            'renderer_frontier_callees':[hex(x) for x in renderer_callees],
            'renderer_frontier_callers':[hex(x) for x in renderer_callers],
            'caller_entries':[hex(x) for x in sorted(caller_set)],
            'called_function_entries':fn.get('called_function_entries',[]),
            'renderer_address_band':in_renderer_band,
            'hits':fhits,
        })

    rows.sort(key=lambda r:(-r['score'],-r['signal_counts'].get('memory_disp_0x1c0',0),r['entry']))
    top=rows[:max(1,args.top)]

    # Full function disassembly for top results, preserving calls surrounding hits.
    for row in top:
        fn=by_entry[row['entry']]
        full=[]
        for body in fn.get('body_ranges',[]):
            lo=int(body['min'],16); hi=int(body['max'],16)+1
            off=v2f(lo,segments)
            if off is None: continue
            blob=raw[off:off+(hi-lo)]
            for insn in md.disasm(blob,lo):
                full.append({'address_hex':hex(insn.address),'mnemonic':insn.mnemonic,'op_str':insn.op_str})
        row['instructions']=full

    report={
        'schema':'d1_executable_slot14_frontier/v1',
        'status':'D1_EXECUTABLE_SLOT14_FRONTIER',
        'executable_sha256':graph.get('program',{}).get('executable_sha256'),
        'proof_boundary':(
            '0x1C0/14 matches are executable observations only. T14 becomes the '
            'STerrain dyemap binding only after a concrete retail dataflow from '
            'the active terrain dyemap/resource into this table position is proven.'
        ),
        'descriptor_assumption':{
            'texture_descriptor_bytes':TEXTURE_DESCRIPTOR_BYTES,
            'slot_index':SLOT14_INDEX,
            'slot_offset_hex':hex(SLOT14_OFFSET),
            'status':'PS4_GNM_TEXTURE_DESCRIPTOR_SIZE_KNOWN_DISCOVERY_MODEL',
        },
        'renderer_frontier_seed_count':len(renderer_entries),
        'global_signal_counts':dict(sorted(global_counts.items())),
        'function_hit_count':len(rows),
        'top_function_count':len(top),
        'functions':top,
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({
        'status':report['status'],
        'function_hit_count':len(rows),
        'global_signal_counts':report['global_signal_counts'],
        'top':[
            {
                'entry':r['entry_hex'],
                'score':r['score'],
                'signals':r['signal_counts'],
                'renderer':r['renderer_frontier_direct'],
                'renderer_callers':r['renderer_frontier_callers'],
                'renderer_callees':r['renderer_frontier_callees'],
            } for r in top[:40]
        ]
    },indent=2))


if __name__=='__main__':
    main()
