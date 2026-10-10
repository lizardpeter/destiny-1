# Destiny 1 Tiger sequential entry streaming benchmark

The original `TigerPackage::read_entry_impl` reads and SHA-1-validates
every logical block into a `Vec<Arc<[u8]>>`, then allocates the final
entry output and copies every block into it. On an uncached entry this
retains all decoded source blocks until the final assembly finishes.
The new single-threaded path reserves the exact output first and
copies each verified block immediately after decoding. It keeps at
most one uncached decoded logical block alive at a time. The
existing native multithreaded gather path is deliberately unchanged.

This public benchmark compiles **the complete original and modified
private `tiger.rs` source** as separate modules. A public benchmark-only
constructor builds valid synthetic uncompressed Tiger physical block
records with SHA-1 hashes. There are no proprietary assets and the
benchmark Oodle module is a rejecting stub. Both versions read actual
16–48 MiB synthetic `.pkg.bin` patch files using production path,
perform SHA-1 validation, and reconstruct source-exact entries.

The benchmark tests:
- 1–32 logical blocks and arbitrary first-block offsets
- cold decoded-block cache and warm bounded per-package cache
- exact byte parity of entry results with source file slices
- wrong SHA-1 fail-closed handling
- existing module unit tests for range caching, patch files, TAR
  member bounds and concurrent readers.

Benchmark numbers exclude compressed Oodle decoding and do not
represent whole-game rendering or map load times. The resource
advantage is bounded in-flight uncached decoded blocks: one versus
entry_block_count (plus final output) in single-threaded mode.

The initial Linux result:
https://github.com/lizardpeter/destiny-1/actions/runs/38017683432

The final README update triggers a fresh independent Windows/Linux
runner verification, with five alternating A/B benchmark rounds for
each workload.
