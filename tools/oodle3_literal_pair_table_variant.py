#!/usr/bin/env python3
"""Generate exact, output-boundary-safe two-literal Huffman prefix candidates.

The decoder's existing 4-byte FastEntry is extended into its padding byte:
symbol:u16 stores two packed literal bytes only when pair_len:u8 != 0;
len remains the *first* symbol's code length for the checked tail reader.
The full fast-model table retains its original 8192-byte size.
"""
import argparse
from pathlib import Path

BEFORE_STRUCT="""struct FastEntry {
    symbol: u16,
    len: u8,
}"""
AFTER_STRUCT="""struct FastEntry {
    symbol: u16,
    len: u8,
    // Uses the existing padding byte. Zero means a normal single symbol;
    // nonzero means a second literal whose code also fits the prefix.
    pair_len: u8,
}"""
BEFORE_ENTRY="""                let entry = FastEntry {
                    symbol: symbol as u16,
                    len,
                };"""
AFTER_ENTRY="""                let entry = FastEntry {
                    symbol: symbol as u16,
                    len,
                    pair_len: 0,
                };"""
END_MODEL="""        Ok(())
    }

    #[inline(always)]
    fn decode_fast_multi"""
PAIR_MODEL="""        // Predecode two sequential literal symbols when their combined
        // canonical code fits inside the existing 11-bit lookup prefix.
        // Build from an immutable original table to avoid recursive pairing.
        let single = self.fast;
        let mask = (1usize << FAST_DECODE_BITS) - 1;
        for prefix in 0..single.len() {
            let first = single[prefix];
            if first.len == 0
                || first.len >= FAST_DECODE_BITS
                || usize::from(first.symbol) >= LITERAL_SYMBOLS
            {
                continue;
            }
            let shifted = (prefix << usize::from(first.len)) & mask;
            let second = single[shifted];
            if second.len == 0
                || usize::from(second.symbol) >= LITERAL_SYMBOLS
                || first.len + second.len > FAST_DECODE_BITS
            {
                continue;
            }
            self.fast[prefix].symbol = first.symbol | (second.symbol << 8);
            self.fast[prefix].pair_len = second.len;
        }
        Ok(())
    }

    #[inline(always)]
    fn decode_fast_multi"""
BEFORE_SIG="fn decode_fast_multi(&self, bits: &mut MsbBitReader<'_>) -> usize {"
AFTER_SIG="fn decode_fast_multi(&self, bits: &mut MsbBitReader<'_>, allow_pair: bool) -> usize {"
BEFORE_DEC="""        let entry = unsafe { *self.fast.get_unchecked(prefix) };
        if entry.len != 0 {
            #[cfg(feature = "profile")]
            profile::huffman_fast();
            bits.consume_buffered(usize::from(entry.len));
            return usize::from(entry.symbol);
        }
"""
AFTER_DEC="""        let entry = unsafe { *self.fast.get_unchecked(prefix) };
        if entry.len != 0 {
            #[cfg(feature = "profile")]
            profile::huffman_fast();
            if entry.pair_len != 0 && allow_pair {
                bits.consume_buffered(usize::from(entry.len + entry.pair_len));
                // Distinguish packed double-literal from all 713 retail symbols.
                return (1usize << 16) | usize::from(entry.symbol);
            }
            bits.consume_buffered(usize::from(entry.len));
            if entry.pair_len != 0 {
                // The output boundary requires only the first literal.
                return usize::from(entry.symbol & 255);
            }
            return usize::from(entry.symbol);
        }
"""
BEFORE_CHECK="""                bits.consume_buffered(usize::from(entry.len));
                return Ok(usize::from(entry.symbol));"""
AFTER_CHECK="""                bits.consume_buffered(usize::from(entry.len));
                return Ok(if entry.pair_len != 0 {
                    usize::from(entry.symbol & 255)
                } else {
                    usize::from(entry.symbol)
                });"""
BEFORE_LOOP="""                let mut symbol = huffman.decode_fast_multi(&mut bits);

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
AFTER_LOOP="""                let mut symbol = huffman.decode_fast_multi(&mut bits, op + 1 < output_end);

                // One 11-bit table hit may cover two consecutive short
                // literals. Both stores and the bit consumption are guarded
                // against the final output byte and the input tail reader.
                while symbol < LITERAL_SYMBOLS || (symbol & (1usize << 16)) != 0 {
                    if (symbol & (1usize << 16)) != 0 {
                        #[cfg(feature = "profile")]
                        {
                            profile::literal();
                            profile::literal();
                        }
                        WRITE_PAIR
                        op += 2;
                    } else {
                        #[cfg(feature = "profile")]
                        profile::literal();
                        unsafe {
                            *output.get_unchecked_mut(op) = symbol as u8;
                        }
                        op += 1;
                    }
                    if op >= output_end || !bits.has_fast_margin() {
                        break 'fast_decode;
                    }
                    symbol = huffman.decode_fast_multi(&mut bits, op + 1 < output_end);
                }
"""
STORE_8="""unsafe {
                            *output.get_unchecked_mut(op) = (symbol & 255) as u8;
                            *output.get_unchecked_mut(op + 1) = ((symbol >> 8) & 255) as u8;
                        }"""
STORE_16="""unsafe {
                            let pair = (symbol & 0xffff) as u16;
                            core::ptr::write_unaligned(output.as_mut_ptr().add(op).cast::<u16>(), pair.to_le());
                        }"""

def replace_once(src, old, new, label):
    if src.count(old)!=1:
        raise RuntimeError(f"Expected one {label}; found {src.count(old)}")
    return src.replace(old,new,1)

def build(src,mode):
    src=replace_once(src,BEFORE_STRUCT,AFTER_STRUCT,"FastEntry")
    src=replace_once(src,BEFORE_ENTRY,AFTER_ENTRY,"canonical entry")
    src=replace_once(src,END_MODEL,PAIR_MODEL,"rebuild append")
    src=replace_once(src,BEFORE_SIG,AFTER_SIG,"fast signature")
    src=replace_once(src,BEFORE_DEC,AFTER_DEC,"fast decode entry")
    start=src.index("    fn decode(&self, bits:")
    end=src.index("}\n\n#[derive(Debug, Clone)]\npub struct Decoder",start)
    checked=src[start:end]
    if checked.count(BEFORE_CHECK)!=1:
        raise RuntimeError("Expected checked tail single symbol")
    src=src[:start]+checked.replace(BEFORE_CHECK,AFTER_CHECK)+src[end:]
    src=replace_once(src,BEFORE_LOOP,AFTER_LOOP.replace("WRITE_PAIR",STORE_8 if mode=="store8" else STORE_16),"literal fast path")
    if mode=="store16":
        # This build targets Windows x86_64. Little-endian u16 writes are
        # architecture-neutral and do not depend on native endianness.
        pass
    return src

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--mode",choices=("store8","store16"),required=True)
    a=p.parse_args()
    result=build(a.original.read_text(),a.mode)
    a.output.write_text(result)
    print("PREDECODED_HUFFMAN_LITERAL_PAIRS",a.mode,len(result))
