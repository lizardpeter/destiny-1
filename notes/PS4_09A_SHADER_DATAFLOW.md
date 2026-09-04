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
GCN binaries.  It intentionally separates proven machine-code behavior from
portable glTF approximations.

## Decoder provenance and byte boundaries

Destiny's PS4 pixel-shader header points to a native Orbis shader payload.  The
payload's `OrbShdr` metadata gives an exact machine-code length and input-usage
table.  `tools/d1_ps4_shader_binary_probe.py` verifies both the Destiny header
size and the Sony footer before extracting code.

The bounded code was disassembled using CLRX 0.1.9 in raw `GFX700` / GCN 1.1
mode.  CLRX reports `.gpu Spectre`, decodes both streams to `s_endpgm`, and
produces no stderr decoder errors.

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

The temporary proof run was GitHub Actions run `33868029823`; the uploaded
artifact was `09A-ps4-gcn-clrx-disassembly`, artifact ID `9934793728`, artifact
ZIP SHA-256 `268655f8c3bf0c4e4bf037ad7ba552e3d56bb56638b441471c322f6f2679412a`.

## Variant 0 / `80AAE14B`: main surface shader

### Five-image material family is visible in the machine code

The shader performs four ordinary image samples near the beginning:

```text
0x08C image_sample v[9:10],  ... dmask:3
0x094 image_sample v[4:5],   ... dmask:3
0x09C image_sample v[11:13], ... dmask:7
0x0A8 image_sample v2,       ... dmask:8
```

and later a cubemap-style explicit-LOD path:

```text
0x22C v_cubema_f32
0x234 v_cubetc_f32
0x23C v_cubesc_f32
0x254 v_cubeid_f32
0x270 image_get_lod ... dmask:2
0x2B0 image_sample_l ... dmask:15
```

This is exactly the expected resource count for `809C475F`, whose material
contains five pixel-texture records.

### Two sampled RG pairs form tangent-space normal data

The first two samples each request `dmask:3`, i.e. two components.  Immediately
after they are combined, the shader reconstructs a third component:

```text
0x0D4  v4 = v7 * v7
0x0D8  v4 += v6 * v6
0x0DC  v4 = clamp(1.0 - v4)
0x0E4  v4 = sqrt(v4)
```

Therefore the shader is reconstructing the missing normal component using:

```text
z = sqrt(max(0, 1 - x*x - y*y))
```

This is direct machine-code proof that the two RG samples are normal/detail-
normal inputs or equivalent two-component tangent-space perturbations.  It is
not an inference from BC5 format alone.

The two known BC5 textures in the material family are:

```text
80AACCDF  1024x1024 BC5
80AACC26   256x256  BC5
```

Exact resource-table index -> texture-hash correlation is tracked separately
and must be resolved before naming which one is the primary normal versus the
detail normal.

### Cubemap/environment path is explicit

The `v_cube*` coordinate instructions followed by `image_get_lod` and
`image_sample_l` prove a cube/environment lookup with explicit LOD selection.
The material's only cube-shaped image is:

```text
80AACC28  64x64 RGBA8, six faces
```

This makes `80AACC28` the uniquely compatible environment/cubemap asset.  The
final binary-proof step is still the serialized `TextureIndex` / resource-table
chunk correlation, but no other bound texture has cubemap dimensionality.

### Remaining RGB and alpha samples fit the duplicated BC3 texture

The other early samples request:

```text
dmask:7 -> RGB
dmask:8 -> alpha/W
```

`809C475F` binds `80AACCDD` twice and that image is 2048x2048 BC3.  Thus the
retail material contains exactly the representation needed to expose RGB and
alpha through separate resource-table entries while the two BC5 assets service
the two RG normal samples and the six-face RGBA8 asset services the cubemap.

This mapping is structurally exact and format-consistent, but the duplicate
BC3 resource-table indices are not promoted to `CONFIRMED_BINARY` until the
serialized material `TextureIndex` values are compared to the table loads.

### Main shader writes two render targets

The tail is:

```text
0x390 v_cvt_pkrtz_f16_f32 ...
0x394 v_cvt_pkrtz_f16_f32 ...
0x398 exp mrt1 ... compr
...
0x3A8 v_cvt_pkrtz_f16_f32 ...
0x3AC v_cvt_pkrtz_f16_f32 ...
0x3B0 exp mrt0 ... done compr vm
0x3B8 s_endpgm
```

So this pass is not a simple forward `baseColor` shader.  It writes two MRTs,
consistent with Destiny's deferred/material-buffer rendering.  A glTF PBR
export will necessarily be an approximation of this native output contract.

## Variant 1 / `816CE0A8`: circuitry palette + parallax path

Material `816CE240` binds the same grayscale BC1 texture `816CE1C5` twice.
The machine code proves those two bindings have different jobs.

### First sample: height/parallax scalar

Base UVs are interpolated from `attr3.xy` and sampled once:

```text
0x014..0x020 interpolate attr3.xy
0x024 image_sample v4, ...
```

Only one sampled scalar is retained.  Later:

```text
0x110 v1 = v4 - 0.5
0x124 scale the centered scalar
0x128/0x12C scale projected/view-space terms
0x130 reciprocal
0x134/0x13C MAD shifted coordinates onto the original UVs
```

The resulting coordinates are used for the second sample:

```text
0x144 image_sample v[0:3], ... dmask:15
```

Therefore texture binding 0 is a height/parallax/offset-mapping scalar and
binding 1 resamples the same image at the displaced coordinates.  The duplicate
texture hashes are intentional, not redundant serialization.

### Exact luminance computation from material `b0` vec3

The 8-vector PS material constant block for `816CE240` is `816CE185`.
The shader loads material-buffer dword offset `0x0C` into `s[8:11]`:

```text
s_buffer_load_dwordx4 s[8:11], ..., 0x0c
```

The offset is in dwords, so this is vec4 index 3.  `816CE185` vec3 is exactly:

```text
[0.30, 0.59, 0.11, 0.0]
```

After the displaced full-RGBA sample, the shader performs:

```text
v3 = s11 * sample.a
v3 += s10 * sample.b
v3 += s9  * sample.g
v3 += s8  * sample.r
v3 = clamp(v3)
```

Therefore the material-controlled scalar is exactly:

```text
L = clamp(0.30*R + 0.59*G + 0.11*B)
```

Alpha contributes zero.  The prior observation that vec3 looked like classic
luminance weights is now instruction-proven.

### Exact palette formula from vec4 and vec5

The same material buffer is then loaded at dword offsets:

```text
0x10 -> vec4 -> s[20:23]
0x14 -> vec5 -> s[4:7]
0x18 -> vec6 -> s[16:19]
0x1C -> vec7.x -> s12
```

The relevant machine code constructs:

```text
palette.r = vec4.r + vec5.r * L
palette.g = vec4.g + vec5.g * L
palette.b = vec4.b + vec5.b * L
```

because:

```text
v5 = vec4.r
v6 = vec4.g
v7 = vec4.b
v5 += vec5.r * L
v6 += vec5.g * L
v7 += vec5.b * L
```

For the default `816CE185` material:

```text
vec4.rgb = [0.0151604200, 0.0208455771, 0.0379010513]
vec5.rgb = [0.3848395940, 0.5291544200, 0.9620989560]
```

Thus the luminance ramp goes from the dark endpoint:

```text
L=0 -> [0.01516042, 0.02084558, 0.03790105]
```

to exactly approximately:

```text
L=1 -> [0.40000001, 0.55000000, 1.00000001]
```

So these are not arbitrary color constants: vec4 is the dark/base endpoint and
vec5 is the delta to the bright endpoint.

Other parent-selected alternatives produce correspondingly different bright
endpoints.  Examples:

```text
816CE0A9: vec4+vec5 ~= [0.41, 0.92, 1.00]
816CE186: vec4+vec5 ~= [0.70, 0.83, 1.00]
816CE187: vec4+vec5 ~= [0.36, 0.33, 1.00]
816CE188: vec4+vec5 ~= [1.00, 0.050876, 0.014085]
816CE189: vec4+vec5 ~= [1.00, 0.03, 0.05]
```

The six external-material alternatives are therefore genuine authored color
palettes over the same circuitry image.

### vec6 and vec7.x form an HDR-intensity branch

Every variant has:

```text
vec6 = [1,1,1,1]
```

and the shader multiplies `vec6.rgb` by `vec7.x` before additional global
scalars and the palette term.  Five materials use:

```text
vec7.x = 5
```

while `816CE188` uses:

```text
vec7.x = 40
```

So vec7.x is instruction-proven as a material RGB intensity multiplier.  Its
higher-level renderer name remains unclaimed; `emissive/HDR intensity` is the
portable interpretation, not a recovered Bungie field name.

### Output contract strongly indicates an additive/emissive-style pass

The shader writes only one target:

```text
0x1F0 pack R/G as f16
0x1F4 pack B/0 as f16
0x1F8 exp mrt0 ... done compr vm
0x200 s_endpgm
```

The exported fourth component is explicitly zero.  Combined with the 5x/40x
material intensity and absence of the main surface shader's second material
MRT, this is strong evidence for an emissive/additive-style circuitry pass.
The exact blend-state semantic is not yet claimed until the material/render
state producer is decoded.

## Portable reconstruction consequences

### Main surface

The native shader cannot be represented exactly by core glTF PBR because it:

- combines two tangent-space perturbation textures;
- reconstructs normal Z in shader;
- samples a dedicated cubemap with explicit LOD;
- writes two native MRTs.

A faithful portable exporter should therefore:

1. preserve all five original texture hashes and native shader/resource metadata
   in `extras`;
2. bake/combine the normal/detail-normal path when a single glTF normal map is
   required;
3. map the BC3 RGB/alpha terms only after exact resource-table index correlation;
4. preserve `80AACC28` as the original environment texture even though core
   glTF material definitions do not directly bind a per-material cubemap.

### Circuitry pass

A portable approximation can be generated much more faithfully now:

1. use `816CE1C5` luminance as the palette coordinate;
2. bake RGB as `vec4.rgb + vec5.rgb * L` for the selected variant;
3. preserve the native parallax recipe and duplicate texture bindings in
   `extras`, because core glTF has no standard parallax/offset mapping;
4. use glTF emissive color / `KHR_materials_emissive_strength` only as a
   portable approximation after the remaining global multipliers and blend
   state are understood.

## Remaining proof frontier

1. Resolve serialized PS4 `STextureTag.TextureIndex` values for `809C475F` and
   `816CE240` and correlate them to the native resource-table/direct API slots.
2. Name the exact main-surface BC3 RGB and alpha terms from downstream dataflow.
3. Trace higher-level constant buffers `b12`/`b13` and the two global scalars
   participating in the circuitry intensity chain.
4. Decode the relevant render/blend state to confirm the circuitry pass's
   additive/emissive composition mode.
5. Build the proof-grade textured + rigged + animated GLB with all native hashes,
   constants, and approximation decisions serialized in `extras`.
