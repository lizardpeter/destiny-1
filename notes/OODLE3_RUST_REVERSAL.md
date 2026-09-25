# Oodle 2.3 native Rust reversal checkpoint

## Reference runtime

Verified Destiny-compatible research runtime:

- file: `oo2core_3_win64.dll`
- size: 894,752 bytes
- SHA-256: `682c0aad216fae443e0f9561876cfabfddaeffcd48e5990613ad2cf47c49fa62`
- PE32+ x86-64
- PE link timestamp: 2016-07-14 14:47:10 UTC
- image base: `0x180000000`
- entry RVA: `0x9f3e4`
- 60 exports; imports only `KERNEL32.dll`

The DLL is not committed. `tools/oodle3_pe_map.py` reproduces the static inventory from a user-supplied copy.

Public entry points used as differential oracle:

- `OodleLZ_Decompress`: RVA `0x5f8b0`
- `OodleLZDecoder_DecodeSome`: RVA `0x5e180`

## Critical Destiny finding: these tested blocks are legacy LZH

The first real Destiny Tower corpus tested is not Kraken. Eight resident compressed blocks from
`ps4_city_tower_destination_024c_5.pkg` (blocks 764 through 771) all begin with a version-3
one-byte block header and decode as legacy **LZH**.

For the observed `0xB7` header:

- version = 3
- block is compressed
- block reset flag = true
- quantum checksums = false
- serialized decode type = 7
- decode type 7 = LZH
- LZH offset shift = 0

The exact reference DLL decodes each test block to `0x40000` bytes.

A modern pure-Rust Oodle implementation (`oozextract` 0.5.5) rejects these streams because it
implements the newer framing/codecs but not this historical LZH path. It remains useful for newer
Oodle codec families but is not the D1 LZH solution.

## Oodle 2.3 block and quantum framing

The native Rust parser now supports both the historical version-3 header used by the D1 corpus and
the newer version-4 two-byte header.

For the D1 LZH corpus:

- raw block size = `0x40000` (256 KiB)
- raw LZH quantum size = `0x4000` (16 KiB)
- 16 quanta per full block
- version-3 block header = 1 byte
- legacy quantum header = 2-byte big-endian value, plus optional checksum/special data
- low 14 bits of a normal quantum header encode `compressed_size - 1`
- bit 14 = transmitted Huffman-model flag
- bit 15 = extra codec flag
- low 14 bits equal to `0x3fff` select whole-match/memset/memcpy special forms

Across real blocks 764-771, the model flag occurs on quanta 0, 4, 8, and 12: the Huffman model is
therefore refreshed every 64 KiB. Every one of the eight blocks parses to its exact stored size with
no unexplained trailing bytes.

## LZH transmitted Huffman model

The exact Oodle 2.3 DLL's LZH model setup routine is at `0x18005d5e0`. It is the legacy
`GotHuffFlag` path, not the LZ payload loop.

Observed model properties:

- alphabet size = 713 symbols
- fast-decode prefix = 10 bits
- Oodle 2.3 accepts code lengths through **16 bits**
- bitstream is MSB-first
- two code-length encodings are supported:
  - sparse symbol/length pairs
  - zero/nonzero runs using Exp-Golomb plus Rice-coded signed length deltas
- reconstructed code lengths are canonical and must satisfy exact Kraft equality

The 16-bit maximum is an important historical distinction: later Oodle source lowered the LZH limit
to 15, but the exact 2.3 DLL compares against 16. Two real D1 models require a 16-bit length.

The clean-room Rust implementation is in `rust/d1_oodle3/src/lzh.rs`. All 32 transmitted models
from blocks 764-771 parse and validate canonically.

Examples from block 764:

- q0: 536 used symbols, top symbol 708, max length 12
- q4: 595 used symbols, top symbol 710, max length 13
- q8: 512 used symbols, top symbol 704, max length 13
- q12: 493 used symbols, top symbol 712, max length 13

## Exact 713-symbol payload alphabet

The payload Huffman alphabet is now structurally resolved:

`713 = 256 literals + 20 recent-distance tokens + (19 length classes × 23 distance classes)`

Symbols 0-255 are literal bytes.

Symbols 256-275 select one of four recent match distances using 2 extra bits and encode match
lengths from these classes:

`2,3,4,5,6,7,8,9+1b,11+1b,13+1b,15+1b,17+2b,21+2b,25+2b,29+3b,37+3b,45+4b,61+5b,93+6b,157+6b/extended`

Symbols 276-712 use an explicit distance class and one of 19 length classes. The 23 distance
base/extra-bit classes are:

- 0 + 4 bits
- 16 + 4 bits
- 32 + 5 bits
- 64 + 6 bits
- 128 + 7 bits
- 256 + 8 bits
- 512 + 8 bits
- 768 + 8 bits
- 1024 + 9 bits
- 1536 + 9 bits
- 2048 + 10 bits
- 3072 + 10 bits
- 4096 + 10 bits
- 5120 + 10 bits
- 6144 + 11 bits
- 8192 + 12 bits
- 12288 + 12 bits
- 16384 + 13 bits
- 24576 + 13 bits
- 32768 + 14 bits
- 49152 + 14 bits
- 65536 + 15 bits
- 98304 + 15 bits

Explicit-distance lengths begin at 3 and use 19 classes ending in `157 + 7 bits/extended`.

The exact DLL metadata table is at `0x1800bd120` and contains 457 eight-byte token descriptors.
The Rust code generates the same logical table from compact class definitions rather than embedding
the proprietary table bytes.

## Payload decoder functions mapped

The legacy architecture separates model setup from quantum decoding.

For the exact D1 LZH shift-0 path:

- model/header reader: `0x18005d5e0`
- LZH dispatch wrappers: `0x180079a70` and `0x180079b40`
- shift-0 payload kernels: `0x180075dc0` and `0x180078b20`

The two payload kernels are safe/availability variants of the same decoder family. They consume the
713-symbol Huffman stream, emit literals or LZ matches, maintain four recent distances, and perform
overlap-safe match copies.

## Regression corpus and CI

Branch: `oodle3-rust-native-20260925`

Native Rust components:

- `rust/d1_oodle3/src/lib.rs` - version-aware Oodle 2.3 framing
- `rust/d1_oodle3/src/lzh.rs` - complete clean-room legacy LZH payload decoder
- `rust/d1_oodle3/src/ffi.rs` - fail-closed `OodleLZ_Decompress` whole-buffer compatibility ABI
- `rust/d1_oodle3/src/bin/frame_scan.rs` - frame/model diagnostic
- `rust/d1_oodle3/src/bin/native_decode.rs` - native decoder CLI
- `tools/oodle3_pe_map.py` - deterministic PE map
- `.github/workflows/d1-oodle3-rust.yml` - Rust fmt/test/clippy
- `.github/workflows/d1-oodle3-native-differential.yml` - exact reference differential harness
- `.github/workflows/d1-oodle3-rust-corpus.yml` - Tower patch-family corpus
- `.github/workflows/d1-oodle3-rust-cross-family.yml` - unrelated package-family samples
- `.github/workflows/d1-oodle3-rust-dll.yml` - Windows compatibility-DLL ABI differential
- `.github/workflows/d1-oodle3-rust-known-offset-corpus.yml` - expanded validated-offset corpus

The LZH payload consumer is now implemented. The earlier red-differential checkpoint is obsolete.

Verified byte-identical results against the exact Oodle 2.3 reference runtime:

- initial Tower differential: 8/8 blocks
- Tower broad corpus: 43/43 blocks across patch members 3, 4, and 5
- unrelated cross-family corpus: 3/3 blocks
- expanded known-offset corpus: 67/67 additional blocks across 21 additional package members
- Windows Rust `cdylib` loaded through the Oodle 14-argument `OodleLZ_Decompress` ABI: 8/8 initial blocks byte-identical
- Linux native shared-library integration: green

The 67-block expanded run is GitHub Actions run `36134573694`. It covered current members from
multiple `globals` and `investment_assets` families, including package IDs 0151, 0154, 0156,
0157, 0158, 0135, 0137, 0139, 013A-0146. Every tested compressed block began with the legacy
`0xB7` version-3 LZH header and decoded byte-identically.

Across the non-overlapping broad/cross-family/known-offset sets, the current certification corpus is
**113 real compressed blocks across 27 physical D1 package members**. Tested raw output sizes include
16 KiB through 256 KiB, with numerous partial final-block sizes. No alternative Oodle codec/header
was encountered in this corpus.

## Current compatibility boundary

For the Destiny package-decompression path actually observed so far, native Rust LZH is green.

This is not yet a claim that the complete `oo2core_3_win64.dll` has been cloned. The compatibility
library intentionally implements the whole-buffer `OodleLZ_Decompress` call shape used by the D1
tooling and fails closed for unsupported callback/phased modes. Other historical Oodle codecs,
compression/encoding APIs, networking APIs, configuration helpers, optional callback behavior, and
the rest of the roughly 60-export DLL surface remain separate work unless a D1 caller requires them.

## Remaining work

1. Continue corpus expansion until every recoverable D1 package family has been scanned.
2. Record a complete census of encountered block-header bytes / serialized decoder types.
3. If any non-LZH block appears, differential-reverse that codec before declaring full D1 package
   decompression coverage.
4. Exercise the Rust compatibility DLL through more existing D1 tools, not just the standalone
   differential harness.
5. Separately map/reimplement the remaining Oodle 2.3 exports if the goal is a complete DLL clone
   rather than only removal of D1's package-decompression dependency.

## Performance baseline

Windows hosted-runner benchmark against the exact Oodle 2.3 DLL was added in
`.github/workflows/d1-oodle3-rust-benchmark.yml`.

Benchmark method:

- blocks 764-771 from `ps4_city_tower_destination_024c_5.pkg`
- both libraries called through the same 14-argument `OodleLZ_Decompress` ABI
- correctness checked byte-for-byte immediately before timing
- 20 shared warmup iterations
- 100 iterations per round across all 8 blocks
- 200 MiB decompressed output per round
- 7 timed rounds
- release-mode Rust build
- Windows 2025 GitHub-hosted runner

Run `36135551343` measured:

- original Oodle 2.3 median: **455.65 MiB/s**
- native Rust median: **73.25 MiB/s**
- Rust/original throughput ratio: **0.1608x**
- original Oodle is about **6.22x faster**
- current Rust throughput is about **83.9% lower**

This is intentionally the unoptimized compatibility implementation, not a tuned target. The current
Rust decoder performs straightforward canonical-Huffman decoding and the FFI path allocates a decoded
`Vec` and then copies it into the caller's output buffer. Future optimization should preserve the
byte-identical corpus while targeting direct-to-caller output, a fast Huffman lookup table matching
the observed 10-bit prefix, reduced bounds-check/branch overhead, and match-copy specialization.

