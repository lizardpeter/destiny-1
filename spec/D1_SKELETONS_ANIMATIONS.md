# Destiny 1 Skeletons and Animations — Living Specification

Status: **PS4 skeleton + skin + runtime-rig + two animation clips validated on retail bytes; general clip schema still incomplete**  
Target: final-era Destiny 1 / Rise of Iron Tiger v24.

## D1 entity -> skeleton chain

D1 ROI entities point to outer `EntityResource` tags whose package reference class is `0x80800861`.

A skeleton EntityResource is distinguished by its `+0x10` ResourcePointer resolving to D1 skeleton discriminator class:

- outer EntityResource: `0x80800861`
- skeleton discriminator: `0x808006BD`
- skeleton-info resource at EntityResource `+0x18`: `0x8080049A`

These class relationships come from Charm's D1 schema/consumer and are encoded in `tools/d1_skeleton_probe.py`. They are now also validated against resident PS4 Rise of Iron bytes from `ps4_arch_vex_com01_0767_0.pkg`.

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

The structural parser has both synthetic regression coverage and successful retail-byte validation on the 12-node Vex skeleton `816CE092`.

## Retail PS4 validation: `816CE092 / 816CE095 / 816CE09D-E`

The current canonical articulated validation cluster is in `ps4_arch_vex_com01_0767_0.pkg`:

- skeleton EntityResource `816CE092`
- **12 skeleton nodes**
- runtime rig EntityResource `816CE095`
- runtime-rig discriminator/info `0x808008B2 -> 0x8080099B`
- validated runtime component hash `76F7A98E`
- **12 controls**
- bone -> control mapping `0..11`
- control -> bone mapping `0..11`
- animation clip `816CE09D`, animation hash `6FB760FF`, 31 frames, static tracks
- animation clip `816CE09E`, animation hash `D3FD602F`, 101 frames
- `816CE09E`: 12 nodes, 3 rotated tracks, 7 translated tracks in the validated export

The mesh `816CE09A` was successfully exported with:

- 4,172 vertices
- D1 triangle-strip/restart conversion
- 5,336 triangles
- UV0 and normals
- `JOINTS_0 / WEIGHTS_0`
- 12-joint glTF skin
- retail inverse bind matrices
- both decoded clips applied successfully

This proves the parser/export path for this concrete PS4 cluster. It does **not** mean every D1 `s_animation_clip` field or compression mode is now generally solved.

## Critical render-role correction: animation proxy vs visible model

`816CE09A` must not be treated as an ordinary final render-owned entity model merely because its geometry, skinning and animation decode correctly.

It is immediately preceded by structured class `0x8080222A` (`816CE099`). Retail comparison against `ps4_arch_vex_00e2_0.pkg` shows the same recurring sequence around multiple special articulated assets:

```text
0x8080222A wrapper
    -> s_entity_model
    -> Havok hk_2012.2.0-r1 payload
    -> animation/control wrapper(s)
    -> s_animation_clip(s)
```

For target wrapper `816CE099`, an aligned dword equals `0xD3FD602F`, exactly the validated animation hash of clip `816CE09E`. An equivalent `00E2` wrapper contains another clip hash in the corresponding observed position.

The project therefore uses the cautious semantic label **animation-bundle/proxy wrapper pattern** for class `0x8080222A`. This is an observed retail role, **not a claim of Bungie's original type name or a solved field schema**.

Reusable classifier:

`tools/d1_animation_bundle_probe.py`

The classifier is intentionally schema-free. It uses:

- exact wrapper class `0x8080222A`;
- forward entry order and class identities;
- nearby `s_entity_model` and `s_animation_clip` entries;
- literal `hk_2012.2.0-r1` payload evidence;
- already-proven EntityResource role decoding;
- raw aligned-dword correlation against nearby TagHashes;
- optional caller-supplied known animation hashes.

A positive proxy-pattern classification explicitly sets `final_render_model_proven = false`. Final visible render ownership still requires a separate ordinary model-parent/entity/material chain.

## Proxy-family comparison: `809C4B97`

`ps4_arch_vex_00e2_0.pkg` contains a close structural analogue:

- skeleton `809C4B90`: **8 bones**
- runtime rig `809C4B93`: `0x808008B2 -> 0x8080099B`
- composition `809C4B94`: `0x8080079A -> 0x80800610`
- wrapper `809C4B96`: `0x8080222A`
- model `809C4B97`: 4,207 vertices, same 12/16-byte vertex-buffer family
- Havok payload `809C4B98`
- clips `809C4B99/9A/9B`

This is strong format corroboration for the proxy-bundle pattern, but it is **not a direct retarget target** for the 12-control `816CE09D/E` clips: its companion skeleton has only 8 nodes.

## Skinning relation

The `816CE09A` validation proves that D1 packed bone indices/weights can be mapped through the decoded skeleton into glTF skinning for at least the current PS4 layout. The general exporter should still retain raw provenance and index-map data because other skeleton families may use different or non-identity remapping.

For new models:

1. decode vertex weight/index streams;
2. decode the exact skeleton EntityResource;
3. preserve `RangeIndexMap` / `InnerIndexMap`;
4. prove any required index remapping from bytes;
5. build glTF `skin.joints` and inverse-bind matrices;
6. validate bind-pose geometry before applying animation.

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

This remains useful evidence that weapon mechanisms are represented through the same hashed-node skeleton architecture, but the archived MDE repository is D2-focused; these names are retained as a cross-generation/source lead rather than promoted to universal D1 binary fact.

## Animation class

Final D1 ROI class:

`0x808005A1 = s_animation_clip`

The current project has decoded and exported two concrete PS4 clips (`816CE09D/E`) from the Vex cluster. The full reusable `s_animation_clip` field/compression decoder used during that runtime investigation has **not yet been promoted into the committed tool tree**, so general animation-track layout remains partially unresolved.

Separately, the supplied Xbox `xboxone_arch_cabal_0059_1.pkg` has 22 `s_animation_clip` entries but all require patch 0, so that package still cannot independently validate Xbox clip reconstruction.

## General animation RE requirements

For each new clip family, retain a loss-preserving path and verify:

1. duration/frame-count/sample-rate representation;
2. animated-node index tables and skeleton-node mapping;
3. translation, rotation and scale tracks;
4. constant/static channels vs sampled channels;
5. quantization/compression mode;
6. interpolation and frame timing;
7. bind/reference-pose behavior;
8. raw unknown track blobs until semantics are complete.

Decoded channels should be emitted to project JSON/provenance before glTF animation samplers/channels are treated as canonical.

## Current frontier

The immediate PS4 problem is no longer “find textures for `816CE09A`.” The byte evidence says `09A` is an animation proxy.

The current target is:

> identify an **ordinary visible Vex model parent + model + skeleton/control cluster** compatible with the proven 12-node / 12-control `816CE092 / 816CE095` rig, then retarget `816CE09D/E` only after compatibility is byte-proven.

`809C44A5 -> 809C47F4` in `00E2_0` is the strongest currently proven ordinary visible/material control fixture, but its 12-control compatibility remains unproven.

Use `tools/d1_animation_proxy_compat_probe.py` to rank ordinary candidates when the base package corpus is available.

## Remaining high-value inputs

- `ps4_arch_vex_00e2_0.pkg` and `ps4_arch_vex_com01_0767_0.pkg` in the active runtime, to execute the new compatibility census against the already-known base bytes.
- `ps4_arch_vex_com01_0767_1.pkg` / `_4.pkg` if available from the user's archive; the public mirror listed them but returned HTTP 404.
- `xboxone_arch_cabal_0059_0.pkg` for the 22 known Xbox clips and likely additional skeleton resources.
