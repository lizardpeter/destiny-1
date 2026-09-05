# D1 Tower common-layer pixel-shader dataflow

This note records instruction-level texture semantics recovered from the exact PS4
Tower common-layer shaders. The input corpus is the 65-family common material set
and the CLRX raw `GFX700` disassembly produced by
`.github/workflows/d1-tower-common-layer-shader-disassembly.yml`.

The same policy used for the baked Tower remains in force: storage format and image
appearance are not semantic proof. A role is promoted only when the native image
instruction can be mapped to an exact D1 t# descriptor and its sampled component can
be followed into the shader output or another proven calculation.

## Newly closed common families

### `8093E96F` — 7 visible common materials

`t0` is a direct surface RGB source.

The shader samples `t0.xyz` with `dmask:7` at address `0x24`. The three returned
components remain separate, are multiplied only by authored scalar/vector constants,
and are packed directly into `mrt0` at the end of the shader. No alpha-only or palette
reinterpretation occurs.

Canonical role:

```text
t0 = surface_rgb
```

This converts seven common materials from a format-only preview guess to a native-
dataflow-proven portable base-color binding.

### `80CA08B0` — 3 visible common materials

This family had been visually tempting because material `t0` is BC1 and `t2` is BC5.
The native shader proves that treating `t0` as base color is wrong.

- `t2.xy` is sampled at `0x54`, affine-remapped, squared, `1-x^2-y^2` is clamped,
  and `sqrt` reconstructs the third component. That is the primary tangent normal.
- `t1` is addressed with the native `v_cubema/v_cubetc/v_cubesc/v_cubeid` sequence,
  queried by `image_get_lod` at `0x1F8`, then sampled by `image_sample_l` at `0x258`.
  It is therefore the environment cubemap.
- `t0.r` is sampled at `0x1CC`; that scalar is folded into the computed cube LOD
  before the `image_sample_l`. It is a reflection-LOD control, not RGB surface color.
- A fourth sampled descriptor, `t11`, comes from the runtime resource table rather
  than the material's serialized t0/t1/t2 bindings and is kept separate from the
  material semantic table.

Canonical roles:

```text
t0 = reflection_lod_control_r
t1 = environment_cubemap
t2 = primary_normal_rg
```

### `80CA08B1` — 3 visible common materials

The shader samples only `t0.r` (`dmask:x`) and uses the scalar to modulate RGB built
from material constants. Texture RGB never reaches the output.

```text
t0 = material_rgb_intensity_mask_r
```

### `80CA08C1` and `80CA08C3` — 2 visible materials each

Both shaders sample only `t0.a` (`dmask:w`). The returned alpha scales RGB assembled
from authored constants. These are siblings of already-proven `80CA08C4`.

```text
t0 = material_rgb_intensity_mask_a
```

This is important negative evidence: the underlying BC3 image is color-capable, but
its RGB channels are not consumed by these shader variants and must not be promoted
to glTF base color by a format fallback.

### `80CA0BFA` — 2 visible common materials

The shader samples all four `t0` channels. The sampled RGB components remain separate
and reach `mrt0` after authored scaling, while sampled alpha contributes to the common
intensity multiplier applied to those RGB values.

```text
t0 = surface_rgb_alpha_intensity_control
```

The RGB portion has a safe portable base-color interpretation; the alpha control is
retained in the richer native role name rather than being misrepresented as generic
transparency.

## Preview fallback correction

`tools/d1_world_texture_role_inventory.py` now treats a proven non-portable role as
negative evidence for incompatible format heuristics. Once native dataflow proves a
binding is, for example, `material_rgb_intensity_mask_a` or
`reflection_lod_control_r`, that same BC/RGBA texture can no longer be selected as a
"sole color-capable t0" base-color preview merely because its storage format could
hold RGB.

Format candidates now consider only bindings whose shader semantics are still
unproven. This fixes a real preview correctness bug without weakening the distinction
between canonical D1 shader semantics and provisional portable rendering adapters.
