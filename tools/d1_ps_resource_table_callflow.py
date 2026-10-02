#!/usr/bin/env python3
"""Trace the exact D1 PS resource-table pointer callflow from the retail eboot.

This is a lightweight companion to the Ghidra decompile. It uses exact Ghidra
function ranges only for boundaries, then Capstone-disassembles the authoritative
01.33 eboot bytes and emits bounded caller/callee neighborhoods around:
  F8DF60 -> F8D880 -> F80210

F80210 is independently proven to emit the PS USER_DATA12 SET_SH_REG pointer
packet consumed by terrain PtrResourceTable at s[12:13].
"""
from __future__ import annotations

import argparse,gzip,json
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from capstone.x86 import X86_OP_IMM,X86_OP_REG,X86_OP_MEM

from d1_executable_probe import parse_elf64_header,parse_elf64_program_headers

TARGETS={0xF80210,0xF83520,0xF8D880,0xF8DF60,0xF8E680}
INTERESTING_CALLEES={0xF80210,0xF8D880,0xF83520}


def load_json(path:Path):
    opener=gzip.open if path.suffix=='.gz' else open
    with opener(path,'rt',encoding='utf-8') as f:return json.load(f)


def v2f(va:int,segments:list[dict])->int|None:
    for seg in segments:
        base=int(seg['virtual_address'],16); size=int(seg['file_size'])
        if base<=va<base+size:
            return int(seg['absolute_file_offset'])+va-base
    return None


def ins_row(ins):
    ops=[]
    for op in ins.operands:
        if op.type==X86_OP_IMM:
            ops.append({'type':'imm','value':int(op.imm)&0xffffffffffffffff,'hex':hex(int(op.imm)&0xffffffffffffffff)})
        elif op.type==X86_OP_REG:
            ops.append({'type':'reg','name':ins.reg_name(op.reg)})
        elif op.type==X86_OP_MEM:
            ops.append({
                'type':'mem',
                'base':ins.reg_name(op.mem.base) if op.mem.base else None,
                'index':ins.reg_name(op.mem.index) if op.mem.index else None,
                'scale':op.mem.scale,
                'disp':op.mem.disp,
                'disp_hex':hex(op.mem.disp & 0xffffffffffffffff),
            })
    return {'address':ins.address,'address_hex':hex(ins.address),'mnemonic':ins.mnemonic,'op_str':ins.op_str,'operands':ops}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('executable',type=Path)
    ap.add_argument('--codegraph',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()

    raw=a.executable.read_bytes()
    h=parse_elf64_header(raw); segs=parse_elf64_program_headers(raw,h)
    graph=load_json(a.codegraph)
    funcs={int(f['entry'],16):f for f in graph.get('functions',[])}

    md=Cs(CS_ARCH_X86,CS_MODE_64); md.detail=True
    rows=[]
    for entry in sorted(TARGETS):
        f=funcs.get(entry)
        if not f: continue
        allins=[]
        for br in f.get('body_ranges',[]):
            lo=int(br['min'],16); hi=int(br['max'],16)+1
            off=v2f(lo,segs)
            if off is None: continue
            allins.extend(list(md.disasm(raw[off:off+(hi-lo)],lo)))
        encoded=[ins_row(x) for x in allins]
        calls=[]
        for i,ins in enumerate(allins):
            if ins.mnemonic!='call' or not ins.operands or ins.operands[0].type!=X86_OP_IMM: continue
            callee=int(ins.operands[0].imm)&0xffffffffffffffff
            if callee not in INTERESTING_CALLEES: continue
            lo=max(0,i-55); hi=min(len(allins),i+18)
            calls.append({
                'call_address':hex(ins.address),
                'callee':hex(callee),
                'preceding_and_following': [ins_row(x) for x in allins[lo:hi]],
            })
        rows.append({
            'entry':entry,'entry_hex':hex(entry),'name':f.get('name'),
            'prototype':f.get('prototype'),'instruction_count':len(encoded),
            'calls_of_interest':calls,
            'instructions':encoded,
        })

    out={
        'schema':'d1_ps_resource_table_callflow/v1',
        'status':'D1_PS_RESOURCE_TABLE_CALLFLOW_EXACT_BINARY',
        'executable_sha256':graph.get('program',{}).get('executable_sha256'),
        'proof_context':{
            'terrain_ps_ptr_resource_table_sgpr_pair':'s[12:13]',
            'terrain_t14_load':'s_load_dwordx8 ..., s[12:13], 0x70 dwords',
            't14_byte_offset':'0x1C0',
            'pm4_writer':'0xF80210',
        },
        'proof_boundary':'Disassembly proves exact register/call dataflow only. Semantic ownership of the pointer as terrain dyemap requires following its producer back to terrain-owned state.',
        'functions':rows,
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({
        'status':out['status'],
        'functions':[(x['entry_hex'],x['instruction_count'],len(x['calls_of_interest'])) for x in rows],
        'call_sites':[
            {'caller':x['entry_hex'],'call':c['call_address'],'callee':c['callee']}
            for x in rows for c in x['calls_of_interest']
        ],
    },indent=2))

if __name__=='__main__':main()
