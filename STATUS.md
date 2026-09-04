# Destiny 1 Reversal — Current Status

Updated: 2026-09-04

## Canonical storage

- Durable source of truth: private GitHub repo `lizardpeter/destiny-1`.
- Raw Destiny `.pkg` files, proprietary `oo2core_*` binaries, compiled bridge binaries and other proprietary/native runtime dependencies are never committed.
- Confirmed specs, tools, tests and lightweight evidence are committed after material findings.
- Runtime-only discoveries are not considered durable until promoted into the repo.

## Executive state

The package/container and compression barriers are crossed. Real final-era D1 PS4 and Xbox One Tiger v24 packages are parsed; Oodle 3 decompression works; logical entries reconstruct; PS4 textures export; model geometry/material selection is substantially decoded; a real PS4 skeleton/skin/runtime-rig pair is validated; and two real PS4 animation clips have been exported successfully.

The former `816CE09A` render-ownership ambiguity is now resolved. Higher 0767 patch siblings contain standard D1 model parent `816CE12B`, which points directly to `816CE09A` and supplies its two external-material ranges. The default visible materials are byte-proven as `809C475F` for `VariantShaderIndex=0` and `816CE240` for `VariantShaderIndex=1`. Their textures, material constants, native PS4 `OrbShdr` resource layouts and both target pixel-shader machine-code streams are now decoded. The active frontier is no longer finding the visible owner; it is completing exact texture-table/register semantics and converting the proven native two-pass material behavior into a loss-preserving portable glTF approximation.

## Real corpus

### PS4 Cabal canonical package sample

`ps4_arch_cabal_005b_1.pkg`

- PS4 / Tiger v24 / package `0x005B` / patch 1
- 89,044,992 bytes
- SHA-256 `d44f2dcbaef32743da9657e38691bcd91372fd9550e96ea3d99a9ce9440c24e0`
- 667 entries / 626 blocks
- all blocks resident and stored-payload SHA-1 verified
- 30/30 Texture2D assets exported through real Oodle + reference-chain + GCN deswizzle path
- useful renderer/material corpus but no resident model/skeleton resource in its eight `0x80800861` EntityResources

### Xbox One Cabal secondary corpus

`xboxone_arch_cabal_0059_1.pkg`

- Xbox One / Tiger v24 / package `0x0059` / patch 1
- 119,173,120 bytes
- SHA-256 `8836546ecbbbf6ba31fd50035a180c80c7bcb6407780f4b61be7a8217d24fde8`
- 8,111 entries / 2,228 block records
- 796 resident patch-1 blocks: 796/796 SHA-1 verified
- 1,432 records belong to missing patch 0
- 16 resident entity models -> 23 meshes / 284 parts
- 11 resident EntityResource model parents
- 411 resident material tags
- 27 resident inline-DXBC pixel shaders
- 276 resident vector/constant containers
- 22 animation clips exist, but all require patch 0

### PS4 Vex articulated target corpus

Primary family:

```text
ps4_arch_vex_com01_0767_0.pkg
ps4_arch_vex_com01_0767_1.pkg
ps4_arch_vex_com01_0767_4.pkg
```

Validated target cluster:

- model `816CE09A`
- standard render owner/model parent `816CE12B`
- 4,172 vertices
- 5,336 triangles after D1 triangle-strip + restart conversion
- UV0 and normals
- skeleton EntityResource `816CE092`: 12 bones
- runtime rig EntityResource `816CE095`
- runtime component hash `76F7A98E`
- 12 runtime controls with validated identity bone/control mapping
- animation `816CE09D`: hash `6FB760FF`, 31 frames, static tracks
- animation `816CE09E`: hash `D3FD602F`, 101 frames
- successful glTF skin, inverse bind matrices and animation export

Trusted rigged/animated validation GLB:

`816CE09A_816CE092_multi_animation_rigged.glb`

SHA-256:

`7c613d4ca28253a1c3ebadbf283a6fac8c0578868ea91c115ceff96211d963da`

This GLB remains trusted for geometry/skin/animation. Its material assignment is being replaced by the newly proven retail render chain rather than the rejected earlier appearance experiment.

### PS4 Vex shared/render-context package

`ps4_arch_vex_00e2_0.pkg`

- package `0x00E2`
- 5,451 entries
- 130 EntityResources
- 47 `s_entity_model` entries
- 35 standard D1 model parents
- 11 animation clips
- 130 techniques
- direct entity/composition correspondence with the `0767` combatant graph
- owns default variant-0 material `809C475F`

This package supplied the ordinary Vex material control fixture and the default variant-0 material used by the actual `816CE09A` parent.

## Retail package acquisition

The public final D1 PS4 corpus is exposed as ten split TAR volumes rather than direct per-package URLs. A reusable sparse extractor is now committed:

`tools/d1_split_tar_extract.py`

Working behavior:

- discovers split sizes with HTTP Range;
- walks TAR headers without downloading skipped package payloads;
- verifies TAR magic/checksums;
- extracts only requested package members across split boundaries;
- records exact logical TAR offsets, sizes and SHA-256 hashes;
- supports validated `--start-offset` resume from previously calibrated family positions.

Known 0767 retail TAR locations:

```text
0767_0 header 0x105C6E000  size 42,686,464
0767_1 header 0x108523A00  size  8,278,016
0767_4 header 0x108D08C00  size     24,576
```

Known 0157 locations:

```text
0157_0 header 0x46AF91400  size 206,192,640
0157_1 header 0x477435600  size  30,326,784
```

The former direct-URL 404 problem is therefore obsolete; higher patch siblings are recoverable deterministically from the split archive.

## Oodle 3

Working with the project Oodle 3 Linux bridge plus a verified `oo2core_3_win64.dll` runtime. Runtime hashes are recorded in `notes/OODLE_RUNTIME.md`; binaries are not committed.

Representative validation:

- PS4 compressed blocks reconstruct exact `0x40000` logical blocks.
- Xbox resident patch-1 blocks reconstruct correctly.
- stored block SHA-1 verification is enforced before decompression.

## Package / resource layer

Working:

- Tiger v24 header, FileEntry and BlockEntry parsing.
- table SHA-1 and stored-block SHA-1 verification.
- patch-family ownership and sibling `.pkg` path handling.
- D1 TagHash construction/decomposition.
- generic decompressed entry reader.
- graph/reference analysis and cross-package comparison.
- `entry_b[23:16]` preservation constraint across observed local edges.
- standard D1 EntityResource role decoding for model/skeleton/physics resources.
- standard model-parent signature `0x80801A80 -> 0x80801A9C`.
- sparse package recovery directly from the public split TAR corpus.

## GPU/resource layer

### Vertex / index

- Vertex header `0x0C`; PS4 marker `BEEFCACE`, Xbox `BEEFDEAD`.
- Index header `0x18`; index width and payload size validated.
- PS4 and Xbox model geometry paths exist.
- D1 triangle strips and `0xFFFF` restart conversion validated on the Vex articulated model.

### PS4 textures

- Texture2D header `0x3C`.
- BC1/BC3/BC4/BC5 validated visually.
- streamed texture backing across package boundaries is resolved.
- exact Vex material textures have been decoded through the `0156/0157` chain.
- `816CE1C5` is a real 256x512 BC1 grayscale Vex circuitry/panel texture.
- target variant-0 images include 2048² BC3 `80AACCDD`, 1024² BC5 `80AACCDF`, 256² BC5 `80AACC26`, and six-face 64² RGBA8 `80AACC28`.

### Xbox textures

- header `0x44` with DXGI format/tile mode, dimensions and three flag words solved.
- first model's bound textures are known but use Durango tile mode 14.
- portable tile-mode-14 detiling remains an Xbox-side engineering target.

### PS4 shaders

Native shader framing and resource binding are now decoded substantially beyond the earlier header-only state.

Reusable tool:

`tools/d1_ps4_shader_binary_probe.py`

Confirmed on target retail binaries:

- D1 PixelShader packed header low 24 bits = native payload size.
- packed header high 8 bits = Sony InputUsageSlot count.
- FileEntry.Reference points to the native Orbis shader payload.
- native payload starts with standard `BEEB03FF` GCN token/instruction.
- source-correlated `OrbShdr` footer formula lands exactly on the sole footer signature.
- 28-byte ShaderBinaryInfo stage, code-length and input-usage metadata parse cleanly.
- Sony InputUsageSlot resource/sampler/constant-buffer layout is decoded.

Target `80AAE14B`:

```text
native payload 80AAE14D
payload 1028 bytes
GCN code 956 bytes
5-image resource table
5 samplers
b0 + b12 constant buffers
```

Target `816CE0A8`:

```text
native payload 816CE0AE
payload 580 bytes
GCN code 516 bytes
2 immediate texture resources
2 samplers
b0 + b12 + b13 constant buffers
```

LLVM 18 exposes the old gfx700 target names but intentionally lacks their disassembler implementation. CLRX 0.1.9 successfully disassembles the exact bounded streams in raw GFX700 / GCN 1.1 mode to `s_endpgm` with no decoder errors.

See:

- `spec/D1_MATERIALS_SHADERS.md`
- `notes/PS4_09A_SHADER_DATAFLOW.md`

## Entity/model layer

D1 ROI `0x80800861` is the EntityResource outer-container class. ROI `s_pattern_component` is `0x80800715`; do not reuse the older TTK mapping.

Confirmed:

- model discriminator `0x80801A80`.
- model parent class `0x80801A9C`.
- PS4 embedded EntityModel field in the standard parent is at the validated D1 source-correlated location used by the project parser.
- Xbox embedded EntityModel field in parent at `+0x1C4`.
- model mesh/part arrays, variant shader indices, resource hashes and buffer descriptors parse across current corpora.
- target parent `816CE12B -> 816CE09A` is byte-proven in higher 0767 patch siblings.

## Materials / shader binding

See `spec/D1_MATERIALS_SHADERS.md`.

Confirmed:

- PS4 ROI material class `0x80801AD7`.
- Xbox material family observed as `0x80801C32`.
- Xbox `STextureTag.TextureIndex` is the actual DXBC `t#` register: 11/11 exact.
- material PS sampler count equals shader sampler count in all validated Xbox overlaps.
- Xbox vector container `0x80801AA5` exact `0x30 + N*16` layout across 276/276 resident examples.
- PS4 subtype `32:7` material-vector header is exactly 16 bytes; `+0x08` is vec4 unit count and FileEntry.Reference resolves to a raw `N*16` vec4 payload.
- material-provided pixel constants feed `b0` semantics across the Xbox/PS4 comparison.
- standard PS4 model-parent `ExternalMaterialsMap` / `ExternalMaterials` selection is decoded.

### Target render owner and default materials

```text
816CE12B -> model 816CE09A

ExternalMaterialsMap[0] count=2 start=0
  809C475F  <- default variant 0
  809C4760

ExternalMaterialsMap[1] count=6 start=2
  816CE240  <- default variant 1
  816CE241
  816CE242
  816CE243
  816CE244
  816CE1A7
```

### Variant 0 default / main surface

`809C475F`:

- PS `80AAE14B`
- PS constant container `80AAE14C`: 19 vec4s
- five material texture records
- machine code proves two two-component normal/detail perturbation samples followed by `sqrt(max(0,1-x²-y²))` normal-Z reconstruction
- machine code proves a cubemap/environment sample with explicit LOD
- remaining early samples read RGB and alpha separately
- native pass exports both `mrt0` and `mrt1`

Known image family:

```text
80AACCDD  2048x2048 BC3, bound twice
80AACCDF  1024x1024 BC5
80AACC26    256x256  BC5
80AACC28     64x64   RGBA8 x6 faces
```

The exact serialized PS4 `TextureIndex` -> resource-table chunk correlation is the remaining proof needed to label primary/detail-normal and duplicated BC3 RGB/A slots without inference.

### Variant 1 default / circuitry palette pass

`816CE240`:

- PS `816CE0A8`
- two texture records, both `816CE1C5`
- PS `b0` container `816CE185`: 8 vec4s
- first texture binding is sampled as a height/parallax scalar and shifts the UVs
- second binding resamples the same texture at the displaced coordinates
- vec3 is instruction-proven luminance weights `[0.30,0.59,0.11,0]`
- exact palette equation is instruction-proven:

```text
L = clamp(dot(sample.rgb, [0.30, 0.59, 0.11]))
palette.rgb = vec4.rgb + vec5.rgb * L
```

Default palette endpoints:

```text
L=0 -> [0.01516042, 0.02084558, 0.03790105]
L=1 -> approximately [0.40, 0.55, 1.00]
```

- vec6 is `[1,1,1,1]` in all six variants.
- vec7.x is an instruction-proven material RGB intensity multiplier: normally `5`, but `816CE188` uses `40`.
- shader writes only `mrt0`; exported fourth component is zero.
- combined behavior strongly indicates an HDR/additive/emissive-style circuitry pass; exact blend-state naming remains pending render-state proof.

## Skeleton / skin / runtime rig

See `spec/D1_SKELETONS_ANIMATIONS.md`.

Validated on PS4 retail bytes:

- skeleton discriminator `0x808006BD`.
- skeleton info `0x8080049A`.
- node hierarchy.
- default and inverse object-space transforms.
- range/inner index maps.
- 12-node skeleton `816CE092`.
- skinning of `816CE09A` into glTF.
- runtime rig `816CE095` with secondary class `0x808008B2`.
- runtime component hash `76F7A98E`.
- 12 controls and identity bone/control mapping for this instance.

The complete general field schema for `0x808008B2` is **not yet durably decoded**. Do not recreate offsets from memory; use only byte-documented fields when promoting the schema.

## Animation

Final ROI clip class:

`0x808005A1 = s_animation_clip`

Two concrete PS4 clips (`816CE09D/E`) have been successfully decoded and exported against the 12-node Vex rig. This proves the current runtime decoding for that clip family, but a reusable general clip decoder is not yet committed.

General D1 animation compression/layout therefore remains **partially solved**, not globally solved.

## `0x8080222A` animation-bundle/proxy pattern

Observed repeatedly:

```text
0x8080222A structured wrapper
    -> nearby/forward s_entity_model
    -> Havok hk_2012.2.0-r1 data
    -> control/wrapper data
    -> s_animation_clip(s)
```

Target wrapper `816CE099` contains aligned dword `D3FD602F`, exactly the validated animation hash of `816CE09E`.

Equivalent clusters occur in `00E2_0`, including `809C4B96 -> 809C4B97`.

Important correction: adjacency to `0x8080222A` does not itself prove render ownership, but it also does **not** negate renderability. The actual standard model parent is now independently proven as `816CE12B`, so `816CE09A` no longer needs to be treated only as an animation proxy.

Reusable classifier:

`tools/d1_animation_bundle_probe.py`

## Current active frontier

The target owner/model/material problem is solved. The active question is now:

> How do we reproduce the two proven native PS4 material passes in a portable, visibly faithful export while preserving every native binding and approximation decision?

Immediate proof tasks:

1. resolve PS4 `STextureTag.TextureIndex` for `809C475F` and `816CE240` against native resource-table/direct API slots;
2. finish exact naming of the BC3 RGB/alpha terms in `80AAE14B` from downstream dataflow;
3. trace `b12` / `b13` producers and the non-material global intensity scalars in `816CE0A8`;
4. decode blend/render state sufficiently to prove the circuitry pass composition mode;
5. bake a single portable normal map from the proven primary+detail normal path if required by glTF;
6. bake the circuitry palette from `816CE1C5` using the exact `vec4 + vec5*L` formula while preserving parallax metadata;
7. attach both portable approximations to the already-valid rigged + animated target GLB and serialize the original parent/material/shader/texture/constants/resource-table hashes in `extras`;
8. validate the resulting GLB structurally and visually.

## Final textured-export acceptance rule

Do not call the portable GLB a faithful retail reconstruction until all applicable checks pass:

1. standard model parent is byte-proven (`816CE12B` passes);
2. visible model is identified from that parent (`816CE09A` passes);
3. skeleton/control relationship is byte-proven (`816CE092/095` passes for this model export);
4. external material selection comes from the model's own parent (passes);
5. texture hashes come from those exact materials (passes at material-list level);
6. native shader resource role is instruction/resource-table proven, not assigned from visual guesswork;
7. portable PBR/emissive substitutions are explicitly labeled approximations and native metadata is preserved losslessly;
8. Blender/glTF validation succeeds with geometry, skin, animations and final material bindings intact.
