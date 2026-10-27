#!/usr/bin/env python3
"""Experimental predicated Huffman refill, reducing an inner-loop dependency.

Only decode_fast_multi calls this method, which is reached exclusively after
a fast-margin check ensuring >=8 input bytes are available. All match extra
bits and checked tail decode retain the original reader. The unconditional
32-bit load is masked out when no refill is needed; the bit count/pointer
advance are predicated. Two spellings permit compiler A/B benchmarking.
"""
import argparse
from pathlib import Path

ANCHOR = """        bits.ensure_bits_fast(usize::from(FAST_DECODE_BITS));
        let prefix = bits.peek_buffered(usize::from(FAST_DECODE_BITS)) as usize;"""
BEFORE = """    #[inline(always)]
    fn read_bits_fast(&mut self, count: usize) -> u64 {"""

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--mode",choices=["mask","select"],required=True)
    a=p.parse_args()
    s=a.original.read_text(encoding="utf-8")
    assert s.count(ANCHOR)==1
    assert s.count(BEFORE)==1
    if a.mode=="mask":
        update="""        let mask = 0u64.wrapping_sub(need as u64);
        self.bit_buf |= (u64::from(word) << shift) & mask;"""
    else:
        update="""        let contribution = if need != 0 {
            u64::from(word) << shift
        } else {
            0
        };
        self.bit_buf |= contribution;"""
    meth="""    #[inline(always)]
    fn ensure_huffman_bits_predicated(&mut self, count: usize) {
        // Called only when has_fast_margin() was true (>=8 input bytes).
        debug_assert!(count <= 16);
        debug_assert!(self.has_fast_margin());
        let need = (usize::from(self.bit_count) < count) as usize;
        let word = unsafe {
            u32::from_be(core::ptr::read_unaligned(self.ptr.cast::<u32>()))
        };
        // When need==0 the shift is intentionally immaterial; modulo 64
        // prevents any underflow/invalid-shift on a nearly full reservoir.
        let shift = 32usize.wrapping_sub(usize::from(self.bit_count)) & 63;
UPDATE
        self.ptr = unsafe { self.ptr.add(need * 4) };
        self.bit_count += (need * 32) as u8;
    }

""".replace("UPDATE",update)
    s=s.replace(BEFORE,meth+BEFORE)
    s=s.replace(ANCHOR,ANCHOR.replace("bits.ensure_bits_fast","bits.ensure_huffman_bits_predicated"))
    a.output.write_text(s,encoding="utf-8")

if __name__=="__main__":
    main()
