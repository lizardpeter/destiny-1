#!/usr/bin/env python3
"""Trace exact D1 calls to the generic pointer-user-data PM4 helper.

The exact eboot probe identified 0xF80210 as the sole constructor of a
4-dword SET_SH_REG packet carrying a 64-bit pointer.  Its only direct callers
in the Ghidra call graph are 0xF8D880 and 0xF8DF60.

This tool disassembles those functions and preserves call-site neighborhoods so
the System V argument values (stage, user-data slot, pointer source) can be
recovered without assigning names by guess.
"""
from __future__ import annotations
import argparse,gzip,json
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from capstone.x86 import X86_OP_IMM
from d1_executable_probe import parse_elf64_header,parse_elf64_program_headers

TARGET=0xF80210
CALLEE_REGISTER=0xF83520

def load(path):
    opener=gzip.open if path.suffix=='.gz' else open
    with opener(path,'rt',encoding='utf-8') as f:return json.load(f)

def v2f(va,segs):
    for s in segs:
        b=int(s['virtual_address'],16); n=int(s['file_size'])
        if b<=va<b+n:return int(s['absolute_file_offset'])+va-b
    return None

def dis_fn(raw,segs,fn):
    md=Cs(CS_ARCH_X86,CS_MODE_64);md.detail=True
    out=[]
    for body in fn.get('body_ranges',[]):
        lo=int(body['min'],16); hi=int(body['max'],16)+1
        off=v2f(lo,segs)
        if off is None:continue
        for ins in md.disasm(raw[off:off+(hi-lo)],lo):
            imms=[int(op.imm)&0xffffffffffffffff for op in ins.operands if op.type==X86_OP_IMM]
            out.append({'address':ins.address,'address_hex':hex(ins.address),'mnemonic':ins.mnemonic,'op_str':ins.op_str,'immediates':imms})
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('executable',type=Path)
    ap.add_argument('--codegraph',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    raw=a.executable.read_bytes(); h=parse_elf64_header(raw); segs=parse_elf64_program_headers(raw,h)
    g=load(a.codegraph)
    by={int(f['entry'],16):f for f in g.get('functions',[])}
    callers={}
    for e in g.get('calls',[]):
        x=int(e['caller'],16); y=int(e['callee'],16); callers.setdefault(y,set()).add(x)
    entries=[TARGET,CALLEE_REGISTER]+sorted(callers.get(TARGET,set()))
    rows=[]
    for entry in entries:
        fn=by[entry]; ins=dis_fn(raw,segs,fn)
        sites=[]
        for i,x in enumerate(ins):
            if TARGET in x['immediates']:
                sites.append({'call_index':i,'call':x,'before':ins[max(0,i-28):i],'after':ins[i+1:min(len(ins),i+12)]})
        rows.append({'entry':entry,'entry_hex':hex(entry),'name':fn.get('name'),'prototype':fn.get('prototype'),'instruction_count':len(ins),'call_sites_to_target':sites,'instructions':ins,'caller_entries':[hex(x) for x in sorted(callers.get(entry,set()))],'called_function_entries':fn.get('called_function_entries',[])})
    out={'schema':'d1_ps_userdata_pointer_callers/v1','status':'D1_PS_USERDATA_POINTER_CALLERS','target':hex(TARGET),'target_callers':[hex(x) for x in sorted(callers.get(TARGET,set()))],'functions':rows}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':out['status'],'target_callers':out['target_callers'],'sites':[{r['entry_hex']:len(r['call_sites_to_target'])} for r in rows]},indent=2))
    for r in rows:
        for site in r['call_sites_to_target']:
            print('\nCALLER',r['entry_hex'],'at',site['call']['address_hex'])
            for x in site['before'][-20:]+[site['call']]+site['after'][:6]:
                print(x['address_hex'],x['mnemonic'],x['op_str'])

if __name__=='__main__':main()
