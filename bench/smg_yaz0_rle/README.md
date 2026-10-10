# Exact-source SMG Yaz0 1-byte backreference optimization

A/B comparison of the production `decompress_yaz0` module on
`Rust-test/main` against its optimized branch. The benchmark compiles both
source modules verbatim except for stripping their `#[cfg(test)]` suites,
which reference private modules not needed by the public harness.

A Yaz0 match with `distance == 1` simply repeats the most recently decoded
byte. Rather than progressively extending an overlapping previous slice with
`Vec::extend_from_within`, the candidate appends the last byte using
`Vec::resize`. No unsafe code or additional allocations.

Parities: decoded bytes and malformed/truncated errors across 8 distinct
match distances and multiple payload lengths, including the largest Yaz0
distance, 4096 bytes. A/B includes 1/2/4/64 match-distance workloads at
4 KiB, 32 KiB, 256 KiB and 1 MiB decoded sizes. 11 alternating release A/B
rounds with native-CPU independent Windows and Linux runners.

These are synthetic repeat-heavy frames, not measured Mario Galaxy retail
archive mixes or overall game-map load performance.
