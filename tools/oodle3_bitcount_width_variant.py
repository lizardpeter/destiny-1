#!/usr/bin/env python3
"""Evaluate machine-register friendly bit-count widths (u16/u32) in MSB reader."""
import argparse
from pathlib import Path

def transform(text,kind):
    a=text.index("struct MsbBitReader<'a> {")
    b=text.index("\n#[cfg(test)]",a)
    reader=text[a:b]
    old="bit_count: u8,"
    if reader.count(old)!=1: raise RuntimeError("unexpected bit counter field")
    if reader.count("count as u8")!=3 or reader.count("consume as u8")!=1:
        raise RuntimeError("unexpected subtract forms")
    new=reader.replace(old,f"bit_count: {kind},")
    new=new.replace("usize::from(self.bit_count)","self.bit_count as usize")
    new=new.replace("count as u8",f"count as {kind}")
    new=new.replace("consume as u8",f"consume as {kind}")
    return text[:a]+new+text[b:]

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--width",choices=("u16","u32"),required=True)
    args=p.parse_args()
    result=transform(args.original.read_text(),args.width)
    args.output.write_text(result)
    print("BIT_COUNT_WIDTH_VARIANT",args.width)
