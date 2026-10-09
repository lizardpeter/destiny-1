#!/usr/bin/env python3
"""Test raw-pointer and cursor based literal output against indexed Rust output."""
import argparse
from pathlib import Path

OLD="""                while symbol < LITERAL_SYMBOLS {
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
DIRECT="""                while symbol < LITERAL_SYMBOLS {
                    #[cfg(feature = "profile")]
                    profile::literal();
                    unsafe {
                        core::ptr::write(output.as_mut_ptr().add(op), symbol as u8);
                    }
                    op += 1;

                    if op >= output_end || !bits.has_fast_margin() {
                        break 'fast_decode;
                    }
                    symbol = huffman.decode_fast_multi(&mut bits);
                }
"""
CURSOR="""                let base_ptr = output.as_mut_ptr();
                let mut literal_ptr = unsafe { base_ptr.add(op) };
                let output_limit = unsafe { base_ptr.add(output_end) };
                while symbol < LITERAL_SYMBOLS {
                    #[cfg(feature = "profile")]
                    profile::literal();
                    unsafe {
                        *literal_ptr = symbol as u8;
                        literal_ptr = literal_ptr.add(1);
                    }
                    if literal_ptr >= output_limit || !bits.has_fast_margin() {
                        op = unsafe { literal_ptr.offset_from(base_ptr) as usize };
                        break 'fast_decode;
                    }
                    symbol = huffman.decode_fast_multi(&mut bits);
                }
                op = unsafe { literal_ptr.offset_from(base_ptr) as usize };
"""
MODES={"ptr_store":DIRECT,"cursor":CURSOR}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--mode",choices=tuple(MODES),required=True)
    a=p.parse_args()
    text=a.original.read_text()
    if text.count(OLD)!=1: raise RuntimeError("Expected verified literal loop not found")
    result=text.replace(OLD,MODES[a.mode])
    a.output.write_text(result)
    print("LITERAL_CURSOR_VARIANT",a.mode,len(result))
