#!/usr/bin/env python3
"""Build an isolated alternative 4-byte Huffman entry representation.

Source-to-source transformations are deliberately strict: fail instead of
silently benchmarking an unmodified or partly modified variant.
"""
import argparse
from pathlib import Path

def transform(source: str, layout: str) -> str:
    start = source.index("#[derive(Debug, Clone, Copy, Default)]\nstruct FastEntry {")
    stop = source.index("\n#[derive(Debug, Clone)]\nstruct CanonicalDecoder", start)
    old_struct = source[start:stop]
    expected_struct = "#[derive(Debug, Clone, Copy, Default)]\nstruct FastEntry {\n    symbol: u16,\n    len: u8,\n}"
    if old_struct != expected_struct:
        raise RuntimeError("Unexpected FastEntry definition")
    source = source[:start] + old_struct.replace(
        "    symbol: u16,\n    len: u8,", "    packed: u32,"
    ) + source[stop:]
    initializer = """let entry = FastEntry {
                    symbol: symbol as u16,
                    len,
                };"""
    if source.count(initializer) != 1:
        raise RuntimeError("Unexpected Huffman fast entry initializer")
    if layout == "length_high":
        expr = "((len as u32) << 16) | (symbol as u32)"
        len_expr = "((entry.packed >> 16) as u8)"
        sym_expr = "((entry.packed & 0xffff) as u16)"
    elif layout == "length_low":
        expr = "((symbol as u32) << 8) | (len as u32)"
        len_expr = "((entry.packed & 0xff) as u8)"
        sym_expr = "((entry.packed >> 8) as u16)"
    else:
        raise RuntimeError("Unexpected variant " + layout)
    source = source.replace(initializer, "let entry = FastEntry { packed: " + expr + " };")
    begin = source.index("impl CanonicalDecoder {")
    end = source.index("\n#[derive(Debug, Clone)]\npub struct Decoder", begin)
    block = source[begin:end]
    if block.count("entry.len") != 4 or block.count("entry.symbol") != 2:
        raise RuntimeError(f"Unexpected fast lookup references: len={block.count('entry.len')} symbol={block.count('entry.symbol')}")
    block = block.replace("entry.len", len_expr).replace("entry.symbol", sym_expr)
    source = source[:begin] + block + source[end:]
    if "entry.len" in block or "entry.symbol" in block:
        raise RuntimeError("Incomplete replacement")
    return source

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--original", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--layout", choices=("length_high", "length_low"), required=True)
    args = ap.parse_args()
    result = transform(args.original.read_text(), args.layout)
    args.output.write_text(result)
    print("HUFFMAN_ENTRY_PACKING_APPLIED", args.layout, len(result))
