#!/usr/bin/env python3
"""Benchmark two alternative 8-byte layouts of Destiny's match-token metadata."""
import argparse
from pathlib import Path

ORIGINAL="""struct TokenMeta {
    distance_base: u32,
    length_base: u16,
    distance_info: u8,
    length_info: u8,
}"""
ORDERS={
    "length_first": """struct TokenMeta {
    length_base: u16,
    distance_info: u8,
    length_info: u8,
    distance_base: u32,
}""",
    "length_last": """struct TokenMeta {
    distance_base: u32,
    distance_info: u8,
    length_info: u8,
    length_base: u16,
}""",
}
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--original",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--layout",choices=tuple(ORDERS),required=True)
    a=parser.parse_args()
    src=a.original.read_text()
    if src.count(ORIGINAL)!=1:
        raise RuntimeError("Unexpected TokenMeta declaration")
    result=src.replace(ORIGINAL,ORDERS[a.layout])
    a.output.write_text(result)
    print("TOKEN_META_LAYOUT_APPLIED",a.layout)
