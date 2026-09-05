# D1 articulated-asset identity correction — 2026-09-05

This note corrects an important semantic overreach in the weapons/characters work.

## Correction

The `0767` articulated fixtures must **not** be described as proven Vex characters/combatants merely because they live in a Vex architecture package and contain model + skeleton + runtime rig + animation resources.

In particular, the cluster around:

```text
parent       816CE12B
model        816CE09A
skeleton     816CE092   12 nodes
runtime rig  816CE095   12 controls
composition  816CE097
wrapper      816CE099
control      816CE09C
clips        816CE09D / 816CE09E
```

is now canonically described as a **12-node articulated Vex-package asset / animation fixture**.

Its exact gameplay identity is **UNPROVEN**. It may be an environmental mechanism, animated prop, machinery, combatant sub-object, or another articulated object. The current byte evidence does not distinguish those possibilities.

The smaller automatically discovered cluster:

```text
parent       816CE0DC
model        816CE1A4
skeleton     816CE0DE   3 nodes
runtime rig  816CE122   3 controls
composition  816CE109
control      816CE10A
clips        816CE113 / 816CE114 / 816CE115
```

is likewise only an **animated articulated asset candidate**.

## Why this correction matters

A D1 object can legitimately contain:

- an `s_entity_model`;
- a skeleton;
- a runtime rig;
- animation clips;
- an animation/control wrapper;

without being a player body or enemy combatant. Environmental machinery and animated props can use the same lower-level animation architecture.

A race/architecture package name such as `arch_vex_*` proves package-family association, not gameplay identity.

Bone count is also not identity proof. However, the 12-node and 3-node fixtures are sufficiently small that treating them as ordinary full humanoid combatants without stronger evidence would be especially unsafe.

## New evidence policy

The generic discovery pipeline is now **asset-first**:

```text
model + skeleton + runtime rig + animation
        -> articulated asset candidate
        != character/combatant
```

Promotion to a gameplay character/combatant requires an additional independent edge, for example:

1. exact `s_entity` / EntityResource ownership tied to a known combatant graph;
2. decoded gameplay/archetype/AI ownership metadata;
3. a runtime spawn/entity table that points to the articulated model cluster;
4. a proven combatant composition component plus an ownership path that actually reaches the model/rig/clip cluster;
5. another equally direct byte-level gameplay identity relation.

Package naming, adjacency, skeleton size, visual resemblance, or animation presence alone are insufficient.

## Tooling change

Canonical census interface:

```text
tools/d1_articulated_asset_census.py
```

It wraps the existing structural census but emits asset-first labels:

```text
animated_articulated_asset_candidate
rigged_articulated_asset_candidate
```

and always leaves:

```text
gameplay_identity_proven = false
character_or_combatant_semantic_proven = false
```

until a separate identity resolver proves otherwise.

The older filename `d1_character_family_census.py` is retained for compatibility with existing workflows/tests, but its character-oriented name must not be interpreted as evidence.

## Character-track implication

The current 0767 work remains valuable because it validates D1 skeleton/rig/clip decoding and reusable retargeting. It should be treated as **format calibration**, not as our proof that enemy character extraction is solved.

The next real character target should come from a package/component where the gameplay combatant identity can be established independently. The Cabal `005B` family census is therefore being evaluated under this stricter rule: first discover articulated assets, then separately determine which—if any—are actual Cabal combatants.
