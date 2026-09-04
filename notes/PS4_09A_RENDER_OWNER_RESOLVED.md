# D1 PS4 `816CE09A` render owner resolved

Date: 2026-09-03/04

This note supersedes the owner *hypothesis* section of
`notes/PS4_09A_RENDER_OWNER_TRACE.md`.  Everything below is derived from the
retail PS4 package bytes and is intended to separate proven render bindings from
older inferred texture experiments.

## Result

The missing standard D1 model parent for articulated model `816CE09A` is:

- EntityResource TagHash **`816CE12B`**
- logical entry index **299** in package `0x0767`
- class **`80800861`**
- entry size **2,096 bytes**

The parent is present in the higher patch namespace exposed by both
`ps4_arch_vex_com01_0767_1.pkg` and `_4.pkg`.

Its standard model-parent discriminator chain is byte-valid:

- outer `+0x10` ResourcePointer -> target `+0x80`, class `80801A80`
- outer `+0x18` ResourcePointer -> target `+0x2A0`, class `80801A9C`
- model-parent payload starts at `+0x2A0`
- model FileHash at parent `+0x15C` = **`816CE09A`**

This resolves the previously missing ownership edge:

```text
816CE12B  EntityResource (80800861)
  +0x10 -> 80801A80
  +0x18 -> 80801A9C model parent
                 |
                 +-- Model = 816CE09A
```

A separate literal structured-payload census independently finds the little-endian
`816CE09A` hash in `816CE12B` at entry-payload offset **1020 (0x3FC)**.

## Exact external-material table

The parent has no TexturePlatesROI entries:

- `TexturePlatesROI.Count = 0`

It instead has two external-material ranges:

```text
ExternalMaterialsMap[0]
  MaterialCount      = 2
  MaterialStartIndex = 0
  Unk08              = 0

ExternalMaterialsMap[1]
  MaterialCount      = 6
  MaterialStartIndex = 2
  Unk08              = 2
```

The complete eight-entry material bank is:

```text
index 0  809C475F
index 1  809C4760
index 2  816CE240
index 3  816CE241
index 4  816CE242
index 5  816CE243
index 6  816CE244
index 7  816CE1A7
```

Charm's current D1 selector is source-confirmed as:

```text
mapEntry = ExternalMaterialsMap[VariantShaderIndex]
material = ExternalMaterials[
    mapEntry.MaterialStartIndex + (0 % mapEntry.MaterialCount)
]
```

Therefore the default visible bindings for the two `09A` geometry ranges are:

- `VariantShaderIndex = 0` -> **`809C475F`**
- `VariantShaderIndex = 1` -> **`816CE240`**

The older inferred `816CE17F` appearance is **not** the byte-proven default
binding and must not be used as the retail reconstruction.

## Exact decoded material records

All eight parent-bank hashes resolve as real PS4 D1 material class `80801AD7`.

### Variant 0 default: `809C475F`

Package ownership from the TagHash formula:

- package ID `0x00E2`
- entry index 1887

Decoded material:

```text
Material            809C475F
size                1712 bytes
Unk08               1
VS                   80AAE149
PS                   80AAE14B
VS Vector4 container FFFFFFFF
PS Vector4 container 80AAE14C
PS TFX bytecode      20 bytes
PS samplers          5
```

Pixel texture slots:

```text
slot 0  80AACCDD
slot 1  80AACCDF
slot 2  80AACC26
slot 3  80AACC28
slot 4  80AACCDD
```

The alternate material in the same variant-0 range, `809C4760`, uses the same
VS/PS and the same slots 1-3, but replaces slots 0/4 with `80AACCE0`:

```text
slot 0  80AACCE0
slot 1  80AACCDF
slot 2  80AACC26
slot 3  80AACC28
slot 4  80AACCE0
```

The `80AACC..` hashes all decode to package ID **`0x0156`**.

### Variant 1 default: `816CE240`

Package ownership:

- package ID `0x0767`
- entry index 576

Decoded material:

```text
Material             816CE240
size                 1456 bytes
Unk08                1
VS                    80AAE149
PS                    816CE0A8
VS Vector4 container FFFFFFFF
PS Vector4 container 816CE185
PS TFX bytecode       8 bytes
PS samplers           2
```

Pixel texture slots:

```text
slot 0  816CE1C5
slot 1  816CE1C5
```

All five additional materials in that six-material range use the same vertex
shader, pixel shader, and two identical texture slots.  Their material-specific
PS Vector4 containers are:

```text
816CE240 -> 816CE185
816CE241 -> 816CE186
816CE242 -> 816CE187
816CE243 -> 816CE188
816CE244 -> 816CE189
816CE1A7 -> 816CE0A9
```

Thus the evidence currently indicates that the six variant-1 alternatives
primarily differ through material constants/state rather than alternate image
assets.

## Retail package recovery is now deterministic

The final D1 PS4 corpus archive is published as split TAR volumes rather than
individual `.pkg` URLs.  Direct `/latest/<package>.pkg` requests therefore 404
even when the package is present in the manifest.

A sparse HTTP Range walk of the ten split TAR volumes recovered all three 0767
members without downloading the 49 GB corpus.

Logical split-TAR size:

- **52,701,281,792 bytes**

Retail package locations and hashes:

```text
ps4_arch_vex_com01_0767_0.pkg
  TAR header = 4,391,886,848 (0x105C6E000)
  data       = 4,391,887,360 (0x105C6E200)
  size       = 42,686,464
  SHA-256    = f2e79a11ef88d1f0e9fc65cb4c649547fa4883fb6a101955a8743611b0e68ae3

ps4_arch_vex_com01_0767_1.pkg
  TAR header = 4,434,573,824 (0x108523A00)
  data       = 4,434,574,336 (0x108523C00)
  size       = 8,278,016
  SHA-256    = 775c777601fa0e98f0b7c4c41a480babe48a75e2ceb038b6ba35391a9880757a

ps4_arch_vex_com01_0767_4.pkg
  TAR header = 4,442,852,352 (0x108D08C00)
  data       = 4,442,852,864 (0x108D08E00)
  size       = 24,576
  SHA-256    = a5fb2bf75d0a605aeb6090353557a4740b4b30c31e52667a271d0624ed3d1df3
```

The higher namespace has 594 logical entries.  All 241 structured type-16
entries were available once `_0`, `_1`, and `_4` were present.

A reusable sparse extractor now lives at:

- `tools/d1_split_tar_extract.py`

It validates Range support and TAR checksums, handles split boundaries, and
records member offsets/sizes/SHA-256 hashes.

## Current exact frontier

The render owner and material binding problem is solved.

The remaining appearance work is now narrowly defined:

1. Decode/export the five unique default texture hashes used by
   `809C475F` and `816CE240`:
   - `80AACCDD`
   - `80AACCDF`
   - `80AACC26`
   - `80AACC28`
   - `816CE1C5`
2. Decode `80AAE14C` and `816CE185` Vector4 constants and compare the six
   variant-1 constant containers.
3. Determine the channel/sampler meaning of PS `80AAE14B` and PS `816CE0A8`
   sufficiently to map the retail look into glTF PBR (while preserving the
   original shader/material hashes in extras).
4. Replace the rejected inferred texture assignment in the already-valid
   rigged + multi-animation `816CE09A` GLB.

No further material guessing is required for the two default visible parts.
