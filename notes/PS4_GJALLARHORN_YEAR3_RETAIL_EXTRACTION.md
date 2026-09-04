# PS4 ROI Year 3 Gjallarhorn retail extraction

Status: exact retail-selected LOD1 geometry assembly recovered and exported.

## Inventory -> art selection

Rise of Iron / Year 3 Gjallarhorn:

- InventoryItemHash: `D471D331` (3564229425)
- retail inventory definition FileHash: `80A6558A`
- package: `0132`, file index 5514
- equipping block class: `80801020`
- `gearArtArrangementIndex = 1229`
- `weaponSandboxPatternIndex = 39`

Year 1 Gjallarhorn (`4BF4BE3F`, item `80A644D4`) independently resolves to the same arrangement 1229 and pattern 39. Iron Gjallarhorn (`45CA94E4`, item `80A65584`) uses arrangement 4182 while retaining pattern 39.

## Arrangement 1229

The retail arrangement is a six-entity assembly, not one monolithic model.

Assignment -> EntityParent -> s_entity -> EntityResource(model) -> s_entity_model:

| EntityParent | s_entity | EntityResource | model |
|---|---|---|---|
| `80A743A3` | `80A743A4` | `80A743A5` | `80A743A6` |
| `80A73BA8` | `80A73BA9` | `80A73BAA` | `80A73BAB` |
| `80A721FF` | `80A72200` | `80A72201` | `80A72202` |
| `80A73178` | `80A73179` | `80A7317A` | `80A7317B` |
| `80A73253` | `80A73254` | `80A73255` | `80A73256` |
| `80A73D10` | `80A73D11` | `80A73D12` | `80A73D13` |

The six models contain 8 mesh records total.

## Geometry export

Successful CI run: `33926314774`

Artifact: `D1-Gjallarhorn-Year3-arrangement-1229-geometry`

GLB: `GJALLARHORN_YEAR3_ARRANGEMENT_1229_GEOMETRY.glb`

- output bytes: 461,772
- SHA-256: `7b6a562ce301e59aa130b42b3795747d50b578cd5ef0762716ee66b6b00f0f30`
- six retail-selected model roots
- eight mesh records
- 10,738 expanded non-degenerate LOD1 triangles
- native geometry resource packages: `011C`, `011E`, `0139`
- combined pre-presentation bbox in exported axis convention:
  - min `[-0.0752146691, -0.1086452454, -0.7475596666]`
  - max `[0.1190228611, 0.3214932680, 0.4835328162]`

The exporter applies each model's serialized model scale/translation and only adds one top-level presentation translation to center the combined visual assembly. No component geometry or transforms are mirrored/invented.

One retail patch corruption boundary is preserved in provenance: model `80A73D13` mesh 1 uses vertex/index streams from `ps4_gear_weapons_011c_1.pkg` after newer snapshots failed structural validation. The exporter now validates native vertex-buffer stride and payload divisibility before accepting a snapshot, rather than accepting corrupt-but-decompressible bytes.

## Native material census

Eleven locally identified materials are decoded:

- `80A39480`, `80A39481`
- `80A73263`, `80A73264`
- `80A73D14`, `80A73D15`
- `80A3D18E`
- `80A88D62`, `80A88D63`, `80A88D7E`, `80A88D7F`

The first geometry GLB intentionally uses neutral portable materials and retains native material hashes in extras. This avoids falsely treating direct shader textures as base-color maps before the dye/texture-plate path is decoded.

Notable direct material texture references already recovered:

- `80A0856C`
- `80A7441A`
- `80A3D241`
- `80A743B4`
- `80A7451D`

These are shader bindings only; their final portable semantic assignment is not yet claimed.

## Exact weapon pattern entity

Weapon pattern 39 resolves through the retail pattern tables:

- PatternGlobalTagIdHash: `81F4DC5C`
- WeaponContentGroupHash: `15A56325`
- WeaponTypeHash: `C9EB0270`
- PatternHash: `811C9DC5`
- sandbox assignment relation / pattern s_entity: `80A6A017`
- package: `0135`

`80A6A017` has 25 Resource[] references spanning local package 0135 and globals 0151/0154/0156/0157/0158. This is now the primary anchor for recovering Gjallarhorn's weapon-level skeleton/audio/animation resources. No anonymous rifle rig should be substituted.

## Remaining work before calling the GLB fully finished

1. Decode the six visual entities' non-model art resources and the dye/texture-plate bindings.
2. Export and bind the correct Gjallarhorn textures/material approximation without mislabeling deferred shader resources.
3. Resolve pattern entity `80A6A017` resources to the exact skeleton and animation-set owners.
4. Recover native movable-part attachment/weight semantics and build reload/fire/equip/idle clips into the six-model assembly.
5. Keep the exact D1 deferred-shader semantics separate from portable glTF PBR approximations.

The geometry/selection problem is now closed for Year 3 Gjallarhorn: the six visual models in arrangement 1229 are retail-selected by the actual inventory item, and all eight LOD1 mesh records are present in the proof GLB.
