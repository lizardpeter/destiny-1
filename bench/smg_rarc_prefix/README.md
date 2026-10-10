# Exact-source RARC prefix-enumeration optimization

The SMG source module stores RARC member paths in a BTreeMap. Its public
`entries_under(prefix)` previously scanned every entry on each call.
This candidate seeks to the sorted lower bound with
`BTreeMap::range(prefix.clone()..)` and stops after the last
`starts_with` match.

The public harness compiles the original and optimized `rarc.rs` source
modules verbatim (excluding their private unit-test modules) and
generates synthetic valid Nintendo RARC archives containing 256, 1024,
4096 and 16384 entries. Byte-accurate prefix results and iteration order
are compared for normalized, uppercase and slash-delimited prefixes,
including absent, singleton, partial and all-entry matches.

Seven alternating A/B rounds time repeated iteration on Windows and
Linux. Selective prefix and absent-prefix paths benefit dramatically;
a prefix matching nearly every entry still scans nearly every entry and
may be around parity. One-time parse/index costs are identical because
the BTreeMap existed before this change.

Benchmarks intentionally isolate prefix enumeration rather than
actual Mario Galaxy scene load, Yaz0 decompression, file I/O, GPU upload,
or game FPS. This documentation update initiates a separate repeat run.
