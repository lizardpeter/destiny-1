# D1 Tower `80CA0DDA -> 809DCD66` native shader proof

Date: 2026-09-06  
Target: final-era Destiny 1 / Rise of Iron, PS4 retail Tower  
Status: **retail-validated native vertex/material/pixel dataflow closed for the recovered family; engine producer names for two `api13` global scalars and native render/blend state remain unresolved**

This note is a durable proof boundary for the 24 visible Tower materials using
vertex shader `80CA0DDA` and pixel shader `809DCD66`.  The family is deliberately
kept separate from portable glTF/PBR preview semantics because neither native
texture is a direct RGB base-color texture and the second sample is view-dependent.

## Evidence policy

Only retail bytes, exact native GCN dataflow, pinned D1 reader behavior, or an
independent cross-source agreement promote a semantic role here.  Appearance,
texture format, adjacency and material order are not semantic evidence.

## Family identity

The ten-cell visible material corpus contains exactly 24 materials with:

```text
VS 80CA0DDA
PS 809DCD66
PS t0 8093E9A3
PS t1 8093E9A2
```

The two textures are exact PS4 resources:

```text
8093E9A3  256x64    BC1 sRGB   t0
8093E9A2  1024x256  BC1 sRGB   t1
```

The material sampler bindings are:

```text
t0 -> 80AAE177  wrap XYZ, bilinear min/mag, linear mip
t1 -> 80AAE176  clamp-last-texel XYZ, bilinear min/mag, linear mip
```

The shader consumes only the sampled red scalar from each texture.

## Exact ROI material PS layout for this family

Retail probing and the ROI material schema agree on the following PS region:

```text
+0x2D0  PS TFX bytecode DynamicArray<u8>
+0x2E0  PS TFX private constants DynamicArray<Vec4>
+0x2F0  PS samplers
+0x300  PS CBuffers DynamicArray<Vec4>
+0x32C  optional external PS Vector4 container
```

All 24 materials contain exactly seven PS CBuffer vectors at `+0x300`.

Ten materials also reference an external PS4 subtype `32:7` vector resource.
For all ten, the seven external vectors are byte-for-byte identical to the seven
inline `+0x300` vectors.  The external resource is therefore a mirror of the same
material b0 payload in this family, not an alternate value set.

The `+0x2E0` TFX-private constant count changes with the program and exactly
covers its highest referenced constant index.  It is separate from the seven
shader-output CBuffer vectors.

Green constant-layout canary:

```text
Actions run 34045866733
commit      9d975a4768a9068e589fe2f94d0ba2f3a31abf52
```

Reusable parser:

```text
tools/d1_material_ps_constant_resolve.py
```

## Material b0 slots consumed by `809DCD66`

The PS4 `OrbShdr` user-data table and GCN SMEM loads close material API slot 0
as the shader b0 source.  `809DCD66` reads:

```text
c2      palette base RGB
c3      palette slope/delta RGB
c4.x    parallax displacement magnitude
c5.rgb  RGB multiplier
c6.x    static or TFX-produced material-local intensity
```

All 24 observed materials use:

```text
c4.x = 0.025
c5    = [1,1,1,1]
```

The family-specific RGB palette is therefore generated from `c2/c3`; no source
texture is directly promoted to base color.

## TFX -> c6 closure

The 24 materials contain six exact PS TFX program families:

```text
8 bytes   x 10  static resource-setup-only family
20 bytes  x  2
25 bytes  x  2
39 bytes  x  2
40 bytes  x  1
41 bytes  x  7
```

The 10 static materials have no PS TFX private constants and serialize a nonzero
`c6.x` of 7 or 10.

The 14 dynamic materials serialize `c6 = [0,0,0,0]`, carry private constants at
`+0x2E0`, execute one of the five arithmetic families, and all terminate in
`42 06`.  Combined with the native PS consuming `c6.x`, this is strong scoped
retail evidence that opcode `0x42` stores the expression result to PS CBuffer
slot 6 for this D1 family.  An engine-wide opcode name remains withheld.

The arithmetic suffixes are replayable using already-closed TFX operations such
as constant loads, `Frame[0]`, multiply/multiply-add, cosine rotations, triangle,
jitter, saturate and constant lerp.  `Frame[0]` remains an abstract native frame
extern until its exact D1 time unit/producer is closed.

Reusable evaluator:

```text
tools/d1_tower_809dcd66_tfx_eval.py
```

Green six-family replay canary:

```text
Actions run 34046335791
```

## Exact PS user-data sources

The native pixel shader exposes:

```text
PtrExtendedUserData  api1
ImmResource          api0   -> t0
ImmSampler           api1
ImmResource          api1   -> t1
ImmSampler           api2
ImmConstBuffer       api0   -> material b0
ImmConstBuffer       api12
ImmConstBuffer       api13
```

The extended user-data descriptor loads map:

```text
extended +0x0C -> material api0/b0
extended +0x10 -> api12
extended +0x14 -> api13
```

SMEM immediate offsets are dword indices in this native interface.

### api12

`api12` dwords 28..30 are directly proven as camera/view position.  The shader
subtracts interpolated `attr4.xyz` from those three values and normalizes the
result before projecting it into the tangent basis for parallax.

### api13

The shader loads `api13` dwords 6 and 7.  Both survive into final RGB as separate
multiplicative global scalar factors.

Their exact arithmetic role is closed, but their engine producer/name and live
runtime values have not yet been recovered.  They remain named only by source:

```text
api13[6]
api13[7]
```

An exporter/Blender adapter must preserve them separately and must not silently
claim a guessed engine semantic.  A preview may use explicit user-provided or
clearly labeled fallback values.

## Exact `809DCD66` pixel equation

Let the interpolated VS outputs be:

```text
N  = attr0.xyz
T  = attr1.xyz
B  = attr2.xyz
uv = attr3.xy
P  = attr4.xyz
```

Let:

```text
V = normalize(camera_position - P)
```

The shader projects the view direction into the interpolated tangent basis:

```text
Tx = dot(V,T)
Ty = dot(V,B)
Tz = dot(V,N)
```

The second texture coordinate is:

```text
uv2.x = uv.x - c4.x * Tx / Tz
uv2.y = uv.y - c4.x * Ty / Tz
```

Samples:

```text
r0 = sample(t0, uv).r
r1 = sample(t1, uv2).r
```

Palette and RGB:

```text
palette = c2.rgb + c3.rgb * saturate(r0)

rgb = palette
    * r1
    * c5.rgb
    * c6.x
    * api13[6]
    * api13[7]
```

The native shader writes its color path with zero output alpha.  The exact blend
or composition state is still unresolved, so this fact alone is not sufficient
to rename the pass as additive/emissive.

Reusable semantic replay:

```text
tools/d1_tower_809dcd66_ps_replay.py
```

This replay deliberately does not claim bit-for-bit GCN `v_rsq_f32`, texture
filter/mip selection, color-pipeline or raster interpolation emulation.

## Exact vertex shader `80CA0DDA`

A current-retail differential against already-closed static-world VS `80CA0CB7`
was extracted from package family `0250` and disassembled with pinned CLRX/GFX700.

Green differential canary:

```text
Actions run 34046926081
artifact    d1-tower-809dcd66-vs-differential
```

Native input interface:

```text
semantic0 -> v4..v6    3 components
semantic1 -> v8..v9    2 components
semantic2 -> v12..v14  3 components
semantic3 -> v16..v19  4 components
```

The target retains the same static instance affine, UV affine, transformed
normal/tangent basis and world-position construction as `80CA0CB7`, but removes
the packed control inputs used by that sibling.

Its pixel-facing exports are:

```text
param0 = (normal.xyz,    1)
param1 = tangent export
param2 = (bitangent.xyz, 1)
param3 = (uv.xy,          0, 1)
param4 = (world_pos.xyz,  1)
```

This closes the `attr0..attr4` meanings consumed by `809DCD66` from vertex-stage
evidence rather than from pixel-shader appearance.

## Exact target static source layout: 8 + 20

A critical retail correction is that this family does **not** use the control-
bearing 8+24 source stream used by `80CA0CB7`.

The Tower cell and exact package backings prove:

```text
primary stride 0x08
  +0x00 int16x3 SNORM position xyz
  +0x06 int16 stored source word not fetched by 80CA0DDA

secondary stride 0x14
  +0x00 int16x2 SNORM UV xy
  +0x04 int16x4 SNORM normal storage; shader fetches xyz
  +0x0C int16x4 SNORM tangent xyzw
```

This independently agrees with the pinned D1 `ReadD1VertexData` stride-20 branch.

Reusable exact source/VS replay:

```text
tools/d1_tower_80ca0dda_vs_replay.py
```

## Retail cell replay closure

The exact Tower cell `80C98254` contains five of the 24 family materials and a
useful cross-package geometry population:

```text
materials   5
geometries  12 distinct variants
placements  64
source      009F + 024C + 0250 current retail package families
layout      12/12 = 8+20
```

The green replay validates, without relaxed assertions:

- all exact material VS/PS identities;
- exact source buffer header strides;
- dedicated `80CA0DDA` decode == generic pinned D1 stride-20 decode;
- exact index ranges and source vertex identities;
- exact placement counts;
- shader-facing instance record reconstruction;
- finite param0..param4 outputs;
- hardcoded removed control lanes;
- world positions against an independent affine expression;
- UVs against an independent sidecar UV-affine expression;
- scoped PS parallax and RGB arithmetic.

Final green run:

```text
Actions run 34047824135
commit      20e13e70b710bba0cf9523176d907be1976794e6
artifact    9993656491 d1-tower-809dcd66-retail-replay
artifact sha256 6bdf4ac23b1cdd142654d6aa337877360a081014867216702d7ddfe3b63eedde
```

## Blender / portable consequence

This family must not be flattened by binding either t0 or t1 directly to glTF
base color.  A faithful Blender material requires the two-sample view-dependent
parallax equation and palette reconstruction above.

Blender 4.5 Geometry node outputs are world-space, and its `Incoming` vector
points toward the viewing point.  That makes native `V` directly representable
at shader-node semantic level.  Tangent-basis handedness still requires explicit
care because D1 consumes tangent W when constructing the bitangent.

Until the tangent-W path and `api13[6:7]` runtime source values are carried into
the Blender graph, any rendered adapter must be labeled a native-equation preview,
not a bit-exact retail renderer.

## Remaining proof boundary

1. Preserve/prove tangent-W handedness through the Blender/glTF import path.
2. Trace the engine producers/names and live runtime values of `api13[6]` and
   `api13[7]`.
3. Recover the native render/blend/composition state for this RGB/alpha-zero pass.
4. Close the exact D1 unit/producer of TFX `Frame[0]` for dynamic animation timing.
5. Build the Blender adapter from the closed equations while retaining all four
   unresolved items above as explicit metadata/inputs rather than guesses.
