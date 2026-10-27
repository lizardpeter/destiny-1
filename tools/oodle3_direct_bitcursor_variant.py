#!/usr/bin/env python3
"""Isolated alternate bit reader: overlapped 32-/64-bit cursor loads.

Keep packet/model decode and fully checked tail decoding unchanged.
For payload decoding only, use a bit cursor and a wide overlapped word
loaded on each symbol rather than a rolling reservoir and conditional
refills. Enter this fast loop only with >=16 physical bytes of input margin
so the longest legal match token's <=7 bytes of extra bits cannot overrun
the selected 4-/8-byte load.
"""
import argparse
from pathlib import Path

def once(s, old, new):
    n=s.count(old)
    assert n==1, f"anchor {old[:90]!r}: {n} occurrences"
    return s.replace(old,new)

DIRECT_READER = """#[derive(Debug, Clone, Copy)]
struct DirectBitReader<'a> {
    start: *const u8,
    byte_pos: usize,
    bit_offset: u8,
    input_len: usize,
    marker: core::marker::PhantomData<&'a [u8]>,
}

impl<'a> DirectBitReader<'a> {
    #[inline(always)]
    fn new(input: &'a [u8]) -> Self {
        Self {
            start: input.as_ptr(),
            byte_pos: 0,
            bit_offset: 0,
            input_len: input.len(),
            marker: core::marker::PhantomData,
        }
    }

    #[inline(always)]
    fn has_fast_margin(&self) -> bool {
        self.input_len >= 16 && self.byte_pos <= self.input_len - 16
    }

    #[inline(always)]
    fn ensure_bits_fast(&mut self, count: usize) {
        debug_assert!(count <= 16);
    }

    #[inline(always)]
    fn peek_buffered(&self, count: usize) -> u64 {
        debug_assert!(count > 0 && count <= 16);
        debug_assert!(self.byte_pos + 8 <= self.input_len);
        let ptr = unsafe { self.start.add(self.byte_pos) };
        WORD_READ
        u64::from(aligned >> (WORD_WIDTH - count))
    }

    #[inline(always)]
    fn consume_buffered(&mut self, count: usize) {
        let advanced = usize::from(self.bit_offset) + count;
        self.byte_pos += advanced >> 3;
        self.bit_offset = (advanced & 7) as u8;
    }

    #[inline(always)]
    fn read_bits_fast(&mut self, count: usize) -> u64 {
        if count == 0 { return 0; }
        let result = self.peek_buffered(count);
        self.consume_buffered(count);
        result
    }
}

"""

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--mode",choices=("cursor32","cursor64"),required=True)
    a=p.parse_args()
    s=a.original.read_text(encoding="utf-8")

    if a.mode=="cursor32":
        word = """let word = unsafe { u32::from_be(core::ptr::read_unaligned(ptr.cast::<u32>())) };
        let aligned = word.wrapping_shl(u32::from(self.bit_offset));"""
        width="32"
    else:
        word = """let word = unsafe { u64::from_be(core::ptr::read_unaligned(ptr.cast::<u64>())) };
        let aligned = word.wrapping_shl(u32::from(self.bit_offset));"""
        width="64"
    reader=DIRECT_READER.replace("WORD_READ",word).replace("WORD_WIDTH",width)
    s=once(s, "#[derive(Debug, Clone, Copy)]\nstruct MsbBitReader",
           reader+"#[derive(Debug, Clone, Copy)]\nstruct MsbBitReader")

    start="    #[inline(always)]\n    fn decode_fast_multi(&self, bits: &mut MsbBitReader<'_>) -> usize {"
    stop="    #[inline(always)]\n    fn decode(&self, bits: &mut MsbBitReader<'_>) -> Result<usize, Error> {"
    i=s.index(start)
    j=s.index(stop,i)
    direct=s[i:j].replace("fn decode_fast_multi(&self, bits: &mut MsbBitReader<'_>)",
                           "fn decode_fast_direct(&self, bits: &mut DirectBitReader<'_>)")
    s=s[:i]+direct+s[i:]

    begin="#[inline(always)]\nfn decode_length_parts_fast(\n    bits: &mut MsbBitReader<'_>,"
    end="#[inline(always)]\nfn decode_length_parts(\n    bits: &mut MsbBitReader<'_>,"
    i=s.index(begin)
    j=s.index(end,i)
    direct=s[i:j].replace("fn decode_length_parts_fast(", "fn decode_length_parts_direct(").replace(
        "bits: &mut MsbBitReader<'_>", "bits: &mut DirectBitReader<'_>")
    s=s[:i]+direct+s[i:]

    s=once(s,
           "        let mut bits = MsbBitReader::new(&payload[payload_offset..]);\n        let start_pos",
           "        let fast_payload = &payload[payload_offset..];\n"
           "        let mut bits = MsbBitReader::new(fast_payload);\n"
           "        let mut direct_bits = DirectBitReader::new(fast_payload);\n"
           "        let start_pos")

    start="        if huffman.one_char.is_none() {\n            'fast_decode: while op < output_end && bits.has_fast_margin() {"
    end="        // Only the final input-boundary region uses the fully checked reader."
    i=s.index(start)
    j=s.index(end,i)
    seg=s[i:j]
    assert seg.count("bits.has_fast_margin()")==2
    assert seg.count("huffman.decode_fast_multi(&mut bits)")==2
    assert seg.count("bits.read_bits_fast(")==2
    assert seg.count("decode_length_parts_fast(")==1
    seg=seg.replace("bits.has_fast_margin()", "direct_bits.has_fast_margin()")
    seg=seg.replace("huffman.decode_fast_multi(&mut bits)", "huffman.decode_fast_direct(&mut direct_bits)")
    seg=seg.replace("bits.read_bits_fast(", "direct_bits.read_bits_fast(")
    seg=seg.replace("decode_length_parts_fast(\n                    &mut bits,",
                    "decode_length_parts_direct(\n                    &mut direct_bits,")
    s=s[:i]+seg+s[j:]
    tail="""        // Resume the original fully checked reservoir at the exact bit offset.
        // Reconstruct it only once, after the direct-cursor payload fast path.
        bits.ptr = unsafe { bits.start.add(direct_bits.byte_pos) };
        if direct_bits.bit_offset != 0 {
            bits.read_bits(usize::from(direct_bits.bit_offset))?;
        }

"""
    s=once(s,end,tail+end)
    assert "huffman.decode_fast_direct(&mut direct_bits)" in s
    assert "decode_length_parts_direct(\n                    &mut direct_bits," in s
    a.output.write_text(s,encoding="utf-8")

if __name__=="__main__":
    main()
