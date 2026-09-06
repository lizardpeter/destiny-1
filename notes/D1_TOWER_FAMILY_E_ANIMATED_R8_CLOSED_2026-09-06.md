# D1 Tower Family E animated r8 closure — 2026-09-06

## Status

`D1_TOWER_FAMILY_E_ANIMATED_LAYER_COMPLETE`

The first source-owner-selected animated articulated Tower family is now closed and published durably.

Successful retail canary:

- workflow: `D1 Tower Family E animated exact-resource layer`
- run: `34060732798`
- commit under test: `6e2a33174933837f46d9fe0d2c796dd9f8ec82ec`
- release: `d1-tower-articulated-family-e-animated-r8-exact-resources`
- output: `D1_TOWER_ARTICULATED_FAMILY_E_OWNER_SELECTED_ANIMATED_EXACT_RESOURCES.glb`
- bytes: `75,876,040`
- SHA-256: `8a68c4e18578824e3799cbbea13def8f828c60b6ad21e6658b8f390f6485caa2`

## Exact family identity

```text
EntityModel   80CA0CFC
skeleton      809D8613   67 nodes
runtime rig   809D856E   67 controls
```

The existing articulated exact-texture layer remains the visual source.  Family E contributes:

```text
source meshes                 4
retail stage-0 draw ranges    26
unique triangles              20,575
runtime placements             6
placement geometry nodes     156
scene placement triangles 123,450
```

The source articulated layer contains 86 meshes, 332 nodes, 35 materials, 70 textures, and 70 images.  The animated output preserves those visual resource counts exactly and grows only by the animation/skin data needed for Family E:

```text
before: 86 meshes / 332 nodes / 0 skins / 0 animations
after:  86 meshes / 740 nodes / 6 skins / 6 animations
```

The original 73,093,112-byte BIN payload is an exact prefix of the final 74,551,096-byte BIN payload.

## Exact owner-selected animation split

Animation ownership was closed independently before the GLB build.  The animated exporter consumes that CLOSED report and does not select clips from appearance, duration, placement order, or naming.

```text
WorldID           SEntity     selected clip
1F763204E6BF153E  80C7AD82    809D8572
288E250AFDC06BC7  80C7AE3E    80C7AE98
28F88CAFCCE615AC  80CA0CD6    809D8572
5A9D48129FB3D22A  80CA0CD6    809D8572
5F523A4A340754A7  80CA0CD6    809D8572
C588D8EE0F1F493D  80CA0CD6    809D8572
```

Exact clip dimensions:

```text
80C7AE98   62 frames   67 nodes / 67 controls
809D8572  324 frames   67 nodes / 67 controls
```

Six separate glTF Animation objects are emitted.  This is intentional: it avoids claiming that the game starts all six clips simultaneously.

Semantic state names, loop behavior, synchronization behavior, and NPC/vendor identity remain unresolved unless separately proven.

## Exact skin storage and portable representation

Fresh retail validation reopens all four Family-E primary streams and checks them against the prior articulated skin census.

Exact source modes:

```text
mesh 0  inline4       141 vertices
mesh 1  inline4     1,381 vertices
mesh 2  inline2       745 vertices
mesh 3  rigid_lane3 19,835 vertices
```

Every retail source vertex has four U8 weight lanes whose sum is exactly `255`.  No malformed weight was repaired.

### Important float32 correction

The first portable validation mistakenly required the glTF FLOAT weights to sum mathematically to `1.0` within `1e-7`.  That is not a valid source-fidelity requirement.

For example, exact source weights:

```text
[128, 64, 32, 31]
```

sum to exactly 255, but the direct float32 encoding `U8 / 255` accumulates to:

```text
1.0000001192092896
```

That is normal float32 rounding.  Renormalizing those floats would change the exact retail ratios.

The closed r8 policy is therefore:

1. the authoritative raw U8 lanes must sum exactly to `255`;
2. every portable lane must be bit-identical to `float32(raw_u8 / 255)`;
3. no post-conversion renormalization is allowed merely to make a floating-point sum exactly `1.0`;
4. float32 sum error is reported diagnostically, not used to rewrite the data.

The retail run measured a maximum absolute float32 sum error of exactly:

```text
1.1920928955078125e-07
```

The successful canary proves:

```text
raw_u8_weight_sum_exact_255       true
float32_conversion_bit_exact      true
portable_float_weights_renormalized false
```

Synthetic regression coverage is in `tests/test_d1_tower_family_e_weight_fidelity.py`, including the `[128,64,32,31]` case so this bug cannot quietly return.

## Logical-package requirement

Two earlier red runs established another important D1 rule before the final green run.

An isolated physical `_5.pkg` member can have the correct entry table and bytes yet still be unable to service an entry because the entry's blocks reference sibling package generations through `patch_id`.

The animated build therefore stages the complete SHA-pinned logical `00EC` and `023D` sibling families before opening `00EC_5` and `023D_5` with `EntryReader`.

This is not optional convenience.  It is part of the package-format proof boundary.

The source-member catalog is `evidence/d1_tower_family_e_animation_source_member_catalog.json` schema v2 and intentionally records the failed minimal-member assumption as negative evidence.

## What is proven vs still unresolved

### Proven

- all six Family-E Tower WorldIDs;
- exact SEntity owner variant for each WorldID;
- exact owner -> control -> clip selection;
- exact 67-node skeleton and 67-control runtime rig compatibility;
- exact 62-frame and 324-frame clip dimensions;
- exact four-mesh skin storage modes;
- exact raw U8 weight sums and joint-domain validity;
- bit-exact U8/255 float32 transport with no renormalization;
- all 26 selected draw ranges and 20,575 unique triangles retained;
- all 156 Family-E placement geometry nodes skinned;
- six independent skins and six independent glTF animations;
- original visual resource counts unchanged;
- original articulated GLB BIN payload remains an exact prefix;
- durable release output SHA-256 `8a68c4e18578824e3799cbbea13def8f828c60b6ad21e6658b8f390f6485caa2`.

### Not yet proven

- human-readable state semantics for either clip;
- whether either clip loops in the Tower runtime;
- relative phase/synchronization between placements;
- vendor/NPC names or roles from appearance;
- animation ownership for the other six articulated model/skeleton families.

## Next integration step

The correct full-Tower r8 composition is:

```text
exact static/common r6 baseline
+
D1_TOWER_ARTICULATED_FAMILY_E_OWNER_SELECTED_ANIMATED_EXACT_RESOURCES.glb
```

Do **not** merge the animated articulated layer on top of integrated articulated r7, because the r8 articulated layer already contains all 37 previously proven articulated placements and that would duplicate them.

The existing `tools/d1_gltf_layer_merge.py` already remaps skin indices, skeleton/joint node indices, inverse-bind accessors, animation samplers, and animation target nodes, so no new glTF merge architecture is needed.
