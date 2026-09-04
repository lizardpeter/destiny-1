# PS4 011C final model binding correction

Date: 2026-09-04

This is a correction checkpoint for the first D1 ROI PS4 weapon fixture.  It
supersedes the earlier working assumption that the main visible shell of
`80A39E12` binds material `80A3CD9A`.

## Byte-proven final model binding

The final `ps4_gear_weapons_011c` logical snapshot parses `80A39E12` with two
meshes.  Its LOD1 material records are:

- mesh 0, small component: `80A3D294`
- mesh 1, main shell: `80A382A6`, plus auxiliary `80AAE10B` and `80AAE10C`

`80A3CD9A` does **not** occur as a material hash in the final model payload.
The proof exporter must therefore use `80A382A6` as the native main-shell
binding unless a later, separately proven runtime substitution layer explicitly
replaces it.  No such layer is currently proven.

`80A382A6` itself is a valid material entry in package `0x011C`:

- entry index: 678 (`0x02A6`)
- class/reference: `80801AD7`
- size: 1,792 bytes
- decoded-entry SHA-256:
  `6f70c47c838343314d323e4354cd5520fcf7e4c69da82f1c79d6bb862ad4e6f`
- VS: `80A3D28E`
- PS: `80A3D145`
- VS vec4 container: `FFFFFFFF`
- PS vec4 container: `FFFFFFFF`
- PS TFX bytecode:
  `0201000002000000101000000000000000010000`
- PS sampler count: 7
- PS TextureIndex 0 -> `80AB0B74` (FileHash package `0x0158`, index `0x0B74`)
- PS TextureIndex 1 -> `80A3D4D6` (FileHash package `0x011E`, index `0x14D6`)

The old exporter binding `80A3CD9A` used the same known VS/PS pair but a
different TextureIndex-0 hash (`80A3D4CF`).  It is retained only as historical
comparison evidence until the final snapshot census is complete; it must not be
silently substituted for the model-inline material.

## Correct final LOD1 geometry census

A cross-package diagnostic corrected an earlier stale component count.  Final
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

Total final exported LOD1 triangles are therefore **2,620**.  The existing
exporter's 2,620-triangle invariant is correct even though its old main-material
constant is not.

## Remaining direct dependencies

- `80AB0B74` package `0x0158`: recovery/texture characterization in progress.
- `80A3D4D6` package `0x011E`: already known as a direct shader texture.
- `80A3D294` small-component material: exact final snapshot decode in progress.
- `80AA9D4D` package `0x0154`: small-component texture recovery in progress.

The entity texture-plate path (`80A39E17` / `80A39E19` / `80A39E1A` /
`80A39E1B`) remains independently proven and is not replaced by these direct
material textures.
