# D1 Tower integrated Family E animated r8 closure — 2026-09-06

## Status

`D1_TOWER_INTEGRATED_FAMILY_E_ANIMATED_R8_COMPLETE`

The exact static/common Tower and the exact-texture articulated Tower layer now coexist in one Blender-targeted GLB, with the six source-owner-selected Family-E placements carrying exact skinning and animation.

Successful integration canary:

- workflow: `D1 Tower integrated Family E animated r8`
- run: `34060964203`
- commit under test: `e6175808c134c926891712ddb6a3ca36266878a3`
- release: `d1-tower-baked-common-family-e-animated-r8-exact-resources`
- output: `D1_TOWER_BAKED_COMMON_PLUS_FAMILY_E_ANIMATED_R8_EXACT_RESOURCES.glb`
- bytes: `634,504,536`
- SHA-256: `d948b1d695fed98a8be0caa10d2271b64c1d2c6807c774e72559ac0cc70b0b80`
- project Blender target: `Blender 5.2.1 LTS`

Generation is a direct glTF 2.0 container merge and therefore has no Blender runtime dependency; Blender 5.2.1 LTS is the validation/import target.

## Inputs pinned by content

### Static/common Tower

Release tag:

`d1-tower-baked-common-textured-r6-exact-resources`

Current release asset:

```text
D1_TOWER_BAKED_PLUS_COMMON_TEXTURED_EXACT_RESOURCES.glb
bytes    558,618,948
sha256   54e6d35f6d2a940e68f4d70bb0266b5af8fd57fdd39c0d0bc8396c4acc224ef9
```

### Animated articulated layer

Release tag:

`d1-tower-articulated-family-e-animated-r8-exact-resources`

```text
D1_TOWER_ARTICULATED_FAMILY_E_OWNER_SELECTED_ANIMATED_EXACT_RESOURCES.glb
bytes     75,876,040
sha256    8a68c4e18578824e3799cbbea13def8f828c60b6ad21e6658b8f390f6485caa2
```

The articulated layer already contains all 37 presently proven source-owned articulated Tower placements, so it is merged directly with the static/common baseline.  It must not be stacked on integrated articulated r7 because that would duplicate the articulated population.

## Final glTF resource census

```text
accessors      5,352
bufferViews    5,838
meshes         2,320
nodes         13,179
materials        534
textures         658
images           658
skins               6
animations          6
scenes              1
```

Input static/common resource census:

```text
accessors      4,585
bufferViews    5,001
meshes         2,234
nodes         12,438
materials        499
textures         588
images           588
skins               0
animations          0
```

Animated articulated layer census:

```text
meshes            86
nodes             740
materials          35
textures           70
images             70
skins               6
animations          6
```

The merger adds one layer parent node, producing `12,438 + 740 + 1 = 13,179` final nodes.

## Skin and animation remap validation

The existing `tools/d1_gltf_layer_merge.py` correctly remaps all animation and skin references when the articulated layer is appended after the static/common arrays.

The successful canary checks every final skin:

- exactly 67 joints;
- every joint index is inside the merged node array;
- skeleton root index is valid;
- inverse-bind accessor index is valid.

It also checks every final animation:

- every sampler input/output references a valid merged accessor;
- every channel sampler index is valid;
- every channel target references a valid merged node;
- every target path is translation, rotation, or scale;
- all six exact Family-E WorldIDs survive;
- exactly one action uses `80C7AE98`;
- exactly five actions use `809D8572`.

No skin/animation index is inferred or repaired after merge.

## Exact base preservation and determinism

The current static/common r6 BIN payload is an exact prefix of the integrated r8 BIN payload.

Every static/common r6 core JSON resource array is also an exact prefix of the integrated resource array:

- accessors
- animations
- bufferViews
- cameras
- images
- materials
- meshes
- nodes
- samplers
- skins
- textures

The merge was executed twice with the same articulated bytes stored under deliberately different filesystem paths and filenames.  Both merged GLBs were byte-identical and produced:

```text
sha256 d948b1d695fed98a8be0caa10d2271b64c1d2c6807c774e72559ac0cc70b0b80
```

Therefore temporary runner paths are not part of emitted GLB identity.

## Family E state retained in the full Tower

```text
all proven articulated placements       37
Family-E animated placements             6
other articulated bind-pose placements  31
Family-E skins                            6
Family-E animations                       6
```

Family E remains:

```text
EntityModel   80CA0CFC
skeleton      809D8613   67 nodes
runtime rig   809D856E   67 controls
```

Owner-selected action split:

```text
80C7AE98   62 frames   1 Tower placement
809D8572  324 frames   5 Tower placements
```

Skin fidelity remains unchanged from the animated-layer closure:

- source U8 weight lanes sum exactly 255;
- glTF floats are bit-exact `float32(U8/255)`;
- no portable-float renormalization;
- measured maximum float32 sum drift `1.1920928955078125e-07`.

## Important negative evidence: release tags are not sufficient content identities

The first integrated-r8 run, `34060894344`, failed before merge because it expected the historical r6 GLB SHA `f85b7ece...` under the r6 release tag.

The release tag had subsequently had its GLB asset replaced with a newer exact-resource build.  Fresh GitHub release metadata and direct download proved the current asset is:

```text
bytes    558,618,948
sha256   54e6d35f6d2a940e68f4d70bb0266b5af8fd57fdd39c0d0bc8396c4acc224ef9
```

The second run pinned both size and SHA and went fully green.

Project rule going forward:

> A GitHub release tag is a locator, not an immutable byte identity. Any retained binary dependency must be pinned by exact asset filename + byte size + SHA-256, and preferably validated against current release metadata before use.

Do not silently substitute an older or newer asset merely because it is under the same tag.

## Proven vs unresolved

### Proven in this checkpoint

- current exact static/common Tower asset bytes;
- all 37 presently proven articulated placements retained once;
- exact Family-E source skinning on all six placements;
- exact Family-E owner-selected action identity on all six placements;
- all six skins and animations survive full-Tower index remapping;
- exact resource counts and base-prefix preservation;
- path-independent deterministic full-Tower output;
- durable release output SHA-256;
- Blender 5.2.1 LTS project target.

### Still unresolved

- semantic state names for `80C7AE98` / `809D8572`;
- loop/synchronization behavior;
- human-readable NPC/vendor identity from source data;
- skin+animation ownership for the other 31 articulated placements / six model-skeleton families;
- final native shader recreation for all material families;
- sky/lighting/volumetric/effect integration beyond already recovered static/common visual content.

## Next highest-value direction

Continue family-by-family animation ownership closure for the remaining articulated Tower population.  Reuse the exact source-owned SEntity -> animation-owner -> control -> clip method from Family E, while keeping clip compatibility separate from ownership and refusing appearance-based NPC/state labels.
