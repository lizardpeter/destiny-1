# PS4 ROI Gjallarhorn Year 3 — full textured + natively bound animated extraction

Status: binary-grounded milestone.

## Retail identity

- InventoryItemHash: `D471D331`
- ArtArrangementIndex: `1229`
- WeaponPatternIndex: `39`
- Pattern s_entity: `80A6A017`

## Exact visual assembly

Art arrangement 1229 selects six visual entities/models:

- entity `80A743A4` -> model `80A743A6`
- entity `80A73BA9` -> model `80A73BAB`
- entity `80A72200` -> model `80A72202`
- entity `80A73179` -> model `80A7317B`
- entity `80A73254` -> model `80A73256`
- entity `80A73D11` -> model `80A73D13`

Combined native LOD1:

- 6 models
- 8 mesh records
- 10,738 triangles
- 9,801 source vertices

No mirrored or synthesized geometry is used.

## Exact recovered texture plates

Model -> TexturePlateHeader:

- `80A743A6 -> 80A39C90`
- `80A73BAB -> 80A398B5`
- `80A72202 -> 80A38D5D`
- `80A7317B -> 80A39407`
- `80A73256 -> 80A3947C`
- `80A73D13 -> 80A7E1B4`

All six albedo, normal and GStack plates are composed from 24 byte-proven source textures with serialized placement dimensions and **no resampling**.

The portable GLB connects the six exact albedo and six exact normal plates. Six exact GStack plate images are embedded as provenance but are not guessed into generic metallic/roughness channels. Final gear-dye coloration remains a separate native-material problem.

## Exact pattern-39 skeleton / rig / animation chain

- pattern entity `80A6A017`
- skeleton EntityResource `80AA3C97`
  - contains D1 skeleton discriminator `808006BD`
  - contains skeleton hierarchy/info `8080049A`
- runtime rig EntityResource `80AA2D6D`
- direct animation control `80AA2DCD`
- serialized clip refs at control payload offsets:
  - `+0xB0` -> `80AA2E4A`
  - `+0xB4` -> `80AA2E4B`

Seven skeleton joints, in source order:

0. `C410084A`
1. `AD2A05CD`
2. `3308E6CC`
3. `752D6334`
4. `FC1090F4`
5. `0AB6C582`
6. `B79A6009`

Hierarchy:

- joint 0 children: 1,2,3,4
- joint 1 child: 6
- joint 2 child: 5

Direct clips:

- `80AA2E4A`: 115 frames, 7 nodes, 7 rig controls, 3.8 s at 30 fps
- `80AA2E4B`: 31 frames, 7 nodes, 7 rig controls, 1.0 s at 30 fps

The pinned animation oracle is `SolUnshadowed/tiger-animation-parser` commit `b9fdc3a43dd28118113275624fcc9054b75855f4`.

## Critical geometry -> joint binding breakthrough

Every selected model has:

- `old_weights = FFFFFFFF`
- `unk_resource = FFFFFFFF`

The fourth signed 16-bit lane of each mesh's 8-byte primary vertex stream contains only values `0..6`, exactly the seven pattern-39 joints. The complete source distributions are:

| model | mesh | vertex count | native rigid joint distribution |
|---|---:|---:|---|
| `80A743A6` | 0 | 563 | joint 0: 340; joint 6: 223 |
| `80A73BAB` | 0 | 2184 | joint 0: 2040; joint 2: 144 |
| `80A72202` | 0 | 86 | joint 5: 86 |
| `80A7317B` | 0 | 1423 | joint 1: 1423 |
| `80A73256` | 0 | 188 | joint 1: 188 |
| `80A73256` | 1 | 5232 | joint 0: 3064; joint 1: 2168 |
| `80A73D13` | 0 | 8 | joint 0: 8 |
| `80A73D13` | 1 | 117 | joint 1: 117 |

Total: all 9,801 vertices have a native rigid joint index.

The GLB therefore emits, per vertex:

```text
JOINTS_0  = [native_lane3_index, 0, 0, 0]
WEIGHTS_0 = [1, 0, 0, 0]
```

This is not a guessed skin. It is a direct representation of the retail vertex data and the absence of an old blended-weight resource.

A spatial independent cross-check is unusually strong: model `80A72202`, whose 86 vertices are all assigned to joint 5, has geometry center approximately `[0, 0.16956, 0.09970]`; joint 5 bind-world origin is approximately `[0.000007, 0.175474, 0.097317]`, only about 0.00638 m apart.

## Final combined GLB

Production workflow:

- `.github/workflows/build-gjallarhorn-1229-textured-animated.yml`
- run `33930517073`
- conclusion: success
- artifact: `D1-Gjallarhorn-Year3-FULL-TEXTURED-ANIMATED`
- artifact id: `9958374114`
- artifact ZIP digest: `sha256:b1315449df2d90ebea11f37027b0baf39cfc1034fcdf336e57c3621012c46968`

GLB:

- `GJALLARHORN_YEAR3_ARRANGEMENT_1229_TEXTURED_ANIMATED.glb`
- 15,199,392 bytes
- SHA-256 `52aadfab799ad377287065b5b19154b43ddba14f106548599d3e4f4feb7ce3f3`
- 8 meshes
- 10,738 LOD1 triangles
- 18 embedded plate images
- 12 core glTF textures
- 1 skin
- 7 joints
- 2 native directly-linked animations
- every primitive has `JOINTS_0` and `WEIGHTS_0`

## Independent animation deformation validation

The combined GLB was re-read independently and its skin matrices were evaluated numerically at every keyed frame.

Maximum source-vertex displacement under `80AA2E4A`:

- `80A743A6` mesh0: ~0.266272 m
- `80A73BAB` mesh0: ~0.168526 m
- `80A72202` mesh0: ~0.371875 m
- `80A7317B` mesh0: ~0.230172 m
- `80A73256` mesh0: ~0.230169 m
- `80A73256` mesh1: ~0.230169 m
- `80A73D13` mesh0: ~0.000002 m
- `80A73D13` mesh1: ~0.230169 m

Thus the first directly-linked clip produces substantial **actual weapon geometry deformation**, not merely invisible armature motion.

`80AA2E4B` remains essentially static in transforms (maximum numerical/noise-scale displacements around 1e-5 to 3.5e-5 m) and is retained because it is directly serialized by the same native control.

## Remaining fidelity boundary

This milestone closes complete visual geometry, model texture plates, exact 7-joint rigid skin binding, and two directly-linked native animation clips for the Year-3 Gjallarhorn retail selection.

Still not claimed solved:

- final native gear-dye / iconic gold-white coloration logic
- complete Destiny deferred GStack -> final material response in generic glTF PBR
- semantic human-readable names for the seven weapon bones
- whether additional gameplay animation controls elsewhere reference further Gjallarhorn-specific clips beyond the two clips directly serialized by `80AA2DCD`

Those remain separate reversal targets and should not be filled by guesses.
