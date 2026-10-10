# IPAK multi-RAW reservation benchmark

Public synthetic 128-byte IPAK header and 2/8/31 command RAW/SKIP block
harness. It compares original command-by-command `Vec::extend_from_slice`
with a precomputed single `reserve` for blocks with 1024–32768 total RAW
output bytes.

All input ranges, checksum validations, and decoded outputs are identical.
The benchmark uses 11 alternating paired A/B rounds with Rust release fat LTO
and one codegen unit. It tests 36 command/payload/skip patterns. On the first
uncapped test we saw major Windows regressions for certain 94–123 KiB totals.
The 32 KiB cap deliberately retains baseline behavior for those blocks.

No proprietary assets are included. The harness is a reduced synthetic
microbenchmark rather than a full build, physical-disk test, or production
game asset-load timing. A second cross-platform run checks repeatability.
