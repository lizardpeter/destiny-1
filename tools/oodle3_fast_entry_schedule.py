#!/usr/bin/env python3
"""Isolated code scheduling experiments for the most common Huffman lookup.

These changes keep the 11-bit fast table and canonical long-code fallback
unchanged; entry.len==0 never consumes buffered bits.
"""
import argparse
from pathlib import Path

FAST_OLD = """        let entry = unsafe { *self.fast.get_unchecked(prefix) };
        if entry.len != 0 {
            #[cfg(feature = "profile")]
            profile::huffman_fast();
            bits.consume_buffered(usize::from(entry.len));
            return usize::from(entry.symbol);
        }
"""
FAST_EAGER = """        let entry = unsafe { *self.fast.get_unchecked(prefix) };
        let length = usize::from(entry.len);
        // Consume early to shorten the next-symbol recurrence. A zero-length
        // long-code sentinel consumes exactly zero bits.
        bits.consume_buffered(length);
        if entry.len != 0 {
            #[cfg(feature = "profile")]
            profile::huffman_fast();
            return usize::from(entry.symbol);
        }
"""
FAST_MANUAL = """        let entry = unsafe { *self.fast.get_unchecked(prefix) };
        // A filled 11-bit fast entry has 1..=11 bits; a long-code
        // fallback sentinel has len=0. ensure_bits_fast guarantees
        // bit_count >= 11, so both operations are exact.
        bits.bit_buf <<= usize::from(entry.len);
        bits.bit_count -= entry.len;
        if entry.len != 0 {
            #[cfg(feature = "profile")]
            profile::huffman_fast();
            return usize::from(entry.symbol);
        }
"""
FAST_SPECULATE = """        let entry = unsafe { *self.fast.get_unchecked(prefix) };
        // Start table-dependent consumption before testing the sentinel.
        // An entry with len=0 is a no-op, preserving the long-code path.
        bits.bit_buf = bits.bit_buf.wrapping_shl(u32::from(entry.len));
        bits.bit_count = bits.bit_count.wrapping_sub(entry.len);
        if entry.len != 0 {
            #[cfg(feature = "profile")]
            profile::huffman_fast();
            return usize::from(entry.symbol);
        }
"""
MODES={"eager":FAST_EAGER,"manual":FAST_MANUAL,"speculate":FAST_SPECULATE}
def transform(src, mode):
    start=src.index("    fn decode_fast_multi(")
    stop=src.index("    fn decode(&self, bits:",start)
    part=src[start:stop]
    if part.count(FAST_OLD)!=1:
        raise RuntimeError("Decoder fast lookup diverged from verified source")
    return src[:start]+part.replace(FAST_OLD,MODES[mode])+src[stop:]

if __name__ == "__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--original",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--mode",choices=tuple(MODES),required=True)
    a=ap.parse_args()
    result=transform(a.original.read_text(),a.mode)
    a.output.write_text(result)
    print("HUFFMAN_ENTRY_SCHEDULE_APPLIED",a.mode,len(result))
