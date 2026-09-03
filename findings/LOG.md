# Reverse-Engineering Log

## 2026-09-03 — Sample acquisition and first verified parse

### Input

Google Drive supplied binary: `ps4_arch_cabal_005b_1.pkg`

- materialized local filename: `ps4_arch_cabal_005b_1.pkg.bin`
- size: `89,044,992` bytes
- SHA-256: `d44f2dcbaef32743da9657e38691bcd91372fd9550e96ea3d99a9ce9440c24e0`

### Container/header findings

- D1 Tiger package version = `24`
- platform code = `7` = PS4
- package id = `91` = `0x005B`
- patch id = `1`
- version fields = `3.0`
- language = none
- tool string = `evil tool_lib test pc_x64 46419.15.08.16.1336.evil 15.08.16 1336`
- header-declared file size exactly matches actual file size

### Tables

- file entries = `667`, at `0x1000`
- blocks = `626`, at `0x4000`
- named tags = `0`
- file-entry table SHA-1 from bytes: `8baf1f6f7e20e85c1475d097780264a1307a316b` — matches header
- block table SHA-1 from bytes: `aa689bff4f38d0b9c32ca34d93de3b1a73ea79bc` — matches header
- named-tag header hash is all zero because count is zero; do not incorrectly compare to SHA1(empty)

### Entry type/subtype census

| Type | Subtype | Count |
|---:|---:|---:|
| 1 | 7 | 163 |
| 16 | 0 | 146 |
| 32 | 7 | 122 |
| 5 | 1 | 122 |
| 32 | 1 | 30 |
| 65 | 1 | 30 |
| 1 | 4 | 11 |
| 32 | 4 | 11 |
| 1 | 6 | 9 |
| 32 | 6 | 9 |
| 1 | 8 | 7 |
| 32 | 8 | 7 |

Observation: several exact-count pairings strongly suggest descriptor/payload or related resource classes. This is only a **HYPOTHESIS** until entry contents are decompressed and references followed.

### References

- `0xFFFFFFFF`: 312 entries
- `0x80801AD7`: 136 entries
- `0x80800861`: 8 entries
- many references point to hashes inside package `0x005B` itself, beginning around `0x808B603A`

### Blocks

- all 626 blocks use patch id `1`
- all 626 blocks have flags `0x1`
- therefore all are compressed and none are encrypted under known flag interpretation
- no entry starts outside the block table
- no entry's calculated block span overruns the block table

### Immediate next step

Obtain an Oodle-compatible decompressor in the analysis environment, decompress all logical blocks, reconstruct every entry losslessly, then perform:

1. per-entry SHA256 and byte signatures
2. reference graph
3. 0x8080 tag structure identification
4. resource type clustering
5. mesh/texture/static-map candidate discovery
6. source-schema correlation with Charm/Phonon/tiger-pkg

## 2026-09-03 — Dependency graph and resource-class identification

Generated a package-local dependency graph from all 667 file entries.

### Reference partition

- sentinel `FFFFFFFF`: 312
- same-package FileHash references: 209
- external FileHash references: 146
- non-FileHash references: 0

All 146 external references originate from `type=16, subtype=0` entries and resolve into package-ID 0 namespace. Frequencies:

- `80801AD7`: 136
- `80800861`: 8
- `80801AF2`: 1
- `80801BD9`: 1

This strongly separates structured-tag class/shared references from local GPU/resource payload links.

### Exact local transitions

- `122 × (32,7) -> (1,7)`
- `30 × (32,1) -> (65,1)`
- `30 × (65,1) -> (5,1)`
- `11 × (32,4) -> (1,4)`
- `9 × (32,6) -> (1,6)`
- `7 × (32,8) -> (1,8)`

These relationships are saved as JSON, CSV and DOT under `evidence/graphs/ps4_arch_cabal_005b_1/`.

### D1 resource names correlated with current QuickTag

Current QuickTag's version-specific D1 classifier identifies:
- `16:0` Tag
- `32:1` Texture2D header
- `32:4 / 1:4` VertexBuffer header/data
- `32:6 / 1:6` IndexBuffer header/data
- `32:8 / 1:8` PixelShader header/data

It leaves subtype 7 unresolved/commented as ConstantBuffer for D1. We preserve that uncertainty.

### Geometry header cross-validation with Charm

- Charm `SVertexHeader` is 12 bytes; all 11 sample `32:4` entries are 12 bytes.
- Charm `SIndexHeader` is 24 bytes; all 9 sample `32:6` entries are 24 bytes.

These sample/source agreements upgrade the geometry header roles to `CONFIRMED_CROSS_SOURCE`.

### Texture reference-chain cross-validation

All 30 `32:1` Texture2D headers point to `65:1`; each of those 30 entries points to `5:1`.

Charm's D1 texture path explicitly follows a texture header reference and, when that referenced file has another valid reference, uses the second reference as the texture data source. This independently corroborates the semantic role of our exact two-hop chain.

Project-local names:
- `65:1` = `D1TextureIntermediate`
- `5:1` = `D1TextureTerminalPayload`

These are **role labels only**, not claimed official Tiger type names.

## 2026-09-03 — FileEntry `entry_b` middle-byte census

Across all 667 entries:

- bits 8..15 are always zero.
- bits 16..23 are nonzero and take exactly seven values:
  - 10: 257
  - 14: 37
  - 15: 173
  - 20: 4
  - 21: 190
  - 24: 4
  - 26: 2

The byte clearly carries structured metadata but its semantics are not yet identified. Full statistics, including type/subtype correlation, are stored in `evidence/analysis/ps4_arch_cabal_005b_1/entry_b_stats.json`.

## 2026-09-03 — Oodle decompression investigation

All sample blocks require decompression before payload-level validation. Independent current D1 implementations use Oodle 3 (`OodleLZ_Decompress`) for ROI packages.

The real sample's first compressed block begins `B7 43 E2 90 ...`, and later blocks also begin with `B7`. This is not sufficient evidence to identify the codec and is not treated as a standard modern Kraken stream.

Open-source Kraken-family implementations were reviewed as possible research aids, but have **not** been demonstrated compatible with these D1 block streams. The preferred immediate path is a user-owned `oo2core_3_win64.dll` loaded at runtime via a Linux-compatible wrapper. The proprietary runtime will not be committed into this research workspace.

## 2026-09-03 — Stored block SHA-1 semantics binary-confirmed

A dedicated verifier hashed the exact stored payload bytes for every block record in `ps4_arch_cabal_005b_1.pkg`.

- block records checked: **626**
- exact SHA-1 matches: **626 / 626**
- mismatches: **0**

Therefore, for this real PS4 Tiger v24 sample, `D1BlockEntry.sha1[20]` is **CONFIRMED_BINARY** as the SHA-1 of the block's stored on-disk payload (`offset .. offset+size`) before decompression.

Regression artifact: `evidence/packages/ps4_arch_cabal_005b_1.block_sha1_verification.json`.

## 2026-09-03 — FileEntry middle metadata byte is a reference-chain invariant

The unknown byte `entry_b[23:16]` was compared across all 209 same-package reference edges. It is preserved across **209 / 209** local links, with zero mismatches. This includes every known GPU header/data pair and every texture two-hop chain.

Examples:

- `32:7(mid=21) -> 1:7(mid=21)` — 61
- `32:7(mid=10) -> 1:7(mid=10)` — 59
- `32:1(mid=15) -> 65:1(mid=15) -> 5:1(mid=15)` — 19 chains
- `32:1(mid=14) -> 65:1(mid=14) -> 5:1(mid=14)` — 9 chains
- `32:4(mid=15) -> 1:4(mid=15)` — 11
- `32:6(mid=15) -> 1:6(mid=15)` — 8

This makes the byte very unlikely to be arbitrary per-entry data. It behaves like resource-family / allocation / streaming metadata propagated along linked resources. Its exact meaning remains **UNKNOWN**.

## 2026-09-03 — Header signature-area observation

The header field currently named `header_signature_offset` contains `0x800`. At exactly `0x800`, the package contains a dense 256-byte blob, followed by zero padding.

- offset: `0x800`
- observed blob length: `0x100` / 256 bytes
- non-zero bytes: 255 / 256
- SHA-256: `14ab10e5ee661c17cf2166916cd143c7bc988c115e23b8aae2a86d4e92d6ee6e`

The location and size are **CONFIRMED_BINARY**. Calling it a cryptographic/RSA signature remains **SOURCE_DERIVED/HYPOTHESIS** until its verification scheme/key is identified.

## 2026-09-03 — ROI structured-tag class resolution

The external/shared `reference` values on `16:0` entries were compared against QuickTag's version-specific `CLASSES_DESTINY_ROI` registry rather than a D2 or TTK registry.

Resolved in the canonical Cabal sample:

- `0x80801AD7` = `s_technique` — **136 entries**
- `0x80801BD9` = `s_expensive_light` — **1 entry**

Unresolved for ROI:

- `0x80800861` — 8 entries. QuickTag names this `s_pattern_component` in its **TTK** class table, but the ROI table uses `0x80800715` for `s_pattern_component`; therefore the TTK name is **not promoted** for our ROI sample.
- `0x80801AF2` — 1 entry, no ROI mapping found in the current QuickTag class registry.

This establishes that at least 136/146 structured tags in `arch_cabal` are shader/material **technique** tags and one is an expensive-light tag.

## 2026-09-03 — Dedicated ROI PS4 Texture2D header identified

QuickTag's current `TextureHeaderRoiPs4` parser resolves the canonical sample's `32:1` stored-size question: the struct ends at offset `0x3C`, exactly matching all 30 real Texture2D-header entry lengths. Source-derived layout: data size at `0x00`, two unknown bytes, packed GCN format at `0x06`, skipped/unknown region through `0x23`, `0xBEEFCAFE` at `0x24`, width/height/depth/array-size at `0x28..0x2F`, and three flag words at `0x30..0x3B`.

QuickTag also has a distinct ROI Xbox One header beginning with DXGI format + `tile_mode`, with `0xBEEFCAFE` at `0x2C`. This is recorded as a planned PS4↔Xbox differential validation target.

## 2026-09-03 — GitHub repository becomes canonical durable workspace

The private repository `lizardpeter/destiny-1` is now the durable source of truth. Runtime copies under `/mnt/data/Destiny1_Reversal/` are working mirrors for binary analysis and generated assets. The repository was initialized with safety ignores that exclude raw game package bytes, proprietary Oodle DLLs, compiled runtime bridges, caches, and bulk generated exports.

During migration, stale documentation was corrected before commit: the Xbox corpus is no longer marked pending mount, Oodle decompression is no longer treated as a blocker, the Xbox texture tail is retired as an unknown, and subtype 7 is promoted from loose hypothesis to `STRONGLY_SUPPORTED` ConstantBuffer role while retaining the neutral project name `GpuSubtype7`.
