# D1 PS4 `816CE09A` native shader dataflow

Date: 2026-09-04
Target model: `816CE09A`
Parent: `816CE12B`
Default visible materials:

```text
VariantShaderIndex 0 -> 809C475F -> PS 80AAE14B
VariantShaderIndex 1 -> 816CE240 -> PS 816CE0A8
```

This note records instruction-level findings from the exact retail PS4 native
GCN binaries. It intentionally separates proven machine-code behavior from
portable glTF approximations.

## Decoder provenance and byte boundaries

Destiny's PS4 pixel-shader header points to a native Orbis shader payload. The
payload's `OrbShdr` metadata gives an exact machine-code length and input-usage
table. `tools/d1_ps4_shader_binary_probe.py` verifies both the Destiny header
size and the Sony footer before extracting code.

The bounded code was disassembled using CLRX 0.1.9 in raw `GFX700` / GCN 1.1
mode. CLRX reports `.gpu Spectre`, decodes both streams to `s_endpgm`, and
produces no decoder errors.

Validated code spans:

```text
80AAE14B -> native 80AAE14D
  native payload 1028 bytes
  code length     956 bytes
  OrbShdr footer  1000

816CE0A8 -> native 816CE0AE
  native payload 580 bytes
  code length     516 bytes
  OrbShdr footer  552
```

The proof run was GitHub Actions run `33868029823`; artifact
`09A-ps4-gcn-clrx-disassembly`, ID `9934793728`, ZIP SHA-256
`268655f8c3bf0c4e4bf037ad7ba552e3d56bb56638b441471c322f6f2679412a`.

## Exact serialized texture/register map

The material `STextureTag` records are eight bytes:

```text
+0x00 u32 TextureIndex
+0x04 u32 Texture TagHash
```

The recovered target material proves the same semantic as Xbox: `TextureIndex`
is the shader texture/resource index.

### Main surface `809C475F`

```text
t0 / index 0 -> 80AACCDD  2048x2048 BC3
t1 / index 1 -> 80AACCDF  1024x1024 BC5
t2 / index 2 -> 80AACC26    256x256 BC5
t3 / index 3 -> 80AACC28      64x64 RGBA8 cube, six faces
t4 / index 4 -> 80AACCDD  2048x2048 BC3 (same image as t0)
```

The `80AAE14B` resource table loads exactly those five indices at table chunks
0..4. Therefore the texture-role mapping below is `CONFIRMED_BINARY`, not based
on image format or visual appearance.

### Circuitry `816CE240`

```text
t0 / index 0 -> 816CE1C5  256x512 BC1
t1 / index 1 -> 816CE1C5  256x512 BC1
```

`816CE0A8` binds these as immediate T0/T1 descriptors. The duplicate image is
intentional: T0 is sampled before UV displacement and T1 after displacement.

## Exact PS4 sampler resources

D1 sampler class `80801A42` is now decoded as:

```text
+0x00 u64 file_size = 24
+0x08 16-byte native Gnm S# descriptor
```

Reusable decoder: `tools/d1_ps4_sampler_probe.py`.

All target samplers use bilinear min/mag filtering and linear mip filtering.
The raw LOD fields are retained because their fixed-point scaling is not named
without a direct source proof.

Main 2D sampler `80AAE177`:

```text
S# words = 00000000 00F00000 0A503F80 00000000
wrap XYZ = Wrap
```

Main cubemap sampler `80AAE176`:

```text
S# words = 00000092 00F00000 0A503F80 00000000
wrap XYZ = ClampLastTexel
```

Circuitry sampler `816CE0AA`:

```text
S# words = 000001B6 00F00000 0A503F80 80000000
wrap XYZ = ClampBorder
border   = OpaqueWhite
```

The wrap/filter/border names come from the public Sony Gnm enum/register layout;
the raw four dwords remain the canonical lossless representation.

## Variant 0 / `80AAE14B`: exact main-surface material math

Material `809C475F` supplies 19 local vec4s through `80AAE14C`:

```text
c0  = [ 2.5,  -1.25, -1.25, -1.25 ]
c1  = [ 0,    -1,     1,     1    ]
c2  = [ 1,     0,     0,     0    ]
c3  = [20,     0.4,   0,     0    ]
c4  = [ 2,    -1,    -1,    -1    ]
c5  = [ 0,     0,     0,     0    ]
c6  = [ 0,     0,     0,     0    ]
c7  = [ 0,     0,     0,     0    ]
c8  = [ 3,     1,     1,     1    ]
c9  = [ 0,     1,     1,     1    ]
c10 = [-1.3,   2.3,   1,     1    ]
c11 = [ 0,     2.5,   0,     0    ]
c12 = [ 1,     0.42,  0,     1    ]
c13 = [ 2,     0,     0,     0    ]
c14 = [ 0.75,  0.75,  1.5,   1.5  ]
c15 = [ 0,     0,     0,     0    ]
c16 = [ 0,     0,     0,     0    ]
c17 = [ 0,     0.4715686738, 120, 121 ]
c18 = [ 0,     0.4754902422, 121, 122 ]
```

The GCN `s_buffer_load` offsets are dword indices and land exactly on these
values. The shader only reads the components documented below; unreferenced
components are not assigned semantics.

### UVs and the two normal samples

Let the interpolated material UV pair be:

```text
u = attr3.x
v = attr3.y
```

`t1` samples directly at `(u,v)`.

The local constants `c1..c3` produce the second coordinates exactly as:

```text
uv_detail.x = 20 * (1 - v)
uv_detail.y = 0.4 * u
```

`t2` samples at `uv_detail`.

The sampled RG pairs are decoded and combined as:

```text
n1_xy = 2 * t1.xy - 1
n2_xy = 2 * t2.xy - 1
n_xy  = 1.25 * n1_xy + n2_xy
n_z   = sqrt(max(0, 1 - dot(n_xy,n_xy)))
```

This follows directly from:

```text
2.5*t1 + 2*t2 - 2.25
```

in each XY component. The result is transformed through the interpolated
attribute basis (`attr0..attr2`) and normalized before reflection and MRT
packing. Naming those basis attributes as tangent/bitangent/normal is the
portable interpretation; the arithmetic itself is proven.

### `t0` RGB and `t4` alpha are two views of the same BC3 image

The shader samples:

```text
B = sample(t0, uv).rgb
S = sample(t4, uv).a
```

Because `t0` and `t4` both serialize `80AACCDD`, this is one BC3 texture used
through separate resource entries for RGB and alpha paths.

`S` is **not transparency**. Native output alpha is sourced from `attr0.w`.

### `S` controls reflection blur / LOD

The local material maps BC3 alpha into an explicit cubemap LOD control:

```text
q = saturate(2.3 * S - 1.3)
material_lod = 3 + 3 * q
lod = max(hardware_cube_lod, material_lod)
E = sample_lod(t3, reflection_vector, lod)
```

Thus the material requests a minimum cubemap LOD between 3 and 6 as `S`
increases. `S` is therefore instruction-proven to contain a
reflection-blur/roughness-like control. The original Bungie field name remains
unknown.

### Reflection vector

The shader reconstructs and normalizes the perturbed surface normal, builds a
normalized view vector from higher-level/global `b12` data and `attr4`, and
executes the standard reflection form:

```text
R = 2 * dot(V,N) * N - V
```

The GCN then converts `R` with `v_cubema/v_cubetc/v_cubesc/v_cubeid`, obtains
hardware cubemap LOD, applies the material minimum above, and samples `t3`.

This proves `80AACC28` is the environment/reflection cubemap.

### `S` also controls reflection amount

After the cubemap sample:

```text
reflection_strength = 2.5 * S * E.a
reflection_rgb = E.rgb * [2.0, 0.84, 0.0] * reflection_strength
```

The local `[2, 0.84, 0]` term comes from `c13.x * c12.rgb`.

The RGB result written to MRT0 is exactly:

```text
mrt0.rgb = B + (0.75 * B + 0.75) * reflection_rgb
mrt0.a   = attr0.w
```

All multiplies above are component-wise. For this material the cubemap is
therefore tint-weighted toward R/G and contributes no B term through the local
`c12.b = 0` multiplier.

### `S` is packed into the deferred normal magnitude too

The perturbed transformed normal is normalized again to `N`. The shader writes
MRT1 XYZ as:

```text
normal_scale = 0.375 + 0.125 * S
mrt1.xyz = saturate(0.5 + normal_scale * N)
```

So BC3 alpha affects three independent native paths:

1. cubemap minimum blur LOD;
2. reflection strength;
3. deferred normal-vector packing magnitude.

This is stronger than simply calling it a roughness texture. The safe recovered
name is **surface/reflection-control scalar `S`**; a glTF roughness/specular map
is an approximation.

MRT1 W is selected from two local constants using `attr3.y`:

```text
mrt1.w = 0.4754902422  if attr3.y > 1
         0.4715686738  otherwise
```

Only `c17.y/c18.y` are loaded by this shader. Their nearby `120/121/122`
constants are preserved but not semantically named.

### Native output contract

`80AAE14B` writes:

```text
mrt0 = surface/reflection RGB + attr0.w
mrt1 = packed perturbed normal/material data
```

It is therefore a deferred material pass, not a forward glTF-style PBR shader.

## Variant 1 / `816CE0A8`: circuitry palette + parallax path

Material `816CE240` binds grayscale BC1 texture `816CE1C5` twice through the
same ClampBorder/OpaqueWhite sampler.

The exact local 8-vector block `816CE185` is:

```text
c0 = [0,0,0,0]
c1 = [0,0,0,0]
c2 = [0.4,0,0,0]
c3 = [0.30,0.59,0.11,0]
c4 = [0.0151604200,0.0208455771,0.0379010513,1]
c5 = [0.3848395940,0.5291544200,0.9620989560,0]
c6 = [1,1,1,1]
c7 = [5,0,0,0]
```

### T0 is the pre-displacement height sample

The shader samples T0 at base UV and retains one scalar `H`. It computes:

```text
Hc = H - 0.5
```

A higher-level/global constant scales `Hc`; a normalized view vector is
projected through the interpolated basis and used to offset the base UV before
the second sample. The exact register arithmetic proves view-dependent
parallax/offset mapping. The global scale producer is still unresolved, so no
Bungie field name is assigned.

### T1 is the displaced full image sample

T1 resamples the same `816CE1C5` image at the displaced UV and produces the
palette coordinate:

```text
L = saturate(0.30*R + 0.59*G + 0.11*B)
```

Alpha has coefficient zero.

### Exact palette equation

The material-local palette is:

```text
palette.rgb = c4.rgb + c5.rgb * L
```

For default `816CE185`:

```text
L=0 -> [0.01516042, 0.02084558, 0.03790105]
L=1 -> [0.40000001, 0.55000000, 1.00000001]
```

All six external-material alternatives use the same image/shader and change
these authored palette constants (and, for one variant, intensity).

### Material-local HDR intensity

The shader multiplies RGB by:

```text
c6.rgb * c7.x
```

before two higher-level/global scalar factors. Since default `c6.rgb=[1,1,1]`
and `c7.x=5`, the default local intensity is 5. Variant `816CE188` uses 40.

The two global multipliers remain unresolved, so a portable exporter may record
5/40 as the proven material-local emissive strength but must not claim it is the
complete on-screen multiplier.

### Output

The circuitry shader writes only MRT0 RGB and explicitly writes output alpha 0.
Together with the 5x/40x local intensity and separate visible material range,
this is strong evidence for an emissive/additive-style pass. The exact render
blend state is still a separate proof target.

## Material TFX byte streams

The exact target streams are:

```text
809C475F: 49 00 47 21  49 01 47 22  49 02 47 23  49 03 47 24  49 04 47 25
816CE240: 49 00 47 21  49 01 47 22
```

Current D1 TFX source names `0x47 = PopTemp` and leaves `0x49` unnamed. Later
Tiger strategies place explicit shader-resource binding opcodes in this opcode
family, and the repetition count here exactly matches texture count, but that is
not enough to rename D1 `0x49`. The raw bytecode is preserved and its exact D1
semantic remains `UNKNOWN`.

## Exact retail texture recovery

The final images are now reproducibly exported through cross-package backing
resolution (`0156 -> 0157`, plus local `0767`) using
`tools/d1_texture_export.py`:

```text
80AACCDD  2048x2048 BC3   backing 80AAE66A
80AACCDF  1024x1024 BC5   backing 80AAE66B
80AACC26    256x256 BC5   backing 80AAE586
80AACC28      64x64 RGBA8 six-face cube
816CE1C5    256x512 BC1   backing 816CE246
```

The exporter now resolves dependency packages by TagHash and deswizzles each
cubemap face independently.

Proof run `33869489031` produced artifact
`09A-shared-samplers-retail-textures`, ID `9935326724`, ZIP SHA-256
`934d52dab19d47e36b83f43e0763957e94c0de7a4c834e88629ac330e4aa6632`.

## Portable reconstruction consequences

### Main surface

Core glTF cannot exactly represent this native pass because it combines two
normal textures, samples a per-material cubemap with explicit LOD, and writes a
deferred MRT pair.

The portable path should:

1. use `80AACCDD.rgb` as the source surface/base color;
2. keep the surface opaque; never use `80AACCDD.a` as glTF alpha;
3. bake or reproduce the two-normal equation when a single glTF normal map is
   required;
4. treat `80AACCDD.a` as a recovered surface/reflection-control source and only
   derive roughness/specular values with an explicit approximation label;
5. preserve `80AACC28` and the exact native reflection equation in `extras`,
   because core glTF has no per-material cubemap binding;
6. preserve both native MRT equations in metadata.

### Circuitry pass

A portable approximation can be substantially faithful:

1. bake `c4.rgb + c5.rgb*L` from `816CE1C5` for the selected palette;
2. record the view-dependent parallax equation and duplicate T0/T1 bindings in
   `extras` (core glTF has no standard parallax mapping);
3. use glTF emissive texture/color plus `KHR_materials_emissive_strength` as an
   approximation, with `c7.x` stored separately as the proven local 5x/40x
   multiplier and the unresolved global scalars called out;
4. preserve sampler ClampBorder/OpaqueWhite behavior in metadata even where a
   target glTF runtime cannot express it exactly.

## Remaining proof frontier

1. Trace the producers/semantics of higher-level `b12` and `b13` values used for
   camera/view/parallax/global intensity data.
2. Decode the relevant render/blend state to prove the circuitry composition
   mode rather than only its shader-side output contract.
3. Map the `attr0..attr4` vertex/pixel interface names exactly, although the
   arithmetic using them is already decoded.
4. Promote the previously successful skin + animation export logic into a
   reusable committed tool for `816CE09D/E` rather than relying on the old
   one-off GLB.
5. Build the proof-grade textured + rigged + animated GLB with native hashes,
   exact constants/samplers, and every portable approximation serialized in
   `extras`.
