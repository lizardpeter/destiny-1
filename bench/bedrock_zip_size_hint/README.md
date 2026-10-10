# Bedrock ZIP2.4 decoded-entry size hint

Reads ZIP entries (Stored or Deflate) using the same `zip = 2.4` crate
configuration as `minecraft-bedrock-importer`. The ZIP central directory
advertises the decoded entry size, which can be used as an initial capacity
hint. The candidate uses `Vec::with_capacity(entry.size().min(262144) as usize)`
instead of `Vec::new()`, leaving `Read::read_to_end` unchanged.

The hard 256 KiB cap prevents an untrusted/malicious advertised size from
triggering an arbitrarily large initial allocation. Larger entries continue
to grow normally; no decompression limits, checksums, parser behavior or
filesystems semantics are modified.

The test builds synthetic ZIP archives using both Stored and Deflate entries
with 64–262144 decoded bytes, compares every output digest/length, and runs
alternating paired release benchmarks on Windows and Linux. It does not test
full Bedrock world import, real resource packs or PNG decoding. The purpose
is to measure isolated entry read allocation overhead. Independent repeat
is triggered on update.
