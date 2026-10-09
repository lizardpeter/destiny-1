#!/usr/bin/env python3
"""Isolate x86-64 MOVBE vs MOV+BSWAP in verified fast 32-bit bit refill."""
import argparse
from pathlib import Path

OLD="            let word = unsafe { u32::from_be(core::ptr::read_unaligned(self.ptr.cast::<u32>())) };"
REPLACE={
"reg_bswap":'''            let mut word = unsafe { core::ptr::read_unaligned(self.ptr.cast::<u32>()) };
            // x86-64 register BSWAP intentionally prevents LLVM from
            // folding the endian transform with the load to MOVBE.
            unsafe {
                core::arch::asm!(
                    "bswap {value:e}",
                    value = inout(reg) word,
                    options(nomem, nostack, preserves_flags),
                );
            }''',
"asm_mem":'''            let word: u32;
            unsafe {
                core::arch::asm!(
                    "mov {value:e}, dword ptr [{source}]",
                    "bswap {value:e}",
                    source = in(reg) self.ptr,
                    value = lateout(reg) word,
                    options(readonly, nostack, preserves_flags),
                );
            }'''
}
def transform(text,mode):
    a=text.index("    fn ensure_bits_fast(")
    b=text.index("    #[inline(always)]\n    fn read_bits_fast(",a)
    fast=text[a:b]
    if fast.count(OLD)!=1:raise RuntimeError("Unexpected fast refill endian-read signature")
    return text[:a]+fast.replace(OLD,REPLACE[mode])+text[b:]

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--mode",choices=tuple(REPLACE),required=True)
    a=p.parse_args()
    result=transform(a.original.read_text(),a.mode)
    a.output.write_text(result)
    print("X86_ENDIAN_REFILL_LOAD_VARIANT",a.mode)
