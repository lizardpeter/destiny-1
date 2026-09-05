# D1 Tower top-shader dataflow — phase 2

Date: 2026-09-05

This continues `notes/TOWER_TOP_SHADER_DATAFLOW.md` using the completed 40/40
retail PS4 shader corpus and the fail-closed native descriptor-provenance pass.
The analyzer now maps all 126 decoded `image_*` instructions to exact D1 t#
resources with zero unmatched instructions.

## `80CA0DD5` — 12 visible materials

Native resource use:

```text
0x118  image_sample    t2, dmask:Y
0x138  image_get_lod   t1, dmask:Y
0x180  image_sample_l  t1, dmask:RGBA
0x188  image_sample    t0, dmask:RGB
```

The shader explicitly builds a cube direction using `v_cubema_f32`,
`v_cubetc_f32`, `v_cubesc_f32` and `v_cubeid_f32`, then queries and samples t1
with explicit LOD. Therefore t1 is instruction-proven as the environment cube.

`t2.y` enters the minimum/reflection LOD path and later both reflection strength
and deferred-normal packing. The normal pack branch computes the same
`0.375 + 0.125 * control` scale already seen in other Tower surface families.
`t0.rgb` is the authored surface RGB source mixed with the sampled environment.

```text
t0 -> surface_rgb                                                PROVEN
t1 -> environment_cubemap                                       PROVEN
t2 -> reflection_lod_intensity_and_deferred_normal_control_y     PROVEN
```

## `80AAE2AD` — 11 visible materials

Native resource use:

```text
0x118  image_sample    t3, dmask:Y
0x138  image_get_lod   t1, dmask:Y
0x188  image_sample    t0, dmask:RGB
0x190  image_sample    t2, dmask:XZ
0x198  image_sample_l  t1, dmask:RGB
```

Again, t1 is used through native cube-coordinate instructions and explicit LOD.
The t2 sample returns X and Z only. Native MAD instructions at `0x1b4..0x1c4`
apply exactly:

```text
adjusted_rgb = t0.rgb * t2.z + t2.x
```

`t3.y` follows the same reflection/deferred-normal control path as `80CA0DD5`.

```text
t0 -> surface_rgb                                                PROVEN
t1 -> environment_cubemap                                       PROVEN
t2 -> surface_rgb_bias_x_scale_z                                 PROVEN
t3 -> reflection_lod_intensity_and_deferred_normal_control_y     PROVEN
```

## `80AADCA6` — 6 visible materials

Native resource use:

```text
0x030  image_sample    t1, dmask:XY
0x1a8  image_sample    t0, dmask:RGBA
0x1cc  image_get_lod   t2, dmask:Y
0x21c  image_sample_l  t2, dmask:RGBA
```

`t1.xy` is converted to signed XY, followed by
`sqrt(max(0, 1-x*x-y*y))`, transformed through the interpolated tangent basis
and normalized. That is an instruction-proven two-channel tangent normal.

The shader computes a reflected cube direction and explicit LOD for t2, proving
t2 as the environment cubemap. `t0.rgb` supplies the authored surface color.
`t0.a` enters the environment LOD/intensity branch and the deferred-normal pack
scale (`0.375 + 0.125 * t0.a`).

```text
t0 -> surface_rgb_alpha_reflection_and_deferred_normal_control   PROVEN
t1 -> primary_normal_rg                                          PROVEN
t2 -> environment_cubemap                                        PROVEN
```

## `8093EB1C` — 4 visible materials

Native resource use:

```text
0x030  image_sample    t1, dmask:XY
0x040  image_sample    t0, dmask:RGBA
0x04c  image_sample    t2, dmask:X
```

`t1.xy` follows the exact signed XY + reconstructed +Z tangent-normal path.
`t0.rgb` contributes to MRT0 and `t0.a` controls the normal-pack magnitude.
`t2.x` interpolates the authored RGB branch toward a material-constant color
branch; it is a scalar color-mix control rather than a direct color image.

```text
t0 -> surface_rgb_alpha_deferred_normal_control                  PROVEN
t1 -> primary_normal_rg                                          PROVEN
t2 -> surface_rgb_mix_control_x                                  PROVEN
```

## `80AAE1AC` — 5 visible materials

Only texture operation:

```text
0x02c  image_sample t0, dmask:A
```

The sampled alpha is compared against a material constant and used to remove
lanes from the execution mask. Surviving pixels output constant `1.0` in MRT0.
No sampled RGB reaches output.

```text
t0 -> alpha_test_mask_a                                          PROVEN
```

This shader must not be flattened by a generic `t0 -> baseColor` rule.

## `80CA08C4` — 5 visible materials

Only texture operation:

```text
0x054  image_sample t0, dmask:A
```

The alpha sample, after an authored UV transform, multiplies a material-authored
RGB vector and global intensity constants before MRT0. The texture's RGB
channels are never sampled.

```text
t0 -> material_rgb_intensity_mask_a                              PROVEN
```

Again, BC3 storage does not make this a base-color texture.

## `809DCD66` — 24 visible materials

Native resource use:

```text
0x110  image_sample t0, dmask:R   # base UV
0x118  image_sample t1, dmask:R   # view-dependent displaced UV
```

The first scalar is clamped and used to interpolate between material-authored
RGB palette endpoints. The second scalar is sampled after a view-dependent UV
displacement and multiplies the resulting RGB. Neither texture contributes RGB
channels directly.

```text
t0 -> base_uv_palette_scalar_r                                   PROVEN
t1 -> parallax_displaced_rgb_modulation_scalar_r                 PROVEN
```

A faithful portable adapter for this family needs the material constant vectors;
binding either source image directly as glTF base color would be incorrect.

## Coverage after phase 2

The centralized instruction-proven table is now in
`tools/d1_shader_texture_roles.py`.

On the current 472-material Tower corpus:

```text
207 / 472 visible materials have an instruction-proven direct RGB base source
 95 / 472 visible materials have an instruction-proven primary BC5 normal
```

On the current corrected three-cell scene (773 geometry variants / 4,702
placements), the exact direct-preview roles correspond to:

```text
404 / 773 geometry variants with PROVEN direct base-color source
2,718 / 4,702 placements with PROVEN direct base-color source

369 / 773 geometry variants with PROVEN primary normal
2,552 / 4,702 placements with PROVEN primary normal
```

These counts refer only to roles that can be mapped directly into the portable
preview. Additional visible materials have exact native scalar/palette/mask or
cubemap semantics but require shader emulation instead of a direct PBR slot.
