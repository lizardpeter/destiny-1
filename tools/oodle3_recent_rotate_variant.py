#!/usr/bin/env python3
"""Alternative recent-distance move-to-front updates in unified LZH dispatch.

Only changes the update of the four-element recent distance list.
All 2-bit selector values 0..3 preserve the original ordering.
"""
import argparse
from pathlib import Path

ORIG = """                    let selector = bits.read_bits_fast(2) as usize;
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
REPLACEMENTS = {
  'safe': """                    let selector = bits.read_bits_fast(2) as usize;
                    let distance = recent[selector];
                    if selector != 0 {
                        recent.copy_within(0..selector, 1);
                        recent[0] = distance;
                    }
""",
  'raw': """                    let selector = bits.read_bits_fast(2) as usize;
                    let distance = unsafe { *recent.get_unchecked(selector) };
                    if selector != 0 {
                        unsafe {
                            core::ptr::copy(recent.as_ptr(), recent.as_mut_ptr().add(1), selector);
                            *recent.get_unchecked_mut(0) = distance;
                        }
                    }
"""
}
if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--original',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--mode',choices=tuple(REPLACEMENTS),required=True)
    args=p.parse_args()
    code=args.original.read_text()
    if code.count(ORIG)!=1:
        raise RuntimeError('Expected exactly one unified recent distance switch')
    args.output.write_text(code.replace(ORIG,REPLACEMENTS[args.mode]))
    print('RECENT_ROTATE_VARIANT',args.mode)
