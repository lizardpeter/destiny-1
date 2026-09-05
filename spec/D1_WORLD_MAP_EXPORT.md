# Destiny 1 World / Map Export Pipeline — Living Specification

Status: **Tower baked-static placement/visibility solved; affine/UV record correction solved; exact visible material texture extraction underway.**  
Target: a reusable final-era D1/Rise of Iron exporter that can reconstruct every world/map without Tower-specific guesses.

## Design rule

The canonical representation is lossless D1 source data. glTF/Blender is an adapter.
Do not mutate source semantics merely to make one viewer look correct.

## Layer 1 — package / Tiger resource resolution

- D1 v24 TagHash construction is solved.
- current physical patch siblings are resolved as one logical package family;
- current-generation/class-stable cross-package resource selection is fail-closed;
- serialized-coverage sized Oodle block reader handles partial logical blocks.

## Layer 2 — map ownership / static cells

- identify map-owned `StaticMapData -> StaticMapData_D1 -> StaticTable` chains;
- preserve the exact map-data-table / parent chain establishing ownership;
- never infer world ownership from package filename or successful mesh decoding alone.

Tower fixture: 9 validated baked-static cells, 40,373 serialized placements.

## Layer 3 — retail visibility

D1 `StaticMapData_D1.GetStatics()` visual gate:

```text
DetailLevel in {0,1,2,3,10}
AND
material.Unk08 == 1
```

Tower fixture: 40,373 serialized -> 9,360 retail-visible placements.

## Layer 4 — baked-static instance record

A D1 baked-static instance is a 0x40-byte record, **not** a homogeneous 4x4 matrix:

```text
+0x00..+0x2F  float3x4 affine SRT transform
+0x30         float UV scale
+0x34         float UV translate X
+0x38         float UV translate Y
+0x3C         unknown/tail; not a homogeneous matrix element
```

Canonical affine matrix synthesizes final row `[0,0,0,1]`.

Per-instance UV application:

```text
u = u * scale + translateX
v = v * (-scale) + 1 - translateY
```

Tower fixture: 1,743 visual geometry variants; 1,742 use exactly one UV transform
across all visible placements, and one uses two. Therefore glTF can retain almost
all instancing while baking the UV transform per exported geometry variant.

## Layer 5 — coordinate adapters

D1 world space is retained canonically as Z-up.

glTF adapter:

```text
D1 Z-up -> glTF Y-up
[ 1  0  0  0 ]
[ 0  0  1  0 ]
[ 0 -1  0  0 ]
[ 0  0  0  1 ]
```

Blender then performs its standard glTF Y-up -> Blender Z-up import conversion.
No per-object cosmetic rotation is part of the source data.

## Layer 6 — static vertex attributes

Source-crosschecked D1 Static layouts currently covered:

Primary stream:
- stride 8: position
- stride 12: position + UV at +8
- stride 28: position + UV at +8 + normal at +0xC
- stride 32: position + UV at +8 + vertex colour near tail

Secondary stream:
- stride 12: UV + normal
- stride 16: normal
- stride 20: UV+normal, or normal+vertex colour if primary UV already exists
- stride 24: UV + normal with the D1 static-specific gap

Position/UV/normal packed components are signed normalized int16 / 32767 for these
layouts. Unsupported layouts fail closed.

## Layer 7 — material / shader / texture dependencies

PS4 ROI material class: `80801AD7`.

Exact material bindings are preserved as:

```text
material
  -> vertex shader
  -> VS TextureIndex t# -> Texture TagHash
  -> pixel shader
  -> PS TextureIndex t# -> Texture TagHash
  -> sampler / constant resources
```

`TextureIndex` is proven to be the shader `t#` register.

Texture resources are reconstructed through the PS4 ROI Texture2D header/stream/
backing chain, deswizzled, and exported to DDS/PNG.

Semantic rule: do not call arbitrary `t0` an albedo map. Shader/register roles are
named only after shader dataflow proves them. The exact register binding remains
usable even before the higher-level PBR interpretation is solved.

## Layer 8 — glTF material adapter

For each shader family:

1. preserve the exact D1 material recipe in glTF extras/sidecar;
2. map proven surface/normal/emissive/etc. resources to glTF PBR slots where valid;
3. preserve unsupported resources and shader constants instead of discarding them;
4. bake the D1 per-instance UV transform into a geometry variant only when required
   by glTF's lack of per-node UV-transform state.

## Layers still to integrate for complete worlds

Baked statics are only one layer of a D1 destination. A complete world exporter must
also enumerate and reconstruct, without guessed ownership:

- entity/model placements and animated/dynamic props;
- decals;
- terrain/natural geometry families;
- sky/environment resources;
- lighting/probes/environment maps;
- particles/VFX where exportable;
- activity/runtime variants and conditional scene content;
- collision/nav/physics as separate optional data products;
- locale/UI/signage content where relevant.

## Current Tower regression fixture

Tower is the first full regression world. A change is not accepted if it breaks any
of these proven invariants:

- 9 map-owned baked-static cells;
- 40,373 serialized placements;
- zero v5 geometry decode holes;
- 9,360 retail-visible placements;
- affine-only node matrices;
- exact per-instance UV metadata retained;
- D1 source Z-up retained canonically;
- visible material/texture dependencies remain exact TagHash/register relationships.
