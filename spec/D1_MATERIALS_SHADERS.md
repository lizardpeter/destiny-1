# Destiny 1 Materials and Shader Bindings — Living Specification

Status: **PARTIALLY SOLVED; Xbox register bindings binary-confirmed**  
Target: final-era Destiny 1 / Rise of Iron. PS4 is the primary finished-export target; Xbox One is the differential/semantic corpus.

## Evidence policy

- `CONFIRMED_BINARY`: demonstrated directly from supplied game bytes.
- `CONFIRMED_CROSS_SOURCE`: binary evidence agrees with an independent implementation/schema.
- `CONFIRMED_CROSS_PLATFORM_SEMANTIC`: PS4/Xbox independently identify the same engine-level role.
- `SOURCE_DERIVED`: implementation/schema evidence not yet directly validated in current bytes.
- `UNKNOWN`: deliberately unresolved.

## Material classes

### PS4 ROI

Charm's D1 `SMaterial_ROI` schema is serialized as little-endian class bytes `D71A8080`, numeric class `0x80801AD7`. The canonical PS4 Cabal package contains 136 instances.

Important offsets:

| Offset | Meaning | State |
|---:|---|---|
| `0x28` | VertexShader | SOURCE_DERIVED |
| `0x38` | VS textures | SOURCE_DERIVED |
| `0x50` | VS TFX bytecode | SOURCE_DERIVED |
| `0x70` | VS samplers | SOURCE_DERIVED |
| `0xAC` | VS vector4 container | SOURCE_DERIVED |
| `0x2A8` | PixelShader | CONFIRMED_CROSS_SOURCE |
| `0x2B8` | PS texture bindings | CONFIRMED_CROSS_PLATFORM_SEMANTIC |
| `0x2D0` | PS TFX bytecode | SOURCE_DERIVED |
| `0x2F0` | PS sampler bindings | CONFIRMED_CROSS_PLATFORM_SEMANTIC |
| `0x300` | inline PS constant vec4 array when no external container is used | CONFIRMED_BINARY on Xbox semantic counterpart |
| `0x32C` | PS vector4/constant container | CONFIRMED_CROSS_PLATFORM_SEMANTIC |

The PS4 sample has 88 material references at exactly `+0x32C` to `32:7` GPU-resource headers.

### Xbox One ROI

Real model-part references identify structured class `0x80801C32` as the Xbox material family. The core semantic offsets above are retained even though platform-native shader and texture serialization differs.

Across 411 resident Xbox material tags:

- 396 reference class `0x80801B7C` at `+0x2A8`.
- 232 reference class `0x80801AA5` at `+0x32C`.

## Xbox inline DXBC pixel shaders

Class `0x80801B7C` is a D1 Xbox pixel-shader inline-DXBC container.

Observed binary invariants over 27/27 resident instances:

- tag begins with a `0x30`-byte header.
- `u64 +0x00` equals actual tag size.
- `u64 +0x08` equals DXBC byte size.
- complete DXBC begins at `+0x30`.
- DXBC chunk sequence is `ISGN`, `OSGN`, `SHEX`.
- SHEX version token is pixel shader model 5.0 (`0x00000050`).

`0x80801AB4` is a source-indicated sibling Xbox inline-DXBC shader class, expected to cover vertex shaders; direct validation awaits a package containing resident examples.

## Texture register binding — solved

Xbox material `STextureTag` records are:

```text
+0x00 u32 TextureIndex
+0x04 u32 Texture TagHash
```

`TextureIndex` is the actual DXBC texture register number `t#`.

Every resident material/shader overlap validates exactly:

- compared: **11**
- material texture register set == DXBC declared texture register set: **11/11**
- mismatches: **0**

Example:

```text
material 808B3A25:
  material TextureIndex = [0,1,2,3]
  shader declarations   = Texture2D t0, TextureCube t1, Texture2D t2, Texture2D t3
```

## Sampler binding

Across the same 11 pairs:

- material PS sampler count == DXBC sampler declaration count: **11/11**.
- shader sampler registers are contiguous `s1..sN`: **11/11**.

The material sampler records are 16 bytes. The first dword is a sampler FileHash. Current overlap contains two hashes, `80AAD3F3` and `80AAD3F1`, both pointing into Xbox package `0x156`. Their trailing 12 bytes remain unnamed. The actual referenced sampler payload is a D3D11 sampler descriptor behind a small sampler header; package `0x156` is therefore a high-value shared dependency.

## Xbox vector container `0x80801AA5` — exact layout

There are 595 entries in the Xbox package and 276 resident in patch 1. All 276/276 satisfy:

```text
+0x00 u64 file_size               == actual size
+0x08 u64 payload_size            == file_size - 0x30
+0x10 u64 element_stride          == 0x10
+0x18 u32 zero                    == 0
+0x1C u32 marker                  == 0x80800184
+0x20 u64 payload_size_repeat     == payload_size
+0x28 u32 element marker          == 0x80800009
+0x2C u32 zero                    == 0
+0x30 Vec4 payload[]
```

Therefore:

```text
vector_count = (file_size - 0x30) / 16
```

## Pixel constant buffer `b0` — solved

For every comparable Xbox material/pixel shader:

- material-provided vector count == DXBC `cbuffer b0` declared vec4 count: **11/11**.

Two material storage modes feed `b0`:

1. external `PSVector4Container` at `+0x32C` -> class `0x80801AA5`.
2. when the external container is invalid/absent, the inline vec4 array at `+0x300` supplies `b0`.

The external container formula is binary-proven, so even two patch-0-backed containers have recoverable vector counts from entry metadata size.

Additional shader cbuffers such as `b12[8]` and `b13[2]` are not supplied by the material-local path. They likely represent higher-level draw/frame/global inputs, but no semantic name is assigned until their producer is traced.

## Cross-platform consequence for PS4 subtype 7

PS4 `SMaterial_ROI +0x32C` references `32:7`; Xbox's corresponding field provides exactly the vec4 data consumed as pixel `b0`.

PS4 binary evidence additionally shows:

- 122/122 `32:7` headers are 16 bytes.
- 122/122 linked payload sizes equal `unit_count * 16`.

Therefore D1 subtype 7 is now semantically confirmed as **material constant/vector-buffer data** across platforms. The exact original Bungie class/type name remains unclaimed.

## Remaining work

1. Acquire/resolve Xbox package `0x156` and decode shared vertex shaders and sampler descriptors.
2. Map sampler-record tail fields.
3. Trace non-`b0` constant buffers (`b12`, `b13`, ...).
4. Decode enough PS4 GCN resource usage to reproduce register-level bindings without Xbox assistance.
5. Convert Destiny materials to portable glTF PBR approximations while preserving original material/shader metadata losslessly.
