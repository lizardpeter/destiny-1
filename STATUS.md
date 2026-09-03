# Destiny 1 Reversal — Current Status

Updated: 2026-09-03

## Canonical storage

- Durable source of truth: private GitHub repo `lizardpeter/destiny-1`.
- Runtime analysis mirror: `/mnt/data/Destiny1_Reversal/`.
- Raw Destiny `.pkg` files, proprietary `oo2core_*` binaries, compiled bridge binaries and other proprietary/native runtime dependencies are never committed.
- Confirmed specs, tools, tests and lightweight evidence are committed after material findings.

## Executive state

The package/container and compression barriers are crossed. Real final-era D1 PS4 and Xbox One Tiger v24 packages are parsed; Oodle 3 decompression works; logical entries reconstruct; PS4 textures export; vertex/index geometry exports; Xbox entity-model metadata is decoded; and material-to-native-shader register binding is now proven.

The active frontier is no longer archive extraction. It is **complete semantic asset assembly**: model/material selection, platform texture layout, skeleton/skin binding, and animation clips.

## Real corpus

### PS4 canonical sample

`ps4_arch_cabal_005b_1.pkg`

- PS4 / Tiger v24 / package `0x005B` / patch 1
- 89,044,992 bytes
- SHA-256 `d44f2dcbaef32743da9657e38691bcd91372fd9550e96ea3d99a9ce9440c24e0`
- 667 entries / 626 blocks
- all blocks resident and stored-payload SHA-1 verified
- 30/30 Texture2D assets exported through real Oodle + reference-chain + GCN deswizzle path
- useful renderer/material corpus but no resident entity-model/skeleton resource in the eight `0x80800861` EntityResource tags

### Xbox One secondary corpus

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

## Oodle 3

Working with user-supplied `oo2core_3_win64.dll` via the project experimental Linux PE bridge. The current runtime DLL hash is recorded in `notes/OODLE_RUNTIME.md`; the DLL itself is not committed.

Representative validation:

- PS4: 12/12 compressed blocks -> exact `0x40000` logical bytes.
- Xbox resident patch 1: 12/12 -> exact `0x40000`.

## Package / resource layer

Working:

- Tiger v24 header, FileEntry and BlockEntry parsing.
- table SHA-1 and stored-block SHA-1 verification.
- patch-family ownership and `.pkg.bin` path handling.
- D1 TagHash construction/decomposition.
- generic decompressed entry reader.
- graph/reference analysis and cross-package comparison.
- `entry_b[23:16]` preserved across every observed local edge: PS4 209/209; Xbox 3,171/3,171.

## GPU/resource layer

### Vertex / index

- Vertex header `0x0C`; PS4 marker `BEEFCACE`, Xbox `BEEFDEAD`.
- Index header `0x18`; index width and payload size validated.
- real topology proof GLBs exist.
- Xbox metadata-driven entity-model GLB export exists.

### PS4 textures

- Texture2D header `0x3C`.
- BC1/BC3/BC4/BC5 validated visually.
- 30/30 canonical textures exported.

### Xbox textures

- header `0x44` with DXGI format/tile mode, dimensions and three flag words solved.
- first model's actual bound textures are known, but use Durango tile mode 14.
- active parallel target: replace/bridge the Windows XG address-computer dependency so tile-mode-14 textures can be detiled and attached to the metadata-driven model.

### PS4 shaders

- native GCN framing and `OrbShdr` footer parsed.
- PixelShader packed header word solved: low 24 bits payload size; high 8 bits input-usage-slot count.

## Entity/model layer

D1 ROI `0x80800861` is treated as the EntityResource outer-container class by the real ROI entity consumer. ROI `s_pattern_component` is `0x80800715`; do not reuse the older TTK mapping.

Xbox real-byte results:

- model discriminator `0x80801A80`.
- model parent class `0x80801A9C`.
- Xbox embedded EntityModel field in parent at `+0x1C4`.
- 16 resident model tags / 23 meshes / 284 parts.
- model `808B3A16` is fully resident and is the first clean end-to-end model target.

## Materials / shader binding

See `spec/D1_MATERIALS_SHADERS.md`.

Confirmed:

- PS4 ROI material class is Charm's `SMaterial_ROI` at numeric `0x80801AD7`.
- Xbox material family observed as `0x80801C32`.
- Xbox `STextureTag.TextureIndex` is the actual DXBC `t#` register: 11/11 exact.
- material PS sampler count equals shader sampler count: 11/11; registers contiguous `s1..sN`.
- Xbox vector container `0x80801AA5` has an exact `0x30 + N*16` layout across 276/276 resident examples.
- material-provided pixel constants equal DXBC `b0` vec4 count: 11/11.
- PS4 subtype 7 is therefore semantically confirmed cross-platform as material constant/vector-buffer data; original Bungie type name remains unclaimed.

Still unresolved:

- sampler record tail fields.
- shared sampler/vertex-shader package `0x156` dependencies.
- non-material cbuffers such as `b12` / `b13`.
- portable PBR semantic mapping for texture slots.

## Skeleton / animation

See `spec/D1_SKELETONS_ANIMATIONS.md`.

Skeleton parser is implemented for D1 source-correlated layout:

- skeleton discriminator `0x808006BD`.
- skeleton info `0x8080049A`.
- node hierarchy, default object transforms, inverse transforms and index maps decoded by the parser.
- current real corpus has no resident skeleton resource to binary-validate this layout yet.

Animation:

- final ROI `s_animation_clip = 0x808005A1`.
- Xbox package contains 22 clips, all patch-0-backed.
- animation track compression/layout remains a genuine active RE target.

Historical Destiny extractor source independently corroborates the node/transform shape and includes weapon-mechanism hash names (`GunBase`, `Trigger`, `Magazine`, etc.); retained as a source lead, not D1 binary fact.

## Current highest-value inputs

1. `xboxone_arch_cabal_0059_0.pkg` — unlocks the 22 known animation clips and likely skeleton resources.
2. A PS4 model/entity/weapon package — enables canonical full textured/skinned PS4 validation.
3. Xbox shared package ID `0x156` — contains observed shared sampler and likely vertex-shader dependencies.

## Immediate engineering/reversal targets

1. Finish Xbox Durango tile-mode-14 detiling and texture model `808B3A16`.
2. Resolve sampler descriptors and shared vertex-shader dependencies.
3. Trace non-`b0` constant buffers.
4. Validate the D1 skeleton parser against real resident bytes as soon as an appropriate package is acquired.
5. Reverse `s_animation_clip` once patch-0 clip bytes are available.
6. Build a global TagHash/class/dependency index over acquired package sets so weapon extraction becomes recursive and package-independent.
7. Produce a one-command loss-preserving asset export path: model + mesh parts + materials + textures + skin + animations + raw provenance metadata.
