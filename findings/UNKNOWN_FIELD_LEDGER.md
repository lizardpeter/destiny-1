# Unknown Field Ledger

This ledger is authoritative for unresolved data. An entry remains here until evidence promotes it; guesses are never silently removed.

| Structure/class | Offset/bits | Raw observation | Status | Validation needed |
|---|---|---|---|---|
| PackageHeader | `0x06` u16 | PS4 sample `1` | UNKNOWN | compare many PS4/XONE packages |
| PackageHeader | `0x08` u64 | PS4 `14312810885725482588` | UNKNOWN | cross-package/platform clustering |
| PackageHeader | `0x10` u64 | PS4 `1439861753` | PARTIAL | exact build-time epoch/semantics |
| PackageHeader | `0x18` u32 | PS4 `46419` | PARTIAL | likely build id; correlate wider corpus |
| PackageHeader | `0xA4` u32 | PS4 `654` | UNKNOWN | cross-corpus |
| PackageHeader | `0xA8` u32 | PS4 `1713152099` | UNKNOWN | cross-corpus |
| PackageHeader | `0xAC` u32 | PS4 `2` | UNKNOWN | cross-corpus |
| Header signature area | 256-byte blob at `header_signature_offset` | dense region on PS4 and Xbox | PARTIAL | identify cryptographic algorithm/key and verification procedure |
| FileEntry.entry_b | bits `8..15` | zero across canonical PS4 sample | UNKNOWN | determine reserved vs meaningful using larger corpus |
| FileEntry.entry_b | bits `16..23` | seven PS4 values; preserved 209/209 PS4 and 3171/3171 Xbox local edges | PARTIAL / semantics UNKNOWN | correlate with package family, streaming/allocation/resource grouping |
| GPU subtype 7 | `32:7 / 1:7` | 16-byte header; unit_count×16 payload; 88 technique refs | STRONGLY_SUPPORTED ConstantBuffer role | confirm through D1 shader/technique binding semantics |
| D1 texture chain | type `65:1` | first hop in two-hop texture path | ROLE SOLVED / OFFICIAL NAME UNKNOWN | wider corpus + structured consumer |
| D1 texture chain | type `5:1` | terminal texture payload | ROLE SOLVED / OFFICIAL NAME UNKNOWN | wider corpus + official class correlation |
| PS4 Texture2D | `0x04..0x05` | two unknown bytes | UNKNOWN | correlate format/mips/tile state across textures |
| PS4 Texture2D | `0x08..0x23` | unparsed region | UNKNOWN | field-by-field cross-texture/platform analysis |
| Xbox Texture2D/Cube | `0x08..0x2B` | unparsed region | UNKNOWN | correlate against Durango surface metadata and PS4 semantics |
| VertexBuffer | header `type` at `0x06` | decoded but semantic values not fully mapped | PARTIAL | bind to D1 mesh layouts/model tags |
| IndexBuffer | `0x00` and `0x02` | canonical values 1 / 0 | UNKNOWN | compare topology/resource variants |
| PixelShader header | words after packed word 0 | payload-size/input-slot word solved; remainder not fully named | PARTIAL | correlate GCN registers/resource tables and other shader stages |
| NamedTag | 68-byte record | no records in canonical PS4 sample | SOURCE_DERIVED | validate package with named tags |
| NamedTag | zero-count hash | 20 zero bytes | CONFIRMED_BINARY for PS4 sample | compare additional zero-count v24 packages |
| BlockEntry.flags | `0x2` | absent in current samples | SOURCE_DERIVED | validate encrypted D1 package |
| BlockEntry.flags | `0x4` | absent | SOURCE_DERIVED | validate alternate-key behavior |
| BlockEntry.flags | `0x8` | absent | UNKNOWN | locate D1 package where set |
| Oodle 3 stream | exact codec enum / internal `B7...` framing | decoding works with Oodle 3 and produces valid `0x40000` blocks | INTERNAL FORMAT UNKNOWN / PIPELINE SOLVED | identify codec/framing only if useful; no longer an extraction blocker |

## Retired unknowns

The following were removed from the active ledger after binary validation:

- Xbox texture `0x38..0x43` tail → `flags1`, `flags2`, `flags3`.
- PS4 Texture2D stored length → exact `0x3C`.
- Xbox Texture2D/Cube stored length → exact `0x44` in observed ROI corpus.
- Oodle compatibility as an extraction blocker → resolved; real PS4/Xbox blocks decompress successfully.
- PixelShader header word 0 → `(num_input_usage_slots << 24) | payload_size`.

## `entry_b[23:16]` current constraint

This byte is not arbitrary per-entry metadata. It is preserved across every observed local resource reference edge in both current corpora, including multi-hop texture chains. Candidate semantic families include inherited resource grouping, streaming/allocation class, or another package-generation property. Do not name it until cross-package evidence separates those possibilities.
