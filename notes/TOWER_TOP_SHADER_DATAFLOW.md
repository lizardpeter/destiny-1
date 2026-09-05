# D1 Tower common pixel-shader texture dataflow

Date: 2026-09-05

This note records instruction-level texture semantics recovered from the exact
retail PS4 Tower pixel shaders.  The inputs are the 40/40 exact native GCN
streams recovered by the Tower top-shader workflow, their Sony
`InputUsageSlot` tables, and CLRX raw GFX700 disassembly.

The important methodological rule is unchanged: texture appearance and storage
format can suggest a preview, but only native instruction dataflow promotes a
semantic role to `PROVEN`.

## Descriptor/register proof

The top-40 recovery is complete: all 40 selected pixel-shader headers and native
payloads were resolved after adding package families `0156`, `00EC` and `00EE`.
Those 40 shader families cover 313 of the Tower's 472 visible materials.

A second reusable stage, `tools/d1_gcn_image_usage_analyze.py`, now follows the
actual Sony user-data layout rather than assuming logical and physical SGPR
numbers are identical:

- direct user-data descriptors below logical register 16 remain resident;
- `PtrExtendedUserData` at the declared pointer SGPR supplies later descriptors;
- SMEM immediate offsets are dword indices, so an extended load at offset `K`
  maps to logical user-data register `16 + K`;
- `PtrResourceTable` loads eight-dword texture descriptors, with table offset
  `8*N` mapping to texture resource `tN` for the observed table base;
- descriptor spill/reload through `v_writelane_b32` / `v_readlane_b32` is
  tracked, which is required by the large `80B8A010` family.

Across the local complete top-40 corpus this resolves all 126 decoded native
`image_*` instructions to a texture-resource provenance; the CI workflow
re-runs this fail-closed analysis from retail bytes.

## `8093EB1E` — 43 visible materials

Exact native samples:

```text
0x030 image_sample t1, dmask:Y
0x038 image_sample t0, dmask:RGB
```

`t0.rgb` is preserved as the surface color path and reaches `mrt0.rgb` after a
separate procedural scalar modulation.  The `t1` sample contributes only its Y
channel.  It does not feed RGB color output.

At native offsets `0x158..0x19c`, the shader computes:

```text
normal_pack_scale = 0.375 + 0.125 * t1.y
mrt1.xyz = saturate(0.5 + normal_pack_scale * N)
```

where `N` is the normalized interpolated surface normal.  Thus:

```text
t0 -> surface_rgb                                  PROVEN
t1 -> deferred_normal_magnitude_control_y          PROVEN
```

The common 128x128 green-looking `t1` images are therefore **not** promoted as
normal maps or color textures merely because of appearance. Their actual native
use is a one-channel deferred normal-packing control.

## `80AAE1C6` — 26 visible materials

This is the simpler sibling of `8093EB1E`.

```text
0x038 image_sample t0, dmask:RGB
0x040 image_sample t1, dmask:Y
```

`t0.rgb` reaches `mrt0.rgb` unchanged. `t1.y` is used only in:

```text
normal_pack_scale = 0.375 + 0.125 * t1.y
mrt1.xyz = saturate(0.5 + normal_pack_scale * N)
```

Therefore:

```text
t0 -> surface_rgb                                  PROVEN
t1 -> deferred_normal_magnitude_control_y          PROVEN
```

## `80AADCB3` — 30 visible materials

Exact native samples:

```text
0x030 image_sample t1, dmask:XY
0x038 image_sample t0, dmask:RGBA
```

`t1.xy` is remapped by material constants into signed XY, the shader computes

```text
z = sqrt(max(0, 1 - x*x - y*y))
```

then transforms the reconstructed vector through the interpolated basis and
normalizes it. This is the same instruction-level normal reconstruction pattern
already proven independently on the Vex `80AAE14B` material.

`t0.rgb` reaches `mrt0.rgb`. `t0.a` enters the deferred normal packing scale:

```text
normal_pack_scale = 0.375 + 0.125 * t0.a
```

Therefore:

```text
t0 -> surface_rgb_alpha_deferred_normal_control    PROVEN
t1 -> primary_normal_rg                            PROVEN
```

## `809DF9A4` — 55 visible materials

This larger family has the same fundamental texture contract as `80AADCB3`:

```text
0x030 image_sample t1, dmask:XY
0x038 image_sample t0, dmask:RGBA
```

`t1.xy` undergoes signed XY conversion, +Z reconstruction, basis transform and
normalization. `t0.rgb` feeds `mrt0.rgb`, with an additional authored/procedural
surface modulation. `t0.a` controls the normal-packing magnitude:

```text
normal_pack_scale = 0.375 + 0.125 * t0.a
```

Therefore:

```text
t0 -> surface_rgb_alpha_deferred_normal_control    PROVEN
t1 -> primary_normal_rg                            PROVEN
```

## `80AADC40` — 20 visible materials

This is a one-texture surface shader:

```text
0x024 image_sample t0, dmask:RGB
```

`t0.rgb` reaches `mrt0.rgb`. `mrt1` is generated only from the interpolated
geometric normal and fixed packing constants; no texture contributes to that
normal path.

```text
t0 -> surface_rgb                                  PROVEN
```

## Immediate coverage consequence

These five newly proven Tower families account for:

```text
55 + 43 + 30 + 26 + 20 = 174 visible materials
```

The two BC3+BC5 families were already good format-based preview candidates, but
are now canonical shader-semantic facts. More importantly, the 69 materials in
`8093EB1E` + `80AAE1C6` can now use `t0` as an exact surface-RGB source even
though both of their textures are BC1 and the old format-only heuristic refused
to choose between them.

## `809DCD66` — deliberately not flattened yet

This 24-material family samples both textures as single-channel scalars. The
native code computes a view-dependent UV displacement before the second sample
and constructs output RGB from material constants and the two sampled scalars.
Neither texture is a direct RGB base-color map, so binding `t0` or `t1` as glTF
base color would be wrong.

The safe next step is to recover its exact palette/constants and emulate that
native scalar-to-RGB path in the portable adapter. Until that is done, this
family remains unflattened rather than being given a guessed PBR texture role.

## Portable preview policy

The glTF preview adapter may directly bind `surface_rgb` and
`surface_rgb_alpha_deferred_normal_control` as base-color sources, ignoring the
non-color alpha semantics for now while keeping glTF alpha opaque. It may bind
`primary_normal_rg` through the existing BC5 XY -> +Z portable conversion.

This is an approximation of D1's deferred renderer, not a claim that glTF PBR is
identical to Bungie's shader. The exact t# bindings and proven per-channel roles
remain the canonical record.
