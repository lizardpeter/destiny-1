# D1 Tower Family G animation-owner closure — 2026-09-06

## Status

`D1_TOWER_FAMILY_G_ANIMATION_OWNER_CONTROL_CLOSED`

Fresh retail canary:

- workflow: `D1 Tower runtime-rig animation owner families`
- run: `34061605868`
- commit under test: `3fd6a22296b35045388c24b46cb91cf6b483d565`
- artifact: `9997650220`
- violations: `0`

## Exact family

```text
EntityModel   80C7AE59
skeleton      80C7AE32   3 nodes
runtime rig   80C7AE39   3 controls
rig component A828E5DE x3
runtime placements 3
```

Exact source-owned placements:

```text
80C7AE17 -> 5764137809E7AC7A
80C7AE18 -> 29E0B9685B2E3BE3
80C7AE19 -> 380FEB53B471ED5E
```

## Exact owner pair and control

```text
80C7AE36
  class pair 808020BF -> 808029D2
  FileHash +0x110
  -> 80C7AE5B

80C7AE38
  class pair 80802B92 -> 808020BB
  FileHash +0x448
  -> 80C7AE5B
```

Both halves independently converge on exact animation control `80C7AE5B` (`80802C0E`).

## Animation list and selected states

Full control animation list:

```text
80C7AE62  11 frames  exact 3/3 compatible, not selected by decoded state
80C7AE63  66 frames  exact 3/3 compatible, selected
80C7AE64  11 frames  exact 3/3 compatible, selected
80C7AE65  31 frames  exact 3/3 compatible, selected
```

Decoded selector records:

```text
B71D2CB1  scalar 2.1666667461395264  -> 80C7AE63
557220AA  scalar 0.3333333432674408  -> 80C7AE64
8405121A  scalar 1.0                 -> 80C7AE65
```

The same three selector hashes occur in Family F. None currently has an exact proven FNV1 preimage in the project dictionary, so they remain hashes.

## Export policy

Family G closes to a **three-action selected set**, not one default action. A Blender/glTF export may expose `80C7AE63`, `80C7AE64`, and `80C7AE65` as separate source-owned actions on each exact 3-bone rig instance. It must not choose one as startup/default without another source state-selection layer.

`80C7AE62` remains source-compatible but is not promoted as a selected action because no decoded selector chooses it.

Still unresolved:

- human-readable state names;
- default/startup state;
- loop behavior;
- cross-instance phase/synchronization;
- actor/NPC/vendor semantics.

Family-G geometry/skin was already exact and export-ready before this animation closure: one source mesh, supported rigid lane skinning, valid bone domain, and no skin frontier.
