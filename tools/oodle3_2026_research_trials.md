# Destiny 1 Oodle3 research-inspired performance trials (2026-10-27)

Goal: decode the existing Destiny 1 legacy Oodle LZH format faster than original Oodle 2.3 per caller thread.
Baseline is the verified Rust-test decoder (Git blob 02f1f671ebaa1fa21db01594537bbb04250338c5).
No trial altered the compressed bitstream format or the private Rust-test source.

## 2026 research

- Zavadskyi and Kovalchuk, Engineering a Faster Huffman Decoder, Data Compression Conference 2026: https://doi.org/10.1109/DCC66757.2026.00029. Discusses model layout, bit-buffer handling, partial table decoding, and SIMD for word-based English text; results cannot be assumed to apply to Destiny.
- Shchebetov and Shabaev, Prediction-Based Speculative Decoding Approach for Prefix Codes in Data Decompression, ISIT 2026: https://doi.org/10.1109/ISIT62367.2026.11654051. Inspired our own exact, guarded speculative second-literal lookup, not a reproduction of the paper.
- Żukowski, PivCo-Huffman, June 2026: https://marcinzukowski.github.io/pivco-huffman/paper-1.0/ph.html. Changes wire format; incompatible as a drop-in decoder for existing Destiny assets.

## Paired Windows benchmark results

Windows-2025, native-CPU Rust, fat LTO, 1 codegen unit. Each variant passed 15 release tests and decoded all 11 Tower/globals blocks byte-for-byte identical to reference Oodle. 11 alternating-order rounds x 75 iterations. Absolute speeds vary between hosted CPUs; within-run ratios are meaningful.

| Strategy | Baseline MiB/s | Candidate MiB/s | Rust-relative result | Run |
| --- | ---: | ---: | ---: | --- |
| Two-literal 14-bit superinstruction table | 485.53 | 341.39 | -29.69% | https://github.com/lizardpeter/destiny-1/actions/runs/40544638336 |
| Two-literal 16-bit superinstruction table | 485.53 | 278.12 | -42.72% | https://github.com/lizardpeter/destiny-1/actions/runs/40544638336 |
| Speculate next code after 7 bits | 395.36 | 364.51 | -7.80% | https://github.com/lizardpeter/destiny-1/actions/runs/40545148532 |
| Speculate next code after 8 bits | 395.36 | 350.52 | -11.34% | https://github.com/lizardpeter/destiny-1/actions/runs/40545148532 |
| Speculate next code after 9 bits | 395.36 | 359.45 | -9.08% | https://github.com/lizardpeter/destiny-1/actions/runs/40545148532 |
| Unconditional 32-bit refill with bitwise mask | 477.79 | 398.86 | -16.52% | https://github.com/lizardpeter/destiny-1/actions/runs/40545533377 |
| Predicated conditional-select refill | 477.79 | 458.22 | -4.10% | https://github.com/lizardpeter/destiny-1/actions/runs/40545533377 |

Trial generators: tools/oodle3_2026_superinstruction_variant.py on bench/oodle3-2026-superinstruction-20261027; tools/oodle3_speculative_prefix_variant.py on bench/oodle3-2026-speculative-prefix-20261027; tools/oodle3_predicated_refill_variant.py on bench/oodle3-2026-predicated-refill-20261027.

## Conclusion and next measurement

Neither larger pair tables, fixed-offset speculation, nor an unconditional refill helped. Newer work on Huffman decoding is relevant but its codec-specific speedups do not automatically carry over to our mixed Huffman/LZ stream. Next: measure stage-separated model parsing versus Huffman-table build versus payload, decode symbol distributions, and on-machine hardware counters for load latency and branch mispredictions before another large redesign. Keep Rust-test main unchanged until a correctness-verified, replicated throughput improvement wins.
