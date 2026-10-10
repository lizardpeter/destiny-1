# Destiny 1 Tiger TAR retained range-read benchmark

Synthetic 32 MiB uncompressed TAR file containing one named Destiny-style
`.pkg.bin` member. Reads derive member offsets with
`tar::Archive::entries_with_seek` and `entry.raw_file_position()`, then
test independent on-disk byte ranges, EOF and overflow rejection, including
16 concurrent readers. The implementation models:

- baseline: open TAR file, seek, read exact range, close, per logical block;
- candidate Unix: retain `File`, use `std::os::unix::fs::FileExt::read_at`;
- candidate Windows: four independent read-only files, round robin through
  `Mutex<File>` seek + exact read. Only the I/O is serialized per handle;
  SHA-1, Oodle decompression and downstream work are unchanged.

Seven alternating A/B rounds with native Rust release builds on Windows
and Linux compare 1, 4 and 16 workers with 64-byte, 4 KiB, 32 KiB and
256 KiB ranges. Entire archive stays in the OS file cache for typical
runs, so these are *warm I/O microbenchmarks*. They exclude Tiger file
table parsing, SHA-1 verification, Oodle decompression, GPU upload, retail
archive file layouts and full scene load times. Windows relative gains vary
with endpoint protection and file-opening overhead.

No proprietary game assets. The source `bench/tiger_tar/src/main.rs` is
an independent benchmark reproduction, not the full private importer module.
Adding this documentation retriggers an independent Windows/Linux run.
