# D1 Guardian exactness reset — 2026-09-05

This note records an explicit methodology correction after Blender validation of the Spektar Pandion Guardian checkpoints.

## Heuristic range overrides are retired

The experimental hand-restoration and shoulder-pruning GLBs were useful only as negative diagnostics. They are **not** part of the authoritative extraction pipeline and must never be promoted as solved character assembly.

Specifically, manually enabling/disabling `80A8274E` ranges based on visual appearance made the hands/shoulders worse. That proves the remaining problem is not safely solvable by eyeballing serialized geometry variants.

From this checkpoint forward:

- no mesh range is promoted because it "looks like a hand" or "looks like a shoulder";
- no skeleton/clip is promoted because its dimensions happen to match the weights;
- no material channel is mapped because it gives a nicer Blender render;
- every visible part, body contribution, rig, animation and shader mapping must have an explicit serialized or source-backed owner/selection edge.

## What remains proven

### Coordinate basis correction

The Tiger -> glTF basis mismatch is independently proven and remains authoritative:

```text
native Tiger mesh: Z-up, X-forward, Y-right
published/parser conversion: [x,y,z] -> [y,z,x]
```

Applying the same basis to mesh and skeleton fixes the catastrophic exploded deformation mechanism. This is orthogonal to character-composition ownership.

### Bungie web gear-stage draw rule

Archived Bungie Spasm code explicitly uses:

```text
Spasm.RenderMesh.prototype.stagesToRender = [0]
```

and renders only the half-open stage-0 part interval whose LOD category name contains `0`.

Therefore the 28-range Spektar set is an exact implementation of the **published Bungie web gear-renderer stage-0 contract**. It is not to be manually altered to repair missing body anatomy.

### EntityModel highest-detail diagnostic is a different exact set

Charm's D1 `ELod.IsHighestLevel()` accepts categories `{0,1,2,3,10}`. Across the five Spektar models that yields 35 exact high-detail serialized ranges. This is a valid EntityModel forensic/highest-detail export mode, but it is **not** proof that all 35 ranges belong in an equipped player-preview character.

The 28-stage0 set and 35-highest-detail set answer different questions and must not be conflated.

## Missing hands now point to full-character composition

Bungie's archived armory/player-preview client does not render an isolated armor item set by guessing body pieces. The armory code passes:

```text
ArmoryDetailPage.model.gearAndDefaultArmor
```

to `setItemReferenceIdsWithMutedItems(...)`, and separately exposes class-indexed `defaultArmor` arrays.

That is direct evidence that a complete preview can include **default armor/body contributions in addition to the selected gear**. The missing physical hands in the five-piece Spektar checkpoint therefore must be solved through exact full-character/default-armor composition provenance, not by re-enabling arbitrary gauntlet ranges.

## Current animation is not owner-proven

The current compatibility-bound animation checkpoint used:

```text
skeleton 809D8613
runtime rig 809D856E
clip 809D8572
control 809D856F
state 13433E07
```

The skin-byte format and dimensions are validated, but a direct character-owner edge from the Spektar/loadout assembly to this exact clip has not been recovered. Therefore the current animated GLB is **diagnostic**, not authoritative character animation.

The shoulder floating seen under that clip must not be "fixed" by deleting shoulder geometry. It is evidence that animation/rig ownership must be proven first.

A separate exact Tower owner trace found Tower-local control `80C7AE68` -> clip `80C7AE98`, state `33C1D9D8`. Therefore `809D8572` is not promoted as the Tower-local clip found by that trace either.

## Stronger exact player-preview target

Bungie's archived D1 player preview explicitly loads:

```text
/common/destiny_content/animations/destiny_player_skeleton.js
/common/destiny_content/animations/destiny_player_animation.js
```

These published resources are now the canonical comparison target for a player-preview rig/animation rather than selecting an arbitrary race-set clip by compatible dimensions.

The new exact provenance workflow is:

```text
.github/workflows/d1-bungie-player-preview-provenance.yml
tools/d1_bungie_player_preview_probe.py
```

It recovers:

1. the current D1 Bungie manifest;
2. the published player skeleton JSON;
3. the published player animation JSON;
4. exact mobile GearAsset database rows for the five Spektar inventory hashes;
5. exact D1 InventoryItem definitions;
6. a direct ordered bone-hash + parent-hierarchy comparison between the published player skeleton and retail PS4 skeleton tag `809D8613`.

The five exact item hashes are:

```text
B4BD27A2 Spektar Pandion Gauntlets
1DF65286 Spektar Pandion Plate
4A37316F Spektar Pandion Mark
4A2AD693 Spektar Pandion Helmet
4A5B75DC Spektar Pandion Greaves
```

## Promotion gate for the next character GLB

No new "fixed Guardian" GLB should be published until all of the following are source-closed:

1. **Composition** — exact gear + default/body items selected by Bungie's player-preview/loadout data.
2. **Geometry selection** — each item's own exact art-content/index-set/stage/LOD selection.
3. **Skeleton identity** — published player skeleton matched to retail skeleton by exact ordered bone identities and hierarchy.
4. **Animation ownership** — published/player-owner animation selected by an exact path, not dimensional compatibility.
5. **Skin semantics** — primary vertex weights mapped under that proven skeleton identity.
6. **Material semantics** — exact D1 dye/detail/GStack behavior reconstructed from source/serialized data; preview PBR fallbacks remain explicitly diagnostic until then.

This evidence-only gate is the reusable policy for all future D1 playable characters, NPCs, vendors, and enemies.
