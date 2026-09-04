# PS4 816CE09A proof GLB + logical package-family checkpoint

Date: 2026-09-04

This note records the first reproducible textured + rigged + multi-animation GLB for the byte-proven D1 PS4 Vex model `816CE09A`, plus package-patch and material-constant behavior established while making the build reproducible.

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

The deterministic DDS decoder was pixel-compared with the older Pillow DDS path for BC5. The decoded RGBA pixels are bit-identical (`maxdiff = 0`); differing PNG SHA-256 values are only different PNG byte encoding/compression. All six cubemap PNGs are byte-identical to the earlier export.

## Package patch behavior: entry-table snapshots plus patch-resident blocks

A reproducibility failure exposed a Tiger behavior that should become first-class in our parser API.

`EntryReader` currently parses the entry/block tables from the physical member that is opened. Each block record then contains a `patch_id`, and `patch_path()` maps that directly to the sibling `..._<patch_id>.pkg` file. Therefore an entry-table snapshot can reference payload blocks physically resident in lower patch members.

Opening a later member without its lower siblings can expose correct entry metadata while making payloads unavailable. The complete required family must be present for deterministic extraction.

For this fixture the successful build requires:

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

A dedicated non-speculative census tool now exists:

- `tools/d1_package_family_probe.py`
- first family/vector census run: `33873725331`

Retail census results:

### 0157

- `_0`: 2,117 entries / 1,623 blocks
- `_1`: 8,192 entries / 1,749 blocks
- union TagHashes: 8,192
- all 2,117 `_0` TagHashes occur in `_1`
- 904 duplicate entries have identical metadata
- 1,213 duplicate entries have changed metadata

### 0767

- `_0`: 424 entries / 239 blocks
- `_1`: 594 entries / 232 blocks
- `_4`: 594 entries / 233 blocks
- union TagHashes: 594
- `_1` vs `_4`: 593/594 entries have identical metadata
- sole `_1` -> `_4` metadata override: `816CE033`
  - `_1`: class `80800576`, 93 bytes, starting block 1 + 108544
  - `_4`: class `80800576`, 120 bytes, starting block 232 + 0

This strongly supports treating later physical members as successive entry-table snapshots/overrides while block `patch_id` selects physical storage. We should still encode the final authoritative-entry precedence rule only after validating header `patch_id`/suffix consistency across a broader corpus.

## IMPORTANT correction: PS4 Vector4 containers are not Xbox `80801AA5`

An earlier compact diagnostic returned zero `80801AA5` resources and was initially misattributed to physical-member namespace visibility. That interpretation was wrong.

Current retail evidence proves two platform representations:

- **PS4 ROI:** material Vector4 FileHash -> FileEntry `type=32, subtype=7`, 16-byte GPU header -> `FileEntry.Reference` raw vec4 payload. Header `+0x08` is vec4 unit count; referenced payload size is `count * 16`.
- **Xbox One ROI:** structured `80801AA5` resource with 0x30-byte header + raw vec4 payload.

The target PS4 hashes are present and decodable in the later entry-table snapshots.

### Main material `80AAE14C`

`80AAE14C` is `32:7 -> 80AAE14E`, vector count 19. It is byte-identical in `0157_0` and `0157_1`.

Exact float4 constants:

0. `[2.5, -1.25, -1.25, -1.25]`
1. `[0, -1, 1, 1]`
2. `[1, 0, 0, 0]`
3. `[20, 0.4, 0, 0]`
4. `[2, -1, -1, -1]`
5. `[0, 0, 0, 0]`
6. `[0, 0, 0, 0]`
7. `[0, 0, 0, 0]`
8. `[3, 1, 1, 1]`
9. `[0, 1, 1, 1]`
10. `[-1.3, 2.3, 1, 1]`
11. `[0, 2.5, 0, 0]`
12. `[1, 0.4200000167, 0, 1]`
13. `[2, 0, 0, 0]`
14. `[0.75, 0.75, 1.5, 1.5]`
15. `[0, 0, 0, 0]`
16. `[0, 0, 0, 0]`
17. `[0, 0.4715686738, 120, 121]`
18. `[0, 0.4754902422, 121, 122]`

Several already-recovered shader equations are directly visible in these constants, including detail UV `[20, 0.4]`, `reflection_q = saturate(2.3*S - 1.3)`, and the `2.5` reflection multiplier. Constants 17/18 remain preserved but not semantically named yet.

### Circuitry family constants

All six variant containers have 8 vec4s. Vectors 0/1 are zero, vec2 is `[0.4,0,0,0]`, vec3 is the luma vector `[0.3,0.59,0.11,0]`, vec6 is `[1,1,1,1]`. Vec4/vec5 form the palette `base + delta*L`; vec7 is the local intensity scalar.

- `816CE0A9`: base `[0.0115131522,0.0258343946,0.0280808620]`, delta `[0.3984868526,0.8941656351,0.9719191194]`, bright endpoint ~= `[0.41,0.92,1.0]`, intensity `5`
- `816CE185` (default `816CE240`): base `[0.0151604200,0.0208455771,0.0379010513]`, delta `[0.3848395944,0.5291544199,0.9620989561]`, bright endpoint ~= `[0.40,0.55,1.0]`, intensity `5`
- `816CE186`: base `[0.0299771838,0.0355443731,0.0428245477]`, delta `[0.6700227857,0.7944555879,0.9571754336]`, bright endpoint ~= `[0.70,0.83,1.0]`, intensity `5`
- `816CE187`: base `[0.0204112902,0.0187103488,0.0566980168]`, delta `[0.3395887315,0.3112896681,0.9433019757]`, bright endpoint ~= `[0.36,0.33,1.0]`, intensity `5`
- `816CE188`: base `[0.0233529322,0.0066123544,0.0021214203]`, delta `[0.9766470790,0.0442637354,0.0119630974]`, bright endpoint ~= `[1.0,0.050876,0.014085]`, intensity **`40`**
- `816CE189`: base `[0.0628910884,0.0018867309,0.0031445611]`, delta `[0.9371089339,0.0281132683,0.0468554385]`, bright endpoint ~= `[1.0,0.03,0.05]`, intensity `5`

Thus the six variant materials are now proven to share the same shader/texture structure while changing principally the palette and, for `816CE188`, a dramatically larger local intensity.

## Export-harness compatibility fixes discovered

The pinned public `tiger-animation-parser` validation oracle uses `numpy.fromfile`, so animation clips must be supplied through a real file descriptor rather than `BytesIO`.

The currently installed `pygltflib` `Sampler` schema does not accept an optional `name=` constructor argument; sampler display labels are therefore omitted. No native semantics are lost because exact D1 sampler hashes and GNM words are preserved in material-recipe provenance.

These compatibility fixes should be promoted from workflow-time adaptations into the durable exporter source after the test artifact is accepted.

## Native reverse-engineering frontier after the GLB

The interchange/export milestone is now achieved. The remaining goal is the native renderer/format reconstruction:

1. Validate entry-table patch precedence and header `patch_id`/filename-suffix consistency across a broader corpus; then formalize a `LogicalPackageReader` that opens the authoritative snapshot while resolving patch-resident blocks.
2. Finish PS4 GCN shader input/resource semantics for `80AAE14B` and `816CE0A8`.
3. Decode exact render-state / MRT / blend behavior, especially the circuitry pass and unresolved global intensity multipliers.
4. Use the Xbox One D1 DXBC counterpart as a semantic oracle for texture-register and constant-buffer usage, then map those semantics back to PS4 GCN.
5. Implement Destiny-native material + shader + sampler behavior directly in the target game renderer instead of relying on glTF PBR.
6. Generalize the proven model/skeleton/rig/animation/material pipeline from this fixture to arbitrary D1 assets and maps.

The GLB is therefore a validation target, not the endpoint of the reverse engineering.