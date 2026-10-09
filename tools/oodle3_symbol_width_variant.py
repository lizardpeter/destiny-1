#!/usr/bin/env python3
"""Test narrow u16/u32 Huffman fast symbol values without changing decoding."""
import argparse
from pathlib import Path

def transform(src,typ):
    a=src.index("    fn decode_fast_multi(&self, bits: &mut MsbBitReader<'_>) -> usize {")
    b=src.index("    #[inline(always)]\n    fn decode(&self, bits:",a)
    func=src[a:b]
    head=func.replace("-> usize {",f"-> {typ} {{",1)
    if head.count("return usize::from(entry.symbol);")!=1 or head.count("return usize::from(symbol);")!=1:
        raise RuntimeError("Unexpected fast Huffman return sites")
    head=head.replace("return usize::from(entry.symbol);",f"return {typ}::from(entry.symbol);")
    head=head.replace("return usize::from(symbol);",f"return {typ}::from(symbol);")
    src=src[:a]+head+src[b:]
    p=src.index("        if huffman.one_char.is_none() {")
    q=src.index("        // Only the final input-boundary region",p)
    body=src[p:q]
    if body.count("symbol - LITERAL_SYMBOLS")!=1:raise RuntimeError("Expected one token meta lookup")
    body=body.replace("symbol - LITERAL_SYMBOLS","(symbol as usize) - LITERAL_SYMBOLS")
    body=body.replace("symbol < LITERAL_SYMBOLS + RECENT_TOKEN_COUNT",f"symbol < (LITERAL_SYMBOLS + RECENT_TOKEN_COUNT) as {typ}")
    body=body.replace("symbol < LITERAL_SYMBOLS",f"symbol < LITERAL_SYMBOLS as {typ}")
    body=body.replace("symbol < SYMBOL_COUNT",f"symbol < SYMBOL_COUNT as {typ}")
    # Ensure every unmodified recent-token bound has been replaced.
    if "symbol < LITERAL_SYMBOLS +" in body: raise RuntimeError("Unconverted bound")
    return src[:p]+body+src[q:]

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--width",choices=("u16","u32"),required=True)
    a=p.parse_args()
    result=transform(a.original.read_text(),a.width)
    a.output.write_text(result)
    print("FAST_SYMBOL_WIDTH_VARIANT",a.width)
