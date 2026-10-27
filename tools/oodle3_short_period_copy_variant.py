#!/usr/bin/env python3
"""Generate isolated, correctness-guarded 2/4-byte-period match-copy trials.

Keep the checked scalar baseline unchanged outside the two short-distance
cases. The 8-byte overstore is used only with at least eight physical output
bytes available; later decode writes own all bytes beyond the logical match.
"""
import argparse
from pathlib import Path

ANCHOR = "    // Opt-in SIMD trial (x86-64 guarantees SSE2). Only use sequential,"
D2 = """    // Experimental: exact periodic expansion of short distance-two matches.
    // Reading the preceding two bytes and repeating them is equivalent to
    // serial LZ copy, including output self-overlap.
    if distance == 2 && length <= 8 && output.len() - match_start >= 8 {
        unsafe {
            let base = output.as_mut_ptr();
            let pattern = core::ptr::read_unaligned(base.add(source_start).cast::<u16>());
            let repeated = u64::from(pattern).wrapping_mul(0x0001_0001_0001_0001);
            core::ptr::write_unaligned(base.add(match_start).cast::<u64>(), repeated);
        }
        *output_pos += length;
        return Ok(());
    }

"""
D4 = """    // Experimental: equivalent periodic expansion of distance-four matches.
    if distance == 4 && length <= 8 && output.len() - match_start >= 8 {
        unsafe {
            let base = output.as_mut_ptr();
            let pattern = core::ptr::read_unaligned(base.add(source_start).cast::<u32>());
            let repeated = u64::from(pattern).wrapping_mul(0x0000_0001_0000_0001);
            core::ptr::write_unaligned(base.add(match_start).cast::<u64>(), repeated);
        }
        *output_pos += length;
        return Ok(());
    }

"""

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--original", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--mode", choices=("distance2", "distance2_4"), required=True)
    a = p.parse_args()
    original = a.original.read_text(encoding="utf-8")
    assert original.count(ANCHOR) == 1, "copy-match insertion anchor changed"
    assert "fn copy_match_into(" in original
    variant = D2 + (D4 if a.mode == "distance2_4" else "")
    a.output.write_text(original.replace(ANCHOR, variant + ANCHOR), encoding="utf-8")

if __name__ == "__main__":
    main()
