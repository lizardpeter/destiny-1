# D1 Tower material 80C9993C — native colour + normal proof

Status: **retail-canary closed for the scoped visible draws**  
Platform: Destiny 1 Rise of Iron, PS4  
Material: `80C9993C`  
Vertex shader: `80CA0CB7`  
Pixel shader: `80C9994A`  
Retail table: `80C99827`  
Visible info records: `976`, `978`  
Canary run: `34043862528`  
Canary artifact: `d1-tower-80c9993c-native-rgb-normal-proof`

This note supersedes the older RGB-only proof as the preferred visual checkpoint.
The RGB-only shader arithmetic was correct, but its proof GLB still passed the
entire serialized 0x40 instance record to glTF as a 4x4 node matrix. The exact VS
replay and the reusable world-static parser independently prove that is wrong:
the final 16 bytes are shader/UV data, not a homogeneous matrix row.

## 1. Exact material bindings

`80C9993C` binds:

```text
VS = 80CA0CB7
PS = 80C9994A

t0 = 80C9988C  BC3 / sRGB
t1 = 80C9988D  BC5 / linear
t2 = 80C9988C  same BC3, second coordinate branch
t3 = 80C9988D  same BC5, second coordinate branch
t4 = 80C9988E  BC4 / linear scalar mask
```

All five PS sampler slots select D1 sampler resource `80AAE177`:

```text
GNM words = 00000000 00F00000 0A503F80 00000000
address    = Wrap XYZ
mag        = Bilinear
min        = Bilinear
mip        = Linear
```

The proof adapter samples mip 0 because the established ROI texture exporter
exposes the full-resolution surface but does not close runtime screen derivatives
or a retail mip chain. That boundary remains explicit.

## 2. Source vertex streams for VS 80CA0CB7

The scoped Tower family is byte-exhausted as:

```text
stream 0, stride 0x08
  +0x00 int16x3  -> v4..v6    position xyz
  +0x06 int16    -> v20       scalar / attr0.w source

stream 1, stride 0x18, branch A
  +0x00 int16x4  -> v8..v11   UV.xy + material-control words
  +0x08 int16x3  -> v12..v14  source normal
  +0x0E int16                stored normal W, not fetched by the XYZ semantic
  +0x10 int16x4  -> v16..v19  source tangent xyz + handedness W
```

All packed signed values use the established D1 signed-16 normalization by
`32767`, clamped at `-1`.

For the two visible `80C9993C` draws:

```text
v10 = 0
v11 spans [0,1]
v20 = 1 exactly
source tangent.w = +/-1 branch-A domain
```

## 3. The 0x40 static instance record is 3x4 affine + shader tail

This is a critical correction.

The serialized 0x40 record is:

```text
+0x00..+0x2F  first three float4 rows = spatial 3x4 affine
+0x30         shader value s8  = per-instance UV scale
+0x34         shader value s9  = per-instance UV translation X
+0x38         shader value s10 = per-instance UV translation Y
+0x3C         shader value s11 = retained tail; not a homogeneous matrix element
```

The last four floats must **never** be handed to glTF as row 4 of a transform.
The two target retail tails make the error obvious:

```text
info 976 / transform 2377:
  [5.469311714, 1.299784660, 1.062750340, 1096572.0]

info 978 / transform 2425:
  [22.30946350, 13.95489120, 15.94134331, 1208840.0]
```

Those are shader data, not projective matrix coefficients.

The spatial rows are:

```text
info 976:
  [  0.0,       36.020576,  0.0,       0.0   ]
  [-36.020576,   0.0,        0.0,      17.75  ]
  [  0.0,        0.0,       36.020576,  1.875 ]

info 978:
  [  0.0,      31.96875, 0.0, ~0.0   ]
  [-31.96875,   0.0,     0.0, 87.625 ]
  [  0.0,       0.0,    31.9375, 4.00000095]
```

`tools/d1_world_static_common.py` independently encodes the same split in
`parse_static_instance_records()`.

## 4. VS 80CA0CB7 replay

The exact native disassembly closes the spatial and tangent-basis outputs.
At semantic float32 precision:

```text
P.x = row0.xyz dot sourcePosition + row0.w
P.y = row1.xyz dot sourcePosition + row1.w
P.z = row2.xyz dot sourcePosition + row2.w

Nraw = M3x3 * sourceNormal
invN = rsq(dot(Nraw,Nraw))

attr0.xyz = Nraw * invN
attr1.xyz = (M3x3 * sourceTangent.xyz) * invN
attr2.xyz = sourceTangent.w * cross(attr0.xyz, attr1.xyz)
attr0.w   = v20

attr3.xy = (s9,s10) + s8 * (v8,v9)
attr3.zw = (v10,v11)
```

A subtle but important native behavior is preserved: the transformed tangent uses
**the normal reciprocal length**, rather than being independently normalized.

Reusable implementation:

- `tools/d1_tower_80ca0cb7_vs_replay.py`
- `tests/test_d1_tower_80ca0cb7_vs_replay.py`

## 5. PS 80C9994A colour branch

Material constants produce:

```text
uv0  = 3.662899971 * attr3.xy + (0.25029999, 0)
uv2  = 4.5          * attr3.xy
uvm  = 4.5          * attr3.xy

weight = saturate(3 * attr3.w - 2 * t4.r)
```

The t0 branch is adjusted by the exact material tint and then selected against t2
with `weight`. BC3 RGB is sampled through the native sRGB resource interpretation,
so the CPU adapter linearizes source RGB before shader arithmetic and re-encodes
the finished glTF base-colour atlas to sRGB.

The resulting 1664x1664 colour atlas has 130,000 distinct occupied RGB values and
visually resolves as dense olive/green Tower grass instead of the earlier white
slab caused by an incorrect portable-material interpretation.

## 6. PS 80C9994A normal branch

The same branch coordinates and weight drive the BC5 normal pair:

```text
t1 = sample(80C9988D, uv0)
t3 = sample(80C9988D, uv2)

n1.xy = 2*t1.rg - 1
n3.xy = 2*t3.rg - 1

xy = lerp(n3.xy, n1.xy, weight)
z  = sqrt(saturate(1 - x*x - y*y))
```

The native PS then consumes the interpolated VS basis:

```text
world = y*attr2 + x*attr1 + z*attr0
world = normalize(world)
```

This establishes the full semantic bridge from serialized source normal/tangent
bytes through the native VS and PS to the final decoded world normal direction.

The target retail canary measured the final glTF-Y-up world-normal component
ranges as:

```text
X [-0.58037984, +0.58166087]
Y [+0.69170326, +1.00000000]
Z [-0.61724496, +0.72100651]
```

The pre-basis tangent-space reconstruction spans:

```text
X [-0.64189714, +0.63917613]
Y [-0.60949171, +0.60877037]
Z [+0.69260973, +1.00000000]
```

## 7. Portable glTF normal adapter

The triangle-private colour atlas necessarily replaces the original UV topology.
Allowing a renderer to derive tangents from those artificial atlas UVs would
therefore rotate the normal map incorrectly.

The portable proof avoids that problem explicitly:

1. duplicate vertices per retail triangle;
2. replay the native final normal direction per atlas pixel;
3. choose one explicit orthonormal reference TBN for that private triangle from
   the solved native basis;
4. re-express the already-solved world normal in that reference TBN;
5. encode the resulting vector as a normal-map texel;
6. export matching standard glTF `NORMAL` and `TANGENT` attributes.

All 648 target triangles resolve to `TANGENT.w = -1` in the explicit adapter
frame. The resulting glTF normal atlas contains **10,166 distinct occupied RGB
vectors**, confirming it is not a flat placeholder.

Trimesh writes arbitrary vertex attributes with a leading underscore. The adapter
therefore performs a deterministic GLB-JSON-only rename from `_TANGENT` to the
standard `TANGENT` semantic while preserving the same binary accessor. The retail
canary independently reparses the GLB and requires:

```text
POSITION
NORMAL
TANGENT
TEXCOORD_0
normalTexture
```

with no `_TANGENT` remaining.

## 8. D1 world basis -> glTF basis

D1 world is Z-up. The visual adapter applies the rigid conversion:

```text
D1 +X -> glTF +X
D1 +Y -> glTF -Z
D1 +Z -> glTF +Y
```

The 3x4 retail spatial affine is baked directly into vertex positions and then
rotated into glTF Y-up. The final GLB nodes have no projective or scale/rotation
matrix at all.

The final proof scene bounds are approximately:

```text
min = (-36.0206, 1.7343, -110.4686)
max = (+36.0206, 4.2495,   +1.4404)
extents ~= (72.0412, 2.5152, 111.9090)
```

## 9. Final validated proof

Retail canary `34043862528` passed:

```text
30 scoped synthetic/source-closed tests
fresh 024c + 0250 retail package recovery
exact material + all 3 texture exports
native colour bake
native normal-direction bake
corrected 3x4 spatial transform handling
D1 Z-up -> glTF Y-up conversion
standard glTF NORMAL + TANGENT + normalTexture validation
independent trimesh scene reload
```

Output summary:

```text
2 geometries
648 triangles
1,944 duplicated atlas vertices
GLB = 13,944,892 bytes
colour atlas = 7,548,475 bytes
glTF normal atlas = 6,291,182 bytes
native tangent-space debug atlas = 6,289,515 bytes
```

Canary SHA-256:

```text
GLB
bb18679c77312238c742c7c693a6435dcf2d5fe09f74b314536a5e65e58a0d20

colour atlas
e1ffc2594e34e6be80fa1934ddbd43af45d8aa2dacb9946e95be502697c72841

glTF normal atlas
2730fd1d26136ac5327e059dc5fe49f77645a1bf1f79b4c198451a07501b5204

native tangent-space debug atlas
b7df7a2db90c0b4aaa1134cdbc40c7996ee60677e977dd3a8e3ac36334a65d38
```

## 10. Remaining proof boundary

Still deliberately unresolved for a bit-identical native frame:

- exact screen-space derivatives used for texture LOD;
- exact runtime mip-chain selection/content in this adapter;
- bit-for-bit GCN `v_rsq_f32` approximation rather than semantic float32
  normalization;
- Destiny deferred MRT1 packing magnitude / auxiliary alpha, which is not needed
  to drive a standard glTF normal map but remains relevant for a native deferred
  framebuffer emulator.

These limitations do **not** reopen material identity, source vertex roles, the
3x4 instance transform split, colour branch arithmetic, BC5 branch arithmetic,
or final normal-direction semantics for the scoped two retail draws.
