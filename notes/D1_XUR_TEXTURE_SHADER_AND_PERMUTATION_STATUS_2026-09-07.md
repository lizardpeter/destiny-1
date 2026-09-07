# D1 Tower Xur texture, shader, and material-permutation proof boundary

Date: 2026-09-07
Target identity: Xur (`StringHash 46C55854`)
Tower serialized entities: `80C7ACC8`, `80C885AA`
Entity model: `80C88CEF`

This note is the authoritative boundary between what is already source-/binary-proven and what is still only a portable preview or an open reverse-engineering target.

## Exact texture closure: solved at the native resource-binding level

The pinned Xur textured checkpoint accepted by `.github/workflows/d1-tower-xur-exact-textured-all-actions.yml` proves:

- 54 exact D1 materials in the Xur model export.
- 104 exact source texture resources embedded.
- 232 exact pixel-shader texture binding edges.
- 0 vertex-shader texture binding edges for this Xur material set.
- 52/54 materials receive an evidence-scoped portable glTF base-color preview binding.
- 45/54 materials receive an evidence-scoped portable glTF normal preview binding.

The authoritative texture representation is **not** the glTF PBR slot assignment. The authoritative representation is the exact native material -> shader stage -> `t#` -> Texture TagHash graph preserved by `material_texture_manifest.json` and copied into glTF material/image extras by `tools/d1_gltf_bind_exact_shader_textures_v3.py`.

Therefore:

- source texture discovery/recovery is closed for the current Xur checkpoint;
- native texture TagHashes and shader-register indices are preserved exactly;
- portable `baseColorTexture` / `normalTexture` bindings remain preview adapters only.

## Native shader binary/resource closure: solved for the current 54-material Xur checkpoint

Workflow `.github/workflows/d1-tower-xur-all-native-shader-census.yml` completed successfully in GitHub Actions run `34145462195`, job `101816429667`.

Durable workflow commit: `7e2353c9044e92a2191b96d5843b2e56a2f2f125`.

Proof artifact:

- name: `D1-TOWER-XUR-ALL-NATIVE-SHADER-CENSUS`
- artifact ID: `10027557806`
- artifact ZIP SHA-256: `e26febd88c0fcc05d998ec7dab04efcf1582095ee594a459ec472c530c7a5086`
- artifact size: 323,302 bytes
- 156 files

The completed census proves:

- 54 exact Xur materials;
- 25 unique pixel-shader header TagHashes;
- 11 unique vertex-shader header TagHashes;
- 36 total unique shader headers;
- 36/36 shader headers resolved to native Orbis shader payloads;
- 36/36 bounded native GCN payloads extracted with zero errors;
- total bounded GCN size = 30,428 bytes;
- all 36 bounded programs CLRX-disassemble in pinned raw `GFX700` mode through `s_endpgm` with no decoder stderr;
- 31 unique bounded GCN programs after grouping exact code by SHA-256;
- no additional native-program package family was required after resolving the exact headers;
- all 25 Xur pixel shaders were analyzed for native image-resource usage;
- 116 native GCN image instructions were found;
- all 116/116 image instructions were resolved back to exact D1 texture-resource indices;
- 0 unmatched image instructions;
- 0 missing pixel-shader disassemblies;
- the existing proven shader-role table remains valid against this Xur-native census with zero validation errors.

The fail-closed final status is:

`D1_XUR_SHADER_BINARY_AND_IMAGE_RESOURCE_CLOSURE_EXACT`

This is stronger than merely retaining shader TagHashes in a GLB: the exact retail PS4 machine code itself is now recovered and bounded for every VS and PS used by the current 54-material Xur checkpoint, and every native pixel-shader image instruction is connected back to the exact serialized D1 `t#` resource namespace.

## Shader semantic recreation: still open

Binary/resource closure is not the same thing as retail-equivalent portable shading.

`notes/PS4_09A_SHADER_DATAFLOW.md` proves that our existing pipeline can lift individual D1 native programs to instruction-level equations, including UV transforms, normal reconstruction, cubemap sampling, palette math, output MRT behavior, and local constant usage. We must now apply that semantic lifting systematically to Xur's **31 unique bounded GCN programs**, rather than treating all 54 materials independently.

Remaining shader work is:

- recover and classify all material-local constant blocks for the 54 materials;
- recover exact sampler descriptors and TFX streams;
- group materials by the 31 exact GCN program families plus their local state;
- lift per-program arithmetic, interpolant semantics, output/MRT behavior, and alpha behavior;
- recover required higher-level/global constant producers;
- recover exact render/blend/depth/raster state where it changes the visible result;
- distinguish instruction-proven texture semantics from preview-only role guesses;
- implement a retail-equivalent portable renderer/material adapter from those recovered equations and states.

Until that is done, the current glTF `baseColorTexture` / `normalTexture` assignments remain a preview adapter and must not be described as the retail shader.

## Material permutation selection: current `main` is still permutation-index 0

The repository was rechecked before this note was written. `tools/d1_render_owner_probe.py` currently parses:

- `TexturePlatesROI`;
- `ExternalMaterialsMap`;
- the full `ExternalMaterials` bank;
- and records the first material for each range as the current Charm-style convenience selection.

It does **not** yet contain an authoritative D1 live switch-key/value evaluator. The actual current export path still behaves as permutation index 0 for an external-material range unless another source-specific resolver overrides it.

This matters because a visually exact Xur export requires two different kinds of closure:

1. **selection closure** — prove which external-material member retail Xur selects for every `VariantShaderIndex`;
2. **shading closure** — reproduce the selected materials' native shader behavior.

Do not mark Xur visually exact until both are closed.

## Comparative implementation evidence

The current MIDA/Charm-family implementation contains a later-strategy `ModelPermutation` mechanism that builds switch-key/value sets and maps exact sorted key/value combinations to permutation indices. Its model-parent schema uses descriptor/index arrays plus switch records. This is useful structural evidence, but its Marathon class hashes/offsets are **not** D1 authority. Any D1 implementation must first be calibrated against exact D1 `0x80801A9C` parent bytes and must fail closed when a pointer/count/range does not validate.

## Immediate continuation

Two proof tracks can now proceed without guessing:

1. **Xur shader semantic lifting** — operate on the 31 exact bounded GCN program families, recover their exact material-local inputs and render state, and turn instruction-level behavior into a reusable D1 shader IR / portable implementation.
2. **D1 live external-material permutation selection** — calibrate the exact D1 `0x80801A9C` model-parent layout from retail bytes, identify its descriptor/index/switch structures without importing later-strategy offsets, locate the instantiated Xur switch-key/value state, and make external-material selection fail-closed and source-owned.

The final Xur visual checkpoint should only be promoted once these two tracks meet: exact selected material member + exact native-equivalent shading for that member.
