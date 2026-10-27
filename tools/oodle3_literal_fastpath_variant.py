#!/usr/bin/env python3
"""Isolated native-CPU LZH literal fast-path variants.

Experiment A/B uses the exact verified Rust-test scalar decoder as a base.
The sentinel variant encodes a long-code prefix as a nonliteral symbol with
zero code length, letting the common literal loop use a single category test.
No unchecked table read is used except the original guarded fast path.
"""
import argparse
from pathlib import Path

START = """                let mut symbol = huffman.decode_fast_multi(&mut bits);

                // D1 LZH is strongly literal-heavy. Stay in a compact literal-only
                // loop until a match token appears instead of returning through the
                // full token-dispatch loop for every literal.
                while symbol < LITERAL_SYMBOLS {
                    #[cfg(feature = "profile")]
                    profile::literal();
                    unsafe {
                        *output.get_unchecked_mut(op) = symbol as u8;
                    }
                    op += 1;

                    if op >= output_end || !bits.has_fast_margin() {
                        break 'fast_decode;
                    }
                    symbol = huffman.decode_fast_multi(&mut bits);
                }

"""
MODE_PRELOAD = """        bits.ensure_bits_fast(usize::from(FAST_DECODE_BITS));
        let prefix = bits.peek_buffered(usize::from(FAST_DECODE_BITS)) as usize;"""
PRELOAD_REPLACEMENT = """        // Experiment: refill ahead to keep a full 16-bit decoding window ready.
        bits.ensure_bits_fast(usize::from(MAX_CODE_LEN));
        let prefix = bits.peek_buffered(usize::from(FAST_DECODE_BITS)) as usize;"""

def replace_once(s, old, new):
    n=s.count(old)
    assert n==1, f"expected one anchor, found {n}: {old[:100]!r}"
    return s.replace(old,new)

def literal_loop(single_test):
    cond = "entry.symbol < LITERAL_SYMBOLS as u16" if single_test else "(entry.len != 0 && entry.symbol < LITERAL_SYMBOLS as u16)"
    return """                // Common literals consume the primary table directly.
                // Rare match symbols and long-code sentinels use the unchanged
                // canonical decoder, preserving all special-token semantics.
                let symbol = loop {
                    bits.ensure_bits_fast(usize::from(FAST_DECODE_BITS));
                    let prefix = bits.peek_buffered(usize::from(FAST_DECODE_BITS)) as usize;
                    let entry = unsafe { *huffman.fast.get_unchecked(prefix) };
                    if COND {
                        debug_assert!(entry.len > 0);
                        #[cfg(feature = "profile")]
                        profile::huffman_fast();
                        bits.consume_buffered(usize::from(entry.len));
                        #[cfg(feature = "profile")]
                        profile::literal();
                        unsafe { *output.get_unchecked_mut(op) = entry.symbol as u8; }
                        op += 1;
                    } else {
                        let decoded = huffman.decode_fast_multi(&mut bits);
                        if decoded >= LITERAL_SYMBOLS {
                            break decoded;
                        }
                        // Valid long Huffman codes may still encode literals.
                        #[cfg(feature = "profile")]
                        profile::literal();
                        unsafe { *output.get_unchecked_mut(op) = decoded as u8; }
                        op += 1;
                    }
                    if op >= output_end || !bits.has_fast_margin() {
                        break 'fast_decode;
                    }
                };

""".replace("COND",cond)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--mode",required=True,choices=("sentinel","plain","preload16"))
    a=p.parse_args()
    s=a.original.read_text(encoding="utf-8")
    if a.mode=="preload16":
        s=replace_once(s,MODE_PRELOAD,PRELOAD_REPLACEMENT)
    else:
        s=replace_once(s,START,literal_loop(a.mode=="sentinel"))
        if a.mode=="sentinel":
            s=replace_once(s,
                """                    self.fast[prefix] = FastEntry::default();""",
                """                    // Nonliteral marker for a long-code prefix.
                    // len==0 retains the canonical fallback semantics.
                    self.fast[prefix] = FastEntry {
                        symbol: LITERAL_SYMBOLS as u16,
                        len: 0,
                    };""")
    assert "'fast_decode: while op < output_end" in s
    a.output.write_text(s,encoding="utf-8")

if __name__=="__main__":
    main()
