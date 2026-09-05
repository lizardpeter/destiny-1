# Destiny 1 PS4 Gjallarhorn shared firing layer and reusable weapon extraction pipeline

Date: 2026-09-04 / 2026-09-05 UTC boundary
Platform/strategy: Destiny 1 Rise of Iron PS4
Canonical calibration item: Year 3 Gjallarhorn

## Status

This note records the first byte-closed path from a retail D1 weapon inventory item through both of Destiny's weapon animation layers:

1. the weapon-specific internal mechanism rig, and
2. the shared first-person/viewmodel action graph used by the calibrated rocket-launcher fixture.

The distinction is required for correct exports. A weapon's pattern-local skeleton does not necessarily own fire/recoil/equip/idle motion.

## Retail Gjallarhorn identity

Year 3 Gjallarhorn:

- InventoryItemHash: `D471D331`
- retail inventory definition: `80A6558A`
- `gearArtArrangementIndex = 1229`
- `weaponSandboxPatternIndex = 39`

Year 1 Gjallarhorn independently selects the same arrangement/pattern. Iron Gjallarhorn retains pattern 39 but selects a different art arrangement.

## Visual assembly layer

Arrangement 1229 resolves to six retail-selected visual entities and six models. The resulting LOD1 export contains:

- 6 selected models
- 8 mesh records
- 10,738 non-degenerate LOD1 triangles
- 9,801 source vertices
- 18 composed texture-plate images
- 12 portable albedo/normal texture bindings

No missing component was reconstructed by mirroring or manual placement.

## Pattern-local internal rig

Weapon pattern 39 resolves through the D1 retail weapon-pattern tables to pattern entity `80A6A017`.

Pattern-local animation resources:

- skeleton EntityResource: `80AA3C97`
- runtime rig: `80AA2D6D`
- internal animation control: `80AA2DCD`
- directly selected clips:
  - `80AA2E4A`: 115 frames / 3.8 seconds
  - `80AA2E4B`: 31 frames / 1.0 second

The weapon visual geometry encodes rigid joint assignment directly in the fourth int16 word of the native 8-byte position stream. Across the complete Gjallarhorn assembly this field contains only values 0..6, exactly matching the seven-bone pattern skeleton. All 9,801 vertices are therefore assigned from retail data rather than guessed weights.

An exhaustive scan of 17 animation-control records and 342 control-referenced clips in `ps4_globals_0151` proved that only `80AA2E4A` and `80AA2E4B` have the 7-node / 7-control signature compatible with the Gjallarhorn internal rig. This is the hard boundary proving that the missing firing recoil is not another omitted clip on the seven-bone weapon rig.

## Shared first-person action layer

Gjallarhorn weapon pattern 39 carries:

- WeaponTypeHash: `C9EB0270`
- exact lowercase D1 FNV1 preimage: `FNV1("rocket_launcher") = C9EB0270`

The calibrated shared action control is:

- `80AA3CC9`
- class/reference `80802C0E`

A generic `80800368` taxonomy record, `80AA3CD1`, contains `C9EB0270`, but this is **not** sufficient by itself to prove that `80AA3CC9` is selected from WeaponTypeHash. The same weapon-type taxonomy is also serialized in `80AA3005`; its first major hash groups are byte-for-byte shared with `80AA3CD1`. Therefore the `80800368` occurrence is treated as generic classification evidence, not as a direct WeaponTypeHash -> control ownership edge.

The remaining automation task is to byte-close the higher-level context/selector record that chooses the correct shared control family for a given weapon type or runtime context.

## Reusable `80802C0E` state selector structure

`tools/d1_animation_control_state_map.py` byte-decodes the D1 ROI action selector table.

For calibrated control `80AA3CC9`:

- `+0x08`: animation-list count
- `+0x10`: relative pointer to animation-list dynamic-array header
- animation list: FileHash array
- `+0x68`: selector-record count
- `+0x70`: relative pointer to selector-record dynamic-array header
- selector stride: `0x20`

Within each selector:

- `+0x10`: action/state StringHash
- `+0x14`: f32 scalar; exact semantic name intentionally unresolved
- `+0x18`: packed animation selection
  - high 16 bits = selection count
  - low 16 bits = zero-based animation-list start index

Every decoded selection range remains inside the serialized animation list, including records selecting two animations.

Known exact action hashes in `80AA3CC9` include:

- `fire` -> `9FAC79C9`
- `idle` -> `6FB760FF`
- `ready` -> `DCA2827A`
- `reload_empty` -> `6D507AD8`
- `reload_full` -> `28F43BD2`
- `base` -> `4CF9B596`
- `jump` -> `E480E089`

Names are assigned only when the exact FNV1 preimage is known.

## Byte-proven known action selections

For control `80AA3CC9`:

- animation-list count = 91
- state-table count = 72

Exact selected actions currently closed:

| state | hash | selection | clip(s) | clip signature |
|---|---|---:|---|---|
| `idle` | `6FB760FF` | start 1, count 1 | `80AA3CD6` | 97 frames, 76 nodes / 74 controls |
| `ready` | `DCA2827A` | start 4, count 1 | `80AA3CDA` | 30 frames, 76 / 74 |
| `jump` | `E480E089` | start 8, count 2 | `80AA3CE2`, `80AA3CE3` | 42 / 26 frames, 76 / 74 |
| `reload_empty` | `6D507AD8` | start 19, count 1 | `80AA3D40` | 105 frames, 75 / 73 |
| `reload_full` | `28F43BD2` | start 19, count 1 | `80AA3D40` | same clip |
| `fire` | `9FAC79C9` | start 33, count 1 | `80AA3D42` | 19 frames, 75 / 73 |

There are 11 selectors in this control that choose two clips, independently validating the packed count/start interpretation.

### Fire record detail

- exactly one selector hashes to `FNV1("fire") = 9FAC79C9`
- selector record index = 5
- selector record offset = 1216 (`0x4C0`)
- scalar = `0.6000000238418579`
- packed selection = `00010021`
- selection count = 1
- selection start = 33
- animation-list[33] = `80AA3D42`
- `80AA3D42` reference = `808005A1` (`s_animation_clip`)

This is direct binary selection, not a duration/name heuristic.

## Shared viewmodel rigs

Two action-signature families are present in the known states.

### 75-node / 73-control family

Exact compatible pair:

- skeleton: `80AA3CBF`
- runtime rig: `80AA3CBE`
- weapon Pedestal `C410084A`: skeleton index 72

Actual decode -> retarget -> local conversion succeeds for:

- `80AA3D40` (`reload_empty` / `reload_full`)
- `80AA3D42` (`fire`)

### 76-node / 74-control family

Two candidate pairs both pass structural counts, contain Pedestal `C410084A` at skeleton index 72, and successfully decode -> retarget -> local-convert all currently selected 76/74 clips:

- `80AA3CB2` rig + `80AA3CB3` skeleton
- `80AA3CB8` rig + `80AA3CB9` skeleton

Both successfully retarget:

- `80AA3CD6` (`idle`)
- `80AA3CDA` (`ready`)
- `80AA3CE2`, `80AA3CE3` (`jump`)

**No semantic choice is made between these two 76/74 pairs yet.** Count compatibility is not enough to assign runtime ownership. Their surrounding wrapper/context structures must decide which pair is correct for each layer/variant.

## `8080222A` wrapper evidence

Three large wrappers in the calibrated cluster are:

- `80AA3CC4`
- `80AA3CC7`
- `80AA3CCB`

Each begins with a sorted action-hash -> local-index map and contains nested resource arrays for those states. Exact known local indices differ by wrapper, for example:

| state | CC4 | CC7 | CCB |
|---|---:|---:|---:|
| idle | 0 | 11 | 11 |
| ready | 4 | 15 | 12 |
| fire | 11 | 4 | 5 |
| reload_empty | 5 | 0 | 0 |
| reload_full | 6 | 1 | 1 |
| jump | 29 | 29 | 28 |

The nested arrays and embedded resource classes are now under active decoding. Their existence is useful for separating multiple control/rig contexts, but the exact semantics of the wrapper variants are not yet claimed.

## `80802750` shared state-index resource

`80AA3CC2` and `80AA3CC9` both literally reference `80AA3CD4` at payload offset `+0x84`.

`80AA3CD4` has reference `80802750`, size 912, and contains a sorted exact action-hash -> small-index table. Known entries include:

- `idle` -> 0
- `fire` -> 1
- `jump` -> 3
- `ready` -> 14

This proves `80AA3CD4` participates in shared action-state indexing for the controls that reference it. The exact semantic names of its additional arrays/fields remain unresolved.

## Generic `80800368` taxonomy evidence

There are exactly two `80800368` entries in the final logical `0151` view:

- `80AA3005`, 1,632 bytes
- `80AA3CD1`, 1,936 bytes

Both serialize the same major hash taxonomy. Exact FNV1 weapon-type names recovered from that hierarchy include:

- `sniper_rifle` = `08D2C38F`
- `shotgun` = `0314A289`
- `machine_gun` = `8A5D6623`
- `sidearm` = `3EB02F1A`
- `rocket_launcher` = `C9EB0270`
- `sword` = `924E78C4`

`rifle` = `FE13412D`, `pistol` = `13569C00`, and `launcher` = `AB32428D` also have exact FNV1 matches in the hierarchy.

The first major group is a 53-row hash/value array plus a 53-row sorted lookup array. The first groups in `80AA3005` and `80AA3CD1` are byte-for-byte identical. `80AA3CD1` additionally contains a third top-level group. The second words in the hash/value rows are intentionally not named yet; they are not assumed to be parent indices or control IDs without further proof.

This is promising for a generic weapon-type resolver, but it is not yet the missing direct type -> action-control bridge.

## Standalone Gjallarhorn fire export

Production workflow:

- `.github/workflows/build-gjallarhorn-rocket-launcher-fire.yml`
- successful run: `33936531958`
- fixing commit: `b343b29a2796d27beb5391fda25fd2d3d882e3e1`
- artifact: `D1-Gjallarhorn-Year3-TEXTURED-ANIMATED-WITH-FIRE`
- artifact id: `9960364078`
- artifact digest: `sha256:4ed7afe9be6820ba5bc440677bc1bdb8915c5e35960a26ebbe88280983c6eab1`

Final GLB:

- `GJALLARHORN_YEAR3_TEXTURED_ANIMATED_WITH_FIRE.glb`
- 15,201,960 bytes
- SHA-256: `323f6940b464164e8ecf398227cf9da94a39cf68e011ccdfe68039bef487e989`
- 8 meshes
- 18 images
- 12 textures
- 1 internal skin / 7 internal Gjallarhorn joints
- three animations:
  - `80AA2E4A`
  - `80AA2E4B`
  - `rocket_launcher_fire_STATE_9FAC79C9_80AA3D42_VIEWMODEL_MOTION`

For a standalone weapon file, the shared viewmodel skeleton is not grafted into the seven-bone internal skin. Instead `tools/d1_gltf_add_external_root_motion.py` evaluates the exact animated world transform of shared-viewmodel Pedestal `C410084A`, rebases it to the first sample, and applies that delta to a parent node above the complete Gjallarhorn asset.

Measured fire delta:

- sample count: 19
- duration: `0.6000000238` s
- max translation from first sample: `0.0080270236`
- max rotation from first sample: `0.4731251` degrees
- max scale delta: ~`6.85e-7`

No recoil curve is generated or tuned by hand.

## Generic D1 inventory-weapon pipeline

The Gjallarhorn work establishes a reusable weapon path rather than a one-off extractor:

```text
InventoryItemHash
  -> D1 inventory definition
     -> gearArtArrangementIndex
     -> weaponSandboxPatternIndex

gearArtArrangementIndex
  -> 80A5FFA7 art arrangement
  -> assignment hash(es)
  -> 80A7E1DD assignment -> EntityParent
  -> EntityParent +0x10 EntityDataROI
  -> one or more visual s_entity records
  -> Resource[]
  -> model resource(s)
  -> s_entity_model(s)
  -> geometry / native material hashes / texture plates

weaponSandboxPatternIndex
  -> 80A5FFA9 weapon-pattern row
  -> PatternGlobalTagIdHash
  -> 80A7E1DC sandbox-pattern assignment
  -> pattern s_entity
  -> weapon-specific skeleton / runtime rig / internal action resources

WeaponTypeHash / shared context
  -> generic taxonomy/context resolver [last ownership bridge still being decoded]
  -> 80802C0E action control
  -> exact FNV1 action state
  -> zero-based animation-list selection
  -> s_animation_clip
  -> compatible shared viewmodel skeleton/runtime rig
  -> weapon Pedestal C410084A world motion
```

This separation is important for broad extraction:

- visual arrangement answers **which model pieces make this inventory item?**
- sandbox pattern answers **which weapon-specific internal rig/resources does it use?**
- shared action graph answers **which first-person actions move the weapon socket?**

## Reusable code already in the repository

- `tools/d1_remote_inventory_art_arrangement_find.py`
- `tools/d1_investment_arrangement_probe.py`
- `tools/d1_weapon_pattern_assignment_probe.py`
- `tools/d1_fnv1_action_probe.py`
- `tools/d1_animation_control_state_map.py`
- `tools/d1_gltf_add_external_root_motion.py`
- model / texture-plate / material / skeleton / animation exporters from earlier reversals

The next engineering target is to remove item-specific constants from orchestration so a caller can supply an InventoryItemHash and receive a machine-readable extraction recipe plus the resolved visual/internal/shared-animation resources.

## Evidence boundary

CONFIRMED_BINARY:

- all FileHash links and arrangement/pattern selections listed above
- FNV1 hashes where an exact preimage is stated
- `80AA3CC9` list/selector structure and packed selection ranges
- exact known-state clip selections listed above
- fire -> list index 33 -> `80AA3D42`
- clip frame/node/control counts
- successful retarget compatibility results and literal Pedestal identities
- `80AA3CD4` literal linkage from controls and its known action hash/index rows
- `80800368` generic taxonomy rows and exact FNV1 matches
- measured Pedestal motion applied to the standalone weapon

NOT YET CLAIMED:

- complete semantic names for all selector hashes
- ownership choice between the two 76/74 shared viewmodel rig pairs
- exact WeaponTypeHash -> action-control selection edge
- that every D1 model category uses the weapon Investment/action pipeline
- exact final D1 deferred/dye rendering in core glTF PBR
- camera-only recoil/VFX/projectile/audio behavior as part of the skeletal fire clip

The goal is a general D1 asset exporter, but weapon extraction and arbitrary world/character/entity extraction should remain separate orchestration modes where their retail ownership systems differ.
