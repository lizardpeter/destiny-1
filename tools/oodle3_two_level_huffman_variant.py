#!/usr/bin/env python3
"""Isolated two-level Huffman table experiments for Destiny LZH.

Replace the canonical >N-bit fallback scan with one indexed secondary
decode table of 2^(16-N) entries for each populated long-code prefix.
The checked tail decoder remains untouched. No source file is modified
until the requested output file is written.
"""
import argparse
from pathlib import Path

def replace_once(s: str, old: str, new: str) -> str:
    assert s.count(old) == 1, f"expected one anchor, found {s.count(old)}: {old[:90]!r}"
    return s.replace(old, new)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--original", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--mode", required=True, choices=("prefix10", "prefix11"))
    a = p.parse_args()
    bits = 10 if a.mode == "prefix10" else 11
    s = a.original.read_text(encoding="utf-8")
    s = replace_once(s,
        "pub const FAST_DECODE_BITS: u8 = 11;",
        f"pub const FAST_DECODE_BITS: u8 = {bits};\nconst SECOND_DECODE_BITS: usize = 16 - FAST_DECODE_BITS as usize;")
    s = replace_once(s,
        "    fast: [FastEntry; 1 << FAST_DECODE_BITS],\n    max_len: u8,",
        "    fast: [FastEntry; 1 << FAST_DECODE_BITS],\n    secondary: Vec<FastEntry>,\n    max_len: u8,")
    s = replace_once(s,
        "            fast: [FastEntry::default(); 1 << FAST_DECODE_BITS],\n            max_len: 0,",
        "            fast: [FastEntry::default(); 1 << FAST_DECODE_BITS],\n            secondary: Vec::new(),\n            max_len: 0,")
    s = replace_once(s,
        "        self.symbols.clear();\n        // Every accepted multi-symbol model is Kraft-complete. Therefore every",
        "        self.symbols.clear();\n"
        "        // u16::MAX marks a primary prefix without a secondary page yet.\n"
        "        self.fast.fill(FastEntry { symbol: u16::MAX, len: 0 });\n"
        "        self.secondary.clear();\n"
        "        // Every accepted multi-symbol model is Kraft-complete. Therefore every")
    s = replace_once(s,
        """                    // Long codes are rare in D1. Mark the shared fast prefix as
                    // a canonical fallback instead of constructing a secondary
                    // table for it.
                    self.fast[prefix] = FastEntry::default();""",
        """                    // Allocate one compact suffix page per distinct long prefix.
                    // Every Kraft-complete model fills its entire used page.
                    let page = if self.fast[prefix].symbol == u16::MAX {
                        let page = self.secondary.len() >> SECOND_DECODE_BITS;
                        if page >= usize::from(u16::MAX) {
                            return Err(Error::NonCanonical);
                        }
                        self.secondary.resize(
                            self.secondary.len() + (1usize << SECOND_DECODE_BITS),
                            FastEntry::default(),
                        );
                        self.fast[prefix] = FastEntry { symbol: page as u16, len: 0 };
                        page
                    } else {
                        usize::from(self.fast[prefix].symbol)
                    };
                    let suffix = (code as usize) & ((1usize << suffix_bits) - 1);
                    let suffix_shift = usize::from(MAX_CODE_LEN - len);
                    let start = (page << SECOND_DECODE_BITS) + (suffix << suffix_shift);
                    let end = start + (1usize << suffix_shift);
                    self.secondary[start..end].fill(entry);""")
    old = """        bits.ensure_bits_fast(usize::from(MAX_CODE_LEN));
        let window = bits.peek_buffered(usize::from(MAX_CODE_LEN)) as u32;
        for len in (usize::from(FAST_DECODE_BITS) + 1)..=usize::from(self.max_len) {
            let code = window >> (usize::from(MAX_CODE_LEN) - len);
            let first = self.first_code[len];
            let count = u32::from(self.counts[len]);
            if code >= first && code - first < count {
                let index = self.first_symbol[len] + (code - first) as usize;
                let symbol = unsafe { *self.symbols.get_unchecked(index) };
                #[cfg(feature = "profile")]
                profile::huffman_long();
                bits.consume_buffered(len);
                return usize::from(symbol);
            }
        }
        debug_assert!(false, "invalid canonical long code");
        0"""
    new = """        // The primary entry stores a suffix page index when len == 0.
        // One indexed lookup replaces a variable-length canonical scan.
        bits.ensure_bits_fast(usize::from(MAX_CODE_LEN));
        let window = bits.peek_buffered(usize::from(MAX_CODE_LEN)) as usize;
        let suffix = window & ((1usize << SECOND_DECODE_BITS) - 1);
        let index = (usize::from(entry.symbol) << SECOND_DECODE_BITS) | suffix;
        let decoded = unsafe { *self.secondary.get_unchecked(index) };
        debug_assert!(decoded.len > FAST_DECODE_BITS);
        #[cfg(feature = "profile")]
        profile::huffman_long();
        bits.consume_buffered(usize::from(decoded.len));
        usize::from(decoded.symbol)"""
    s = replace_once(s, old, new)
    assert "secondary: Vec<FastEntry>" in s
    assert s.count("let decoded = unsafe { *self.secondary.get_unchecked(index) };") == 1
    a.output.write_text(s, encoding="utf-8")

if __name__ == "__main__":
    main()
