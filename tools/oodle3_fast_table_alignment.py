#!/usr/bin/env python3
"""Place unchanged 8192-byte Huffman fast lookup on an aligned boundary."""
import argparse
from pathlib import Path

def transform(src,align):
    anchor="""#[derive(Debug, Clone)]
struct CanonicalDecoder {"""
    table=f"""#[derive(Debug, Clone)]
#[repr(align({align}))]
struct AlignedFastTable([FastEntry; 1 << FAST_DECODE_BITS]);

impl core::ops::Deref for AlignedFastTable {{
    type Target = [FastEntry; 1 << FAST_DECODE_BITS];
    #[inline(always)]
    fn deref(&self) -> &Self::Target {{
        &self.0
    }}
}}

impl core::ops::DerefMut for AlignedFastTable {{
    #[inline(always)]
    fn deref_mut(&mut self) -> &mut Self::Target {{
        &mut self.0
    }}
}}

"""
    if src.count(anchor)!=1:raise RuntimeError('Could not find CanonicalDecoder')
    src=src.replace(anchor,table+anchor)
    original="fast: [FastEntry; 1 << FAST_DECODE_BITS],"
    initializer="fast: [FastEntry::default(); 1 << FAST_DECODE_BITS],"
    if src.count(original)!=1 or src.count(initializer)!=1:
        raise RuntimeError("Unexpected fast lookup storage")
    src=src.replace(original,"fast: AlignedFastTable,")
    src=src.replace(initializer,"fast: AlignedFastTable([FastEntry::default(); 1 << FAST_DECODE_BITS]),")
    return src

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--align",type=int,choices=(32,64,128),required=True)
    a=p.parse_args()
    result=transform(a.original.read_text(),a.align)
    a.output.write_text(result)
    print('HUFFMAN_TABLE_ALIGN',a.align,len(result))
