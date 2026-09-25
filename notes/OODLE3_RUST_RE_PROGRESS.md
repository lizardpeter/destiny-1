# Oodle 3 Native Rust Reimplementation — Reversal Progress

Updated: 2026-09-25

## Goal

Replace the runtime dependency on `oo2core_3_win64.dll` for the Destiny 1 Rise of Iron package pipeline with a native Rust decoder that reproduces the Destiny-required behavior of `OodleLZ_Decompress`.

This is a compatibility-oriented clean-room implementation target. The project will preserve behavioral evidence, function maps, synthetic oracle vectors, and independently written Rust code rather than committing the proprietary DLL or copied decompiler output.

## Exact reference runtime

Validation runtime already established by the D1 project:

- file: `oo2core_3_win64.dll`
- size: 894,752 bytes
- SHA-256: `682c0aad216fae443e0f9561876cfabfddaeffcd48e5990613ad2cf47c49fa62`
- PE32+ x86-64
- exports `OodleLZ_Decompress`
- known-good against both PS4 and Xbox One D1 ROI Tiger compressed blocks

## Compatibility target

The first milestone is intentionally narrower than "all Oodle 2.3":

1. Decode the streams emitted for Destiny-era Oodle 3 package blocks.
2. Match the exact D1 call contract already used by the project:
   - fuzzSafe = 1
   - checkCRC = 0
   - verbosity = minimal/compatible
   - optional buffers/callbacks = null for independent blocks
   - threadPhase = 3
3. Support exact destination lengths from 0x4000 through 0x40000 in D1's 0x4000 quantum.
4. Return the same success/failure semantics needed by `d1_oodle_probe.py` / `EntryReader`.
5. Remove the Windows DLL and Linux PE-loader bridge from the steady-state decode path.

Compression is useful as an oracle-vector generator but is not required for the first runtime replacement milestone.

## Reversal strategy

### A. Static map

`tools/oodle3_static_probe.py` validates the exact DLL hash, parses PE sections/imports/exports, finds `OodleLZ_Decompress`, conservatively walks direct call targets in `.text`, records branch/call structure, and extracts nearby code/data references. Output is evidence only; no proprietary binary is committed.

### B. Behavioral oracle

`tools/oodle3_oracle_vectors.py` runs on Windows against the verified DLL. It feeds deterministic synthetic inputs through `OodleLZ_Compress` and verifies `OodleLZ_Decompress` round trips, producing compact JSON metadata and compressed test vectors derived from non-game synthetic data.

Vectors are selected to isolate:
- literals / incompressible data
- long repeated runs
- short periodic matches
- long-distance matches
- sparse zero regions
- byte ramps and structured records
- boundary sizes around likely chunk/block cut points

### C. Differential decoder

The Rust crate starts with strict framing/bitstream primitives and a decoder interface. Each reversed stage is added behind differential tests against oracle vectors. Unknown fields remain named by location/behavior until proven.

### D. Destiny acceptance

A native decoder is not considered complete until it produces byte-identical output for the existing PS4/Xbox package corpus and passes the current package/texture/model/animation pipelines without a DLL or PE bridge.

## Known external clues to verify, not assume

Public wrappers confirm the legacy DLL exposes the expected compress/decompress ABI and use a compression bound of approximately `raw + 274 * ceil(raw/0x40000)`. Historical public analysis also places one Oodle 3 `OodleLZ_Decompress` export near RVA `0x5F8B0`; the exact reference DLL will be measured directly before relying on this.

## Progress checklist

- [x] Exact DLL identity already pinned and cross-corpus decode validated.
- [x] Latest Destiny branch selected as base.
- [x] Static PE/call-graph probe scaffolded.
- [x] Synthetic compression/decompression oracle generator scaffolded.
- [x] Native Rust crate scaffolded.
- [ ] Run exact binary static probe and record export/function map. (workflow trigger checkpoint pushed 2026-09-25)
- [ ] Generate deterministic oracle-vector family on Windows.
- [ ] Identify top-level stream framing and codec dispatch.
- [ ] Identify entropy/literal decode path.
- [ ] Identify match-length and offset decode path.
- [ ] Implement first native vector decode.
- [ ] Reach full synthetic vector parity.
- [ ] Reach D1 real-block parity.
- [ ] Remove DLL/bridge dependency from package reader.
