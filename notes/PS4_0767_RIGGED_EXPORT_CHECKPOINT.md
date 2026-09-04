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

## Texture decoding breakthrough

The D1 ROI PS4 texture pipeline is validated end-to-end on retail bytes from `0767`.

### Resident texture census

`ps4_arch_vex_com01_0767_0.pkg` contains **23 resident Texture2D headers** (`file_type=32`, `file_subtype=1`). All 23 were reconstructed to linear DDS and decoded to viewable PNG successfully.

Observed format census:

- BC1 / GCN `0x23`: 6 textures
- BC3 / GCN `0x25`: 8 textures
- BC4 / GCN `0x26`: 1 texture
- BC5 / GCN `0x27`: 7 textures
- RGBA8 / GCN `0x0A`: 1 texture

Largest validated image is `816CE138`, a 4096x4096 BC1 texture. Multiple 2048x2048 BC3/BC5 color/normal pairs also decode coherently.

### Exact observed backing chain

ROI texture headers can resolve through either a direct data entry or a streamed chain. The observed full-resolution streamed form is:

`32:1 texture header -> 65:1 streamed/mip record -> 5:1 full-resolution backing data`

Examples:

- `816CE05C -> 816CE05E -> 816CE19A`, 256x512 BC1, 65,536-byte full-resolution backing
- `816CE0B6 -> 816CE0BB -> 816CE19E`, 1024x1024 BC3, 1,048,576-byte backing
- `816CE0B7 -> 816CE0BC -> 816CE19F`, 1024x1024 BC5, 1,048,576-byte backing
- `816CE138 -> 816CE139 -> 816CE18A`, 4096x4096 BC1, 8,388,608-byte backing

### PS4 texture semantics now implemented

For D1 ROI PS4 texture headers:

- GCN format is `(ROIFormat >> 4) & 0x3f`
- width/height/depth/array are stored at `+0x28`
- `flags1` is at `+0x30`
- image data is PS4 Morton/8x8-block unswizzled when `(flags1 & 0xC00) != 0x400` (or cubemap)
- block-compressed formats use 4x4 BC blocks
- decoded BC1/BC3/BC4/BC5 and RGBA8 images visually validate the reconstruction

Local validation artifacts:

- `/mnt/data/0767_resident_textures.zip`
- `/mnt/data/0767_textures/contact_sheet.jpg`
- `/mnt/data/0767_textures/texture_manifest.json`
- `/mnt/data/d1_texture_export.py`

Resident texture archive SHA-256:

`97bf079b8b63cd022f6ad2146e1374ab127a2d0966698889a3eecde6fc7a2855`

## IMPORTANT correction: `80AAE10B/80AAE10C` are not the main visible 09A surface materials

A later byte-level part-table + Charm source comparison corrected the earlier interpretation.

`816CE09A` has four D1 mesh parts:

- part 0: inline material `FFFFFFFF`, `VariantShaderIndex=0`, strip range `927/7780`
- part 1: inline material `80AAE10B`, `VariantShaderIndex=-1`, same `927/7780` range
- part 2: inline material `FFFFFFFF`, `VariantShaderIndex=1`, strip range `0/926`
- part 3: inline material `80AAE10C`, `VariantShaderIndex=-1`, same `927/7780` range

Charm's D1 `DynamicMeshPart` behavior is source-confirmed:

- `VariantShaderIndex == -1` -> use the inline part material;
- otherwise -> resolve through the model parent `ExternalMaterialsMap` and `ExternalMaterials` arrays.

Charm also skips a D1 part when its resolved material has no vertex shader or no pixel shader.

`ps4_globals_0157_0.pkg` is now available and both direct inline technique tags were decoded correctly:

- `80AAE10B`: 1,160 bytes, VS shader `80AAE1DB`, **pixel shader `FFFFFFFF`**, VS texture count 0, PS texture count 0
- `80AAE10C`: 1,160 bytes, VS shader `80AAE1DD`, **pixel shader `FFFFFFFF`**, VS texture count 0, PS texture count 0

Therefore `80AAE10B/80AAE10C` cannot be the ordinary visible surface passes under Charm's own D1 filtering rule. They are more likely auxiliary/depth/shadow-like passes.

The visible 09A geometry is instead the `VariantShaderIndex=0` and `VariantShaderIndex=1` path, whose materials must be selected from the model parent's external-material tables.

This moves the exact texturing frontier from **"decode 10B/10C texture arrays"** to **"locate 09A's owning model parent and resolve external material variants 0/1"**.

## D1 model-parent material selector now calibrated

For the standard D1 model parent (`0x80801A9C`) the parent structure contains:

- model FileHash at `+0x15C`
- `TexturePlatesROI` DynamicArray at `+0x1A8`
- `ExternalMaterialsMap` at `+0x230`, element size `0x0C`
- `ExternalMaterials` at `+0x270`, element size `0x04`

D1 DynamicArray layout used here is:

- count = `u32(field+0)`
- relative pointer = `qword(field+8)`
- absolute data offset = `(field+8) + rel + 0x10`

Charm's external selector is:

`mapEntry = ExternalMaterialsMap[VariantShaderIndex]`

`material = ExternalMaterials[mapEntry.MaterialStartIndex + 0 % mapEntry.MaterialCount]`

Calibrated resident parents in 0767:

- `816CE061 -> model 816CE062`: map `(count=3,start=0)`, materials `80AD2003,80AD294D,80AD2898`
- `816CE0C1 -> model 816CE0C4`: no external materials
- `816CE0C2 -> model 816CE0C5`: map `(6,0)`, six external materials
- `816CE0C3 -> model 816CE0C6`: maps `(6,0)` and `(6,6)`, twelve external material slots

No standard model-parent EntityResource resident in 0767 points to model `816CE09A`. A scan of all 500 type-16 tags in `ps4_globals_0157_0.pkg` also found no literal `816CE09A` reference or standard D1 model-parent class. Thus 09A is currently best interpreted as a reusable articulated submodel whose owning/render-context parent is elsewhere in the package graph.

## `ps4_globals_0157_0.pkg` checkpoint

Package `0x0157` `_0` is now available and parsed:

- 2,117 entries
- 1,623 blocks
- 117 `0x80801AD7` technique entries
- 13 PS4 Texture2D headers
- 688 `5:1` payload entries
- 3 `65:1` streamed texture entries
- 117 type `32:8` shaders
- 171 type `32:9` shaders

At least one resident texture was decoded immediately:

- `80AAE02F -> 80AAE030`, RGBA8, 1024x32, coherent color-ramp/lookup image

The Oodle bridge can occasionally fault on an individual block under the lightweight PE loader; retrying the same block in a fresh process with `LINOODLE_SKIP_DLLMAIN=1` succeeds and should be treated as bridge instability rather than package corruption.

## Current remaining path to a faithfully textured animated export

1. Resolve the owning/render-context model parent for `816CE09A`.
2. Read parent `ExternalMaterialsMap[0]` and `[1]` and resolve the corresponding actual surface material hashes.
3. Parse those materials' shader texture arrays / texture plates / any remaining material indirections.
4. Follow texture TagHashes to owning packages.
5. Reconstruct the exact retail PS4 images using the already-proven texture exporter.
6. Map the D1 channels into an approximate glTF PBR material while preserving original material/texture hashes and semantics in `extras`.
7. Replace the placeholder materials in the already-valid rigged + multi-animation GLB.
8. Continue adding compatible clips using runtime-rig component `76F7A98E`.

The hard mesh, skeleton, skinning, animation-codec, package-compression, and PS4 texture-format problems are solved for this fixture. The active problem is now exact **render-context/material binding** for the reusable articulated model.
