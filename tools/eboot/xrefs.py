#!/usr/bin/env python3
"""Whole-program xrefs from exact FDE function ranges (capstone, linear sweep per function).

Writes:
  calls.tsv  caller_fn  callee_va  kind(call|jmp|tail)
  drefs.tsv  fn  target_va           (RIP-relative data refs: lea/mov/etc.)
usage: xrefs.py EBOOT META_DIR OUT_DIR
"""
import bisect, os, sys
from capstone import Cs, CS_ARCH_X86, CS_MODE_64
from capstone.x86 import X86_OP_IMM, X86_OP_MEM, X86_REG_RIP

def main(eboot, meta, out):
    d = open(eboot, 'rb').read()
    os.makedirs(out, exist_ok=True)
    fns = [tuple(int(x, 16) for x in l.split()) for l in open(f'{meta}/functions.tsv')]
    starts = [s for s, _ in fns]
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    md.detail = True
    md.skipdata = True
    calls, drefs, bad = open(f'{out}/calls.tsv', 'w'), open(f'{out}/drefs.tsv', 'w'), 0
    for n, (s, z) in enumerate(fns):
        code = d[s + 0x4000: s + 0x4000 + z]
        for ins in md.disasm(code, s):
            if ins.id == 0:
                bad += 1
                continue
            m = ins.mnemonic
            for op in ins.operands:
                if op.type == X86_OP_IMM and (m == 'call' or m.startswith('j')):
                    t = op.imm
                    if m == 'call':
                        calls.write(f'{s:x}\t{t:x}\tcall\n')
                    elif not (s <= t < s + z):
                        calls.write(f'{s:x}\t{t:x}\t{"tail" if m == "jmp" else "jcc"}\n')
                elif op.type == X86_OP_MEM and op.mem.base == X86_REG_RIP:
                    t = ins.address + ins.size + op.mem.disp
                    if m in ('call', 'jmp'):
                        calls.write(f'{s:x}\t{t:x}\t{m}_ind\n')
                    else:
                        drefs.write(f'{s:x}\t{t:x}\n')
        if n % 5000 == 0:
            print(n, file=sys.stderr)
    print('undecodable bytes groups:', bad)


if __name__ == '__main__':
    main(*sys.argv[1:4])
