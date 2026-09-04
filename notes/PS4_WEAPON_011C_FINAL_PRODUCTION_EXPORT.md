# PS4 011C final production weapon export

Date: 2026-09-04

This checkpoint records the first fully validated final-snapshot production GLB
for D1 ROI PS4 weapon model `80A39E12`, including the corrected current main
material, the instruction-proven small masked material, all twelve recovered
animations, and the logical-package sibling guard.

## Production run

Workflow:

- `.github/workflows/build-weapon-011c-test-glb.yml`
- run: `33904330327`
- head commit: `800542362704d53935611fbfb2add06e8d09858e`
- conclusion: **success**
- artifact: `80A39E12-final-weapon-glb`
- artifact id: `9948934544`
- artifact ZIP digest reported by GitHub:
  `sha256:aa44e051d04b110f1661ca1d6c0fdac761d067e94e8b9a9a32610a2bddae2bd5`

The workflow passed all of the following independently gated stages:

1. exact retail 011C/011E/0154/0157/0158 family recovery
2. final material and shader-resource assertions
3. exact texture recovery and texture-plate composition
4. deliberate same-logical-family dependency rejection
5. pinned animation parser/oracle recovery
6. corrected rigid 12-animation GLB build
7. structural/material/attachment validation
8. artifact bundle upload

## Independently downloaded GLB

`80A39E12_WEAPON_FINAL_RIGID_ANIMATED.glb`:

- size: `8,332,100` bytes
- SHA-256:
  `2f604d0285c1748369f4c53c7aa99006dc46262caf5f05b3641c590a8c07652f`
- glTF version: 2
- meshes: 2
- nodes: 76
- skin objects: 1
- animations: 12
- materials: 2
- embedded images: 11
- textures: 3
- samplers: 2

Exact animation names:

```text
80A39DF6
80A39DF7
80A39DF8
80A39DF9
80A39DFA
80A39DFB
80A39DFC
80A39DFD
80A39DFE
80A39DFF
80A39E00
80A39E01
```

## Final LOD1 geometry

Model `80A39E12` exports **2,620 nondegenerate LOD1 triangles**.

### Mesh 0 — small component

- vertices: 28
- source VB0: `80A39E1D`
- source VB1: `80A39E1F`
- source IB: `80A39E20`
- source strip range: offset 0, count 36
- expanded nondegenerate triangles: **16**
- final material: `80A3D294`

The emitted triangle-list index accessor contains 48 indices, independently
confirming `48 / 3 = 16` triangles.

### Mesh 1 — main shell

- vertices: 2,500
- source VB0: `80A39E13`
- source VB1: `80A39E14`
- source IB: `80A39E18`
- final visible material: `80A382A6`
- auxiliary native passes: `80AAE10B`, `80AAE10C`

Final visible strip expansion:

- source range offset 114, count 2,015 -> **1,294** nondegenerate triangles
- source range offset 2,240, count 2,188 -> **1,310** nondegenerate triangles
- total main shell: **2,604** triangles

The GLB independently confirms this through emitted triangle-list index-accessor
counts:

- 3,882 indices / 3 = 1,294 triangles
- 3,930 indices / 3 = 1,310 triangles

This supersedes the stale per-range split `1,193 + 1,411` recorded in the
older binding-correction note. The old note's **2,604 main / 2,620 total**
invariants were correct; only its distribution between the two source ranges
was stale.

The unresolved repeated stride-24 tail remains exactly:

```text
i16  [15974, 15974]
hex  [3E66, 3E66]
```

No semantic is assigned to that tail yet.

## Final rigid attachment

The native weapon geometry has no skin weights. Portable export therefore
preserves the proven native rigid hierarchy instead of fabricating vertex
weights.

- weapon Pedestal bone hash: `C410084A`
- skeleton/glTF bone node index: 72
- final mesh nodes: 74 and 75
- node 72 children: `[74, 75]`
- both mesh nodes have `skin = null`

The hierarchy remains:

```text
Hand.R -> Grip.R -> Weapon Pedestal C410084A -> rigid weapon mesh nodes
```

## Final native material bindings

### Main shell `80A382A6`

- entry index: 678
- class: `80801AD7`
- declared/actual size: 1,792 bytes
- VS: `80A3D28E`
- PS: `80A3D145`
- PS Vector4 container: `FFFFFFFF`
- PS TextureIndex 0: `80AB0B74`
- PS TextureIndex 1: `80A3D4D6`
- PS sampler records: 7

Sampler-record first dwords in material order:

```text
0  80AAE176
1  80AAE177
2  80AAE177
3  80AAE177
4  80AADBAB
5  80AADBAB
6  80AADBAB
```

The main shell continues to use the exact entity albedo and BC5 normal texture
plates for portable core glTF. `80AB0B74`, `80A3D4D6`, and the GStack plate
remain preserved as native provenance until `80A3D145` instruction dataflow
assigns stronger renderer semantics.

### Small component `80A3D294`

- entry index: 4756
- class: `80801AD7`
- declared/actual size: 1,328 bytes
- VS: `80AAE149`
- PS: `80AA9D63`
- PS Vector4 container: `80AAE1E1`
- sampler: `80AAE1D5`
- TextureIndex 0: `80AA9D4D`

Exact GCN proof established:

```text
coordinates = attr0.xy / TEXCOORD_0
RGB         = sampled atlas RGB
discard     = sampled_alpha < 0.5
```

Portable material therefore legitimately uses:

- `80AA9D4D` as baseColorTexture on TEXCOORD_0
- `alphaMode = MASK`
- `alphaCutoff = 0.5`
- `REPEAT` wrap S/T

Native sampler `80AAE1D5` is Wrap/Wrap/Wrap, anisotropic bilinear min+mag,
linear mip filtering. Core glTF cannot express the exact anisotropy; the export
uses linear mipmapped repeat filtering and retains the exact native descriptor
in material extras.

## Logical package namespace rule

Physical patch siblings such as `_0`, `_1`, `_4`, `_5` are one logical package
namespace. They are not cross-package dependencies. The selected final entry
table resolves physical payload blocks through `patch_id` and sibling paths.

`d1_texture_export.py` now rejects attempts to supply a same-family sibling as
`--dependency-pkg`, and the production workflow contains an expected-failure
regression proving that guard.

## Current next boundary

The remaining renderer-semantic frontier for this fixture is main PS
`80A3D145`. A dedicated exact GCN disassembly workflow was started in commit
`6cb7e3c9befa8d848f9c59b27907c53409644a3e` to determine how the current
`80AB0B74` cubemap, `80A3D4D6`, and the seven native sampler records participate
in the native pixel-shader output. No additional core-glTF semantic will be
assigned until that instruction dataflow proves it.
