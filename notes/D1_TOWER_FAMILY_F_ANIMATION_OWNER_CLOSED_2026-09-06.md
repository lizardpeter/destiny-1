# D1 Tower Family F animation-owner closure — 2026-09-06

## Status

`D1_TOWER_FAMILY_F_ANIMATION_OWNER_CONTROL_CLOSED`

Fresh retail canary:

- workflow: `D1 Tower Family F animation ownership`
- run: `34061302982`
- commit under test: `9ead94820c2fe2f2ef661138e1c7a1184cea0c51`
- artifact: `9997553056`
- violations: `0`

## Exact articulated family

```text
EntityModel   80C7AF4C
skeleton      80C7AF3A   2 nodes
runtime rig   80C7AF40   2 controls
rig component 1752ABBD x2
SEntities     80C7ADE5, 80C7AE14, 80C7AE15, 80C7AE16, 80C7AE1B
runtime placements 8
```

Exact runtime WorldIDs:

```text
80C7ADE5
  064E5A7957373FA3

80C7AE14
  29191E38D272B06B
  4FB47A0143A95F31
  747235765D9899D9
  CFEA129378E00812

80C7AE15
  0F6676AA91C2392A

80C7AE16
  A7D4B393917E2436

80C7AE1B
  6CB2EB24B545063B
```

## Exact owner pair

All five SEntity owners contain the same two animation-owner resources.

```text
80C7AF3D
  EntityResource class pair 808020BF -> 808029D2
  FileHash slot +0x110
  -> 80C7AF4E

80C7AF3F
  EntityResource class pair 80802B92 -> 808020BB
  FileHash slot +0x448
  -> 80C7AF4E
```

Both halves independently converge on the same retail animation control:

```text
80C7AF4E   class 80802C0E
```

The offsets are the same homologous source-owned slots already proven in Tower Family E.  Family F was not promoted from class homology alone: the class pairs, offsets, FileHashes, control class, selector table, skeleton, rig, and clips were all reopened from current SHA-pinned retail 023D bytes.

## Control animation list

The exact animation-list FileHashes are:

```text
index 0  80C7AF59   11 frames
index 1  80C7AF5A   66 frames
index 2  80C7AF5B   11 frames
index 3  80C7AF5C   31 frames
```

All four clips parse as exact Family-F-compatible animations:

```text
node_count        2
rig_control_count 2
runtime component fingerprint == 1752ABBD x2
```

`80C7AF59` is present in the animation list but is not selected by any decoded selector record.

## Exact state-selected set

The decoded `80802C0E` selector records are:

```text
state hash  B71D2CB1
scalar      2.1666667461395264
selection   index 1, count 1
clip        80C7AF5A   66 frames

state hash  557220AA
scalar      0.3333333432674408
selection   index 2, count 1
clip        80C7AF5B   11 frames

state hash  8405121A
scalar      1.0
selection   index 3, count 1
clip        80C7AF5C   31 frames
```

The three state hashes have no currently proven FNV1 preimages in the project's exact action-name dictionary.  They therefore remain hashes.  The scalar field also retains its deliberately unresolved semantic name.

## Correct export consequence

Family F is **not** equivalent to Family E's one-clip owner selection.  Its owner/control chain closes to a set of three state-selected actions.

The exporter may safely expose all three as source-owned animation actions for the exact 2-bone rig, but it must not choose one as a runtime default without another serialized state-selection layer.

Do not infer:

- idle/open/close/spin/etc. names from motion;
- startup/default state;
- loop behavior;
- synchronization across the eight placements;
- NPC/vendor semantics.

## Broader architecture result

The other still-unsolved runtime-rig Tower families expose the same two owner-resource class pairs:

```text
Family A, 4 bones
  80C7A2A5  80802B92 -> 808020BB
  80BC6412  808020BF -> 808029D2

Family G, 3 bones
  80C7AE38  80802B92 -> 808020BB
  80C7AE36  808020BF -> 808029D2
```

This is structural evidence that the owner-pair decoder can be generalized, but neither A nor G is considered animation-closed until their literal FileHash slots, controls, selector tables, and clip compatibility are freshly validated.
