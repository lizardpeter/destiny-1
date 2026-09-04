# Destiny 1 PS4 00E2 Vex render-context findings

Date: 2026-09-04
Package: `ps4_arch_vex_00e2_0.pkg`
Context target: render/material ownership of `816CE09A` from `ps4_arch_vex_com01_0767_0.pkg`.

## Why 00E2 matters

The retail PS4 manifest contains only two architecture-level Vex package families relevant to this search:

- `ps4_arch_vex_00e2_[0,1,2,4].pkg`
- `ps4_arch_vex_com01_0767_[0,1,4].pkg`

`816CE0B2` in 0767 points directly to five hashes owned by package `0x00E2`, making the 00E2 family the strongest base/shared Vex render-context dependency.

## Exact base/combatant entity correspondence

`809C4667` in 00E2 and `816CE01C` in 0767 have the same three-resource entity pattern:

- shared `80AAE3A4` from package 0157
- package-local composition resource (`809C4668` in 00E2 / `816CE01E` in 0767)
- shared `80AADE40` from package 0156

This is a byte-level cross-package correspondence, not a naming inference.

## 809C4668 / 816CE01E composition class

Both local resources are `0x80800861 EntityResource` wrappers whose nested discriminator/info classes resolve to:

- `0x8080079A`
- `0x80800610`

These resources are higher-level composition/serialization structures, not ordinary D1 model parents. Their recurring `80AAE395..39F` / `80AAE485..486` references from package 0157 were decoded and proved to be class/schema metadata records (`0x8080058A`) for the composition class, not texture or material tags.

## True D1 model-parent calibration in 00E2

All ordinary D1 model parents (`0x80801A80 -> 0x80801A9C`) resident in 00E2_0 were scanned. Example:

`809C44A5 -> model 809C47F4`

- `ExternalMaterialsMap = [(2,0,0),(2,2,0)]`
- `ExternalMaterials = [809C475F,809C4760,809C475F,809C4760]`
- `TexturePlatesROI count = 0`

The parent therefore resolves visible variant 0 and variant 1 through the `809C475F/809C4760` material family.

## Exact visible material texture bindings

`809C475F` and `809C4760` are real `0x80801AD7` techniques with vertex shader `80AAE149` and pixel shader `80AAE14B`. Their pixel texture arrays are explicit:

### 809C475F

- slot 0 -> `80AACCDD`
- slot 1 -> `80AACCDF`
- slot 2 -> `80AACC26`
- slot 3 -> `80AACC28`
- slot 4 -> `80AACCDD`

### 809C4760

- slot 0 -> `80AACCE0`
- slot 1 -> `80AACCDF`
- slot 2 -> `80AACC26`
- slot 3 -> `80AACC28`
- slot 4 -> `80AACCE0`

The texture headers are resident in `ps4_globals_0156_0.pkg`, and their streamed full-resolution backing payloads resolve into `ps4_globals_0157_0.pkg`.

Decoded exact retail textures:

- `80AACCDD`: 2048x2048 BC3 -> backing `80AAE66A` (4 MiB)
- `80AACCE0`: 1024x1024 BC3 -> backing `80AAE66C` (1 MiB)
- `80AACCDF`: 1024x1024 BC5 -> backing `80AAE66B` (1 MiB)
- `80AACC26`: 256x256 BC5 -> backing `80AAE586` (64 KiB)
- `80AACC28`: 64x64 RGBA8, array size 6/cubemap-like direct payload `80AACC29`

These are the first fully byte-proven Vex architecture material->texture chains in the current reversal.

## Special model-cluster correspondence

The `809C4B97` cluster in 00E2 is structurally very close to the `816CE09A` cluster in 0767.

00E2 cluster:

- `809C4B90`: skeleton EntityResource (`808006BD -> 8080049A`), 8 bones
- `809C4B91`: `808020BF -> 808029D2`
- `809C4B92`: `80802B92 -> 808020BB`
- `809C4B93`: runtime rig (`808008B2 -> 8080099B`)
- `809C4B94`: composition (`8080079A -> 80800610`)
- `809C4B95`: `80802C0E`
- `809C4B96`: `8080222A`
- `809C4B97`: entity model
- `809C4B98`: Havok `hk_2012.2.0-r1` blob
- `809C4B99/9A/9B`: animation clips

0767 cluster:

- `816CE092`: skeleton EntityResource, 12 bones
- `816CE093`: `808020BF -> 808029D2`
- `816CE094`: `80802B92 -> 808020BB`
- `816CE095`: runtime rig (`808008B2 -> 8080099B`)
- `816CE096`: combatant-specific `80802465 -> 80802955`
- `816CE097`: composition (`8080079A -> 80800610`)
- `816CE098`: combatant-specific `80802397 -> 80802818`
- `816CE099`: `8080222A`
- `816CE09A`: entity model
- `816CE09B`: Havok `hk_2012.2.0-r1` blob
- `816CE09C`: `80802C0E`
- `816CE09D/9E`: animation clips

The base and combatant clusters therefore share the same core skeleton/control/runtime-rig/composition/animation architecture, while 0767 adds combatant-specific control resources and expands the skeleton from 8 to 12 bones.

## Geometry fingerprint

`809C4B97` uses the same exact buffer-stride family as `816CE09A`:

- 4B97 buffer0: 50,484 bytes / stride 12 = 4,207 vertices
- 4B97 buffer1: 67,312 bytes / stride 16 = 4,207 vertices
- 09A buffer0: 50,064 bytes / stride 12 = 4,172 vertices
- 09A buffer1: 66,752 bytes / stride 16 = 4,172 vertices

The 35-vertex difference is strong evidence that these are closely related articulated Vex submodel families, though they are not byte-identical rigs (8 vs 12 bones).

## Important negative result: no parent in _0

An exhaustive scan of every resident structured type-16 entry in `ps4_arch_vex_00e2_0.pkg` found **zero literal references to model `809C4B97`**. The same scan successfully found normal parent `809C44A5 -> 809C47F4`, proving the method works when an ordinary parent is resident.

Other special animation-cluster models such as `809C4809`, `809C4974`, and `809C4EBB` likewise have no normal model-parent backlink in `_0`.

This strongly supports a patch-sibling ownership model: geometry/model bytes may reside in `_0` while owning/render-context resources are present only in `_1/_2/_4`.

That is consistent with the project's earlier D1 package rule that higher patch siblings can carry refs/ownership even when `_0` carries the payload bytes.

## Opaque blob correction

`816CE09B` and `809C4B98` both begin with the same Havok serialization marker/string:

`hk_2012.2.0-r1`

They are therefore Havok animation/physics serialization payloads, not hidden material tables.

## Current highest-value next packages

For the actual target `816CE09A`, highest priority is now:

1. `ps4_arch_vex_com01_0767_1.pkg`
2. `ps4_arch_vex_com01_0767_4.pkg`

because a later 0767 patch sibling is the most direct place for the missing owner/ExternalMaterialsMap of `816CE09A`.

For validating the base 00E2 special-model path:

3. `ps4_arch_vex_00e2_1.pkg`
4. `ps4_arch_vex_00e2_2.pkg`
5. `ps4_arch_vex_00e2_4.pkg`

Do not attach another guessed texture set to 09A before resolving that patch-sibling render context.
