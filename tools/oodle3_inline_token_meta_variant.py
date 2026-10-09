#!/usr/bin/env python3
"""Alternative 8-byte FastEntry carrying entire retail token semantics.

Token distance_base is divisible by 16, so its 17-bit maximum can be
losslessly represented by u16 distance_base/16. length_base<=157 fits u8.
This retains exact semantics and avoids a dependent TOKEN_META load
for the (less frequent) non-literal symbols.
"""
import argparse
from pathlib import Path

ENTRY_OLD="""struct FastEntry {
    symbol: u16,
    len: u8,
}"""
ENTRY_NEW="""struct FastEntry {
    symbol: u16,
    len: u8,
    length_base: u8,
    distance_base_16: u16,
    distance_info: u8,
    length_info: u8,
}"""
INITIALIZER_OLD="""                let entry = FastEntry {
                    symbol: symbol as u16,
                    len,
                };"""
INITIALIZER_NEW="""                let entry = if symbol < LITERAL_SYMBOLS {
                    FastEntry {
                        symbol: symbol as u16, len,
                        length_base: 0, distance_base_16: 0,
                        distance_info: 0, length_info: 0,
                    }
                } else {
                    let meta = TOKEN_META[symbol - LITERAL_SYMBOLS];
                    debug_assert_eq!(meta.distance_base & 15, 0);
                    debug_assert!(meta.distance_base >> 4 <= u16::MAX as u32);
                    debug_assert!(meta.length_base <= u8::MAX as u16);
                    FastEntry {
                        symbol: symbol as u16, len,
                        length_base: meta.length_base as u8,
                        distance_base_16: (meta.distance_base >> 4) as u16,
                        distance_info: meta.distance_info,
                        length_info: meta.length_info,
                    }
                };"""
FAST_OLD="""fn decode_fast_multi(&self, bits: &mut MsbBitReader<'_>) -> usize {"""
FAST_NEW="""fn decode_fast_multi(&self, bits: &mut MsbBitReader<'_>) -> FastEntry {"""
FAST_RETURN="""            return usize::from(entry.symbol);"""
FAST_RETURN_NEW="""            return entry;"""
FALLBACK_RETURN="""                return usize::from(symbol);"""
FALLBACK_RETURN_NEW="""                return if usize::from(symbol) < LITERAL_SYMBOLS {
                    FastEntry {
                        symbol, len: len as u8, length_base: 0,
                        distance_base_16: 0, distance_info: 0, length_info: 0,
                    }
                } else {
                    let meta = TOKEN_META[usize::from(symbol) - LITERAL_SYMBOLS];
                    FastEntry {
                        symbol, len: len as u8,
                        length_base: meta.length_base as u8,
                        distance_base_16: (meta.distance_base >> 4) as u16,
                        distance_info: meta.distance_info,
                        length_info: meta.length_info,
                    }
                };"""
LOOP_INIT="""                let mut symbol = huffman.decode_fast_multi(&mut bits);"""
LOOP_INIT_NEW="""                let mut entry = huffman.decode_fast_multi(&mut bits);
                let mut symbol = usize::from(entry.symbol);"""
LOOP_NEXT="""                    symbol = huffman.decode_fast_multi(&mut bits);"""
LOOP_NEXT_NEW="""                    entry = huffman.decode_fast_multi(&mut bits);
                    symbol = usize::from(entry.symbol);"""
TOKEN_META_OLD="""                let meta = unsafe { *TOKEN_META.get_unchecked(symbol - LITERAL_SYMBOLS) };"""
TOKEN_META_NEW="""                let meta = TokenMeta {
                    distance_base: u32::from(entry.distance_base_16) << 4,
                    length_base: u16::from(entry.length_base),
                    distance_info: entry.distance_info,
                    length_info: entry.length_info,
                };"""
def replace_once(s,old,new,label):
    n=s.count(old)
    if n!=1:
        raise RuntimeError(f"Expected exactly one {label}, got {n}")
    return s.replace(old,new,1)

def make(s):
    s=replace_once(s,ENTRY_OLD,ENTRY_NEW,"FastEntry")
    s=replace_once(s,INITIALIZER_OLD,INITIALIZER_NEW,"initializer")
    a=s.index("    fn decode_fast_multi(")
    b=s.index("    fn decode(&self, bits:",a)
    fn=s[a:b]
    fn=replace_once(fn,FAST_OLD,FAST_NEW,"fast return type")
    fn=replace_once(fn,FAST_RETURN,FAST_RETURN_NEW,"fast table return")
    fn=replace_once(fn,FALLBACK_RETURN,FALLBACK_RETURN_NEW,"long decode return")
    fn=replace_once(fn,"        0\n    }", "        FastEntry::default()\n    }", "unreachable malformed return")
    s=s[:a]+fn+s[b:]
    a=s.index("        if huffman.one_char.is_none() {")
    b=s.index("        // Only the final input-boundary region",a)
    fragment=s[a:b]
    fragment=replace_once(fragment,LOOP_INIT,LOOP_INIT_NEW,"loop first entry")
    fragment=replace_once(fragment,LOOP_NEXT,LOOP_NEXT_NEW,"loop next entry")
    fragment=replace_once(fragment,TOKEN_META_OLD,TOKEN_META_NEW,"inlined token metadata")
    s=s[:a]+fragment+s[b:]
    return s

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    modified=make(a.original.read_text())
    a.output.write_text(modified)
    print("INLINED_TOKEN_METADATA_FASTENTRY8",len(modified))
