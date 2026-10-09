#!/usr/bin/env python3
"""Experimental two-literal fast loop with identical Huffman state transitions."""
import argparse
from pathlib import Path

START = "                while symbol < LITERAL_SYMBOLS {"
END = "\n                debug_assert!(symbol < SYMBOL_COUNT);"
def transform(src, mode):
    a=src.index(START)
    b=src.index(END,a)
    orig=src[a:b]
    if orig.count("huffman.decode_fast_multi(&mut bits)")!=1:
        raise RuntimeError("Unexpected original literal loop")
    common="""                while symbol < LITERAL_SYMBOLS {
                    #[cfg(feature = "profile")]
                    profile::literal();
                    if op + 1 < output_end && bits.has_fast_margin() {
                        let following = huffman.decode_fast_multi(&mut bits);
                        if following < LITERAL_SYMBOLS {
                            #[cfg(feature = "profile")]
                            profile::literal();
                            WRITE_PAIR
                            op += 2;
                            if op >= output_end || !bits.has_fast_margin() {
                                break 'fast_decode;
                            }
                            symbol = huffman.decode_fast_multi(&mut bits);
                            continue;
                        }
                        // The second lookup was a match token; consume its
                        // bits exactly once, then dispatch the token normally.
                        unsafe {
                            *output.get_unchecked_mut(op) = symbol as u8;
                        }
                        op += 1;
                        symbol = following;
                        break;
                    }
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
    if mode=="store16":
        store="""unsafe {
                                let packed = u16::from_ne_bytes([symbol as u8, following as u8]);
                                core::ptr::write_unaligned(
                                    output.as_mut_ptr().add(op).cast::<u16>(),
                                    packed,
                                );
                            }"""
    elif mode=="store8":
        store="""unsafe {
                                *output.get_unchecked_mut(op) = symbol as u8;
                                *output.get_unchecked_mut(op + 1) = following as u8;
                            }"""
    else: raise RuntimeError("bad mode")
    return src[:a]+common.replace("WRITE_PAIR",store)+src[b:]

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--mode",choices=("store16","store8"),required=True)
    a=p.parse_args()
    content=transform(a.original.read_text(),a.mode)
    a.output.write_text(content)
    print("PAIRED_LITERAL_FAST_LOOP",a.mode)
