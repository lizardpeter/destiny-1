# Destiny 1 standalone Tiger PKG file-handle reuse

Tiger packages read logical blocks from source `.pkg.bin` files and
their patch-package siblings. The old importer opened and closed one
file for every block range. Unlike TAR-backed packages, the standalone
file path had no persistent handle retention.

Benchmark compares this original sequence (open, metadata, bounds,
seek, exact read, close) against a bounded cache of at most eight
distinct package files. On Unix each retained file performs positioned
reads. On Windows each patch file uses up to four independent read-only
handles, each with a short seek/read lock. After eight package owners,
unseen owners still use the original open/seek/read fallback.

A 12-package synthetic dataset with 4 MiB per patch verifies exact
byte parity, boundary and overflow errors, the eight-file limit, and
12 concurrent readers. Seven alternating A/B timing rounds compare
4 or 12 patch owners, one or eight readers, and 4 KiB or 32 KiB
ranges. Both platforms use an OS-warm file-cache workload.

This is an isolated Rust reproduction of the production read path,
not a build of the complete private Destiny importer. SHA-1
verification, Oodle decompression, Tiger package parsing, GPU upload
and total game loading are excluded. No game assets are included.

Publishing this benchmark note triggers an independent second
Windows/Linux hosted CI run.
