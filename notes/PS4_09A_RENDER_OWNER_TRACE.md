# D1 PS4 `816CE09A` render-owner trace

Date: 2026-09-03/04

Target articulated model: `816CE09A` in `ps4_arch_vex_com01_0767_0.pkg`.

This note records only byte-proven findings and explicitly marks calibration-only hypotheses so incorrect texture bindings are not reintroduced.

## Known target state

`816CE09A` is already reconstructed as a valid rigged + animated GLB using:

- model `816CE09A`
- skeleton EntityResource `816CE092` (12 bones)
- runtime rig EntityResource `816CE095` (12 controls, identity bone/control mapping)
- animations `816CE09D` and `816CE09E`

The remaining unsolved problem is the exact retail render context for the two visible mesh parts whose `VariantShaderIndex` values are 0 and 1.

The inline materials `80AAE10B` and `80AAE10C` are not the ordinary visible surface passes: both decode with a vertex shader but `PixelShader = FFFFFFFF` and empty direct texture arrays. Charm's D1 part loader would skip such a pass.

## `ps4_globals_0156_0.pkg`

`0156_0` was supplied and fully scanned for the target chain.

It definitely contains shared Vex rig/control infrastructure referenced by the `0767` entity/skeleton/runtime-rig graph, including the `80AADD86/87/88/8F` and `80AADE40` families.

A complete structured-tag scan was then performed:

- all 64 blocks containing type-16 structured entries were decompressed
- all structured payloads were searched for literal TagHashes:
  - `816CE09A`
  - `816CE092`
  - `816CE095`

Result: **zero occurrences**.

Therefore `0156_0` is shared rig/control infrastructure, not the direct render/model owner for `816CE09A`.

## `ps4_arch_vex_00e2_0.pkg`

Package `00E2` is the shared/base Vex architecture package family.

The strongest cross-package structural counterpart was found:

`00E2:809C4667` is an `s_entity` with exactly these three EntityResources:

- `80AAE3A4` (`0157`)
- `809C4668` (local `00E2`)
- `80AADE40` (`0156`)

This is byte-for-byte the same outer dependency pattern as `0767:816CE01C`:

- `80AAE3A4` (`0157`)
- `816CE01E` (local `0767`)
- `80AADE40` (`0156`)

So `809C4668` is the base-Vex counterpart of the combatant-specific `816CE01E` resource.

### Counterpart resource structure

Both `809C4668` and `816CE01E` share the same first three nested ResourcePointer classes:

- `+0x08` -> class `8080043F`
- `+0x10` -> class `8080079A`
- `+0x18` -> class `80800610`

The combatant resource `816CE01E` still directly references `00E2:809C466D`, proving that the combatant package reuses the shared Vex resource graph rather than replacing it wholesale.

`809C466C` and `809C466D` are shared Vex entities with:

- `809C466C -> 80AAE3A4 + 809C466E`
- `809C466D -> 80AAE3A4 + 809C466F`

`809C466E/466F` remain in the `8080079A -> 80800610` visual/control family and reference local effect/light-style resources `809C4672..467A`; they are not standard D1 model parents.

### Complete standard-parent census

All 130 resident `0x80800861` EntityResources in `00E2_0` were parsed after separately decompressing all 55 blocks that contain type-16 structured tags.

35 resources are standard D1 entity-model parents (`Unk10 class 80801A80`, `Unk18 class 80801A9C`). Their embedded model hashes were enumerated.

**None embeds `816CE09A`.**

A complete structured-tag literal backlink scan for:

- `816CE09A`
- `816CE092`
- `816CE095`

returned **zero hits** across `00E2_0`.

Therefore `00E2_0` is not the direct owner of the combatant model.

## Base Vex model/material calibration around `809C4656/4657`

Immediately before the `4667/4668` resource chain, `00E2` contains a standard parent/model pair:

- parent EntityResource `809C4656`
- embedded model `809C4657`

This is useful as calibration only.

`809C4656` has:

- `ExternalMaterialsMap` count 2
- variant 0 map: `(MaterialCount=35, MaterialStartIndex=0, Unk08=0)`
- variant 1 map: `(MaterialCount=35, MaterialStartIndex=35, Unk08=0)`
- `ExternalMaterials` count 70
- no `TexturePlatesROI` entries

Charm's current D1 selector uses the first material in each map bank (`MaterialStartIndex + 0 % MaterialCount`). Therefore this base parent resolves:

- variant 0 -> `80AD2899`
- variant 1 -> `80AD289E`

Those material hashes belong to package ID `0x0169`, whose retail package names are:

- `ps4_globals_pvp_0169_0.pkg`
- `ps4_globals_pvp_0169_1.pkg`
- `ps4_globals_pvp_0169_2.pkg`

**Important:** this material family is *not yet proven to apply to `816CE09A`*. `809C4657` is geometrically different (small 48-index primitive) and there is no proven ownership edge from `09A` to parent `809C4656`. Do not use `80AD2899/80AD289E` for another textured `09A` GLB unless a later package proves the shared render-parent relationship.

## `0157` selector branch is not the final material bank

The repeatedly referenced `0157` records `80AAE395..80AAE3A3` are class `8080058A` selector/descriptor records, not D1 materials.

`80AAE3A4` is an EntityResource that nests other selector/configuration classes (`80800660`, `80800617`). This branch appears to be shared appearance/configuration metadata but is not itself the final visible shader-material table.

## Current strongest owner hypothesis

After complete scans of:

- `0767_0` resident entries
- `0157_0`
- `0157_1` patch resources
- `0156_0` structured entries
- `00E2_0` structured entries

no standard parent or literal backlink to `816CE09A` has been found outside the model's own package entry.

`0767_0` contains only 424 entries, while higher patch siblings in D1 can expand a logical package to the full 8192-entry namespace (observed directly with `0157_1`).

Therefore the strongest current hypothesis is that the actual `816CE09A` model parent / render context is introduced or patched in one of the higher `0767` package members, especially:

1. `ps4_arch_vex_com01_0767_1.pkg`
2. `ps4_arch_vex_com01_0767_4.pkg`

These should be searched before applying any further texture mapping to `09A`.

## Next deterministic test

For each available `0767` patch sibling:

1. parse the full logical entry table
2. identify all `0x80800861` EntityResources
3. parse ResourcePointers
4. find `Unk10 class 80801A80` + `Unk18 class 80801A9C`
5. read parent model at `parent + 0x15C`
6. locate an embedded `816CE09A`
7. decode `ExternalMaterialsMap[0]` and `[1]`
8. decode `TexturePlatesROI`
9. resolve exact material/texture hashes
10. only then rebuild the textured rigged GLB

The previously generated `TEXTURED_INFERRED` and B8 texture-plate candidate exports are rejected as retail appearance reconstructions. Keep only the clean rigged+animated GLB as the trusted export baseline until the render owner is byte-proven.
