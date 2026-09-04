# PS4 0156 scan and 00E2 Vex owner trace

Date: 2026-09-04

This note records the material/render-owner investigation for the articulated D1 ROI PS4 model `816CE09A` from `ps4_arch_vex_com01_0767_0.pkg`.

## Why this exists

The mesh, 12-bone skeleton, skinning and animation for `816CE09A` are already byte-proven and export correctly. Two provisional texture bindings were visually falsified in Blender. The remaining task is to locate the actual D1 model-parent/render context so `VariantShaderIndex=0/1` can resolve through the retail `ExternalMaterialsMap` rather than by guessed texture adjacency.

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

## What 0156 does contain for the 09A cluster

The package contains multiple resource/control descriptors referenced directly by the 0767 skeleton/runtime-rig/control cluster.

### `80AADE40`

- entry 7744
- EntityResource
- size 736
- `Unk10` nested class: `0x8080279B`
- `Unk18` nested class: `0x80802202`
- not a standard D1 model parent
- references descriptor family around `80AADD78..80AADD81`

### Skeleton descriptor family

`80AADD86` is a large descriptor payload containing 29 repeated nested `0x808006BD` skeleton-resource class markers.

`80AADD88` also contains `0x808006BD`.

These hashes are referenced by the same 12-bone skeleton/control cluster around `816CE092`.

### Runtime-rig descriptor family

`80AADD87` contains repeated `0x808008B2` runtime-rig class markers.

`80AADD8F` also contains `0x808008B2`.

These are associated with the runtime rig around `816CE095`.

### Other direct 0156 dependencies around the cluster

The local 0767 control resource `816CE098` references `80AADD3F..80AADD42` in package `0156`.

The Vex entity `816CE01C` references `80AADE40` in package `0156`.

Conclusion: `0156` is definitively part of the shared Vex skeleton/runtime-control metadata graph, but it is **not yet the missing retail render/model parent**.

## Strongest next owner lead: package `0x00E2`

The retail PS4 package manifest was filtered for all package names containing `vex`.

The architecture-level Vex package families are effectively:

- `ps4_arch_vex_00e2_0.pkg`
- `ps4_arch_vex_00e2_1.pkg`
- `ps4_arch_vex_00e2_2.pkg`
- `ps4_arch_vex_00e2_4.pkg`
- `ps4_arch_vex_com01_0767_0.pkg`
- `ps4_arch_vex_com01_0767_1.pkg`
- `ps4_arch_vex_com01_0767_4.pkg`

The remaining Vex-named packages in the manifest are PvP Vex-tube activity/destination packages, not general architecture packages.

This matters because local resource `816CE0B2`, immediately following the `816CE09A` model/buffer/rig cluster in `0767`, references five hashes in package `0x00E2`:

- `809C55DB`
- `809C55DD`
- `809C55DC`
- `809C55DE`
- `809C4667`

Package ID `0x00E2` resolves exactly to the shared `ps4_arch_vex_00e2_*` family above.

This is now the strongest evidence-based render-owner/material-context candidate for `816CE09A`.

## Also implicated but lower-priority for rendering

The same 09A neighborhood contains control references into:

- package `0x0158` (`80AB02E3`, `80AB02E5`, `80AB02F4..80AB02F8`)
- package `0x0157` (`80AAE396..80AAE39F`)
- package `0x0156` (`80AADD3F..80AADD42` and skeleton/rig descriptors)
- package `0x04E4` (repeated `811C9DC5`)

The PS4 manifest lists `ps4_globals_0158_1.pkg` but no `_0` member. Based on local class context, these `0158` links currently look more like animation/control data than the main material owner, so `00E2` has higher priority.

## Required next proof

Obtain `ps4_arch_vex_00e2_0.pkg` first, then scan it for:

1. literal `816CE09A` references;
2. standard D1 model-parent resources (`0x80801A80` / `0x80801A9C`);
3. backlinks from `809C55DB/DD/DC/DE` and `809C4667`;
4. texture-plate header class `0x80801C3C` and plate class `0x80800147` associated with the model parent;
5. `ExternalMaterialsMap` entries corresponding to `VariantShaderIndex 0` and `1`;
6. exact visible material hashes and their pixel texture slots.

Only after this mapping is byte-proven should another textured `816CE09A` GLB be produced.

## Explicitly rejected hypotheses

Do not regress to either of these without new byte evidence:

- assigning material family `816CE17F` / texture `816CE138` to `816CE09A`;
- assigning `816CE0B8/816CE0B9` as atlas plates via invented `0.5 * rawUV + 0.5` mapping.

Both produced visibly incorrect Blender output and are falsified as faithful 09A bindings.

The clean rigged + animated GLB remains the trusted asset while material-owner reversal continues.
