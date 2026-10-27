#!/usr/bin/env python3
"""Generate byte-exact experimental pre-refill threshold variants.

On the usual 11-bit primary Huffman lookup, opportunistically ensure N
buffered bits before the table access. The 32-bit refill and long-code
decoder are unchanged. N must remain 11..32 as required by MsbBitReader.
"""
from pathlib import Path
import argparse

ANCHOR = """        bits.ensure_bits_fast(usize::from(FAST_DECODE_BITS));
        let prefix = bits.peek_buffered(usize::from(FAST_DECODE_BITS)) as usize;"""

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--mode",required=True,choices=["preload14","preload15","preload16","preload20","preload24"])
    a=p.parse_args()
    count=int(a.mode.removeprefix("preload"))
    source=a.original.read_text(encoding="utf-8")
    assert source.count(ANCHOR)==1
    variant=source.replace(ANCHOR,f"""        // Experimental: keep {count} prefix bits ready for next symbol.
        bits.ensure_bits_fast({count});
        let prefix = bits.peek_buffered(usize::from(FAST_DECODE_BITS)) as usize;""")
    a.output.write_text(variant,encoding="utf-8")

if __name__=="__main__":
    main()
