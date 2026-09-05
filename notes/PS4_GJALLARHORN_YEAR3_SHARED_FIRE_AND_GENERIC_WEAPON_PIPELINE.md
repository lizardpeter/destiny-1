# Destiny 1 PS4 Gjallarhorn shared firing layer and reusable weapon extraction pipeline

Date: 2026-09-04 / 2026-09-05 UTC boundary
Platform/strategy: Destiny 1 Rise of Iron PS4
Canonical calibration item: Year 3 Gjallarhorn

## Status

This note records the first byte-closed path from a retail D1 weapon inventory item through both of Destiny's weapon animation layers:

1. the weapon-specific internal mechanism rig, and
2. the shared weapon-type first-person/viewmodel action graph.

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

## Shared rocket-launcher action layer

Gjallarhorn weapon pattern 39 carries:

- WeaponTypeHash: `C9EB0270`

The exact lowercase D1 FNV1 preimage is:

- `FNV1("rocket_launcher") = C9EB0270`

The shared rocket-launcher control cluster is anchored by animation control:

- `80AA3CC9`
- class/reference `80802C0E`

`80AA3CD1` contains the exact `C9EB0270` value in the same action-graph cluster, independently tying this family to `rocket_launcher`.

## Reusable 80802C0E state selector structure

`tools/d1_animation_control_state_map.py` byte-decodes the D1 ROI action selector table.

For the calibrated control `80AA3CC9`:

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

Known exact action hashes in the rocket-launcher control include:

- `fire` -> `9FAC79C9`
- `idle` -> `6FB760FF`
- `ready` -> `DCA2827A`
- `reload_empty` -> `6D507AD8`
- `reload_full` -> `28F43BD2`
- `base` -> `4CF9B596`
- `jump` -> `E480E089`

Names are assigned only when the exact FNV1 preimage is known.

## Byte-proven fire selection

For control `80AA3CC9`:

- animation-list count = 91
- state-table count = 72
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

Cross-state sanity from the same table:

- idle starts at list index 1
- ready starts at index 4
- reload_empty starts at index 19
- reload_full starts at index 19
- 11 selectors choose two clips

## Shared fire clip and viewmodel rig

The selected `80AA3D42` clip is:

- 19 frames
- 0.6 seconds at 30 fps
- 75 animation nodes
- 73 rig controls

Matching shared rocket-launcher viewmodel resources:

- skeleton: `80AA3CBF`
- runtime rig: `80AA3CBE`
- weapon Pedestal bone hash: `C410084A`

`C410084A` is present literally in the 75-node skeleton. It is the same weapon Pedestal identity previously recovered under `Grip.R` in the 73-node first-person/player weapon fixture.

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
- duration: 0.6000000238 s
- max translation from first sample: 0.0080270236
- max rotation from first sample: 0.4731251 degrees
- max scale delta: ~6.85e-7

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

WeaponTypeHash
  -> shared weapon-type action graph
  -> 80802C0E state selector
  -> exact FNV1 action state
  -> zero-based animation-list selection
  -> s_animation_clip
  -> compatible shared viewmodel skeleton/runtime rig
  -> weapon Pedestal C410084A world motion
```

This separation is important for broad extraction:

- visual arrangement answers **which model pieces make this inventory item?**
- sandbox pattern answers **which weapon-specific internal rig/resources does it use?**
- weapon type/action graph answers **which shared first-person actions does the weapon use?**

## Reusable code already in the repository

- `tools/d1_remote_inventory_art_arrangement_find.py`
- `tools/d1_investment_arrangement_probe.py`
- `tools/d1_weapon_pattern_assignment_probe.py`
- `tools/d1_fnv1_action_probe.py`
- `tools/d1_animation_control_state_map.py`
- `tools/d1_gltf_add_external_root_motion.py`
- model / texture-plate / material / skeleton / animation exporters from earlier reversals

The next engineering target is to remove Gjallarhorn-specific constants from the orchestration layer so a caller can supply an InventoryItemHash and receive a machine-readable extraction recipe plus the resolved visual/internal/shared-animation resources.

## Evidence boundary

CONFIRMED_BINARY:

- all FileHash links and arrangement/pattern selections listed above
- FNV1 hashes where an exact preimage is stated
- `80AA3CC9` list/selector structure and packed selection ranges
- fire -> list index 33 -> `80AA3D42`
- fire clip frame/node/control counts
- `80AA3CBF`/`80AA3CBE` structural compatibility and Pedestal identity
- measured Pedestal motion applied to the standalone weapon

NOT YET CLAIMED:

- complete semantic names for all 72 selector hashes
- that every D1 model category uses the weapon Investment/action pipeline
- exact final D1 deferred/dye rendering in core glTF PBR
- camera-only recoil/VFX/projectile/audio behavior as part of the skeletal fire clip

The goal is a general D1 asset exporter, but weapon extraction and arbitrary world/character/entity extraction should remain separate orchestration modes where their retail ownership systems differ.
