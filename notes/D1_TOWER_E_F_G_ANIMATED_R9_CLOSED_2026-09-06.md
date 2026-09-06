# D1 Tower E/F/G animated r9 closure — 2026-09-06

## Status

`D1_TOWER_INTEGRATED_E_F_G_ANIMATED_R9_COMPLETE`

The exact static/common Tower and all 37 source-owned articulated Tower placements now coexist in one Blender-targeted GLB with Families E, F, and G carrying exact retail skinning and source-selected animation actions.

Successful canary:

- workflow: `D1 Tower Families F G animated r9`
- run: `34063464973`
- commit under test: `20d3ca69daf94cf5e8e05f5d172cabe8bc883f72`
- articulated release: `d1-tower-articulated-e-f-g-animated-r9-exact-resources`
- full release: `d1-tower-baked-common-e-f-g-animated-r9-exact-resources`
- Blender target: `Blender 5.2.1 LTS`

## Exact articulated r9 layer

```text
D1_TOWER_ARTICULATED_E_F_G_ANIMATED_R9_EXACT_RESOURCES.glb
bytes    76,004,468
sha256   5b459d7ec8e9c9912ce63bb3f988c8c02b87b020bca0b17f4fee120609e237a2
```

Resource census:

```text
meshes          86
nodes          776
materials       35
textures        70
images          70
skins           17
animations      39
```

The articulated layer still contains all 37 previously proven runtime WorldIDs exactly once. It starts from the exact Family-E animated r8 layer and appends only Families F and G.

The builder was executed twice from byte-identical r8 inputs stored under different paths/names. Both r9 GLBs were byte-identical.

## Family E retained exactly

Family E remains the prior closed 67-bone layer:

```text
EntityModel   80CA0CFC
skeleton      809D8613   67 nodes
runtime rig   809D856E   67 controls
placements    6
skins         6
animations    6
```

No Family-E geometry, material, texture, skin, or animation is regenerated from an approximation; r9 takes the exact published r8 articulated bytes as its input checkpoint.

## Family F promoted

```text
EntityModel   80C7AF4C
skeleton      80C7AF3A   2 nodes
runtime rig   80C7AF40   2 controls
placements    8
visible ranges 2
unique triangles 827
```

Exact source skin stream:

```text
header   80C7AF5E
backing  80C7AF69
stride   12
vertices 2,177
mode     rigid_lane3
bone domain [0,1]
raw U8 weight sum 255 exactly
```

Owner-selected action set:

```text
B71D2CB1 -> 80C7AF5A   66 frames
557220AA -> 80C7AF5B   11 frames
8405121A -> 80C7AF5C   31 frames
```

All three selected actions are exported separately for each of the eight exact Family-F WorldIDs:

```text
8 skins
24 animations
```

No startup/default state is selected because no higher-level placement selector has been proven. The three state hashes remain unnamed.

## Family G promoted

```text
EntityModel   80C7AE59
skeleton      80C7AE32   3 nodes
runtime rig   80C7AE39   3 controls
placements    3
visible ranges 2
unique triangles 827
```

Exact source skin stream:

```text
header   80C7AE95
backing  80C7AEE0
stride   12
vertices 2,016
mode     rigid_lane3
bone domain [0,1]
raw U8 weight sum 255 exactly
```

Owner-selected action set:

```text
B71D2CB1 -> 80C7AE63   66 frames
557220AA -> 80C7AE64   11 frames
8405121A -> 80C7AE65   31 frames
```

All three selected actions are exported separately for each of the three exact Family-G WorldIDs:

```text
3 skins
9 animations
```

Again, no default/startup/loop/synchronization semantic is inferred.

## Weight fidelity

Families F and G use the same retail-fidelity gate established for Family E:

- authoritative U8 lanes sum exactly `255`;
- emitted glTF floats are bit-exact `float32(U8/255)`;
- no post-conversion float renormalization;
- unknown/unsupported skin storage fails closed.

## Full Tower r9

```text
D1_TOWER_BAKED_COMMON_PLUS_E_F_G_ANIMATED_R9_EXACT_RESOURCES.glb
bytes    634,633,660
sha256   55dc9ba97548a888d407094894588a0e50b8f409686d6c5b9e5992f0f3c7633a
```

Final resource census:

```text
meshes        2,320
nodes        13,215
materials       534
textures        658
images          658
skins            17
animations       39
```

Skin joint-count distribution:

```text
67 joints x 6 skins   Family E
 2 joints x 8 skins   Family F
 3 joints x 3 skins   Family G
```

Animation distribution:

```text
Family E   6
Family F  24
Family G   9
----------------
total     39
```

## Static/common preservation and determinism

The static/common input remains the SHA-pinned current r6 asset:

```text
bytes    558,618,948
sha256   54e6d35f6d2a940e68f4d70bb0266b5af8fd57fdd39c0d0bc8396c4acc224ef9
```

The full r9 merger proves:

- r6 BIN is an exact prefix of the final BIN;
- every r6 core JSON resource array remains an exact prefix;
- merging the same r9 layer under different temporary paths/names produces byte-identical full Tower GLBs;
- all skin joint, inverse-bind, animation sampler, accessor, and target-node references are in range after merge.

## Remaining articulated bind-pose population

```text
Family A   1 placement
Family B   1 placement
Family C  15 placements
Family D   3 placements
----------------------
total     20 bind-pose placements
```

Family A is not promoted despite its exact owner-control closure because its selected `idle` clip uses runtime-rig component `C3747E31 x1`, while the proven model rig is `69289DF6 x4`. See `D1_TOWER_FAMILY_A_CROSS_PACKAGE_ANIMATION_FRONTIER_2026-09-06.md`.

Families B/C/D still lack a proven runtime-rig animation path and remain untouched.

## Current proof boundary

Proven:

- all 37 articulated placements retained once;
- exact E/F/G skinning;
- exact source-selected E/F/G animation identity;
- separate F/G actions without fabricated default state;
- full-Tower glTF remapping;
- path-independent deterministic layer build and full merge;
- exact published byte identities.

Not proven:

- F/G human-readable state names;
- default/startup action choice for F/G;
- loop/synchronization behavior;
- Family-A `C3747E31` child target;
- B/C/D runtime-rig animation ownership;
- vendor/NPC semantic names from appearance;
- final native D1 shader/lighting/effect recreation beyond the recovered visual layers.
