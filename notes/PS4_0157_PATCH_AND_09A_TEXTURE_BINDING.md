# PS4 0157 patch analysis and 816CE09A texture-binding frontier

Date: 2026-09-03/04

## Inputs

- `ps4_arch_vex_com01_0767_0.pkg`
- `ps4_globals_0157_0.pkg`
- `ps4_globals_0157_1.pkg`

## 0157 patch pair

`ps4_globals_0157_0.pkg`:

- package ID `0x0157`
- patch ID `0`
- 2,117 entries
- 1,623 blocks

`ps4_globals_0157_1.pkg`:

- package ID `0x0157`
- patch ID `1`
- 8,192-entry full namespace
- 1,692 blocks
- SHA-256 `928da89841e76d9aa08706e8ecc65a64bf295d11bb01940619112e90be0ee4c2`
- 645 patch-1 EntityResources were decoded and searched

The patch package does not replace the two 0767 inline auxiliary techniques `80AAE10B`/`80AAE10C`; those still resolve to patch-0 data. No new patch-1 EntityResource contains a literal reference to model `816CE09A`, skeleton `816CE092`, or runtime rig `816CE095`. Therefore 0157_1 does not contain the missing standard model parent for 09A.

## Correct visible-material interpretation

`816CE09A` has four D1 parts. The two normal visible paths use `VariantShaderIndex` 0 and 1. The duplicate inline-material passes use `80AAE10B` and `80AAE10C`, but both decoded techniques have a vertex shader, no pixel shader (`FFFFFFFF`), and zero direct texture arrays; under Charm's D1 filtering behavior they are not ordinary visible surface passes.

Charm's D1 path is:

- `VariantShaderIndex == -1` -> inline material
- otherwise -> model parent `ExternalMaterialsMap[variant]` -> `ExternalMaterials[...]`

The exact standard ROI model-parent offsets were calibrated as:

- model FileHash `+0x15C`
- TexturePlatesROI `+0x1A8`
- ExternalMaterialsMap `+0x230` (0x0C-byte entries)
- ExternalMaterials `+0x270` (4-byte material hashes)

## Strong shared-material candidate: 816CE17F

The neighboring Vex models `816CE0C5` and `816CE0C6` use the same 12-byte position + 16-byte secondary vertex-buffer layout as articulated model `816CE09A`. `816CE0C6` also uses variant paths 0 and 1. Its resident parent `816CE0C3` maps both variants, under Charm's current D1 selector, to the default external material family headed by `816CE17F`.

Therefore `816CE17F` is currently a **strongly inferred shared/default material candidate** for 09A, but it is not yet directly proven by locating 09A's owning parent.

`816CE17F` is a real visible material:

- VS `80AAE149`
- PS `816CE0F3`
- 8 pixel texture slots

Texture slots:

| Slot | Texture hash | Owner package |
|---:|---|---:|
| 0 | `80AACED2` | `0x0156` |
| 1 | `816CE138` | `0x0767` |
| 2 | `816CE118` | `0x0767` |
| 3 | `816CE119` | `0x0767` |
| 4 | `8166A984` | `0x0735` |
| 5 | `80AACED3` | `0x0156` |
| 6 | `8166A985` | `0x0735` |
| 7 | `80AACF1D` | `0x0156` |

Three local textures are already decoded and visually coherent:

- `816CE138`: 4096x4096 BC1, large white/gray Vex hard-surface atlas
- `816CE118`: 2048x2048 BC3, tiled dirty/rocky detail color
- `816CE119`: 2048x2048 BC5, matching tiled detail normal

## Exact D1 second UV set

Charm's D1 mesh path constructs a second detail UV set at 5x scale. Given already-transformed UV0:

- `u1 = 5 * u0`
- `v1 = 5 * v0 - 4`

This relation has now been added to the provisional glTF as `TEXCOORD_1` rather than approximating the detail normal with the base UV set.

## Provisional textured single-GLB validation

A single GLB has now been generated containing:

- model `816CE09A`
- 4,172 vertices / 5,336 triangles
- 12-joint skeleton `816CE092`
- skinning
- runtime rig `816CE095`
- animation `816CE09E` (101 frames)
- animation `816CE09D` (31 frames)
- exact D1-derived `TEXCOORD_1`
- embedded retail textures `816CE138`, `816CE118`, `816CE119`
- candidate material provenance and all eight original D1 slot hashes stored in glTF `extras`

Local output:

`/mnt/data/0767_export/816CE09A_816CE092_multi_animation_rigged_TEXTURED_INFERRED.glb`

SHA-256:

`bc3e4ca04e5b9d1bd21cf56d4074a85f206620bff6f136636213eacc0901e243`

Size: 20,889,736 bytes.

The file reloads successfully with pygltflib and contains 3 embedded images, 3 textures, 2 materials, both animations, one skin, and TEXCOORD_1 on both mesh primitives.

Important: this is an **inferred shared-material test build**, not the final proof-grade 09A material binding.

## Remaining external texture packages

The public PS4 package manifest resolves the remaining package IDs to:

- `0x0156` -> `ps4_globals_0156_0.pkg`, `ps4_globals_0156_1.pkg`
- `0x0735` -> `ps4_globals_pvp_com01_0735_0.pkg`, `ps4_globals_pvp_com01_0735_1.pkg`

Required texture hashes:

From 0156:

- `80AACED2`
- `80AACED3`
- `80AACF1D`

From 0735:

- `8166A984`
- `8166A985`

The `crypt.cohae.dev` manifest lists these filenames, but direct retrieval of `ps4_globals_0156_0.pkg` from the mirror returned HTTP 404. Another corpus/source or user-supplied package bytes are therefore required for those five slots.

## Top-level cross-package entity evidence

A complete 0767 entity-resource-array parse found explicit globals dependencies:

- entity `816CE01C` -> `80AAE3A4` (0157), local `816CE01E`, and `80AADE40` (0156)
- entities `816CE0BF` / `816CE0C0` -> local model/skeleton resources plus `80AAE1D4` (0157)

This confirms that Vex render/resource context is intentionally distributed across 0767 and global packages such as 0156/0157 rather than being self-contained in each entity-model tag.

## Next proof-grade steps

1. Acquire the 0156 and 0735 package pairs or at least whichever patch members own the five hashes above.
2. Decode the remaining five textures.
3. Determine their shader semantics from slots and retained PS shader instructions.
4. Continue searching the package graph for 09A's actual owning parent/material context.
5. Once the direct parent is found, compare its variant-0/1 materials to `816CE17F` and either confirm or reject the shared-material inference.
6. Produce the final textured rigged multi-animation GLB with no unresolved material inference.
