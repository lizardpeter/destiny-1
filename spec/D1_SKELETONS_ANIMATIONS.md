# Destiny 1 Skeletons and Animations — Living Specification

Status: **skeleton parser ready/source-correlated; real resident skeleton still needed; animation payload not yet decoded**  
Target: final-era Destiny 1 / Rise of Iron Tiger v24.

## D1 entity -> skeleton chain

D1 ROI entities point to outer `EntityResource` tags whose package reference class is `0x80800861`.

A skeleton EntityResource is distinguished by its `+0x10` ResourcePointer resolving to D1 skeleton discriminator class:

- outer EntityResource: `0x80800861`
- skeleton discriminator: `0x808006BD`
- skeleton-info resource at EntityResource `+0x18`: `0x8080049A`

These class relationships come from Charm's D1 schema/consumer and are encoded in `tools/d1_skeleton_probe.py`. The current supplied Xbox patch contains 119 resident EntityResource tags but **zero resident skeleton resources**; its relevant skeleton data is expected across the missing patch-0 boundary.

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

The project parser reconstructs:

- bone/node hashes
- parent, first-child, next-sibling topology
- default object-space transform
- default inverse object-space transform
- range-index and inner-index maps

The structural parser has a synthetic regression test. Direct game-byte promotion awaits a resident D1 skeleton sample.

## Cross-source skeleton corroboration

MontagueM's historical MDE skeleton code independently uses the same 0x10 node record and 0x20 transform record. Its hardcoded hash dictionary contains standard body nodes and weapon-mechanism names including:

- `GunBase`
- `Hammer`
- `MagRelease`
- `Trigger`
- `CraneRotate`
- `CraneExtend`
- `Cylinder`
- `Magazine`

This is useful evidence that weapon mechanisms are represented through the same hashed-node skeleton architecture, but the current archived MDE repository is D2-focused; these names are retained as a cross-generation/source lead rather than promoted to D1 binary fact.

## Skinning relation

D1 vertex decoding already exposes layouts containing packed weights and bone/weight indices. Once a real skeleton resource and its model are available, the next validation is:

1. decode model vertex weight/index streams.
2. map packed bone indices through `RangeIndexMap` / `InnerIndexMap` as required.
3. build glTF `skin.joints` and inverse-bind matrices.
4. verify skinned bind-pose geometry matches the unskinned model positions.

## Animation class

Final D1 ROI class:

`0x808005A1 = s_animation_clip`

The supplied Xbox `0059_1` package has 22 entries of this class, but **all 22 require patch 0**, so none can currently be reconstructed. `xboxone_arch_cabal_0059_0.pkg` is therefore the highest-value missing binary for the rig/animation frontier.

Current Charm source exposes the class identity and skeleton consumers but no obvious end-to-end D1 animation-clip decoder. Animation track layout remains a genuine RE target rather than a solved exporter feature.

## Animation RE plan once clip bytes are resident

For each clip:

1. identify file-size/header invariants and embedded resource/array markers.
2. locate duration/frame-count/sample-rate representation.
3. identify animated-node index tables and correlate to skeleton NodeHash/order.
4. locate translation, rotation and scale tracks.
5. determine constant/static channels vs sampled channels.
6. solve quantization/compression independently by reconstructing bind-pose or known idle clips.
7. export losslessly to project JSON first, then glTF animation samplers/channels.
8. retain unknown/raw track blobs alongside decoded channels until semantics are complete.

## Current blockers

- `xboxone_arch_cabal_0059_0.pkg` for the 22 known animation clips and likely skeleton resources.
- a PS4 entity/weapon package containing a complete model+skeleton pair for canonical export validation.
