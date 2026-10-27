#!/usr/bin/env python3
"""Research-inspired 14/16-bit dual-literal superinstruction experiments.

For each accepted canonical Huffman model, enumerate all literal-literal
codeword pairs with combined length <= N; materialize packed lookup entries
that emit both bytes with a single unaligned little-endian store. On a
miss, execute the exact original 11-bit decoder and match-token path.
This is NOT an implementation of PivCo's changed wire format.
"""
import argparse
from pathlib import Path

def once(s, a, b):
    n=s.count(a)
    assert n==1, f"expected one anchor, got {n}: {a[:90]!r}"
    return s.replace(a,b)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--mode", choices=["pairs14","pairs16"], required=True)
    a=p.parse_args()
    n=int(a.mode.removeprefix("pairs"))
    s=a.original.read_text(encoding="utf-8")
    s=once(s, "pub const FAST_DECODE_BITS: u8 = 11;",
      f"pub const FAST_DECODE_BITS: u8 = 11;\nconst PAIR_DECODE_BITS: usize = {n};")
    s=once(s,
      "    fast: [FastEntry; 1 << FAST_DECODE_BITS],\n    max_len: u8,",
      "    fast: [FastEntry; 1 << FAST_DECODE_BITS],\n    literal_pairs: Vec<u32>,\n    max_len: u8,")
    s=once(s,
      "            fast: [FastEntry::default(); 1 << FAST_DECODE_BITS],\n            max_len: 0,",
      "            fast: [FastEntry::default(); 1 << FAST_DECODE_BITS],\n            literal_pairs: vec![0u32; 1 << PAIR_DECODE_BITS],\n            max_len: 0,")
    s=once(s,
      "        self.symbols.clear();\n        // Every accepted multi-symbol model is Kraft-complete.",
      "        self.symbols.clear();\n        self.literal_pairs.fill(0);\n        // Every accepted multi-symbol model is Kraft-complete.")
    s=once(s,
      "        let mut next_symbol = self.first_symbol;\n        let mut next_code = self.first_code;",
      "        let mut next_symbol = self.first_symbol;\n        let mut next_code = self.first_code;\n        let mut literal_codes = [0u16; LITERAL_SYMBOLS];\n        let mut literal_lens = [0u8; LITERAL_SYMBOLS];")
    s=once(s,
      "                let code = next_code[len_index];\n                next_code[len_index] += 1;",
      "                let code = next_code[len_index];\n                next_code[len_index] += 1;\n                if symbol < LITERAL_SYMBOLS {\n                    literal_codes[symbol] = code as u16;\n                    literal_lens[symbol] = len;\n                }")
    s=once(s,
      """        Ok(())
    }

    #[inline(always)]
    fn decode_fast_multi(&self, bits: &mut MsbBitReader<'_>) -> usize {""",
      """        // Expand only pairs of literal codewords with a combined prefix
        // length that fits the direct table. Each table entry is a full
        // two-symbol transition (two output bytes + total bits consumed).
        for first in 0..LITERAL_SYMBOLS {
            let first_len = usize::from(literal_lens[first]);
            if first_len == 0 || first_len >= PAIR_DECODE_BITS {
                continue;
            }
            for second in 0..LITERAL_SYMBOLS {
                let second_len = usize::from(literal_lens[second]);
                let combined_len = first_len + second_len;
                if second_len == 0 || combined_len > PAIR_DECODE_BITS {
                    continue;
                }
                let combined_code = (usize::from(literal_codes[first]) << second_len)
                    | usize::from(literal_codes[second]);
                let shift = PAIR_DECODE_BITS - combined_len;
                let start = combined_code << shift;
                let end = start + (1usize << shift);
                debug_assert!(end <= self.literal_pairs.len());
                let packed = ((combined_len as u32) << 16)
                    | ((second as u32) << 8)
                    | first as u32;
                self.literal_pairs[start..end].fill(packed);
            }
        }

        Ok(())
    }

    #[inline(always)]
    fn decode_fast_multi(&self, bits: &mut MsbBitReader<'_>) -> usize {""")
    s=once(s,
      """            'fast_decode: while op < output_end && bits.has_fast_margin() {
                let mut symbol = huffman.decode_fast_multi(&mut bits);""",
      """            'fast_decode: while op < output_end && bits.has_fast_margin() {
                // Decode two common literals as one superinstruction when the
                // 14/16-bit prefix contains two complete literal codewords.
                // Everything else falls through to the original decoder.
                if output_end - op >= 2 {
                    bits.ensure_bits_fast(PAIR_DECODE_BITS);
                    let prefix = bits.peek_buffered(PAIR_DECODE_BITS) as usize;
                    let packed = unsafe { *huffman.literal_pairs.get_unchecked(prefix) };
                    if packed != 0 {
                        bits.consume_buffered((packed >> 16) as usize);
                        unsafe {
                            core::ptr::write_unaligned(
                                output.as_mut_ptr().add(op).cast::<u16>(),
                                (packed as u16).to_le(),
                            );
                        }
                        op += 2;
                        continue;
                    }
                }
                let mut symbol = huffman.decode_fast_multi(&mut bits);""")
    a.output.write_text(s, encoding="utf-8")

if __name__=="__main__":
    main()
