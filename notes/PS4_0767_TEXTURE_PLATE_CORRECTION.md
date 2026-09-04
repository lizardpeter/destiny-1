# PS4 0767 texture-plate correction

Date: 2026-09-03/04
Fixture: `ps4_arch_vex_com01_0767_0.pkg`
Model: `816CE09A`

## Why this checkpoint exists

A Blender validation screenshot falsified the first provisional texturing attempt. The file `816CE09A_816CE092_multi_animation_rigged_TEXTURED_INFERRED.glb` had treated texture `816CE138` as direct glTF base color on the model's transformed/tiled UV0. That produced giant black/white strips and visibly incorrect sampling.

The mesh, skeleton, skinning, and animations were not implicated. The error was the material/texture-coordinate binding.

## Confirmed D1 UV transform used by Charm

Charm source confirms D1 entity model UV transformation:

```text
UV0.x = raw.x * scale.x + translation.x
UV0.y = raw.y * -scale.y + 1 - translation.y

UV1.x = raw.x * scale.x * 5 + translation.x * 5
UV1.y = raw.y * -scale.y * 5 + 1 - translation.y * 5
```

So `UV1.x = 5*UV0.x` and `UV1.y = 5*UV0.y - 4`.

For `816CE09A`, the mesh metadata is:

```text
TexcoordScale       = (3.2610001564, 3.2610001564)
TexcoordTranslation = (0.7239000797, 1.5973000526)
```

The transformed UV set is deliberately tiled and ranges far outside 0..1. This is not a suitable direct atlas coordinate for `816CE138`.

## Strong texture-plate association discovered

The resident texture cluster contains two BC3/BC5 plate-like pairs:

```text
816CE0B6  1024x1024 BC3
816CE0B7  1024x1024 BC5
816CE0B8  1024x1024 BC3
816CE0B9  1024x1024 BC5
```

`816CE0B8` is visually a Vex architectural color atlas matching the geometry class of `816CE09A`; `816CE0B9` is the matching BC5 normal plate.

A differential occupancy test provides much stronger evidence than visual similarity. The packed final two int16 values from stride-12 VB0 were converted to signed-normalized values and remapped to an atlas domain:

```text
plate_u = raw_snorm_u * 0.5 + 0.5
plate_v = raw_snorm_v * 0.5 + 0.5
```

Sampling the BC3 alpha occupancy at model vertices gives:

### `816CE0B8` occupancy hit rate

```text
816CE09A  0.7884
816CE0C5  0.3237
816CE0C6  0.2057
```

### `816CE0B6` occupancy hit rate

```text
816CE09A  0.5518
816CE0C5  0.7631
816CE0C6  0.8009
```

This is a strong cross-model discriminator:

- `B8/B9` preferentially match `09A`.
- `B6/B7` preferentially match neighboring models `0C5/0C6`.

Therefore the previous `816CE138` direct-base-color binding is rejected, and `816CE0B8/0B9` are now the leading texture-plate pair for `816CE09A`.

## Material-family correction

The earlier `816CE17F` external-material inference is also rejected as the direct appearance material for `09A`.

Important material pairs found in retail bytes:

```text
816CE0B3: VS 80AAE147, PS 816CE0F3
816CE0C7: VS 80AAE149, PS 816CE0F3
```

These two share the same pixel shader and the same 8-texture set, while using different vertex shaders. This is consistent with skinned/non-skinned vertex-shader variants.

`816CE17F` uses VS `80AAE149` and the same PS `816CE0F3`, but changes the detail pair to `816CE118/816CE119`, which visually decode as a gray rocky material. Applying that appearance family to `09A` was therefore not justified.

`816CE0B3` instead uses:

```text
slot0  80AACED2
slot1  816CE138
slot2  816CE17D   (brown/rust/copper detail color)
slot3  80AA9F35   (external; likely paired normal/detail resource)
slot4  8166A984
slot5  80AACED3
slot6  8166A985
slot7  80AACF1D
```

A second material `816CE0B4` uses the resident pair `816CE0EF/816CE0F0` and is another plausible specialized pass for this asset family.

These shader/material observations remain separate from the newly evidenced B8/B9 texture-plate binding; the exact PS4 shader combination is still under reversal.

## Corrected GLB candidate

A new validation export was built from the clean rigged + multi-animation GLB, not from the rejected provisional file:

```text
816CE09A_RIGGED_ANIMATED_TEXTURE_PLATE_CORRECTED_CANDIDATE.glb
SHA-256: 92a0a7f6ca94aa4e0ed47ea56c777d3f42eca5dd30869243599ce57098d828bf
```

It preserves:

- 4,172 vertices
- 5,336 triangles
- 12-joint skin
- animations `816CE09E` and `816CE09D`
- transformed D1 UV0 for later shader/detail reconstruction

It adds a separate atlas UV set derived from packed SNORM coordinates and binds `816CE0B8` as the candidate color texture plate. The candidate intentionally does **not** claim final shader-faithful PBR reconstruction yet.

## Current confidence boundary

CONFIRMED:

- first provisional `816CE138` direct-base-color binding is wrong;
- D1 transformed/detail UV equations above match Charm source;
- `B8` is a dramatically stronger atlas-occupancy match to `09A` than to `0C5/0C6`;
- `B6` shows the opposite preference and matches `0C5/0C6` much better;
- `B8/B9` form a coherent BC3/BC5 color/normal pair;
- `B3/C7` share PS + full texture set but differ in VS.

STRONGLY SUPPORTED, NOT YET SHADER-DECOMPILE CONFIRMED:

- `816CE0B8/816CE0B9` are the 09A color/normal texture plates;
- the plate coordinate path is `raw_snorm * 0.5 + 0.5`;
- `816CE0B3` is a skinned material-family counterpart relevant to the 09A render context.

UNRESOLVED:

- exact parent ExternalMaterialsMap for `09A`;
- exact PS4 pixel-shader sampling/compositing semantics for `816CE0F3`;
- final role of global slots from packages 0154/0156/0735;
- exact use of `816CE0B4` / `816CE0EF` / `816CE0F0`;
- BC5 tangent-space handedness needed for final glTF normal-map conversion.

## Xbox shader cross-check attempt

A temporary GitHub Actions probe tested the known public mirror stems `xbox`, `xboxone`, and `xb1` for an Xbox package manifest. All returned HTTP 404, so no Xbox counterpart was recovered through that mirror. This does not affect the PS4 texture-plate evidence above.
