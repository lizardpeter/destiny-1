# Super Mario Galaxy BCSV wide-field hash-index benchmark

BCSV / JMap source tables contain a fixed field table. The existing SMG
importer hashes a field name with the original 0x1F rolling algorithm and
searches all field records with Vec::position for each row/property lookup.

The candidate indexes the FIRST occurrence of each name hash with
HashMap<u32,usize> only for tables with **at least 64 fields**, and keeps
the linear scan for smaller tables. The duplicate-field rule is critical:
BCSV hash collisions must resolve to the first physical field, just like
the original code. Parsed values and row representation are unchanged.

The public benchmark compiles both unmodified and updated private
`bcsv.rs` source modules and runs new source-level tests. Real synthetic
BCSV binary tables are generated for varied widths; result parity is
asserted for every field and row, duplicates, missing names, row bounds.
Release A/B timing uses nine alternating rounds, 100,000 or 250,000
lookups across 128 rows, hits and ~50% misses, Windows and Linux.

Initial tests showed slowdowns with a naive 24-field threshold. The
tested production cutoff is now **64** so smaller tables use the
proven old path. The benefit for tables with ≥64 fields depends on
query frequency and success/miss mix.

These are isolated BCSV field-lookup results, NOT a benchmark of scene
loading, the full importer, shaders, GPU upload or frame time. Repeating
after this documentation change triggers another Windows/Linux run.
