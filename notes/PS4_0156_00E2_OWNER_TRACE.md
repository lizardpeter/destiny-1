# PS4 0156 / 00E2 Vex owner trace

Date: 2026-09-04

This note records the material/render-owner investigation for D1 ROI PS4 model `816CE09A` from `ps4_arch_vex_com01_0767_0.pkg`.

## Critical correction

`816CE09A` should no longer be treated as a normal visible entity model awaiting a guessed texture assignment.

Two provisional texture bindings were visually falsified in Blender. Subsequent byte-level reverse references and comparison against `ps4_arch_vex_00e2_0.pkg` show that `816CE09A` belongs to a special `0x8080222A` **animation model bundle**, not a standard D1 entity model parent.

The trusted state remains:

- geometry extraction: proven;
- 12-bone skeleton: proven;
- skinning: proven;
- runtime rig: proven;
- animations: proven;
- treating `816CE09A` itself as the final textured game-visible Vex body: **rejected**.

The correct goal is now to identify the retail visible model using the same compatible runtime rig/control mapping and apply the decoded clips to that model.

## `ps4_globals_0156_0.pkg`

User-supplied package scanned successfully.

- package ID: `0x0156`
- version: 24
- platform: PS4 / 7
- entries: 8192
- blocks: 279
- file size: 51,275,776 bytes
- tool string: `live tool_lib test pc_x64 41345.14.06.30.2046.live 14.06.30 2046`

### Standard D1 model parents found

Scanning resident `0x80800861` EntityResources for the ordinary D1 model-parent discriminator (`Unk10 = 0x80801A80`, with nested `Unk18 = 0x80801A9C`) found these model links:

- `80AAC2A7 -> 80AAC2BD`
- `80AAC3AF -> 80AAC3B2`
- `80AAC4EB -> 80AAC4EE`
- `80AAC823 -> 80AAC871`
- `80AAC8A4 -> 80AAC9C3`
- `80AACB5C -> 80AACB60`
- `80AACF8C -> 80AACF8D`

None points to `816CE09A`, and no decoded `0156` EntityResource contains a literal `816CE09A` reference.

Therefore `0156_0` does **not** contain the ordinary owning model parent for `816CE09A`.

## Shared skeleton/runtime-control descriptors in 0156

`0156` is definitively part of the same Vex control graph.

### `80AADE40`

- entry 7744
- EntityResource
- size 736
- `Unk10` nested class: `0x8080279B`
- `Unk18` nested class: `0x80802202`
- not a standard D1 model parent
- references descriptor family around `80AADD78..80AADD81`

### Skeleton descriptor family

`80AADD86` contains 29 repeated `0x808006BD` skeleton-resource class markers.

`80AADD88` also contains `0x808006BD`.

### Runtime-rig descriptor family

`80AADD87` contains repeated `0x808008B2` runtime-rig class markers.

`80AADD8F` also contains `0x808008B2`.

The Vex entity/control resources in `0767` reference these same 0156 descriptor families.

Conclusion: `0156` is shared skeleton/runtime-control metadata, not the missing visible-model parent.

## `ps4_arch_vex_00e2_0.pkg`

User-supplied package scanned successfully.

- package ID: `0x00E2`
- version: 24
- platform: PS4 / 7
- entries: 5,451
- blocks: 601
- file size: 96,925,696 bytes
- 6 `s_entity` entries
- 130 `0x80800861` EntityResources
- 47 `s_entity_model` entries
- 11 animation clips
- 130 techniques

### Direct entity bridge from 0767 to 00E2

`809C4667` is the shared-package counterpart of the `0767` Vex entity chain.

Its resources are:

- `80AAE3A4` (package 0157)
- `809C4668` (local 00E2)
- `80AADE40` (package 0156)

This matches the global-resource pair seen from `816CE01C` in `0767`.

`809C4668` then refers to shared entities `809C466C` and `809C466D` through its nested resource graph. Those entities resolve to local resources `809C466E` and `809C466F` respectively.

None of `4668/466E/466F` is a standard model parent.

### Complete standard-model-parent census

Using the byte-proven D1 parent signature:

- `+0x64 = 0x8080080F`
- `+0x7C = 0x80801A80`
- `+0x90 = 0x80801A9C`

all 130 EntityResources were scanned.

35 ordinary D1 model parents are resident in `00E2_0`.

None points to `816CE09A`, and none of the 130 EntityResources contains a literal `816CE09A`, `816CE092`, `816CE095`, `816CE09D`, or `816CE09E` reference.

Therefore the `09A` bundle is **not owned by a standard model parent in `00E2_0`**.

## Decisive animation-bundle evidence

`816CE09A` is immediately preceded by:

- `816CE099`, class `0x8080222A`, 168 bytes

and followed by:

- raw bundle data `816CE09B`
- animation wrapper `816CE09C`
- clips `816CE09D` and `816CE09E`
- vertex/index descriptors and payloads

The same layout repeats in `00E2_0`:

- `809C4A5D` -> model `809C4A5E` -> raw data -> animation clip
- `809C4B96` -> model `809C4B97` -> raw data -> multiple clips
- `809C4EBA` -> model `809C4EBB` -> raw data -> animation clip

The `0x8080222A` wrapper for `816CE09A` contains dword `0xD3FD602F`, exactly the animation hash of clip `816CE09E`.

An equivalent 00E2 wrapper contains a different animation hash in the same field.

This is strong byte evidence that `0x8080222A` is an animation-bundle wrapper and the adjacent `s_entity_model` is part of the animation asset bundle rather than an ordinary entity render parent.

### Reverse-reference proof inside 0767

A complete aligned-dword scan of every decompressed `0767_0` entry found **zero references to `816CE09A`**.

By contrast:

- `816CE09C` explicitly references clips `816CE09D` and `816CE09E`.

This reinforces that `09A` is not locally owned through the ordinary visible-entity graph.

## Closest structural 00E2 animation-bundle counterpart

All 47 `00E2_0` models were compared by vertex count, buffer strides, index count, part count and variant pattern.

`816CE09A`:

- 4,172 vertices
- buffer strides 12 / 16
- 8,707 indices
- D1 triangle strips
- visible variants 0 and 1
- auxiliary `80AAE10B/80AAE10C` passes

Closest base-package structural counterpart:

`809C4B97`:

- 4,207 vertices
- buffer strides 12 / 16
- 5,066 indices
- D1 triangle strips
- visible variants 0..3
- same auxiliary `80AAE10B/80AAE10C` pass family
- immediately preceded by its own `0x8080222A` animation wrapper `809C4B96`

This is further evidence that both are animation-bundle models of the same broad Vex asset family.

## Proven ordinary Vex material control case

A normal visible model using the same variant/auxiliary rendering convention was identified:

- parent `809C44A5`
- model `809C47F4`

Its parent resolves:

`ExternalMaterialsMap`:

- variant 0: `(MaterialCount=2, MaterialStartIndex=0)`
- variant 1: `(MaterialCount=2, MaterialStartIndex=2)`

`ExternalMaterials`:

- `809C475F`
- `809C4760`
- `809C475F`
- `809C4760`

Both real visible materials use the same shader pair and 5 PS texture slots:

`809C475F`:

- slot 0 -> `80AACCDD`
- slot 1 -> `80AACCDF`
- slot 2 -> `80AACC26`
- slot 3 -> `80AACC28`
- slot 4 -> `80AACCDD`

`809C4760` differs only in the variant texture:

- slot 0 -> `80AACCE0`
- slot 4 -> `80AACCE0`

The shared textures resolve through `0156` headers and `0157` top-mip backing data:

- `80AACCDD`: 2048x2048 BC3 -> top mip `80AAE66A`
- `80AACCE0`: 1024x1024 BC3 -> top mip `80AAE66C`
- `80AACCDF`: 1024x1024 BC5 -> top mip `80AAE66B`
- `80AACC26`: 256x256 BC5 -> top mip `80AAE586`
- `80AACC28`: 64x64 RGBA8 cubemap, direct local data

This is the first fully byte-proven retail Vex material stack from the same rendering family. It is a control/reference, **not permission to assign these textures to `816CE09A`**.

## Patch sibling status

The public mirror manifest lists:

- `ps4_arch_vex_00e2_1.pkg`
- `ps4_arch_vex_00e2_2.pkg`
- `ps4_arch_vex_00e2_4.pkg`
- `ps4_arch_vex_com01_0767_1.pkg`
- `ps4_arch_vex_com01_0767_4.pkg`

Direct mirror retrieval of all five was attempted through GitHub Actions and every package returned HTTP 404.

Therefore these patch siblings must come from the user's package corpus if needed.

## Current next priority

Because `816CE09A` resides in package ID `0767` but has no local owner in `_0`, the highest-priority next package is now:

`ps4_arch_vex_com01_0767_1.pkg`

Then, if needed:

`ps4_arch_vex_com01_0767_4.pkg`

These are more likely than `00E2_1` to add/override the same-package EntityResource that consumes the `_0` animation bundle or maps it into a visible entity/control graph.

Separately, the long-term exporter should stop treating `0x8080222A` adjacent models as automatically final textured models. They should be labeled animation-bundle/proxy models until a visible entity/model-parent ownership path is proven.

## Explicitly rejected texture hypotheses

Do not regress to either without new byte evidence:

- material family `816CE17F` / texture `816CE138` on `816CE09A`;
- `816CE0B8/816CE0B9` via invented `0.5 * rawUV + 0.5` atlas mapping.

Both were visibly incorrect in Blender and are falsified as faithful `09A` bindings.

The clean rigged + animated GLB remains a useful **animation-bundle validation artifact**, but should not be presented as the final retail textured Vex model.
