#!/usr/bin/env python3
"""Trace exact D1 resource-table state setter functions.

This is a focused exact-build disassembly helper for the graphics state API
cluster that owns the 0x642-dword per-stage shader-state shadow. It preserves
full instructions for a small fixed set of functions plus their exact callers.
No semantic names are promoted solely from this trace.
"""
from __future__ import annotations
import argparse,gzip,json
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from capstone.x86 import X86_OP_IMM,X86_OP_MEM
from d1_executable_probe import parse_elf64_header,parse_elf64_program_headers

TARGETS={0xF8AFD0,0xF8B0C0,0xF8B1F0,0xF8B2E0,0xF8B410,0xF8B500,0xF8B600}
CALLERS={0x7DC270,0x7DD6A0,0x7DE8C0,0x7DEF20,0x7DF250,0x7DF310,
         0x7E0040,0x7E05C0,0x7E08A0,0x7E0AE0,0x7E1110,0x7E1510,
         0x7E1960,0x7E1D10,0x7E2480,0x7E2B50,0x7E2CB0}

def load(path):
    op=gzip.open if path.suffix=='.gz' else open
    with op(path,'rt',encoding='utf-8') as f:return json.load(f)

def v2f(va,segs):
    for s in segs:
        base=int(s['virtual_address'],16); size=int(s['file_size'])
        if base<=va<base+size:
            return int(s['absolute_file_offset'])+va-base
    return None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('executable',type=Path)
    ap.add_argument('--codegraph',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    raw=a.executable.read_bytes()
    h=parse_elf64_header(raw); segs=parse_elf64_program_headers(raw,h)
    g=load(a.codegraph)
    funcs={int(f['entry'],16):f for f in g.get('functions',[])}
    md=Cs(CS_ARCH_X86,CS_MODE_64); md.detail=True
    rows=[]
    for entry in sorted(TARGETS|CALLERS):
        f=funcs.get(entry)
        if not f: continue
        insns=[]
        for br in f.get('body_ranges',[]):
            lo=int(br['min'],16); hi=int(br['max'],16)+1
            off=v2f(lo,segs)
            if off is None: continue
            for ins in md.disasm(raw[off:off+(hi-lo)],lo):
                imms=[]; mem=[]
                for op in ins.operands:
                    if op.type==X86_OP_IMM:
                        imms.append(int(op.imm)&0xffffffffffffffff)
                    elif op.type==X86_OP_MEM:
                        mem.append({
                          'base':ins.reg_name(op.mem.base) if op.mem.base else None,
                          'index':ins.reg_name(op.mem.index) if op.mem.index else None,
                          'scale':op.mem.scale,'disp':op.mem.disp,
                        })
                insns.append({
                  'address':ins.address,'address_hex':hex(ins.address),
                  'mnemonic':ins.mnemonic,'op_str':ins.op_str,
                  'immediates':[hex(x) for x in imms],'memory':mem,
                })
        calls=[]
        for i,x in enumerate(insns):
            if x['mnemonic']!='call': continue
            vals=[int(v,16) for v in x['immediates']]
            tgt=vals[0] if vals else None
            if tgt in TARGETS:
                calls.append({
                  'address':x['address'],'address_hex':x['address_hex'],
                  'target':tgt,'target_hex':hex(tgt),
                  'context':insns[max(0,i-20):min(len(insns),i+12)]
                })
        rows.append({
          'entry':entry,'entry_hex':hex(entry),'name':f.get('name'),
          'instruction_count':len(insns),'is_target':entry in TARGETS,
          'instructions':insns,'calls_to_target_setters':calls,
        })
    out={
      'schema':'d1_resource_shadow_api_trace/v1',
      'status':'D1_RESOURCE_SHADOW_API_TRACE',
      'executable_sha256':g.get('program',{}).get('executable_sha256'),
      'known_layout':{
        'per_stage_stride_dwords':'0x642',
        'ptr_resource_table_api_slot_0_base_dword':'0x0',
        'texture_descriptor_dwords':8,
        'terrain_t14_dword_offset':'0x70',
      },
      'proof_boundary':'Disassembly records exact state-setter arithmetic/call arguments only. Terrain ownership requires a source pointer tied to active STerrain effective dyemap.',
      'functions':rows,
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('functions',len(rows))
    for row in rows:
        if row['is_target']:
            print('\nTARGET',row['entry_hex'],row['name'],'ins',row['instruction_count'])
            for x in row['instructions']:
                if '0x642' in x['op_str'] or '0x70' in x['op_str'] or '0x20' in x['op_str']:
                    print(' ',x['address_hex'],x['mnemonic'],x['op_str'])
        for c in row['calls_to_target_setters']:
            print('\nCALL',row['entry_hex'],c['address_hex'],'->',c['target_hex'])
            for x in c['context']:
                print(' ',x['address_hex'],x['mnemonic'],x['op_str'])

if __name__=='__main__':main()
