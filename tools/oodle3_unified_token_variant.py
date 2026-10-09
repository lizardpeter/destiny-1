#!/usr/bin/env python3
"""Isolated, exact-source transformations of D1 LZH match-token dispatch.

All variants retain canonical Huffman parsing and original matched-output
semantics. They change only how the token branch obtains distance, length,
and dispatches the common copy operation.
"""
import argparse
from pathlib import Path

START = "                debug_assert!(symbol < SYMBOL_COUNT);"
END = "\n            }\n\n        }\n\n        // Only the final input-boundary"
RECENT = """
                    let selector = bits.read_bits_fast(2) as usize;
                    let distance = match selector {
                        0 => recent[0],
                        1 => {
                            recent.swap(0, 1);
                            recent[0]
                        }
                        2 => {
                            recent.swap(1, 2);
                            recent.swap(0, 1);
                            recent[0]
                        }
                        3 => {
                            recent.swap(2, 3);
                            recent.swap(1, 2);
                            recent.swap(0, 1);
                            recent[0]
                        }
                        _ => unreachable!(),
                    };
"""
EXPLICIT = """
                    let distance = meta.distance_base as usize
                        + bits.read_bits_fast(usize::from(meta.distance_info)) as usize
                        + 1;
                    if meta.distance_base != 0 {
                        recent[3] = recent[2];
                        recent[2] = recent[1];
                        recent[1] = distance;
                    }
"""
DISTANCE = """
                let distance = if symbol < LITERAL_SYMBOLS + RECENT_TOKEN_COUNT {
                    #[cfg(feature = "profile")]
                    profile::recent_match();""" + RECENT + """
                    distance
                } else {
                    #[cfg(feature = "profile")]
                    profile::explicit_match();""" + EXPLICIT + """
                    distance
                };
"""
PROFILE = """
                #[cfg(feature = "profile")]
                {
                    profile::distance(distance);
                    profile::length(match_len);
                }
                copy_match_into(output, &mut op, output_end, distance, match_len)?;
"""
def variant(original: str, mode: str) -> str:
    start = original.index(START)
    end = original.index(END, start)
    old = original[start:end]
    if old.count("copy_match_into(") != 2 or old.count("decode_length_parts_fast(") != 2:
        raise RuntimeError("Expected two separate reference token paths")
    if mode == "meta_unified":
        code = """                debug_assert!(symbol < SYMBOL_COUNT);
                let meta = unsafe { *TOKEN_META.get_unchecked(symbol - LITERAL_SYMBOLS) };
""" + DISTANCE + """
                let match_len = decode_length_parts_fast(
                    &mut bits,
                    meta.length_base,
                    meta.length_info & !TOKEN_EXTENDED_FLAG,
                    (meta.length_info & TOKEN_EXTENDED_FLAG) != 0,
                );
""" + PROFILE
    elif mode == "length_unified":
        # Retain the direct recent-length table (avoids a match-token meta
        # lookup for recent tokens), but share the full length decoder and
        # copy call between recent and explicit matches.
        code = """                debug_assert!(symbol < SYMBOL_COUNT);
                let (distance, length) =
                    if symbol < LITERAL_SYMBOLS + RECENT_TOKEN_COUNT {
                        #[cfg(feature = "profile")]
                        profile::recent_match();
                        let length = unsafe {
                            *RECENT_LENGTHS.get_unchecked(symbol - LITERAL_SYMBOLS)
                        };
""" + RECENT.replace("                    ", "                        ") + """
                        (distance, length)
                    } else {
                        #[cfg(feature = "profile")]
                        profile::explicit_match();
                        let meta =
                            unsafe { *TOKEN_META.get_unchecked(symbol - LITERAL_SYMBOLS) };
""" + EXPLICIT.replace("                    ", "                        ") + """
                        (distance, token_length(meta))
                    };
                let match_len = decode_length_parts_fast(
                    &mut bits,
                    length.base,
                    length.extra_bits,
                    length.extended,
                );
""" + PROFILE
    else:
        raise RuntimeError("Unexpected mode")
    if code.count("copy_match_into(") != 1 or code.count("decode_length_parts_fast(") != 1:
        raise RuntimeError("Wrong number of combined operations")
    return original[:start] + code + original[end:]

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--original", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--mode", choices=("meta_unified", "length_unified"), required=True)
    a = p.parse_args()
    transformed = variant(a.original.read_text(), a.mode)
    a.output.write_text(transformed)
    print("UNIFIED_TOKEN_DISPATCH_VARIANT", a.mode, len(transformed))
