# Destiny 1 Reversal — Current Status

Updated: 2026-09-04

## Canonical storage

- Durable source of truth: private GitHub repo `lizardpeter/destiny-1`.
- Raw Destiny `.pkg` files, proprietary `oo2core_*` binaries, compiled bridge binaries and other proprietary/native runtime dependencies are never committed.
- Confirmed specs, tools, tests and lightweight evidence are committed after material findings.
- Runtime-only discoveries are not considered durable until promoted into the repo.

## Executive state

The package/container and compression barriers are crossed. Real final-era D1 PS4 and Xbox One Tiger v24 packages are parsed; Oodle 3 decompression works; logical entries reconstruct; PS4 textures export; model geometry/material selection is substantially decoded; a real PS4 skeleton/skin/runtime-rig pair is validated; and two real PS4 animation clips have been exported successfully.

The newest correction is architectural: the articulated Vex model `816CE09A`, although fully reconstructable as a rigged/animated GLB, is **not currently treated as the final visible retail combatant model**. Retail byte evidence places it in a recurring `0x8080222A` animation-bundle/proxy pattern. The active frontier is therefore to connect validated animation bundles to the correct ordinary visible model/entity/material ownership graph without guessing textures or parentage.

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

### PS4 Vex articulated validation corpus

Primary target package:

`ps4_arch_vex_com01_0767_0.pkg`

Validated target cluster:

- model/proxy `816CE09A`
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

The clean rigged/animated `816CE09A` GLB remains a trusted **animation-system validation artifact**, not a final textured combatant claim.

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

This package supplied the decisive animation-proxy comparison and the first fully byte-proven ordinary Vex external-material chain.

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

### Xbox textures

- header `0x44` with DXGI format/tile mode, dimensions and three flag words solved.
- first model's bound textures are known but use Durango tile mode 14.
- portable tile-mode-14 detiling remains an Xbox-side engineering target.

### PS4 shaders

- native GCN framing and `OrbShdr` footer parsed.
- PixelShader packed header word solved: low 24 bits payload size; high 8 bits input-usage-slot count.

## Entity/model layer

D1 ROI `0x80800861` is the EntityResource outer-container class. ROI `s_pattern_component` is `0x80800715`; do not reuse the older TTK mapping.

Confirmed:

- model discriminator `0x80801A80`.
- model parent class `0x80801A9C`.
- PS4 embedded EntityModel field in the standard parent is at the validated D1 source-correlated location used by the project parser.
- Xbox embedded EntityModel field in parent at `+0x1C4`.
- model mesh/part arrays, variant shader indices, resource hashes and buffer descriptors parse across current corpora.

## Materials / shader binding

See `spec/D1_MATERIALS_SHADERS.md`.

Confirmed:

- PS4 ROI material class `0x80801AD7`.
- Xbox material family observed as `0x80801C32`.
- Xbox `STextureTag.TextureIndex` is the actual DXBC `t#` register: 11/11 exact.
- material PS sampler count equals shader sampler count in all validated overlaps.
- Xbox vector container `0x80801AA5` exact `0x30 + N*16` layout across 276/276 resident examples.
- material-provided pixel constants equal DXBC `b0` vec4 count in all validated overlaps.
- standard PS4 model-parent `ExternalMaterialsMap` / `ExternalMaterials` selection is decoded.

### Proven ordinary Vex render/material fixture

`809C44A5 -> 809C47F4`

- ordinary standard model parent
- variants 0 and 1 resolved through real external materials
- material family `809C475F / 809C4760`
- exact PS texture bindings decoded
- backing textures resolved through `0156/0157`

This is a rendering/material **control fixture**. Its skeleton/runtime-control compatibility with the 12-control `816CE095` rig is not yet proven.

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

This is the largest semantic correction in the current frontier.

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

Safe project conclusion:

- observed semantic role: **animation-bundle/proxy pattern**
- original Bungie class name: unknown
- internal field schema: unresolved
- adjacency to this wrapper does **not** prove final visible render ownership

Reusable classifier:

`tools/d1_animation_bundle_probe.py`

It uses no guessed wrapper offsets. It correlates class/order, Havok markers, EntityResource roles and optional known raw animation-hash dwords.

## Direct-retarget elimination: `809C4B97`

`809C4B97` is the closest known proxy-family geometry analogue to `816CE09A`, but its companion skeleton `809C4B90` has **8 bones**, versus 12 bones/12 controls for `816CE092/095`.

It is therefore eliminated as a direct skeleton-compatible target for `816CE09D/E` under the current acceptance criteria. It remains a valuable format comparison fixture.

## Current active frontier

The next question is not “which textures belong on `816CE09A`?”

It is:

> Which ordinary visible Vex model parent/model/skeleton/control cluster is byte-compatible with the validated 12-node / 12-control `816CE092 / 816CE095 / 76F7A98E` animation bundle?

New ranking tool:

`tools/d1_animation_proxy_compat_probe.py`

It ranks standard visible-model candidates using only proven parsers plus raw graph/fingerprint evidence. Its score is explicitly heuristic and cannot itself promote a candidate to final visible-model status.

First candidate-specific byte test:

```text
809C44A5 -> 809C47F4
    ? co-referenced 12-bone skeleton
    ? 76F7A98E runtime-component fingerprint
    ? equivalent 12-control mapping
```

If that fixture fails, enumerate the other 34 standard parents in `00E2_0`.

## Patch sibling recovery status

The public manifest names higher Vex patch siblings including:

- `ps4_arch_vex_com01_0767_1.pkg`
- `ps4_arch_vex_com01_0767_4.pkg`
- `ps4_arch_vex_00e2_1.pkg`
- `ps4_arch_vex_00e2_2.pkg`
- `ps4_arch_vex_00e2_4.pkg`

Historical GitHub Actions artifacts were inspected directly. All five public-mirror recovery attempts were recorded as HTTP 404/misses. No retained historical artifact contains those package bytes, and no retained artifact contains the base `_0` package payloads.

Do not repeat the same mirror attempt unless the mirror changes.

## Immediate engineering / reversal targets

1. Run `d1_animation_proxy_compat_probe.py` over `0767_0 + 00E2_0 + 0156_0 (+0157)` when those already-used package bytes are available in the active runtime.
2. Test `809C44A5 -> 809C47F4` for 12-bone / `76F7A98E` / 12-control compatibility before any retarget or texture claim.
3. Generalize and durably document the `0x808008B2` runtime-rig field layout from real bytes.
4. Promote the successful PS4 animation-clip decoder into a reusable committed tool without overgeneralizing beyond validated compression modes.
5. Use `d1_animation_bundle_probe.py` to classify `0x8080222A` neighborhoods across future packages and prevent proxy models from being mislabeled as final render models.
6. Finish Xbox Durango tile-mode-14 detiling and texture model `808B3A16`.
7. Build the global TagHash/class/dependency index so complete asset export becomes package-independent.
8. Produce a one-command loss-preserving asset path: visible model + materials + textures + skin + compatible animations + raw provenance metadata.

## Final-visible-model acceptance rule

Do not call a Vex candidate the final retail animated body until all applicable checks pass:

1. ordinary standard model parent is byte-proven;
2. visible model is identified from that parent;
3. compatible skeleton/control relationship is byte-proven;
4. runtime control map matches the 12-control animation bundle;
5. clips retarget without hierarchy/transform anomalies;
6. external material selection is resolved from the candidate's own parent;
7. textures come from those exact materials, not adjacency or visual guessing;
8. Blender/glTF validation succeeds.
