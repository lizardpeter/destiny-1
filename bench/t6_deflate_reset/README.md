# T6 FastFile DEFLATE record-state reuse

The BO2 FastFile decoder reads many independent raw-DEFLATE compressed
records. The current importer constructs a fresh `DeflateDecoder` for each
record, even when very short. `flate2::bufread::DeflateDecoder::reset`
allows its zlib-rs decompression state to be reused between records.

The candidate places each compressed record in a recycled owned `Vec`
inside `Cursor<Vec<u8>>`, then resets and runs the same exact
`read_to_end` logic. Encoded records **larger than 4096 bytes** continue
through the old fresh-decoder path after an uncapped Linux test showed a
fivefold regression for 32780-byte incompressible records. No change to
DEFLATE semantics, decompressed length limits, validation, encryption
algorithms or record chaining is intended.

The public synthetic benchmark exercises 24 combinations of payload
lengths/data types and truncated/corrupt frame parity, plus 11
alternating release A/B timing rounds for 64, 1024, 4096 and 32768
decoded bytes. Windows and Linux use `flate2` with
`default-features=false` and `zlib-rs`, matching the private importer.

Benchmarks measure DEFLATE construction and output accumulation only,
not Salsa20 decrypt, SHA-1 nonce chaining, output hashing, physical I/O
or full retail FastFile loading. A follow-up run is independently triggered.
