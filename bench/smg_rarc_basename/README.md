# Exact-source Super Mario Galaxy RARC basename fallback A/B

The SMG RARC parser stores files by normalized full path in a BTreeMap.
When a caller requests a basename under an unrecognized directory,
the original `get` scanned *every* archive entry to find a single
case-insensitive filename match and rejected ambiguity.

The candidate builds one `HashMap<String, Option<String>>` after
parsing the full archive. Each unique normalized basename points to
its full source path; duplicates store `None` and remain unresolved.
Full-path lookups continue to use the original BTreeMap.

This public harness compiles the original and optimized private-source
`rarc.rs` modules (without their unit-test modules) directly with
rustc, generating genuine uncompressed RARC bytes containing exactly
16, 256, 1024 and 4096 entries. The test verifies every full-path and
basename-fallback lookup byte-for-byte; it times repeated fallback
queries with nine alternating A/B rounds.

The harness does not decode embedded Yaz0 assets, measure material
processing, the one-time index-build cost separately or determine how
frequently real SMG archives use fallback-name lookups. Reported
speedups apply only to basename fallback queries, not loading scenes,
texture processing or rendering. Independent runner repeat is triggered
by this documentation change.
