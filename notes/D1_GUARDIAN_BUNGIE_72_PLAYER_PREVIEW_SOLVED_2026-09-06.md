# D1 Guardian exact Bungie 72-node player-preview skin palette — 2026-09-06

This note records the correction that resolves the Spektar Pandion shoulder deformation without remapping or guessing any source joint index.

It supersedes the earlier use of retail skeleton `809D8613` as a direct-index skin target. The D1 inline skin-byte decoder itself remains valid; the error was the skeleton **index palette** the decoded bytes were evaluated against.

## 1. Why the 67-node direct-index target was invalid

The exact PS4 Spektar skin data uses 27 nonzero joint indices:

```text
1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,25,26,27,28,40,42
```

Comparing those source indices against Bungie's exact published 72-node D1 player-preview skeleton and retail `809D8613` proves six direct-index semantic failures. Most importantly:

```text
source index 27
  published player palette: b_l_shoulder_twist_fixup
  retail 809D8613 index 27: different bone

source index 28
  published player palette: b_r_shoulder_twist_fixup
  retail 809D8613 index 28: different bone
```

Those two indices carry very large Spektar gauntlet influence totals. Directly evaluating them as `809D8613[27]` / `[28]` therefore deforms the shoulder region around the wrong pivots.

The same audit also finds published-vs-809D8613 mismatches for source indices `25`, `26`, `40`, and `42`.

The direct-index `809D8613` path is retired. No source JOINTS value is rewritten to make that skeleton fit.

## 2. Bungie's published viewer provides the exact 72-node palette

The archived D1 `Spasm.ItemPreview` renderer explicitly allocates:

```text
boneCount = 72
u_skinning_matrices[72]
```

and loads:

```text
/common/destiny_content/animations/destiny_player_skeleton.js
/common/destiny_content/animations/destiny_player_animation.js
```

Current exact file hashes:

```text
destiny_player_skeleton.js
SHA256 a477e58e2b9c23dcc75e8b538c24cc181f2a3af4b2cb2340b603aacf2f47e716
nodes 72

published source joint 27 = b_l_shoulder_twist_fixup
published source joint 28 = b_r_shoulder_twist_fixup

destiny_player_animation.js
SHA256 2d6d419a357e8e141cf717b20ab68034cb6e6ded51f63fc3377bb26ce2fef3b5
frames 146
nodes 72
rig controls 72
```

The published skeleton contains exact object-space and inverse-object-space bind transforms for all 72 nodes.

## 3. Exact published animation semantics are source-closed

Archived Bungie `Spasm.Animation` code defines the decode directly:

1. `static_bone_data` and `animated_bone_data` each provide scale/rotation/translation control maps.
2. For each node and component, the node index selects either the static frame-0 value or the corresponding animated-frame value.
3. The resulting local SRT is converted to a matrix.
4. Parent matrices are accumulated in hierarchy order.
5. Skinning matrix is `animated_object_space * default_inverse_object_space`.

The published animation's static/animated maps partition all 72 nodes for every S/R/T component with no overlap or missing node.

The archived viewer advances `frameIndex` by `0.5` per `requestAnimationFrame`. The glTF checkpoint serializes the 146 source frames at 30 fps as an explicit export cadence; this is not claimed to be a PS4 serialized clip-rate field.

## 4. Corrected exact player-preview diagnostic

Reusable tools:

```text
tools/d1_bungie_published_player_preview_bind.py
tools/d1_gltf_skin_deformation_bounds.py
```

Workflow:

```text
.github/workflows/d1-spektr-pandion-bungie-72-player-preview.yml
run 34012043938
result SUCCESS
```

Artifact:

```text
D1-SPEKTAR-PANDION-BUNGIE-72-PLAYER-PREVIEW
artifact ID 9982762195
artifact ZIP SHA256 d3dc4047f952d93f6846b47b1c402b440afa3cb58f333108fb1026578cb95b0f
```

Primary GLB:

```text
SPEKTAR_PANDION_TITAN_MASCULINE_STAGE0_TEXTURED_BUNGIE_72_PLAYER_PREVIEW.glb
bytes 19,432,512
SHA256 91aecb7f8d01d45661b9741d4668183da4666520d5f278812617224deaa81fd5
visible stage-0 mesh nodes 28
skin joints 72
animation frames 146
animation channels 216
```

The build starts from the already basis-corrected 28-stage0 textured static Spektar checkpoint. It removes the old 67-node skin and `809D8572` animation, preserves the exact source `JOINTS_0` / `WEIGHTS_0` values unchanged, and evaluates those source indices against the exact published 72-node Bungie player palette.

Tiger -> glTF basis remains the proven cyclic permutation:

```text
[x,y,z] -> [y,z,x]
```

Bind/inverse-bind consistency is validated independently:

```text
max source bind * source inverse-bind error  2.8282e-06
max serialized glTF bind identity error       5.0757e-06
```

## 5. Independent CPU deformation proof

`d1_gltf_skin_deformation_bounds.py` reparses the emitted GLB and evaluates its serialized node hierarchy, animation channels, JOINTS/WEIGHTS and inverse-bind matrices independently of the binder.

Sampled animated bounds:

```text
frame   span X      span Y      span Z
0       0.899883    1.888110    0.567437
1       0.899934    1.888111    0.567263
30      0.902189    1.888243    0.563027
60      0.899978    1.890480    0.558629
100     0.900341    1.888862    0.562993
145     0.899883    1.888110    0.567437
```

All six samples remain a coherent human-scale body volume. This is qualitatively different from the old 67-node diagnostic, whose wrong palette produced large shoulder displacement even after the mesh/skeleton coordinate basis was corrected.

This numerical result is not a substitute for Blender inspection, but it closes the deformation mechanism at the serialized math level.

## 6. What is and is not promoted

Promoted:

- exact D1 inline Guardian skin byte formats;
- exact source Spektar JOINTS/WEIGHTS;
- exact Bungie published 72-node player-preview joint palette;
- exact published 72-node bind/inverse-bind transforms;
- exact published 146-frame player-preview animation data and archived decode semantics;
- exact 28-stage0 Bungie web gear-render contract;
- the new 72-node GLB as the authoritative **Bungie player-preview diagnostic** for the five selected Spektar pieces.

Not yet promoted:

- a claim that a byte-identical 72-node skeleton tag has been found in the PS4 `race_set` packages;
- a PS4 runtime owner edge from the five Spektar entities to this exact published preview animation;
- complete player body composition.

The last point matters for the missing hands. Archived Armory code passes `gearAndDefaultArmor` into ItemPreview and exposes class-indexed `defaultArmor`. Therefore missing body/hands must still be solved by recovering the exact default/body item contribution, not by manually turning additional Spektar ranges on.

## Evidence policy

Do not remap a raw source joint index merely because another retail skeleton contains the same bone hash elsewhere. For this checkpoint, source joint index `n` means published player-preview palette entry `n`, because that is the only exact 72-slot Bungie skinning palette whose semantics agree with the source indices, including the heavily weighted shoulder twist-fixup slots.
