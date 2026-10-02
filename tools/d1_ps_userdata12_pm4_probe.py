#!/usr/bin/env python3
"""Exact D1 eboot probe for PS PtrResourceTable user-data binding.

For the proven terrain PS families:
  PtrResourceTable -> PS user SGPR 12
  PS USER_DATA_0 register = 0xB030
  USER_DATA_12 register   = 0xB060
  SI_SH_REG_OFFSET        = 0xB000
  SET_SH_REG register index = (0xB060 - 0xB000) / 4 = 0x18

A direct 64-bit pointer write through a GNM-style helper emits:
  dword0 = PKT3(SET_SH_REG=0x76, count=2, predicate=0) = 0xC0027600
  dword1 = 0x18
  dword2 = pointer_lo
  dword3 = pointer_hi

This tool finds exact executable functions constructing that PM4 shape. It also
reports raw contiguous header/register pairs. A hit proves PS user-data-12
binding machinery, not terrain/dyemap ownership by itself.
"""
from __future__ import annotations

import argparse,bisect,gzip,json,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from capstone.x86 import X86_OP_IMM,X86_OP_MEM

from d1_executable_probe import parse_elf64_header,parse_elf64_program_headers

HEADER=0xC0027600
REG_INDEX=0x18
COMBINED=(REG_INDEX<<32)|HEADER


def load_json(path):
    opener=gzip.open if path.suffix=='.gz' else open
    with opener(path,'rt',encoding='utf-8') as f:return json.load(f)

def v2f(va,segments):
    for seg in segments:
        base=int(seg['virtual_address'],16); size=int(seg['file_size'])
        if base<=va<base+size:return int(seg['absolute_file_offset'])+va-base
    return None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('executable',type=Path)
    ap.add_argument('--codegraph',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()

    raw=args.executable.read_bytes()
    h=parse_elf64_header(raw)
    segments=parse_elf64_program_headers(raw,h)
    graph=load_json(args.codegraph)

    pair=struct.pack('<II',HEADER,REG_INDEX)
    raw_pairs=[]
    start=0
    while True:
        i=raw.find(pair,start)
        if i<0:break
        raw_pairs.append(i);start=i+1

    md=Cs(CS_ARCH_X86,CS_MODE_64);md.detail=True
    candidates=[]
    for fn in graph.get('functions',[]):
        entry=int(fn['entry'],16)
        instructions=[]
        for body in fn.get('body_ranges',[]):
            lo=int(body['min'],16);hi=int(body['max'],16)+1
            off=v2f(lo,segments)
            if off is None:continue
            for ins in md.disasm(raw[off:off+(hi-lo)],lo):
                imms=[]
                for op in ins.operands:
                    if op.type==X86_OP_IMM:
                        imms.append(int(op.imm)&0xffffffffffffffff)
                instructions.append({
                    'address':ins.address,'address_hex':hex(ins.address),
                    'mnemonic':ins.mnemonic,'op_str':ins.op_str,'immediates':imms,
                })
        header_idxs=[i for i,x in enumerate(instructions) if HEADER in x['immediates']]
        combined_idxs=[i for i,x in enumerate(instructions) if COMBINED in x['immediates']]
        if not header_idxs and not combined_idxs:continue
        neighborhoods=[]
        score=0
        for i in sorted(set(header_idxs+combined_idxs)):
            lo=max(0,i-12);hi=min(len(instructions),i+20)
            ctx=instructions[lo:hi]
            has_reg=any(REG_INDEX in x['immediates'] for x in ctx)
            has_header=any(HEADER in x['immediates'] for x in ctx)
            has_combined=any(COMBINED in x['immediates'] for x in ctx)
            stores=[
                x for x in ctx
                if x['mnemonic'].startswith('mov') and '[' in x['op_str']
            ]
            local_score=100
            if has_reg: local_score+=120
            if has_combined: local_score+=180
            if len(stores)>=2: local_score+=20
            score=max(score,local_score)
            neighborhoods.append({
                'center':instructions[i]['address_hex'],
                'has_header':has_header,'has_register_index_0x18':has_reg,
                'has_combined_qword':has_combined,
                'instructions':ctx,
            })
        candidates.append({
            'entry':entry,'entry_hex':hex(entry),'name':fn.get('name'),
            'instruction_count':fn.get('instruction_count'),
            'score':score,'neighborhoods':neighborhoods,
            'called_function_entries':fn.get('called_function_entries',[]),
        })

    candidates.sort(key=lambda x:(-x['score'],x['entry']))
    out={
        'schema':'d1_ps_userdata12_pm4_probe/v1',
        'status':'D1_PS_USERDATA12_PM4_FRONTIER',
        'constants':{
            'set_sh_reg_header_hex':hex(HEADER),
            'ps_userdata12_register':'0xB060',
            'sh_register_base':'0xB000',
            'set_sh_reg_index_hex':hex(REG_INDEX),
            'combined_qword_hex':hex(COMBINED),
        },
        'proof_boundary':'Hits prove construction/use of the PM4 shape for a two-dword PS user-data-12 write. They do not by themselves identify the pointer as terrain or T14.',
        'raw_contiguous_pair_file_offsets':raw_pairs,
        'candidate_count':len(candidates),
        'candidates':candidates,
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({
        'status':out['status'],'raw_pair_count':len(raw_pairs),
        'candidate_count':len(candidates),
        'top':[{'entry':x['entry_hex'],'score':x['score'],'ins':x['instruction_count']} for x in candidates[:40]]
    },indent=2))

if __name__=='__main__':main()
