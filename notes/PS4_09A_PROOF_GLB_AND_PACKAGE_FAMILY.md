# PS4 816CE09A proof GLB + logical package-family checkpoint

Date: 2026-09-04

This note records the first reproducible textured + rigged + multi-animation GLB for the byte-proven D1 PS4 Vex model `816CE09A`, and a package-resolution behavior discovered while making the build reproducible.

## Reproducible proof GLB

GitHub Actions workflow:

- `.github/workflows/build-09a-test-glb.yml`
- successful run: `33873254513`
- head commit: `2a4dda7387aab5280a3776db4667d741b224b832`
- artifact: `816CE09A-proven-material-test-glb`

Generated GLB:

- `816CE09A_PROVEN_MATERIAL_TEST.glb`
- size: `7,245,808` bytes
- SHA-256: `df63fbafd77f745a056220978d6c5579bc968ba6bd141f7571e8660ccbd396d7`

Independent post-download validation confirmed:

- glTF 2.0 GLB header and declared length are exact
- 1 mesh
- 2 visible primitives
- 4,172 vertices
- 5,336 triangles
- 1 skin
- 12 joints
- inverse bind matrices present
- JOINTS_0 / WEIGHTS_0 present on both visible primitives
- 2 animations: `816CE09D`, `816CE09E`
- 36 channels in each animation = translation/rotation/scale for all 12 joints
- 2 portable materials
- 11 embedded images
- native D1 hashes/equations/approximation policy preserved in glTF `extras`

This GLB is a test/export interchange artifact. It is **not** a claim that glTF PBR reproduces Destiny's renderer. Native D1 material/shader/sampler semantics remain authoritative and must eventually be implemented directly in the target game renderer.

## Native provenance represented by the GLB

Render owner / model:

- owner EntityResource: `816CE12B`
- model: `816CE09A`
- skeleton: `816CE092`
- runtime rig: `816CE095`
- animations: `816CE09D`, `816CE09E`

Parent-selected visible materials:

- `VariantShaderIndex 0 -> 809C475F`
- `VariantShaderIndex 1 -> 816CE240`

Visible source geometry ranges:

- variant 1: index offset 0, count 926 -> 564 triangles
- variant 0: index offset 927, count 7,780 -> 4,772 triangles

Auxiliary inline passes:

- `80AAE10B`, `VariantShaderIndex=-1`, range `927/7780`
- `80AAE10C`, `VariantShaderIndex=-1`, range `927/7780`
- both have pixel shader `FFFFFFFF` and are filtered by the source-confirmed D1 render path
- they are retained as provenance, not emitted as visible glTF primitives

Main portable material is based on byte-proven native material `809C475F`:

- PS `80AAE14B`
- PS constants `80AAE14C`
- t0 `80AACCDD`
- t1 `80AACCDF`
- t2 `80AACC26`
- t3 `80AACC28`
- t4 `80AACCDD`

Circuitry portable material is based on byte-proven native material `816CE240`:

- PS `816CE0A8`
- PS constants `816CE185`
- texture `816CE1C5`
- sampler `816CE0AA`

Native equations and unresolved renderer state are preserved by `tools/d1_gltf_material_recipe.py`; portable PBR fields must not be used to redefine native semantics.

## Exact retail texture chains reproduced in the build

- `80AACCDD` 2048x2048 BC3 -> `80AACCDE` -> `80AAE66A` (0157 full backing)
- `80AACCDF` 1024x1024 BC5 -> `80AACCE1` -> `80AAE66B`
- `80AACC26` 256x256 BC5 -> `80AACC27` -> `80AAE586`
- `80AACC28` 64x64 RGBA8 cubemap-like array of 6 -> `80AACC29`
- `816CE1C5` 256x512 BC1 -> `816CE1CA` -> `816CE246`

`tools/d1_texture_export.py` now resolves cross-package second-hop backing hashes and emits cubemap faces independently.

## Important package-format finding: physical patch members are one logical namespace

A reproducibility failure exposed a Tiger behavior that should become first-class in our parser API.

Opening only the highest physical patch member (for example `ps4_globals_0156_5.pkg`) exposes the logical entry metadata but can leave referenced data blocks unavailable. The corresponding lower patch siblings must be present beside it so `EntryReader` can resolve the logical package's block residency.

For this fixture the successful build requires the complete relevant families:

### 0156

- `ps4_globals_0156_0.pkg`
- `ps4_globals_0156_1.pkg`
- `ps4_globals_0156_2.pkg`
- `ps4_globals_0156_3.pkg`
- `ps4_globals_0156_4.pkg`
- `ps4_globals_0156_5.pkg`

### 0157

- `ps4_globals_0157_0.pkg`
- `ps4_globals_0157_1.pkg`

### 0767

- `ps4_arch_vex_com01_0767_0.pkg`
- `ps4_arch_vex_com01_0767_1.pkg`
- `ps4_arch_vex_com01_0767_4.pkg`

This means our public abstraction should eventually be something like `LogicalPackageFamily`, with one merged entry namespace and deterministic block lookup across `_0`, `_1`, `_2`, ... patch members. Individual physical `.pkg` files are storage members, not necessarily self-contained semantic packages.

The same issue explains why a compact `d1_vector_container_probe.py` run against individual `_1` / `_4` files returned zero `80801AA5` containers even though materials reference `80AAE14C`, `816CE185`, etc. Vector-constant probing should be redone through the logical family view rather than treating one physical member as the whole namespace.

## Export-harness compatibility fixes discovered

The pinned public `tiger-animation-parser` validation oracle uses `numpy.fromfile`, so animation clips must be supplied through a real file descriptor rather than `BytesIO`.

The currently installed `pygltflib` `Sampler` schema does not accept an optional `name=` constructor argument; sampler display labels are therefore omitted. No native semantics are lost because exact D1 sampler hashes and GNM words are preserved in material-recipe provenance.

These compatibility fixes should be promoted from workflow-time adaptations into the durable exporter source after the test artifact is accepted.

## Native reverse-engineering frontier after the GLB

The interchange/export milestone is now achieved. The remaining goal is the native renderer/format reconstruction:

1. Implement a first-class logical package-family reader and migrate probes/exporters to it.
2. Re-probe `80AAE14C`, `816CE185/186/187/188/189/0A9` through the merged namespace and preserve exact float4 constants.
3. Finish PS4 GCN shader input/resource semantics for `80AAE14B` and `816CE0A8`.
4. Decode exact render-state / MRT / blend behavior, especially the circuitry pass and unresolved global intensity multipliers.
5. Use the Xbox One D1 DXBC counterpart as a semantic oracle for texture-register and constant-buffer usage, then map those semantics back to PS4 GCN.
6. Implement Destiny-native material + shader + sampler behavior directly in the target game renderer instead of relying on glTF PBR.
7. Generalize the proven model/skeleton/rig/animation/material pipeline from this fixture to arbitrary D1 assets and maps.

The GLB is therefore a validation target, not the endpoint of the reverse engineering.