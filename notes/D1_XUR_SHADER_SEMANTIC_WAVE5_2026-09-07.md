# D1 Xur shader semantic wave 5 closure

Date: 2026-09-07

This note extends `notes/D1_XUR_TEXTURE_SHADER_AND_PERMUTATION_STATUS_2026-09-07.md`. The older note remains the broader proof-boundary document; this file records the later Wave 5 shader-semantic promotion and reusable-registry checkpoint.

## Exact Wave 5 checkpoint

GitHub Actions run `34155152832` completed successfully from commit `6d6f39d2fe00ad48cd2f1bdf80e1c83c412916eb`.

Artifact:

- name: `D1-TOWER-XUR-SHADER-SEMANTIC-WAVE5`
- artifact ID: `10030701808`
- ZIP SHA-256: `e62373d1b3ee008498472f0b0a42ed26c6e3086636e98a733debc620240cf1fb`
- status: `D1_XUR_NATIVE_GCN_DATAFLOW_WAVE5_EXACT`

Wave 5 exact semantic coverage is:

- 10 / 31 unique bounded native GCN programs instruction-level closed;
- 15 / 38 stage structural units closed;
- 11 / 33 combined material structural families have both VS and PS native dataflow closed;
- 29 / 54 current Xur materials have both current VS and PS native dataflow closed;
- 31 / 54 materials have exact PS dataflow coverage;
- 48 / 54 materials have exact VS dataflow coverage.

The two materials newly promoted to both-stage closure in this wave are `8087623F` and `80876411`.

## PS 80876579: psychedelic preview root cause is source-closed

`tools/d1_xur_ps_80876579_semantic_proof.py` closes native PS `80876579` / bounded GCN SHA-256 `f60720572d9bd42f06c3fffc3ef5e178f8a9d7917fa8c83d96511830e45b0c00` for four materials:

- `808761EC`
- `80876227`
- `8087623F`
- `80876411`

The exact retail texture register set is:

- t0 `80876551` — BC1 sRGB;
- t1 `80876552` — BC3 sRGB;
- t2 `80AB04BB` — BC3 sRGB;
- t3 `80AAF8B8` — BC3 sRGB;
- t4 `80876553` — BC1 sRGB;
- t5 `80876554` — BC5 linear;
- t6 `80AB04BC` — BC5 linear;
- t7 `80AACC28` — RGBA8 linear, six-face 64x64 cube.

The native GCN proves that t0 is **not visible base color**. Its RGB channels drive palette/control and coverage math. Visible surface RGB originates from t1 multiplied by a t0-selected palette before reflection composition. The old portable glTF preview exposed t0 directly as `baseColor`, which is the exact source of the saturated blue/green/red Xur appearance seen in Blender.

The proof also closes:

- t5+t6 normal construction and tangent-basis transform;
- camera/view-vector and reflected-vector construction;
- explicit-LOD t7 cubemap sampling;
- palette reconstruction from t0+t2+t3+t4;
- surface/palette multiplication;
- Fresnel/reflection contribution;
- MRT0 surface output and MRT1 normal packing.

TFX producer semantics are intentionally still a separate gate. The scoped stream ends in `42 0A`, strongly associating the final TFX result with material CBuffer vector 10 used by the PS alpha-test path, but the global semantic meaning of opcode `0x42`, the exact `Frame` producer, and runtime evolution of c10 are not yet promoted beyond the scoped evidence.

## Reusable native shader semantic registry

The current reusable registry is `evidence/d1_native_shader_semantic_registry_v1.json` and is keyed by:

`shader stage + exact bounded native GCN SHA-256`

After Wave 5 it contains 10 exact program handlers: 7 PS and 3 VS. `80876579` is registered as semantic class `control_palette_surface_reflection`.

The registry validator was promoted to Wave 5 and completed green in GitHub Actions run `34155309901` at commit `3f2b3606e10627442c48c01529e3251ca1bdd431`.

This is the reuse boundary for other characters and game assets: exact instruction-level semantics may be reused when stage+GCN SHA match, but each future asset must still supply and validate its own textures, constants, TFX values, samplers, fetch layout, runtime/global state, render state, and material selection.

## Still open before a retail-equivalent Xur Blender export

Wave 5 does **not** promote the current GLB to retail-equivalent rendering. The remaining independent gates include:

- remaining native PS/VS semantic units;
- TFX producer semantics where visually required;
- exact render/blend/depth/raster state where relevant;
- missing runtime/default texture descriptors for the two previously identified `808768C0` cases;
- exact D1 live external-material permutation selection rather than member/permutation 0;
- portable shader/material recreation using the recovered equations;
- Blender-visible validation of the corrected selected Xur model with all 267 retail actions.

The next highest-leverage PS target is `80876952` (GCN SHA `cd1acacbbf0fa69a229255ab4d21c8f218fb50b3c031d63a6bb3c866d5dc57a7`). It covers three materials (`808764C9`, `808767AE`, `808767AF`), all of which already use a closed four-influence dual-quaternion VS, so closing this single PS can promote three more materials to both-stage native-dataflow closure.
