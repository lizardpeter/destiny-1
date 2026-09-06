# D1 Tower Family A cross-package animation frontier — 2026-09-06

## Status

`D1_TOWER_FAMILY_A_OWNER_CONTROL_CLOSED__MODEL_RIG_BINDING_UNRESOLVED`

Family A's animation-owner architecture is now source-closed across its real package boundary, but its selected animation must **not** be attached to the proven 4-bone model rig yet.

Successful source recovery / partial compatibility canary:

- workflow: `D1 Tower runtime-rig animation owner families`
- run: `34063052693`
- commit: `61e92349c5bd9bf5671f888b3f24162727619ba2`
- artifact: `9998081280`
- report: `TOWER_FAMILY_A_ANIMATION_OWNERSHIP.json`

## Exact Family-A model side

```text
SEntity       80C7A05E
WorldID       592D3113E2C5BDB4
EntityModel   80C7AD2A
skeleton      80BC60B2   4 nodes
runtime rig   80BC60B4   4 controls
rig component 69289DF6 x4
```

The skeleton and runtime rig are physically in exact current `01E3` Globals Cinematic members. The SEntity and the high animation-owner half are in Tower Activity `023D`.

## Cross-package owner pair is exact

The two homologous owner halves independently converge on the same live animation control:

```text
01E3  80BC6412   808020BF -> 808029D2   FileHash +0x110 = 80BC6489
023D  80C7A2A5   80802B92 -> 808020BB   FileHash +0x448 = 80BC6489
```

This proves that the earlier single-package failure was a package-locality assumption, not a broken owner layout.

## Source-selected state/action

Control `80BC6489` resolves uniquely in `01E3` and decodes to exactly one animation-list entry and exactly one selector state:

```text
state hash    6FB760FF
state name    idle          exact known FNV1 preimage
scalar        1.0
selected clip 80BC648A
frames        31
```

Unlike Families F/G, the state semantic `idle` is source-grounded here because the exact state hash already has a known FNV1 preimage in the project dictionary.

## Why the clip is not promoted to the 4-bone model

The selected clip itself parses as:

```text
80BC648A
node count          1
rig control count   1
rig component       C3747E31 x1
```

That component fingerprint does **not** match the proven Family-A model runtime rig:

```text
clip       C3747E31 x1
model rig  69289DF6 x4
```

The pinned `tiger-animation-parser` production retargeter (`b9fdc3a43dd28118113275624fcc9054b75855f4`) only advances its compatible-control limit while animation and target runtime-rig component hashes agree. A first-component hash mismatch therefore yields a compatible control limit of zero for `80BC648A` against `80BC60B4`.

Attaching this 31-frame clip directly to the four Family-A model bones would consequently fabricate a relationship that the production compatibility rule does not support.

## Current interpretation boundary

The binary evidence proves all of the following independently:

1. `80C7A05E` owns the exact Family-A model/skeleton/runtime-rig resources.
2. Its cross-package owner pair converges on `80BC6489`.
3. `80BC6489` selects source state `idle` -> `80BC648A`.
4. `80BC648A` is a real 31-frame 1-node / 1-control animation.
5. That animation is not compatible with the proven four-control model rig fingerprint.

The unresolved question is **what 1-control child/subcomponent the owner control is animating**. The correct next proof is to trace component `C3747E31` and/or the remaining Family-A SEntity resources to its exact matching skeleton/runtime rig and then determine whether that child is represented by geometry in the articulated model export.

No same-shaped local rig, repeated bind track, zero-filled synthetic track, or four-bone expansion is permitted.

## Export policy

Until the `C3747E31` target is source-resolved:

- Family A remains bind pose in the Tower GLB;
- `80BC648A` is retained as exact owner-selected animation evidence but is not bound to `80C7AD2A`;
- r9 may advance independently with already-closed Families F and G;
- this frontier must not be described as a failure of the cross-package owner resolver.
