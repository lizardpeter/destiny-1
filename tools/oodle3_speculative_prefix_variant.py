#!/usr/bin/env python3
"""Speculative two-literal code-position prediction on original D1 Huffman tables.

Inspired by 2026 research on prediction-based prefix-code decoding, but
optimized here only for exact existing Destiny 1 LZH streams. Predict that
the first Huffman literal has code length 7/8/9, read the next entry at
the predicted bit offset independently of the first table lookup, and
commit two literals iff the prediction and both symbol classes are valid.
On all other paths use the original byte-exact decoder. No extra tables.
"""
import argparse
from pathlib import Path

ANCHOR = """            'fast_decode: while op < output_end && bits.has_fast_margin() {
                let mut symbol = huffman.decode_fast_multi(&mut bits);"""

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--mode",choices=["guess7","guess8","guess9"],required=True)
    args=p.parse_args()
    predicted=int(args.mode.removeprefix("guess"))
    s=args.original.read_text(encoding="utf-8")
    assert s.count(ANCHOR)==1, "expected exactly one optimized literal-loop anchor"
    replacement=f"""            'fast_decode: while op < output_end && bits.has_fast_margin() {{
                // Speculative two-literal decode with an independently indexed
                // second lookup. Only commit when first.len is predicted and
                // both entries encode literals, not match tokens or sentinels.
                if output_end - op >= 2 {{
                    bits.ensure_bits_fast(24);
                    let window = bits.peek_buffered(24) as usize;
                    let first_prefix = window >> (24 - usize::from(FAST_DECODE_BITS));
                    let second_prefix = ((window << {predicted})
                        >> (24 - usize::from(FAST_DECODE_BITS)))
                        & ((1usize << FAST_DECODE_BITS) - 1);
                    let first = unsafe {{ *huffman.fast.get_unchecked(first_prefix) }};
                    let second = unsafe {{ *huffman.fast.get_unchecked(second_prefix) }};
                    if first.len == {predicted}
                        && first.symbol < LITERAL_SYMBOLS as u16
                        && second.len != 0
                        && second.symbol < LITERAL_SYMBOLS as u16
                    {{
                        bits.consume_buffered(
                            usize::from(first.len) + usize::from(second.len)
                        );
                        let two_bytes = u16::from(first.symbol)
                            | (second.symbol << 8);
                        unsafe {{
                            core::ptr::write_unaligned(
                                output.as_mut_ptr().add(op).cast::<u16>(),
                                two_bytes.to_le(),
                            );
                        }}
                        op += 2;
                        continue;
                    }}
                }}
                let mut symbol = huffman.decode_fast_multi(&mut bits);"""
    s=s.replace(ANCHOR,replacement)
    args.output.write_text(s,encoding="utf-8")

if __name__=="__main__":
    main()
