# D1 native Tiger model / skin / animation basis closure — 2026-09-07

## Why this note exists

The Tower character work exposed a renderer-independent coordinate-basis bug that can
make a GLB mathematically self-consistent while visibly exploding or rotating a skin.
This is a format/exporter rule, not a one-model Blender workaround, and must remain
explicit in every future D1 character/weapon/animated-model exporter.

## Source boundary

The pinned animation implementation is:

- `SolUnshadowed/tiger-animation-parser@b9fdc3a43dd28118113275624fcc9054b75855f4`

Its D1 skeleton reader intentionally converts Tiger coordinates as:

```text
native Tiger [x, y, z] -> parser [y, z, x]
```

`rig_retarget()` works in that parser-space representation and
`convert_obj_to_local()` therefore returns parser-space local animation tracks.

The D1 model geometry exporters in this repository preserve source model vertex
positions in native D1/Tiger local space. World-placement basis conversion is a
separate downstream concern. Therefore parser-space joint transforms / inverse-bind
matrices / retargeted local tracks must not be attached directly to those native-D1
vertices.

## Direct Tower E/F/G proof

The old r9 articulated layer reused parser-space skeleton/animation data on native D1
geometry. Family E looked exploded in Blender even though the serialized skin data was
correct.

The structural Family-E diagnostic proved the suspected skin/index errors were not
real:

- `bone_to_control` = identity for all 67 entries;
- `control_to_bone` = identity for all 67 entries;
- source object-space × inverse-object-space maximum identity error:
  `7.051816233172303e-07`;
- current hierarchy reconstruction maximum error:
  `2.0934237583425386e-06`;
- decompose/recompose maximum error:
  `2.705409389847091e-07`;
- the source skin joint domain is unchanged by the hypothetical control-to-bone map.

The actual defect was then isolated geometrically: Family-E mesh geometry is native
D1 Z-up while the parser-converted skeleton is Y-up. The r10 adapter applies the exact
inverse basis to skeleton bind data and animation tracks before using the world
placement adapter.

Source-closed r10 checkpoint:

```text
D1_TOWER_ARTICULATED_E_F_G_ANIMATED_R10_BASIS_FIXED.glb
bytes   76,007,176
sha256  d7ba8084cebe4c2d100b37fe89dec41793249b14a99b29da37f2fbad34bfc331
workflow run 34066423705
commit 43e8135bc3b6a27dc4bcf73517d50f581201f1c5
```

Family-E geometry/skeleton weighted-centroid median distance changed from about
`1.70427` to `0.014324`, and the animation deformation maximum diagonal ratio changed
from about `2.88487` to `1.15255` without altering the source skin weights.

This is source/math closure, not a claim that every downstream viewer/importer has
visually validated the file.

## Spawned Tower actor proof

The same bug existed independently in all 13 exact spawned-actor skinned model
checkpoints. Before correction every model was tall on native geometry Z while its
parser-space skeleton was tall on Y.

The generic correction is now implemented by:

- `tools/d1_gltf_restore_native_tiger_skin_basis.py`
- `tools/d1_gltf_single_skin_geometry_alignment_probe.py`

Workflow:

```text
.github/workflows/d1-tower-spawned-actor-native-basis-r2.yml
run      34085219497
commit   8ce5d96fdae01014b1f344cd39802ec7fb78726e
artifact 10004976921
zip sha  03fb6a4a48efa0533f01edc4a6754cd0535bbc98cf21609d85533e0128f6d003
status   D1_TOWER_SPAWNED_ACTOR_NATIVE_BASIS_SKINS_CLOSED
```

All 13/13 models pass:

- geometry remains native D1 and is byte/topology unchanged;
- exact `JOINTS_0` is unchanged;
- exact retail U8 weights / exact float32(U8/255) transport are unchanged;
- joint local bind transforms are conjugated by the exact inverse parser basis;
- inverse-bind matrices are conjugated by the same basis;
- every post-correction skeleton is Z-up like its source geometry;
- every geometry/skeleton median alignment distance improves to <20% of the old
  value (actual ratios are about 0.0084–0.0162);
- global bind-identity maximum error is
  `3.1447324682076783e-06`.

Examples:

```text
80C885E3 City Frame family
  before median distance  ~1.70427
  after median distance   ~0.014324

80C88437 Shaxx family
  before median distance  ~1.81694
  after median distance   ~0.02937

808765E2 leader family
  before median distance  ~1.79657
  after median distance   ~0.02355
```

## Animation rule

A corrected native-D1 skin cannot be driven by parser-space local animation tracks.
The exact inverse basis must also be applied to every joint-targeted animation output:

```text
translation parser [x,y,z] -> native [z,x,y]
scale       parser [x,y,z] -> native [z,x,y]
rotation    R_native = P^-1 * R_parser * P
```

where `P` is the parser's native->parser axis permutation matrix.

Reusable adapters:

- `tools/d1_gltf_restore_native_tiger_animation_basis.py`
- `tools/d1_gltf_restore_native_tiger_skin_animation_basis.py`

These adapters do **not** alter animation times, interpolation, channel targets,
action/selector identity, mesh geometry, joint indices, weights, materials or texture
bindings.

## Mandatory exporter policy

For any D1 mesh using `tiger-animation-parser` skeleton or animation data:

1. State explicitly whether the model vertices are in native Tiger space or parser
   space.
2. State explicitly whether skeleton bind data is native or parser space.
3. State explicitly whether retargeted animation tracks are native or parser space.
4. Before writing a glTF skin, make those three domains agree. Do not rely only on
   `jointWorld * inverseBind == identity`; the same wrong basis can satisfy that test
   internally.
5. Preserve exact source weights. Never compensate for a basis error by remapping
   joints, changing weights, normalizing vertices, moving bones by eye, or editing the
   placement transform.
6. Run both a bind-identity test and a geometry-vs-skeleton spatial alignment canary.
7. Apply world/Tiger->portable scene basis conversion only at the explicit scene/world
   adapter boundary, not opportunistically inside skeleton parsing.

This policy applies beyond Tower NPCs: Guardians, weapons, enemies, vehicles and any
other animated D1 asset can reproduce the same failure if native model data is mixed
with parser-space skeleton/animation data.
