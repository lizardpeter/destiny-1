# D1 Spektar Pandion — exact shared glove/collar static checkpoint

Date: 2026-09-06

This note closes the missing-hand/shared-glove-collar material checkpoint without changing the already visually confirmed geometry.

## Source ownership

The source-proven chain is:

```text
80A6A022  s_entity
  -> 80A6A125  EntityResource
     -> 80A6A345  shared player glove/collar s_entity_model
```

The exact retail player skeleton used by the current Guardian checkpoint is `80AD27B2`. Independent comparison against Bungie's published 72-node player skeleton proved exact ordered node hashes, exact ordered parent indices, and matching default/inverse bind transforms within the locked tolerance.

## ExternalMaterialsMap closure

The two highest-detail `80A6A345` stage parts whose inline material field is `FFFFFFFF` are not material-less. Their owning `80A6A125` EntityResource contains the D1 external-material map/bank required by the retail `VariantShaderIndex` path.

Exact results:

```text
mesh 0  range 0 / 1365     LOD 1  stage group 0  variant 0
  FFFFFFFF -> 80A6A3F9

mesh 2  range 1192 / 23    LOD 1  stage group 0  variant 2
  FFFFFFFF -> 80A6A400
```

A separate serialized LOD-8-only range also resolves correctly but is not active in the normal highest-detail visual selection:

```text
mesh 2  range 1184 / 7     LOD 8  variant 1
  FFFFFFFF -> 80A6A400
```

The external material map has three entries with starts 0, 7, and 14 and seven materials per variant. Variant 0 begins at `80A6A3F9`; variants 1 and 2 begin at `80A6A400`.

The external materials themselves were decoded exactly:

```text
80A6A3F9  VS 80AAD091  PS 80AD28F6
80A6A400  VS 80AAE149  PS 80AD28F6

PS texture order for both:
80A6A76C, 80A6A76D, 80A0856C, 80A6A76E
```

Thus the external variants directly consume the exact glove diffuse/normal/scratch family plus `80A0856C`; no heuristic redirect to another inline material is required.

## Exact visible stage-group-0 surface map

`ELod.IsHighestLevel` remains `{0,1,2,3,10}` and the source stage-part grouping is preserved. The normal visual checkpoint exposes exactly nine stage-group-0 ranges:

| Model range | Active material |
| --- | --- |
| mesh0 `0 / 1365` | `80A6A3F9` |
| mesh0 `1366 / 7678` | `80A6A766` |
| mesh0 `9045 / 8757` | `80A6A766` |
| mesh0 `17803 / 268` | `80A6A767` |
| mesh0 `18072 / 268` | `80A6A767` |
| mesh2 `49 / 547` | `80A6A76A` |
| mesh2 `639 / 544` | `80A6A76A` |
| mesh2 `1192 / 23` | `80A6A400` |
| mesh2 `1405 / 53` | `80A6A76B` |

The other nine serialized model ranges remain scene-unreachable. They are retained for forensic completeness but are not rebound or re-enabled.

## Exact static material texture arrays

The four historical/static hand/collar materials retain their exact serialized PS texture order:

```text
80A6A766:
  80A6A76C, 80A6AC9C, 80A6A76D, 80A6AC9D, 80A6A76E

80A6A767:
  80A6A76C, 80A6AC9E, 80A6A76D, 80A6AC9F, 80A6A76E

80A6A76A:
  80A6ACA0, 80A6ACA1

80A6A76B:
  80A6A76C, 80A6AC9C, 80A6A76D, 80A6AC9D, 80A6A76E
```

All nine exact PS4 image chains were decoded with no fallback substitution:

- `80A6A76C` — player gloves diffuse, 1024x1024
- `80A6A76D` — player gloves normal, 1024x1024
- `80A6A76E` — player gloves scratch/control texture, 1024x1024
- `80A6AC9C` / `80A6AC9D` — exact detail diffuse/normal pair
- `80A6AC9E` / `80A6AC9F` — exact alternate detail diffuse/normal pair
- `80A6ACA0` / `80A6ACA1` — exact collar diffuse/normal pair, 1024x512

For the portable Blender checkpoint, only source-proven base diffuse and normal roles are translated into ordinary glTF PBR slots. The native D1 detail/scratch/gear-stack arithmetic is not approximated; the exact source texture identities remain preserved in evidence/artifact metadata.

## Exact source skin attributes

The nine active component ranges were mapped back to their exact retail index ranges and primary vertex bytes. `JOINTS_0` / `WEIGHTS_0` were reconstructed without synthesized influences.

Locked result:

```text
active primitives: 9
bound source vertices: 7,891
node-count limit: 72
used bone domain: 18..71 with the exact sparse set recorded in the report
```

The component geometry then receives the already-proven Tiger-to-glTF basis permutation:

```text
[x, y, z] -> [y, z, x]
```

No node offsets or hand repositioning are applied.

## Final Blender checkpoint

Workflow:

```text
D1 Spektar exact glove-collar static v1
run 34049265556
head f185c141b72c9469beefa8e9654f8a7d0a6be1a6
```

Artifact:

```text
D1-SPEKTAR-EXACT-GLOVE-COLLAR-STATIC-V1
artifact id 9994048656
artifact sha256 199cd573a8fb2b9782543606fd1de9a22bcc032b1c253d2c8d8c743919471bd0
```

Primary GLB:

```text
SPEKTAR_PANDION_TITAN_BUNGIE72_EXACT_GLOVE_COLLAR_STATIC_V1.glb
48,604,336 bytes
sha256 ad74e32f3c2802db50080eff4be8e89e44f1e4cd4feaa16ad8c87811782419d4
```

Final invariants:

```text
active shared glove/collar scene ranges = 9
retained dormant matching ranges         = 9
skin count                               = 1
skin joints                              = 72
animation count                          = 0
```

The first workflow attempt correctly exposed a portability adapter bug: the post-merge skin binder scanned all serialized matching nodes and encountered dormant `mesh1_range0_171`, which intentionally had no restored source skin attributes. The binder was corrected to use active-scene reachability as authoritative. Dormant LOD/pass nodes are now explicitly recorded and untouched.

## Proof boundary

This checkpoint does **not**:

- re-enable `_0/_1` or other dormant serialized ranges;
- invent hand placement, wrist offsets, or bone transforms;
- synthesize skin weights;
- reuse the old 67-joint animation;
- claim that glTF PBR reproduces the native D1 detail/scratch/gear-stack shader.

The previous published preview animation was intentionally stripped from this checkpoint. A final animated player build remains gated on source-proven retail player animation ownership/selection/retargeting through the 72-node player architecture.
