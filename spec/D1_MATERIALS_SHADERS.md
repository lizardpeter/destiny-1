# Destiny 1 Materials and Shader Bindings — Living Specification

Status: **PS4/Xbox material texture registers, material b0 constants, PS4 native sampler descriptors, and target shader dataflow substantially solved**  
Target: final-era Destiny 1 / Rise of Iron. PS4 is the primary finished-export target; Xbox One is the differential/semantic corpus.

## Evidence policy

- `CONFIRMED_BINARY`: demonstrated directly from supplied/recovered retail game bytes.
- `CONFIRMED_CROSS_SOURCE`: binary evidence agrees with an independent implementation/schema.
- `CONFIRMED_CROSS_PLATFORM_SEMANTIC`: PS4/Xbox independently identify the same engine-level role.
- `SOURCE_DERIVED`: implementation/schema evidence not yet directly validated in current bytes.
- `UNKNOWN`: deliberately unresolved.

## Material classes

### PS4 ROI

Charm's D1 `SMaterial_ROI` schema is serialized as little-endian class bytes
`D71A8080`, numeric class `0x80801AD7`.

Important offsets:

| Offset | Meaning | State |
|---:|---|---|
| `0x28` | VertexShader | CONFIRMED_CROSS_SOURCE |
| `0x38` | VS textures | CONFIRMED_CROSS_SOURCE |
| `0x50` | VS TFX bytecode | CONFIRMED_CROSS_SOURCE |
| `0x70` | VS sampler records | CONFIRMED_CROSS_SOURCE |
| `0xAC` | VS vector4 container | CONFIRMED_CROSS_SOURCE |
| `0x2A8` | PixelShader | CONFIRMED_CROSS_SOURCE |
| `0x2B8` | PS texture records | CONFIRMED_CROSS_PLATFORM_SEMANTIC |
| `0x2D0` | PS TFX bytecode | CONFIRMED_CROSS_SOURCE |
| `0x2F0` | PS sampler records | CONFIRMED_CROSS_SOURCE |
| `0x300` | inline PS constant vec4 array when no external container is used | CONFIRMED_BINARY on Xbox semantic counterpart |
| `0x32C` | PS vector4/constant container | CONFIRMED_CROSS_PLATFORM_SEMANTIC |

### Xbox One ROI

Real model-part references identify structured class `0x80801C32` as the Xbox
material family. The same engine-level texture-index and material-constant
semantics survive despite different native shader/resource representations.

Across the established Xbox Cabal corpus:

- 411 resident material tags;
- 396 reference pixel-shader class `0x80801B7C` at `+0x2A8`;
- 232 reference vector-container class `0x80801AA5` at `+0x32C`.

## `STextureTag` layout and texture-register semantics — solved

D1 ROI material texture records are:

```text
+0x00 u32 TextureIndex
+0x04 u32 Texture TagHash
```

### Xbox proof

Across 11 resident material/DXBC overlaps:

```text
material TextureIndex set == DXBC declared t# set
11/11 exact
0 mismatches
```

Therefore Xbox `TextureIndex` is the actual shader `t#` register.

### PS4 proof

The target PS4 materials independently validate the same semantic against native
GCN resource binding.

Main surface `809C475F`, shader `80AAE14B`:

```text
TextureIndex 0 -> 80AACCDD
TextureIndex 1 -> 80AACCDF
TextureIndex 2 -> 80AACC26
TextureIndex 3 -> 80AACC28
TextureIndex 4 -> 80AACCDD
```

The `OrbShdr` usage mask exposes exactly five resource-table chunks, and the GCN
code loads chunks 0..4 one-for-one. Instruction dataflow proves their roles:

```text
t0 -> 80AACCDD RGB surface term
t1 -> 80AACCDF primary RG normal term
t2 -> 80AACC26 detail RG normal term
t3 -> 80AACC28 six-face environment cubemap
t4 -> 80AACCDD alpha surface/reflection-control term
```

Circuitry `816CE240`, shader `816CE0A8`:

```text
TextureIndex 0 -> 816CE1C5
TextureIndex 1 -> 816CE1C5
```

`OrbShdr` exposes direct immediate T0/T1 resources. GCN proves T0 is the
pre-displacement height sample and T1 is the displaced full image sample.

Thus D1 `STextureTag.TextureIndex` is `CONFIRMED_CROSS_PLATFORM_SEMANTIC` as the
shader texture/resource index.

## PS4 native sampler class `0x80801A42` — exact layout

Target sampler hashes resolve to structured class `80801A42`, each exactly 24
bytes:

```text
+0x00 u64 file_size = 24
+0x08 u32 SQ_IMG_SAMP_WORD0
+0x0C u32 SQ_IMG_SAMP_WORD1
+0x10 u32 SQ_IMG_SAMP_WORD2
+0x14 u32 SQ_IMG_SAMP_WORD3
```

The final 16 bytes are a native PS4 Gnm sampler S# descriptor.

Reusable decoder:

- `tools/d1_ps4_sampler_probe.py`

Raw words are canonical; Sony/Gnm enum names are source-correlated convenience
labels.

Target descriptors:

```text
80AAE177  main 2D sampler
  00000000 00F00000 0A503F80 00000000
  wrap XYZ   = Wrap
  min/mag    = Bilinear
  mip filter = Linear

80AAE176  main cubemap sampler
  00000092 00F00000 0A503F80 00000000
  wrap XYZ   = ClampLastTexel
  min/mag    = Bilinear
  mip filter = Linear

816CE0AA  circuitry sampler
  000001B6 00F00000 0A503F80 80000000
  wrap XYZ   = ClampBorder
  border     = OpaqueWhite
  min/mag    = Bilinear
  mip filter = Linear
```

The target raw LOD fields are common:

```text
min_lod_raw          = 0
max_lod_raw          = 3840
lod_bias_signed14    = -128
secondary_lod_bias   = 0
```

Their fixed-point conversion is intentionally not named until directly proven.

A small census over the resident target/shared namespaces found 18
`80801A42` sampler tags and 18 unique descriptors, demonstrating this is a real
state-resource class rather than a three-value target special case.

## Material TFX bytecode

The target PS TFX streams are preserved exactly:

```text
809C475F:
49 00 47 21 49 01 47 22 49 02 47 23 49 03 47 24 49 04 47 25

816CE240:
49 00 47 21 49 01 47 22
```

Current D1 TFX source names `0x47 = PopTemp` but leaves `0x49` unknown. The
repetition count matches texture count, and later Tiger strategies place shader
resource-binding operations in this opcode family, but this is insufficient to
rename D1 `0x49`. Its exact D1 meaning remains `UNKNOWN`.

## Xbox inline DXBC pixel shaders

Class `0x80801B7C` is a D1 Xbox pixel-shader inline-DXBC container.

Observed binary invariants over 27/27 resident instances:

- `0x30`-byte D1 header;
- `u64 +0x00` equals actual tag size;
- `u64 +0x08` equals DXBC size;
- complete DXBC begins at `+0x30`;
- chunk sequence `ISGN`, `OSGN`, `SHEX`;
- SHEX version token = pixel shader model 5.0 (`0x00000050`).

`0x80801AB4` is a source-indicated sibling Xbox inline-DXBC shader class,
expected to cover vertex shaders; direct validation awaits a resident fixture.

## Xbox vector container `0x80801AA5` — exact layout

There are 595 entries in the established Xbox package and 276 resident in patch
1. All 276/276 satisfy:

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

## Pixel material constant buffer `b0` — solved cross-platform

For every comparable Xbox material/pixel shader:

```text
material vector count == DXBC cbuffer b0 vec4 count
11/11 exact
```

Xbox storage modes:

1. external `PSVector4Container +0x32C -> 0x80801AA5`;
2. inline vec4 array at `+0x300` if no external container is used.

PS4 stores equivalent material constants through subtype `32:7`.

## PS4 subtype `32:7` material constants — exact representation

```text
32:7 GPU-resource header (16 bytes)
  +0x00 u32 unknown
  +0x04 u32 unknown
  +0x08 u32 unit_count
  +0x0C u32 marker/unknown

FileEntry.Reference
  -> raw payload
       byte_size = unit_count * 16
       Vec4[unit_count]
```

Corpus evidence:

- 122/122 observed headers exactly 16 bytes;
- 122/122 linked metadata sizes = `unit_count*16`;
- target payloads decode as ordinary IEEE-754 float4 arrays with exact raw-u32
  preservation.

Target fixtures:

```text
809C475F / PS 80AAE14B -> 80AAE14C -> 19 vec4s
816CE240 / PS 816CE0A8 -> 816CE185 -> 8 vec4s
```

The PS4 `OrbShdr` metadata independently declares constant-buffer API slot 0,
and GCN load offsets land exactly on the recovered local vectors. This is direct
instruction-level confirmation that the subtype-7 payload feeds material `b0`.

Reusable decoder:

- `tools/d1_vector_container_probe.py`

## PS4 native pixel shaders and `OrbShdr` metadata

### D1 engine shader header

Observed PS4 pixel shaders are FileEntry `type=32, subtype=8`:

- packed low 24 bits = referenced native shader payload size;
- packed high 8 bits = `InputUsageSlot` count;
- FileEntry.Reference = native Orbis GCN shader payload.

### Native Orbis binary framing

The referenced payload uses standard Sony `OrbShdr` metadata. The 28-byte
`ShaderBinaryInfo` footer is recovered by the standard first-token formula and
matches the sole footer signature in each target payload.

Reusable decoder:

- `tools/d1_ps4_shader_binary_probe.py`

It validates D1 header size, native payload size, footer accounting, exact code
length, usage slots, and usage masks before any instruction analysis.

### `80AAE14B` main surface binding layout

```text
shader               80AAE14B
native payload        80AAE14D
native payload size   1028 bytes
GCN code length       956 bytes
InputUsageSlots       9
```

Input usage:

```text
PtrExtendedUserData             API 1   user SGPR 2
ImmSampler                      API 1   user SGPR 4
ImmSampler                      API 2   user SGPR 8
PtrResourceTable                API 0   user SGPR 12   usage mask 0x1F
ImmSampler                      API 3   user SGPR 16
ImmSampler                      API 4   user SGPR 20
ImmSampler                      API 5   user SGPR 24
ImmConstBuffer                  API 0   user SGPR 28
ImmConstBuffer                  API 12  user SGPR 32
```

Five active resource-table chunks exactly match material texture indices 0..4.

### `816CE0A8` circuitry binding layout

```text
shader               816CE0A8
native payload        816CE0AE
native payload size   580 bytes
GCN code length       516 bytes
InputUsageSlots       8
```

Input usage:

```text
PtrExtendedUserData             API 1   user SGPR 2
ImmResource                     API 0   user SGPR 4
ImmSampler                      API 1   user SGPR 12
ImmResource                     API 1   user SGPR 16
ImmSampler                      API 2   user SGPR 24
ImmConstBuffer                  API 0   user SGPR 28
ImmConstBuffer                  API 12  user SGPR 32
ImmConstBuffer                  API 13  user SGPR 36
```

## Target instruction-level dataflow — solved locally

The exact equations are documented in `notes/PS4_09A_SHADER_DATAFLOW.md`.
Important recovered facts follow.

### Main surface `80AAE14B`

Let `u=attr3.x`, `v=attr3.y`.

Normal path:

```text
t1 = sample(80AACCDF, u,v)
t2 = sample(80AACC26, 20*(1-v), 0.4*u)

n1_xy = 2*t1.xy - 1
n2_xy = 2*t2.xy - 1
n_xy  = 1.25*n1_xy + n2_xy
n_z   = sqrt(max(0,1-dot(n_xy,n_xy)))
```

Surface/reflection source:

```text
B = sample(80AACCDD,t0).rgb
S = sample(80AACCDD,t4).a
```

`S` is not transparency. It drives reflection blur, reflection strength, and
native deferred-normal packing.

Cubemap minimum LOD:

```text
q = saturate(2.3*S - 1.3)
material_lod = 3 + 3*q
lod = max(hardware_cube_lod, material_lod)
E = sample_lod(80AACC28,R,lod)
```

Reflection/local color:

```text
strength = 2.5*S*E.a
reflection_rgb = E.rgb * [2,0.84,0] * strength
mrt0.rgb = B + (0.75*B + 0.75) * reflection_rgb
mrt0.a = attr0.w
```

Deferred normal packing:

```text
normal_scale = 0.375 + 0.125*S
mrt1.xyz = saturate(0.5 + normal_scale*N)
mrt1.w = 0.4754902422 if attr3.y > 1 else 0.4715686738
```

The shader writes two MRTs, so core glTF cannot reproduce the native deferred
contract exactly.

### Circuitry `816CE0A8`

T0 provides the centered height sample used for view-dependent UV offset.
T1 resamples the same BC1 image at displaced coordinates.

```text
L = saturate(0.30*R + 0.59*G + 0.11*B)
palette.rgb = vec4.rgb + vec5.rgb*L
```

Default material `816CE185`:

```text
vec4.rgb = [0.0151604200,0.0208455771,0.0379010513]
vec5.rgb = [0.3848395940,0.5291544200,0.9620989560]
bright endpoint ~= [0.4,0.55,1.0]
vec6 = [1,1,1,1]
vec7.x = 5
```

`vec7.x` is a proven material-local RGB intensity factor before two unresolved
global scalar multipliers. One variant (`816CE188`) uses 40.

The shader writes only MRT0 RGB with output alpha zero, strongly indicating a
separate HDR/emissive/additive-style composition pass. Exact render blend state
is still unresolved.

## Exact target texture recovery

The shared `0156` family has six retail patch members `_0.._5`; the target
texture headers/stream records may live there while high-resolution backing is
in `0157`.

`tools/d1_texture_export.py` now supports repeatable dependency packages and
cross-package TagHash resolution, plus per-face PS4 cubemap deswizzling.

Recovered target images:

```text
80AACCDD  2048x2048 BC3   backing 80AAE66A in 0157
80AACCDF  1024x1024 BC5   backing 80AAE66B in 0157
80AACC26    256x256 BC5   backing 80AAE586 in 0157
80AACC28      64x64 RGBA8 six-face cube
816CE1C5    256x512 BC1   backing 816CE246 in 0767
```

Proof artifact: Actions run `33869489031`, artifact
`09A-shared-samplers-retail-textures`, ID `9935326724`, ZIP SHA-256
`934d52dab19d47e36b83f43e0763957e94c0de7a4c834e88629ac330e4aa6632`.

## Portable glTF consequence

A loss-preserving exporter must distinguish **native truth** from **portable
approximation**.

Main surface:

- base-color source: `80AACCDD.rgb`;
- opaque surface: never map `80AACCDD.a` to transparency;
- combined normal requires the exact two-sample equation or a bake;
- `80AACCDD.a` can seed a glTF roughness/specular approximation, but its proven
  native role is broader surface/reflection control;
- native `80AACC28` environment cubemap and explicit LOD equation must be kept
  in `extras` even if core glTF cannot bind them.

Circuitry:

- bake palette RGB from `816CE1C5` and local vec4/vec5;
- preserve the view-dependent parallax equation in `extras`;
- glTF emissive + `KHR_materials_emissive_strength` is the portable
  approximation; keep local 5/40 intensity distinct from unresolved global
  scalars.

## Remaining work

1. Trace producers/semantics of global `b12`/`b13` fields used by view/parallax
   and global circuitry intensity.
2. Decode the render/blend state that composes the circuitry pass.
3. Name the `attr0..attr4` shader interface exactly from vertex-stage evidence.
4. Promote the already successful target skeleton/animation decode/export into
   a reusable committed exporter.
5. Produce the proof-grade textured + rigged + animated GLB with original
   parent/material/shader/texture/sampler/constant metadata serialized in
   `extras` and all glTF approximations explicitly labeled.
