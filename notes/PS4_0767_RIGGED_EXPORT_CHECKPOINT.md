# Destiny 1 PS4 0767 rigged-export checkpoint

Date: 2026-09-03
Package: `ps4_arch_vex_com01_0767_0.pkg`
Package ID: `0x0767`

## End-to-end result now achieved

A real retail D1 PS4 asset has been reconstructed into a single glTF/GLB containing:

- decoded model `816CE09A`
- 4,172 vertices
- 5,336 triangles after D1 triangle-strip + `0xFFFF` restart conversion
- decoded UV0 and normals
- `JOINTS_0` / `WEIGHTS_0`
- 12-joint skin from skeleton EntityResource `816CE092`
- inverse bind matrices from the retail skeleton
- runtime rig EntityResource `816CE095`
- animation `816CE09E`, hash `D3FD602F`, 101 frames
- animation `816CE09D`, hash `6FB760FF`, 31 frames (static tracks)
- both animations target all 12 joints in the same GLB

Validated combined GLB:

`816CE09A_816CE092_multi_animation_rigged.glb`

SHA-256:

`7c613d4ca28253a1c3ebadbf283a6fac8c0578868ea91c115ceff96211d963da`

## Compression solved for this package

Legacy D1 ROI PS4 blocks use Oodle 2.3/LZH and decode with `oo2core_3_win64.dll` through `liblinoodle3.so`.

Verified DLL:

- size: 894,752 bytes
- SHA-256: `682c0aad216fae443e0f9561876cfabfddaeffcd48e5990613ad2cf47c49fa62`

Blocks 0-237 decode to `0x40000`; final block 238 requires exact destination length `0x1C000`.

## Skeleton layout validated against retail bytes

D1 skeletons are not top-level `0x808006BD` table entries. They are nested in outer `0x80800861` EntityResources:

- `+0x10` ResourcePointer -> class `0x808006BD`
- `+0x18` ResourcePointer -> class `0x8080049A`

Four resident skeleton EntityResources were identified in 0767:

- `816CE06A`: 1 bone
- `816CE092`: 12 bones
- `816CE0D9`: 1 bone
- `816CE0DF`: 1 bone

The articulated model uses `816CE092`.

## Vertex skinning validated

`816CE09A` uses:

- buffer 0 descriptor `816CE09F` -> payload `816CE0A5`, stride `0x0C`
- buffer 1 descriptor `816CE0A0` -> payload `816CE0A6`, stride `0x10`
- index descriptor `816CE0A1` -> payload `816CE0A7`

For this D1 stride-12 layout:

- first 3 int16 values: SNORM position xyz
- fourth int16: rigid bone index for these vertices
- final 2 int16 values: UV

All 4,172 vertices have valid joint indices in the 12-bone skeleton. Observed used bones:

- 2: 672 vertices
- 3: 252
- 4: 424
- 6: 84
- 7: 84
- 8: 84
- 9: 742
- 10: 578
- 11: 1,252

No invalid influences.

## Primitive/index layout validated

Source index buffer:

- 8,707 uint16 values
- 704 `0xFFFF` primitive restart markers
- D1 primitive type 5 = triangle strip

Unique geometry ranges used for the first export:

- offset 0, count 926 -> 564 triangles
- offset 927, count 7,780 -> 4,772 triangles

Total: 5,336 triangles.

## Runtime rig and animations validated

Runtime rig `816CE095`:

- secondary class `0x808008B2`
- component hash `76F7A98E`
- count 12
- bone -> control map is identity 0..11
- control -> bone map is identity 0..11

Animation `816CE09E`:

- animation hash `D3FD602F`
- 101 frames
- 12 nodes / 12 rig controls
- static codec 3
- animated codec 2
- 3 animated rotation tracks
- 7 animated translation tracks

Animation `816CE09D`:

- animation hash `6FB760FF`
- 31 frames
- 12 nodes / 12 rig controls
- static codec 3
- no animated streams

`tiger-animation-parser` D1 ROI retargeting successfully generated the retail skeleton animation tracks and glTF armature.

## Material / texture frontier

The rigged GLB currently has placeholder glTF materials because the actual model materials are external:

- `80AAE10B`
- `80AAE10C`

Both TagHashes decode to package ID `0x0157`.

The public D1 PS4 package manifest resolves package `0x0157` to:

- `ps4_globals_0157_0.pkg`
- `ps4_globals_0157_1.pkg`

The public manifest server does not expose the package binaries at the obvious sibling URL (HTTP 404), and those package files are not currently available in the local corpus/connected Drive search.

Therefore original material/texture reconstruction is now blocked only on acquiring the `ps4_globals_0157` package pair (or another corpus containing those material tags), not on mesh/rig/animation reverse engineering.

## Remaining path to fully textured animated export

1. Acquire `ps4_globals_0157_0.pkg` and preferably `_1.pkg`.
2. Decode entries `0x10B` and `0x10C` (`80AAE10B`, `80AAE10C`).
3. Parse D1 material fields and shader texture bindings.
4. Recursively resolve texture TagHashes to owning packages.
5. Decode PS4 texture metadata/mips/swizzle as necessary.
6. Map D1 channels to glTF PBR approximately while retaining original hashes/semantics in extras.
7. Replace placeholder materials in the already-working GLB.
8. Add any additional compatible clips found for the same runtime-rig component.

At this point, the first asset is fully rigged and animated. The main missing fidelity layer is original materials/textures.
