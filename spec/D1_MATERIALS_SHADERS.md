# Destiny 1 Materials and Shader Bindings — Living Specification

Status: **PARTIALLY SOLVED; Xbox DXBC and PS4 OrbShdr resource bindings binary-confirmed**  
Target: final-era Destiny 1 / Rise of Iron. PS4 is the primary finished-export target; Xbox One is the differential/semantic corpus.

## Evidence policy

- `CONFIRMED_BINARY`: demonstrated directly from supplied/recovered retail game bytes.
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

## Texture register binding — solved on Xbox

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

Across the same 11 Xbox pairs:

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

Additional shader cbuffers such as `b12` and `b13` are not supplied by the material-local path. They represent higher-level draw/frame/global inputs, but no semantic name is assigned until their producer is traced.

## PS4 subtype `32:7` material constants — exact representation

PS4 `SMaterial_ROI +0x32C` references FileEntries with:

```text
type    = 32
subtype = 7
size    = 0x10
```

The representation is now directly decoded from retail PS4 bytes:

```text
32:7 GPU-resource header (16 bytes)
  +0x00 u32  unknown
  +0x04 u32  unknown
  +0x08 u32  unit_count          CONFIRMED_BINARY
  +0x0C u32  marker/unknown

FileEntry.Reference
  -> raw payload entry
       byte_size = unit_count * 16
       Vec4[unit_count]
```

The first two words and `+0x0C` remain unnamed; they are preserved losslessly.

Corpus evidence already established:

- 122/122 observed `32:7` headers are exactly 16 bytes.
- 122/122 linked payload metadata sizes equal `unit_count * 16`.
- recovered Vex material containers decode to ordinary IEEE-754 float4 arrays with exact raw-u32 preservation.

Concrete target fixture:

- `809C475F` / PS `80AAE14B` -> container `80AAE14C` -> **19 vec4s**.
- `816CE240` / PS `816CE0A8` -> container `816CE185` -> **8 vec4s**.
- all six `816CE240..244/816CE1A7` variant-1 alternatives likewise provide 8 vec4s and differ only in a small subset of those constants.

Because the Xbox semantic counterpart feeds pixel constant buffer `b0`, and the PS4 native shader metadata independently declares immediate constant-buffer API slot 0 for both target pixel shaders, the PS4 subtype-7 payload is now **CONFIRMED_CROSS_PLATFORM_SEMANTIC** material pixel-constant data.

Reusable decoder:

- `tools/d1_vector_container_probe.py`

It handles both the PS4 `32:7 -> raw Vec4 payload` representation and the Xbox `0x80801AA5` structured representation while preserving exact float and raw-u32 forms.

## PS4 native pixel shaders and `OrbShdr` metadata — resource binding solved

### D1 engine shader header

The PS4 D1 pixel-shader resource observed here is FileEntry `type=32, subtype=8` with a small engine header. `tools/d1_entry_extract.py` already validates the packed shader-header word:

- low 24 bits = referenced native shader payload byte size.
- high 8 bits = native shader InputUsageSlot count.
- FileEntry.Reference = native Orbis GCN shader payload entry.

### Native Orbis binary framing

The referenced payload uses the standard Sony/Orbis `OrbShdr` representation. Retail target bytes validate the public Gnm structure exactly:

```text
u32 token[0] = BEEB03FF
u32 token[1] = sizeInWords immediate
```

`BEEB03FF` is itself the standard leading GCN instruction `s_mov_b32 vcc_hi, #imm`.

The 28-byte `ShaderBinaryInfo` footer is located by the source-correlated rule:

```text
footer = token + (token[1] + 1) * 2 dwords
       = byte offset (token[1] + 1) * 8
```

For both target shaders:

- the formula lands exactly on the sole `OrbShdr` signature in the native payload;
- the footer's stage field is PixelShader;
- the footer's code-length field ends before the InputUsageSlot/usage-mask region with exact accounting;
- the footer InputUsageSlot count equals the high byte of the D1 engine header's packed word.

This is `CONFIRMED_CROSS_SOURCE`, not a filename/signature guess.

Reusable decoder:

- `tools/d1_ps4_shader_binary_probe.py`

The tool resolves the D1 engine shader header to its native payload, validates the declared size, locates/parses `OrbShdr`, extracts the exact machine-code span, and decodes Sony `InputUsageSlot` records.

### Target PS `80AAE14B` — main Vex surface

D1 header:

```text
shader               80AAE14B
native payload        80AAE14D
native payload size   1028 bytes
InputUsageSlot count  9
```

Native binary:

```text
OrbShdr footer offset 1000
GCN code length       956 bytes
bytes after code and before footer = 44
  9 InputUsageSlots * 4 = 36 bytes
  2 usage-mask dwords   = 8 bytes
```

Decoded input usage:

```text
PtrExtendedUserData             API 1   user SGPR 2
ImmSampler                      API 1   user SGPR 4
ImmSampler                      API 2   user SGPR 8
PtrResourceTable                API 0   user SGPR 12   chunk mask 1
ImmSampler                      API 3   user SGPR 16
ImmSampler                      API 4   user SGPR 20
ImmSampler                      API 5   user SGPR 24
ImmConstBuffer                  API 0   user SGPR 28
ImmConstBuffer                  API 12  user SGPR 32
```

Usage masks:

```text
0000001F
00000000
```

The first mask has exactly five low resource-table chunks active, matching the five serialized PS texture records and five immediate samplers of material `809C475F`. Thus this shader receives its five sampled-image descriptors through a flat resource table rather than five immediate `ImmResource` records.

### Target PS `816CE0A8` — variant-1 Vex circuitry/palette path

Latest retail patch namespace resolves:

```text
shader               816CE0A8
native payload        816CE0AE
native payload size   580 bytes
InputUsageSlot count  8
```

Native binary:

```text
OrbShdr footer offset 552
GCN code length       516 bytes
bytes after code and before footer = 36
  8 InputUsageSlots * 4 = 32 bytes
  1 usage-mask dword    = 4 bytes
```

Decoded input usage:

```text
PtrExtendedUserData             API 1   user SGPR 2
ImmResource (T# texture/image)  API 0   user SGPR 4
ImmSampler                      API 1   user SGPR 12
ImmResource (T# texture/image)  API 1   user SGPR 16
ImmSampler                      API 2   user SGPR 24
ImmConstBuffer                  API 0   user SGPR 28
ImmConstBuffer                  API 12  user SGPR 32
ImmConstBuffer                  API 13  user SGPR 36
```

This exactly matches material `816CE240`'s two PS texture records and two PS sampler records: unlike `80AAE14B`, this shader binds the two texture descriptors directly as immediate resources.

### Current instruction-level boundary

The resource/register binding layer is solved without requiring Xbox assistance. What remains is **shader instruction dataflow semantics**, especially:

- which `80AAE14B` texture-table chunk feeds base color, normal/detail, cube/environment, and other terms;
- the exact role of the duplicate `816CE1C5` samples in `816CE0A8`;
- how the eight variant-1 `b0` vec4s drive palette/recolor/emissive output;
- exact output packing/blending behavior before mapping the native material to portable glTF PBR.

LLVM 18 exposes the gfx700 targets but deliberately has no disassembler implementation for those old subtargets (`Disassembly not yet supported for subtarget`). This is a tooling limitation, not invalid shader data. The current instruction-analysis path therefore uses a GCN-1.1-capable decoder (CLRX/GPCS4) against the exact `OrbShdr`-bounded code bytes.

## Current Vex evidence relevant to portable material reconstruction

`816CE0A8`'s six parent-selected material alternatives use the same shader and the same two copies of grayscale BC1 texture `816CE1C5`. Their 8-vec4 `b0` blocks share several exact constants, including:

```text
vec2 = [0.4, 0, 0, 0]
vec3 = [0.30, 0.59, 0.11, 0]
vec6 = [1, 1, 1, 1]
```

`[0.30, 0.59, 0.11]` is the canonical RGB-luminance coefficient triplet. Variant differences are concentrated in vec4/vec5 and sometimes vec7; one alternative changes vec7.x from `5` to `40`. Combined with the grayscale source image, this is strong evidence for a palette/recolor and intensity/emissive-style path, but the exact semantic names remain **PROVISIONAL** until native instruction dataflow proves which constants feed which output operation.

## Remaining work

1. Finish instruction-level GCN 1.1 dataflow decode for `80AAE14B` and `816CE0A8`.
2. Prove PS4 serialized `STextureTag.TextureIndex` values against the native resource-table/immediate API slots for the two target materials.
3. Trace higher-level constant buffers `b12` and `b13` to their producer classes/resources.
4. Map sampler-record tail fields and sampler state semantics.
5. Convert the exact Destiny Vex materials to portable glTF PBR/emissive approximations while preserving original parent/material/shader/texture hashes and native binding metadata losslessly in `extras`.
