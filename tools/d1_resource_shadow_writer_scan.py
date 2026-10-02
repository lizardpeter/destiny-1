#!/usr/bin/env python3
"""Find exact D1 eboot writers of the PS4 resource-table shadow.

The PtrResourceTable producer at F8BFF0 proves that resource table 0 is dumped
from CE constant-RAM dword region:
    stage * 0x642 + texture_index * 8
where one texture descriptor is 8 dwords / 32 bytes.

This scanner searches every exact Ghidra function body for independent code
signatures of writes into that layout. Scores are discovery-only; no terrain
semantic is assigned here.
"""
from __future__ import annotations

import argparse,gzip,json
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from capstone.x86 import X86_OP_IMM,X86_OP_MEM

from d1_executable_probe import parse_elf64_header,parse_elf64_program_headers

STAGE_STRIDE_DWORDS=0x642
RESOURCE_DESC_DWORDS=8
RESOURCE_DESC_BYTES=32
KNOWN_RESOURCE_PATH={0xF8BFF0,0xF8D5E0,0xF8D6C0,0xF8D880,0xF8DF60,0x1005960,0x1005A00}

def load(path:Path):
    opener=gzip.open if path.suffix=='.gz' else open
    with opener(path,'rt',encoding='utf-8') as f:return json.load(f)

def v2f(va,segs):
    for s in segs:
        base=int(s['virtual_address'],16); size=int(s['file_size'])
        if base<=va<base+size:
            return int(s['absolute_file_offset'])+va-base
    return None

def dis_fn(md,raw,segs,fn):
    out=[]
    for br in fn.get('body_ranges',[]):
        lo=int(br['min'],16); hi=int(br['max'],16)+1
        off=v2f(lo,segs)
        if off is None: continue
        out.extend(md.disasm(raw[off:off+(hi-lo)],lo))
    return out

def row(ins):
    imms=[]
    mems=[]
    for op in ins.operands:
        if op.type==X86_OP_IMM:
            imms.append(int(op.imm)&0xffffffffffffffff)
        elif op.type==X86_OP_MEM:
            mems.append({
                'base':ins.reg_name(op.mem.base) if op.mem.base else None,
                'index':ins.reg_name(op.mem.index) if op.mem.index else None,
                'scale':op.mem.scale,
                'disp':op.mem.disp,
            })
    return {
        'address':ins.address,'address_hex':hex(ins.address),
        'mnemonic':ins.mnemonic,'op_str':ins.op_str,
        'immediates':[hex(x) for x in imms],'memory':mems,
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('executable',type=Path)
    ap.add_argument('--codegraph',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--top',type=int,default=160)
    a=ap.parse_args()

    raw=a.executable.read_bytes()
    h=parse_elf64_header(raw); segs=parse_elf64_program_headers(raw,h)
    g=load(a.codegraph)
    funcs={int(f['entry'],16):f for f in g.get('functions',[])}
    callers={}
    for e in g.get('calls',[]):
        x=int(e['caller'],16); y=int(e['callee'],16)
        callers.setdefault(y,set()).add(x)

    md=Cs(CS_ARCH_X86,CS_MODE_64); md.detail=True

    # Fast prefilter: 0x642 is the exact source-closed per-stage dword stride.
    # Find its literal little-endian encoding in the executable, map those file
    # offsets back to VAs/functions, then include one caller/callee hop. This
    # avoids disassembling the entire program merely to discover the small state
    # API cluster that owns this layout.
    import struct,bisect
    literal=struct.pack('<I',STAGE_STRIDE_DWORDS)
    file_hits=[]
    start=0
    while True:
        pos=raw.find(literal,start)
        if pos<0: break
        file_hits.append(pos)
        start=pos+1

    ranges=[]
    for entry,fn in funcs.items():
        for br in fn.get('body_ranges',[]):
            ranges.append((int(br['min'],16),int(br['max'],16),entry))
    ranges.sort()
    range_starts=[x[0] for x in ranges]

    def file_to_va(off):
        for seg in segs:
            base_file=int(seg['absolute_file_offset']); size=int(seg['file_size'])
            if base_file<=off<base_file+size:
                return int(seg['virtual_address'],16)+(off-base_file)
        return None

    seed_entries=set()
    raw_hit_rows=[]
    for off in file_hits:
        va=file_to_va(off)
        owner=None
        if va is not None:
            idx=bisect.bisect_right(range_starts,va)-1
            if idx>=0:
                lo,hi,entry=ranges[idx]
                if lo<=va<=hi:
                    owner=entry
                    seed_entries.add(entry)
        raw_hit_rows.append({'file_offset':off,'file_offset_hex':hex(off),'va':va,'va_hex':hex(va) if va is not None else None,'owner_entry':owner,'owner_entry_hex':hex(owner) if owner is not None else None})

    candidate_entries=set(seed_entries)
    for entry in list(seed_entries):
        candidate_entries.update(callers.get(entry,set()))
        fn=funcs.get(entry,{})
        for target in fn.get('called_function_entries',[]):
            if isinstance(target,str):
                try: candidate_entries.add(int(target,16))
                except ValueError: pass

    candidates=[]
    for entry in sorted(candidate_entries):
        fn=funcs.get(entry)
        if fn is None: continue
        insns=list(dis_fn(md,raw,segs,fn))
        if not insns: continue
        hits=[]; score=0
        has_stride=False
        writes=0
        desc_copy_like=0
        for i,ins in enumerate(insns):
            r=row(ins)
            imms=[int(op.imm)&0xffffffffffffffff for op in ins.operands if op.type==X86_OP_IMM]
            memdisps=[op.mem.disp for op in ins.operands if op.type==X86_OP_MEM]
            local=0; reasons=[]
            if STAGE_STRIDE_DWORDS in imms:
                local+=180; reasons.append('stage_stride_0x642_immediate'); has_stride=True
            if STAGE_STRIDE_DWORDS in memdisps or -STAGE_STRIDE_DWORDS in memdisps:
                local+=160; reasons.append('stage_stride_0x642_displacement'); has_stride=True
            if RESOURCE_DESC_DWORDS in imms:
                local+=4; reasons.append('descriptor_dwords_8')
            if RESOURCE_DESC_BYTES in imms:
                local+=8; reasons.append('descriptor_bytes_0x20')
            if 0x5c1 in imms or 0x5c1 in memdisps:
                local+=30; reasons.append('userdata_shadow_anchor_0x5c1')
            if 0x10c in memdisps:
                local+=30; reasons.append('resource_table_count_state_0x10c')
            # Exact 32-byte stores/copies often appear as 8 scalar writes or
            # two 16-byte vector moves in a short neighborhood.
            if ins.mnemonic.startswith('mov') and ins.operands and ins.operands[0].type==X86_OP_MEM:
                writes+=1
                if any(abs(d) in {0,4,8,12,16,20,24,28} for d in memdisps):
                    desc_copy_like+=1
            if local:
                lo=max(0,i-10); hi=min(len(insns),i+14)
                hits.append({
                    'center':r,
                    'score':local,
                    'reasons':reasons,
                    'context':[row(x) for x in insns[lo:hi]],
                })
                score+=local

        # A stage-stride function with clustered stores is high-value.
        if has_stride:
            score+=min(120,writes*2)+min(120,desc_copy_like*4)
        # Call-graph relation to proven resource path is useful, not semantic proof.
        callees={int(x,16) for x in fn.get('called_function_entries',[]) if isinstance(x,str)}
        direct_known=sorted(callees & KNOWN_RESOURCE_PATH)
        direct_callers=sorted(callers.get(entry,set()) & KNOWN_RESOURCE_PATH)
        if direct_known:
            score+=80*len(direct_known)
        if direct_callers:
            score+=60*len(direct_callers)
        if score<=0: continue
        candidates.append({
            'entry':entry,'entry_hex':hex(entry),'name':fn.get('name'),
            'prototype':fn.get('prototype'),'instruction_count':len(insns),
            'score':score,'has_stage_stride':has_stride,
            'memory_write_instruction_count':writes,
            'descriptor_copy_like_write_count':desc_copy_like,
            'calls_known_resource_path':[hex(x) for x in direct_known],
            'called_by_known_resource_path':[hex(x) for x in direct_callers],
            'caller_entries':[hex(x) for x in sorted(callers.get(entry,set()))],
            'called_function_entries':fn.get('called_function_entries',[]),
            'hits':hits,
        })

    candidates.sort(key=lambda x:(-x['score'],x['entry']))
    candidates=candidates[:a.top]
    out={
        'schema':'d1_resource_shadow_writer_scan/v1',
        'status':'D1_RESOURCE_SHADOW_WRITER_FRONTIER',
        'executable_sha256':g.get('program',{}).get('executable_sha256'),
        'proven_layout':{
            'stage_stride_dwords':hex(STAGE_STRIDE_DWORDS),
            'resource_descriptor_dwords':RESOURCE_DESC_DWORDS,
            'resource_descriptor_bytes':RESOURCE_DESC_BYTES,
            'resource_table_zero_entry_formula':'stage*0x642 + texture_index*8 dwords',
        },
        'proof_boundary':'Scores identify exact-code writer candidates only. A writer is not terrain/T14 until its source descriptor is tied to the active STerrain mesh-group dyemap.',
        'raw_stage_stride_literal_hits':raw_hit_rows,
        'stage_stride_seed_entries':[hex(x) for x in sorted(seed_entries)],
        'prefilter_candidate_entry_count':len(candidate_entries),
        'candidate_count':len(candidates),
        'candidates':candidates,
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({
        'status':out['status'],
        'candidate_count':len(candidates),
        'top':[{
            'entry':x['entry_hex'],'score':x['score'],'stride':x['has_stage_stride'],
            'writes':x['memory_write_instruction_count'],
            'known':x['calls_known_resource_path'],
        } for x in candidates[:40]],
    },indent=2))

if __name__=='__main__': main()
