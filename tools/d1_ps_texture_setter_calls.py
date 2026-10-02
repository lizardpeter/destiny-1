#!/usr/bin/env python3
"""Trace exact D1 pixel texture setter call sites, especially slot 14.

Retail closure already establishes:
  0xF8AFD0(state, stage, slot, count, descriptor_ptr)
      -> stage*0x642 + slot*8 dwords
  0x7DF310(ctx, slot, descriptor_ptr)
      -> 0xF8AFD0(stage=1, slot, count=1, descriptor_ptr)

This probe disassembles every direct caller of the known pixel texture setter
wrappers and preserves bounded call contexts, then performs conservative
backward constant tracking for RSI/ESI (slot) and RDX (descriptor source).
"""
from __future__ import annotations

import argparse,gzip,json
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from capstone.x86 import X86_OP_IMM,X86_OP_REG
from d1_executable_probe import parse_elf64_header,parse_elf64_program_headers

TARGETS={
    0x7DF310:"set_ps_texture_descriptor",
    0x7DF250:"resolve_and_set_ps_texture",
    0x7DEF20:"set_stage_texture_switch",
    0x7DE8C0:"set_stage_texture_cached",
}
INTERESTING_SLOT=14

def load(path:Path):
    op=gzip.open if path.suffix=='.gz' else open
    with op(path,'rt',encoding='utf-8') as f:return json.load(f)

def v2f(va,segs):
    for s in segs:
        base=int(s['virtual_address'],16); size=int(s['file_size'])
        if base<=va<base+size:return int(s['absolute_file_offset'])+va-base
    return None

def dis_fn(md,raw,segs,fn):
    out=[]
    for br in fn.get('body_ranges',[]):
        lo=int(br['min'],16); hi=int(br['max'],16)+1
        off=v2f(lo,segs)
        if off is None:continue
        out.extend(md.disasm(raw[off:off+(hi-lo)],lo))
    return out

def row(ins):
    return {'address':ins.address,'address_hex':hex(ins.address),
            'mnemonic':ins.mnemonic,'op_str':ins.op_str}

def direct_call_target(ins):
    if ins.mnemonic!='call' or not ins.operands:return None
    op=ins.operands[0]
    if op.type==X86_OP_IMM:return int(op.imm)&0xffffffffffffffff
    return None

def backward_reg_constant(insns, call_index, reg_names, limit=24):
    """Very conservative local constant recovery for x86 integer arg registers."""
    wanted=set(reg_names)
    for j in range(call_index-1,max(-1,call_index-limit-1),-1):
        ins=insns[j]
        if len(ins.operands)<2:continue
        dst=ins.operands[0]
        if dst.type!=X86_OP_REG:continue
        dst_name=ins.reg_name(dst.reg)
        if dst_name not in wanted:continue
        src=ins.operands[1]
        if ins.mnemonic in ('mov','movabs') and src.type==X86_OP_IMM:
            return {'status':'constant','value':int(src.imm)&0xffffffffffffffff,
                    'source':row(ins)}
        if ins.mnemonic=='xor' and src.type==X86_OP_REG and ins.reg_name(src.reg)==dst_name:
            return {'status':'constant','value':0,'source':row(ins)}
        # Any other write to the argument register makes local constant unknown.
        return {'status':'written_nonconstant','source':row(ins)}
    return {'status':'not_found'}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('executable',type=Path)
    ap.add_argument('--codegraph',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()

    raw=a.executable.read_bytes()
    h=parse_elf64_header(raw);segs=parse_elf64_program_headers(raw,h)
    g=load(a.codegraph)
    funcs={int(f['entry'],16):f for f in g.get('functions',[])}
    caller_entries={t:set() for t in TARGETS}
    for edge in g.get('calls',[]):
        try:caller=int(edge['caller'],16);callee=int(edge['callee'],16)
        except Exception:continue
        if callee in TARGETS:caller_entries[callee].add(caller)

    md=Cs(CS_ARCH_X86,CS_MODE_64);md.detail=True
    calls=[]
    for target,callers in caller_entries.items():
        for entry in sorted(callers):
            fn=funcs.get(entry)
            if not fn:continue
            insns=list(dis_fn(md,raw,segs,fn))
            for i,ins in enumerate(insns):
                if direct_call_target(ins)!=target:continue
                slot=backward_reg_constant(insns,i,{'esi','rsi'})
                descriptor=backward_reg_constant(insns,i,{'rdx','edx'})
                context=[row(x) for x in insns[max(0,i-28):min(len(insns),i+14)]]
                calls.append({
                    'caller_entry':entry,'caller_entry_hex':hex(entry),
                    'caller_name':fn.get('name'),
                    'call_address':ins.address,'call_address_hex':hex(ins.address),
                    'target':target,'target_hex':hex(target),'target_role':TARGETS[target],
                    'slot_local':slot,
                    'descriptor_arg_local':descriptor,
                    'literal_slot14':slot.get('status')=='constant' and slot.get('value')==INTERESTING_SLOT,
                    'context':context,
                })

    calls.sort(key=lambda x:(not x['literal_slot14'],x['target'],x['caller_entry'],x['call_address']))
    out={
      'schema':'d1_ps_texture_setter_calls/v1',
      'status':'D1_PS_TEXTURE_SETTER_CALLS',
      'executable_sha256':g.get('program',{}).get('executable_sha256'),
      'targets':{hex(k):v for k,v in TARGETS.items()},
      'interesting_slot':INTERESTING_SLOT,
      'proof_boundary':'A slot-14 call identifies a retail write to PS PtrResourceTable[14]. Terrain/dyemap ownership still requires tracing the supplied descriptor back to active STerrain state.',
      'call_count':len(calls),
      'literal_slot14_call_count':sum(x['literal_slot14'] for x in calls),
      'calls':calls,
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('calls',len(calls),'literal slot14',out['literal_slot14_call_count'])
    for x in calls:
      print('\nCALLER',x['caller_entry_hex'],'CALL',x['call_address_hex'],'->',x['target_hex'],
            'slot',x['slot_local'])
      if x['literal_slot14']:
        for y in x['context']:print(' ',y['address_hex'],y['mnemonic'],y['op_str'])

if __name__=='__main__':main()
