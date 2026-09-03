# Destiny 1 Tiger Resource Classes — Living Map

Status: **PARTIALLY SOLVED**  
Target strategy: final-era Destiny 1 / Rise of Iron Tiger v24.  
Primary binary corpus: PS4. Xbox One is retained for differential validation.

## Evidence policy

A numeric type/subtype is not given an official semantic name unless the evidence supports it. A D2 mapping is never automatically promoted to D1.

- `CONFIRMED_BINARY`: directly demonstrated from supplied bytes.
- `CONFIRMED_CROSS_SOURCE`: supplied bytes + independent implementation/spec agree.
- `SOURCE_DERIVED`: present in a current implementation but not yet directly demonstrated in our corpus.
- `STRONGLY_SUPPORTED`: multiple binary constraints support the semantic role, but a D1-specific semantic confirmation is still missing.
- `HYPOTHESIS`: plausible, not sufficiently demonstrated.
- `UNKNOWN`: intentionally unresolved.

## Known D1 package resource classes

| Type | Subtype | Role | Status | Current evidence |
|---:|---:|---|---|---|
| 16 | 0 | structured Tiger Tag | CONFIRMED_CROSS_SOURCE | 146 PS4 entries; class refs resolve to ROI tag classes |
| 32 | 1 | Texture2D header | CONFIRMED_CROSS_SOURCE | 30 PS4 headers decoded/exported; 267 Xbox headers observed |
| 65 | 1 | D1 texture intermediate / large-buffer first hop | CONFIRMED_CROSS_SOURCE role; official name UNKNOWN | two-hop texture chains |
| 5 | 1 | D1 texture terminal payload | CONFIRMED_CROSS_SOURCE role; official name UNKNOWN | terminal texture bytes |
| 1 | 1 | Texture2D direct data | CONFIRMED_BINARY | direct-payload Xbox texture mode |
| 32 | 2 | TextureCube header | CONFIRMED_CROSS_SOURCE | 4 Xbox headers, 0x44 bytes |
| 1 | 2 | TextureCube data | CONFIRMED_BINARY role | Xbox local reference pairs |
| 32 | 3 | Texture3D header | SOURCE_DERIVED | not yet validated in current payload corpus |
| 32 | 4 | VertexBuffer header | CONFIRMED_CROSS_SOURCE | PS4 + Xbox decoded headers |
| 1 | 4 | VertexBuffer data | CONFIRMED_CROSS_SOURCE | sizes/strides validated |
| 32 | 6 | IndexBuffer header | CONFIRMED_CROSS_SOURCE | PS4 + Xbox decoded headers |
| 1 | 6 | IndexBuffer data | CONFIRMED_CROSS_SOURCE | u16/u32 topology validated |
| 32 | 7 | `GpuSubtype7` header; likely D1 ConstantBuffer | STRONGLY_SUPPORTED | 122 PS4 headers; payload size = unit_count×16; 88 ROI material PSVector4Container refs |
| 1 | 7 | `GpuSubtype7` data | STRONGLY_SUPPORTED | linked payload family |
| 32 | 8 | PixelShader header | CONFIRMED_CROSS_SOURCE | 7 PS4 headers; packed size/input-slot field solved |
| 1 | 8 | PixelShader native data | CONFIRMED_CROSS_SOURCE | GCN + OrbShdr parsed |
| 32 | 9 | VertexShader header | SOURCE_DERIVED | absent from canonical PS4 sample |
| 32 | 16 | TextureSampler header | CONFIRMED_BINARY role / SOURCE_DERIVED name | observed in Xbox graph |
| 1 | 16 | TextureSampler data | CONFIRMED_BINARY role | Xbox local pairs |
| 128 | 0 | TagGlobal | SOURCE_DERIVED | not present in canonical PS4 sample |
| 0 | 19 | Wwise init bank | SOURCE_DERIVED | D1 classifier |
| 0 | 20 | Wwise bank | CONFIRMED_CROSS_SOURCE class | Xbox corpus contains 35 |
| 8 | 21 | Wwise stream | CONFIRMED_CROSS_SOURCE class | Xbox corpus contains 68 |

## D1 Texture2D storage modes

Two storage patterns are now observed:

```text
Direct:
32:1 Texture2D header -> 1:1 texture data

Large/two-hop:
32:1 Texture2D header -> 65:1 intermediate -> 5:1 terminal texture payload
```

The canonical PS4 package contains 30 two-hop Texture2D chains. The Xbox sample contains both modes. Public D1 texture implementations independently follow the second reference when present, corroborating the semantic storage role.

`65:1` and `5:1` are project-local role labels only; their official Tiger class names remain unknown.

## Geometry cross-checks

- Vertex header is `0x0C`; decoded `data_size`, stride, type, and platform marker are validated.
- Index header is `0x18`; decoded `data_size`, index-width flag and marker are validated.
- D1 vertex layouts have dedicated decoding logic and must not inherit D2 assumptions.
- Six PS4 vertex/index groups have independently matching vertex counts and index maxima and are exportable as topology proof GLBs.

See `spec/D1_GPU_RESOURCES.md` for field-level layouts.

## ROI texture headers

### PS4 Texture2D

- exact header size `0x3C`.
- `0xBEEFCAFE` at `0x24`.
- dimensions at `0x28..0x2F`.
- flags1/2/3 at `0x30..0x3B`.
- all 30 canonical headers were reconstructed and exported through the actual Oodle + reference + GCN deswizzle pipeline.

### Xbox One Texture2D / Cube

- exact observed header size `0x44`.
- DXGI format at `0x00`; tile mode at `0x04`.
- `0xBEEFCAFE` at `0x2C`.
- dimensions at `0x30..0x37`.
- flags1/2/3 at `0x38..0x43`.

The former 12-byte Xbox tail is therefore solved, not padding.

## Subtype 7 status

Do not silently rename D1 subtype 7 to ConstantBuffer yet. However, the case is now strong:

- 122/122 PS4 headers are exactly 16 bytes.
- 122/122 linked payloads satisfy `payload_size = header.unit_count * 16`.
- all headers use marker `0x20077FAC` in the canonical sample.
- 88 ROI PS4 material tags (`0x80801AD7 = SMaterial_ROI`) reference a subtype-7 header at exact offset `0x32C`, which Charm identifies as `PSVector4Container`.
- later Tiger generations map subtype 7 to ConstantBuffer, while QuickTag deliberately leaves the D1 mapping commented.

Canonical project term remains `GpuSubtype7` until the exact official D1 semantic name is confirmed.

## Next validations

1. Continue model/entity/static-map tags that bind GPU resources to actual objects, parts, LODs, transforms and materials; metadata-driven entity-model export is now working on Xbox.
2. Resolve official names/semantics for type `65:1` and `5:1` across a wider texture corpus.
3. Promote the exact semantic name for D1 subtype 7 using material/shader binding semantics; `PSVector4Container` usage is now source-correlated.
4. Validate VertexShader and additional shader classes from packages where they occur.
5. Implement Xbox Durango detiling and validate full texture export.
