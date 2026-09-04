# PS4 weapon 011C first extraction fixture

Date: 2026-09-04

This note records the first proof-oriented Destiny 1 ROI PS4 weapon extraction
fixture.  It is intentionally conservative: rigid attachment, geometry,
materials, texture plates and animation ownership are recorded separately so a
portable GLB cannot silently redefine native Tiger semantics.

## Archive package families

### `ps4_gear_weapons_011c`

Logical TAR members recovered from the final PS4 archive:

| member | TAR header | size | SHA-256 |
|---|---:|---:|---|
| `_0` | `0x43779C800` | 28,882,944 | `e56205adcb4eba2cb586f6cda23712cf6c4a43dfa7cc164370d5965dac65ba3e` |
| `_1` | `0x439328200` | 5,388,288 | `d5b1be75baef7031819b7c12a78cd7b4f8da1f886a914a7ab77e8e06bfceb480` |
| `_2` | `0x43984BC00` | 1,351,680 | `83a94bcd97072eeac6eaa19e2fccc00282adff7dba978b84104f1fcc059387ff` |
| `_3` | `0x439995E00` | 268,288 | `8a3031f4e993ec6776e7ad347aa503ca9720aa4ad0152ed46184a778c39045d2` |
| `_5` | `0x4399D7800` | 184,320 | `bb5db7a5fb4846f5082ab34d620f5e69db8fd19f551461ab3c377297d7d3c993` |

### `ps4_gear_weapons_011e`

This family supplies shared weapon materials and texture-plate source textures.

| member | TAR header | size | SHA-256 |
|---|---:|---:|---|
| `_0` | `0x439A04A00` | 325,689,344 | `dac0ae5312d88bfea7d2e8ab5fbff3c3b5cf9707c1bc5158a66ac1138989a6f9` |
| `_1` | `0x44D09EC00` | 23,506,944 | `13cb2aa34231b00e6b973379e464920c3e38af5099674bb3b043861d750b0b10` |
| `_2` | `0x44E709E00` | 7,139,328 | `52af78a3568017bfbe9949f7e02d7eefc01a5c65b2fecaf896f6198c5d1aebf9` |
| `_3` | `0x44EDD9000` | 540,672 | `593b7a38bc7a58af3f1071e2b426de209e4a6f920561e038fd07df0a9e7b99cf` |
| `_5` | `0x44EE5D200` | 208,896 | `6c9166bc4ce539d83db41bf5521edd02af9e5cb05ee195b1110ef8215dec6923` |

A physical `_N` member is **not** an independent logical package namespace.
Entry/block tables are snapshots/overrides and block `patch_id` selects the
physical sibling containing bytes.  Do not merge `_0/_1/...` as independent
TagHash dictionaries and reject changed duplicates.  A durable
`LogicalPackageReader` remains required.

## Coherent weapon cluster

The first fixture is centered on:

- model: `80A39E12` (`s_entity_model`, class `80801AB5`)
- normal model parent EntityResource: `80A39E0F`
- skeleton: `80A39DF2`
- runtime rig: `80A39DF1`
- animation clips: `80A39DF6` through `80A39E01` (12 clips)

The parent `80A39E0F` embeds `80A39E12`, has one `TexturePlatesROI` record and
has no external material bank.  This exercises a different render-binding path
from the solved Vex `816CE09A` fixture.

## Geometry

`80A39E12` is 944 bytes and contains two meshes.

### Main weapon shell

- 2,500 vertices
- vertex buffer 0: `80A39E13 -> 80A39E15`, 20,000 bytes, stride 8
- vertex buffer 1: `80A39E14 -> 80A39E16`, 60,000 bytes, stride 24
- indices: `80A39E18 -> 80A39E1C`, 8,856 bytes, uint16
- primitive type 5: triangle strip with `0xFFFF` restart

Four physical index ranges are repeated under three inline material records:

- `0 / 113`
- `114 / 2015`
- `2130 / 109`
- `2240 / 2188`

Visible material: `80A3CD9A`.
Repeated `80AAE10B` / `80AAE10C` records match the already-established
auxiliary/no-pixel-shader family and must not be emitted as duplicate visible
geometry.

### Small component

- 28 vertices
- `80A39E1D -> 80A39E1E`, 224 bytes
- `80A39E1F -> 80A39E21`, 560 bytes
- `80A39E20 -> 80A39E22`, 72 bytes of indices
- one 36-index strip
- material `80A3D294`

## Vertex formats

### Main buffer 0, stride 8

The first three int16 values are SNORM position.  The fourth int16 is zero for
all 2,500 vertices.  Therefore this shell does **not** use the Vex fixture's
rigid-bone-index word and must not be exported with invented skin weights.

### Main buffer 1, stride 24

Current byte-proven layout:

```text
int16[0:2]   UV
int16[2:6]   padded normal (xyz + pad)
int16[6:10]  tangent (xyz + fourth component)
int16[10:12] unresolved final pair
```

The unresolved final pair is `0x3E66, 0x3E66` for every main-shell vertex.
It is retained as unknown rather than given a guessed semantic.

`tools/d1_entity_model_export.py` now supports primitive type 5/restart and the
24-byte stream.

## Player rig + rigid weapon attachment

The 73-node skeleton `80A39DF2` is not a 73-bone deforming firearm.  Nodes
0-71 are the standard player skeleton.  Node 72 has hash `C410084A`, identified
by the public Destiny animation dictionary as the weapon `Pedestal`.

Proven hierarchy:

```text
Hand.R
  -> Grip.R                 (bone 24)
       -> Weapon Pedestal   (bone 72, hash C410084A)
```

Runtime rig `80A39DF1` maps:

- `Grip.R`: bone 24 -> control 2
- weapon Pedestal: bone 72 -> control 70
- control 70 -> bone 72

Therefore the correct portable model is a **rigid weapon node parented under
weapon Pedestal**, not a shell skinned to 73 joints.

All 12 clips decode and retarget through the 73-node rig using the pinned public
`tiger-animation-parser` commit
`b9fdc3a43dd28118113275624fcc9054b75855f4`.

Frame counts:

- `80A39DF6` 75
- `80A39DF7` 19
- `80A39DF8` 38
- `80A39DF9` 22
- `80A39DFA` 19
- `80A39DFB` 19
- `80A39DFC` 31
- `80A39DFD` 23
- `80A39DFE` 49
- `80A39DFF` 32
- `80A39E00` 2
- `80A39E01` 20

Motion evidence is split between `Grip.R` and the child weapon Pedestal.  For
example `80A39DF6` leaves `Grip.R` static while moving the weapon Pedestal,
whereas `80A39DFF` has strong `Grip.R` motion while the weapon Pedestal is
locally static.  Both nodes are therefore semantically required.

## Main material cross-package dependency

Visible main-shell material `80A3CD9A` resolves to package ID `0x011E`, entry
3482.  From the valid `011e_0` table:

- class `80801AD7`
- size 1,792
- VS `80A3D28E`
- PS `80A3D145`
- no PS vector4 container
- PS TextureIndex 0 -> `80A3D4CF`
  - 128x128 BC1 cubemap, six faces
- PS TextureIndex 1 -> `80A3D4D6`
  - 128x128 BC1 2D

These direct material textures are not substitutes for the entity texture
plates; preserve both dependency sets in provenance.

The small-component material `80A3D294` uses `80AA9D4D`, whose FileHash points
to package ID `0x0154`.  That dependency is still to be recovered.

## Exact TexturePlatesROI structure

Reusable probe: `tools/d1_texture_plate_probe.py`.

Charm source confirms the D1 path:

- ROI record +0x28 -> texture-plate header (`3C1C8080`, FileEntry reference `80801C3C`)
- header +0x24 AlbedoPlate
- +0x28 NormalPlate
- +0x2C GStackPlate
- each plate is `47018080` / FileEntry reference `80800147`
- each 0x14-byte transform is FileHash texture + int32 translation XY + int32 scale XY

For parent `80A39E0F`:

- texture-plate header `80A39E17`
- albedo plate `80A39E19`
  - source `80A3D844` (package `0x011E`, entry 6212)
  - translation `[0, 768]`
  - scale `[1280, 1280]`
- normal plate `80A39E1A`
  - source `80A3D845` (entry 6213)
  - same placement
- gstack plate `80A39E1B`
  - source `80A3D846` (entry 6214)
  - same placement

All three resulting plates are 2048x2048.  Each source occupies exactly the
rectangle x `[0,1280)`, y `[768,2048)`.

Reusable compositor: `tools/d1_texture_plate_compose.py`.  Proof mode refuses
implicit source resampling.

## Native UV transform correction

The plate geometry gives a strong independent check of the D1 UV transform.
For the 2,500-vertex main shell:

```text
texcoord_scale       = [0.49747315049, 0.49747315049]
texcoord_translation = [0.49812737107, 0.73159074783]

native_u = snorm_u * scale_x + translation_x
native_v = snorm_v * scale_y + translation_y
```

Observed native UV bounds are approximately:

- U `0.000654 .. 0.623350`
- V `0.377376 .. 0.995092`

In a 2048 plate that is approximately:

- x `1.34 .. 1276.62`
- y `772.87 .. 2037.95`

Those bounds almost exactly occupy the byte-proven plate placement rectangle
x `0..1280`, y `768..2048`.

Therefore the **native D1 model UV transform does not contain a V flip**.  Any
V inversion performed for an interchange library/image convention is a
portable conversion and must not be described as native Tiger semantics.

## Current export frontier

1. Resolve the 011E same-family snapshot/patch-table behavior cleanly enough to
   export `80A3D844/45/46` without treating physical `_N` files as separate
   logical namespaces.
2. Compose the three exact 2048 plates and validate that no resampling is
   required.
3. Produce a static GLB for both `80A39E12` meshes using strip/restart support.
4. Attach the rigid weapon node to bone 72 `C410084A` and include all 12 proven
   animations without assigning fake JOINTS/WEIGHTS to the shell.
5. Resolve the small-mesh `0x0154` texture/material dependency.
6. Preserve model/parent/material/shader/direct-texture/plate/source/rig/clip
   provenance in glTF `extras`; use portable PBR only as an explicitly labeled
   approximation.
