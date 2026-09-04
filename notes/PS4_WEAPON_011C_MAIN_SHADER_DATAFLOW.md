# PS4 011C final main-shell shader dataflow

Date: 2026-09-04

Target weapon model: `80A39E12`

Final visible main-shell material:

```text
80A382A6
  VS 80A3D28E
  PS 80A3D145
```

This checkpoint records instruction-level behavior from the exact retail PS4
GCN binaries. It deliberately separates machine-code-proven behavior from
strong but not-yet-byte-closed runtime binding inferences.

## Binary provenance

### Pixel shader `80A3D145`

Exact bounded native code:

- payload: `80A3D146`
- code length: 1,444 bytes
- GCN SHA-256:
  `27abce95b795fdbec39934d21f3841e7fca98ad00809948c0ac59921ecc8cff4`
- OrbShdr stage: PixelShader
- OrbShdr input-usage slots: 11
- usage masks: `0000007F 00000000`

The seven low bits in the resource-table usage mask are set, matching the seven
resource chunks `t0..t6` consumed by the native shader.

Exact disassembly workflow:

- workflow: `.github/workflows/tmp-disasm-80A3D145.yml`
- run: `33904501706`
- result: success
- artifact: `80A3D145-clrx-disassembly`
- artifact id: `9948982249`

### Vertex shader `80A3D28E`

Exact bounded native code:

- payload: `80A3D28F`
- code length: 516 bytes
- GCN SHA-256:
  `c212e3fadd3293c2d001a47f7199feee71026aa11004039723ede2cfef2303ad`
- OrbShdr stage: VertexShader

VS/sampler closure workflow:

- workflow: `.github/workflows/tmp-disasm-80A3D28E-samplers.yml`
- run: `33905024740`
- result: success
- artifact: `80A3D28E-vs-main-samplers`
- artifact id: `9949194210`
- artifact ZIP digest:
  `sha256:f29cf20387b8f9e63a4b27d1b0a130910a6eed141edba2c9f2e8512453c6a337`

## Material-side serialized resources

Final material `80A382A6` contains only two ordinary PS texture records:

```text
TextureIndex 0 -> 80AB0B74  128x128 BC1 cubemap, 6 faces
TextureIndex 1 -> 80A3D4D6  128x128 BC1 2D
```

It has no PS Vector4 container:

```text
ps_vector4_container = FFFFFFFF
```

It serializes seven sampler records, in shader-slot order:

```text
slot 1 -> 80AAE176
slot 2 -> 80AAE177
slot 3 -> 80AAE177
slot 4 -> 80AAE177
slot 5 -> 80AADBAB
slot 6 -> 80AADBAB
slot 7 -> 80AADBAB
```

The PS resource table uses 8 bytes per texture/resource descriptor chunk, so
instruction loads at offsets `0x00,0x08,...,0x30` correspond exactly to
`t0..t6`.

## Exact native sampler descriptors

### `80AAE176` — t0 cubemap sampler

```text
S# words = 00000092 00F00000 0A503F80 00000000
wrap XYZ = ClampLastTexel
mag       = Bilinear
min       = Bilinear
mip       = Linear
```

### `80AAE177` — t1/t2/t3 2D sampler

```text
S# words = 00000000 00F00000 0A503F80 00000000
wrap XYZ = Wrap
mag       = Bilinear
min       = Bilinear
mip       = Linear
```

### `80AADBAB` — t4/t5/t6 primary-surface sampler

```text
S# words = 00000492 00F00000 0AF03F80 00000000
wrap XYZ = ClampLastTexel
max_aniso_ratio_raw = 2
mag       = AnisoBilinear
min       = AnisoBilinear
mip       = Linear
```

The same three-resource sampler grouping is encoded directly by the final
material and then consumed by the exact PS input-usage layout.

## Vertex-to-pixel interpolant contract

The exact VS ends with:

```text
param0 = (v5,  v4,  v6,  v0)
param1 = (v11, v14, v2,  v2)
param2 = (v1,  v8,  v9,  1)
param3 = (v15, v16, v12, v13)
param4 = (v7,  v10, v3,  1)
```

The pixel shader consumes these as `attr0..attr4`.

The exact VS arithmetic for `param3` is:

```text
u0 = s6 + s4 * fetched_v8
v0 = s7 + s5 * fetched_v9
u1 = fetched_v20 * u0
v1 = fetched_v21 * v0

param3 = (u0, v0, u1, v1)
```

Therefore the native PS has two related coordinate pairs:

```text
primary   = attr3.xy
secondary = attr3.zw
```

The secondary pair is not an unrelated arbitrary UV set: the VS derives it from
the primary pair using two fetched per-vertex multipliers. The exact fetch-
shader mapping of `v8/v9/v20/v21` back to named packed vertex-stream elements
remains a separate boundary and is not guessed here.

The PS also proves that native MRT0 alpha comes from interpolated `attr0.w`.
Neither `80A3D4D6` nor the cubemap alpha is material transparency.

## t2/t3 and t4/t5/t6 sample structure

The first five 2D samples are instruction-visible before any semantic naming:

```text
t2 -> RGBA sampled from an affine transform of attr3.zw
t3 -> RG   sampled from the same secondary coordinates

t4 -> RGB  sampled from attr3.xy
t5 -> RG   sampled from attr3.xy
t6 -> RGB  sampled from attr3.xy
```

The two RG pairs (`t3`, `t5`) are both decoded from `[0,1]` to `[-1,1]`, blended,
and used to reconstruct a Z component followed by normalization. They are
therefore instruction-proven contributors to the surface-normal path.

The color paths are also distinct:

- `t2.rgb` participates in the secondary/dye/detail color path;
- `t4.rgb` participates in the primary surface color path;
- `t6.rgb` supplies control/material scalars used by blending and the reflection
  path;
- `t6.r` also participates in deferred material packing/selection logic.

### Current binding confidence

The model owner contains exactly the D1 ROI texture-plate triplet:

```text
AlbedoPlate
NormalPlate
GStackPlate
```

The shader has exactly a three-resource primary-UV group `t4/t5/t6`, all using
one anisotropic ClampLastTexel sampler. Its machine-code shapes are
RGB / RG-normal / RGB-control, which is an extremely strong structural match to
that owner triplet.

However, the D1 78-byte TFX resource-binding stream still contains an opcode
currently named `Unk49` by the available D1 parser, so this checkpoint does NOT
yet label the following as `CONFIRMED_BINARY`:

```text
t4 = AlbedoPlate
t5 = NormalPlate
t6 = GStackPlate
```

Those assignments remain `INFERRED_STRONG` until the D1 TFX binding program or
an equivalent runtime binding source closes the exact slot identities. The
portable exporter may continue using the owner albedo/normal plates because
the owner relationship itself is proven, but it must not claim the native
`t4/t5/t6` register names as solved yet.

Likewise `t2/t3` have a clear secondary color + normal structure but are not
assigned Bungie field names here.

## t0 / `80AB0B74` is now a proven reflection/environment cubemap

This is no longer based merely on the resource being a six-face image.

The native PS constructs a normalized reflection-like vector and executes the
GCN cube-address sequence:

```text
v_cubema_f32
v_cubetc_f32
v_cubesc_f32
v_cubeid_f32
```

It then performs:

```text
image_get_lod ... t0
lod = max(hardware_cube_lod, CB0[dword 0x0c])
image_sample_l ... t0
```

The sampled t0 RGB contributes directly to final MRT0 RGB. Sampled t0 alpha is
also used as a multiplier on the cubemap contribution.

Therefore:

```text
TextureIndex 0 / t0 / 80AB0B74
```

is instruction-proven as an environment/reflection cubemap path.

Core glTF 2.0 has no native material cubemap slot equivalent to this deferred
D1 path, so retaining the six exact faces as provenance is more faithful than
inventing a core-PBR mapping.

## t1 / `80A3D4D6` is a proven reflection-modulation scalar texture

The PS loads resource-table offset `0x08`, therefore `t1`, and samples one
channel from an affine transform of `attr3.xy`.

That scalar is multiplied by additional material/control scalars derived from
`t6` and CB0. The result multiplies the t0 cubemap RGB before the cubemap term
is added to the final surface color.

Thus:

```text
TextureIndex 1 / t1 / 80A3D4D6
```

is instruction-proven to be a 2D scalar modulation of the reflection/cubemap
contribution. It is not base color and it is not opacity.

No more specific Bungie-authored semantic name is assigned from the image's
visual appearance.

## Deferred output contract

The shader writes two MRTs:

```text
MRT1 = packed normal/material data
MRT0 = final surface/reflection RGB + attr0.w alpha
```

Both are emitted in compressed half-float form at the end of the shader.

This is a native deferred material pass, not a forward glTF metallic/roughness
shader. Any core glTF material remains an explicitly portable approximation.

## Export policy after this closure

Evidence-backed behavior that may be recorded in GLB extras:

- exact PS/VS code SHA-256s;
- exact seven-resource usage mask;
- t0 `80AB0B74` = environment/reflection cubemap path;
- cubemap uses hardware LOD plus a minimum LOD from CB0;
- t1 `80A3D4D6` = 2D scalar modulation of cubemap contribution;
- exact native sampler descriptors for t0, t1/t2/t3, t4/t5/t6;
- t2/t3 secondary color+normal structure;
- t4/t5/t6 primary RGB + normal + control structure;
- native MRT0 alpha = `attr0.w`;
- native pass is deferred.

Still forbidden to claim without further proof:

- a Bungie field name for `80A3D4D6`;
- exact `t4/t5/t6` plate slot identities;
- a glTF roughness/metallic interpretation for GStack channels;
- a core-glTF cubemap equivalent to the native reflection path.
