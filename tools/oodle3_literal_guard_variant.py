#!/usr/bin/env python3
"""Replace per-literal fast-path margins with a conservative literal budget.

Each Huffman fast lookup consumes at most two 4-byte refills; budgeting eight
input bytes per symbol guarantees all speculative fast-input accesses remain
within the compressed stream. The original boundary path stays untouched.
"""
import argparse
from pathlib import Path

def transform(src: str, window: int):
    if window not in (4, 8):
        raise ValueError("Only 4- and 8-literal budgets are supported")
    start=src.index("'fast_decode: while op < output_end && bits.has_fast_margin() {")
    end=src.index("                debug_assert!(symbol < SYMBOL_COUNT);", start)
    block=src[start:end]
    anchor="                while symbol < LITERAL_SYMBOLS {"
    if block.count(anchor)!=1:
        raise RuntimeError("Literal-only loop changed")
    block=block.replace(anchor,"                let mut literal_budget = 0usize;\n"+anchor)
    check="""                    if op >= output_end || !bits.has_fast_margin() {
                        break 'fast_decode;
                    }
                    symbol = huffman.decode_fast_multi(&mut bits);"""
    if block.count(check)!=1:
        raise RuntimeError("Original literal margin guard changed")
    substitute="""                    if literal_budget == 0 {
                        if op >= output_end || !bits.has_fast_margin() {
                            break 'fast_decode;
                        }
                        // Every lookup consumes at most 8 whole bytes.
                        // Do not skip any check when close to either end.
                        literal_budget = (bits.bytes_remaining() / 8)
                            .min(output_end - op)
                            .min(WINDOW);
                        debug_assert!(literal_budget > 0);
                    }
                    literal_budget -= 1;
                    symbol = huffman.decode_fast_multi(&mut bits);""".replace("WINDOW",str(window))
    block=block.replace(check,substitute)
    return src[:start]+block+src[end:]
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--window",type=int,choices=(4,8),required=True)
    args=p.parse_args()
    modified=transform(args.original.read_text(),args.window)
    args.output.write_text(modified)
    print("LITERAL_BUDGET_VARIANT_APPLIED",args.window)
