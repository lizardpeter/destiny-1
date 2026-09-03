# Destiny 1 Entity Models — Living Specification

Status: **PARTIALLY SOLVED / METADATA-DRIVEN EXPORT WORKING**  
Target: final-era Destiny 1 / Rise of Iron Tiger.  
Primary export target: PS4. Differential corpus: Xbox One.

## Evidence levels

- `CONFIRMED_BINARY` — demonstrated directly from supplied Destiny package bytes.
- `CONFIRMED_CROSS_SOURCE` — binary evidence agrees with an independent implementation/schema.
- `SOURCE_DERIVED` — known from an implementation but not yet independently validated in our bytes.
- `STRONGLY_SUPPORTED` — multiple binary constraints identify a semantic role without complete field proof.
- `UNKNOWN` — intentionally unresolved.

## `s_entity_model`

D1 class hash: `0x80801AB5` (`B51A8080` little-endian schema bytes).  
Charm source layout size: `0x44`.  
Xbox corpus directly validates the header and mesh-array pointer behavior.

| Offset | Field | Status |
|---:|---|---|
| `0x00` | u64 file size | CONFIRMED_CROSS_SOURCE |
| `0x08` | reserved/unknown through array header prelude | PARTIAL |
| `0x10` | DynamicArray of `SEntityModelMesh` | CONFIRMED_CROSS_SOURCE |
| `0x20` | Vector4 unknown | SOURCE_DERIVED / semantics UNKNOWN |
| `0x30` | u64 unknown | SOURCE_DERIVED / semantics UNKNOWN |
| `0x38` | u64 flags/unknown | SOURCE_DERIVED / semantics UNKNOWN |

D1 model transforms live in each mesh rather than in the root model record.

## DynamicArray encoding used here

The D1 arrays validated so far use the 16-byte Tiger DynamicArray form:

```text
+0x00 u32 count
+0x04 u32 unknown/reserved
+0x08 i64 relative pointer
```

The element data address is:

```text
(pointer_field_address at +0x08) + relative_value + 0x10
```

This matches Charm's `DynamicArray<T>` implementation and resolves cleanly in the real Xbox model tags.

## `SEntityModelMesh`

D1 class hash: `0x80801BBF` (`BF1B8080`).  
Record size: `0xA0`.

| Offset | Field | Status |
|---:|---|---|
| `0x00` | Vector4 model scale | CONFIRMED_CROSS_SOURCE |
| `0x10` | Vector4 model translation | CONFIRMED_CROSS_SOURCE |
| `0x20` | Vector2 texcoord scale | CONFIRMED_CROSS_SOURCE |
| `0x28` | Vector2 texcoord translation | CONFIRMED_CROSS_SOURCE |
| `0x30` | VertexBuffer 1 hash — positions / primary stream | CONFIRMED_CROSS_SOURCE |
| `0x34` | VertexBuffer 2 hash — UV/normal/tangent stream | CONFIRMED_CROSS_SOURCE |
| `0x38` | old weights VertexBuffer hash or `FFFFFFFF` | SOURCE_DERIVED / observed |
| `0x3C` | unknown resource/hash | UNKNOWN |
| `0x40` | IndexBuffer hash | CONFIRMED_CROSS_SOURCE |
| `0x44` | zero/unknown u32 in current Xbox models | UNKNOWN |
| `0x48` | DynamicArray of mesh parts (`0x24` each) | CONFIRMED_CROSS_SOURCE |
| `0x58` | stage/part offset region | platform differential; see below |

### D1 Xbox One tail — binary-confirmed

Across **23/23 resident Xbox meshes** from `xboxone_arch_cabal_0059_1`:

- `0x58..0x7F`: 20 little-endian int16 stage-part offsets.
- offsets are monotonic.
- first offset is 0.
- last offset equals the exact mesh `part_count`.
- `0x80..0x93`: 20-byte ASCII slot; observed as 19 printable characters + NUL.
- `0x94..0x9F`: 12 zero bytes.

This means the real Xbox One D1 record is **not byte-for-byte equivalent** to Charm's PS4-oriented annotation of 30 shorts beginning at `0x58`. The high-level semantic region is shared, but this tail is platform-specific or under-described upstream. PS4 must be validated with a PS4 package that actually contains `s_entity_model` before assigning its exact tail layout.

Observed Xbox stage codes include:

```text
000-00000000-000000
///-////////-//////
DDDDDDDDDDDDDDDDDDD
111-11111111-111111
```

The exact meaning of the code remains unknown.

## Mesh part record

D1 record size: `0x24`; Charm D1 schema class bytes `EF1A8080`.

| Offset | Field | Status |
|---:|---|---|
| `0x00` | material hash / material binding | CONFIRMED_CROSS_SOURCE role |
| `0x04` | int16 variant shader index | SOURCE_DERIVED |
| `0x06` | int16 primitive type | CONFIRMED_CROSS_SOURCE |
| `0x08` | u32 index offset | CONFIRMED_CROSS_SOURCE |
| `0x0C` | u32 index count | CONFIRMED_CROSS_SOURCE |
| `0x10` | u32 unknown | UNKNOWN |
| `0x14` | u32 unknown | UNKNOWN |
| `0x18` | int16 external identifier | SOURCE_DERIVED |
| `0x1A` | byte unknown | UNKNOWN |
| `0x1B` | byte unknown | UNKNOWN |
| `0x1C` | int16 D1 flags | SOURCE_DERIVED / partly consumed |
| `0x1E` | byte gear-dye change-color index | SOURCE_DERIVED |
| `0x1F` | byte LOD category | CONFIRMED_CROSS_SOURCE |
| `0x20` | byte unknown | UNKNOWN |
| `0x21` | byte LOD run | SOURCE_DERIVED |
| `0x22..0x23` | tail | UNKNOWN |

Primitive type values:
- `3` = triangles.
- `5` = triangle strip.

Known D1 LOD category values from Charm:
- `0` MainGeom0
- `1` GripStock0
- `2` Stickers0
- `3` InternalGeom0
- `4` LowPolyGeom1
- `7` LowPolyGeom2
- `8` GripStockScope2
- `9` LowPolyGeom3
- `10` Detail0

## D1 vertex unpack transforms

Primary D1 position stream values are signed normalized 16-bit values for the standard packed layouts:

```text
normalized = max(raw_i16 / 32767.0, -1.0)
```

D1 model position transform:

```text
position.xyz = normalized_position.xyz * mesh.ModelScale.xyz
             + mesh.ModelTranslation.xyz
```

D1 UV transform:

```text
u = raw_snorm_u * TexcoordScale.x + TexcoordTranslation.x
v = raw_snorm_v * -TexcoordScale.y + 1 - TexcoordTranslation.y
```

These formulas now drive `tools/d1_entity_model_export.py`.

## First metadata-driven model export

Xbox model TagHash `808B3A16` is fully resident in patch 1 and contains two meshes whose required VB/IB resources are all available.

Validated resource counts:

### Mesh 0
- 243 vertices in VB0, stride `0x08`.
- 243 vertices in VB1, stride `0x0C`.
- 750 u16 indices.
- 7 mesh-part records.
- unique triangle ranges: `0/612`, `612/126`, `738/12`.

### Mesh 1
- 911 vertices in VB0, stride `0x08`.
- 911 vertices in VB1, stride `0x14`.
- 2151 u16 indices.
- 9 mesh-part records.
- unique triangle ranges: `0/2049`, `2049/84`, `2133/18`.

`tools/d1_entity_model_export.py` uses the actual mesh transforms, UV transforms, part index ranges, decoded normals and candidate material hashes to produce a metadata-driven GLB. This is materially stronger than the earlier adjacency-based topology proofs.

## Material differential discovered from model parts

The local material hashes referenced by `808B3A16` are `16:0` tags whose class reference is **`0x80801C32`**. This role is therefore `STRONGLY_SUPPORTED` as the Xbox One D1 material class for this corpus.

For the current Xbox materials:
- material `+0x2A8` overwhelmingly references class `0x80801B7C`; reconstructed targets contain literal `DXBC` shader containers.
- material `+0x32C` frequently references class `0x80801AA5`; reconstructed targets are packed float/vector containers.
- material offsets around `0x404`, `0x40C`, `0x414`, `0x41C` commonly contain Texture2D/Cube TagHashes.

This closely mirrors the semantic positions in the PS4 ROI material schema while using Xbox-native DXBC shader payloads.

## Next model milestones

1. Decode Xbox material `0x80801C32` field-by-field and bind textures to model parts.
2. Resolve material variants/external-material selection rather than retaining all candidates.
3. Validate the exact PS4 `SEntityModelMesh` tail with a PS4 model-containing package.
4. Connect entity-resource parents to skeleton definitions and model instances.
5. Decode the D1 skeleton hierarchy/default/inverse transforms.
6. Decode `s_animation_clip` (`0x808005A1`) and bind clips to skeleton nodes.
7. Generalize to a one-command model/weapon export pipeline.
