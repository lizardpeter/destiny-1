# PS4 011C final model binding correction

Date: 2026-09-04

This is a correction checkpoint for the first D1 ROI PS4 weapon fixture. It
supersedes the earlier working assumption that the main visible shell of
`80A39E12` binds material `80A3CD9A`.

## Byte-proven final model binding

The final `ps4_gear_weapons_011c` logical snapshot parses `80A39E12` with two
meshes. Its LOD1 material records are:

- mesh 0, small component: `80A3D294`
- mesh 1, main shell: `80A382A6`, plus auxiliary `80AAE10B` and `80AAE10C`

`80A3CD9A` does **not** occur as a material hash in the final model payload.
The proof exporter must therefore use `80A382A6` as the native main-shell
binding unless a later, separately proven runtime substitution layer explicitly
replaces it. No such layer is currently proven.

### Final main material `80A382A6`

`80A382A6` is a valid material entry in package `0x011C`:

- entry index: 678 (`0x02A6`)
- class/reference: `80801AD7`
- size: 1,792 bytes
- decoded-entry SHA-256:
  `6f70c47c838343314d323e4354cd5520fcf7e4c69da82f1c79d6bb862ad4e6f`
- VS: `80A3D28E`
- PS: `80A3D145`
- VS vec4 container: `FFFFFFFF`
- PS vec4 container: `FFFFFFFF`
- PS TFX bytecode: 78 bytes:
  `490047214901472249024723490347244904472549054726490647273f1b0046223f1b0146233f190046243f190146253f190246263d1f00420e3d1b03420f3d1b0142103d1b0242113d1b044212`
- PS sampler count: 7
- PS TextureIndex 0 -> `80AB0B74` (FileHash package `0x0158`, index `0x0B74`)
- PS TextureIndex 1 -> `80A3D4D6` (FileHash package `0x011E`, index `0x14D6`)

The old exporter binding `80A3CD9A` used the same VS `80A3D28E`, PS
`80A3D145`, TFX bytecode, and seven sampler records, but a different
TextureIndex-0 hash (`80A3D4CF`). Its snapshot census is decisive:

- `011E_0`: valid 1,792-byte material, SHA-256
  `ffa459e20e3aa48ab374e4a5ac9a488f7c9d730be316ec7af1c0f90cca46459a`
- `011E_1`: same valid material / same SHA-256
- `011E_2`, `_3`, `_5`: tombstoned (`reference=FFFFFFFF`, type/subtype 0/0,
  file size 0)

So `80A3CD9A` is historical/stale in the final package state and must not be
silently substituted for the model-inline `80A382A6`.

### Final small-component material `80A3D294`

The 28-vertex component uses `80A3D294` from the final `011E_5` snapshot:

- declared/actual material size: 1,328 bytes
- VS: `80AAE149`
- PS: `80AA9D63`
- VS vec4 container: `FFFFFFFF`
- PS vec4 container: `80AAE1E1`
- PS TFX bytecode: 4 bytes `49004721`
- PS sampler count: 1
- sampler tag: `80AAE1D5`
- PS TextureIndex 0 -> `80AA9D4D`

The exact `80AA9D63` instruction dataflow, `80AAE1E1` constants and
`80AAE1D5` native sampler descriptor are being traced separately before core
glTF PBR semantics are assigned.

## Correct final LOD1 geometry census

A cross-package diagnostic corrected an earlier stale component count. Final
LOD1 geometry for `80A39E12` is:

### Mesh 0 — small component

- vertices: 28
- triangles: 16
- connected components: 2
- range: index offset 0, count 36
- material: `80A3D294`
- Tiger-model-space LOD1 bbox:
  - min `[-0.010091308556886806, -0.7685507642281186, -0.013777271911498676]`
  - max `[0.004982827722874994, -0.7471769253930449, 0.008952042325450767]`

### Mesh 1 — main shell

- vertices: 2,500
- triangles: 2,604
- connected components: 2
- visible LOD1 ranges:
  - offset 114, count 2,015 -> 1,193 triangles
  - offset 2,240, count 2,188 -> 1,411 triangles
- each range carries `80A382A6` plus auxiliary `80AAE10B` / `80AAE10C`
- Tiger-model-space LOD1 bbox:
  - min `[-0.0873924091167519, -0.5662020376878294, -0.11292465937112696]`
  - max `[0.13001584411137054, 0.09447768176331646, 0.19802221187969895]`

Total final exported LOD1 triangles are therefore **2,620**. The existing
exporter's 2,620-triangle invariant is correct even though its old main-material
constant is not.

## Resolved direct texture dependencies

### `80AB0B74` — final main-material TextureIndex 0

Resolved in `ps4_globals_0158` final logical snapshot:

- header entry: package `0x0158`, index 2932
- type/subtype: `32:2` (`TextureCubeHeader`)
- reference/backing: `80AB0B75`
- header size: 60 bytes
- header SHA-256:
  `481cc1d84c358ae94b1192ae69992f2e2c48ddd9145d0258b47aa3ec9d847950`
- dimensions: 128 x 128 x 6 faces
- PS4 surface format: `0x23` = BC1
- top-level backing bytes: 49,152
- face-wise PS4 Morton unswizzle succeeds for all six faces
- output DDS SHA-256 values:
  - face0 `d1816657a85fc61f11c9f8ed4f7b04608ee48f835b7bd12b7e99cc7f4b2d68c8`
  - face1 `0b0e5f09483e984828aa38fdfaee12ab75531dab78a6bc6a80dd013c62746f25`
  - face2 `c0102e07b5222362e2b75ee0a5964a4f6245de0e42658a51a91429ebf2358be0`
  - face3 `24b6feac2141fd769b2aa832f64b083014978b29028c6479f3e64c71bda1ca04`
  - face4 `09632fbaaa24f38d9da14168520913eebbc9d9743e69af0f31dd0845fc6d95fe`
  - face5 `ee965ca0f841fcdf0e6c8a8000ef19dc7e12fdfc383900c9b8b08bd2d8b8e157`

Visual decoding shows a low-frequency grayscale environment/reflection-like
cube. That visual description is not promoted to a native shader semantic;
resource-table/instruction provenance remains authoritative.

Final `ps4_globals_0158` archive members recovered:

| member | TAR header | data | size | SHA-256 |
|---|---:|---:|---:|---|
| `_1` | `0x47AFAAA00` | `0x47AFAAC00` | 16,465,920 | `1264074ace241e069d26ffcbb96bce2a4379b283ae0ae61adf0e1e6262f83e50` |
| `_2` | `0x47BF5EC00` | `0x47BF5EE00` | 121,954,304 | `a912b07555ec00a982b1b57b3b729d751d80376142bd6d11adea56146d8a4c24` |
| `_3` | `0x4833ACE00` | `0x4833AD000` | 5,095,424 | `991aed958470557098c0b05e42a9442f228cae1f0a0c0cdfee85211d750e57a7` |
| `_4` | `0x483889000` | `0x483889200` | 4,018,176 | `758bf5ee43fd5545b0bdf8a5e36ce77c95ca2cffeae55eaf991ae98dc752f970` |
| `_5` | `0x483C5E200` | `0x483C5E400` | 3,821,568 | `03e3b08129cd2bfe64024342e8cfe3b8e0975850d5f440741cb0e50f9e56c158` |
| `_6` | `0x484003400` | `0x484003600` | 122,880 | `e498d678bd6ba688b5905eec1aa0124c9fab9532120a310c90053e087ceb7cb3` |

### `80AA9D4D` — small-component TextureIndex 0

Resolved in `ps4_globals_0154` final logical snapshot:

- header entry: package `0x0154`, index 7501
- type/subtype: `32:1` (`Texture2DHeader`)
- reference/backing: `80AA9D4E`
- header size: 60 bytes
- header SHA-256:
  `5ab1363e54c1a426916a3887f35211f6c9b1d694118965af9d1a2867d0d94b99`
- dimensions: 1024 x 1024
- PS4 surface format: `0x25` = BC3
- recovered backing bytes before top-level crop: 354,304
- PS4 unswizzle succeeds and emits a valid 1024 x 1024 DDS
- DDS SHA-256:
  `eb03f1d8202cb75dbd07ce9964d4a55353058e50473756bb286a9b048bc95647`

Decoded pixels reveal a densely packed sign/decal/marking atlas with alpha and
large unused transparent regions. This is useful portable-export evidence, but
the exact PS `80AA9D63` dataflow still determines how the atlas is consumed.

Final `ps4_globals_0154` archive members recovered:

| member | TAR header | data | size | SHA-256 |
|---|---:|---:|---:|---|
| `_0` | `0x45B642200` | `0x45B642400` | 82,126,848 | `d2643f2c4a871faab61b0f6f2d56d2d9e0fda46aeb8d2c698ffcd1aba998693f` |
| `_1` | `0x460494C00` | `0x460494E00` | 14,962,688 | `f02c517b4c901d5367e392a6bef42684bfa3fcbb62551e0e50d732e19efd6f14` |
| `_2` | `0x4612D9E00` | `0x4612DA000` | 7,340,032 | `9527bd96574e7a6f1d475e4ac9aa81eb4951f0fd4941116a3ecf004df0a282f7` |
| `_3` | `0x4619DA000` | `0x4619DA200` | 163,840 | `110ec15600b24dee67c16764c89b7c4dc770bbc483ff36e2d0314364ee5ceadd` |
| `_4` | `0x461A02200` | `0x461A02400` | 157,696 | `775edd3533833849968c86fc98fe7a8d41a47767ff5792e3cb6915591c553a04` |
| `_5` | `0x461A28C00` | `0x461A28E00` | 157,696 | `05f94e8303974e5776f2fd0c4d544a940a9faa48b3b3dec99258e1aff5aa21bd` |

## Logical-package guardrail

Physical `_N` siblings are snapshots/block owners of one logical package. They
must not be supplied to `d1_texture_export.py` as separate cross-package
`--dependency-pkg` namespaces. Doing so creates artificial duplicate TagHashes.
The final logical snapshot resolves historical block bytes through `patch_id`
and sibling paths by itself.

## Still-proven independent plate path

The entity texture-plate path (`80A39E17` / `80A39E19` / `80A39E1A` /
`80A39E1B`) remains independently proven and is not replaced by these direct
material textures. Main-shell core glTF PBR continues to use the exact composed
albedo/normal plates while direct shader textures remain native provenance until
their shader roles are proven.
