# Destiny 1 Skeletons and Animations — Living Specification

Status: **PS4 skeleton + skin + runtime-rig + two animation clips validated on retail bytes; target `816CE09A` visible ownership now independently proven; general clip schema still incomplete**  
Target: final-era Destiny 1 / Rise of Iron Tiger v24.

## D1 entity -> skeleton chain

D1 ROI entities point to outer `EntityResource` tags whose package reference
class is `0x80800861`.

A skeleton EntityResource is distinguished by its `+0x10` ResourcePointer
resolving to D1 skeleton discriminator class:

- outer EntityResource: `0x80800861`
- skeleton discriminator: `0x808006BD`
- skeleton-info resource at EntityResource `+0x18`: `0x8080049A`

These class relationships come from source correlation and are now validated
against resident PS4 Rise of Iron bytes from the Vex `0767` family.

## D1 skeleton-info layout

D1 skeleton-info struct size: `0xE0`.

Dynamic-array headers:

```text
+0x88 NodeHierarchy
+0x98 DefaultObjectSpaceTransforms
+0xA8 DefaultInverseObjectSpaceTransforms
+0xB8 RangeIndexMap
+0xC8 InnerIndexMap
```

### Node element (`0x10` bytes)

```text
+0x00 u32 NodeHash
+0x04 s32 ParentNodeIndex
+0x08 s32 FirstChildNodeIndex
+0x0C s32 NextSiblingNodeIndex
```

### Object-space transform (`0x20` bytes)

```text
+0x00 float4 Rotation quaternion
+0x10 float4 Translation.xyz + Scale.w
```

The project parser reconstructs node hashes, topology, default object-space and
inverse object-space transforms, and range/inner index maps.

## Retail PS4 validation: `816CE092 / 816CE095 / 816CE09A / 816CE09D-E`

Canonical articulated cluster:

- skeleton EntityResource `816CE092`
- **12 skeleton nodes**
- runtime rig EntityResource `816CE095`
- runtime-rig discriminator/info `0x808008B2 -> 0x8080099B`
- runtime component hash `76F7A98E`
- **12 controls**
- bone -> control mapping `0..11`
- control -> bone mapping `0..11`
- model `816CE09A`
- animation clip `816CE09D`, animation hash `6FB760FF`, 31 frames, static tracks
- animation clip `816CE09E`, animation hash `D3FD602F`, 101 frames
- `816CE09E`: 12 nodes, 3 rotated tracks, 7 translated tracks in the validated export

The model was successfully exported with:

- 4,172 vertices
- D1 triangle-strip/restart conversion
- 5,336 triangles
- UV0 and normals
- `JOINTS_0 / WEIGHTS_0`
- 12-joint glTF skin
- retail inverse bind matrices
- both decoded clips targeting the same 12 joints

This proves the parser/export path for this concrete PS4 cluster. It does **not**
mean every D1 `s_animation_clip` compression mode is globally solved.

## `816CE09A` is also a byte-proven visible model

An earlier project phase treated `816CE09A` only as an animation-bundle/proxy
geometry fixture because it sits next to `0x8080222A` wrapper `816CE099`.
That conclusion is superseded.

Higher retail patch namespace exposes ordinary EntityResource `816CE12B` with
the standard D1 model-parent chain:

```text
816CE12B  EntityResource 80800861
  +0x10 -> 80801A80
  +0x18 -> 80801A9C model parent
                 |
                 +-- model = 816CE09A
```

The same parent has a normal external-material bank and material maps. Its
default visible bindings are independently solved:

```text
VariantShaderIndex 0 -> 809C475F
VariantShaderIndex 1 -> 816CE240
```

Therefore:

- adjacency to an animation-bundle wrapper **does not imply that the model is
  non-visible**;
- `816CE09A` participates in an animation bundle **and** has an ordinary standard
  visible render owner;
- visible ownership and animation-bundle membership are independent graph roles.

The prior rule “positive `0x8080222A` classification => final render model false”
is invalid and must not be used for exclusion.

## `0x8080222A` animation-bundle/wrapper pattern — retained but narrowed

Retail bytes still prove a recurring animation-oriented neighborhood:

```text
0x8080222A structured wrapper
    -> nearby s_entity_model
    -> Havok hk_2012.2.0-r1 data
    -> control/wrapper data
    -> s_animation_clip(s)
```

Target wrapper `816CE099` contains aligned dword `D3FD602F`, exactly the
validated animation hash of `816CE09E`. Equivalent clusters occur in `00E2`.

Safe conclusion:

- observed semantic role: **animation-bundle/wrapper pattern**;
- original Bungie class name: unknown;
- internal field schema: unresolved;
- wrapper adjacency alone says nothing definitive about whether the nearby model
  also has a standard visible owner elsewhere.

Reusable classifier:

- `tools/d1_animation_bundle_probe.py`

Any field/report named `final_render_model_proven=false` in older classifier
output should be interpreted only as “this classifier did not prove render
ownership,” **not** as evidence that render ownership is false. A future cleanup
should rename that output to remove the ambiguity.

## Proxy-family comparison fixture: `809C4B97`

`ps4_arch_vex_00e2_0.pkg` contains a useful structural analogue:

- skeleton `809C4B90`: **8 bones**
- runtime rig `809C4B93`: `0x808008B2 -> 0x8080099B`
- composition `809C4B94`: `0x8080079A -> 0x80800610`
- wrapper `809C4B96`: `0x8080222A`
- model `809C4B97`: 4,207 vertices
- Havok payload `809C4B98`
- clips `809C4B99/9A/9B`

This remains a high-value format comparison fixture. Its eight-node companion
skeleton makes it incompatible as a direct target for the 12-control
`816CE09D/E` clips.

## Skinning relation

The `816CE09A` validation proves that D1 packed bone indices/weights can be
mapped through the decoded skeleton into glTF skinning for the current PS4
layout. General exporters must still retain raw provenance and index-map data
because other skeleton families may require non-identity remapping.

For new models:

1. decode vertex weight/index streams;
2. decode the exact skeleton EntityResource;
3. preserve `RangeIndexMap` / `InnerIndexMap`;
4. prove any required index remapping from bytes;
5. build glTF `skin.joints` and inverse-bind matrices;
6. validate bind-pose geometry before animation.

## Cross-source skeleton corroboration

Historical tooling independently uses the same 0x10 node record and 0x20
transform record and includes standard body/weapon mechanism hashes such as
`GunBase`, `Hammer`, `MagRelease`, `Trigger`, `CraneRotate`, `CraneExtend`,
`Cylinder`, and `Magazine`.

Those names remain cross-generation/source leads until validated on the specific
D1 weapon bytes being exported.

## Animation class

Final D1 ROI class:

```text
0x808005A1 = s_animation_clip
```

Two concrete PS4 clips (`816CE09D/E`) have been decoded and exported against the
12-node rig. The full reusable clip decoder used during the successful runtime
investigation has **not yet been promoted into the committed tool tree**, so the
general animation-track layout remains partially unresolved.

The supplied Xbox Cabal patch-1 package has 22 clip entries but they require
patch 0 and therefore still cannot independently validate Xbox clip decoding.

## General animation RE requirements

For each new clip family retain a loss-preserving path and verify:

1. duration/frame-count/sample-rate representation;
2. animated-node index tables and skeleton-node mapping;
3. translation, rotation and scale tracks;
4. constant/static channels vs sampled channels;
5. quantization/compression mode;
6. interpolation and frame timing;
7. bind/reference-pose behavior;
8. raw unknown track blobs until semantics are complete.

Decoded channels should be emitted to project JSON/provenance before glTF
animation samplers/channels are treated as canonical.

## Current frontier

For the target `816CE09A`, visible-model identification is no longer a frontier.
We now have independently proven:

```text
visible parent/material owner: 816CE12B
model:                         816CE09A
skeleton:                      816CE092
runtime rig:                   816CE095
clips:                         816CE09D / 816CE09E
materials:                     809C475F / 816CE240
```

The active animation engineering target is to **promote the successful clip +
skin export into reusable code** and combine it with the now-solved material /
texture pipeline.

Immediate deliverable target:

```text
816CE12B owner
  -> 816CE09A geometry
  -> 816CE092 skin
  -> 816CE095 control mapping
  -> 816CE09D/E animations
  -> 809C475F + 816CE240 materials
  -> exact retail textures/samplers/constants
  -> loss-preserving glTF/GLB approximation
```

## Remaining high-value inputs

- the already recoverable `0767` package family for durable clip-decoder
  reconstruction and regression tests;
- Xbox patch 0 for independent Xbox animation validation;
- additional PS4 weapon/skeleton families to prove non-identity control and
  weapon-mechanism mappings.
