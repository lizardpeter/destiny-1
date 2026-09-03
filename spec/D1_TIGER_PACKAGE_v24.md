# Destiny 1 Tiger Package v24 — Living Binary Specification

Status: **PARTIALLY SOLVED**  
Primary corpus: PS4 Rise of Iron/final-era packages.  
Secondary corpus planned: Xbox One matching packages.

## Evidence levels

- `CONFIRMED_BINARY` — demonstrated directly against supplied package bytes with internal checks/hashes.
- `CONFIRMED_CROSS_SOURCE` — direct binary evidence agrees with multiple independent implementations/source references.
- `SOURCE_DERIVED` — known from existing implementation but not yet independently proven against our corpus.
- `HYPOTHESIS` — plausible interpretation requiring validation.
- `UNKNOWN` — raw field is located but meaning unresolved.

## Endianness

PS4 final D1 package structures are little-endian. `CONFIRMED_BINARY`

## Package header

The supplied sample parses as version 24 with the following known fields. Offsets below are from the start of the package.

| Offset | Size | Type | Meaning | Status |
|---:|---:|---|---|---|
| `0x00` | 2 | u16 | version (`24`) | CONFIRMED_BINARY |
| `0x02` | 2 | u16 | platform (`7` = PS4) | CONFIRMED_CROSS_SOURCE |
| `0x04` | 2 | u16 | package id | CONFIRMED_BINARY |
| `0x06` | 2 | u16 | unknown | UNKNOWN |
| `0x08` | 8 | u64 | unknown | UNKNOWN |
| `0x10` | 8 | u64 | build time/raw timestamp-ish field | SOURCE_DERIVED; semantics incomplete |
| `0x18` | 4 | u32 | build id-ish field | SOURCE_DERIVED; semantics incomplete |
| `0x1C` | 2 | u16 | major version | CONFIRMED_BINARY |
| `0x1E` | 2 | u16 | minor version | CONFIRMED_BINARY |
| `0x20` | 2 | u16 | patch id | CONFIRMED_BINARY |
| `0x22` | 2 | u16 | language | CONFIRMED_CROSS_SOURCE |
| `0x24` | 128 | char[] | tool/build string | CONFIRMED_BINARY |
| `0xA4` | 4 | u32 | unknown | UNKNOWN |
| `0xA8` | 4 | u32 | unknown | UNKNOWN |
| `0xAC` | 4 | u32 | unknown | UNKNOWN |
| `0xB0` | 4 | u32 | header signature offset | SOURCE_DERIVED |
| `0xB4` | 4 | u32 | file-entry count | CONFIRMED_BINARY |
| `0xB8` | 4 | u32 | file-entry table offset | CONFIRMED_BINARY |
| `0xBC` | 20 | SHA1 | file-entry table SHA-1 | CONFIRMED_BINARY |
| `0xD0` | 4 | u32 | block-entry count | CONFIRMED_BINARY |
| `0xD4` | 4 | u32 | block-entry table offset | CONFIRMED_BINARY |
| `0xD8` | 20 | SHA1 | block-entry table SHA-1 | CONFIRMED_BINARY |
| `0xEC` | 4 | u32 | named-tag count | CONFIRMED_BINARY |
| `0xF0` | 4 | u32 | named-tag table offset | CONFIRMED_BINARY |
| `0xF4` | 20 | SHA1 | named-tag table SHA-1 / zero-count convention | CONFIRMED_BINARY for zero-count sample; record-table hashing otherwise SOURCE_DERIVED |
| `0x13C` | 4 | u32 | package file size | CONFIRMED_BINARY |

### Sample header — `ps4_arch_cabal_005b_1.pkg`

- version: `24`
- platform: `7` / PS4
- package id: `0x005B`
- patch id: `1`
- language: `0` / none
- tool string: `evil tool_lib test pc_x64 46419.15.08.16.1336.evil 15.08.16 1336`
- entry count: `667`
- entry table offset: `0x1000`
- block count: `626`
- block table offset: `0x4000`
- named-tag count: `0`
- file size: `89,044,992` bytes
- header file size equals actual file size: yes
- entry-table SHA-1 matches: yes
- block-table SHA-1 matches: yes
- named-tag count is zero and the stored named-tag hash is 20 zero bytes (not SHA1(empty)): yes

### Header signature-area observation

In the canonical sample, the field at `0xB0` equals `0x800`. Exactly 256 dense bytes occupy `0x800..0x8FF`, followed by zero padding. The 256-byte blob SHA-256 is `14ab10e5ee661c17cf2166916cd143c7bc988c115e23b8aae2a86d4e92d6ee6e`. Location/length are `CONFIRMED_BINARY`; cryptographic signature semantics are not yet independently verified.

## File entry — 16 bytes

```c
struct D1FileEntryRaw {
    uint32_t reference; // +0x00
    uint32_t entry_b;   // +0x04
    uint64_t block_info;// +0x08
};
```

Decoded fields currently used:

```text
file_type              = entry_b & 0xFF
file_subtype           = entry_b >> 24
starting_block         = block_info & 0x3FFF
starting_block_offset  = ((block_info >> 14) & 0x3FFF) << 4
file_size              = (block_info >> 28) & 0x3FFFFFFF
```

The starting offset is therefore 16-byte granular. `CONFIRMED_CROSS_SOURCE`

### `entry_b` middle bits — real sample census

The established type/subtype decoding leaves two middle bytes. In the Cabal sample:

```text
bits  0..7   = file_type
bits  8..15  = 0 for all 667 entries in this package
bits 16..23  = UNKNOWN structured byte
bits 24..31  = file_subtype
```

Observed values for bits 16..23:

| Value | Count |
|---:|---:|
| 10 | 257 |
| 14 | 37 |
| 15 | 173 |
| 20 | 4 |
| 21 | 190 |
| 24 | 4 |
| 26 | 2 |

These values are preserved exactly and are not currently interpreted. `CONFIRMED_BINARY` for the distribution; semantic meaning `UNKNOWN`.

### `entry_b[23:16]` propagation invariant

Across all 209 same-package reference edges in the canonical sample, the byte is preserved exactly from source to destination: **209/209 matches, 0 mismatches**. It also propagates through both hops of every observed `32:1 -> 65:1 -> 5:1` texture chain. `CONFIRMED_BINARY`.

This establishes that the byte is shared resource metadata rather than an independent value for each entry. Its semantic interpretation remains `UNKNOWN`.

### Reference graph semantics in the Cabal sample

References partition cleanly:

- 312 entries: `0xFFFFFFFF` sentinel
- 209 entries: valid references to another entry in package `0x005B`
- 146 entries: external FileHash references, all from structured `16:0` Tag entries and all in package-ID 0 namespace

Local transitions:

```text
122 × 32:7 -> 1:7
 30 × 32:1 -> 65:1 -> 5:1
 11 × 32:4 -> 1:4
  9 × 32:6 -> 1:6
  7 × 32:8 -> 1:8
```

The numeric transitions are `CONFIRMED_BINARY`; semantic resource names are tracked separately in `D1_RESOURCE_CLASSES.md`.

### TagHash / FileHash construction

For D1 package entry index `i` in package id `p`:

```text
hash32 = 0x80800000 + (p << 13) + (i mod 8192)
```

For package id `0x005B`, entry 0 is `0x808B6000`. `CONFIRMED_CROSS_SOURCE`

## Block entry — 32 bytes

```c
struct D1BlockEntry {
    uint32_t offset;
    uint32_t size;
    uint16_t patch_id;
    uint16_t flags;
    uint8_t  sha1[20];
};
```

For the canonical Cabal sample, all **626/626** records exactly match `SHA1(package[offset:offset+size])`. Thus the SHA-1 field is `CONFIRMED_BINARY` as the digest of the stored block payload before decompression for PS4 v24.

Known flag bits:

- `0x1`: compressed — CONFIRMED_CROSS_SOURCE
- `0x2`: encrypted — SOURCE_DERIVED for shared Tiger logic; not observed in sample
- `0x4`: alternate encryption key selector — SOURCE_DERIVED; not observed in sample
- `0x8`: special/unavailable/redacted-style condition in later shared tooling — semantics UNKNOWN for D1

Logical decompressed Tiger block size: `0x40000` / 262,144 bytes. `CONFIRMED_CROSS_SOURCE`

### Sample block behavior

All `626` block records in the supplied Cabal package have `flags = 0x1`, `patch_id = 1`. No encrypted blocks occur.

## File assembly

A file begins at `starting_block` + `starting_block_offset` and may continue across sequential logical 0x40000-byte decompressed blocks until `file_size` bytes are reconstructed. `CONFIRMED_CROSS_SOURCE`

## Named-tag record

Existing implementations use 68-byte D1 named-tag records consisting of:

```c
uint32_t tag_hash;
uint32_t class_hash;
uint8_t  name[60];
```

Status: `SOURCE_DERIVED`; this sample has zero named tags, so independent binary validation requires another package.

## Unknowns / required next validations

1. Precisely name/interpret header fields at `0x06`, `0x08`, `0xA4`, `0xA8`, `0xAC`.
2. Resolve exact semantics of build-time/build-id fields and `header_signature_offset`.
3. Validate the observed zero-entry named-tag hash convention across additional packages (this sample definitively stores 20 zero bytes rather than SHA1(empty)).
4. Validate all block flag semantics using packages exhibiting encryption/other flags.
5. Identify meaning of middle bits in `entry_b` currently ignored by type/subtype extraction.
6. Validate package-patch dependency rules across `_0`, `_1`, ... sibling files.
7. Build PS4↔Xbox One matched-package diff corpus.
