# Bedrock ZIP resource-pack central directory reuse

`TextureCatalog::from_zip` builds ZIP metadata once and resolves
`textures/terrain_texture.json`. The old asset-reader path created
`ZipArchive` anew for every texture, normal/PBR layer and resource JSON.
The candidate reuses that same initialized archive index.

This public synthetic ZIP 2.4 harness benchmarks 16/64/256/512 named asset
lookups and byte-for-byte output identity with 512-byte and 4096-byte files.
Baseline: rebuild `ZipArchive<Cursor<&[u8]>>` per entry. Candidate: one
`ZipArchive` and repeated by-name lookup. The separate shared-reader parity
test uses an actual `ZipArchive<File>` in `Arc<Mutex<...>>`, clones the
handle and verifies byte values under eight concurrent worker threads, then
checks that the file handle is closed so temporary file deletion succeeds on
Windows.

This intentionally excludes physical file open/close costs from the timed
baseline; the production path previously paid those costs too.
All tests use synthetic resources. Speedups concern isolated ZIP lookup and
extraction, not total Bedrock world load, PNG decode, mesh build or rendering.
